"""Backend-independent contract suite exercised with a fake Model Port."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from types import TracebackType
from uuid import uuid4

import pytest

from margpa_runtime_llm.bootstrap.model_registry_loader import load_model_definition
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationChunk,
    GenerationRequest,
    GenerationResult,
    GenerationStream,
    GenerationTerminalState,
    GenerationTiming,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    GpuOffloadEvidence,
    ModelCapabilities,
    ModelDigest,
    ModelLoadConfig,
    ModelRuntimeInfo,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import (
    MODEL_REQUIRED_CAPABILITIES,
    CapabilityFeature,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.inference.domain.lifecycle import ModelLifecycleState
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition
from margpa_runtime_llm.modules.inference.ports.model_port import ModelPort

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITION = load_model_definition(PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml")
MAC_RUNTIME_CAPABILITIES = MODEL_REQUIRED_CAPABILITIES | {CapabilityFeature.GPU_OFFLOAD}


class FakeGenerationStream:
    def __init__(self, request: GenerationRequest) -> None:
        self._request = request
        self._generation_id = str(uuid4())
        self._terminal_state = GenerationTerminalState.ACTIVE

    @property
    def generation_id(self) -> str:
        return self._generation_id

    @property
    def terminal_state(self) -> GenerationTerminalState:
        return self._terminal_state

    @property
    def timing(self) -> GenerationTiming | None:
        return None

    def __iter__(self) -> Iterator[GenerationChunk]:
        yield GenerationChunk(
            request_id=self._request.request_id,
            sequence=0,
            text_delta="<think>raw</think>final",
            is_final=False,
        )
        self._terminal_state = GenerationTerminalState.COMPLETED
        yield GenerationChunk(
            request_id=self._request.request_id,
            sequence=1,
            text_delta="",
            is_final=True,
            finish_reason=FinishReason.STOP,
        )

    def cancel(self) -> None:
        if self._terminal_state is GenerationTerminalState.ACTIVE:
            self._terminal_state = GenerationTerminalState.CANCELLED

    def close(self) -> None:
        if self._terminal_state is GenerationTerminalState.ACTIVE:
            self._terminal_state = GenerationTerminalState.CLOSED_BY_CONSUMER

    def __enter__(self) -> GenerationStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


class FakeModelPort:
    def __init__(
        self,
        features: frozenset[CapabilityFeature] = MAC_RUNTIME_CAPABILITIES,
    ) -> None:
        self._state = ModelLifecycleState.UNLOADED
        self._runtime_info: ModelRuntimeInfo | None = None
        self._definition: ModelDefinition | None = None
        self._features = features

    @property
    def state(self) -> ModelLifecycleState:
        return self._state

    @property
    def runtime_info(self) -> ModelRuntimeInfo | None:
        return self._runtime_info

    def load(self, definition: ModelDefinition, config: ModelLoadConfig) -> ModelRuntimeInfo:
        if self._definition is not None:
            if self._definition.model_key == definition.model_key:
                assert self._runtime_info is not None
                return self._runtime_info
            raise InferenceError(
                code=InferenceErrorCode.MODEL_ALREADY_LOADED,
                safe_message="A different model is already loaded.",
            )
        self._definition = definition
        self._state = ModelLifecycleState.LOADED
        capabilities = ModelCapabilities(
            features=self._features,
            native_context_limit=definition.model.native_context_limit,
            loaded_context_size=config.context_size,
            max_concurrent_generations=1,
            supported_message_roles=frozenset(
                {MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT}
            ),
        )
        self._runtime_info = ModelRuntimeInfo(
            load_instance_id=str(uuid4()),
            model_key=definition.model_key,
            backend_key="fake",
            backend_version="1",
            model_architecture=definition.model.architecture,
            format=definition.artifact.format,
            quantization=definition.artifact.quantization,
            artifact_size_bytes=definition.artifact.size_bytes,
            artifact_digest=ModelDigest(value=definition.artifact.sha512),
            definition_file_sha512=definition.definition_file_sha512,
            loaded_context_size=config.context_size,
            effective_capabilities=capabilities,
            chat_template_source="fake",
            chat_template_digest=ModelDigest(value="a" * 128),
            device="fake",
            device_kind="gpu",
            acceleration_api="metal",
            gpu_offload=True,
            gpu_offload_evidence=GpuOffloadEvidence(
                supported=True,
                requested=True,
                observed=True,
                observation_source="metal_model_load",
            ),
        )
        return self._runtime_info

    def unload(self) -> None:
        self._state = ModelLifecycleState.UNLOADED
        self._definition = None
        self._runtime_info = None

    def capabilities(self) -> ModelCapabilities:
        if self._runtime_info is None:
            raise InferenceError(
                code=InferenceErrorCode.MODEL_NOT_LOADED,
                safe_message="The model is not loaded.",
            )
        return self._runtime_info.effective_capabilities

    def generate(self, request: GenerationRequest) -> GenerationResult:
        if self._runtime_info is None:
            raise InferenceError(
                code=InferenceErrorCode.MODEL_NOT_LOADED,
                safe_message="The model is not loaded.",
            )
        return GenerationResult(
            request_id=request.request_id,
            model_key=request.model_key,
            content="<think>raw</think>final",
            finish_reason=FinishReason.STOP,
            backend_finish_reason="stop",
            timing=GenerationTiming(total_generation_seconds=0.01),
            runtime_info=self._runtime_info.reference(),
        )

    def stream(self, request: GenerationRequest) -> GenerationStream:
        return FakeGenerationStream(request)


def request(model_key: str = DEFINITION.model_key) -> GenerationRequest:
    return GenerationRequest(
        request_id="request-1",
        model_key=model_key,
        messages=(ChatMessage(role=MessageRole.USER, content="hello"),),
    )


def test_fake_structurally_satisfies_model_port() -> None:
    port: ModelPort = FakeModelPort()
    assert port.state is ModelLifecycleState.UNLOADED


def test_load_and_unload_are_idempotent() -> None:
    port = FakeModelPort()
    first = port.load(DEFINITION, ModelLoadConfig())
    second = port.load(DEFINITION, ModelLoadConfig())
    assert first.load_instance_id == second.load_instance_id

    port.unload()
    port.unload()
    assert port.state is ModelLifecycleState.UNLOADED


def test_different_model_requires_explicit_unload() -> None:
    port = FakeModelPort()
    port.load(DEFINITION, ModelLoadConfig())
    another = DEFINITION.model_copy(update={"model_key": "main.another-model"})

    with pytest.raises(InferenceError) as captured:
        port.load(another, ModelLoadConfig())

    assert captured.value.code is InferenceErrorCode.MODEL_ALREADY_LOADED


def test_service_rejects_generation_before_load_and_wrong_model() -> None:
    service = InferenceService(FakeModelPort())
    with pytest.raises(InferenceError) as not_loaded:
        service.generate(request())
    assert not_loaded.value.code is InferenceErrorCode.MODEL_NOT_LOADED

    service.load(DEFINITION, ModelLoadConfig())
    with pytest.raises(InferenceError) as wrong_model:
        service.generate(request("main.wrong-model"))
    assert wrong_model.value.code is InferenceErrorCode.INVALID_REQUEST


def test_service_fails_load_when_required_capability_is_missing() -> None:
    port = FakeModelPort(MODEL_REQUIRED_CAPABILITIES - {CapabilityFeature.CHAT})
    service = InferenceService(port)

    with pytest.raises(InferenceError) as captured:
        service.load(DEFINITION, ModelLoadConfig())

    assert captured.value.code is InferenceErrorCode.UNSUPPORTED_CAPABILITY
    assert port.state is ModelLifecycleState.UNLOADED


def test_service_does_not_treat_deployment_gpu_as_model_required() -> None:
    service = InferenceService(FakeModelPort(MODEL_REQUIRED_CAPABILITIES))

    runtime = service.load(DEFINITION, ModelLoadConfig())

    assert CapabilityFeature.GPU_OFFLOAD not in runtime.effective_capabilities.features
    assert service.state is ModelLifecycleState.LOADED


def test_stream_sequence_final_chunk_and_close_are_stable() -> None:
    service = InferenceService(FakeModelPort())
    service.load(DEFINITION, ModelLoadConfig())
    stream = service.stream(request())

    chunks = list(stream)
    assert [chunk.sequence for chunk in chunks] == [0, 1]
    assert chunks[-1].is_final
    assert chunks[-1].finish_reason is FinishReason.STOP
    assert stream.terminal_state is GenerationTerminalState.COMPLETED
    assert chunks[0].text_delta == "<think>raw</think>final"

    stream.close()
    stream.close()
    assert stream.terminal_state is GenerationTerminalState.COMPLETED


def test_model_port_generation_result_remains_raw() -> None:
    service = InferenceService(FakeModelPort())
    service.load(DEFINITION, ModelLoadConfig())

    result = service.generate(request())

    assert result.content == "<think>raw</think>final"


def test_cancel_is_idempotent_and_distinct_from_close() -> None:
    stream = FakeGenerationStream(request())
    stream.cancel()
    stream.cancel()
    assert stream.terminal_state is GenerationTerminalState.CANCELLED

    other = FakeGenerationStream(request())
    other.close()
    assert other.terminal_state is GenerationTerminalState.CLOSED_BY_CONSUMER
