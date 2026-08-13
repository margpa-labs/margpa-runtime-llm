"""Safe optional composition for local process configuration control."""

from __future__ import annotations

from margpa_runtime_llm.modules.configuration_control import (
    ApplyDisposition,
    ConfigurationControlService,
    ConfigurationField,
    ConfigurationSource,
    DocumentationRagControlMode,
    FeatureHookDescriptor,
    RecordingControlMode,
    RecordingHookDescriptor,
    ResearchDeveloperMode,
)
from margpa_runtime_llm.web.access_profiles import DocumentationRagEffectiveState

from .config_loader import EffectivePhase1Config


def build_configuration_control(
    *,
    effective: EffectivePhase1Config,
    documentation_rag_state: DocumentationRagEffectiveState,
) -> ConfigurationControlService:
    """Project the finite safe startup allowlist into a process-local service."""

    sources = effective.field_sources
    fields = (
        ConfigurationField(
            key="selected_model",
            value=effective.selected_model,
            source=sources.selected_model,
            apply_disposition=ApplyDisposition.RESTART_REQUIRED,
        ),
        ConfigurationField(
            key="profile_key",
            value=effective.profile_key,
            source=sources.profile_key,
            apply_disposition=ApplyDisposition.READ_ONLY,
        ),
        ConfigurationField(
            key="context_size",
            value=effective.load.context_size,
            source=sources.context_size,
            apply_disposition=ApplyDisposition.RESTART_REQUIRED,
        ),
        ConfigurationField(
            key="backend_kind",
            value=effective.backend_runtime.build_variant_key,
            source=sources.backend_kind,
            apply_disposition=ApplyDisposition.READ_ONLY,
        ),
        ConfigurationField(
            key="device_kind",
            value=effective.compute.compute_kind_key,
            source=sources.device_kind,
            apply_disposition=ApplyDisposition.READ_ONLY,
        ),
        ConfigurationField(
            key="acceleration_api",
            value=effective.compute.acceleration_api_key,
            source=sources.acceleration_api,
            apply_disposition=ApplyDisposition.READ_ONLY,
        ),
        ConfigurationField(
            key="max_new_tokens",
            value=effective.generation.max_new_tokens,
            source=sources.max_new_tokens,
            apply_disposition=ApplyDisposition.READ_ONLY,
        ),
        ConfigurationField(
            key="research_developer_mode",
            value=ResearchDeveloperMode.OFF.value,
            source=ConfigurationSource.BUILT_IN_DEFAULT,
            apply_disposition=ApplyDisposition.RUNTIME_APPLICABLE,
        ),
    )
    rag_enabled = documentation_rag_state is DocumentationRagEffectiveState.ENABLED
    rag_available = documentation_rag_state in {
        DocumentationRagEffectiveState.DISABLED,
        DocumentationRagEffectiveState.ENABLED,
    }
    feature_hooks = (
        FeatureHookDescriptor(
            component_key="documentation_rag",
            allowed_modes=(
                DocumentationRagControlMode.DISABLED,
                DocumentationRagControlMode.ENABLED,
            ),
            current_mode=(
                DocumentationRagControlMode.ENABLED
                if rag_enabled
                else DocumentationRagControlMode.DISABLED
            ),
            available=rag_available,
        ),
    )
    recording_hooks = (
        RecordingHookDescriptor(
            component_key="conversation_recording",
            allowed_modes=(RecordingControlMode.OFF,),
            current_mode=RecordingControlMode.OFF,
            available=False,
        ),
    )
    return ConfigurationControlService(
        fields=fields,
        feature_hooks=feature_hooks,
        recording_hooks=recording_hooks,
    )
