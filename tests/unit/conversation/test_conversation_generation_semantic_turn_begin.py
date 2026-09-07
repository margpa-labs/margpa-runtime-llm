"""R2-WU-01 (Controller Review IR-CI-01), tightened by R3-WU-01 (Controller
Review IR-R2-01): the Evaluation Turn Context must freeze once, at
`ConversationGenerationService.start()` -- the identical Attempt boundary
`_resolve_judge_modes()`/`_resolve_runtime_snapshot()` already use -- never
lazily, on first touch, from inside a Judge Completion Hook that only runs
after generation completes (the confirmed gap: Main OFF/absent meant
nothing froze the Turn until the Judge Hook itself read Live Mode/Provider
at that later moment).

These tests pin `semantic_turn_begin_hook` at the `ConversationGeneration
Service` boundary directly (a plain `Callable[[str, JudgeExecutionMode
Snapshot], object]`, matching the `judge_completion_hook`/`runtime_
snapshot_provider` Hook shapes this module already accepts) -- no real
Model, no `runtime_governance` import (this module stays exactly as
decoupled from Runtime Governance/Judge concrete types as it already is).
R3-WU-01 passes the already-resolved `JudgeExecutionModeSnapshot` as this
Hook's own second argument (see `start()`'s own docstring) -- these Fakes
accept it positionally without inspecting its value, since this module's
own concern is purely call-timing/ordering, not the Snapshot's content."""

from __future__ import annotations

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
    JudgeExecutionModeSnapshot,
)
from margpa_runtime_llm.modules.conversation.public import (
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


class _FakeStream:
    @property
    def generation_id(self) -> str:
        return "fake-generation"

    @property
    def terminal_state(self) -> GenerationTerminalState:
        return GenerationTerminalState.ACTIVE

    @property
    def timing(self) -> GenerationTiming | None:
        return None

    def __iter__(self) -> object:
        yield GenerationChunk(
            request_id="fake-request",
            sequence=0,
            text_delta="",
            is_final=True,
            finish_reason=FinishReason.STOP,
        )

    def cancel(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __enter__(self) -> _FakeStream:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()


class _FakeInference:
    def __init__(self) -> None:
        self.requests: list[GenerationRequest] = []

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return _FakeStream()  # type: ignore[return-value]


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


def _service(**kwargs: object) -> ConversationGenerationService:
    return ConversationGenerationService(
        inference=kwargs.pop("inference", _FakeInference()),  # type: ignore[arg-type]
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key="main.bootstrap-model",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=_presentation_policy(),
        **kwargs,  # type: ignore[arg-type]
    )


def test_semantic_turn_begin_hook_fires_once_at_start_with_the_request_id() -> None:
    calls: list[str] = []
    session = _service(
        semantic_turn_begin_hook=lambda request_id, _judge_modes: calls.append(request_id)
    ).start(_conversation_input())

    assert calls == [session.request_id]


def test_semantic_turn_begin_hook_fires_before_generation_ever_starts() -> None:
    """The whole point of the fix: freezing must happen at `start()`,
    strictly before the real Model Call/Judge Hook -- never lazily deferred
    until Judge itself first asks for a Snapshot post-generation."""
    order: list[str] = []
    inference = _FakeInference()

    class _OrderTrackingInference:
        def stream(self, request: GenerationRequest) -> GenerationStream:
            order.append("generate")
            return inference.stream(request)

    session = _service(
        inference=_OrderTrackingInference(),
        semantic_turn_begin_hook=lambda _request_id, _judge_modes: order.append(
            "semantic_turn_begin"
        ),
    ).start(_conversation_input())
    list(session.events())

    assert order == ["semantic_turn_begin", "generate"]


def test_semantic_turn_begin_hook_fires_even_with_no_judge_completion_hook_wired() -> None:
    """Judge OFF/absent (no `judge_completion_hook` at all) must not gate
    the Turn-freeze boundary itself -- Main's own structural OBSERVE/
    ENFORCE independence (this Rework's own top-level invariant) requires
    the neutral Turn boundary to exist independent of Judge's presence."""
    calls: list[str] = []
    session = _service(
        semantic_turn_begin_hook=lambda request_id, _judge_modes: calls.append(request_id)
    ).start(_conversation_input())

    assert len(calls) == 1
    assert calls[0] == session.request_id


def test_semantic_turn_begin_hook_receives_the_already_resolved_judge_modes() -> None:
    """R3-WU-01 (Controller Review IR-R2-01): the Hook's own second
    argument must be the identical `JudgeExecutionModeSnapshot` `start()`
    already resolved via `_resolve_judge_modes()` -- never a placeholder,
    and never a second independent read."""
    captured: list[JudgeExecutionModeSnapshot] = []

    _service(
        semantic_turn_begin_hook=lambda _request_id, judge_modes: captured.append(judge_modes),
        judge_mode_snapshot_provider=lambda: JudgeExecutionModeSnapshot(
            judge_mode="enforce", repair_mode="off", recording_mode="full"
        ),
        judge_completion_hook=lambda _context: None,
    ).start(_conversation_input())

    assert len(captured) == 1
    assert captured[0].judge_mode == "enforce"
    assert captured[0].repair_mode == "off"
    assert captured[0].recording_mode == "full"


def test_semantic_turn_begin_hook_failure_never_blocks_the_turn() -> None:
    """A Semantic Turn freeze failure must never become a Main Model
    Runtime failure (P4-GD-005's own "Definitions absent/failure never
    blocks Main Model Runtime", extended here to the neutral Turn-freeze
    boundary Judge/Main now share as peers)."""

    def _raising_hook(_request_id: str, _judge_modes: JudgeExecutionModeSnapshot) -> None:
        raise RuntimeError("boom")

    session = _service(semantic_turn_begin_hook=_raising_hook).start(_conversation_input())
    events = list(session.events())

    assert any(event.event.value == "completed" for event in events)


def test_judge_completion_context_is_unaffected_by_the_begin_hook_wiring() -> None:
    """Wiring `semantic_turn_begin_hook` must not change any existing
    `JudgeCompletionContext` field -- this Hook exists purely to freeze the
    separate neutral Coordinator's own Turn state, never to feed anything
    back into this module's own Context shape."""
    captured: list[JudgeCompletionContext] = []

    session = _service(
        semantic_turn_begin_hook=lambda _request_id, _judge_modes: None,
        judge_completion_hook=captured.append,
    ).start(_conversation_input())
    list(session.events())

    assert len(captured) == 1
    assert captured[0].request_id == session.request_id
