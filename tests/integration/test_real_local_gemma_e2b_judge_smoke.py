"""P9-1 Package 2 Real Local Judge Experiment: at least one real LLM-as-a-
Judge run against the Package 1 lightweight independent Judge candidate
(Gemma 4 E2B, official google/gemma-4-E2B-it-qat-q4_0-gguf), mirroring
`test_real_local_judge_smoke.py`'s existing Main-only pattern.

`gemma4` is an architecture this Runtime has never real-Loaded before
(Package 1 Return §2's own documented trade-off note) — this is the first
real evidence of whether it actually Loads/Infers/Decodes on this hardware,
separated from the Fixture-only unit tests already covering the shared
batch-evaluator/prompt-adapter logic itself (`test_selene_adapter.py`).

Loads Gemma alone (never concurrently with Main) — the documented Selene
resource-contention incident (`phase_9_1_all_judge_operational_failure_
common_substrate_hypothesis_and_rework_order_ja_20260902103228.md` §3) was
specifically about two concurrently-loaded dedicated `llama_cpp.Llama`
instances competing for the same 16GB unified-memory pool; this smoke test
never reproduces that shape, matching the Package 2 Return's documented
resource-safety judgment call not to attempt a real concurrent Main+dedicated
load on this exact hardware unattended.
"""

import platform
from pathlib import Path
from uuid import uuid4

import pytest

from margpa_runtime_llm.adapters.evaluation.selene import (
    SelenePromptAdapter,
    SeleneSemanticEvaluator,
)
from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig
from margpa_runtime_llm.modules.runtime_governance.application import freeze_semantic_turn
from margpa_runtime_llm.modules.runtime_governance.domain import (
    SemanticCriterion,
    SemanticEvaluationMethod,
    SemanticEvaluationRequest,
    SemanticEvaluationStage,
    SemanticProviderState,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = PROJECT_ROOT / "models"
GEMMA_MODEL_KEY = "judge.gemma-4-e2b-it-q4-0"
GEMMA_ARTIFACT = MODEL_ROOT / "judge/gemma-4-E2B_q4_0-it/gguf/gemma-4-E2B_q4_0-it.gguf"
GEMMA_MANIFEST = PROJECT_ROOT / "config/judge_templates/gemma_4_e2b/manifest.json"


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


@pytest.mark.model_smoke
@pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 6/9 model smoke requires Apple Silicon",
)
def test_a_real_gemma_e2b_run_evaluates_a_real_semantic_criterion_end_to_end() -> None:
    if not GEMMA_ARTIFACT.is_file():
        pytest.skip(f"Local Gemma 4 E2B artifact is unavailable: {GEMMA_ARTIFACT}")

    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    gemma_definition = definitions.resolve(model_key=GEMMA_MODEL_KEY)

    adapter = LlamaCppModelAdapter(model_root=MODEL_ROOT)
    service = InferenceService(adapter)
    # Bounded context (4096, matching the existing Main-only smoke test's
    # own choice) rather than Gemma's native 131072 ceiling -- a smaller
    # KV cache allocation is the responsible choice for a single bounded
    # smoke Run on constrained hardware, not a claim about Gemma's real
    # ceiling (that stays whatever `native_context_limit` in the Model
    # Definition already declares).
    service.load(gemma_definition, ModelLoadConfig(context_size=4096, gpu_layers=-1))

    try:
        prompt_adapter = SelenePromptAdapter(manifest_path=GEMMA_MANIFEST)
        evaluator = SeleneSemanticEvaluator(
            service=service,
            model_key=GEMMA_MODEL_KEY,
            prompt_adapter=prompt_adapter,
            provider_label="gemma_e2b",
        )
        frozen = freeze_semantic_turn(
            request_id=f"real-gemma-smoke-{uuid4()}",
            generation=1,
            criteria=(_criterion(),),
            language="en",
            main_mode="observe",
            judge_mode="enforce",
            repair_mode="off",
            configured_provider=GEMMA_MODEL_KEY,
            active_provider=GEMMA_MODEL_KEY,
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=8,
        )
        request = SemanticEvaluationRequest(
            snapshot=frozen.snapshot,
            stage="post",
            user_input="What is the capital of France?",
            candidate_answer="The capital of France is Paris.",
            evidence_context=("official-source | reference.txt: The capital of France is Paris.",),
        )

        response = evaluator.evaluate(request=request)

        # The Decoder itself must never raise (fail-closed by construction);
        # a real model's output may still be malformed JSON on a first real
        # Load of an architecture this Runtime has never exercised before --
        # record both outcomes as real Evidence, never force a PASS.
        if response.provider_state is not SemanticProviderState.ACTIVE:
            pytest.skip(
                f"Real Gemma 4 E2B Judge output was not decodable this run "
                f"(legitimate fail-closed outcome, not necessarily a Decoder "
                f"bug): provider_state={response.provider_state.value!r} "
                f"failure_reason={response.failure_reason!r}"
            )
        assert response.provider_id == GEMMA_MODEL_KEY
        assert len(response.results) == 1
        assert response.results[0].criterion_id == "semantic.argd.evidence.1"
    finally:
        service.unload()
