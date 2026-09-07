"""R2-WU-06 (Handoff §7): "Fixture Modelによる Production Composition
Integrationを先に作り、配線を確定する" -- the Fixture-model half of the
Production Web Composition Golden Path this Rework requires before any real-
hardware confirmation:

    Main Governance: ENFORCE
    Judge: Gemma (dedicated, Selene-shaped Batched Evaluator) ENFORCE
    Repair (Judge-side toggle): OFF
    Recording: FULL
    real Persistence, real same-Turn save

`test_judge_repair_rejudge_normal_enforce_save_path.py` already proves the
real Conversation -> Judge Hook -> Repair -> Rejudge -> same-Turn-save chain
for Main-origin authorization, but only ever through the unbatched Main-
shared general-quality dispatch, and always with `recording_mode="off"`.
This module closes both gaps at once: Judge dispatches through a dedicated
`SeleneSemanticEvaluator`-shaped Fake (the same duck-typed shape Gemma's own
`SeleneRoleAdapter.semantic_evaluator` presents -- see `judge_live_
integration.py`'s `selene_evaluator is not None` branch), and Recording is
genuinely FULL, writing real Turn/Judge-Evidence JSON files via the real
`LocalFilesystemRecordingWriter` (never a Fake sink) into `tmp_path`, read
back and asserted on directly -- proving persistence, not merely a Hook
callback firing.

Guard is not wired at all here (`guardrail_pre_hook`/`guardrail_post_hook`
left `None`) -- the Handoff's own "Guard OFF" arm; `ConversationGeneration
Session` already tolerates an unwired Guardrail Hook as Guard-absent, the
identical shape Guard OFF itself produces (Detector/Action Call 0), so
this is a faithful, no-op stand-in for that arm."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from concurrent.futures import Future
from datetime import UTC, datetime, timedelta
from functools import partial
from pathlib import Path
from types import TracebackType

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
from margpa_runtime_llm.adapters.runtime_observability.local_filesystem_recording_writer import (
    LocalFilesystemRecordingWriter,
)
from margpa_runtime_llm.bootstrap.judge_live_integration import (
    build_judge_completion_hook,
)
from margpa_runtime_llm.bootstrap.recording_live_integration import (
    build_judge_evidence_recorder,
    build_recording_completion_hook,
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
from margpa_runtime_llm.modules.runtime_governance.application import SemanticRuntimeCoordinator
from margpa_runtime_llm.modules.runtime_governance.domain import (
    RuntimeCapabilitySnapshot,
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticEvaluationMethod,
    SemanticEvaluationRequest,
    SemanticEvaluationResponse,
    SemanticEvaluationStage,
    SemanticProviderState,
)
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.modules.runtime_observability.domain.recording import RecordingMode
from margpa_runtime_llm.modules.summarization.public import SummaryMode

SCOPE = ConversationScopeId(value="scope-production-composition")
CID = ConversationId(value="conversation-production-composition-1")
_GEMMA_MODEL_KEY = "judge.gemma-4-e2b-it-q4-0"
_MAIN_MODEL_KEY = "main.test-model"
_WRONG_ANSWER = "The capital of France is Tenon."
_CORRECTED_ANSWER = "The capital of France is Paris."
_RUNTIME_REF = ModelRuntimeReference(
    load_instance_id="load-1",
    model_key=_GEMMA_MODEL_KEY,
    backend_key="fake",
    backend_version="0.0.0",
    definition_file_sha512="a" * 128,
)
# The real EXECUTED Judge Provider's own `ModelRuntimeInfo` (distinct from
# `_RUNTIME_REF` above -- `GenerationResult.runtime_info` uses the lighter
# `ModelRuntimeReference` shape, while `InferenceService.runtime_info`, the
# one `_pending_evidence()` actually reads its Artifact Digest/Backend
# Key/Version from, is this full contract) -- proves R2-WU-02's fix reaches
# real persisted Evidence with Gemma's own identity, never Main's.
_GEMMA_RUNTIME_INFO = ModelRuntimeInfo(
    load_instance_id="gemma-load-1",
    model_key=_GEMMA_MODEL_KEY,
    backend_key="fake_gemma_backend",
    backend_version="1.2.3-fixture",
    model_architecture="gemma3",
    format="gguf",
    quantization="q4_0",
    artifact_size_bytes=1024,
    artifact_digest=ModelDigest(value="c" * 128),
    definition_file_sha512="a" * 128,
    loaded_context_size=8192,
    effective_capabilities=ModelCapabilities(
        features=frozenset(),
        native_context_limit=8192,
        loaded_context_size=8192,
        supported_message_roles=frozenset({MessageRole.SYSTEM, MessageRole.USER}),
    ),
    chat_template_source="fixture",
    chat_template_digest=ModelDigest(value="d" * 128),
    device="cpu",
    device_kind="cpu",
    acceleration_api="none",
    gpu_offload=False,
    gpu_offload_evidence=GpuOffloadEvidence(
        supported=False, requested=False, observed=False, observation_source="not_requested"
    ),
)
_CRITERION_COUNT = 4


class _Clock:
    def __init__(self) -> None:
        self.value = datetime(2026, 9, 5, tzinfo=UTC)

    def __call__(self) -> datetime:
        self.value += timedelta(seconds=1)
        return self.value


class _FakeStream:
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
    def __init__(self, *, answer: str) -> None:
        self.answer = answer
        self.requests: list[GenerationRequest] = []

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return _FakeStream(text_deltas=(self.answer,))


class _GemmaRepairRejudgeService:
    """`InferenceService`-shaped Fake standing in for Gemma's own dedicated
    `InferenceService` (`SeleneRoleAdapter.load()`'s `InferenceService(port=
    self._llama_adapter)`) -- used only for the Repair Candidate and Rejudge
    real Calls `attempt_live_repair()` itself issues via `rejudge_service=
    evaluator.inference_service` (`judge_live_integration.py`'s
    `_run_selene_dispatch`). The INITIAL Judge dispatch never calls this --
    it goes through `_FakeGemmaEvaluator.evaluate()` below instead, matching
    real Gemma's own batched-Selene-shaped dispatch."""

    def __init__(self, *, repair_candidate: str, rejudge_output: str) -> None:
        self._repair_candidate = repair_candidate
        self._rejudge_output = rejudge_output
        self.calls: list[GenerationRequest] = []
        self.runtime_info = _GEMMA_RUNTIME_INFO

    def count_chat_prompt_tokens(self, messages: tuple[object, ...], thinking_mode: object) -> int:
        del thinking_mode
        return sum(len(str(getattr(message, "content", ""))) for message in messages)

    def generate(
        self, request: GenerationRequest, *, cancellation: CancellationToken | None = None
    ) -> GenerationResult:
        self.calls.append(request)
        content = (
            self._repair_candidate
            if request.request_id.endswith(":repair")
            else self._rejudge_output
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


class _FakeGemmaEvaluator:
    """Duck-typed `SeleneSemanticEvaluator` shape (`.evaluate()` +
    `.inference_service`) -- the exact shape `judge_live_integration.py`'s
    dispatch router reads off `active_adapter.semantic_evaluator` for a
    genuinely dedicated (Gemma/Selene) Judge Provider."""

    def __init__(
        self, *, response: SemanticEvaluationResponse, inference_service: object
    ) -> None:
        self._response = response
        self.inference_service = inference_service
        self.calls: list[SemanticEvaluationRequest] = []

    def evaluate(
        self,
        *,
        request: SemanticEvaluationRequest,
        cancellation: CancellationToken | None = None,
        inference_budget_ms: int = 0,
        late_worker_observer: Callable[[Future[object]], None] | None = None,
        batch_evidence_observer: Callable[[object], None] | None = None,
    ) -> SemanticEvaluationResponse:
        del cancellation, inference_budget_ms, late_worker_observer, batch_evidence_observer
        self.calls.append(request)
        # `SemanticRuntimeCoordinator.record_response()` refuses any
        # response whose `request_id`/`generation` do not match the real
        # Frozen Snapshot it began -- the real request_id is a fresh UUID
        # per Turn, unknown ahead of time, so this Fake must echo back
        # whatever the real dispatch actually froze, never a fixed
        # placeholder.
        return self._response.model_copy(
            update={
                "request_id": request.snapshot.request_id,
                "generation": request.snapshot.generation,
            }
        )


class _FakeGemmaRoleAdapter:
    def __init__(self, *, provider_id: str, evaluator: _FakeGemmaEvaluator) -> None:
        self.provider_id = provider_id
        self.semantic_evaluator = evaluator


class _RoleHandle:
    def __init__(self, adapter: object, *, lease: object = "fake-gemma-lease") -> None:
        self.adapter = adapter
        self.lease = lease


def _criteria() -> tuple[SemanticCriterion, ...]:
    digest = "a" * 128
    return tuple(
        SemanticCriterion(
            criterion_id=f"semantic.argd.evidence.{index}",
            descriptor_id=f"argd.evidence.{index}",
            source_definition_id="argd",
            source_definition_digest_sha512=digest,
            source_pointer=f"/rules/evidence/{index}",
            source_text_digest_sha512=digest,
            instruction="Do not contradict the cited evidence.",
            governance_point="main_model.semantic",
            evaluation_stage=SemanticEvaluationStage.POST,
            evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
            severity_policy="high",
            recommended_action_policy="repair_or_safe_fallback",
            evidence_requirements=("request_identity",),
        )
        for index in range(_CRITERION_COUNT)
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


def test_production_composition_main_enforce_gemma_judge_repair_recording_full_same_turn_save(
    tmp_path: Path,
) -> None:
    """The full R2-WU-06 Fixture Golden Path in one Test: Main Governance
    ENFORCE authorizes a Repair (`repair_requested_by == "main_governance"`,
    Judge-side Repair Mode left OFF throughout), Judge is a dedicated Gemma-
    shaped Batched Evaluator (never Main-shared), the same Frozen 32-
    Criterion-shaped set (here `_CRITERION_COUNT` for a bounded Fixture) is
    Rejudged by the identical Gemma Fake after Repair, the improved answer
    replaces the known-wrong Candidate in the SAME (only) Turn, real
    Persistence stores it, and Recording FULL writes a real Judge Evidence
    file naming the real executing Gemma identity -- read back from disk,
    not merely inferred from a Hook return value."""
    criteria = _criteria()
    deviated_criterion = criteria[0]
    initial_response = SemanticEvaluationResponse(
        request_id="placeholder",
        generation=1,
        provider_id=_GEMMA_MODEL_KEY,
        provider_state=SemanticProviderState.ACTIVE,
        results=tuple(
            SemanticCriterionResult(
                criterion_id=item.criterion_id,
                descriptor_id=item.descriptor_id,
                disposition=(
                    SemanticCriterionDisposition.DEVIATION
                    if item.criterion_id == deviated_criterion.criterion_id
                    else SemanticCriterionDisposition.PASS
                ),
                confidence=0.9,
                reason_code=(
                    "unsupported_claim"
                    if item.criterion_id == deviated_criterion.criterion_id
                    else None
                ),
                evidence_refs=("REFERENCE SENTINEL",),
            )
            for item in criteria
        ),
        latency_ms=10,
    )
    rejudge_output = json.dumps(
        {
            "recommendation": "accept",
            "confidence": 0.9,
            "criterion_results": [
                {"criterion_id": item.criterion_id, "disposition": "pass", "confidence": 0.9}
                for item in criteria
            ],
        }
    )
    rejudge_service = _GemmaRepairRejudgeService(
        repair_candidate=_CORRECTED_ANSWER, rejudge_output=rejudge_output
    )
    evaluator = _FakeGemmaEvaluator(response=initial_response, inference_service=rejudge_service)
    gemma_role_adapter = _FakeGemmaRoleAdapter(provider_id=_GEMMA_MODEL_KEY, evaluator=evaluator)

    runtime_governance = RuntimeGovernanceComposition(
        capability=RuntimeCapabilitySnapshot(
            model_key=_MAIN_MODEL_KEY,
            backend_kind="llama_cpp",
            supports_streaming=True,
            supports_thinking=True,
            max_context_tokens=16384,
        ),
    )
    runtime_governance.semantic_runtime = SemanticRuntimeCoordinator(criteria=criteria)
    runtime_governance.set_semantic_context_provider(
        lambda: SemanticRuntimeBindingContext(
            language="en",
            judge_mode="enforce",
            # Judge-side Repair Mode toggle stays OFF throughout -- the
            # Handoff's own "Repair: OFF" arm. Only Main Governance's own
            # ENFORCE decision may authorize the Repair below.
            repair_mode="off",
            configured_provider=_GEMMA_MODEL_KEY,
            active_provider=_GEMMA_MODEL_KEY,
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=_CRITERION_COUNT,
        )
    )

    recording_root = tmp_path / "recording"
    evaluations_writer = LocalFilesystemRecordingWriter(
        base_dir=recording_root / "evaluations", max_total_bytes=10_000_000
    )
    evidence_writer = LocalFilesystemRecordingWriter(
        base_dir=recording_root / "evidence", max_total_bytes=10_000_000
    )
    recording_mode_control = RecordingModeController()
    recording_mode_control.apply_mode(RecordingMode.FULL)
    recording_completion_hook, _recording_state = build_recording_completion_hook(
        recording_mode_controller=recording_mode_control,
        writer=evaluations_writer,
        metadata_fields_provider=lambda context: {"model_identity": context.model_key},
    )
    judge_evidence_recorder, _judge_evidence_state = build_judge_evidence_recorder(
        writer=evidence_writer
    )

    judge_controller = JudgeModeController()
    repair_controller = RepairModeController()  # default OFF -- Judge-side gate never opens
    coordinator = ModelAccessCoordinator()
    hook, hook_composition = build_judge_completion_hook(
        service=rejudge_service,  # type: ignore[arg-type]
        judge_mode_controller=judge_controller,
        model_access_coordinator=coordinator,
        repair_mode_controller=repair_controller,
        recording_mode_controller=recording_mode_control,
        repair_executor=partial(
            attempt_live_repair,
            service=rejudge_service,  # type: ignore[arg-type]
            model_key=_GEMMA_MODEL_KEY,
            persistent=None,
        ),
        judge_evidence_recorder=judge_evidence_recorder,
        semantic_snapshot_provider=lambda rid: runtime_governance.begin_semantic_turn(
            request_id=rid, main_mode="enforce"
        ),
        semantic_result_recorder=lambda response: runtime_governance.record_semantic_response(
            response=response
        ),
        begin_judge_role_turn=lambda: _RoleHandle(gemma_role_adapter),
    )
    main_service = _MainInference(answer=_WRONG_ANSWER)
    generation_service = ConversationGenerationService(
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
            judge_mode="enforce", repair_mode="off", recording_mode="full"
        ),
        recording_completion_hook=recording_completion_hook,
        model_access_coordinator=coordinator,
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

    # 1. Main Governance itself authorized the Repair -- Judge-side Repair
    #    Mode was OFF throughout.
    result = hook_composition.last_result()
    assert result is not None
    assert result.repair_requested_by == "main_governance"
    assert result.repair_accepted is True
    assert result.executed_provider == _GEMMA_MODEL_KEY

    # 2. The identical Frozen Criterion set was Rejudged by the same Gemma
    #    identity -- the Repair Candidate + Rejudge Calls both reached the
    #    dedicated `rejudge_service`, never Main's own.
    assert len(rejudge_service.calls) == 2
    assert rejudge_service.calls[0].request_id.endswith(":repair")
    assert rejudge_service.calls[1].request_id.endswith(":rejudge")

    # 3. The improved answer replaced the known-wrong Candidate in the SAME
    #    (only) Turn -- real Persistence, never a second Turn.
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

    # Judge Evidence publication runs on a shutdown-tracked auxiliary
    # Thread, off the Model lease (`_start_evidence_publication()`) --
    # never synchronous within `hook()`/`generate_turn()` itself. Joining
    # it here is what makes the on-disk assertions below deterministic,
    # not merely usually-fast.
    assert coordinator.shutdown()

    # 4. Recording FULL genuinely wrote real files to disk -- read back
    #    directly, not inferred from a Hook callback having fired.
    evaluation_files = list((recording_root / "evaluations").glob("*.json"))
    assert len(evaluation_files) == 1
    turn_record = json.loads(evaluation_files[0].read_text(encoding="utf-8"))
    assert turn_record["metadata_fields"]["model_identity"] == _MAIN_MODEL_KEY

    evidence_files = list((recording_root / "evidence").glob("*.json"))
    assert len(evidence_files) == 1
    judge_evidence = json.loads(evidence_files[0].read_text(encoding="utf-8"))
    # The Executed Judge Provider (Gemma) -- never Main's own identity --
    # confirming R2-WU-02's Identity-separation fix reaches real persisted
    # Evidence, not merely the in-memory `LiveJudgeResult`.
    assert judge_evidence["metadata_fields"]["model_identity"] == _GEMMA_MODEL_KEY
    assert judge_evidence["metadata_fields"]["evaluated_model_identity"] == _MAIN_MODEL_KEY
    assert judge_evidence["metadata_fields"]["repair_accepted"] is True
    # The Executed Judge's own real Artifact/Backend -- never Main's own
    # (`ConversationGenerationService` here never wires a `model_runtime_
    # info` for Main at all, so a regression reading Main's identity back
    # here would show `"unavailable"`, not Gemma's real fixture values).
    assert judge_evidence["metadata_fields"]["artifact_digest_sha512"] == "c" * 128
    assert judge_evidence["metadata_fields"]["backend_key"] == "fake_gemma_backend"
    assert judge_evidence["metadata_fields"]["backend_version"] == "1.2.3-fixture"
