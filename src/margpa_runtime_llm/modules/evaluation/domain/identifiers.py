"""Enums for the Evaluation Domain (Architecture 6.1/6.3)."""

from enum import StrEnum


class EvaluationMode(StrEnum):
    OFF = "off"
    OBSERVE = "observe"
    ENFORCE = "enforce"


class EvaluatorClass(StrEnum):
    DETERMINISTIC = "deterministic"
    LLM_JUDGE = "llm_judge"


class EvaluationExecutionState(StrEnum):
    NOT_INVOKED = "not_invoked"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationRecommendation(StrEnum):
    ACCEPT = "accept"
    NEEDS_REPAIR = "needs_repair"
    UNKNOWN = "unknown"
