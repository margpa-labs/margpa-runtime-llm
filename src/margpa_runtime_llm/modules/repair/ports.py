"""Ports for the Repair Domain (Architecture 7.1, Phase 6-E-WU-003)."""

from typing import Protocol, runtime_checkable

from .domain.plan import RepairPlan


@runtime_checkable
class RepairAttemptGeneratorPort(Protocol):
    """Produces a New Attempt's candidate text; never rewrites the Original Attempt."""

    def generate_repair_attempt(self, *, plan: RepairPlan, structured_feedback: str) -> str: ...
