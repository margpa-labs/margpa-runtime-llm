"""Local-private `/api/v2/conversations` routes and safe error mapping."""

from __future__ import annotations

import asyncio
import hashlib
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, NoReturn

from fastapi import APIRouter, Path, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

from margpa_runtime_llm.modules.conversation.application import (
    PersistentConversationError,
    PersistentConversationErrorCode,
    PersistentConversationService,
    PersistentGenerationIdentities,
)
from margpa_runtime_llm.modules.conversation.contracts import ConversationEvent
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationMessageId,
    ConversationOperationId,
    ConversationSessionId,
    ConversationState,
    ConversationStorageError,
    ConversationStorageErrorCode,
    ConversationTurnId,
    ConversationTurnOrigin,
)
from margpa_runtime_llm.modules.conversation.ports import StoredConversation

from .contracts import WebRuntime
from .persistent_contracts import (
    WEB_ID_PATTERN,
    PersistentConversationDetailResponse,
    PersistentConversationPageResponse,
    PersistentCreateRequest,
    PersistentDerivedStreamRequest,
    PersistentMutationRequest,
    PersistentMutationResponse,
    PersistentRenameRequest,
    PersistentRuntimeResponse,
    PersistentStopRequest,
    PersistentStopResponse,
    PersistentTurnStreamRequest,
    project_persistent_detail,
    project_persistent_page,
)
from .persistent_streaming import PersistentSseBridge

PERSISTENT_API_PREFIX = "/api/v2/conversations"
PERSISTENT_FEATURES = ("list", "resume", "retry", "regenerate", "branch", "rename", "delete")
_DEFAULT_LIST_STATES = frozenset(ConversationState) - {ConversationState.DELETED}
_WEB_ID_DOMAIN = b"margpa-persistent-web-v2\0"


@dataclass(frozen=True, slots=True)
class PersistentWebError(Exception):
    status_code: int
    code: str
    message: str
    current_revision: int | None = None


def create_persistent_router() -> APIRouter:
    router = APIRouter(prefix=PERSISTENT_API_PREFIX)

    @router.get("/runtime", response_model=PersistentRuntimeResponse)
    async def runtime(request: Request) -> PersistentRuntimeResponse:
        enabled = _optional_service(request) is not None
        return PersistentRuntimeResponse(
            enabled=enabled,
            features=PERSISTENT_FEATURES if enabled else (),
        )

    @router.get("", response_model=PersistentConversationPageResponse)
    async def list_conversations(
        request: Request,
        state: ConversationState | None = None,
        cursor: str | None = Query(default=None, max_length=512),
        limit: int = Query(default=50, ge=1, le=100),
    ) -> PersistentConversationPageResponse:
        service = _service(request)
        page = await asyncio.to_thread(
            service.list_conversations,
            states=_DEFAULT_LIST_STATES if state is None else frozenset({state}),
            limit=limit,
            cursor=cursor,
        )
        return project_persistent_page(page)

    @router.post("", response_model=PersistentMutationResponse)
    async def create_conversation(
        request: Request,
        body: PersistentCreateRequest,
    ) -> PersistentMutationResponse:
        service = _service(request)
        operation_id = _operation("conversation", body.operation_id)
        await _reject_applied(service, operation_id)
        stored = await asyncio.to_thread(
            service.create_conversation,
            conversation_id=_conversation_id(body.operation_id),
            session_id=_session_id("session", body.operation_id),
            operation_id=operation_id,
        )
        return PersistentMutationResponse(detail=await _project_detail(service, stored))

    @router.get("/{conversation_id}", response_model=PersistentConversationDetailResponse)
    async def detail(
        request: Request,
        conversation_id: str = _path_id(),
    ) -> PersistentConversationDetailResponse:
        service = _service(request)
        stored = await asyncio.to_thread(
            service.get_conversation,
            ConversationId(value=conversation_id),
        )
        return await _project_detail(service, stored)

    @router.post("/{conversation_id}/resume", response_model=PersistentMutationResponse)
    async def resume(
        request: Request,
        body: PersistentMutationRequest,
        conversation_id: str = _path_id(),
    ) -> PersistentMutationResponse:
        service = _service(request)
        operation_id = _operation("resume", body.operation_id)
        await _reject_applied(service, operation_id)
        stored = await asyncio.to_thread(
            service.resume_conversation,
            conversation_id=ConversationId(value=conversation_id),
            session_id=_session_id("session", body.operation_id),
            operation_id=operation_id,
            expected_revision=body.expected_revision,
        )
        return PersistentMutationResponse(detail=await _project_detail(service, stored))

    @router.post("/{conversation_id}/archive", response_model=PersistentMutationResponse)
    async def archive(
        request: Request,
        body: PersistentMutationRequest,
        conversation_id: str = _path_id(),
    ) -> PersistentMutationResponse:
        return await _archive_mutation(request, conversation_id, body, archived=True)

    @router.post("/{conversation_id}/unarchive", response_model=PersistentMutationResponse)
    async def unarchive(
        request: Request,
        body: PersistentMutationRequest,
        conversation_id: str = _path_id(),
    ) -> PersistentMutationResponse:
        return await _archive_mutation(request, conversation_id, body, archived=False)

    @router.post("/{conversation_id}/rename", response_model=PersistentMutationResponse)
    async def rename(
        request: Request,
        body: PersistentRenameRequest,
        conversation_id: str = _path_id(),
    ) -> PersistentMutationResponse:
        service = _service(request)
        operation_id = _operation("rename", body.operation_id)
        await _reject_applied(service, operation_id)
        stored = await asyncio.to_thread(
            service.rename_conversation,
            conversation_id=ConversationId(value=conversation_id),
            operation_id=operation_id,
            expected_revision=body.expected_revision,
            title=body.title or None,
        )
        return PersistentMutationResponse(detail=await _project_detail(service, stored))

    @router.post("/{conversation_id}/delete", response_model=PersistentMutationResponse)
    async def delete(
        request: Request,
        body: PersistentMutationRequest,
        conversation_id: str = _path_id(),
    ) -> PersistentMutationResponse:
        service = _service(request)
        operation_id = _operation("delete", body.operation_id)
        await _reject_applied(service, operation_id)
        stored = await asyncio.to_thread(
            service.set_deleted,
            conversation_id=ConversationId(value=conversation_id),
            operation_id=operation_id,
            expected_revision=body.expected_revision,
        )
        return PersistentMutationResponse(detail=await _project_detail(service, stored))

    @router.post("/{conversation_id}/turns/stream")
    async def normal_stream(
        request: Request,
        body: PersistentTurnStreamRequest,
        conversation_id: str = _path_id(),
    ) -> StreamingResponse:
        service = _service(request)
        identities = _generation_identities(body.operation_id)
        await _reject_applied(service, identities.append_operation_id)
        events = service.generate_turn(
            conversation_id=ConversationId(value=conversation_id),
            content=body.content,
            settings=body.settings,
            identities=identities,
            expected_revision=body.expected_revision,
        )
        return await _stream_response(
            request=request,
            service=service,
            conversation_id=ConversationId(value=conversation_id),
            turn_id=identities.turn_id,
            events=events,
        )

    @router.post("/{conversation_id}/turns/{turn_id}/retry/stream")
    async def retry_stream(
        request: Request,
        body: PersistentDerivedStreamRequest,
        conversation_id: str = _path_id(),
        turn_id: str = _turn_path_id(),
    ) -> StreamingResponse:
        return await _derived_stream_response(
            request=request,
            conversation_id=conversation_id,
            source_turn_id=turn_id,
            origin=ConversationTurnOrigin.RETRY,
            body=body,
        )

    @router.post("/{conversation_id}/turns/{turn_id}/regenerate/stream")
    async def regenerate_stream(
        request: Request,
        body: PersistentDerivedStreamRequest,
        conversation_id: str = _path_id(),
        turn_id: str = _turn_path_id(),
    ) -> StreamingResponse:
        return await _derived_stream_response(
            request=request,
            conversation_id=conversation_id,
            source_turn_id=turn_id,
            origin=ConversationTurnOrigin.REGENERATE,
            body=body,
        )

    @router.post(
        "/{conversation_id}/branches/{turn_id}/select",
        response_model=PersistentMutationResponse,
    )
    async def select_branch(
        request: Request,
        body: PersistentMutationRequest,
        conversation_id: str = _path_id(),
        turn_id: str = _turn_path_id(),
    ) -> PersistentMutationResponse:
        service = _service(request)
        operation_id = _operation("head-select", body.operation_id)
        await _reject_applied(service, operation_id)
        stored = await asyncio.to_thread(
            service.select_branch_head,
            conversation_id=ConversationId(value=conversation_id),
            completed_turn_id=ConversationTurnId(value=turn_id),
            operation_id=operation_id,
            expected_revision=body.expected_revision,
        )
        return PersistentMutationResponse(detail=await _project_detail(service, stored))

    @router.post(
        "/{conversation_id}/generations/{request_id}/stop",
        response_model=PersistentStopResponse,
    )
    async def stop_generation(
        request: Request,
        body: PersistentStopRequest,
        conversation_id: str = _path_id(),
        request_id: str = Path(min_length=1, max_length=128),
    ) -> PersistentStopResponse:
        if body.request_id != request_id:
            raise PersistentWebError(422, "invalid_request", "The request is invalid.")
        await asyncio.to_thread(
            _service(request).cancel_active_generation,
            conversation_id=ConversationId(value=conversation_id),
            request_id=request_id,
            expected_revision=body.expected_revision,
        )
        return PersistentStopResponse()

    return router


async def _archive_mutation(
    request: Request,
    conversation_id: str,
    body: PersistentMutationRequest,
    *,
    archived: bool,
) -> PersistentMutationResponse:
    service = _service(request)
    operation_id = _operation("archive" if archived else "unarchive", body.operation_id)
    await _reject_applied(service, operation_id)
    stored = await asyncio.to_thread(
        service.set_archived,
        conversation_id=ConversationId(value=conversation_id),
        operation_id=operation_id,
        expected_revision=body.expected_revision,
        archived=archived,
    )
    return PersistentMutationResponse(detail=await _project_detail(service, stored))


async def _derived_stream_response(
    *,
    request: Request,
    conversation_id: str,
    source_turn_id: str,
    origin: ConversationTurnOrigin,
    body: PersistentDerivedStreamRequest,
) -> StreamingResponse:
    service = _service(request)
    identities = _generation_identities(body.operation_id)
    await _reject_applied(service, identities.append_operation_id)
    events = service.generate_derived_turn(
        conversation_id=ConversationId(value=conversation_id),
        source_turn_id=ConversationTurnId(value=source_turn_id),
        origin=origin,
        expected_revision=body.expected_revision,
        settings=body.settings,
        identities=identities,
    )
    return await _stream_response(
        request=request,
        service=service,
        conversation_id=ConversationId(value=conversation_id),
        turn_id=identities.turn_id,
        events=events,
    )


async def _stream_response(
    *,
    request: Request,
    service: PersistentConversationService,
    conversation_id: ConversationId,
    turn_id: ConversationTurnId,
    events: Iterator[ConversationEvent],
) -> StreamingResponse:
    bridge = PersistentSseBridge(
        events=events,
        service=service,
        conversation_id=conversation_id,
        turn_id=turn_id,
    )
    await bridge.prepare()
    return StreamingResponse(
        bridge.stream(request),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"},
    )


async def _reject_applied(
    service: PersistentConversationService,
    operation_id: ConversationOperationId,
) -> None:
    if await asyncio.to_thread(service.operation_was_applied, operation_id):
        raise PersistentWebError(
            409,
            "operation_already_applied",
            "The operation was already applied. Reload the conversation detail.",
        )


def _optional_service(request: Request) -> PersistentConversationService | None:
    runtime: WebRuntime = request.app.state.runtime
    return runtime.persistent_conversation


def _service(request: Request) -> PersistentConversationService:
    service = _optional_service(request)
    if service is None:
        raise PersistentWebError(
            404,
            "persistent_conversation_unavailable",
            "Persistent conversations are unavailable.",
        )
    return service


async def _project_detail(
    service: PersistentConversationService,
    stored: StoredConversation,
) -> PersistentConversationDetailResponse:
    """Project a `StoredConversation` including its persisted citation evidence."""

    citations = await asyncio.to_thread(
        service.get_conversation_citations,
        stored.conversation.conversation_id,
    )
    return project_persistent_detail(stored, citations_by_turn=citations)


def persistent_error_response(error: BaseException) -> JSONResponse:
    if isinstance(error, PersistentWebError):
        content: dict[str, object] = {"code": error.code, "message": error.message}
        if error.current_revision is not None:
            content["current_revision"] = error.current_revision
        return JSONResponse(status_code=error.status_code, content=content)
    if isinstance(error, PersistentConversationError):
        status, code = {
            PersistentConversationErrorCode.NOT_FOUND: (404, "not_found"),
            PersistentConversationErrorCode.INVALID_LIFECYCLE: (409, "invalid_lifecycle"),
            PersistentConversationErrorCode.GENERATION_CONTEXT_LIMIT_EXCEEDED: (
                422,
                "invalid_request",
            ),
            PersistentConversationErrorCode.STORAGE_NOT_READY: (423, "storage_not_ready"),
            PersistentConversationErrorCode.TERMINAL_PERSISTENCE_FAILED: (
                503,
                "storage_unavailable",
            ),
            PersistentConversationErrorCode.GENERATION_NOT_ACTIVE: (
                404,
                "generation_not_active",
            ),
        }[error.code]
        return JSONResponse(
            status_code=status,
            content={"code": code, "message": error.safe_message},
        )
    if isinstance(error, ConversationStorageError):
        if error.code is ConversationStorageErrorCode.CONFLICT:
            content = {
                "code": "revision_conflict",
                "message": "The conversation changed. Reload the conversation detail.",
            }
            if error.actual_revision is not None:
                content["current_revision"] = error.actual_revision
            return JSONResponse(status_code=409, content=content)
        if error.code in {
            ConversationStorageErrorCode.MIGRATION_REQUIRED,
            ConversationStorageErrorCode.MIGRATION_INCOMPLETE,
            ConversationStorageErrorCode.UNSUPPORTED_SCHEMA,
        }:
            return JSONResponse(
                status_code=423,
                content={
                    "code": "storage_not_ready",
                    "message": "The conversation store is not ready.",
                },
            )
        return JSONResponse(
            status_code=503,
            content={
                "code": "storage_unavailable",
                "message": "The conversation store is unavailable.",
            },
        )
    raise TypeError("unsupported persistent error")


def _mapped(kind: str, client_operation_id: str) -> str:
    return hashlib.sha512(
        _WEB_ID_DOMAIN + kind.encode("ascii") + b"\0" + client_operation_id.encode("utf-8")
    ).hexdigest()


def _operation(kind: str, client_operation_id: str) -> ConversationOperationId:
    return ConversationOperationId(value=_mapped(kind, client_operation_id))


def _conversation_id(client_operation_id: str) -> ConversationId:
    return ConversationId(value=_mapped("conversation", client_operation_id))


def _session_id(kind: str, client_operation_id: str) -> ConversationSessionId:
    return ConversationSessionId(value=_mapped(kind, client_operation_id))


def _generation_identities(client_operation_id: str) -> PersistentGenerationIdentities:
    return PersistentGenerationIdentities(
        turn_id=ConversationTurnId(value=_mapped("turn", client_operation_id)),
        user_message_id=ConversationMessageId(value=_mapped("user-message", client_operation_id)),
        assistant_message_id=ConversationMessageId(
            value=_mapped("assistant-message", client_operation_id)
        ),
        append_operation_id=_operation("append", client_operation_id),
        start_operation_id=_operation("start", client_operation_id),
        terminal_operation_id=_operation("terminal", client_operation_id),
    )


def _path_id() -> Any:
    return Path(min_length=1, max_length=128, pattern=WEB_ID_PATTERN)


def _turn_path_id() -> Any:
    return Path(min_length=1, max_length=128, pattern=WEB_ID_PATTERN)


def raise_persistent_error(error: BaseException) -> NoReturn:
    """Typing helper used by the application-level exception handlers."""

    raise error
