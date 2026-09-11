"""Safe, typed Context Compaction domain failures."""

from __future__ import annotations

from enum import StrEnum


class ContextCompactionDomainErrorCode(StrEnum):
    CORE_UNAVAILABLE = "core_unavailable"
    """Persistent Conversation is not enabled -- Compaction Core has no
    Canonical Conversation to snapshot/compact against (SS5.1 `core_state
    = unavailable`), not a disabled Mode."""
    DISABLED_BY_INTERNAL_SAFETY_GATE = "disabled_by_internal_safety_gate"
    MANUAL_COMPACTION_REQUIRED = "manual_compaction_required"
    """Hard Reserve reached with Auto Compaction OFF: ordinary Generation
    is temporarily refused; Manual Compaction stays available."""
    SNAPSHOT_FAILED = "snapshot_failed"
    CANDIDATE_REJECTED = "candidate_rejected"
    VALIDATION_FAILED = "validation_failed"
    PERSISTENCE_FAILED = "persistence_failed"
    REVISION_CONFLICT = "revision_conflict"
    STALE_REVISION = "stale_revision"
    ATTEMPT_NOT_FOUND = "attempt_not_found"
    ATTEMPT_NOT_CANCELLABLE = "attempt_not_cancellable"
    ATTEMPT_ALREADY_TERMINAL = "attempt_already_terminal"
    ARTIFACT_NOT_FOUND = "artifact_not_found"
    ARTIFACT_DIGEST_MISMATCH = "artifact_digest_mismatch"
    ARTIFACT_CORRUPT = "artifact_corrupt"
    UNKNOWN_SCHEMA_VERSION = "unknown_schema_version"
    REHYDRATION_NOT_FOUND = "rehydration_not_found"
    REHYDRATION_CONFLICT = "rehydration_conflict"
    REHYDRATION_STALE = "rehydration_stale"
    REHYDRATION_BUDGET_EXCEEDED = "rehydration_budget_exceeded"
    INVALID_LIFECYCLE = "invalid_lifecycle"


class ContextCompactionDomainError(Exception):
    """Safe application-facing failure carrying no raw storage/model detail."""

    def __init__(self, *, code: ContextCompactionDomainErrorCode, safe_message: str) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message

    def to_safe_dict(self) -> dict[str, object]:
        return {"code": self.code.value, "safe_message": self.safe_message}
