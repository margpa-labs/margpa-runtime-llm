"""Application service coordinating the backend-independent Model Port."""

from ..contracts.generation import (
    GenerationRequest,
    GenerationResult,
    GenerationStream,
    ThinkingMode,
)
from ..contracts.messages import ChatMessage
from ..contracts.runtime import ModelCapabilities, ModelLoadConfig, ModelRuntimeInfo
from ..domain.cancellation import CancellationToken
from ..domain.capabilities import CapabilityFeature
from ..domain.errors import InferenceError, InferenceErrorCode
from ..domain.lifecycle import ModelLifecycleState
from ..domain.model_definition import ModelDefinition
from ..ports.model_port import ChatPromptTokenCounterPort, ModelPort, TextTokenCounterPort


class InferenceService:
    def __init__(self, port: ModelPort) -> None:
        self._port = port

    @property
    def state(self) -> ModelLifecycleState:
        return self._port.state

    @property
    def runtime_info(self) -> ModelRuntimeInfo | None:
        return self._port.runtime_info

    def load(self, definition: ModelDefinition, config: ModelLoadConfig) -> ModelRuntimeInfo:
        runtime_info = self._port.load(definition, config)
        try:
            self._validate_capabilities(
                runtime_info.effective_capabilities,
                definition.capabilities.required_features,
                definition.model_key,
            )
        except InferenceError:
            self._port.unload()
            raise
        return runtime_info

    def unload(self) -> None:
        self._port.unload()

    def capabilities(self) -> ModelCapabilities:
        return self._port.capabilities()

    def generate(
        self,
        request: GenerationRequest,
        *,
        cancellation: CancellationToken | None = None,
    ) -> GenerationResult:
        self._validate_request(request)
        return self._port.generate(request, cancellation=cancellation)

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self._validate_request(request)
        return self._port.stream(request)

    def count_text_tokens(self, text: str) -> int:
        if not isinstance(self._port, TextTokenCounterPort):
            raise InferenceError(
                code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
                safe_message="Text token counting is unavailable for this backend.",
            )
        return self._port.count_text_tokens(text)

    def count_chat_prompt_tokens(
        self,
        messages: tuple[ChatMessage, ...],
        thinking_mode: ThinkingMode,
    ) -> int:
        if not isinstance(self._port, ChatPromptTokenCounterPort):
            raise InferenceError(
                code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
                safe_message="Exact chat prompt token counting is unavailable for this backend.",
            )
        return self._port.count_chat_prompt_tokens(messages, thinking_mode)

    def _validate_request(self, request: GenerationRequest) -> None:
        runtime_info = self._port.runtime_info
        if runtime_info is None or self._port.state is ModelLifecycleState.UNLOADED:
            raise InferenceError(
                code=InferenceErrorCode.MODEL_NOT_LOADED,
                safe_message="The model is not loaded.",
                request_id=request.request_id,
                model_key=request.model_key,
            )
        if runtime_info.model_key != request.model_key:
            raise InferenceError(
                code=InferenceErrorCode.INVALID_REQUEST,
                safe_message="The requested model does not match the loaded model.",
                request_id=request.request_id,
                model_key=request.model_key,
            )
        capabilities = runtime_info.effective_capabilities
        unsupported_roles = {
            message.role
            for message in request.messages
            if message.role not in capabilities.supported_message_roles
        }
        if unsupported_roles:
            raise InferenceError(
                code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
                safe_message="The loaded model does not support one or more message roles.",
                request_id=request.request_id,
                model_key=request.model_key,
                details={"roles": ",".join(sorted(role.value for role in unsupported_roles))},
            )

    @staticmethod
    def _validate_capabilities(
        capabilities: ModelCapabilities,
        required_capabilities: frozenset[CapabilityFeature],
        model_key: str,
    ) -> None:
        missing = required_capabilities - capabilities.features
        if missing:
            raise InferenceError(
                code=InferenceErrorCode.UNSUPPORTED_CAPABILITY,
                safe_message="The loaded runtime is missing required capabilities.",
                model_key=model_key,
                details={"capabilities": ",".join(sorted(feature.value for feature in missing))},
            )
