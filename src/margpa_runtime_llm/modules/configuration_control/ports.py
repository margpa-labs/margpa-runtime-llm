"""Replaceable typed descriptor ports for configuration control."""

from typing import Protocol, runtime_checkable

from .contracts import (
    FeatureHookDescriptor,
    GovernanceControlMode,
    GovernanceHookDescriptor,
    GuardrailGovernanceControlMode,
    GuardrailGovernanceHookDescriptor,
    MainGovernanceControlMode,
    MainGovernanceHookDescriptor,
    RecordingHookDescriptor,
)


@runtime_checkable
class FeatureHookDescriptorPort(Protocol):
    def descriptor(self) -> FeatureHookDescriptor: ...


@runtime_checkable
class RecordingHookDescriptorPort(Protocol):
    def descriptor(self) -> RecordingHookDescriptor: ...


@runtime_checkable
class GovernanceModeApplierPort(Protocol):
    """Bridges Configuration Control's Apply transaction to the real
    Governance Mode state machine, without this module depending on the
    governance_definitions module's concrete types (P3-CODEX-001).

    `apply()` may raise any exception on failure — `ConfigurationControlService`
    translates it into a Typed `ConfigurationControlError` and leaves its
    own committed state untouched (mirrors `GovernanceDefinitionsRuntime.
    apply_mode`'s own build-before-commit contract, P3-CODEX-003)."""

    def apply(self, mode: GovernanceControlMode) -> GovernanceHookDescriptor: ...


@runtime_checkable
class MainGovernanceModeApplierPort(Protocol):
    """Bridges Configuration Control's Apply transaction to the real
    Phase 4 `MainGovernanceModeController`, without this module depending
    on `runtime_governance`'s concrete types (P4-CODEX-002 Rework, mirrors
    `GovernanceModeApplierPort`).

    `apply()` may raise (e.g. `enforce` requested while not Binding-ready)
    — `ConfigurationControlService.apply()` translates it into a Typed
    `ConfigurationControlError` and leaves its own committed state
    untouched, never a silent downgrade to a lower Mode (P4-MOD-005)."""

    def apply(self, mode: MainGovernanceControlMode) -> MainGovernanceHookDescriptor: ...


@runtime_checkable
class GuardrailGovernanceModeApplierPort(Protocol):
    """Bridges Configuration Control's Apply transaction to the real
    Phase 5 `GuardrailModeController`, without this module depending on
    `guardrail_governance`'s concrete types (P5-F-WU-002, mirrors
    `MainGovernanceModeApplierPort`).

    `apply()` may raise — `ConfigurationControlService.apply()` translates
    it into a Typed `ConfigurationControlError` and leaves its own
    committed state untouched, never a silent downgrade to a lower Mode."""

    def apply(self, mode: GuardrailGovernanceControlMode) -> GuardrailGovernanceHookDescriptor: ...
