"""Phase 6-C-WU-005 Baseline Verification.

Covers: Model 0 (deterministic evaluators never call a model), Judge OFF
(zero evaluator calls), Deterministic-only (no LLM Judge dependency at all),
Unknown Reference (a legitimate non-error outcome), and a Malformed Case
(missing required field must fail closed at construction, never silently
coerce to a default).
"""

import pydantic
import pytest

from margpa_runtime_llm.adapters.evaluation.deterministic.evaluators import (
    ExactReferenceMatchEvaluator,
)
from margpa_runtime_llm.modules.evaluation.application.evaluation_orchestrator import (
    EvaluationOrchestrator,
)
from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationMode,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.evaluation.domain.result import EvaluationResult
from margpa_runtime_llm.modules.evaluation.domain.run import EvaluationRun

from .conftest import make_run
from .fixtures_loader import load_qwen_known_failure_modes


def test_dataset_loads_with_a_verifiable_digest_and_all_declared_cases() -> None:
    dataset, cases = load_qwen_known_failure_modes()
    assert dataset.dataset_id == "qwen_known_failure_modes"
    assert len(dataset.digest_sha512) == 128
    assert len(cases) == 6
    assert {case.case_id for case in cases} == {
        "overconfidence_001",
        "definition_confusion_001",
        "insufficient_grounding_001",
        "contradiction_001",
        "format_deviation_001",
        "uncertainty_expression_001",
    }


def test_model_zero_no_deterministic_evaluator_ever_reports_a_model_call() -> None:
    _, cases = load_qwen_known_failure_modes()
    evaluator = ExactReferenceMatchEvaluator()
    for case in cases:
        result = evaluator.evaluate(
            run=make_run(mode=EvaluationMode.ENFORCE, run_id=case.case_id),
            case=case,
            candidate_answer="some candidate answer",
        )
        assert result.call_count == 0
        assert result.token_usage == 0


def test_judge_off_makes_zero_additional_calls_across_the_whole_dataset() -> None:
    _, cases = load_qwen_known_failure_modes()

    class _CountingEvaluator:
        def __init__(self) -> None:
            self.calls = 0

        def evaluate(
            self, *, run: EvaluationRun, case: EvaluationCase, candidate_answer: str
        ) -> EvaluationResult:
            self.calls += 1
            raise AssertionError("must not be called while orchestrator mode is OFF")

    counting_evaluator = _CountingEvaluator()
    orchestrator = EvaluationOrchestrator(mode=EvaluationMode.OFF, evaluator=counting_evaluator)
    for case in cases:
        result = orchestrator.run(
            run=make_run(mode=EvaluationMode.OFF, run_id=case.case_id),
            case=case,
            candidate_answer="anything",
        )
        assert result is None
    assert counting_evaluator.calls == 0


def test_deterministic_only_produces_a_recommendation_with_no_llm_judge_dependency() -> None:
    _, cases = load_qwen_known_failure_modes()
    definition_case = next(case for case in cases if case.case_id == "definition_confusion_001")
    evaluator = ExactReferenceMatchEvaluator()

    result = evaluator.evaluate(
        run=make_run(mode=EvaluationMode.ENFORCE),
        case=definition_case,
        candidate_answer="the time between request and first observable response",
    )

    assert result.recommendation is EvaluationRecommendation.ACCEPT


def test_unknown_reference_case_is_a_legitimate_non_error_outcome() -> None:
    _, cases = load_qwen_known_failure_modes()
    unknown_reference_case = next(
        case for case in cases if case.case_id == "uncertainty_expression_001"
    )
    assert unknown_reference_case.reference is None

    evaluator = ExactReferenceMatchEvaluator()
    result = evaluator.evaluate(
        run=make_run(mode=EvaluationMode.ENFORCE),
        case=unknown_reference_case,
        candidate_answer="I cannot know this without benchmarking.",
    )

    assert result.recommendation is EvaluationRecommendation.UNKNOWN
    assert result.failure_reason is not None


def test_malformed_case_missing_criteria_fails_closed_at_construction() -> None:
    with pytest.raises(pydantic.ValidationError):
        EvaluationCase.model_validate(
            {
                "case_id": "malformed-1",
                "input": "some input",
                "reference": None,
                "criteria": [],
                "language": "en",
                "tags": [],
            }
        )
