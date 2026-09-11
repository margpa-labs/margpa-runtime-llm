"""Read-only access to the Canonical Conversation (SS7's "original/legacy
projection" input) -- Compaction never writes through this Port."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.conversation.domain.identity import (
    ConversationId,
    ConversationMessageId,
    ConversationTurnId,
)
from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from ..domain.identity import ContextBranchId


class SourceConversationTurn(ImmutableContract):
    turn_id: ConversationTurnId
    sequence: int = Field(ge=0)
    user_message_id: ConversationMessageId
    user_content: str = Field(min_length=1)
    assistant_message_id: ConversationMessageId | None = Field(default=None)
    assistant_content: str | None = Field(default=None)

    @model_validator(mode="after")
    def validate_assistant_pair(self) -> SourceConversationTurn:
        has_id = self.assistant_message_id is not None
        has_content = self.assistant_content is not None
        if has_id != has_content:
            raise ValueError("assistant message id and content must be set together")
        return self


class ConversationSourceProjection(ImmutableContract):
    """The completed branch, in chronological order, at one exact
    Conversation Revision -- exactly what `project_generation_history()`
    would build, but Compaction-shaped (per-Turn Source Identity retained
    rather than flattened into a message list)."""

    conversation_id: ConversationId
    branch_id: ContextBranchId
    source_conversation_revision: int = Field(ge=1)
    turns: tuple[SourceConversationTurn, ...] = Field(default=())


@runtime_checkable
class ConversationSourceProjectionPort(Protocol):
    def read(self, conversation_id: ConversationId) -> ConversationSourceProjection | None:
        """`None` when the Conversation does not exist or has no completed
        Turn yet (nothing to compact); never raises for a merely-empty
        Conversation."""
        ...
