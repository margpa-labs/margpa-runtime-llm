"""End-to-end wiring of the real `guardrail_governance` Incremental
Stream Guard through `ConversationGenerationSession`'s
`guardrail_stream_guard_factory` seam (P5-PNT-003, ADR-5-006,
P5-F-WU-001, P5-ACC-013/022).

Unlike `tests/unit/conversation/test_conversation_generation_guardrail_hooks.py`
(which keeps the Conversation module fully decoupled behind plain
Callables), this test deliberately crosses the module boundary and
wires the genuine `IncrementalStreamGuard` — the two modules only ever
cooperate through the `GuardrailStreamGuardLike` Protocol, never a
direct import inside `conversation_generation.py` itself.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from types import TracebackType

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    GuardrailStreamGuardFactory,
)
from margpa_runtime_llm.modules.conversation.public import (
    ConversationEvent,
    ConversationEventType,
    ConversationGenerationInput,
    ConversationGenerationService,
    ConversationGenerationSession,
    ConversationMessage,
    ConversationRole,
    ConversationSettings,
)
from margpa_runtime_llm.modules.guardrail_governance.application import IncrementalStreamGuard
from margpa_runtime_llm.modules.guardrail_governance.domain import (
    CATEGORY_SECRET,
    CATEGORY_UNKNOWN_UNRESOLVED,
    DetectionOutcome,
    GuardDetection,
    Severity,
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


class _MarkerDetector:
    """Minimal `DetectorPort` fixture: MATCHes on one fixed substring."""

    detector_id = "test.marker"

    def __init__(self, marker: str = "secret-marker") -> None:
        self._marker = marker
        self.max_match_length = len(marker)

    def detect(self, *, content: str) -> GuardDetection:
        if self._marker in content.lower():
            return GuardDetection(
                detection_id="test-detection-match",
                detector_id=self.detector_id,
                category_id=CATEGORY_SECRET,
                outcome=DetectionOutcome.MATCH,
                severity=Severity.HIGH,
            )
        return GuardDetection(
            detection_id="test-detection-clear",
            detector_id=self.detector_id,
            category_id=CATEGORY_UNKNOWN_UNRESOLVED,
            outcome=DetectionOutcome.CLEAR,
        )


class FakeStream:
    def __init__(
        self,
        *,
        text_deltas: tuple[str, ...] = ("answer",),
        on_second_chunk_pulled: Callable[[], None] | None = None,
    ) -> None:
        self.text_deltas = text_deltas
        self.cancelled = False
        self.closed = False
        # Fires the instant the *second* Chunk is pulled from this Stream
        # — lets a Test simulate a Cancel arriving strictly between two
        # Chunks, without a real background thread (P5-CODEX-004 item 5).
        self._on_second_chunk_pulled = on_second_chunk_pulled

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
            if sequence == 1 and self._on_second_chunk_pulled is not None:
                self._on_second_chunk_pulled()
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
    def __init__(self, factory: Callable[[], GenerationStream]) -> None:
        self.factory = factory
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


def _conversation_input_with_thinking(
    *, visibility: ThinkingVisibility
) -> ConversationGenerationInput:
    return ConversationGenerationInput(
        messages=(ConversationMessage(role=ConversationRole.USER, content="hello"),),
        settings=ConversationSettings(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_mode=ThinkingMode.ENABLED,
            thinking_visibility=visibility,
        ),
    )


def _service(
    inference: FakeInference,
    *,
    guardrail_stream_guard_factory: GuardrailStreamGuardFactory | None = None,
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
        guardrail_stream_guard_factory=guardrail_stream_guard_factory,
    )


def _delta_texts(events: list[ConversationEvent]) -> list[str]:
    return [
        str(event.data["text"]) for event in events if event.event is ConversationEventType.DELTA
    ]


def test_clean_stream_with_stream_guard_active_still_delivers_full_content() -> None:
    inference = FakeInference(factory=lambda: FakeStream(text_deltas=("Hello, ", "World!")))
    session = _service(
        inference,
        guardrail_stream_guard_factory=lambda: IncrementalStreamGuard(
            detectors=(_MarkerDetector(),)
        ),
    ).start(_conversation_input())
    events = list(session.events())
    assert "".join(_delta_texts(events)) == "Hello, World!"
    completed = next(e for e in events if e.event is ConversationEventType.COMPLETED)
    assert completed.data["assistant_message"] == {"role": "assistant", "content": "Hello, World!"}


def test_pattern_split_exactly_across_two_stream_chunks_is_still_caught() -> None:
    # The Marker "secret-marker" never appears whole in either individual
    # Chunk — only the Guard's full-buffer re-scan on every `feed()` call
    # can catch it (the Cross-chunk-split adversarial case, P5-ACC-013).
    inference = FakeInference(factory=lambda: FakeStream(text_deltas=("SECRET-MAR", "KER world")))
    session = _service(
        inference,
        guardrail_stream_guard_factory=lambda: IncrementalStreamGuard(
            detectors=(_MarkerDetector(),)
        ),
    ).start(_conversation_input())
    events = list(session.events())
    assert [e.event for e in events] == [
        ConversationEventType.STATUS,
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.ERROR,
    ]
    # Not even a partial Fragment of the Matched buffer was ever released
    # to the client before Termination (P5-ACC-014 Ghost-Completion
    # prevention equivalent for Streaming).
    assert _delta_texts(events) == []
    assert events[-1].data["code"] == CATEGORY_SECRET
    assert events[-1].data["retryable"] is False


def test_no_factory_supplied_is_byte_identical_to_pre_phase_5_behavior() -> None:
    inference = FakeInference(factory=lambda: FakeStream(text_deltas=("SECRET-MARKER world",)))
    session = _service(inference).start(_conversation_input())
    events = list(session.events())
    # With no Stream Guard wired in at all (`None` factory, the default),
    # even content that would otherwise Match is delivered unmodified —
    # P5-ACC-004's byte-identical-when-OFF guarantee.
    assert "".join(_delta_texts(events)) == "SECRET-MARKER world"
    assert any(e.event is ConversationEventType.COMPLETED for e in events)


def test_cancel_between_chunks_never_releases_the_held_back_prefix() -> None:
    # P5-CODEX-004 item 5: a Cancel/Disconnect arriving strictly between
    # two Chunks must never surface whatever the Stream Guard was still
    # holding back — `_run_stage()` converges straight to `cancelled`
    # without ever calling `finalize()`, so the Held-back content is
    # simply discarded, never leaked.
    session_holder: list[ConversationGenerationSession] = []

    def _cancel_now() -> None:
        session_holder[0].request_cancel()

    inference = FakeInference(
        factory=lambda: FakeStream(
            text_deltas=("clean text", "more clean text"),
            on_second_chunk_pulled=_cancel_now,
        )
    )

    # A 50-char Marker (never present) drives `max_match_length=50`, well
    # past the 10-char first Chunk — nothing from it can be released
    # before the Guard sees more content than it is willing to Holdback.
    def _guard_factory() -> IncrementalStreamGuard:
        return IncrementalStreamGuard(detectors=(_MarkerDetector(marker="x" * 50),))

    session = _service(inference, guardrail_stream_guard_factory=_guard_factory).start(
        _conversation_input()
    )
    session_holder.append(session)
    events = list(session.events())
    assert [e.event for e in events] == [
        ConversationEventType.STATUS,
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.CANCELLED,
    ]
    assert _delta_texts(events) == []


def test_concurrent_turns_each_get_an_independent_stream_guard() -> None:
    # P5-CODEX-004 item 5 / P5-ACC-022: each `_run_stage()` Call
    # constructs its own fresh Guard via the Factory — feeding one
    # Turn's Guard must never influence another's Holdback/Termination
    # State, proven here by literally running two Turns through the
    # *same* Factory and confirming their outcomes never cross.
    def guard_factory() -> IncrementalStreamGuard:
        return IncrementalStreamGuard(detectors=(_MarkerDetector(),))

    clean_inference = FakeInference(factory=lambda: FakeStream(text_deltas=("clean answer",)))
    clean_session = _service(clean_inference, guardrail_stream_guard_factory=guard_factory).start(
        _conversation_input()
    )
    matching_inference = FakeInference(
        factory=lambda: FakeStream(text_deltas=("secret-marker leaked",))
    )
    matching_session = _service(
        matching_inference, guardrail_stream_guard_factory=guard_factory
    ).start(_conversation_input())

    clean_events = list(clean_session.events())
    matching_events = list(matching_session.events())

    assert "".join(_delta_texts(clean_events)) == "clean answer"
    assert any(e.event is ConversationEventType.COMPLETED for e in clean_events)

    assert [e.event for e in matching_events] == [
        ConversationEventType.STATUS,
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.ERROR,
    ]
    assert _delta_texts(matching_events) == []


def test_visible_reasoning_leaking_a_secret_is_caught_by_its_own_stream_guard() -> None:
    # P5-CODEX-009 Rework (Codex Second Independent Review item 3): the
    # previous unconditional `kind is ThinkingContentKind.REASONING`
    # exemption in `_emit_guarded()` skipped the Stream Guard for
    # Reasoning content in every Mode, including `enforce` — but only
    # when Thinking Visibility is VISIBLE does Reasoning ever actually
    # reach a real client at all (HIDDEN Reasoning never even becomes a
    # semantic Delta, see the sibling test below). That combination was
    # exactly the leak: content genuinely streamed to the client, never
    # scanned. Here the Secret sits entirely inside the `<think>...</think>`
    # block, never in the visible Final answer.
    inference = FakeInference(
        factory=lambda: FakeStream(
            text_deltas=("<think>leaked secret-marker here</think>", "final answer")
        )
    )
    session = _service(
        inference,
        guardrail_stream_guard_factory=lambda: IncrementalStreamGuard(
            detectors=(_MarkerDetector(),)
        ),
    ).start(_conversation_input_with_thinking(visibility=ThinkingVisibility.VISIBLE))
    events = list(session.events())
    assert [e.event for e in events] == [
        ConversationEventType.STATUS,
        ConversationEventType.STATUS,
        ConversationEventType.START,
        ConversationEventType.ERROR,
    ]
    # Neither the Reasoning fragment nor the Final answer that followed
    # it ever reached the client — a genuine Match anywhere in the
    # Stream converges on one Fail-closed Stop for the whole Stage.
    assert _delta_texts(events) == []
    assert events[-1].data["code"] == CATEGORY_SECRET
    assert inference.requests[0] is not None


def test_hidden_reasoning_with_a_secret_never_reaches_any_stream_guard_at_all() -> None:
    # The companion guarantee the fix above must not break (P5-CODEX-009
    # "Hidden Reasoningは非表示・非永続の既存契約を維持する"): when
    # Visibility is HIDDEN, `ThinkingPresentationSession._visible_
    # semantic_deltas()` filters Reasoning-kind segments out *before*
    # `_emit_guarded()` ever sees them — so a Secret sitting only inside
    # Hidden Reasoning must neither leak (it never becomes a Delta at
    # all) nor spuriously trip the Guard/terminate the Stage.
    inference = FakeInference(
        factory=lambda: FakeStream(
            text_deltas=("<think>leaked secret-marker here</think>", "final answer")
        )
    )
    session = _service(
        inference,
        guardrail_stream_guard_factory=lambda: IncrementalStreamGuard(
            detectors=(_MarkerDetector(),)
        ),
    ).start(_conversation_input_with_thinking(visibility=ThinkingVisibility.HIDDEN))
    events = list(session.events())
    assert "".join(_delta_texts(events)) == "final answer"
    completed = next(e for e in events if e.event is ConversationEventType.COMPLETED)
    assert completed.data["assistant_message"] == {"role": "assistant", "content": "final answer"}


def test_stream_guard_summary_hook_is_called_once_with_the_terminal_match_count() -> None:
    # P5-CODEX-009 Rework item 2: the Stage's Terminal Stream Guard
    # Summary must reach `guardrail_stream_result_hook` exactly once,
    # carrying the real Match/Detection Counts — this is the mechanism
    # `GuardrailGovernanceComposition.record_stream_guard_summary()`
    # turns into the `guardrail.stream_candidate` Status/Evidence Point
    # a Client can actually observe (previously nothing ever routed a
    # Stream's outcome there at all).
    inference = FakeInference(factory=lambda: FakeStream(text_deltas=("clean answer",)))
    summaries: list[object] = []
    service = ConversationGenerationService(
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
        guardrail_stream_guard_factory=lambda: IncrementalStreamGuard(
            detectors=(_MarkerDetector(),)
        ),
        guardrail_stream_result_hook=summaries.append,
    )
    events = list(service.start(_conversation_input()).events())
    assert any(e.event is ConversationEventType.COMPLETED for e in events)
    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.detection_count >= 1  # type: ignore[attr-defined]
    assert summary.match_count == 0  # type: ignore[attr-defined]
    assert summary.terminated is False  # type: ignore[attr-defined]


def test_stream_guard_summary_hook_reports_termination_on_a_genuine_match() -> None:
    inference = FakeInference(factory=lambda: FakeStream(text_deltas=("secret-marker leaked",)))
    summaries: list[object] = []
    service = ConversationGenerationService(
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
        guardrail_stream_guard_factory=lambda: IncrementalStreamGuard(
            detectors=(_MarkerDetector(),)
        ),
        guardrail_stream_result_hook=summaries.append,
    )
    events = list(service.start(_conversation_input()).events())
    assert any(e.event is ConversationEventType.ERROR for e in events)
    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.terminated is True  # type: ignore[attr-defined]
    assert summary.match_count == 1  # type: ignore[attr-defined]
