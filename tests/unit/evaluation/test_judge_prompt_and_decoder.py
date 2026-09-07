import json
import time

import pytest

from margpa_runtime_llm.modules.evaluation.application.judge_output_decoder import (
    JudgeDecodeError,
    decode_judge_output,
    decode_judge_output_fail_closed,
)
from margpa_runtime_llm.modules.evaluation.application.judge_prompt_builder import (
    build_judge_prompt,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import (
    JudgeFailureReason,
    JudgeIndependenceClass,
)

from .conftest import make_case


def test_prompt_is_deterministic_for_identical_inputs() -> None:
    case = make_case()
    first = build_judge_prompt(case=case, candidate_answer="Paris", rubric_id="r1")
    second = build_judge_prompt(case=case, candidate_answer="Paris", rubric_id="r1")
    assert first == second


def test_prompt_marks_unknown_reference_explicitly_rather_than_omitting_it() -> None:
    case = make_case().model_copy(update={"reference": None})
    prompt = build_judge_prompt(case=case, candidate_answer="anything", rubric_id="r1")
    assert "(none provided)" in prompt
    assert "absence of a separate reference answer" in prompt


def test_prompt_carries_user_correction_and_citation_evidence_as_distinct_sections() -> None:
    case = make_case().model_copy(
        update={"input": "No, the reading is Amane Kanata.", "reference": None}
    )
    prompt = build_judge_prompt(
        case=case,
        candidate_answer="The official reading is Tenon.",
        rubric_id="r1",
        dialogue_context=("assistant: The reading is Tenon.",),
        evidence_context=("ref-1 | official.md: Amane Kanata",),
    )
    assert "Prior dialogue" in prompt
    assert "assistant: The reading is Tenon." in prompt
    assert "Citation evidence" in prompt
    assert "ref-1 | official.md: Amane Kanata" in prompt
    assert "contradiction" in prompt


def test_prompt_instructs_a_strict_json_response_schema() -> None:
    prompt = build_judge_prompt(case=make_case(), candidate_answer="Paris", rubric_id="r1")
    assert "recommendation" in prompt
    assert "confidence" in prompt


def test_decode_accepts_a_well_formed_response() -> None:
    raw = json.dumps({"recommendation": "accept", "confidence": 0.9, "reasoning": "matches"})
    response = decode_judge_output(
        raw_text=raw,
        judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
        token_usage=42,
        latency_ms=100,
    )
    assert response.recommendation is EvaluationRecommendation.ACCEPT
    assert response.confidence == 0.9
    assert response.execution_state is EvaluationExecutionState.COMPLETED
    assert response.reasoning == "matches"


def test_decode_accepts_numeric_string_confidence_values() -> None:
    raw = json.dumps(
        {
            "recommendation": "needs_repair",
            "confidence": "0.1",
            "reasoning": "fixture",
            "criterion_results": [
                {
                    "criterion_id": "c1",
                    "disposition": "deviation",
                    "confidence": "0.9",
                    "reason_code": "x",
                    "evidence_refs": [],
                }
            ],
        }
    )
    response = decode_judge_output(
        raw_text=raw,
        judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
        token_usage=1,
        latency_ms=1,
        expected_criterion_ids=("c1",),
    )
    assert response.confidence == 0.1
    assert response.criterion_results[0].confidence == 0.9


def test_decode_criterion_reason_code_and_evidence_refs_are_optional_fields() -> None:
    """R4-WU-04 (Controller Review IR-R3-04): pins the shared Decoder's
    existing contract BEFORE relying on it -- `reason_code`/`evidence_refs`
    are genuinely OPTIONAL per-criterion fields (`_decode_criterion_
    results()` reads them via `.get("reason_code")` / `.get("evidence_
    refs", [])`, never a required-key check), defaulting to `None`/`()`
    when the Model's own JSON omits the keys entirely -- never a Decode
    failure. This is the exact substrate fact that makes a Provider-local
    Compact Criterion Schema (only `criterion_id`/`disposition`/
    `confidence`, see `GemmaPromptAdapter`) safe to introduce WITHOUT any
    change to this shared Decoder, Selene's own Prompt Schema, or the
    Main-shared Prompt."""
    raw = json.dumps(
        {
            "recommendation": "needs_repair",
            "confidence": 0.4,
            "criterion_results": [
                {"criterion_id": "c1", "disposition": "deviation", "confidence": 0.8},
            ],
        }
    )
    response = decode_judge_output(
        raw_text=raw,
        judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
        token_usage=1,
        latency_ms=1,
        expected_criterion_ids=("c1",),
    )
    assert response.execution_state is EvaluationExecutionState.COMPLETED
    assert response.criterion_results[0].reason_code is None
    assert response.criterion_results[0].evidence_refs == ()


@pytest.mark.parametrize(
    "raw_text",
    [
        '```json\n{"recommendation":"accept","confidence":0.9}\n```',
        '<think>check the evidence</think>\n{"recommendation":"needs_repair","confidence":0.8}',
        'Evaluation result: {"recommendation":"unknown","confidence":0.2} End.',
    ],
)
def test_decode_accepts_one_strict_object_inside_known_provider_wrappers(raw_text: str) -> None:
    response = decode_judge_output(
        raw_text=raw_text,
        judge_role=JudgeIndependenceClass.MAIN_SELF,
        token_usage=1,
        latency_ms=1,
    )
    assert response.execution_state is EvaluationExecutionState.COMPLETED


def test_decode_pathologically_deep_json_nesting_fails_closed_not_recursion_error() -> None:
    """P9-1 Judge Dispatch Fix Round 6 Self-review correction (Round 4,
    Finding 1 from an independent adversarial-input audit):
    `json.JSONDecoder.raw_decode()`'s recursive-descent parser raises
    `RecursionError`, not `json.JSONDecodeError`, for pathologically deep
    nesting -- a degraded quantized Model repeating `{` is a realistic
    failure mode, not a purely theoretical one. Uncaught, this broke
    `decode_judge_output_fail_closed()`'s own documented "never raises"
    contract and would propagate all the way out of `run_tracked_stage()`
    to crash the whole Judge/Enforce dispatch. Must now fail closed as an
    ordinary `malformed_output`-classified `JudgeDecodeError`, exactly like
    any other genuinely broken JSON.

    Further Self-review correction (Round 6, two independent Findings):
    (1) A Test Coverage audit found the original fixture (`"{" * 5000`)
    never actually triggered `RecursionError` at all -- it silently
    exercised the ordinary `JSONDecodeError` retry path instead, so this
    Test passed even with the `except RecursionError` branch deleted
    entirely, detecting nothing. (2) Simply repeating `{` turned out to be
    the reason why: `"{{{{..."` is not valid nested JSON at any depth --
    the decoder rejects it as a syntax error (`Expecting property name...`)
    after the *second* character, before recursion ever has a chance to
    build up, regardless of how many more `{` follow. A pathologically deep
    nesting fixture needs to be genuinely well-formed at every level (each
    `{"a":` opens a real nested object the decoder must actually recurse
    into to keep parsing) -- `'{"a":' * N + '1' + '}' * N` is exactly that
    shape. The precondition itself (this fixture really does raise
    `RecursionError` from the raw decoder) is asserted first, so a future
    environment/Python version where it stops doing so fails this Test
    loudly here, instead of silently no-op-testing the target code path
    again."""
    pathologically_nested = '{"a":' * 20000 + "1" + "}" * 20000
    with pytest.raises(RecursionError):
        json.JSONDecoder().raw_decode(pathologically_nested)
    with pytest.raises(JudgeDecodeError):
        decode_judge_output(
            raw_text=pathologically_nested,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=1,
            latency_ms=1,
        )
    response = decode_judge_output_fail_closed(
        raw_text=pathologically_nested,
        judge_role=JudgeIndependenceClass.MAIN_SELF,
        token_usage=1,
        latency_ms=1,
    )
    assert response.execution_state is EvaluationExecutionState.FAILED
    assert response.failure_reason is JudgeFailureReason.MALFORMED_OUTPUT


def test_decode_large_criterion_batch_stays_fast_and_correct() -> None:
    """P9-1 Judge Dispatch Fix Round 6 Self-review correction (Round 4,
    Finding 3 from an independent adversarial-input audit):
    `_decode_criterion_results()`'s membership check used to test against
    `expected_criterion_ids` (a tuple) directly -- an O(n) scan per
    Criterion, O(n^2) overall. Confirms both that decoding a large batch
    (well beyond this codebase's real ~32-Criteria-per-Turn shape) still
    completes quickly and that every entry decodes correctly, not merely
    that it doesn't time out.

    Self-review correction (Round 6, Finding from an independent Test
    Coverage audit): the original version of this Test asserted only
    correctness, with no timing check at all -- so it could not actually
    catch a regression back to O(n^2) (2000 entries alone does not run
    long enough for that to matter either way). Now measures wall time
    against a generous bound and uses a large enough batch (20000) that
    the O(n^2) shape this Fix replaced would measurably and reliably blow
    past it (real-hardware measurement of the pre-fix code: ~0.7s at
    16000 entries), while a correct O(n) implementation finishes in a
    small fraction of the 2-second bound on any reasonable machine."""
    criterion_ids = tuple(f"c{i}" for i in range(20000))
    raw = json.dumps(
        {
            "recommendation": "accept",
            "confidence": 0.9,
            "criterion_results": [
                {"criterion_id": criterion_id, "disposition": "pass", "confidence": 0.9}
                for criterion_id in criterion_ids
            ],
        }
    )
    started = time.monotonic()
    response = decode_judge_output(
        raw_text=raw,
        judge_role=JudgeIndependenceClass.MAIN_SELF,
        token_usage=1,
        latency_ms=1,
        expected_criterion_ids=criterion_ids,
    )
    elapsed = time.monotonic() - started
    assert elapsed < 2.0, (
        f"decode_judge_output took {elapsed:.2f}s for 20000 criteria "
        "(possible O(n^2) regression in _decode_criterion_results)"
    )
    assert len(response.criterion_results) == 20000
    assert {item.criterion_id for item in response.criterion_results} == set(criterion_ids)


def test_decode_rejects_unrecognized_schema_extensions() -> None:
    with pytest.raises(JudgeDecodeError):
        decode_judge_output(
            raw_text='{"recommendation":"accept","confidence":0.9,"verdict":"pass"}',
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=1,
            latency_ms=1,
        )


def test_decode_rejects_conflicting_json_objects_with_no_criteria_to_reconcile() -> None:
    """P9-1 Judge/Governance Rework (WU-02), replacing Round 6's Finding 5:
    Round 6's `_extract_first_json_object()` took the first well-formed
    object among several and silently discarded the rest -- so a response
    containing one object recommending `accept` immediately followed by one
    recommending `needs_repair` decoded as a clean ACCEPT. That conformed to
    a self-written test, but never proved picking the first object was the
    *correct* choice between two mutually-contradictory Judge verdicts.
    With no `criterion_results` to reconcile against (`expected_criterion_
    ids=()`, the general single-shot Judge shape), two distinct,
    non-identical top-level objects are a genuine ambiguity -- this must
    now fail closed as `malformed_output` rather than silently pick a
    winner. Replaces `test_decode_multiple_json_objects_uses_the_first_
    well_formed_one`, which asserted the old (pre-Rework) silent-pick
    behavior on this exact input."""
    with pytest.raises(JudgeDecodeError):
        decode_judge_output(
            raw_text=(
                '{"recommendation":"accept","confidence":0.9} '
                '{"recommendation":"needs_repair","confidence":0.9}'
            ),
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=1,
            latency_ms=1,
        )


def test_decode_accepts_a_harmless_byte_for_byte_duplicate_object() -> None:
    """A Model (or a wrapper) that echoes the identical object twice is a
    harmless duplicate, not an ambiguity -- decoding must still succeed,
    using the single shared verdict."""
    raw_object = '{"recommendation":"accept","confidence":0.9,"reasoning":"fixture"}'
    response = decode_judge_output(
        raw_text=f"{raw_object} {raw_object}",
        judge_role=JudgeIndependenceClass.MAIN_SELF,
        token_usage=1,
        latency_ms=1,
    )
    assert response.recommendation is EvaluationRecommendation.ACCEPT
    assert response.confidence == 0.9


def test_decode_rejects_a_well_formed_object_followed_by_a_truncated_fragment() -> None:
    """Controller Review (2026-09-04 19:16, IR-01) Probe Case 1: a
    well-formed `accept` object followed by a newline and an unclosed
    `needs_repair` fragment (no closing brace) decoded as a clean ACCEPT
    under the pre-Controller version of `_extract_json_objects()`, which
    silently discarded the truncated fragment's `{` on parse failure and
    proceeded as if only the first object had ever been written. The
    truncated fragment is a judgment attempt whose validity cannot be
    confirmed -- it must fail the whole decode closed, never be dropped in
    favor of the earlier well-formed object."""
    raw_text = (
        '{"recommendation":"accept","confidence":0.9,'
        '"criterion_results":[{"criterion_id":"c1","disposition":"pass","confidence":0.9}]}\n'
        '{"recommendation":"needs_repair","confidence":0.9'
    )
    with pytest.raises(JudgeDecodeError):
        decode_judge_output(
            raw_text=raw_text,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=1,
            latency_ms=1,
            expected_criterion_ids=("c1",),
        )


def test_decode_rejects_an_unterminated_outer_object_wrapping_a_valid_inner_one() -> None:
    """Controller Review (2026-09-04 19:16, IR-01) Probe Case 2: an
    unterminated outer object (`{"unfinished": ` followed by a complete,
    well-formed inner object, with the outer object itself never closed)
    decoded as a clean ACCEPT under the pre-Controller version of
    `_extract_json_objects()` -- the outer `{` failed to parse (its own
    content never closes), was silently skipped, and the scan re-entered at
    the inner `{`, accepting it as if it were the whole top-level answer.
    The outer object is a genuinely broken/truncated top-level judgment
    attempt; the well-formed object nested inside it must never be unmasked
    and substituted for it."""
    inner = (
        '{"recommendation":"accept","confidence":0.9,'
        '"criterion_results":[{"criterion_id":"c1","disposition":"pass","confidence":0.9}]}'
    )
    raw_text = f'{{"unfinished": {inner}'
    with pytest.raises(JudgeDecodeError):
        decode_judge_output(
            raw_text=raw_text,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=1,
            latency_ms=1,
            expected_criterion_ids=("c1",),
        )


def test_decode_reconciles_a_genuine_per_criterion_object_split() -> None:
    """P9-1 Judge/Governance Rework (WU-02): real-hardware evidence
    (Gemma 4 E2B, DeepSeek) shows a degraded quantized Model emitting one
    complete object (its own `recommendation`/`confidence`/
    `criterion_results`) per Batch Criterion instead of one combined
    object, even though the Prompt schema requests exactly one. When every
    object carries a `criterion_results` field and their concatenated ids
    exactly cover `expected_criterion_ids` with no duplicate/conflicting
    id, this is a legitimate per-batch split -- concatenating recovers a
    fully usable, unambiguous result (mirrors the real Batch shape: one
    Selene/Main-shared dispatch Batch is up to 8 Criteria, split here
    across 2 fragments of 1 each for a minimal, readable fixture)."""
    raw_text = (
        '{"recommendation":"accept","confidence":0.9,'
        '"criterion_results":[{"criterion_id":"c1","disposition":"pass","confidence":0.9}]} '
        '{"recommendation":"needs_repair","confidence":0.8,'
        '"criterion_results":[{"criterion_id":"c2","disposition":"deviation","confidence":0.8}]}'
    )
    response = decode_judge_output(
        raw_text=raw_text,
        judge_role=JudgeIndependenceClass.MAIN_SELF,
        token_usage=1,
        latency_ms=1,
        expected_criterion_ids=("c1", "c2"),
    )
    assert {item.criterion_id: item.disposition.value for item in response.criterion_results} == {
        "c1": "pass",
        "c2": "deviation",
    }
    # Mirrors the already-fixed Round 6 Finding 5 behavior this Rework
    # keeps unchanged: the Recommendation is derived mechanically from the
    # reconciled Dispositions, never trusting either fragment's own
    # self-reported (and here, mutually differing) `recommendation` field.
    assert response.recommendation is EvaluationRecommendation.NEEDS_REPAIR


def test_decode_rejects_a_per_criterion_split_with_a_conflicting_duplicate_id() -> None:
    """The exact 'first PASS, later DEVIATION' shape for the *same*
    Criterion id -- a genuine same-criterion conflict between fragments,
    not a harmless duplicate. Concatenation is attempted (both fragments
    carry a `criterion_results` field), but the merged list still passes
    through the existing, unchanged `_decode_criterion_results()`
    duplicate-id check, which fails closed exactly as it already does for
    a single malformed object."""
    raw_text = (
        '{"confidence":0.9,'
        '"criterion_results":[{"criterion_id":"c1","disposition":"pass","confidence":0.9}]} '
        '{"confidence":0.8,'
        '"criterion_results":[{"criterion_id":"c1","disposition":"deviation","confidence":0.8}]}'
    )
    with pytest.raises(JudgeDecodeError, match="duplicate criterion id"):
        decode_judge_output(
            raw_text=raw_text,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=1,
            latency_ms=1,
            expected_criterion_ids=("c1",),
        )


def test_decode_rejects_a_per_criterion_split_in_reversed_order_too() -> None:
    """The reversed-order mirror of the conflicting-duplicate-id case above
    -- confirms the conflict is detected regardless of which Disposition
    (DEVIATION or PASS) happens to appear first, i.e. there is no
    first-object bias hiding in the reconciliation itself."""
    raw_text = (
        '{"confidence":0.8,'
        '"criterion_results":[{"criterion_id":"c1","disposition":"deviation","confidence":0.8}]} '
        '{"confidence":0.9,'
        '"criterion_results":[{"criterion_id":"c1","disposition":"pass","confidence":0.9}]}'
    )
    with pytest.raises(JudgeDecodeError, match="duplicate criterion id"):
        decode_judge_output(
            raw_text=raw_text,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=1,
            latency_ms=1,
            expected_criterion_ids=("c1",),
        )


def test_decode_rejects_a_per_criterion_split_still_missing_an_expected_id() -> None:
    """Concatenating the fragments' `criterion_results` does not by itself
    guarantee success -- two non-conflicting fragments (`c1`, `c2`, no
    overlap) still leave `c3` uncovered when three ids are expected, so
    the existing missing-id check (unchanged) still fails closed, exactly
    as it already does for a single, incomplete object."""
    raw_text = (
        '{"confidence":0.9,'
        '"criterion_results":[{"criterion_id":"c1","disposition":"pass","confidence":0.9}]} '
        '{"confidence":0.9,'
        '"criterion_results":[{"criterion_id":"c2","disposition":"pass","confidence":0.9}]}'
    )
    with pytest.raises(JudgeDecodeError, match="missing criterion ids"):
        decode_judge_output(
            raw_text=raw_text,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=1,
            latency_ms=1,
            expected_criterion_ids=("c1", "c2", "c3"),
        )


def test_decode_omitted_recommendation_still_derives_from_criterion_results() -> None:
    """P9-1 Judge Dispatch Fix Round 6 (Finding 5, Self-review correction):
    the `recommendation` field's schema check (`not in
    _VALID_RECOMMENDATIONS`) used to run unconditionally before deciding
    whether it would even be used, so a Model that omitted `recommendation`
    entirely (or wrote an out-of-vocabulary value) was still rejected as
    `malformed_output` even when `criterion_results` was itself perfectly
    decodable -- defeating this Finding's own "derive from criterion_results,
    don't trust the self-report" intent. `recommendation` is entirely absent
    here; decoding must still succeed and derive ACCEPT from the two `pass`
    Dispositions."""
    raw = json.dumps(
        {
            "confidence": 0.95,
            "reasoning": "both pass",
            "criterion_results": [
                {"criterion_id": "c1", "disposition": "pass", "confidence": 0.95},
                {"criterion_id": "c2", "disposition": "pass", "confidence": 0.9},
            ],
        }
    )
    response = decode_judge_output(
        raw_text=raw,
        judge_role=JudgeIndependenceClass.MAIN_SELF,
        token_usage=1,
        latency_ms=1,
        expected_criterion_ids=("c1", "c2"),
    )
    assert response.recommendation is EvaluationRecommendation.ACCEPT


def test_decode_reasoning_is_none_when_absent() -> None:
    raw = json.dumps({"recommendation": "accept", "confidence": 0.9})
    response = decode_judge_output(
        raw_text=raw,
        judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
        token_usage=0,
        latency_ms=0,
    )
    assert response.reasoning is None


@pytest.mark.parametrize("reasoning_raw", ["", "   ", 42, None, ["not", "a", "string"]])
def test_decode_reasoning_falls_back_to_none_on_blank_or_non_string(
    reasoning_raw: object,
) -> None:
    raw = json.dumps({"recommendation": "accept", "confidence": 0.9, "reasoning": reasoning_raw})
    response = decode_judge_output(
        raw_text=raw,
        judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
        token_usage=0,
        latency_ms=0,
    )
    assert response.reasoning is None


@pytest.mark.parametrize(
    "raw_text",
    [
        "not json at all",
        json.dumps(["accept", 0.9]),
        json.dumps({"recommendation": "definitely_probably_yes", "confidence": 0.9}),
        json.dumps({"recommendation": "accept", "confidence": "high"}),
        json.dumps({"recommendation": "accept", "confidence": "1e999"}),
        json.dumps({"recommendation": "accept", "confidence": 1.5}),
        json.dumps({"recommendation": "accept"}),
    ],
)
def test_decode_fails_closed_on_every_malformed_shape(raw_text: str) -> None:
    with pytest.raises(JudgeDecodeError):
        decode_judge_output(
            raw_text=raw_text,
            judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
            token_usage=0,
            latency_ms=0,
        )


def test_fail_closed_variant_never_raises_and_reports_malformed_output() -> None:
    response = decode_judge_output_fail_closed(
        raw_text="not json",
        judge_role=JudgeIndependenceClass.SHARED_ARTIFACT,
        token_usage=10,
        latency_ms=50,
    )
    assert response.execution_state is EvaluationExecutionState.FAILED
    assert response.failure_reason is JudgeFailureReason.MALFORMED_OUTPUT
    assert response.recommendation is EvaluationRecommendation.UNKNOWN
