"""Governance Mode Contract: default off, observe available, enforce
unavailable, no silent downgrade (P3-F-WU-001)."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.configuration_control import ApplyDisposition
from margpa_runtime_llm.modules.governance_definitions.domain import (
    GovernanceMode,
    GovernanceModeAvailability,
    GovernanceModeTransitionError,
    build_governance_mode_snapshot,
    request_mode_transition,
)


def test_off_and_observe_are_available_enforce_is_not() -> None:
    from margpa_runtime_llm.modules.governance_definitions.domain import (
        PHASE_3_MODE_DESCRIPTORS,
    )

    by_mode = {d.mode: d for d in PHASE_3_MODE_DESCRIPTORS}
    assert by_mode[GovernanceMode.OFF].availability is GovernanceModeAvailability.AVAILABLE
    assert by_mode[GovernanceMode.OBSERVE].availability is GovernanceModeAvailability.AVAILABLE
    assert by_mode[GovernanceMode.ENFORCE].availability is GovernanceModeAvailability.UNAVAILABLE
    assert by_mode[GovernanceMode.ENFORCE].apply_disposition is ApplyDisposition.UNSUPPORTED
    assert by_mode[GovernanceMode.ENFORCE].unavailable_reason_code is not None


def test_request_mode_transition_off_to_observe_succeeds() -> None:
    result = request_mode_transition(
        current_mode=GovernanceMode.OFF, requested_mode=GovernanceMode.OBSERVE
    )
    assert result is GovernanceMode.OBSERVE


def test_request_mode_transition_to_enforce_raises_never_silently_downgrades() -> None:
    with pytest.raises(GovernanceModeTransitionError) as excinfo:
        request_mode_transition(
            current_mode=GovernanceMode.OFF, requested_mode=GovernanceMode.ENFORCE
        )
    assert excinfo.value.requested_mode is GovernanceMode.ENFORCE
    # The failure must not have silently produced OBSERVE as a fallback —
    # callers only ever see the exception, never a substituted mode.


def test_redundant_transition_request_is_a_no_op_not_an_error() -> None:
    result = request_mode_transition(
        current_mode=GovernanceMode.OBSERVE, requested_mode=GovernanceMode.OBSERVE
    )
    assert result is GovernanceMode.OBSERVE


def test_snapshot_digest_changes_with_mode_or_revision() -> None:
    snapshot_off = build_governance_mode_snapshot(revision=1, current_mode=GovernanceMode.OFF)
    snapshot_observe = build_governance_mode_snapshot(
        revision=1, current_mode=GovernanceMode.OBSERVE
    )
    snapshot_off_rev2 = build_governance_mode_snapshot(revision=2, current_mode=GovernanceMode.OFF)

    assert snapshot_off.digest_sha512 != snapshot_observe.digest_sha512
    assert snapshot_off.digest_sha512 != snapshot_off_rev2.digest_sha512


def test_default_snapshot_mode_is_off() -> None:
    # The Contract itself does not hardcode a "default" — P3-MOD-002's
    # off-as-initial-default is a Bootstrap-layer decision (P3-F-WU-002).
    # This test documents that OFF is at minimum a legal, always-available
    # starting point with RUNTIME_APPLICABLE apply disposition.
    snapshot = build_governance_mode_snapshot(revision=0, current_mode=GovernanceMode.OFF)
    assert snapshot.current_mode is GovernanceMode.OFF
    off_descriptor = next(d for d in snapshot.descriptors if d.mode is GovernanceMode.OFF)
    assert off_descriptor.apply_disposition is ApplyDisposition.RUNTIME_APPLICABLE
