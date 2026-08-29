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


def _conversation_input(
    *, content: str = "hello", response_language: ResponseLanguage = ResponseLanguage.JA
) -> ConversationGenerationInput:
    return ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content=content),),
        settings=ConversationSettings(
            response_language=response_language,
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
    request_correlation_begin: Callable[[str, str], None] | None = None,
    request_correlation_terminal: Callable[[str, str, str], None] | None = None,
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
        request_correlation_begin=request_correlation_begin,
        request_correlation_terminal=request_correlation_terminal,
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


def test_judge_hook_response_language_auto_resolves_to_ja_for_japanese_input() -> None:
    """P6-RR-R18-WU-004..006 (Post-Claude Independent Review Rework,
    resolves P6-CODEX-083): `ResponseLanguage.AUTO` must not collapse to
    `en` regardless of the User's actual input language — the previous
    `is JA -> ja else en` binary check did exactly that. A Japanese User
    Turn with AUTO must resolve the Hook Context's `response_language`
    to `ja`."""
    inference = FakeInference()
    calls: list[JudgeCompletionContext] = []

    def _spy(context: JudgeCompletionContext) -> None:
        calls.append(context)

    session = _service(inference, judge_completion_hook=_spy).start(
        _conversation_input(
            content="今日の天気を教えてください", response_language=ResponseLanguage.AUTO
        )
    )
    list(session.events())

    assert len(calls) == 1
    assert calls[0].response_language == "ja"


def test_judge_hook_response_language_auto_resolves_to_en_for_english_input() -> None:
    """The converse of the above: AUTO with an English User Turn must
    resolve to `en`, not just default there incidentally."""
    inference = FakeInference()
    calls: list[JudgeCompletionContext] = []

    def _spy(context: JudgeCompletionContext) -> None:
        calls.append(context)

    session = _service(inference, judge_completion_hook=_spy).start(
        _conversation_input(
            content="What is today's weather?", response_language=ResponseLanguage.AUTO
        )
    )
    list(session.events())

    assert len(calls) == 1
    assert calls[0].response_language == "en"


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


def test_request_correlation_begin_fires_before_judge_hook_with_the_turn_request_id() -> None:
    """P6-RR-R19-WU-001..004 (Post-Claude Independent Review Rework,
    resolves P6-CODEX-082): the Begin Hook must fire at Turn start —
    before Judge (or Recording) ever runs — with exactly this Turn's own
    `request_id`, so a concurrent Status reader's "Current" anchor is
    valid from the very first moment of the Turn, not only after it
    completes."""
    inference = FakeInference()
    begin_calls: list[tuple[str, str]] = []
    order: list[str] = []

    def _on_begin(request_id: str, started_at: str) -> None:
        begin_calls.append((request_id, started_at))
        order.append("begin")

    def _judge_hook(context: JudgeCompletionContext) -> None:
        order.append("judge")

    session = _service(
        inference,
        judge_completion_hook=_judge_hook,
        request_correlation_begin=_on_begin,
    ).start(_conversation_input())
    list(session.events())

    assert len(begin_calls) == 1
    assert begin_calls[0][0] == session.request_id
    assert begin_calls[0][1]  # a non-empty ISO timestamp
    assert order == ["begin", "judge"]


def test_request_correlation_terminal_fires_once_completed_for_a_normal_turn() -> None:
    inference = FakeInference()
    terminal_calls: list[tuple[str, str, str]] = []

    session = _service(
        inference,
        request_correlation_terminal=lambda rid, status, at: terminal_calls.append(
            (rid, status, at)
        ),
    ).start(_conversation_input())
    list(session.events())

    assert len(terminal_calls) == 1
    assert terminal_calls[0][0] == session.request_id
    assert terminal_calls[0][1] == "completed"
    assert terminal_calls[0][2]


def test_request_correlation_terminal_fires_failed_when_guardrail_rejects() -> None:
    inference = FakeInference()
    terminal_calls: list[tuple[str, str, str]] = []

    def _reject(content: str) -> tuple[bool, str]:
        return True, "guardrail_reject_output"

    session = _service(
        inference,
        guardrail_post_hook=_reject,
        request_correlation_terminal=lambda rid, status, at: terminal_calls.append(
            (rid, status, at)
        ),
    ).start(_conversation_input())
    list(session.events())

    assert len(terminal_calls) == 1
    assert terminal_calls[0][1] == "failed"


def test_request_correlation_terminal_fires_cancelled_when_the_user_cancels() -> None:
    entered = threading.Event()
    terminal_calls: list[tuple[str, str, str]] = []

    def _slow_enforce(context: JudgeCompletionContext) -> JudgeCompletionDecision:
        assert context.cancellation is not None
        entered.set()
        assert context.cancellation.wait(timeout=2.0)
        return JudgeCompletionDecision(
            presented_content=SEMANTIC_ENFORCEMENT_SAFE_FALLBACK,
            presentation_outcome="safe_fallback",
            candidate_withheld=True,
            finalize_evidence=lambda _published: None,
        )

    service = _service(
        FakeInference(),
        judge_completion_hook=_slow_enforce,
        judge_mode_snapshot_provider=lambda: "enforce",
        request_correlation_terminal=lambda rid, status, at: terminal_calls.append(
            (rid, status, at)
        ),
    )
    session = service.start(_conversation_input())
    events: list[ConversationEvent] = []
    consumer = threading.Thread(target=lambda: events.extend(session.events()))
    consumer.start()

    assert entered.wait(timeout=2.0)
    assert service.cancel(session.request_id) is True
    consumer.join(timeout=2.0)

    assert not consumer.is_alive()
    assert len(terminal_calls) == 1
    assert terminal_calls[0] == (session.request_id, "cancelled", terminal_calls[0][2])


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
        "content": (
            "回答を安全に検証できなかったため、表示を保留しました。"
            "再試行するか、信頼できる情報源で確認してください。"
        ),
    }
    assert "internal judge detail" not in str(completed.data)


def test_enforce_hook_failure_with_auto_and_japanese_input_uses_the_japanese_fallback() -> None:
    """P6-RR-R18-WU-004..006 (resolves P6-CODEX-083): the previous
    `is JA -> ja else en` binary check would have shown the *English*
    Safe Fallback here even though this Turn's own User Input is
    Japanese and `response_language` is AUTO — the exact regression this
    Package closes."""
    inference = FakeInference()

    def _explode(_context: JudgeCompletionContext) -> JudgeCompletionDecision:
        raise RuntimeError("internal judge detail")

    session = _service(
        inference,
        judge_completion_hook=_explode,
        judge_mode_snapshot_provider=lambda: "enforce",
    ).start(
        _conversation_input(
            content="今日の天気を教えてください", response_language=ResponseLanguage.AUTO
        )
    )
    events = list(session.events())
    completed = next(event for event in events if event.event is ConversationEventType.COMPLETED)
    assert completed.data["assistant_message"] == {
        "role": "assistant",
        "content": (
            "回答を安全に検証できなかったため、表示を保留しました。"
            "再試行するか、信頼できる情報源で確認してください。"
        ),
    }
    assert completed.data["assistant_message"]["content"] != SEMANTIC_ENFORCEMENT_SAFE_FALLBACK


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
