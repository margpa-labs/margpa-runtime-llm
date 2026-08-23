"""Process-local, non-persistent configuration control service."""

from __future__ import annotations

import re
import threading
from dataclasses import replace

from .contracts import (
    ApplyDisposition,
    ConfigurationApplyOutcome,
    ConfigurationApplyResult,
    ConfigurationControlError,
    ConfigurationControlErrorCode,
    ConfigurationField,
    ConfigurationPatch,
    ConfigurationPreview,
    ConfigurationPreviewOutcome,
    ConfigurationSource,
    DocumentationRagControlMode,
    EffectiveConfigurationSnapshot,
    FeatureHookDescriptor,
    GovernanceControlMode,
    GovernanceHookDescriptor,
    GuardrailGovernanceControlMode,
    GuardrailGovernanceHookDescriptor,
    MainGovernanceControlMode,
    MainGovernanceHookDescriptor,
    RecordingControlMode,
    RecordingHookDescriptor,
    RedactedConfigurationChange,
    SafeConfigurationValue,
    configuration_digest,
)
from .ports import (
    GovernanceModeApplierPort,
    GuardrailGovernanceModeApplierPort,
    MainGovernanceModeApplierPort,
)

_EXTERNAL_APPLIER_KEYS = frozenset(
    {"governance_mode", "main_governance_mode", "guardrail_governance_mode"}
)


class ConfigurationControlService:
    """Own only live process state; never stage or persist restart proposals."""

    def __init__(
        self,
        *,
        fields: tuple[ConfigurationField, ...],
        feature_hooks: tuple[FeatureHookDescriptor, ...],
        recording_hooks: tuple[RecordingHookDescriptor, ...],
        governance_hooks: tuple[GovernanceHookDescriptor, ...] = (),
        governance_mode_applier: GovernanceModeApplierPort | None = None,
        main_governance_hooks: tuple[MainGovernanceHookDescriptor, ...] = (),
        main_governance_mode_applier: MainGovernanceModeApplierPort | None = None,
        guardrail_governance_hooks: tuple[GuardrailGovernanceHookDescriptor, ...] = (),
        guardrail_governance_mode_applier: GuardrailGovernanceModeApplierPort | None = None,
    ) -> None:
        self._lock = threading.Lock()
        self._fields = self._validated_fields(fields)
        self._feature_hooks = self._validated_feature_hooks(feature_hooks)
        self._recording_hooks = self._validated_recording_hooks(recording_hooks)
        self._governance_hooks = self._validated_governance_hooks(governance_hooks)
        self._governance_mode_applier = governance_mode_applier
        self._main_governance_hooks = self._validated_main_governance_hooks(main_governance_hooks)
        self._main_governance_mode_applier = main_governance_mode_applier
        self._guardrail_governance_hooks = self._validated_guardrail_governance_hooks(
            guardrail_governance_hooks
        )
        self._guardrail_governance_mode_applier = guardrail_governance_mode_applier
        self._revision = 1
        self._applied_operations: set[str] = set()

    def runtime(self) -> dict[str, object]:
        return {
            "enabled": True,
            "schema_version": "1",
            "non_persistent": True,
            "live_fields": ("research_developer_mode",),
        }

    def effective(self) -> EffectiveConfigurationSnapshot:
        with self._lock:
            return self._snapshot()

    def preview(self, patch: ConfigurationPatch) -> ConfigurationPreview:
        with self._lock:
            snapshot = self._snapshot()
            changes = self._changes(patch)
            restart_fields = tuple(
                item.key
                for item in changes
                if item.apply_disposition is ApplyDisposition.RESTART_REQUIRED
            )
            outcome = (
                ConfigurationPreviewOutcome.NO_CHANGE
                if not changes
                else (
                    ConfigurationPreviewOutcome.RESTART_REQUIRED
                    if restart_fields
                    else ConfigurationPreviewOutcome.READY
                )
            )
            return ConfigurationPreview(
                outcome=outcome,
                base_revision=snapshot.revision,
                base_digest=snapshot.digest_sha512,
                redacted_changes=changes,
                restart_fields=restart_fields,
            )

    def apply(
        self,
        *,
        operation_id: str,
        expected_revision: int,
        expected_digest: str,
        patch: ConfigurationPatch,
    ) -> ConfigurationApplyResult:
        if re.fullmatch(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$", operation_id) is None:
            raise self._invalid()
        with self._lock:
            snapshot = self._snapshot()
            if operation_id in self._applied_operations:
                raise ConfigurationControlError(
                    code=ConfigurationControlErrorCode.OPERATION_ALREADY_APPLIED,
                    safe_message="The configuration operation was already applied.",
                    current_revision=snapshot.revision,
                    current_digest=snapshot.digest_sha512,
                )
            if expected_revision != snapshot.revision or expected_digest != snapshot.digest_sha512:
                raise ConfigurationControlError(
                    code=ConfigurationControlErrorCode.CONFLICT,
                    safe_message="The effective configuration changed. Reload it before applying.",
                    current_revision=snapshot.revision,
                    current_digest=snapshot.digest_sha512,
                )
            changes = self._changes(patch)
            if not changes:
                return ConfigurationApplyResult(
                    outcome=ConfigurationApplyOutcome.NO_CHANGE,
                    revision=snapshot.revision,
                    digest_sha512=snapshot.digest_sha512,
                    redacted_changes=(),
                )
            restart_fields = tuple(
                item.key
                for item in changes
                if item.apply_disposition is ApplyDisposition.RESTART_REQUIRED
            )
            if restart_fields:
                return ConfigurationApplyResult(
                    outcome=ConfigurationApplyOutcome.RESTART_REQUIRED,
                    revision=snapshot.revision,
                    digest_sha512=snapshot.digest_sha512,
                    redacted_changes=changes,
                    restart_fields=restart_fields,
                )
            if any(
                item.apply_disposition is not ApplyDisposition.RUNTIME_APPLICABLE
                for item in changes
            ):
                raise self._unsupported()
            changed_keys = {item.key for item in changes}
            if not changed_keys & ({"research_developer_mode"} | _EXTERNAL_APPLIER_KEYS):
                raise self._invalid()
            # P4-CODEX-009: independent External Appliers (Phase 3
            # Governance, Phase 4 Main Governance, Phase 5 Guardrail
            # Governance) cannot be Committed as one Atomic transaction —
            # there is no Prepare/Commit/Rollback contract between them.
            # Rather than risk a Partial Apply (one Applier's external
            # State already mutated, another Applier fails, and this
            # Service's own Snapshot/Revision stays at the old value while
            # a real Mode elsewhere has already moved), a Patch touching
            # more than one External Applier is rejected before any of
            # them is ever called — the documented Phase 4 MVP minimal
            # safe choice (Required Correction option 2), extended
            # unchanged to Phase 5's own External Applier.
            if len(changed_keys & _EXTERNAL_APPLIER_KEYS) > 1:
                raise ConfigurationControlError(
                    code=ConfigurationControlErrorCode.UNSUPPORTED,
                    safe_message=(
                        "Only one governance-family mode may be changed in the same operation."
                    ),
                )

            # Governance is applied first, and only committed to local
            # state together with every other RUNTIME_APPLICABLE change
            # once it has *already* succeeded — a failure here must leave
            # `self._fields`/`self._governance_hooks`/`self._revision`
            # completely untouched (P3-CODEX-001/003 one success boundary).
            new_governance_hooks = self._governance_hooks
            if "governance_mode" in changed_keys:
                applier = self._governance_mode_applier
                if applier is None:
                    raise self._unsupported()
                assert patch.governance_mode is not None
                try:
                    new_descriptor = applier.apply(patch.governance_mode)
                except Exception as error:
                    raise ConfigurationControlError(
                        code=ConfigurationControlErrorCode.UNSUPPORTED,
                        safe_message="The requested governance mode could not be applied.",
                    ) from error
                new_governance_hooks = (new_descriptor,)

            # Same build-before-commit contract as Governance above
            # (P4-CODEX-002 Rework) — Phase 4 Main Governance Mode's
            # *only* Mutation path is this Apply transaction; no separate
            # direct-Apply route may exist alongside it (no dual-writer,
            # no stale cache between this hook and the live Mode state).
            new_main_governance_hooks = self._main_governance_hooks
            if "main_governance_mode" in changed_keys:
                main_applier = self._main_governance_mode_applier
                if main_applier is None:
                    raise self._unsupported()
                assert patch.main_governance_mode is not None
                try:
                    new_main_descriptor = main_applier.apply(patch.main_governance_mode)
                except Exception as error:
                    raise ConfigurationControlError(
                        code=ConfigurationControlErrorCode.UNSUPPORTED,
                        safe_message=("The requested main governance mode could not be applied."),
                    ) from error
                new_main_governance_hooks = (new_main_descriptor,)

            # Same build-before-commit contract as Governance/Main
            # Governance above (P5-F-WU-002, mirrors P4-CODEX-002
            # Rework) — Phase 5 Guardrail Governance Mode's *only*
            # Mutation path is this Apply transaction.
            new_guardrail_governance_hooks = self._guardrail_governance_hooks
            if "guardrail_governance_mode" in changed_keys:
                guardrail_applier = self._guardrail_governance_mode_applier
                if guardrail_applier is None:
                    raise self._unsupported()
                assert patch.guardrail_governance_mode is not None
                try:
                    new_guardrail_descriptor = guardrail_applier.apply(
                        patch.guardrail_governance_mode
                    )
                except Exception as error:
                    raise ConfigurationControlError(
                        code=ConfigurationControlErrorCode.UNSUPPORTED,
                        safe_message=(
                            "The requested guardrail governance mode could not be applied."
                        ),
                    ) from error
                new_guardrail_governance_hooks = (new_guardrail_descriptor,)

            new_fields = self._fields
            if "research_developer_mode" in changed_keys:
                mode = patch.research_developer_mode
                assert mode is not None
                new_fields = tuple(
                    replace(
                        item,
                        value=mode.value,
                        source=ConfigurationSource.RUNTIME_OVERRIDE,
                    )
                    if item.key == "research_developer_mode"
                    else item
                    for item in self._fields
                )

            self._fields = new_fields
            self._governance_hooks = new_governance_hooks
            self._main_governance_hooks = new_main_governance_hooks
            self._guardrail_governance_hooks = new_guardrail_governance_hooks
            self._revision += 1
            self._applied_operations.add(operation_id)
            applied = self._snapshot()
            return ConfigurationApplyResult(
                outcome=ConfigurationApplyOutcome.APPLIED,
                revision=applied.revision,
                digest_sha512=applied.digest_sha512,
                redacted_changes=changes,
            )

    def _snapshot(self) -> EffectiveConfigurationSnapshot:
        return EffectiveConfigurationSnapshot(
            schema_version="1",
            revision=self._revision,
            digest_sha512=configuration_digest(
                fields=self._fields,
                feature_hooks=self._feature_hooks,
                recording_hooks=self._recording_hooks,
                governance_hooks=self._governance_hooks,
                main_governance_hooks=self._main_governance_hooks,
                guardrail_governance_hooks=self._guardrail_governance_hooks,
            ),
            fields=self._fields,
            feature_hooks=self._feature_hooks,
            recording_hooks=self._recording_hooks,
            governance_hooks=self._governance_hooks,
            main_governance_hooks=self._main_governance_hooks,
            guardrail_governance_hooks=self._guardrail_governance_hooks,
        )

    def _changes(
        self,
        patch: ConfigurationPatch,
    ) -> tuple[RedactedConfigurationChange, ...]:
        current_fields = {item.key: item for item in self._fields}
        candidates: list[tuple[str, SafeConfigurationValue | None]] = [
            (
                "research_developer_mode",
                (
                    patch.research_developer_mode.value
                    if patch.research_developer_mode is not None
                    else None
                ),
            ),
            ("selected_model", patch.selected_model),
            ("context_size", patch.context_size),
        ]
        changes: list[RedactedConfigurationChange] = []
        for key, after in candidates:
            if after is None:
                continue
            field = current_fields[key]
            if field.value == after:
                continue
            changes.append(
                RedactedConfigurationChange(
                    key=key,
                    before=field.value,
                    after=after,
                    source=field.source,
                    apply_disposition=field.apply_disposition,
                    restart_reason=(
                        "Trusted startup input change and process restart are required."
                        if field.apply_disposition is ApplyDisposition.RESTART_REQUIRED
                        else None
                    ),
                )
            )
        if patch.documentation_rag_mode is not None:
            descriptor = self._feature_hooks[0]
            if patch.documentation_rag_mode not in descriptor.allowed_modes:
                raise self._unsupported()
            if patch.documentation_rag_mode is not descriptor.current_mode:
                if not descriptor.available:
                    raise self._unsupported()
                changes.append(
                    RedactedConfigurationChange(
                        key="documentation_rag_mode",
                        before=descriptor.current_mode.value,
                        after=patch.documentation_rag_mode.value,
                        source=ConfigurationSource.COMPOSED_RUNTIME,
                        apply_disposition=descriptor.apply_disposition,
                        restart_reason=(
                            "Trusted startup input change and process restart are required."
                        ),
                    )
                )
        if patch.recording_mode is not None:
            recording_descriptor = self._recording_hooks[0]
            if patch.recording_mode is not RecordingControlMode.OFF:
                raise self._unsupported()
            if patch.recording_mode not in recording_descriptor.allowed_modes:
                raise self._unsupported()
        if patch.governance_mode is not None:
            if not self._governance_hooks:
                raise self._unsupported()
            governance_descriptor = self._governance_hooks[0]
            if patch.governance_mode not in governance_descriptor.allowed_modes:
                raise self._unsupported()
            if patch.governance_mode is not governance_descriptor.current_mode:
                if not governance_descriptor.available:
                    raise self._unsupported()
                changes.append(
                    RedactedConfigurationChange(
                        key="governance_mode",
                        before=governance_descriptor.current_mode.value,
                        after=patch.governance_mode.value,
                        source=ConfigurationSource.COMPOSED_RUNTIME,
                        apply_disposition=governance_descriptor.apply_disposition,
                    )
                )
        if patch.main_governance_mode is not None:
            if not self._main_governance_hooks:
                raise self._unsupported()
            main_governance_descriptor = self._main_governance_hooks[0]
            if patch.main_governance_mode not in main_governance_descriptor.allowed_modes:
                raise self._unsupported()
            if patch.main_governance_mode is not main_governance_descriptor.current_mode:
                if not main_governance_descriptor.available:
                    raise self._unsupported()
                changes.append(
                    RedactedConfigurationChange(
                        key="main_governance_mode",
                        before=main_governance_descriptor.current_mode.value,
                        after=patch.main_governance_mode.value,
                        source=ConfigurationSource.COMPOSED_RUNTIME,
                        apply_disposition=main_governance_descriptor.apply_disposition,
                    )
                )
        if patch.guardrail_governance_mode is not None:
            if not self._guardrail_governance_hooks:
                raise self._unsupported()
            guardrail_governance_descriptor = self._guardrail_governance_hooks[0]
            if patch.guardrail_governance_mode not in guardrail_governance_descriptor.allowed_modes:
                raise self._unsupported()
            if patch.guardrail_governance_mode is not guardrail_governance_descriptor.current_mode:
                if not guardrail_governance_descriptor.available:
                    raise self._unsupported()
                changes.append(
                    RedactedConfigurationChange(
                        key="guardrail_governance_mode",
                        before=guardrail_governance_descriptor.current_mode.value,
                        after=patch.guardrail_governance_mode.value,
                        source=ConfigurationSource.COMPOSED_RUNTIME,
                        apply_disposition=guardrail_governance_descriptor.apply_disposition,
                    )
                )
        return tuple(changes)

    @staticmethod
    def _validated_fields(
        fields: tuple[ConfigurationField, ...],
    ) -> tuple[ConfigurationField, ...]:
        expected = {
            "selected_model",
            "profile_key",
            "context_size",
            "backend_kind",
            "device_kind",
            "acceleration_api",
            "max_new_tokens",
            "research_developer_mode",
            "conversation_storage_kind",
            "conversation_storage_version",
        }
        keys = [item.key for item in fields]
        if set(keys) != expected or len(keys) != len(set(keys)):
            raise ValueError("configuration field projection is invalid")
        by_key = {item.key: item for item in fields}
        expected_dispositions = {
            "selected_model": ApplyDisposition.RESTART_REQUIRED,
            "profile_key": ApplyDisposition.READ_ONLY,
            "context_size": ApplyDisposition.RESTART_REQUIRED,
            "backend_kind": ApplyDisposition.READ_ONLY,
            "device_kind": ApplyDisposition.READ_ONLY,
            "acceleration_api": ApplyDisposition.READ_ONLY,
            "max_new_tokens": ApplyDisposition.READ_ONLY,
            "research_developer_mode": ApplyDisposition.RUNTIME_APPLICABLE,
            "conversation_storage_kind": ApplyDisposition.READ_ONLY,
            "conversation_storage_version": ApplyDisposition.READ_ONLY,
        }
        if any(
            by_key[key].apply_disposition is not disposition
            for key, disposition in expected_dispositions.items()
        ):
            raise ValueError("configuration field disposition is invalid")
        if (
            not isinstance(by_key["selected_model"].value, str)
            or not isinstance(by_key["profile_key"].value, str)
            or not isinstance(by_key["backend_kind"].value, str)
            or not isinstance(by_key["device_kind"].value, str)
            or not isinstance(by_key["acceleration_api"].value, str)
            or type(by_key["context_size"].value) is not int
            or type(by_key["max_new_tokens"].value) is not int
            or by_key["research_developer_mode"].value not in {"off", "on"}
            or not isinstance(by_key["conversation_storage_kind"].value, str)
            or not isinstance(by_key["conversation_storage_version"].value, str)
        ):
            raise ValueError("configuration field value is invalid")
        for key in (
            "selected_model",
            "profile_key",
            "backend_kind",
            "device_kind",
            "acceleration_api",
            "conversation_storage_kind",
            "conversation_storage_version",
        ):
            value = by_key[key].value
            if (
                not isinstance(value, str)
                or re.fullmatch(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$", value) is None
            ):
                raise ValueError("configuration field identifier is invalid")
        return tuple(sorted(fields, key=lambda item: item.key))

    @staticmethod
    def _validated_feature_hooks(
        hooks: tuple[FeatureHookDescriptor, ...],
    ) -> tuple[FeatureHookDescriptor, ...]:
        if len(hooks) != 1:
            raise ValueError("feature hook projection is invalid")
        descriptor = hooks[0]
        if (
            descriptor.component_key != "documentation_rag"
            or descriptor.allowed_modes
            != (
                DocumentationRagControlMode.DISABLED,
                DocumentationRagControlMode.ENABLED,
            )
            or descriptor.current_mode not in descriptor.allowed_modes
            or descriptor.apply_disposition is not ApplyDisposition.RESTART_REQUIRED
            or (
                descriptor.current_mode is DocumentationRagControlMode.ENABLED
                and not descriptor.available
            )
        ):
            raise ValueError("feature hook projection is invalid")
        return hooks

    @staticmethod
    def _validated_recording_hooks(
        hooks: tuple[RecordingHookDescriptor, ...],
    ) -> tuple[RecordingHookDescriptor, ...]:
        if (
            len(hooks) != 1
            or hooks[0].component_key != "conversation_recording"
            or hooks[0].current_mode is not RecordingControlMode.OFF
            or hooks[0].allowed_modes != (RecordingControlMode.OFF,)
        ):
            raise ValueError("recording hook projection is invalid")
        return hooks

    @staticmethod
    def _validated_governance_hooks(
        hooks: tuple[GovernanceHookDescriptor, ...],
    ) -> tuple[GovernanceHookDescriptor, ...]:
        # Unlike documentation_rag/recording (always exactly 1 entry),
        # governance is an optional Phase 3 feature: 0 entries means it is
        # not active at all in this process, not a malformed projection.
        if not hooks:
            return hooks
        if len(hooks) != 1:
            raise ValueError("governance hook projection is invalid")
        descriptor = hooks[0]
        if (
            descriptor.component_key != "governance_mode"
            or descriptor.allowed_modes
            != (
                GovernanceControlMode.OFF,
                GovernanceControlMode.OBSERVE,
            )
            or descriptor.current_mode not in descriptor.allowed_modes
            or descriptor.apply_disposition is not ApplyDisposition.RUNTIME_APPLICABLE
        ):
            raise ValueError("governance hook projection is invalid")
        return hooks

    @staticmethod
    def _validated_main_governance_hooks(
        hooks: tuple[MainGovernanceHookDescriptor, ...],
    ) -> tuple[MainGovernanceHookDescriptor, ...]:
        # Like Phase 3 Governance, Phase 4 Main Governance is an optional
        # feature: 0 entries means it is not active in this process at
        # all, not a malformed projection.
        if not hooks:
            return hooks
        if len(hooks) != 1:
            raise ValueError("main governance hook projection is invalid")
        descriptor = hooks[0]
        if (
            descriptor.component_key != "main_governance_mode"
            or descriptor.allowed_modes
            != (
                MainGovernanceControlMode.OFF,
                MainGovernanceControlMode.OBSERVE,
                MainGovernanceControlMode.ENFORCE,
            )
            or descriptor.current_mode not in descriptor.allowed_modes
            or descriptor.apply_disposition is not ApplyDisposition.RUNTIME_APPLICABLE
        ):
            raise ValueError("main governance hook projection is invalid")
        return hooks

    @staticmethod
    def _validated_guardrail_governance_hooks(
        hooks: tuple[GuardrailGovernanceHookDescriptor, ...],
    ) -> tuple[GuardrailGovernanceHookDescriptor, ...]:
        # Like Phase 3/4 Governance, Phase 5 Guardrail Governance is an
        # optional feature: 0 entries means it is not active in this
        # process at all, not a malformed projection.
        if not hooks:
            return hooks
        if len(hooks) != 1:
            raise ValueError("guardrail governance hook projection is invalid")
        descriptor = hooks[0]
        if (
            descriptor.component_key != "guardrail_governance_mode"
            or descriptor.allowed_modes
            != (
                GuardrailGovernanceControlMode.OFF,
                GuardrailGovernanceControlMode.OBSERVE,
                GuardrailGovernanceControlMode.ENFORCE,
            )
            or descriptor.current_mode not in descriptor.allowed_modes
            or descriptor.apply_disposition is not ApplyDisposition.RUNTIME_APPLICABLE
        ):
            raise ValueError("guardrail governance hook projection is invalid")
        return hooks

    @staticmethod
    def _invalid() -> ConfigurationControlError:
        return ConfigurationControlError(
            code=ConfigurationControlErrorCode.INVALID_PATCH,
            safe_message="The configuration patch is invalid.",
        )

    @staticmethod
    def _unsupported() -> ConfigurationControlError:
        return ConfigurationControlError(
            code=ConfigurationControlErrorCode.UNSUPPORTED,
            safe_message="The requested configuration is unsupported.",
        )
