"""Fast tests for llama.cpp mapping, template, stream, and integrity boundaries."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, cast

import pytest
from llama_cpp import Llama

from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.model_backends.llama_cpp.chat_template import (
    FormattedPrompt,
    LlamaCppChatTemplate,
)
from margpa_runtime_llm.adapters.model_backends.llama_cpp.error_mapping import (
    map_finish_reason,
    parse_token_usage,
    raise_mapped_backend_error,
)
from margpa_runtime_llm.adapters.model_backends.llama_cpp.stream import (
    LlamaCppGenerationStream,
)
from margpa_runtime_llm.bootstrap.model_registry_loader import load_model_definition
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationParameters,
    GenerationRequest,
    GenerationTerminalState,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    GpuOffloadEvidence,
    ModelCapabilities,
    ModelDigest,
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

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITION = load_model_definition(PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml")
MAC_RUNTIME_CAPABILITIES = MODEL_REQUIRED_CAPABILITIES | {CapabilityFeature.GPU_OFFLOAD}


class FakeTemplateModel:
    def __init__(self, template: str) -> None:
        self.metadata = {"tokenizer.chat_template": template}

    def token_eos(self) -> int:
        return 1

    def token_bos(self) -> int:
        return 2

    def detokenize(
        self,
        tokens: list[int],
        prev_tokens: list[int] | None = None,
        special: bool = False,
    ) -> bytes:
        return b"<special>" if special else b""

    def tokenize(self, text: bytes, add_bos: bool = True, special: bool = False) -> list[int]:
        return list(range(max(1, len(text.split()))))


class ClosableNativeIterator:
    def __init__(self, payloads: list[dict[str, Any]]) -> None:
        self._payloads = iter(payloads)
        self.close_calls = 0

    def __iter__(self) -> ClosableNativeIterator:
        return self

    def __next__(self) -> dict[str, Any]:
        return next(self._payloads)

    def close(self) -> None:
        self.close_calls += 1


class ProcessControlNativeIterator:
    def __init__(self, exception_type: type[BaseException]) -> None:
        self._exception_type = exception_type
        self.close_calls = 0

    def __iter__(self) -> ProcessControlNativeIterator:
        return self

    def __next__(self) -> dict[str, Any]:
        raise self._exception_type

    def close(self) -> None:
        self.close_calls += 1


def request(max_new_tokens: int = 16) -> GenerationRequest:
    return GenerationRequest(
        request_id="request-1",
        model_key=DEFINITION.model_key,
        messages=(ChatMessage(role=MessageRole.USER, content="hello"),),
        parameters=GenerationParameters(max_new_tokens=max_new_tokens),
    )


def assert_terminal_state(
    stream: LlamaCppGenerationStream,
    expected: GenerationTerminalState,
) -> None:
    assert stream.terminal_state is expected


def runtime_info(context_size: int = 4096) -> ModelRuntimeInfo:
    capabilities = ModelCapabilities(
        features=MAC_RUNTIME_CAPABILITIES,
        native_context_limit=32768,
        loaded_context_size=context_size,
        supported_message_roles=frozenset(
            {MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT}
        ),
    )
    return ModelRuntimeInfo(
        load_instance_id="load-1",
        model_key=DEFINITION.model_key,
        backend_key="llama_cpp",
        backend_version="0.3.34",
        model_architecture="qwen3",
        format="gguf",
        quantization="Q4_K_M",
        artifact_size_bytes=DEFINITION.artifact.size_bytes,
        artifact_digest=ModelDigest(value=DEFINITION.artifact.sha512),
        definition_file_sha512=DEFINITION.definition_file_sha512,
        loaded_context_size=context_size,
        effective_capabilities=capabilities,
        chat_template_source="gguf_metadata",
        chat_template_digest=ModelDigest(value="a" * 128),
        device="metal",
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


def test_finish_reason_and_token_usage_mapping() -> None:
    assert map_finish_reason("stop") == (FinishReason.STOP, "stop")
    assert map_finish_reason("new_backend_reason") == (
        FinishReason.UNKNOWN,
        "new_backend_reason",
    )
    assert (
        parse_token_usage(
            {"usage": {"prompt_tokens": 2, "completion_tokens": 3, "total_tokens": 5}}
        )
        is not None
    )
    assert parse_token_usage({"usage": {"prompt_tokens": None}}) is None


def test_hard_thinking_switch_is_forwarded_to_embedded_template() -> None:
    template = (
        "{% for message in messages %}{{ message['content'] }}{% endfor %}"
        "{% if enable_thinking %}THINKING_ON{% else %}THINKING_OFF{% endif %}"
    )
    controller = LlamaCppChatTemplate(cast(Llama, FakeTemplateModel(template)))
    messages = (ChatMessage(role=MessageRole.USER, content="hello"),)

    disabled = controller.format_prompt(messages, ThinkingMode.DISABLED)
    enabled = controller.format_prompt(messages, ThinkingMode.ENABLED)

    assert controller.hard_switch_supported
    assert "THINKING_OFF" in disabled.prompt
    assert "THINKING_ON" in enabled.prompt
    assert not controller.warnings


def test_soft_thinking_switch_is_explicitly_warned() -> None:
    template = "{% for message in messages %}{{ message['content'] }}{% endfor %}"
    controller = LlamaCppChatTemplate(cast(Llama, FakeTemplateModel(template)))
    messages = (ChatMessage(role=MessageRole.USER, content="hello"),)

    disabled = controller.format_prompt(messages, ThinkingMode.DISABLED)

    assert not controller.hard_switch_supported
    assert "/no_think" in disabled.prompt
    assert controller.warnings[0].code == "thinking_soft_switch"


def test_stream_maps_sequence_terminal_usage_and_timing() -> None:
    terminal_calls = 0

    def on_terminal() -> None:
        nonlocal terminal_calls
        terminal_calls += 1

    native = ClosableNativeIterator(
        [
            {"choices": [{"delta": {"content": "A"}, "finish_reason": None}]},
            {"choices": [{"delta": {"content": "B"}, "finish_reason": None}]},
            {
                "choices": [{"delta": {}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 2, "completion_tokens": 2, "total_tokens": 4},
            },
        ]
    )
    stream = LlamaCppGenerationStream(
        generation_id="generation-1",
        request_id="request-1",
        model_key=DEFINITION.model_key,
        native_stream=native,
        on_terminal=on_terminal,
    )

    chunks = list(stream)

    assert [chunk.sequence for chunk in chunks] == [0, 1, 2]
    assert "".join(chunk.text_delta for chunk in chunks) == "AB"
    assert chunks[-1].finish_reason is FinishReason.STOP
    assert chunks[-1].usage is not None
    assert stream.terminal_state is GenerationTerminalState.COMPLETED
    assert stream.timing is not None
    assert stream.timing.first_content_latency_seconds is not None
    assert terminal_calls == 1


def test_stream_cancel_and_close_are_idempotent_and_distinct() -> None:
    native = ClosableNativeIterator([])
    calls = 0

    def terminal() -> None:
        nonlocal calls
        calls += 1

    stream = LlamaCppGenerationStream(
        generation_id="generation-1",
        request_id="request-1",
        model_key=DEFINITION.model_key,
        native_stream=native,
        on_terminal=terminal,
    )
    stream.cancel()
    stream.cancel()
    assert stream.terminal_state is GenerationTerminalState.CANCELLED
    assert native.close_calls == 1
    assert calls == 1

    other = LlamaCppGenerationStream(
        generation_id="generation-2",
        request_id="request-1",
        model_key=DEFINITION.model_key,
        native_stream=ClosableNativeIterator([]),
        on_terminal=lambda: None,
    )
    other.close()
    assert other.terminal_state is GenerationTerminalState.CLOSED_BY_CONSUMER


def test_stream_without_terminal_chunk_is_protocol_error() -> None:
    stream = LlamaCppGenerationStream(
        generation_id="generation-1",
        request_id="request-1",
        model_key=DEFINITION.model_key,
        native_stream=ClosableNativeIterator([]),
        on_terminal=lambda: None,
    )

    with pytest.raises(InferenceError) as captured:
        list(stream)

    assert captured.value.code is InferenceErrorCode.BACKEND_PROTOCOL_ERROR
    assert stream.terminal_state is GenerationTerminalState.FAILED


@pytest.mark.parametrize("exception_type", [KeyboardInterrupt, SystemExit])
def test_stream_does_not_map_process_control_exceptions(
    exception_type: type[BaseException],
) -> None:
    terminal_calls = 0

    def on_terminal() -> None:
        nonlocal terminal_calls
        terminal_calls += 1

    native = ProcessControlNativeIterator(exception_type)
    stream = LlamaCppGenerationStream(
        generation_id="generation-process-control",
        request_id="request-1",
        model_key=DEFINITION.model_key,
        native_stream=native,
        on_terminal=on_terminal,
    )

    with pytest.raises(exception_type):
        next(iter(stream))

    assert_terminal_state(stream, GenerationTerminalState.ACTIVE)
    assert terminal_calls == 0
    stream.cancel()
    assert_terminal_state(stream, GenerationTerminalState.CANCELLED)
    assert native.close_calls == 1
    assert terminal_calls == 1


@pytest.mark.parametrize("exception", [KeyboardInterrupt(), SystemExit(130)])
def test_backend_error_mapper_never_consumes_process_control(
    exception: BaseException,
) -> None:
    with pytest.raises(type(exception)):
        raise_mapped_backend_error("stream", exception)


def test_context_overflow_reports_required_and_available_tokens() -> None:
    class StubTemplate:
        def format_prompt(
            self,
            messages: tuple[ChatMessage, ...],
            thinking_mode: ThinkingMode,
        ) -> FormattedPrompt:
            return FormattedPrompt(prompt="formatted", token_count=15)

    with pytest.raises(InferenceError) as captured:
        LlamaCppModelAdapter._validate_context(
            request(max_new_tokens=2),
            cast(LlamaCppChatTemplate, StubTemplate()),
            runtime_info(context_size=16),
        )

    assert captured.value.code is InferenceErrorCode.CONTEXT_LIMIT_EXCEEDED
    assert captured.value.details["required_tokens"] == 17
    assert captured.value.details["available_tokens"] == 16


def test_artifact_integrity_rejects_same_size_different_digest(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.gguf"
    artifact.write_bytes(b"phase-1b-model")
    digest = hashlib.sha512(artifact.read_bytes()).hexdigest()
    artifact_definition = DEFINITION.artifact.model_copy(
        update={
            "relative_path": Path("artifact.gguf"),
            "file_name": "artifact.gguf",
            "size_bytes": artifact.stat().st_size,
            "sha512": digest,
        }
    )
    definition = DEFINITION.model_copy(update={"artifact": artifact_definition})
    adapter = LlamaCppModelAdapter(model_root=tmp_path)

    resolved, actual = adapter._verify_artifact(definition)
    assert resolved == artifact
    assert actual == digest

    mismatch = definition.model_copy(
        update={"artifact": artifact_definition.model_copy(update={"sha512": "0" * 128})}
    )
    assert mismatch.artifact.size_bytes == artifact.stat().st_size
    with pytest.raises(InferenceError) as captured:
        adapter._verify_artifact(mismatch)
    assert captured.value.code is InferenceErrorCode.MODEL_INTEGRITY_MISMATCH


def test_inference_core_does_not_import_llama_cpp() -> None:
    inference_root = PROJECT_ROOT / "src/margpa_runtime_llm/modules/inference"
    for path in inference_root.rglob("*.py"):
        assert "import llama_cpp" not in path.read_text(encoding="utf-8")
