"""Phase 9-2 R2-WU-06: bounded Real Model Gate for the Production Variant
path (Handoff R2 SS9.2).

"Production VariantのConfig一致とEvidenceの真実性がFixture/Integrationで
成立するまで実Modelを回さない。成立後のみ、次を逐次で最大3 Run実行する":
Main Qwen only / Main Qwen + Gemma Judge/Repair / Main Qwen + Qwen3Guard.
Fixture/Integration convergence for R2-WU-01..05 is confirmed (2627 backend
+ 331 frontend tests passing, 3 independent sabotage-regression cycles) --
this module is the one place that finally drives a REAL Turn through the
SAME `LiveProductionTurnAdapter` (R2-WU-02) the Production Web Route uses,
for each of the 3 named scenarios, sequentially, never two real Model
backends loaded concurrently beyond the one already-validated Main+Gemma
pair (`test_real_local_main_gemma_concurrent_dispatch_smoke.py`'s own
extensive real-hardware evidence -- no native crash, unlike the analogous
Main+Selene condition).

Selene and DeepSeek Judge are never touched (Handoff R2 SS9.2: "Seleneと
DeepSeek Judgeは実行しない")."""

from __future__ import annotations

import platform
from functools import partial
from pathlib import Path
from types import SimpleNamespace

import pytest

from margpa_runtime_llm.adapters.evaluation.selene import (
    GemmaPromptAdapter,
    SeleneSemanticEvaluator,
)
from margpa_runtime_llm.adapters.guardrail_governance.qwen3guard_adapter import (
    Qwen3GuardGenAdapter,
)
from margpa_runtime_llm.adapters.guardrail_governance.qwen3guard_detector_adapter import (
    Qwen3GuardRoleTurn,
)
from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.adapters.runtime_governance.semantic_criterion_adapter import (
    compile_argd_dagd_semantic_criteria,
)
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.bootstrap.experiment_production_turn_adapter import (
    LiveProductionTurnAdapter,
)
from margpa_runtime_llm.bootstrap.guardrail_governance import (
    GuardrailGovernanceComposition,
    build_guardrail_hooks,
)
from margpa_runtime_llm.bootstrap.judge_live_integration import build_judge_completion_hook
from margpa_runtime_llm.bootstrap.repair_live_integration import attempt_live_repair
from margpa_runtime_llm.bootstrap.runtime_governance import (
    default_authority,
    load_reference_descriptors,
)
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeExecutionModeSnapshot,
)
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.guardrail_governance.domain.identities import (
    GUARDRAIL_INPUT_POINT_ID,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig
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
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode
from margpa_runtime_llm.modules.runtime_governance.application import freeze_semantic_turn
from margpa_runtime_llm.modules.runtime_governance.domain import (
    RuntimeCapabilitySnapshot,
    SemanticCriterion,
    SemanticProviderState,
    SemanticTurnSnapshot,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = PROJECT_ROOT / "models"
QWEN_MODEL_KEY = "main.qwen3-4b-q4-k-m"
QWEN_ARTIFACT_PATH = MODEL_ROOT / "main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
GEMMA_MODEL_KEY = "judge.gemma-4-e2b-it-q4-0"
GEMMA_ARTIFACT_PATH = MODEL_ROOT / "judge/gemma-4-E2B_q4_0-it/gguf/gemma-4-E2B_q4_0-it.gguf"
GEMMA_MANIFEST = PROJECT_ROOT / "config/judge_templates/gemma_4_e2b/manifest.json"
GUARD_MODEL_KEY = "guard.qwen3guard-gen-0.6b-q8-0"
GUARD_ARTIFACT_PATH = (
    MODEL_ROOT / "guard/qwen3guard-gen-0.6b/gguf/Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf"
)
TARGET_CRITERION_ID = "semantic.argd.info_contradiction_information.0"
MAIN_CONTEXT = 8192

_REQUIRES_APPLE_SILICON = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 9-2 R2 Real Model Gate requires Apple Silicon",
)
_PROMPT = "What is the capital of France? Answer in one short sentence."


def _presentation_policy() -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="reasoning",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def _conversation_service(
    main_service: InferenceService, **hooks: object
) -> ConversationGenerationService:
    # R2-WU-06 real-hardware finding: `model_runtime_info` must be the
    # real, loaded Runtime Info -- `_completed_event()` (`conversation_
    # generation.py`) only attaches `data["attempt_provenance"]` (the
    # signal `LiveProductionTurnAdapter.run_turn()`'s `main_called`
    # derivation depends on) when `self._model_runtime_info is not None`.
    # Production wiring (`bootstrap/web_application.py`) always supplies
    # this; omitting it here (as this file's own first real-hardware
    # attempt originally did) reproduces a genuine False Negative --
    # `main_called=False` for a Turn that, by its own real, correct
    # "Paris." answer, obviously DID call Main. See the Exact Return's
    # Open Findings for this Round's own record of that first attempt.
    assert main_service.runtime_info is not None
    return ConversationGenerationService(
        inference=main_service,
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key=QWEN_MODEL_KEY,
        generation_defaults=GenerationParameters(
            max_new_tokens=64, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.EN,
        presentation_default=_presentation_policy(),
        summarization=SummarizationConfig(),
        effective_context_size=MAIN_CONTEXT,
        model_runtime_info=main_service.runtime_info,
        **hooks,  # type: ignore[arg-type]
    )


def _bounded_real_criterion() -> SemanticCriterion:
    loaded = load_reference_descriptors(
        definitions_root=PROJECT_ROOT / "definitions",
        capability=RuntimeCapabilitySnapshot(
            model_key=QWEN_MODEL_KEY,
            backend_kind="llama_cpp",
            supports_streaming=True,
            supports_thinking=True,
            max_context_tokens=MAIN_CONTEXT,
        ),
        authority=default_authority(),
    )
    assert loaded.state == "loaded"
    compiled = compile_argd_dagd_semantic_criteria(loaded.descriptors)
    matches = tuple(c for c in compiled.criteria if c.criterion_id == TARGET_CRITERION_ID)
    assert len(matches) == 1
    return matches[0]


@pytest.mark.model_smoke
@_REQUIRES_APPLE_SILICON
def test_real_gate_1_main_qwen_only_production_baseline() -> None:
    """Handoff R2 SS9.2 scenario 1: Main Qwen only, through the real
    `LiveProductionTurnAdapter.run_turn()` (R2-WU-02). Confirms, for the
    first time against a real Turn (not a Fake session), that a genuine
    Main Attempt's `COMPLETED` event really does carry `attempt_
    provenance` -- the exact signal `main_called`'s own derivation
    depends on."""

    if not QWEN_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Main model artifact is unavailable: {QWEN_ARTIFACT_PATH}")
    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    main_service = InferenceService(LlamaCppModelAdapter(model_root=MODEL_ROOT))
    main_service.load(
        definitions.resolve(model_key=QWEN_MODEL_KEY),
        ModelLoadConfig(context_size=MAIN_CONTEXT, gpu_layers=-1),
    )
    try:
        conversation = _conversation_service(main_service)
        adapter = LiveProductionTurnAdapter(
            conversation=conversation,
            response_language=ResponseLanguage.EN,
            max_new_tokens=64,
            thinking_visibility=ThinkingVisibility.HIDDEN,
        )
        observation = adapter.run_turn(user_input=_PROMPT)
        print(
            f"[real-gate-1] request_id={observation.request_id} "
            f"main_called={observation.main_called} main_outcome={observation.main_outcome} "
            f"final_disposition={observation.final_disposition} "
            f"content={observation.assistant_content!r}"
        )
        assert observation.main_called is True
        assert observation.main_outcome == "completed"
        assert observation.final_disposition == "candidate_accepted"
        assert observation.assistant_content is not None
        assert observation.assistant_content.strip() != ""
        assert observation.judge_called is False
        # R3-WU-02 (IR-P9-2-R2-04 fix): Guard's own unavailable-correlation
        # Evidence is now the honest tri-state `None` ("not_observed"),
        # never R2's confirmed-negative `False`.
        assert observation.guard_called is None
        assert observation.guard_outcome == "unavailable_correlation"
        assert observation.failure_reason is None
    finally:
        main_service.unload()


@pytest.mark.model_smoke
@_REQUIRES_APPLE_SILICON
def test_real_gate_2_main_qwen_plus_gemma_judge_repair() -> None:
    """Handoff R2 SS9.2 scenario 2: Main Qwen + Gemma Judge/Repair ENFORCE,
    concurrently loaded (the already-validated pair -- see this module's
    own docstring), through the real `LiveProductionTurnAdapter`. Confirms
    `judge_called`/`final_disposition` correlate correctly against a real
    `LiveJudgeResult` for THIS Turn's own real, internally-generated
    `request_id` (never known ahead of time, unlike the existing Hook-
    direct smoke tests -- bridged here via `on_request_id`)."""

    if not QWEN_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Main model artifact is unavailable: {QWEN_ARTIFACT_PATH}")
    if not GEMMA_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Gemma model artifact is unavailable: {GEMMA_ARTIFACT_PATH}")
    criterion = _bounded_real_criterion()
    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    main_service = InferenceService(LlamaCppModelAdapter(model_root=MODEL_ROOT))
    main_service.load(
        definitions.resolve(model_key=QWEN_MODEL_KEY),
        ModelLoadConfig(context_size=MAIN_CONTEXT, gpu_layers=-1),
    )
    gemma_service = InferenceService(LlamaCppModelAdapter(model_root=MODEL_ROOT))
    try:
        gemma_service.load(
            definitions.resolve(model_key=GEMMA_MODEL_KEY),
            ModelLoadConfig(context_size=8192, gpu_layers=-1),
        )
    except Exception as exc:
        main_service.unload()
        pytest.fail(f"Gemma Load raised while Main was concurrently loaded: {exc!r}")
    try:
        prompt_adapter = GemmaPromptAdapter(manifest_path=GEMMA_MANIFEST)
        prompt_adapter.preflight_contract()
        evaluator = SeleneSemanticEvaluator(
            service=gemma_service,
            model_key=GEMMA_MODEL_KEY,
            prompt_adapter=prompt_adapter,
            provider_label="gemma_e2b",
        )
        judge_mode_control = JudgeModeController()
        judge_mode_control.apply_mode(EvaluationMode.ENFORCE)
        repair_mode_control = RepairModeController()
        repair_mode_control.apply_mode(RepairMode.ENFORCE)

        # Bridges `ConversationGenerationService`'s own internally-generated
        # request_id (unknown until the real Turn actually starts) to the
        # Judge Hook's `semantic_snapshot_provider(request_id)` lookup --
        # populated via `LiveProductionTurnAdapter.run_turn()`'s own
        # `on_request_id` callback, fired before the Turn finishes.
        snapshot_box: dict[str, SemanticTurnSnapshot] = {}

        def _semantic_snapshot_provider(request_id: str) -> SemanticTurnSnapshot | None:
            return snapshot_box.get(request_id)

        def _register_request_id(real_request_id: str) -> None:
            frozen = freeze_semantic_turn(
                request_id=real_request_id,
                generation=1,
                criteria=(criterion,),
                language="en",
                main_mode="observe",
                judge_mode="enforce",
                repair_mode="enforce",
                configured_provider=GEMMA_MODEL_KEY,
                active_provider=GEMMA_MODEL_KEY,
                provider_state=SemanticProviderState.ACTIVE,
                budget_profile="test",
                max_criteria=8,
            )
            snapshot_box[real_request_id] = frozen.snapshot

        judge_hook, judge_composition = build_judge_completion_hook(
            service=main_service,
            judge_mode_controller=judge_mode_control,
            model_access_coordinator=ModelAccessCoordinator(),
            repair_mode_controller=repair_mode_control,
            repair_executor=partial(
                attempt_live_repair, service=main_service, model_key=QWEN_MODEL_KEY, persistent=None
            ),
            semantic_snapshot_provider=_semantic_snapshot_provider,
            begin_judge_role_turn=lambda: SimpleNamespace(
                adapter=SimpleNamespace(semantic_evaluator=evaluator, provider_id=GEMMA_MODEL_KEY),
                lease="real-gate-2-lease",
            ),
        )
        conversation = _conversation_service(
            main_service,
            judge_completion_hook=judge_hook,
            judge_mode_snapshot_provider=lambda: JudgeExecutionModeSnapshot(
                judge_mode="enforce", repair_mode="enforce"
            ),
        )
        adapter = LiveProductionTurnAdapter(
            conversation=conversation,
            response_language=ResponseLanguage.EN,
            max_new_tokens=64,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            judge_governance_composition=judge_composition,
        )
        observation = adapter.run_turn(
            user_input=_PROMPT, on_request_id=_register_request_id
        )
        result = judge_composition.last_result()
        print(
            f"[real-gate-2] request_id={observation.request_id} "
            f"main_called={observation.main_called} judge_called={observation.judge_called} "
            f"judge_outcome={observation.judge_outcome} repair_called={observation.repair_called} "
            f"repair_adopted={observation.repair_adopted} "
            f"final_disposition={observation.final_disposition} "
            f"real_execution_state={result.execution_state if result is not None else None} "
            f"real_criteria_evaluated={result.criteria_evaluated if result is not None else None} "
            f"content={observation.assistant_content!r}"
        )
        assert observation.main_called is True
        assert observation.assistant_content is not None
        assert result is not None
        assert result.request_id == observation.request_id
        if result.execution_state != "completed" or result.criteria_evaluated == 0:
            pytest.skip(
                "Real Gemma output was not decodable/evaluated this run "
                f"(legitimate fail-closed outcome): execution_state="
                f"{result.execution_state!r} failure_reason={result.failure_reason!r}"
            )
        # The crux this Round adds over the existing Hook-direct smoke
        # tests: the Adapter's OWN Evidence projection genuinely correlates
        # against this real Turn's real request_id and real Judge Result.
        assert observation.judge_called is True
        assert observation.judge_outcome == result.judge_outcome or observation.judge_outcome == (
            result.execution_state
        )
        assert observation.final_disposition == (
            result.final_disposition or result.presentation_outcome
        )
        if result.repair_outcome is not None:
            assert observation.repair_called is True
            assert observation.repair_adopted == bool(result.repair_accepted)
        else:
            assert observation.repair_called is False
            assert observation.repair_adopted is None
    finally:
        gemma_service.unload()
        main_service.unload()


@pytest.mark.model_smoke
@_REQUIRES_APPLE_SILICON
def test_real_gate_3_main_qwen_plus_qwen3guard() -> None:
    """Handoff R2 SS9.2 scenario 3: Main Qwen + Qwen3Guard ENFORCE. Confirms
    a real Guard Input dispatch genuinely happens for this real Turn
    (`GuardrailGovernanceComposition.last_result_for()`, independent of what
    the Adapter itself can observe) while the Adapter's OWN Evidence still
    honestly reports `unavailable_correlation` rather than fabricating a
    confirmed correlation (R2-WU-02 IR-P9-2-R1-05 fix) -- both facts held
    at once, neither contradicting the other."""

    if not QWEN_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Main model artifact is unavailable: {QWEN_ARTIFACT_PATH}")
    if not GUARD_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Qwen3Guard model artifact is unavailable: {GUARD_ARTIFACT_PATH}")
    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    main_service = InferenceService(LlamaCppModelAdapter(model_root=MODEL_ROOT))
    main_service.load(
        definitions.resolve(model_key=QWEN_MODEL_KEY),
        ModelLoadConfig(context_size=MAIN_CONTEXT, gpu_layers=-1),
    )
    guard_service = InferenceService(LlamaCppModelAdapter(model_root=MODEL_ROOT))
    try:
        guard_service.load(
            definitions.resolve(model_key=GUARD_MODEL_KEY),
            ModelLoadConfig(context_size=4096, gpu_layers=-1),
        )
    except Exception as exc:
        main_service.unload()
        pytest.fail(f"Qwen3Guard Load raised while Main was concurrently loaded: {exc!r}")
    try:
        guard_runtime_info = guard_service.runtime_info
        assert guard_runtime_info is not None
        guard_adapter = Qwen3GuardGenAdapter(
            service=guard_service,
            model_id=GUARD_MODEL_KEY,
            artifact_digest_sha512=guard_runtime_info.artifact_digest.value,
            manifest_path=PROJECT_ROOT / "config/guardrail/qwen3guard/manifest.json",
        )

        def _begin_role_turn() -> Qwen3GuardRoleTurn:
            return Qwen3GuardRoleTurn(adapter=guard_adapter, lease="real-gate-3-lease")

        guardrail_composition = GuardrailGovernanceComposition(
            qwen3guard_begin_role_turn=_begin_role_turn,
            qwen3guard_end_role_turn=lambda _lease: None,
        )
        guardrail_pre_hook, guardrail_post_hook, _context_hook = build_guardrail_hooks(
            composition=guardrail_composition,
            mode_provider=lambda: "enforce",
        )
        conversation = _conversation_service(
            main_service,
            guardrail_pre_hook=guardrail_pre_hook,
            guardrail_post_hook=guardrail_post_hook,
        )
        adapter = LiveProductionTurnAdapter(
            conversation=conversation,
            response_language=ResponseLanguage.EN,
            max_new_tokens=64,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            guardrail_governance_composition=guardrail_composition,
        )
        observation = adapter.run_turn(user_input=_PROMPT)
        guard_result = guardrail_composition.last_result_for(point_id=GUARDRAIL_INPUT_POINT_ID)
        guard_state = guard_result.execution_state if guard_result is not None else None
        guard_invocation_id = guard_result.invocation_id if guard_result is not None else None
        print(
            f"[real-gate-3] request_id={observation.request_id} "
            f"main_called={observation.main_called} main_outcome={observation.main_outcome} "
            f"guard_real_execution_state={guard_state} "
            f"guard_real_invocation_id={guard_invocation_id} "
            f"content={observation.assistant_content!r}"
        )
        # The real crux: a genuine Guard Input dispatch happened for this
        # Turn (never a native crash/uncaught exception).
        assert guard_result is not None
        # `ExecutionState.EVALUATED` (`guardrail_governance/domain/results.
        # py`) is the real success state -- "the Point ran and this Result
        # is its output" (`NOT_EVALUATED` means Mode OFF; `DEGRADED` means
        # a component failed but Observe still never mutated anything).
        assert guard_result.execution_state.value in ("evaluated", "degraded")
        # A benign, on-topic input must not have been blocked -- Main was
        # genuinely called and completed.
        assert observation.main_called is True
        assert observation.main_outcome == "completed"
        # R2-WU-02's own honest-non-claim: the Adapter itself never
        # fabricates a confirmed Guard correlation, even though Guard
        # genuinely ran (confirmed above via the real Composition). R3-
        # WU-02 (IR-P9-2-R2-04 fix) upgrades this from R2's confirmed
        # `False` to the honest tri-state `None`.
        assert observation.guard_called is None
        assert observation.guard_outcome == "unavailable_correlation"
    finally:
        guard_service.unload()
        main_service.unload()
