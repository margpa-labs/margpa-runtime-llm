"""Coordinate one cancellable conversation generation without storing chat history."""

from __future__ import annotations

import hashlib
import json
import threading
from collections.abc import Callable, Generator, Iterator
from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DOCUMENTATION_RAG_CITATION_SOURCE_CLASS,
    DocumentationAugmentation,
    DocumentationMeasurementUnit,
    DocumentationRagAvailability,
    DocumentationRagMode,
    DocumentationRagRequestContext,
)
from margpa_runtime_llm.modules.documentation_rag.ports import (
    ContextualRagOrchestratorPort,
    RagOrchestratorPort,
)
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationParameters,
    GenerationRequest,
    GenerationStream,
    ThinkingMode,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.response import (
    ResolvedResponseLanguagePolicy,
    ResponseLanguage,
    ResponseLanguageSource,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelRuntimeInfo
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
    ThinkingPresentationSession,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingContentKind,
    ThinkingParseStatus,
    ThinkingParseWarning,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode
from margpa_runtime_llm.orchestration.response_language import (
    compose_conversation_generation_messages,
)
from margpa_runtime_llm.orchestration.summarization import compose_summary_messages

from ..contracts import (
    ContextUsagePromptInjectionMode,
    ConversationDeltaChannel,
    ConversationEvent,
    ConversationEventType,
    ConversationGenerationInput,
    ExpressiveMode,
)

# P5-CODEX-006 Rework (Codex Second/Third Independent Review): the
# Source Class an untyped, flat `reference_message` string never
# carried — used for the local `_ContextSourceItem` this module builds
# itself, never a real `guardrail_governance` import (decoupling
# preserved exactly, see `GuardrailContextSourceHook` below). The
# per-Citation case reads `DocumentationReferenceBlock.source_class`
# directly (the RAG module's own declared classification, Third Review
# Rework) rather than this module independently re-guessing it; this
# constant remains only for the Legacy flat fallback, which has no
# `DocumentationReferenceBlock` to read a Source Class from at all.
_DOCUMENTATION_RAG_LEGACY_FLAT_SOURCE_CLASS = "documentation_rag_legacy_flat"

# P5-CODEX-006 Rework (Codex Third Independent Review item "Hard-codeせず
# ...決定すること"): the Prompt Composition Role for a given RAG Source
# Class is looked up here, never hard-coded inline at the single call
# site — a future distinct `source_class` (e.g. a Tool-call result, a
# fetched URL) gets its own Role mapping entry without touching
# `_inject_documentation_reference()`'s own logic. Both of today's
# known Source Classes map to `TOOL`; a Class absent from this mapping
# still falls back to `TOOL` (the safer default — never silently
# reusing `SYSTEM`/`USER`, see `_inject_documentation_reference()`).
_PROMPT_ROLE_BY_SOURCE_CLASS: dict[str, MessageRole] = {
    DOCUMENTATION_RAG_CITATION_SOURCE_CLASS: MessageRole.TOOL,
    _DOCUMENTATION_RAG_LEGACY_FLAT_SOURCE_CLASS: MessageRole.TOOL,
}

# Phase 4 Main Model Governance Points (P4-D-WU-002/003, P4-PNT-005/006,
# P4-COM-006/007): both Callables are optional and this module has no
# dependency on `runtime_governance` — it only calls a plain function and
# interprets `(should_intervene, reason_code)`, exactly the same
# decoupling already used for `GenerationObserverPort`'s `mode_provider`.
# A raised exception from either Callable fails *open* (generation
# proceeds unmodified) — a Governance bug must never break the core
# conversation feature; the caller wiring it in is responsible for its
# own Evidence/Degraded reporting.
GovernancePreHook = Callable[[GenerationRequest], "tuple[bool, str]"]
GovernancePostHook = Callable[[str], "tuple[bool, str]"]

# Phase 5 Guardrail Points (P5-0-WU-002 Additive Composition): the exact
# same decoupling as the Governance Hooks above — this module has no
# dependency on `guardrail_governance`. `guardrail_pre_hook`/
# `guardrail_post_hook` share the Governance Hooks' Callable shape
# exactly. `guardrail_stream_guard_factory` is evaluated once per Stage
# (never shared across Turns/Tabs, architecture §10) — it only needs to
# return an object with `feed(delta) -> Decision`/`finalize() -> Decision`,
# where `Decision` only needs `safe_release`/`terminated`/`reason_code`
# (structurally satisfied by `IncrementalStreamGuard`/`StreamGuardDecision`
# without this module importing them).
GuardrailPreHook = Callable[[GenerationRequest], "tuple[bool, str]"]
GuardrailPostHook = Callable[[str], "tuple[bool, str]"]


# `guardrail.context_source` (P5-CODEX-001 Rework, then P5-CODEX-006
# Rework per Codex Second Independent Review): evaluated once retrieval
# has produced real Reference content but *before* any of it is spliced
# into `GenerationRequest.messages` (P5-PNT-001/003), so a genuine Stop
# means Model Call 0 by construction. P5-CODEX-006 replaced the single
# flattened `str` this Hook originally received with a tuple of
# per-Source units — each retrieved chunk/citation is judged on its own
# `content` before any collapse into one untyped block, and each carries
# its own opaque `source_id` and `source_class` (never merely a `name`
# tag on an already-built `ChatMessage`, which Codex's Second Review
# explicitly rejected as insufficient Authority separation). This module
# still has zero import dependency on `guardrail_governance` — the Hook
# type stays a plain structural Protocol, satisfied by the local
# `_ContextSourceItem` dataclass this module builds itself.
class ContextSourceItemLike(Protocol):
    @property
    def source_id(self) -> str: ...

    @property
    def source_class(self) -> str: ...

    @property
    def content(self) -> str: ...


GuardrailContextSourceHook = Callable[["tuple[ContextSourceItemLike, ...]"], "tuple[bool, str]"]


@dataclass(frozen=True, slots=True)
class JudgeCompletionContext:
    """Everything a Judge Hook needs to correlate and evaluate one Turn
    (P6-CODEX-001) — no Evaluation/Judge module type appears here, keeping
    the same zero-dependency decoupling as the Governance/Guardrail Hooks
    above. `request_id` is the correlation key a caller (e.g.
    PersistentConversationService) already stores on its own Turn record,
    so a later reader can join Judge Evidence back to a specific
    Conversation/Turn without this module knowing about either.

    `model_key`/`model_runtime_info` (P6-CODEX-025, Fourth Rework) are the
    exact values this specific Attempt actually ran with — sourced from
    `ConversationGenerationSession`'s own already-per-Attempt-frozen
    `_request.model_key`/`_model_runtime_info` fields, never independently
    re-resolved by a Hook implementation. This is what makes Judge/Repair/
    Recording use the real Loaded Model identity instead of a stale
    bootstrap-time constant after a Runtime Model Switch."""

    request_id: str
    user_input: str
    assistant_content: str
    model_key: str
    model_runtime_info: ModelRuntimeInfo | None = None


# Called only after both Governance and Guardrail Post-checks have already
# Allowed the content (never on a rejected/error Turn) — a mode-OFF check,
# the actual Model Call, and any persistence are entirely the Hook
# implementation's responsibility; this module only guarantees *when* it is
# called and *never* uses its return value (Judge cannot affect Canonical
# Completion, P6-ACC-018/P6-CODEX-001). A raised exception is swallowed
# exactly like every other Hook here — a Judge bug must never break the
# core conversation feature.
JudgeCompletionHook = Callable[[JudgeCompletionContext], None]

# Reuses the exact same Context shape as Judge (P6-CODEX-011, Second
# Rework): Recording needs the identical 3 correlation/content fields and
# gains nothing from a parallel duplicate type. Unlike Judge, a Recording
# Hook never touches the shared Model Backend at all (pure local file I/O),
# so it carries none of Judge's same-Turn self-collision concerns and is
# invoked synchronously, inline, independent of Judge Mode (Mode
# orthogonality, ADR-6-013) — the two Hooks are stored and invoked
# separately so toggling one Mode OFF never silently starves the other.
RecordingCompletionHook = Callable[[JudgeCompletionContext], None]


@dataclass(frozen=True, slots=True)
class _ContextSourceItem:
    source_id: str
    source_class: str
    content: str


def _context_source_items(
    augmentation: DocumentationAugmentation,
) -> tuple[_ContextSourceItem, ...]:
    """P5-CODEX-006 Rework: one Source per retrieved chunk/citation,
    each judged on its own `content` — never the already-flattened
    `reference_message` string. `augmentation.reference_blocks`
    (`DocumentationReferenceBlock`, one per Citation, same order) is the
    real production `ContextualRagOrchestratorPort` path's per-chunk
    structure; the legacy, non-Contextual `RagOrchestratorPort` Protocol
    has no production adapter and never populates it, so its one
    flattened `reference_message` is still honestly scanned as exactly
    one, coarser-grained Source rather than silently skipped.

    Module-level (not a Session method) as of the Third Independent
    Review Rework: both the Guardrail check (`ConversationGenerationSession.
    _guardrail_context_source_check()`) and Prompt Composition
    (`ConversationGenerationService._inject_documentation_reference()`)
    call this exact same function on the exact same `augmentation`
    object — the identical typed `tuple[_ContextSourceItem, ...]` flows
    from Guardrail judgment through to immediately before the Backend
    Prompt is built, never re-derived independently at each boundary
    (P5-CODEX-006 Required Rework item 3)."""

    if augmentation.reference_blocks:
        return tuple(
            _ContextSourceItem(
                source_id=block.chunk_id,
                source_class=block.source_class,
                content=block.content,
            )
            for block in augmentation.reference_blocks
        )
    if augmentation.reference_message is not None:
        return (
            _ContextSourceItem(
                source_id="reference_message",
                source_class=_DOCUMENTATION_RAG_LEGACY_FLAT_SOURCE_CLASS,
                content=augmentation.reference_message,
            ),
        )
    return ()


@dataclass(frozen=True, slots=True)
class _CombinedStreamSummary:
    detection_count: int
    match_count: int
    degraded: bool
    terminated: bool
    reason_code: str | None = None


def _combine_stream_summaries(
    summaries: tuple[GuardrailStreamSummaryLike | None, ...],
) -> GuardrailStreamSummaryLike | None:
    """P5-CODEX-009 Rework: FINAL and REASONING each get their own,
    independent Stream Guard instance (never one shared scan state
    across the two Channels, which would let a Holdback flush of one
    Channel's tail be mis-tagged as the other's) — but both still
    report into the single `guardrail.stream_candidate` Point, so their
    Terminal Summaries are combined into one here before the Result
    Hook ever sees them."""

    present = tuple(summary for summary in summaries if summary is not None)
    if not present:
        return None
    terminated = any(summary.terminated for summary in present)
    reason_code = next((summary.reason_code for summary in present if summary.terminated), None)
    return _CombinedStreamSummary(
        detection_count=sum(summary.detection_count for summary in present),
        match_count=sum(summary.match_count for summary in present),
        degraded=any(summary.degraded for summary in present),
        terminated=terminated,
        reason_code=reason_code,
    )


class _StreamGuardDecisionLike(Protocol):
    """Read-only by design (`@property`, not plain attributes): a frozen
    `StreamGuardDecision` only exposes read-only fields, and a Protocol
    with plain mutable attributes is invariant in mypy, which a frozen
    dataclass can never structurally satisfy."""

    @property
    def safe_release(self) -> str: ...

    @property
    def terminated(self) -> bool: ...

    @property
    def reason_code(self) -> str | None: ...


class GuardrailStreamSummaryLike(Protocol):
    """P5-CODEX-009 Rework (Codex Second Independent Review item 2):
    the Terminal, Bounded roll-up of one Stage's Stream Guard activity
    — structurally satisfied by `StreamGuardSummary` without this
    module importing `guardrail_governance`."""

    @property
    def detection_count(self) -> int: ...

    @property
    def match_count(self) -> int: ...

    @property
    def degraded(self) -> bool: ...

    @property
    def terminated(self) -> bool: ...

    @property
    def reason_code(self) -> str | None: ...


class GuardrailStreamGuardLike(Protocol):
    def feed(self, delta: str) -> _StreamGuardDecisionLike: ...

    def finalize(self) -> _StreamGuardDecisionLike: ...

    def summary(self) -> GuardrailStreamSummaryLike: ...


GuardrailStreamGuardFactory = Callable[[], GuardrailStreamGuardLike]
# `guardrail_stream_result_hook` (P5-CODEX-009 Rework): called at most
# once per Stage that actually had a real (non-`None`) Stream Guard,
# right after that Guard's lifecycle for the Stage ends — regardless of
# whether it ended via Cancel, a genuine Reject, or normal completion
# (`_run_stage()`'s own `finally` block, mirroring the existing
# `_active_stream` cleanup there exactly). Exceptions are swallowed the
# same way every other optional Hook in this module already is — a
# Status/Evidence bug must never break the core Streaming feature.
GuardrailStreamResultHook = Callable[[GuardrailStreamSummaryLike], None]

TOKEN_LIMIT_WARNING = "最終回答を生成する前にToken上限へ到達しました。"
SUMMARY_FALLBACK_WARNING = (
    "The summary could not be completed safely. The original answer is shown."
)
CONTEXT_USAGE_NOTICE_MESSAGE_NAME = "context_usage_notice"
EXPRESSIVE_STYLE_NOTICE_MESSAGE_NAME = "expressive_style_notice"


class ConversationInference(Protocol):
    def stream(self, request: GenerationRequest) -> GenerationStream: ...


ChatPromptTokenCounter = Callable[[tuple[ChatMessage, ...], ThinkingMode], int]
TextTokenCounter = Callable[[str], int]
DOCUMENTATION_REFERENCE_MESSAGE_NAME = "documentation_reference"


@dataclass(frozen=True, slots=True)
class _StageResult:
    finish_reason: FinishReason | None = None
    usage: TokenUsage | None = None
    final_content: str = ""
    display_content: str = ""
    parse_status: ThinkingParseStatus | None = None
    warnings: tuple[ThinkingParseWarning, ...] = ()
    cancelled: bool = False
    # Phase 5 Guardrail Stream Candidate (ADR-5-006): set only when a
    # `guardrail_stream_guard_factory` was actually supplied and its
    # Scanner found a Match mid-stream — the Model Stream is cancelled
    # and no further Delta for this Stage is ever yielded, so the
    # matched Content itself never left this process.
    guardrail_stream_rejected: bool = False
    guardrail_stream_reason_code: str | None = None


class ConversationGenerationSession:
    def __init__(
        self,
        *,
        request_id: str,
        request: GenerationRequest | None,
        inference: ConversationInference,
        presentation: ThinkingPresentationService,
        presentation_policy: ResolvedThinkingPresentationPolicy,
        summarization: SummarizationConfig,
        summary_mode: SummaryMode,
        response_language: ResponseLanguage,
        documentation_augmentation: DocumentationAugmentation | None,
        documentation_rag: RagOrchestratorPort | ContextualRagOrchestratorPort | None,
        documentation_query: str | None,
        documentation_request_context: DocumentationRagRequestContext | None,
        documentation_request_factory: (
            Callable[[DocumentationAugmentation], GenerationRequest] | None
        ),
        text_token_counter: TextTokenCounter | None,
        effective_context_size: int,
        model_runtime_info: ModelRuntimeInfo | None,
        release: Callable[[], None],
        governance_pre_hook: GovernancePreHook | None = None,
        governance_post_hook: GovernancePostHook | None = None,
        guardrail_pre_hook: GuardrailPreHook | None = None,
        guardrail_post_hook: GuardrailPostHook | None = None,
        guardrail_stream_guard_factory: GuardrailStreamGuardFactory | None = None,
        guardrail_context_source_hook: GuardrailContextSourceHook | None = None,
        guardrail_stream_result_hook: GuardrailStreamResultHook | None = None,
        judge_completion_hook: JudgeCompletionHook | None = None,
        recording_completion_hook: RecordingCompletionHook | None = None,
    ) -> None:
        self._request_id = request_id
        self._request = request
        self._inference = inference
        self._presentation = presentation
        self._presentation_policy = presentation_policy
        self._summarization = summarization
        self._summary_mode = summary_mode
        self._response_language = response_language
        self._documentation_augmentation = documentation_augmentation
        self._documentation_rag = documentation_rag
        self._documentation_query = documentation_query
        self._documentation_request_context = documentation_request_context
        self._documentation_request_factory = documentation_request_factory
        self._text_token_counter = text_token_counter
        self._effective_context_size = effective_context_size
        self._model_runtime_info = model_runtime_info
        self._release = release
        self._governance_pre_hook = governance_pre_hook
        self._governance_post_hook = governance_post_hook
        self._guardrail_pre_hook = guardrail_pre_hook
        self._guardrail_post_hook = guardrail_post_hook
        self._guardrail_stream_guard_factory = guardrail_stream_guard_factory
        self._guardrail_context_source_hook = guardrail_context_source_hook
        self._guardrail_stream_result_hook = guardrail_stream_result_hook
        self._judge_completion_hook = judge_completion_hook
        self._recording_completion_hook = recording_completion_hook
        self._cancel_requested = threading.Event()
        self._finished = threading.Event()
        self._consumption_lock = threading.Lock()
        self._stream_lock = threading.Lock()
        self._active_stream: GenerationStream | None = None

    @property
    def request_id(self) -> str:
        return self._request_id

    @property
    def finished(self) -> bool:
        return self._finished.is_set()

    @property
    def documentation_augmentation(self) -> DocumentationAugmentation | None:
        """The RAG result for this generation, if any, once `events()` has run it."""

        return self._documentation_augmentation

    def request_cancel(self) -> None:
        self._cancel_requested.set()

    def wait(self, timeout: float | None = None) -> bool:
        return self._finished.wait(timeout)

    def force_cancel(self) -> None:
        """Legacy emergency hook; normal callers use cooperative request_cancel()."""

        self._cancel_requested.set()
        with self._stream_lock:
            stream = self._active_stream
        if stream is not None:
            stream.cancel()

    def events(self) -> Iterator[ConversationEvent]:
        if not self._consumption_lock.acquire(blocking=False):
            raise RuntimeError("a conversation generation session can only be consumed once")

        try:
            # P6-CODEX-012 (Second Rework, P6-OBS-004's Current Request
            # State Machine): the very first thing any Turn does, before
            # even Documentation Retrieval or the Guardrail/Governance
            # Pre-checks below — a plain STATUS event (never the `START`
            # type, which stays reserved for its pre-existing meaning) so
            # existing consumers that only handle `start`/`completed`/etc.
            # are unaffected by this new, purely additive phase marker.
            yield self._status_event(state="preparing")
            if self._documentation_rag is not None:
                yield self._start_event(state="retrieving_documentation")
                assert self._documentation_query is not None
                if isinstance(self._documentation_rag, ContextualRagOrchestratorPort):
                    assert self._documentation_request_context is not None
                    augmentation = self._documentation_rag.augment_with_context(
                        self._documentation_query,
                        self._documentation_request_context,
                        cancelled=self._cancel_requested.is_set,
                    )
                else:
                    augmentation = self._documentation_rag.augment(
                        self._documentation_query,
                        cancelled=self._cancel_requested.is_set,
                    )
                self._documentation_augmentation = augmentation
                yield self._retrieval_event(augmentation)
                if self._cancel_requested.is_set():
                    yield self._cancelled_event()
                    return
                if not augmentation.should_generate:
                    warning = augmentation.warnings[-1]
                    yield self._error_event(
                        code=warning.code,
                        message=warning.message,
                        retryable=False,
                    )
                    return
                context_source_stop = self._guardrail_context_source_check(augmentation)
                if context_source_stop is not None:
                    yield context_source_stop
                    return
                assert self._documentation_request_factory is not None
                self._request = self._documentation_request_factory(augmentation)
            if self._summary_mode is SummaryMode.OFF:
                yield from self._events_without_summary()
            else:
                yield from self._events_with_summary()
        except InferenceError as exc:
            yield self._error_event(
                code=exc.code.value,
                message=exc.safe_message,
                retryable=exc.retryable,
            )
        except Exception:
            yield self._error_event(
                code="unexpected_error",
                message="The generation failed unexpectedly.",
                retryable=False,
            )
        finally:
            self._finished.set()
            self._release()

    def _events_without_summary(self) -> Generator[ConversationEvent, None, None]:
        assert self._request is not None
        yield self._status_event(state="guarding")
        pre_stop = self._guardrail_pre_check() or self._governance_pre_check()
        if pre_stop is not None:
            yield pre_stop
            return
        if self._documentation_augmentation is None:
            yield self._start_event(state="generating")
        else:
            yield ConversationEvent(
                event=ConversationEventType.STATUS,
                data={"request_id": self.request_id, "state": "generating"},
            )
        result = yield from self._run_stage(
            request=self._request,
            presentation=self._presentation.start_stream(self._presentation_policy),
            emit_deltas=True,
        )
        if result.cancelled:
            yield self._cancelled_event()
            return
        if result.guardrail_stream_rejected:
            yield self._error_event(
                code=result.guardrail_stream_reason_code or "guardrail_stream_rejected",
                message="Generation was stopped by the Guardrail during streaming.",
                retryable=False,
            )
            return
        yield from self._warning_events(result.warnings)
        yield self._completed_event(
            presented=result,
            original=result,
            summary=None,
            include_summary_metadata=False,
        )

    def _events_with_summary(self) -> Generator[ConversationEvent, None, None]:
        assert self._request is not None
        yield self._status_event(state="guarding")
        pre_stop = self._guardrail_pre_check() or self._governance_pre_check()
        if pre_stop is not None:
            yield pre_stop
            return
        if self._documentation_augmentation is None:
            yield self._start_event(state="generating_answer")
        else:
            yield ConversationEvent(
                event=ConversationEventType.STATUS,
                data={"request_id": self.request_id, "state": "generating_answer"},
            )
        hidden_policy = self._presentation_policy.model_copy(
            update={"visibility": ThinkingVisibility.HIDDEN}
        )
        original = yield from self._run_stage(
            request=self._request,
            presentation=self._presentation.start_stream(hidden_policy),
            emit_deltas=False,
        )
        if original.cancelled or self._cancel_requested.is_set():
            yield self._cancelled_event()
            return

        yield ConversationEvent(
            event=ConversationEventType.STATUS,
            data={"request_id": self.request_id, "state": "summarizing_answer"},
        )
        if not original.final_content.strip():
            yield from self._summary_fallback_events(original)
            return
        if self._cancel_requested.is_set():
            yield self._cancelled_event()
            return

        summary: _StageResult | None = None
        try:
            summary = yield from self._run_stage(
                request=self._build_summary_request(original.final_content),
                presentation=self._presentation.start_stream(hidden_policy),
                emit_deltas=False,
            )
        except Exception:
            summary = None

        if self._cancel_requested.is_set() or (summary is not None and summary.cancelled):
            yield self._cancelled_event()
            return
        if not self._valid_summary(summary):
            yield from self._summary_fallback_events(original)
            return

        assert summary is not None
        yield self._delta_event(
            summary.final_content,
            channel=ConversationDeltaChannel.FINAL,
        )
        yield from self._warning_events(original.warnings)
        yield self._completed_event(
            presented=summary,
            original=original,
            summary=summary,
            include_summary_metadata=True,
        )

    def _run_stage(
        self,
        *,
        request: GenerationRequest,
        presentation: ThinkingPresentationSession,
        emit_deltas: bool,
    ) -> Generator[ConversationEvent, None, _StageResult]:
        if self._cancel_requested.is_set():
            return _StageResult(cancelled=True)

        # Phase 5 `guardrail.stream_candidate` (ADR-5-006): only wired for
        # the genuinely incremental path (`emit_deltas=True`) — the
        # Summary-mode Stages (`emit_deltas=False`) never Delta-emit
        # anything live during generation at all, so there is nothing for
        # a Stream Guard to intercept there; Summary Mode's own single
        # one-shot Delta is unchanged Phase 4/Existing behavior, not
        # rewired here (P5-0-WU-002 Additive, non-invasive scope).
        #
        # P5-CODEX-009 Rework (Codex Second Independent Review item 3):
        # FINAL and REASONING each get their *own* fresh Scanner instance
        # — never shared across Turns/Tabs (architecture §10, P5-ACC-022)
        # *and never shared across Channels either*, since a Holdback
        # flush released mid-Channel-transition would otherwise get
        # mis-tagged with whichever Channel happened to trigger the
        # release. `reasoning_stream_guard` only ever actually receives a
        # `feed()` call when `ThinkingVisibility` is `VISIBLE` — Hidden
        # Reasoning is filtered out of `semantic_deltas` upstream by
        # `ThinkingPresentationSession._visible_semantic_deltas()` before
        # this method ever sees it, so the previous unconditional
        # `kind is ThinkingContentKind.REASONING` exemption below used to
        # exempt Reasoning from scanning *precisely and only* when it was
        # actually reaching a real client — the exact leak Codex's Second
        # Review flagged (Secret/PII inside Visible Thinking streamed
        # ungoverned in every Mode, including `enforce`).
        stream_guard: GuardrailStreamGuardLike | None = (
            self._guardrail_stream_guard_factory()
            if emit_deltas and self._guardrail_stream_guard_factory is not None
            else None
        )
        reasoning_stream_guard: GuardrailStreamGuardLike | None = (
            self._guardrail_stream_guard_factory()
            if emit_deltas and self._guardrail_stream_guard_factory is not None
            else None
        )

        def _emit_guarded(
            kind: ThinkingContentKind, text_delta: str
        ) -> tuple[ConversationEvent | None, str | None]:
            """Returns `(event_or_none, guard_reject_reason_or_none)` for
            one Semantic Segment. Any Segment when no Stream Guard is
            active passes through unchanged (byte-identical to the
            pre-Phase-5 behavior, P5-ACC-004)."""
            guard = (
                reasoning_stream_guard if kind is ThinkingContentKind.REASONING else stream_guard
            )
            if guard is None:
                return (self._segment_delta_event(kind, text_delta) if text_delta else None, None)
            decision = guard.feed(text_delta)
            if decision.terminated:
                return None, decision.reason_code or "unknown"
            if decision.safe_release:
                return self._segment_delta_event(kind, decision.safe_release), None
            return None, None

        finish_reason: FinishReason | None = None
        usage: TokenUsage | None = None
        stream = self._inference.stream(request)
        with self._stream_lock:
            self._active_stream = stream
        try:
            with stream:
                for chunk in stream:
                    if self._cancel_requested.is_set():
                        stream.cancel()
                        return _StageResult(cancelled=True)
                    if chunk.is_final:
                        finish_reason = chunk.finish_reason
                        usage = chunk.usage
                    presentation_delta = presentation.feed_presentation(chunk.text_delta)
                    for segment in presentation_delta.semantic_deltas:
                        if not emit_deltas:
                            continue
                        event, reject_reason = _emit_guarded(segment.kind, segment.text_delta)
                        if reject_reason is not None:
                            stream.cancel()
                            return _StageResult(
                                guardrail_stream_rejected=True,
                                guardrail_stream_reason_code=reject_reason,
                            )
                        if event is not None:
                            yield event

                if self._cancel_requested.is_set() or finish_reason is FinishReason.CANCELLED:
                    stream.cancel()
                    return _StageResult(cancelled=True)

                terminal = presentation.finish()
                if emit_deltas:
                    for segment in terminal.semantic_deltas:
                        event, reject_reason = _emit_guarded(segment.kind, segment.text_delta)
                        if reject_reason is not None:
                            return _StageResult(
                                guardrail_stream_rejected=True,
                                guardrail_stream_reason_code=reject_reason,
                            )
                        if event is not None:
                            yield event
                    if reasoning_stream_guard is not None:
                        reasoning_final_decision = reasoning_stream_guard.finalize()
                        if reasoning_final_decision.terminated:
                            reason_code = reasoning_final_decision.reason_code or "unknown"
                            return _StageResult(
                                guardrail_stream_rejected=True,
                                guardrail_stream_reason_code=reason_code,
                            )
                        if reasoning_final_decision.safe_release:
                            yield self._delta_event(
                                reasoning_final_decision.safe_release,
                                channel=ConversationDeltaChannel.REASONING,
                            )
                    if stream_guard is not None:
                        final_decision = stream_guard.finalize()
                        if final_decision.terminated:
                            reason_code = final_decision.reason_code or "unknown"
                            return _StageResult(
                                guardrail_stream_rejected=True,
                                guardrail_stream_reason_code=reason_code,
                            )
                        if final_decision.safe_release:
                            yield self._delta_event(
                                final_decision.safe_release, channel=ConversationDeltaChannel.FINAL
                            )
                normalized = terminal.presented.normalized
                warnings = list(normalized.warnings)
                if finish_reason is FinishReason.LENGTH and not normalized.final_content.strip():
                    warnings.append(
                        ThinkingParseWarning(
                            code="final_answer_token_limit",
                            safe_message=TOKEN_LIMIT_WARNING,
                        )
                    )
                return _StageResult(
                    finish_reason=finish_reason,
                    usage=usage,
                    final_content=normalized.final_content,
                    display_content=terminal.presented.display_content,
                    parse_status=normalized.parse_status,
                    warnings=tuple(warnings),
                )
        finally:
            with self._stream_lock:
                if self._active_stream is stream:
                    self._active_stream = None
            # P5-CODEX-009 Rework: report the Stage's Terminal Stream
            # Guard Summary exactly once, regardless of which `return`
            # path above was taken (Cancel, genuine Reject, or normal
            # completion) — combines FINAL and REASONING's independent
            # Guards into the single `guardrail.stream_candidate` Point
            # a Status/Evidence consumer already reads.
            if self._guardrail_stream_result_hook is not None:
                combined = _combine_stream_summaries(
                    (
                        stream_guard.summary() if stream_guard is not None else None,
                        reasoning_stream_guard.summary()
                        if reasoning_stream_guard is not None
                        else None,
                    )
                )
                if combined is not None:
                    try:
                        self._guardrail_stream_result_hook(combined)
                    except Exception:
                        pass

    def _build_summary_request(self, original_answer: str) -> GenerationRequest:
        assert self._request is not None
        return GenerationRequest(
            request_id=f"{self.request_id}:summary",
            model_key=self._request.model_key,
            messages=compose_summary_messages(
                original_answer=original_answer,
                response_language=self._response_language,
            ),
            parameters=self._request.parameters.model_copy(
                update={
                    "max_new_tokens": self._summarization.max_new_tokens,
                    "thinking_mode": ThinkingMode.DISABLED,
                }
            ),
        )

    @staticmethod
    def _valid_summary(summary: _StageResult | None) -> bool:
        return bool(
            summary is not None
            and summary.finish_reason is FinishReason.STOP
            and summary.parse_status
            in {ThinkingParseStatus.PLAIN_TEXT, ThinkingParseStatus.COMPLETE}
            and summary.final_content.strip()
        )

    def _summary_fallback_events(
        self,
        original: _StageResult,
    ) -> Generator[ConversationEvent, None, None]:
        if original.final_content:
            yield self._delta_event(
                original.final_content,
                channel=ConversationDeltaChannel.FINAL,
            )
        yield from self._warning_events(original.warnings)
        yield ConversationEvent(
            event=ConversationEventType.WARNING,
            data={
                "request_id": self.request_id,
                "code": "summary_fallback_original",
                "message": SUMMARY_FALLBACK_WARNING,
            },
        )
        yield self._completed_event(
            presented=original,
            original=original,
            summary=None,
            include_summary_metadata=True,
        )

    def _start_event(self, *, state: str) -> ConversationEvent:
        return ConversationEvent(
            event=ConversationEventType.START,
            data={"request_id": self.request_id, "state": state},
        )

    def _status_event(self, *, state: str) -> ConversationEvent:
        return ConversationEvent(
            event=ConversationEventType.STATUS,
            data={"request_id": self.request_id, "state": state},
        )

    def _segment_delta_event(
        self,
        kind: ThinkingContentKind,
        text: str,
    ) -> ConversationEvent:
        channel = (
            ConversationDeltaChannel.REASONING
            if kind is ThinkingContentKind.REASONING
            else ConversationDeltaChannel.FINAL
        )
        return self._delta_event(text, channel=channel)

    def _delta_event(
        self,
        text: str,
        *,
        channel: ConversationDeltaChannel,
    ) -> ConversationEvent:
        return ConversationEvent(
            event=ConversationEventType.DELTA,
            data={
                "request_id": self.request_id,
                "channel": channel.value,
                "text": text,
            },
        )

    def _warning_events(
        self,
        warnings: tuple[ThinkingParseWarning, ...],
    ) -> Generator[ConversationEvent, None, None]:
        for warning in warnings:
            yield ConversationEvent(
                event=ConversationEventType.WARNING,
                data={
                    "request_id": self.request_id,
                    "code": warning.code,
                    "message": warning.safe_message,
                },
            )

    def _completed_event(
        self,
        *,
        presented: _StageResult,
        original: _StageResult,
        summary: _StageResult | None,
        include_summary_metadata: bool,
    ) -> ConversationEvent:
        rejection = self._governance_post_check(presented.final_content)
        if rejection is not None:
            return rejection
        guardrail_rejection = self._guardrail_post_check(presented.final_content)
        if guardrail_rejection is not None:
            return guardrail_rejection
        data: dict[str, object] = {
            "request_id": self.request_id,
            "finish_reason": (
                presented.finish_reason.value if presented.finish_reason is not None else "unknown"
            ),
            "assistant_message": {
                "role": "assistant",
                "content": presented.final_content,
            },
            "usage": (
                presented.usage.model_dump(mode="json") if presented.usage is not None else None
            ),
            "context_usage": self._context_usage(original),
        }
        if self._model_runtime_info is not None:
            # P6-CODEX-013: the real Model/Backend/Artifact/Context identity
            # this specific Generation Attempt actually ran with — read here
            # (once, per completed Attempt) so a Persistent caller can carry
            # it onto the completed Turn record itself, not just correlate
            # by request_id to an ephemeral runtime snapshot.
            data["attempt_provenance"] = {
                "model_identity": self._model_runtime_info.model_key,
                "backend_key": self._model_runtime_info.backend_key,
                "backend_version": self._model_runtime_info.backend_version,
                "artifact_digest_sha512": self._model_runtime_info.artifact_digest.value,
                "context_size": self._effective_context_size,
                # P6-CODEX-023: the actually-applied Generation Parameters
                # for this specific Attempt, canonicalized and digested —
                # `ConversationTurnProvenance.generation_config_digest_
                # sha512` exists on the domain model but was never actually
                # populated here, so P6-ACC-008's "Generation Config Digest
                # persisted" claim was not true until this field is
                # threaded through to the caller that builds the Turn
                # Provenance (see `PersistentConversationService`).
                "generation_config_digest_sha512": self._generation_config_digest_sha512(),
            }
        if include_summary_metadata:
            data.update(
                {
                    "transformation": {
                        "summary_mode": SummaryMode.POST_GENERATION.value,
                        "summary_applied": summary is not None,
                        "fallback_used": summary is None,
                        "original_finish_reason": (
                            original.finish_reason.value
                            if original.finish_reason is not None
                            else None
                        ),
                        "summary_finish_reason": (
                            summary.finish_reason.value
                            if summary is not None and summary.finish_reason is not None
                            else None
                        ),
                    },
                }
            )
        if self._documentation_augmentation is not None:
            augmentation = self._documentation_augmentation
            data["documentation_retrieval"] = {
                "state": augmentation.state.value,
                "citations": [
                    citation.model_dump(mode="json") for citation in augmentation.citations
                ],
                "index_rebuilt": augmentation.index_rebuilt,
                "warnings": [warning.model_dump(mode="json") for warning in augmentation.warnings],
            }
        # P6-CODEX-012 (Second Rework, real-hardware finding): this Turn's
        # own Model Access Coordinator "main" slot must be released *before*
        # the Judge Hook below tries to acquire a "background" slot for it —
        # `events()`'s own `finally: self._release()` does not run until
        # this whole generator is exhausted, which is *after* this method
        # returns its single COMPLETED event, by which point
        # `_invoke_judge_completion_hook()` has already called
        # `start_background()`. Without releasing here first,
        # `start_background()` always saw this Turn's own still-held "main"
        # slot and returned `False` — Judge silently never ran, for any
        # Mode, on every real Turn (caught via a real Browser + real model
        # Golden Path check, not by any Fake-Inference unit test, since
        # those call the Hook directly and never exercise this exact
        # release-timing relationship). Calling `_release()` again in
        # `events()`'s `finally` afterward is a safe, idempotent no-op.
        self._release()
        # Recording (P6-CODEX-011): independent of Judge Mode entirely —
        # invoked here unconditionally (the Hook itself checks Recording
        # Mode and no-ops on OFF), never gated on whether Judge ran at all.
        # Placed before the Judge Hook call below only for stable read
        # order; the two never contend (Recording is pure local file I/O,
        # never the shared Model Backend lock Judge/Repair need).
        self._invoke_recording_completion_hook(presented.final_content)
        # Deliberately last (P6-CODEX-006/007 real-hardware finding): this
        # method's own `_context_usage()` call above may itself need the
        # shared Model Backend's single generation lock (via
        # `_text_token_counter`) when the Turn includes a System/RAG
        # Reference message. Spawning the Judge Thread any earlier in this
        # method raced that same-Turn token count against the
        # just-started background Judge call — a self-collision, not a
        # cross-Turn one — and could turn a successful completion into a
        # spurious model_busy error. Calling this last means every other
        # use of the shared lock for *this* Turn has already finished.
        self._invoke_judge_completion_hook(presented.final_content)
        return ConversationEvent(event=ConversationEventType.COMPLETED, data=data)

    def _generation_config_digest_sha512(self) -> str | None:
        """P6-CODEX-023: a canonical SHA-512 of the `GenerationParameters`
        this Attempt actually ran with (`self._request.parameters`), so a
        later Config change is verifiably visible on the next Attempt's own
        Digest rather than only assumed. `None` (never a fabricated
        placeholder) only in the narrow case `self._request` itself is
        `None` — a state `_completed_event()`'s existing `assert self.
        _request is not None` call sites elsewhere in this class show does
        not occur once generation has actually completed, but this method
        stays defensive rather than asserting."""
        if self._request is None:
            return None
        payload = self._request.parameters.model_dump(mode="json")
        return hashlib.sha512(
            json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()

    def _context_usage(self, original: _StageResult) -> dict[str, object] | None:
        """Low-cost, approximate context-window occupancy for the turn just answered.

        Uses `original` (the real conversation request/response), not `presented`
        (which, under summary mode, reflects a much smaller summarization
        sub-request and would misrepresent context occupancy).
        """

        if original.usage is None:
            return None
        prompt_tokens = original.usage.prompt_tokens
        completion_tokens = original.usage.completion_tokens
        total_tokens = original.usage.total_tokens
        system_prompt_tokens = 0
        rag_context_tokens = 0
        if self._text_token_counter is not None and self._request is not None:
            try:
                for message in self._request.messages:
                    # P5-CODEX-006 Rework: the RAG Reference Message no
                    # longer carries `MessageRole.SYSTEM` (see
                    # `ConversationGenerationService._inject_documentation_
                    # reference` below) — matched by `name` alone here so
                    # this split stays correct regardless of which Role it
                    # is actually spliced in under.
                    if message.name == DOCUMENTATION_REFERENCE_MESSAGE_NAME:
                        rag_context_tokens += self._text_token_counter(message.content)
                        continue
                    if message.role is not MessageRole.SYSTEM:
                        continue
                    system_prompt_tokens += self._text_token_counter(message.content)
            except Exception:
                # Defense in depth (P6-CODEX-006/007): the shared Model
                # Backend's token counter can transiently raise (e.g.
                # model_busy) if something else is briefly using the same
                # generation lock. This estimate degrades to 0 for the
                # System/RAG portion rather than failing the whole
                # already-succeeded completion.
                system_prompt_tokens = 0
                rag_context_tokens = 0
        conversation_history_tokens = max(
            0, prompt_tokens - system_prompt_tokens - rag_context_tokens
        )
        free_tokens = max(0, self._effective_context_size - total_tokens)
        usage_ratio = (
            min(1.0, total_tokens / self._effective_context_size)
            if self._effective_context_size > 0
            else 0.0
        )
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "loaded_context_size": self._effective_context_size,
            "usage_ratio": usage_ratio,
            "breakdown": {
                "conversation_history_tokens": conversation_history_tokens,
                "system_prompt_tokens": system_prompt_tokens,
                "rag_context_tokens": rag_context_tokens,
                "free_tokens": free_tokens,
            },
        }

    def _retrieval_event(
        self,
        augmentation: DocumentationAugmentation,
    ) -> ConversationEvent:
        return ConversationEvent(
            event=ConversationEventType.RETRIEVAL,
            data={
                "request_id": self.request_id,
                "state": augmentation.state.value,
                "citations": [
                    citation.model_dump(mode="json") for citation in augmentation.citations
                ],
                "document_count": augmentation.document_count,
                "selected_chunk_count": augmentation.selected_chunk_count,
                "index_rebuilt": augmentation.index_rebuilt,
                "duration_ms": augmentation.duration_ms,
                "warnings": [warning.model_dump(mode="json") for warning in augmentation.warnings],
            },
        )

    def _cancelled_event(self) -> ConversationEvent:
        return ConversationEvent(
            event=ConversationEventType.CANCELLED,
            data={"request_id": self.request_id, "state": "cancelled"},
        )

    def _governance_pre_check(self) -> ConversationEvent | None:
        """`main_model.pre` Enforce gate (P4-PNT-006, P4-MOD-002): only
        called before the first event of this generation is ever
        yielded, so a Stop decision here means `_run_stage`/the Model
        Port's `.stream()` is never reached at all — zero Model Call."""

        if self._governance_pre_hook is None:
            return None
        assert self._request is not None
        try:
            should_stop, reason_code = self._governance_pre_hook(self._request)
        except Exception:
            return None
        if not should_stop:
            return None
        return self._error_event(
            code=reason_code or "governance_stopped",
            message="Generation was stopped by Runtime Governance before starting.",
            retryable=False,
        )

    def _governance_post_check(self, content: str) -> ConversationEvent | None:
        """`main_model.post` Enforce gate (P4-COM-006/007): called from
        inside `_completed_event()`, so a Reject decision here means the
        Canonical `completed` event carrying `content` is never
        constructed or yielded — every consumer (SSE forwarder, Persistent
        commit-and-project) instead sees the same `error` event this
        module already emits for any other generation failure, so no new
        Event Shape and no Ghost Completion is ever produced."""

        if self._governance_post_hook is None:
            return None
        try:
            should_reject, reason_code = self._governance_post_hook(content)
        except Exception:
            return None
        if not should_reject:
            return None
        return self._error_event(
            code=reason_code or "governance_rejected",
            message="The generated response was rejected by Runtime Governance.",
            retryable=False,
        )

    def _guardrail_pre_check(self) -> ConversationEvent | None:
        """`guardrail.input` Enforce gate (P5-PNT-002, P5-MOD-002).
        Evaluated *before* `_governance_pre_check()` — Security is a
        higher-priority Boundary than reasoning-quality Governance, and
        rejecting untrusted Input before it is ever forwarded to Phase 4
        is the cheapest possible Fail-closed Stop. Zero Model Call either
        way, exactly like the Governance gate above."""

        if self._guardrail_pre_hook is None:
            return None
        assert self._request is not None
        try:
            should_stop, reason_code = self._guardrail_pre_hook(self._request)
        except Exception:
            return None
        if not should_stop:
            return None
        return self._error_event(
            code=reason_code or "guardrail_stopped",
            message="Generation was stopped by the Guardrail before starting.",
            retryable=False,
        )

    def _guardrail_post_check(self, content: str) -> ConversationEvent | None:
        """`guardrail.output_candidate` Enforce gate (P5-PNT-004,
        architecture §6.3 Terminal order). Evaluated *after*
        `_governance_post_check()` in `_completed_event()` — Phase 5
        Security is the last gate before an Assistant Message ever
        commits, so a Governance Allow can never override a Guardrail
        Deny (ADR-5-001/§7 "Main Governance Allowで Safety Denyが解除されない")."""

        if self._guardrail_post_hook is None:
            return None
        try:
            should_reject, reason_code = self._guardrail_post_hook(content)
        except Exception:
            return None
        if not should_reject:
            return None
        return self._error_event(
            code=reason_code or "guardrail_rejected",
            message="The generated response was rejected by the Guardrail.",
            retryable=False,
        )

    def _invoke_judge_completion_hook(self, assistant_content: str) -> None:
        """Called from `_completed_event()` only after both Post-checks
        Allowed the content (P6-CODEX-001) — a mode-OFF check and the actual
        Model Call are entirely the Hook implementation's own concern (kept
        out of Core, same decoupling as Governance/Guardrail). A raised
        exception is swallowed exactly like every other Hook here."""

        if self._judge_completion_hook is None:
            return
        assert self._request is not None
        user_input = next(
            (
                message.content
                for message in reversed(self._request.messages)
                if message.role is MessageRole.USER
            ),
            "",
        )
        try:
            self._judge_completion_hook(
                JudgeCompletionContext(
                    request_id=self.request_id,
                    user_input=user_input,
                    assistant_content=assistant_content,
                    model_key=self._request.model_key,
                    model_runtime_info=self._model_runtime_info,
                )
            )
        except Exception:
            return

    def _invoke_recording_completion_hook(self, assistant_content: str) -> None:
        """Called from `_completed_event()` unconditionally (P6-CODEX-011:
        Mode orthogonality — Recording must never depend on Judge Mode). A
        raised exception is swallowed exactly like every other Hook here; a
        Recording bug must never break the core conversation feature."""

        if self._recording_completion_hook is None:
            return
        assert self._request is not None
        user_input = next(
            (
                message.content
                for message in reversed(self._request.messages)
                if message.role is MessageRole.USER
            ),
            "",
        )
        try:
            self._recording_completion_hook(
                JudgeCompletionContext(
                    request_id=self.request_id,
                    user_input=user_input,
                    assistant_content=assistant_content,
                    model_key=self._request.model_key,
                    model_runtime_info=self._model_runtime_info,
                )
            )
        except Exception:
            return

    def _guardrail_context_source_check(
        self, augmentation: DocumentationAugmentation
    ) -> ConversationEvent | None:
        """`guardrail.context_source` Enforce gate (P5-CODEX-001 Rework,
        P5-CODEX-006 Rework, P5-PNT-001/003, architecture Point/Action
        Matrix "context_source: exclude/reject only if explicit
        policy/authority"). Evaluated once RAG retrieval has produced
        real Reference content but *before*
        `_documentation_request_factory()` ever splices any of it into
        `GenerationRequest.messages` — a genuine Stop here means the
        retrieved Reference Content never reaches the Model at all (Model
        Call 0), and it is never promoted to the same Instruction
        Authority a real System Prompt carries (P5-ACC-007) — each Source
        is judged on its own content, never a single joined string
        (P5-CODEX-006)."""

        if self._guardrail_context_source_hook is None:
            return None
        sources = _context_source_items(augmentation)
        if not sources:
            return None
        try:
            should_stop, reason_code = self._guardrail_context_source_hook(sources)
        except Exception:
            return None
        if not should_stop:
            return None
        return self._error_event(
            code=reason_code or "guardrail_context_source_rejected",
            message=(
                "Generation was stopped because retrieved reference content "
                "failed a Guardrail Security check."
            ),
            retryable=False,
        )

    def _error_event(self, *, code: str, message: str, retryable: bool) -> ConversationEvent:
        return ConversationEvent(
            event=ConversationEventType.ERROR,
            data={
                "request_id": self.request_id,
                "code": code,
                "message": message,
                "retryable": retryable,
            },
        )


@dataclass(frozen=True, slots=True)
class RuntimeGenerationSnapshot:
    """The exact Model/Generation state one Attempt should Freeze at Main
    Turn start (P6-CODEX-025, Fourth Rework). Before this existed,
    `ConversationGenerationService` cached `model_key`/`generation_defaults`/
    `effective_context_size`/`model_runtime_info` once at bootstrap and
    never re-read them — so a Runtime Model Switch or a Max New Tokens/
    Context Size change made via `RuntimeModelController` never reached
    Chat, Judge, Repair, or Recording at all (they kept building Requests
    against the *original* Model Key, causing `InferenceService.
    _validate_request()`'s `model_key != runtime_info.model_key` check to
    reject every Generation the moment the real Adapter had actually
    switched models).

    A caller with a live `RuntimeModelController` supplies a
    `RuntimeGenerationSnapshotProvider` that reads its *current* Snapshot;
    a caller without one (most existing tests, and any deployment without
    Runtime Model Control enabled) needs no changes — `ConversationGeneration
    Service` falls back to its own bootstrap-time constants, exactly as
    before this Rework."""

    model_key: str
    generation_defaults: GenerationParameters
    effective_context_size: int
    model_runtime_info: ModelRuntimeInfo | None


RuntimeGenerationSnapshotProvider = Callable[[], RuntimeGenerationSnapshot]


class ConversationGenerationService:
    def __init__(
        self,
        *,
        inference: ConversationInference,
        presentation: ThinkingPresentationService,
        model_key: str,
        generation_defaults: GenerationParameters,
        response_language_default: ResponseLanguage,
        presentation_default: ResolvedThinkingPresentationPolicy,
        summarization: SummarizationConfig | None = None,
        thinking_control_available: bool = True,
        documentation_rag: RagOrchestratorPort | ContextualRagOrchestratorPort | None = None,
        documentation_rag_availability: DocumentationRagAvailability = (
            DocumentationRagAvailability.UNAVAILABLE
        ),
        chat_prompt_token_counter: ChatPromptTokenCounter | None = None,
        text_token_counter: TextTokenCounter | None = None,
        effective_context_size: int = 4096,
        model_runtime_info: ModelRuntimeInfo | None = None,
        governance_pre_hook: GovernancePreHook | None = None,
        governance_post_hook: GovernancePostHook | None = None,
        guardrail_pre_hook: GuardrailPreHook | None = None,
        guardrail_post_hook: GuardrailPostHook | None = None,
        guardrail_stream_guard_factory: GuardrailStreamGuardFactory | None = None,
        guardrail_context_source_hook: GuardrailContextSourceHook | None = None,
        guardrail_stream_result_hook: GuardrailStreamResultHook | None = None,
        judge_completion_hook: JudgeCompletionHook | None = None,
        recording_completion_hook: RecordingCompletionHook | None = None,
        model_access_coordinator: ModelAccessCoordinator | None = None,
        runtime_snapshot_provider: RuntimeGenerationSnapshotProvider | None = None,
    ) -> None:
        self._inference = inference
        self._presentation = presentation
        self._model_key = model_key
        self._generation_defaults = generation_defaults
        self._runtime_snapshot_provider = runtime_snapshot_provider
        self._response_language_default = response_language_default
        self._presentation_default = presentation_default
        self._summarization = summarization or SummarizationConfig()
        self._thinking_control_available = thinking_control_available
        self._documentation_rag = documentation_rag
        self._documentation_rag_availability = documentation_rag_availability
        self._chat_prompt_token_counter = chat_prompt_token_counter
        self._text_token_counter = text_token_counter
        if isinstance(effective_context_size, bool) or effective_context_size <= 0:
            raise ValueError("effective context size must be a positive integer")
        self._effective_context_size = effective_context_size
        self._model_runtime_info = model_runtime_info
        self._governance_pre_hook = governance_pre_hook
        self._governance_post_hook = governance_post_hook
        self._guardrail_pre_hook = guardrail_pre_hook
        self._guardrail_post_hook = guardrail_post_hook
        self._guardrail_stream_guard_factory = guardrail_stream_guard_factory
        self._guardrail_context_source_hook = guardrail_context_source_hook
        self._guardrail_stream_result_hook = guardrail_stream_result_hook
        self._judge_completion_hook = judge_completion_hook
        self._recording_completion_hook = recording_completion_hook
        self._model_access_coordinator = model_access_coordinator or ModelAccessCoordinator()
        self._active_lock = threading.Lock()
        self._active: ConversationGenerationSession | None = None

    @property
    def model_access_coordinator(self) -> ModelAccessCoordinator:
        return self._model_access_coordinator

    @property
    def active_request_id(self) -> str | None:
        with self._active_lock:
            return self._active.request_id if self._active is not None else None

    def start(self, value: ConversationGenerationInput) -> ConversationGenerationSession:
        if (
            value.settings.thinking_mode is ThinkingMode.ENABLED
            and not self._thinking_control_available
        ):
            raise InferenceError(
                code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
                safe_message="Thinking generation control is unavailable for this model.",
            )
        if value.settings.documentation_rag_mode is DocumentationRagMode.ENABLED:
            if self._documentation_rag_availability is DocumentationRagAvailability.DENIED:
                raise InferenceError(
                    code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
                    safe_message="Documentation RAG is denied by this access profile.",
                )
            if (
                self._documentation_rag_availability is not DocumentationRagAvailability.AVAILABLE
                or self._documentation_rag is None
            ):
                raise InferenceError(
                    code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
                    safe_message="Documentation RAG is unavailable in this runtime.",
                )
        request_id = str(uuid4())
        # P6-CODEX-025 (Fourth Rework): resolved exactly once per Attempt,
        # here at Main Turn start — never re-read mid-Attempt (Requirements
        # "実行中Attemptの途中で値を変えない"). Every downstream consumer of
        # Model Key/Generation Defaults/Context Size/Runtime Info for *this*
        # Attempt (the initial Request, a later RAG-augmented rebuild of the
        # same Attempt, the Session's Context-usage accounting, and the
        # Judge/Repair/Recording Hooks via `JudgeCompletionContext`) reads
        # this one frozen `runtime_snapshot`, never `self._model_key` et al.
        # directly and never a fresh independent read of whatever Runtime
        # Model Control reports "now".
        runtime_snapshot = self._resolve_runtime_snapshot()
        # P6-CODEX-010 (Second Rework): Main Turns take Priority over any
        # Background (Judge/Repair) Task already using the shared Model
        # Backend — acquire_main() waits briefly (bounded) for a
        # Background Task to finish rather than failing immediately, but
        # still fails fast for a genuine Main-vs-Main conflict (e.g. two
        # browser tabs), matching the pre-existing tested contract.
        self._model_access_coordinator.acquire_main(task_id=request_id)
        try:
            documentation_enabled = (
                value.settings.documentation_rag_mode is DocumentationRagMode.ENABLED
            )
            request = (
                None
                if documentation_enabled
                else self._build_request(
                    value,
                    request_id=request_id,
                    augmentation=None,
                    runtime_snapshot=runtime_snapshot,
                )
            )
            policy = self._presentation_default.model_copy(
                update={
                    "visibility": (
                        value.settings.thinking_visibility
                        if value.settings.thinking_mode is ThinkingMode.ENABLED
                        else ThinkingVisibility.HIDDEN
                    )
                }
            )
            session = ConversationGenerationSession(
                request_id=request_id,
                request=request,
                inference=self._inference,
                presentation=self._presentation,
                presentation_policy=policy,
                summarization=self._summarization,
                summary_mode=value.settings.summary_mode,
                response_language=value.settings.response_language,
                documentation_augmentation=None,
                documentation_rag=(self._documentation_rag if documentation_enabled else None),
                documentation_query=(value.messages[-1].content if documentation_enabled else None),
                documentation_request_context=(
                    self._build_documentation_request_context(
                        value, runtime_snapshot=runtime_snapshot
                    )
                    if documentation_enabled
                    else None
                ),
                documentation_request_factory=(
                    (
                        lambda augmentation: self._build_request(
                            value,
                            request_id=request_id,
                            augmentation=augmentation,
                            runtime_snapshot=runtime_snapshot,
                        )
                    )
                    if documentation_enabled
                    else None
                ),
                text_token_counter=self._text_token_counter,
                effective_context_size=runtime_snapshot.effective_context_size,
                model_runtime_info=runtime_snapshot.model_runtime_info,
                release=lambda: self._release(request_id),
                governance_pre_hook=self._governance_pre_hook,
                governance_post_hook=self._governance_post_hook,
                guardrail_pre_hook=self._guardrail_pre_hook,
                guardrail_post_hook=self._guardrail_post_hook,
                guardrail_stream_guard_factory=self._guardrail_stream_guard_factory,
                guardrail_context_source_hook=self._guardrail_context_source_hook,
                guardrail_stream_result_hook=self._guardrail_stream_result_hook,
                judge_completion_hook=self._judge_completion_hook,
                recording_completion_hook=self._recording_completion_hook,
            )
            with self._active_lock:
                self._active = session
            return session
        except BaseException:
            self._model_access_coordinator.release_main(task_id=request_id)
            raise

    def cancel(self, request_id: str) -> bool:
        with self._active_lock:
            session = self._active
            if session is None or session.request_id != request_id:
                return False
            session.request_cancel()
            return True

    def shutdown(self, timeout: float = 10.0) -> bool:
        with self._active_lock:
            session = self._active
        if session is None:
            return True
        session.request_cancel()
        return session.wait(timeout)

    def _resolve_runtime_snapshot(self) -> RuntimeGenerationSnapshot:
        """P6-CODEX-025: the single call site that decides what "the
        current Model/Generation state" means for a new Attempt. A live
        `runtime_snapshot_provider` (wired to `RuntimeModelController` in
        production) is authoritative when present; the bootstrap-time
        constants remain the fallback for callers that never wire one
        (e.g. most existing unit tests, or a deployment with Runtime Model
        Control disabled) — behaviorally identical to this class before
        P6-CODEX-025."""
        if self._runtime_snapshot_provider is not None:
            return self._runtime_snapshot_provider()
        return RuntimeGenerationSnapshot(
            model_key=self._model_key,
            generation_defaults=self._generation_defaults,
            effective_context_size=self._effective_context_size,
            model_runtime_info=self._model_runtime_info,
        )

    def _build_request(
        self,
        value: ConversationGenerationInput,
        *,
        request_id: str,
        augmentation: DocumentationAugmentation | None,
        runtime_snapshot: RuntimeGenerationSnapshot,
    ) -> GenerationRequest:
        response_policy = ResolvedResponseLanguagePolicy(
            language=value.settings.response_language,
            source=ResponseLanguageSource.EXPLICIT,
        )
        composed_messages = compose_conversation_generation_messages(
            messages=value.messages,
            policy=response_policy,
        )
        messages = self._inject_documentation_reference(composed_messages, augmentation)
        if value.settings.expressive_mode is ExpressiveMode.ENABLED:
            messages = self._inject_expressive_style_notice(messages)
        if (
            value.settings.context_usage_prompt_injection_mode
            is ContextUsagePromptInjectionMode.ENABLED
            and self._chat_prompt_token_counter is not None
        ):
            try:
                prompt_tokens = self._chat_prompt_token_counter(
                    messages, value.settings.thinking_mode
                )
            except Exception:
                prompt_tokens = None
            if prompt_tokens is not None:
                messages = self._inject_context_usage_notice(
                    messages,
                    prompt_tokens=prompt_tokens,
                )
        # P6-CODEX-025 (Fourth Rework): Architecture 5.2's own formula is
        # `request_limit <= min(configured_limit, ...)` — the Runtime
        # Override (`runtime_snapshot.generation_defaults.max_new_tokens`,
        # sourced from `RuntimeModelController.current_max_new_tokens`) is
        # a real ceiling this Turn's own `value.settings.max_new_tokens`
        # can never exceed, not a value the Turn's own setting silently
        # replaces outright. Before this fix, the Turn's setting always
        # won verbatim regardless of the Runtime Override, so lowering
        # Max New Tokens via the Runtime Model Control surface had zero
        # observable effect on real Chat (the exact P6-CODEX-025 (1)
        # symptom) — a real-hardware Chat test with the override set to 5
        # tokens produced a full, unconstrained multi-paragraph answer
        # under the pre-fix code.
        effective_max_new_tokens = min(
            value.settings.max_new_tokens, runtime_snapshot.generation_defaults.max_new_tokens
        )
        parameters = runtime_snapshot.generation_defaults.model_copy(
            update={
                "max_new_tokens": effective_max_new_tokens,
                "thinking_mode": value.settings.thinking_mode,
            }
        )
        return GenerationRequest(
            request_id=request_id,
            model_key=runtime_snapshot.model_key,
            messages=messages,
            parameters=parameters,
        )

    def _build_documentation_request_context(
        self,
        value: ConversationGenerationInput,
        *,
        runtime_snapshot: RuntimeGenerationSnapshot,
    ) -> DocumentationRagRequestContext:
        response_policy = ResolvedResponseLanguagePolicy(
            language=value.settings.response_language,
            source=ResponseLanguageSource.EXPLICIT,
        )
        messages = compose_conversation_generation_messages(
            messages=value.messages,
            policy=response_policy,
        )
        prompt_tokens: int | None = None
        prompt_exact = False
        if self._chat_prompt_token_counter is not None:
            try:
                prompt_tokens = self._chat_prompt_token_counter(
                    messages,
                    value.settings.thinking_mode,
                )
                prompt_exact = True
            except Exception:
                prompt_tokens = None
        return DocumentationRagRequestContext(
            effective_context_size=runtime_snapshot.effective_context_size,
            requested_max_new_tokens=value.settings.max_new_tokens,
            system_history_current_prompt_tokens=prompt_tokens,
            prompt_measurement_unit=DocumentationMeasurementUnit.TOKENS,
            prompt_token_count_exact=prompt_exact,
        )

    @staticmethod
    def _inject_documentation_reference(
        messages: tuple[ChatMessage, ...],
        augmentation: DocumentationAugmentation | None,
    ) -> tuple[ChatMessage, ...]:
        """P5-CODEX-006 Rework (Codex Third Independent Review): the RAG
        Reference block is spliced in as `MessageRole.TOOL` — Codex's
        Second Review rejected `role=SYSTEM` (Codex's First Review) and
        then `role=USER` (Codex's Second Review, since both Retrieved
        content and the real human turn shared the identical Nominal
        Authority once both used `USER`) as insufficient. `TOOL` is a
        genuinely distinct third Role, semantically the correct one for
        externally-retrieved data a human never typed and the System
        Prompt never declared (P5-CODEX-006 Required Rework item 1/2:
        never merely a `name` Tag, natural-language Prefix, or Message
        order). `LlamaCppChatTemplate`'s `supported_message_roles` was
        extended to include `TOOL` for exactly this (`adapter.py`); the
        Role selection itself is read from `DocumentationReferenceBlock.
        source_class`/the flat-Legacy fallback's own declared Class via
        `_context_source_items()`/`_PROMPT_ROLE_BY_SOURCE_CLASS` below —
        never hard-coded independent of that Domain-level Class (item 3:
        the exact same typed `_ContextSourceItem` tuple the Guardrail
        check judged is what decides the Role here, not a second,
        independent guess). Placed *before* every real conversation
        message, so `LlamaCppChatTemplate._append_soft_switch()`'s
        backward walk for "the last `MessageRole.USER` message" still
        finds the genuine final User turn, unaffected either way since
        `TOOL != USER`."""

        if augmentation is None or augmentation.reference_message is None:
            return messages
        sources = _context_source_items(augmentation)
        source_class = (
            sources[0].source_class if sources else _DOCUMENTATION_RAG_LEGACY_FLAT_SOURCE_CLASS
        )
        role = _PROMPT_ROLE_BY_SOURCE_CLASS.get(source_class, MessageRole.TOOL)
        reference = ChatMessage(
            role=role,
            content=augmentation.reference_message,
            name=DOCUMENTATION_REFERENCE_MESSAGE_NAME,
        )
        if messages and messages[0].role is MessageRole.SYSTEM:
            return (messages[0], reference, *messages[1:])
        return (reference, *messages)

    @staticmethod
    def _inject_expressive_style_notice(
        messages: tuple[ChatMessage, ...],
    ) -> tuple[ChatMessage, ...]:
        notice = ChatMessage(
            role=MessageRole.SYSTEM,
            content=(
                "[表現Style指示] 以下は回答の言葉遣い・雰囲気にのみ適用される指示です。"
                "推論の正確性・結論・事実内容は、この指示が無い場合と全く同じ水準を保ってください。\n"
                "- ノリよく、テンション高めの口調にする。\n"
                "- 「www」「笑」等の砕けた笑いの表現を適度に使う。\n"
                "- 顔文字（例：(^ω^)、(´・ω・`)）を適宜使う。\n"  # noqa: RUF001
                "- 絵文字（😄、🎉、👍等）を積極的に使う。\n"  # noqa: RUF001
                "- ★や✨等の記号・アイコン的な装飾を適宜使う。\n"
                "- 全体として、親しみやすくCasualな雰囲気にする。"
            ),
            name=EXPRESSIVE_STYLE_NOTICE_MESSAGE_NAME,
        )
        if messages and messages[0].role is MessageRole.SYSTEM:
            return (messages[0], notice, *messages[1:])
        return (notice, *messages)

    def _inject_context_usage_notice(
        self,
        messages: tuple[ChatMessage, ...],
        *,
        prompt_tokens: int,
    ) -> tuple[ChatMessage, ...]:
        ratio = (
            min(1.0, prompt_tokens / self._effective_context_size)
            if self._effective_context_size > 0
            else 0.0
        )
        notice = ChatMessage(
            role=MessageRole.SYSTEM,
            content=(
                f"[Context使用状況] 現在のPrompt Token使用率は約{ratio:.0%}"
                f"({prompt_tokens}/{self._effective_context_size} tokens)です。"
                "ユーザーからContext使用率・残量について明示的に尋ねられた場合にのみ、"
                "この情報を用いて簡潔に回答してください。尋ねられていない場合は、"
                "この情報について自発的に言及しないでください。"
            ),
            name=CONTEXT_USAGE_NOTICE_MESSAGE_NAME,
        )
        if messages and messages[0].role is MessageRole.SYSTEM:
            return (messages[0], notice, *messages[1:])
        return (notice, *messages)

    def _release(self, request_id: str) -> None:
        with self._active_lock:
            if self._active is not None and self._active.request_id == request_id:
                self._active = None
        self._model_access_coordinator.release_main(task_id=request_id)
