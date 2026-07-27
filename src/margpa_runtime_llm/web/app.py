"""FastAPI application factory kept outside the inference and presentation core."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response

from margpa_runtime_llm.modules.conversation.public import ConversationGenerationInput
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError

from .auth import WebAccessPolicy
from .contracts import StopGenerationRequest, WebRuntime
from .error_mapping import http_status_for_inference_error
from .streaming import stream_session_as_sse

MAX_CHAT_REQUEST_BYTES = 262_144
STATIC_ROOT = Path(__file__).resolve().parent / "static"
SHUTDOWN_FAILURE_MESSAGE = "The web runtime could not shut down cleanly."
RuntimeFactory = Callable[[], WebRuntime]
CallNext = Callable[[Request], Awaitable[Response]]
logger = logging.getLogger(__name__)


def create_web_app(
    *,
    runtime_factory: RuntimeFactory,
    access_policy: WebAccessPolicy,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        try:
            runtime = await asyncio.to_thread(runtime_factory)
        except InferenceError as exc:
            raise RuntimeError(exc.safe_message) from None
        except Exception:
            raise RuntimeError("The web runtime could not start.") from None
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
        if request.url.path == "/api/v1/chat/stream":
            content_length = request.headers.get("content-length")
            if content_length is not None:
                try:
                    request_size = int(content_length)
                except ValueError:
                    request_size = MAX_CHAT_REQUEST_BYTES + 1
                if request_size > MAX_CHAT_REQUEST_BYTES:
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
    async def index() -> FileResponse:
        return FileResponse(STATIC_ROOT / "index.html", media_type="text/html")

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
        session = await asyncio.to_thread(runtime.conversation.start, body)
        return StreamingResponse(
            stream_session_as_sse(request, session),
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

    app.mount("/assets", StaticFiles(directory=STATIC_ROOT), name="assets")
    return app


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
