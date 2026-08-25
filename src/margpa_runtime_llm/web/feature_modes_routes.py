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

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from margpa_runtime_llm.bootstrap.recording_live_integration import RecordingOutcome
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode
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


class JudgeModeSnapshotResponse(ModeSnapshotResponse):
    # Current-Request Judge Run state (P6-CODEX-012, partial): `idle` means
    # no Judge Run is in flight right now, so `last_result` (if any) is
    # necessarily from a *previous* Turn — a Status reader must not read
    # `last_result` as "this Turn's outcome" while `state` is `running`.
    state: str | None = None
    current_request_id: str | None = None
    last_result: JudgeLastResultResponse | None = None


class RecordingOutcomeResponse(_FeatureModesContract):
    request_id: str
    ok: bool
    degraded_reason: str | None = None


class RecordingModeSnapshotResponse(ModeSnapshotResponse):
    # `last_outcome` reflects the Turn-level recorder only (never Judge
    # Evidence's own, separate recorder) — see `judge_evidence_last_outcome`
    # below for that one, kept distinct so a reader never conflates the two.
    last_outcome: RecordingOutcomeResponse | None = None
    judge_evidence_last_outcome: RecordingOutcomeResponse | None = None


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


def _judge_snapshot(runtime: WebRuntime) -> JudgeModeSnapshotResponse:
    controller = runtime.judge_mode_control
    if controller is None:
        return JudgeModeSnapshotResponse(enabled=False)
    snapshot = controller.mode_snapshot()
    composition = runtime.judge_governance_composition
    last_result = composition.last_result() if composition is not None else None
    return JudgeModeSnapshotResponse(
        enabled=True,
        revision=snapshot.revision,
        current_mode=snapshot.current_mode.value,
        state=composition.current_state() if composition is not None else None,
        current_request_id=(composition.current_request_id() if composition is not None else None),
        last_result=(
            None
            if last_result is None
            else JudgeLastResultResponse(
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
            )
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
    return RecordingModeSnapshotResponse(
        enabled=True,
        revision=snapshot.revision,
        current_mode=snapshot.current_mode.value,
        last_outcome=_recording_outcome_response(
            runtime.recording_composition.last_outcome()
            if runtime.recording_composition is not None
            else None
        ),
        judge_evidence_last_outcome=_recording_outcome_response(
            runtime.judge_evidence_recording_composition.last_outcome()
            if runtime.judge_evidence_recording_composition is not None
            else None
        ),
    )


def _project_status(runtime: WebRuntime) -> FeatureModesStatusResponse:
    return FeatureModesStatusResponse(
        judge=_judge_snapshot(runtime),
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
        return _project_status(_runtime(request))

    @router.post("/judge", response_model=FeatureModesStatusResponse)
    async def apply_judge(
        request: Request, body: ApplyJudgeModeRequest
    ) -> FeatureModesStatusResponse:
        runtime = _runtime(request)
        if runtime.judge_mode_control is not None:
            runtime.judge_mode_control.apply_mode(body.requested_mode)
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
