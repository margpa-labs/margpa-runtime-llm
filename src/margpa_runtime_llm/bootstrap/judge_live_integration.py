"""Live Judge Integration (P6-CODEX-001, hardened P6-CODEX-010 Second
Rework, hardened P6-CODEX-020 Third Rework): wires the already-tested Judge
Domain/Application layer (judge_role_resolver, judge_prompt_builder,
judge_output_decoder, judge_budget_gate) into real Conversation Generation
via `ConversationGenerationSession.JudgeCompletionHook` — a zero-dependency
Callable Core already calls, last, inside `_completed_event()`, only after
both Governance/Guardrail Post-checks Allow the content and this Turn's own
`_context_usage()` token counting has already finished (P6-CODEX-007's
same-Turn self-collision fix).

Judge OFF is checked *inside* the Hook, first, before anything else: no
EvaluationCase, no Prompt, no Model Call is ever built (P6-ACC-016).

Lifecycle ownership (P6-CODEX-010): the actual Model Call runs on a Thread
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

Recording (P6-CODEX-011): decoupled entirely — this module no longer calls
any Recording Writer. See `bootstrap/recording_live_integration.py`.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Protocol, cast

from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    GovernancePostHook,
    GuardrailPostHook,
    JudgeCompletionContext,
    JudgeCompletionHook,
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
        governance_post_hook: GovernancePostHook | None,
        guardrail_post_hook: GuardrailPostHook | None,
        cancellation: CancellationToken | None,
        model_runtime_info: ModelRuntimeInfo | None = None,
        stage_hook: Callable[[str], None] | None = None,
    ) -> RepairExecutionResult | None: ...


_LIVE_RUBRIC_ID = "live_conversation_general_quality_v1"
_LIVE_CRITERIA = ("correctness", "safety", "coherence")
_LIVE_JUDGE_BUDGET = EvaluationBudget(max_calls=1, max_tokens=2000, max_wall_time_ms=30_000)
_LIVE_JUDGE_MAX_NEW_TOKENS = 200
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

    def mark_running(
        self, *, request_id: str, stage: Literal["judging", "repairing", "rejudging"] = "judging"
    ) -> None:
        """P6-CODEX-031 (Fourth Rework): `stage` lets a Run's Current State
        move through `judging` -> `repairing` -> `rejudging` as it actually
        progresses (called again, in place, at each real transition) —
        never frozen at a single generic `running` value for the Run's
        entire duration."""
        with self._lock:
            self._state = stage
            self._current_request_id = request_id

    def record_result(self, result: LiveJudgeResult) -> None:
        with self._lock:
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

    def mark_skipped(self, *, request_id: str, reason: str) -> None:
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
            self._state = "queued_or_skipped"
            self._current_request_id = request_id
            self._skip_reason = reason

    def current_state(self) -> JudgeRunState:
        with self._lock:
            return self._state

    def current_request_id(self) -> str | None:
        with self._lock:
            return self._current_request_id

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
) -> tuple[JudgeCompletionHook, JudgeGovernanceComposition]:
    """`model_key`/`model_runtime_info` are no longer accepted as bootstrap
    parameters here (P6-CODEX-025, Fourth Rework): the only correct source
    for "which Model did this specific Attempt actually run with" is the
    Session's own per-Attempt-frozen `JudgeCompletionContext.model_key` /
    `.model_runtime_info`, never a value frozen once at Hook-construction
    time. A bootstrap-time value would silently go stale across any Runtime
    Model Switch that happens after this Hook is built."""
    composition = JudgeGovernanceComposition()

    def _run_judge_and_repair(
        context: JudgeCompletionContext,
        *,
        judge_mode: EvaluationMode,
        repair_mode: RepairMode | None,
        recording_mode: RecordingMode,
        cancellation: CancellationToken,
    ) -> LiveJudgeResult:
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
            case=case, candidate_answer=context.assistant_content, rubric_id=_LIVE_RUBRIC_ID
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
            _record_evidence(
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
                failure_reason=f"model_call_error:{type(exc).__name__}",
                judge_role=JudgeIndependenceClass.MAIN_SELF,
                prompt=prompt,
            )
            return LiveJudgeResult(
                request_id=context.request_id,
                judge_role=JudgeIndependenceClass.MAIN_SELF,
                recommendation="unknown",
                confidence=0.0,
                execution_state="failed",
                failure_reason=f"model_call_error:{type(exc).__name__}",
            )
        if cancellation.is_cancelled():
            # P6-CODEX-019/020: Main-priority preemption reached this Run —
            # never decode a possibly-truncated partial response as if it
            # were a genuine Judge answer.
            _record_evidence(
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
            )
            return LiveJudgeResult(
                request_id=context.request_id,
                judge_role=JudgeIndependenceClass.MAIN_SELF,
                recommendation="unknown",
                confidence=0.0,
                execution_state="cancelled",
                failure_reason="preempted_by_main_priority",
            )
        latency_ms = int((time.monotonic() - started) * 1000)
        decoded = decode_judge_output_fail_closed(
            raw_text=result.content,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=result.usage.completion_tokens if result.usage is not None else 0,
            latency_ms=latency_ms,
        )
        gated = apply_judge_budget_gate(budget=_LIVE_JUDGE_BUDGET, response=decoded)
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
                        )

                # P6-CODEX-031 (Fourth Rework): the Run's observable state
                # advances to `repairing` here, at the actual transition —
                # `stage_hook` lets `attempt_live_repair` itself advance it
                # once more, to `rejudging`, right before its own second
                # real Model Call, since that sub-transition happens
                # entirely inside that function, invisible from here.
                composition.mark_running(request_id=context.request_id, stage="repairing")
                repair_result = repair_executor(
                    request_id=context.request_id,
                    model_key=context.model_key,
                    user_input=context.user_input,
                    original_answer=context.assistant_content,
                    before_recommendation=gated.recommendation,
                    judge_reasoning=gated.reasoning or "",
                    governance_post_hook=governance_post_hook,
                    guardrail_post_hook=guardrail_post_hook,
                    cancellation=cancellation,
                    model_runtime_info=context.model_runtime_info,
                    stage_hook=_apply_repair_stage,
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
        _record_evidence(
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
        return LiveJudgeResult(
            request_id=context.request_id,
            judge_role=gated.judge_role,
            recommendation=gated.recommendation.value,
            confidence=gated.confidence,
            execution_state=execution_state,
            failure_reason=failure_reason,
            repair_eligibility=eligibility.value if eligibility is not None else None,
            repair_outcome=repair_result.outcome if repair_result is not None else None,
            repair_accepted=(repair_result.accepted if repair_result is not None else None),
            repair_new_turn_id=(repair_result.new_turn_id if repair_result is not None else None),
        )

    def _run_judge(
        context: JudgeCompletionContext,
        *,
        judge_mode: EvaluationMode,
        repair_mode: RepairMode | None,
        recording_mode: RecordingMode,
        cancellation: CancellationToken,
    ) -> None:
        composition.mark_running(request_id=context.request_id)
        try:
            result = _run_judge_and_repair(
                context,
                judge_mode=judge_mode,
                repair_mode=repair_mode,
                recording_mode=recording_mode,
                cancellation=cancellation,
            )
        except Exception as exc:
            # P6-CODEX-020: any exception anywhere in the Run's body
            # (Prompt construction, Budget, Repair Executor, Evidence
            # Recorder — not only the Model Call, which `
            # _run_judge_and_repair` already handles itself) must still
            # reach a terminal state here, never leave `composition` stuck
            # at "running".
            result = LiveJudgeResult(
                request_id=context.request_id,
                judge_role=JudgeIndependenceClass.MAIN_SELF,
                recommendation="unknown",
                confidence=0.0,
                execution_state="failed",
                failure_reason=f"unhandled_error:{type(exc).__name__}",
            )
        composition.record_result(result)

    def hook(context: JudgeCompletionContext) -> None:
        judge_mode = judge_mode_controller.mode_snapshot().current_mode
        # P6-CODEX-020: Repair Mode is frozen here, at the exact same moment
        # as Judge Mode, not re-read later inside the Background Task after
        # the Judge Model Call has already completed.
        repair_mode = (
            repair_mode_controller.mode_snapshot().current_mode
            if repair_mode_controller is not None
            else None
        )
        # P6-CODEX-029 (Fourth Rework): Recording Mode is frozen into this
        # same snapshot, at this same moment — previously it was the one
        # value still re-read fresh, later, by the Judge Evidence Recorder
        # itself at write-time on the Background Thread.
        recording_mode = (
            recording_mode_controller.mode_snapshot().current_mode
            if recording_mode_controller is not None
            else RecordingMode.OFF
        )
        if judge_mode is EvaluationMode.OFF:
            composition.mark_skipped(request_id=context.request_id, reason="judge_off")
            return
        cancellation = CancellationToken()
        started = model_access_coordinator.start_background(
            task_id=context.request_id,
            cancel=cancellation.cancel,
            target=lambda: _run_judge(
                context,
                judge_mode=judge_mode,
                repair_mode=repair_mode,
                recording_mode=recording_mode,
                cancellation=cancellation,
            ),
        )
        if not started:
            # Never queue, never block the caller — a Main Turn or another
            # Background Task already owns the shared Model; this Turn's
            # Judge Run is skipped outright (Current state stays/returns to
            # idle, never a stale or fabricated result).
            composition.mark_skipped(request_id=context.request_id, reason="model_busy")

    return hook, composition


def _record_evidence(
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
) -> None:
    if recorder is None:
        return
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
        backend_key=(model_runtime_info.backend_key if model_runtime_info is not None else None),
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
