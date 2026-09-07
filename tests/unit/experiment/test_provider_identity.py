"""Phase 9-2 R4-WU-01: `domain.provider_identity.ProviderIdentityEnvelope`."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.experiment.domain.errors import ExperimentCoreError
from margpa_runtime_llm.modules.experiment.domain.identity import ComponentKey
from margpa_runtime_llm.modules.experiment.domain.provider_identity import (
    ProviderIdentityDetail,
    ProviderIdentityEnvelope,
)


def _envelope(
    *,
    main: ProviderIdentityDetail | None = None,
    judge: ProviderIdentityDetail | None = None,
    guard: ProviderIdentityDetail | None = None,
) -> ProviderIdentityEnvelope:
    return ProviderIdentityEnvelope(
        main=main if main is not None else ProviderIdentityDetail(component_key=ComponentKey.MAIN),
        judge=judge
        if judge is not None
        else ProviderIdentityDetail(component_key=ComponentKey.JUDGE),
        guard=guard
        if guard is not None
        else ProviderIdentityDetail(component_key=ComponentKey.GUARD),
    )


def test_a_slot_carrying_the_wrong_component_key_is_rejected() -> None:
    with pytest.raises(ExperimentCoreError):
        _envelope(main=ProviderIdentityDetail(component_key=ComponentKey.JUDGE))


def test_configured_and_active_are_independently_reportable() -> None:
    """Hard Assert (Handoff R4 SS4.2): "Configured Gemma/Active noneと、
    Configured Gemma/Active Gemmaを区別できる"."""

    configured_only = ProviderIdentityDetail(
        component_key=ComponentKey.JUDGE,
        configured_selector_id="judge.gemma-4-e2b-it-q4-0",
        active_selector_id=None,
    )
    configured_and_active = ProviderIdentityDetail(
        component_key=ComponentKey.JUDGE,
        configured_selector_id="judge.gemma-4-e2b-it-q4-0",
        active_selector_id="judge.gemma-4-e2b-it-q4-0",
    )
    assert configured_only.configured_selector_id == configured_and_active.configured_selector_id
    assert configured_only.active_selector_id is None
    assert configured_and_active.active_selector_id is not None


def test_artifact_digest_is_never_substituted_across_components() -> None:
    """Hard Assert: "Judge/Guard Artifact不明をMain Artifact Digestで代用
    しない" -- each slot's `artifact_digest_sha512` is independent; an
    Unavailable Judge/Guard digest must stay `None`, never borrow Main's."""

    envelope = _envelope(
        main=ProviderIdentityDetail(
            component_key=ComponentKey.MAIN,
            active_selector_id="main.qwen3-4b-q4-k-m",
            artifact_digest_sha512="a" * 128,
        ),
        judge=ProviderIdentityDetail(component_key=ComponentKey.JUDGE, active_selector_id=None),
    )
    assert envelope.judge.artifact_digest_sha512 is None
    assert envelope.judge.artifact_digest_sha512 != envelope.main.artifact_digest_sha512


def test_with_expected_executed_fills_in_only_that_field() -> None:
    envelope = _envelope(
        judge=ProviderIdentityDetail(
            component_key=ComponentKey.JUDGE,
            configured_selector_id="judge.gemma-4-e2b-it-q4-0",
            active_selector_id=None,
        )
    )
    updated = envelope.with_expected_executed(
        main="main.qwen3-4b-q4-k-m", judge="judge.gemma-4-e2b-it-q4-0", guard=None
    )
    assert updated.judge.expected_executed_selector_id == "judge.gemma-4-e2b-it-q4-0"
    assert updated.judge.configured_selector_id == "judge.gemma-4-e2b-it-q4-0"
    assert updated.judge.active_selector_id is None
    assert updated.main.expected_executed_selector_id == "main.qwen3-4b-q4-k-m"
    assert updated.guard.expected_executed_selector_id is None
