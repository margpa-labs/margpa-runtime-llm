"""Context Budget/Pressure Core (Canonical Design SS6).

`compute_pressure_state()` is a pure function over already-measured values:
it never performs I/O, never calls a Model, and never mutates anything --
matching Invariant 4 ("Auto OFFでもBudget Measurement...は利用可能である").
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.conversation.domain.identity import ConversationId
from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identity import ContextBranchId
from .measurement import MeasuredTokens, MeasurementClass


class PressureState(StrEnum):
    NORMAL = "normal"
    APPROACHING_AUTO_TRIGGER = "approaching_auto_trigger"
    AUTO_COMPACTION_REQUIRED = "auto_compaction_required"
    MANUAL_COMPACTION_REQUIRED = "manual_compaction_required"
    HARD_RESERVE_PROTECTED = "hard_reserve_protected"
    UNKNOWN = "unknown"


class ThresholdConfig(ImmutableContract):
    """Token-count floors on Effective Remaining Budget (SS6.1/6.3).

    `hard_reserve_boundary` is deliberately not a separate field: by SS6.1's
    own formula, once every Reserve (Generation/System-Governance/RAG-Tool/
    Compaction-Working/Safety Margin) has already been subtracted, crossing
    zero Effective Remaining Budget *is* the Hard Reserve boundary -- a
    second, independent threshold for the same event would let the two
    disagree.
    """

    advisory_remaining_budget_floor: int = Field(ge=0)
    auto_trigger_remaining_budget_floor: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_ordering(self) -> ThresholdConfig:
        if self.auto_trigger_remaining_budget_floor > self.advisory_remaining_budget_floor:
            raise ValueError(
                "auto_trigger_remaining_budget_floor must not exceed the advisory floor"
            )
        return self


class ContextBudgetSnapshot(ImmutableContract):
    conversation_id: ConversationId
    branch_id: ContextBranchId
    source_conversation_revision: int = Field(ge=1)
    model_context_capacity: MeasuredTokens
    current_prompt_usage: MeasuredTokens
    generation_reserve: MeasuredTokens
    system_governance_reserve: MeasuredTokens
    rag_tool_reserve: MeasuredTokens
    compaction_working_reserve: MeasuredTokens
    safety_margin: MeasuredTokens
    computed_at: datetime


def compute_effective_remaining_budget(snapshot: ContextBudgetSnapshot) -> int | None:
    """`None` (never 0) when any contributing measurement is Unknown."""

    components = (
        snapshot.model_context_capacity,
        snapshot.current_prompt_usage,
        snapshot.generation_reserve,
        snapshot.system_governance_reserve,
        snapshot.rag_tool_reserve,
        snapshot.compaction_working_reserve,
        snapshot.safety_margin,
    )
    if any(component.measurement_class is MeasurementClass.UNKNOWN for component in components):
        return None
    capacity = snapshot.model_context_capacity.value
    assert capacity is not None
    reserved_and_used = sum(
        component.value  # type: ignore[misc]
        for component in components[1:]
    )
    return capacity - reserved_and_used


def compute_pressure_state(
    snapshot: ContextBudgetSnapshot,
    thresholds: ThresholdConfig,
    *,
    auto_compaction_enabled: bool,
) -> PressureState:
    effective_remaining = compute_effective_remaining_budget(snapshot)
    if effective_remaining is None:
        return PressureState.UNKNOWN
    if effective_remaining <= 0:
        return (
            PressureState.HARD_RESERVE_PROTECTED
            if auto_compaction_enabled
            else PressureState.MANUAL_COMPACTION_REQUIRED
        )
    if effective_remaining <= thresholds.auto_trigger_remaining_budget_floor:
        return (
            PressureState.AUTO_COMPACTION_REQUIRED
            if auto_compaction_enabled
            else PressureState.APPROACHING_AUTO_TRIGGER
        )
    if effective_remaining <= thresholds.advisory_remaining_budget_floor:
        return PressureState.APPROACHING_AUTO_TRIGGER
    return PressureState.NORMAL


def generation_should_be_blocked(pressure: PressureState) -> bool:
    """Only `manual_compaction_required` blocks ordinary Generation
    (SS6.4) -- `hard_reserve_protected` means Auto is expected to resolve
    it through the normal Coordinator Pipeline before the next Attempt,
    never a silent block."""

    return pressure is PressureState.MANUAL_COMPACTION_REQUIRED
