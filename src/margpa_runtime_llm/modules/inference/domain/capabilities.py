"""Model and backend capabilities understood by the inference core."""

from enum import StrEnum


class CapabilityFeature(StrEnum):
    CHAT = "chat"
    STREAMING = "streaming"
    COOPERATIVE_CANCEL = "cooperative_cancel"
    STOP_SEQUENCES = "stop_sequences"
    SEED = "seed"
    TOKEN_USAGE = "token_usage"
    MODEL_METADATA = "model_metadata"
    CHAT_TEMPLATE = "chat_template"
    THINKING_CONTROL = "thinking_control"
    GPU_OFFLOAD = "gpu_offload"
    GRAMMAR = "grammar"
    JSON_SCHEMA = "json_schema"
    LOGIT_BIAS = "logit_bias"
    TOKEN_PROBABILITIES = "token_probabilities"
    TOOL_CALLING = "tool_calling"
    VISION = "vision"
    EMBEDDING = "embedding"
    REMOTE_CANCELLATION = "remote_cancellation"
    PARALLEL_GENERATION = "parallel_generation"


MODEL_REQUIRED_CAPABILITIES = frozenset(
    {
        CapabilityFeature.CHAT,
        CapabilityFeature.STREAMING,
        CapabilityFeature.COOPERATIVE_CANCEL,
        CapabilityFeature.STOP_SEQUENCES,
        CapabilityFeature.SEED,
        CapabilityFeature.TOKEN_USAGE,
        CapabilityFeature.MODEL_METADATA,
        CapabilityFeature.CHAT_TEMPLATE,
        CapabilityFeature.THINKING_CONTROL,
    }
)
