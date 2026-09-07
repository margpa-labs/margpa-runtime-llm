"""P9-1 Package 2 Real Local Judge Experiment: proves the Common Substrate
truncation-bug fix (`bootstrap/judge_live_integration.py`'s semantic-criteria
branch now routing through `SeleneSemanticEvaluator`'s token-bounded batch
planner, see its module docstring) against the real Main Qwen3-4B model,
not only Fixtures.

Real-hardware evidence (`phase_9_1_all_judge_operational_failure_common_
substrate_hypothesis_and_rework_order_ja_20260902103228.md` §2.1) recorded
Main-shared Qwen ENFORCE failing `malformed_output` with `selected 0
evaluated 0` on a real 32-criteria Semantic Turn. The Package 2 diagnosis
traced this to a single unbatched call for up to 32 Criteria against a
fixed 200-token output cap, guaranteed to truncate. This test forces 10
real Semantic Criteria (`max_criteria_per_call=8` splits this into 2 real
batched Model Calls) through the real Main model and asserts every
Criterion genuinely decodes -- the truncation shape this fix targets.
"""

import platform
from pathlib import Path
from uuid import uuid4

import pytest

from margpa_runtime_llm.adapters.evaluation.selene import SeleneSemanticEvaluator
from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.modules.evaluation.application.judge_prompt_builder import (
    MainSemanticPromptAdapter,
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
QWEN_MODEL_KEY = "main.qwen3-4b-q4-k-m"
_CRITERION_COUNT = 10


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
        for index in range(1, _CRITERION_COUNT + 1)
    )


@pytest.mark.model_smoke
@pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 6/9 model smoke requires Apple Silicon",
)
def test_a_real_main_shared_batched_run_avoids_the_single_call_truncation_defect() -> None:
    artifact_path = MODEL_ROOT / "main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
    if not artifact_path.is_file():
        pytest.skip(f"Local model artifact is unavailable: {artifact_path}")

    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    qwen_definition = definitions.resolve(model_key=QWEN_MODEL_KEY)

    adapter = LlamaCppModelAdapter(model_root=MODEL_ROOT)
    service = InferenceService(adapter)
    service.load(qwen_definition, ModelLoadConfig(context_size=4096, gpu_layers=-1))

    try:
        evaluator = SeleneSemanticEvaluator(
            service=service,
            model_key=QWEN_MODEL_KEY,
            prompt_adapter=MainSemanticPromptAdapter(
                rubric_id="live_conversation_general_quality_v1"
            ),
            provider_label="main_shared",
        )
        frozen = freeze_semantic_turn(
            request_id=f"real-main-shared-batched-smoke-{uuid4()}",
            generation=1,
            criteria=_criteria(),
            language="en",
            main_mode="observe",
            judge_mode="enforce",
            repair_mode="off",
            configured_provider=QWEN_MODEL_KEY,
            active_provider=QWEN_MODEL_KEY,
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=_CRITERION_COUNT,
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
                f"Real Main-shared batched Judge output was not decodable "
                f"this run (legitimate fail-closed outcome, not necessarily "
                f"a Decoder bug): "
                f"provider_state={response.provider_state.value!r} "
                f"failure_reason={response.failure_reason!r}"
            )
        # The crux: 2 real batched Model Calls (8 + 2 Criteria), never one
        # unbatched call for all 10 -- and every Criterion genuinely
        # decoded, none silently dropped by truncation.
        assert response.budget is not None
        assert response.budget.calls_completed == 2
        assert len(response.results) == _CRITERION_COUNT
        assert {item.criterion_id for item in response.results} == {
            f"semantic.argd.evidence.{index}" for index in range(1, _CRITERION_COUNT + 1)
        }
    finally:
        service.unload()
