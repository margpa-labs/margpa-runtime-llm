"""Local-private `/api/v3/guardrail-governance/status` route (P5-F-WU-003,
mirrors `runtime_governance_routes.py`).

Read-only only — Phase 5 Guardrail Governance Mode Mutation has exactly
one Canonical path, `/api/v2/configuration` Preview→Apply CAS (a
`guardrail_governance_mode` Patch field), the same machinery Phase 3/4's
own Governance Modes already use. This module exposes no direct Apply
endpoint, matching the Phase 4 Rework rationale exactly (P4-CODEX-002):
a second, un-versioned direct-Apply route would be a dual Mutation path
with its own Revision/Cache.

Status projects each wired Guardrail Point's last observed
`GuardrailResult` as Safe Counts only (Detection/Match/Recommended/
Executed Action counts, Severity, Execution State, Unavailable/Degraded
Reason). No Raw Content, Typed Span offsets, Category detail beyond a
Count, Path, or Exception ever crosses this boundary (mirrors P4-STS-002).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from margpa_runtime_llm.modules.guardrail_governance.domain import (
    GUARDRAIL_CONTEXT_SOURCE_POINT_ID,
    GUARDRAIL_INPUT_POINT_ID,
    GUARDRAIL_OUTPUT_CANDIDATE_POINT_ID,
    GUARDRAIL_STREAM_CANDIDATE_POINT_ID,
    DetectionOutcome,
)

from .contracts import WebRuntime

if TYPE_CHECKING:
    from margpa_runtime_llm.bootstrap.guardrail_governance import GuardrailGovernanceComposition
    from margpa_runtime_llm.modules.guardrail_governance.domain import GuardrailResult

GUARDRAIL_GOVERNANCE_API_PREFIX = "/api/v3/guardrail-governance"


class _GuardrailGovernanceContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class GuardrailModeDescriptorResponse(_GuardrailGovernanceContract):
    mode: str
    availability: str
    unavailable_reason_code: str | None = None


class GuardrailPointStatusResponse(_GuardrailGovernanceContract):
    point_id: str
    execution_state: str | None = None
    severity: str | None = None
    recommended_action_count: int | None = None
    executed_action_count: int | None = None
    unavailable_reason_code: str | None = None
    degraded_reason_code: str | None = None
    latency_ms: int | None = None
    # Safe Count-only projection of `GuardrailResult.detections` — never
    # re-evaluated, never Raw Content/Category detail/Typed Span offsets
    # (mirrors P4-CODEX-013 §3.3's Observation Count precedent). Lets a
    # User see that Detection actually ran even in `observe` Mode, where
    # nothing is ever intervened on (ADR-5-002-equivalent).
    detection_count: int | None = None
    match_count: int | None = None


class GuardrailGovernanceStatusResponse(_GuardrailGovernanceContract):
    enabled: bool
    revision: int | None = None
    current_mode: str | None = None
    descriptors: tuple[GuardrailModeDescriptorResponse, ...] = ()
    points: tuple[GuardrailPointStatusResponse, ...] = ()


def _detection_summary(result: GuardrailResult) -> tuple[int, int]:
    match_count = sum(
        1 for detection in result.detections if detection.outcome is DetectionOutcome.MATCH
    )
    return len(result.detections), match_count


def _point_status(
    composition: GuardrailGovernanceComposition, *, point_id: str
) -> GuardrailPointStatusResponse:
    result = composition.last_result_for(point_id=point_id)
    if result is None:
        return GuardrailPointStatusResponse(point_id=point_id)
    detection_count, match_count = _detection_summary(result)
    return GuardrailPointStatusResponse(
        point_id=point_id,
        execution_state=result.execution_state.value,
        severity=result.severity.value,
        recommended_action_count=len(result.recommended_actions),
        executed_action_count=sum(1 for action in result.executed_actions if action.executed),
        unavailable_reason_code=result.unavailable_reason_code,
        degraded_reason_code=result.degraded_reason_code,
        latency_ms=result.latency_ms,
        detection_count=detection_count,
        match_count=match_count,
    )


def _project_status(runtime: WebRuntime) -> GuardrailGovernanceStatusResponse:
    composition = runtime.guardrail_governance_composition
    if composition is None:
        return GuardrailGovernanceStatusResponse(enabled=False)
    snapshot = composition.mode_controller.mode_snapshot()
    return GuardrailGovernanceStatusResponse(
        enabled=True,
        revision=snapshot.revision,
        current_mode=snapshot.current_mode.value,
        descriptors=tuple(
            GuardrailModeDescriptorResponse(
                mode=descriptor.mode.value,
                availability=descriptor.availability.value,
                unavailable_reason_code=descriptor.unavailable_reason_code,
            )
            for descriptor in snapshot.descriptors
        ),
        points=(
            _point_status(composition, point_id=GUARDRAIL_INPUT_POINT_ID),
            _point_status(composition, point_id=GUARDRAIL_OUTPUT_CANDIDATE_POINT_ID),
            _point_status(composition, point_id=GUARDRAIL_CONTEXT_SOURCE_POINT_ID),
            _point_status(composition, point_id=GUARDRAIL_STREAM_CANDIDATE_POINT_ID),
        ),
    )


def create_guardrail_governance_router() -> APIRouter:
    router = APIRouter(prefix=GUARDRAIL_GOVERNANCE_API_PREFIX)

    @router.get("/status", response_model=GuardrailGovernanceStatusResponse)
    async def get_status(request: Request) -> GuardrailGovernanceStatusResponse:
        return _project_status(_runtime(request))

    return router


def _runtime(request: Request) -> WebRuntime:
    runtime: WebRuntime = request.app.state.runtime
    return runtime
