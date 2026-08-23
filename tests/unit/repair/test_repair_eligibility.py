from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationRecommendation
from margpa_runtime_llm.modules.repair.application.repair_eligibility_resolver import (
    RepairEligibility,
    resolve_repair_eligibility,
)
from margpa_runtime_llm.modules.repair.domain.budget import RepairBudget, RepairBudgetUsage
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode

_BUDGET = RepairBudget(
    max_attempts=2,
    max_wall_time_ms=10000,
    max_additional_tokens=1000,
    max_total_model_calls=4,
    max_depth=1,
)
_ZERO_USAGE = RepairBudgetUsage(
    attempts_used=0,
    wall_time_used_ms=0,
    additional_tokens_used=0,
    total_model_calls_used=0,
    current_depth=0,
)


def test_guardrail_deny_wins_over_everything_else_including_enforce_mode() -> None:
    eligibility = resolve_repair_eligibility(
        mode=RepairMode.ENFORCE,
        guardrail_denied=True,
        judge_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        budget=_BUDGET,
        usage=_ZERO_USAGE,
    )
    assert eligibility is RepairEligibility.NOT_ELIGIBLE_GUARDRAIL_DENY


def test_mode_off_is_not_eligible_even_with_a_repair_recommendation() -> None:
    eligibility = resolve_repair_eligibility(
        mode=RepairMode.OFF,
        guardrail_denied=False,
        judge_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        budget=_BUDGET,
        usage=_ZERO_USAGE,
    )
    assert eligibility is RepairEligibility.NOT_ELIGIBLE_MODE_OFF


def test_accept_recommendation_is_not_eligible_nothing_to_repair() -> None:
    eligibility = resolve_repair_eligibility(
        mode=RepairMode.ENFORCE,
        guardrail_denied=False,
        judge_recommendation=EvaluationRecommendation.ACCEPT,
        budget=_BUDGET,
        usage=_ZERO_USAGE,
    )
    assert eligibility is RepairEligibility.NOT_ELIGIBLE_NO_REPAIR_RECOMMENDATION


def test_exhausted_budget_is_not_eligible() -> None:
    usage = _ZERO_USAGE.model_copy(update={"attempts_used": 2})
    eligibility = resolve_repair_eligibility(
        mode=RepairMode.ENFORCE,
        guardrail_denied=False,
        judge_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        budget=_BUDGET,
        usage=usage,
    )
    assert eligibility is RepairEligibility.NOT_ELIGIBLE_BUDGET_EXHAUSTED


def test_all_conditions_satisfied_is_eligible() -> None:
    eligibility = resolve_repair_eligibility(
        mode=RepairMode.ENFORCE,
        guardrail_denied=False,
        judge_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        budget=_BUDGET,
        usage=_ZERO_USAGE,
    )
    assert eligibility is RepairEligibility.ELIGIBLE
