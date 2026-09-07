"""Phase 9-2 WU-A A2: EffectiveConfigurationSnapshot."""

from __future__ import annotations

from dataclasses import dataclass, replace

import pytest

from margpa_runtime_llm.modules.experiment.domain.config_snapshot import (
    EffectiveConfigurationSnapshot,
    build_effective_configuration_snapshot,
    compute_configuration_digest_sha512,
)
from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.identity import ComponentKey, ComponentSelection


def _slot(
    key: ComponentKey, selector_id: str | None = None, mode: str | None = None
) -> ComponentSelection:
    return ComponentSelection(component_key=key, selector_id=selector_id, mode=mode)


@dataclass(frozen=True)
class _Slots:
    main: ComponentSelection
    judge: ComponentSelection
    guard: ComponentSelection
    main_governance: ComponentSelection
    definition_set: ComponentSelection
    rag: ComponentSelection
    repair: ComponentSelection
    recording: ComponentSelection
    presentation: ComponentSelection


def _default_slots() -> _Slots:
    return _Slots(
        main=_slot(ComponentKey.MAIN, "main.qwen3-4b"),
        judge=_slot(ComponentKey.JUDGE, "judge.gemma-4-e2b-it-q4-0", "enforce"),
        guard=_slot(ComponentKey.GUARD, mode="off"),
        main_governance=_slot(ComponentKey.MAIN_GOVERNANCE, mode="off"),
        definition_set=_slot(ComponentKey.DEFINITION_SET, "definition-set-a"),
        rag=_slot(ComponentKey.RAG, mode="off"),
        repair=_slot(ComponentKey.REPAIR, mode="off"),
        recording=_slot(ComponentKey.RECORDING, mode="full"),
        presentation=_slot(ComponentKey.PRESENTATION, mode="strict_buffer"),
    )


def test_build_effective_configuration_snapshot_computes_a_verifiable_digest() -> None:
    slots = _default_slots()
    snapshot = build_effective_configuration_snapshot(
        main=slots.main,
        judge=slots.judge,
        guard=slots.guard,
        main_governance=slots.main_governance,
        definition_set=slots.definition_set,
        rag=slots.rag,
        repair=slots.repair,
        recording=slots.recording,
        presentation=slots.presentation,
    )
    expected = compute_configuration_digest_sha512(
        main=slots.main,
        judge=slots.judge,
        guard=slots.guard,
        main_governance=slots.main_governance,
        definition_set=slots.definition_set,
        rag=slots.rag,
        repair=slots.repair,
        recording=slots.recording,
        presentation=slots.presentation,
        provider_artifact_digest_sha512=None,
        definition_digest_sha512=None,
        case_digest_sha512=None,
        plan_digest_sha512=None,
    )
    assert snapshot.configuration_digest_sha512 == expected
    rehydrated = EffectiveConfigurationSnapshot.model_validate(snapshot.model_dump(mode="json"))
    assert rehydrated == snapshot


def test_effective_configuration_snapshot_rejects_component_key_slot_mismatch() -> None:
    # `main`'s slot must carry component_key=MAIN -- swap in JUDGE's own.
    slots = replace(_default_slots(), main=_slot(ComponentKey.JUDGE, "judge-in-main-slot"))
    with pytest.raises(ExperimentCoreError) as excinfo:
        build_effective_configuration_snapshot(
            main=slots.main,
            judge=slots.judge,
            guard=slots.guard,
            main_governance=slots.main_governance,
            definition_set=slots.definition_set,
            rag=slots.rag,
            repair=slots.repair,
            recording=slots.recording,
            presentation=slots.presentation,
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.COMPONENT_SLOT_MISMATCH


def test_effective_configuration_snapshot_rejects_a_hand_picked_mismatched_digest() -> None:
    slots = _default_slots()
    with pytest.raises(ExperimentCoreError) as excinfo:
        EffectiveConfigurationSnapshot(
            main=slots.main,
            judge=slots.judge,
            guard=slots.guard,
            main_governance=slots.main_governance,
            definition_set=slots.definition_set,
            rag=slots.rag,
            repair=slots.repair,
            recording=slots.recording,
            presentation=slots.presentation,
            configuration_digest_sha512="0" * 128,
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.CONFIGURATION_DIGEST_MISMATCH
