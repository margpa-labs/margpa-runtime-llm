"""P6-CODEX-025 (Fourth Rework): `ConversationGenerationService` must read
`model_key` / `generation_defaults` / `effective_context_size` /
`model_runtime_info` fresh from a live `runtime_snapshot_provider` on every
`start()` call, never only once at bootstrap construction time.

Before this fix, these four values were frozen instance fields set once at
`__init__` — so a live Runtime Model Switch (via `RuntimeModelController`)
updated the Controller's own Snapshot correctly, but every subsequent Turn
still built its `GenerationRequest` with the OLD `model_key`. That stale
value then failed `InferenceService._validate_request()`'s
`runtime_info.model_key != request.model_key` check on every following
call — Chat became unusable immediately after any switch. These tests
pin the fix at the `ConversationGenerationService` boundary directly,
independent of any real Model/Controller.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from types import TracebackType

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
    RuntimeGenerationSnapshot,
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
    runtime_snapshot_provider: Callable[[], RuntimeGenerationSnapshot] | None = None,
    judge_completion_hook: Callable[[JudgeCompletionContext], None] | None = None,
) -> ConversationGenerationService:
    return ConversationGenerationService(
        inference=inference,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key="main.bootstrap-model",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=_presentation_policy(),
        judge_completion_hook=judge_completion_hook,
        runtime_snapshot_provider=runtime_snapshot_provider,
    )


def _event_types(events: list[ConversationEvent]) -> list[ConversationEventType]:
    return [event.event for event in events]


def test_no_provider_falls_back_to_the_bootstrap_model_key() -> None:
    """Backward-compatible default: identical to pre-fix behavior when no
    live Controller is wired (e.g. `runtime_model_control_enabled=False`)."""
    inference = FakeInference()
    session = _service(inference).start(_conversation_input())
    list(session.events())

    assert len(inference.requests) == 1
    assert inference.requests[0].model_key == "main.bootstrap-model"


def test_live_provider_model_key_overrides_the_bootstrap_value() -> None:
    """The central P6-CODEX-025 fix: after a live Runtime Model Switch, the
    NEXT Turn's `GenerationRequest.model_key` must reflect the Controller's
    current Snapshot, not the value frozen at construction time — otherwise
    `InferenceService._validate_request()` rejects every post-switch call."""
    inference = FakeInference()

    def _provider() -> RuntimeGenerationSnapshot:
        return RuntimeGenerationSnapshot(
            model_key="main.switched-model",
            generation_defaults=GenerationParameters(max_new_tokens=2048),
            effective_context_size=4096,
            model_runtime_info=None,
        )

    session = _service(inference, runtime_snapshot_provider=_provider).start(_conversation_input())
    list(session.events())

    assert len(inference.requests) == 1
    assert inference.requests[0].model_key == "main.switched-model"


def test_live_provider_generation_defaults_reach_the_request() -> None:
    """P6-CODEX-025 item (1): a live `generation_defaults` override (e.g.
    from a Config Control change applied via `RuntimeModelController`) must
    be the base every Turn's `GenerationParameters` is built from. (Turn
    settings always specify their own `thinking_mode` explicitly — see
    `_build_request` — so this checks a field the Turn does *not*
    override: `temperature`. `max_new_tokens` has its own dedicated
    ceiling-clamping tests below, since Architecture 5.2 makes it a real
    ceiling on the Turn's own setting, not a field the Turn simply
    replaces outright.)"""
    inference = FakeInference()

    def _provider() -> RuntimeGenerationSnapshot:
        return RuntimeGenerationSnapshot(
            model_key="main.bootstrap-model",
            generation_defaults=GenerationParameters(max_new_tokens=2048, temperature=0.33),
            effective_context_size=4096,
            model_runtime_info=None,
        )

    session = _service(inference, runtime_snapshot_provider=_provider).start(_conversation_input())
    list(session.events())

    assert inference.requests[0].parameters.temperature == 0.33


def test_runtime_max_new_tokens_ceiling_clamps_a_larger_turn_setting() -> None:
    """P6-CODEX-025 item (1), the central real-hardware regression this
    fix closes: Architecture 5.2's own formula is `request_limit <= min(
    configured_limit, ...)` — the live Runtime Override
    (`RuntimeModelController.current_max_new_tokens`, surfaced here via
    `generation_defaults.max_new_tokens`) must be a real ceiling the
    Turn's own `settings.max_new_tokens` can never exceed. Before this
    fix, the Turn's own setting always won verbatim (the Runtime Override
    was silently ignored), which a real-hardware Chat test caught
    directly: lowering Max New Tokens to 5 via the Runtime Model Control
    UI had zero effect on an actual multi-paragraph Chat answer."""
    inference = FakeInference()

    def _provider() -> RuntimeGenerationSnapshot:
        return RuntimeGenerationSnapshot(
            model_key="main.bootstrap-model",
            generation_defaults=GenerationParameters(max_new_tokens=5),
            effective_context_size=4096,
            model_runtime_info=None,
        )

    # _conversation_input()'s own ConversationSettings.max_new_tokens is
    # 128 — larger than the live Runtime ceiling of 5 above.
    session = _service(inference, runtime_snapshot_provider=_provider).start(_conversation_input())
    list(session.events())

    assert inference.requests[0].parameters.max_new_tokens == 5


def test_turn_setting_still_applies_when_smaller_than_the_runtime_ceiling() -> None:
    """The symmetric case: the Runtime ceiling never forces a Turn's own,
    already-smaller request upward — `min()`, not an outright override in
    either direction."""
    inference = FakeInference()

    def _provider() -> RuntimeGenerationSnapshot:
        return RuntimeGenerationSnapshot(
            model_key="main.bootstrap-model",
            generation_defaults=GenerationParameters(max_new_tokens=2048),
            effective_context_size=4096,
            model_runtime_info=None,
        )

    # _conversation_input()'s own ConversationSettings.max_new_tokens is
    # 128 — smaller than the live Runtime ceiling of 2048 above.
    session = _service(inference, runtime_snapshot_provider=_provider).start(_conversation_input())
    list(session.events())

    assert inference.requests[0].parameters.max_new_tokens == 128


def test_live_provider_model_key_reaches_the_judge_completion_context() -> None:
    """P6-CODEX-025 item (4): Judge/Repair/Recording Evidence must record
    the Model Identity this specific Attempt actually ran with, sourced
    from the same live Snapshot the Main Turn itself used — never an
    independently re-resolved or bootstrap-frozen value."""
    inference = FakeInference()
    captured: list[JudgeCompletionContext] = []

    def _provider() -> RuntimeGenerationSnapshot:
        return RuntimeGenerationSnapshot(
            model_key="main.switched-model",
            generation_defaults=GenerationParameters(max_new_tokens=2048),
            effective_context_size=4096,
            model_runtime_info=None,
        )

    def _spy(context: JudgeCompletionContext) -> None:
        captured.append(context)

    session = _service(
        inference, runtime_snapshot_provider=_provider, judge_completion_hook=_spy
    ).start(_conversation_input())
    list(session.events())

    assert len(captured) == 1
    assert captured[0].model_key == "main.switched-model"


def test_each_start_call_re_resolves_the_snapshot_independently() -> None:
    """Two sequential Turns after a live switch must each see the Snapshot
    current at their own `start()` time — proving the value is re-read per
    Turn, not cached from the first resolution."""
    inference = FakeInference()
    current_model_key = "main.model-a"

    def _provider() -> RuntimeGenerationSnapshot:
        return RuntimeGenerationSnapshot(
            model_key=current_model_key,
            generation_defaults=GenerationParameters(max_new_tokens=2048),
            effective_context_size=4096,
            model_runtime_info=None,
        )

    service = _service(inference, runtime_snapshot_provider=_provider)

    list(service.start(_conversation_input()).events())
    current_model_key = "main.model-b"
    list(service.start(_conversation_input()).events())

    assert [request.model_key for request in inference.requests] == [
        "main.model-a",
        "main.model-b",
    ]
