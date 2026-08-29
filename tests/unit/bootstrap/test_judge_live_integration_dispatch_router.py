"""P6-RR-R2 (Post-Claude Independent Review Rework): reproduces, and
verifies the fix for, P6-CODEX-063 — `_run_judge_and_repair()` previously
dispatched to Main-self unconditionally, regardless of what the real
Provider Selection/Role Lifecycle reported as Active. This module tests
the new Active-Adapter Dispatch Router directly:

- No `begin_judge_role_turn` resolver supplied at all -> the exact pre-
  Rework unconditional Main-self dispatch is preserved (a deployment shape
  with no Provider Selection concept to override).
- A resolver supplied but returning `None` -> a typed, Model-Call-0
  failure (never a silent Main-self default) — this is the actual
  P6-CODEX-063/P6-GOV-018 Scenario-adjacent gap this Rework closes.
- A resolver returning a Main-shared-shaped Adapter (`.provider_id`, no
  `.semantic_evaluator`) -> dispatches through Main's Service, tagged with
  the real `executed_provider`.
- A resolver returning a Selene-shaped Adapter (`.semantic_evaluator`)
  -> dispatches to the dedicated Semantic Evaluator, never touching
  Main's Service at all, and the per-criterion results are correctly
  bridged into the shared Repair/Presentation pipeline.

P6-RR-R21 (Post-Codex Independent Review Rework, resolves P6-CODEX-086):
`begin_judge_role_turn` now returns an Adapter+Lease pair (`_handle()`
below) rather than a bare Adapter — `test_selene_initial_judge_repair_and_
frozen_selene_rejudge_single_turn_e2e` additionally asserts the acquired
Lease is Released exactly once by the time the whole Initial-Judge ->
Repair -> Rejudge Run has completed."""

from __future__ import annotations

import time
from types import SimpleNamespace

from margpa_runtime_llm.bootstrap.judge_live_integration import (
    JudgeGovernanceComposition,
    LiveJudgeResult,
    build_judge_completion_hook,
)
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
)
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationRequest,
    GenerationResult,
    GenerationTiming,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelRuntimeReference
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode
from margpa_runtime_llm.modules.runtime_governance.application import freeze_semantic_turn
from margpa_runtime_llm.modules.runtime_governance.domain import (
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticEvaluationMethod,
    SemanticEvaluationRequest,
    SemanticEvaluationResponse,
    SemanticEvaluationStage,
    SemanticProviderState,
)

_RUNTIME_REF = ModelRuntimeReference(
    load_instance_id="load-1",
    model_key="main.test-model",
    backend_key="fake",
    backend_version="0.0.0",
    definition_file_sha512="a" * 128,
)
_SELENE_PROVIDER_ID = "judge.selene-1-mini-llama-3.1-8b-q5-k-m"
_DEEPSEEK_PROVIDER_ID = "main.deepseek-r1-0528-qwen3-8b-q4-k-m"


class _FakeInferenceService:
    def __init__(self, *, content: str) -> None:
        self.content = content
        self.calls: list[GenerationRequest] = []

    def generate(
        self, request: GenerationRequest, *, cancellation: object = None
    ) -> GenerationResult:
        self.calls.append(request)
        return GenerationResult(
            request_id=request.request_id,
            model_key=request.model_key,
            content=self.content,
            finish_reason=FinishReason.STOP,
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            timing=GenerationTiming(total_generation_seconds=0.01),
            runtime_info=_RUNTIME_REF,
        )


class _FakeMainSharedAdapter:
    """Duck-typed `MainSharedJudgeRoleAdapter` shape: only `provider_id`,
    never `semantic_evaluator` — the Dispatch Router must treat any object
    lacking `semantic_evaluator` as a Main-shared selection."""

    def __init__(self, *, provider_id: str) -> None:
        self.provider_id = provider_id


class _FakeSeleneEvaluator:
    def __init__(
        self, *, response: SemanticEvaluationResponse, inference_service: object | None = None
    ) -> None:
        self._response = response
        self.calls: list[SemanticEvaluationRequest] = []
        # P6-RR-R20-WU-002 (resolves the S9 half of P6-CODEX-085): a real
        # `SeleneSemanticEvaluator` exposes its own `inference_service` —
        # `_run_selene_dispatch()` reads it via `getattr(evaluator,
        # "inference_service", None)` to source Rejudge's own Frozen
        # Judge identity. Optional/defaulted so existing Tests that never
        # touch Repair are unaffected.
        self.inference_service = inference_service

    def evaluate(self, *, request: SemanticEvaluationRequest) -> SemanticEvaluationResponse:
        self.calls.append(request)
        return self._response


class _FakeSeleneRoleAdapter:
    """Duck-typed `SeleneRoleAdapter` shape: exposes a real
    `semantic_evaluator` — the one signal the Dispatch Router uses to pick
    the Selene branch over the Main-shared branch."""

    def __init__(self, *, provider_id: str, evaluator: _FakeSeleneEvaluator) -> None:
        self.provider_id = provider_id
        self.semantic_evaluator = evaluator


def _handle(adapter: object, *, lease: object = "test-lease") -> SimpleNamespace:
    """P6-RR-R21: the Adapter+Lease pair `begin_judge_role_turn` returns —
    `_begin_judge_role_turn()` in `judge_live_integration.py` reads both
    via `getattr`, so any object exposing `.adapter`/`.lease` (this
    duck-typed `SimpleNamespace`, or the real `RoleTurnHandle`) works."""
    return SimpleNamespace(adapter=adapter, lease=lease)


class _ReleaseTracker:
    def __init__(self) -> None:
        self.released: list[object] = []

    def __call__(self, lease: object) -> None:
        self.released.append(lease)


def _wait_for_result(
    composition: JudgeGovernanceComposition, *, timeout_seconds: float = 2.0
) -> LiveJudgeResult:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        result = composition.last_result()
        if result is not None:
            return result
        time.sleep(0.005)
    raise AssertionError("Judge background thread did not record a result in time")


def _criterion(*, criterion_id: str = "semantic.argd.evidence.1") -> SemanticCriterion:
    return SemanticCriterion(
        criterion_id=criterion_id,
        descriptor_id="argd.evidence.1",
        source_definition_id="argd",
        source_definition_digest_sha512="a" * 128,
        source_pointer="/rules/evidence/1",
        source_text_digest_sha512="a" * 128,
        instruction="Do not contradict cited evidence.",
        governance_point="main_model.semantic",
        evaluation_stage=SemanticEvaluationStage.POST,
        evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        severity_policy="high",
        recommended_action_policy="repair_or_safe_fallback",
        evidence_requirements=("request_identity",),
    )


def test_no_resolver_supplied_preserves_legacy_unconditional_main_self_dispatch() -> None:
    """Deployment shape with no Provider Selection concept at all (the
    `begin_judge_role_turn` parameter itself omitted) — R2 must
    not regress this pre-Rework behavior."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-legacy-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert len(service.calls) == 1
    assert result.judge_role.value == "main_self"
    assert result.execution_state == "completed"
    assert result.executed_provider is None


def test_provider_selection_wired_no_active_adapter_fails_closed_zero_model_calls() -> None:
    """P6-CODEX-063: once Provider Selection genuinely IS wired for this
    deployment (a resolver was supplied), reporting no Active Judge
    Adapter must never silently default to Main-self."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        begin_judge_role_turn=lambda: None,
    )

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-no-adapter-1",
            user_input="Question",
            assistant_content="Answer",
            enforce_presented_final=True,
        )
    )

    assert service.calls == []
    assert decision is not None
    assert decision.candidate_withheld is True
    result = composition.last_result()
    assert result is not None
    assert result.judge_role.value == "unavailable"
    assert result.execution_state == "failed"
    assert result.failure_reason == "judge_provider_unavailable"
    assert result.executed_provider is None


def test_main_shared_active_adapter_is_dispatched_and_tagged_as_executed_provider() -> None:
    """R2-WU-002/004: an explicit Main-shared Judge selection (e.g.
    DeepSeek chosen while Main itself is DeepSeek) is genuinely Dispatched
    — never merely assumed — and the real Executed Provider identity is
    carried onto the Result as its own Field (R2-WU-005)."""
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content='{"recommendation": "accept", "confidence": 0.9}')
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        begin_judge_role_turn=lambda: _handle(
            _FakeMainSharedAdapter(provider_id=_DEEPSEEK_PROVIDER_ID)
        ),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-main-shared-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert len(service.calls) == 1
    assert service.calls[0].model_key == _DEEPSEEK_PROVIDER_ID
    assert result.judge_role.value == "main_self"
    assert result.executed_provider == _DEEPSEEK_PROVIDER_ID
    assert result.execution_state == "completed"


def test_selene_shaped_active_adapter_dispatches_via_semantic_evaluator_never_touches_main_service() -> (  # noqa: E501
    None
):
    """R2-WU-002: a genuinely Active Selene Adapter is dispatched to its
    own dedicated `semantic_evaluator` — Main's Service must see zero
    Calls, and the per-criterion PASS results must resolve to an ACCEPT
    recommendation carried through the shared Repair/Presentation tail."""
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-selene-1",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="off",
        configured_provider=_SELENE_PROVIDER_ID,
        active_provider=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    selene_response = SemanticEvaluationResponse(
        request_id="req-selene-1",
        generation=1,
        provider_id=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        results=(
            SemanticCriterionResult(
                criterion_id=criterion.criterion_id,
                descriptor_id=criterion.descriptor_id,
                disposition=SemanticCriterionDisposition.PASS,
                confidence=0.95,
            ),
        ),
        latency_ms=42,
    )
    evaluator = _FakeSeleneEvaluator(response=selene_response)
    recorded: list[SemanticEvaluationResponse] = []
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    service = _FakeInferenceService(content="should never be used")
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-selene-1" else None
        ),
        semantic_result_recorder=recorded.append,
        begin_judge_role_turn=lambda: _handle(
            _FakeSeleneRoleAdapter(provider_id=_SELENE_PROVIDER_ID, evaluator=evaluator)
        ),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-selene-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert service.calls == []
    assert len(evaluator.calls) == 1
    assert len(recorded) == 1
    assert recorded[0].provider_id == _SELENE_PROVIDER_ID
    assert result.judge_role.value == "independent_artifact"
    assert result.executed_provider == _SELENE_PROVIDER_ID
    assert result.recommendation == "accept"
    assert result.execution_state == "completed"
    assert result.criteria_selected == 1
    assert result.criteria_evaluated == 1
    assert result.criteria_passed == 1
    assert result.budget_profile == "local_macos_selene_judge_v1"


def test_selene_initial_judge_repair_and_frozen_selene_rejudge_single_turn_e2e() -> None:
    """Regression Scenario S9 exact (P6-RR-R20-WU-002, resolves the S9
    half of P6-CODEX-085): Initial Judge dispatches to a Fake Selene
    Adapter, reports a DEVIATION criterion (-> `needs_repair`), Repair
    Eligibility resolves ELIGIBLE, and the Repair Executor is invoked
    with a Rejudge Identity sourced from that *same* Selene Evaluator's
    own `inference_service` — never Main-self, never a fresh/different
    Judge — proving Initial Judge -> Repair -> Frozen Selene Rejudge as
    one continuous Turn, not three independently-tested mechanisms."""
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-selene-repair-1",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="enforce",
        configured_provider=_SELENE_PROVIDER_ID,
        active_provider=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    selene_response = SemanticEvaluationResponse(
        request_id="req-selene-repair-1",
        generation=1,
        provider_id=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        results=(
            SemanticCriterionResult(
                criterion_id=criterion.criterion_id,
                descriptor_id=criterion.descriptor_id,
                disposition=SemanticCriterionDisposition.DEVIATION,
                confidence=0.9,
                reason_code="unsupported_claim",
            ),
        ),
        latency_ms=42,
    )
    selene_inference_service = _FakeInferenceService(content="selene's own backing service")
    evaluator = _FakeSeleneEvaluator(
        response=selene_response, inference_service=selene_inference_service
    )
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)
    main_service = _FakeInferenceService(content="should never be used by Main-self")

    captured_calls: list[dict[str, object]] = []

    def _fake_repair_executor(
        *,
        request_id: str,
        model_key: str,
        user_input: str,
        original_answer: str,
        before_recommendation: object,
        judge_reasoning: str,
        dialogue_context: tuple[str, ...],
        evidence_context: tuple[str, ...],
        governance_post_hook: object,
        guardrail_post_hook: object,
        cancellation: object = None,
        model_runtime_info: object = None,
        stage_hook: object = None,
        persist_accepted_attempt: bool = True,
        stage_budget: object = None,
        rejudge_service: object = None,
        rejudge_model_key: str | None = None,
        rejudge_role: object = None,
        language: str = "en",
    ) -> object:
        from margpa_runtime_llm.bootstrap.repair_live_integration import RepairExecutionResult

        captured_calls.append(
            {
                "before_recommendation": before_recommendation,
                "rejudge_service": rejudge_service,
                "rejudge_model_key": rejudge_model_key,
                "rejudge_role": rejudge_role,
            }
        )
        return RepairExecutionResult(
            request_id=request_id,
            outcome="improved",
            accepted=True,
            new_turn_id="new-turn-selene-1",
            rejected_reason=None,
            presented_content="A corrected answer",
        )

    release = _ReleaseTracker()
    hook, composition = build_judge_completion_hook(
        service=main_service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=_fake_repair_executor,  # type: ignore[arg-type]
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-selene-repair-1" else None
        ),
        begin_judge_role_turn=lambda: _handle(
            _FakeSeleneRoleAdapter(provider_id=_SELENE_PROVIDER_ID, evaluator=evaluator),
            lease="selene-repair-lease",
        ),
        end_judge_role_turn=release,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-selene-repair-1",
            user_input="Question",
            assistant_content="A shaky answer",
            enforce_presented_final=True,
        )
    )
    result = _wait_for_result(composition)

    assert main_service.calls == []
    assert len(evaluator.calls) == 1
    assert result.judge_role.value == "independent_artifact"
    assert result.recommendation == "needs_repair"
    assert len(captured_calls) == 1
    call = captured_calls[0]
    assert call["before_recommendation"] == "needs_repair"
    # The exact S9 assertion: Rejudge's Identity is the *same* Selene
    # Evaluator's own backing service — never Main-self's, never a
    # different/fresh one.
    assert call["rejudge_service"] is selene_inference_service
    assert call["rejudge_model_key"] == _SELENE_PROVIDER_ID
    rejudge_role = call["rejudge_role"]
    assert getattr(rejudge_role, "value", rejudge_role) == "independent_artifact"
    assert result.repair_outcome == "improved"
    assert result.repair_accepted is True
    assert result.repair_new_turn_id == "new-turn-selene-1"
    # P6-RR-R21 (resolves P6-CODEX-086): the single Turn Lease acquired at
    # Hook entry is held across Initial Judge -> Repair -> Rejudge and
    # Released exactly once, only once the whole Run (`composition.
    # last_result()` above already confirms it reached a terminal state)
    # has actually finished.
    assert release.released == ["selene-repair-lease"]


def test_selene_dispatch_unavailable_response_produces_typed_failure() -> None:
    """Selene's own internal failure handling (`SeleneSemanticEvaluator.
    evaluate()`'s except-branch) must surface as a typed Judge failure
    through the same Dispatch Router, never a fabricated success."""
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-selene-2",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider=_SELENE_PROVIDER_ID,
        active_provider=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    unavailable_response = SemanticEvaluationResponse(
        request_id="req-selene-2",
        generation=1,
        provider_id=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.UNAVAILABLE,
        results=(),
        latency_ms=5,
        failure_reason="selene_unavailable:RuntimeError",
    )
    evaluator = _FakeSeleneEvaluator(response=unavailable_response)
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content="should never be used")
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-selene-2" else None
        ),
        begin_judge_role_turn=lambda: _handle(
            _FakeSeleneRoleAdapter(provider_id=_SELENE_PROVIDER_ID, evaluator=evaluator)
        ),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-selene-2",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert service.calls == []
    assert result.judge_role.value == "independent_artifact"
    assert result.executed_provider == _SELENE_PROVIDER_ID
    assert result.execution_state == "failed"
    assert result.recommendation == "unknown"
