"""Enums for the Repair Domain (Architecture 7.1/7.2)."""

from enum import StrEnum


class RepairStrategyId(StrEnum):
    """Names only; executable Strategy availability is Adapter Registry/Authority-owned."""

    REGENERATE_WITH_STRUCTURED_FEEDBACK = "regenerate_with_structured_feedback"
    ABSTAIN_WHEN_REFERENCE_INSUFFICIENT = "abstain_when_reference_insufficient"
    REQUEST_CLARIFICATION = "request_clarification"
    FORMAT_ONLY_REPAIR = "format_only_repair"


class RepairState(StrEnum):
    PLANNED = "planned"
    AUTHORIZED = "authorized"
    GENERATING_REPAIR = "generating_repair"
    REJUDGING = "rejudging"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXHAUSTED = "exhausted"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RepairMode(StrEnum):
    """Independent from Evaluation/Judge Mode (Acceptance P6-ACC-025), Default OFF."""

    OFF = "off"
    OBSERVE = "observe"
    ENFORCE = "enforce"


class RepairOutcome(StrEnum):
    IMPROVED = "improved"
    NO_CHANGE = "no_change"
    WORSE = "worse"
    UNKNOWN = "unknown"
