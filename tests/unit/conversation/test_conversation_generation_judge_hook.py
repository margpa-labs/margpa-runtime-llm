"""P6-CODEX-001 `JudgeCompletionHook` wiring inside
`ConversationGenerationSession`/`ConversationGenerationService`.

This module never imports the `evaluation` package — the Hook is a plain
Callable, matching Governance/Guardrail's own decoupling pattern exactly
(see `test_conversation_generation_guardrail_hooks.py`). Default (`None`)
must reproduce `test_conversation_generation.py`'s exact behavior.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from types import TracebackType

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
)
from margpa_runtime_llm.modules.conversation.public import (
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
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
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
    def __init__(
        self,
        *,
        text_deltas: tuple[str, ...] = ("answer",),
        usage: TokenUsage | None = None,
    ) -> None:
        self.text_deltas = text_deltas
        self.usage = usage
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
            usage=self.usage,
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


def _service(
    inference: FakeInference,
    *,
    judge_completion_hook: Callable[[JudgeCompletionContext], None] | None = None,
    guardrail_post_hook: Callable[[str], tuple[bool, str]] | None = None,
    text_token_counter: Callable[[str], int] | None = None,
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
        guardrail_post_hook=guardrail_post_hook,
        judge_completion_hook=judge_completion_hook,
        text_token_counter=text_token_counter,
    )


def _event_types(events: list[ConversationEvent]) -> list[ConversationEventType]:
    return [event.event for event in events]


def test_judge_hook_is_not_called_when_none() -> None:
    # Default behavior (no Hook wired at all, e.g. Feature Modes disabled)
    # must be identical to before this Hook existed.
    inference = FakeInference()
    session = _service(inference).start(_conversation_input())
    events = list(session.events())
    assert ConversationEventType.COMPLETED in _event_types(events)


def test_judge_hook_receives_the_correlated_request_user_input_and_answer() -> None:
    inference = FakeInference()
    calls: list[JudgeCompletionContext] = []

    def _spy(context: JudgeCompletionContext) -> None:
        calls.append(context)

    session = _service(inference, judge_completion_hook=_spy).start(
        _conversation_input(content="what is 2+2?")
    )
    events = list(session.events())
    completed = next(e for e in events if e.event is ConversationEventType.COMPLETED)

    assert len(calls) == 1
    assert calls[0].request_id == session.request_id
    assert calls[0].user_input == "what is 2+2?"
    assert calls[0].assistant_content == "answer"
    # Judge never affects the Canonical content (P6-ACC-018/P6-CODEX-001).
    assert completed.data["assistant_message"] == {"role": "assistant", "content": "answer"}


def test_judge_hook_is_never_called_when_guardrail_post_check_rejects() -> None:
    inference = FakeInference()
    calls: list[JudgeCompletionContext] = []

    def _spy(context: JudgeCompletionContext) -> None:
        calls.append(context)

    def _reject(content: str) -> tuple[bool, str]:
        return True, "guardrail_reject_output"

    session = _service(inference, judge_completion_hook=_spy, guardrail_post_hook=_reject).start(
        _conversation_input()
    )
    events = list(session.events())

    assert ConversationEventType.COMPLETED not in _event_types(events)
    assert calls == []


def test_judge_hook_exception_never_breaks_the_completed_event() -> None:
    inference = FakeInference()

    def _explode(context: JudgeCompletionContext) -> None:
        raise RuntimeError("judge bug")

    session = _service(inference, judge_completion_hook=_explode).start(_conversation_input())
    events = list(session.events())
    completed = next(e for e in events if e.event is ConversationEventType.COMPLETED)
    assert completed.data["assistant_message"] == {"role": "assistant", "content": "answer"}


def test_context_usage_token_counting_runs_before_the_judge_hook_fires() -> None:
    """Real-hardware regression (P6-CODEX-006/007): this Turn's own
    `_context_usage()` call and a background Judge Thread both need the
    shared Model Backend's single generation lock. Firing the Judge Hook
    before `_context_usage()` finishes raced the Judge Thread against this
    same Turn's own token count and could turn a successful completion into
    a spurious model_busy error. The Judge Hook must fire last."""
    usage = TokenUsage(prompt_tokens=100, completion_tokens=20, total_tokens=120)
    inference = FakeInference(lambda: FakeStream(usage=usage))
    call_order: list[str] = []

    def _counter(text: str) -> int:
        call_order.append("token_counter")
        return len(text)

    def _judge(context: JudgeCompletionContext) -> None:
        call_order.append("judge_hook")

    session = _service(inference, judge_completion_hook=_judge, text_token_counter=_counter).start(
        _conversation_input()
    )
    events = list(session.events())
    completed = next(e for e in events if e.event is ConversationEventType.COMPLETED)

    # The default Response Language policy always prepends a System
    # instruction message, so _context_usage()'s SYSTEM-role branch (and
    # therefore the token counter) is exercised on every real Turn.
    assert "token_counter" in call_order
    assert call_order.index("token_counter") < call_order.index("judge_hook")
    assert completed.data["assistant_message"] == {"role": "assistant", "content": "answer"}


def test_context_usage_degrades_gracefully_when_the_token_counter_is_busy() -> None:
    """Defense in depth: even if the shared lock is transiently busy for
    an unrelated reason, the already-succeeded completion must not fail."""
    usage = TokenUsage(prompt_tokens=100, completion_tokens=20, total_tokens=120)
    inference = FakeInference(lambda: FakeStream(usage=usage))

    def _busy_counter(text: str) -> int:
        raise RuntimeError("model_busy")

    session = _service(inference, text_token_counter=_busy_counter).start(_conversation_input())
    events = list(session.events())
    completed = next(e for e in events if e.event is ConversationEventType.COMPLETED)
    assert completed.data["assistant_message"] == {"role": "assistant", "content": "answer"}
