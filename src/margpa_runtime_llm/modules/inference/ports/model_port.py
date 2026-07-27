"""Backend-independent Model Port."""

from typing import Protocol

from ..contracts.generation import (
    GenerationRequest,
    GenerationResult,
    GenerationStream,
)
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
