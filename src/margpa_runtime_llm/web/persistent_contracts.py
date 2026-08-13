"""Typed safe contracts for the local-private persistent conversation API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from margpa_runtime_llm.modules.conversation.contracts import (
    MAX_CONVERSATION_MESSAGE_CHARACTERS,
    ConversationSettings,
)
from margpa_runtime_llm.modules.conversation.domain import ConversationSnapshot
from margpa_runtime_llm.modules.conversation.ports import ConversationPage, StoredConversation

WEB_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class _PersistentContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class PersistentRuntimeResponse(_PersistentContract):
    enabled: bool
    api_version: Literal["2"] = "2"
    source_of_truth: Literal["server"] = "server"
    features: tuple[str, ...] = ()


class PersistentCreateRequest(_PersistentContract):
    operation_id: str = Field(min_length=1, max_length=128, pattern=WEB_ID_PATTERN)
    expected_revision: None = None


class PersistentMutationRequest(_PersistentContract):
    operation_id: str = Field(min_length=1, max_length=128, pattern=WEB_ID_PATTERN)
    expected_revision: int = Field(strict=True, ge=1)


class PersistentTurnStreamRequest(PersistentMutationRequest):
    content: str = Field(max_length=MAX_CONVERSATION_MESSAGE_CHARACTERS)
    settings: ConversationSettings

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("persistent conversation content must not be blank")
        return value


class PersistentDerivedStreamRequest(PersistentMutationRequest):
    settings: ConversationSettings


class PersistentStopRequest(_PersistentContract):
    request_id: str = Field(min_length=1, max_length=128)
    expected_revision: int = Field(strict=True, ge=1)

    @field_validator("request_id")
    @classmethod
    def validate_request_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("request id must not be blank")
        return value


class PersistentConversationSummaryResponse(_PersistentContract):
    conversation_id: str
    state: str
    head_turn_id: str | None = None
    created_at: datetime
    updated_at: datetime


class PersistentConversationPageResponse(_PersistentContract):
    items: tuple[PersistentConversationSummaryResponse, ...]
    next_cursor: str | None = None


class PersistentSessionResponse(_PersistentContract):
    session_id: str
    state: str
    opened_at: datetime
    finished_at: datetime | None = None


class PersistentMessageResponse(_PersistentContract):
    role: Literal["user", "assistant"]
    content: str


class PersistentTurnResponse(_PersistentContract):
    turn_id: str
    sequence: int
    state: str
    origin: str
    parent_turn_id: str | None = None
    derived_from_turn_id: str | None = None
    request_id: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    messages: tuple[PersistentMessageResponse, ...]


class PersistentConversationDetailResponse(_PersistentContract):
    conversation_id: str
    state: str
    head_turn_id: str | None = None
    storage_revision: int
    created_at: datetime
    updated_at: datetime
    sessions: tuple[PersistentSessionResponse, ...]
    turns: tuple[PersistentTurnResponse, ...]


class PersistentMutationResponse(_PersistentContract):
    status: Literal["accepted"] = "accepted"
    detail: PersistentConversationDetailResponse


class PersistentStopResponse(_PersistentContract):
    status: Literal["cancellation_requested"] = "cancellation_requested"


def project_persistent_page(page: ConversationPage) -> PersistentConversationPageResponse:
    return PersistentConversationPageResponse(
        items=tuple(
            PersistentConversationSummaryResponse(
                conversation_id=item.conversation_id.value,
                state=item.state.value,
                head_turn_id=item.head_turn_id.value if item.head_turn_id is not None else None,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in page.items
        ),
        next_cursor=page.next_cursor,
    )


def project_persistent_detail(
    stored: StoredConversation,
) -> PersistentConversationDetailResponse:
    snapshot: ConversationSnapshot = stored.conversation
    messages_by_turn: dict[str, list[PersistentMessageResponse]] = {}
    for message in snapshot.messages:
        messages_by_turn.setdefault(message.turn_id.value, []).append(
            PersistentMessageResponse(role=message.role.value, content=message.content)
        )
    return PersistentConversationDetailResponse(
        conversation_id=snapshot.conversation_id.value,
        state=snapshot.state.value,
        head_turn_id=(snapshot.head_turn_id.value if snapshot.head_turn_id is not None else None),
        storage_revision=stored.storage_revision,
        created_at=snapshot.created_at,
        updated_at=snapshot.updated_at,
        sessions=tuple(
            PersistentSessionResponse(
                session_id=session.session_id.value,
                state=session.state.value,
                opened_at=session.opened_at,
                finished_at=session.finished_at,
            )
            for session in snapshot.sessions
        ),
        turns=tuple(
            PersistentTurnResponse(
                turn_id=turn.turn_id.value,
                sequence=turn.sequence,
                state=turn.state.value,
                origin=turn.origin.value,
                parent_turn_id=(
                    turn.parent_turn_id.value if turn.parent_turn_id is not None else None
                ),
                derived_from_turn_id=(
                    turn.derived_from_turn_id.value
                    if turn.derived_from_turn_id is not None
                    else None
                ),
                request_id=turn.request_id,
                started_at=turn.started_at,
                finished_at=turn.finished_at,
                messages=tuple(messages_by_turn.get(turn.turn_id.value, ())),
            )
            for turn in snapshot.turns
        ),
    )
