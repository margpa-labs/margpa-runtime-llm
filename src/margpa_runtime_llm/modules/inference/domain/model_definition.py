"""Validated model registry definition."""

import unicodedata
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from ..contracts.base import ImmutableContract
from .capabilities import CapabilityFeature

SHA512_PATTERN = r"^[0-9a-f]{128}$"


class ModelSourceDefinition(ImmutableContract):
    provider: str
    distribution_repository: str
    upstream_model: str
    revision: str | None = None


class ModelArtifactDefinition(ImmutableContract):
    relative_path: Path
    file_name: str
    format: str
    quantization: str
    size_bytes: int = Field(gt=0)
    sha512: str = Field(pattern=SHA512_PATTERN)

    @field_validator("relative_path")
    @classmethod
    def validate_relative_path(cls, value: Path) -> Path:
        if value.is_absolute() or ".." in value.parts:
            raise ValueError("artifact path must be a safe relative path")
        return value

    @model_validator(mode="after")
    def validate_file_name(self) -> "ModelArtifactDefinition":
        if self.relative_path.name != self.file_name:
            raise ValueError("artifact file_name must match relative_path")
        return self


class ModelBackendDefinition(ImmutableContract):
    backend_key: str
    required_version: str


class ModelMetadataDefinition(ImmutableContract):
    architecture: str
    native_context_limit: int = Field(gt=0)
    chat_template_source: str


class ModelExpectedCapabilities(ImmutableContract):
    required_features: frozenset[CapabilityFeature]
    optional_features: frozenset[CapabilityFeature] = frozenset()


class ModelVerificationDefinition(ImmutableContract):
    state: str
    provenance_complete: bool


class ThinkingOutputProtocolDefinition(ImmutableContract):
    parser_key: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]*$")
    opening_delimiter: str | None = None
    closing_delimiter: str | None = None

    @field_validator("opening_delimiter", "closing_delimiter")
    @classmethod
    def validate_delimiter(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value:
            raise ValueError("output protocol delimiter must not be empty")
        if any(unicodedata.category(character).startswith("C") for character in value):
            raise ValueError("output protocol delimiter contains a control character")
        return value

    @model_validator(mode="after")
    def validate_protocol_shape(self) -> "ThinkingOutputProtocolDefinition":
        if self.parser_key == "plain_text_v1":
            if self.opening_delimiter is not None or self.closing_delimiter is not None:
                raise ValueError("plain text output protocol must not declare delimiters")
        elif self.parser_key == "tagged_thinking_v1":
            if self.opening_delimiter is None or self.closing_delimiter is None:
                raise ValueError("tagged thinking output protocol requires both delimiters")
            if self.opening_delimiter == self.closing_delimiter:
                raise ValueError("thinking output protocol delimiters must be distinct")
        return self


class ModelOutputProtocolDefinition(ImmutableContract):
    thinking: ThinkingOutputProtocolDefinition


class ModelDefinition(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["2"] = "2"
    model_key: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9._-]+$")
    logical_role: str
    enabled: bool
    source: ModelSourceDefinition
    artifact: ModelArtifactDefinition
    backend: ModelBackendDefinition
    model: ModelMetadataDefinition
    capabilities: ModelExpectedCapabilities
    verification: ModelVerificationDefinition
    output_protocol: ModelOutputProtocolDefinition
    definition_file_sha512: str = Field(pattern=SHA512_PATTERN)
