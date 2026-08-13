"""Safe errors for persistent conversation domain and storage boundaries."""

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType

type ConversationSafeDetail = str | int | float | bool | None


class ConversationDomainErrorCode(StrEnum):
    INVALID_IDENTITY = "invalid_identity"
    INVALID_TRANSITION = "invalid_transition"
    INVARIANT_VIOLATION = "invariant_violation"


class ConversationDomainError(Exception):
    def __init__(
        self,
        *,
        code: ConversationDomainErrorCode,
        safe_message: str,
        details: Mapping[str, ConversationSafeDetail] | None = None,
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.details: Mapping[str, ConversationSafeDetail] = MappingProxyType(dict(details or {}))

    def to_safe_dict(self) -> dict[str, object]:
        return {
            "code": self.code.value,
            "safe_message": self.safe_message,
            "details": dict(self.details),
        }


class StorageMutationOutcome(StrEnum):
    NOT_APPLIED = "not_applied"
    APPLIED = "applied"
    UNKNOWN = "unknown"


class ConversationStorageErrorCode(StrEnum):
    CONFLICT = "conflict"
    INVALID_RECORD = "invalid_record"
    UNSUPPORTED_SCHEMA = "unsupported_schema"
    MIGRATION_REQUIRED = "migration_required"
    MIGRATION_INCOMPLETE = "migration_incomplete"
    CORRUPT_DATA = "corrupt_data"
    STORAGE_UNAVAILABLE = "storage_unavailable"
    STORAGE_TIMEOUT = "storage_timeout"
    CAPACITY_EXCEEDED = "capacity_exceeded"
    PERMISSION_DENIED = "permission_denied"
    READ_ONLY = "read_only"
    ATOMIC_COMMIT_FAILED = "atomic_commit_failed"


class ConversationStorageError(Exception):
    """Storage-independent error whose public representation contains no raw data."""

    def __init__(
        self,
        *,
        code: ConversationStorageErrorCode,
        safe_message: str,
        retryable: bool = False,
        mutation_outcome: StorageMutationOutcome = StorageMutationOutcome.NOT_APPLIED,
        conversation_id: str | None = None,
        operation_id: str | None = None,
        expected_revision: int | None = None,
        actual_revision: int | None = None,
        details: Mapping[str, ConversationSafeDetail] | None = None,
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.retryable = retryable
        self.mutation_outcome = mutation_outcome
        self.conversation_id = conversation_id
        self.operation_id = operation_id
        self.expected_revision = expected_revision
        self.actual_revision = actual_revision
        self.details: Mapping[str, ConversationSafeDetail] = MappingProxyType(dict(details or {}))

    def to_safe_dict(self) -> dict[str, object]:
        return {
            "code": self.code.value,
            "safe_message": self.safe_message,
            "retryable": self.retryable,
            "mutation_outcome": self.mutation_outcome.value,
            "conversation_id": self.conversation_id,
            "operation_id": self.operation_id,
            "expected_revision": self.expected_revision,
            "actual_revision": self.actual_revision,
            "details": dict(self.details),
        }
