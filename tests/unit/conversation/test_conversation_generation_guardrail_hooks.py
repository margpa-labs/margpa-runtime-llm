"""Phase 5 `guardrail.input`/`guardrail.output_candidate` Hook wiring
inside `ConversationGenerationSession`/`ConversationGenerationService`
(P5-PNT-002/004, ADR-5-001, P5-F-WU-001).

This module never imports `guardrail_governance` — the hooks are plain
Callables, matching Phase 4's own `governance_pre_hook`/
`governance_post_hook` decoupling pattern exactly. Default (`None`)
hooks must reproduce the exact behavior of
`tests/unit/conversation/test_conversation_generation.py` (P5-ACC-004).
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from types import TracebackType

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
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


def _conversation_input() -> ConversationGenerationInput:
    return ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="hello"),),
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
    governance_pre_hook: Callable[[GenerationRequest], tuple[bool, str]] | None = None,
    governance_post_hook: Callable[[str], tuple[bool, str]] | None = None,
    guardrail_pre_hook: Callable[[GenerationRequest], tuple[bool, str]] | None = None,
    guardrail_post_hook: Callable[[str], tuple[bool, str]] | None = None,
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
        governance_pre_hook=governance_pre_hook,
        governance_post_hook=governance_post_hook,
        guardrail_pre_hook=guardrail_pre_hook,
        guardrail_post_hook=guardrail_post_hook,
    )


def _event_types(events: list[ConversationEvent]) -> list[ConversationEventType]:
    return [event.event for event in events]


def test_default_hooks_are_none_and_behavior_is_unchanged() -> None:
    inference = FakeInference()
    session = _service(inference).start(_conversation_input())
    events = list(session.events())
    assert _event_types(events) == [
        ConversationEventType.STATUS,
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.DELTA,
        ConversationEventType.COMPLETED,
    ]
    assert len(inference.requests) == 1


def test_pre_hook_stop_prevents_any_model_call() -> None:
    inference = FakeInference()

    def _stop(request: GenerationRequest) -> tuple[bool, str]:
        return True, "guardrail_reject_input"

    session = _service(inference, guardrail_pre_hook=_stop).start(_conversation_input())
    events = list(session.events())
    assert _event_types(events) == [
        ConversationEventType.STATUS,
        ConversationEventType.STATUS,
        ConversationEventType.ERROR,
    ]
    assert events[-1].data["code"] == "guardrail_reject_input"
    assert events[-1].data["retryable"] is False
    # Zero-Model-Call guarantee (P5-MOD-002/P5-PNT-002): `.stream()` on
    # the Model Port was never invoked.
    assert inference.requests == []


def test_pre_hook_allow_proceeds_normally() -> None:
    inference = FakeInference()

    def _allow(request: GenerationRequest) -> tuple[bool, str]:
        return False, ""

    session = _service(inference, guardrail_pre_hook=_allow).start(_conversation_input())
    events = list(session.events())
    assert ConversationEventType.COMPLETED in _event_types(events)
    assert len(inference.requests) == 1


def test_pre_hook_exception_fails_open_generation_still_proceeds() -> None:
    inference = FakeInference()

    def _explode(request: GenerationRequest) -> tuple[bool, str]:
        raise RuntimeError("guardrail bug")

    session = _service(inference, guardrail_pre_hook=_explode).start(_conversation_input())
    events = list(session.events())
    assert ConversationEventType.COMPLETED in _event_types(events)


def test_guardrail_pre_hook_runs_before_governance_pre_hook() -> None:
    # Security is the highest-priority, cheapest Fail-closed Stop
    # (architecture §6.3): when the Guardrail already stops Generation,
    # Governance must never even be consulted.
    inference = FakeInference()
    governance_calls: list[GenerationRequest] = []

    def _guardrail_stop(request: GenerationRequest) -> tuple[bool, str]:
        return True, "guardrail_reject_input"

    def _governance_spy(request: GenerationRequest) -> tuple[bool, str]:
        governance_calls.append(request)
        return False, ""

    session = _service(
        inference,
        guardrail_pre_hook=_guardrail_stop,
        governance_pre_hook=_governance_spy,
    ).start(_conversation_input())
    events = list(session.events())
    assert events[-1].data["code"] == "guardrail_reject_input"
    assert governance_calls == []
    assert inference.requests == []


def test_post_hook_reject_replaces_completed_with_error_never_a_new_shape() -> None:
    inference = FakeInference()

    def _reject(content: str) -> tuple[bool, str]:
        assert content == "answer"
        return True, "guardrail_reject_output"

    session = _service(inference, guardrail_post_hook=_reject).start(_conversation_input())
    events = list(session.events())
    assert _event_types(events) == [
        ConversationEventType.STATUS,
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.DELTA,
        ConversationEventType.ERROR,
    ]
    assert ConversationEventType.COMPLETED not in _event_types(events)
    assert events[-1].data["code"] == "guardrail_reject_output"
    assert events[-1].data["retryable"] is False
    # No Ghost Completion / unauthorized content surface anywhere in the
    # rejected terminal event (P5-ACC-020-equivalent guarantee).
    assert "assistant_message" not in events[-1].data


def test_post_hook_allow_completes_normally_with_the_real_content() -> None:
    inference = FakeInference()

    def _allow(content: str) -> tuple[bool, str]:
        return False, ""

    session = _service(inference, guardrail_post_hook=_allow).start(_conversation_input())
    events = list(session.events())
    completed = next(e for e in events if e.event is ConversationEventType.COMPLETED)
    assert completed.data["assistant_message"] == {"role": "assistant", "content": "answer"}


def test_post_hook_exception_fails_open_completion_still_delivered() -> None:
    inference = FakeInference()

    def _explode(content: str) -> tuple[bool, str]:
        raise RuntimeError("guardrail bug")

    session = _service(inference, guardrail_post_hook=_explode).start(_conversation_input())
    events = list(session.events())
    assert ConversationEventType.COMPLETED in _event_types(events)


def test_guardrail_post_hook_runs_after_governance_post_hook() -> None:
    # ADR-5-001 "Main Governance Allow never overrides Safety Deny":
    # Governance Post-check runs first; only once it allows does the
    # Guardrail get the final say as the last gate before commit.
    inference = FakeInference()
    guardrail_calls: list[str] = []

    def _governance_reject(content: str) -> tuple[bool, str]:
        return True, "governance_reject_output"

    def _guardrail_spy(content: str) -> tuple[bool, str]:
        guardrail_calls.append(content)
        return False, ""

    session = _service(
        inference,
        governance_post_hook=_governance_reject,
        guardrail_post_hook=_guardrail_spy,
    ).start(_conversation_input())
    events = list(session.events())
    assert events[-1].data["code"] == "governance_reject_output"
    assert guardrail_calls == []


def test_guardrail_post_hook_is_consulted_when_governance_allows() -> None:
    inference = FakeInference()

    def _governance_allow(content: str) -> tuple[bool, str]:
        return False, ""

    def _guardrail_reject(content: str) -> tuple[bool, str]:
        return True, "guardrail_reject_output"

    session = _service(
        inference,
        governance_post_hook=_governance_allow,
        guardrail_post_hook=_guardrail_reject,
    ).start(_conversation_input())
    events = list(session.events())
    assert events[-1].data["code"] == "guardrail_reject_output"
