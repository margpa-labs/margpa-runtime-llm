"""Safe errors for the audit/evidence domain and storage boundaries."""

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType

type AuditSafeDetail = str | int | float | bool | None


class AuditDomainErrorCode(StrEnum):
    INVALID_IDENTITY = "invalid_identity"
    INVALID_EVENT_KIND = "invalid_event_kind"
    INVALID_PAYLOAD = "invalid_payload"
    INVALID_TIMESTAMP = "invalid_timestamp"


class AuditDomainError(Exception):
    def __init__(
        self,
        *,
        code: AuditDomainErrorCode,
        safe_message: str,
        details: Mapping[str, AuditSafeDetail] | None = None,
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.details: Mapping[str, AuditSafeDetail] = MappingProxyType(dict(details or {}))

    def to_safe_dict(self) -> dict[str, object]:
        return {
            "code": self.code.value,
            "safe_message": self.safe_message,
            "details": dict(self.details),
        }


class EvidenceStoreErrorCode(StrEnum):
    APPEND_FAILED = "append_failed"
    DUPLICATE_EVENT = "duplicate_event"
    DIGEST_MISMATCH = "digest_mismatch"
    PARTIAL_TAIL = "partial_tail"
    UNKNOWN_SCHEMA = "unknown_schema"
    PATH_VIOLATION = "path_violation"
    STORE_UNAVAILABLE = "store_unavailable"
    DEGRADED = "degraded"
    CAPACITY_EXCEEDED = "capacity_exceeded"


class EvidenceStoreError(Exception):
    """Storage-independent error whose public representation contains no raw data."""

    def __init__(
        self,
        *,
        code: EvidenceStoreErrorCode,
        safe_message: str,
        run_id: str | None = None,
        event_id: str | None = None,
        details: Mapping[str, AuditSafeDetail] | None = None,
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.run_id = run_id
        self.event_id = event_id
        self.details: Mapping[str, AuditSafeDetail] = MappingProxyType(dict(details or {}))

    def to_safe_dict(self) -> dict[str, object]:
        return {
            "code": self.code.value,
            "safe_message": self.safe_message,
            "run_id": self.run_id,
            "event_id": self.event_id,
            "details": dict(self.details),
        }
