"""Bounded HTTP contracts for local configuration control."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from margpa_runtime_llm.modules.configuration_control import (
    ConfigurationApplyResult,
    ConfigurationPatch,
    ConfigurationPreview,
    DocumentationRagControlMode,
    EffectiveConfigurationSnapshot,
    RecordingControlMode,
    RedactedConfigurationChange,
    ResearchDeveloperMode,
)

CONTROL_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
DIGEST_PATTERN = r"^[0-9a-f]{128}$"


class _ConfigurationContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class ConfigurationPatchRequest(_ConfigurationContract):
    research_developer_mode: ResearchDeveloperMode | None = None
    selected_model: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$",
    )
    context_size: int | None = Field(default=None, strict=True, ge=1, le=1_048_576)
    documentation_rag_mode: DocumentationRagControlMode | None = None
    recording_mode: RecordingControlMode | None = None

    @model_validator(mode="after")
    def require_one_field(self) -> ConfigurationPatchRequest:
        if not self.model_fields_set:
            raise ValueError("configuration patch must not be empty")
        return self

    def to_domain(self) -> ConfigurationPatch:
        return ConfigurationPatch(
            research_developer_mode=self.research_developer_mode,
            selected_model=self.selected_model,
            context_size=self.context_size,
            documentation_rag_mode=self.documentation_rag_mode,
            recording_mode=self.recording_mode,
        )


class ConfigurationPreviewRequest(_ConfigurationContract):
    patch: ConfigurationPatchRequest


class ConfigurationApplyRequest(_ConfigurationContract):
    operation_id: str = Field(min_length=1, max_length=128, pattern=CONTROL_ID_PATTERN)
    expected_revision: int = Field(strict=True, ge=1)
    expected_digest: str = Field(pattern=DIGEST_PATTERN)
    patch: ConfigurationPatchRequest


class ConfigurationRuntimeResponse(_ConfigurationContract):
    enabled: Literal[True] = True
    schema_version: Literal["1"] = "1"
    non_persistent: Literal[True] = True
    live_fields: tuple[Literal["research_developer_mode"], ...] = ("research_developer_mode",)


class ConfigurationFieldResponse(_ConfigurationContract):
    key: str
    value: str | int | bool
    source: str
    apply_disposition: str


class FeatureHookResponse(_ConfigurationContract):
    component_key: str
    allowed_modes: tuple[str, ...]
    current_mode: str
    available: bool
    apply_disposition: str


class RecordingHookResponse(FeatureHookResponse):
    pass


class EffectiveConfigurationResponse(_ConfigurationContract):
    schema_version: Literal["1"]
    revision: int
    digest_sha512: str
    fields: tuple[ConfigurationFieldResponse, ...]
    feature_hooks: tuple[FeatureHookResponse, ...]
    recording_hooks: tuple[RecordingHookResponse, ...]


class ConfigurationChangeResponse(_ConfigurationContract):
    key: str
    before: str | int | bool
    after: str | int | bool
    source: str
    apply_disposition: str
    restart_reason: str | None = None


class ConfigurationPreviewResponse(_ConfigurationContract):
    outcome: str
    base_revision: int
    base_digest: str
    redacted_changes: tuple[ConfigurationChangeResponse, ...]
    restart_fields: tuple[str, ...]


class ConfigurationApplyResponse(_ConfigurationContract):
    outcome: str
    revision: int
    digest_sha512: str
    redacted_changes: tuple[ConfigurationChangeResponse, ...]
    restart_fields: tuple[str, ...]


def project_effective(
    value: EffectiveConfigurationSnapshot,
) -> EffectiveConfigurationResponse:
    return EffectiveConfigurationResponse(
        schema_version="1",
        revision=value.revision,
        digest_sha512=value.digest_sha512,
        fields=tuple(
            ConfigurationFieldResponse(
                key=item.key,
                value=item.value,
                source=item.source.value,
                apply_disposition=item.apply_disposition.value,
            )
            for item in value.fields
        ),
        feature_hooks=tuple(
            FeatureHookResponse(
                component_key=item.component_key,
                allowed_modes=tuple(mode.value for mode in item.allowed_modes),
                current_mode=item.current_mode.value,
                available=item.available,
                apply_disposition=item.apply_disposition.value,
            )
            for item in value.feature_hooks
        ),
        recording_hooks=tuple(
            RecordingHookResponse(
                component_key=item.component_key,
                allowed_modes=tuple(mode.value for mode in item.allowed_modes),
                current_mode=item.current_mode.value,
                available=item.available,
                apply_disposition=item.apply_disposition.value,
            )
            for item in value.recording_hooks
        ),
    )


def project_preview(value: ConfigurationPreview) -> ConfigurationPreviewResponse:
    return ConfigurationPreviewResponse(
        outcome=value.outcome.value,
        base_revision=value.base_revision,
        base_digest=value.base_digest,
        redacted_changes=_project_changes(value.redacted_changes),
        restart_fields=value.restart_fields,
    )


def project_apply(value: ConfigurationApplyResult) -> ConfigurationApplyResponse:
    return ConfigurationApplyResponse(
        outcome=value.outcome.value,
        revision=value.revision,
        digest_sha512=value.digest_sha512,
        redacted_changes=_project_changes(value.redacted_changes),
        restart_fields=value.restart_fields,
    )


def _project_changes(
    values: tuple[RedactedConfigurationChange, ...],
) -> tuple[ConfigurationChangeResponse, ...]:
    return tuple(
        ConfigurationChangeResponse(
            key=item.key,
            before=item.before,
            after=item.after,
            source=item.source.value,
            apply_disposition=item.apply_disposition.value,
            restart_reason=item.restart_reason,
        )
        for item in values
    )
