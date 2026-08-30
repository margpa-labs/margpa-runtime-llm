"""Local-private `/api/v2/local-corpus` routes and safe errors (P7-B)."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from fastapi import APIRouter, Path, Request
from fastapi.responses import JSONResponse

from margpa_runtime_llm.modules.documentation_rag.local_corpus_contracts import (
    LOCAL_CORPUS_DOCUMENT_ID_PATTERN,
    LocalCorpusDocumentNotFound,
    LocalCorpusDocumentState,
    LocalCorpusLimitExceeded,
    summarize,
)
from margpa_runtime_llm.modules.documentation_rag.local_corpus_ports import (
    LocalCorpusRegistryPort,
)

from .contracts import WebRuntime
from .local_corpus_contracts import (
    LocalCorpusDocumentInputRequest,
    LocalCorpusDocumentListResponse,
    LocalCorpusDocumentResponse,
    LocalCorpusDocumentSummaryResponse,
    project_document,
    project_list,
    project_summary,
)

LOCAL_CORPUS_API_PREFIX = "/api/v2/local-corpus"


@dataclass(frozen=True, slots=True)
class LocalCorpusWebError(Exception):
    status_code: int
    code: str
    safe_message: str


def create_local_corpus_router() -> APIRouter:
    router = APIRouter(prefix=LOCAL_CORPUS_API_PREFIX)

    @router.get("/documents", response_model=LocalCorpusDocumentListResponse)
    async def list_documents(request: Request) -> LocalCorpusDocumentListResponse:
        registry = _registry(request)
        records = await asyncio.to_thread(registry.list_active)
        return project_list(records)

    @router.post("/documents", response_model=LocalCorpusDocumentResponse, status_code=201)
    async def register_document(
        request: Request,
        body: LocalCorpusDocumentInputRequest,
    ) -> LocalCorpusDocumentResponse:
        registry = _registry(request)
        try:
            record = await asyncio.to_thread(registry.register, body.to_domain())
        except LocalCorpusLimitExceeded as exc:
            raise LocalCorpusWebError(422, exc.code, _limit_message(exc.code)) from exc
        return project_document(record)

    @router.get("/documents/{document_id}", response_model=LocalCorpusDocumentResponse)
    async def get_document(
        request: Request,
        document_id: str = Path(pattern=LOCAL_CORPUS_DOCUMENT_ID_PATTERN),
    ) -> LocalCorpusDocumentResponse:
        registry = _registry(request)
        record = await asyncio.to_thread(registry.get, document_id)
        if record is None or record.state is not LocalCorpusDocumentState.ACTIVE:
            raise _not_found(document_id)
        return project_document(record)

    @router.put("/documents/{document_id}", response_model=LocalCorpusDocumentResponse)
    async def update_document(
        request: Request,
        body: LocalCorpusDocumentInputRequest,
        document_id: str = Path(pattern=LOCAL_CORPUS_DOCUMENT_ID_PATTERN),
    ) -> LocalCorpusDocumentResponse:
        registry = _registry(request)
        try:
            record = await asyncio.to_thread(registry.update, document_id, body.to_domain())
        except LocalCorpusDocumentNotFound as exc:
            raise _not_found(document_id) from exc
        except LocalCorpusLimitExceeded as exc:
            raise LocalCorpusWebError(422, exc.code, _limit_message(exc.code)) from exc
        return project_document(record)

    @router.delete("/documents/{document_id}", response_model=LocalCorpusDocumentSummaryResponse)
    async def delete_document(
        request: Request,
        document_id: str = Path(pattern=LOCAL_CORPUS_DOCUMENT_ID_PATTERN),
    ) -> LocalCorpusDocumentSummaryResponse:
        registry = _registry(request)
        try:
            record = await asyncio.to_thread(registry.delete, document_id)
        except LocalCorpusDocumentNotFound as exc:
            raise _not_found(document_id) from exc
        return project_summary(summarize(record))

    return router


def local_corpus_error_response(error: LocalCorpusWebError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code,
        content={"code": error.code, "message": error.safe_message},
    )


def _limit_message(code: str) -> str:
    if code == "local_corpus_document_limit_exceeded":
        return "Local Corpus Documentの登録数上限へ到達しました。"
    return "Local Corpusの合計Size上限へ到達しました。"


def _not_found(document_id: str) -> LocalCorpusWebError:
    del document_id
    return LocalCorpusWebError(
        404,
        "local_corpus_document_not_found",
        "The requested Local Corpus document was not found.",
    )


def _registry(request: Request) -> LocalCorpusRegistryPort:
    runtime: WebRuntime = request.app.state.runtime
    registry = runtime.local_corpus_registry
    if registry is None:
        raise LocalCorpusWebError(
            404,
            "local_corpus_unavailable",
            "Local Corpus document management is unavailable.",
        )
    return registry
