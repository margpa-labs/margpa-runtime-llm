"""Domain-level Failure contracts for the Repair Domain."""

from dataclasses import dataclass

from .identifiers import RepairState


@dataclass(frozen=True, slots=True)
class RepairIllegalTransition(Exception):
    current_state: RepairState
    requested_state: RepairState

    def __str__(self) -> str:
        return f"illegal repair transition: {self.current_state} -> {self.requested_state}"


@dataclass(frozen=True, slots=True)
class RepairBudgetExhausted(Exception):
    reason: str

    def __str__(self) -> str:
        return f"repair budget exhausted: {self.reason}"
