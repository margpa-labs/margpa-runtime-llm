"""Model, deployment, capability, and runtime observation contracts."""

from enum import StrEnum
from typing import Literal

from pydantic import Field, model_validator

from ..domain.capabilities import CapabilityFeature
from .base import ImmutableContract
from .messages import MessageRole

KEY_PATTERN = r"^[a-z0-9][a-z0-9._-]*$"


class DeploymentVerificationState(StrEnum):
    DEFINED = "defined"
    IMPLEMENTED = "implemented"
    STATICALLY_VERIFIED = "statically_verified"
    NATIVE_VERIFIED = "native_verified"
    UNSUPPORTED = "unsupported"
    EXPERIMENTAL = "experimental"


class FallbackPolicy(StrEnum):
    DENY = "deny"
    WARN = "warn"
    EXPLICIT_FALLBACK = "explicit_fallback"


class HostPlatformDefinition(ImmutableContract):
    operating_system_key: str = Field(pattern=KEY_PATTERN)
    architecture_key: str = Field(pattern=KEY_PATTERN)
    execution_environment_key: str = Field(pattern=KEY_PATTERN)
    os_version_constraint: str | None = None
    distribution_key: str | None = Field(default=None, pattern=KEY_PATTERN)


class ComputeTargetDefinition(ImmutableContract):
    compute_kind_key: str = Field(pattern=KEY_PATTERN)
    vendor_key: str | None = Field(default=None, pattern=KEY_PATTERN)
    acceleration_api_key: str = Field(pattern=KEY_PATTERN)
    memory_topology_key: str | None = Field(default=None, pattern=KEY_PATTERN)
    device_selector: str = Field(default="auto", min_length=1)
    offload_policy_key: str = Field(pattern=KEY_PATTERN)


class BackendRuntimeDefinition(ImmutableContract):
    backend_key: str = Field(pattern=KEY_PATTERN)
    required_version: str = Field(min_length=1)
    build_variant_key: str = Field(pattern=KEY_PATTERN)
    execution_mode_key: str = Field(pattern=KEY_PATTERN)


class DeploymentRequirements(ImmutableContract):
    required_capabilities: frozenset[CapabilityFeature] = frozenset()
    required_device_kind: str | None = Field(default=None, pattern=KEY_PATTERN)
    required_acceleration_api: str | None = Field(default=None, pattern=KEY_PATTERN)
    fallback_policy: FallbackPolicy = FallbackPolicy.DENY


class GpuOffloadEvidence(ImmutableContract):
    """Separate build capability and request intent from observed GPU use."""

    supported: bool
    requested: bool
    observed: bool
    observation_source: Literal[
        "metal_model_load",
        "nvidia_process_memory",
        "not_requested",
        "unsupported",
        "observation_unavailable",
    ]
    process_gpu_memory_bytes: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_evidence(self) -> "GpuOffloadEvidence":
        if self.observed and (not self.supported or not self.requested):
            raise ValueError("observed GPU offload requires support and a request")
        if self.observation_source == "not_requested" and (self.requested or self.observed):
            raise ValueError("not_requested evidence must not claim a request or observation")
        if self.observation_source == "unsupported" and (self.supported or self.observed):
            raise ValueError("unsupported evidence must not claim support or observation")
        if self.observation_source == "nvidia_process_memory":
            memory_observed = (self.process_gpu_memory_bytes or 0) > 0
            if self.observed != memory_observed:
                raise ValueError("CUDA observation must match process GPU memory evidence")
        elif self.process_gpu_memory_bytes is not None:
            raise ValueError("process GPU memory is only valid for NVIDIA evidence")
        if self.observation_source == "observation_unavailable" and self.observed:
            raise ValueError("unavailable observation must fail closed")
        return self


class DetectedRuntimeState(ImmutableContract):
    """Backend and device state observed while preparing the loaded runtime."""

    backend_key: str = Field(pattern=KEY_PATTERN)
    backend_version: str = Field(min_length=1)
    build_variant_key: str = Field(pattern=KEY_PATTERN)
    build_variant_source: Literal["declared", "observed"]
    device_kind_key: str = Field(pattern=KEY_PATTERN)
    device_name: str | None = None
    device_id: str | None = None
    acceleration_api_key: str = Field(pattern=KEY_PATTERN)
    gpu_offload: bool
    gpu_offload_evidence: GpuOffloadEvidence
    capabilities: frozenset[CapabilityFeature]

    @model_validator(mode="after")
    def validate_gpu_offload_evidence(self) -> "DetectedRuntimeState":
        if self.gpu_offload != self.gpu_offload_evidence.observed:
            raise ValueError("gpu_offload must equal the observed evidence state")
        return self


class ExecutedRuntimeState(ImmutableContract):
    """Backend and device state evidenced for one executed inference request."""

    backend_key: str = Field(pattern=KEY_PATTERN)
    backend_version: str = Field(min_length=1)
    device_kind_key: str = Field(pattern=KEY_PATTERN)
    acceleration_api_key: str = Field(pattern=KEY_PATTERN)
    gpu_offload: bool


class RuntimeObservation(ImmutableContract):
    host: HostPlatformDefinition
    detected: DetectedRuntimeState
    executed: ExecutedRuntimeState | None = None
    observation_warnings: tuple[str, ...] = ()


class ModelDigest(ImmutableContract):
    algorithm: Literal["sha512"] = "sha512"
    value: str = Field(pattern=r"^[0-9a-f]{128}$")


class ModelLoadConfig(ImmutableContract):
    context_size: int = Field(default=4096, gt=0)
    batch_size: int = Field(default=256, gt=0)
    micro_batch_size: int = Field(default=256, gt=0)
    threads: int = Field(default=6, gt=0)
    threads_batch: int = Field(default=6, gt=0)
    gpu_layers: int = -1
    use_mmap: bool = True
    use_mlock: bool = False
    verbose_backend: bool = False
    verify_artifact_hash: Literal[True] = True

    @model_validator(mode="after")
    def validate_batch_sizes(self) -> "ModelLoadConfig":
        if self.micro_batch_size > self.batch_size:
            raise ValueError("micro_batch_size must not exceed batch_size")
        return self


class ModelCapabilities(ImmutableContract):
    features: frozenset[CapabilityFeature]
    native_context_limit: int = Field(gt=0)
    loaded_context_size: int = Field(gt=0)
    max_concurrent_generations: int = Field(default=1, ge=1)
    supported_message_roles: frozenset[MessageRole]


class InferenceWarning(ImmutableContract):
    code: str
    safe_message: str
    capability: CapabilityFeature | None = None
    details: tuple[str, ...] = ()


class ModelRuntimeReference(ImmutableContract):
    load_instance_id: str
    model_key: str
    backend_key: str
    backend_version: str
    definition_file_sha512: str = Field(pattern=r"^[0-9a-f]{128}$")


class ModelRuntimeInfo(ImmutableContract):
    load_instance_id: str
    model_key: str
    backend_key: str
    backend_version: str
    backend_build_variant: str | None = Field(default=None, pattern=KEY_PATTERN)
    model_architecture: str
    format: str
    quantization: str
    artifact_size_bytes: int = Field(gt=0)
    artifact_digest: ModelDigest
    artifact_digest_verified: Literal[True] = True
    definition_file_sha512: str = Field(pattern=r"^[0-9a-f]{128}$")
    loaded_context_size: int = Field(gt=0)
    effective_capabilities: ModelCapabilities
    chat_template_source: str
    chat_template_digest: ModelDigest
    device: str
    device_kind: str = Field(pattern=KEY_PATTERN)
    acceleration_api: str = Field(pattern=KEY_PATTERN)
    gpu_offload: bool
    gpu_offload_evidence: GpuOffloadEvidence
    warnings: tuple[InferenceWarning, ...] = ()

    @model_validator(mode="after")
    def validate_gpu_offload_evidence(self) -> "ModelRuntimeInfo":
        evidence = self.gpu_offload_evidence
        if self.gpu_offload != evidence.observed:
            raise ValueError("gpu_offload must equal the observed evidence state")
        return self

    def reference(self) -> ModelRuntimeReference:
        return ModelRuntimeReference(
            load_instance_id=self.load_instance_id,
            model_key=self.model_key,
            backend_key=self.backend_key,
            backend_version=self.backend_version,
            definition_file_sha512=self.definition_file_sha512,
        )
