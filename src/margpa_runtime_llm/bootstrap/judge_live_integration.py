"""Live Judge Integration (P6-CODEX-001, hardened P6-CODEX-010 Second
Rework, hardened P6-CODEX-020 Third Rework): wires the already-tested Judge
Domain/Application layer (judge_role_resolver, judge_prompt_builder,
judge_output_decoder, judge_budget_gate) into real Conversation Generation
via `ConversationGenerationSession.JudgeCompletionHook` — a zero-dependency
Callable Core calls at its Presented Final boundary, only after
both Governance/Guardrail Post-checks Allow the content and this Turn's own
`_context_usage()` token counting has already finished (P6-CODEX-007's
same-Turn self-collision fix).

Judge OFF is checked *inside* the Hook, first, before anything else: no
EvaluationCase, no Prompt, no Model Call is ever built (P6-ACC-016).

Lifecycle ownership (P6-CODEX-010/P6-RW7-JDG-006): the actual Model Call runs on a Thread
owned and tracked by `ModelAccessCoordinator.start_background()`, never a
detached daemon Thread this module loses track of. `start_background()`
returns `False` (this module then skips the Turn's Judge Run entirely,
recording an explicit `queued_or_skipped` state) if anything else — another
Main Turn, or another Background Task — is already active; it never
queues. Main Turns, symmetrically, actively preempt a running Background
Task (see `ModelAccessCoordinator.acquire_main`) rather than failing, so
`model_busy` from an internal Judge/Repair call becomes a genuine internal
fault, never a routine occurrence.

Mode Freeze (P6-CODEX-010, extended P6-CODEX-020, extended again P6-CODEX-029
Fourth Rework): `judge_mode`, `repair_mode`, AND `recording_mode` are all
read exactly once, together, at Hook entry — before `start_background` is
even called — never re-read mid-flight or at two different times. Before
P6-CODEX-029, `recording_mode` alone was still re-read fresh by the Judge
Evidence Recorder at write-time (on the Background Thread, potentially long
after Hook entry), so a live Recording Mode change mid-Run could still
affect whether that in-flight Run's own Evidence got written — the exact
inconsistency this Freeze exists to prevent for Judge/Repair Mode already.
A live Mode change while this Run is already executing cannot change what
that Run itself does (Repair Eligibility, Recording emission for this
specific Run are all decided from the one frozen snapshot).

Typed terminal boundary (P6-CODEX-020): every single Hook invocation
correlates the Current Request Identity with an explicit outcome —
`queued_or_skipped` (Judge OFF, or the Model was busy), `running`,
`completed`, `failed`, `cancelled` (Main-priority preemption reached this
Run), or `degraded` (the Run completed but a Governance/Guardrail Hook
inside Repair itself failed Fail-closed) — never silently leaving a stale
`last_result` from several Turns ago looking "current," and never leaving
`running` stuck forever if an exception occurs anywhere in the Run's body
(Prompt construction, Decode, Budget, Repair Executor, Evidence Recorder —
not only the Model Call itself).

No separate Judge Artifact exists in this environment (confirmed by every
real-hardware Recovery Entry so far) — this module reuses the same loaded
Main Model via `Phase1Application.service`, so every invocation is honestly
`JudgeIndependenceClass.MAIN_SELF` (P6-ACC-020: never displayed as
Independent).

OBSERVE remains asynchronous and never changes the Candidate. ENFORCE is
waited synchronously by the Presented Final boundary: ACCEPT preserves the
Candidate, an accepted bounded Repair replaces it, and every Failure/UNKNOWN/
unaccepted Repair converges to a safe user-facing fallback. A known failed
Candidate is therefore never emitted as the Canonical ENFORCE result.

Recording (P6-CODEX-011): decoupled entirely — this module no longer calls
any Recording Writer. See `bootstrap/recording_live_integration.py`.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from typing import Literal, Protocol, cast

from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    SEMANTIC_ENFORCEMENT_SAFE_FALLBACK,
    GovernancePostHook,
    GuardrailPostHook,
    JudgeCompletionContext,
    JudgeCompletionDecision,
    JudgeCompletionHook,
)
from margpa_runtime_llm.modules.evaluation.application.evaluation_orchestrator import (
    resolve_evaluation_disposition,
)
from margpa_runtime_llm.modules.evaluation.application.judge_budget_gate import (
    apply_judge_budget_gate,
)
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.application.judge_output_decoder import (
    decode_judge_output_fail_closed,
)
from margpa_runtime_llm.modules.evaluation.application.judge_prompt_builder import (
    build_judge_prompt,
)
from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationMode,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass
from margpa_runtime_llm.modules.evaluation.domain.run import EvaluationBudget
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelRuntimeInfo
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.repair.application.repair_eligibility_resolver import (
    RepairEligibility,
    resolve_repair_eligibility,
)
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.repair.domain.budget import RepairBudgetUsage
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.modules.runtime_observability.domain.recording import RecordingMode

from .recording_live_integration import JudgeEvidenceRecorder
from .repair_live_integration import LIVE_REPAIR_BUDGET, RepairExecutionResult


class RepairExecutorPort(Protocol):
    """Matches `repair_live_integration.attempt_live_repair`'s own
    runtime-parameter subset — `service`/`model_key`/`persistent` are
    already bound into the Callable via `functools.partial` at the
    bootstrap call site, so this module never needs to know about
    `PersistentConversationService` directly (kept decoupled, same
    pattern as every other Hook here)."""

    def __call__(
        self,
        *,
        request_id: str,
        model_key: str,
        user_input: str,
        original_answer: str,
        before_recommendation: EvaluationRecommendation,
        judge_reasoning: str,
        dialogue_context: tuple[str, ...],
        evidence_context: tuple[str, ...],
        governance_post_hook: GovernancePostHook | None,
        guardrail_post_hook: GuardrailPostHook | None,
        cancellation: CancellationToken | None,
        model_runtime_info: ModelRuntimeInfo | None = None,
        stage_hook: Callable[[str], None] | None = None,
        persist_accepted_attempt: bool = True,
    ) -> RepairExecutionResult | None: ...


_LIVE_RUBRIC_ID = "live_conversation_general_quality_v1"
_LIVE_CRITERIA = ("correctness", "safety", "coherence")
_LIVE_JUDGE_BUDGET = EvaluationBudget(max_calls=1, max_tokens=2000, max_wall_time_ms=30_000)
_LIVE_JUDGE_MAX_NEW_TOKENS = 200
_LIVE_ENFORCE_WAIT_TIMEOUT_SECONDS = _LIVE_JUDGE_BUDGET.max_wall_time_ms / 1000
_LIVE_ENFORCE_CANCEL_GRACE_SECONDS = 0.25
_LIVE_ENFORCE_WAIT_POLL_SECONDS = 0.01
_LIVE_JUDGE_CONFIG_DIGEST_SHA512 = hashlib.sha512(
    json.dumps(
        {
            "role": "judge",
            "rubric_id": _LIVE_RUBRIC_ID,
            "criteria": list(_LIVE_CRITERIA),
            "max_new_tokens": _LIVE_JUDGE_MAX_NEW_TOKENS,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()
_ZERO_REPAIR_USAGE = RepairBudgetUsage(
    attempts_used=0,
    wall_time_used_ms=0,
    additional_tokens_used=0,
    total_model_calls_used=0,
    current_depth=0,
)

JudgeRunState = Literal[
    "idle",
    "queued_or_skipped",
    "judging",
    "repairing",
    "rejudging",
    "completed",
    "failed",
    "cancelled",
    "degraded",
]
"""P6-OBS-004 (Fourth Rework, P6-CODEX-031): matches the Frozen Requirement's
exact Runtime State vocabulary's in-flight sub-states for this Hook's own
portion of the pipeline (`preparing`/`guarding`/`generating` precede this
Hook and are projected elsewhere, from `ConversationGenerationSession`
itself; `rejected` is a Main Turn outcome this Hook never produces). A
single generic `"running"` — this module's own state before this Rework —
collapsed the Judge call, the Repair candidate call, and the Rejudge call
into one indistinguishable value; Fourth Review explicitly rejected
treating that collapse as an acceptable simplification of the
Requirement."""


@dataclass(frozen=True, slots=True)
class LiveJudgeResult:
    request_id: str
    judge_role: JudgeIndependenceClass
    recommendation: str
    confidence: float
    execution_state: str
    failure_reason: str | None
    repair_eligibility: str | None = None
    repair_outcome: str | None = None
    repair_accepted: bool | None = None
    repair_new_turn_id: str | None = None
    presentation_outcome: str | None = None
    candidate_withheld: bool = False
    presented_content: str | None = None


@dataclass(frozen=True, slots=True)
class _PendingJudgeEvidence:
    """Memory-only publication intent; constructing it performs no I/O."""

    publish_action: Callable[[], None]

    def publish(self) -> None:
        self.publish_action()


@dataclass(frozen=True, slots=True)
class _JudgeWorkerOutcome:
    result: LiveJudgeResult
    pending_evidence: _PendingJudgeEvidence | None = None


class JudgeGovernanceComposition:
    """Holds the Current Request's Judge Run state plus the most recent
    completed Result. A Status projection reads `current_state()`/
    `current_request_id()`/`last_result()` together: `last_result()` is only
    "current" when `last_result().request_id == current_request_id()` — a
    Turn for which Judge was OFF, or for which the Model was busy, still
    updates `current_request_id()` (via `mark_skipped`) even though it
    leaves `last_result()` untouched, so a stale earlier `last_result` can
    never be mistaken for this Turn's own outcome (P6-CODEX-020)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._state: JudgeRunState = "idle"
        self._current_request_id: str | None = None
        self._last_result: LiveJudgeResult | None = None
        self._skip_reason: str | None = None
        self._run_sequence = 0
        self._active_run_generation: int | None = None
        self._evidence_publication_failure: str | None = None

    def begin_run(self, *, request_id: str) -> int:
        """Claim projection ownership for one Judge run generation."""

        with self._lock:
            self._run_sequence += 1
            self._active_run_generation = self._run_sequence
            self._state = "judging"
            self._current_request_id = request_id
            self._skip_reason = None
            self._evidence_publication_failure = None
            return self._run_sequence

    def mark_running(
        self,
        *,
        request_id: str,
        stage: Literal["judging", "repairing", "rejudging"] = "judging",
        run_generation: int | None = None,
    ) -> bool:
        """P6-CODEX-031 (Fourth Rework): `stage` lets a Run's Current State
        move through `judging` -> `repairing` -> `rejudging` as it actually
        progresses (called again, in place, at each real transition) —
        never frozen at a single generic `running` value for the Run's
        entire duration."""
        with self._lock:
            if run_generation is not None and run_generation != self._active_run_generation:
                return False
            self._state = stage
            self._current_request_id = request_id
            return True

    def record_result(self, result: LiveJudgeResult, *, run_generation: int | None = None) -> bool:
        with self._lock:
            if run_generation is not None and run_generation != self._active_run_generation:
                return False
            self._state = (
                "failed"
                if result.execution_state == "failed"
                else "cancelled"
                if result.execution_state == "cancelled"
                else "degraded"
                if result.execution_state == "degraded"
                else "completed"
            )
            self._current_request_id = result.request_id
            self._last_result = result
            self._active_run_generation = None
            return True

    def mark_skipped(
        self, *, request_id: str, reason: str, run_generation: int | None = None
    ) -> bool:
        """P6-CODEX-020: correlates *this* Turn's request_id with an
        explicit "did not run" outcome — called for both Judge OFF and a
        busy-Model skip — so `current_request_id()` always reflects the
        latest Turn the Hook actually saw, never leaving it (and by
        extension the freshness check on `last_result()`) stale across an
        arbitrary number of subsequent non-judged Turns. `reason` ("
        judge_off" | "model_busy") is not currently surfaced beyond this
        Composition but is kept as a first-class field rather than
        discarded, for future Status/Evidence detail."""
        with self._lock:
            if run_generation is not None and run_generation != self._active_run_generation:
                return False
            self._state = "queued_or_skipped"
            self._current_request_id = request_id
            self._skip_reason = reason
            self._active_run_generation = None
            return True

    def current_state(self) -> JudgeRunState:
        with self._lock:
            return self._state

    def current_request_id(self) -> str | None:
        with self._lock:
            return self._current_request_id

    def record_evidence_publication_failure(self, *, reason: str) -> None:
        """Expose a tracked Publisher start/run failure without changing
        the already-owned Presented Final or Judge terminal projection."""

        with self._lock:
            self._evidence_publication_failure = reason

    def evidence_publication_failure(self) -> str | None:
        with self._lock:
            return self._evidence_publication_failure

    def last_result(self) -> LiveJudgeResult | None:
        with self._lock:
            return self._last_result


def build_judge_completion_hook(
    *,
    service: InferenceService,
    judge_mode_controller: JudgeModeController,
    model_access_coordinator: ModelAccessCoordinator,
    repair_mode_controller: RepairModeController | None = None,
    recording_mode_controller: RecordingModeController | None = None,
    governance_post_hook: GovernancePostHook | None = None,
    guardrail_post_hook: GuardrailPostHook | None = None,
    repair_executor: RepairExecutorPort | None = None,
    judge_evidence_recorder: JudgeEvidenceRecorder | None = None,
    enforce_wait_timeout_seconds: float = _LIVE_ENFORCE_WAIT_TIMEOUT_SECONDS,
    enforce_cancel_grace_seconds: float = _LIVE_ENFORCE_CANCEL_GRACE_SECONDS,
) -> tuple[JudgeCompletionHook, JudgeGovernanceComposition]:
    """`model_key`/`model_runtime_info` are no longer accepted as bootstrap
    parameters here (P6-CODEX-025, Fourth Rework): the only correct source
    for "which Model did this specific Attempt actually run with" is the
    Session's own per-Attempt-frozen `JudgeCompletionContext.model_key` /
    `.model_runtime_info`, never a value frozen once at Hook-construction
    time. A bootstrap-time value would silently go stale across any Runtime
    Model Switch that happens after this Hook is built."""
    if enforce_wait_timeout_seconds <= 0 or enforce_cancel_grace_seconds < 0:
        raise ValueError("ENFORCE wait bounds must be positive and non-negative")
    composition = JudgeGovernanceComposition()

    def _start_evidence_publication(
        *, request_id: str, pending_evidence: _PendingJudgeEvidence
    ) -> None:
        """Publish off the Model lease on a shutdown-tracked auxiliary Task."""

        def _publish_evidence() -> None:
            try:
                pending_evidence.publish()
            except Exception as exc:
                composition.record_evidence_publication_failure(
                    reason=f"publisher_error:{type(exc).__name__}"
                )

        if not model_access_coordinator.start_auxiliary(
            task_id=f"{request_id}:judge-evidence",
            target=_publish_evidence,
        ):
            composition.record_evidence_publication_failure(reason="publisher_start_rejected")

    def _run_judge_and_repair(
        context: JudgeCompletionContext,
        *,
        judge_mode: EvaluationMode,
        repair_mode: RepairMode | None,
        recording_mode: RecordingMode,
        cancellation: CancellationToken,
        run_generation: int,
    ) -> _JudgeWorkerOutcome:
        """Never raises — every exit path returns a terminal
        `LiveJudgeResult` (P6-CODEX-020's "Run全体をTyped terminal boundary
        で囲む" requirement); the caller (`_run_judge`) is the single place
        that records it onto `composition`, guaranteeing exactly one
        terminal record per Run regardless of which stage failed."""
        case = EvaluationCase(
            case_id=context.request_id,
            input=context.user_input or "(no input captured)",
            reference=None,
            criteria=_LIVE_CRITERIA,
            language="en",
        )
        prompt = build_judge_prompt(
            case=case,
            candidate_answer=context.assistant_content,
            rubric_id=_LIVE_RUBRIC_ID,
            dialogue_context=context.dialogue_context,
            evidence_context=context.evidence_context,
        )
        started = time.monotonic()
        try:
            result = service.generate(
                GenerationRequest(
                    request_id=f"{context.request_id}:judge",
                    model_key=context.model_key,
                    messages=(ChatMessage(role=MessageRole.USER, content=prompt),),
                    parameters=GenerationParameters(max_new_tokens=_LIVE_JUDGE_MAX_NEW_TOKENS),
                ),
                cancellation=cancellation,
            )
        except Exception as exc:
            model_failure_reason = f"model_call_error:{type(exc).__name__}"
            return _JudgeWorkerOutcome(
                result=LiveJudgeResult(
                    request_id=context.request_id,
                    judge_role=JudgeIndependenceClass.MAIN_SELF,
                    recommendation="unknown",
                    confidence=0.0,
                    execution_state="failed",
                    failure_reason=model_failure_reason,
                ),
                pending_evidence=_pending_evidence(
                    judge_evidence_recorder,
                    context=context,
                    model_key=context.model_key,
                    model_runtime_info=context.model_runtime_info,
                    recording_mode=recording_mode,
                    recommendation="unknown",
                    confidence=0.0,
                    token_usage=0,
                    latency_ms=int((time.monotonic() - started) * 1000),
                    execution_state="failed",
                    failure_reason=model_failure_reason,
                    judge_role=JudgeIndependenceClass.MAIN_SELF,
                    prompt=prompt,
                ),
            )
        if cancellation.is_cancelled():
            # P6-CODEX-019/020: Main-priority preemption reached this Run —
            # never decode a possibly-truncated partial response as if it
            # were a genuine Judge answer.
            return _JudgeWorkerOutcome(
                result=LiveJudgeResult(
                    request_id=context.request_id,
                    judge_role=JudgeIndependenceClass.MAIN_SELF,
                    recommendation="unknown",
                    confidence=0.0,
                    execution_state="cancelled",
                    failure_reason="preempted_by_main_priority",
                ),
                pending_evidence=_pending_evidence(
                    judge_evidence_recorder,
                    context=context,
                    model_key=context.model_key,
                    model_runtime_info=context.model_runtime_info,
                    recording_mode=recording_mode,
                    recommendation="unknown",
                    confidence=0.0,
                    token_usage=0,
                    latency_ms=int((time.monotonic() - started) * 1000),
                    execution_state="cancelled",
                    failure_reason="preempted_by_main_priority",
                    judge_role=JudgeIndependenceClass.MAIN_SELF,
                    prompt=prompt,
                ),
            )
        latency_ms = int((time.monotonic() - started) * 1000)
        decoded = decode_judge_output_fail_closed(
            raw_text=result.content,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=result.usage.completion_tokens if result.usage is not None else 0,
            latency_ms=latency_ms,
        )
        gated = apply_judge_budget_gate(budget=_LIVE_JUDGE_BUDGET, response=decoded)
        disposition = resolve_evaluation_disposition(
            mode=judge_mode,
            execution_state=gated.execution_state,
            recommendation=gated.recommendation,
        )
        eligibility: RepairEligibility | None = None
        repair_result: RepairExecutionResult | None = None
        judge_is_enforcing = judge_mode is EvaluationMode.ENFORCE
        if (
            judge_is_enforcing
            and repair_mode is not None
            and repair_mode_controller is not None
            and gated.execution_state is EvaluationExecutionState.COMPLETED
        ):
            eligibility = resolve_repair_eligibility(
                mode=repair_mode,
                guardrail_denied=False,
                judge_recommendation=gated.recommendation,
                budget=LIVE_REPAIR_BUDGET,
                usage=_ZERO_REPAIR_USAGE,
            )
            # P6-ACC-026/P6-GOV-002 (Second Rework): `resolve_repair_eligibility()`
            # itself treats OBSERVE identically to ENFORCE for Eligibility
            # classification purposes (it only excludes OFF) — Eligibility
            # is a pure classification, deliberately mode-agnostic, so a
            # Status reader can see "this would be Eligible" even under
            # OBSERVE. Actually *invoking* the Repair Executor (2 further
            # real Model Calls: the candidate + the Rejudge) must stay
            # gated on ENFORCE specifically here at the call site — this
            # was the exact gap: without this check, Repair OBSERVE could
            # silently cause the same additional Generation ENFORCE does.
            # `repair_mode` here is the one Frozen Snapshot value read at
            # Hook entry (P6-CODEX-020) — never re-read mid-Run.
            if (
                eligibility is RepairEligibility.ELIGIBLE
                and disposition.repair_requested
                and repair_mode is RepairMode.ENFORCE
                and repair_executor is not None
            ):

                def _apply_repair_stage(stage: str) -> None:
                    """`repair_executor`'s own `stage_hook` boundary is
                    typed as plain `str` (`repair_live_integration.py`
                    cannot import this module's `JudgeRunState` Literal
                    without creating a circular import), so the value is
                    validated here, at the one place it re-enters this
                    module's own typed vocabulary."""
                    if stage in ("judging", "repairing", "rejudging"):
                        composition.mark_running(
                            request_id=context.request_id,
                            stage=cast(Literal["judging", "repairing", "rejudging"], stage),
                            run_generation=run_generation,
                        )

                # P6-CODEX-031 (Fourth Rework): the Run's observable state
                # advances to `repairing` here, at the actual transition —
                # `stage_hook` lets `attempt_live_repair` itself advance it
                # once more, to `rejudging`, right before its own second
                # real Model Call, since that sub-transition happens
                # entirely inside that function, invisible from here.
                composition.mark_running(
                    request_id=context.request_id,
                    stage="repairing",
                    run_generation=run_generation,
                )
                repair_result = repair_executor(
                    request_id=context.request_id,
                    model_key=context.model_key,
                    user_input=context.user_input,
                    original_answer=context.assistant_content,
                    before_recommendation=gated.recommendation,
                    judge_reasoning=gated.reasoning or "",
                    dialogue_context=context.dialogue_context,
                    evidence_context=context.evidence_context,
                    governance_post_hook=governance_post_hook,
                    guardrail_post_hook=guardrail_post_hook,
                    cancellation=cancellation,
                    model_runtime_info=context.model_runtime_info,
                    stage_hook=_apply_repair_stage,
                    # The synchronous ENFORCE path has not committed the
                    # source Turn yet. Its accepted Repair becomes that
                    # Turn's Canonical Presented Final instead of creating
                    # a second derived Turn behind the user's answer.
                    persist_accepted_attempt=not context.enforce_presented_final,
                )
        execution_state = gated.execution_state.value
        failure_reason: str | None = (
            gated.failure_reason.value if gated.failure_reason is not None else None
        )
        if repair_result is not None and repair_result.degraded:
            # P6-CODEX-020/021: a Governance/Guardrail Hook's own internal
            # failure inside Repair is surfaced on the overall Judge Run
            # too, distinctly from an ordinary clean "completed" Run — an
            # operator scanning Judge Run state must be able to see this
            # without separately correlating Repair Evidence.
            execution_state = "degraded"
        pending_evidence = _pending_evidence(
            judge_evidence_recorder,
            context=context,
            model_key=context.model_key,
            model_runtime_info=context.model_runtime_info,
            recording_mode=recording_mode,
            recommendation=gated.recommendation.value,
            confidence=gated.confidence,
            token_usage=gated.token_usage,
            latency_ms=gated.latency_ms,
            execution_state=execution_state,
            failure_reason=failure_reason,
            judge_role=gated.judge_role,
            prompt=prompt,
            repair_result=repair_result,
        )
        presentation_outcome = "observed_candidate"
        candidate_withheld = False
        presented_content = context.assistant_content
        if context.enforce_presented_final:
            if disposition.candidate_may_be_presented:
                presentation_outcome = "candidate_accepted"
            elif (
                repair_result is not None
                and repair_result.accepted
                and repair_result.presented_content is not None
                and repair_result.presented_content.strip()
            ):
                presentation_outcome = "repair_accepted"
                candidate_withheld = True
                presented_content = repair_result.presented_content
            else:
                # Judge failure, UNKNOWN, a failed/budget-exhausted Repair,
                # or an unavailable Repair route all converge here. None
                # may fabricate PASS or expose the known failed Candidate.
                presentation_outcome = "safe_fallback"
                candidate_withheld = True
                presented_content = SEMANTIC_ENFORCEMENT_SAFE_FALLBACK
        return _JudgeWorkerOutcome(
            result=LiveJudgeResult(
                request_id=context.request_id,
                judge_role=gated.judge_role,
                recommendation=gated.recommendation.value,
                confidence=gated.confidence,
                execution_state=execution_state,
                failure_reason=failure_reason,
                repair_eligibility=eligibility.value if eligibility is not None else None,
                repair_outcome=repair_result.outcome if repair_result is not None else None,
                repair_accepted=(repair_result.accepted if repair_result is not None else None),
                repair_new_turn_id=(
                    repair_result.new_turn_id if repair_result is not None else None
                ),
                presentation_outcome=presentation_outcome,
                candidate_withheld=candidate_withheld,
                presented_content=presented_content,
            ),
            pending_evidence=pending_evidence,
        )

    def _run_judge(
        context: JudgeCompletionContext,
        *,
        judge_mode: EvaluationMode,
        repair_mode: RepairMode | None,
        recording_mode: RecordingMode,
        cancellation: CancellationToken,
        run_generation: int,
        record_terminal: bool = True,
    ) -> _JudgeWorkerOutcome:
        composition.mark_running(
            request_id=context.request_id,
            run_generation=run_generation,
        )
        try:
            outcome = _run_judge_and_repair(
                context,
                judge_mode=judge_mode,
                repair_mode=repair_mode,
                recording_mode=recording_mode,
                cancellation=cancellation,
                run_generation=run_generation,
            )
        except Exception as exc:
            # P6-CODEX-020: any exception anywhere in the Run's body
            # (Prompt construction, Budget, Repair Executor, Evidence
            # Recorder — not only the Model Call, which `
            # _run_judge_and_repair` already handles itself) must still
            # reach a terminal state here, never leave `composition` stuck
            # at "running".
            outcome = _JudgeWorkerOutcome(
                result=LiveJudgeResult(
                    request_id=context.request_id,
                    judge_role=JudgeIndependenceClass.MAIN_SELF,
                    recommendation="unknown",
                    confidence=0.0,
                    execution_state="failed",
                    failure_reason=f"unhandled_error:{type(exc).__name__}",
                )
            )
        result = outcome.result
        if context.enforce_presented_final and result.presentation_outcome is None:
            # Early typed failures (Model call, cancellation, unexpected
            # integration error) return before the ordinary projection at
            # the end of `_run_judge_and_repair`; normalize every one to the
            # same fail-closed Presented Final contract.
            accepted = (
                result.execution_state == EvaluationExecutionState.COMPLETED.value
                and result.recommendation == EvaluationRecommendation.ACCEPT.value
            )
            result = replace(
                result,
                presentation_outcome=("candidate_accepted" if accepted else "safe_fallback"),
                candidate_withheld=not accepted,
                presented_content=(
                    context.assistant_content if accepted else SEMANTIC_ENFORCEMENT_SAFE_FALLBACK
                ),
            )
            outcome = replace(outcome, result=result)
        if record_terminal:
            if outcome.pending_evidence is not None:
                _start_evidence_publication(
                    request_id=context.request_id,
                    pending_evidence=outcome.pending_evidence,
                )
            # Publish registration is complete before the observable Judge
            # terminal is projected. The Recorder itself remains async;
            # this only closes a shutdown/status observation gap where a
            # terminal Result was visible while its tracked Publisher had
            # not yet been registered.
            composition.record_result(result, run_generation=run_generation)
        return outcome

    def _safe_enforcement_result(
        context: JudgeCompletionContext,
        *,
        execution_state: Literal["failed", "cancelled"],
        failure_reason: str,
    ) -> LiveJudgeResult:
        return LiveJudgeResult(
            request_id=context.request_id,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            recommendation="unknown",
            confidence=0.0,
            execution_state=execution_state,
            failure_reason=failure_reason,
            presentation_outcome="safe_fallback",
            candidate_withheld=True,
            presented_content=SEMANTIC_ENFORCEMENT_SAFE_FALLBACK,
        )

    def hook(context: JudgeCompletionContext) -> JudgeCompletionDecision | None:
        judge_mode = (
            EvaluationMode(context.judge_mode)
            if context.judge_mode in {member.value for member in EvaluationMode}
            else judge_mode_controller.mode_snapshot().current_mode
        )
        # P6-CODEX-020: Repair Mode is frozen here, at the exact same moment
        # as Judge Mode, not re-read later inside the Background Task after
        # the Judge Model Call has already completed.
        repair_mode = (
            RepairMode(context.repair_mode)
            if context.repair_mode in {member.value for member in RepairMode}
            else (
                repair_mode_controller.mode_snapshot().current_mode
                if repair_mode_controller is not None
                else None
            )
        )
        # P6-CODEX-029 (Fourth Rework): Recording Mode is frozen into this
        # same snapshot, at this same moment — previously it was the one
        # value still re-read fresh, later, by the Judge Evidence Recorder
        # itself at write-time on the Background Thread.
        recording_mode = (
            RecordingMode(context.recording_mode)
            if context.recording_mode in {member.value for member in RecordingMode}
            else (
                recording_mode_controller.mode_snapshot().current_mode
                if recording_mode_controller is not None
                else RecordingMode.OFF
            )
        )
        if judge_mode is EvaluationMode.OFF:
            composition.mark_skipped(request_id=context.request_id, reason="judge_off")
            return None
        cancellation = context.cancellation or CancellationToken()
        run_generation = composition.begin_run(request_id=context.request_id)
        if judge_mode is EvaluationMode.ENFORCE and context.enforce_presented_final:
            # Use the Coordinator's owned Background slot even though the
            # caller waits synchronously for Presented Final. This prevents
            # a new Main Turn or Runtime Switch from racing the Judge calls;
            # Main priority can still cancel this bounded task normally.
            result_ready = threading.Event()
            publication_decided = threading.Event()
            publication_lock = threading.Lock()
            outcome_holder: list[_JudgeWorkerOutcome] = []

            def _decide_publication(publish: bool) -> None:
                with publication_lock:
                    if publication_decided.is_set():
                        return
                    pending_evidence = (
                        outcome_holder[0].pending_evidence if outcome_holder else None
                    )
                    publication_allowed = (
                        publish and not cancellation.is_cancelled() and pending_evidence is not None
                    )
                    publication_decided.set()
                if not publication_allowed or pending_evidence is None:
                    return
                _start_evidence_publication(
                    request_id=context.request_id,
                    pending_evidence=pending_evidence,
                )

            def _run_enforcement() -> None:
                try:
                    outcome = _run_judge(
                        context,
                        judge_mode=judge_mode,
                        repair_mode=repair_mode,
                        recording_mode=recording_mode,
                        cancellation=cancellation,
                        run_generation=run_generation,
                        # The waiting caller owns terminal projection and
                        # Evidence authorization. This Worker can only
                        # construct a Memory-only Pending payload.
                        record_terminal=False,
                    )
                    outcome_holder.append(outcome)
                    result_ready.set()
                    # The Model Worker is finished as soon as it returns its
                    # typed Result + memory-only Pending Evidence. It never
                    # waits for terminal arbitration and never performs
                    # Recorder I/O. Terminal authorization later starts a
                    # separate tracked auxiliary Publisher which owns no
                    # Model-access lease.
                finally:
                    result_ready.set()

            started = model_access_coordinator.start_background(
                task_id=context.request_id,
                cancel=cancellation.cancel,
                target=_run_enforcement,
            )
            if not started:
                result = _safe_enforcement_result(
                    context,
                    execution_state="failed",
                    failure_reason="model_busy",
                )
                composition.record_result(result, run_generation=run_generation)
            else:
                deadline = time.monotonic() + enforce_wait_timeout_seconds
                while True:
                    # Cancellation has deterministic priority over a
                    # simultaneous Worker completion. This is what makes a
                    # User Stop win the terminal race instead of becoming a
                    # Safe-Fallback ``completed`` event.
                    if cancellation.is_cancelled():
                        result = _safe_enforcement_result(
                            context,
                            execution_state="cancelled",
                            failure_reason="cancelled_by_request",
                        )
                        _decide_publication(False)
                        break
                    if result_ready.is_set():
                        outcome = outcome_holder[0] if outcome_holder else None
                        result = (
                            outcome.result
                            if outcome is not None
                            else _safe_enforcement_result(
                                context,
                                execution_state="failed",
                                failure_reason="enforcement_worker_failed",
                            )
                        )
                        break
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        result = _safe_enforcement_result(
                            context,
                            execution_state="failed",
                            failure_reason="deadline_exceeded",
                        )
                        cancellation.cancel()
                        _decide_publication(False)
                        break
                    result_ready.wait(timeout=min(_LIVE_ENFORCE_WAIT_POLL_SECONDS, remaining))

                # Cooperative cancellation normally releases the tracked
                # Worker immediately. The grace is deliberately bounded:
                # a pathological backend may retain Coordinator ownership,
                # but it cannot retain the SSE caller or mutate the already
                # committed Presented Final / Last-result projection.
                if not result_ready.is_set() and enforce_cancel_grace_seconds > 0:
                    result_ready.wait(timeout=enforce_cancel_grace_seconds)
                composition.record_result(result, run_generation=run_generation)
            return JudgeCompletionDecision(
                presented_content=result.presented_content or SEMANTIC_ENFORCEMENT_SAFE_FALLBACK,
                presentation_outcome=result.presentation_outcome or "safe_fallback",
                candidate_withheld=result.candidate_withheld,
                finalize_evidence=(
                    _decide_publication
                    if started and outcome_holder and not publication_decided.is_set()
                    else None
                ),
            )

        def _run_background() -> None:
            _run_judge(
                context,
                judge_mode=judge_mode,
                repair_mode=repair_mode,
                recording_mode=recording_mode,
                cancellation=cancellation,
                run_generation=run_generation,
            )

        started = model_access_coordinator.start_background(
            task_id=context.request_id,
            cancel=cancellation.cancel,
            target=_run_background,
        )
        if not started:
            # Never queue, never block the caller — a Main Turn or another
            # Background Task already owns the shared Model; this Turn's
            # Judge Run is skipped outright (Current state stays/returns to
            # idle, never a stale or fabricated result).
            composition.mark_skipped(
                request_id=context.request_id,
                reason="model_busy",
                run_generation=run_generation,
            )
        return None

    return hook, composition


def _pending_evidence(
    recorder: JudgeEvidenceRecorder | None,
    *,
    context: JudgeCompletionContext,
    model_key: str,
    model_runtime_info: ModelRuntimeInfo | None,
    recording_mode: RecordingMode,
    recommendation: str,
    confidence: float,
    token_usage: int,
    latency_ms: int,
    execution_state: str,
    failure_reason: str | None,
    judge_role: JudgeIndependenceClass,
    prompt: str,
    repair_result: RepairExecutionResult | None = None,
) -> _PendingJudgeEvidence | None:
    # Recording OFF is zero Recorder Calls, not merely a Recorder call that
    # notices OFF internally. Synchronous ENFORCE stores this closure only
    # in memory; its Worker cannot invoke it without the terminal owner's
    # later explicit authorization.
    if recorder is None or recording_mode is RecordingMode.OFF:
        return None

    def _publish() -> None:
        recorder(
            request_id=context.request_id,
            recording_mode=recording_mode,
            model_identity=model_key,
            # P6-CODEX-022: the Artifact Digest and Backend Identity/Version
            # actually loaded — `model_identity` alone (a bare config key) is
            # not enough to distinguish a re-download or backend upgrade of the
            # same key, which P6-LJG-002's "necessary Traces" also requires.
            artifact_digest_sha512=(
                model_runtime_info.artifact_digest.value if model_runtime_info is not None else None
            ),
            backend_key=(
                model_runtime_info.backend_key if model_runtime_info is not None else None
            ),
            backend_version=(
                model_runtime_info.backend_version if model_runtime_info is not None else None
            ),
            judge_role=judge_role.value,
            rubric_id=_LIVE_RUBRIC_ID,
            prompt=prompt,
            recommendation=recommendation,
            confidence=confidence,
            token_usage=token_usage,
            latency_ms=latency_ms,
            execution_state=execution_state,
            failure_reason=failure_reason,
            repair_outcome=repair_result.outcome if repair_result is not None else None,
            repair_accepted=(repair_result.accepted if repair_result is not None else None),
            repair_new_turn_id=(repair_result.new_turn_id if repair_result is not None else None),
            config_digest_sha512=_LIVE_JUDGE_CONFIG_DIGEST_SHA512,
        )

    return _PendingJudgeEvidence(publish_action=_publish)
