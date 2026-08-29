"""Composition root for Phase 5 Guardrail/Security/Policy/Authority
Governance.

Additive to Phase 3/4 (P5-0-WU-002): this module never modifies
`runtime_governance`/`configuration_control`'s existing Phase 3/4 shape.
`GuardrailGovernanceComposition` holds every process-local component the
`guardrail.input`/`guardrail.output_candidate` Points and the Stream
Guard need. Policy/Authority/Action Registry are fixed local defaults
for this MVP (mirrors Phase 4's own `RuntimeGovernanceComposition`
docstring rationale) — a future Phase can make them
Configuration-driven without changing this module's external shape.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Protocol
from uuid import uuid4

from margpa_runtime_llm.adapters.guardrail_governance.deterministic_detectors import (
    build_input_detectors,
    build_output_detectors,
)
from margpa_runtime_llm.adapters.guardrail_governance.local_authority_provider import (
    LocalAuthorityProvider,
)
from margpa_runtime_llm.adapters.guardrail_governance.local_policy_provider import (
    LocalPolicyProvider,
)
from margpa_runtime_llm.adapters.guardrail_governance.qwen3guard_detector_adapter import (
    Qwen3GuardDetectorAdapter,
    Qwen3GuardRoleTurn,
)
from margpa_runtime_llm.adapters.guardrail_governance.registered_actions import (
    LocalGuardActionAdapter,
)
from margpa_runtime_llm.adapters.guardrail_governance.unavailable_approval_port import (
    UnavailableApprovalPort,
)
from margpa_runtime_llm.modules.guardrail_governance.application import (
    GuardrailModeController,
    GuardrailPointRuntime,
    IncrementalStreamGuard,
    NullStreamGuard,
    ObservingStreamGuard,
)
from margpa_runtime_llm.modules.guardrail_governance.domain import (
    CATEGORY_UNKNOWN_UNRESOLVED,
    GUARDRAIL_CONTEXT_SOURCE_POINT_ID,
    GUARDRAIL_INPUT_POINT_ID,
    GUARDRAIL_OUTPUT_CANDIDATE_POINT_ID,
    GUARDRAIL_STREAM_CANDIDATE_POINT_ID,
    ActionId,
    ActionRegistryEntry,
    ActionRegistrySnapshot,
    ContextSourceUnit,
    DetectionOutcome,
    DetectorRegistrySnapshot,
    ExecutedAction,
    ExecutionState,
    GuardDetection,
    GuardrailResult,
    Qwen3GuardTarget,
    Severity,
)
from margpa_runtime_llm.modules.guardrail_governance.ports import (
    ActionRegistryPort,
    AuthorityProviderPort,
    DetectorRegistryPort,
    GuardActionAdapterPort,
)

logger = logging.getLogger(__name__)

_VALID_MODES = frozenset({"off", "observe", "enforce"})


def _default_registry_entries() -> dict[str, ActionRegistryEntry]:
    return {
        ActionId.REJECT_INPUT.value: ActionRegistryEntry(
            action_id=ActionId.REJECT_INPUT,
            allowed_points=(GUARDRAIL_INPUT_POINT_ID,),
            side_effect_class="local",
        ),
        ActionId.REJECT_OUTPUT.value: ActionRegistryEntry(
            action_id=ActionId.REJECT_OUTPUT,
            allowed_points=(GUARDRAIL_OUTPUT_CANDIDATE_POINT_ID,),
            side_effect_class="local",
        ),
        ActionId.REDACT_TYPED_SECRET.value: ActionRegistryEntry(
            action_id=ActionId.REDACT_TYPED_SECRET,
            allowed_points=(GUARDRAIL_OUTPUT_CANDIDATE_POINT_ID,),
            side_effect_class="local",
        ),
        ActionId.REDACT_TYPED_PII.value: ActionRegistryEntry(
            action_id=ActionId.REDACT_TYPED_PII,
            allowed_points=(GUARDRAIL_OUTPUT_CANDIDATE_POINT_ID,),
            side_effect_class="local",
        ),
        ActionId.WARN.value: ActionRegistryEntry(
            action_id=ActionId.WARN,
            allowed_points=(GUARDRAIL_INPUT_POINT_ID, GUARDRAIL_OUTPUT_CANDIDATE_POINT_ID),
            side_effect_class="evidence_status_projection",
        ),
        ActionId.STOP_BEFORE_GENERATION.value: ActionRegistryEntry(
            action_id=ActionId.STOP_BEFORE_GENERATION,
            allowed_points=(GUARDRAIL_CONTEXT_SOURCE_POINT_ID,),
            side_effect_class="local",
        ),
    }


class _StreamGuardSummaryLike(Protocol):
    """Structural mirror of `conversation_generation.py`'s own
    `GuardrailStreamSummaryLike` Protocol (P5-CODEX-009 Rework) — a
    Stage may report either a plain `StreamGuardSummary` (one Channel)
    or that module's own `_CombinedStreamSummary` (two Channels
    combined); `record_stream_guard_summary()` below only ever reads
    these five fields, so it accepts anything satisfying this shape
    rather than being pinned to one concrete class."""

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


class _FixedDetectorRegistryProvider:
    """`DetectorRegistryPort` wrapping a fixed, process-lifetime
    `DetectorRegistrySnapshot` (P5-CODEX-007 Rework) — this MVP's
    Detector set never actually changes mid-process, but exposing it as
    a re-callable Port (rather than a bare digest string, as before)
    lets `GuardrailPointRuntime` perform a genuine second, independent
    `.snapshot()` read at Resolution time, and lets a Test substitute a
    Fake that *does* change between calls to prove the Fail-closed path
    is real."""

    def __init__(self, snapshot: DetectorRegistrySnapshot) -> None:
        self._snapshot = snapshot

    def snapshot(self) -> DetectorRegistrySnapshot:
        return self._snapshot


class _FixedActionRegistryProvider:
    """`ActionRegistryPort` counterpart to `_FixedDetectorRegistryProvider`
    (P5-CODEX-007 Rework)."""

    def __init__(self, snapshot: ActionRegistrySnapshot) -> None:
        self._snapshot = snapshot

    def snapshot(self) -> ActionRegistrySnapshot:
        return self._snapshot


class GuardrailGovernanceComposition:
    def __init__(
        self,
        *,
        qwen3guard_begin_role_turn: (Callable[[], Qwen3GuardRoleTurn | None] | None) = None,
        qwen3guard_end_role_turn: (Callable[[object], None] | None) = None,
    ) -> None:
        self.policy_provider = LocalPolicyProvider()
        # P5-CODEX-007 Rework: the live Provider itself, not a Snapshot
        # captured once at construction and reused forever — every
        # `invoke_*` call below re-reads it, exactly like
        # `self.policy_provider` already did, closing the asymmetry
        # Codex's Second Independent Review flagged (Authority never
        # refreshed while Policy always was).
        self.authority_provider: AuthorityProviderPort = LocalAuthorityProvider()
        self.approval_port = UnavailableApprovalPort()
        self._registry_entries = _default_registry_entries()
        registered = tuple(entry.action_id.value for entry in self._registry_entries.values())
        self.action_registry_snapshot = ActionRegistrySnapshot(
            registry_revision=1, registered_action_ids=registered
        )
        self._action_registry_provider: ActionRegistryPort = _FixedActionRegistryProvider(
            self.action_registry_snapshot
        )
        adapter: GuardActionAdapterPort = LocalGuardActionAdapter()
        self._adapters: dict[str, GuardActionAdapterPort] = dict.fromkeys(
            self._registry_entries, adapter
        )
        input_detectors = build_input_detectors()
        output_detectors = build_output_detectors()
        # `guardrail.context_source` reuses the exact same Detector set
        # as `guardrail.input` (Injection/Jailbreak/Authority-spoofing/
        # Secret/PII) — a malicious or compromised RAG Document is the
        # same class of threat as a malicious User Input, just arriving
        # through a different Channel (P5-CODEX-001 Rework, P5-ACC-007).
        context_source_detectors = build_input_detectors()
        if qwen3guard_begin_role_turn is not None and qwen3guard_end_role_turn is not None:
            # P6-RR-O-WU-002 (Production Wiring Delta, resolves
            # P6-CODEX-048): additive to the Rule/Pattern Detectors above
            # — never replaces them, never removed from the static
            # Detector Registry regardless of whether the dedicated Guard
            # is currently Active (see `Qwen3GuardDetectorAdapter`'s own
            # docstring for why Registry membership must stay static
            # while Model availability stays dynamic).
            #
            # P6-RR-R21 (resolves P6-CODEX-086): each of the 3 Points below
            # shares the same `begin_role_turn`/`end_role_turn` pair —
            # every real `classify_point` call this Detector makes now
            # holds a genuine Turn Lease for its own exact duration (see
            # `Qwen3GuardDetectorAdapter.detect()`), never the previous
            # bare-Adapter-reference resolve-then-call with no Lease at
            # all.
            input_detectors = (
                *input_detectors,
                Qwen3GuardDetectorAdapter(
                    target=Qwen3GuardTarget.INPUT,
                    begin_role_turn=qwen3guard_begin_role_turn,
                    end_role_turn=qwen3guard_end_role_turn,
                ),
            )
            output_detectors = (
                *output_detectors,
                Qwen3GuardDetectorAdapter(
                    target=Qwen3GuardTarget.OUTPUT_CANDIDATE,
                    begin_role_turn=qwen3guard_begin_role_turn,
                    end_role_turn=qwen3guard_end_role_turn,
                ),
            )
            context_source_detectors = (
                *context_source_detectors,
                Qwen3GuardDetectorAdapter(
                    target=Qwen3GuardTarget.CONTEXT_SOURCE,
                    begin_role_turn=qwen3guard_begin_role_turn,
                    end_role_turn=qwen3guard_end_role_turn,
                ),
            )
        self._input_runtime = GuardrailPointRuntime(detectors=input_detectors)
        self._output_runtime = GuardrailPointRuntime(detectors=output_detectors)
        self._context_source_runtime = GuardrailPointRuntime(detectors=context_source_detectors)
        self._input_detector_registry_provider: DetectorRegistryPort = (
            _FixedDetectorRegistryProvider(
                DetectorRegistrySnapshot(
                    registry_revision=1,
                    registered_detector_ids=tuple(
                        detector.detector_id for detector in input_detectors
                    ),
                )
            )
        )
        self._output_detector_registry_provider: DetectorRegistryPort = (
            _FixedDetectorRegistryProvider(
                DetectorRegistrySnapshot(
                    registry_revision=1,
                    registered_detector_ids=tuple(
                        detector.detector_id for detector in output_detectors
                    ),
                )
            )
        )
        self._context_source_detector_registry_provider: DetectorRegistryPort = (
            _FixedDetectorRegistryProvider(
                DetectorRegistrySnapshot(
                    registry_revision=1,
                    registered_detector_ids=tuple(
                        detector.detector_id for detector in context_source_detectors
                    ),
                )
            )
        )
        self.mode_controller = GuardrailModeController()
        self._last_results: dict[str, GuardrailResult] = {}
        self._last_results_lock = threading.Lock()

    def invoke_input(self, *, invocation_id: str, mode: str, content: str) -> GuardrailResult:
        return self._input_runtime.invoke(
            invocation_id=invocation_id,
            point_id=GUARDRAIL_INPUT_POINT_ID,
            mode=mode,
            content=content,
            policy_provider=self.policy_provider,
            authority_provider=self.authority_provider,
            approval_port=self.approval_port,
            action_registry_provider=self._action_registry_provider,
            detector_registry_provider=self._input_detector_registry_provider,
            registry=self._registry_entries,
            adapters=self._adapters,
        )

    def invoke_output(self, *, invocation_id: str, mode: str, content: str) -> GuardrailResult:
        return self._output_runtime.invoke(
            invocation_id=invocation_id,
            point_id=GUARDRAIL_OUTPUT_CANDIDATE_POINT_ID,
            mode=mode,
            content=content,
            policy_provider=self.policy_provider,
            authority_provider=self.authority_provider,
            approval_port=self.approval_port,
            action_registry_provider=self._action_registry_provider,
            detector_registry_provider=self._output_detector_registry_provider,
            registry=self._registry_entries,
            adapters=self._adapters,
        )

    def invoke_context_source(
        self,
        *,
        invocation_id: str,
        mode: str,
        content_sources: tuple[ContextSourceUnit, ...],
    ) -> GuardrailResult:
        return self._context_source_runtime.invoke(
            invocation_id=invocation_id,
            point_id=GUARDRAIL_CONTEXT_SOURCE_POINT_ID,
            mode=mode,
            content="",
            content_sources=content_sources,
            policy_provider=self.policy_provider,
            authority_provider=self.authority_provider,
            approval_port=self.approval_port,
            action_registry_provider=self._action_registry_provider,
            detector_registry_provider=self._context_source_detector_registry_provider,
            registry=self._registry_entries,
            adapters=self._adapters,
        )

    def record_stream_guard_summary(self, summary: _StreamGuardSummaryLike) -> None:
        """`guardrail.stream_candidate` Terminal Result routing
        (P5-CODEX-009 Rework, Codex Second Independent Review item 2):
        the Stream Guard itself never depends on `guardrail_governance`
        (`conversation_generation.py` only calls a Callable satisfying a
        local Protocol) — this method is the concrete other end, turning
        one Stage's `StreamGuardSummary` into the same `GuardrailResult`
        shape every other Point already produces, so it crosses the
        identical Safe-Count-only Status boundary
        (`guardrail_governance_routes.py`) without a special case."""

        mode = self.mode_controller.current_mode_value()
        if mode == "off":
            self.record_result(
                point_id=GUARDRAIL_STREAM_CANDIDATE_POINT_ID,
                result=GuardrailResult(
                    invocation_id=str(uuid4()),
                    point_id=GUARDRAIL_STREAM_CANDIDATE_POINT_ID,
                    mode=mode,
                    execution_state=ExecutionState.NOT_EVALUATED,
                ),
            )
            return
        detections = tuple(
            GuardDetection(
                detection_id=f"stream-summary-{index}",
                detector_id="stream_guard_summary",
                category_id=CATEGORY_UNKNOWN_UNRESOLVED,
                outcome=(
                    DetectionOutcome.MATCH
                    if index < summary.match_count
                    else DetectionOutcome.CLEAR
                ),
                severity=Severity.HIGH if index < summary.match_count else Severity.NONE,
            )
            for index in range(summary.detection_count)
        )
        execution_state = ExecutionState.DEGRADED if summary.degraded else ExecutionState.EVALUATED
        executed_actions = (
            (
                ExecutedAction(
                    action_id=ActionId.SUPPRESS_STREAM_CANDIDATE.value,
                    executed=True,
                    intervening=True,
                ),
            )
            if summary.terminated
            else ()
        )
        result = GuardrailResult(
            invocation_id=str(uuid4()),
            point_id=GUARDRAIL_STREAM_CANDIDATE_POINT_ID,
            mode=mode,
            execution_state=execution_state,
            degraded_reason_code=(
                "guardrail_stream_detector_degraded" if summary.degraded else None
            ),
            detections=detections,
            severity=(
                Severity.CRITICAL
                if summary.terminated
                else (Severity.MODERATE if summary.match_count else Severity.NONE)
            ),
            executed_actions=executed_actions,
            call_count=summary.detection_count,
        )
        self.record_result(point_id=GUARDRAIL_STREAM_CANDIDATE_POINT_ID, result=result)

    def new_stream_guard(
        self,
    ) -> IncrementalStreamGuard | ObservingStreamGuard | NullStreamGuard:
        """Request-local — a fresh instance per Invocation, never shared
        across Turns/Tabs/Users (architecture §10, P5-ACC-022).

        Mode-gated at the *point of creation* (P5-G Audit fix then
        P5-CODEX-004 Rework, P5-MOD-002/003, P5-ACC-004/005):
        `IncrementalStreamGuard` has no Mode concept of its own. `off`
        gets `NullStreamGuard` (Detector Call 0). `observe` gets
        `ObservingStreamGuard` — architecture §6.1 requires OBSERVE to
        actually *observe* (Bounded Scanner State records
        Detection/Failure) while staying Byte-identical and never
        Terminating; a `NullStreamGuard` here would be "unobserved", not
        "non-intervening". Only `enforce` gets the real Terminating
        Scanner. Read fresh on every call so a Mode change applied
        mid-run via the Configuration Control CAS takes effect on the
        very next Stage, not just at Session construction time."""
        mode = self.mode_controller.current_mode_value()
        if mode == "enforce":
            return IncrementalStreamGuard(detectors=build_output_detectors())
        if mode == "observe":
            return ObservingStreamGuard(detectors=build_output_detectors())
        return NullStreamGuard()

    def record_result(self, *, point_id: str, result: GuardrailResult) -> None:
        with self._last_results_lock:
            self._last_results[point_id] = result

    def last_result_for(self, *, point_id: str) -> GuardrailResult | None:
        with self._last_results_lock:
            return self._last_results.get(point_id)


def _safe_mode(mode_provider: Callable[[], str]) -> str:
    try:
        mode = mode_provider()
    except Exception:
        logger.warning("guardrail_governance: mode provider raised", exc_info=True)
        return "mode_unavailable"
    return mode if mode in _VALID_MODES else "mode_unavailable"


def _pre_input_snapshot(messages: object) -> str:
    """Canonical scan target for `guardrail.input` — the latest user
    message content only (never the full System Prompt/Thinking)."""
    try:
        last = messages[-1]  # type: ignore[index]
        content = getattr(last, "content", "")
        return content if isinstance(content, str) else ""
    except Exception:
        return ""


class _ContextSourceItemLike(Protocol):
    """Structural mirror of `conversation_generation.py`'s own
    `ContextSourceItemLike` Protocol (P5-CODEX-006 Rework) — this
    Composition module *is* `guardrail_governance`, so it imports the
    concrete `ContextSourceUnit` directly below, but the Hook signature
    itself stays a plain structural shape so any caller satisfying it
    (not only `conversation_generation.py`) can supply Sources without
    importing this module's concrete Domain types."""

    @property
    def source_id(self) -> str: ...

    @property
    def source_class(self) -> str: ...

    @property
    def content(self) -> str: ...


def build_guardrail_hooks(
    *,
    composition: GuardrailGovernanceComposition,
    mode_provider: Callable[[], str],
) -> tuple[
    Callable[[object], tuple[bool, str]],
    Callable[[str], tuple[bool, str]],
    Callable[[tuple[_ContextSourceItemLike, ...]], tuple[bool, str]],
]:
    """Builds the plain `(guardrail_pre_hook, guardrail_post_hook,
    guardrail_context_source_hook)` triple with the exact same shape
    `ConversationGenerationService` already accepts for Phase 4's
    `governance_pre_hook`/`governance_post_hook` (P5-0-WU-002 Additive
    Composition) — Conversation stays decoupled from
    `guardrail_governance`, it only sees a Callable.

    `off` short-circuits before any Detector/Policy/Action Call
    (P5-MOD-002, Call 0). `observe` never intervenes (P5-MOD-003).
    `enforce` Fail-closes on an unreadable Mode, mirroring Phase 4's own
    `mode_unavailable` contract exactly.
    """

    def guardrail_pre_hook(request: object) -> tuple[bool, str]:
        mode = _safe_mode(mode_provider)
        if mode == "off":
            return False, ""
        if mode == "mode_unavailable":
            return True, "guardrail_mode_unavailable"
        invocation_id = str(uuid4())
        content = _pre_input_snapshot(getattr(request, "messages", ()))
        try:
            result = composition.invoke_input(
                invocation_id=invocation_id, mode=mode, content=content
            )
        except Exception:
            logger.warning("guardrail_governance: input point invocation failed", exc_info=True)
            if mode == "enforce":
                return True, "guardrail_enforce_evaluation_failed"
            return False, ""
        composition.record_result(point_id=GUARDRAIL_INPUT_POINT_ID, result=result)
        for action in result.executed_actions:
            if action.action_id == ActionId.REJECT_INPUT.value and action.executed:
                return True, "guardrail_reject_input"
        return False, ""

    def guardrail_post_hook(content: str) -> tuple[bool, str]:
        mode = _safe_mode(mode_provider)
        if mode == "off":
            return False, ""
        if mode == "mode_unavailable":
            return True, "guardrail_mode_unavailable"
        invocation_id = str(uuid4())
        try:
            result = composition.invoke_output(
                invocation_id=invocation_id, mode=mode, content=content
            )
        except Exception:
            logger.warning("guardrail_governance: output point invocation failed", exc_info=True)
            if mode == "enforce":
                return True, "guardrail_enforce_evaluation_failed"
            return False, ""
        composition.record_result(point_id=GUARDRAIL_OUTPUT_CANDIDATE_POINT_ID, result=result)
        for action in result.executed_actions:
            if action.action_id == ActionId.REJECT_OUTPUT.value and action.executed:
                return True, "guardrail_reject_output"
        return False, ""

    def guardrail_context_source_hook(
        sources: tuple[_ContextSourceItemLike, ...],
    ) -> tuple[bool, str]:
        mode = _safe_mode(mode_provider)
        if mode == "off":
            return False, ""
        if mode == "mode_unavailable":
            return True, "guardrail_mode_unavailable"
        if not sources:
            return False, ""
        invocation_id = str(uuid4())
        content_sources = tuple(
            ContextSourceUnit(
                source_id=item.source_id, source_class=item.source_class, content=item.content
            )
            for item in sources
        )
        try:
            result = composition.invoke_context_source(
                invocation_id=invocation_id, mode=mode, content_sources=content_sources
            )
        except Exception:
            logger.warning(
                "guardrail_governance: context_source point invocation failed", exc_info=True
            )
            if mode == "enforce":
                return True, "guardrail_enforce_evaluation_failed"
            return False, ""
        composition.record_result(point_id=GUARDRAIL_CONTEXT_SOURCE_POINT_ID, result=result)
        for action in result.executed_actions:
            if action.action_id == ActionId.STOP_BEFORE_GENERATION.value and action.executed:
                return True, "guardrail_context_source_rejected"
        return False, ""

    return guardrail_pre_hook, guardrail_post_hook, guardrail_context_source_hook
