"""RepairResult (Architecture 7.1/8): Before/After compared under the same Criteria."""

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identifiers import RepairOutcome


class RepairResult(ImmutableContract):
    repair_plan_id: str = Field(min_length=1)
    attempt_id: str = Field(min_length=1)
    before_evaluation_run_ref: str = Field(min_length=1)
    after_evaluation_run_ref: str = Field(min_length=1)
    outcome: RepairOutcome
    accepted: bool
    presented_answer_is_repair: bool
    """False unless outcome is IMPROVED and accepted is True (Architecture 8:
    Repair Candidate is adopted as the Presented Answer only on success)."""
