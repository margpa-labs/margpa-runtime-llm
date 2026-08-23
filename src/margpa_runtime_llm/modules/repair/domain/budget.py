"""RepairBudget (Architecture 7.3)."""

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract


class RepairBudget(ImmutableContract):
    max_attempts: int = Field(gt=0)
    max_wall_time_ms: int = Field(gt=0)
    max_additional_tokens: int = Field(gt=0)
    max_total_model_calls: int = Field(gt=0)
    max_depth: int = Field(gt=0)
    deadline: str | None = None
    """ISO-8601 timestamp; None means no absolute deadline beyond the other limits."""


class RepairBudgetUsage(ImmutableContract):
    """Current consumption, tracked separately from the immutable Budget itself."""

    attempts_used: int = Field(ge=0)
    wall_time_used_ms: int = Field(ge=0)
    additional_tokens_used: int = Field(ge=0)
    total_model_calls_used: int = Field(ge=0)
    current_depth: int = Field(ge=0)
