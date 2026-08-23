"""FastAPI application factory kept outside the inference and presentation core."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from margpa_runtime_llm.modules.audit_evidence.generation_observation import (
    GenerationObserverPort,
)
from margpa_runtime_llm.modules.configuration_control import ConfigurationControlError
from margpa_runtime_llm.modules.conversation.application import PersistentConversationError
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationOperationId,
    ConversationStorageError,
    ConversationStorageErrorCode,
)
from margpa_runtime_llm.modules.conversation.public import (
    ConversationGenerationInput,
    ConversationGenerationSession,
)
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError
from margpa_runtime_llm.modules.runtime_model_control.domain.errors import (
    RuntimeModelBusyError,
    RuntimeModelContextLimitExceeded,
    RuntimeModelLoadFailure,
    RuntimeModelMaxNewTokensExceeded,
    RuntimeModelRevisionConflict,
    RuntimeModelRollbackFailure,
    RuntimeModelTargetNotRegistered,
)

from .access_profiles import (
    DisabledPublicControlPolicy,
    PublicControlPolicyPort,
    WebExposureMode,
)
from .auth import WebAccessPolicy, WebAuthMode
from .configuration_routes import (
    ConfigurationWebError,
    configuration_error_response,
    configuration_web_error_response,
    create_configuration_router,
)
from .contracts import StopGenerationRequest, WebRuntime
from .error_mapping import http_status_for_inference_error
from .feature_modes_routes import create_feature_modes_router
from .generation_observation import GenerationObservationTracker
from .governance_routes import (
    GovernanceWebError,
    create_governance_router,
    governance_error_response,
)
from .guardrail_governance_routes import create_guardrail_governance_router
from .persistent_routes import (
    PersistentWebError,
    create_persistent_router,
    persistent_error_response,
)
from .runtime_composition_routes import (
    RuntimeCompositionWebError,
    create_runtime_composition_router,
    runtime_composition_error_response,
)
from .runtime_governance_routes import create_runtime_governance_router
from .runtime_model_control_routes import (
    RuntimeModelControlWebError,
    create_runtime_model_control_router,
    runtime_model_control_error_response,
    runtime_model_control_web_error_response,
)
from .streaming import stream_session_as_sse

MAX_CHAT_REQUEST_BYTES = 262_144
MAX_PERSISTENT_REQUEST_BYTES = 131_072
MAX_CONFIGURATION_REQUEST_BYTES = 32_768
STATIC_ROOT = Path(__file__).resolve().parent / "static"
CONFIGURATION_BOOTSTRAP_DISABLED = (
    '<script id="configuration-bootstrap" type="application/json">{"enabled":false}</script>'
)
CONFIGURATION_BOOTSTRAP_ENABLED = (
    '<script id="configuration-bootstrap" type="application/json">{"enabled":true}</script>'
)
GOVERNANCE_BOOTSTRAP_DISABLED = (
    '<script id="governance-bootstrap" type="application/json">{"enabled":false}</script>'
)
GOVERNANCE_BOOTSTRAP_ENABLED = (
    '<script id="governance-bootstrap" type="application/json">{"enabled":true}</script>'
)
RUNTIME_GOVERNANCE_BOOTSTRAP_DISABLED = (
    '<script id="runtime-governance-bootstrap" type="application/json">{"enabled":false}</script>'
)
RUNTIME_GOVERNANCE_BOOTSTRAP_ENABLED = (
    '<script id="runtime-governance-bootstrap" type="application/json">{"enabled":true}</script>'
)
GUARDRAIL_BOOTSTRAP_DISABLED = (
    '<script id="guardrail-bootstrap" type="application/json">{"enabled":false}</script>'
)
GUARDRAIL_BOOTSTRAP_ENABLED = (
    '<script id="guardrail-bootstrap" type="application/json">{"enabled":true}</script>'
)
SHUTDOWN_FAILURE_MESSAGE = "The web runtime could not shut down cleanly."
RuntimeFactory = Callable[[], WebRuntime]
CallNext = Callable[[Request], Awaitable[Response]]
DEFAULT_CONTROL_POLICY: PublicControlPolicyPort = DisabledPublicControlPolicy()
logger = logging.getLogger(__name__)


def create_web_app(
    *,
    runtime_factory: RuntimeFactory,
    access_policy: WebAccessPolicy,
    control_policy: PublicControlPolicyPort = DEFAULT_CONTROL_POLICY,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            runtime = await asyncio.to_thread(runtime_factory)
        except InferenceError as exc:
            raise RuntimeError(exc.safe_message) from None
        except Exception:
            raise RuntimeError("The web runtime could not start.") from None
        if runtime.persistent_conversation is not None and (
            access_policy.exposure_mode is not WebExposureMode.LOCAL
            or access_policy.mode is not WebAuthMode.DISABLED
            or access_policy.non_loopback_allowed
        ):
            try:
                await asyncio.to_thread(runtime.close)
            finally:
                raise RuntimeError(
                    "Persistent conversations require local loopback access."
                ) from None
        if runtime.configuration_control is not None and (
            access_policy.exposure_mode is not WebExposureMode.LOCAL
            or access_policy.mode is not WebAuthMode.DISABLED
            or access_policy.non_loopback_allowed
        ):
            try:
                await asyncio.to_thread(runtime.close)
            finally:
                raise RuntimeError(
                    "Configuration control requires local loopback access."
                ) from None
        if runtime.runtime_governance_composition is not None and (
            access_policy.exposure_mode is not WebExposureMode.LOCAL
            or access_policy.mode is not WebAuthMode.DISABLED
            or access_policy.non_loopback_allowed
        ):
            try:
                await asyncio.to_thread(runtime.close)
            finally:
                raise RuntimeError(
                    "Runtime governance control requires local loopback access."
                ) from None
        if runtime.guardrail_governance_composition is not None and (
            access_policy.exposure_mode is not WebExposureMode.LOCAL
            or access_policy.mode is not WebAuthMode.DISABLED
            or access_policy.non_loopback_allowed
        ):
            try:
                await asyncio.to_thread(runtime.close)
            finally:
                raise RuntimeError(
                    "Guardrail governance control requires local loopback access."
                ) from None
        if runtime.runtime_model_control is not None and (
            access_policy.exposure_mode is not WebExposureMode.LOCAL
            or access_policy.mode is not WebAuthMode.DISABLED
            or access_policy.non_loopback_allowed
        ):
            try:
                await asyncio.to_thread(runtime.close)
            finally:
                raise RuntimeError(
                    "Runtime model control requires local loopback access."
                ) from None
        if (
            runtime.judge_mode_control is not None
            or runtime.repair_mode_control is not None
            or runtime.recording_mode_control is not None
        ) and (
            access_policy.exposure_mode is not WebExposureMode.LOCAL
            or access_policy.mode is not WebAuthMode.DISABLED
            or access_policy.non_loopback_allowed
        ):
            try:
                await asyncio.to_thread(runtime.close)
            finally:
                raise RuntimeError("Feature mode control requires local loopback access.") from None
        app.state.runtime = runtime
        try:
            yield
        finally:
            try:
                await asyncio.to_thread(runtime.close)
            except Exception:
                logger.error(SHUTDOWN_FAILURE_MESSAGE)
                raise RuntimeError(SHUTDOWN_FAILURE_MESSAGE) from None

    app = FastAPI(
        title="MARGPA Runtime LLM Preview",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )
    app.state.public_control_policy = control_policy

    @app.middleware("http")
    async def secure_requests(request: Request, call_next: CallNext) -> Response:
        if request.url.path == "/healthz":
            response = await call_next(request)
            return _apply_security_headers(response)
        if not access_policy.authorize(request.headers.get("authorization")):
            return _apply_security_headers(
                JSONResponse(
                    status_code=401,
                    content={
                        "code": "authentication_required",
                        "message": "Preview authentication is required.",
                    },
                    headers={"WWW-Authenticate": 'Basic realm="MARGPA Preview", charset="UTF-8"'},
                )
            )
        request_limit = None
        if request.url.path == "/api/v1/chat/stream":
            request_limit = MAX_CHAT_REQUEST_BYTES
        elif request.url.path.startswith("/api/v2/conversations"):
            request_limit = MAX_PERSISTENT_REQUEST_BYTES
        elif request.url.path.startswith("/api/v2/configuration"):
            request_limit = MAX_CONFIGURATION_REQUEST_BYTES
        if request_limit is not None:
            content_length = request.headers.get("content-length")
            if content_length is not None:
                try:
                    request_size = int(content_length)
                except ValueError:
                    request_size = request_limit + 1
                if request_size > request_limit:
                    return _apply_security_headers(
                        JSONResponse(
                            status_code=413,
                            content={
                                "code": "request_too_large",
                                "message": "The chat request is too large.",
                            },
                        )
                    )
        response = await call_next(request)
        return _apply_security_headers(response)

    @app.exception_handler(RequestValidationError)
    async def request_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        del request, exc
        return JSONResponse(
            status_code=422,
            content={"code": "invalid_request", "message": "The request is invalid."},
        )

    @app.exception_handler(InferenceError)
    async def inference_error(request: Request, exc: InferenceError) -> JSONResponse:
        del request
        return JSONResponse(
            status_code=http_status_for_inference_error(exc.code),
            content={
                "code": exc.code.value,
                "message": exc.safe_message,
                "retryable": exc.retryable,
            },
        )

    @app.exception_handler(ConfigurationWebError)
    async def configuration_web_error(
        request: Request,
        exc: ConfigurationWebError,
    ) -> JSONResponse:
        del request
        return configuration_web_error_response(exc)

    @app.exception_handler(ConfigurationControlError)
    async def configuration_control_error(
        request: Request,
        exc: ConfigurationControlError,
    ) -> JSONResponse:
        del request
        return configuration_error_response(exc)

    @app.exception_handler(RuntimeModelControlWebError)
    async def runtime_model_control_web_error(
        request: Request,
        exc: RuntimeModelControlWebError,
    ) -> JSONResponse:
        del request
        return runtime_model_control_web_error_response(exc)

    @app.exception_handler(RuntimeModelRevisionConflict)
    @app.exception_handler(RuntimeModelContextLimitExceeded)
    @app.exception_handler(RuntimeModelMaxNewTokensExceeded)
    @app.exception_handler(RuntimeModelBusyError)
    @app.exception_handler(RuntimeModelLoadFailure)
    @app.exception_handler(RuntimeModelRollbackFailure)
    @app.exception_handler(RuntimeModelTargetNotRegistered)
    async def runtime_model_control_domain_error(
        request: Request,
        exc: (
            RuntimeModelRevisionConflict
            | RuntimeModelContextLimitExceeded
            | RuntimeModelMaxNewTokensExceeded
            | RuntimeModelBusyError
            | RuntimeModelLoadFailure
            | RuntimeModelRollbackFailure
            | RuntimeModelTargetNotRegistered
        ),
    ) -> JSONResponse:
        del request
        return runtime_model_control_error_response(exc)

    @app.exception_handler(RuntimeCompositionWebError)
    async def runtime_composition_web_error(
        request: Request,
        exc: RuntimeCompositionWebError,
    ) -> JSONResponse:
        del request
        return runtime_composition_error_response(exc)

    @app.exception_handler(GovernanceWebError)
    async def governance_web_error(
        request: Request,
        exc: GovernanceWebError,
    ) -> JSONResponse:
        del request
        return governance_error_response(exc)

    @app.exception_handler(PersistentWebError)
    async def persistent_web_error(
        request: Request,
        exc: PersistentWebError,
    ) -> JSONResponse:
        del request
        return persistent_error_response(exc)

    @app.exception_handler(PersistentConversationError)
    async def persistent_application_error(
        request: Request,
        exc: PersistentConversationError,
    ) -> JSONResponse:
        del request
        return persistent_error_response(exc)

    @app.exception_handler(ConversationStorageError)
    async def persistent_storage_error(
        request: Request,
        exc: ConversationStorageError,
    ) -> JSONResponse:
        if exc.code is ConversationStorageErrorCode.CONFLICT and exc.operation_id is not None:
            service = _runtime(request).persistent_conversation
            if service is not None:
                try:
                    already_applied = await asyncio.to_thread(
                        service.operation_was_applied,
                        ConversationOperationId(value=exc.operation_id),
                    )
                except Exception:
                    already_applied = False
                if already_applied:
                    return persistent_error_response(
                        PersistentWebError(
                            409,
                            "operation_already_applied",
                            ("The operation was already applied. Reload the conversation detail."),
                        )
                    )
        return persistent_error_response(exc)

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        del request, exc
        return JSONResponse(
            status_code=500,
            content={
                "code": "unexpected_error",
                "message": "The request failed unexpectedly.",
            },
        )

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/")
    async def index(request: Request) -> HTMLResponse:
        html = (STATIC_ROOT / "index.html").read_text(encoding="utf-8")
        if _runtime(request).configuration_control is not None:
            if html.count(CONFIGURATION_BOOTSTRAP_DISABLED) != 1:
                raise RuntimeError("The configuration bootstrap marker is invalid.")
            html = html.replace(
                CONFIGURATION_BOOTSTRAP_DISABLED,
                CONFIGURATION_BOOTSTRAP_ENABLED,
            )
        governance_runtime = getattr(request.app.state, "governance_definitions_runtime", None)
        if governance_runtime is not None:
            if html.count(GOVERNANCE_BOOTSTRAP_DISABLED) != 1:
                raise RuntimeError("The governance bootstrap marker is invalid.")
            html = html.replace(
                GOVERNANCE_BOOTSTRAP_DISABLED,
                GOVERNANCE_BOOTSTRAP_ENABLED,
            )
        if _runtime(request).runtime_governance_composition is not None:
            if html.count(RUNTIME_GOVERNANCE_BOOTSTRAP_DISABLED) != 1:
                raise RuntimeError("The runtime governance bootstrap marker is invalid.")
            html = html.replace(
                RUNTIME_GOVERNANCE_BOOTSTRAP_DISABLED,
                RUNTIME_GOVERNANCE_BOOTSTRAP_ENABLED,
            )
        if _runtime(request).guardrail_governance_composition is not None:
            if html.count(GUARDRAIL_BOOTSTRAP_DISABLED) != 1:
                raise RuntimeError("The guardrail bootstrap marker is invalid.")
            html = html.replace(
                GUARDRAIL_BOOTSTRAP_DISABLED,
                GUARDRAIL_BOOTSTRAP_ENABLED,
            )
        return HTMLResponse(html)

    @app.get("/api/v1/runtime")
    async def runtime_info(request: Request) -> dict[str, object]:
        runtime = _runtime(request)
        return runtime.snapshot.model_dump(mode="json")

    @app.post("/api/v1/chat/stream")
    async def chat_stream(
        request: Request,
        body: ConversationGenerationInput,
    ) -> StreamingResponse:
        runtime = _runtime(request)
        control_policy.check_request()
        control_policy.before_generation()
        try:
            session = await asyncio.to_thread(runtime.conversation.start, body)
        except BaseException:
            control_policy.after_generation()
            raise
        observer: GenerationObserverPort | None = getattr(
            request.app.state, "generation_observer", None
        )
        # Bind (or don't) exactly once, at generation start: this is what
        # makes "off -> zero Governance Hook calls" literal, and what
        # keeps a generation that started under `observe` completing its
        # Start/Terminal pair even if Mode changes mid-stream, rather than
        # re-checking Mode on every event (P3-CODEX-002).
        observation_tracker = (
            GenerationObservationTracker(observer, profile_key=runtime.snapshot.profile_key)
            if observer is not None and observer.is_active()
            else None
        )
        return StreamingResponse(
            stream_session_with_control_policy(
                request=request,
                session=session,
                control_policy=control_policy,
                observation_tracker=observation_tracker,
            ),
            media_type="text/event-stream",
            headers={"X-Accel-Buffering": "no"},
        )

    @app.post("/api/v1/chat/stop")
    async def chat_stop(request: Request, body: StopGenerationRequest) -> JSONResponse:
        runtime = _runtime(request)
        accepted = runtime.conversation.cancel(body.request_id)
        if not accepted:
            return JSONResponse(
                status_code=404,
                content={
                    "code": "generation_not_active",
                    "message": "The requested generation is not active.",
                },
            )
        return JSONResponse(content={"status": "cancellation_requested"})

    app.include_router(create_persistent_router())
    app.include_router(create_configuration_router())
    app.include_router(create_runtime_composition_router())
    app.include_router(create_governance_router())
    app.include_router(create_runtime_governance_router())
    app.include_router(create_guardrail_governance_router())
    app.include_router(create_runtime_model_control_router())
    app.include_router(create_feature_modes_router())

    app.mount("/assets", StaticFiles(directory=STATIC_ROOT), name="assets")
    return app


async def stream_session_with_control_policy(
    *,
    request: Request,
    session: ConversationGenerationSession,
    control_policy: PublicControlPolicyPort,
    observation_tracker: GenerationObservationTracker | None = None,
) -> AsyncIterator[str]:
    try:
        async for chunk in stream_session_as_sse(request, session, observation_tracker):
            if chunk.startswith("event:"):
                control_policy.observe_generation()
            yield chunk
    finally:
        control_policy.after_generation()


def _runtime(request: Request) -> WebRuntime:
    runtime: WebRuntime = request.app.state.runtime
    return runtime


def _apply_security_headers(response: Response) -> Response:
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; "
        "frame-ancestors 'none'"
    )
    return response
