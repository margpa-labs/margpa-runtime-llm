"""Process-local configuration-control state machine tests."""

from __future__ import annotations

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
