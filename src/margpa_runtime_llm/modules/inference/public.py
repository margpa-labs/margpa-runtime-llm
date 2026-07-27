"""Stable Phase 1-B inference surface for entrypoints and future governance."""

from .application.inference_service import InferenceService
from .contracts.generation import (
    FinishReason,
    GenerationChunk,
    GenerationParameters,
    GenerationRequest,
    GenerationResult,
    GenerationStream,
    GenerationTerminalState,
    GenerationTiming,
    ThinkingMode,
    TokenUsage,
)
from .contracts.messages import ChatMessage, MessageRole
from .contracts.response import (
    ResolvedResponseLanguagePolicy,
    ResponseLanguage,
    ResponseLanguageSource,
    ResponsePolicyConfig,
)
from .contracts.runtime import (
    BackendRuntimeDefinition,
    ComputeTargetDefinition,
    DeploymentRequirements,
    DeploymentVerificationState,
    DetectedRuntimeState,
    ExecutedRuntimeState,
    FallbackPolicy,
    GpuOffloadEvidence,
    HostPlatformDefinition,
    InferenceWarning,
    ModelCapabilities,
    ModelDigest,
    ModelLoadConfig,
    ModelRuntimeInfo,
    ModelRuntimeReference,
    RuntimeObservation,
)
from .domain.capabilities import CapabilityFeature
from .domain.errors import InferenceError, InferenceErrorCode
from .domain.lifecycle import ModelLifecycleState
from .domain.model_definition import (
    ModelDefinition,
    ModelOutputProtocolDefinition,
    ThinkingOutputProtocolDefinition,
)
from .ports.model_port import ModelPort

__all__ = [
    "BackendRuntimeDefinition",
    "CapabilityFeature",
    "ChatMessage",
    "ComputeTargetDefinition",
    "DeploymentRequirements",
    "DeploymentVerificationState",
    "DetectedRuntimeState",
    "ExecutedRuntimeState",
    "FallbackPolicy",
    "FinishReason",
    "GenerationChunk",
    "GenerationParameters",
    "GenerationRequest",
    "GenerationResult",
    "GenerationStream",
    "GenerationTerminalState",
    "GenerationTiming",
    "GpuOffloadEvidence",
    "HostPlatformDefinition",
    "InferenceError",
    "InferenceErrorCode",
    "InferenceService",
    "InferenceWarning",
    "MessageRole",
    "ModelCapabilities",
    "ModelDefinition",
    "ModelDigest",
    "ModelLifecycleState",
    "ModelLoadConfig",
    "ModelOutputProtocolDefinition",
    "ModelPort",
    "ModelRuntimeInfo",
    "ModelRuntimeReference",
    "ResolvedResponseLanguagePolicy",
    "ResponseLanguage",
    "ResponseLanguageSource",
    "ResponsePolicyConfig",
    "RuntimeObservation",
    "ThinkingMode",
    "ThinkingOutputProtocolDefinition",
    "TokenUsage",
]
