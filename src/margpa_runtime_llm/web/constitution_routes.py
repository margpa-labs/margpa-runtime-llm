"""Local-private `/api/v2/constitution` routes and safe errors (P8-C/P8-RW6-D).

Read-only by design (Provisional Runtime Constitution, P8-REQ-013): this
Bounded Task exposes the current Manifest/Capability View for observation
only — no mutation Route exists here, and Mode is fixed to `OFF` at
Composition time (see `bootstrap/constitution.py`) since nothing in this
Task actually enforces a Rule yet.

P8-RW6-D adds `/preview`: a second read-only Route that compares OFF/
OBSERVE/ENFORCE side by side for the *same* Manifest — Pure Evaluation via
`resolve_constitution_mode_preview()`, never touching `WebRuntime.
constitution_mode` (the Production Active Mode `/runtime` above reads,
still hard-locked to OFF). Constructing this Response never activates
Runtime Enforcement, grants Tool Authority, or injects anything into a
Model.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from margpa_runtime_llm.modules.constitution import (
    ConstitutionManifest,
    ConstitutionMode,
    ConstitutionProviderPort,
    ConstitutionView,
    resolve_capability_view,
    resolve_constitution_mode_preview,
)

from .constitution_contracts import (
    ConstitutionModePreviewResponse,
    ConstitutionRuntimeResponse,
    project_capability_views,
    project_mode_previews,
)
from .contracts import WebRuntime

CONSTITUTION_API_PREFIX = "/api/v2/constitution"
_ALL_VIEWS: tuple[ConstitutionView, ...] = ("chat", "agent", "tool")


@dataclass(frozen=True, slots=True)
class ConstitutionWebError(Exception):
    status_code: int
    code: str
    safe_message: str


def create_constitution_router() -> APIRouter:
    router = APIRouter(prefix=CONSTITUTION_API_PREFIX)

    @router.get("/runtime", response_model=ConstitutionRuntimeResponse)
    async def runtime(request: Request) -> ConstitutionRuntimeResponse:
        provider = _provider(request)
        manifest = await asyncio.to_thread(provider.load_manifest)
        if not isinstance(manifest, ConstitutionManifest):
            raise ConstitutionWebError(
                404,
                "constitution_unavailable",
                "The Provisional Runtime Constitution is unavailable.",
            )
        mode = _mode(request)
        views = tuple(
            resolve_capability_view(manifest, view=view, mode=mode) for view in _ALL_VIEWS
        )
        return project_capability_views(manifest, views)

    @router.get("/preview", response_model=ConstitutionModePreviewResponse)
    async def preview(request: Request) -> ConstitutionModePreviewResponse:
        provider = _provider(request)
        manifest = await asyncio.to_thread(provider.load_manifest)
        if not isinstance(manifest, ConstitutionManifest):
            raise ConstitutionWebError(
                404,
                "constitution_unavailable",
                "The Provisional Runtime Constitution is unavailable.",
            )
        previews = tuple(
            resolve_constitution_mode_preview(manifest, view=view) for view in _ALL_VIEWS
        )
        return project_mode_previews(manifest, previews, active_production_mode=_mode(request))

    return router


def constitution_error_response(error: ConstitutionWebError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.safe_message},
    )


def _provider(request: Request) -> ConstitutionProviderPort:
    web_runtime: WebRuntime = request.app.state.runtime
    provider = web_runtime.constitution_provider
    if provider is None:
        raise ConstitutionWebError(
            404,
            "constitution_unavailable",
            "The Provisional Runtime Constitution is unavailable.",
        )
    return provider


def _mode(request: Request) -> ConstitutionMode:
    web_runtime: WebRuntime = request.app.state.runtime
    return web_runtime.constitution_mode
