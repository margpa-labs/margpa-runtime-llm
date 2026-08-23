"""Safe errors for the runtime governance domain (Phase 4)."""

from __future__ import annotations

from enum import StrEnum


class RuntimeGovernanceErrorCode(StrEnum):
    BINDING_UNAVAILABLE = "binding_unavailable"
    UNKNOWN_ACTION = "unknown_action"
    AUTHORITY_INSUFFICIENT = "authority_insufficient"
    CAPABILITY_INSUFFICIENT = "capability_insufficient"
    BUDGET_EXCEEDED = "budget_exceeded"
    CONFLICT_UNRESOLVED = "conflict_unresolved"
    MODE_UNAVAILABLE = "mode_unavailable"
    INVALID_INPUT = "invalid_input"


class RuntimeGovernanceError(Exception):
    """Storage/transport-independent error whose public representation
    contains no raw prompt, output, or exception text."""

    def __init__(self, *, code: RuntimeGovernanceErrorCode, safe_message: str) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
