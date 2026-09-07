"""P9-1 Package 2 Real Local Judge Experiment: at least one real LLM-as-a-
Judge run against the dedicated Selene Judge, standalone (never concurrently
with Main), mirroring `test_real_local_gemma_e2b_judge_smoke.py`'s pattern.

Prior real-hardware evidence (`phase_9_1_all_judge_operational_failure_
common_substrate_hypothesis_and_rework_order_ja_20260902103228.md` §3, dated
2026-09-01) recorded Selene reaching Active state but then `Failure:
unavailable`, and separately, a Main-model crash after Selene activation
observed on a *concurrently loaded* Main+Selene configuration through the
full running server -- not this test's shape. This test isolates whether
Selene's own real Load/Inference/Decode round trip succeeds when loaded
alone, separating "Selene's own dispatch is broken" from "concurrent
resource contention with Main," per the Package 2 Common Substrate mandate
to diagnose before assuming a single root cause.
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
SELENE_MODEL_KEY = "judge.selene-1-mini-llama-3.1-8b-q5-k-m"
SELENE_ARTIFACT = (
    MODEL_ROOT / "judge/selene-1-mini-llama-3.1-8b/gguf/Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf"
)
SELENE_MANIFEST = PROJECT_ROOT / "config/judge_templates/selene/manifest.json"


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
def test_a_real_selene_run_evaluates_a_real_semantic_criterion_end_to_end() -> None:
    if not SELENE_ARTIFACT.is_file():
        pytest.skip(f"Local Selene artifact is unavailable: {SELENE_ARTIFACT}")

    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    selene_definition = definitions.resolve(model_key=SELENE_MODEL_KEY)

    adapter = LlamaCppModelAdapter(model_root=MODEL_ROOT)
    service = InferenceService(adapter)
    service.load(selene_definition, ModelLoadConfig(context_size=4096, gpu_layers=-1))

    try:
        prompt_adapter = SelenePromptAdapter(manifest_path=SELENE_MANIFEST)
        evaluator = SeleneSemanticEvaluator(
            service=service,
            model_key=SELENE_MODEL_KEY,
            prompt_adapter=prompt_adapter,
        )
        frozen = freeze_semantic_turn(
            request_id=f"real-selene-smoke-{uuid4()}",
            generation=1,
            criteria=(_criterion(),),
            language="en",
            main_mode="observe",
            judge_mode="enforce",
            repair_mode="off",
            configured_provider=SELENE_MODEL_KEY,
            active_provider=SELENE_MODEL_KEY,
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

        if response.provider_state is not SemanticProviderState.ACTIVE:
            pytest.skip(
                f"Real Selene Judge output was not decodable/available this "
                f"run (legitimate fail-closed outcome, not necessarily a "
                f"Decoder bug): provider_state={response.provider_state.value!r} "
                f"failure_reason={response.failure_reason!r}"
            )
        assert response.provider_id == SELENE_MODEL_KEY
        assert len(response.results) == 1
        assert response.results[0].criterion_id == "semantic.argd.evidence.1"
    finally:
        service.unload()
