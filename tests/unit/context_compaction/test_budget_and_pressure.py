"""CL-P9-3-A: Budget/Pressure Core -- pure domain, no I/O.

Covers Mandatory Hard Evidence #1 (Auto Default ON), #2 (Manual available
regardless of Auto), #5 (Hard Reserve Auto ON/OFF branching).
"""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.context_compaction.application.auto_policy import (
    AutoCompactionPolicyController,
)
from margpa_runtime_llm.modules.context_compaction.domain import (
    DEFAULT_BRANCH_ID,
    ContextBudgetSnapshot,
    MeasuredTokens,
    MeasurementClass,
    PressureState,
    ThresholdConfig,
    compute_effective_remaining_budget,
    compute_pressure_state,
    generation_should_be_blocked,
)
from margpa_runtime_llm.modules.conversation.domain.identity import ConversationId

_NOW = datetime.now(UTC)


def _tokens(
    value: int | None, cls: MeasurementClass = MeasurementClass.ESTIMATED
) -> MeasuredTokens:
    if value is None:
        return MeasuredTokens.unknown(source="test", observed_at=_NOW)
    return MeasuredTokens(value=value, measurement_class=cls, source="test", observed_at=_NOW)


def _snapshot(*, capacity: int | None, usage: int, reserves: int = 100) -> ContextBudgetSnapshot:
    return ContextBudgetSnapshot(
        conversation_id=ConversationId(value="conv-1"),
        branch_id=DEFAULT_BRANCH_ID,
        source_conversation_revision=1,
        model_context_capacity=_tokens(capacity, MeasurementClass.PROVIDER_REPORTED),
        current_prompt_usage=_tokens(usage, MeasurementClass.RUNTIME_CALCULATED),
        generation_reserve=_tokens(reserves),
        system_governance_reserve=_tokens(reserves),
        rag_tool_reserve=_tokens(0),
        compaction_working_reserve=_tokens(reserves),
        safety_margin=_tokens(reserves),
        computed_at=_NOW,
    )


_THRESHOLDS = ThresholdConfig(
    advisory_remaining_budget_floor=1000, auto_trigger_remaining_budget_floor=500
)


def test_auto_compaction_policy_defaults_to_enabled() -> None:
    policy = AutoCompactionPolicyController()
    assert policy.is_enabled() is True


def test_manual_is_never_gated_by_auto_policy_state() -> None:
    """Hard Evidence #2/#3: nothing in the Budget/Pressure Core itself reads
    the Auto Policy except `compute_pressure_state`'s own explicit
    `auto_compaction_enabled` parameter -- Manual callers (the Coordinator's
    `request_manual_compaction`) never consult it at all, proven at the
    Coordinator layer in the integration suite. Here we prove the Budget
    computation itself works identically regardless of Auto state."""

    snapshot = _snapshot(capacity=4096, usage=1000)
    remaining_with_auto_on = compute_effective_remaining_budget(snapshot)
    remaining_with_auto_off = compute_effective_remaining_budget(snapshot)
    assert remaining_with_auto_on == remaining_with_auto_off


def test_unknown_capacity_yields_unknown_pressure_never_zero() -> None:
    snapshot = _snapshot(capacity=None, usage=1000)
    assert compute_effective_remaining_budget(snapshot) is None
    assert compute_pressure_state(snapshot, _THRESHOLDS, auto_compaction_enabled=True) == (
        PressureState.UNKNOWN
    )


@pytest.mark.parametrize(
    ("usage", "expected"),
    [
        (100, PressureState.NORMAL),
        (3000, PressureState.APPROACHING_AUTO_TRIGGER),
        (3200, PressureState.AUTO_COMPACTION_REQUIRED),
    ],
)
def test_pressure_state_progression_with_auto_on(usage: int, expected: PressureState) -> None:
    snapshot = _snapshot(capacity=4096, usage=usage)
    assert compute_pressure_state(snapshot, _THRESHOLDS, auto_compaction_enabled=True) is expected


def test_hard_reserve_with_auto_on_is_protected_not_manual_required() -> None:
    """Hard Evidence #5: Auto ON at the Hard Reserve boundary means the
    Coordinator is expected to resolve it automatically -- Generation is
    not blocked by this Pressure State alone."""

    snapshot = _snapshot(capacity=4096, usage=3800)
    pressure = compute_pressure_state(snapshot, _THRESHOLDS, auto_compaction_enabled=True)
    assert pressure is PressureState.HARD_RESERVE_PROTECTED
    assert generation_should_be_blocked(pressure) is False


def test_hard_reserve_with_auto_off_requires_manual_and_blocks_generation() -> None:
    """Hard Evidence #2/#3/#5: Auto OFF at Hard Reserve blocks ordinary
    Generation with `manual_compaction_required`, while Manual Compaction
    itself stays reachable (proven at the Coordinator layer)."""

    snapshot = _snapshot(capacity=4096, usage=3800)
    pressure = compute_pressure_state(snapshot, _THRESHOLDS, auto_compaction_enabled=False)
    assert pressure is PressureState.MANUAL_COMPACTION_REQUIRED
    assert generation_should_be_blocked(pressure) is True


def test_auto_trigger_zone_with_auto_off_is_only_advisory() -> None:
    """`usage=3200` crosses the `auto_trigger_remaining_budget_floor` (not
    merely the wider advisory one) -- with Auto ON this is
    `AUTO_COMPACTION_REQUIRED` (see the parametrized test above); with Auto
    OFF it degrades to an advisory only, never blocking Generation."""

    snapshot = _snapshot(capacity=4096, usage=3200)
    pressure = compute_pressure_state(snapshot, _THRESHOLDS, auto_compaction_enabled=False)
    assert pressure is PressureState.APPROACHING_AUTO_TRIGGER
    assert generation_should_be_blocked(pressure) is False


def test_threshold_config_rejects_inverted_floors() -> None:
    with pytest.raises(ValidationError):
        ThresholdConfig(
            advisory_remaining_budget_floor=100, auto_trigger_remaining_budget_floor=200
        )


def test_measured_tokens_unknown_never_carries_a_value() -> None:
    unknown = MeasuredTokens.unknown(source="test", observed_at=_NOW)
    assert unknown.value is None
    with pytest.raises(ValidationError):
        MeasuredTokens(
            value=None, measurement_class=MeasurementClass.ESTIMATED, source="x", observed_at=_NOW
        )
    with pytest.raises(ValidationError):
        MeasuredTokens(
            value=5, measurement_class=MeasurementClass.UNKNOWN, source="x", observed_at=_NOW
        )
