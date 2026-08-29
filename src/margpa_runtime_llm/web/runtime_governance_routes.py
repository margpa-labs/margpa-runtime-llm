"""Local-private `/api/v3/runtime-governance/status` route (P3-F-WU-003
sibling, P4-F-WU-002/003, P4-CODEX-002/003 Rework).

Read-only only — Phase 4 Main Governance Mode Mutation has exactly one
Canonical path, `/api/v2/configuration` Preview→Apply CAS (a
`main_governance_mode` Patch field), the same machinery Phase 3's own
Governance Mode already uses. This module no longer exposes any direct
Apply endpoint: a second, un-versioned direct-Apply route alongside the
CAS flow would be a dual Mutation path with its own Revision/Cache,
exactly the "二重Controller/二重Revision" Codex flagged (P4-CODEX-002).

Status additionally now projects each Governance Point's last observed
`StandardGovernanceResult` (Binding State, selected Descriptor/Rule
Count, Severity, Recommended/Executed Action Count, Degraded/Unavailable
Reason — P4-STS-001) plus the Governance Evidence Observer's own Safe
Degraded status. No Source Path, Definition body, Raw Exception, Secret,
or User Content ever crosses this boundary (P4-STS-002).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from margpa_runtime_llm.modules.runtime_governance.domain import (
    MAIN_MODEL_POST_POINT_ID,
    MAIN_MODEL_PRE_POINT_ID,
    Observation,
    ObservationOutcome,
)

from .contracts import WebRuntime

if TYPE_CHECKING:
    from margpa_runtime_llm.bootstrap.runtime_governance import RuntimeGovernanceComposition

RUNTIME_GOVERNANCE_API_PREFIX = "/api/v3/runtime-governance"


class _RuntimeGovernanceContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class MainGovernanceModeDescriptorResponse(_RuntimeGovernanceContract):
    mode: str
    availability: str
    unavailable_reason_code: str | None = None


class GovernancePointStatusResponse(_RuntimeGovernanceContract):
    point_id: str
    execution_state: str | None = None
    selected_descriptor_count: int | None = None
    severity: str | None = None
    recommended_action_count: int | None = None
    executed_action_count: int | None = None
    unavailable_reason_code: str | None = None
    degraded_reason_code: str | None = None
    latency_ms: int | None = None
    # P4-CODEX-013 §3.3: a Safe Count-only projection of this same
    # `StandardGovernanceResult.observations` — never re-evaluated, never
    # Rule text/Prompt/Output/Path/Exception/Secret. Lets a User see that
    # OBSERVE actually ran and what it found (pass/deviation/deferred)
    # even though OBSERVE itself stays non-intervening (ADR-4-007) —
    # "non-intervening" and "invisible" are not the same thing.
    observation_count: int | None = None
    pass_count: int | None = None
    deviation_count: int | None = None
    unknown_count: int | None = None
    deferred_count: int | None = None


class GovernanceEvidenceStatusResponse(_RuntimeGovernanceContract):
    degraded: bool
    degraded_reason_code: str | None = None
    degraded_event_count: int = 0
    # P4-CODEX-007: a fault in the *interaction* with the Observer/Port
    # itself (`is_active()`/any `observe_*` call raising) — distinct from
    # `degraded` above, which is the Observer's own self-reported Store
    # Write failure. The Observer cannot self-report a fault it is itself
    # the cause of, so the Composition tracks this separately.
    observer_interaction_degraded: bool = False


class MainGovernanceStatusResponse(_RuntimeGovernanceContract):
    enabled: bool
    revision: int | None = None
    current_mode: str | None = None
    descriptors: tuple[MainGovernanceModeDescriptorResponse, ...] = ()
    points: tuple[GovernancePointStatusResponse, ...] = ()
    evidence: GovernanceEvidenceStatusResponse | None = None


def _observation_summary(observations: tuple[Observation, ...]) -> tuple[int, int, int, int, int]:
    """One-pass, non-re-evaluating Count over an already-computed
    Observation set — each count only ever increments on an exact known
    `ObservationOutcome` match; an Outcome this projection doesn't
    recognize (e.g. a future addition) still counts toward the Total but
    is never folded into a specific bucket (P4-CODEX-013 §3.3 Security)."""

    pass_count = 0
    deviation_count = 0
    unknown_count = 0
    deferred_count = 0
    for observation in observations:
        if observation.outcome is ObservationOutcome.PASS:
            pass_count += 1
        elif observation.outcome is ObservationOutcome.DEVIATION:
            deviation_count += 1
        elif observation.outcome is ObservationOutcome.UNKNOWN:
            unknown_count += 1
        elif observation.outcome is ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR:
            deferred_count += 1
    return len(observations), pass_count, deviation_count, unknown_count, deferred_count


def _point_status(
    composition: RuntimeGovernanceComposition, *, point_id: str
) -> GovernancePointStatusResponse:
    result = composition.last_result_for(point_id=point_id)
    if result is None:
        return GovernancePointStatusResponse(point_id=point_id)
    observations = result.observations
    if point_id == MAIN_MODEL_POST_POINT_ID:
        # P6-RR-R3-WU-006 (Post-Claude Independent Review Rework, resolves
        # part of P6-CODEX-064 / N-WU-004): `result.observations` here is
        # the Structural-only set frozen at Post-hook time — it never
        # updates again, so a Deferred-to-Semantic-Evaluator placeholder
        # stayed Deferred forever even after real Semantic evaluation
        # completed (P6-GOV-017's "Deferred (semantic evaluation pending) 109" that never
        # resolves). `SemanticRuntimeCoordinator.latest_evidence()` already
        # guards against a late/stale Turn overwriting a newer one
        # internally (`record_response()`'s own request_id/generation
        # check) — using its `merged_observations` here, only for the
        # POST Point (Semantic Criteria evaluate the Candidate Answer,
        # which does not exist yet at PRE time — PRE's own Deferred count
        # is an honest, permanent reflection of that ordering, not a bug),
        # projects the real outcome once available instead of the frozen
        # placeholder. `latest_evidence() is None` (not yet recorded, or
        # the previous Turn's Dispatch was preempted/cancelled before
        # recording) falls back to the Structural-only set exactly as
        # before this Rework — never a fabricated or stale substitution.
        evidence = composition.semantic_runtime.latest_evidence()
        if evidence is not None:
            observations = evidence.merged_observations
    observation_count, pass_count, deviation_count, unknown_count, deferred_count = (
        _observation_summary(observations)
    )
    return GovernancePointStatusResponse(
        point_id=point_id,
        execution_state=result.execution_state.value,
        selected_descriptor_count=len(result.selected_descriptor_ids),
        severity=result.severity.value,
        recommended_action_count=len(result.recommended_actions),
        executed_action_count=sum(1 for action in result.executed_actions if action.executed),
        unavailable_reason_code=result.unavailable_reason_code,
        degraded_reason_code=result.degraded_reason_code,
        latency_ms=result.latency_ms,
        observation_count=observation_count,
        pass_count=pass_count,
        deviation_count=deviation_count,
        unknown_count=unknown_count,
        deferred_count=deferred_count,
    )


def _project_status(runtime: WebRuntime) -> MainGovernanceStatusResponse:
    composition = runtime.runtime_governance_composition
    if composition is None:
        return MainGovernanceStatusResponse(enabled=False)
    snapshot = composition.mode_controller.mode_snapshot()
    evidence_status = None
    if composition.governance_observer is not None:
        observer_status = composition.governance_observer.status()
        evidence_status = GovernanceEvidenceStatusResponse(
            degraded=observer_status.degraded,
            degraded_reason_code=observer_status.degraded_reason_code,
            degraded_event_count=observer_status.degraded_event_count,
            observer_interaction_degraded=composition.observer_interaction_degraded(),
        )
    return MainGovernanceStatusResponse(
        enabled=True,
        revision=snapshot.revision,
        current_mode=snapshot.current_mode.value,
        descriptors=tuple(
            MainGovernanceModeDescriptorResponse(
                mode=descriptor.mode.value,
                availability=descriptor.availability.value,
                unavailable_reason_code=descriptor.unavailable_reason_code,
            )
            for descriptor in snapshot.descriptors
        ),
        points=(
            _point_status(composition, point_id=MAIN_MODEL_PRE_POINT_ID),
            _point_status(composition, point_id=MAIN_MODEL_POST_POINT_ID),
        ),
        evidence=evidence_status,
    )


def create_runtime_governance_router() -> APIRouter:
    router = APIRouter(prefix=RUNTIME_GOVERNANCE_API_PREFIX)

    @router.get("/status", response_model=MainGovernanceStatusResponse)
    async def get_status(request: Request) -> MainGovernanceStatusResponse:
        return _project_status(_runtime(request))

    return router


def _runtime(request: Request) -> WebRuntime:
    runtime: WebRuntime = request.app.state.runtime
    return runtime
