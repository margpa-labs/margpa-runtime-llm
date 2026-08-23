"""Strict Judge Output Decoder (Phase 6-D-WU-003): Unknown/Malformed Fail-closed.

Mirrors the guardrail_governance safety-model decode pattern (Phase 5): the
raw model text is untrusted input; any structural or value deviation raises
JudgeDecodeError rather than being coerced to a default recommendation.
"""

import json
from dataclasses import dataclass

from ..domain.identifiers import EvaluationExecutionState, EvaluationRecommendation
from ..domain.llm_judge import JudgeFailureReason, JudgeIndependenceClass, LlmJudgeResponse

_VALID_RECOMMENDATIONS = {member.value for member in EvaluationRecommendation}


@dataclass(frozen=True, slots=True)
class JudgeDecodeError(Exception):
    reason: str

    def __str__(self) -> str:
        return f"judge output decode failed: {self.reason}"


def decode_judge_output(
    *,
    raw_text: str,
    judge_role: JudgeIndependenceClass,
    token_usage: int,
    latency_ms: int,
) -> LlmJudgeResponse:
    """Raises JudgeDecodeError on any malformed/unknown output; never guesses."""
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise JudgeDecodeError(reason=f"not valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise JudgeDecodeError(reason="top-level JSON value must be an object")

    recommendation_raw = payload.get("recommendation")
    if recommendation_raw not in _VALID_RECOMMENDATIONS:
        raise JudgeDecodeError(reason=f"unrecognized recommendation value: {recommendation_raw!r}")

    confidence_raw = payload.get("confidence")
    if not isinstance(confidence_raw, int | float) or isinstance(confidence_raw, bool):
        raise JudgeDecodeError(reason=f"confidence must be a number, got {confidence_raw!r}")
    if not (0.0 <= float(confidence_raw) <= 1.0):
        raise JudgeDecodeError(reason=f"confidence out of range [0,1]: {confidence_raw!r}")

    reasoning_raw = payload.get("reasoning")
    reasoning = reasoning_raw if isinstance(reasoning_raw, str) and reasoning_raw.strip() else None

    return LlmJudgeResponse(
        judge_role=judge_role,
        recommendation=EvaluationRecommendation(recommendation_raw),
        confidence=float(confidence_raw),
        reasoning=reasoning,
        token_usage=token_usage,
        latency_ms=latency_ms,
        execution_state=EvaluationExecutionState.COMPLETED,
        failure_reason=None,
    )


def decode_judge_output_fail_closed(
    *,
    raw_text: str,
    judge_role: JudgeIndependenceClass,
    token_usage: int,
    latency_ms: int,
) -> LlmJudgeResponse:
    """Never raises: converts a JudgeDecodeError into a typed FAILED response.

    Use this at the seam that calls an untrusted provider so a malformed
    return degrades to a Typed Failure Result instead of an escaping
    exception (same shape as Phase 5's SafetyModelDetectorAdapter.detect()).
    """
    try:
        return decode_judge_output(
            raw_text=raw_text,
            judge_role=judge_role,
            token_usage=token_usage,
            latency_ms=latency_ms,
        )
    except JudgeDecodeError:
        return LlmJudgeResponse(
            judge_role=judge_role,
            recommendation=EvaluationRecommendation.UNKNOWN,
            confidence=0.0,
            token_usage=token_usage,
            latency_ms=latency_ms,
            execution_state=EvaluationExecutionState.FAILED,
            failure_reason=JudgeFailureReason.MALFORMED_OUTPUT,
        )
