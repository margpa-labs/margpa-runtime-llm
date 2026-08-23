"""P6-CODEX-013 (Second Rework): a completed Generation Attempt's real
Model/Backend/Artifact/Context identity is captured on the COMPLETED
`ConversationEvent.data["attempt_provenance"]`, sourced from the same
`ModelRuntimeInfo` object bootstrap already resolves once at Model load
(`Phase1Application.service.runtime_info`) — never a second, possibly
inconsistent lookup, and never fabricated when no such info was supplied
(the default `None` case must match every pre-existing test's behavior
exactly, hence the explicit "absent" test below).
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from types import TracebackType

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
from margpa_runtime_llm.modules.conversation.public import (
    ConversationEventType,
    ConversationGenerationInput,
    ConversationGenerationService,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationChunk,
    GenerationParameters,
    GenerationRequest,
    GenerationStream,
    GenerationTerminalState,
    GenerationTiming,
    ThinkingMode,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.messages import MessageRole
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    GpuOffloadEvidence,
    ModelCapabilities,
    ModelDigest,
    ModelRuntimeInfo,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import CapabilityFeature
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)


class FakeStream:
    def __init__(self, *, text_deltas: tuple[str, ...] = ("answer",)) -> None:
        self.text_deltas = text_deltas
        self.cancelled = False
        self.closed = False

    @property
    def generation_id(self) -> str:
        return "fake-generation"

    @property
    def terminal_state(self) -> GenerationTerminalState:
        return GenerationTerminalState.ACTIVE

    @property
    def timing(self) -> GenerationTiming | None:
        return None

    def __iter__(self) -> Iterator[GenerationChunk]:
        for sequence, text in enumerate(self.text_deltas):
            yield GenerationChunk(
                request_id="fake-request", sequence=sequence, text_delta=text, is_final=False
            )
        yield GenerationChunk(
            request_id="fake-request",
            sequence=len(self.text_deltas),
            text_delta="",
            is_final=True,
            finish_reason=FinishReason.STOP,
            usage=TokenUsage(prompt_tokens=5, completion_tokens=1, total_tokens=6),
        )

    def cancel(self) -> None:
        self.cancelled = True

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> FakeStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self.cancelled:
            self.close()


class FakeInference:
    def __init__(self, factory: Callable[[], GenerationStream] | None = None) -> None:
        self.factory = factory or FakeStream
        self.requests: list[GenerationRequest] = []

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return self.factory()


def _presentation_policy() -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def _conversation_input(*, content: str = "hello") -> ConversationGenerationInput:
    return ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content=content),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
        ),
    )


def _runtime_info(*, context_size: int = 8192) -> ModelRuntimeInfo:
    return ModelRuntimeInfo(
        load_instance_id="load-1",
        model_key="main.qwen3-4b",
        backend_key="llama_cpp",
        backend_version="b1234",
        model_architecture="qwen3",
        format="gguf",
        quantization="q4_k_m",
        artifact_size_bytes=1024,
        artifact_digest=ModelDigest(value="a" * 128),
        definition_file_sha512="b" * 128,
        loaded_context_size=context_size,
        effective_capabilities=ModelCapabilities(
            features=frozenset({CapabilityFeature.CHAT}),
            native_context_limit=context_size,
            loaded_context_size=context_size,
            supported_message_roles=frozenset({MessageRole.USER, MessageRole.ASSISTANT}),
        ),
        chat_template_source="embedded",
        chat_template_digest=ModelDigest(value="c" * 128),
        device="cpu",
        device_kind="cpu",
        acceleration_api="none",
        gpu_offload=False,
        gpu_offload_evidence=GpuOffloadEvidence(
            supported=False, requested=False, observed=False, observation_source="not_requested"
        ),
    )


def _service(
    inference: FakeInference,
    *,
    model_runtime_info: ModelRuntimeInfo | None = None,
    effective_context_size: int = 8192,
) -> ConversationGenerationService:
    return ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key="main.model",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=_presentation_policy(),
        effective_context_size=effective_context_size,
        model_runtime_info=model_runtime_info,
    )


def test_attempt_provenance_is_absent_by_default_matching_pre_existing_behavior() -> None:
    inference = FakeInference()
    session = _service(inference).start(_conversation_input())
    events = list(session.events())
    completed = next(e for e in events if e.event is ConversationEventType.COMPLETED)

    assert "attempt_provenance" not in completed.data


def test_attempt_provenance_carries_the_real_model_backend_artifact_and_context() -> None:
    inference = FakeInference()
    runtime_info = _runtime_info(context_size=8192)
    session = _service(
        inference, model_runtime_info=runtime_info, effective_context_size=8192
    ).start(_conversation_input())
    events = list(session.events())
    completed = next(e for e in events if e.event is ConversationEventType.COMPLETED)

    provenance = completed.data["attempt_provenance"]
    assert isinstance(provenance, dict)
    assert provenance["model_identity"] == "main.qwen3-4b"
    assert provenance["backend_key"] == "llama_cpp"
    assert provenance["backend_version"] == "b1234"
    assert provenance["artifact_digest_sha512"] == "a" * 128
    assert provenance["context_size"] == 8192
    # P6-CODEX-023 (Third Rework): the actually-applied Generation Config
    # Digest is now genuinely populated here — previously this Field
    # existed on `ConversationTurnProvenance` but nothing upstream of it
    # ever set it, so P6-ACC-008's "Generation Config Digest persisted"
    # claim was not actually true.
    assert isinstance(provenance["generation_config_digest_sha512"], str)
    assert len(provenance["generation_config_digest_sha512"]) == 128


def test_attempt_provenance_generation_config_digest_changes_with_generation_parameters() -> None:
    """P6-CODEX-023: the Digest must reflect the actually-applied
    GenerationParameters for *this* Attempt, not a static constant — two
    Attempts with different applied parameters (here, `max_new_tokens` via
    a different `ConversationSettings`) must produce different Digests."""
    runtime_info = _runtime_info()

    inference_a = FakeInference()
    session_a = _service(inference_a, model_runtime_info=runtime_info).start(_conversation_input())
    completed_a = next(e for e in session_a.events() if e.event is ConversationEventType.COMPLETED)
    digest_a = completed_a.data["attempt_provenance"]["generation_config_digest_sha512"]  # type: ignore[index]

    inference_b = FakeInference()
    different_input = ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="hello"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=64,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
        ),
    )
    session_b = _service(inference_b, model_runtime_info=runtime_info).start(different_input)
    completed_b = next(e for e in session_b.events() if e.event is ConversationEventType.COMPLETED)
    digest_b = completed_b.data["attempt_provenance"]["generation_config_digest_sha512"]  # type: ignore[index]

    assert digest_a != digest_b


def test_attempt_provenance_is_absent_on_a_non_completed_terminal_event() -> None:
    def _factory() -> GenerationStream:
        raise RuntimeError("boom")

    inference = FakeInference(factory=_factory)
    session = _service(inference, model_runtime_info=_runtime_info()).start(_conversation_input())
    events = list(session.events())

    assert all(event.event is not ConversationEventType.COMPLETED for event in events)
