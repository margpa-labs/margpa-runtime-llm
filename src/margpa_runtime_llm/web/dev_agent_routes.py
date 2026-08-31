"""Local-private `/api/v2/dev-agent` routes and safe errors (P8-D).

Production Wiring composes the Run Service against the Fake/Deterministic
Tool Adapter only (`bootstrap/dev_agent.py`) — every Run these Routes can
start actually executes end to end against real, live, in-process Fixture
Tools; there is nothing simulated about the wiring itself, only about what
the Tools touch (never the real filesystem or network).
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from margpa_runtime_llm.modules.constitution import ConstitutionManifest, resolve_capability_view
from margpa_runtime_llm.modules.dev_agent import (
    CapabilityId,
    DevAgentRunService,
    InvalidRunTransitionError,
    RunNotFoundError,
    RunSnapshot,
)

from .contracts import WebRuntime
from .dev_agent_contracts import (
    DevAgentApprovalRequest,
    DevAgentCapabilityResponse,
    DevAgentCompletionApprovalRequest,
    DevAgentRunResponse,
    DevAgentStartRunRequest,
    DevAgentToolDescriptorResponse,
    project_run,
    project_tool_descriptor,
)

DEV_AGENT_API_PREFIX = "/api/v2/dev-agent"


@dataclass(frozen=True, slots=True)
class DevAgentWebError(Exception):
    status_code: int
    code: str
    safe_message: str


def create_dev_agent_router() -> APIRouter:
    router = APIRouter(prefix=DEV_AGENT_API_PREFIX)

    @router.get("/capabilities", response_model=tuple[DevAgentCapabilityResponse, ...])
    async def capabilities() -> tuple[DevAgentCapabilityResponse, ...]:
        return tuple(DevAgentCapabilityResponse(capability_id=c) for c in CapabilityId)

    @router.get("/tools", response_model=tuple[DevAgentToolDescriptorResponse, ...])
    async def tools(request: Request) -> tuple[DevAgentToolDescriptorResponse, ...]:
        service = _service(request)
        descriptors = await asyncio.to_thread(service.list_tool_descriptors)
        return tuple(project_tool_descriptor(d) for d in descriptors)

    @router.post("/runs", response_model=DevAgentRunResponse)
    async def start_run(request: Request, body: DevAgentStartRunRequest) -> DevAgentRunResponse:
        service = _service(request)
        constitution_mode, constitution_rule_ids = await asyncio.to_thread(
            _resolve_constitution_correlation, request
        )
        run = await asyncio.to_thread(
            service.start_run,
            capability_id=body.capability_id,
            plan=body.to_plan(),
            approval_profile=body.approval_profile,
            max_steps=body.max_steps,
            retry_policy=body.to_retry_policy(),
            deadline_seconds=body.deadline_seconds,
            constitution_mode=constitution_mode,
            constitution_rule_ids=constitution_rule_ids,
            budget_limit=body.budget_limit,
        )
        return project_run(run)

    @router.get("/runs/{run_id}", response_model=DevAgentRunResponse)
    async def get_run(request: Request, run_id: str) -> DevAgentRunResponse:
        service = _service(request)
        run = await asyncio.to_thread(service.get_run, run_id)
        if run is None:
            raise DevAgentWebError(404, "dev_agent_run_not_found", "The Run was not found.")
        return project_run(run)

    @router.post("/runs/{run_id}/advance", response_model=DevAgentRunResponse)
    async def advance(request: Request, run_id: str) -> DevAgentRunResponse:
        service = _service(request)
        run = await _guarded(service.advance, run_id)
        return project_run(run)

    @router.post("/runs/{run_id}/approvals", response_model=DevAgentRunResponse)
    async def submit_approval(
        request: Request, run_id: str, body: DevAgentApprovalRequest
    ) -> DevAgentRunResponse:
        service = _service(request)
        run = await _guarded(service.submit_approval, run_id, body.step_id, body.decision)
        return project_run(run)

    @router.post("/runs/{run_id}/completion-approval", response_model=DevAgentRunResponse)
    async def submit_completion_approval(
        request: Request, run_id: str, body: DevAgentCompletionApprovalRequest
    ) -> DevAgentRunResponse:
        service = _service(request)
        run = await _guarded(service.submit_completion_approval, run_id, body.decision)
        return project_run(run)

    @router.post("/runs/{run_id}/cancel", response_model=DevAgentRunResponse)
    async def cancel_run(request: Request, run_id: str) -> DevAgentRunResponse:
        service = _service(request)
        run = await _guarded(service.cancel_run, run_id)
        return project_run(run)

    return router


async def _guarded(fn: Callable[..., RunSnapshot], *args: object) -> RunSnapshot:
    try:
        return await asyncio.to_thread(fn, *args)
    except RunNotFoundError as error:
        raise DevAgentWebError(404, "dev_agent_run_not_found", "The Run was not found.") from error
    except InvalidRunTransitionError as error:
        raise DevAgentWebError(409, "dev_agent_invalid_transition", str(error)) from error


def dev_agent_error_response(error: DevAgentWebError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.safe_message},
    )


def _service(request: Request) -> DevAgentRunService:
    web_runtime: WebRuntime = request.app.state.runtime
    service = web_runtime.dev_agent_run_service
    if service is None:
        raise DevAgentWebError(
            404, "dev_agent_unavailable", "The Dev Agent Foundation is unavailable."
        )
    return service


def _resolve_constitution_correlation(
    request: Request,
) -> tuple[str | None, tuple[str, ...] | None]:
    """P8-E: correlate the Run against whatever the `agent` Capability View
    actually says at the moment the Run starts. `None`/`None` is the honest
    result when no Constitution Provider is bound or its Manifest cannot be
    verified — never a fabricated "no Rules apply" stand-in."""

    web_runtime: WebRuntime = request.app.state.runtime
    provider = web_runtime.constitution_provider
    if provider is None:
        return None, None
    manifest = provider.load_manifest()
    if not isinstance(manifest, ConstitutionManifest):
        return None, None
    mode = web_runtime.constitution_mode
    view = resolve_capability_view(manifest, view="agent", mode=mode)
    return mode.value, view.rule_ids
