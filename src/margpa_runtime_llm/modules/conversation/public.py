"""Stable Phase 1-G conversation application surface."""

from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode

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
    ContextUsagePromptInjectionMode,
    ConversationDeltaChannel,
    ConversationEvent,
    ConversationEventType,
    ConversationGenerationInput,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
    ExpressiveMode,
)

__all__ = [
    "MAX_CONVERSATION_MESSAGES",
    "MAX_CONVERSATION_MESSAGE_CHARACTERS",
    "MAX_CONVERSATION_TOTAL_CHARACTERS",
    "MAX_WEB_NEW_TOKENS",
    "SUMMARY_FALLBACK_WARNING",
    "TOKEN_LIMIT_WARNING",
    "ContextUsagePromptInjectionMode",
    "ConversationDeltaChannel",
    "ConversationEvent",
    "ConversationEventType",
    "ConversationGenerationInput",
    "ConversationGenerationService",
    "ConversationGenerationSession",
    "ConversationMessage",
    "ConversationRole",
    "ConversationSettings",
    "DocumentationRagMode",
    "ExpressiveMode",
]
