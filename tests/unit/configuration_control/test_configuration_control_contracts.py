"""Configuration-control contract and canonical digest tests."""

from dataclasses import replace

import pytest

from margpa_runtime_llm.modules.configuration_control import (
    ApplyDisposition,
    ConfigurationField,
    ConfigurationPatch,
    ConfigurationSource,
    DocumentationRagControlMode,
    FeatureHookDescriptor,
    RecordingControlMode,
    RecordingHookDescriptor,
    configuration_digest,
)


def test_patch_requires_a_known_typed_field_and_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        ConfigurationPatch()
    with pytest.raises(ValueError):
        ConfigurationPatch(selected_model=" ")
    with pytest.raises(ValueError):
        ConfigurationPatch(context_size=0)
    with pytest.raises(ValueError):
        ConfigurationPatch(context_size=True)
    with pytest.raises(ValueError):
        ConfigurationPatch(research_developer_mode="on")  # type: ignore[arg-type]


def test_safe_projection_digest_is_order_independent_stable_and_sensitive() -> None:
    fields = (
        ConfigurationField(
            key="selected_model",
            value="main.model",
            source=ConfigurationSource.APPLICATION,
            apply_disposition=ApplyDisposition.RESTART_REQUIRED,
        ),
        ConfigurationField(
            key="research_developer_mode",
            value="off",
            source=ConfigurationSource.BUILT_IN_DEFAULT,
            apply_disposition=ApplyDisposition.RUNTIME_APPLICABLE,
        ),
    )
    feature = (
        FeatureHookDescriptor(
            component_key="documentation_rag",
            allowed_modes=(
                DocumentationRagControlMode.DISABLED,
                DocumentationRagControlMode.ENABLED,
            ),
            current_mode=DocumentationRagControlMode.DISABLED,
            available=False,
        ),
    )
    recording = (
        RecordingHookDescriptor(
            component_key="conversation_recording",
            allowed_modes=(RecordingControlMode.OFF,),
            current_mode=RecordingControlMode.OFF,
            available=False,
        ),
    )

    first = configuration_digest(
        fields=fields,
        feature_hooks=feature,
        recording_hooks=recording,
    )
    reordered = configuration_digest(
        fields=tuple(reversed(fields)),
        feature_hooks=feature,
        recording_hooks=recording,
    )
    changed = configuration_digest(
        fields=(fields[0], replace(fields[1], value="on")),
        feature_hooks=feature,
        recording_hooks=recording,
    )

    assert len(first) == 128
    assert first == reordered
    assert first != changed


def test_hook_contracts_are_component_specific_and_do_not_expose_generic_maps() -> None:
    rag = FeatureHookDescriptor(
        component_key="documentation_rag",
        allowed_modes=(
            DocumentationRagControlMode.DISABLED,
            DocumentationRagControlMode.ENABLED,
        ),
        current_mode=DocumentationRagControlMode.DISABLED,
        available=False,
    )
    recording = RecordingHookDescriptor(
        component_key="conversation_recording",
        allowed_modes=(RecordingControlMode.OFF,),
        current_mode=RecordingControlMode.OFF,
        available=False,
    )

    assert tuple(mode.value for mode in rag.allowed_modes) == ("disabled", "enabled")
    assert tuple(mode.value for mode in recording.allowed_modes) == ("off",)
    assert not hasattr(rag, "metadata")
    assert not hasattr(recording, "protected_capture")
