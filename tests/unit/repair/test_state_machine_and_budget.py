import pytest

from margpa_runtime_llm.modules.repair.domain.budget import RepairBudget, RepairBudgetUsage
from margpa_runtime_llm.modules.repair.domain.errors import (
    RepairBudgetExhausted,
    RepairIllegalTransition,
)
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairState
from margpa_runtime_llm.modules.repair.domain.state_machine import (
    check_repair_budget,
    is_terminal,
    validate_repair_transition,
)

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


@pytest.mark.parametrize(
    ("current", "requested"),
    [
        (RepairState.PLANNED, RepairState.AUTHORIZED),
        (RepairState.AUTHORIZED, RepairState.GENERATING_REPAIR),
        (RepairState.GENERATING_REPAIR, RepairState.REJUDGING),
        (RepairState.REJUDGING, RepairState.ACCEPTED),
        (RepairState.REJUDGING, RepairState.REJECTED),
        (RepairState.REJUDGING, RepairState.EXHAUSTED),
        (RepairState.PLANNED, RepairState.CANCELLED),
    ],
)
def test_valid_transitions_are_accepted(current: RepairState, requested: RepairState) -> None:
    assert validate_repair_transition(current_state=current, requested_state=requested) is requested


@pytest.mark.parametrize(
    ("current", "requested"),
    [
        (RepairState.PLANNED, RepairState.REJUDGING),  # skips authorized/generating_repair
        (RepairState.PLANNED, RepairState.ACCEPTED),
        (RepairState.ACCEPTED, RepairState.REJUDGING),  # terminal -> anything
        (RepairState.CANCELLED, RepairState.PLANNED),  # terminal -> anything
        (RepairState.GENERATING_REPAIR, RepairState.ACCEPTED),  # skips rejudging
    ],
)
def test_illegal_transitions_are_rejected(current: RepairState, requested: RepairState) -> None:
    with pytest.raises(RepairIllegalTransition):
        validate_repair_transition(current_state=current, requested_state=requested)


def test_terminal_states_are_identified() -> None:
    for state in (
        RepairState.ACCEPTED,
        RepairState.REJECTED,
        RepairState.EXHAUSTED,
        RepairState.FAILED,
        RepairState.CANCELLED,
    ):
        assert is_terminal(state=state) is True
    for state in (
        RepairState.PLANNED,
        RepairState.AUTHORIZED,
        RepairState.GENERATING_REPAIR,
        RepairState.REJUDGING,
    ):
        assert is_terminal(state=state) is False


def test_budget_within_limits_does_not_raise() -> None:
    check_repair_budget(budget=_BUDGET, usage=_ZERO_USAGE)


def test_budget_exhausted_on_attempts_raises() -> None:
    usage = _ZERO_USAGE.model_copy(update={"attempts_used": 2})
    with pytest.raises(RepairBudgetExhausted):
        check_repair_budget(budget=_BUDGET, usage=usage)


def test_budget_exhausted_on_depth_raises() -> None:
    usage = _ZERO_USAGE.model_copy(update={"current_depth": 1})
    with pytest.raises(RepairBudgetExhausted):
        check_repair_budget(budget=_BUDGET, usage=usage)
