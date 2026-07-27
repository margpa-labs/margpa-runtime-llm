"""Stable Phase 1-G conversation application surface."""

from .application.conversation_generation import (
    SUMMARY_FALLBACK_WARNING,
    TOKEN_LIMIT_WARNING,
    ConversationGenerationService,
    ConversationGenerationSession,
)
from .contracts import (
    MAX_CONVERSATION_MESSAGE_CHARACTERS,
    MAX_CONVERSATION_MESSAGES,
    MAX_CONVERSATION_TOTAL_CHARACTERS,
    MAX_WEB_NEW_TOKENS,
    ConversationDeltaChannel,
    ConversationEvent,
    ConversationEventType,
    ConversationGenerationInput,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
)

__all__ = [
    "MAX_CONVERSATION_MESSAGES",
    "MAX_CONVERSATION_MESSAGE_CHARACTERS",
    "MAX_CONVERSATION_TOTAL_CHARACTERS",
    "MAX_WEB_NEW_TOKENS",
    "SUMMARY_FALLBACK_WARNING",
    "TOKEN_LIMIT_WARNING",
    "ConversationDeltaChannel",
    "ConversationEvent",
    "ConversationEventType",
    "ConversationGenerationInput",
    "ConversationGenerationService",
    "ConversationGenerationSession",
    "ConversationMessage",
    "ConversationRole",
    "ConversationSettings",
]
