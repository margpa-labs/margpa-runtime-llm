"""RepairPlan/RepairAttempt (Architecture 7.1)."""

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .budget import RepairBudget
from .identifiers import RepairState, RepairStrategyId


class RepairPlan(ImmutableContract):
    repair_plan_id: str = Field(min_length=1)
    trigger_result_refs: tuple[str, ...] = Field(min_length=1)
    strategy_id: RepairStrategyId
    target_attempt_ref: str = Field(min_length=1)
    authority_ref: str | None = None
    policy_ref: str | None = None
    budget: RepairBudget
    success_criteria: tuple[str, ...] = Field(min_length=1)
    state: RepairState


class RepairAttempt(ImmutableContract):
    """A new Attempt Identity, never a rewrite of the Original Attempt (Architecture 7.2)."""

    attempt_id: str = Field(min_length=1)
    repair_plan_id: str = Field(min_length=1)
    attempt_number: int = Field(gt=0)
    original_attempt_ref: str = Field(min_length=1)
    state: RepairState
