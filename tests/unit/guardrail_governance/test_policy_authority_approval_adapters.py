"""Local Policy/Authority/Approval Adapter Tests (P5-D-WU-001/002,
P5-ACC-013)."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.adapters.guardrail_governance.local_authority_provider import (
    LocalAuthorityProvider,
)
from margpa_runtime_llm.adapters.guardrail_governance.local_policy_provider import (
    LocalPolicyProvider,
)
from margpa_runtime_llm.adapters.guardrail_governance.registered_actions import (
    LocalGuardActionAdapter,
)
from margpa_runtime_llm.adapters.guardrail_governance.safety_model_adapters import (
    DeterministicFakeSafetyModelAdapter,
    UnavailableSafetyModelAdapter,
)
from margpa_runtime_llm.adapters.guardrail_governance.unavailable_approval_port import (
    UnavailableApprovalPort,
)
from margpa_runtime_llm.modules.guardrail_governance.domain import (
    ActionId,
    ApprovalOutcome,
    DetectionOutcome,
    GuardDetection,
    PolicyApplicability,
    Severity,
)
from margpa_runtime_llm.modules.guardrail_governance.ports import SafetyModelUnavailable


def _detection(*, category_id: str, outcome: DetectionOutcome) -> GuardDetection:
    return GuardDetection(
        detection_id="d1",
        detector_id="det1",
        category_id=category_id,
        outcome=outcome,
        severity=Severity.HIGH,
    )


def test_policy_provider_recommends_reject_input_for_prompt_injection() -> None:
    provider = LocalPolicyProvider()
    decisions = provider.evaluate(
        point_id="guardrail.input",
        detections=(_detection(category_id="prompt_injection", outcome=DetectionOutcome.MATCH),),
    )
    assert decisions[0].applicability is PolicyApplicability.APPLICABLE
    assert decisions[0].recommended_action_ids == (ActionId.REJECT_INPUT.value,)


def test_policy_provider_marks_clear_detections_not_applicable() -> None:
    provider = LocalPolicyProvider()
    decisions = provider.evaluate(
        point_id="guardrail.input",
        detections=(_detection(category_id="prompt_injection", outcome=DetectionOutcome.CLEAR),),
    )
    assert decisions[0].applicability is PolicyApplicability.NOT_APPLICABLE


def test_policy_provider_never_guesses_an_action_for_an_unmapped_category() -> None:
    provider = LocalPolicyProvider()
    decisions = provider.evaluate(
        point_id="guardrail.input",
        detections=(_detection(category_id="unknown_unresolved", outcome=DetectionOutcome.MATCH),),
    )
    assert decisions[0].applicability is PolicyApplicability.UNKNOWN
    assert decisions[0].recommended_action_ids == ()


def test_authority_provider_never_grants_repair_or_tool_actions() -> None:
    snapshot = LocalAuthorityProvider().snapshot()
    assert "repair" not in snapshot.granted_action_ids
    assert "regenerate" not in snapshot.granted_action_ids
    assert ActionId.REJECT_OUTPUT.value in snapshot.granted_action_ids


def test_approval_port_never_fabricates_approved() -> None:
    port = UnavailableApprovalPort()
    state = port.state_for(action_id="reject_output")
    assert state.outcome is ApprovalOutcome.UNAVAILABLE


def test_registered_action_adapter_flags_intervening_actions_correctly() -> None:
    adapter = LocalGuardActionAdapter()
    reject = adapter.execute(action_id="reject_output", point_id="guardrail.output_candidate")
    warn = adapter.execute(action_id="warn", point_id="guardrail.output_candidate")
    assert reject.intervening is True
    assert warn.intervening is False


def test_unavailable_safety_model_adapter_raises_never_fakes_success() -> None:
    adapter = UnavailableSafetyModelAdapter()
    with pytest.raises(SafetyModelUnavailable):
        adapter.classify(content="anything")


def test_fake_safety_model_adapter_is_deterministic_and_labeled_as_test_only() -> None:
    # P5-CODEX-008 Rework: `.classify()` now returns the raw,
    # unvalidated `RawSafetyModelObservation` — the Fake's own
    # determinism/labeling is checked on that raw shape directly, and
    # the Decoded/Bridged behavior (`.detection`/`.is_trustworthy`) is
    # covered end-to-end in `test_safety_model_seam.py`.
    adapter = DeterministicFakeSafetyModelAdapter(match_marker="TESTMATCH")
    hit = adapter.classify(content="prefix TESTMATCH suffix")
    clear = adapter.classify(content="nothing interesting here")
    assert hit.raw_signal is DetectionOutcome.MATCH
    assert clear.raw_signal is DetectionOutcome.CLEAR
    assert hit.model_id != "" and "test" in hit.model_id
