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
from collections.abc import Callable, Mapping
from concurrent.futures import Future
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Literal, Protocol, cast

from margpa_runtime_llm.adapters.evaluation.selene import (
    BatchDispatchEvidence,
    SeleneSemanticEvaluator,
)
from margpa_runtime_llm.bootstrap.stage_deadline import stage_deadline
from margpa_runtime_llm.bootstrap.tracked_stage_worker import (
    TrackedStageWorkerRegistry,
    run_tracked_stage,
)
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    GovernancePostHook,
    GuardrailPostHook,
    JudgeCompletionContext,
    JudgeCompletionDecision,
    JudgeCompletionHook,
)
from margpa_runtime_llm.modules.evaluation.application.evaluation_orchestrator import (
    resolve_evaluation_disposition,
)
from margpa_runtime_llm.modules.evaluation.application.failure_presentation import (
    EvaluationFailureCode,
    classify_evaluation_failure,
    present_evaluation_failure,
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
    JudgePromptCriterion,
    MainSemanticPromptAdapter,
    build_judge_prompt,
)
from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationMode,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import (
    JudgeCriterionDisposition,
    JudgeCriterionResult,
    JudgeFailureReason,
    JudgeIndependenceClass,
    LlmJudgeResponse,
)
from margpa_runtime_llm.modules.evaluation.domain.run import EvaluationBudget
from margpa_runtime_llm.modules.evaluation.domain.stage_budget import (
    LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET,
    StageBudgetProfile,
    resolve_local_macos_judge_budget,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
    StructuredOutputConstraint,
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
from margpa_runtime_llm.modules.runtime_governance.domain import (
    SemanticActionDecision,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticDeferredReason,
    SemanticEvaluationRequest,
    SemanticEvaluationResponse,
    SemanticFinalDisposition,
    SemanticProviderState,
    SemanticRuntimeEvidence,
    SemanticTurnSnapshot,
)
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
        stage_budget: StageBudgetProfile = LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET,
        rejudge_service: InferenceService | None = None,
        rejudge_model_key: str | None = None,
        rejudge_role: JudgeIndependenceClass = JudgeIndependenceClass.MAIN_SELF,
        language: str = "en",
        rejudge_criteria: tuple[JudgePromptCriterion, ...] = (),
        tracked_stage_registry: TrackedStageWorkerRegistry | None = None,
        rejudge_structured_output_schema_factory: (
            Callable[[tuple[str, ...]], StructuredOutputConstraint] | None
        ) = None,
        rejudge_sampling_overrides: Mapping[str, object] | None = None,
    ) -> RepairExecutionResult | None: ...


_LIVE_RUBRIC_ID = "live_conversation_general_quality_v1"
# Mirrors `runtime_model_control.application.BUILT_IN_JUDGE`'s value as a
# local literal (P6-RR-N-WU-001) — this module deliberately never imports
# from `runtime_model_control` (see module docstring's Provider-neutral
# boundary rationale for the rest of this file).
_BUILT_IN_JUDGE_PROVIDER_ID = "built_in.deterministic"
# P6-RR-R2-WU-004: a clearly-labeled sentinel for a state that should not
# be reachable in practice (see `_record_semantic_result`) — never a
# Configured-identity fallback.
_UNRESOLVED_EXECUTED_PROVIDER_ID = "unresolved_executed_provider"
_LIVE_CRITERIA = ("correctness", "safety", "coherence")
_LIVE_STAGE_BUDGET = LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET
_LIVE_JUDGE_BUDGET = EvaluationBudget(
    max_calls=1,
    max_tokens=2000,
    max_wall_time_ms=_LIVE_STAGE_BUDGET.inference_budget_ms,
)
_LIVE_JUDGE_MAX_NEW_TOKENS = 200
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
    started_at: str | None = None
    completed_at: str | None = None
    frozen_main_mode: str | None = None
    frozen_guard_mode: str | None = None
    frozen_judge_mode: str | None = None
    frozen_repair_mode: str | None = None
    recording_mode: str | None = None
    configured_provider: str | None = None
    active_provider: str | None = None
    executed_provider: str | None = None
    budget_profile: str | None = None
    criteria_selected: int = 0
    criteria_evaluated: int = 0
    criteria_passed: int = 0
    criteria_deviated: int = 0
    criteria_unknown: int = 0
    criteria_not_applicable: int = 0
    criteria_deferred: int = 0
    judge_outcome: str | None = None
    final_disposition: str | None = None
    failure_message: str | None = None
    failure_language: str | None = None
    repair_rejudge_provider: str | None = None
    repair_rejudge_role: str | None = None
    repair_requested_by: str | None = None
    """P9-1 Judge/Governance Rework (WU-03): `"judge"` / `"main_governance"`
    / `"judge_and_main"`, set only when a Repair Attempt actually ran
    (`repair_result is not None`) -- surfaces which side(s) authorized the
    Repair Executor invocation this Run made, so a Status reader can tell
    Main Governance's own ENFORCE-origin correction apart from the
    pre-existing Judge/Repair-Mode-origin one (or both, when they
    converged on the same Candidate) without inferring it from `frozen_
    repair_mode` alone -- which, since this Rework, no longer implies
    whether a Repair actually happened. `None` whenever no Repair Attempt
    ran at all (never fabricated as "requested" just because either side's
    own recommendation/Eligibility check would have allowed one)."""


@dataclass(frozen=True, slots=True)
class _RunCorrelation:
    started_at: str
    language: str
    frozen_main_mode: str | None
    frozen_guard_mode: str | None
    frozen_judge_mode: str
    frozen_repair_mode: str | None
    recording_mode: str
    configured_provider: str
    active_provider: str | None
    budget_profile: str


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
    deferred_role_release: Future[object] | None = None


@dataclass(frozen=True, slots=True)
class _CriterionCounts:
    selected: int
    evaluated: int
    passed: int
    deviated: int
    unknown: int
    not_applicable: int
    deferred: int


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
        self._run_correlations: dict[int, _RunCorrelation] = {}
        self._evidence_publication_failure: str | None = None

    def begin_run(self, *, request_id: str, correlation: _RunCorrelation) -> int:
        """Claim projection ownership for one Judge run generation."""

        with self._lock:
            self._run_sequence += 1
            self._active_run_generation = self._run_sequence
            self._run_correlations[self._run_sequence] = correlation
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
            correlation = (
                self._run_correlations.pop(run_generation, None)
                if run_generation is not None
                else None
            )
            failure_code = classify_evaluation_failure(result.failure_reason)
            if failure_code is None and result.recommendation == "unknown":
                failure_code = EvaluationFailureCode.EVALUATION_INCONCLUSIVE
            presentation = (
                present_evaluation_failure(
                    reason_code=failure_code,
                    frozen_language=correlation.language if correlation is not None else "en",
                )
                if failure_code is not None
                else None
            )
            if correlation is not None:
                result = replace(
                    result,
                    started_at=correlation.started_at,
                    completed_at=datetime.now(UTC).isoformat(),
                    frozen_main_mode=correlation.frozen_main_mode,
                    frozen_guard_mode=correlation.frozen_guard_mode,
                    frozen_judge_mode=correlation.frozen_judge_mode,
                    frozen_repair_mode=correlation.frozen_repair_mode,
                    recording_mode=correlation.recording_mode,
                    configured_provider=correlation.configured_provider,
                    active_provider=correlation.active_provider,
                    budget_profile=correlation.budget_profile,
                    judge_outcome=result.judge_outcome or result.recommendation,
                    final_disposition=result.final_disposition or result.presentation_outcome,
                    failure_message=(presentation.message if presentation is not None else None),
                    failure_language=(presentation.language if presentation is not None else None),
                )
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
            if run_generation is not None:
                self._run_correlations.pop(run_generation, None)
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
    semantic_snapshot_provider: Callable[[str], SemanticTurnSnapshot | None] | None = None,
    semantic_result_recorder: (
        Callable[[SemanticEvaluationResponse], SemanticRuntimeEvidence | None] | None
    ) = None,
    semantic_deferred_recorder: (Callable[[str, SemanticDeferredReason], object] | None) = None,
    judge_provider_is_built_in: Callable[[], bool] | None = None,
    guardrail_mode_resolver: Callable[[], str] | None = None,
    begin_judge_role_turn: Callable[[], object | None] | None = None,
    begin_judge_role_turn_with_cancellation: (
        Callable[[CancellationToken], object | None] | None
    ) = None,
    end_judge_role_turn: Callable[[object], None] | None = None,
    stage_budget: StageBudgetProfile = _LIVE_STAGE_BUDGET,
    stage_budget_resolver: Callable[[str | None], StageBudgetProfile] = (
        resolve_local_macos_judge_budget
    ),
    enforce_wait_timeout_seconds: float | None = None,
    enforce_cancel_grace_seconds: float | None = None,
    tracked_stage_registry: TrackedStageWorkerRegistry | None = None,
) -> tuple[JudgeCompletionHook, JudgeGovernanceComposition]:
    """`model_key`/`model_runtime_info` are no longer accepted as bootstrap
    parameters here (P6-CODEX-025, Fourth Rework): the only correct source
    for "which Model did this specific Attempt actually run with" is the
    Session's own per-Attempt-frozen `JudgeCompletionContext.model_key` /
    `.model_runtime_info`, never a value frozen once at Hook-construction
    time. A bootstrap-time value would silently go stale across any Runtime
    Model Switch that happens after this Hook is built."""
    if (enforce_wait_timeout_seconds is not None and enforce_wait_timeout_seconds <= 0) or (
        enforce_cancel_grace_seconds is not None and enforce_cancel_grace_seconds < 0
    ):
        raise ValueError("ENFORCE wait bounds must be positive and non-negative")
    composition = JudgeGovernanceComposition()

    def _semantic_snapshot(request_id: str) -> SemanticTurnSnapshot | None:
        if semantic_snapshot_provider is None:
            return None
        try:
            return semantic_snapshot_provider(request_id)
        except Exception:
            return None

    def _judge_provider_is_built_in() -> bool:
        """P6-RR-N-WU-001: read once per Hook invocation (frozen alongside
        judge_mode/repair_mode/recording_mode). Defensive by construction —
        an exception or absent resolver means "not Built-in", i.e. this
        module's pre-existing Main-Model path, never a crash."""
        if judge_provider_is_built_in is None:
            return False
        try:
            return judge_provider_is_built_in()
        except Exception:
            return False

    def _frozen_guard_mode() -> str | None:
        """P6-RR-O-WU-004 (Production Wiring Delta, resolves the
        `frozen_guard_mode=None` half of P6-CODEX-053/061): reads the real
        Guardrail Mode once per Run, at the identical Mode-Freeze moment as
        judge_mode/repair_mode/recording_mode/built_in_active — never a
        second, later read. Absent resolver or a raised exception yields
        `None`, exactly the prior literal — this module never regresses
        below its pre-Delta behavior when unwired."""
        if guardrail_mode_resolver is None:
            return None
        try:
            return guardrail_mode_resolver()
        except Exception:
            return None

    def _begin_judge_role_turn(
        cancellation: CancellationToken,
    ) -> tuple[object | None, object | None]:
        """P6-RR-R2-WU-001, extended P6-RR-R21 (resolves P6-CODEX-086):
        read once per Hook invocation (frozen alongside judge_mode/
        repair_mode/recording_mode/built_in_active/frozen_guard_mode) —
        returns `(adapter, lease)`, the Frozen Active Adapter this Run
        dispatches from AND the genuine Turn Lease that Adapter was
        resolved together with (`begin_judge_role_turn`, backed by
        `RoleProviderLifecycleManager.begin_role_turn()`'s single-Lock
        atomic pairing — never a bare Adapter reference with no Lease at
        all, the pre-R21 shape). Defensive by construction: an exception
        or absent resolver, or a resolver that hands back a handle with no
        usable `.adapter`, means `(None, None)` — "no Active Adapter"
        (`_run_judge_and_repair` treats that as a typed failure), never a
        crash and never a silent fallback. `lease` is `None` whenever
        `adapter` is `None` — there is never a Lease to release without a
        corresponding Adapter this Run actually dispatches through."""
        if (
            begin_judge_role_turn is None
            and begin_judge_role_turn_with_cancellation is None
        ):
            return None, None
        try:
            handle = (
                begin_judge_role_turn_with_cancellation(cancellation)
                if begin_judge_role_turn_with_cancellation is not None
                else begin_judge_role_turn()
            )
        except Exception:
            return None, None
        if handle is None:
            return None, None
        adapter = getattr(handle, "adapter", None)
        if adapter is None:
            return None, None
        return adapter, getattr(handle, "lease", None)

    def _end_judge_role_turn(lease: object | None) -> None:
        """Exactly-once Release counterpart to `_begin_judge_role_turn` —
        a no-op when no Lease was ever acquired (`lease is None`, e.g.
        Built-in/none Provider, or no `end_judge_role_turn` wired at all).
        Never raises: an exception here must never mask this Run's own
        already-computed typed terminal Result."""
        if lease is None or end_judge_role_turn is None:
            return
        try:
            end_judge_role_turn(lease)
        except Exception:
            pass

    def _release_judge_role_turn_when_done(
        *,
        lease: object | None,
        future: Future[object],
    ) -> None:
        def release(_: Future[object]) -> None:
            _end_judge_role_turn(lease)

        future.add_done_callback(release)

    def _frozen_stage_budget(
        *, semantic_snapshot: SemanticTurnSnapshot | None, active_adapter: object | None
    ) -> StageBudgetProfile:
        provider_id = (
            getattr(active_adapter, "provider_id", None)
            if active_adapter is not None
            else (semantic_snapshot.active_provider if semantic_snapshot is not None else None)
        )
        try:
            return stage_budget_resolver(provider_id)
        except Exception:
            return stage_budget

    def _record_semantic_deferred(request_id: str, reason: SemanticDeferredReason) -> None:
        if semantic_deferred_recorder is None:
            return
        try:
            semantic_deferred_recorder(request_id, reason)
        except Exception:
            composition.record_evidence_publication_failure(
                reason="semantic_deferred_record_failed"
            )

    def _record_semantic_result(
        *,
        snapshot: SemanticTurnSnapshot | None,
        provider_state: SemanticProviderState,
        criterion_results: tuple[object, ...],
        latency_ms: int,
        failure_reason: str | None,
    ) -> SemanticActionDecision | None:
        """P9-1 Judge/Governance Rework (WU-03): now returns Main
        Governance's own `SemanticActionDecision` (via `semantic_result_
        recorder`'s typed `SemanticRuntimeEvidence | None` return, no
        longer a discarded `object`) so a caller reaching a genuinely
        Decoded/Completed result can pass it on to `_finalize_judge_
        dispatch()` as `main_action` -- see that function's own docstring
        for how a Main-origin repair request is reconciled with a
        Judge-origin one. `None` whenever recording did not happen at all
        (no snapshot, no recorder wired) or the recorder itself raised --
        never fabricated from a failure/cancellation, since those callers
        below never reach the subsequent `_finalize_judge_dispatch()` call
        this return value would otherwise feed."""
        if snapshot is None or semantic_result_recorder is None:
            return None
        translated: list[SemanticCriterionResult] = []
        descriptors = {item.criterion_id: item.descriptor_id for item in snapshot.criteria}
        for raw in criterion_results:
            criterion_id = getattr(raw, "criterion_id", None)
            if not isinstance(criterion_id, str):
                continue
            descriptor_id = descriptors.get(criterion_id)
            disposition = getattr(raw, "disposition", None)
            if descriptor_id is None or not isinstance(disposition, JudgeCriterionDisposition):
                continue
            translated.append(
                SemanticCriterionResult(
                    criterion_id=criterion_id,
                    descriptor_id=descriptor_id,
                    disposition={
                        JudgeCriterionDisposition.PASS: SemanticCriterionDisposition.PASS,
                        JudgeCriterionDisposition.DEVIATION: (
                            SemanticCriterionDisposition.DEVIATION
                        ),
                        JudgeCriterionDisposition.UNKNOWN: SemanticCriterionDisposition.UNKNOWN,
                    }[disposition],
                    confidence=getattr(raw, "confidence", None),
                    reason_code=getattr(raw, "reason_code", None),
                    evidence_refs=tuple(getattr(raw, "evidence_refs", ())),
                )
            )
        response = SemanticEvaluationResponse(
            request_id=snapshot.request_id,
            generation=snapshot.generation,
            # P6-RR-R2-WU-004 (Post-Claude Independent Review Rework,
            # resolves P6-CODEX-063 / Addendum M-WU-006): never fall back
            # to `configured_provider` — this call site is only reached
            # from the Main-shared dispatch branch below, which is itself
            # gated on a genuinely Active adapter (`active_adapter` is
            # non-None there), so `active_provider` is always populated
            # whenever this path actually runs. The sentinel is a
            # defensive, clearly-labeled fallback for a state that should
            # not be reachable, never a silent substitution of an
            # unexecuted Configured identity.
            provider_id=(snapshot.active_provider or _UNRESOLVED_EXECUTED_PROVIDER_ID),
            provider_state=provider_state,
            results=tuple(translated),
            latency_ms=latency_ms,
            failure_reason=failure_reason,
        )
        try:
            evidence = semantic_result_recorder(response)
        except Exception:
            composition.record_evidence_publication_failure(reason="semantic_result_record_failed")
            return None
        return evidence.action if evidence is not None else None

    def _judge_criterion_counts(response: LlmJudgeResponse, *, deferred: int) -> _CriterionCounts:
        passed = sum(
            item.disposition is JudgeCriterionDisposition.PASS
            for item in response.criterion_results
        )
        deviated = sum(
            item.disposition is JudgeCriterionDisposition.DEVIATION
            for item in response.criterion_results
        )
        unknown = sum(
            item.disposition is JudgeCriterionDisposition.UNKNOWN
            for item in response.criterion_results
        )
        return _CriterionCounts(
            selected=len(response.criterion_results),
            evaluated=passed + deviated,
            passed=passed,
            deviated=deviated,
            unknown=unknown,
            not_applicable=0,
            deferred=deferred,
        )

    def _semantic_criterion_counts(
        snapshot: SemanticTurnSnapshot, response: SemanticEvaluationResponse
    ) -> _CriterionCounts:
        expected = {item.criterion_id: item for item in snapshot.criteria}
        supplied = {
            item.criterion_id: item
            for item in response.results
            if (
                item.criterion_id in expected
                and expected[item.criterion_id].descriptor_id == item.descriptor_id
            )
        }
        dispositions = [
            result.disposition
            if (result := supplied.get(item.criterion_id)) is not None
            else SemanticCriterionDisposition.UNKNOWN
            for item in snapshot.criteria
        ]
        passed = sum(item is SemanticCriterionDisposition.PASS for item in dispositions)
        deviated = sum(item is SemanticCriterionDisposition.DEVIATION for item in dispositions)
        unknown = sum(item is SemanticCriterionDisposition.UNKNOWN for item in dispositions)
        not_applicable = sum(
            item is SemanticCriterionDisposition.NOT_APPLICABLE for item in dispositions
        )
        deferred = sum(item is SemanticCriterionDisposition.DEFERRED for item in dispositions)
        return _CriterionCounts(
            selected=len(snapshot.criteria),
            evaluated=passed + deviated,
            passed=passed,
            deviated=deviated,
            unknown=unknown,
            not_applicable=not_applicable,
            deferred=deferred + snapshot.deferred_criteria_count,
        )

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

    def _run_built_in_semantic_judge(
        *,
        context: JudgeCompletionContext,
        semantic_snapshot: SemanticTurnSnapshot | None,
        recording_mode: RecordingMode,
    ) -> _JudgeWorkerOutcome:
        """P6-RR-N-WU-001 (Production Wiring Delta): `built_in.deterministic`
        is a Provider *Type*, never a Model — this path never calls
        `service.generate()` (Model Call 0 is guaranteed by construction,
        not by a Mode gate, mirroring `DeterministicEvaluator`'s own
        guarantee for Phase 4's structural checks). Every ARGD/DAGD Semantic
        Criterion uses `SemanticEvaluationMethod.CLASSIFICATION*` /
        `ABSOLUTE_SCORING` (see `runtime_governance/domain/semantic_
        criteria.py`) — inherently qualitative judgments no deterministic
        check can honestly resolve — so each is reported `NOT_APPLICABLE`
        with `SemanticDeferredReason.UNSUPPORTED_MAPPING`, which the
        existing `merge_structural_and_semantic_observations` projection
        already treats as `DEFERRED_TO_SEMANTIC_EVALUATOR` (genuinely
        deferred to a real semantic Judge, never fabricated as evaluated).

        The overall Recommendation is honestly `unknown` (Built-in cannot
        judge general quality either) with `execution_state=completed` —
        not `failed` (P6-RR-DELTA §4.2: never present `malformed_output` as
        Built-in's normal-path Outcome). Under ENFORCE this correctly
        converges to `safe_fallback` via `_run_judge()`'s own existing
        early-return normalization (recommendation != ACCEPT); under
        OBSERVE the Candidate is unaffected, exactly like every other
        Judge Provider."""
        criteria = semantic_snapshot.criteria if semantic_snapshot is not None else ()
        if semantic_snapshot is not None and semantic_result_recorder is not None:
            # Bypasses `_record_semantic_result()`'s own translation layer:
            # that helper only accepts `JudgeCriterionDisposition` (the LLM
            # Decoder's own PASS/DEVIATION/UNKNOWN vocabulary, no
            # NOT_APPLICABLE) and silently drops anything else — correct for
            # its one real caller (the Model-backed path below), but wrong
            # here where the honest per-criterion Disposition is always
            # NOT_APPLICABLE. Constructs the identical `SemanticEvaluation
            # Response` shape directly instead.
            response = SemanticEvaluationResponse(
                request_id=semantic_snapshot.request_id,
                generation=semantic_snapshot.generation,
                # P6-RR-Q Internal Review Cycle 1 Finding (fixed): never
                # fall back to `configured_provider` here — this call only
                # happens when `built_in_active` is already True, which
                # itself is derived from the real Active Provider equaling
                # Built-in, so the Active value (when present) is always
                # correct on its own. Falling back to Configured would
                # reproduce the exact "infer Executed from Configured"
                # anti-pattern P6-GOV-018 §7 flags, even though this
                # particular call site can only ever be reached when
                # Built-in is genuinely Active.
                provider_id=(semantic_snapshot.active_provider or _BUILT_IN_JUDGE_PROVIDER_ID),
                provider_state=SemanticProviderState.ACTIVE,
                results=tuple(
                    SemanticCriterionResult(
                        criterion_id=item.criterion_id,
                        descriptor_id=item.descriptor_id,
                        disposition=SemanticCriterionDisposition.NOT_APPLICABLE,
                        reason_code=SemanticDeferredReason.UNSUPPORTED_MAPPING.value,
                    )
                    for item in criteria
                ),
                latency_ms=0,
            )
            try:
                semantic_result_recorder(response)
            except Exception:
                composition.record_evidence_publication_failure(
                    reason="semantic_result_record_failed"
                )
        result = LiveJudgeResult(
            request_id=context.request_id,
            judge_role=JudgeIndependenceClass.BUILT_IN,
            recommendation="unknown",
            confidence=0.0,
            execution_state="completed",
            failure_reason=None,
            executed_provider=_BUILT_IN_JUDGE_PROVIDER_ID,
            criteria_selected=len(criteria),
            # P6-RR-R3-WU-005 (Post-Claude Independent Review Rework,
            # resolves the rest of P6-CODEX-064): every Criterion here is
            # NOT_APPLICABLE, never both "evaluated" and "unknown" at once
            # (the previous `criteria_evaluated=len(criteria)` +
            # `criteria_unknown=len(criteria)` double-counted the same
            # Criteria into two buckets that should be mutually exclusive
            # and conflated NOT_APPLICABLE with UNKNOWN, a different
            # Disposition). `criteria_evaluated`/`criteria_unknown` stay 0
            # — Built-in performs no real Evaluation.
            criteria_evaluated=0,
            criteria_unknown=0,
            criteria_not_applicable=len(criteria),
            criteria_deferred=(
                semantic_snapshot.deferred_criteria_count if semantic_snapshot is not None else 0
            ),
            judge_outcome="unknown",
        )
        pending_evidence = _pending_evidence(
            judge_evidence_recorder,
            context=context,
            # R3-WU-02 (Controller Review IR-R2-02): the EXECUTED Judge
            # Provider here genuinely IS `built_in.deterministic` -- never
            # `context.model_key` (Main's own identity, the Model being
            # EVALUATED, not the one that executed this Judge Run). Passing
            # Main's own `model_key`/`model_runtime_info` here re-mixed
            # Built-in's own Model-Call-0 Evidence with Main's real
            # Artifact/Backend/Version, exactly the confirmed real bug this
            # fixes. `model_runtime_info=None` is itself the honest signal
            # (no Model Artifact backs this Provider Type at all) --
            # `_pending_evidence()`'s own caller-side contract already
            # renders a `None` Runtime Info as `"unavailable"`, never a
            # fabricated value.
            model_key=_BUILT_IN_JUDGE_PROVIDER_ID,
            model_runtime_info=None,
            recording_mode=recording_mode,
            recommendation="unknown",
            confidence=0.0,
            token_usage=0,
            latency_ms=0,
            execution_state="completed",
            failure_reason=None,
            judge_role=JudgeIndependenceClass.BUILT_IN,
            prompt="(built_in.deterministic: no prompt; zero Model Calls)",
            configured_judge_provider=(
                semantic_snapshot.configured_provider if semantic_snapshot is not None else None
            ),
            active_judge_provider=(
                semantic_snapshot.active_provider if semantic_snapshot is not None else None
            ),
        )
        return _JudgeWorkerOutcome(result=result, pending_evidence=pending_evidence)

    def _judge_failure_reason_from_semantic_response(
        response: SemanticEvaluationResponse,
    ) -> JudgeFailureReason:
        """P9-1 Package 2 Common Substrate fix: `SeleneSemanticEvaluator`
        (shared by every LLM-backed Judge provider, not only Selene) tags
        its own `failure_reason` string precisely — `"malformed_output:..."`
        for a genuine Strict-Decode rejection, `"..._inference_deadline_
        exceeded"`/`"..._cancelled"`/`"..._generation_cancelled"` for a
        timeout or cancellation, anything else for a real adapter/
        infrastructure failure. Previously every non-ACTIVE `provider_state`
        collapsed to the single `JudgeFailureReason.UNAVAILABLE` here,
        discarding that distinction — so a truncated/invalid JSON response
        (the model *did* respond) was indistinguishable from the model
        genuinely being unreachable, for every provider using this shared
        engine. This mirrors the same `JudgeFailureReason` vocabulary the
        Main-self decode pipeline (`judge_output_decoder.
        decode_judge_output_fail_closed`) already uses, so failure
        presentation is consistent across every LLM-backed Judge provider."""
        reason = response.failure_reason or ""
        if reason.startswith("malformed_output"):
            return JudgeFailureReason.MALFORMED_OUTPUT
        if "deadline_exceeded" in reason:
            return JudgeFailureReason.TIMEOUT
        if "cancelled" in reason:
            return JudgeFailureReason.CANCELLED
        return JudgeFailureReason.UNAVAILABLE

    def _judge_response_from_semantic_results(
        response: SemanticEvaluationResponse,
        *,
        judge_role: JudgeIndependenceClass = JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
    ) -> LlmJudgeResponse:
        """P6-RR-R2-WU-002: bridges Selene's criterion-shaped
        `SemanticEvaluationResponse` into the same `LlmJudgeResponse` shape
        the Main-self decode pipeline already produces, so
        `_finalize_judge_dispatch()`'s Repair/Presentation logic (unchanged)
        treats both Dispatch targets identically. Mirrors
        `runtime_governance.application.semantic_runtime.resolve_semantic_
        action()`'s own has_deviation/has_uncertain classification, applied
        here to derive an `EvaluationRecommendation` instead of a
        `SemanticFinalDisposition`.

        P9-1 Package 2: `judge_role` defaults to `INDEPENDENT_ARTIFACT`
        (Selene's own, unchanged, correct identity) but the Main-shared
        semantic-criteria dispatch now reusing this same bridge (see
        `_run_selene_dispatch`'s caller in the semantic-criteria branch of
        `_run_judge_and_repair`) passes `MAIN_SELF` explicitly — a Main
        Model judging its own answer must never be displayed as an
        Independent Judge Artifact (module docstring, P6-ACC-020).

        Gemma Judge-only Constrained Decoding Rework (WU-05): `token_usage`
        is `response.budget.completion_tokens` -- the real accumulated sum
        across every Batch Call this Run actually made (`SeleneSemantic
        Evaluator.evaluate()`'s own `completion_tokens` accumulator, which
        already increments before a Batch's own Decode outcome is known) --
        never the previous hardcoded `0`, in both the FAILED and COMPLETED
        branches below."""
        real_token_usage = response.budget.completion_tokens if response.budget is not None else 0
        if response.provider_state is not SemanticProviderState.ACTIVE:
            return LlmJudgeResponse(
                judge_role=judge_role,
                recommendation=EvaluationRecommendation.UNKNOWN,
                confidence=0.0,
                execution_state=EvaluationExecutionState.FAILED,
                failure_reason=_judge_failure_reason_from_semantic_response(response),
                token_usage=real_token_usage,
                latency_ms=response.latency_ms,
            )
        results = response.results
        has_deviation = any(
            item.disposition is SemanticCriterionDisposition.DEVIATION for item in results
        )
        # P9-1 Judge Dispatch Fix Round 6 Self-review correction (Round 4,
        # Finding from an independent existing-role/backward-compat audit):
        # NOT_APPLICABLE added here too, keeping this genuinely in sync
        # with `resolve_semantic_action()`'s own Round 6 has_uncertain fix
        # (semantic_runtime.py) that this function's own docstring already
        # claims to "Mirror". Not reachable today (this bridge is only ever
        # fed Selene/Main-shared results, whose Disposition Mapping in
        # `adapters/evaluation/selene.py` never produces NOT_APPLICABLE —
        # only the separate Built-in Judge path does, and it never calls
        # this function), but keeping the two has_uncertain definitions
        # identical now avoids a silent, hard-to-notice re-divergence if
        # that ever changes.
        has_uncertain = any(
            item.disposition
            in (
                SemanticCriterionDisposition.UNKNOWN,
                SemanticCriterionDisposition.DEFERRED,
                SemanticCriterionDisposition.NOT_APPLICABLE,
            )
            for item in results
        )
        recommendation = (
            EvaluationRecommendation.NEEDS_REPAIR
            if has_deviation
            else EvaluationRecommendation.UNKNOWN
            if has_uncertain
            else EvaluationRecommendation.ACCEPT
        )
        return LlmJudgeResponse(
            judge_role=judge_role,
            recommendation=recommendation,
            confidence=(1.0 if recommendation is EvaluationRecommendation.ACCEPT else 0.0),
            criterion_results=tuple(
                JudgeCriterionResult(
                    criterion_id=item.criterion_id,
                    disposition={
                        SemanticCriterionDisposition.PASS: JudgeCriterionDisposition.PASS,
                        SemanticCriterionDisposition.DEVIATION: JudgeCriterionDisposition.DEVIATION,
                    }.get(item.disposition, JudgeCriterionDisposition.UNKNOWN),
                    confidence=item.confidence or 0.0,
                    reason_code=item.reason_code,
                    evidence_refs=item.evidence_refs,
                )
                for item in results
            ),
            token_usage=real_token_usage,
            latency_ms=response.latency_ms,
            execution_state=EvaluationExecutionState.COMPLETED,
        )

    def _run_judge_and_repair(
        context: JudgeCompletionContext,
        *,
        judge_mode: EvaluationMode,
        repair_mode: RepairMode | None,
        recording_mode: RecordingMode,
        cancellation: CancellationToken,
        run_generation: int,
        built_in_active: bool,
        active_adapter: object | None,
        provider_selection_wired: bool,
        run_stage_budget: StageBudgetProfile,
    ) -> _JudgeWorkerOutcome:
        """Never raises — every exit path returns a terminal
        `LiveJudgeResult` (P6-CODEX-020's "Run全体をTyped terminal boundary
        で囲む" requirement); the caller (`_run_judge`) is the single place
        that records it onto `composition`, guaranteeing exactly one
        terminal record per Run regardless of which stage failed.

        P6-RR-R2-WU-001/002/003/006 (Post-Claude Independent Review Rework,
        resolves P6-CODEX-063): `active_adapter` is the Frozen Active Judge
        Adapter Lease this Hook resolved at entry (mirrors `built_in_active`
        /`frozen_guard_mode`'s own once-per-Run Freeze discipline) — the
        *only* source this function ever dispatches from. A `None` Active
        Adapter is a typed failure (Model Call 0), never a silent fallback
        to Main-self (the previous unconditional behavior this Rework
        replaces); a Selene-shaped Adapter (exposes `semantic_evaluator`)
        dispatches to the dedicated Semantic Evaluator; anything else is
        treated as an explicit Main-shared Judge selection and dispatches
        through Main's own already-loaded Service, exactly as before, but
        now *earned* by a genuinely Active Adapter rather than assumed."""
        semantic_snapshot = _semantic_snapshot(context.request_id)
        if built_in_active:
            return _run_built_in_semantic_judge(
                context=context,
                semantic_snapshot=semantic_snapshot,
                recording_mode=recording_mode,
            )
        if (
            active_adapter is not None
            and semantic_snapshot is not None
            and semantic_snapshot.active_provider is not None
            and getattr(active_adapter, "provider_id", None) != semantic_snapshot.active_provider
        ):
            # R3-WU-01 (Controller Review IR-R2-01 residual): the Dedicated
            # Adapter genuinely resolved at Judge Completion time must
            # match the Active Provider this Turn already froze at Turn
            # start -- a live Provider switch landing between the two
            # moments must never silently dispatch a real Model Call
            # against a DIFFERENT Provider than the one this Turn's own
            # Snapshot/Evidence already claims. Model Call 0; the Lease
            # `hook()` already acquired for `active_adapter` is released by
            # `_run_judge`'s own unconditional `finally`, exactly as the
            # sibling `active_adapter is None` branch below already relies
            # on without a manual release call here.
            _record_semantic_deferred(
                context.request_id, SemanticDeferredReason.PROVIDER_IDENTITY_MISMATCH
            )
            return _JudgeWorkerOutcome(
                result=LiveJudgeResult(
                    request_id=context.request_id,
                    judge_role=JudgeIndependenceClass.UNAVAILABLE,
                    recommendation="unknown",
                    confidence=0.0,
                    execution_state="failed",
                    failure_reason="judge_provider_identity_mismatch",
                    executed_provider=None,
                )
            )
        if active_adapter is None and provider_selection_wired:
            # P6-RR-R2-WU-003/006: Provider Selection is genuinely wired
            # for this deployment (a `begin_judge_role_turn` resolver was
            # supplied) but reports no Active Judge adapter right now —
            # a real, reachable state (Selection changed, Activation
            # failed/pending, etc.), never silently defaulted to
            # Main-self. Model Call 0.
            _record_semantic_deferred(
                context.request_id, SemanticDeferredReason.PROVIDER_UNAVAILABLE
            )
            return _JudgeWorkerOutcome(
                result=LiveJudgeResult(
                    request_id=context.request_id,
                    judge_role=JudgeIndependenceClass.UNAVAILABLE,
                    recommendation="unknown",
                    confidence=0.0,
                    execution_state="failed",
                    failure_reason="judge_provider_unavailable",
                    executed_provider=None,
                )
            )
        selene_evaluator = (
            getattr(active_adapter, "semantic_evaluator", None)
            if active_adapter is not None
            else None
        )
        if selene_evaluator is not None:
            # R2-WU-02 (Controller Review IR-CI-02): the real executing
            # identity's own Runtime Info -- the Dedicated Role's own real
            # Load Receipt (`SeleneRoleAdapter.load()`'s `InferenceService
            # (port=self._llama_adapter)`, exposed via `SeleneSemanticEvaluator
            # .inference_service`), never `context.model_runtime_info`
            # (Main's own identity). This is the confirmed real bug: a
            # genuinely `independent_artifact`-role Gemma Run recorded
            # `artifact_digest_sha512`/`backend_key`/`backend_version` as
            # Main Qwen's own, even though `model_identity` (fixed last
            # Round) already correctly said "Gemma".
            executed_service = getattr(selene_evaluator, "inference_service", None)
            executed_model_runtime_info = (
                getattr(executed_service, "runtime_info", None)
                if executed_service is not None
                else None
            )
            return _run_selene_dispatch(
                context,
                semantic_snapshot=semantic_snapshot,
                evaluator=selene_evaluator,
                executed_provider=getattr(active_adapter, "provider_id", None),
                executed_model_runtime_info=cast(
                    "ModelRuntimeInfo | None", executed_model_runtime_info
                ),
                judge_mode=judge_mode,
                repair_mode=repair_mode,
                recording_mode=recording_mode,
                cancellation=cancellation,
                run_generation=run_generation,
                stage_budget=run_stage_budget,
            )
        # Main-shared dispatch when Provider Selection is wired and
        # genuinely Active; the exact pre-Rework unconditional Main-self
        # dispatch when no `begin_judge_role_turn` resolver was supplied at
        # all (a simpler deployment shape with no Provider Selection
        # concept to silently override — P6-RR-R2 Entry §2 note).
        executed_provider = (
            getattr(active_adapter, "provider_id", None) if active_adapter is not None else None
        )
        if semantic_snapshot is not None and semantic_snapshot.criteria:
            # P9-1 Package 2 Common Substrate fix: a real Semantic Turn
            # Snapshot with Criteria to evaluate must go through the same
            # token-bounded batch planner every LLM-backed Judge provider
            # now shares (`SeleneSemanticEvaluator` — provider-neutral
            # despite its name, see its own module docstring), never a
            # single unbatched call for up to `max_criteria` (32) Criteria
            # against a small fixed output-token cap. That single-call
            # shape is exactly what silently truncated the requested
            # `criterion_results` JSON array and surfaced as Main-shared's
            # `malformed_output` failure (P9-1 Package 2 diagnosis) — never
            # reached by this branch anymore. `_run_selene_dispatch` is
            # itself already provider-neutral (duck-typed `evaluator:
            # object`); reused unchanged here rather than duplicating its
            # batching/decode/failure-mapping logic a second time. The
            # general-quality branch below (no Semantic Criteria selected)
            # is unaffected — its own single-call/200-token shape was never
            # the broken one.
            evaluator = SeleneSemanticEvaluator(
                service=service,
                model_key=executed_provider or context.model_key,
                prompt_adapter=MainSemanticPromptAdapter(rubric_id=_LIVE_RUBRIC_ID),
                tracked_stage_registry=tracked_stage_registry,
                provider_label="main_shared",
            )
            return _run_selene_dispatch(
                context,
                semantic_snapshot=semantic_snapshot,
                evaluator=evaluator,
                executed_provider=executed_provider,
                # R2-WU-02: this batched-criteria evaluator wraps Main's
                # own shared `service` (constructed just above) -- the
                # executing identity genuinely IS Main's own frozen
                # Runtime Info here, unlike the dedicated Gemma/Selene
                # branch above.
                executed_model_runtime_info=context.model_runtime_info,
                judge_mode=judge_mode,
                repair_mode=repair_mode,
                recording_mode=recording_mode,
                cancellation=cancellation,
                run_generation=run_generation,
                stage_budget=run_stage_budget,
                judge_role=JudgeIndependenceClass.MAIN_SELF,
                prompt_description=(
                    "(main-shared batched evaluator: prompt built per-batch by "
                    "MainSemanticPromptAdapter/build_judge_prompt)"
                ),
            )
        prompt_criteria = (
            tuple(
                JudgePromptCriterion(
                    criterion_id=item.criterion_id,
                    instruction=item.instruction,
                    evaluation_method=item.evaluation_method.value,
                    source_pointer=item.source_pointer,
                )
                for item in semantic_snapshot.criteria
            )
            if semantic_snapshot is not None
            else ()
        )
        case = EvaluationCase(
            case_id=context.request_id,
            input=context.user_input or "(no input captured)",
            reference=None,
            criteria=(
                tuple(item.criterion_id for item in prompt_criteria)
                if prompt_criteria
                else _LIVE_CRITERIA
            ),
            # P6-RR-R14-WU-006/007: the Turn's own frozen Response
            # Language, never the Semantic Snapshot's (see `frozen_language`
            # below for the identical rationale — the Candidate Answer
            # this Judge evaluates was itself generated in
            # `context.response_language`, independent of Main Runtime
            # Governance / Semantic Snapshot availability).
            language=context.response_language,
        )
        # P6-RR-R18-WU-001..003 (Post-Claude Independent Review Rework,
        # resolves the Prompt Build half of P6-CODEX-081): `build_judge_
        # prompt()` runs on its own Tracked Stage Worker Thread — the
        # caller (this function) never waits past `prompt_build_budget_ms`
        # regardless of how long that Thread actually takes. A Timeout
        # here returns the exact same typed `prompt_build_timeout` Failure
        # as before; the previous post-hoc elapsed-time comparison (which
        # could only ever report a Timeout *after* already paying the
        # full cost of the slow call) is replaced by this real bound.
        prompt_outcome = run_tracked_stage(
            work=lambda: build_judge_prompt(
                case=case,
                candidate_answer=context.assistant_content,
                rubric_id=_LIVE_RUBRIC_ID,
                dialogue_context=context.dialogue_context,
                evidence_context=context.evidence_context,
                semantic_criteria=prompt_criteria,
            ),
            budget_ms=run_stage_budget.prompt_build_budget_ms,
            registry=tracked_stage_registry,
        )
        if prompt_outcome.timed_out or prompt_outcome.result is None:
            return _JudgeWorkerOutcome(
                result=LiveJudgeResult(
                    request_id=context.request_id,
                    judge_role=JudgeIndependenceClass.MAIN_SELF,
                    recommendation="unknown",
                    confidence=0.0,
                    execution_state="failed",
                    failure_reason="prompt_build_timeout",
                    executed_provider=executed_provider,
                )
            )
        prompt = prompt_outcome.result
        started = time.monotonic()
        try:
            # P6-RR-R14-WU-001..005: the Inference Stage owns its own real,
            # preemptive Deadline — a slow real Model Call is actually
            # interrupted at `run_stage_budget.inference_budget_ms`, never
            # only measured after the fact, and never able to consume time
            # the outer ENFORCE Pipeline Deadline meant for a different
            # Stage.
            with stage_deadline(
                cancellation=cancellation, budget_ms=run_stage_budget.inference_budget_ms
            ) as inference_stage_timed_out:
                result = service.generate(
                    GenerationRequest(
                        request_id=f"{context.request_id}:judge",
                        model_key=executed_provider or context.model_key,
                        messages=(ChatMessage(role=MessageRole.USER, content=prompt),),
                        parameters=GenerationParameters(max_new_tokens=_LIVE_JUDGE_MAX_NEW_TOKENS),
                    ),
                    cancellation=cancellation,
                )
        except Exception as exc:
            model_failure_reason = f"model_call_error:{type(exc).__name__}"
            _record_semantic_result(
                snapshot=semantic_snapshot,
                provider_state=SemanticProviderState.FAILED,
                criterion_results=(),
                latency_ms=int((time.monotonic() - started) * 1000),
                failure_reason=model_failure_reason,
            )
            return _JudgeWorkerOutcome(
                result=LiveJudgeResult(
                    request_id=context.request_id,
                    judge_role=JudgeIndependenceClass.MAIN_SELF,
                    recommendation="unknown",
                    confidence=0.0,
                    execution_state="failed",
                    failure_reason=model_failure_reason,
                    executed_provider=executed_provider,
                ),
                pending_evidence=_pending_evidence(
                    judge_evidence_recorder,
                    context=context,
                    # P9-1 Component Independence Rework (WU-04): the real
                    # executing identity for this Run, matching the
                    # `GenerationRequest.model_key` actually dispatched
                    # above -- never unconditionally `context.model_key`
                    # (Main's own identity), which conflates "the Model
                    # evaluated" with "the Model that executed this Judge
                    # Run" whenever Provider Selection genuinely chose a
                    # different explicit Main-shared `executed_provider`.
                    model_key=executed_provider or context.model_key,
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
                    configured_judge_provider=(
                        semantic_snapshot.configured_provider
                        if semantic_snapshot is not None
                        else None
                    ),
                    active_judge_provider=(
                        semantic_snapshot.active_provider if semantic_snapshot is not None else None
                    ),
                ),
            )
        if cancellation.is_cancelled():
            # P9-1 Component Independence Rework (WU-04), Race-fixed by
            # R2-WU-03 (Controller Review IR-CI-03): a signalled
            # Cancellation Token reaching this point has at least three
            # structurally distinct real origins this module can itself
            # tell apart -- this Stage's own local Timer (`stage_deadline`
            # above), genuine Main-priority preemption (`ModelAccessCoordinator
            # .acquire_main()` signalling this Run's own registered `cancel`
            # directly -- see its own `was_preempted()` docstring), and a
            # genuine external Stop/disconnect (`ConversationGeneration
            # Session.request_cancel()`/`force_cancel()`, never routed
            # through that Coordinator at all). `was_preempted()` is now a
            # non-destructive peek -- this Worker-thread read and the
            # ENFORCE Wait Loop's own concurrent read (below) can no
            # longer race for a single one-shot consumption of the same
            # flag; both always see the same, correct answer. The single
            # internal Reason string is shared with that other call site
            # (unified by R2-WU-03; both still classify to the identical
            # Typed `CANCELLED` presentation via `classify_evaluation_
            # failure()`, unchanged).
            cancel_reason = (
                "inference_stage_deadline_exceeded"
                if inference_stage_timed_out()
                else "cancelled_by_main_priority_preemption"
                if model_access_coordinator.was_preempted(task_id=context.request_id)
                else "cancelled_by_request"
            )
            _record_semantic_result(
                snapshot=semantic_snapshot,
                provider_state=SemanticProviderState.FAILED,
                criterion_results=(),
                latency_ms=int((time.monotonic() - started) * 1000),
                failure_reason=cancel_reason,
            )
            return _JudgeWorkerOutcome(
                result=LiveJudgeResult(
                    request_id=context.request_id,
                    judge_role=JudgeIndependenceClass.MAIN_SELF,
                    recommendation="unknown",
                    confidence=0.0,
                    execution_state="cancelled",
                    failure_reason=cancel_reason,
                    executed_provider=executed_provider,
                ),
                pending_evidence=_pending_evidence(
                    judge_evidence_recorder,
                    context=context,
                    model_key=executed_provider or context.model_key,
                    model_runtime_info=context.model_runtime_info,
                    recording_mode=recording_mode,
                    recommendation="unknown",
                    confidence=0.0,
                    token_usage=0,
                    latency_ms=int((time.monotonic() - started) * 1000),
                    execution_state="cancelled",
                    failure_reason=cancel_reason,
                    judge_role=JudgeIndependenceClass.MAIN_SELF,
                    prompt=prompt,
                    configured_judge_provider=(
                        semantic_snapshot.configured_provider
                        if semantic_snapshot is not None
                        else None
                    ),
                    active_judge_provider=(
                        semantic_snapshot.active_provider if semantic_snapshot is not None else None
                    ),
                ),
            )
        latency_ms = int((time.monotonic() - started) * 1000)
        # P6-RR-R18-WU-001..003 (resolves the Decode half of
        # P6-CODEX-081): `decode_judge_output_fail_closed()` runs on its
        # own Tracked Stage Worker Thread — same real Bound as Prompt
        # Build above. On Timeout, a typed TIMEOUT LlmJudgeResponse is
        # constructed directly (never a second call into the Decoder,
        # which could itself hang the same way); a late-completing
        # Decode is never awaited or consulted again.
        decode_token_usage = result.usage.completion_tokens if result.usage is not None else 0
        decode_outcome = run_tracked_stage(
            work=lambda: decode_judge_output_fail_closed(
                raw_text=result.content,
                judge_role=JudgeIndependenceClass.MAIN_SELF,
                token_usage=decode_token_usage,
                latency_ms=latency_ms,
                expected_criterion_ids=tuple(item.criterion_id for item in prompt_criteria),
            ),
            budget_ms=run_stage_budget.decode_budget_ms,
            registry=tracked_stage_registry,
        )
        if decode_outcome.timed_out or decode_outcome.result is None:
            decoded = LlmJudgeResponse(
                judge_role=JudgeIndependenceClass.MAIN_SELF,
                recommendation=EvaluationRecommendation.UNKNOWN,
                confidence=0.0,
                token_usage=decode_token_usage,
                latency_ms=latency_ms,
                execution_state=EvaluationExecutionState.FAILED,
                failure_reason=JudgeFailureReason.TIMEOUT,
            )
        else:
            decoded = decode_outcome.result
        judge_budget = EvaluationBudget(
            max_calls=1,
            max_tokens=_LIVE_JUDGE_BUDGET.max_tokens,
            max_wall_time_ms=run_stage_budget.inference_budget_ms,
        )
        gated = apply_judge_budget_gate(budget=judge_budget, response=decoded)
        main_action = _record_semantic_result(
            snapshot=semantic_snapshot,
            provider_state=(
                SemanticProviderState.ACTIVE
                if gated.execution_state is EvaluationExecutionState.COMPLETED
                else SemanticProviderState.FAILED
            ),
            criterion_results=tuple(gated.criterion_results),
            latency_ms=gated.latency_ms,
            failure_reason=(
                gated.failure_reason.value if gated.failure_reason is not None else None
            ),
        )
        return _finalize_judge_dispatch(
            context,
            gated=gated,
            main_action=main_action,
            prompt=prompt,
            executed_provider=executed_provider,
            # R2-WU-02: this branch dispatches via Main's own shared
            # `service` (`service.generate(...)` above) -- the executing
            # identity genuinely IS Main's own frozen Runtime Info here.
            executed_model_runtime_info=context.model_runtime_info,
            configured_judge_provider=(
                semantic_snapshot.configured_provider if semantic_snapshot is not None else None
            ),
            active_judge_provider=(
                semantic_snapshot.active_provider if semantic_snapshot is not None else None
            ),
            judge_mode=judge_mode,
            repair_mode=repair_mode,
            recording_mode=recording_mode,
            cancellation=cancellation,
            run_generation=run_generation,
            stage_budget=run_stage_budget,
            rejudge_service=service,
            rejudge_model_key=executed_provider or context.model_key,
            rejudge_role=JudgeIndependenceClass.MAIN_SELF,
            frozen_language=context.response_language,
            criterion_counts=_judge_criterion_counts(
                gated,
                deferred=(
                    semantic_snapshot.deferred_criteria_count
                    if semantic_snapshot is not None
                    else 0
                ),
            ),
            # `prompt_criteria` is always empty on this path: reached only
            # when `semantic_snapshot is None or not semantic_snapshot.
            # criteria` (the real Semantic-criteria case redirects to
            # `_run_selene_dispatch` above, before this branch). No Frozen
            # Criterion set exists to preserve for the Rejudge here.
            rejudge_criteria=prompt_criteria,
        )

    def _run_selene_dispatch(
        context: JudgeCompletionContext,
        *,
        semantic_snapshot: SemanticTurnSnapshot | None,
        evaluator: object,
        executed_provider: str | None,
        executed_model_runtime_info: ModelRuntimeInfo | None,
        judge_mode: EvaluationMode,
        repair_mode: RepairMode | None,
        recording_mode: RecordingMode,
        cancellation: CancellationToken,
        run_generation: int,
        stage_budget: StageBudgetProfile,
        judge_role: JudgeIndependenceClass = JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
        prompt_description: str = (
            "(dedicated Selene evaluator: prompt built internally by SelenePromptAdapter)"
        ),
    ) -> _JudgeWorkerOutcome:
        """P6-RR-R2-WU-002 (Dedicated Selene明示Dispatch): dispatches to
        `SeleneRoleAdapter.semantic_evaluator` (a `SeleneSemanticEvaluator`,
        duck-typed here rather than imported by concrete class — this
        module stays decoupled from `runtime_model_control`/dedicated
        adapter types, matching every other Hook boundary in this file).
        Never reachable without a human-granted Exact Model Authority
        Receipt (`SeleneRoleAdapter.preflight()` Fail-closes otherwise) —
        the dispatch itself is real and Fixture-tested (R7-WU-001), but
        cannot be exercised against a real Selene Artifact in this Task's
        current Authority state.

        P9-1 Package 2: also reused, unchanged, for the Main-shared Judge's
        semantic-criteria dispatch (`_run_judge_and_repair`'s semantic-
        criteria branch, passing its own freshly-constructed
        `SeleneSemanticEvaluator` instance plus `judge_role=MAIN_SELF` and a
        Main-accurate `prompt_description`) — the whole point of sharing
        this function is that neither caller repeats the other's Batching/
        Decode/Failure-mapping Workaround."""
        if semantic_snapshot is None:
            return _JudgeWorkerOutcome(
                result=LiveJudgeResult(
                    request_id=context.request_id,
                    judge_role=judge_role,
                    recommendation="unknown",
                    confidence=0.0,
                    execution_state="failed",
                    failure_reason="semantic_snapshot_unavailable",
                    executed_provider=executed_provider,
                )
            )
        semantic_request = SemanticEvaluationRequest(
            snapshot=semantic_snapshot,
            stage="post",
            user_input=context.user_input,
            candidate_answer=context.assistant_content,
            dialogue_context=context.dialogue_context,
            evidence_context=context.evidence_context,
        )
        late_worker: Future[object] | None = None

        def record_late_worker(future: Future[object]) -> None:
            nonlocal late_worker
            late_worker = future

        # Gemma Judge-only Constrained Decoding Rework (WU-05): collected
        # regardless of Provider (Selene/Gemma/Main-shared all share this
        # one batching Engine) -- an empty list for a caller whose own
        # `evaluate()` never emits any (impossible today, since every
        # `SeleneSemanticEvaluator` instance now supports the Observer) is
        # handled identically to "no Batch ran at all" by `_finalize_judge_
        # dispatch()`'s own fallback below.
        batch_evidence: list[BatchDispatchEvidence] = []
        response = evaluator.evaluate(  # type: ignore[attr-defined]
            request=semantic_request,
            cancellation=cancellation,
            inference_budget_ms=stage_budget.inference_budget_ms,
            late_worker_observer=record_late_worker,
            batch_evidence_observer=batch_evidence.append,
        )
        if cancellation.is_cancelled():
            return _JudgeWorkerOutcome(
                result=LiveJudgeResult(
                    request_id=context.request_id,
                    judge_role=judge_role,
                    recommendation="unknown",
                    confidence=0.0,
                    execution_state="cancelled",
                    failure_reason="selene_cancelled",
                    executed_provider=executed_provider,
                ),
                deferred_role_release=late_worker,
            )
        main_action: SemanticActionDecision | None = None
        if semantic_result_recorder is not None:
            # Selene's own SemanticEvaluationResponse already carries the
            # correct `provider_id` (`SeleneSemanticEvaluator.evaluate()`
            # sets it directly, no Configured-fallback anti-pattern) —
            # recorded as-is, mirroring the Built-in path's own bypass of
            # `_record_semantic_result()`'s Main-self-shaped translation.
            # P9-1 Judge/Governance Rework (WU-03): the recorder's typed
            # `SemanticRuntimeEvidence | None` return is captured here too
            # (this Selene/Main-shared-batched dispatch path is the one
            # that actually carries real Semantic Criteria, so it is the
            # one Main Governance's own `resolve_semantic_action()` can
            # produce a genuine `REPAIR_REQUESTED` for).
            try:
                evidence = semantic_result_recorder(response)
                main_action = evidence.action if evidence is not None else None
            except Exception:
                composition.record_evidence_publication_failure(
                    reason="semantic_result_record_failed"
                )
        gated = _judge_response_from_semantic_results(response, judge_role=judge_role)
        # Controller Review (2026-09-04 19:16, IR-02) fix: the exact Frozen
        # Criterion definitions (instruction/evaluation method/source
        # pointer, not merely the ids) `gated.criterion_results` was itself
        # just decoded against this Run -- restricted to that same id set
        # (never the full `semantic_snapshot.criteria`, which may include
        # PRE-stage or otherwise not-dispatched-this-call entries `gated`
        # never actually evaluated) so a Repair Attempt's Rejudge re-scores
        # under the identical conditions, not a superset or a silently
        # narrower one.
        evaluated_criterion_ids = {item.criterion_id for item in gated.criterion_results}
        rejudge_criteria = (
            tuple(
                JudgePromptCriterion(
                    criterion_id=item.criterion_id,
                    instruction=item.instruction,
                    evaluation_method=item.evaluation_method.value,
                    source_pointer=item.source_pointer,
                )
                for item in semantic_snapshot.criteria
                if item.criterion_id in evaluated_criterion_ids
            )
            if semantic_snapshot is not None
            else ()
        )
        frozen_batch_evidence = tuple(batch_evidence)
        return _finalize_judge_dispatch(
            context,
            gated=gated,
            main_action=main_action,
            prompt=prompt_description,
            executed_provider=executed_provider,
            executed_model_runtime_info=executed_model_runtime_info,
            configured_judge_provider=(
                semantic_snapshot.configured_provider if semantic_snapshot is not None else None
            ),
            active_judge_provider=(
                semantic_snapshot.active_provider if semantic_snapshot is not None else None
            ),
            judge_mode=judge_mode,
            repair_mode=repair_mode,
            recording_mode=recording_mode,
            cancellation=cancellation,
            run_generation=run_generation,
            stage_budget=stage_budget,
            rejudge_service=getattr(evaluator, "inference_service", None),
            rejudge_model_key=executed_provider,
            rejudge_role=judge_role,
            frozen_language=context.response_language,
            criterion_counts=_semantic_criterion_counts(semantic_snapshot, response),
            rejudge_criteria=rejudge_criteria,
            # Gemma Judge-only Constrained Decoding Rework (WU-03): `None`
            # for Selene/Main-shared (their own `SeleneSemanticEvaluator`
            # instances never receive a Factory) -- only the real Gemma-
            # configured instance exposes a non-`None` one here.
            rejudge_structured_output_schema_factory=getattr(
                evaluator, "structured_output_schema_factory", None
            ),
            # Gemma Constrained Decoding Final Contract Micro Rework
            # (IR-FC-01): `None`/empty for Selene/Main-shared (their own
            # `SeleneSemanticEvaluator` instances never receive Sampling
            # Overrides) -- only the real Gemma-configured instance exposes
            # a non-empty mapping here, via `sampling_overrides`'s own
            # read-only property (mirrors `structured_output_schema_
            # factory`'s established getattr pattern immediately above).
            rejudge_sampling_overrides=getattr(evaluator, "sampling_overrides", None),
            # WU-05: real per-Batch/Run Evidence, replacing the pre-Rework
            # flat `call_count=1`/`token_usage=0`/`seed=unpinned`/generic
            # single-call `config_digest_sha512` for this Dedicated batched
            # dispatch (Selene, Gemma, and the Main-shared semantic-
            # criteria dispatch all share this fix, since all three share
            # this one Engine).
            #
            # Gemma Constrained Decoding Final Contract Micro Rework
            # (IR-FC-03) fix: the previous `or 1` fallback fabricated a
            # single Call whenever zero real Batches ever reached the Model
            # (e.g. every Criterion Budget-Deferred before dispatch) --
            # this Evidence field must honestly record `0` for a genuine
            # Model-Call-0 Run, distinguishable from a genuine single real
            # Call, never silently indistinguishable from one.
            call_count=len(frozen_batch_evidence),
            seed=(
                frozen_batch_evidence[0].parameters.seed if frozen_batch_evidence else None
            ),
            config_digest_sha512=getattr(
                evaluator, "config_digest_sha512", _LIVE_JUDGE_CONFIG_DIGEST_SHA512
            ),
            prompt_digest_sha512_override=_batch_dispatch_prompt_digest_sha512(
                frozen_batch_evidence
            ),
            batch_evidence_json=_batch_dispatch_evidence_json(frozen_batch_evidence),
        )

    def _finalize_judge_dispatch(
        context: JudgeCompletionContext,
        *,
        gated: LlmJudgeResponse,
        main_action: SemanticActionDecision | None,
        prompt: str,
        executed_provider: str | None,
        executed_model_runtime_info: ModelRuntimeInfo | None,
        judge_mode: EvaluationMode,
        repair_mode: RepairMode | None,
        recording_mode: RecordingMode,
        cancellation: CancellationToken,
        run_generation: int,
        stage_budget: StageBudgetProfile,
        rejudge_service: InferenceService | None,
        rejudge_model_key: str | None,
        rejudge_role: JudgeIndependenceClass,
        frozen_language: str,
        criterion_counts: _CriterionCounts,
        rejudge_criteria: tuple[JudgePromptCriterion, ...] = (),
        configured_judge_provider: str | None = None,
        active_judge_provider: str | None = None,
        rejudge_structured_output_schema_factory: (
            Callable[[tuple[str, ...]], StructuredOutputConstraint] | None
        ) = None,
        rejudge_sampling_overrides: Mapping[str, object] | None = None,
        call_count: int = 1,
        seed: int | None = None,
        config_digest_sha512: str = _LIVE_JUDGE_CONFIG_DIGEST_SHA512,
        prompt_digest_sha512_override: str | None = None,
        batch_evidence_json: str | None = None,
    ) -> _JudgeWorkerOutcome:
        """Shared Repair/Presentation tail (P6-RR-R2): identical for every
        real Dispatch target (Main-shared, Selene) — only `gated`/`prompt`/
        `executed_provider`/`criteria_selected` differ per caller. Extracted
        unchanged from the pre-Rework single Main-self body so this Rework
        never alters that already-tested Repair/Presentation behavior.

        P9-1 Judge/Governance Rework (WU-03): `main_action` is Main
        Governance's own `resolve_semantic_action()` recommendation for
        this exact Turn (`None` whenever no real Semantic Criteria were
        evaluated this Run, e.g. the general-quality Main-shared shape
        with no Criteria selected -- see `resolve_semantic_action()`'s
        own `if not results` early return). When `main_action.executed_
        disposition is REPAIR_REQUESTED`, Main Governance itself is
        authorizing a correction for a confirmed Rule violation,
        independent of the separate Judge-side Repair Mode toggle (see
        `resolve_semantic_action()`'s own WU-03 docstring for why). Both
        origins converge on invoking `repair_executor` **at most once**
        per Run below (Codex Controller Handoff WU-03's Matrix "既存
        Repair=ENFORCE" row: Judge- and Main-origin both authorize --
        never runs the Repair Executor twice for the same Candidate).
        Neither origin ever bypasses Guardrail Deny/Budget: both still go
        through the shared `resolve_repair_eligibility()` Resolver, just
        with a different `mode` argument reflecting which side is doing
        the authorizing (`repair_mode` for Judge-origin, unchanged;
        `RepairMode.ENFORCE` for Main-origin, representing Main
        Governance's own ENFORCE decision -- never a rewrite of the
        actual `repair_mode_controller`/frozen `repair_mode` value used
        anywhere else in this function or Evidence).

        Controller Review (2026-09-04 19:16, IR-02) fix: `rejudge_criteria`
        is the exact Frozen `SemanticCriterion` set (id/instruction/
        evaluation method/source pointer) `gated` was itself just scored
        against this Run -- carried through to `repair_executor` unchanged
        so the Rejudge inside it re-evaluates under the *same* conditions,
        never the previous silent fallback to a fixed, criteria-less
        `correctness`/`safety`/`coherence` triad that let a Rejudge accept
        with no per-criterion evidence at all (see `repair_live_
        integration.attempt_live_repair()`'s own `rejudge_criteria`
        docstring for the reproduced defect and full fix rationale). Empty
        whenever `gated` itself carries no `criterion_results` (the
        pre-existing unstructured general-quality shape) -- there is no
        Frozen Criterion set to preserve, so the Rejudge correctly keeps
        its prior unstructured shape unchanged."""
        disposition = resolve_evaluation_disposition(
            mode=judge_mode,
            execution_state=gated.execution_state,
            recommendation=gated.recommendation,
        )
        eligibility: RepairEligibility | None = None
        repair_result: RepairExecutionResult | None = None
        judge_authorized = False
        main_authorized = False
        judge_is_enforcing = judge_mode is EvaluationMode.ENFORCE
        main_requests_repair = (
            main_action is not None
            and main_action.executed_disposition is SemanticFinalDisposition.REPAIR_REQUESTED
        )
        judge_gate_open = (
            judge_is_enforcing and repair_mode is not None and repair_mode_controller is not None
        )
        if gated.execution_state is EvaluationExecutionState.COMPLETED and (
            judge_gate_open or main_requests_repair
        ):
            judge_eligibility: RepairEligibility | None = None
            if judge_gate_open:
                # `judge_gate_open`'s own definition already requires
                # `repair_mode is not None` -- re-asserted here only so
                # the type checker narrows it the same way this branch's
                # own guard already guarantees at runtime.
                assert repair_mode is not None
                judge_eligibility = resolve_repair_eligibility(
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
            judge_authorized = (
                judge_eligibility is RepairEligibility.ELIGIBLE
                and disposition.repair_requested
                and repair_mode is RepairMode.ENFORCE
            )
            main_eligibility: RepairEligibility | None = None
            if main_requests_repair:
                main_eligibility = resolve_repair_eligibility(
                    mode=RepairMode.ENFORCE,
                    guardrail_denied=False,
                    judge_recommendation=gated.recommendation,
                    budget=LIVE_REPAIR_BUDGET,
                    usage=_ZERO_REPAIR_USAGE,
                )
            main_authorized = main_eligibility is RepairEligibility.ELIGIBLE
            # Judge-origin Eligibility is reported whenever it was
            # classified at all (`judge_gate_open`), matching the
            # pre-existing Status/observability contract unchanged by this
            # Rework: a Status reader must see "this would be Eligible"
            # even under OBSERVE/OFF, never silently blank just because
            # Main Governance's own separate request happened to exist
            # too. Only falls back to Main-origin Eligibility when Judge
            # never classified one at all (e.g. `judge_mode != enforce`).
            eligibility = judge_eligibility if judge_eligibility is not None else main_eligibility
            if (judge_authorized or main_authorized) and repair_executor is not None:

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
                violation_lines = tuple(
                    (
                        f"criterion={item.criterion_id}; "
                        f"disposition={item.disposition.value}; "
                        f"reason={item.reason_code or 'not_supplied'}; "
                        f"evidence={','.join(item.evidence_refs) or 'not_supplied'}"
                    )
                    for item in gated.criterion_results
                    if item.disposition is not JudgeCriterionDisposition.PASS
                )
                repair_feedback = gated.reasoning or ""
                if violation_lines:
                    repair_feedback = "\n".join(
                        (
                            repair_feedback or "Judge reported criterion violations.",
                            *violation_lines,
                        )
                    )
                repair_result = repair_executor(
                    request_id=context.request_id,
                    model_key=context.model_key,
                    user_input=context.user_input,
                    original_answer=context.assistant_content,
                    before_recommendation=gated.recommendation,
                    judge_reasoning=repair_feedback,
                    dialogue_context=context.dialogue_context,
                    evidence_context=context.evidence_context,
                    governance_post_hook=governance_post_hook,
                    guardrail_post_hook=guardrail_post_hook,
                    cancellation=cancellation,
                    model_runtime_info=context.model_runtime_info,
                    stage_hook=_apply_repair_stage,
                    stage_budget=stage_budget,
                    rejudge_service=rejudge_service,
                    rejudge_model_key=rejudge_model_key,
                    rejudge_role=rejudge_role,
                    language=frozen_language,
                    # The synchronous ENFORCE path has not committed the
                    # source Turn yet. Its accepted Repair becomes that
                    # Turn's Canonical Presented Final instead of creating
                    # a second derived Turn behind the user's answer.
                    persist_accepted_attempt=not context.enforce_presented_final,
                    # Controller Review IR-02 fix: the same Frozen Criterion
                    # set `gated` was scored against this Run.
                    rejudge_criteria=rejudge_criteria,
                    # Controller Review (2026-09-05 00:35, IR-R4-01) fix:
                    # the same Registry this Hook's own Prompt Build/Decode
                    # Stages already share, so Repair's own Rejudge Token-
                    # counting Stage is tracked by, and Bounded-Joined at
                    # Shutdown by, the identical single Owner.
                    tracked_stage_registry=tracked_stage_registry,
                    # Gemma Judge-only Constrained Decoding Rework (WU-03):
                    # `None` for every caller except the real Gemma-
                    # configured dedicated dispatch (`_run_selene_dispatch`
                    # reads it off its own `evaluator.structured_output_
                    # schema_factory`) -- the identical Factory the initial
                    # Judge dispatch used constrains the Rejudge Call too.
                    rejudge_structured_output_schema_factory=(
                        rejudge_structured_output_schema_factory
                    ),
                    # Gemma Constrained Decoding Final Contract Micro Rework
                    # (IR-FC-01): `None` for every caller except the real
                    # Gemma-configured dedicated dispatch (`_run_selene_
                    # dispatch` reads it off its own `evaluator.sampling_
                    # overrides`) -- the identical frozen Sampling contract
                    # the initial Judge Batches used also governs the
                    # Rejudge Call.
                    rejudge_sampling_overrides=rejudge_sampling_overrides,
                )
        execution_state = gated.execution_state.value
        failure_reason: str | None = (
            gated.failure_reason.value if gated.failure_reason is not None else None
        )
        # P9-1 Judge/Governance Rework (WU-03): only set when a Repair
        # Attempt genuinely ran (never fabricated from an Eligibility
        # check alone) — see `LiveJudgeResult.repair_requested_by`'s own
        # docstring.
        repair_requested_by: str | None = None
        if repair_result is not None:
            repair_requested_by = (
                "judge_and_main"
                if judge_authorized and main_authorized
                else "judge"
                if judge_authorized
                else "main_governance"
            )
        if (
            repair_result is not None
            and not repair_result.accepted
            and repair_result.rejected_reason is not None
        ):
            failure_reason = repair_result.rejected_reason
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
            # P9-1 Component Independence Rework (WU-04, confirmed real
            # Failure: `judge_run_evidence` for a genuinely `independent_
            # artifact`-role Gemma Run recorded `metadata_fields.
            # model_identity` as Main's own `main.qwen3-4b-q4-k-m` instead
            # of the real executing Gemma identity, even though the UI's
            # own Executed Provider correctly showed Gemma): this shared
            # tail serves both the Main-shared dispatch AND the dedicated
            # Selene/Gemma dispatch (`_run_selene_dispatch`'s own caller
            # above) -- `context.model_key` is only ever the real executing
            # identity for the former. `executed_provider` (already
            # correctly populated by both callers) is the real executing
            # identity either way; `context.model_key` is kept only as the
            # legacy fallback for the one deployment shape with no Provider
            # Selection concept at all (`executed_provider is None`).
            model_key=executed_provider or context.model_key,
            # R2-WU-02 (Controller Review IR-CI-02): `executed_model_
            # runtime_info` is each caller's own already-correct Runtime
            # Info for the identity that actually executed -- Main's own
            # for the Main-shared branches, the Dedicated Role's own real
            # Load Receipt for Gemma/Selene. Never `context.model_runtime_
            # info` unconditionally (the confirmed bug: that stayed Main's
            # own even for a genuinely Dedicated Gemma Run).
            model_runtime_info=executed_model_runtime_info,
            configured_judge_provider=configured_judge_provider,
            active_judge_provider=active_judge_provider,
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
            call_count=call_count,
            seed=seed,
            config_digest_sha512=config_digest_sha512,
            prompt_digest_sha512_override=prompt_digest_sha512_override,
            batch_evidence_json=batch_evidence_json,
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
                failure_code = (
                    classify_evaluation_failure(failure_reason)
                    or EvaluationFailureCode.EVALUATION_INCONCLUSIVE
                )
                presented_content = present_evaluation_failure(
                    reason_code=failure_code,
                    frozen_language=frozen_language,
                ).message
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
                executed_provider=executed_provider,
                criteria_selected=criterion_counts.selected,
                criteria_evaluated=criterion_counts.evaluated,
                criteria_passed=criterion_counts.passed,
                criteria_deviated=criterion_counts.deviated,
                criteria_unknown=criterion_counts.unknown,
                criteria_not_applicable=criterion_counts.not_applicable,
                criteria_deferred=criterion_counts.deferred,
                judge_outcome=gated.recommendation.value,
                final_disposition=presentation_outcome,
                repair_rejudge_provider=(
                    repair_result.rejudge_model_identity if repair_result is not None else None
                ),
                repair_rejudge_role=(
                    repair_result.rejudge_role if repair_result is not None else None
                ),
                repair_requested_by=repair_requested_by,
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
        built_in_active: bool,
        active_adapter: object | None,
        provider_selection_wired: bool,
        run_stage_budget: StageBudgetProfile,
        frozen_language: str,
        role_turn_lease: object | None = None,
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
                built_in_active=built_in_active,
                active_adapter=active_adapter,
                provider_selection_wired=provider_selection_wired,
                run_stage_budget=run_stage_budget,
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
        finally:
            # P6-RR-R21 (resolves P6-CODEX-086): exactly-once Release,
            # covering every exit out of the `try` above — the normal
            # return, and the `except` branch's own typed-failure
            # fallback. `_run_judge_and_repair` (Prompt Build, Inference
            # Stage, Decode, Repair/Rejudge) is the only place in this
            # Run that ever touches the leased Adapter; nothing after this
            # point (Presented Final normalization, Evidence Recorder
            # scheduling, `composition.record_result`) does.
            if outcome.deferred_role_release is None:
                _end_judge_role_turn(role_turn_lease)
            else:
                _release_judge_role_turn_when_done(
                    lease=role_turn_lease,
                    future=outcome.deferred_role_release,
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
                    context.assistant_content
                    if accepted
                    else present_evaluation_failure(
                        reason_code=(
                            classify_evaluation_failure(result.failure_reason)
                            or EvaluationFailureCode.EVALUATION_INCONCLUSIVE
                        ),
                        frozen_language=frozen_language,
                    ).message
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
        frozen_language: str,
    ) -> LiveJudgeResult:
        failure_code = (
            classify_evaluation_failure(failure_reason)
            or EvaluationFailureCode.EVALUATION_INCONCLUSIVE
        )
        return LiveJudgeResult(
            request_id=context.request_id,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            recommendation="unknown",
            confidence=0.0,
            execution_state=execution_state,
            failure_reason=failure_reason,
            presentation_outcome="safe_fallback",
            candidate_withheld=True,
            presented_content=present_evaluation_failure(
                reason_code=failure_code,
                frozen_language=frozen_language,
            ).message,
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
        # P6-RR-N-WU-001 (Production Wiring Delta): frozen into the same
        # Mode-Freeze moment as judge_mode/repair_mode/recording_mode above
        # — never re-read mid-Run, exactly the same discipline P6-CODEX-020/
        # 029 already established for the other three.
        built_in_active = _judge_provider_is_built_in()
        frozen_guard_mode = _frozen_guard_mode()
        # P6-RR-R21 (resolves P6-CODEX-086): `provider_selection_wired` is
        # a bare None-check on the resolver Callable itself — no Lease is
        # acquired by computing it, so it stays safe to read before the
        # Judge OFF check below.
        provider_selection_wired = (
            begin_judge_role_turn is not None
            or begin_judge_role_turn_with_cancellation is not None
        )
        if judge_mode is EvaluationMode.OFF:
            _record_semantic_deferred(context.request_id, SemanticDeferredReason.JUDGE_OFF)
            composition.mark_skipped(request_id=context.request_id, reason="judge_off")
            return None
        # P6-RR-R2-WU-001, extended P6-RR-R21: resolved once here, not when
        # Built-in is active (Built-in dispatches through `_run_built_in_
        # semantic_judge`, which never consults an Adapter at all) — and
        # deliberately *after* the Judge OFF early-return immediately
        # above. `begin_judge_role_turn` now genuinely acquires a Turn
        # Lease (P6-RR-R21, resolves P6-CODEX-086); resolving it before an
        # OFF-mode Turn's early `return None` would acquire a Lease this
        # function then never releases (Judge OFF never reaches `_run_
        # judge`, the sole `_end_judge_role_turn` call site).
        cancellation = context.cancellation or CancellationToken()
        active_adapter, judge_role_lease = (
            (None, None)
            if built_in_active
            else _begin_judge_role_turn(cancellation)
        )
        try:
            correlation_snapshot = _semantic_snapshot(context.request_id)
            run_stage_budget = _frozen_stage_budget(
                semantic_snapshot=correlation_snapshot,
                active_adapter=active_adapter,
            )
            # P6-RR-R14-WU-006/007 (Post-Claude Independent Review Rework,
            # resolves P6-CODEX-076): the Turn's own frozen Response
            # Language (`context.response_language`) is the sole source —
            # never the Semantic Snapshot's `language` field, which is
            # `None` whenever Main Runtime Governance is OFF (Judge runs
            # independently of it) and, even when present, historically
            # reflected a static bootstrap-time config default rather than
            # this Turn's actual selected language.
            frozen_language = context.response_language
            run_generation = composition.begin_run(
                request_id=context.request_id,
                correlation=_RunCorrelation(
                    started_at=datetime.now(UTC).isoformat(),
                    language=frozen_language,
                    frozen_main_mode=(
                        correlation_snapshot.frozen_main_mode
                        if correlation_snapshot is not None
                        else None
                    ),
                    frozen_guard_mode=frozen_guard_mode,
                    frozen_judge_mode=judge_mode.value,
                    frozen_repair_mode=(repair_mode.value if repair_mode is not None else None),
                    recording_mode=recording_mode.value,
                    configured_provider=(
                        correlation_snapshot.configured_provider
                        if correlation_snapshot is not None
                        else context.model_key
                    ),
                    active_provider=(
                        correlation_snapshot.active_provider
                        if correlation_snapshot is not None
                        else context.model_key
                    ),
                    budget_profile=run_stage_budget.profile_id,
                ),
            )
        except Exception:
            # P6-RR-R21 (resolves P6-CODEX-086) safety net: none of the
            # three dispatch branches below (Built-in / ENFORCE-sync /
            # OBSERVE-background — each of which owns its own eventual
            # `_end_judge_role_turn` Release) has run yet, so nothing else
            # will ever Release this Lease if this Run-Correlation setup
            # itself raises. Release exactly once here and skip the Run
            # outright, rather than dispatch a real Model Call against an
            # inconsistent Run-Correlation state.
            _end_judge_role_turn(judge_role_lease)
            composition.mark_skipped(request_id=context.request_id, reason="hook_internal_error")
            return None
        if built_in_active:
            # P6-RR-R14-WU-003/004 (Post-Claude Independent Review Rework,
            # resolves the rest of P6-CODEX-075): Built-in performs zero
            # I/O and zero Model Calls — it is fully synchronous and
            # deterministic, so it never needs the Background-Task +
            # Timeout-Wait machinery the Model-backed paths require (that
            # machinery exists to serialize real shared Model access;
            # nothing here ever touches it). Resolving it inline removes
            # the 0ms-Pipeline-Budget/Background-Thread-Scheduling Race
            # entirely — the previous `wait_timeout_seconds=0` path could
            # spuriously report `deadline_exceeded` purely from thread
            # scheduling latency between `start_background()` returning
            # and the Worker Thread actually running, never a genuine
            # Built-in failure (Built-in cannot fail; its Recommendation
            # is honestly `unknown`, never a Model error).
            built_in_outcome = _run_judge(
                context,
                judge_mode=judge_mode,
                repair_mode=repair_mode,
                recording_mode=recording_mode,
                cancellation=cancellation,
                run_generation=run_generation,
                built_in_active=True,
                active_adapter=None,
                provider_selection_wired=provider_selection_wired,
                run_stage_budget=run_stage_budget,
                frozen_language=frozen_language,
                # Built-in never resolves an Adapter (see the `hook()`
                # resolution above), so `judge_role_lease` is always
                # already `None` on this branch — passed through rather
                # than a literal `None` so this call site stays correct
                # even if that invariant ever changes.
                role_turn_lease=judge_role_lease,
            )
            built_in_result = built_in_outcome.result
            if not context.enforce_presented_final:
                return None
            return JudgeCompletionDecision(
                presented_content=built_in_result.presented_content
                or present_evaluation_failure(
                    reason_code=EvaluationFailureCode.EVALUATION_INCONCLUSIVE,
                    frozen_language=frozen_language,
                ).message,
                presentation_outcome=built_in_result.presentation_outcome or "safe_fallback",
                candidate_withheld=built_in_result.candidate_withheld,
                # Evidence was already published synchronously above
                # (`_run_judge(..., record_terminal=True)`'s own
                # unconditional `_start_evidence_publication` call) —
                # nothing further for the caller to authorize/discard.
                finalize_evidence=None,
            )
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
                        built_in_active=built_in_active,
                        active_adapter=active_adapter,
                        provider_selection_wired=provider_selection_wired,
                        run_stage_budget=run_stage_budget,
                        frozen_language=frozen_language,
                        role_turn_lease=judge_role_lease,
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
                # P6-RR-R21 (resolves P6-CODEX-086): `_run_enforcement` (the
                # sole `_run_judge` call, and therefore the sole `_end_
                # judge_role_turn` Release, on this branch) never runs when
                # the Coordinator refuses the slot — the Lease `hook()`
                # already acquired above must still be Released here, or it
                # leaks for this Run's entire remaining lifetime.
                _end_judge_role_turn(judge_role_lease)
                result = _safe_enforcement_result(
                    context,
                    execution_state="failed",
                    failure_reason="model_busy",
                    frozen_language=frozen_language,
                )
                composition.record_result(result, run_generation=run_generation)
                _record_semantic_deferred(
                    context.request_id, SemanticDeferredReason.PROVIDER_UNAVAILABLE
                )
            else:
                # A production caller does not own this deadline.  It is
                # derived from the same Active Provider budget frozen for this
                # run; tests may supply a narrower explicit probe bound.
                wait_timeout_seconds = (
                    enforce_wait_timeout_seconds
                    if enforce_wait_timeout_seconds is not None
                    else run_stage_budget.enforce_pipeline_budget_ms / 1000
                )
                cancel_grace_seconds = (
                    enforce_cancel_grace_seconds
                    if enforce_cancel_grace_seconds is not None
                    else run_stage_budget.cancel_grace_ms / 1000
                )
                deadline = time.monotonic() + wait_timeout_seconds
                while True:
                    # Cancellation has deterministic priority over a
                    # simultaneous Worker completion. This is what makes a
                    # User Stop win the terminal race instead of becoming a
                    # Safe-Fallback ``completed`` event.
                    if cancellation.is_cancelled():
                        # P9-1 Component Independence Rework (WU-04), Race-
                        # fixed by R2-WU-03 (Controller Review IR-CI-03),
                        # residual Race fixed by R3-WU-03 (Controller
                        # Review IR-R2-03): a signalled Cancellation Token
                        # has at least two structurally distinct real
                        # origins this module can itself tell apart -- a
                        # genuine external Stop/disconnect
                        # (`ConversationGenerationSession.request_cancel()`/
                        # `force_cancel()`, never routed through `model_
                        # access_coordinator`) and Main-priority preemption
                        # (`ModelAccessCoordinator.acquire_main()` signalling
                        # this exact Run's own registered `cancel` directly,
                        # with no User/Client action at all -- see that
                        # Coordinator's own `was_preempted()` docstring).
                        # Reporting both as the same generic `cancelled_by_
                        # request` misattributes an ordinary Main-priority
                        # scheduling event as if the User had asked to stop,
                        # which they did not.
                        #
                        # R3-WU-03: this Wait Loop runs on the caller's own
                        # thread. The Worker's own Terminal boundary
                        # (`ModelAccessCoordinator.start_background()`'s own
                        # `_run()` `finally`) discards this exact `task_id`
                        # from `_preempted_task_ids` the INSTANT the Worker
                        # itself returns -- which can genuinely happen
                        # before this Loop's own next iteration runs (the
                        # Worker completing first, then this Loop's own
                        # `cancellation.is_cancelled()` check landing after
                        # that discard already occurred, a real Schedule a
                        # Controller Probe reproduced). A fresh `was_
                        # preempted()` re-classification at that point would
                        # then wrongly see `False` and silently overwrite
                        # the Worker's own ALREADY-correct classification
                        # with a generic `cancelled_by_request`. When the
                        # Worker has already produced its own genuinely
                        # terminal `cancelled` outcome, THAT stored
                        # classification is authoritative and is reused
                        # verbatim here -- never re-derived from a
                        # bookkeeping flag that may have already been
                        # cleaned up.
                        #
                        # R4-WU-03 (Controller Review IR-R3-03): an ordinary
                        # Worker `failed` outcome is deliberately EXCLUDED
                        # from this reuse -- only a Worker's own already-
                        # classified `cancelled` is authoritative here. A
                        # `failed` result (e.g. a genuine Model/Decode
                        # error, unrelated to Cancellation) that happens to
                        # become Ready at the exact instant a User Stop or
                        # Main-priority Preemption is detected must never
                        # silently override that Cancellation with the
                        # unrelated Failure -- "Cancellation has
                        # deterministic priority" (this Loop's own opening
                        # comment) applies to a genuine Cancellation origin
                        # racing a Worker Failure exactly as much as it
                        # already applies to a Worker Completion; reusing a
                        # `failed` Worker outcome here previously let an
                        # ordinary Failure silently masquerade as this
                        # Turn's own outcome instead of surfacing as the
                        # User Stop / Main-priority Cancellation that
                        # actually occurred. A `failed` outcome always falls
                        # through to the fresh classification below, exactly
                        # like a still-running Worker would.
                        worker_outcome = outcome_holder[0] if outcome_holder else None
                        if (
                            result_ready.is_set()
                            and worker_outcome is not None
                            and worker_outcome.result.execution_state == "cancelled"
                        ):
                            result = worker_outcome.result
                        else:
                            failure_reason = (
                                "cancelled_by_main_priority_preemption"
                                if model_access_coordinator.was_preempted(
                                    task_id=context.request_id
                                )
                                else "cancelled_by_request"
                            )
                            result = _safe_enforcement_result(
                                context,
                                execution_state="cancelled",
                                failure_reason=failure_reason,
                                frozen_language=frozen_language,
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
                                frozen_language=frozen_language,
                            )
                        )
                        break
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        result = _safe_enforcement_result(
                            context,
                            execution_state="failed",
                            failure_reason="deadline_exceeded",
                            frozen_language=frozen_language,
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
                if not result_ready.is_set() and cancel_grace_seconds > 0:
                    result_ready.wait(timeout=cancel_grace_seconds)
                composition.record_result(result, run_generation=run_generation)
            return JudgeCompletionDecision(
                presented_content=result.presented_content
                or present_evaluation_failure(
                    reason_code=EvaluationFailureCode.EVALUATION_INCONCLUSIVE,
                    frozen_language=frozen_language,
                ).message,
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
                built_in_active=built_in_active,
                active_adapter=active_adapter,
                provider_selection_wired=provider_selection_wired,
                run_stage_budget=run_stage_budget,
                frozen_language=frozen_language,
                role_turn_lease=judge_role_lease,
            )

        started = model_access_coordinator.start_background(
            task_id=context.request_id,
            cancel=cancellation.cancel,
            target=_run_background,
        )
        if not started:
            # P6-RR-R21 (resolves P6-CODEX-086): `_run_background` (the
            # sole `_run_judge` call, and therefore the sole `_end_judge_
            # role_turn` Release, on this OBSERVE path) never runs when the
            # Coordinator refuses the slot — Release the Lease `hook()`
            # already acquired above here, or it leaks for this Run's
            # entire remaining lifetime.
            _end_judge_role_turn(judge_role_lease)
            # Never queue, never block the caller — a Main Turn or another
            # Background Task already owns the shared Model; this Turn's
            # Judge Run is skipped outright (Current state stays/returns to
            # idle, never a stale or fabricated result).
            composition.mark_skipped(
                request_id=context.request_id,
                reason="model_busy",
                run_generation=run_generation,
            )
            _record_semantic_deferred(
                context.request_id, SemanticDeferredReason.PROVIDER_UNAVAILABLE
            )
        return None

    return hook, composition


def _batch_dispatch_evidence_json(batch_evidence: tuple[BatchDispatchEvidence, ...]) -> str | None:
    """Gemma Judge-only Constrained Decoding Rework (WU-05): a compact JSON
    Array of every real Batch this Run made -- digests/counts/enums/numbers
    only (`raw_output_sha512`/`raw_output_byte_length` stand in for the Raw
    Model output text itself, never persisted). `None` (never `"[]"`) when
    no Batch ran at all, so a Reader can tell "the still-unbatched Main-self
    general-quality dispatch" apart from "a batched dispatch that
    genuinely made zero Batch Calls" (the latter should not occur in
    practice, but this keeps the two honestly distinguishable)."""
    if not batch_evidence:
        return None
    entries = [
        {
            "batch_index": item.batch_index,
            "prompt_digest_sha512": item.prompt_digest_sha512,
            "expected_criterion_ids_digest_sha512": item.expected_criterion_ids_digest_sha512,
            "expected_criterion_count": item.expected_criterion_count,
            "max_new_tokens": item.parameters.max_new_tokens,
            "seed": item.parameters.seed,
            "temperature": item.parameters.temperature,
            "top_p": item.parameters.top_p,
            "top_k": item.parameters.top_k,
            "min_p": item.parameters.min_p,
            "structured_output_enabled": item.parameters.structured_output is not None,
            "structured_output_schema_digest_sha512": (
                item.parameters.structured_output.schema_digest_sha512
                if item.parameters.structured_output is not None
                else None
            ),
            "finish_reason": item.finish_reason,
            "prompt_tokens": item.prompt_tokens,
            "completion_tokens": item.completion_tokens,
            "raw_output_byte_length": item.raw_output_byte_length,
            "raw_output_sha512": item.raw_output_sha512,
            "strict_decode_state": item.strict_decode_state,
            "strict_decode_reason": item.strict_decode_reason,
        }
        for item in batch_evidence
    ]
    return json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _batch_dispatch_prompt_digest_sha512(
    batch_evidence: tuple[BatchDispatchEvidence, ...],
) -> str:
    """WU-05: a genuine, real-content-derived digest for the flat legacy
    `prompt_digest_sha512` field -- the SHA-512 of the ordered concatenation
    of every real per-Batch Prompt Digest, never a fixed description-string
    Placeholder.

    Gemma Final Contract Micro Rework (IR-FC-04) fix: previously returned
    `None` when no Batch ran, which `record_judge_evidence()` interpreted
    as "no override supplied" and fell back to hashing the caller's own
    `prompt` argument -- for this Dedicated batched dispatch route, that
    argument is never real Prompt content, only the fixed description
    string `"(dedicated Selene evaluator: prompt built internally by
    SelenePromptAdapter)"`. A genuine Model-Call-0 Run (no real Batch ever
    reached the Model) therefore still recorded a legitimate-looking
    128-hex-digit `prompt_digest_sha512`, indistinguishable from a real
    Prompt Digest. Returning the literal `"unavailable"` string here
    instead -- the same fixed-string-for-truly-unknown convention already
    used by `config_digest_sha512`/`artifact_digest_sha512`/`backend_key`
    in this same Evidence record -- is passed straight through as a
    non-`None` override, so it is recorded verbatim rather than triggering
    that fallback hash."""
    if not batch_evidence:
        return "unavailable"
    joined = "".join(item.prompt_digest_sha512 for item in batch_evidence)
    return hashlib.sha512(joined.encode("utf-8")).hexdigest()


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
    configured_judge_provider: str | None = None,
    active_judge_provider: str | None = None,
    call_count: int = 1,
    seed: int | None = None,
    config_digest_sha512: str = _LIVE_JUDGE_CONFIG_DIGEST_SHA512,
    prompt_digest_sha512_override: str | None = None,
    batch_evidence_json: str | None = None,
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
            # R2-WU-02 (Controller Review IR-CI-02): `model_key` here is
            # always the Executed Judge Provider (each caller already
            # resolves it that way -- see `_finalize_judge_dispatch()`'s
            # own `executed_provider or context.model_key`), never the
            # Main Candidate being evaluated. `context.model_key` (the
            # Main Model actually evaluated) is a distinct, separate
            # identity, recorded below unconditionally regardless of which
            # Judge Role executed this Run.
            model_identity=model_key,
            evaluated_model_identity=context.model_key,
            configured_judge_provider=configured_judge_provider,
            active_judge_provider=active_judge_provider,
            # P6-CODEX-022: the Artifact Digest and Backend Identity/Version
            # actually loaded — `model_identity` alone (a bare config key) is
            # not enough to distinguish a re-download or backend upgrade of the
            # same key, which P6-LJG-002's "necessary Traces" also requires.
            # R2-WU-02: `model_runtime_info` here must already be the
            # EXECUTED identity's own Runtime Info (each caller resolves
            # this correctly per dispatch route -- Main-shared routes pass
            # `context.model_runtime_info` because that IS the executing
            # identity there; the dedicated Gemma/Selene route passes its
            # own Loaded Adapter's Runtime Info instead, never Main's).
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
            call_count=call_count,
            seed=seed,
            config_digest_sha512=config_digest_sha512,
            prompt_digest_sha512_override=prompt_digest_sha512_override,
            batch_evidence_json=batch_evidence_json,
        )

    return _PendingJudgeEvidence(publish_action=_publish)
