"""Map persisted canonical branch history into the unchanged v1 generation input."""

from __future__ import annotations

from pydantic import ValidationError

from ..contracts import (
    ConversationGenerationInput,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
)
from ..domain import (
    ConversationSnapshot,
    ConversationTurnId,
    PersistedConversationRole,
    project_generation_history,
)
from .persistence_models import (
    PersistentConversationError,
    PersistentConversationErrorCode,
)


def map_generation_context(
    snapshot: ConversationSnapshot,
    *,
    pending_turn_id: ConversationTurnId,
    settings: ConversationSettings,
) -> ConversationGenerationInput:
    persisted = project_generation_history(snapshot, pending_turn_id=pending_turn_id)
    messages = tuple(
        ConversationMessage(
            role=(
                ConversationRole.USER
                if item.role is PersistedConversationRole.USER
                else ConversationRole.ASSISTANT
            ),
            content=item.content,
        )
        for item in persisted
    )
    try:
        return ConversationGenerationInput(messages=messages, settings=settings)
    except ValidationError:
        raise PersistentConversationError(
            code=PersistentConversationErrorCode.GENERATION_CONTEXT_LIMIT_EXCEEDED,
            safe_message="The conversation context exceeds the generation limit.",
        ) from None
