"""Framework-independent Phase 1-G conversation contract tests."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from types import TracebackType

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.modules.conversation.public import (
    TOKEN_LIMIT_WARNING,
    ConversationEvent,
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
)
from margpa_runtime_llm.modules.inference.contracts.messages import MessageRole
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError, InferenceErrorCode
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.summarization.public import SummaryMode
from margpa_runtime_llm.orchestration.response_language import JAPANESE_RESPONSE_INSTRUCTION


class FakeStream:
    def __init__(
        self,
        *,
        text_deltas: tuple[str, ...] = ("answer",),
        finish_reason: FinishReason = FinishReason.STOP,
        failure: InferenceError | None = None,
    ) -> None:
        self.text_deltas = text_deltas
        self.finish_reason = finish_reason
        self.failure = failure
        self.cancelled = False
        self.closed = False

    @property
    def generation_id(self) -> str:
        return "fake-generation"

    @property
    def terminal_state(self) -> GenerationTerminalState:
        if self.cancelled:
            return GenerationTerminalState.CANCELLED
        if self.closed:
            return GenerationTerminalState.CLOSED_BY_CONSUMER
        return GenerationTerminalState.ACTIVE

    @property
    def timing(self) -> GenerationTiming | None:
        return None

    def __iter__(self) -> Iterator[GenerationChunk]:
        if self.failure is not None:
            raise self.failure
        for sequence, text in enumerate(self.text_deltas):
            yield GenerationChunk(
                request_id="fake-request",
                sequence=sequence,
                text_delta=text,
                is_final=False,
            )
        yield GenerationChunk(
            request_id="fake-request",
            sequence=len(self.text_deltas),
            text_delta="",
            is_final=True,
            finish_reason=self.finish_reason,
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


class NoTerminalStream(FakeStream):
    def __iter__(self) -> Iterator[GenerationChunk]:
        yield GenerationChunk(
            request_id="fake-request",
            sequence=0,
            text_delta="incomplete summary",
            is_final=False,
        )


class FakeInference:
    def __init__(self, factory: Callable[[], GenerationStream] | None = None) -> None:
        self.factory = factory or FakeStream
        self.requests: list[GenerationRequest] = []

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return self.factory()


def presentation_policy(
    visibility: ThinkingVisibility = ThinkingVisibility.HIDDEN,
) -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=visibility,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def conversation_input(
    *,
    visibility: ThinkingVisibility = ThinkingVisibility.HIDDEN,
    thinking_mode: ThinkingMode = ThinkingMode.ENABLED,
    max_new_tokens: int = 128,
    summary_mode: SummaryMode = SummaryMode.OFF,
) -> ConversationGenerationInput:
    return ConversationGenerationInput(
        messages=(
            ConversationMessage(role=ConversationRole.USER, content="first"),
            ConversationMessage(role=ConversationRole.ASSISTANT, content="prior answer"),
            ConversationMessage(role=ConversationRole.USER, content="next"),
        ),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=max_new_tokens,
            thinking_mode=thinking_mode,
            thinking_visibility=visibility,
            summary_mode=summary_mode,
        ),
    )


def service(inference: FakeInference) -> ConversationGenerationService:
    return ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(
                opening_delimiter="<think>",
                closing_delimiter="</think>",
            )
        ),
        model_key="main.model",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048,
            thinking_mode=ThinkingMode.ENABLED,
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
    )


def event_types(events: list[ConversationEvent]) -> list[ConversationEventType]:
    return [event.event for event in events]


def test_history_contract_rejects_invalid_roles_order_and_values() -> None:
    with pytest.raises(ValidationError):
        ConversationMessage.model_validate({"role": "system", "content": "unsafe"})
    with pytest.raises(ValidationError):
        ConversationMessage(role=ConversationRole.USER, content=" ")
    with pytest.raises(ValidationError):
        ConversationGenerationInput(
            messages=(ConversationMessage(role=ConversationRole.ASSISTANT, content="bad"),),
            settings=conversation_input().settings,
        )
    with pytest.raises(ValidationError):
        ConversationGenerationInput(
            messages=(
                ConversationMessage(role=ConversationRole.USER, content="one"),
                ConversationMessage(role=ConversationRole.USER, content="two"),
            ),
            settings=conversation_input().settings,
        )


@pytest.mark.parametrize("value", [True, 1.5, "128", 0, 2049])
def test_max_new_tokens_is_a_bounded_strict_integer(value: object) -> None:
    with pytest.raises(ValidationError):
        ConversationSettings.model_validate(
            {
                "response_language": "ja",
                "max_new_tokens": value,
                "thinking_visibility": "hidden",
            }
        )


def test_summary_mode_rejects_unknown_client_value() -> None:
    with pytest.raises(ValidationError):
        ConversationSettings.model_validate(
            {
                "response_language": "ja",
                "max_new_tokens": 128,
                "thinking_visibility": "hidden",
                "summary_mode": "on",
            }
        )


@pytest.mark.parametrize("value", ["model_default", "unknown"])
def test_web_thinking_mode_rejects_unsupported_values(value: str) -> None:
    with pytest.raises(ValidationError):
        ConversationSettings.model_validate(
            {
                "response_language": "ja",
                "max_new_tokens": 128,
                "thinking_mode": value,
                "thinking_visibility": "hidden",
            }
        )


def test_request_composition_preserves_history_and_only_overrides_allowed_values() -> None:
    inference = FakeInference()
    generation = service(inference)

    events = list(generation.start(conversation_input(max_new_tokens=128)).events())

    request = inference.requests[0]
    assert [message.role for message in request.messages] == [
        MessageRole.SYSTEM,
        MessageRole.USER,
        MessageRole.ASSISTANT,
        MessageRole.USER,
    ]
    assert request.messages[0].content == JAPANESE_RESPONSE_INSTRUCTION
    assert [message.content for message in request.messages[1:]] == [
        "first",
        "prior answer",
        "next",
    ]
    assert request.parameters.max_new_tokens == 128
    assert request.parameters.thinking_mode is ThinkingMode.ENABLED
    assert event_types(events) == [
        ConversationEventType.START,
        ConversationEventType.DELTA,
        ConversationEventType.COMPLETED,
    ]


def test_hidden_thinking_never_enters_display_payload_or_canonical_history() -> None:
    inference = FakeInference(
        lambda: FakeStream(text_deltas=("<think>secret", "</think>safe answer"))
    )

    events = list(service(inference).start(conversation_input()).events())
    deltas = "".join(
        str(event.data["text"]) for event in events if event.event is ConversationEventType.DELTA
    )
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)

    assert deltas == "safe answer"
    assert all(
        event.data["channel"] == "final"
        for event in events
        if event.event is ConversationEventType.DELTA
    )
    assert "secret" not in deltas
    assert completed.data["assistant_message"] == {
        "role": "assistant",
        "content": "safe answer",
    }


def test_visible_thinking_is_display_only_and_canonical_final_stays_separate() -> None:
    inference = FakeInference(lambda: FakeStream(text_deltas=("<think>reason", "</think>answer")))

    events = list(
        service(inference).start(conversation_input(visibility=ThinkingVisibility.VISIBLE)).events()
    )
    deltas = [event for event in events if event.event is ConversationEventType.DELTA]
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)

    assert [(event.data["channel"], event.data["text"]) for event in deltas] == [
        ("reasoning", "reason"),
        ("final", "answer"),
    ]
    assert completed.data["assistant_message"] == {"role": "assistant", "content": "answer"}


@pytest.mark.parametrize(
    ("thinking_mode", "visibility", "expected_channels"),
    [
        (ThinkingMode.DISABLED, ThinkingVisibility.HIDDEN, ["final"]),
        (ThinkingMode.DISABLED, ThinkingVisibility.VISIBLE, ["final"]),
        (ThinkingMode.ENABLED, ThinkingVisibility.HIDDEN, ["final"]),
        (ThinkingMode.ENABLED, ThinkingVisibility.VISIBLE, ["reasoning", "final"]),
    ],
)
def test_thinking_generation_and_visibility_combinations_are_separate(
    thinking_mode: ThinkingMode,
    visibility: ThinkingVisibility,
    expected_channels: list[str],
) -> None:
    inference = FakeInference(
        lambda: FakeStream(text_deltas=("<think>private-trace-2371</think>answer",))
    )

    events = list(
        service(inference)
        .start(conversation_input(thinking_mode=thinking_mode, visibility=visibility))
        .events()
    )

    assert inference.requests[0].parameters.thinking_mode is thinking_mode
    assert [
        str(event.data["channel"]) for event in events if event.event is ConversationEventType.DELTA
    ] == expected_channels
    if visibility is ThinkingVisibility.HIDDEN or thinking_mode is ThinkingMode.DISABLED:
        assert "private-trace-2371" not in repr(events)


def test_unavailable_thinking_control_rejects_enablement_without_taking_gate() -> None:
    inference = FakeInference()
    generation = ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(
                opening_delimiter="<think>",
                closing_delimiter="</think>",
            )
        ),
        model_key="main.model",
        generation_defaults=GenerationParameters(),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy(),
        thinking_control_available=False,
    )

    with pytest.raises(InferenceError) as captured:
        generation.start(conversation_input(thinking_mode=ThinkingMode.ENABLED))
    assert captured.value.code is InferenceErrorCode.UNSUPPORTED_CAPABILITY

    completed = list(
        generation.start(conversation_input(thinking_mode=ThinkingMode.DISABLED)).events()
    )
    assert completed[-1].event is ConversationEventType.COMPLETED


def test_final_answer_token_exhaustion_is_explicit() -> None:
    inference = FakeInference(
        lambda: FakeStream(
            text_deltas=("<think>unfinished",),
            finish_reason=FinishReason.LENGTH,
        )
    )

    events = list(service(inference).start(conversation_input()).events())
    warnings = [event for event in events if event.event is ConversationEventType.WARNING]

    assert any(event.data.get("code") == "final_answer_token_limit" for event in warnings)
    assert any(event.data.get("message") == TOKEN_LIMIT_WARNING for event in warnings)


def test_busy_cancel_and_post_cancel_generation_release_the_gate() -> None:
    streams: list[FakeStream] = []

    def factory() -> FakeStream:
        result = FakeStream(text_deltas=("chunk",))
        streams.append(result)
        return result

    generation = service(FakeInference(factory))
    first = generation.start(conversation_input())
    with pytest.raises(InferenceError) as captured:
        generation.start(conversation_input())
    assert captured.value.code is InferenceErrorCode.MODEL_BUSY
    assert generation.cancel("wrong-request") is False
    assert generation.cancel(first.request_id) is True

    first_events = list(first.events())
    assert ConversationEventType.CANCELLED in event_types(first_events)
    assert streams == []

    second_events = list(generation.start(conversation_input()).events())
    assert second_events[-1].event is ConversationEventType.COMPLETED


def test_stream_failure_is_sanitized_and_releases_the_gate() -> None:
    call_count = 0

    def factory() -> FakeStream:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return FakeStream(
                failure=InferenceError(
                    code=InferenceErrorCode.GENERATION_FAILED,
                    safe_message="Safe generation failure.",
                )
            )
        return FakeStream()

    generation = service(FakeInference(factory))
    failed = list(generation.start(conversation_input()).events())
    recovered = list(generation.start(conversation_input()).events())

    assert failed[-1].event is ConversationEventType.ERROR
    assert failed[-1].data["message"] == "Safe generation failure."
    assert recovered[-1].event is ConversationEventType.COMPLETED


def test_post_generation_summary_is_sequential_buffered_and_canonical() -> None:
    pending_streams = iter(
        (
            FakeStream(text_deltas=("<think>normal secret</think>Long original answer",)),
            FakeStream(text_deltas=("<think>summary secret</think>Short summary",)),
        )
    )
    inference = FakeInference(lambda: next(pending_streams))

    events = list(
        service(inference)
        .start(conversation_input(summary_mode=SummaryMode.POST_GENERATION))
        .events()
    )

    assert event_types(events) == [
        ConversationEventType.START,
        ConversationEventType.STATUS,
        ConversationEventType.DELTA,
        ConversationEventType.COMPLETED,
    ]
    assert events[0].data["state"] == "generating_answer"
    assert events[1].data["state"] == "summarizing_answer"
    assert events[2].data["text"] == "Short summary"
    serialized_events = repr([event.model_dump(mode="json") for event in events])
    assert "normal secret" not in serialized_events
    assert "summary secret" not in serialized_events
    assert "Long original answer" not in serialized_events

    assert len(inference.requests) == 2
    original_request, summary_request = inference.requests
    assert original_request.parameters.max_new_tokens == 128
    assert summary_request.model_key == original_request.model_key
    assert summary_request.parameters.max_new_tokens == 1024
    assert summary_request.parameters.thinking_mode is ThinkingMode.DISABLED
    assert len(summary_request.messages) == 2
    assert "Long original answer" in summary_request.messages[-1].content
    assert "first" not in summary_request.messages[-1].content
    assert "next" not in summary_request.messages[-1].content

    completed = events[-1]
    assert completed.data["assistant_message"] == {
        "role": "assistant",
        "content": "Short summary",
    }
    assert completed.data["transformation"] == {
        "summary_mode": "post_generation",
        "summary_applied": True,
        "fallback_used": False,
        "original_finish_reason": "stop",
        "summary_finish_reason": "stop",
    }
    assert "original_assistant_message" not in completed.data
    assert "summary_assistant_message" not in completed.data


@pytest.mark.parametrize(
    "summary_stream",
    [
        FakeStream(text_deltas=("partial summary",), finish_reason=FinishReason.LENGTH),
        FakeStream(text_deltas=("   ",)),
        FakeStream(text_deltas=("<think>unclosed reasoning",)),
        NoTerminalStream(),
        FakeStream(
            failure=InferenceError(
                code=InferenceErrorCode.CONTEXT_LIMIT_EXCEEDED,
                safe_message="Safe context error.",
            )
        ),
    ],
)
def test_invalid_summary_falls_back_to_original_without_leaking_partial_output(
    summary_stream: FakeStream,
) -> None:
    pending_streams = iter((FakeStream(text_deltas=("Original answer",)), summary_stream))
    inference = FakeInference(lambda: next(pending_streams))

    events = list(
        service(inference)
        .start(conversation_input(summary_mode=SummaryMode.POST_GENERATION))
        .events()
    )

    display = "".join(
        str(event.data["text"]) for event in events if event.event is ConversationEventType.DELTA
    )
    warnings = [event for event in events if event.event is ConversationEventType.WARNING]
    completed = events[-1]
    assert display == "Original answer"
    assert all("partial summary" not in repr(event.data) for event in events)
    assert any(event.data["code"] == "summary_fallback_original" for event in warnings)
    assert completed.event is ConversationEventType.COMPLETED
    assert completed.data["assistant_message"] == {
        "role": "assistant",
        "content": "Original answer",
    }
    assert completed.data["transformation"] == {
        "summary_mode": "post_generation",
        "summary_applied": False,
        "fallback_used": True,
        "original_finish_reason": "stop",
        "summary_finish_reason": None,
    }
    assert "original_assistant_message" not in completed.data
    assert "summary_assistant_message" not in completed.data


def test_cancel_between_normal_and_summary_is_not_a_fallback_or_history_result() -> None:
    inference = FakeInference(lambda: FakeStream(text_deltas=("Original answer",)))
    session = service(inference).start(conversation_input(summary_mode=SummaryMode.POST_GENERATION))
    events = session.events()

    assert next(events).event is ConversationEventType.START
    status = next(events)
    assert status.event is ConversationEventType.STATUS
    assert len(inference.requests) == 1
    session.request_cancel()
    remaining = list(events)

    assert event_types(remaining) == [ConversationEventType.CANCELLED]
    assert len(inference.requests) == 1
    assert all(event.event is not ConversationEventType.WARNING for event in remaining)
    assert session.finished
