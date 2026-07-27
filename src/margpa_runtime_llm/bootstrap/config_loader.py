"""Load typed Phase 1 configuration inputs and compose effective configuration."""

from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract
from margpa_runtime_llm.modules.inference.contracts.generation import GenerationParameters
from margpa_runtime_llm.modules.inference.contracts.response import (
    ResolvedResponseLanguagePolicy,
    ResponseLanguage,
    ResponsePolicyConfig,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    BackendRuntimeDefinition,
    ComputeTargetDefinition,
    DeploymentRequirements,
    DeploymentVerificationState,
    HostPlatformDefinition,
    ModelLoadConfig,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    PresentationConfig,
    ResolvedThinkingPresentationPolicy,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig
from margpa_runtime_llm.orchestration.response_language import resolve_response_policy
from margpa_runtime_llm.orchestration.thinking_presentation import (
    resolve_thinking_presentation_policy,
)

GENERATION_ENVIRONMENT_FIELDS = {
    "MARGPA_MAX_NEW_TOKENS": "max_new_tokens",
    "MARGPA_TEMPERATURE": "temperature",
    "MARGPA_TOP_P": "top_p",
    "MARGPA_TOP_K": "top_k",
    "MARGPA_MIN_P": "min_p",
    "MARGPA_PRESENCE_PENALTY": "presence_penalty",
    "MARGPA_FREQUENCY_PENALTY": "frequency_penalty",
    "MARGPA_REPEAT_PENALTY": "repeat_penalty",
    "MARGPA_THINKING_MODE": "thinking_mode",
}

LOAD_ENVIRONMENT_FIELDS = {
    "MARGPA_CONTEXT_SIZE": "context_size",
}


class ModelRootConfig(ImmutableContract):
    default: Path = Path("./models")
    environment_variable: str = Field(
        default="MARGPA_MODEL_ROOT",
        pattern=r"^[A-Z][A-Z0-9_]*$",
    )

    @field_validator("default")
    @classmethod
    def reject_user_absolute_path(cls, value: Path) -> Path:
        if value.is_absolute() or ".." in value.parts:
            raise ValueError("tracked model root must be a safe relative path")
        return value


class ApplicationLoadDefaults(ImmutableContract):
    context_size: int = Field(default=4096, gt=0)
    verbose_backend: bool = False
    verify_artifact_hash: Literal[True] = True


class DeploymentLoadOverrides(ImmutableContract):
    context_size: int | None = Field(default=None, gt=0)
    batch_size: int | None = Field(default=None, gt=0)
    micro_batch_size: int | None = Field(default=None, gt=0)
    threads: int | None = Field(default=None, gt=0)
    threads_batch: int | None = Field(default=None, gt=0)
    gpu_layers: int | None = None
    use_mmap: bool | None = None
    use_mlock: bool | None = None


class ApplicationLayers(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    summarization: SummarizationConfig


class ApplicationConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["3"] = "3"
    application_key: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    selected_model: str
    model_root: ModelRootConfig = ModelRootConfig()
    load_defaults: ApplicationLoadDefaults = ApplicationLoadDefaults()
    generation: GenerationParameters = GenerationParameters()
    response: ResponsePolicyConfig = ResponsePolicyConfig()
    presentation: PresentationConfig
    layers: ApplicationLayers


class DeploymentProfile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["3"] = "3"
    profile_key: str
    verification_state: DeploymentVerificationState
    host: HostPlatformDefinition
    compute: ComputeTargetDefinition
    backend_runtime: BackendRuntimeDefinition
    runtime_requirements: DeploymentRequirements
    load_overrides: DeploymentLoadOverrides = DeploymentLoadOverrides()


class EffectivePhase1Config(ImmutableContract):
    application_schema_version: Literal["3"]
    application_key: str
    profile_key: str
    selected_model: str
    verification_state: DeploymentVerificationState
    host: HostPlatformDefinition
    compute: ComputeTargetDefinition
    backend_runtime: BackendRuntimeDefinition
    runtime_requirements: DeploymentRequirements
    model_root: Path
    load: ModelLoadConfig
    generation: GenerationParameters
    response: ResolvedResponseLanguagePolicy
    presentation: ResolvedThinkingPresentationPolicy
    summarization: SummarizationConfig
    profile_resolution_source: Literal["explicit", "environment", "platform_default"]
    applied_sources: tuple[str, ...] = Field(default_factory=tuple)


def load_application_config(path: Path) -> ApplicationConfig:
    try:
        with path.open("rb") as config_file:
            return ApplicationConfig.model_validate(tomllib.load(config_file))
    except FileNotFoundError as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The application configuration was not found.",
            details={"exception_type": type(exc).__name__},
        ) from exc
    except (OSError, tomllib.TOMLDecodeError, ValidationError) as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The application configuration is invalid.",
            details={"exception_type": type(exc).__name__},
        ) from exc


def load_deployment_profile(path: Path) -> DeploymentProfile:
    try:
        with path.open("rb") as profile_file:
            return DeploymentProfile.model_validate(tomllib.load(profile_file))
    except FileNotFoundError as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The deployment profile was not found.",
            details={"exception_type": type(exc).__name__},
        ) from exc
    except (OSError, tomllib.TOMLDecodeError, ValidationError) as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The deployment profile is invalid.",
            details={"exception_type": type(exc).__name__},
        ) from exc


def resolve_effective_config(
    application: ApplicationConfig,
    profile: DeploymentProfile,
    *,
    project_root: Path,
    environment: Mapping[str, str] | None = None,
    cli_model_root: Path | None = None,
    cli_model_key: str | None = None,
    generation_overrides: Mapping[str, object] | None = None,
    load_overrides: Mapping[str, object] | None = None,
    response_language: ResponseLanguage | str | None = None,
    thinking_visibility: ThinkingVisibility | str | None = None,
    thinking_label: str | None = None,
    profile_resolution_source: Literal["explicit", "environment", "platform_default"] = "explicit",
) -> EffectivePhase1Config:
    """Apply profile, environment, and explicit CLI values in ascending precedence."""

    current_environment = os.environ if environment is None else environment
    applied_sources = ["built_in_defaults", "application", "deployment_profile"]

    model_root_value = Path(
        current_environment.get(
            application.model_root.environment_variable,
            application.model_root.default,
        )
    )
    selected_model = current_environment.get("MARGPA_MODEL_KEY", application.selected_model)

    environment_applied = False
    if (
        any(variable in current_environment for variable in GENERATION_ENVIRONMENT_FIELDS)
        or any(variable in current_environment for variable in LOAD_ENVIRONMENT_FIELDS)
        or application.model_root.environment_variable in current_environment
        or "MARGPA_MODEL_KEY" in current_environment
        or "MARGPA_PROFILE" in current_environment
        or "MARGPA_RESPONSE_LANGUAGE" in current_environment
        or "MARGPA_THINKING_VISIBILITY" in current_environment
        or "MARGPA_THINKING_LABEL" in current_environment
    ):
        environment_applied = True
    if environment_applied:
        applied_sources.append("environment")

    explicit_override = False
    if cli_model_root is not None:
        model_root_value = cli_model_root
        explicit_override = True
    if cli_model_key is not None:
        selected_model = cli_model_key
        explicit_override = True
    if (
        generation_overrides
        or load_overrides
        or response_language is not None
        or thinking_visibility is not None
        or thinking_label is not None
    ):
        explicit_override = True
    if explicit_override:
        applied_sources.append("cli_override")

    try:
        resolved_root = (
            (
                model_root_value
                if model_root_value.is_absolute()
                else project_root / model_root_value
            )
            .expanduser()
            .resolve()
        )
        load = resolve_load_config(
            application_defaults=application.load_defaults,
            deployment_overrides=profile.load_overrides,
            environment=current_environment,
            explicit_overrides=load_overrides,
        )
        generation = resolve_generation_config(
            application_defaults=application.generation,
            environment=current_environment,
            explicit_overrides=generation_overrides,
        )
        response = resolve_response_policy(
            application_policy=application.response,
            environment=current_environment,
            explicit_language=response_language,
        )
        presentation = resolve_thinking_presentation_policy(
            application_policy=application.presentation.thinking,
            environment=current_environment,
            explicit_visibility=thinking_visibility,
            explicit_display_label=thinking_label,
        )
        return EffectivePhase1Config(
            application_schema_version=application.schema_version,
            application_key=application.application_key,
            profile_key=profile.profile_key,
            selected_model=selected_model,
            verification_state=profile.verification_state,
            host=profile.host,
            compute=profile.compute,
            backend_runtime=profile.backend_runtime,
            runtime_requirements=profile.runtime_requirements,
            model_root=resolved_root,
            load=load,
            generation=generation,
            response=response,
            presentation=presentation,
            summarization=application.layers.summarization,
            profile_resolution_source=profile_resolution_source,
            applied_sources=tuple(applied_sources),
        )
    except ValidationError as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The effective runtime configuration is invalid.",
            details={"exception_type": type(exc).__name__},
        ) from exc


def resolve_load_config(
    *,
    application_defaults: ApplicationLoadDefaults,
    deployment_overrides: DeploymentLoadOverrides,
    environment: Mapping[str, str],
    explicit_overrides: Mapping[str, object] | None,
) -> ModelLoadConfig:
    data = ModelLoadConfig().model_dump()
    data.update(
        {
            "context_size": application_defaults.context_size,
            "verbose_backend": application_defaults.verbose_backend,
            "verify_artifact_hash": application_defaults.verify_artifact_hash,
        }
    )
    deployment_data = deployment_overrides.model_dump(exclude_none=True)
    deployment_data.pop("schema_version", None)
    data.update(deployment_data)
    for variable, field_name in LOAD_ENVIRONMENT_FIELDS.items():
        if variable in environment:
            data[field_name] = environment[variable]
    if explicit_overrides:
        data.update(explicit_overrides)
    return ModelLoadConfig.model_validate(data)


def resolve_generation_config(
    *,
    application_defaults: GenerationParameters,
    environment: Mapping[str, str],
    explicit_overrides: Mapping[str, object] | None,
) -> GenerationParameters:
    data = GenerationParameters().model_dump()
    data.update(application_defaults.model_dump())
    for variable, field_name in GENERATION_ENVIRONMENT_FIELDS.items():
        if variable in environment:
            data[field_name] = environment[variable]
    if explicit_overrides:
        data.update(explicit_overrides)
    return GenerationParameters.model_validate(data)
