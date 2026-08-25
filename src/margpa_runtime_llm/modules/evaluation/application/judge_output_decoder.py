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
_ALLOWED_FIELDS = {"recommendation", "confidence", "reasoning"}


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
    payload = _extract_single_json_object(raw_text)

    if not isinstance(payload, dict):
        raise JudgeDecodeError(reason="top-level JSON value must be an object")
    unexpected_fields = set(payload) - _ALLOWED_FIELDS
    if unexpected_fields:
        raise JudgeDecodeError(
            reason=f"unexpected fields: {sorted(str(field) for field in unexpected_fields)!r}"
        )

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


def _extract_single_json_object(raw_text: str) -> object:
    """Extract one provider-wrapped JSON object without guessing semantics.

    Local Qwen/DeepSeek may surround the requested object with a thinking
    prefix, a Markdown fence, or a short explanation. We accept those wrappers
    only because they do not alter the object. Zero objects, two objects, an
    incomplete object, or a schema/value mismatch still fail closed.
    """

    decoder = json.JSONDecoder()
    candidates: list[object] = []
    cursor = 0
    while cursor < len(raw_text):
        object_start = raw_text.find("{", cursor)
        if object_start < 0:
            break
        try:
            candidate, consumed = decoder.raw_decode(raw_text[object_start:])
        except json.JSONDecodeError:
            cursor = object_start + 1
            continue
        candidates.append(candidate)
        cursor = object_start + consumed
    if len(candidates) != 1:
        raise JudgeDecodeError(reason=f"expected exactly one JSON object, found {len(candidates)}")
    return candidates[0]


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
