"""Typed, framework-independent contracts for process-local configuration control."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import StrEnum


class ConfigurationSource(StrEnum):
    BUILT_IN_DEFAULT = "built_in_default"
    APPLICATION = "application"
    DEPLOYMENT_PROFILE = "deployment_profile"
    ENVIRONMENT = "environment"
    EXPLICIT_CLI = "explicit_cli"
    RUNTIME_OVERRIDE = "runtime_override"
    COMPOSED_RUNTIME = "composed_runtime"


class ApplyDisposition(StrEnum):
    RUNTIME_APPLICABLE = "runtime_applicable"
    RESTART_REQUIRED = "restart_required"
    UNSUPPORTED = "unsupported"
    READ_ONLY = "read_only"


class ResearchDeveloperMode(StrEnum):
    OFF = "off"
    ON = "on"


class DocumentationRagControlMode(StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"


class RecordingControlMode(StrEnum):
    OFF = "off"
    METADATA = "metadata"
    FULL = "full"


class ConfigurationPreviewOutcome(StrEnum):
    READY = "ready"
    NO_CHANGE = "no_change"
    RESTART_REQUIRED = "restart_required"


class ConfigurationApplyOutcome(StrEnum):
    APPLIED = "applied"
    NO_CHANGE = "no_change"
    RESTART_REQUIRED = "restart_required"


class ConfigurationControlErrorCode(StrEnum):
    CONFLICT = "configuration_conflict"
    OPERATION_ALREADY_APPLIED = "operation_already_applied"
    INVALID_PATCH = "invalid_configuration_patch"
    UNSUPPORTED = "unsupported_configuration"


type SafeConfigurationValue = str | int | bool
SAFE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


@dataclass(frozen=True, slots=True)
class ConfigurationControlError(Exception):
    code: ConfigurationControlErrorCode
    safe_message: str
    current_revision: int | None = None
    current_digest: str | None = None


@dataclass(frozen=True, slots=True)
class EffectiveConfigFieldSources:
    """Exact source trace for the finite safe projection allowlist."""

    selected_model: ConfigurationSource = ConfigurationSource.APPLICATION
    profile_key: ConfigurationSource = ConfigurationSource.COMPOSED_RUNTIME
    context_size: ConfigurationSource = ConfigurationSource.APPLICATION
    backend_kind: ConfigurationSource = ConfigurationSource.DEPLOYMENT_PROFILE
    device_kind: ConfigurationSource = ConfigurationSource.DEPLOYMENT_PROFILE
    acceleration_api: ConfigurationSource = ConfigurationSource.DEPLOYMENT_PROFILE
    max_new_tokens: ConfigurationSource = ConfigurationSource.APPLICATION


@dataclass(frozen=True, slots=True)
class ConfigurationField:
    key: str
    value: SafeConfigurationValue
    source: ConfigurationSource
    apply_disposition: ApplyDisposition


@dataclass(frozen=True, slots=True)
class FeatureHookDescriptor:
    component_key: str
    allowed_modes: tuple[DocumentationRagControlMode, ...]
    current_mode: DocumentationRagControlMode
    available: bool
    apply_disposition: ApplyDisposition = ApplyDisposition.RESTART_REQUIRED


@dataclass(frozen=True, slots=True)
class RecordingHookDescriptor:
    component_key: str
    allowed_modes: tuple[RecordingControlMode, ...]
    current_mode: RecordingControlMode
    available: bool
    apply_disposition: ApplyDisposition = ApplyDisposition.READ_ONLY


@dataclass(frozen=True, slots=True)
class ConfigurationPatch:
    research_developer_mode: ResearchDeveloperMode | None = None
    selected_model: str | None = None
    context_size: int | None = None
    documentation_rag_mode: DocumentationRagControlMode | None = None
    recording_mode: RecordingControlMode | None = None

    def __post_init__(self) -> None:
        if self.research_developer_mode is not None and not isinstance(
            self.research_developer_mode, ResearchDeveloperMode
        ):
            raise ValueError("research developer mode is invalid")
        if self.selected_model is not None and not isinstance(self.selected_model, str):
            raise ValueError("selected model is invalid")
        if self.context_size is not None and type(self.context_size) is not int:
            raise ValueError("context size is invalid")
        if self.documentation_rag_mode is not None and not isinstance(
            self.documentation_rag_mode, DocumentationRagControlMode
        ):
            raise ValueError("documentation RAG mode is invalid")
        if self.recording_mode is not None and not isinstance(
            self.recording_mode, RecordingControlMode
        ):
            raise ValueError("recording mode is invalid")
        if all(
            value is None
            for value in (
                self.research_developer_mode,
                self.selected_model,
                self.context_size,
                self.documentation_rag_mode,
                self.recording_mode,
            )
        ):
            raise ValueError("configuration patch must contain at least one field")
        if self.selected_model is not None and not SAFE_IDENTIFIER_PATTERN.fullmatch(
            self.selected_model
        ):
            raise ValueError("selected model is invalid")
        if self.context_size is not None and not 1 <= self.context_size <= 1_048_576:
            raise ValueError("context size is invalid")


@dataclass(frozen=True, slots=True)
class RedactedConfigurationChange:
    key: str
    before: SafeConfigurationValue
    after: SafeConfigurationValue
    source: ConfigurationSource
    apply_disposition: ApplyDisposition
    restart_reason: str | None = None


@dataclass(frozen=True, slots=True)
class EffectiveConfigurationSnapshot:
    schema_version: str
    revision: int
    digest_sha512: str
    fields: tuple[ConfigurationField, ...]
    feature_hooks: tuple[FeatureHookDescriptor, ...]
    recording_hooks: tuple[RecordingHookDescriptor, ...]


@dataclass(frozen=True, slots=True)
class ConfigurationPreview:
    outcome: ConfigurationPreviewOutcome
    base_revision: int
    base_digest: str
    redacted_changes: tuple[RedactedConfigurationChange, ...]
    restart_fields: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ConfigurationApplyResult:
    outcome: ConfigurationApplyOutcome
    revision: int
    digest_sha512: str
    redacted_changes: tuple[RedactedConfigurationChange, ...]
    restart_fields: tuple[str, ...] = ()


def configuration_digest(
    *,
    fields: tuple[ConfigurationField, ...],
    feature_hooks: tuple[FeatureHookDescriptor, ...],
    recording_hooks: tuple[RecordingHookDescriptor, ...],
) -> str:
    """Hash only the finite safe effective projection using canonical JSON."""

    payload = {
        "schema_version": "1",
        "fields": [
            {
                "key": item.key,
                "value": item.value,
                "source": item.source.value,
                "apply_disposition": item.apply_disposition.value,
            }
            for item in sorted(fields, key=lambda item: item.key)
        ],
        "feature_hooks": [
            {
                "component_key": item.component_key,
                "allowed_modes": sorted(mode.value for mode in item.allowed_modes),
                "current_mode": item.current_mode.value,
                "available": item.available,
                "apply_disposition": item.apply_disposition.value,
            }
            for item in sorted(feature_hooks, key=lambda item: item.component_key)
        ],
        "recording_hooks": [
            {
                "component_key": item.component_key,
                "allowed_modes": sorted(mode.value for mode in item.allowed_modes),
                "current_mode": item.current_mode.value,
                "available": item.available,
                "apply_disposition": item.apply_disposition.value,
            }
            for item in sorted(recording_hooks, key=lambda item: item.component_key)
        ],
    }
    canonical = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()
