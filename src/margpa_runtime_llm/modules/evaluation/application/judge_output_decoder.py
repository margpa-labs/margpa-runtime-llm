"""Strict Judge Output Decoder (Phase 6-D-WU-003): Unknown/Malformed Fail-closed.

Mirrors the guardrail_governance safety-model decode pattern (Phase 5): the
raw model text is untrusted input; any structural or value deviation raises
JudgeDecodeError rather than being coerced to a default recommendation.
"""

import json
from dataclasses import dataclass

from ..domain.identifiers import EvaluationExecutionState, EvaluationRecommendation
from ..domain.llm_judge import (
    JudgeCriterionDisposition,
    JudgeCriterionResult,
    JudgeFailureReason,
    JudgeIndependenceClass,
    LlmJudgeResponse,
)

_VALID_RECOMMENDATIONS = {member.value for member in EvaluationRecommendation}
_ALLOWED_FIELDS = {"recommendation", "confidence", "reasoning"}
_CRITERION_ALLOWED_FIELDS = {
    "criterion_id",
    "disposition",
    "confidence",
    "reason_code",
    "evidence_refs",
}


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
    expected_criterion_ids: tuple[str, ...] = (),
) -> LlmJudgeResponse:
    """Raises JudgeDecodeError on any malformed/unknown output; never guesses."""
    payload = _extract_single_json_object(raw_text)

    if not isinstance(payload, dict):
        raise JudgeDecodeError(reason="top-level JSON value must be an object")
    allowed_fields = _ALLOWED_FIELDS | ({"criterion_results"} if expected_criterion_ids else set())
    unexpected_fields = set(payload) - allowed_fields
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
    criterion_results = _decode_criterion_results(
        payload.get("criterion_results"), expected_criterion_ids=expected_criterion_ids
    )
    dispositions = {item.disposition for item in criterion_results}
    if recommendation_raw == EvaluationRecommendation.ACCEPT.value and (
        JudgeCriterionDisposition.DEVIATION in dispositions
        or JudgeCriterionDisposition.UNKNOWN in dispositions
    ):
        raise JudgeDecodeError(reason="recommendation contradicts criterion results")
    if (
        recommendation_raw == EvaluationRecommendation.NEEDS_REPAIR.value
        and criterion_results
        and JudgeCriterionDisposition.DEVIATION not in dispositions
    ):
        raise JudgeDecodeError(reason="repair recommendation has no deviated criterion")

    return LlmJudgeResponse(
        judge_role=judge_role,
        recommendation=EvaluationRecommendation(recommendation_raw),
        confidence=float(confidence_raw),
        reasoning=reasoning,
        criterion_results=criterion_results,
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


def _decode_criterion_results(
    value: object, *, expected_criterion_ids: tuple[str, ...]
) -> tuple[JudgeCriterionResult, ...]:
    if not expected_criterion_ids:
        return ()
    if len(set(expected_criterion_ids)) != len(expected_criterion_ids):
        raise JudgeDecodeError(reason="expected criterion ids are not unique")
    if not isinstance(value, list):
        raise JudgeDecodeError(reason="criterion_results must be an array")
    decoded: dict[str, JudgeCriterionResult] = {}
    for item in value:
        if not isinstance(item, dict):
            raise JudgeDecodeError(reason="criterion result must be an object")
        unexpected = set(item) - _CRITERION_ALLOWED_FIELDS
        if unexpected:
            raise JudgeDecodeError(reason=f"unexpected criterion fields: {sorted(unexpected)!r}")
        criterion_id = item.get("criterion_id")
        if not isinstance(criterion_id, str) or criterion_id not in expected_criterion_ids:
            raise JudgeDecodeError(reason=f"unexpected criterion id: {criterion_id!r}")
        if criterion_id in decoded:
            raise JudgeDecodeError(reason=f"duplicate criterion id: {criterion_id!r}")
        disposition = item.get("disposition")
        if not isinstance(disposition, str):
            raise JudgeDecodeError(reason="criterion disposition must be a string")
        try:
            typed_disposition = JudgeCriterionDisposition(disposition)
        except (TypeError, ValueError):
            raise JudgeDecodeError(
                reason=f"invalid criterion disposition: {disposition!r}"
            ) from None
        confidence = item.get("confidence")
        if not isinstance(confidence, int | float) or isinstance(confidence, bool):
            raise JudgeDecodeError(reason="criterion confidence must be a number")
        if not 0.0 <= float(confidence) <= 1.0:
            raise JudgeDecodeError(reason="criterion confidence is outside [0,1]")
        reason_code = item.get("reason_code")
        if reason_code is not None and not isinstance(reason_code, str):
            raise JudgeDecodeError(reason="criterion reason_code must be a string or null")
        evidence_refs = item.get("evidence_refs", [])
        if not isinstance(evidence_refs, list) or not all(
            isinstance(reference, str) for reference in evidence_refs
        ):
            raise JudgeDecodeError(reason="criterion evidence_refs must be a string array")
        decoded[criterion_id] = JudgeCriterionResult(
            criterion_id=criterion_id,
            disposition=typed_disposition,
            confidence=float(confidence),
            reason_code=reason_code,
            evidence_refs=tuple(evidence_refs),
        )
    missing = set(expected_criterion_ids) - set(decoded)
    if missing:
        raise JudgeDecodeError(reason=f"missing criterion ids: {sorted(missing)!r}")
    return tuple(decoded[criterion_id] for criterion_id in expected_criterion_ids)


def decode_judge_output_fail_closed(
    *,
    raw_text: str,
    judge_role: JudgeIndependenceClass,
    token_usage: int,
    latency_ms: int,
    expected_criterion_ids: tuple[str, ...] = (),
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
            expected_criterion_ids=expected_criterion_ids,
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
