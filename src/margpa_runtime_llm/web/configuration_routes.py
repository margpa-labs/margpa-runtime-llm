"""Local-private `/api/v2/configuration` routes and safe errors."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from margpa_runtime_llm.modules.configuration_control import (
    ConfigurationControlError,
    ConfigurationControlErrorCode,
    ConfigurationControlService,
)

from .configuration_contracts import (
    ConfigurationApplyRequest,
    ConfigurationApplyResponse,
    ConfigurationPreviewRequest,
    ConfigurationPreviewResponse,
    ConfigurationRuntimeResponse,
    EffectiveConfigurationResponse,
    project_apply,
    project_effective,
    project_preview,
)
from .contracts import WebRuntime

CONFIGURATION_API_PREFIX = "/api/v2/configuration"


@dataclass(frozen=True, slots=True)
class ConfigurationWebError(Exception):
    status_code: int
    code: str
    safe_message: str


def create_configuration_router() -> APIRouter:
    router = APIRouter(prefix=CONFIGURATION_API_PREFIX)

    @router.get("/runtime", response_model=ConfigurationRuntimeResponse)
    async def runtime(request: Request) -> ConfigurationRuntimeResponse:
        _service(request)
        return ConfigurationRuntimeResponse()

    @router.get("/effective", response_model=EffectiveConfigurationResponse)
    async def effective(request: Request) -> EffectiveConfigurationResponse:
        value = await asyncio.to_thread(_service(request).effective)
        return project_effective(value)

    @router.post("/preview", response_model=ConfigurationPreviewResponse)
    async def preview(
        request: Request,
        body: ConfigurationPreviewRequest,
    ) -> ConfigurationPreviewResponse:
        value = await asyncio.to_thread(_service(request).preview, body.patch.to_domain())
        return project_preview(value)

    @router.post("/apply", response_model=ConfigurationApplyResponse)
    async def apply(
        request: Request,
        body: ConfigurationApplyRequest,
    ) -> ConfigurationApplyResponse:
        value = await asyncio.to_thread(
            _service(request).apply,
            operation_id=body.operation_id,
            expected_revision=body.expected_revision,
            expected_digest=body.expected_digest,
            patch=body.patch.to_domain(),
        )
        return project_apply(value)

    return router


def configuration_error_response(error: ConfigurationControlError) -> JSONResponse:
    status = (
        409
        if error.code
        in {
            ConfigurationControlErrorCode.CONFLICT,
            ConfigurationControlErrorCode.OPERATION_ALREADY_APPLIED,
        }
        else 422
    )
    content: dict[str, object] = {
        "code": error.code.value,
        "message": error.safe_message,
    }
    if error.current_revision is not None:
        content["current_revision"] = error.current_revision
    if error.current_digest is not None:
        content["current_digest"] = error.current_digest
    return JSONResponse(status_code=status, content=content)


def configuration_web_error_response(error: ConfigurationWebError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.safe_message},
    )


def _service(request: Request) -> ConfigurationControlService:
    runtime: WebRuntime = request.app.state.runtime
    service = runtime.configuration_control
    if service is None:
        raise ConfigurationWebError(
            status_code=404,
            code="configuration_control_unavailable",
            safe_message="Configuration control is unavailable.",
        )
    return service
