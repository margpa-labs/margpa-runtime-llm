"""Fast tests for llama.cpp mapping, template, stream, and integrity boundaries."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, cast

import pydantic
import pytest
from llama_cpp import Llama
from llama_cpp.llama_grammar import LlamaGrammar

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
from margpa_runtime_llm.modules.inference.application.inference_service import (
    InferenceService,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationParameters,
    GenerationRequest,
    GenerationTerminalState,
    StructuredOutputConstraint,
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
from margpa_runtime_llm.modules.inference.domain.lifecycle import ModelLifecycleState

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITION = load_model_definition(PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml")
MAC_RUNTIME_CAPABILITIES = MODEL_REQUIRED_CAPABILITIES | {CapabilityFeature.GPU_OFFLOAD}


class FakeTemplateModel:
    def __init__(self, template: str) -> None:
        self.metadata = {"tokenizer.chat_template": template}
        self.tokenize_calls: list[tuple[bytes, bool, bool]] = []

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
        self.tokenize_calls.append((text, add_bos, special))
        return list(range(max(1, len(text.split()))))


class FakeTemplateModelWithSpecialTokens(FakeTemplateModel):
    def __init__(self, template: str, *, eos_token: str) -> None:
        super().__init__(template)
        self._eos_token = eos_token

    def detokenize(
        self,
        tokens: list[int],
        prev_tokens: list[int] | None = None,
        special: bool = False,
    ) -> bytes:
        del prev_tokens
        if special and tokens == [self.token_eos()]:
            return self._eos_token.encode("utf-8")
        if special and tokens == [self.token_bos()]:
            return b"<bos>"
        return b""


class FakeCompletionModel(FakeTemplateModel):
    """Gemma Judge-only Constrained Decoding Rework (WU-02/WU-06): the
    existing `FakeTemplateModel` family never implemented `create_
    completion()` at all -- `LlamaCppChatTemplate.create_chat_completion()`'s
    real `Llama.create_completion(...)` call site had no direct Unit Test
    coverage before this Rework, only real-hardware exercise. This Fake
    records every kwarg it was called with, so a Test can assert exactly
    what `grammar=` value a given `GenerationParameters` produces without
    touching a real Model."""

    def __init__(self, template: str) -> None:
        super().__init__(template)
        self.create_completion_calls: list[dict[str, Any]] = []

    def create_completion(self, **kwargs: Any) -> dict[str, Any]:
        self.create_completion_calls.append(kwargs)
        return {
            "choices": [{"text": "ok", "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }


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


def runtime_info(
    context_size: int = 4096,
    *,
    extra_features: frozenset[CapabilityFeature] = frozenset(),
) -> ModelRuntimeInfo:
    capabilities = ModelCapabilities(
        features=MAC_RUNTIME_CAPABILITIES | extra_features,
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


def test_deepseek_literal_eos_variant_is_normalized_to_tokenizer_bytes() -> None:
    broken_eos = "<｜end▁of▁sentence｜>"  # noqa: RUF001
    canonical_eos = "<｜end of sentence｜>"  # noqa: RUF001
    model = FakeTemplateModelWithSpecialTokens(broken_eos, eos_token=canonical_eos)
    controller = LlamaCppChatTemplate(cast(Llama, model))

    formatted = controller.format_prompt(
        (ChatMessage(role=MessageRole.USER, content="hello"),),
        ThinkingMode.MODEL_DEFAULT,
    )

    assert broken_eos not in formatted.prompt
    assert formatted.prompt == canonical_eos
    assert model.tokenize_calls[-1] == (canonical_eos.encode(), False, True)


def test_qwen_eos_without_spaces_is_left_byte_identical() -> None:
    canonical_eos = "<|im_end|>"
    template = "{{ eos_token }}"
    model = FakeTemplateModelWithSpecialTokens(template, eos_token=canonical_eos)
    controller = LlamaCppChatTemplate(cast(Llama, model))

    formatted = controller.format_prompt(
        (ChatMessage(role=MessageRole.USER, content="hello"),),
        ThinkingMode.MODEL_DEFAULT,
    )

    assert formatted.prompt == canonical_eos
    assert model.tokenize_calls[-1] == (canonical_eos.encode(), False, True)


def test_text_token_counter_uses_loaded_tokenizer_without_adding_bos() -> None:
    template = "{% for message in messages %}{{ message['content'] }}{% endfor %}"
    model = FakeTemplateModel(template)
    controller = LlamaCppChatTemplate(cast(Llama, model))

    count = controller.count_text_tokens("参照 context text")

    assert count == 3
    assert model.tokenize_calls[-1] == (
        "参照 context text".encode(),
        False,
        True,
    )


def test_text_token_counter_failure_does_not_expose_raw_text() -> None:
    raw_text = "SECRET-RAG-TEXT"

    class FailingTokenModel(FakeTemplateModel):
        def tokenize(
            self,
            text: bytes,
            add_bos: bool = True,
            special: bool = False,
        ) -> list[int]:
            del add_bos, special
            raise TypeError(text.decode())

    template = "{% for message in messages %}{{ message['content'] }}{% endfor %}"
    controller = LlamaCppChatTemplate(cast(Llama, FailingTokenModel(template)))

    with pytest.raises(InferenceError) as captured:
        controller.count_text_tokens(raw_text)

    assert captured.value.code is InferenceErrorCode.BACKEND_PROTOCOL_ERROR
    assert raw_text not in captured.value.safe_message
    assert raw_text not in str(captured.value)


def test_adapter_token_counter_obeys_loaded_lifecycle(tmp_path: Path) -> None:
    template = (
        "{% for message in messages %}{{ message['content'] }} {% endfor %}"
        "{% if enable_thinking %}THINKING_ON{% else %}THINKING_OFF{% endif %}"
    )
    model = FakeTemplateModel(template)
    controller = LlamaCppChatTemplate(cast(Llama, model))
    adapter = LlamaCppModelAdapter(model_root=tmp_path)
    adapter._state = ModelLifecycleState.LOADED
    adapter._chat_template = controller

    service = InferenceService(adapter)
    assert service.count_text_tokens("one two") == 2
    messages = (ChatMessage(role=MessageRole.USER, content="日本語の長い会話"),)
    disabled_count = service.count_chat_prompt_tokens(messages, ThinkingMode.DISABLED)
    assert disabled_count == controller.format_prompt(messages, ThinkingMode.DISABLED).token_count
    assert b"THINKING_OFF" in model.tokenize_calls[-1][0]
    enabled_count = service.count_chat_prompt_tokens(messages, ThinkingMode.ENABLED)
    assert enabled_count == controller.format_prompt(messages, ThinkingMode.ENABLED).token_count
    assert b"THINKING_ON" in model.tokenize_calls[-1][0]

    adapter._state = ModelLifecycleState.UNLOADED
    with pytest.raises(InferenceError) as unloaded:
        adapter.count_chat_prompt_tokens(messages, ThinkingMode.DISABLED)
    assert unloaded.value.code is InferenceErrorCode.MODEL_NOT_LOADED
    with pytest.raises(InferenceError) as unloaded_text:
        adapter.count_text_tokens("one two")
    assert unloaded_text.value.code is InferenceErrorCode.MODEL_NOT_LOADED


def test_adapter_token_counter_is_never_gated_by_an_in_flight_generation(
    tmp_path: Path,
) -> None:
    """P9-1 Judge Dispatch "unavailable" Root Cause Fix regression test.

    Confirmed by real-hardware reproduction: `SeleneSemanticEvaluator.
    _plan_batches()` calls `count_chat_prompt_tokens()` ahead of every Judge
    Batch dispatch. Before this fix, that call raised `MODEL_BUSY` whenever a
    prior real `generate()` call on the same dedicated Judge/Guard Adapter
    was still in flight on an orphaned `run_tracked_stage()` background
    Thread (`tracked_stage_worker.py`'s documented "abandoned Thread keeps
    running" design) — collapsing to the generic displayed "unavailable"
    failure category for every subsequent Turn on that Adapter instance,
    identically for Selene and Gemma (both share this exact code path).
    Tokenization only reads the loaded model's vocab/chat template, never
    the mutable generation state `_generation_lock` actually protects, so it
    must succeed regardless of `_state`/`_generation_lock` reflecting an
    in-flight `generate()` (`GENERATING`) — this is what `_begin_generation`
    sets while real generation work is running, the exact real-world
    condition an orphaned Thread leaves behind past its own caller's
    Timeout."""
    template = "{% for message in messages %}{{ message['content'] }}{% endfor %}"
    model = FakeTemplateModel(template)
    controller = LlamaCppChatTemplate(cast(Llama, model))
    adapter = LlamaCppModelAdapter(model_root=tmp_path)
    adapter._state = ModelLifecycleState.LOADED
    adapter._chat_template = controller
    messages = (ChatMessage(role=MessageRole.USER, content="hello"),)

    assert adapter._generation_lock.acquire(blocking=False)
    try:
        adapter._state = ModelLifecycleState.GENERATING
        assert adapter.count_text_tokens("one two") == 2
        count = adapter.count_chat_prompt_tokens(messages, ThinkingMode.DISABLED)
        assert count == controller.format_prompt(messages, ThinkingMode.DISABLED).token_count
    finally:
        adapter._generation_lock.release()


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
        fallback_prompt_tokens=0,
        completion_text_token_counter=len,
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


def test_stream_falls_back_to_tokenized_usage_when_backend_omits_it() -> None:
    """llama.cpp's streaming chat format never reports `usage` per-chunk
    (unlike its non-streaming response) — the stream must compute its own
    approximation from the prompt token count and the accumulated completion
    text rather than silently leaving `usage` as `None`."""

    native = ClosableNativeIterator(
        [
            {"choices": [{"delta": {"content": "he"}, "finish_reason": None}]},
            {"choices": [{"delta": {"content": "llo"}, "finish_reason": None}]},
            {"choices": [{"delta": {}, "finish_reason": "stop"}]},
        ]
    )
    stream = LlamaCppGenerationStream(
        generation_id="generation-fallback",
        request_id="request-1",
        model_key=DEFINITION.model_key,
        native_stream=native,
        on_terminal=lambda: None,
        fallback_prompt_tokens=15,
        completion_text_token_counter=len,
    )

    chunks = list(stream)

    usage = chunks[-1].usage
    assert usage is not None
    assert usage.prompt_tokens == 15
    assert usage.completion_tokens == len("hello")
    assert usage.total_tokens == 15 + len("hello")


def test_stream_trusts_native_usage_over_the_fallback_when_present() -> None:
    native = ClosableNativeIterator(
        [
            {"choices": [{"delta": {"content": "hi"}, "finish_reason": None}]},
            {
                "choices": [{"delta": {}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 2, "completion_tokens": 2, "total_tokens": 4},
            },
        ]
    )
    stream = LlamaCppGenerationStream(
        generation_id="generation-native-usage",
        request_id="request-1",
        model_key=DEFINITION.model_key,
        native_stream=native,
        on_terminal=lambda: None,
        fallback_prompt_tokens=9999,
        completion_text_token_counter=len,
    )

    chunks = list(stream)

    usage = chunks[-1].usage
    assert usage is not None
    assert usage.prompt_tokens == 2
    assert usage.completion_tokens == 2
    assert usage.total_tokens == 4


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
        fallback_prompt_tokens=0,
        completion_text_token_counter=len,
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
        fallback_prompt_tokens=0,
        completion_text_token_counter=len,
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
        fallback_prompt_tokens=0,
        completion_text_token_counter=len,
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
        fallback_prompt_tokens=0,
        completion_text_token_counter=len,
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


_GEMMA_STRUCTURED_SCHEMA = {
    "type": "object",
    "properties": {"recommendation": {"type": "string", "enum": ["accept"]}},
    "required": ["recommendation"],
    "additionalProperties": False,
}


def test_create_chat_completion_passes_grammar_none_without_structured_output() -> None:
    """Gemma Judge-only Constrained Decoding Rework (WU-02/WU-06 isolation
    item 3/4/5): a Request with no `structured_output` (every Main/Repair/
    Guard Request, unchanged by this Rework) must build `grammar=None` --
    byte-identical to `Llama.create_completion()`'s own default, never a
    silently different code path."""
    template = "{% for message in messages %}{{ message['content'] }}{% endfor %}"
    model = FakeCompletionModel(template)
    controller = LlamaCppChatTemplate(cast(Llama, model))

    controller.create_chat_completion(
        (ChatMessage(role=MessageRole.USER, content="hello"),),
        GenerationParameters(max_new_tokens=8),
        stream=False,
    )

    assert model.create_completion_calls[-1]["grammar"] is None


def test_create_chat_completion_builds_a_real_grammar_when_structured_output_is_set() -> None:
    """WU-02: a Request that DOES carry a `structured_output` constraint
    builds a genuine `LlamaGrammar` (not a stub/sentinel) and passes it
    through to the real Backend call -- the one and only Request shape
    this Rework changes."""
    template = "{% for message in messages %}{{ message['content'] }}{% endfor %}"
    model = FakeCompletionModel(template)
    controller = LlamaCppChatTemplate(cast(Llama, model))
    constraint = StructuredOutputConstraint.from_schema(_GEMMA_STRUCTURED_SCHEMA)

    controller.create_chat_completion(
        (ChatMessage(role=MessageRole.USER, content="hello"),),
        GenerationParameters(max_new_tokens=8, structured_output=constraint),
        stream=False,
    )

    grammar = model.create_completion_calls[-1]["grammar"]
    assert isinstance(grammar, LlamaGrammar)


def test_create_chat_completion_never_falls_back_to_unconstrained_on_grammar_compile_failure() -> (
    None
):
    """WU-02: "Grammar構築失敗を通常生成へFallbackしてはならない" -- a Schema
    this Contract's own lightweight validation accepts (non-empty, JSON-
    serializable, bounded size) but the real llama.cpp JSON-Schema-to-
    Grammar converter cannot compile (an unrecognized `type` value) must
    fail the whole call closed with a Typed `InferenceError`, never
    silently retry the real Model call with `grammar=None`."""
    template = "{% for message in messages %}{{ message['content'] }}{% endfor %}"
    model = FakeCompletionModel(template)
    controller = LlamaCppChatTemplate(cast(Llama, model))
    constraint = StructuredOutputConstraint.from_schema(
        {"type": "not-a-real-json-schema-type"}
    )

    with pytest.raises(InferenceError) as captured:
        controller.create_chat_completion(
            (ChatMessage(role=MessageRole.USER, content="hello"),),
            GenerationParameters(max_new_tokens=8, structured_output=constraint),
            stream=False,
        )

    assert captured.value.code is InferenceErrorCode.INVALID_CONFIGURATION
    assert model.create_completion_calls == []


def test_create_chat_completion_fails_closed_when_schema_mutated_after_construction() -> None:
    """Codex Controller Review (2026-09-06 12:44, IR-FC-02) fix: `frozen=
    True` blocks reassigning `StructuredOutputConstraint.json_schema`
    itself, but `dict` is still a mutable object -- Controller's own Probe
    confirmed `constraint.json_schema["type"] = "number"` still succeeds
    after construction, leaving `schema_digest_sha512` stale (describing
    the ORIGINAL Schema, not the mutated one). `_build_grammar()` now
    re-serializes and re-hashes `constraint.json_schema` immediately
    before compiling and Fails Closed on a Digest mismatch -- a mutated
    Schema must never silently reach the real Backend under a Digest that
    no longer describes it."""
    template = "{% for message in messages %}{{ message['content'] }}{% endfor %}"
    model = FakeCompletionModel(template)
    controller = LlamaCppChatTemplate(cast(Llama, model))
    constraint = StructuredOutputConstraint.from_schema(_GEMMA_STRUCTURED_SCHEMA)
    # `GenerationParameters(...)`'s own constructor still validates a
    # freshly-attached, not-yet-mutated `constraint` -- the real gap this
    # fix closes is a `GenerationParameters` instance that was ALREADY
    # frozen/validated having its nested Schema `dict` mutated afterward
    # (e.g. by code still holding a reference to the same `StructuredOutput
    # Constraint` object), which no further Pydantic validation ever
    # revisits. Mutating only after this Request-shaped Parameters object
    # already exists reproduces that exact window.
    parameters = GenerationParameters(max_new_tokens=8, structured_output=constraint)
    assert parameters.structured_output is not None
    parameters.structured_output.json_schema["type"] = "number"

    with pytest.raises(InferenceError) as captured:
        controller.create_chat_completion(
            (ChatMessage(role=MessageRole.USER, content="hello"),),
            parameters,
            stream=False,
        )

    assert captured.value.code is InferenceErrorCode.INVALID_CONFIGURATION
    assert model.create_completion_calls == []


def test_structured_output_constraint_from_schema_converges_non_serializable_input_to_typed_failure() -> (  # noqa: E501
    None
):
    """Codex Controller Review (2026-09-06 12:44, IR-FC-02) fix:
    "from_schema()のJSON非直列化可能入力がRaw TypeErrorで終わる現状も、既存
    ContractのTyped Validation Failureと整合させる" -- before this fix, a
    non-JSON-serializable `json_schema` raised a raw `TypeError` straight
    out of `from_schema()`, bypassing the Contract's own `_validate_schema`
    entirely. Must now converge to the same `pydantic.ValidationError`
    every other invalid `json_schema` (empty, oversized, digest-mismatched)
    already produces via direct construction."""
    with pytest.raises(pydantic.ValidationError) as captured:
        StructuredOutputConstraint.from_schema({"type": object()})

    assert "not JSON-serializable" in str(captured.value)


def test_create_chat_completion_other_sampling_arguments_are_unaffected_by_grammar() -> None:
    """WU-06 isolation item 7: every OTHER `create_completion()` argument
    (temperature/top_p/top_k/min_p/seed/max_tokens/penalties) stays exactly
    what the unchanged pre-Rework call already produced, whether or not a
    `structured_output` constraint is attached -- only `grammar=` differs."""
    template = "{% for message in messages %}{{ message['content'] }}{% endfor %}"
    model = FakeCompletionModel(template)
    controller = LlamaCppChatTemplate(cast(Llama, model))
    parameters = GenerationParameters(
        max_new_tokens=8, temperature=0.3, top_p=0.5, top_k=7, seed=42
    )

    controller.create_chat_completion(
        (ChatMessage(role=MessageRole.USER, content="hello"),), parameters, stream=False
    )
    unconstrained_call = dict(model.create_completion_calls[-1])
    del unconstrained_call["grammar"]

    constraint = StructuredOutputConstraint.from_schema(_GEMMA_STRUCTURED_SCHEMA)
    controller.create_chat_completion(
        (ChatMessage(role=MessageRole.USER, content="hello"),),
        parameters.model_copy(update={"structured_output": constraint}),
        stream=False,
    )
    constrained_call = dict(model.create_completion_calls[-1])
    del constrained_call["grammar"]

    assert unconstrained_call == constrained_call


class _FakeGenerationPort:
    """A minimal duck-typed `ModelPort` stand-in that only ever needs to
    answer `.runtime_info`/`.state` -- `InferenceService._validate_request()`
    must reject an unsupported `structured_output` Request before this
    Port's own `generate()` is ever reached."""

    def __init__(
        self,
        *,
        runtime_info: ModelRuntimeInfo,
        state: ModelLifecycleState = ModelLifecycleState.LOADED,
    ) -> None:
        self.runtime_info = runtime_info
        self.state = state
        self.generate_calls = 0

    def generate(
        self, request: GenerationRequest, *, cancellation: object | None = None
    ) -> Any:
        self.generate_calls += 1
        from margpa_runtime_llm.modules.inference.contracts.generation import (
            GenerationResult,
            GenerationTiming,
        )

        return GenerationResult(
            request_id=request.request_id,
            model_key=request.model_key,
            content="ok",
            finish_reason=FinishReason.STOP,
            timing=GenerationTiming(total_generation_seconds=0.01),
            runtime_info=self.runtime_info.reference(),
        )


def test_structured_output_request_is_rejected_when_backend_lacks_json_schema_capability() -> None:
    """WU-02: "Backend Versionの実Capability、Request validation、Typed
    failureを整合させる" -- a Request that carries `structured_output`
    against a Backend whose own `effective_capabilities.features` does not
    genuinely include `JSON_SCHEMA` must be rejected, Typed, before it ever
    reaches the Backend's own `generate()`."""
    info = runtime_info()
    assert CapabilityFeature.JSON_SCHEMA not in info.effective_capabilities.features
    port = _FakeGenerationPort(runtime_info=info)
    service = InferenceService(port)  # type: ignore[arg-type]
    constraint = StructuredOutputConstraint.from_schema(_GEMMA_STRUCTURED_SCHEMA)
    req = request().model_copy(
        update={"parameters": GenerationParameters(structured_output=constraint)}
    )

    with pytest.raises(InferenceError) as captured:
        service.generate(req)

    assert captured.value.code is InferenceErrorCode.UNSUPPORTED_CAPABILITY
    assert port.generate_calls == 0


def test_structured_output_request_is_accepted_when_backend_reports_the_capability() -> None:
    """WU-02: the same Request succeeds once the Backend genuinely reports
    `JSON_SCHEMA` support -- validation is a real Capability check, not a
    blanket rejection of every `structured_output` Request."""
    info = runtime_info(extra_features=frozenset({CapabilityFeature.JSON_SCHEMA}))
    port = _FakeGenerationPort(runtime_info=info)
    service = InferenceService(port)  # type: ignore[arg-type]
    constraint = StructuredOutputConstraint.from_schema(_GEMMA_STRUCTURED_SCHEMA)
    req = request().model_copy(
        update={"parameters": GenerationParameters(structured_output=constraint)}
    )

    result = service.generate(req)

    assert result.content == "ok"
    assert port.generate_calls == 1


def test_inference_core_does_not_import_llama_cpp() -> None:
    inference_root = PROJECT_ROOT / "src/margpa_runtime_llm/modules/inference"
    for path in inference_root.rglob("*.py"):
        assert "import llama_cpp" not in path.read_text(encoding="utf-8")
