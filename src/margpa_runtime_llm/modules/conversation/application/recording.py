"""Sensitive-data-minimized recording boundary; no concrete recorder is provided."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol, runtime_checkable

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from ..domain import ConversationId, ConversationScopeId, ConversationTurnId


class ConversationRecordingMode(StrEnum):
    OFF = "off"


class ConversationRecordingOutcome(StrEnum):
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class ConversationRecordingMetadata(ImmutableContract):
    """Metadata deliberately unable to represent message or hidden model content."""

    scope_id: ConversationScopeId
    conversation_id: ConversationId
    turn_id: ConversationTurnId
    outcome: ConversationRecordingOutcome
    occurred_at_utc: str = Field(min_length=1, max_length=64)
    duration_ms: int | None = Field(default=None, strict=True, ge=0)
    input_tokens: int | None = Field(default=None, strict=True, ge=0)
    output_tokens: int | None = Field(default=None, strict=True, ge=0)
    configuration_digest: str | None = Field(
        default=None,
        pattern=r"^[a-f0-9]{128}$",
    )


@runtime_checkable
class ConversationRecordingPort(Protocol):
    def record(self, event: ConversationRecordingMetadata) -> None: ...
