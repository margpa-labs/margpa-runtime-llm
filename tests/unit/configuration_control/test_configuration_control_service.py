"""Process-local configuration-control state machine tests."""

from __future__ import annotations

import threading

import pytest

from margpa_runtime_llm.modules.configuration_control import (
    ApplyDisposition,
    ConfigurationApplyOutcome,
    ConfigurationControlError,
    ConfigurationControlErrorCode,
    ConfigurationControlService,
    ConfigurationField,
    ConfigurationPatch,
    ConfigurationPreviewOutcome,
    ConfigurationSource,
    DocumentationRagControlMode,
    FeatureHookDescriptor,
    GovernanceControlMode,
    GovernanceHookDescriptor,
    GuardrailGovernanceControlMode,
    GuardrailGovernanceHookDescriptor,
    MainGovernanceControlMode,
    MainGovernanceHookDescriptor,
    RecordingControlMode,
    RecordingHookDescriptor,
    ResearchDeveloperMode,
)


def service() -> ConfigurationControlService:
    fields = tuple(
        ConfigurationField(
            key=key,
            value=value,
            source=source,
            apply_disposition=disposition,
        )
        for key, value, source, disposition in (
            (
                "selected_model",
                "main.model",
                ConfigurationSource.APPLICATION,
                ApplyDisposition.RESTART_REQUIRED,
            ),
            (
                "profile_key",
                "local.profile",
                ConfigurationSource.EXPLICIT_CLI,
                ApplyDisposition.READ_ONLY,
            ),
            (
                "context_size",
                4096,
                ConfigurationSource.DEPLOYMENT_PROFILE,
                ApplyDisposition.RESTART_REQUIRED,
            ),
            (
                "backend_kind",
                "metal",
                ConfigurationSource.DEPLOYMENT_PROFILE,
                ApplyDisposition.READ_ONLY,
            ),
            (
                "device_kind",
                "gpu",
                ConfigurationSource.DEPLOYMENT_PROFILE,
                ApplyDisposition.READ_ONLY,
            ),
            (
                "acceleration_api",
                "metal",
                ConfigurationSource.DEPLOYMENT_PROFILE,
                ApplyDisposition.READ_ONLY,
            ),
            (
                "max_new_tokens",
                2048,
                ConfigurationSource.APPLICATION,
                ApplyDisposition.READ_ONLY,
            ),
            (
                "research_developer_mode",
                "off",
                ConfigurationSource.BUILT_IN_DEFAULT,
                ApplyDisposition.RUNTIME_APPLICABLE,
            ),
            (
                "conversation_storage_kind",
                "sqlite",
                ConfigurationSource.COMPOSED_RUNTIME,
                ApplyDisposition.READ_ONLY,
            ),
            (
                "conversation_storage_version",
                "3.45.1",
                ConfigurationSource.COMPOSED_RUNTIME,
                ApplyDisposition.READ_ONLY,
            ),
        )
    )
    return ConfigurationControlService(
        fields=fields,
        feature_hooks=(
            FeatureHookDescriptor(
                component_key="documentation_rag",
                allowed_modes=(
                    DocumentationRagControlMode.DISABLED,
                    DocumentationRagControlMode.ENABLED,
                ),
                current_mode=DocumentationRagControlMode.DISABLED,
                available=True,
            ),
        ),
        recording_hooks=(
            RecordingHookDescriptor(
                component_key="conversation_recording",
                allowed_modes=(RecordingControlMode.OFF,),
                current_mode=RecordingControlMode.OFF,
                available=False,
            ),
        ),
    )


def service_with_rag_hook(
    hook: FeatureHookDescriptor,
) -> ConfigurationControlService:
    base = service()
    return ConfigurationControlService(
        fields=base.effective().fields,
        feature_hooks=(hook,),
        recording_hooks=base.effective().recording_hooks,
    )


_GOVERNANCE_ALLOWED_MODES = (GovernanceControlMode.OFF, GovernanceControlMode.OBSERVE)


class _RecordingGovernanceApplier:
    def __init__(self) -> None:
        self.calls: list[GovernanceControlMode] = []

    def apply(self, mode: GovernanceControlMode) -> GovernanceHookDescriptor:
        self.calls.append(mode)
        return GovernanceHookDescriptor(
            component_key="governance_mode",
            allowed_modes=_GOVERNANCE_ALLOWED_MODES,
            current_mode=mode,
            available=True,
        )


class _FailingGovernanceApplier:
    def apply(self, mode: GovernanceControlMode) -> GovernanceHookDescriptor:
        del mode
        raise RuntimeError("simulated governance pipeline failure")


def service_with_governance(
    applier: object, *, current_mode: GovernanceControlMode = GovernanceControlMode.OFF
) -> ConfigurationControlService:
    base = service()
    return ConfigurationControlService(
        fields=base.effective().fields,
        feature_hooks=base.effective().feature_hooks,
        recording_hooks=base.effective().recording_hooks,
        governance_hooks=(
            GovernanceHookDescriptor(
                component_key="governance_mode",
                allowed_modes=_GOVERNANCE_ALLOWED_MODES,
                current_mode=current_mode,
                available=True,
            ),
        ),
        governance_mode_applier=applier,  # type: ignore[arg-type]
    )


def test_preview_is_read_only_and_reports_restart_without_staging() -> None:
    control = service()
    before = control.effective()

    preview = control.preview(
        ConfigurationPatch(selected_model="candidate.model", context_size=8192)
    )

    assert preview.outcome is ConfigurationPreviewOutcome.RESTART_REQUIRED
    assert preview.restart_fields == ("selected_model", "context_size")
    assert control.effective() == before


def test_only_research_mode_applies_and_restart_creates_a_fresh_default() -> None:
    control = service()
    before = control.effective()

    applied = control.apply(
        operation_id="apply-research",
        expected_revision=before.revision,
        expected_digest=before.digest_sha512,
        patch=ConfigurationPatch(research_developer_mode=ResearchDeveloperMode.ON),
    )

    assert applied.outcome is ConfigurationApplyOutcome.APPLIED
    assert applied.revision == 2
    assert applied.digest_sha512 != before.digest_sha512
    field = next(
        item for item in control.effective().fields if item.key == "research_developer_mode"
    )
    assert field.value == "on"
    assert field.source is ConfigurationSource.RUNTIME_OVERRIDE
    restarted = service().effective()
    assert restarted.revision == 1
    assert (
        next(item for item in restarted.fields if item.key == "research_developer_mode").value
        == "off"
    )


def test_stale_and_duplicate_operations_are_conflicts_without_mutation() -> None:
    control = service()
    initial = control.effective()
    control.apply(
        operation_id="first",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(research_developer_mode=ResearchDeveloperMode.ON),
    )
    applied = control.effective()

    with pytest.raises(ConfigurationControlError) as duplicate:
        control.apply(
            operation_id="first",
            expected_revision=applied.revision,
            expected_digest=applied.digest_sha512,
            patch=ConfigurationPatch(research_developer_mode=ResearchDeveloperMode.OFF),
        )
    assert duplicate.value.code is ConfigurationControlErrorCode.OPERATION_ALREADY_APPLIED
    with pytest.raises(ConfigurationControlError) as stale:
        control.apply(
            operation_id="stale",
            expected_revision=1,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(research_developer_mode=ResearchDeveloperMode.OFF),
        )
    assert stale.value.code is ConfigurationControlErrorCode.CONFLICT
    assert control.effective() == applied


def test_noop_and_mixed_restart_patch_do_not_mutate_or_consume_receipt() -> None:
    control = service()
    initial = control.effective()
    noop = control.apply(
        operation_id="reusable",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(research_developer_mode=ResearchDeveloperMode.OFF),
    )
    assert noop.outcome is ConfigurationApplyOutcome.NO_CHANGE
    restart = control.apply(
        operation_id="reusable",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(
            research_developer_mode=ResearchDeveloperMode.ON,
            context_size=8192,
        ),
    )
    assert restart.outcome is ConfigurationApplyOutcome.RESTART_REQUIRED
    assert control.effective() == initial


@pytest.mark.parametrize("mode", [RecordingControlMode.METADATA, RecordingControlMode.FULL])
def test_recording_modes_and_unknown_hook_projection_are_fail_closed(
    mode: RecordingControlMode,
) -> None:
    control = service()
    before = control.effective()
    with pytest.raises(ConfigurationControlError) as captured:
        control.preview(ConfigurationPatch(recording_mode=mode))
    assert captured.value.code is ConfigurationControlErrorCode.UNSUPPORTED
    assert control.effective() == before

    with pytest.raises(ConfigurationControlError):
        control.apply(
            operation_id="mixed-unsupported",
            expected_revision=before.revision,
            expected_digest=before.digest_sha512,
            patch=ConfigurationPatch(
                research_developer_mode=ResearchDeveloperMode.ON,
                recording_mode=mode,
            ),
        )
    assert control.effective() == before


def test_constructor_rejects_duplicate_fields_and_unknown_components() -> None:
    control = service()
    fields = control.effective().fields
    with pytest.raises(ValueError):
        ConfigurationControlService(
            fields=(*fields, fields[0]),
            feature_hooks=control.effective().feature_hooks,
            recording_hooks=control.effective().recording_hooks,
        )
    with pytest.raises(ValueError):
        ConfigurationControlService(
            fields=fields,
            feature_hooks=(
                FeatureHookDescriptor(
                    component_key="unknown_component",
                    allowed_modes=(DocumentationRagControlMode.DISABLED,),
                    current_mode=DocumentationRagControlMode.DISABLED,
                    available=False,
                ),
            ),
            recording_hooks=control.effective().recording_hooks,
        )


@pytest.mark.parametrize(
    "hook",
    [
        FeatureHookDescriptor(
            component_key="documentation_rag",
            allowed_modes=(DocumentationRagControlMode.DISABLED,),
            current_mode=DocumentationRagControlMode.DISABLED,
            available=True,
        ),
        FeatureHookDescriptor(
            component_key="documentation_rag",
            allowed_modes=(
                DocumentationRagControlMode.DISABLED,
                DocumentationRagControlMode.ENABLED,
            ),
            current_mode=DocumentationRagControlMode.ENABLED,
            available=False,
        ),
        FeatureHookDescriptor(
            component_key="documentation_rag",
            allowed_modes=(
                DocumentationRagControlMode.DISABLED,
                DocumentationRagControlMode.ENABLED,
            ),
            current_mode=DocumentationRagControlMode.DISABLED,
            available=True,
            apply_disposition=ApplyDisposition.READ_ONLY,
        ),
    ],
)
def test_constructor_rejects_inconsistent_rag_descriptors(
    hook: FeatureHookDescriptor,
) -> None:
    with pytest.raises(ValueError, match="feature hook projection"):
        service_with_rag_hook(hook)


@pytest.mark.parametrize("apply", [False, True])
def test_unavailable_rag_mode_change_is_unsupported_and_mutation_zero(apply: bool) -> None:
    control = service_with_rag_hook(
        FeatureHookDescriptor(
            component_key="documentation_rag",
            allowed_modes=(
                DocumentationRagControlMode.DISABLED,
                DocumentationRagControlMode.ENABLED,
            ),
            current_mode=DocumentationRagControlMode.DISABLED,
            available=False,
        )
    )
    before = control.effective()
    patch = ConfigurationPatch(documentation_rag_mode=DocumentationRagControlMode.ENABLED)

    with pytest.raises(ConfigurationControlError) as captured:
        if apply:
            control.apply(
                operation_id="unavailable-rag",
                expected_revision=before.revision,
                expected_digest=before.digest_sha512,
                patch=patch,
            )
        else:
            control.preview(patch)

    assert captured.value.code is ConfigurationControlErrorCode.UNSUPPORTED
    assert control.effective() == before


def test_unavailable_rag_same_mode_remains_noop() -> None:
    control = service_with_rag_hook(
        FeatureHookDescriptor(
            component_key="documentation_rag",
            allowed_modes=(
                DocumentationRagControlMode.DISABLED,
                DocumentationRagControlMode.ENABLED,
            ),
            current_mode=DocumentationRagControlMode.DISABLED,
            available=False,
        )
    )
    before = control.effective()

    preview = control.preview(
        ConfigurationPatch(documentation_rag_mode=DocumentationRagControlMode.DISABLED)
    )

    assert preview.outcome is ConfigurationPreviewOutcome.NO_CHANGE
    assert control.effective() == before


def test_research_mode_does_not_create_authority_or_protected_capabilities() -> None:
    control = service()
    initial = control.effective()
    control.apply(
        operation_id="authority-negative",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(research_developer_mode=ResearchDeveloperMode.ON),
    )
    snapshot = control.effective()
    keys = {item.key for item in snapshot.fields}
    assert keys == {
        "acceleration_api",
        "backend_kind",
        "context_size",
        "device_kind",
        "max_new_tokens",
        "profile_key",
        "research_developer_mode",
        "selected_model",
        "conversation_storage_kind",
        "conversation_storage_version",
    }
    assert not keys & {"authority", "permission", "agent", "tool", "protected_capture"}


# -- P3-CODEX-001: governance_mode is a Typed Field on the existing
# Preview/Apply state machine, sharing Revision/Digest/CAS/Idempotency. --


def test_governance_mode_applies_through_the_shared_apply_transaction() -> None:
    applier = _RecordingGovernanceApplier()
    control = service_with_governance(applier)
    initial = control.effective()

    result = control.apply(
        operation_id="governance-apply-1",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(governance_mode=GovernanceControlMode.OBSERVE),
    )

    assert result.outcome is ConfigurationApplyOutcome.APPLIED
    assert applier.calls == [GovernanceControlMode.OBSERVE]
    assert control.effective().governance_hooks[0].current_mode is GovernanceControlMode.OBSERVE
    assert control.effective().revision == initial.revision + 1


def test_a_failing_governance_applier_leaves_every_field_untouched() -> None:
    control = service_with_governance(_FailingGovernanceApplier())
    initial = control.effective()

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="governance-apply-fail",
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(governance_mode=GovernanceControlMode.OBSERVE),
        )

    assert excinfo.value.code is ConfigurationControlErrorCode.UNSUPPORTED
    assert control.effective() == initial  # one success boundary: nothing committed


def test_a_failing_governance_applier_also_blocks_a_combined_research_mode_change() -> None:
    """A single Patch touching both governance_mode and
    research_developer_mode must commit *both* or *neither* — never a
    partial Mutation where research_developer_mode lands but governance
    does not (P3-CODEX-001/003 one success boundary)."""

    control = service_with_governance(_FailingGovernanceApplier())
    initial = control.effective()

    with pytest.raises(ConfigurationControlError):
        control.apply(
            operation_id="governance-apply-combined",
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(
                governance_mode=GovernanceControlMode.OBSERVE,
                research_developer_mode=ResearchDeveloperMode.ON,
            ),
        )

    snapshot = control.effective()
    assert snapshot == initial
    research_field = next(f for f in snapshot.fields if f.key == "research_developer_mode")
    assert research_field.value == "off"


def test_governance_mode_patch_is_unsupported_when_the_feature_is_not_active() -> None:
    control = service()  # no governance_hooks at all
    initial = control.effective()

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="governance-apply-inactive",
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(governance_mode=GovernanceControlMode.OBSERVE),
        )
    assert excinfo.value.code is ConfigurationControlErrorCode.UNSUPPORTED


def test_governance_control_mode_cannot_represent_enforce_at_all() -> None:
    assert not hasattr(GovernanceControlMode, "ENFORCE")
    assert {mode.value for mode in GovernanceControlMode} == {"off", "observe"}


def test_redundant_governance_mode_request_is_a_true_noop_without_calling_the_applier() -> None:
    applier = _RecordingGovernanceApplier()
    control = service_with_governance(applier, current_mode=GovernanceControlMode.OFF)
    initial = control.effective()

    preview = control.preview(ConfigurationPatch(governance_mode=GovernanceControlMode.OFF))

    assert preview.outcome is ConfigurationPreviewOutcome.NO_CHANGE
    assert applier.calls == []
    assert control.effective() == initial


# -- P4-CODEX-002 Rework: main_governance_mode is a Typed Field on the
# same shared Preview/Apply state machine — unlike Phase 3's
# `governance_mode`, `enforce` *is* representable, gated by the Applier
# raising (never Patch-level exclusion, P4-MOD-005). --

_MAIN_GOVERNANCE_ALLOWED_MODES = (
    MainGovernanceControlMode.OFF,
    MainGovernanceControlMode.OBSERVE,
    MainGovernanceControlMode.ENFORCE,
)


class _RecordingMainGovernanceApplier:
    def __init__(self) -> None:
        self.calls: list[MainGovernanceControlMode] = []

    def apply(self, mode: MainGovernanceControlMode) -> MainGovernanceHookDescriptor:
        self.calls.append(mode)
        return MainGovernanceHookDescriptor(
            component_key="main_governance_mode",
            allowed_modes=_MAIN_GOVERNANCE_ALLOWED_MODES,
            current_mode=mode,
            available=True,
        )


class _FailingMainGovernanceApplier:
    def apply(self, mode: MainGovernanceControlMode) -> MainGovernanceHookDescriptor:
        del mode
        raise RuntimeError("simulated enforce-not-binding-ready failure")


def service_with_main_governance(
    applier: object, *, current_mode: MainGovernanceControlMode = MainGovernanceControlMode.OFF
) -> ConfigurationControlService:
    base = service()
    return ConfigurationControlService(
        fields=base.effective().fields,
        feature_hooks=base.effective().feature_hooks,
        recording_hooks=base.effective().recording_hooks,
        main_governance_hooks=(
            MainGovernanceHookDescriptor(
                component_key="main_governance_mode",
                allowed_modes=_MAIN_GOVERNANCE_ALLOWED_MODES,
                current_mode=current_mode,
                available=True,
            ),
        ),
        main_governance_mode_applier=applier,  # type: ignore[arg-type]
    )


def test_main_governance_mode_applies_through_the_shared_apply_transaction() -> None:
    applier = _RecordingMainGovernanceApplier()
    control = service_with_main_governance(applier)
    initial = control.effective()

    result = control.apply(
        operation_id="main-governance-apply-1",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.OBSERVE),
    )

    assert result.outcome is ConfigurationApplyOutcome.APPLIED
    assert applier.calls == [MainGovernanceControlMode.OBSERVE]
    assert (
        control.effective().main_governance_hooks[0].current_mode
        is MainGovernanceControlMode.OBSERVE
    )
    assert control.effective().revision == initial.revision + 1


def test_main_governance_mode_can_represent_enforce_unlike_phase_3_governance_mode() -> None:
    assert hasattr(MainGovernanceControlMode, "ENFORCE")
    assert {mode.value for mode in MainGovernanceControlMode} == {"off", "observe", "enforce"}

    applier = _RecordingMainGovernanceApplier()
    control = service_with_main_governance(applier)
    initial = control.effective()

    result = control.apply(
        operation_id="main-governance-apply-enforce",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.ENFORCE),
    )
    assert result.outcome is ConfigurationApplyOutcome.APPLIED
    assert applier.calls == [MainGovernanceControlMode.ENFORCE]


def test_a_failing_main_governance_applier_leaves_every_field_untouched() -> None:
    # Simulates requesting `enforce` while the real Composition's Binding
    # is not ready — the Applier raises, and no Field/Hook/Revision here
    # may move, never a silent downgrade to a lower Mode (P4-MOD-005).
    control = service_with_main_governance(_FailingMainGovernanceApplier())
    initial = control.effective()

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="main-governance-apply-fail",
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.ENFORCE),
        )

    assert excinfo.value.code is ConfigurationControlErrorCode.UNSUPPORTED
    assert control.effective() == initial  # one success boundary: nothing committed


def test_main_governance_mode_patch_is_unsupported_when_the_feature_is_not_active() -> None:
    control = service()  # no main_governance_hooks at all
    initial = control.effective()

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="main-governance-apply-inactive",
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.OBSERVE),
        )
    assert excinfo.value.code is ConfigurationControlErrorCode.UNSUPPORTED


def test_redundant_main_governance_mode_request_is_a_true_noop_without_calling_the_applier() -> (
    None
):
    applier = _RecordingMainGovernanceApplier()
    control = service_with_main_governance(applier, current_mode=MainGovernanceControlMode.OFF)
    initial = control.effective()

    preview = control.preview(
        ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.OFF)
    )

    assert preview.outcome is ConfigurationPreviewOutcome.NO_CHANGE
    assert applier.calls == []
    assert control.effective() == initial


def test_stale_revision_and_digest_are_rejected_as_a_conflict_not_applied() -> None:
    applier = _RecordingMainGovernanceApplier()
    control = service_with_main_governance(applier)
    initial = control.effective()

    # A concurrent, unrelated Apply moves the Revision first.
    control.apply(
        operation_id="unrelated-change",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(research_developer_mode=ResearchDeveloperMode.ON),
    )

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="main-governance-apply-stale",
            expected_revision=initial.revision,  # stale on purpose
            expected_digest=initial.digest_sha512,  # stale on purpose
            patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.OBSERVE),
        )
    assert excinfo.value.code is ConfigurationControlErrorCode.CONFLICT
    assert applier.calls == []  # never even reached the Applier


def test_duplicate_operation_id_is_idempotent_not_reapplied() -> None:
    applier = _RecordingMainGovernanceApplier()
    control = service_with_main_governance(applier)
    initial = control.effective()

    first = control.apply(
        operation_id="main-governance-apply-once",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.OBSERVE),
    )
    assert first.outcome is ConfigurationApplyOutcome.APPLIED
    assert applier.calls == [MainGovernanceControlMode.OBSERVE]

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="main-governance-apply-once",  # same operation_id, replayed
            expected_revision=initial.revision,  # even with the stale pre-apply CAS pair
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.OBSERVE),
        )
    assert excinfo.value.code is ConfigurationControlErrorCode.OPERATION_ALREADY_APPLIED
    assert applier.calls == [MainGovernanceControlMode.OBSERVE]  # not called a second time


def test_concurrent_apply_attempts_serialize_exactly_one_winner() -> None:
    applier = _RecordingMainGovernanceApplier()
    control = service_with_main_governance(applier)
    initial = control.effective()
    barrier = threading.Barrier(8)
    outcomes: list[ConfigurationApplyOutcome] = []
    conflicts = 0
    outcomes_lock = threading.Lock()

    def _attempt(index: int) -> None:
        nonlocal conflicts
        barrier.wait(timeout=5)
        try:
            result = control.apply(
                operation_id=f"main-governance-apply-race-{index}",
                expected_revision=initial.revision,
                expected_digest=initial.digest_sha512,
                patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.OBSERVE),
            )
        except ConfigurationControlError as error:
            assert error.code is ConfigurationControlErrorCode.CONFLICT
            with outcomes_lock:
                conflicts += 1
            return
        with outcomes_lock:
            outcomes.append(result.outcome)

    threads = [threading.Thread(target=_attempt, args=(i,)) for i in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=5)

    # Exactly one thread's stale-CAS-pair Apply could win (the Lock
    # serializes Apply calls; only the first observes a matching
    # Revision/Digest) — every other concurrent attempt using the same
    # pre-apply CAS pair must see CONFLICT, never a second silent Apply.
    assert len(outcomes) == 1
    assert outcomes == [ConfigurationApplyOutcome.APPLIED]
    assert conflicts == 7
    assert len(applier.calls) == 1
    assert control.effective().revision == initial.revision + 1


# -- P4-CODEX-010 Rework: a Patch touching two independent External
# Appliers (Phase 3 Governance, Phase 4 Main Governance) has no Atomic
# Prepare/Commit/Rollback contract between them, so it must be rejected
# *before* either Applier is ever called — never a silent sequential
# Partial Apply. --


def service_with_both_governances(
    governance_applier: object,
    main_governance_applier: object,
    *,
    governance_current_mode: GovernanceControlMode = GovernanceControlMode.OFF,
    main_governance_current_mode: MainGovernanceControlMode = MainGovernanceControlMode.OFF,
) -> ConfigurationControlService:
    base = service()
    return ConfigurationControlService(
        fields=base.effective().fields,
        feature_hooks=base.effective().feature_hooks,
        recording_hooks=base.effective().recording_hooks,
        governance_hooks=(
            GovernanceHookDescriptor(
                component_key="governance_mode",
                allowed_modes=_GOVERNANCE_ALLOWED_MODES,
                current_mode=governance_current_mode,
                available=True,
            ),
        ),
        governance_mode_applier=governance_applier,  # type: ignore[arg-type]
        main_governance_hooks=(
            MainGovernanceHookDescriptor(
                component_key="main_governance_mode",
                allowed_modes=_MAIN_GOVERNANCE_ALLOWED_MODES,
                current_mode=main_governance_current_mode,
                available=True,
            ),
        ),
        main_governance_mode_applier=main_governance_applier,  # type: ignore[arg-type]
    )


def test_mixed_governance_patch_is_rejected_before_calling_either_applier() -> None:
    governance_applier = _RecordingGovernanceApplier()
    main_governance_applier = _RecordingMainGovernanceApplier()
    control = service_with_both_governances(governance_applier, main_governance_applier)
    initial = control.effective()

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="mixed-governance-apply",
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(
                governance_mode=GovernanceControlMode.OBSERVE,
                main_governance_mode=MainGovernanceControlMode.OBSERVE,
            ),
        )

    assert excinfo.value.code is ConfigurationControlErrorCode.UNSUPPORTED
    # Neither Applier was ever called — not "called then rolled back",
    # never called at all.
    assert governance_applier.calls == []
    assert main_governance_applier.calls == []
    assert control.effective() == initial


def test_mixed_patch_with_one_true_noop_side_only_calls_the_real_changes_applier() -> None:
    # The Atomicity risk is specifically two Appliers each mutating real
    # External State in one transaction. A Patch field equal to its
    # already-current value never reaches `changed_keys` at all (existing
    # no-op filtering in `_changes()`), so only the genuinely-changing
    # side's Applier is ever called — a single-Applier Apply, not a
    # sequential multi-Applier one, and therefore not the Atomicity risk
    # this Rework's rejection targets.
    governance_applier = _RecordingGovernanceApplier()
    main_governance_applier = _RecordingMainGovernanceApplier()
    control = service_with_both_governances(
        governance_applier,
        main_governance_applier,
        governance_current_mode=GovernanceControlMode.OFF,
    )
    initial = control.effective()

    result = control.apply(
        operation_id="mixed-governance-apply-partial-noop",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(
            governance_mode=GovernanceControlMode.OFF,  # already current -> a true no-op
            main_governance_mode=MainGovernanceControlMode.OBSERVE,
        ),
    )

    assert result.outcome is ConfigurationApplyOutcome.APPLIED
    assert governance_applier.calls == []
    assert main_governance_applier.calls == [MainGovernanceControlMode.OBSERVE]


def test_a_second_applier_failure_never_leaves_the_first_appliers_state_committed() -> None:
    """Simulates what a naive sequential-apply implementation would do:
    even if the rejection above did not exist, a first-Applier-succeeds/
    second-Applier-fails sequence must never leave this Service's own
    Snapshot/Revision/Operation Receipt partially advanced. Exercised
    directly against each Applier in isolation (single-field Patches),
    since the combined-Patch path is now rejected outright above."""

    governance_applier = _RecordingGovernanceApplier()
    failing_main_governance_applier = _FailingMainGovernanceApplier()
    control = service_with_both_governances(governance_applier, failing_main_governance_applier)
    initial = control.effective()

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="second-applier-fails",
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.ENFORCE),
        )
    assert excinfo.value.code is ConfigurationControlErrorCode.UNSUPPORTED
    assert governance_applier.calls == []  # never touched: single-field Patch
    snapshot = control.effective()
    assert snapshot == initial
    assert snapshot.revision == initial.revision
    assert snapshot.digest_sha512 == initial.digest_sha512
    assert snapshot.governance_hooks[0].current_mode is GovernanceControlMode.OFF
    assert snapshot.main_governance_hooks[0].current_mode is MainGovernanceControlMode.OFF


def test_single_field_governance_and_main_governance_applies_still_work_independently() -> None:
    governance_applier = _RecordingGovernanceApplier()
    main_governance_applier = _RecordingMainGovernanceApplier()
    control = service_with_both_governances(governance_applier, main_governance_applier)
    initial = control.effective()

    first = control.apply(
        operation_id="governance-only",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(governance_mode=GovernanceControlMode.OBSERVE),
    )
    assert first.outcome is ConfigurationApplyOutcome.APPLIED
    assert governance_applier.calls == [GovernanceControlMode.OBSERVE]
    assert main_governance_applier.calls == []

    second = control.apply(
        operation_id="main-governance-only",
        expected_revision=first.revision,
        expected_digest=first.digest_sha512,
        patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.OBSERVE),
    )
    assert second.outcome is ConfigurationApplyOutcome.APPLIED
    assert main_governance_applier.calls == [MainGovernanceControlMode.OBSERVE]
    assert control.effective().governance_hooks[0].current_mode is GovernanceControlMode.OBSERVE
    assert (
        control.effective().main_governance_hooks[0].current_mode
        is MainGovernanceControlMode.OBSERVE
    )


# -- P5-F-WU-002: guardrail_governance_mode is a Typed Field on the same
# shared Preview/Apply state machine — mirrors main_governance_mode's own
# Applier-may-raise contract (ADR-5-003, never a silent downgrade). --

_GUARDRAIL_GOVERNANCE_ALLOWED_MODES = (
    GuardrailGovernanceControlMode.OFF,
    GuardrailGovernanceControlMode.OBSERVE,
    GuardrailGovernanceControlMode.ENFORCE,
)


class _RecordingGuardrailGovernanceApplier:
    def __init__(self) -> None:
        self.calls: list[GuardrailGovernanceControlMode] = []

    def apply(self, mode: GuardrailGovernanceControlMode) -> GuardrailGovernanceHookDescriptor:
        self.calls.append(mode)
        return GuardrailGovernanceHookDescriptor(
            component_key="guardrail_governance_mode",
            allowed_modes=_GUARDRAIL_GOVERNANCE_ALLOWED_MODES,
            current_mode=mode,
            available=True,
        )


class _FailingGuardrailGovernanceApplier:
    def apply(self, mode: GuardrailGovernanceControlMode) -> GuardrailGovernanceHookDescriptor:
        del mode
        raise RuntimeError("simulated guardrail pipeline failure")


def service_with_guardrail_governance(
    applier: object,
    *,
    current_mode: GuardrailGovernanceControlMode = GuardrailGovernanceControlMode.OFF,
) -> ConfigurationControlService:
    base = service()
    return ConfigurationControlService(
        fields=base.effective().fields,
        feature_hooks=base.effective().feature_hooks,
        recording_hooks=base.effective().recording_hooks,
        guardrail_governance_hooks=(
            GuardrailGovernanceHookDescriptor(
                component_key="guardrail_governance_mode",
                allowed_modes=_GUARDRAIL_GOVERNANCE_ALLOWED_MODES,
                current_mode=current_mode,
                available=True,
            ),
        ),
        guardrail_governance_mode_applier=applier,  # type: ignore[arg-type]
    )


def test_guardrail_governance_mode_applies_through_the_shared_apply_transaction() -> None:
    applier = _RecordingGuardrailGovernanceApplier()
    control = service_with_guardrail_governance(applier)
    initial = control.effective()

    result = control.apply(
        operation_id="guardrail-governance-apply-1",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(guardrail_governance_mode=GuardrailGovernanceControlMode.OBSERVE),
    )

    assert result.outcome is ConfigurationApplyOutcome.APPLIED
    assert applier.calls == [GuardrailGovernanceControlMode.OBSERVE]
    assert (
        control.effective().guardrail_governance_hooks[0].current_mode
        is GuardrailGovernanceControlMode.OBSERVE
    )
    assert control.effective().revision == initial.revision + 1


def test_guardrail_governance_mode_can_represent_enforce() -> None:
    assert {mode.value for mode in GuardrailGovernanceControlMode} == {
        "off",
        "observe",
        "enforce",
    }

    applier = _RecordingGuardrailGovernanceApplier()
    control = service_with_guardrail_governance(applier)
    initial = control.effective()

    result = control.apply(
        operation_id="guardrail-governance-apply-enforce",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(guardrail_governance_mode=GuardrailGovernanceControlMode.ENFORCE),
    )
    assert result.outcome is ConfigurationApplyOutcome.APPLIED
    assert applier.calls == [GuardrailGovernanceControlMode.ENFORCE]


def test_a_failing_guardrail_governance_applier_leaves_every_field_untouched() -> None:
    control = service_with_guardrail_governance(_FailingGuardrailGovernanceApplier())
    initial = control.effective()

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="guardrail-governance-apply-fail",
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(
                guardrail_governance_mode=GuardrailGovernanceControlMode.ENFORCE
            ),
        )

    assert excinfo.value.code is ConfigurationControlErrorCode.UNSUPPORTED
    assert control.effective() == initial  # one success boundary: nothing committed


def test_guardrail_governance_mode_patch_is_unsupported_when_the_feature_is_not_active() -> None:
    control = service()  # no guardrail_governance_hooks at all
    initial = control.effective()

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="guardrail-governance-inactive",
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(
                guardrail_governance_mode=GuardrailGovernanceControlMode.OBSERVE
            ),
        )

    assert excinfo.value.code is ConfigurationControlErrorCode.UNSUPPORTED
    assert control.effective() == initial


def test_redundant_guardrail_governance_mode_request_is_a_true_noop() -> None:
    applier = _RecordingGuardrailGovernanceApplier()
    control = service_with_guardrail_governance(
        applier, current_mode=GuardrailGovernanceControlMode.OFF
    )
    initial = control.effective()

    result = control.apply(
        operation_id="guardrail-governance-noop",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(guardrail_governance_mode=GuardrailGovernanceControlMode.OFF),
    )

    assert result.outcome is ConfigurationApplyOutcome.NO_CHANGE
    assert applier.calls == []  # a true no-op never reaches the Applier
    assert control.effective() == initial


def service_with_main_and_guardrail_governance(
    main_governance_applier: object,
    guardrail_governance_applier: object,
    *,
    main_governance_current_mode: MainGovernanceControlMode = MainGovernanceControlMode.OFF,
    guardrail_governance_current_mode: (
        GuardrailGovernanceControlMode
    ) = GuardrailGovernanceControlMode.OFF,
) -> ConfigurationControlService:
    base = service()
    return ConfigurationControlService(
        fields=base.effective().fields,
        feature_hooks=base.effective().feature_hooks,
        recording_hooks=base.effective().recording_hooks,
        main_governance_hooks=(
            MainGovernanceHookDescriptor(
                component_key="main_governance_mode",
                allowed_modes=_MAIN_GOVERNANCE_ALLOWED_MODES,
                current_mode=main_governance_current_mode,
                available=True,
            ),
        ),
        main_governance_mode_applier=main_governance_applier,  # type: ignore[arg-type]
        guardrail_governance_hooks=(
            GuardrailGovernanceHookDescriptor(
                component_key="guardrail_governance_mode",
                allowed_modes=_GUARDRAIL_GOVERNANCE_ALLOWED_MODES,
                current_mode=guardrail_governance_current_mode,
                available=True,
            ),
        ),
        guardrail_governance_mode_applier=guardrail_governance_applier,  # type: ignore[arg-type]
    )


def test_mixed_main_and_guardrail_governance_patch_is_rejected_before_calling_either_applier() -> (
    None
):
    # Proves the generalized `_EXTERNAL_APPLIER_KEYS` rejection (extended
    # from P4-CODEX-010's original governance/main_governance-only pair)
    # also covers Phase 5's new Guardrail Applier — not just the original
    # two-Applier case it was first written for.
    main_governance_applier = _RecordingMainGovernanceApplier()
    guardrail_governance_applier = _RecordingGuardrailGovernanceApplier()
    control = service_with_main_and_guardrail_governance(
        main_governance_applier, guardrail_governance_applier
    )
    initial = control.effective()

    with pytest.raises(ConfigurationControlError) as excinfo:
        control.apply(
            operation_id="mixed-main-and-guardrail-governance-apply",
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            patch=ConfigurationPatch(
                main_governance_mode=MainGovernanceControlMode.OBSERVE,
                guardrail_governance_mode=GuardrailGovernanceControlMode.OBSERVE,
            ),
        )

    assert excinfo.value.code is ConfigurationControlErrorCode.UNSUPPORTED
    assert main_governance_applier.calls == []
    assert guardrail_governance_applier.calls == []
    assert control.effective() == initial


def test_single_field_main_and_guardrail_governance_applies_still_work_independently() -> None:
    main_governance_applier = _RecordingMainGovernanceApplier()
    guardrail_governance_applier = _RecordingGuardrailGovernanceApplier()
    control = service_with_main_and_guardrail_governance(
        main_governance_applier, guardrail_governance_applier
    )
    initial = control.effective()

    first = control.apply(
        operation_id="main-governance-only-2",
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        patch=ConfigurationPatch(main_governance_mode=MainGovernanceControlMode.OBSERVE),
    )
    assert first.outcome is ConfigurationApplyOutcome.APPLIED
    assert main_governance_applier.calls == [MainGovernanceControlMode.OBSERVE]
    assert guardrail_governance_applier.calls == []

    second = control.apply(
        operation_id="guardrail-governance-only-2",
        expected_revision=first.revision,
        expected_digest=first.digest_sha512,
        patch=ConfigurationPatch(guardrail_governance_mode=GuardrailGovernanceControlMode.ENFORCE),
    )
    assert second.outcome is ConfigurationApplyOutcome.APPLIED
    assert guardrail_governance_applier.calls == [GuardrailGovernanceControlMode.ENFORCE]
    assert (
        control.effective().main_governance_hooks[0].current_mode
        is MainGovernanceControlMode.OBSERVE
    )
    assert (
        control.effective().guardrail_governance_hooks[0].current_mode
        is GuardrailGovernanceControlMode.ENFORCE
    )
