"""Backend-independent Model Port."""

from typing import Protocol, runtime_checkable

from ..contracts.generation import (
    GenerationRequest,
    GenerationResult,
    GenerationStream,
    ThinkingMode,
)
from ..contracts.messages import ChatMessage
from ..contracts.runtime import ModelCapabilities, ModelLoadConfig, ModelRuntimeInfo
from ..domain.lifecycle import ModelLifecycleState
from ..domain.model_definition import ModelDefinition


class ModelPort(Protocol):
    @property
    def state(self) -> ModelLifecycleState: ...

    @property
    def runtime_info(self) -> ModelRuntimeInfo | None: ...

    def load(
        self,
        definition: ModelDefinition,
        config: ModelLoadConfig,
    ) -> ModelRuntimeInfo: ...

    def unload(self) -> None: ...

    def capabilities(self) -> ModelCapabilities: ...

    def generate(self, request: GenerationRequest) -> GenerationResult: ...

    def stream(self, request: GenerationRequest) -> GenerationStream: ...


@runtime_checkable
class TextTokenCounterPort(Protocol):
    """Optional narrow capability for a loaded backend tokenizer."""

    def count_text_tokens(self, text: str) -> int: ...


@runtime_checkable
class ChatPromptTokenCounterPort(Protocol):
    """Optional narrow capability for exact loaded-model chat prompt measurement."""

    def count_chat_prompt_tokens(
        self,
        messages: tuple[ChatMessage, ...],
        thinking_mode: ThinkingMode,
    ) -> int: ...
