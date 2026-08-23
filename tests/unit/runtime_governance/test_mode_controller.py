"""Main Governance Mode Controller (P4-F-WU-002, P4-MOD-004/005)."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.governance_definitions.domain import (
    GovernanceMode,
    GovernanceModeAvailability,
    GovernanceModeTransitionError,
)
from margpa_runtime_llm.modules.runtime_governance.application import (
    MainGovernanceModeController,
)


def test_default_mode_is_off() -> None:
    controller = MainGovernanceModeController(enforce_ready=True)
    snapshot = controller.mode_snapshot()
    assert snapshot.current_mode is GovernanceMode.OFF
    assert snapshot.revision == 1


def test_enforce_unready_marks_enforce_unavailable_with_a_reason() -> None:
    controller = MainGovernanceModeController(enforce_ready=False)
    descriptors = {d.mode: d for d in controller.mode_snapshot().descriptors}
    assert descriptors[GovernanceMode.OFF].availability is GovernanceModeAvailability.AVAILABLE
    assert descriptors[GovernanceMode.OBSERVE].availability is GovernanceModeAvailability.AVAILABLE
    assert (
        descriptors[GovernanceMode.ENFORCE].availability is GovernanceModeAvailability.UNAVAILABLE
    )
    assert descriptors[GovernanceMode.ENFORCE].unavailable_reason_code is not None


def test_enforce_ready_marks_enforce_available() -> None:
    controller = MainGovernanceModeController(enforce_ready=True)
    descriptors = {d.mode: d for d in controller.mode_snapshot().descriptors}
    assert descriptors[GovernanceMode.ENFORCE].availability is GovernanceModeAvailability.AVAILABLE


def test_requesting_unavailable_enforce_raises_never_silently_downgrades() -> None:
    controller = MainGovernanceModeController(enforce_ready=False)
    with pytest.raises(GovernanceModeTransitionError):
        controller.apply_mode(GovernanceMode.ENFORCE)
    assert controller.current_mode_value() == "off"


def test_apply_mode_increments_revision_only_on_a_real_change() -> None:
    controller = MainGovernanceModeController(enforce_ready=True)
    first = controller.mode_snapshot()
    same = controller.apply_mode(GovernanceMode.OFF)
    assert same.revision == first.revision

    changed = controller.apply_mode(GovernanceMode.OBSERVE)
    assert changed.revision == first.revision + 1
    assert controller.current_mode_value() == "observe"


def test_apply_mode_to_enforce_succeeds_when_ready() -> None:
    controller = MainGovernanceModeController(enforce_ready=True)
    snapshot = controller.apply_mode(GovernanceMode.ENFORCE)
    assert snapshot.current_mode is GovernanceMode.ENFORCE
    assert controller.current_mode_value() == "enforce"
