"""Local-private, read-only `/api/v2/runtime/components` route.

Reports the state each existing component's own gate already resolved; it
grants no execution authority and mutates nothing (`GET` only).
"""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from margpa_runtime_llm.modules.runtime_composition.application import ComponentRegistryService
from margpa_runtime_llm.modules.runtime_composition.contracts import ComponentDescriptor

from .contracts import WebRuntime

RUNTIME_COMPOSITION_API_PREFIX = "/api/v2/runtime"


class _RuntimeCompositionContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class RuntimeComponentResponse(_RuntimeCompositionContract):
    component_key: str
    kind: str
    version: str
    state: str
    canonical_digest: str
    capabilities: tuple[str, ...]
    required_dependencies: tuple[str, ...]
    optional_dependencies: tuple[str, ...]
    conflicts_with: tuple[str, ...]
    degraded_reasons: tuple[str, ...]
    side_effect_level: str
    apply_disposition: str
    restart_required: bool
    effective_source: str
    revision: int
    governance_seam_mode: str


class RuntimeComponentsResponse(_RuntimeCompositionContract):
    components: tuple[RuntimeComponentResponse, ...]


def _project_component(descriptor: ComponentDescriptor) -> RuntimeComponentResponse:
    return RuntimeComponentResponse(
        component_key=descriptor.component_key,
        kind=descriptor.kind,
        version=descriptor.version,
        state=descriptor.state.value,
        canonical_digest=descriptor.canonical_digest,
        capabilities=descriptor.capabilities,
        required_dependencies=descriptor.required_dependencies,
        optional_dependencies=descriptor.optional_dependencies,
        conflicts_with=descriptor.conflicts_with,
        degraded_reasons=descriptor.degraded_reasons,
        side_effect_level=descriptor.side_effect_level.value,
        apply_disposition=descriptor.apply_disposition.value,
        restart_required=descriptor.restart_required,
        effective_source=descriptor.effective_source.value,
        revision=descriptor.revision,
        governance_seam_mode=descriptor.governance_seam_mode,
    )


@dataclass(frozen=True, slots=True)
class RuntimeCompositionWebError(Exception):
    status_code: int
    code: str
    safe_message: str


def create_runtime_composition_router() -> APIRouter:
    router = APIRouter(prefix=RUNTIME_COMPOSITION_API_PREFIX)

    @router.get("/components", response_model=RuntimeComponentsResponse)
    async def components(request: Request) -> RuntimeComponentsResponse:
        registry = _registry(request)
        return RuntimeComponentsResponse(
            components=tuple(_project_component(item) for item in registry.list_components())
        )

    return router


def runtime_composition_error_response(error: RuntimeCompositionWebError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.safe_message},
    )


def _registry(request: Request) -> ComponentRegistryService:
    runtime: WebRuntime = request.app.state.runtime
    registry = runtime.runtime_composition
    if registry is None:
        raise RuntimeCompositionWebError(
            status_code=404,
            code="runtime_composition_unavailable",
            safe_message="Runtime composition inspection is unavailable.",
        )
    return registry
