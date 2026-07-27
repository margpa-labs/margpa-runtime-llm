"""One-shot and streaming generation contracts."""

from collections.abc import Iterator
from enum import StrEnum
from types import TracebackType
from typing import Protocol

from pydantic import Field, field_validator, model_validator

from .base import ImmutableContract
from .messages import ChatMessage
from .runtime import InferenceWarning, ModelRuntimeReference


class ThinkingMode(StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    MODEL_DEFAULT = "model_default"


class GenerationParameters(ImmutableContract):
    max_new_tokens: int = Field(default=512, gt=0)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.8, gt=0.0, le=1.0)
    top_k: int = Field(default=20, ge=0)
    min_p: float = Field(default=0.0, ge=0.0, le=1.0)
    presence_penalty: float = Field(default=1.5, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    repeat_penalty: float = Field(default=1.0, gt=0.0)
    seed: int | None = None
    stop_sequences: tuple[str, ...] = ()
    thinking_mode: ThinkingMode = ThinkingMode.DISABLED

    @field_validator("stop_sequences")
    @classmethod
    def validate_stop_sequences(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item for item in value):
            raise ValueError("stop sequences must not contain an empty string")
        if len(set(value)) != len(value):
            raise ValueError("stop sequences must be unique")
        return value


class GenerationRequest(ImmutableContract):
    request_id: str
    model_key: str
    messages: tuple[ChatMessage, ...]
    parameters: GenerationParameters = GenerationParameters()

    @field_validator("request_id", "model_key")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("identifier must not be blank")
        return value

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, value: tuple[ChatMessage, ...]) -> tuple[ChatMessage, ...]:
        if not value:
            raise ValueError("at least one message is required")
        return value


class FinishReason(StrEnum):
    STOP = "stop"
    LENGTH = "length"
    CANCELLED = "cancelled"
    TOOL_CALL = "tool_call"
    CONTENT_FILTER = "content_filter"
    UNKNOWN = "unknown"


class TokenUsage(ImmutableContract):
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_total(self) -> "TokenUsage":
        if self.total_tokens != self.prompt_tokens + self.completion_tokens:
            raise ValueError("total_tokens must equal prompt_tokens + completion_tokens")
        return self


class GenerationTiming(ImmutableContract):
    first_content_latency_seconds: float | None = Field(default=None, ge=0.0)
    total_generation_seconds: float = Field(ge=0.0)
    tokens_per_second: float | None = Field(default=None, ge=0.0)


class GenerationResult(ImmutableContract):
    request_id: str
    model_key: str
    content: str
    finish_reason: FinishReason
    backend_finish_reason: str | None = None
    usage: TokenUsage | None = None
    timing: GenerationTiming
    runtime_info: ModelRuntimeReference
    warnings: tuple[InferenceWarning, ...] = ()


class GenerationChunk(ImmutableContract):
    request_id: str
    sequence: int = Field(ge=0)
    text_delta: str
    is_final: bool
    finish_reason: FinishReason | None = None
    usage: TokenUsage | None = None

    @model_validator(mode="after")
    def validate_terminal_fields(self) -> "GenerationChunk":
        if self.is_final and self.finish_reason is None:
            raise ValueError("a final chunk requires finish_reason")
        if not self.is_final and (self.finish_reason is not None or self.usage is not None):
            raise ValueError("only a final chunk may contain terminal fields")
        return self


class GenerationTerminalState(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CLOSED_BY_CONSUMER = "closed_by_consumer"
    FAILED = "failed"


class GenerationStream(Protocol):
    @property
    def generation_id(self) -> str: ...

    @property
    def terminal_state(self) -> GenerationTerminalState: ...

    @property
    def timing(self) -> GenerationTiming | None: ...

    def __iter__(self) -> Iterator[GenerationChunk]: ...

    def cancel(self) -> None: ...

    def close(self) -> None: ...

    def __enter__(self) -> "GenerationStream": ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
