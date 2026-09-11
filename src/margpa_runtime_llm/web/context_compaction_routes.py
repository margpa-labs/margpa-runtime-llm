"""Local-private `/api/v8/context-compaction` routes (Phase 9-3, CL-P9-3-F).

Compaction Core has no separate opt-in flag: it is `enabled` exactly when
Persistent Conversation itself is (see `WebRuntime.context_compaction_
coordinator`'s own docstring) -- absent, every route below degrades to the
same `context_compaction_unavailable` Disabled Contract, mirroring
`persistent_routes.py`'s own `persistent_conversation_unavailable` shape.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import Field

from margpa_runtime_llm.modules.context_compaction.application.coordinator import (
    CompactionCoordinator,
)
from margpa_runtime_llm.modules.context_compaction.domain.artifacts import (
    CompactionAttempt,
    CompactionAttemptState,
)
from margpa_runtime_llm.modules.context_compaction.domain.errors import (
    ContextCompactionDomainError,
)
from margpa_runtime_llm.modules.conversation.domain import ConversationId
from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .contracts import WebRuntime

CONTEXT_COMPACTION_API_PREFIX = "/api/v8/context-compaction"
_DEFAULT_GENERATION_RESERVE_TOKENS = 1024
_TERMINAL_ATTEMPT_STATES = frozenset(
    {
        CompactionAttemptState.COMPLETED,
        CompactionAttemptState.REJECTED,
        CompactionAttemptState.FAILED,
        CompactionAttemptState.CANCELLED,
        CompactionAttemptState.CONFLICTED,
        CompactionAttemptState.ROLLED_BACK,
        CompactionAttemptState.INTERRUPTED_BY_RESTART,
    }
)


@dataclass(frozen=True, slots=True)
class ContextCompactionWebError(Exception):
    status_code: int
    code: str
    message: str


def context_compaction_error_response(error: BaseException) -> JSONResponse:
    if isinstance(error, ContextCompactionWebError):
        return JSONResponse(
            status_code=error.status_code, content={"code": error.code, "message": error.message}
        )
    if isinstance(error, ContextCompactionDomainError):
        return JSONResponse(
            status_code=409, content={"code": error.code.value, "message": error.safe_message}
        )
    return JSONResponse(
        status_code=500,
        content={"code": "internal_error", "message": "An internal error occurred."},
    )


def _disabled_error() -> ContextCompactionWebError:
    return ContextCompactionWebError(
        503,
        "context_compaction_unavailable",
        "Context Compaction is not enabled in this deployment.",
    )


def _optional_coordinator(request: Request) -> CompactionCoordinator | None:
    runtime: WebRuntime = request.app.state.runtime
    return runtime.context_compaction_coordinator


def _coordinator(request: Request) -> CompactionCoordinator:
    coordinator = _optional_coordinator(request)
    if coordinator is None:
        raise _disabled_error()
    return coordinator


class StatusResponse(ImmutableContract):
    enabled: bool
    auto_compaction_enabled: bool | None = None


class MeasuredTokensResponse(ImmutableContract):
    value: int | None
    measurement_class: str
    source: str


class BudgetResponse(ImmutableContract):
    conversation_id: str
    source_conversation_revision: int
    pressure: str
    model_context_capacity: MeasuredTokensResponse
    current_prompt_usage: MeasuredTokensResponse


class PreviewResponse(ImmutableContract):
    feasible: bool
    reason: str | None
    pressure: str
    estimated_token_reduction: int | None


class AttemptResponse(ImmutableContract):
    attempt_id: str
    state: str
    is_terminal: bool
    structured_context_id: str | None = None
    terminal_reason: str | None = None
    error_code: str | None = None


class RollbackResponse(ImmutableContract):
    attempt_id: str
    result: str


class HandoffResponse(ImmutableContract):
    handoff_artifact_id: str
    current_objective: str
    current_position: str
    exact_next_route: str
    recent_verbatim_tail_markdown: str


class AutoPolicyRequest(ImmutableContract):
    enabled: bool


class CompactRequest(ImmutableContract):
    generation_reserve_tokens: int = Field(
        default=_DEFAULT_GENERATION_RESERVE_TOKENS, gt=0, le=32_768
    )


def _attempt_response(attempt: CompactionAttempt) -> AttemptResponse:
    return AttemptResponse(
        attempt_id=attempt.attempt_id.value,
        state=attempt.state.value,
        is_terminal=attempt.state in _TERMINAL_ATTEMPT_STATES,
        structured_context_id=(
            attempt.structured_context_id.value
            if attempt.structured_context_id is not None
            else None
        ),
        terminal_reason=attempt.terminal_reason,
        error_code=attempt.error_code,
    )


def _measured(value: object) -> MeasuredTokensResponse:
    return MeasuredTokensResponse(
        value=value.value,  # type: ignore[attr-defined]
        measurement_class=value.measurement_class.value,  # type: ignore[attr-defined]
        source=value.source,  # type: ignore[attr-defined]
    )


def create_context_compaction_router() -> APIRouter:
    router = APIRouter(prefix=CONTEXT_COMPACTION_API_PREFIX)

    @router.get("/status", response_model=StatusResponse)
    async def status(request: Request) -> StatusResponse:
        runtime: WebRuntime = request.app.state.runtime
        coordinator = runtime.context_compaction_coordinator
        auto_policy = runtime.context_compaction_auto_policy
        return StatusResponse(
            enabled=coordinator is not None,
            auto_compaction_enabled=(
                auto_policy.is_enabled() if auto_policy is not None else None
            ),
        )

    @router.put("/auto-policy", response_model=StatusResponse)
    async def set_auto_policy(request: Request, body: AutoPolicyRequest) -> StatusResponse:
        runtime: WebRuntime = request.app.state.runtime
        if runtime.context_compaction_auto_policy is None:
            raise _disabled_error()
        runtime.context_compaction_auto_policy.set_enabled(body.enabled)
        return StatusResponse(
            enabled=True,
            auto_compaction_enabled=runtime.context_compaction_auto_policy.is_enabled(),
        )

    @router.get("/{conversation_id}/budget", response_model=BudgetResponse)
    async def budget(request: Request, conversation_id: str) -> BudgetResponse:
        coordinator = _coordinator(request)
        result = await asyncio.to_thread(
            coordinator.budget,
            ConversationId(value=conversation_id),
            generation_reserve_tokens=_DEFAULT_GENERATION_RESERVE_TOKENS,
        )
        if result is None:
            raise ContextCompactionWebError(
                404, "no_completed_turn", "The conversation has no completed turn yet."
            )
        snapshot, pressure = result
        return BudgetResponse(
            conversation_id=conversation_id,
            source_conversation_revision=snapshot.source_conversation_revision,
            pressure=pressure.value,
            model_context_capacity=_measured(snapshot.model_context_capacity),
            current_prompt_usage=_measured(snapshot.current_prompt_usage),
        )

    @router.post("/{conversation_id}/preview", response_model=PreviewResponse)
    async def preview(
        request: Request, conversation_id: str, body: CompactRequest | None = None
    ) -> PreviewResponse:
        coordinator = _coordinator(request)
        reserve = body.generation_reserve_tokens if body is not None else (
            _DEFAULT_GENERATION_RESERVE_TOKENS
        )
        result = await asyncio.to_thread(
            coordinator.preview,
            ConversationId(value=conversation_id),
            generation_reserve_tokens=reserve,
        )
        if result is None:
            raise ContextCompactionWebError(
                404, "no_completed_turn", "The conversation has no completed turn yet."
            )
        return PreviewResponse(
            feasible=result.feasible,
            reason=result.reason,
            pressure=result.pressure.value,
            estimated_token_reduction=result.estimated_token_reduction,
        )

    @router.post("/{conversation_id}/compact", response_model=AttemptResponse, status_code=202)
    async def compact(
        request: Request, conversation_id: str, body: CompactRequest | None = None
    ) -> AttemptResponse:
        coordinator = _coordinator(request)
        reserve = body.generation_reserve_tokens if body is not None else (
            _DEFAULT_GENERATION_RESERVE_TOKENS
        )
        attempt = await asyncio.to_thread(
            coordinator.request_manual_compaction,
            ConversationId(value=conversation_id),
            generation_reserve_tokens=reserve,
        )
        return _attempt_response(attempt)

    @router.get("/attempts/{attempt_id}", response_model=AttemptResponse)
    async def get_attempt(request: Request, attempt_id: str) -> AttemptResponse:
        coordinator = _coordinator(request)
        attempt = coordinator.get_attempt(attempt_id)
        if attempt is None:
            raise ContextCompactionWebError(
                404, "attempt_not_found", "The requested Compaction Attempt does not exist."
            )
        return _attempt_response(attempt)

    @router.post("/attempts/{attempt_id}/cancel", response_model=AttemptResponse)
    async def cancel_attempt(request: Request, attempt_id: str) -> AttemptResponse:
        coordinator = _coordinator(request)
        coordinator.request_cancel(attempt_id)
        attempt = coordinator.get_attempt(attempt_id)
        if attempt is None:
            raise ContextCompactionWebError(
                404, "attempt_not_found", "The requested Compaction Attempt does not exist."
            )
        return _attempt_response(attempt)

    @router.post("/attempts/{attempt_id}/rollback", response_model=RollbackResponse)
    async def rollback(request: Request, attempt_id: str) -> RollbackResponse:
        coordinator = _coordinator(request)
        record = await asyncio.to_thread(coordinator.rollback, attempt_id)
        return RollbackResponse(attempt_id=attempt_id, result=record.result.value)

    @router.get("/{conversation_id}/handoff", response_model=HandoffResponse)
    async def handoff(request: Request, conversation_id: str) -> HandoffResponse:
        coordinator = _coordinator(request)
        artifact = await asyncio.to_thread(
            coordinator.build_handoff,
            ConversationId(value=conversation_id),
            handoff_artifact_id_value=f"handoff-{conversation_id}",
        )
        if artifact is None:
            raise ContextCompactionWebError(
                404, "no_completed_turn", "The conversation has no completed turn yet."
            )
        tail_lines = [
            f"**{turn.role}**: {turn.content}" for turn in artifact.sections.recent_verbatim_tail
        ]
        return HandoffResponse(
            handoff_artifact_id=artifact.handoff_artifact_id.value,
            current_objective=artifact.sections.current_objective,
            current_position=artifact.sections.current_position,
            exact_next_route=artifact.sections.exact_next_route,
            recent_verbatim_tail_markdown="\n\n".join(tail_lines),
        )

    return router
