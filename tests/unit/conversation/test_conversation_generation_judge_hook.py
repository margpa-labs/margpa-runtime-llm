"""P6-CODEX-001 `JudgeCompletionHook` wiring inside
`ConversationGenerationSession`/`ConversationGenerationService`.

This module never imports the `evaluation` package — the Hook is a plain
Callable, matching Governance/Guardrail's own decoupling pattern exactly
(see `test_conversation_generation_guardrail_hooks.py`). Default (`None`)
must reproduce `test_conversation_generation.py`'s exact behavior.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable, Iterator
from types import TracebackType

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    SEMANTIC_ENFORCEMENT_SAFE_FALLBACK,
    JudgeCompletionContext,
    JudgeCompletionDecision,
    JudgeExecutionModeSnapshot,
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
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
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
    judge_completion_hook: (
        Callable[[JudgeCompletionContext], JudgeCompletionDecision | None] | None
    ) = None,
    judge_mode_snapshot_provider: (Callable[[], str | JudgeExecutionModeSnapshot] | None) = None,
    guardrail_post_hook: Callable[[str], tuple[bool, str]] | None = None,
    text_token_counter: Callable[[str], int] | None = None,
    model_access_coordinator: ModelAccessCoordinator | None = None,
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
        judge_mode_snapshot_provider=judge_mode_snapshot_provider,
        text_token_counter=text_token_counter,
        model_access_coordinator=model_access_coordinator,
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


def test_enforce_withholds_raw_deltas_and_presents_the_repaired_decision() -> None:
    inference = FakeInference(lambda: FakeStream(text_deltas=("known ", "bad answer")))
    calls: list[JudgeCompletionContext] = []

    def _enforce(context: JudgeCompletionContext) -> JudgeCompletionDecision:
        calls.append(context)
        return JudgeCompletionDecision(
            presented_content="verified repaired answer",
            presentation_outcome="repair_accepted",
            candidate_withheld=True,
        )

    session = _service(
        inference,
        judge_completion_hook=_enforce,
        judge_mode_snapshot_provider=lambda: "enforce",
    ).start(_conversation_input(content="correct the previous claim"))
    events = list(session.events())
    final_deltas = [
        event.data["text"]
        for event in events
        if event.event is ConversationEventType.DELTA and event.data.get("channel") == "final"
    ]
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)

    assert final_deltas == ["verified repaired answer"]
    assert "known bad answer" not in "".join(str(value) for value in final_deltas)
    assert completed.data["assistant_message"] == {
        "role": "assistant",
        "content": "verified repaired answer",
    }
    assert completed.data["semantic_evaluation"] == {
        "mode": "enforce",
        "presentation_outcome": "repair_accepted",
        "candidate_withheld": True,
    }
    assert calls[0].enforce_presented_final is True
    assert calls[0].judge_mode == "enforce"


def test_enforce_hook_failure_converges_to_safe_user_facing_final() -> None:
    inference = FakeInference()

    def _explode(_context: JudgeCompletionContext) -> JudgeCompletionDecision:
        raise RuntimeError("internal judge detail")

    session = _service(
        inference,
        judge_completion_hook=_explode,
        judge_mode_snapshot_provider=lambda: "enforce",
    ).start(_conversation_input())
    events = list(session.events())
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    assert completed.data["assistant_message"] == {
        "role": "assistant",
        "content": SEMANTIC_ENFORCEMENT_SAFE_FALLBACK,
    }
    assert "internal judge detail" not in str(completed.data)


def test_off_mode_has_zero_judge_actions() -> None:
    inference = FakeInference()
    calls = 0

    def _spy(_context: JudgeCompletionContext) -> None:
        nonlocal calls
        calls += 1

    session = _service(
        inference,
        judge_completion_hook=_spy,
        judge_mode_snapshot_provider=lambda: "off",
    ).start(_conversation_input())
    events = list(session.events())
    assert any(event.event is ConversationEventType.COMPLETED for event in events)
    assert calls == 0


def test_judge_repair_and_recording_modes_are_frozen_together_at_turn_start() -> None:
    inference = FakeInference()
    current = JudgeExecutionModeSnapshot(
        judge_mode="enforce", repair_mode="enforce", recording_mode="full"
    )
    calls: list[JudgeCompletionContext] = []

    def _snapshot() -> JudgeExecutionModeSnapshot:
        return current

    def _judge(context: JudgeCompletionContext) -> JudgeCompletionDecision:
        calls.append(context)
        return JudgeCompletionDecision(
            presented_content=context.assistant_content,
            presentation_outcome="candidate_accepted",
            candidate_withheld=False,
        )

    session = _service(
        inference,
        judge_completion_hook=_judge,
        judge_mode_snapshot_provider=_snapshot,
    ).start(_conversation_input())
    current = JudgeExecutionModeSnapshot(judge_mode="off", repair_mode="off", recording_mode="off")
    list(session.events())

    assert len(calls) == 1
    assert calls[0].judge_mode == "enforce"
    assert calls[0].repair_mode == "enforce"
    assert calls[0].recording_mode == "full"


def test_slow_enforce_judge_keeps_active_request_and_user_cancel_wins_once() -> None:
    """RW8-A: Main lease release must not release Session correlation."""

    entered = threading.Event()
    returned = threading.Event()
    evidence_finalizations: list[bool] = []

    def _slow_enforce(context: JudgeCompletionContext) -> JudgeCompletionDecision:
        assert context.cancellation is not None
        entered.set()
        assert context.cancellation.wait(timeout=2.0)
        returned.set()
        return JudgeCompletionDecision(
            presented_content=SEMANTIC_ENFORCEMENT_SAFE_FALLBACK,
            presentation_outcome="safe_fallback",
            candidate_withheld=True,
            finalize_evidence=evidence_finalizations.append,
        )

    service = _service(
        FakeInference(),
        judge_completion_hook=_slow_enforce,
        judge_mode_snapshot_provider=lambda: "enforce",
    )
    session = service.start(_conversation_input())
    events: list[ConversationEvent] = []
    consumer = threading.Thread(target=lambda: events.extend(session.events()))
    consumer.start()

    assert entered.wait(timeout=2.0)
    assert service.active_request_id == session.request_id
    assert service.cancel(session.request_id) is True
    consumer.join(timeout=2.0)

    assert not consumer.is_alive()
    assert returned.is_set()
    assert service.active_request_id is None
    assert _event_types(events).count(ConversationEventType.CANCELLED) == 1
    assert ConversationEventType.COMPLETED not in _event_types(events)
    assert evidence_finalizations == [False]


def test_shutdown_during_enforce_judge_cancels_and_joins_the_active_session() -> None:
    """RW8-A: shutdown cannot report clean before synchronous Judge exits."""

    entered = threading.Event()
    returned = threading.Event()
    evidence_finalizations: list[bool] = []

    def _slow_enforce(context: JudgeCompletionContext) -> JudgeCompletionDecision:
        assert context.cancellation is not None
        entered.set()
        assert context.cancellation.wait(timeout=2.0)
        returned.set()
        return JudgeCompletionDecision(
            presented_content=SEMANTIC_ENFORCEMENT_SAFE_FALLBACK,
            presentation_outcome="safe_fallback",
            candidate_withheld=True,
            finalize_evidence=evidence_finalizations.append,
        )

    service = _service(
        FakeInference(),
        judge_completion_hook=_slow_enforce,
        judge_mode_snapshot_provider=lambda: "enforce",
    )
    session = service.start(_conversation_input())
    events: list[ConversationEvent] = []
    consumer = threading.Thread(target=lambda: events.extend(session.events()))
    consumer.start()

    assert entered.wait(timeout=2.0)
    assert service.shutdown(timeout=2.0) is True
    consumer.join(timeout=2.0)

    assert returned.is_set()
    assert not consumer.is_alive()
    assert service.active_request_id is None
    assert _event_types(events).count(ConversationEventType.CANCELLED) == 1
    assert ConversationEventType.COMPLETED not in _event_types(events)
    assert evidence_finalizations == [False]


def test_enforce_completed_terminal_is_the_only_pending_evidence_publisher() -> None:
    evidence_finalizations: list[bool] = []

    def _enforce(context: JudgeCompletionContext) -> JudgeCompletionDecision:
        return JudgeCompletionDecision(
            presented_content=context.assistant_content,
            presentation_outcome="candidate_accepted",
            candidate_withheld=False,
            finalize_evidence=evidence_finalizations.append,
        )

    session = _service(
        FakeInference(),
        judge_completion_hook=_enforce,
        judge_mode_snapshot_provider=lambda: "enforce",
    ).start(_conversation_input())

    events = list(session.events())

    assert _event_types(events).count(ConversationEventType.COMPLETED) == 1
    assert ConversationEventType.CANCELLED not in _event_types(events)
    assert evidence_finalizations == [True]


def test_slow_replacement_final_post_check_does_not_expire_pending_evidence() -> None:
    evidence_finalizations: list[bool] = []
    post_checks = 0

    def _enforce(_context: JudgeCompletionContext) -> JudgeCompletionDecision:
        return JudgeCompletionDecision(
            presented_content="replacement final",
            presentation_outcome="repair_accepted",
            candidate_withheld=True,
            finalize_evidence=evidence_finalizations.append,
        )

    def _slow_allow(_content: str) -> tuple[bool, str]:
        nonlocal post_checks
        post_checks += 1
        if post_checks == 2:
            time.sleep(0.3)
        return False, "allowed"

    session = _service(
        FakeInference(),
        judge_completion_hook=_enforce,
        judge_mode_snapshot_provider=lambda: "enforce",
        guardrail_post_hook=_slow_allow,
    ).start(_conversation_input())

    events = list(session.events())

    assert _event_types(events).count(ConversationEventType.COMPLETED) == 1
    assert evidence_finalizations == [True]


def test_rejected_replacement_final_discards_pending_evidence() -> None:
    evidence_finalizations: list[bool] = []
    post_checks = 0

    def _enforce(_context: JudgeCompletionContext) -> JudgeCompletionDecision:
        return JudgeCompletionDecision(
            presented_content="replacement final",
            presentation_outcome="repair_accepted",
            candidate_withheld=True,
            finalize_evidence=evidence_finalizations.append,
        )

    def _reject_replacement(_content: str) -> tuple[bool, str]:
        nonlocal post_checks
        post_checks += 1
        return post_checks == 2, "replacement_rejected"

    session = _service(
        FakeInference(),
        judge_completion_hook=_enforce,
        judge_mode_snapshot_provider=lambda: "enforce",
        guardrail_post_hook=_reject_replacement,
    ).start(_conversation_input())

    events = list(session.events())

    assert ConversationEventType.COMPLETED not in _event_types(events)
    assert evidence_finalizations == [False]
