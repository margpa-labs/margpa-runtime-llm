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

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from margpa_runtime_llm.bootstrap.repair_live_integration import (
    LIVE_REPAIR_BUDGET,
    attempt_live_repair,
)
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
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationRecommendation
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationRequest,
    GenerationResult,
    GenerationTiming,
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
from margpa_runtime_llm.modules.repair.domain.budget import RepairBudget
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


def test_budget_exhausted_by_rejudge_tokens_blocks_persistence_after_the_second_call(
    tmp_path: Path,
) -> None:
    """P6-CODEX-030 (Fourth Rework): the Budget was previously re-checked
    only ONCE, before the Rejudge call — nothing re-verified it after the
    Rejudge actually completed and consumed its own real tokens, so a
    Rejudge that pushed Usage over budget could still have its Candidate
    Decoded, evaluated as Accepted, and PERSISTED. Here the candidate
    call's own 5 completion tokens alone stay within an 8-token budget (so
    the before-Rejudge check still lets the Rejudge run), but the
    Rejudge's own further 5 tokens push total usage to 10 — over budget —
    and the New Attempt must be rejected before any Decode/Acceptance/
    Persistence, leaving the Turn exactly as it was before this Attempt."""
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
    assert result.rejected_reason == "repair_budget_exceeded_after_rejudge"
    assert len(service.calls) == 2  # both the candidate AND the rejudge call happened
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
