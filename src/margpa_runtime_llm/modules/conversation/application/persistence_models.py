"""Application-level safe contracts for persistent conversations."""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from ..domain import (
    ConversationMessageId,
    ConversationOperationId,
    ConversationTurnId,
)

type PersistenceSafeDetail = str | int | float | bool | None


class PersistentConversationErrorCode(StrEnum):
    NOT_FOUND = "not_found"
    INVALID_LIFECYCLE = "invalid_lifecycle"
    GENERATION_CONTEXT_LIMIT_EXCEEDED = "generation_context_limit_exceeded"
    STORAGE_NOT_READY = "storage_not_ready"
    TERMINAL_PERSISTENCE_FAILED = "terminal_persistence_failed"
    GENERATION_NOT_ACTIVE = "generation_not_active"


class PersistentConversationError(Exception):
    """Safe application failure with no raw storage or message material."""

    def __init__(
        self,
        *,
        code: PersistentConversationErrorCode,
        safe_message: str,
        retryable: bool = False,
        details: Mapping[str, PersistenceSafeDetail] | None = None,
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.retryable = retryable
        self.details = MappingProxyType(dict(details or {}))

    def to_safe_dict(self) -> dict[str, object]:
        return {
            "code": self.code.value,
            "safe_message": self.safe_message,
            "retryable": self.retryable,
            "details": dict(self.details),
        }


class PersistentServiceReadiness(StrEnum):
    NOT_READY = "not_ready"
    READY = "ready"
    FAILED = "failed"


class RecoveryResult(ImmutableContract):
    inspected_conversations: int
    recovered_conversations: int


class PersistentGenerationIdentities(ImmutableContract):
    turn_id: ConversationTurnId
    user_message_id: ConversationMessageId
    assistant_message_id: ConversationMessageId
    append_operation_id: ConversationOperationId
    start_operation_id: ConversationOperationId
    terminal_operation_id: ConversationOperationId
