"""Strict Judge Output Decoder (Phase 6-D-WU-003): Unknown/Malformed Fail-closed.

Mirrors the guardrail_governance safety-model decode pattern (Phase 5): the
raw model text is untrusted input; any structural or value deviation raises
JudgeDecodeError rather than being coerced to a default recommendation.
"""

import json
import math
from dataclasses import dataclass
from typing import cast

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


def _decode_probability(value: object, *, field_name: str) -> float:
    if isinstance(value, bool):
        raise JudgeDecodeError(reason=f"{field_name} must be a number, got {value!r}")
    if isinstance(value, int | float):
        decoded = float(value)
    elif isinstance(value, str):
        text = value.strip()
        try:
            decoded = float(text)
        except ValueError as exc:
            raise JudgeDecodeError(
                reason=f"{field_name} must be numeric when provided as string, got {value!r}"
            ) from exc
    else:
        raise JudgeDecodeError(reason=f"{field_name} must be a number, got {value!r}")
    if not math.isfinite(decoded) or not (0.0 <= decoded <= 1.0):
        raise JudgeDecodeError(reason=f"{field_name} out of range [0,1]: {value!r}")
    return decoded


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
    objects = _extract_json_objects(raw_text)
    payload = _reconcile_json_objects(objects, expected_criterion_ids=expected_criterion_ids)

    if not isinstance(payload, dict):
        raise JudgeDecodeError(reason="top-level JSON value must be an object")
    allowed_fields = _ALLOWED_FIELDS | ({"criterion_results"} if expected_criterion_ids else set())
    unexpected_fields = set(payload) - allowed_fields
    if unexpected_fields:
        raise JudgeDecodeError(
            reason=f"unexpected fields: {sorted(str(field) for field in unexpected_fields)!r}"
        )

    confidence_raw = payload.get("confidence")
    confidence = _decode_probability(confidence_raw, field_name="confidence")

    reasoning_raw = payload.get("reasoning")
    reasoning = reasoning_raw if isinstance(reasoning_raw, str) and reasoning_raw.strip() else None
    criterion_results = _decode_criterion_results(
        payload.get("criterion_results"), expected_criterion_ids=expected_criterion_ids
    )
    # P9-1 Judge Dispatch Fix Round 6 (Finding 5, Self-review correction):
    # when real structured Criteria were decoded, the final Recommendation
    # is derived mechanically from their Dispositions rather than trusting
    # the Model's own self-reported `recommendation` field -- see
    # `_recommendation_from_criterion_results()`'s own docstring for why.
    # An earlier version of this fix still schema-validated
    # `recommendation_raw` (`not in _VALID_RECOMMENDATIONS`)
    # unconditionally, *before* deciding whether it would even be used --
    # so a Model that omitted the `recommendation` field entirely, or wrote
    # an out-of-vocabulary value, was still rejected as `malformed_output`
    # even when `criterion_results` was itself perfectly decodable and
    # sufficient to derive a Recommendation from, defeating this Finding's
    # own "don't trust the self-report" intent. The schema check now only
    # runs -- and only matters -- in the one branch that actually still
    # uses `recommendation_raw`: the general single-shot Judge shape with
    # no Criteria at all (`expected_criterion_ids=()`).
    recommendation_raw = payload.get("recommendation")
    if criterion_results:
        recommendation = _recommendation_from_criterion_results(criterion_results)
    else:
        if recommendation_raw not in _VALID_RECOMMENDATIONS:
            raise JudgeDecodeError(
                reason=f"unrecognized recommendation value: {recommendation_raw!r}"
            )
        recommendation = EvaluationRecommendation(recommendation_raw)

    return LlmJudgeResponse(
        judge_role=judge_role,
        recommendation=recommendation,
        confidence=confidence,
        reasoning=reasoning,
        criterion_results=criterion_results,
        token_usage=token_usage,
        latency_ms=latency_ms,
        execution_state=EvaluationExecutionState.COMPLETED,
        failure_reason=None,
    )


def _recommendation_from_criterion_results(
    criterion_results: tuple[JudgeCriterionResult, ...],
) -> EvaluationRecommendation:
    """P9-1 Judge Dispatch Fix Round 6 (Finding 5): derive the final
    Recommendation mechanically from the decoded per-criterion Dispositions
    instead of trusting the Model's own self-reported `recommendation` field.
    Mirrors the identical has_deviation/has_uncertain priority already used
    by `runtime_governance.application.semantic_runtime.
    resolve_semantic_action()`'s Enforce branch (Finding 6 reorder) and
    `bootstrap.judge_live_integration._judge_response_from_semantic_
    results()` -- has_deviation takes priority over has_uncertain, so a
    handful of `unknown` Criteria never suppress a Repair recommendation a
    majority of genuine Deviations otherwise supports.

    Before this fix, `decode_judge_output()` instead *validated* the Model's
    self-reported `recommendation` against the decoded Dispositions and
    raised `JudgeDecodeError` on any mismatch (e.g. the Model says `accept`
    but a Criterion is `deviation`, or says `needs_repair` with no
    `deviation` Criterion at all) -- collapsing an internally inconsistent
    but otherwise perfectly decodable response into the same
    `malformed_output` failure category as genuinely broken JSON. A real
    Judge frequently writes a self-contradictory `recommendation` field even
    when every per-criterion Disposition is itself well-formed and useful;
    deriving the Recommendation instead of rejecting on mismatch recovers a
    usable result from that response instead of discarding it."""
    dispositions = {item.disposition for item in criterion_results}
    if JudgeCriterionDisposition.DEVIATION in dispositions:
        return EvaluationRecommendation.NEEDS_REPAIR
    if JudgeCriterionDisposition.UNKNOWN in dispositions:
        return EvaluationRecommendation.UNKNOWN
    return EvaluationRecommendation.ACCEPT


def _extract_json_objects(raw_text: str) -> tuple[object, ...]:
    """Extract every well-formed JSON object in provider-wrapped output, in order.

    Local Qwen/DeepSeek may surround the requested object with a thinking
    prefix, a Markdown fence, or a short explanation -- and some Models
    (Gemma 4 E2B, first observed pre-Round-A during OF-P2-002; DeepSeek,
    newly confirmed during the Round A/3-angle investigation)
    additionally emit *multiple* separate JSON objects in one response (e.g.
    one per Batch Criterion instead of a single combined object), even
    though the Prompt schema requests exactly one. Every well-formed object
    found is returned, in the order it appears, for `_reconcile_json_
    objects()` to judge whether the multiple candidates are a harmless
    duplicate, a reconcilable per-criterion split, or a genuine conflict
    (see that function's own docstring -- P9-1 Judge/Governance Rework,
    WU-02, replacing Round 6's Finding 5, which took the first candidate
    unconditionally and ignored the rest: that silently picked a winner
    among mutually-contradictory decodable objects instead of judging
    whether picking one was ever justified). Zero objects still fail closed.

    Controller Review (2026-09-04 19:16, IR-01) found a second, distinct
    defect a self-review pass had missed: the pre-Controller version of this
    function, on hitting a `{` that failed to `raw_decode` as a complete
    object, treated that exactly like ordinary non-JSON wrapper prose --
    silently advanced one character and kept scanning for the *next* `{`,
    discarding the failed span entirely. Two real shapes exploit this and
    both were reproduced by the Controller's in-memory Probe:
    (1) a well-formed ACCEPT object followed by a truncated, unclosed
    `needs_repair` fragment -- the truncated fragment's `{` failed to
    parse, was silently skipped, and decoding proceeded as if only the
    ACCEPT object had ever been written; (2) an unterminated *outer* wrapper
    object (`{"unfinished": ` + a complete inner object, never closed) --
    the outer `{` failed to parse (its own content never closes), was
    skipped, and the scan re-entered at the *inner* `{`, which parses fine
    entirely on its own and was accepted as if it were the whole answer.
    Both are a judgment fragment whose validity could not be confirmed,
    silently promoted to a clean success -- exactly the "妥当性を確認でき
    ない判定断片を捨てて成功化しない" (never discard an unconfirmable
    judgment fragment to manufacture a success) requirement this module's
    own module docstring already commits to for every other malformed
    shape. A `{` is only ever reached here because it is the start of what
    the Prompt schema calls for -- a JSON object -- never incidental prose
    (the tested wrapper shapes -- Markdown fences, `<think>` prefixes, a
    plain-English lead-in/trailer -- contain no stray `{` of their own); a
    `{` that fails to parse into a complete object is therefore always a
    genuinely broken or truncated judgment attempt, not harmless wrapper
    noise, and must fail the whole decode closed immediately rather than
    being silently discarded and possibly unmasking an unrelated *nested*
    object as if it were the top-level answer.
    """

    decoder = json.JSONDecoder()
    cursor = 0
    objects: list[object] = []
    while cursor < len(raw_text):
        object_start = raw_text.find("{", cursor)
        if object_start < 0:
            break
        try:
            candidate, consumed = decoder.raw_decode(raw_text[object_start:])
        except json.JSONDecodeError as exc:
            # IR-01 fix: no longer `cursor = object_start + 1; continue`.
            # Silently retrying past a `{` that failed to parse is exactly
            # the defect the Controller reproduced -- it either drops a
            # truncated trailing judgment fragment (Case 1) or lets the
            # retry land on and accept an unrelated *nested* object inside
            # an unterminated outer one (Case 2). Every `{` reached here is
            # an attempted JSON object per the Prompt schema; one that does
            # not parse completely is a genuinely malformed/truncated
            # response, not wrapper prose, and must fail closed immediately.
            raise JudgeDecodeError(
                reason=(
                    "found `{` that does not decode as one complete, "
                    "well-formed JSON object -- a truncated or malformed "
                    "judgment fragment, not a harmless wrapper"
                )
            ) from exc
        except RecursionError:
            # P9-1 Judge Dispatch Fix Round 6 Self-review correction
            # (Round 4, Finding 1 from an independent adversarial-input
            # audit): `json.JSONDecoder.raw_decode()`'s recursive descent
            # parser raises `RecursionError`, not `json.JSONDecodeError`,
            # for pathologically deep nesting (e.g. a degraded quantized
            # Model repeating `{` — a realistic failure mode, not a purely
            # theoretical one). Uncaught, this broke `decode_judge_output_
            # fail_closed()`'s own documented "never raises" contract and
            # propagated all the way out of `run_tracked_stage()` to crash
            # the whole Judge/Enforce dispatch. Converts it to the same
            # fail-closed `JudgeDecodeError` (-> `malformed_output`) every
            # other genuinely malformed input already gets here, instead
            # of retrying at `object_start + 1` (which would very likely
            # re-enter the same pathological nesting immediately).
            raise JudgeDecodeError(
                reason="json object nesting exceeds a safe recursion depth"
            ) from None
        objects.append(candidate)
        # `raw_decode()` always consumes at least one character for a
        # successfully-parsed object (`{...}` is never empty), so this
        # always advances -- no risk of looping on the same `object_start`.
        cursor = object_start + consumed
    if not objects:
        raise JudgeDecodeError(reason="no JSON object found in provider output")
    return tuple(objects)


def _reconcile_json_objects(
    objects: tuple[object, ...],
    *,
    expected_criterion_ids: tuple[str, ...],
) -> object:
    """Judge whether multiple well-formed JSON objects may be treated as one
    decodable Judge response, instead of silently preferring one.

    P9-1 Judge/Governance Rework (WU-02): Round 6's Finding 5 took the
    *first* successfully-parsed object among several and discarded the
    rest unconditionally -- so a Model response containing one object
    recommending `accept` immediately followed by a second recommending
    `needs_repair` decoded as a clean ACCEPT, silently picking a winner
    between two mutually-contradictory Judge verdicts. Conforming to the
    "take the first object" test the Round 6 fix itself wrote never
    proved that choice was the *correct* one to trust.

    A single object is always returned unchanged (the ordinary case).
    Among multiple objects:
      - If every object is byte-for-byte identical, the duplication is
        harmless (the same verdict repeated, e.g. by a wrapper or a Model
        that echoes its own answer) -- the first is used.
      - Otherwise, if every object carries a `criterion_results` field
        (`expected_criterion_ids` non-empty, i.e. a real per-criterion
        Judge dispatch), the objects are treated as a legitimate per-batch
        split -- a real observed failure shape where a degraded quantized
        Model emits one complete object per Criterion (or per Batch) instead
        of one combined object -- and their `criterion_results` arrays are
        concatenated in order, replacing the first object's own array. Any
        other top-level field (`recommendation`/`confidence`/`reasoning`)
        is taken from the *first* object only -- harmless, since a non-empty
        merged `criterion_results` always makes `decode_judge_output()`
        derive the Recommendation mechanically instead of trusting any
        object's self-reported one anyway (see `_recommendation_from_
        criterion_results()`). This does *not* by itself guarantee success:
        the concatenated list still passes through `_decode_criterion_
        results()` unchanged, which independently rejects a duplicate
        `criterion_id` (a genuine same-criterion conflict, e.g. one
        fragment says `pass` and another says `deviation` for the same id)
        and a still-incomplete set (missing criterion ids) -- exactly the
        same fail-closed checks a single well-formed object already had to
        pass. This function only decides whether concatenation is
        *reconcilable* to attempt at all; it never resolves a conflict on
        the caller's behalf.
      - Any other case (some object carries no `criterion_results` field at
        all, or there are no criteria to reconcile against in the first
        place) is a genuine ambiguity between distinct, not-obviously-
        equivalent candidates -- raises `JudgeDecodeError` rather than
        guessing which one to trust.
    """

    if len(objects) == 1:
        return objects[0]
    first = objects[0]
    if not all(item == first for item in objects[1:]):
        if (
            expected_criterion_ids
            and isinstance(first, dict)
            and all(isinstance(item, dict) and "criterion_results" in item for item in objects)
        ):
            merged: list[object] = []
            for item in objects:
                fragment = cast(dict[str, object], item)["criterion_results"]
                if not isinstance(fragment, list):
                    raise JudgeDecodeError(
                        reason="criterion_results must be an array in every JSON object"
                    )
                merged.extend(fragment)
            merged_payload = dict(cast(dict[str, object], first))
            merged_payload["criterion_results"] = merged
            return merged_payload
        raise JudgeDecodeError(
            reason=(
                f"multiple conflicting JSON objects found: {len(objects)} distinct, "
                "not-reconcilable candidates"
            )
        )
    return first


def _decode_criterion_results(
    value: object, *, expected_criterion_ids: tuple[str, ...]
) -> tuple[JudgeCriterionResult, ...]:
    if not expected_criterion_ids:
        return ()
    # P9-1 Judge Dispatch Fix Round 6 Self-review correction (Round 4,
    # Finding 3 from an independent adversarial-input audit): the
    # membership check below used to test against `expected_criterion_ids`
    # (a tuple) directly, an O(n) scan per Criterion for O(n^2) overall on
    # an Adversarial (or simply very large) `criterion_results` batch. This
    # `set` was already being built one line below purely to check
    # uniqueness and then discarded; reusing it for the membership check
    # too makes both O(1) per Criterion.
    expected_criterion_id_set = set(expected_criterion_ids)
    if len(expected_criterion_id_set) != len(expected_criterion_ids):
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
        if not isinstance(criterion_id, str) or criterion_id not in expected_criterion_id_set:
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
        confidence = _decode_probability(item.get("confidence"), field_name="criterion confidence")
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
            confidence=confidence,
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
