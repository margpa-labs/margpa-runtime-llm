"""Repair State Machine transition validation (Architecture 7.2).

    planned -> authorized -> generating_repair -> rejudging
      -> accepted | rejected | exhausted | failed | cancelled

Cancellation and failure can also interrupt earlier states directly.
"""

from .budget import RepairBudget, RepairBudgetUsage
from .errors import RepairBudgetExhausted, RepairIllegalTransition
from .identifiers import RepairState

_TERMINAL_STATES = frozenset(
    {
        RepairState.ACCEPTED,
        RepairState.REJECTED,
        RepairState.EXHAUSTED,
        RepairState.FAILED,
        RepairState.CANCELLED,
    }
)

_ALLOWED_TRANSITIONS: dict[RepairState, frozenset[RepairState]] = {
    RepairState.PLANNED: frozenset(
        {RepairState.AUTHORIZED, RepairState.CANCELLED, RepairState.FAILED}
    ),
    RepairState.AUTHORIZED: frozenset(
        {RepairState.GENERATING_REPAIR, RepairState.CANCELLED, RepairState.FAILED}
    ),
    RepairState.GENERATING_REPAIR: frozenset(
        {RepairState.REJUDGING, RepairState.CANCELLED, RepairState.FAILED}
    ),
    RepairState.REJUDGING: frozenset(
        {
            RepairState.ACCEPTED,
            RepairState.REJECTED,
            RepairState.EXHAUSTED,
            RepairState.CANCELLED,
            RepairState.FAILED,
        }
    ),
}


def validate_repair_transition(
    *, current_state: RepairState, requested_state: RepairState
) -> RepairState:
    if current_state in _TERMINAL_STATES:
        raise RepairIllegalTransition(current_state=current_state, requested_state=requested_state)
    allowed = _ALLOWED_TRANSITIONS.get(current_state, frozenset())
    if requested_state not in allowed:
        raise RepairIllegalTransition(current_state=current_state, requested_state=requested_state)
    return requested_state


def is_terminal(*, state: RepairState) -> bool:
    return state in _TERMINAL_STATES


def check_repair_budget(*, budget: RepairBudget, usage: RepairBudgetUsage) -> None:
    """Raises RepairBudgetExhausted on the first exceeded limit; never partially allows."""
    if usage.attempts_used >= budget.max_attempts:
        raise RepairBudgetExhausted(
            reason=f"attempts_used={usage.attempts_used} >= max_attempts={budget.max_attempts}"
        )
    if usage.wall_time_used_ms >= budget.max_wall_time_ms:
        raise RepairBudgetExhausted(
            reason=(
                f"wall_time_used_ms={usage.wall_time_used_ms} "
                f">= max_wall_time_ms={budget.max_wall_time_ms}"
            )
        )
    if usage.additional_tokens_used >= budget.max_additional_tokens:
        raise RepairBudgetExhausted(
            reason=(
                f"additional_tokens_used={usage.additional_tokens_used} "
                f">= max_additional_tokens={budget.max_additional_tokens}"
            )
        )
    if usage.total_model_calls_used >= budget.max_total_model_calls:
        raise RepairBudgetExhausted(
            reason=(
                f"total_model_calls_used={usage.total_model_calls_used} "
                f">= max_total_model_calls={budget.max_total_model_calls}"
            )
        )
    if usage.current_depth >= budget.max_depth:
        raise RepairBudgetExhausted(
            reason=f"current_depth={usage.current_depth} >= max_depth={budget.max_depth}"
        )
