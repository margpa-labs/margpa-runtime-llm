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
from collections.abc import Callable
from concurrent.futures import Future
from functools import partial
from types import SimpleNamespace

from margpa_runtime_llm.bootstrap.judge_live_integration import (
    JudgeGovernanceComposition,
    LiveJudgeResult,
    build_judge_completion_hook,
)
from margpa_runtime_llm.bootstrap.repair_live_integration import attempt_live_repair
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
)
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass
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
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
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
_GEMMA_E2B_PROVIDER_ID = "judge.gemma-4-e2b-it-q4-0"
_DEEPSEEK_PROVIDER_ID = "main.deepseek-r1-0528-qwen3-8b-q4-k-m"


class _FakeInferenceService:
    def __init__(self, *, content: str) -> None:
        self.content = content
        self.calls: list[GenerationRequest] = []
        # `SeleneSemanticEvaluator._context_limit_tokens()` reads
        # `self._service.runtime_info` unconditionally when planning
        # batches (P9-1 Package 2: now also exercised by Main-shared's
        # semantic-criteria dispatch) -- `None` here falls back to the
        # evaluator's own `max_prompt_tokens_per_call`, exactly like a
        # real `InferenceService` with nothing loaded yet would.
        self.runtime_info: object | None = None

    def count_chat_prompt_tokens(self, messages: tuple[object, ...], thinking_mode: object) -> int:
        # P9-1 Package 2: Main-shared's semantic-criteria dispatch now
        # routes through `SeleneSemanticEvaluator`'s batch planner, which
        # requires this method on the underlying Inference Service (see
        # `ChatPromptTokenCounterPort`) to size batches before any
        # `generate()` call -- a trivial length-based count is sufficient
        # for a Fixture Fake.
        del thinking_mode
        return sum(len(str(getattr(message, "content", ""))) for message in messages)

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


class _MultiStageInferenceService:
    """A single Fixture Inference Service returning distinct content per
    real Model Call stage, keyed by the `request_id` suffix `judge_live_
    integration.py`/`attempt_live_repair` actually use (no suffix =
    Initial Judge, `:repair` = Repair Candidate Generation, `:rejudge` =
    Rejudge). Proves the real Production `attempt_live_repair()`
    Composition genuinely executes Repair Generation and Rejudge as two
    further distinct real Model Calls — a Fake Repair Executor that
    returns `accepted=True` immediately (as the pre-P9-CODEX-002 Test did)
    could never be distinguished from this by content alone."""

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
        self, request: GenerationRequest, *, cancellation: object = None
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


def test_main_shared_active_adapter_genuinely_evaluates_semantic_criteria() -> None:
    """P9-1-B-WU-004 (Phase 9-1): the Built-in Judge Provider can never
    genuinely evaluate any of the 109 Semantic Criteria -- every compiled
    Criterion uses `CLASSIFICATION*`/`ABSOLUTE_SCORING`
    (`semantic_criterion_adapter.py`'s `_ARGD_MAP`/`_mapping_for()`), an
    inherently qualitative judgment no deterministic check can honestly
    resolve (`_run_built_in_semantic_judge()`'s own docstring). The one
    Judge Provider that genuinely escapes `Deferred`/`evaluated 0` without
    any dedicated Model Authority is Main-shared self-judge -- it reuses
    whichever Model is already loaded for MAIN, so it needs no separate
    Load/Artifact/Network at all. The existing
    `test_main_shared_active_adapter_is_dispatched_and_tagged_as_executed_
    provider` test above only proves routing/tagging with a criterion-free
    response; this proves the real per-criterion Decode/Evidence path a
    Semantic Snapshot actually exercises through Main-self."""
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-main-shared-semantic-1",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="off",
        configured_provider=_DEEPSEEK_PROVIDER_ID,
        active_provider=_DEEPSEEK_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    judge_output = (
        '{"recommendation": "accept", "confidence": 0.93, "reasoning": "fixture", '
        '"criterion_results": [{"criterion_id": "semantic.argd.evidence.1", '
        '"disposition": "pass", "confidence": 0.91, "reason_code": "fixture_result", '
        '"evidence_refs": ["REFERENCE SENTINEL"]}]}'
    )
    recorded: list[object] = []
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.OBSERVE)
    service = _FakeInferenceService(content=judge_output)
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-main-shared-semantic-1" else None
        ),
        semantic_result_recorder=recorded.append,
        begin_judge_role_turn=lambda: _handle(
            _FakeMainSharedAdapter(provider_id=_DEEPSEEK_PROVIDER_ID)
        ),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-main-shared-semantic-1",
            user_input="Question",
            assistant_content="Answer",
        )
    )
    result = _wait_for_result(composition)

    assert len(service.calls) == 1
    assert service.calls[0].model_key == _DEEPSEEK_PROVIDER_ID
    assert result.judge_role.value == "main_self"
    assert result.executed_provider == _DEEPSEEK_PROVIDER_ID
    assert result.recommendation == "accept"
    assert result.execution_state == "completed"
    # The crux: genuinely evaluated, not Deferred/0 -- the actual escape
    # from the User Mac Evidence's "everything Deferred/evaluated 0" symptom.
    assert result.criteria_selected == 1
    assert result.criteria_evaluated == 1
    assert result.criteria_passed == 1
    assert result.criteria_deferred == 0
    # Evidence must be Lossless: `_record_semantic_result()` recorded the
    # real decoded per-criterion PASS, not a fabricated/empty projection.
    assert len(recorded) == 1


def test_main_shared_judge_needs_repair_and_rejudge_reuses_the_same_main_service_single_turn_e2e() -> (  # noqa: E501
    None
):
    """Scope note (P9-CODEX-002, Controller Finding Ledger): this Test's
    own `_fake_repair_executor` returns `accepted=True` immediately --
    it never runs a real Repair Candidate Generation or Rejudge Model
    Call. It is correctly scoped as a Parameter/Frozen Identity Wiring
    Test only: it proves `_run_judge_and_repair()` calls whatever Repair
    Executor it is given with the right `rejudge_service`/`rejudge_
    model_key`/`rejudge_role` values (the same already-loaded Main
    Service/Provider, never a fresh/different one). It does NOT prove the
    Production Repair Executor itself (`attempt_live_repair()`) genuinely
    executes -- see `test_main_shared_judge_repair_and_rejudge_genuinely_
    execute_via_the_production_repair_composition` below for that real
    end-to-end proof (real Repair Generation + real Rejudge, 2 further
    real Model Calls on the same Fixture Service).

    P9-1-C-WU-002/003/006 (Phase 9-1): the Selene analog of this Test
    (`test_selene_initial_judge_repair_and_frozen_selene_rejudge_single_
    turn_e2e` below) proves Initial Judge -> Repair -> Frozen Selene
    Rejudge as one continuous Turn -- but that path is unreachable without
    dedicated Model Authority this Task does not have. This is the
    Main-shared (Authority-independent) analog: a real Semantic-109
    Criterion resolves DEVIATION (-> `needs_repair`), Repair Eligibility
    resolves ELIGIBLE, and the Repair Executor's Rejudge Identity is the
    *same* already-loaded Main Service/Provider -- Main-self Judge and
    Main-self Rejudge share one Model, never a fresh/different one --
    proving the Criterion/Judge/Repair/Rejudge Identity Chain holds for
    the one Judge Provider this Task's Authority can actually exercise
    end to end."""
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-main-shared-repair-1",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="enforce",
        configured_provider=_DEEPSEEK_PROVIDER_ID,
        active_provider=_DEEPSEEK_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    judge_output = (
        '{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague", '
        '"criterion_results": [{"criterion_id": "semantic.argd.evidence.1", '
        '"disposition": "deviation", "confidence": 0.85, "reason_code": "unsupported_claim", '
        '"evidence_refs": ["REFERENCE SENTINEL"]}]}'
    )
    service = _FakeInferenceService(content=judge_output)
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)

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
        rejudge_criteria: object = (),
        tracked_stage_registry: object = None,
        rejudge_structured_output_schema_factory: object = None,
        rejudge_sampling_overrides: object = None,
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
            new_turn_id="new-turn-main-shared-1",
            rejected_reason=None,
            presented_content="A corrected answer",
        )

    release = _ReleaseTracker()
    recorded: list[object] = []
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=_fake_repair_executor,  # type: ignore[arg-type]
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-main-shared-repair-1" else None
        ),
        semantic_result_recorder=recorded.append,
        begin_judge_role_turn=lambda: _handle(
            _FakeMainSharedAdapter(provider_id=_DEEPSEEK_PROVIDER_ID),
            lease="main-shared-repair-lease",
        ),
        end_judge_role_turn=release,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-main-shared-repair-1",
            user_input="Question",
            assistant_content="A shaky answer",
            enforce_presented_final=True,
        )
    )
    result = _wait_for_result(composition)

    assert len(service.calls) == 1
    assert result.judge_role.value == "main_self"
    assert result.executed_provider == _DEEPSEEK_PROVIDER_ID
    assert result.recommendation == "needs_repair"
    assert result.criteria_evaluated == 1
    assert result.criteria_deviated == 1
    assert len(recorded) == 1
    assert len(captured_calls) == 1
    call = captured_calls[0]
    assert call["before_recommendation"] == "needs_repair"
    # The crux: Rejudge's Identity is the *same* already-loaded Main
    # Service/Provider -- never a fresh or different one.
    assert call["rejudge_service"] is service
    assert call["rejudge_model_key"] == _DEEPSEEK_PROVIDER_ID
    rejudge_role = call["rejudge_role"]
    assert rejudge_role is JudgeIndependenceClass.MAIN_SELF
    assert result.repair_outcome == "improved"
    assert result.repair_accepted is True
    assert result.repair_new_turn_id == "new-turn-main-shared-1"
    # The single Turn Lease acquired at Hook entry is held across Initial
    # Judge -> Repair -> Rejudge and Released exactly once.
    assert release.released == ["main-shared-repair-lease"]


def test_main_shared_judge_repair_and_rejudge_genuinely_execute_via_the_production_repair_composition() -> (  # noqa: E501
    None
):
    """P9-CODEX-002 (Controller Finding Ledger): the Test above proves the
    Repair Executor is *invoked* with the right Frozen Identity, but its
    Fake Executor returns `accepted=True` immediately -- it never proves
    the real Production `attempt_live_repair()` Composition (2 further
    real Model Calls: Repair Candidate Generation, then Rejudge) actually
    runs. This Test wires the exact Production function
    (`repair_live_integration.attempt_live_repair`, bound via
    `functools.partial` the same way `web_application.py`'s Composition
    Root binds `service`/`model_key`/`persistent`) as the real Repair
    Executor, backed by one Fixture Inference Service that returns
    distinct content per real Model Call stage -- proving all 3 real
    Model Calls (Initial Judge, Repair Candidate, Rejudge) genuinely
    happen, in that order, on the same Main-shared Service, ending in a
    real Adopt.

    Controller Review (2026-09-04 19:16, IR-02) fix: the Rejudge fixture
    below now returns a genuine `criterion_results` entry for the exact
    same Frozen `semantic.argd.evidence.1` id the Initial Judge scored --
    before this fix, `attempt_live_repair()` never passed `expected_
    criterion_ids` to its Rejudge decode at all, so a criterion-less
    `{"recommendation":"accept","confidence":0.9}` (this Test's own
    pre-Controller fixture value) was accepted at face value and this
    assertion passed for the wrong reason (an un-evidenced self-report,
    exactly Controller Review IR-02's reproduced defect). Proves the
    Rejudge is genuinely required to re-verify the *same* Frozen Criterion,
    not merely produce *some* `accept` recommendation."""
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-main-shared-real-repair-1",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="enforce",
        configured_provider=_DEEPSEEK_PROVIDER_ID,
        active_provider=_DEEPSEEK_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    initial_judge_output = (
        '{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague", '
        '"criterion_results": [{"criterion_id": "semantic.argd.evidence.1", '
        '"disposition": "deviation", "confidence": 0.85, "reason_code": "unsupported_claim", '
        '"evidence_refs": ["REFERENCE SENTINEL"]}]}'
    )
    rejudge_output = (
        '{"recommendation": "accept", "confidence": 0.9, '
        '"criterion_results": [{"criterion_id": "semantic.argd.evidence.1", '
        '"disposition": "pass", "confidence": 0.9}]}'
    )
    service = _MultiStageInferenceService(
        initial_judge=initial_judge_output,
        repair_candidate="A corrected, source-grounded answer.",
        rejudge=rejudge_output,
    )
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)

    release = _ReleaseTracker()
    recorded: list[object] = []
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=partial(
            attempt_live_repair,
            service=service,  # type: ignore[arg-type]
            model_key=_DEEPSEEK_PROVIDER_ID,
            persistent=None,
        ),
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-main-shared-real-repair-1" else None
        ),
        semantic_result_recorder=recorded.append,
        begin_judge_role_turn=lambda: _handle(
            _FakeMainSharedAdapter(provider_id=_DEEPSEEK_PROVIDER_ID),
            lease="main-shared-real-repair-lease",
        ),
        end_judge_role_turn=release,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-main-shared-real-repair-1",
            user_input="Question",
            assistant_content="A shaky answer",
            enforce_presented_final=True,
        )
    )
    result = _wait_for_result(composition)

    # The crux: 3 distinct real Model Calls actually happened, in order --
    # Initial Judge, then real Repair Candidate Generation, then real
    # Rejudge -- never a Fake Executor short-circuit. The Initial Judge
    # call's request_id now carries the shared batch evaluator's
    # `{request_id}:{provider_label}:{batch_index}` shape (P9-1 Package 2
    # Common Substrate fix: Main-shared's semantic-criteria dispatch now
    # goes through the same token-bounded batch planner Selene uses,
    # tagged `main_shared` -- one Criterion fits in exactly one batch).
    assert [call.request_id for call in service.calls] == [
        "req-main-shared-real-repair-1:main_shared:1",
        "req-main-shared-real-repair-1:repair",
        "req-main-shared-real-repair-1:rejudge",
    ]
    assert result.judge_role.value == "main_self"
    assert result.executed_provider == _DEEPSEEK_PROVIDER_ID
    assert result.recommendation == "needs_repair"
    assert result.criteria_evaluated == 1
    assert result.criteria_deviated == 1
    assert len(recorded) == 1
    assert result.repair_outcome == "improved"
    assert result.repair_accepted is True
    # `persist_accepted_attempt=False` (the synchronous ENFORCE-Presented-
    # Final path) -- Adopt returns the real generated candidate content
    # directly, never a persisted-Turn id.
    assert result.repair_new_turn_id is None
    assert release.released == ["main-shared-real-repair-lease"]


def test_main_shared_rejudge_with_no_criterion_results_is_never_accepted() -> None:
    """Controller Review (2026-09-04 19:16, IR-02) exact reproduction: same
    Production wiring as the Test above (real `attempt_live_repair()`, real
    Judge Hook, only the Model Service's 3 calls scripted), except the
    Rejudge fixture is the pre-Controller-fix shape -- a criterion-less
    generic `{"recommendation":"accept","confidence":0.99}` with no
    `criterion_results` at all, exactly Controller's own in-memory Probe
    (initial Judge DEVIATION -> Repair returns the flawed candidate
    unmodified -> Rejudge reports a bare accept). Controller reproduced
    `repair_accepted=True` here against the pre-fix code (`rejudge_
    response_has_criterion_results: False`, yet still adopted). With the
    Frozen Criterion now threaded through to the Rejudge's `expected_
    criterion_ids`, a response missing that Criterion's `criterion_results`
    entry must fail the Rejudge decode closed (-> UNKNOWN), so `evaluate_
    repair_success()` can never call it IMPROVED and the known-flawed
    original answer must never be adopted as a genuine repair."""
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-main-shared-ir02-repro-1",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="enforce",
        configured_provider=_DEEPSEEK_PROVIDER_ID,
        active_provider=_DEEPSEEK_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    initial_judge_output = (
        '{"recommendation": "needs_repair", "confidence": 0.4, "reasoning": "vague", '
        '"criterion_results": [{"criterion_id": "semantic.argd.evidence.1", '
        '"disposition": "deviation", "confidence": 0.85, "reason_code": "unsupported_claim", '
        '"evidence_refs": ["REFERENCE SENTINEL"]}]}'
    )
    service = _MultiStageInferenceService(
        initial_judge=initial_judge_output,
        # The Repair candidate deliberately does not actually fix the
        # flaw (mirrors Controller's Probe step 2: "誤りを含む元回答をその
        # まま返す").
        repair_candidate="A shaky answer",
        # The pre-Controller-fix Rejudge shape: no `criterion_results` at
        # all -- a bare self-reported accept with no per-criterion
        # evidence (mirrors Controller's Probe step 3).
        rejudge='{"recommendation": "accept", "confidence": 0.99}',
    )
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    repair_controller = RepairModeController()
    repair_controller.apply_mode(RepairMode.ENFORCE)

    release = _ReleaseTracker()
    hook, composition = build_judge_completion_hook(
        service=service,  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        repair_mode_controller=repair_controller,
        repair_executor=partial(
            attempt_live_repair,
            service=service,  # type: ignore[arg-type]
            model_key=_DEEPSEEK_PROVIDER_ID,
            persistent=None,
        ),
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-main-shared-ir02-repro-1" else None
        ),
        semantic_result_recorder=lambda response: None,
        begin_judge_role_turn=lambda: _handle(
            _FakeMainSharedAdapter(provider_id=_DEEPSEEK_PROVIDER_ID),
            lease="main-shared-ir02-repro-lease",
        ),
        end_judge_role_turn=release,
    )

    decision = hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-main-shared-ir02-repro-1",
            user_input="Question",
            assistant_content="A shaky answer",
            enforce_presented_final=True,
        )
    )
    result = _wait_for_result(composition)

    assert [call.request_id for call in service.calls] == [
        "req-main-shared-ir02-repro-1:main_shared:1",
        "req-main-shared-ir02-repro-1:repair",
        "req-main-shared-ir02-repro-1:rejudge",
    ]
    # The crux: the criterion-less Rejudge must never be adopted as a
    # genuine repair, and the known-flawed original answer must never reach
    # the Presented Final either.
    assert result.repair_outcome == "unknown"
    assert result.repair_accepted is False
    assert decision is not None
    assert decision.presentation_outcome != "candidate_accepted"


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


def test_selene_shaped_dispatch_records_the_executing_providers_evidence_identity() -> None:
    """P9-1 Component Independence Rework (WU-04): confirmed real Failure
    -- a genuinely `independent_artifact`-role Judge Run's own recorded
    `judge_run_evidence` carried `metadata_fields.model_identity` equal to
    Main's own identity (`context.model_key`) instead of the real
    executing dedicated Adapter's identity, even though the UI's own
    Executed Provider correctly showed the dedicated Adapter. `model_
    identity` in this Evidence record must mean "the Model that actually
    executed this Judge Run", matching the adjacent `judge_role` field it
    is recorded alongside — never silently the evaluated Main Turn's own
    identity, which is separately available via the correlated Turn-level
    "evaluations" record, not this one."""
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-selene-evidence-identity-1",
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
        request_id="req-selene-evidence-identity-1",
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
        latency_ms=10,
    )
    evaluator = _FakeSeleneEvaluator(response=selene_response)
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    evidence_calls: list[dict[str, object]] = []
    hook, composition = build_judge_completion_hook(
        service=_FakeInferenceService(content="should never be used"),  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-selene-evidence-identity-1" else None
        ),
        judge_evidence_recorder=lambda **fields: evidence_calls.append(fields),
        begin_judge_role_turn=lambda: _handle(
            _FakeSeleneRoleAdapter(provider_id=_SELENE_PROVIDER_ID, evaluator=evaluator)
        ),
    )

    hook(
        JudgeCompletionContext(
            # Main's own identity -- deliberately different from
            # `_SELENE_PROVIDER_ID` so the two are never accidentally
            # indistinguishable in this Test's own assertion.
            model_key="main.test-model",
            request_id="req-selene-evidence-identity-1",
            user_input="Question",
            assistant_content="Answer",
            recording_mode="full",
        )
    )
    _wait_for_result(composition)

    assert len(evidence_calls) == 1
    assert evidence_calls[0]["model_identity"] == _SELENE_PROVIDER_ID
    assert evidence_calls[0]["model_identity"] != "main.test-model"


def test_selene_shaped_dispatch_with_zero_batch_calls_records_evidence_call_count_zero() -> None:
    """Codex Controller Review (2026-09-06 12:44, IR-FC-03) fix: before this
    fix, `_run_selene_dispatch()` recorded `call_count=len(frozen_batch_
    evidence) or 1` -- a genuine Model-Call-0 Run (e.g. Prior Dialogue
    pushing every Criterion's own Prompt over Budget, so every Criterion
    lands Deferred and no real Batch is ever dispatched to the Model) still
    recorded a fabricated `call_count=1`, indistinguishable from a genuine
    single real Call. `_FakeSeleneEvaluator.evaluate()` never invokes
    `batch_evidence_observer` (see its own definition above) regardless of
    what canned `response` it returns, so this Fixture -- an all-Deferred,
    zero-criteria-supplied `SemanticEvaluationResponse` -- exercises
    exactly the "zero real Batch Calls reached the Model" shape the fixed
    line (`call_count=len(frozen_batch_evidence)`, no `or 1` fallback) must
    now record honestly as `0`, never fabricated Prompt/Batch Evidence for
    the Model-Call-0 case."""
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-selene-zero-calls-1",
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
    zero_call_response = SemanticEvaluationResponse(
        request_id="req-selene-zero-calls-1",
        generation=1,
        provider_id=_SELENE_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        results=(),
        latency_ms=5,
    )
    evaluator = _FakeSeleneEvaluator(response=zero_call_response)
    controller = JudgeModeController()
    controller.apply_mode(EvaluationMode.ENFORCE)
    evidence_calls: list[dict[str, object]] = []
    hook, composition = build_judge_completion_hook(
        service=_FakeInferenceService(content="should never be used"),  # type: ignore[arg-type]
        judge_mode_controller=controller,
        model_access_coordinator=ModelAccessCoordinator(),
        semantic_snapshot_provider=lambda request_id: (
            frozen.snapshot if request_id == "req-selene-zero-calls-1" else None
        ),
        judge_evidence_recorder=lambda **fields: evidence_calls.append(fields),
        begin_judge_role_turn=lambda: _handle(
            _FakeSeleneRoleAdapter(provider_id=_SELENE_PROVIDER_ID, evaluator=evaluator)
        ),
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-selene-zero-calls-1",
            user_input="Question",
            assistant_content="Answer",
            recording_mode="full",
        )
    )
    _wait_for_result(composition)

    assert len(evidence_calls) == 1
    assert evidence_calls[0]["call_count"] == 0
    assert evidence_calls[0].get("seed") is None
    assert evidence_calls[0].get("batch_evidence_json") is None
    # Codex Controller Review (2026-09-06 13:35, IR-FC-04) fix: before this
    # fix, zero real Batch Calls meant no override was threaded at all
    # (`None`), which the Recorder then re-derived from the fixed
    # description-string `prompt` argument -- a legitimate-looking but
    # fabricated 128-hex-digit `prompt_digest_sha512` for a Run with no
    # real Prompt at all. The literal `"unavailable"` string must now be
    # threaded through as the override instead.
    assert evidence_calls[0]["prompt_digest_sha512_override"] == "unavailable"


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
        rejudge_criteria: object = (),
        tracked_stage_registry: object = None,
        rejudge_structured_output_schema_factory: object = None,
        rejudge_sampling_overrides: object = None,
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


def test_gemma_e2b_initial_judge_repair_and_frozen_gemma_rejudge_single_turn_e2e() -> None:
    """P9-1 Package 2 (User-mandated Fresh Runtime default change, item 5:
    "Judge→Repair→RejudgeでFrozen Provider IdentityがGemmaのまま維持される").
    Identical scenario to `test_selene_initial_judge_repair_and_frozen_
    selene_rejudge_single_turn_e2e` above, with the Active Adapter's
    `provider_id`/`semantic_evaluator` now shaped as Gemma 4 E2B (the
    Fresh Runtime default as of this Package) -- proves the Dispatch
    Router's Rejudge Identity threading (`rejudge_service=getattr(
    evaluator, "inference_service", None)`, `rejudge_model_key=
    executed_provider`) is genuinely Provider-neutral, not something that
    only happened to work for Selene specifically."""
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-gemma-repair-1",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="enforce",
        configured_provider=_GEMMA_E2B_PROVIDER_ID,
        active_provider=_GEMMA_E2B_PROVIDER_ID,
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    gemma_response = SemanticEvaluationResponse(
        request_id="req-gemma-repair-1",
        generation=1,
        provider_id=_GEMMA_E2B_PROVIDER_ID,
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
    gemma_inference_service = _FakeInferenceService(content="gemma's own backing service")
    evaluator = _FakeSeleneEvaluator(
        response=gemma_response, inference_service=gemma_inference_service
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
        rejudge_criteria: object = (),
        tracked_stage_registry: object = None,
        rejudge_structured_output_schema_factory: object = None,
        rejudge_sampling_overrides: object = None,
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
            new_turn_id="new-turn-gemma-1",
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
            frozen.snapshot if request_id == "req-gemma-repair-1" else None
        ),
        begin_judge_role_turn=lambda: _handle(
            _FakeSeleneRoleAdapter(provider_id=_GEMMA_E2B_PROVIDER_ID, evaluator=evaluator),
            lease="gemma-repair-lease",
        ),
        end_judge_role_turn=release,
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-gemma-repair-1",
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
    # The crux: Rejudge's Identity is the *same* Gemma Evaluator's own
    # backing service -- never Main-self's, never a different/fresh one,
    # and never silently re-resolved to whatever the Fresh default is
    # (this same value) rather than the Provider that actually produced
    # the Initial Judge.
    assert call["rejudge_service"] is gemma_inference_service
    assert call["rejudge_model_key"] == _GEMMA_E2B_PROVIDER_ID
    rejudge_role = call["rejudge_role"]
    assert getattr(rejudge_role, "value", rejudge_role) == "independent_artifact"
    assert result.repair_outcome == "improved"
    assert result.repair_accepted is True
    assert result.repair_new_turn_id == "new-turn-gemma-1"
    assert release.released == ["gemma-repair-lease"]


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
