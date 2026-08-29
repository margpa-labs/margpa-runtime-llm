"""Local-private `/api/v5/feature-modes` routes (Phase 6-G-WU-004, Judge
Live Result added P6-CODEX-001).

Exposes Judge/Repair/Recording Mode status and toggle, each backed by its
own independent Mode Controller (Acceptance P6-ACC-025: "Judge Mode and
Repair Mode are independent, Default OFF"). Toggling a Mode here only
changes what that Controller reports — the Mode value itself is read by the
live Judge Hook at `bootstrap/judge_live_integration.py`, which is the
actual place that decides whether to invoke the Model (this route never
calls it directly). `judge.last_result` surfaces the most recent Live Judge
outcome (if any) so a Golden Path can observe it without a separate
Recording sink (P6-CODEX-004 remains a distinct, larger integration step).
Judge ENFORCE now owns the Presented Final boundary and can route one bounded
Repair/Rejudge attempt; Recording remains a separate, orthogonal local sink.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from margpa_runtime_llm.bootstrap.judge_live_integration import LiveJudgeResult
from margpa_runtime_llm.bootstrap.recording_live_integration import RecordingOutcome
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode
from margpa_runtime_llm.modules.runtime_model_control.application.role_lifecycle_manager import (
    ModeReadResult,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderRuntimeState,
    ProviderSelectionError,
    ProviderSelectionErrorCode,
)
from margpa_runtime_llm.modules.runtime_observability.domain.recording import RecordingMode

from .contracts import WebRuntime

FEATURE_MODES_API_PREFIX = "/api/v5/feature-modes"


class _FeatureModesContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ModeSnapshotResponse(_FeatureModesContract):
    enabled: bool
    revision: int | None = None
    current_mode: str | None = None


class JudgeLastResultResponse(_FeatureModesContract):
    request_id: str
    judge_role: str
    recommendation: str
    confidence: float
    execution_state: str
    failure_reason: str | None = None
    repair_eligibility: str | None = None
    repair_outcome: str | None = None
    repair_accepted: bool | None = None
    repair_new_turn_id: str | None = None
    presentation_outcome: str | None = None
    candidate_withheld: bool = False
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


class JudgeModeSnapshotResponse(ModeSnapshotResponse):
    # Current-Request Judge Run state (P6-CODEX-012, partial): `idle` means
    # no Judge Run is in flight right now, so `last_result` (if any) is
    # necessarily from a *previous* Turn — a Status reader must not read
    # `last_result` as "this Turn's outcome" while `state` is `running`.
    state: str | None = None
    current_request_id: str | None = None
    last_result: JudgeLastResultResponse | None = None
    historical_last_result: JudgeLastResultResponse | None = None


class RecordingOutcomeResponse(_FeatureModesContract):
    request_id: str
    ok: bool
    degraded_reason: str | None = None


class RequestCorrelationSummaryResponse(_FeatureModesContract):
    """P6-RR-R19-WU-001..004 (Post-Claude Independent Review Rework,
    resolves P6-CODEX-082): the single Server-side Join of everything a
    Status reader needs about the Current Request — Turn Metadata (from
    `RequestCorrelationRegistry`, valid from the instant the Turn
    started, not only once it completes), Judge Result (Outcome, Final
    Disposition, Failure, Configured/Active/Executed Provider, Budget,
    Frozen Modes — all already carried by `JudgeLastResultResponse`), and
    both Recording outcomes — never assembled by the client from
    separately-polled, potentially inconsistent pieces."""

    request_id: str
    status: str
    started_at: str
    completed_at: str | None = None
    judge_result: JudgeLastResultResponse | None = None
    turn_recording: RecordingOutcomeResponse | None = None
    judge_evidence_recording: RecordingOutcomeResponse | None = None


class RecordingCorrelationResponse(_FeatureModesContract):
    """P6-RR-R15-WU-001..004 (resolves P6-CODEX-077), extended
    P6-RR-R19-WU-001..004 (resolves P6-CODEX-082): `request_id` anchors on
    `RequestCorrelationRegistry.current_request_id()` — set the instant a
    Turn starts, independent of whether Judge or Recording have run yet —
    never on a completion-only proxy like Recording's own last outcome
    (which stays stuck on the *previous* Turn while a new one is still in
    flight, the exact "opens a moment after sending shows the previous
    Turn" lag this fix closes). `current` is the full Server-side Join;
    `current_turn`/`current_judge_evidence` are kept for backward
    compatibility with callers that only need those two fields directly.
    Only records sharing the Current request_id are Current; everything
    else falls into `historical_or_unmatched`."""

    request_id: str | None = None
    current: RequestCorrelationSummaryResponse | None = None
    current_turn: RecordingOutcomeResponse | None = None
    current_judge_evidence: RecordingOutcomeResponse | None = None
    historical_or_unmatched: tuple[RecordingOutcomeResponse, ...] = ()


class RecordingModeSnapshotResponse(ModeSnapshotResponse):
    # `last_outcome` reflects the Turn-level recorder only (never Judge
    # Evidence's own, separate recorder) — see `judge_evidence_last_outcome`
    # below for that one, kept distinct so a reader never conflates the two.
    last_outcome: RecordingOutcomeResponse | None = None
    judge_evidence_last_outcome: RecordingOutcomeResponse | None = None
    correlation: RecordingCorrelationResponse | None = None


class FeatureModesStatusResponse(_FeatureModesContract):
    judge: JudgeModeSnapshotResponse
    repair: ModeSnapshotResponse
    recording: RecordingModeSnapshotResponse


class ApplyJudgeModeRequest(_FeatureModesContract):
    requested_mode: EvaluationMode


class ApplyRepairModeRequest(_FeatureModesContract):
    requested_mode: RepairMode


class ApplyRecordingModeRequest(_FeatureModesContract):
    requested_mode: RecordingMode


def _last_result_response(last_result: LiveJudgeResult) -> JudgeLastResultResponse:
    return JudgeLastResultResponse(
        request_id=last_result.request_id,
        judge_role=last_result.judge_role.value,
        recommendation=last_result.recommendation,
        confidence=last_result.confidence,
        execution_state=last_result.execution_state,
        failure_reason=last_result.failure_reason,
        repair_eligibility=last_result.repair_eligibility,
        repair_outcome=last_result.repair_outcome,
        repair_accepted=last_result.repair_accepted,
        repair_new_turn_id=last_result.repair_new_turn_id,
        presentation_outcome=last_result.presentation_outcome,
        candidate_withheld=last_result.candidate_withheld,
        started_at=last_result.started_at,
        completed_at=last_result.completed_at,
        frozen_main_mode=last_result.frozen_main_mode,
        frozen_guard_mode=last_result.frozen_guard_mode,
        frozen_judge_mode=last_result.frozen_judge_mode,
        frozen_repair_mode=last_result.frozen_repair_mode,
        recording_mode=last_result.recording_mode,
        configured_provider=last_result.configured_provider,
        active_provider=last_result.active_provider,
        executed_provider=last_result.executed_provider,
        budget_profile=last_result.budget_profile,
        criteria_selected=last_result.criteria_selected,
        criteria_evaluated=last_result.criteria_evaluated,
        criteria_passed=last_result.criteria_passed,
        criteria_deviated=last_result.criteria_deviated,
        criteria_unknown=last_result.criteria_unknown,
        criteria_not_applicable=last_result.criteria_not_applicable,
        criteria_deferred=last_result.criteria_deferred,
        judge_outcome=last_result.judge_outcome,
        final_disposition=last_result.final_disposition,
        failure_message=last_result.failure_message,
        failure_language=last_result.failure_language,
        repair_rejudge_provider=last_result.repair_rejudge_provider,
        repair_rejudge_role=last_result.repair_rejudge_role,
    )


def _read_judge_mode(runtime: WebRuntime) -> ModeReadResult:
    """P6-RR-R17-WU-001..004 (resolves P6-CODEX-080): the sole place Judge
    Mode is ever read from `judge_mode_control` directly — every other
    caller in this module goes through this function (either live, for an
    unbound `role_provider_lifecycle`, or via a `CompositeRoleStatus`
    already read under `RoleProviderLifecycleManager`'s own Lock) so a
    Reader never independently re-reads Mode outside that Lock while a
    Transition is in flight."""
    controller = runtime.judge_mode_control
    if controller is None:
        return ModeReadResult(revision=None, value=EvaluationMode.OFF.value)
    snapshot = controller.mode_snapshot()
    return ModeReadResult(revision=snapshot.revision, value=snapshot.current_mode.value)


def _read_guard_mode(runtime: WebRuntime) -> ModeReadResult:
    composition = runtime.guardrail_governance_composition
    if composition is None:
        return ModeReadResult(revision=None, value=GovernanceMode.OFF.value)
    snapshot = composition.mode_controller.mode_snapshot()
    return ModeReadResult(revision=snapshot.revision, value=snapshot.current_mode.value)


def _judge_snapshot(
    runtime: WebRuntime, *, mode: ModeReadResult | None = None
) -> JudgeModeSnapshotResponse:
    controller = runtime.judge_mode_control
    if controller is None:
        return JudgeModeSnapshotResponse(enabled=False)
    resolved_mode = mode if mode is not None else _read_judge_mode(runtime)
    composition = runtime.judge_governance_composition
    last_result = composition.last_result() if composition is not None else None
    current_request_id = composition.current_request_id() if composition is not None else None
    is_current = (
        last_result is not None
        and last_result.request_id == current_request_id
        and resolved_mode.value != EvaluationMode.OFF.value
    )
    return JudgeModeSnapshotResponse(
        enabled=True,
        revision=resolved_mode.revision,
        current_mode=resolved_mode.value,
        state=composition.current_state() if composition is not None else None,
        current_request_id=current_request_id,
        last_result=(
            _last_result_response(last_result) if last_result is not None and is_current else None
        ),
        historical_last_result=(
            _last_result_response(last_result)
            if last_result is not None and not is_current
            else None
        ),
    )


def _repair_snapshot(runtime: WebRuntime) -> ModeSnapshotResponse:
    controller = runtime.repair_mode_control
    if controller is None:
        return ModeSnapshotResponse(enabled=False)
    snapshot = controller.mode_snapshot()
    return ModeSnapshotResponse(
        enabled=True, revision=snapshot.revision, current_mode=snapshot.current_mode.value
    )


def _recording_outcome_response(
    outcome: RecordingOutcome | None,
) -> RecordingOutcomeResponse | None:
    if outcome is None:
        return None
    return RecordingOutcomeResponse(
        request_id=outcome.request_id,
        ok=outcome.ok,
        degraded_reason=outcome.degraded_reason,
    )


def _recording_snapshot(runtime: WebRuntime) -> RecordingModeSnapshotResponse:
    controller = runtime.recording_mode_control
    if controller is None:
        return RecordingModeSnapshotResponse(enabled=False)
    snapshot = controller.mode_snapshot()
    turn_outcome = _recording_outcome_response(
        runtime.recording_composition.last_outcome()
        if runtime.recording_composition is not None
        else None
    )
    judge_evidence_outcome = _recording_outcome_response(
        runtime.judge_evidence_recording_composition.last_outcome()
        if runtime.judge_evidence_recording_composition is not None
        else None
    )
    # P6-RR-R19-WU-001..004 (Post-Claude Independent Review Rework,
    # resolves P6-CODEX-082): Current Request Identity now comes from
    # `RequestCorrelationRegistry.current_request_id()` — set the instant
    # a Turn *starts*, before Judge/Repair/Recording ever run — never
    # from a completion-only proxy. The R15 fix (anchoring on Recording's
    # own last outcome rather than Judge's) correctly removed the
    # Judge-OFF staleness, but still only became correct *after* the
    # Turn's own Recording Hook fired; a brand-new in-flight Turn was
    # still shown as the *previous* one until then. A Registry entry is
    # authoritative the instant it exists, so this closes that residual
    # gap. When no Registry is wired (e.g. Feature Modes disabled at
    # Bootstrap), degrade to the prior Recording-outcome-anchored
    # behavior rather than losing Correlation entirely.
    registry = runtime.request_correlation_registry
    current_request_id = registry.current_request_id() if registry is not None else None
    if current_request_id is None and registry is None:
        current_request_id = turn_outcome.request_id if turn_outcome is not None else None
    current_entry = (
        registry.entry_for(current_request_id)
        if registry is not None and current_request_id is not None
        else None
    )
    current_turn = (
        turn_outcome
        if turn_outcome is not None and turn_outcome.request_id == current_request_id
        else None
    )
    current_judge_evidence = (
        judge_evidence_outcome
        if judge_evidence_outcome is not None
        and judge_evidence_outcome.request_id == current_request_id
        else None
    )
    outcomes = tuple(
        outcome
        for outcome in (turn_outcome, judge_evidence_outcome)
        if outcome is not None and outcome.request_id != current_request_id
    )
    current_judge_result = None
    judge_composition = runtime.judge_governance_composition
    if judge_composition is not None:
        last_judge_result = judge_composition.last_result()
        if last_judge_result is not None and last_judge_result.request_id == current_request_id:
            current_judge_result = _last_result_response(last_judge_result)
    current_summary = (
        RequestCorrelationSummaryResponse(
            request_id=current_request_id,
            status=current_entry.status if current_entry is not None else "pending",
            started_at=current_entry.started_at if current_entry is not None else "",
            completed_at=current_entry.completed_at if current_entry is not None else None,
            judge_result=current_judge_result,
            turn_recording=current_turn,
            judge_evidence_recording=current_judge_evidence,
        )
        if current_request_id is not None
        else None
    )
    return RecordingModeSnapshotResponse(
        enabled=True,
        revision=snapshot.revision,
        current_mode=snapshot.current_mode.value,
        last_outcome=turn_outcome,
        judge_evidence_last_outcome=judge_evidence_outcome,
        correlation=RecordingCorrelationResponse(
            request_id=current_request_id,
            current=current_summary,
            current_turn=current_turn,
            current_judge_evidence=current_judge_evidence,
            historical_or_unmatched=outcomes,
        ),
    )


def _project_status(
    runtime: WebRuntime, *, judge_mode: ModeReadResult | None = None
) -> FeatureModesStatusResponse:
    return FeatureModesStatusResponse(
        judge=_judge_snapshot(runtime, mode=judge_mode),
        repair=_repair_snapshot(runtime),
        recording=_recording_snapshot(runtime),
    )


def _runtime(request: Request) -> WebRuntime:
    runtime: WebRuntime = request.app.state.runtime
    return runtime


def create_feature_modes_router() -> APIRouter:
    router = APIRouter(prefix=FEATURE_MODES_API_PREFIX)

    @router.get("/status", response_model=FeatureModesStatusResponse)
    async def get_status(request: Request) -> FeatureModesStatusResponse:
        runtime = _runtime(request)
        if runtime.role_provider_lifecycle is not None:
            # P6-RR-R17-WU-001..004 (Post-Claude Independent Review Rework,
            # resolves P6-CODEX-080): Judge Mode is read through the same
            # Transition Lock `apply_mode_transition`/`apply_provider_
            # selection` hold for their whole critical section — never an
            # independent `judge_mode_control.mode_snapshot()` call that
            # could observe a torn Provider/Mode Tuple mid-Transition.
            composite = await asyncio.to_thread(
                runtime.role_provider_lifecycle.composite_status,
                read_judge_mode=lambda: _read_judge_mode(runtime),
                read_guard_mode=lambda: _read_guard_mode(runtime),
            )
            return _project_status(runtime, judge_mode=composite.judge_mode)
        return _project_status(runtime)

    @router.post("/judge", response_model=FeatureModesStatusResponse)
    async def apply_judge(
        request: Request, body: ApplyJudgeModeRequest
    ) -> FeatureModesStatusResponse:
        runtime = _runtime(request)
        if runtime.judge_mode_control is not None:
            judge_mode_control = runtime.judge_mode_control
            if runtime.role_provider_lifecycle is not None:
                # P6-RR-R13-WU-001..004 (Post-Claude Independent Review
                # Rework, resolves P6-CODEX-074/069/062): Mode commit now
                # happens *inside* `RoleProviderLifecycleManager`'s own
                # Lock, in the same call as Activation/Deactivation — never
                # a separate, later `apply_mode()` call outside that Lock,
                # which previously left a real TOCTOU window against a
                # concurrent Provider-Selection change.
                def _commit_judge_mode() -> None:
                    judge_mode_control.apply_mode(body.requested_mode)

                # P6-RR-R17-WU-001..004 (resolves P6-CODEX-080): the
                # returned CompositeRoleStatus is read *inside* the same
                # Lock the Transition itself just ran under — this
                # Response is built directly from it, never from a later,
                # separate `_project_status(runtime)` re-read (which could
                # legitimately race a concurrent request and end up
                # showing a Mode/Provider Tuple from a *different*
                # Transition than the one this call just committed).
                composite = await asyncio.to_thread(
                    runtime.role_provider_lifecycle.apply_mode_transition,
                    role=ModelRole.JUDGE,
                    target_mode_is_off=body.requested_mode is EvaluationMode.OFF,
                    commit_mode=_commit_judge_mode,
                    read_judge_mode=lambda: _read_judge_mode(runtime),
                    read_guard_mode=lambda: _read_guard_mode(runtime),
                )
                if body.requested_mode is not EvaluationMode.OFF:
                    judge = next(
                        item
                        for item in composite.provider.selections
                        if item.role is ModelRole.JUDGE
                    )
                    if judge.state is not ProviderRuntimeState.ACTIVE:
                        raise ProviderSelectionError(
                            code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                            safe_message=(
                                "The configured Judge provider could not be activated: "
                                f"{judge.failure_reason or judge.state.value}"
                            ),
                        )
                return _project_status(runtime, judge_mode=composite.judge_mode)
            judge_mode_control.apply_mode(body.requested_mode)
        return _project_status(runtime)

    @router.post("/repair", response_model=FeatureModesStatusResponse)
    async def apply_repair(
        request: Request, body: ApplyRepairModeRequest
    ) -> FeatureModesStatusResponse:
        runtime = _runtime(request)
        if runtime.repair_mode_control is not None:
            runtime.repair_mode_control.apply_mode(body.requested_mode)
        return _project_status(runtime)

    @router.post("/recording", response_model=FeatureModesStatusResponse)
    async def apply_recording(
        request: Request, body: ApplyRecordingModeRequest
    ) -> FeatureModesStatusResponse:
        runtime = _runtime(request)
        if runtime.recording_mode_control is not None:
            runtime.recording_mode_control.apply_mode(body.requested_mode)
        return _project_status(runtime)

    return router
