"""Deployment profile resolution, platform normalization, and runtime validation."""

from __future__ import annotations

import os
import platform
import tomllib
from collections.abc import Callable, Hashable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    BackendRuntimeDefinition,
    ComputeTargetDefinition,
    DeploymentRequirements,
    DetectedRuntimeState,
    FallbackPolicy,
    HostPlatformDefinition,
    ModelRuntimeInfo,
    RuntimeObservation,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelBackendDefinition

type ProfileResolutionSource = Literal["explicit", "environment", "platform_default"]


@dataclass(frozen=True, slots=True)
class ProfileResolution:
    path: Path
    source: ProfileResolutionSource
    detected_host: HostPlatformDefinition


class PlatformAliasDefinition(ImmutableContract):
    raw_value: str = Field(min_length=1)
    canonical_key: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")

    @field_validator("raw_value")
    @classmethod
    def normalize_raw_value(cls, value: str) -> str:
        normalized = value.strip().casefold()
        if not normalized:
            raise ValueError("platform alias must not be empty")
        return normalized


class PlatformDefaultDefinition(ImmutableContract):
    operating_system_key: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    architecture_key: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    execution_environment_key: str = Field(pattern=r"^[a-z0-9][a-z0-9._-]*$")
    profile_path: Path

    @field_validator("profile_path")
    @classmethod
    def validate_profile_path(cls, value: Path) -> Path:
        if value.is_absolute() or ".." in value.parts:
            raise ValueError("default profile must be a safe relative path")
        return value


class PlatformRegistry(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["2"] = "2"
    execution_environment_keys: frozenset[str]
    operating_system_aliases: tuple[PlatformAliasDefinition, ...]
    architecture_aliases: tuple[PlatformAliasDefinition, ...]
    profile_defaults: tuple[PlatformDefaultDefinition, ...] = ()

    @model_validator(mode="after")
    def validate_unique_entries(self) -> PlatformRegistry:
        if not self.execution_environment_keys:
            raise ValueError("execution environment keys must not be empty")
        if any(not _is_valid_platform_key(value) for value in self.execution_environment_keys):
            raise ValueError("execution environment key is invalid")
        if not self.operating_system_aliases:
            raise ValueError("operating system aliases must not be empty")
        if not self.architecture_aliases:
            raise ValueError("architecture aliases must not be empty")
        _require_unique(
            (alias.raw_value for alias in self.operating_system_aliases),
            "operating system alias",
        )
        _require_unique(
            (alias.raw_value for alias in self.architecture_aliases),
            "architecture alias",
        )
        _require_unique(
            (
                (
                    default.operating_system_key,
                    default.architecture_key,
                    default.execution_environment_key,
                )
                for default in self.profile_defaults
            ),
            "platform default",
        )
        operating_system_keys = {alias.canonical_key for alias in self.operating_system_aliases}
        architecture_keys = {alias.canonical_key for alias in self.architecture_aliases}
        for default in self.profile_defaults:
            if default.operating_system_key not in operating_system_keys:
                raise ValueError("default profile references an unknown operating system key")
            if default.architecture_key not in architecture_keys:
                raise ValueError("default profile references an unknown architecture key")
            if default.execution_environment_key not in self.execution_environment_keys:
                raise ValueError("default profile references an unknown execution environment key")
        return self

    def default_profile_for(self, host: HostPlatformDefinition) -> Path | None:
        host_key = (
            host.operating_system_key,
            host.architecture_key,
            host.execution_environment_key,
        )
        for default in self.profile_defaults:
            if (
                default.operating_system_key,
                default.architecture_key,
                default.execution_environment_key,
            ) == host_key:
                return default.profile_path
        return None


def load_platform_registry(path: Path) -> PlatformRegistry:
    try:
        with path.open("rb") as registry_file:
            return PlatformRegistry.model_validate(tomllib.load(registry_file))
    except FileNotFoundError as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The platform registry was not found.",
            details={"exception_type": type(exc).__name__},
        ) from exc
    except (OSError, tomllib.TOMLDecodeError, ValidationError) as exc:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The platform registry is invalid.",
            details={"exception_type": type(exc).__name__},
        ) from exc


def normalize_operating_system(raw_value: str, registry: PlatformRegistry) -> str:
    normalized = _normalize_platform_alias(raw_value, registry.operating_system_aliases)
    if normalized is None:
        raise InferenceError(
            code=InferenceErrorCode.UNSUPPORTED_PLATFORM,
            safe_message="The host operating system is not supported by the profile resolver.",
        )
    return normalized


def normalize_architecture(raw_value: str, registry: PlatformRegistry) -> str:
    normalized = _normalize_platform_alias(raw_value, registry.architecture_aliases)
    if normalized is None:
        raise InferenceError(
            code=InferenceErrorCode.UNSUPPORTED_PLATFORM,
            safe_message="The host architecture is not supported by the profile resolver.",
        )
    return normalized


def normalize_execution_environment(raw_value: str, registry: PlatformRegistry) -> str:
    normalized = raw_value.strip().casefold()
    if normalized not in registry.execution_environment_keys:
        raise InferenceError(
            code=InferenceErrorCode.UNSUPPORTED_PLATFORM,
            safe_message="The execution environment is not supported by the profile resolver.",
        )
    return normalized


def detect_execution_environment(
    *,
    registry: PlatformRegistry,
    environment: Mapping[str, str] | None = None,
    marker_path_exists: Callable[[Path], bool] | None = None,
    cgroup_text: str | None = None,
) -> str:
    """Detect a container without allowing a user setting to spoof host evidence."""

    current_environment = os.environ if environment is None else environment
    path_exists = Path.exists if marker_path_exists is None else marker_path_exists
    container_environment = current_environment.get("container", "").strip().casefold()
    container_markers = (Path("/.dockerenv"), Path("/run/.containerenv"))
    marker_present = bool(container_environment) or any(
        path_exists(path) for path in container_markers
    )

    observed_cgroup = cgroup_text
    if observed_cgroup is None:
        try:
            observed_cgroup = Path("/proc/1/cgroup").read_text(
                encoding="utf-8",
                errors="replace",
            )
        except OSError:
            observed_cgroup = ""
    normalized_cgroup = observed_cgroup.casefold()
    cgroup_present = any(
        marker in normalized_cgroup
        for marker in ("docker", "containerd", "kubepods", "libpod", "lxc")
    )
    detected = "container" if marker_present or cgroup_present else "native"
    return normalize_execution_environment(detected, registry)


def detect_host_platform(
    *,
    registry: PlatformRegistry,
    raw_system: str | None = None,
    raw_machine: str | None = None,
    raw_execution_environment: str | None = None,
    raw_distribution: str | None = None,
    environment: Mapping[str, str] | None = None,
    marker_path_exists: Callable[[Path], bool] | None = None,
    cgroup_text: str | None = None,
) -> HostPlatformDefinition:
    operating_system_key = normalize_operating_system(
        platform.system() if raw_system is None else raw_system,
        registry,
    )
    execution_environment_key = (
        detect_execution_environment(
            registry=registry,
            environment=environment,
            marker_path_exists=marker_path_exists,
            cgroup_text=cgroup_text,
        )
        if raw_execution_environment is None
        else normalize_execution_environment(raw_execution_environment, registry)
    )
    distribution_key = raw_distribution
    if distribution_key is None and operating_system_key == "linux":
        distribution_key = _detect_linux_distribution()
    return HostPlatformDefinition(
        operating_system_key=operating_system_key,
        architecture_key=normalize_architecture(
            platform.machine() if raw_machine is None else raw_machine,
            registry,
        ),
        execution_environment_key=execution_environment_key,
        distribution_key=(
            _normalize_distribution_key(distribution_key) if distribution_key is not None else None
        ),
    )


def resolve_profile_path(
    *,
    project_root: Path,
    explicit_path: Path | None,
    environment: Mapping[str, str] | None,
    registry: PlatformRegistry,
    raw_system: str | None = None,
    raw_machine: str | None = None,
    raw_execution_environment: str | None = None,
    raw_distribution: str | None = None,
) -> ProfileResolution:
    current_environment = os.environ if environment is None else environment
    detected_host = detect_host_platform(
        registry=registry,
        raw_system=raw_system,
        raw_machine=raw_machine,
        raw_execution_environment=raw_execution_environment,
        raw_distribution=raw_distribution,
        environment=current_environment,
    )

    if explicit_path is not None:
        return ProfileResolution(
            path=_resolve_project_path(project_root, explicit_path),
            source="explicit",
            detected_host=detected_host,
        )

    environment_profile = current_environment.get("MARGPA_PROFILE")
    if environment_profile is not None:
        if not environment_profile.strip():
            raise InferenceError(
                code=InferenceErrorCode.INVALID_CONFIGURATION,
                safe_message="The deployment profile environment setting is empty.",
            )
        return ProfileResolution(
            path=_resolve_project_path(project_root, Path(environment_profile)),
            source="environment",
            detected_host=detected_host,
        )

    default_path = registry.default_profile_for(detected_host)
    if default_path is None:
        raise InferenceError(
            code=InferenceErrorCode.PROFILE_REQUIRED,
            safe_message="No default deployment profile is available for this platform.",
        )
    return ProfileResolution(
        path=_resolve_project_path(project_root, default_path),
        source="platform_default",
        detected_host=detected_host,
    )


def validate_preload_deployment(
    *,
    expected_host: HostPlatformDefinition,
    detected_host: HostPlatformDefinition,
    requirements: DeploymentRequirements,
    deployment_backend: BackendRuntimeDefinition,
    model_backend: ModelBackendDefinition,
    model_key: str,
) -> None:
    if (
        expected_host.operating_system_key != detected_host.operating_system_key
        or expected_host.architecture_key != detected_host.architecture_key
        or expected_host.execution_environment_key != detected_host.execution_environment_key
        or (
            expected_host.distribution_key is not None
            and expected_host.distribution_key != detected_host.distribution_key
        )
    ):
        raise InferenceError(
            code=InferenceErrorCode.UNSUPPORTED_PLATFORM,
            safe_message="The deployment profile does not match the detected host platform.",
            model_key=model_key,
        )
    if requirements.fallback_policy is not FallbackPolicy.DENY:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The configured deployment fallback policy is not implemented.",
            model_key=model_key,
        )
    if (
        model_backend.backend_key != deployment_backend.backend_key
        or model_backend.required_version != deployment_backend.required_version
    ):
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The deployment backend does not match the model definition.",
            model_key=model_key,
        )


def build_runtime_observation(
    *,
    host: HostPlatformDefinition,
    backend: BackendRuntimeDefinition,
    runtime_info: ModelRuntimeInfo,
) -> RuntimeObservation:
    observed_build_variant = runtime_info.backend_build_variant
    build_variant_key = observed_build_variant or backend.build_variant_key
    build_variant_source: Literal["declared", "observed"] = (
        "observed" if observed_build_variant is not None else "declared"
    )
    warnings = (
        () if observed_build_variant is not None else ("build_variant_declared_not_observed",)
    )
    return RuntimeObservation(
        host=host,
        detected=DetectedRuntimeState(
            backend_key=runtime_info.backend_key,
            backend_version=runtime_info.backend_version,
            build_variant_key=build_variant_key,
            build_variant_source=build_variant_source,
            device_kind_key=runtime_info.device_kind,
            acceleration_api_key=runtime_info.acceleration_api,
            gpu_offload=runtime_info.gpu_offload,
            gpu_offload_evidence=runtime_info.gpu_offload_evidence,
            capabilities=runtime_info.effective_capabilities.features,
        ),
        executed=None,
        observation_warnings=warnings,
    )


def validate_deployment_runtime(
    *,
    compute: ComputeTargetDefinition,
    backend: BackendRuntimeDefinition,
    requirements: DeploymentRequirements,
    observation: RuntimeObservation,
    model_key: str,
) -> None:
    detected = observation.detected
    if (
        detected.backend_key != backend.backend_key
        or detected.backend_version != backend.required_version
    ):
        _raise_runtime_mismatch(model_key, "backend_runtime")
    if detected.build_variant_key != backend.build_variant_key:
        _raise_runtime_mismatch(model_key, "backend_build_variant")
    if detected.device_kind_key != compute.compute_kind_key:
        _raise_runtime_mismatch(model_key, "compute_kind")
    if detected.acceleration_api_key != compute.acceleration_api_key:
        _raise_runtime_mismatch(model_key, "acceleration_api")
    if (
        requirements.required_device_kind is not None
        and detected.device_kind_key != requirements.required_device_kind
    ):
        _raise_runtime_mismatch(model_key, "required_device_kind")
    if (
        requirements.required_acceleration_api is not None
        and detected.acceleration_api_key != requirements.required_acceleration_api
    ):
        _raise_runtime_mismatch(model_key, "required_acceleration_api")

    missing = requirements.required_capabilities - detected.capabilities
    if missing:
        raise InferenceError(
            code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
            safe_message="The loaded runtime is missing required deployment capabilities.",
            model_key=model_key,
            details={"capabilities": ",".join(sorted(feature.value for feature in missing))},
        )


def _resolve_project_path(project_root: Path, value: Path) -> Path:
    return (value if value.is_absolute() else project_root / value).expanduser().resolve()


def _normalize_platform_alias(
    raw_value: str,
    aliases: tuple[PlatformAliasDefinition, ...],
) -> str | None:
    candidate = raw_value.strip().casefold()
    return next(
        (alias.canonical_key for alias in aliases if alias.raw_value == candidate),
        None,
    )


def _detect_linux_distribution() -> str | None:
    try:
        release = platform.freedesktop_os_release()
    except OSError:
        return None
    raw_value = release.get("ID")
    return raw_value if raw_value else None


def _normalize_distribution_key(raw_value: str) -> str:
    normalized = raw_value.strip().casefold().replace(" ", "-")
    if not _is_valid_platform_key(normalized):
        raise InferenceError(
            code=InferenceErrorCode.UNSUPPORTED_PLATFORM,
            safe_message="The host distribution identifier is invalid.",
        )
    return normalized


def _is_valid_platform_key(value: str) -> bool:
    return (
        bool(value)
        and value[0].isalnum()
        and all(character.isalnum() or character in "._-" for character in value)
    )


def _require_unique(values: Iterable[Hashable], label: str) -> None:
    entries = tuple(values)
    if len(entries) != len(set(entries)):
        raise ValueError(f"duplicate {label}")


def _raise_runtime_mismatch(model_key: str, field: str) -> None:
    raise InferenceError(
        code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
        safe_message="The loaded runtime does not satisfy the deployment profile.",
        model_key=model_key,
        details={"field": field},
    )
