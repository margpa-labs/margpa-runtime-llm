import pydantic
import pytest

from margpa_runtime_llm.modules.repair.domain.budget import RepairBudget
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairState, RepairStrategyId
from margpa_runtime_llm.modules.repair.domain.plan import RepairPlan

_BUDGET = RepairBudget(
    max_attempts=3,
    max_wall_time_ms=30000,
    max_additional_tokens=2048,
    max_total_model_calls=6,
    max_depth=1,
)


def _plan(*, state: RepairState = RepairState.PLANNED) -> RepairPlan:
    return RepairPlan(
        repair_plan_id="plan-1",
        trigger_result_refs=("eval-run-1",),
        strategy_id=RepairStrategyId.REGENERATE_WITH_STRUCTURED_FEEDBACK,
        target_attempt_ref="attempt-1",
        budget=_BUDGET,
        success_criteria=("exact_reference_match",),
        state=state,
    )


def test_plan_requires_at_least_one_trigger_result_ref() -> None:
    with pytest.raises(pydantic.ValidationError):
        RepairPlan.model_validate(
            {
                "repair_plan_id": "plan-1",
                "trigger_result_refs": [],
                "strategy_id": RepairStrategyId.FORMAT_ONLY_REPAIR.value,
                "target_attempt_ref": "attempt-1",
                "budget": _BUDGET.model_dump(),
                "success_criteria": ["exact_reference_match"],
                "state": RepairState.PLANNED.value,
            }
        )


def test_plan_is_constructible_with_a_named_strategy() -> None:
    plan = _plan()
    assert plan.strategy_id is RepairStrategyId.REGENERATE_WITH_STRUCTURED_FEEDBACK
    assert plan.state is RepairState.PLANNED
