"""Local-private `/api/v2/web-search` routes and safe errors (P7-E/F)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from margpa_runtime_llm.modules.web_knowledge.application import WebKnowledgeService
from margpa_runtime_llm.modules.web_knowledge.contracts import WebEvidenceGovernanceMode

from .contracts import WebRuntime
from .web_search_contracts import (
    WebSearchRequest,
    WebSearchResponse,
    WebSearchRuntimeResponse,
    project_web_search_result,
)

WEB_SEARCH_API_PREFIX = "/api/v2/web-search"


@dataclass(frozen=True, slots=True)
class WebSearchWebError(Exception):
    status_code: int
    code: str
    safe_message: str


def create_web_search_router() -> APIRouter:
    router = APIRouter(prefix=WEB_SEARCH_API_PREFIX)

    @router.get("/runtime", response_model=WebSearchRuntimeResponse)
    async def runtime(request: Request) -> WebSearchRuntimeResponse:
        _, governance_mode = _service(request)
        return WebSearchRuntimeResponse(governance_mode=governance_mode)

    @router.post("/search", response_model=WebSearchResponse)
    async def search(request: Request, body: WebSearchRequest) -> WebSearchResponse:
        service, governance_mode = _service(request)
        result = await asyncio.to_thread(
            service.search_and_fetch,
            body.query,
            request_id=uuid4().hex,
            activation=body.activation,
            governance_mode=governance_mode,
        )
        return project_web_search_result(result)

    return router


def web_search_error_response(error: WebSearchWebError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.safe_message},
    )


def _service(request: Request) -> tuple[WebKnowledgeService, WebEvidenceGovernanceMode]:
    runtime: WebRuntime = request.app.state.runtime
    service = runtime.web_knowledge_service
    if service is None:
        raise WebSearchWebError(
            404,
            "web_search_unavailable",
            "Web Search is unavailable.",
        )
    return service, runtime.web_search_governance_mode
