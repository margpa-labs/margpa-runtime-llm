"""P6-CODEX-009 (Second Rework), hardened P6-CODEX-021 (Third Rework): real
Bounded Repair execution coverage.

Covers: not-located passthrough (Ephemeral chat has no Turn to attach a
Repair Attempt to); Generation/Rejudge Model Call failure and empty-output
typed rejection; Governance/Guardrail Phase 4/5 post-check re-entry (a Deny
is never bypassed regardless of Judge/Repair Mode, ADR-5-001) — including a
Hook that itself raises being Fail-closed, not Fail-open; Before/After
Improved-only acceptance (a Worse/No-Change outcome creates zero additional
Turn); real Budget enforcement (a Budget whose `max_total_model_calls`
cannot afford the Rejudge Call blocks it before spending it); Main-priority
Cancellation stopping Repair before its second real Model Call; persistence
failure compensation (an orphaned Turn is explicitly marked FAILED rather
than left PENDING/GENERATING); and, on genuine acceptance, real atomic
persistence through the same CAS-guarded append_derived_turn ->
start_generation -> complete_generation sequence Retry/Regenerate already
use.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest

from margpa_runtime_llm.adapters.runtime_model_control.dedicated_role_adapters import (
    GEMMA_JUDGE_DETERMINISTIC_SAMPLING,
)
from margpa_runtime_llm.bootstrap.repair_live_integration import (
    _REJUDGE_TOKENS_PER_CRITERION,
    _REPAIR_MAX_NEW_TOKENS,
    LIVE_REPAIR_BUDGET,
    _plan_rejudge,
    attempt_live_repair,
)
from margpa_runtime_llm.bootstrap.tracked_stage_worker import TrackedStageWorkerRegistry
from margpa_runtime_llm.modules.conversation.adapters import SQLiteConversationStore
from margpa_runtime_llm.modules.conversation.application import (
    PersistentConversationService,
    PersistentGenerationIdentities,
)
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEvent,
    ConversationEventType,
    ConversationGenerationInput,
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
    ConversationTurnProvenance,
    ConversationTurnState,
)
from margpa_runtime_llm.modules.conversation.ports import StoredConversation
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DocumentationAugmentation,
    DocumentationRagMode,
)
from margpa_runtime_llm.modules.evaluation.application.judge_prompt_builder import (
    JudgePromptCriterion,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationRecommendation
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationRequest,
    GenerationResult,
    GenerationTiming,
    StructuredOutputConstraint,
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
    ModelRuntimeReference,
)
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.inference.domain.capabilities import CapabilityFeature
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.repair.domain.budget import RepairBudget, RepairBudgetUsage
from margpa_runtime_llm.modules.summarization.public import SummaryMode

SCOPE = ConversationScopeId(value="scope-private")
CID = ConversationId(value="conversation-1")

_RUNTIME_REF = ModelRuntimeReference(
    load_instance_id="load-1",
    model_key="main.test-model",
    backend_key="fake",
    backend_version="0.0.0",
    definition_file_sha512="a" * 128,
)


class _Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 8, 23, tzinfo=UTC)

    def __call__(self) -> datetime:
        self.value += timedelta(seconds=1)
        return self.value


class _Session:
    def __init__(self, request_id: str, answer: str) -> None:
        self.request_id = request_id
        self.answer = answer
        self.documentation_augmentation = None
        self.web_search_result = None

    def events(self) -> Iterator[ConversationEvent]:
        yield ConversationEvent(
            event=ConversationEventType.START,
            data={"request_id": self.request_id, "state": "generating"},
        )
        yield ConversationEvent(
            event=ConversationEventType.COMPLETED,
            data={
                "request_id": self.request_id,
                "finish_reason": "stop",
                "assistant_message": {"role": "assistant", "content": self.answer},
            },
        )


class _Generation:
    def __init__(self) -> None:
        self.inputs: list[ConversationGenerationInput] = []

    def start(self, value: ConversationGenerationInput) -> _Session:
        self.inputs.append(value)
        request_id = f"request-{len(self.inputs)}"
        return _Session(request_id, f"original-answer-{len(self.inputs)}")

    def cancel(self, request_id: str) -> bool:
        return False


def _settings() -> ConversationSettings:
    return ConversationSettings(
        response_language=ResponseLanguage.JA,
        max_new_tokens=128,
        thinking_mode=ThinkingMode.DISABLED,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        summary_mode=SummaryMode.OFF,
        documentation_rag_mode=DocumentationRagMode.DISABLED,
    )


def _build_persistent_with_one_completed_turn(
    tmp_path: Path,
) -> tuple[PersistentConversationService, str]:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=SCOPE,
    )
    store.initialize_new_store()
    generation = _Generation()
    persistent = PersistentConversationService(
        repository=store,
        bound_scope_id=SCOPE,
        generation_service=generation,  # type: ignore[arg-type]
        clock=_Clock(),
    )
    persistent.recover_incomplete_conversations()
    persistent.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=ConversationOperationId(value="create"),
    )
    events = tuple(
        persistent.generate_turn(
            conversation_id=CID,
            content="What is the capital of France?",
            settings=_settings(),
            identities=_ids("source"),
            expected_revision=1,
        )
    )
    assert events[-1].event is ConversationEventType.COMPLETED
    return persistent, "request-1"


def _ids(label: str) -> PersistentGenerationIdentities:
    return PersistentGenerationIdentities(
        turn_id=ConversationTurnId(value=f"turn-{label}"),
        user_message_id=ConversationMessageId(value=f"message-user-{label}"),
        assistant_message_id=ConversationMessageId(value=f"message-assistant-{label}"),
        append_operation_id=ConversationOperationId(value=f"append-{label}"),
        start_operation_id=ConversationOperationId(value=f"start-{label}"),
        terminal_operation_id=ConversationOperationId(value=f"terminal-{label}"),
    )


def _runtime_info() -> ModelRuntimeInfo:
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
        loaded_context_size=8192,
        effective_capabilities=ModelCapabilities(
            features=frozenset({CapabilityFeature.CHAT}),
            native_context_limit=8192,
            loaded_context_size=8192,
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


class _FakeRepairService:
    def __init__(
        self,
        *,
        repair_content: str = "An improved answer.",
        rejudge_content: str = '{"recommendation": "accept", "confidence": 0.9}',
        fail_on_suffix: str | None = None,
    ) -> None:
        self.repair_content = repair_content
        self.rejudge_content = rejudge_content
        self.fail_on_suffix = fail_on_suffix
        self.calls: list[GenerationRequest] = []

    def generate(
        self,
        request: GenerationRequest,
        *,
        cancellation: CancellationToken | None = None,
    ) -> GenerationResult:
        self.calls.append(request)
        if self.fail_on_suffix is not None and request.request_id.endswith(self.fail_on_suffix):
            raise RuntimeError("boom")
        content = (
            self.rejudge_content if request.request_id.endswith(":rejudge") else self.repair_content
        )
        return GenerationResult(
            request_id=request.request_id,
            model_key=request.model_key,
            content=content,
            finish_reason=FinishReason.STOP,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            timing=GenerationTiming(total_generation_seconds=0.01),
            runtime_info=_RUNTIME_REF,
        )


class _UsageScriptedRepairService:
    """Controller Review (2026-09-04 22:41, P1/IR-R2-01) coverage: unlike
    `_FakeRepairService` (a fixed `completion_tokens=5` for every real
    Model Call, regardless of stage), this Fixture lets a test script the
    exact `completion_tokens` the Repair Candidate call and the Rejudge
    call each report -- needed to distinguish a genuine AFTER-the-call
    Budget overspend (the Model actually returned more tokens than
    planned) from the pre-call Typed failure `_plan_rejudge()` now
    produces when the plan itself was never affordable to begin with.
    Also optionally exposes `runtime_info`/`count_chat_prompt_tokens` (the
    same shape a real `InferenceService` has) so a test can exercise
    `_plan_rejudge()`'s input-Context bound; both are `None` by default,
    matching `_FakeRepairService`'s existing minimal-Fixture behavior."""

    def __init__(
        self,
        *,
        repair_content: str = "An improved answer.",
        rejudge_content: str = '{"recommendation": "accept", "confidence": 0.9}',
        repair_completion_tokens: int = 5,
        rejudge_completion_tokens: int = 5,
        loaded_context_size: int | None = None,
        prompt_token_count: int = 0,
    ) -> None:
        self.repair_content = repair_content
        self.rejudge_content = rejudge_content
        self.repair_completion_tokens = repair_completion_tokens
        self.rejudge_completion_tokens = rejudge_completion_tokens
        self.calls: list[GenerationRequest] = []
        self.runtime_info = (
            None
            if loaded_context_size is None
            else SimpleNamespace(loaded_context_size=loaded_context_size)
        )
        self._prompt_token_count = prompt_token_count

    def count_chat_prompt_tokens(self, messages: object, thinking_mode: object) -> int:
        del messages, thinking_mode
        return self._prompt_token_count

    def generate(
        self,
        request: GenerationRequest,
        *,
        cancellation: CancellationToken | None = None,
    ) -> GenerationResult:
        self.calls.append(request)
        is_rejudge = request.request_id.endswith(":rejudge")
        content = self.rejudge_content if is_rejudge else self.repair_content
        completion_tokens = (
            self.rejudge_completion_tokens if is_rejudge else self.repair_completion_tokens
        )
        return GenerationResult(
            request_id=request.request_id,
            model_key=request.model_key,
            content=content,
            finish_reason=FinishReason.STOP,
            usage=TokenUsage(
                prompt_tokens=10,
                completion_tokens=completion_tokens,
                total_tokens=10 + completion_tokens,
            ),
            timing=GenerationTiming(total_generation_seconds=0.01),
            runtime_info=_RUNTIME_REF,
        )


class _CounterRaisingRepairService(_UsageScriptedRepairService):
    """Controller Review (2026-09-04 23:54, IR-R3-01) exact reproduction:
    `count_chat_prompt_tokens()` itself raises (Controller's own Probe:
    `RuntimeError('controller_counter_failure')`) -- proves the exception
    is caught inside `_plan_rejudge()`, never propagated past `attempt_
    live_repair()` uncaught."""

    def count_chat_prompt_tokens(self, messages: object, thinking_mode: object) -> int:
        del messages, thinking_mode
        raise RuntimeError("controller_counter_failure")


class _SlowCounterRepairService(_UsageScriptedRepairService):
    """Controller Review (2026-09-04 23:54, IR-R3-01) exact reproduction:
    `count_chat_prompt_tokens()` itself spends real wall-clock time
    (Controller's own Probe: 50ms) -- proves the overall Repair Budget's
    remaining wall time is re-checked AFTER Planning's own real cost,
    before the Rejudge Call is ever made, for both Cancellation branches."""

    def __init__(self, *, counter_delay_seconds: float, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._counter_delay_seconds = counter_delay_seconds

    def count_chat_prompt_tokens(self, messages: object, thinking_mode: object) -> int:
        time.sleep(self._counter_delay_seconds)
        return super().count_chat_prompt_tokens(messages, thinking_mode)


class _EventBlockingCounterRepairService(_UsageScriptedRepairService):
    """Controller Review (2026-09-05 00:35, IR-R4-01) exact reproduction:
    `count_chat_prompt_tokens()` blocks on a `threading.Event` until it is
    externally released -- a genuinely unbounded wait, unlike `_SlowCounter
    RepairService`'s own fixed, finite delay. Proves the calling Thread
    itself is never left waiting past the real remaining `RepairBudget.
    max_wall_time_ms` (via `run_tracked_stage()`), even though the
    background Thread actually running the Counter is left to finish (or
    keep blocking) entirely on its own -- never killed, matching `bootstrap/
    tracked_stage_worker.py`'s own documented Python-level constraint. The
    Event is always released by the Test itself (a `threading.Timer` safety
    net plus an explicit release in `finally`), so no Thread is ever left
    permanently blocked past the Test's own lifetime."""

    def __init__(self, *, block_event: threading.Event, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._block_event = block_event

    def count_chat_prompt_tokens(self, messages: object, thinking_mode: object) -> int:
        self._block_event.wait()
        return super().count_chat_prompt_tokens(messages, thinking_mode)


class _SelfCancellingCounterRepairService(_UsageScriptedRepairService):
    """Controller Review (2026-09-05 00:35, IR-R4-01) exact reproduction:
    `count_chat_prompt_tokens()` cancels the SAME `CancellationToken` the
    Attempt itself was given (a simulated Main-priority preemption arriving
    while counting is genuinely in progress), then returns normally --
    proves the Executor checks Cancellation again after Planning returns,
    before ever reaching the real Rejudge Call, rather than only checking
    Cancellation inside the Rejudge Call's own `stage_deadline()` wrapper
    (which Controller's own Probe showed the Rejudge Service Call had
    already been reached by, in the pre-fix version)."""

    def __init__(self, *, cancellation: CancellationToken, **kwargs: object) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        self._cancellation = cancellation

    def count_chat_prompt_tokens(self, messages: object, thinking_mode: object) -> int:
        self._cancellation.cancel()
        return super().count_chat_prompt_tokens(messages, thinking_mode)


def _criterion(criterion_id: str) -> JudgePromptCriterion:
    return JudgePromptCriterion(
        criterion_id=criterion_id,
        instruction="Do not contradict the cited evidence.",
        evaluation_method="classification_with_reference",
        source_pointer="/rules/evidence/1",
    )


def test_returns_none_when_request_id_was_never_located(tmp_path: Path) -> None:
    persistent, _ = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id="never-seen-request",
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
    )

    assert result is None
    assert service.calls == []


def test_presented_final_repair_needs_no_persisted_source_and_returns_content() -> None:
    service = _FakeRepairService(repair_content="Source-grounded corrected answer.")

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=None,
        request_id="ephemeral-enforce-1",
        user_input="No, the correct reading is Amane Kanata.",
        original_answer="The official reading is Tenon.",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="contradicts the supplied evidence",
        dialogue_context=("assistant: The official reading is Tenon.",),
        evidence_context=("ref-1 | official.md: Amane Kanata",),
        governance_post_hook=None,
        guardrail_post_hook=None,
        persist_accepted_attempt=False,
    )

    assert result is not None
    assert result.accepted is True
    assert result.new_turn_id is None
    assert result.presented_content == "Source-grounded corrected answer."
    assert len(service.calls) == 2
    repair_prompt = service.calls[0].messages[0].content
    rejudge_prompt = service.calls[1].messages[0].content
    assert "ref-1 | official.md: Amane Kanata" in repair_prompt
    assert "ref-1 | official.md: Amane Kanata" in rejudge_prompt
    assert "Violated criteria and prohibited errors" in repair_prompt


def test_repair_rejudge_uses_explicit_selected_judge_service_identity() -> None:
    main_service = _FakeRepairService(repair_content="Corrected answer")
    selected_judge_service = _FakeRepairService(
        rejudge_content='{"recommendation": "accept", "confidence": 0.9}'
    )

    result = attempt_live_repair(
        service=main_service,  # type: ignore[arg-type]
        model_key="main.test-model",
        rejudge_service=selected_judge_service,  # type: ignore[arg-type]
        rejudge_model_key="judge.selene-test",
        rejudge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
        persistent=None,
        request_id="selected-rejudge-1",
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="criterion=semantic.argd.evidence.1; evidence=ref-1",
        governance_post_hook=None,
        guardrail_post_hook=None,
        persist_accepted_attempt=False,
    )

    assert result is not None
    assert result.accepted is True
    assert len(main_service.calls) == 1
    assert len(selected_judge_service.calls) == 1
    assert selected_judge_service.calls[0].model_key == "judge.selene-test"
    assert result.rejudge_model_identity == "judge.selene-test"
    assert result.rejudge_role == "independent_artifact"


def test_repair_generation_failure_is_a_typed_rejection(tmp_path: Path) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService(fail_on_suffix=":repair")

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
    )

    assert result is not None
    assert result.accepted is False
    assert result.new_turn_id is None
    assert result.rejected_reason == "repair_generation_failed"


def test_repair_generation_empty_output_is_a_typed_rejection(tmp_path: Path) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService(repair_content="   ")

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "repair_generation_empty"


def test_governance_post_reject_short_circuits_before_rejudge(tmp_path: Path) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=lambda _content: (True, "denied"),
        guardrail_post_hook=None,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "governance_post_reject"
    # Only the repair-candidate call happened; rejudge never ran.
    assert len(service.calls) == 1


def test_guardrail_post_reject_short_circuits_before_rejudge(tmp_path: Path) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=lambda _content: (True, "denied"),
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "guardrail_post_reject"
    assert len(service.calls) == 1


def test_rejudge_failure_is_a_typed_rejection(tmp_path: Path) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService(fail_on_suffix=":rejudge")

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "rejudge_failed"


def test_no_change_outcome_is_rejected_and_creates_no_new_turn(tmp_path: Path) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    before_conversation = persistent.get_conversation(CID)
    before_turn_count = len(before_conversation.conversation.turns)
    service = _FakeRepairService(
        rejudge_content='{"recommendation": "needs_repair", "confidence": 0.5}'
    )

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
    )

    assert result is not None
    assert result.outcome == "no_change"
    assert result.accepted is False
    assert result.new_turn_id is None
    after_conversation = persistent.get_conversation(CID)
    assert len(after_conversation.conversation.turns) == before_turn_count


def test_improved_outcome_is_accepted_and_persists_a_real_repair_turn(tmp_path: Path) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    before_conversation = persistent.get_conversation(CID)
    before_turn_count = len(before_conversation.conversation.turns)
    service = _FakeRepairService(repair_content="A corrected, better answer.")

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="was vague",
        governance_post_hook=None,
        guardrail_post_hook=None,
    )

    assert result is not None
    assert result.outcome == "improved"
    assert result.accepted is True
    assert result.new_turn_id is not None

    after_conversation = persistent.get_conversation(CID)
    assert len(after_conversation.conversation.turns) == before_turn_count + 1
    new_turn = next(
        turn
        for turn in after_conversation.conversation.turns
        if turn.turn_id.value == result.new_turn_id
    )
    assert new_turn.origin is ConversationTurnOrigin.REPAIR
    assert after_conversation.conversation.head_turn_id == new_turn.turn_id
    assistant_message = next(
        message
        for message in after_conversation.conversation.messages
        if message.message_id == new_turn.assistant_message_id
    )
    assert assistant_message.content == "A corrected, better answer."


def test_accepted_repair_turn_also_carries_real_attempt_provenance(tmp_path: Path) -> None:
    """P6-CODEX-013: a Repair Attempt is a Generation Attempt too — it must
    not be a second-class citizen missing the Provenance a Normal/Retry/
    Regenerate Turn already carries."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService(repair_content="A corrected, better answer.")

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="was vague",
        governance_post_hook=None,
        guardrail_post_hook=None,
        model_runtime_info=_runtime_info(),
    )

    assert result is not None
    assert result.accepted is True
    after_conversation = persistent.get_conversation(CID)
    new_turn = next(
        turn
        for turn in after_conversation.conversation.turns
        if turn.turn_id.value == result.new_turn_id
    )
    assert new_turn.provenance is not None
    assert new_turn.provenance.model_identity == "main.qwen3-4b"
    assert new_turn.provenance.backend_key == "llama_cpp"
    assert new_turn.provenance.context_size == 8192
    # P6-CODEX-023: Repair's own Attempt Config Digest is actually populated,
    # not left `None` as it was before this Rework.
    assert new_turn.provenance.generation_config_digest_sha512 is not None
    assert len(new_turn.provenance.generation_config_digest_sha512) == 128


def test_governance_post_hook_exception_is_fail_closed_and_marked_degraded(
    tmp_path: Path,
) -> None:
    """P6-CODEX-021: a Governance Hook that itself raises must Deny, not
    silently Allow — the previous `except Exception: should_reject = False`
    was a genuine Fail-open Safety bug."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()

    def _raising_hook(_content: str) -> tuple[bool, str]:
        raise RuntimeError("governance hook internal failure")

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=_raising_hook,
        guardrail_post_hook=None,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "governance_post_hook_exception_fail_closed"
    assert result.degraded is True
    # Rejudge never ran — the exception is treated as an immediate Deny.
    assert len(service.calls) == 1


def test_guardrail_post_hook_exception_is_fail_closed_and_marked_degraded(
    tmp_path: Path,
) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()

    def _raising_hook(_content: str) -> tuple[bool, str]:
        raise RuntimeError("guardrail hook internal failure")

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=_raising_hook,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "guardrail_post_hook_exception_fail_closed"
    assert result.degraded is True


def test_normal_reject_is_not_marked_degraded(tmp_path: Path) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=lambda _content: (True, "denied"),
        guardrail_post_hook=None,
    )

    assert result is not None
    assert result.degraded is False


def test_budget_exhausted_before_rejudge_blocks_the_second_model_call(
    tmp_path: Path,
) -> None:
    """P6-CODEX-021: `max_total_model_calls` is now actually enforced — a
    Budget that only affords 1 real Call must block the Rejudge Call
    outright, never merely document an intent nothing checks."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()
    one_call_budget = RepairBudget(
        max_attempts=1,
        max_wall_time_ms=30_000,
        max_additional_tokens=2000,
        max_total_model_calls=1,
        max_depth=1,
    )

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=one_call_budget,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "repair_budget_exceeded_before_rejudge"
    assert len(service.calls) == 1  # the candidate call happened; rejudge never did


def test_budget_too_tight_for_the_rejudge_plan_is_rejected_before_the_call_is_ever_made(
    tmp_path: Path,
) -> None:
    """Controller Review (2026-09-04 22:41, P1/IR-R2-01) fix: a Budget
    whose remaining headroom (after the Repair Candidate call's own real
    consumption) cannot afford `_plan_rejudge()`'s own calibrated Rejudge
    allowance is now a Typed pre-call failure -- the Rejudge Call is never
    spent on a request already known to be infeasible. Superseded the
    pre-fix version of this test (`repair_budget_exceeded_after_rejudge`,
    `len(service.calls) == 2`): before this fix, `_REJUDGE_MAX_NEW_TOKENS`
    (200) was requested unconditionally regardless of the 8-token budget
    used here, the call was actually spent, and only the AFTER-the-call
    Usage check caught the overspend. See the test below for that AFTER-
    the-call check's own remaining real coverage (a Rejudge that overruns
    its own already-affordable plan)."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    before_conversation = persistent.get_conversation(CID)
    before_turn_count = len(before_conversation.conversation.turns)
    service = _FakeRepairService()
    tight_token_budget = RepairBudget(
        max_attempts=1,
        max_wall_time_ms=30_000,
        max_additional_tokens=8,
        max_total_model_calls=2,
        max_depth=1,
    )

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=tight_token_budget,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "repair_rejudge_budget_insufficient"
    # The crux: the Rejudge Call was never spent -- only the candidate
    # call happened, unlike the pre-fix behavior this test superseded.
    assert len(service.calls) == 1
    after_conversation = persistent.get_conversation(CID)
    assert len(after_conversation.conversation.turns) == before_turn_count


def test_a_rejudge_that_overruns_its_own_affordable_plan_is_still_rejected_after_the_call(
    tmp_path: Path,
) -> None:
    """P6-CODEX-030's original AFTER-the-call overspend check remains real
    coverage distinct from the pre-call `_plan_rejudge()` gate above: even
    when the plan itself was genuinely affordable (default `LIVE_REPAIR_
    BUDGET`, empty `rejudge_criteria` -> a 200-token plan, comfortably
    within the current 3600-token total), a Model that actually returns
    more completion tokens than requested must still be caught and
    rejected -- never silently Decoded/Accepted/Persisted merely because
    the pre-call plan looked affordable on paper."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    before_conversation = persistent.get_conversation(CID)
    before_turn_count = len(before_conversation.conversation.turns)
    service = _UsageScriptedRepairService(
        repair_completion_tokens=5,
        # Genuinely over LIVE_REPAIR_BUDGET.max_additional_tokens (3600)
        # combined with the candidate's own 5 -- simulates a real Model
        # that overran the `max_new_tokens` it was actually given.
        rejudge_completion_tokens=4000,
    )

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "repair_budget_exceeded_after_rejudge"
    # The crux: unlike the pre-call gate, this scenario's plan WAS
    # affordable on paper, so both real Calls actually happened.
    assert len(service.calls) == 2
    after_conversation = persistent.get_conversation(CID)
    assert len(after_conversation.conversation.turns) == before_turn_count


def test_stage_hook_is_called_with_rejudging_right_before_the_second_call(
    tmp_path: Path,
) -> None:
    """P6-OBS-004/P6-CODEX-031 (Fourth Rework): the "repairing" -> "
    rejudging" sub-transition happens entirely inside this function (the
    caller only ever sees one opaque `attempt_live_repair()` call) — the
    caller's own observable state can only advance past "repairing" via
    this `stage_hook`, called with exactly "rejudging" right before the
    Rejudge Model Call, never before the candidate call or after."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()
    stages_seen: list[str] = []

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        stage_hook=stages_seen.append,
    )

    assert stages_seen == ["rejudging"]
    assert result is not None
    assert result.accepted is True


def test_default_live_budget_allows_exactly_the_two_real_calls_repair_makes(
    tmp_path: Path,
) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
    )

    assert result is not None
    assert result.accepted is True
    assert len(service.calls) == 2


def test_cancellation_after_candidate_call_stops_before_rejudge(tmp_path: Path) -> None:
    """P6-CODEX-019/021: Main-priority preemption reaching Repair mid-flight
    must stop before spending the second real Model Call, not doggedly
    finish Rejudge first."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    cancellation = CancellationToken()

    class _CancelsAfterFirstCall(_FakeRepairService):
        def generate(
            self,
            request: GenerationRequest,
            *,
            cancellation: CancellationToken | None = None,
        ) -> GenerationResult:
            result = super().generate(request, cancellation=cancellation)
            cancellation_token.cancel()
            return result

    cancellation_token = cancellation
    service = _CancelsAfterFirstCall()

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        cancellation=cancellation,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "cancelled_by_main_priority"
    assert len(service.calls) == 1


def test_persistence_failure_at_start_generation_marks_the_orphan_turn_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P6-CODEX-021: a failure between append_derived_turn and
    start_generation must not leave the newly-appended Turn stuck PENDING
    forever — it is explicitly compensated to FAILED."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()
    real_start_generation = persistent.start_generation
    call_count = {"n": 0}

    def _failing_start_generation(
        *,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        request_id: str,
        operation_id: ConversationOperationId,
        expected_revision: int,
    ) -> StoredConversation:
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise RuntimeError("simulated storage failure")
        return real_start_generation(
            conversation_id=conversation_id,
            turn_id=turn_id,
            request_id=request_id,
            operation_id=operation_id,
            expected_revision=expected_revision,
        )

    monkeypatch.setattr(persistent, "start_generation", _failing_start_generation)

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "repair_persistence_failed_start"

    after_conversation = persistent.get_conversation(CID)
    orphan_candidates = [
        turn
        for turn in after_conversation.conversation.turns
        if turn.origin is ConversationTurnOrigin.REPAIR
    ]
    assert len(orphan_candidates) == 1
    assert orphan_candidates[0].state is ConversationTurnState.FAILED


def test_persistence_failure_at_complete_generation_marks_the_orphan_turn_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    service = _FakeRepairService()
    real_complete_generation = persistent.complete_generation
    call_count = {"n": 0}

    def _failing_complete_generation(
        *,
        conversation_id: ConversationId,
        turn_id: ConversationTurnId,
        assistant_message_id: ConversationMessageId,
        content: str,
        operation_id: ConversationOperationId,
        expected_revision: int,
        documentation_augmentation: DocumentationAugmentation | None = None,
        provenance: ConversationTurnProvenance | None = None,
    ) -> StoredConversation:
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise RuntimeError("simulated storage failure")
        return real_complete_generation(
            conversation_id=conversation_id,
            turn_id=turn_id,
            assistant_message_id=assistant_message_id,
            content=content,
            operation_id=operation_id,
            expected_revision=expected_revision,
            documentation_augmentation=documentation_augmentation,
            provenance=provenance,
        )

    monkeypatch.setattr(persistent, "complete_generation", _failing_complete_generation)

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
    )

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "repair_persistence_failed_complete"

    after_conversation = persistent.get_conversation(CID)
    orphan_candidates = [
        turn
        for turn in after_conversation.conversation.turns
        if turn.origin is ConversationTurnOrigin.REPAIR
    ]
    assert len(orphan_candidates) == 1
    assert orphan_candidates[0].state is ConversationTurnState.FAILED


# Controller Review (2026-09-04 22:41, P1/IR-R2-01) -- `_plan_rejudge()`
# own direct coverage. Unlike the `attempt_live_repair()` end-to-end tests
# below, these exercise the pure planning function in isolation: it takes
# no `cancellation` parameter at all, which is itself the structural proof
# that the same plan is computed regardless of Cancellation presence (see
# `test_rejudge_max_new_tokens_requested_is_identical_with_and_without_a_
# cancellation_token` below for the end-to-end confirmation of the same
# fact through the real production Call sites).


def test_plan_rejudge_uses_the_full_calibrated_allowance_for_a_normal_criterion_count() -> None:
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(5))
    plan = _plan_rejudge(
        rejudge_criteria=criteria,
        budget=LIVE_REPAIR_BUDGET,
        usage=RepairBudgetUsage(
            attempts_used=0,
            wall_time_used_ms=0,
            additional_tokens_used=5,  # the candidate call's own real cost
            total_model_calls_used=1,
            current_depth=0,
        ),
        rejudge_service=_UsageScriptedRepairService(),  # type: ignore[arg-type]  # no runtime_info -> no Context bound
        rejudge_prompt="(irrelevant when no Context bound applies)",
    )
    assert plan is not None
    assert plan.max_new_tokens == _REJUDGE_TOKENS_PER_CRITERION * 5


def test_plan_rejudge_fails_typed_before_any_call_for_a_large_criterion_count_over_budget() -> None:
    """A Criterion count well past the true default selection size (32):
    the full calibrated allowance for 40 Criteria (4000 tokens) cannot fit
    the ~3595 tokens actually remaining in the current 3600-token total
    Budget (`LIVE_REPAIR_BUDGET.max_additional_tokens`, User-authorized
    2026-09-05) after a 5-token candidate call -- `_plan_rejudge()` must
    return `None` (a pre-call Typed failure), never a silently-shrunk plan
    and never a plan that drops any Criterion to make a smaller request
    fit. (Before the 2000->2800->3600 Budget changes, the true default
    32-Criterion selection itself was this genuinely-over-budget case --
    see this section's own updated 32/33-Criterion boundary Tests further
    below for the Current boundary that replaced it.)"""
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(40))
    plan = _plan_rejudge(
        rejudge_criteria=criteria,
        budget=LIVE_REPAIR_BUDGET,
        usage=RepairBudgetUsage(
            attempts_used=0,
            wall_time_used_ms=0,
            additional_tokens_used=5,
            total_model_calls_used=1,
            current_depth=0,
        ),
        rejudge_service=_UsageScriptedRepairService(),  # type: ignore[arg-type]
        rejudge_prompt="(irrelevant when no Context bound applies)",
    )
    assert plan is None


def test_plan_rejudge_never_returns_a_plan_smaller_than_the_full_calibrated_allowance() -> None:
    """The remaining Budget is exactly 1 token short of the full
    5-Criterion allowance -- a plan that silently shrank to fit (e.g. the
    1-token-short amount) would violate "never drop/shrink below what
    every Criterion needs"; the only correct outcome is `None`."""
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(5))
    desired = _REJUDGE_TOKENS_PER_CRITERION * 5
    tight_budget = RepairBudget(
        max_attempts=1,
        max_wall_time_ms=30_000,
        max_additional_tokens=5 + desired - 1,  # 5 (candidate) + 1 short of the full allowance
        max_total_model_calls=2,
        max_depth=1,
    )
    plan = _plan_rejudge(
        rejudge_criteria=criteria,
        budget=tight_budget,
        usage=RepairBudgetUsage(
            attempts_used=0,
            wall_time_used_ms=0,
            additional_tokens_used=5,
            total_model_calls_used=1,
            current_depth=0,
        ),
        rejudge_service=_UsageScriptedRepairService(),  # type: ignore[arg-type]
        rejudge_prompt="(irrelevant when no Context bound applies)",
    )
    assert plan is None


def test_plan_rejudge_is_bounded_by_the_models_own_input_context() -> None:
    """A remaining token Budget alone would afford the full 5-Criterion
    allowance (750), but the Model's own loaded Context (200 tokens) minus
    this Rejudge Prompt's real token count (50, per the scripted `count_
    chat_prompt_tokens`) leaves only 150 tokens of room -- below what the
    full allowance needs. Mirrors `SeleneSemanticEvaluator._effective_max_
    prompt_tokens()`'s own established input-Context bound pattern."""
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(5))
    plan = _plan_rejudge(
        rejudge_criteria=criteria,
        budget=LIVE_REPAIR_BUDGET,
        usage=RepairBudgetUsage(
            attempts_used=0,
            wall_time_used_ms=0,
            additional_tokens_used=5,
            total_model_calls_used=1,
            current_depth=0,
        ),
        rejudge_service=_UsageScriptedRepairService(  # type: ignore[arg-type]
            loaded_context_size=200, prompt_token_count=50
        ),
        rejudge_prompt="(a real prompt would be scored by count_chat_prompt_tokens)",
    )
    assert plan is None


def test_plan_rejudge_skips_the_context_bound_when_the_service_exposes_no_runtime_info() -> None:
    """A minimal Fixture Service exposing neither `runtime_info` nor
    `count_chat_prompt_tokens` (`_FakeRepairService`'s own shape, used
    throughout this file's other tests) must never crash `_plan_rejudge()`
    -- the input-Context bound is simply skipped, exactly like Selene's
    own `_context_limit_tokens()` defensive fallback."""
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(5))
    plan = _plan_rejudge(
        rejudge_criteria=criteria,
        budget=LIVE_REPAIR_BUDGET,
        usage=RepairBudgetUsage(
            attempts_used=0,
            wall_time_used_ms=0,
            additional_tokens_used=5,
            total_model_calls_used=1,
            current_depth=0,
        ),
        rejudge_service=_FakeRepairService(),  # type: ignore[arg-type]
        rejudge_prompt="(irrelevant -- no runtime_info means no Context bound)",
    )
    assert plan is not None
    assert plan.max_new_tokens == _REJUDGE_TOKENS_PER_CRITERION * 5


# Controller Review (2026-09-04 22:41, P1/IR-R2-01) -- end-to-end coverage
# through the real production `attempt_live_repair()` Call sites (both the
# Cancellation-present and Cancellation-absent branches), not only the
# pure planner tested directly above.


def _multi_criterion_rejudge_json(criteria: tuple[JudgePromptCriterion, ...]) -> str:
    results = ",".join(
        f'{{"criterion_id": "{item.criterion_id}", "disposition": "pass", "confidence": 0.9}}'
        for item in criteria
    )
    return f'{{"recommendation": "accept", "confidence": 0.9, "criterion_results": [{results}]}}'


def test_a_normal_criterion_count_rejudge_succeeds_end_to_end_within_the_default_live_budget(
    tmp_path: Path,
) -> None:
    """P2 instruction "1件だけでなく通常件数の条件を検証" -- a normal (5)
    Criterion count, not just 1, genuinely succeeds within `LIVE_REPAIR_
    BUDGET`'s current 3600-token total, using the full calibrated
    per-Criterion allowance (500, never silently reduced)."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(5))
    service = _UsageScriptedRepairService(
        rejudge_content=_multi_criterion_rejudge_json(criteria),
    )

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
        rejudge_criteria=criteria,
    )

    assert result is not None
    assert result.accepted is True
    assert len(service.calls) == 2
    rejudge_call = service.calls[1]
    assert rejudge_call.parameters.max_new_tokens == _REJUDGE_TOKENS_PER_CRITERION * 5
    # Gemma Judge-only Constrained Decoding Rework (WU-06 isolation item 2):
    # a Main-self Rejudge (no `rejudge_structured_output_schema_factory`
    # supplied -- the default for every caller except the real Gemma-
    # configured dispatch) must never carry a `structured_output`
    # constraint.
    assert rejudge_call.parameters.structured_output is None
    # Gemma Constrained Decoding Final Contract Micro Rework (IR-FC-01
    # Required Test: "Factory/Override未指定の既存Rejudgeは現在のDefault
    # のまま"): no `rejudge_sampling_overrides` supplied (the default for
    # every caller except the real Gemma-configured dispatch) must leave
    # `GenerationParameters`'s own ordinary library defaults untouched.
    assert rejudge_call.parameters.temperature == 0.7
    assert rejudge_call.parameters.top_p == 0.8
    assert rejudge_call.parameters.top_k == 20
    assert rejudge_call.parameters.seed is None


def test_rejudge_applies_the_supplied_structured_output_schema_factory_to_the_exact_criteria(
    tmp_path: Path,
) -> None:
    """Gemma Judge-only Constrained Decoding Rework (WU-03): when a caller
    DOES supply `rejudge_structured_output_schema_factory` (only the real
    Gemma-configured dedicated dispatch does), the Rejudge Call's own
    `GenerationParameters.structured_output` must be built from the exact
    `rejudge_criteria` id set this same Rejudge Prompt was rendered
    against -- proving the initial dispatch and the Rejudge share one
    Schema-generation rule, in isolation from the full Fixture Golden
    Path's own end-to-end proof."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(3))
    service = _UsageScriptedRepairService(
        rejudge_content=_multi_criterion_rejudge_json(criteria),
    )
    factory_calls: list[tuple[str, ...]] = []

    def factory(criterion_ids: tuple[str, ...]) -> StructuredOutputConstraint:
        factory_calls.append(criterion_ids)
        return StructuredOutputConstraint.from_schema(
            {
                "type": "object",
                "properties": {
                    "criterion_results": {"type": "array", "minItems": len(criterion_ids)}
                },
            }
        )

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
        rejudge_criteria=criteria,
        rejudge_structured_output_schema_factory=factory,
    )

    assert result is not None
    assert result.accepted is True
    rejudge_call = service.calls[1]
    assert factory_calls == [tuple(item.criterion_id for item in criteria)]
    constraint = rejudge_call.parameters.structured_output
    assert constraint is not None
    properties = cast(dict[str, object], constraint.json_schema["properties"])
    criterion_results_schema = cast(dict[str, object], properties["criterion_results"])
    assert criterion_results_schema["minItems"] == 3


def test_rejudge_applies_the_supplied_sampling_overrides_matching_the_initial_judge_contract(
    tmp_path: Path,
) -> None:
    """Codex Controller Review (2026-09-06 12:44, IR-FC-01) fix: before this
    fix, the Rejudge Call's own `GenerationParameters` was always built as
    bare `GenerationParameters(max_new_tokens=...)`, silently falling back
    to library defaults (`temperature=0.7`/`top_p=0.8`/`top_k=20`/
    `presence_penalty=1.5`/`seed=None`) regardless of what Provider-local
    frozen Sampling contract the initial Judge Batches actually used --
    Controller confirmed a real Gemma Rejudge ran under a DIFFERENT
    generation contract than its own initial verdict. Supplying the exact
    real `GEMMA_JUDGE_DETERMINISTIC_SAMPLING` mapping here (the one real
    caller, `judge_live_integration.py`'s `_run_selene_dispatch()`, sources
    this from its own Gemma-configured `SeleneSemanticEvaluator.sampling_
    overrides` property) must make the Rejudge Call carry the identical
    values, while the Rejudge Plan's own `max_new_tokens` -- a completely
    separate concern -- is never overridden by this mapping."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(3))
    service = _UsageScriptedRepairService(
        rejudge_content=_multi_criterion_rejudge_json(criteria),
    )

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
        rejudge_criteria=criteria,
        rejudge_sampling_overrides=GEMMA_JUDGE_DETERMINISTIC_SAMPLING,
    )

    assert result is not None
    assert result.accepted is True
    rejudge_call = service.calls[1]
    assert rejudge_call.parameters.temperature == 0.0
    assert rejudge_call.parameters.top_p == 1.0
    assert rejudge_call.parameters.top_k == 1
    assert rejudge_call.parameters.min_p == 0.0
    assert rejudge_call.parameters.presence_penalty == 0.0
    assert rejudge_call.parameters.frequency_penalty == 0.0
    assert rejudge_call.parameters.repeat_penalty == 1.0
    assert rejudge_call.parameters.seed == 0
    # The Rejudge Plan's own token budget is a separate concern from
    # Sampling -- never silently replaced by the Sampling contract, even
    # though `GEMMA_JUDGE_DETERMINISTIC_SAMPLING` itself has no `max_new_
    # tokens` key today (defense in depth against a future override that
    # might add one).
    assert rejudge_call.parameters.max_new_tokens == _REJUDGE_TOKENS_PER_CRITERION * 3


def test_rejudge_sampling_overrides_never_leak_into_the_repair_candidate_call(
    tmp_path: Path,
) -> None:
    """Codex Controller Review (2026-09-06 12:44, IR-FC-01) Required Test:
    "Repair CandidateにSampling/Grammarが逆流しない" -- the Repair
    Candidate generation Call (the first of the two real Model Calls this
    function makes) must stay exactly as it always has, unaffected by
    whatever `rejudge_sampling_overrides` the caller supplies for the
    SECOND (Rejudge) Call only."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(3))
    service = _UsageScriptedRepairService(
        rejudge_content=_multi_criterion_rejudge_json(criteria),
    )

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
        rejudge_criteria=criteria,
        rejudge_sampling_overrides=GEMMA_JUDGE_DETERMINISTIC_SAMPLING,
    )

    assert result is not None
    candidate_call = service.calls[0]
    assert candidate_call.parameters.temperature == 0.7
    assert candidate_call.parameters.top_p == 0.8
    assert candidate_call.parameters.top_k == 20
    assert candidate_call.parameters.seed is None
    assert candidate_call.parameters.structured_output is None
    assert candidate_call.parameters.max_new_tokens == _REPAIR_MAX_NEW_TOKENS


def test_a_normal_32_criterion_selection_rejudge_succeeds_end_to_end_within_the_3600_token_live_budget(  # noqa: E501
    tmp_path: Path,
) -> None:
    """Handoff requirement (`docs/project/phases/phase_9/handoffs/
    phase_9_controller_real_32_criterion_rejudge_budget_3600_exact_
    handoff_ja_20260905091431.md` §3.2): the true default selection size
    (32 Criteria, `bootstrap.runtime_governance.SemanticRuntimeBindingContext.
    max_criteria`'s own default) genuinely succeeds Repair->Rejudge->
    adoption end to end within `LIVE_REPAIR_BUDGET`'s current
    (User-authorized) 3600-token ceiling -- never merely a Plan-acceptance
    check. The Repair Candidate is scripted to consume its full 400-token
    allowance (`_REPAIR_MAX_NEW_TOKENS`), the single tightest realistic
    boundary (`400+100*32=3600<=3600`, zero headroom) -- not just a
    minimal-cost case. All 32 Criteria arrive at the Rejudge Decoder
    (never dropped, never batched), exactly 2 real Model Calls are made
    (Candidate then Rejudge, never more), and the improved answer is
    genuinely accepted (this Fixture-scripted Test proves the pre-call
    Plan/Budget arithmetic only -- whether a real Gemma Rejudge finishes
    without truncating within 3200 real Tokens is a separate, real-Model
    question this Test cannot answer; see `test_real_local_main_gemma_
    concurrent_dispatch_smoke.py`'s own real-hardware Test for that).
    Before the 2000->2800->3600 Budget changes, this exact scenario was
    the genuinely-infeasible case at each prior ceiling in turn."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(32))
    service = _UsageScriptedRepairService(
        repair_completion_tokens=_REPAIR_MAX_NEW_TOKENS,
        rejudge_content=_multi_criterion_rejudge_json(criteria),
    )

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
        rejudge_criteria=criteria,
    )

    assert result is not None
    assert result.accepted is True
    # The crux: both real Model Calls were made -- the Rejudge Call was
    # never blocked by a Typed pre-call failure, unlike each of this
    # exact selection size's genuine infeasibilities at prior ceilings.
    assert len(service.calls) == 2
    rejudge_call = service.calls[1]
    assert rejudge_call.parameters.max_new_tokens == _REJUDGE_TOKENS_PER_CRITERION * 32 == 3200
    total_used = service.repair_completion_tokens + service.rejudge_completion_tokens
    assert total_used <= LIVE_REPAIR_BUDGET.max_additional_tokens


# Controller Review (2026-09-04 23:54, IR-R3-02; corrected 2026-09-05
# 00:35, IR-R4-02; superseded 2026-09-05 07:52, User-authorized 2000->2800
# Budget change; superseded again 2026-09-05 09:14, User-authorized
# 75->100 per-Criterion and 2800->3600 Budget change, `docs/project/
# phases/phase_9/handoffs/phase_9_controller_real_32_criterion_rejudge_
# budget_3600_exact_handoff_ja_20260905091431.md`) -- historical record:
# the real, evidence-based recalibration of `_REJUDGE_TOKENS_PER_CRITERION`
# (150 -> 75, see that constant's own updated docstring for the
# measurement) did NOT by itself make the true default selection size (32,
# `SemanticRuntimeBindingContext.max_criteria`) fit the THEN-current
# `LIVE_REPAIR_BUDGET.max_additional_tokens=2000` ceiling. User then
# authorized raising `max_additional_tokens` from 2000 to 2800 (at the
# time, `_REJUDGE_TOKENS_PER_CRITERION` stayed 75); a real-hardware trial
# against that 2800 ceiling then confirmed (via Test-only Observability,
# `docs/project/phases/phase_9/handoffs/phase_9_claude_real_32_criterion_
# complete_log_capture_exact_return_ja_20260905085935.md`) a genuine
# Decoder FAILED (`finish_reason=LENGTH`, truncated mid-JSON) at that
# ceiling. Based on that confirmed real Evidence, User authorized raising
# BOTH `_REJUDGE_TOKENS_PER_CRITERION` (75 -> 100) and `max_additional_
# tokens` (2800 -> 3600) together -- the only Budget/Criterion/Decoder
# changes made across this whole multi-round investigation.
# `_REPAIR_MAX_NEW_TOKENS` (400) and the real default selection size (32)
# are unchanged throughout.
#
# IR-R4-02 correction (still applies, unchanged by either Budget change):
# the Tests immediately below call `_plan_rejudge()` directly and check
# only `max_new_tokens` -- they prove `_plan_rejudge()` ACCEPTS a Token
# Plan for a given Criterion count, never generation, Decode, improved-
# answer adoption, or persistence. "32件Plan受理" (a 32-Criterion Plan is
# accepted) is the honest description of these direct-call Tests; "32件
# Repair→Rejudge成立/実行成立" (32 Criteria genuinely succeed end to end)
# is proven separately, by `test_a_normal_32_criterion_selection_rejudge_
# succeeds_end_to_end_within_the_3600_token_live_budget` further above,
# which exercises the real `attempt_live_repair()` production path. The
# 100-token/Criterion figure itself remains a measured-verbosity estimate
# informed by real Gemma truncation Evidence, not a guarantee that a real
# Model genuinely finishes within it -- see `_REJUDGE_TOKENS_PER_CRITERION`'s
# own docstring.
#
# Current boundary (3600-token ceiling): a minimal 5-token Candidate cost
# (as used below, matching this module's other Fixtures) admits 32
# Criteria with room to spare (`100*32=3200 <= 3600-5=3595`); the Repair
# Candidate's own `max_new_tokens` ceiling is 400, and if a real Candidate
# genuinely used that full allowance, the true default selection size of
# 32 Criteria fits EXACTLY, with zero headroom
# (`400+100*32=3600<=3600`), while one Criterion further (33) does not
# (`400+100*33=3700>3600`) -- both included below as their own Test, not
# silently omitted. The former 2000-token-era and 2800-token-era boundary
# Tests this section used to carry are replaced below so no stale
# superseded boundary is left describing Current behavior; the historical
# record itself is preserved, unedited, in `docs/project/shared/history/
# unresolved/phase_9_1_rejudge_token_calibration_and_32_criterion_
# infeasibility_snapshot_ja_20260905000817.md` and `phase_9_1_26_criterion_
# plan_acceptance_vs_execution_claim_correction_snapshot_ja_
# 20260905005446.md`.


def test_a_32_criterion_token_plan_is_accepted_within_the_3600_budget_after_a_minimal_candidate_cost() -> (  # noqa: E501
    None
):
    """`_plan_rejudge()` accepts a Token Plan for the true default
    selection size (32 Criteria) within `LIVE_REPAIR_BUDGET`'s current
    (User-authorized) 3600-token ceiling, given a minimal 5-token
    Candidate cost: `100 * 32 = 3200 <= 3600 - 5 = 3595`. This is Plan
    acceptance only (see this section's own header comment) -- never a
    claim that a real 32-Criterion Repair->Rejudge Attempt against a real
    Model succeeds end to end (see the dedicated End-to-End Test further
    above for that), and never a Fixture shrunk or a Criterion dropped to
    make a smaller number "work"."""
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(32))
    plan = _plan_rejudge(
        rejudge_criteria=criteria,
        budget=LIVE_REPAIR_BUDGET,
        usage=RepairBudgetUsage(
            attempts_used=0,
            wall_time_used_ms=0,
            additional_tokens_used=5,
            total_model_calls_used=1,
            current_depth=0,
        ),
        rejudge_service=_UsageScriptedRepairService(),  # type: ignore[arg-type]
        rejudge_prompt="(irrelevant when no Context bound applies)",
    )
    assert plan is not None
    assert plan.max_new_tokens == _REJUDGE_TOKENS_PER_CRITERION * 32 == 3200


def test_a_32_criterion_token_plan_is_the_boundary_when_the_candidate_uses_its_full_token_allowance() -> (  # noqa: E501
    None
):
    """The exact boundary Codex Controller's own minimal-change proposal
    computed: the Repair Candidate's own `max_new_tokens` ceiling is 400
    (`_REPAIR_MAX_NEW_TOKENS`) -- if a real Candidate genuinely consumed
    that full allowance, the true default selection size of 32 Criteria
    fits EXACTLY, with zero headroom to spare (`400+100*32=3600<=3600`),
    while one Criterion further (33) does not
    (`400+100*33=3700>3600`). Plan acceptance only, same caveat as the
    32-Criterion Test above."""
    criteria_32 = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(32))
    plan_32 = _plan_rejudge(
        rejudge_criteria=criteria_32,
        budget=LIVE_REPAIR_BUDGET,
        usage=RepairBudgetUsage(
            attempts_used=0,
            wall_time_used_ms=0,
            additional_tokens_used=_REPAIR_MAX_NEW_TOKENS,
            total_model_calls_used=1,
            current_depth=0,
        ),
        rejudge_service=_UsageScriptedRepairService(),  # type: ignore[arg-type]
        rejudge_prompt="(irrelevant when no Context bound applies)",
    )
    assert plan_32 is not None
    assert plan_32.max_new_tokens == _REJUDGE_TOKENS_PER_CRITERION * 32 == 3200

    criteria_33 = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(33))
    plan_33 = _plan_rejudge(
        rejudge_criteria=criteria_33,
        budget=LIVE_REPAIR_BUDGET,
        usage=RepairBudgetUsage(
            attempts_used=0,
            wall_time_used_ms=0,
            additional_tokens_used=_REPAIR_MAX_NEW_TOKENS,
            total_model_calls_used=1,
            current_depth=0,
        ),
        rejudge_service=_UsageScriptedRepairService(),  # type: ignore[arg-type]
        rejudge_prompt="(irrelevant when no Context bound applies)",
    )
    assert plan_33 is None


def test_the_3600_token_budget_is_exceeded_by_exactly_one_token_and_rejected() -> None:
    """Handoff requirement (`phase_9_controller_real_32_criterion_rejudge_
    budget_3600_exact_handoff_ja_20260905091431.md` §3.3): a Plan that
    would exceed the 3600-token ceiling by even a single token is
    rejected, never silently accepted or shrunk.

    Candidate cost is kept at the realistic 400 ceiling (the same
    tightest real boundary the 32/33-Criterion Test above already
    exercises, mirroring the 2026-09-05 08:25 Controller correction that
    first established this pattern for the prior 2800 ceiling); a
    separate, LOCAL Budget object one token tighter than Production
    (3599, never mutating `LIVE_REPAIR_BUDGET` itself) is used instead,
    so `100*32=3200` genuinely exceeds the `3599-400=3199` remaining by
    exactly one token."""
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(32))
    one_token_short_of_3600 = RepairBudget(
        max_attempts=LIVE_REPAIR_BUDGET.max_attempts,
        max_wall_time_ms=LIVE_REPAIR_BUDGET.max_wall_time_ms,
        max_additional_tokens=3599,
        max_total_model_calls=LIVE_REPAIR_BUDGET.max_total_model_calls,
        max_depth=LIVE_REPAIR_BUDGET.max_depth,
    )
    plan = _plan_rejudge(
        rejudge_criteria=criteria,
        budget=one_token_short_of_3600,
        usage=RepairBudgetUsage(
            attempts_used=0,
            wall_time_used_ms=0,
            additional_tokens_used=_REPAIR_MAX_NEW_TOKENS,
            total_model_calls_used=1,
            current_depth=0,
        ),
        rejudge_service=_UsageScriptedRepairService(),  # type: ignore[arg-type]
        rejudge_prompt="(irrelevant when no Context bound applies)",
    )
    assert plan is None
    # Confirms the Production Budget itself was never mutated by this Test.
    assert LIVE_REPAIR_BUDGET.max_additional_tokens == 3600


def test_rejudge_max_new_tokens_requested_is_identical_with_and_without_a_cancellation_token(
    tmp_path: Path,
) -> None:
    """The crux of P1/IR-R2-01: before this fix, the Cancellation-present
    branch requested `_rejudge_max_new_tokens(rejudge_criteria)` (750 for
    5 Criteria) while the Cancellation-absent branch silently requested
    the old fixed 200 for the identical Criterion set -- two different
    real requests for the same Rejudge. Both branches now go through the
    same `_plan_rejudge()` call site, so the actual `max_new_tokens` sent
    to the Model is identical either way."""
    criteria = tuple(_criterion(f"semantic.argd.evidence.{i}") for i in range(5))
    rejudge_json = _multi_criterion_rejudge_json(criteria)

    persistent_a, request_id_a = _build_persistent_with_one_completed_turn(tmp_path)
    service_a = _UsageScriptedRepairService(rejudge_content=rejudge_json)
    result_a = attempt_live_repair(
        service=service_a,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent_a,
        request_id=request_id_a,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
        rejudge_criteria=criteria,
        cancellation=CancellationToken(),
    )

    second_store_root = tmp_path / "second-store"
    second_store_root.mkdir()
    persistent_b, request_id_b = _build_persistent_with_one_completed_turn(second_store_root)
    service_b = _UsageScriptedRepairService(rejudge_content=rejudge_json)
    result_b = attempt_live_repair(
        service=service_b,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent_b,
        request_id=request_id_b,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
        rejudge_criteria=criteria,
        cancellation=None,
    )

    assert result_a is not None and result_a.accepted is True
    assert result_b is not None and result_b.accepted is True
    tokens_a = service_a.calls[1].parameters.max_new_tokens
    tokens_b = service_b.calls[1].parameters.max_new_tokens
    assert tokens_a == tokens_b == _REJUDGE_TOKENS_PER_CRITERION * 5


# Controller Review (2026-09-04 23:54, IR-R3-01) -- Planner exception and
# remaining-Deadline boundary coverage. Exact reproduction of Controller's
# own two Probes against the P1/IR-R2-01 fix above.


def test_a_counter_exception_returns_a_typed_result_never_an_uncaught_exception(
    tmp_path: Path,
) -> None:
    """Controller's own Probe: subclass `_UsageScriptedRepairService` with
    `loaded_context_size=8192`, `count_chat_prompt_tokens()` raising
    `RuntimeError`. Before this fix, that exception propagated straight
    out of `_plan_rejudge()` and past `attempt_live_repair()` uncaught --
    the Candidate Call happened but no Typed Repair Result was ever
    returned for the Attempt.

    Controller Review (2026-09-05 07:18, IR-R5-01) correction: this Test
    previously asserted `rejected_reason == "repair_rejudge_budget_
    insufficient"` -- Controller correctly flagged that as wrong: a Counter
    that raises is an infrastructure fault, never a genuine Token/Context
    shortfall, and conflating the two hid this exact case from an operator
    reading the reported reason. Now Typed distinctly as `repair_rejudge_
    counter_failed`."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    criteria = (_criterion("semantic.argd.evidence.1"),)
    service = _CounterRaisingRepairService(loaded_context_size=8192)

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
        rejudge_criteria=criteria,
    )

    # The crux: a real Typed Result came back -- the Counter's own failure
    # never escaped as an uncaught exception, and is reported as its own
    # real cause, never as a generic "budget insufficient".
    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "repair_rejudge_counter_failed"
    # The Candidate Call happened; the Rejudge Call was never attempted
    # (the Counter failure is a pre-call Typed failure, same as a genuine
    # over-budget Plan).
    assert len(service.calls) == 1


def test_a_slow_counter_exhausting_the_overall_deadline_blocks_the_rejudge_call(
    tmp_path: Path,
) -> None:
    """Controller's own second Probe: a 50ms Counter against a 20ms total
    Repair Budget. Before this fix, neither Cancellation branch re-checked
    the overall wall-time Budget after Planning's own real cost -- both
    spent the real Rejudge Call anyway and were only caught by the
    existing AFTER-the-call check (`repair_budget_exceeded_after_rejudge`),
    which had already wasted the Call. Checked for both Cancellation
    presence and absence, matching P1's own "same Plan/boundary regardless
    of Cancellation" contract."""
    tight_deadline_budget = RepairBudget(
        max_attempts=1,
        max_wall_time_ms=20,
        max_additional_tokens=2000,
        max_total_model_calls=2,
        max_depth=1,
    )
    criteria = (_criterion("semantic.argd.evidence.1"),)

    persistent_a, request_id_a = _build_persistent_with_one_completed_turn(tmp_path)
    service_a = _SlowCounterRepairService(loaded_context_size=8192, counter_delay_seconds=0.05)
    result_a = attempt_live_repair(
        service=service_a,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent_a,
        request_id=request_id_a,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=tight_deadline_budget,
        rejudge_criteria=criteria,
        cancellation=CancellationToken(),
    )

    second_store_root = tmp_path / "second-store"
    second_store_root.mkdir()
    persistent_b, request_id_b = _build_persistent_with_one_completed_turn(second_store_root)
    service_b = _SlowCounterRepairService(loaded_context_size=8192, counter_delay_seconds=0.05)
    result_b = attempt_live_repair(
        service=service_b,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent_b,
        request_id=request_id_b,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=tight_deadline_budget,
        rejudge_criteria=criteria,
        cancellation=None,
    )

    for result, service in ((result_a, service_a), (result_b, service_b)):
        assert result is not None
        assert result.accepted is False
        # The crux: the Rejudge Call was never made -- caught by the
        # pre-call Deadline re-check, never the AFTER-the-call check.
        assert result.rejected_reason == "repair_budget_exceeded_before_rejudge"
        assert len(service.calls) == 1


# Controller Review (2026-09-05 00:35, IR-R4-01) -- Planner wait/Cancel
# boundary. Both Tests reproduce Controller's own two exact Probes: a
# Counter that blocks past the Deadline on an external Event (never a
# fixed, finite delay), and a Counter that cancels its own passed-in
# CancellationToken mid-count.


def test_a_counter_that_blocks_past_the_deadline_returns_promptly_and_never_reaches_rejudge(
    tmp_path: Path,
) -> None:
    """Controller's own exact reproduction: a Counter Fixture that blocks
    on a `threading.Event` released only externally -- genuinely unbounded
    from this function's own perspective, unlike `_SlowCounterRepairService`'s
    fixed delay. Before this fix, `attempt_live_repair()` itself did not
    return until the Counter's blocking call finally returned (Controller's
    own measurement: ~120-123ms against a 20ms Budget) -- the AFTER-the-fact
    Budget check was correct once reached, but nothing bounded the *wait*
    itself. `run_tracked_stage()` now bounds that wait to the real
    remaining `RepairBudget.max_wall_time_ms` -- this function must return
    close to that Budget, never wait for the full, unbounded block
    duration. The blocked background Thread is never killed (Python cannot
    safely do that); a `threading.Timer` safety net plus an explicit
    release in `finally` guarantee the Event is always eventually set, so
    no Thread is left blocked past this Test's own lifetime."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    criteria = (_criterion("semantic.argd.evidence.1"),)
    block_event = threading.Event()
    # Safety net: even if the fix under test were broken (this function
    # waiting for the full, unbounded block), the Test itself must not
    # hang forever -- this guarantees the Event is released within 5s
    # regardless, turning a would-be hang into a plain, fast assertion
    # failure instead.
    safety_timer = threading.Timer(5.0, block_event.set)
    safety_timer.start()
    service = _EventBlockingCounterRepairService(loaded_context_size=8192, block_event=block_event)
    tight_deadline_budget = RepairBudget(
        max_attempts=1,
        max_wall_time_ms=100,
        max_additional_tokens=2000,
        max_total_model_calls=2,
        max_depth=1,
    )
    started = time.monotonic()
    try:
        result = attempt_live_repair(
            service=service,  # type: ignore[arg-type]
            model_key="main.test-model",
            persistent=persistent,
            request_id=request_id,
            user_input="Question",
            original_answer="Original",
            before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
            judge_reasoning="",
            governance_post_hook=None,
            guardrail_post_hook=None,
            budget=tight_deadline_budget,
            rejudge_criteria=criteria,
        )
        elapsed_ms = (time.monotonic() - started) * 1000
    finally:
        block_event.set()
        safety_timer.cancel()

    assert result is not None
    assert result.accepted is False
    assert result.rejected_reason == "repair_budget_exceeded_before_rejudge"
    # The crux: the Rejudge Call was never made.
    assert len(service.calls) == 1
    # The crux: this function returned close to the real Budget (100ms),
    # never waiting for the Event's own unbounded block duration. A
    # generous but meaningful ceiling -- well under the 5s safety net,
    # proving the real `run_tracked_stage()` boundary is what returned
    # control, not the safety net catching a hang.
    assert elapsed_ms < 2000, f"expected a prompt return near 100ms, took {elapsed_ms:.0f}ms"


def test_a_cancellation_firing_during_counting_blocks_the_rejudge_call(tmp_path: Path) -> None:
    """Controller's own exact reproduction: a Counter Fixture that cancels
    the same `CancellationToken` `attempt_live_repair()` itself was given,
    then returns normally (never raising, never blocking) -- simulates a
    genuine Main-priority preemption arriving while counting is in
    progress. Before this fix, Cancellation was never re-checked after
    Planning returned a valid Plan, so the real Rejudge Service Call was
    still reached (Controller's own Probe confirmed this) and only that
    Call's own `stage_deadline()` wrapper eventually reported `cancelled_
    by_main_priority` -- after a real Model Call had already been spent.
    Now the Executor's own explicit re-check, immediately after Planning
    returns and before the Budget check, catches this before the Rejudge
    Call is ever made."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    criteria = (_criterion("semantic.argd.evidence.1"),)
    cancellation = CancellationToken()
    service = _SelfCancellingCounterRepairService(
        loaded_context_size=8192, cancellation=cancellation
    )

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
        rejudge_criteria=criteria,
        cancellation=cancellation,
    )

    assert result is not None
    assert result.accepted is False
    # The crux: reported as a genuine Cancellation, never conflated with
    # "budget insufficient" or a successful Plan.
    assert result.rejected_reason == "cancelled_by_main_priority"
    # The crux: the Rejudge Call was never made.
    assert len(service.calls) == 1


# Controller Review (2026-09-05 07:18, IR-R5-01) -- Planner Failure
# classification. Controller's own second exact Probe from that Review: a
# `TrackedStageWorkerRegistry` that has already begun `shutdown()` refuses
# a NEW Stage submission -- `_plan_rejudge()`'s pre-fix version could only
# convert that into the same bare `None` a genuine Token/Context shortfall
# produces, which the caller then reported as the same generic
# `repair_rejudge_budget_insufficient`, even though nothing about the
# Repair's own Token/Context Budget was ever actually insufficient.


def test_a_shutting_down_worker_registry_rejects_counting_and_is_reported_distinctly(
    tmp_path: Path,
) -> None:
    """Controller's own exact reproduction: shut down a real
    `TrackedStageWorkerRegistry` BEFORE this Attempt begins, then pass it
    in as `tracked_stage_registry` -- `TrackedStageWorkerRegistry.submit()`
    refuses the new Counter submission outright (`accepting_new_work()` is
    already `False`), and `run_tracked_stage()` reports that as a Timeout-
    shaped Outcome carrying `bootstrap.tracked_stage_worker.REGISTRY_
    SHUTTING_DOWN_MESSAGE`. The crux: this must be Typed as its own real
    cause (`repair_rejudge_worker_registry_unavailable`), never re-labeled
    as "budget insufficient" and never an uncaught exception."""
    persistent, request_id = _build_persistent_with_one_completed_turn(tmp_path)
    criteria = (_criterion("semantic.argd.evidence.1"),)
    service = _UsageScriptedRepairService(loaded_context_size=8192)
    registry = TrackedStageWorkerRegistry()
    # Shut down before this Attempt even starts -- `accepting_new_work()`
    # is already `False` by the time the Counter would be submitted.
    assert registry.shutdown(timeout_seconds=1.0) is True

    result = attempt_live_repair(
        service=service,  # type: ignore[arg-type]
        model_key="main.test-model",
        persistent=persistent,
        request_id=request_id,
        user_input="Question",
        original_answer="Original",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        judge_reasoning="",
        governance_post_hook=None,
        guardrail_post_hook=None,
        budget=LIVE_REPAIR_BUDGET,
        rejudge_criteria=criteria,
        tracked_stage_registry=registry,
    )

    assert result is not None
    assert result.accepted is False
    # The crux: a shutting-down Registry is its own real, Typed cause --
    # never conflated with a genuine Token/Context shortfall.
    assert result.rejected_reason == "repair_rejudge_worker_registry_unavailable"
    # The Candidate Call happened; the Rejudge Call was never attempted.
    assert len(service.calls) == 1
