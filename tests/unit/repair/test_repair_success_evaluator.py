from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationRecommendation
from margpa_runtime_llm.modules.repair.application.repair_success_evaluator import (
    evaluate_repair_success,
    repair_should_be_accepted,
)
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairOutcome


def test_needs_repair_to_accept_is_improved_and_accepted() -> None:
    outcome = evaluate_repair_success(
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        after_recommendation=EvaluationRecommendation.ACCEPT,
    )
    assert outcome is RepairOutcome.IMPROVED
    assert repair_should_be_accepted(outcome=outcome) is True


def test_accept_to_needs_repair_is_worse_and_never_accepted() -> None:
    outcome = evaluate_repair_success(
        before_recommendation=EvaluationRecommendation.ACCEPT,
        after_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
    )
    assert outcome is RepairOutcome.WORSE
    assert repair_should_be_accepted(outcome=outcome) is False


def test_no_change_is_never_accepted() -> None:
    outcome = evaluate_repair_success(
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        after_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
    )
    assert outcome is RepairOutcome.NO_CHANGE
    assert repair_should_be_accepted(outcome=outcome) is False


def test_either_side_unknown_is_unknown_never_coerced_to_improved() -> None:
    outcome = evaluate_repair_success(
        before_recommendation=EvaluationRecommendation.UNKNOWN,
        after_recommendation=EvaluationRecommendation.ACCEPT,
    )
    assert outcome is RepairOutcome.UNKNOWN
    assert repair_should_be_accepted(outcome=outcome) is False
