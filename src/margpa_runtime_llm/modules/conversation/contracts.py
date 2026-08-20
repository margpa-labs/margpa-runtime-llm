"""Framework-independent contracts for ephemeral multi-turn generation."""

from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode

MAX_CONVERSATION_MESSAGES = 64
MAX_CONVERSATION_MESSAGE_CHARACTERS = 32_768
MAX_CONVERSATION_TOTAL_CHARACTERS = 131_072
MAX_WEB_NEW_TOKENS = 2_048


class ConversationRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class ConversationMessage(ImmutableContract):
    role: ConversationRole
    content: str = Field(max_length=MAX_CONVERSATION_MESSAGE_CHARACTERS)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("conversation message content must not be blank")
        return value


class ContextUsagePromptInjectionMode(StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"


class ExpressiveMode(StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"


class ConversationSettings(ImmutableContract):
    response_language: ResponseLanguage
    max_new_tokens: int = Field(strict=True, gt=0, le=MAX_WEB_NEW_TOKENS)
    thinking_mode: ThinkingMode = ThinkingMode.DISABLED
    thinking_visibility: ThinkingVisibility
    summary_mode: SummaryMode = SummaryMode.OFF
    documentation_rag_mode: DocumentationRagMode = DocumentationRagMode.DISABLED
    context_usage_prompt_injection_mode: ContextUsagePromptInjectionMode = (
        ContextUsagePromptInjectionMode.DISABLED
    )
    expressive_mode: ExpressiveMode = ExpressiveMode.DISABLED

    @field_validator("thinking_mode")
    @classmethod
    def reject_model_default_thinking_mode(cls, value: ThinkingMode) -> ThinkingMode:
        if value is ThinkingMode.MODEL_DEFAULT:
            raise ValueError("web thinking mode must be disabled or enabled")
        return value


class ConversationGenerationInput(ImmutableContract):
    messages: tuple[ConversationMessage, ...] = Field(
        min_length=1,
        max_length=MAX_CONVERSATION_MESSAGES,
    )
    settings: ConversationSettings

    @model_validator(mode="after")
    def validate_history(self) -> "ConversationGenerationInput":
        if self.messages[-1].role is not ConversationRole.USER:
            raise ValueError("the final conversation message must have the user role")
        expected = ConversationRole.USER
        total_characters = 0
        for message in self.messages:
            if message.role is not expected:
                raise ValueError("conversation roles must alternate from user to assistant")
            expected = (
                ConversationRole.ASSISTANT
                if expected is ConversationRole.USER
                else ConversationRole.USER
            )
            total_characters += len(message.content)
        if total_characters > MAX_CONVERSATION_TOTAL_CHARACTERS:
            raise ValueError("conversation history is too large")
        return self


class ConversationEventType(StrEnum):
    START = "start"
    STATUS = "status"
    RETRIEVAL = "retrieval"
    DELTA = "delta"
    WARNING = "warning"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class ConversationDeltaChannel(StrEnum):
    REASONING = "reasoning"
    FINAL = "final"


class ConversationEvent(ImmutableContract):
    event: ConversationEventType
    data: dict[str, object] = Field(default_factory=dict)
