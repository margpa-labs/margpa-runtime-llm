import json

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


@pytest.mark.parametrize(
    "raw_text",
    [
        '{"recommendation":"accept","confidence":0.9} '
        '{"recommendation":"needs_repair","confidence":0.9}',
        '{"recommendation":"accept","confidence":0.9,"verdict":"pass"}',
    ],
)
def test_decode_rejects_ambiguous_multiple_objects_and_schema_extensions(raw_text: str) -> None:
    with pytest.raises(JudgeDecodeError):
        decode_judge_output(
            raw_text=raw_text,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=1,
            latency_ms=1,
        )


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
