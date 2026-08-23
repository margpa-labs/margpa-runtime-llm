"""Safe optional composition for local process configuration control."""

from __future__ import annotations

from margpa_runtime_llm.modules.configuration_control import (
    ApplyDisposition,
    ConfigurationControlService,
    ConfigurationField,
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
from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode
from margpa_runtime_llm.modules.governance_definitions.runtime import (
    GovernanceDefinitionsRuntime,
)
from margpa_runtime_llm.web.access_profiles import DocumentationRagEffectiveState

from .config_loader import EffectivePhase1Config
from .guardrail_governance import GuardrailGovernanceComposition
from .runtime_governance import RuntimeGovernanceComposition

_GOVERNANCE_ALLOWED_MODES = (GovernanceControlMode.OFF, GovernanceControlMode.OBSERVE)
_MAIN_GOVERNANCE_ALLOWED_MODES = (
    MainGovernanceControlMode.OFF,
    MainGovernanceControlMode.OBSERVE,
    MainGovernanceControlMode.ENFORCE,
)
_GUARDRAIL_GOVERNANCE_ALLOWED_MODES = (
    GuardrailGovernanceControlMode.OFF,
    GuardrailGovernanceControlMode.OBSERVE,
    GuardrailGovernanceControlMode.ENFORCE,
)


class _GovernanceModeApplierAdapter:
    """Bridges Configuration Control's `GovernanceModeApplierPort` to a
    real `GovernanceDefinitionsRuntime` (P3-CODEX-001). Any failure from
    `apply_mode()` — rejected `enforce`, or a Typed Observe pipeline
    failure — propagates as-is; `ConfigurationControlService.apply()` is
    the layer that catches and translates it into a Safe Failure."""

    def __init__(self, runtime: GovernanceDefinitionsRuntime) -> None:
        self._runtime = runtime

    def apply(self, mode: GovernanceControlMode) -> GovernanceHookDescriptor:
        snapshot = self._runtime.apply_mode(GovernanceMode(mode.value))
        return GovernanceHookDescriptor(
            component_key="governance_mode",
            allowed_modes=_GOVERNANCE_ALLOWED_MODES,
            current_mode=GovernanceControlMode(snapshot.current_mode.value),
            available=True,
        )


class _MainGovernanceModeApplierAdapter:
    """Bridges Configuration Control's `MainGovernanceModeApplierPort` to
    a real `RuntimeGovernanceComposition.mode_controller` (P4-CODEX-002
    Rework, mirrors `_GovernanceModeApplierAdapter`). Any failure from
    `apply_mode()` — rejected `enforce` while not Binding-ready —
    propagates as-is; `ConfigurationControlService.apply()` is the layer
    that catches and translates it into a Safe Failure. This Adapter is
    the *only* caller of `apply_mode()` this Composition Root wires —
    no separate direct-Apply route exists alongside it."""

    def __init__(self, composition: RuntimeGovernanceComposition) -> None:
        self._composition = composition

    def apply(self, mode: MainGovernanceControlMode) -> MainGovernanceHookDescriptor:
        snapshot = self._composition.mode_controller.apply_mode(GovernanceMode(mode.value))
        return MainGovernanceHookDescriptor(
            component_key="main_governance_mode",
            allowed_modes=_MAIN_GOVERNANCE_ALLOWED_MODES,
            current_mode=MainGovernanceControlMode(snapshot.current_mode.value),
            available=True,
        )


class _GuardrailGovernanceModeApplierAdapter:
    """Bridges Configuration Control's `GuardrailGovernanceModeApplierPort`
    to a real `GuardrailGovernanceComposition.mode_controller` (P5-F-WU-002,
    mirrors `_MainGovernanceModeApplierAdapter`). Any failure from
    `apply_mode()` propagates as-is; `ConfigurationControlService.apply()`
    is the layer that catches and translates it into a Safe Failure. This
    Adapter is the *only* caller of `apply_mode()` this Composition Root
    wires — no separate direct-Apply route exists alongside it."""

    def __init__(self, composition: GuardrailGovernanceComposition) -> None:
        self._composition = composition

    def apply(self, mode: GuardrailGovernanceControlMode) -> GuardrailGovernanceHookDescriptor:
        snapshot = self._composition.mode_controller.apply_mode(GovernanceMode(mode.value))
        return GuardrailGovernanceHookDescriptor(
            component_key="guardrail_governance_mode",
            allowed_modes=_GUARDRAIL_GOVERNANCE_ALLOWED_MODES,
            current_mode=GuardrailGovernanceControlMode(snapshot.current_mode.value),
            available=True,
        )


def build_configuration_control(
    *,
    effective: EffectivePhase1Config,
    documentation_rag_state: DocumentationRagEffectiveState,
    conversation_persistence_enabled: bool = False,
    conversation_storage_backend: str | None = None,
    conversation_storage_backend_version: str | None = None,
    governance_definitions_runtime: GovernanceDefinitionsRuntime | None = None,
    runtime_governance_composition: RuntimeGovernanceComposition | None = None,
    guardrail_governance_composition: GuardrailGovernanceComposition | None = None,
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
        ConfigurationField(
            key="conversation_storage_kind",
            value=(
                conversation_storage_backend
                if conversation_persistence_enabled and conversation_storage_backend is not None
                else "disabled"
            ),
            source=ConfigurationSource.COMPOSED_RUNTIME,
            apply_disposition=ApplyDisposition.READ_ONLY,
        ),
        ConfigurationField(
            key="conversation_storage_version",
            value=(
                conversation_storage_backend_version
                if conversation_persistence_enabled
                and conversation_storage_backend_version is not None
                else "disabled"
            ),
            source=ConfigurationSource.COMPOSED_RUNTIME,
            apply_disposition=ApplyDisposition.READ_ONLY,
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
    governance_hooks: tuple[GovernanceHookDescriptor, ...] = ()
    governance_mode_applier = None
    if governance_definitions_runtime is not None:
        governance_hooks = (
            GovernanceHookDescriptor(
                component_key="governance_mode",
                allowed_modes=_GOVERNANCE_ALLOWED_MODES,
                current_mode=GovernanceControlMode(
                    governance_definitions_runtime.mode_snapshot().current_mode.value
                ),
                available=True,
            ),
        )
        governance_mode_applier = _GovernanceModeApplierAdapter(governance_definitions_runtime)
    main_governance_hooks: tuple[MainGovernanceHookDescriptor, ...] = ()
    main_governance_mode_applier = None
    if runtime_governance_composition is not None:
        main_governance_hooks = (
            MainGovernanceHookDescriptor(
                component_key="main_governance_mode",
                allowed_modes=_MAIN_GOVERNANCE_ALLOWED_MODES,
                current_mode=MainGovernanceControlMode(
                    runtime_governance_composition.mode_controller.current_mode_value()
                ),
                available=True,
            ),
        )
        main_governance_mode_applier = _MainGovernanceModeApplierAdapter(
            runtime_governance_composition
        )
    guardrail_governance_hooks: tuple[GuardrailGovernanceHookDescriptor, ...] = ()
    guardrail_governance_mode_applier = None
    if guardrail_governance_composition is not None:
        guardrail_governance_hooks = (
            GuardrailGovernanceHookDescriptor(
                component_key="guardrail_governance_mode",
                allowed_modes=_GUARDRAIL_GOVERNANCE_ALLOWED_MODES,
                current_mode=GuardrailGovernanceControlMode(
                    guardrail_governance_composition.mode_controller.current_mode_value()
                ),
                available=True,
            ),
        )
        guardrail_governance_mode_applier = _GuardrailGovernanceModeApplierAdapter(
            guardrail_governance_composition
        )
    return ConfigurationControlService(
        fields=fields,
        feature_hooks=feature_hooks,
        recording_hooks=recording_hooks,
        governance_hooks=governance_hooks,
        governance_mode_applier=governance_mode_applier,
        main_governance_hooks=main_governance_hooks,
        main_governance_mode_applier=main_governance_mode_applier,
        guardrail_governance_hooks=guardrail_governance_hooks,
        guardrail_governance_mode_applier=guardrail_governance_mode_applier,
    )
