"""Controller Review (2026-09-04 22:41, P2/IR-R2-02; and 2026-09-04 23:54,
IR-R3-03) fix: proves the real production save path -- Conversation ->
Judge Hook -> Repair -> same-condition Rejudge -> the SAME Turn's
persisted final answer -- actually works end to end, with a Fixture Model
(never real hardware), for BOTH real Repair authorization origins: the
pre-existing Judge-side Repair Mode ENFORCE path, and Main Runtime
Governance's own independent ENFORCE authorization
(`repair_requested_by == "main_governance"`, `repair_mode` OFF on the
Judge side, matching `test_real_local_main_governance_origin_repair_
smoke.py`'s own real-hardware wiring, here driven through the full
`ConversationGenerationService`/`PersistentConversationService` pipeline
instead of a Hook-direct call).

Before the P2/IR-R2-02 fix, the only coverage that came close was two
separate halves that never touched the real `PersistentConversationService`
save path together: `test_real_local_main_governance_origin_repair_
smoke.py`'s Hook-direct Test calls `build_judge_completion_hook()`'s
returned callable directly (never through a real `ConversationGeneration
Service`/`PersistentConversationService`), and its persistence Test calls
`attempt_live_repair()` directly with `persist_accepted_attempt=True` (a
distinct, Executor-driven REPAIR-origin Turn, never the same-Turn
in-place replacement the normal ENFORCE Conversation path actually uses).

The real production shape (`conversation_generation.py`'s `_completed_
event()` -> `judge_live_integration.py`'s Dispatch, which always passes
`persist_accepted_attempt=not context.enforce_presented_final` -- `False`
for the normal synchronous ENFORCE path) never creates a second Turn at
all: `attempt_live_repair()` only returns the corrected text as
`presented_content`, and it is `PersistentConversationService.generate_
turn()`'s own `complete_generation()` call (fed by the Conversation
Session's COMPLETED event, whose `assistant_message.content` `_completed_
event()` already swapped in) that persists it -- into the SAME Turn the
Conversation started, never a new one. This module drives exactly that
real chain, through `PersistentConversationService.generate_turn()`, never
substituting a direct Executor call for it.

Controller Review (2026-09-04 23:54, IR-R3-03) finding: the P2 Tests
below the module docstring boundary (added for IR-R2-02) all wired
`judge_mode="enforce"`/`repair_mode="enforce"` on the Judge side with
`semantic_result_recorder=lambda response: None` -- Controller's own
in-memory Probe against that exact wiring showed `repair_requested_by`
came back `"judge"`, never `"main_governance"`, so those Tests proved the
Judge-origin path's own same-Turn save, not a Main-origin one. Those
Tests are kept unchanged below (still real, still valid coverage of the
Judge-origin path); the NEW Tests further down add the missing Main-
origin coverage with a real `RuntimeGovernanceComposition`/`Semantic
RuntimeCoordinator` wired to the real `semantic_result_recorder`, `repair_
mode="off"` on the Judge side (so only Main Governance's own ENFORCE
decision can authorize the Repair), asserting `repair_requested_by ==
"main_governance"` directly off the real `JudgeGovernanceComposition`
this module's builder now also returns.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from functools import partial
from pathlib import Path
from types import TracebackType

import pytest

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
from margpa_runtime_llm.bootstrap.judge_live_integration import (
    JudgeGovernanceComposition,
    build_judge_completion_hook,
)
from margpa_runtime_llm.bootstrap.repair_live_integration import attempt_live_repair
from margpa_runtime_llm.bootstrap.runtime_governance import (
    RuntimeGovernanceComposition,
    SemanticRuntimeBindingContext,
)
from margpa_runtime_llm.modules.conversation.adapters import SQLiteConversationStore
from margpa_runtime_llm.modules.conversation.application import (
    PersistentConversationService,
    PersistentGenerationIdentities,
)
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeExecutionModeSnapshot,
)
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEventType,
    ConversationSettings,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationMessageId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSessionId,
    ConversationTurnId,
    ConversationTurnOrigin,
    ConversationTurnState,
)
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationChunk,
    GenerationParameters,
    GenerationRequest,
    GenerationResult,
    GenerationStream,
    GenerationTerminalState,
    GenerationTiming,
    ThinkingMode,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelRuntimeReference
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.runtime_governance.application import (
    SemanticRuntimeCoordinator,
    freeze_semantic_turn,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    RuntimeCapabilitySnapshot,
    SemanticCriterion,
    SemanticEvaluationMethod,
    SemanticEvaluationStage,
    SemanticProviderState,
)
from margpa_runtime_llm.modules.summarization.public import SummaryMode

SCOPE = ConversationScopeId(value="scope-private")
CID = ConversationId(value="conversation-1")
_JUDGE_MODEL_KEY = "judge.test-model"
_MAIN_MODEL_KEY = "main.test-model"
_WRONG_ANSWER = "The capital of France is Tenon."
_CORRECTED_ANSWER = "The capital of France is Paris."
_RUNTIME_REF = ModelRuntimeReference(
    load_instance_id="load-1",
    model_key=_JUDGE_MODEL_KEY,
    backend_key="fake",
    backend_version="0.0.0",
    definition_file_sha512="a" * 128,
)


class _Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 9, 4, tzinfo=UTC)

    def __call__(self) -> datetime:
        self.value += timedelta(seconds=1)
        return self.value


class _FakeStream:
    """Mirrors `test_conversation_generation_judge_hook.py`'s own
    `FakeStream` -- the Main Candidate's streaming Generation port."""

    def __init__(self, *, text_deltas: tuple[str, ...]) -> None:
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
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )

    def cancel(self) -> None:
        self.cancelled = True

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> _FakeStream:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self.cancelled:
            self.close()


class _MainInference:
    """The real Candidate the Turn actually generates -- deliberately the
    known-wrong `_WRONG_ANSWER`, so a genuine Repair is required."""

    def __init__(self, *, answer: str = _WRONG_ANSWER) -> None:
        self.answer = answer
        self.requests: list[GenerationRequest] = []

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return _FakeStream(text_deltas=(self.answer,))


class _JudgeRepairService:
    """The `InferenceService`-shaped Fixture backing the Judge Hook's own
    `service=` -- used for the Main-shared batched Initial Judge dispatch
    AND (via `attempt_live_repair`'s own `service=`) the Repair Candidate
    and Rejudge Calls, exactly the single-Service production wiring
    `web_application.py`'s Composition Root uses for Main-self Judge/
    Repair. Distinguishes stage by the real `request_id` suffix each real
    Call site actually uses."""

    def __init__(self, *, initial_judge: str, repair_candidate: str, rejudge: str) -> None:
        self._initial_judge = initial_judge
        self._repair_candidate = repair_candidate
        self._rejudge = rejudge
        self.calls: list[GenerationRequest] = []
        self.runtime_info: object | None = None

    def count_chat_prompt_tokens(self, messages: tuple[object, ...], thinking_mode: object) -> int:
        del thinking_mode
        return sum(len(str(getattr(message, "content", ""))) for message in messages)

    def generate(
        self, request: GenerationRequest, *, cancellation: CancellationToken | None = None
    ) -> GenerationResult:
        self.calls.append(request)
        if request.request_id.endswith(":repair"):
            content = self._repair_candidate
        elif request.request_id.endswith(":rejudge"):
            content = self._rejudge
        else:
            content = self._initial_judge
        return GenerationResult(
            request_id=request.request_id,
            model_key=request.model_key,
            content=content,
            finish_reason=FinishReason.STOP,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            timing=GenerationTiming(total_generation_seconds=0.01),
            runtime_info=_RUNTIME_REF,
        )


def _criterion() -> SemanticCriterion:
    digest = "a" * 128
    return SemanticCriterion(
        criterion_id="semantic.argd.evidence.1",
        descriptor_id="argd.evidence.1",
        source_definition_id="argd",
        source_definition_digest_sha512=digest,
        source_pointer="/rules/evidence/1",
        source_text_digest_sha512=digest,
        instruction="Do not contradict the cited evidence.",
        governance_point="main_model.semantic",
        evaluation_stage=SemanticEvaluationStage.POST,
        evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        severity_policy="high",
        recommended_action_policy="repair_or_safe_fallback",
        evidence_requirements=("request_identity",),
    )


def _presentation_policy() -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="thinking",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def _settings() -> ConversationSettings:
    return ConversationSettings(
        response_language=ResponseLanguage.EN,
        max_new_tokens=128,
        thinking_mode=ThinkingMode.DISABLED,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        summary_mode=SummaryMode.OFF,
        documentation_rag_mode=DocumentationRagMode.DISABLED,
    )


def _ids(label: str) -> PersistentGenerationIdentities:
    return PersistentGenerationIdentities(
        turn_id=ConversationTurnId(value=f"turn-{label}"),
        user_message_id=ConversationMessageId(value=f"message-user-{label}"),
        assistant_message_id=ConversationMessageId(value=f"message-assistant-{label}"),
        append_operation_id=ConversationOperationId(value=f"append-{label}"),
        start_operation_id=ConversationOperationId(value=f"start-{label}"),
        terminal_operation_id=ConversationOperationId(value=f"terminal-{label}"),
    )


def _build_generation_service(
    *,
    main_service: _MainInference,
    judge_service: _JudgeRepairService,
    coordinator: ModelAccessCoordinator,
) -> ConversationGenerationService:
    judge_controller = JudgeModeController()
    repair_controller = RepairModeController()
    hook, _composition = build_judge_completion_hook(
        service=judge_service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=coordinator,
        repair_mode_controller=repair_controller,
        repair_executor=partial(
            attempt_live_repair,
            service=judge_service,  # type: ignore[arg-type]
            model_key=_JUDGE_MODEL_KEY,
            # Never located: the normal ENFORCE-presented-final path always
            # passes `persist_accepted_attempt=False` to the Repair
            # Executor (`judge_live_integration._finalize_judge_dispatch`,
            # `persist_accepted_attempt=not context.enforce_presented_
            # final`) -- Repair itself never touches persistence on this
            # path; only `PersistentConversationService.generate_turn()`'s
            # own `complete_generation()` call, below, does.
            persistent=None,
        ),
        semantic_snapshot_provider=lambda rid: freeze_semantic_turn(
            request_id=rid,
            generation=1,
            criteria=(_criterion(),),
            language="en",
            main_mode="observe",
            judge_mode="enforce",
            repair_mode="enforce",
            configured_provider=_MAIN_MODEL_KEY,
            active_provider=_MAIN_MODEL_KEY,
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=8,
        ).snapshot,
        semantic_result_recorder=lambda response: None,
    )
    return ConversationGenerationService(
        inference=main_service,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key=_MAIN_MODEL_KEY,
        generation_defaults=GenerationParameters(
            max_new_tokens=128, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.EN,
        presentation_default=_presentation_policy(),
        judge_completion_hook=hook,
        judge_mode_snapshot_provider=lambda: JudgeExecutionModeSnapshot(
            judge_mode="enforce", repair_mode="enforce", recording_mode="off"
        ),
        # Shared with `build_judge_completion_hook()` above -- the real
        # production Composition Root wires exactly one `ModelAccessCoordinator`
        # instance to both (`web_application.py`), so Main's own Turn Lease
        # (released before the synchronous ENFORCE Judge/Repair Call, see
        # `conversation_generation.py`'s `_completed_event()`) and the
        # Judge/Repair Background Task genuinely share the same coordination
        # state this Test is meant to exercise, not two independent ones
        # that would never actually contend.
        model_access_coordinator=coordinator,
    )


def _build_generation_service_main_origin(
    *,
    main_service: _MainInference,
    judge_service: _JudgeRepairService,
    coordinator: ModelAccessCoordinator,
    repair_mode: str = "off",
) -> tuple[ConversationGenerationService, JudgeGovernanceComposition]:
    """Controller Review (2026-09-04 23:54, IR-R3-03; parametrized 2026-09-05
    00:35, IR-R4 §4): the Main-origin counterpart of `_build_generation_
    service` above. Judge-side `repair_mode` (`"off"` or `"observe"` --
    never `"enforce"`, which would let the pre-existing Judge-origin gate
    independently authorize the Repair too, defeating this Test's own
    point) is parametrized rather than hardcoded, since Controller's own
    memory-patched Probe additionally exercised `"observe"` and found it
    passed identically to `"off"`. Whichever value is used applies to both
    the Conversation Session's own `judge_mode_snapshot_provider` and the
    `RuntimeGovernanceComposition`'s `SemanticRuntimeBindingContext` --
    the whole point being that only Main Runtime Governance's own
    independent ENFORCE decision (`main_action.executed_disposition is
    REPAIR_REQUESTED`, computed by the real `semantic_result_recorder`
    wired below, never a `lambda: None` stub) can authorize the Repair,
    exactly mirroring `test_real_local_main_governance_origin_repair_
    smoke.py`'s own real-hardware wiring -- here driven through the full
    `ConversationGenerationService`/`PersistentConversationService` save
    path instead of a Hook-direct call. Returns the real `JudgeGovernance
    Composition` too (discarded by `_build_generation_service` above) so
    a Test can assert `repair_requested_by` directly, the same field
    Controller's own Probe used to prove the pre-existing P2 Tests were
    Judge-origin, not Main-origin."""
    criterion = _criterion()
    composition = RuntimeGovernanceComposition(
        capability=RuntimeCapabilitySnapshot(
            model_key=_MAIN_MODEL_KEY,
            backend_kind="llama_cpp",
            supports_streaming=True,
            supports_thinking=True,
            max_context_tokens=16384,
        ),
    )
    composition.semantic_runtime = SemanticRuntimeCoordinator(criteria=(criterion,))
    composition.set_semantic_context_provider(
        lambda: SemanticRuntimeBindingContext(
            language="en",
            judge_mode="enforce",
            repair_mode=repair_mode,
            configured_provider=_MAIN_MODEL_KEY,
            active_provider=_MAIN_MODEL_KEY,
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=8,
        )
    )
    judge_controller = JudgeModeController()
    # Never left at its own default mode value for gating purposes here --
    # `context.repair_mode` (the parametrized `repair_mode` string below)
    # is what the Hook actually reads; this object's own presence (never
    # `None`) is what the Judge-side gate additionally requires.
    repair_controller = RepairModeController()
    hook, hook_composition = build_judge_completion_hook(
        service=judge_service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=coordinator,
        repair_mode_controller=repair_controller,
        repair_executor=partial(
            attempt_live_repair,
            service=judge_service,  # type: ignore[arg-type]
            model_key=_JUDGE_MODEL_KEY,
            persistent=None,
        ),
        # `begin_semantic_turn()` both begins AND returns the Snapshot for
        # whatever `request_id` the real Conversation pipeline actually
        # generates (unknown ahead of time, unlike the Hook-direct
        # real-hardware Test's own fixed id) -- called fresh per real Turn.
        semantic_snapshot_provider=lambda rid: composition.begin_semantic_turn(
            request_id=rid, main_mode="enforce"
        ),
        semantic_result_recorder=lambda response: composition.record_semantic_response(
            response=response
        ),
    )
    service = ConversationGenerationService(
        inference=main_service,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key=_MAIN_MODEL_KEY,
        generation_defaults=GenerationParameters(
            max_new_tokens=128, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.EN,
        presentation_default=_presentation_policy(),
        judge_completion_hook=hook,
        judge_mode_snapshot_provider=lambda: JudgeExecutionModeSnapshot(
            judge_mode="enforce", repair_mode=repair_mode, recording_mode="off"
        ),
        model_access_coordinator=coordinator,
    )
    return service, hook_composition


def _persistent_service(
    tmp_path: Path, *, generation_service: ConversationGenerationService
) -> PersistentConversationService:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data", bound_scope_id=SCOPE
    )
    store.initialize_new_store()
    persistent = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=generation_service,
        clock=_Clock(),
    )
    persistent.recover_incomplete_conversations()
    persistent.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=ConversationOperationId(value="create"),
    )
    return persistent


def test_a_normal_enforce_turn_repairs_and_persists_the_corrected_answer_into_the_same_turn(
    tmp_path: Path,
) -> None:
    """The crux of P2/IR-R2-02: drives the real `PersistentConversationService.
    generate_turn()` -> Conversation Session -> real Judge Hook -> real
    `attempt_live_repair()` -> same-condition Rejudge chain, never an
    Executor-direct shortcut. Asserts the SAME (only) Turn's own persisted
    assistant message becomes the repaired content -- never a second
    REPAIR-origin Turn, and never the known-wrong original answer."""
    criterion = _criterion()
    initial_judge_output = (
        '{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague", '
        f'"criterion_results": [{{"criterion_id": "{criterion.criterion_id}", '
        '"disposition": "deviation", "confidence": 0.85, "reason_code": "unsupported_claim", '
        '"evidence_refs": ["REFERENCE SENTINEL"]}]}'
    )
    rejudge_output = (
        '{"recommendation": "accept", "confidence": 0.9, '
        f'"criterion_results": [{{"criterion_id": "{criterion.criterion_id}", '
        '"disposition": "pass", "confidence": 0.9}]}'
    )
    main_service = _MainInference(answer=_WRONG_ANSWER)
    judge_service = _JudgeRepairService(
        initial_judge=initial_judge_output,
        repair_candidate=_CORRECTED_ANSWER,
        rejudge=rejudge_output,
    )
    coordinator = ModelAccessCoordinator()
    generation_service = _build_generation_service(
        main_service=main_service, judge_service=judge_service, coordinator=coordinator
    )
    persistent = _persistent_service(tmp_path, generation_service=generation_service)

    events = list(
        persistent.generate_turn(
            conversation_id=CID,
            content="What is the capital of France?",
            settings=_settings(),
            identities=_ids("t1"),
            expected_revision=1,
        )
    )

    assert events[-1].event is ConversationEventType.COMPLETED
    stored = persistent.get_conversation(CID)
    # The crux: exactly one Turn exists -- Repair never created a second,
    # separate REPAIR-origin Turn on this path.
    assert len(stored.conversation.turns) == 1
    turn = stored.conversation.turns[0]
    assert turn.origin is ConversationTurnOrigin.NORMAL
    assert turn.state is ConversationTurnState.COMPLETED
    assert turn.assistant_message_id is not None
    persisted_message = next(
        item
        for item in stored.conversation.messages
        if item.message_id == turn.assistant_message_id
    )
    # The crux: the repaired content, genuinely produced by the real
    # `attempt_live_repair()` Call chain, is what actually landed in
    # persistent storage for this Turn -- not merely returned in-memory by
    # the Hook.
    assert persisted_message.content == _CORRECTED_ANSWER
    assert "Tenon" not in persisted_message.content
    # Both real Judge/Repair/Rejudge Calls (plus the Initial Judge) ran on
    # the shared Judge/Repair Service.
    assert len(judge_service.calls) == 3


def test_a_normal_enforce_turn_never_persists_the_known_wrong_answer_when_repair_fails(
    tmp_path: Path,
) -> None:
    """Repair failure detection, distinct from the success path above:
    when the Rejudge itself still finds a Deviation (Repair genuinely did
    not fix the flaw), the SAME Turn must still never persist the known-
    wrong original Candidate -- and must still create no second Turn."""
    criterion = _criterion()
    initial_judge_output = (
        '{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague", '
        f'"criterion_results": [{{"criterion_id": "{criterion.criterion_id}", '
        '"disposition": "deviation", "confidence": 0.85, "reason_code": "unsupported_claim", '
        '"evidence_refs": ["REFERENCE SENTINEL"]}]}'
    )
    # The Repair Candidate deliberately fails to fix the flaw, and the
    # Rejudge still reports the same Deviation -- a genuine Repair
    # failure, never silently treated as success.
    still_wrong_rejudge = (
        '{"recommendation": "needs_repair", "confidence": 0.3, '
        f'"criterion_results": [{{"criterion_id": "{criterion.criterion_id}", '
        '"disposition": "deviation", "confidence": 0.8, "reason_code": "still_contradicts"}]}'
    )
    main_service = _MainInference(answer=_WRONG_ANSWER)
    judge_service = _JudgeRepairService(
        initial_judge=initial_judge_output,
        repair_candidate=_WRONG_ANSWER,
        rejudge=still_wrong_rejudge,
    )
    coordinator = ModelAccessCoordinator()
    generation_service = _build_generation_service(
        main_service=main_service, judge_service=judge_service, coordinator=coordinator
    )
    persistent = _persistent_service(tmp_path, generation_service=generation_service)

    events = list(
        persistent.generate_turn(
            conversation_id=CID,
            content="What is the capital of France?",
            settings=_settings(),
            identities=_ids("t1"),
            expected_revision=1,
        )
    )

    assert events[-1].event is ConversationEventType.COMPLETED
    stored = persistent.get_conversation(CID)
    assert len(stored.conversation.turns) == 1
    turn = stored.conversation.turns[0]
    assert turn.origin is ConversationTurnOrigin.NORMAL
    assert turn.state is ConversationTurnState.COMPLETED
    assert turn.assistant_message_id is not None
    persisted_message = next(
        item
        for item in stored.conversation.messages
        if item.message_id == turn.assistant_message_id
    )
    # The crux: the known-wrong Candidate is never what actually landed in
    # persistent storage, regardless of whether Repair succeeded.
    assert persisted_message.content != _WRONG_ANSWER
    assert persisted_message.content.strip() != ""


# Controller Review (2026-09-04 23:54, IR-R3-03) -- Main Runtime
# Governance's own ENFORCE-origin authorization, distinct from the
# Judge-side Repair Mode ENFORCE path the two Tests above cover. Judge-
# side `repair_mode` is `"off"` throughout; only a real `SemanticAction
# Decision.executed_disposition is REPAIR_REQUESTED` (computed by a real
# `semantic_result_recorder`, never a `lambda: None` stub) can authorize
# the Repair here.


@pytest.mark.parametrize("repair_mode", ["off", "observe"])
def test_a_main_governance_origin_enforce_turn_repairs_and_persists_the_corrected_answer(
    repair_mode: str,
    tmp_path: Path,
) -> None:
    """The crux of IR-R3-03: `repair_requested_by == "main_governance"`,
    the same Frozen Criterion Main Governance itself flagged a Deviation
    on carries through to the Rejudge, and the improved answer lands in
    the SAME (only) normal Turn -- never a second REPAIR-origin Turn,
    never the known-wrong original answer, and never a Judge-origin
    authorization silently substituting for the Main-origin one this
    Test's own wiring makes structurally impossible. Parametrized over
    Judge-side `repair_mode` (2026-09-05, IR-R4 §4) -- `"off"` and
    `"observe"` both structurally prevent the pre-existing Judge-origin
    gate from independently authorizing the Repair (only `"enforce"`
    would), so both must behave identically here."""
    criterion = _criterion()
    initial_judge_output = (
        '{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague", '
        f'"criterion_results": [{{"criterion_id": "{criterion.criterion_id}", '
        '"disposition": "deviation", "confidence": 0.85, "reason_code": "unsupported_claim", '
        '"evidence_refs": ["REFERENCE SENTINEL"]}]}'
    )
    rejudge_output = (
        '{"recommendation": "accept", "confidence": 0.9, '
        f'"criterion_results": [{{"criterion_id": "{criterion.criterion_id}", '
        '"disposition": "pass", "confidence": 0.9}]}'
    )
    main_service = _MainInference(answer=_WRONG_ANSWER)
    judge_service = _JudgeRepairService(
        initial_judge=initial_judge_output,
        repair_candidate=_CORRECTED_ANSWER,
        rejudge=rejudge_output,
    )
    coordinator = ModelAccessCoordinator()
    generation_service, hook_composition = _build_generation_service_main_origin(
        main_service=main_service,
        judge_service=judge_service,
        coordinator=coordinator,
        repair_mode=repair_mode,
    )
    persistent = _persistent_service(tmp_path, generation_service=generation_service)

    events = list(
        persistent.generate_turn(
            conversation_id=CID,
            content="What is the capital of France?",
            settings=_settings(),
            identities=_ids("t1"),
            expected_revision=1,
        )
    )

    assert events[-1].event is ConversationEventType.COMPLETED
    # The crux: Main Governance itself authorized this Repair -- never the
    # Judge-side Repair Mode, which was OFF/OBSERVE (never ENFORCE)
    # throughout this Test.
    result = hook_composition.last_result()
    assert result is not None
    assert result.repair_requested_by == "main_governance"
    assert result.repair_accepted is True
    stored = persistent.get_conversation(CID)
    assert len(stored.conversation.turns) == 1
    turn = stored.conversation.turns[0]
    assert turn.origin is ConversationTurnOrigin.NORMAL
    assert turn.state is ConversationTurnState.COMPLETED
    assert turn.assistant_message_id is not None
    persisted_message = next(
        item
        for item in stored.conversation.messages
        if item.message_id == turn.assistant_message_id
    )
    assert persisted_message.content == _CORRECTED_ANSWER
    assert "Tenon" not in persisted_message.content
    assert len(judge_service.calls) == 3


@pytest.mark.parametrize("repair_mode", ["off", "observe"])
def test_a_main_governance_origin_enforce_turn_never_persists_the_known_wrong_answer_when_repair_fails(  # noqa: E501
    repair_mode: str,
    tmp_path: Path,
) -> None:
    """Main-origin counterpart of the Judge-origin failure Test above:
    when the Rejudge (still authorized solely by Main Governance) finds
    the Deviation persists, the SAME Turn must still never persist the
    known-wrong original Candidate, and no second Turn is created.
    Parametrized over Judge-side `repair_mode` (2026-09-05, IR-R4 §4),
    same rationale as the success Test above."""
    criterion = _criterion()
    initial_judge_output = (
        '{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague", '
        f'"criterion_results": [{{"criterion_id": "{criterion.criterion_id}", '
        '"disposition": "deviation", "confidence": 0.85, "reason_code": "unsupported_claim", '
        '"evidence_refs": ["REFERENCE SENTINEL"]}]}'
    )
    still_wrong_rejudge = (
        '{"recommendation": "needs_repair", "confidence": 0.3, '
        f'"criterion_results": [{{"criterion_id": "{criterion.criterion_id}", '
        '"disposition": "deviation", "confidence": 0.8, "reason_code": "still_contradicts"}]}'
    )
    main_service = _MainInference(answer=_WRONG_ANSWER)
    judge_service = _JudgeRepairService(
        initial_judge=initial_judge_output,
        repair_candidate=_WRONG_ANSWER,
        rejudge=still_wrong_rejudge,
    )
    coordinator = ModelAccessCoordinator()
    generation_service, hook_composition = _build_generation_service_main_origin(
        main_service=main_service,
        judge_service=judge_service,
        coordinator=coordinator,
        repair_mode=repair_mode,
    )
    persistent = _persistent_service(tmp_path, generation_service=generation_service)

    events = list(
        persistent.generate_turn(
            conversation_id=CID,
            content="What is the capital of France?",
            settings=_settings(),
            identities=_ids("t1"),
            expected_revision=1,
        )
    )

    assert events[-1].event is ConversationEventType.COMPLETED
    result = hook_composition.last_result()
    assert result is not None
    assert result.repair_requested_by == "main_governance"
    assert result.repair_accepted is False
    stored = persistent.get_conversation(CID)
    assert len(stored.conversation.turns) == 1
    turn = stored.conversation.turns[0]
    assert turn.origin is ConversationTurnOrigin.NORMAL
    assert turn.state is ConversationTurnState.COMPLETED
    assert turn.assistant_message_id is not None
    persisted_message = next(
        item
        for item in stored.conversation.messages
        if item.message_id == turn.assistant_message_id
    )
    assert persisted_message.content != _WRONG_ANSWER
    assert persisted_message.content.strip() != ""


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
