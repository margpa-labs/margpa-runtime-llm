"""Map persisted canonical branch history into the unchanged v1 generation input."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import ValidationError

from ..contracts import (
    ConversationGenerationInput,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
)
from ..domain import (
    ConversationId,
    ConversationSnapshot,
    ConversationTurnId,
    PersistedConversationRole,
    project_generation_history,
)
from .persistence_models import (
    PersistentConversationError,
    PersistentConversationErrorCode,
)


@runtime_checkable
class ActiveContextProjectionPort(Protocol):
    """Phase 9-3 CL-P9-3-E.5: an Optional Port consulted immediately before
    Generation Input is built. Absence (`None` passed to
    `map_generation_context`) or any Exception raised here must never break
    ordinary Chat -- both fall back to `original_messages` unchanged
    (Invariant: Compaction absence/failure must never affect other
    Components)."""

    def resolve_messages(
        self,
        *,
        conversation_id: ConversationId,
        current_source_revision: int,
        original_messages: tuple[ConversationMessage, ...],
    ) -> tuple[ConversationMessage, ...]: ...


def map_generation_context(
    snapshot: ConversationSnapshot,
    *,
    pending_turn_id: ConversationTurnId,
    settings: ConversationSettings,
    context_projection_port: ActiveContextProjectionPort | None = None,
    source_conversation_revision: int | None = None,
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
    if context_projection_port is not None and source_conversation_revision is not None:
        try:
            messages = context_projection_port.resolve_messages(
                conversation_id=snapshot.conversation_id,
                current_source_revision=source_conversation_revision,
                original_messages=messages,
            )
        except Exception:
            # Defense in depth: a Compaction-side failure degrades to the
            # original, unmodified projection -- never a broken/blocked Turn.
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
