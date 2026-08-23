"""Local-private `/api/v3/governance/*` routes (P3-F-WU-003, P3-CODEX-001
rework).

Read-only Status Surface only — Governance Mode Mutation is not
authoritative here. Per architecture §8.3/§9.2, `governance_mode` is a
Typed Field on the existing Configuration Control Preview/Apply flow
(`/api/v2/configuration/*`), which keeps Revision/Digest/CAS, Operation
Idempotency, and a single success boundary shared with every other
runtime-applicable setting. This module never mutates
`GovernanceDefinitionsRuntime` — it only projects `status()`.

Every response is built from `GovernanceStatusSnapshot`/
`GovernanceModeSnapshot` — no absolute path, Source body, or raw
exception ever crosses this boundary (P3-UI-005, P3-SEC-*).

The `evidence` field (P3-CODEX-009) is this route's only cross-cutting
addition: it independently reads the optional `generation_observer` off
`app.state` (parallel to, not coupled with, `GovernanceDefinitionsRuntime`
— the Definition and Evidence pipelines stay loosely coupled per
architecture §4) and projects its Safe, aggregate-only `status()`, so an
Evidence Write failure that never touches Model/SSE output is still
visible somewhere rather than silently invisible.
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from margpa_runtime_llm.modules.audit_evidence.generation_observation import (
    GenerationObserverPort,
    GenerationObserverStatus,
)
from margpa_runtime_llm.modules.governance_definitions.runtime import (
    GovernanceDefinitionsRuntime,
    GovernanceObserveSummary,
)

GOVERNANCE_API_PREFIX = "/api/v3/governance"


class _GovernanceContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class GovernanceModeDescriptorResponse(_GovernanceContract):
    mode: str
    availability: str
    apply_disposition: str
    unavailable_reason_code: str | None = None


class GovernanceModeResponse(_GovernanceContract):
    revision: int
    digest_sha512: str
    current_mode: str
    descriptors: tuple[GovernanceModeDescriptorResponse, ...]


class GovernanceObserveSummaryResponse(_GovernanceContract):
    provider_state: str
    package_found: bool
    package_state: str | None = None
    definition_count: int
    valid_definition_count: int
    invalid_definition_count: int
    unsupported_definition_count: int
    compiled_plan_id: str | None = None


class EvidenceObserverStatusResponse(_GovernanceContract):
    degraded: bool
    degraded_reason_code: str | None = None
    degraded_event_count: int


class GovernanceStatusResponse(_GovernanceContract):
    mode: GovernanceModeResponse
    observe_summary: GovernanceObserveSummaryResponse | None = None
    evidence: EvidenceObserverStatusResponse | None = None


@dataclass(frozen=True, slots=True)
class GovernanceWebError(Exception):
    status_code: int
    code: str
    safe_message: str


def _project_observe_summary(
    summary: GovernanceObserveSummary | None,
) -> GovernanceObserveSummaryResponse | None:
    if summary is None:
        return None
    return GovernanceObserveSummaryResponse(
        provider_state=summary.provider_state,
        package_found=summary.package_found,
        package_state=summary.package_state,
        definition_count=summary.definition_count,
        valid_definition_count=summary.valid_definition_count,
        invalid_definition_count=summary.invalid_definition_count,
        unsupported_definition_count=summary.unsupported_definition_count,
        compiled_plan_id=summary.compiled_plan_id,
    )


def _project_evidence_status(
    status: GenerationObserverStatus | None,
) -> EvidenceObserverStatusResponse | None:
    if status is None:
        return None
    return EvidenceObserverStatusResponse(
        degraded=status.degraded,
        degraded_reason_code=status.degraded_reason_code,
        degraded_event_count=status.degraded_event_count,
    )


def _project_status(
    runtime: GovernanceDefinitionsRuntime,
    evidence_status: GenerationObserverStatus | None,
) -> GovernanceStatusResponse:
    status = runtime.status()
    return GovernanceStatusResponse(
        mode=GovernanceModeResponse(
            revision=status.mode.revision,
            digest_sha512=status.mode.digest_sha512,
            current_mode=status.mode.current_mode.value,
            descriptors=tuple(
                GovernanceModeDescriptorResponse(
                    mode=descriptor.mode.value,
                    availability=descriptor.availability.value,
                    apply_disposition=descriptor.apply_disposition.value,
                    unavailable_reason_code=descriptor.unavailable_reason_code,
                )
                for descriptor in status.mode.descriptors
            ),
        ),
        observe_summary=_project_observe_summary(status.observe_summary),
        evidence=_project_evidence_status(evidence_status),
    )


def create_governance_router() -> APIRouter:
    router = APIRouter(prefix=GOVERNANCE_API_PREFIX)

    @router.get("/runtime", response_model=GovernanceStatusResponse)
    async def get_runtime_status(request: Request) -> GovernanceStatusResponse:
        observer: GenerationObserverPort | None = getattr(
            request.app.state, "generation_observer", None
        )
        evidence_status = observer.status() if observer is not None else None
        return _project_status(_runtime(request), evidence_status)

    return router


def governance_error_response(error: GovernanceWebError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.safe_message},
    )


def _runtime(request: Request) -> GovernanceDefinitionsRuntime:
    runtime: GovernanceDefinitionsRuntime | None = getattr(
        request.app.state, "governance_definitions_runtime", None
    )
    if runtime is None:
        raise GovernanceWebError(
            status_code=404,
            code="governance_definitions_unavailable",
            safe_message="Phase 3 Governance Definitions is unavailable.",
        )
    return runtime
