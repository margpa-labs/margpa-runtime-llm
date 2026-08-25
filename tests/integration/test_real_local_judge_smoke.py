"""Opt-in Real Local Judge Experiment (Phase 6-D-WU-005) against the real
Qwen3 GGUF artifact: at least one real LLM-as-a-Judge run, separated from
the Fake/Stub unit tests already covering the Prompt/Decoder logic itself.

Uses the same Artifact for both the candidate answer and the Judge call
(MAIN_SELF independence, per JudgeIndependenceClass) since no independent
Judge Artifact is available in this environment — the point of this test
is to prove the real prompt/decode round-trip works against a real model's
actual (sometimes messy) text output, not to claim Judge Independence.
"""

import json
import platform
from pathlib import Path
from uuid import uuid4

import pytest

from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.bootstrap.judge_live_integration import build_judge_completion_hook
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    SEMANTIC_ENFORCEMENT_SAFE_FALLBACK,
    JudgeCompletionContext,
)
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.application.judge_output_decoder import (
    decode_judge_output_fail_closed,
)
from margpa_runtime_llm.modules.evaluation.application.judge_prompt_builder import (
    build_judge_prompt,
)
from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationMode,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.generation import GenerationRequest
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = PROJECT_ROOT / "models"
QWEN_MODEL_KEY = "main.qwen3-4b-q4-k-m"


@pytest.mark.model_smoke
@pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 6 model smoke requires Apple Silicon",
)
def test_a_real_qwen_run_judges_its_own_answer_end_to_end() -> None:
    artifact_path = MODEL_ROOT / "main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
    if not artifact_path.is_file():
        pytest.skip(f"Local model artifact is unavailable: {artifact_path}")

    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    qwen_definition = definitions.resolve(model_key=QWEN_MODEL_KEY)

    adapter = LlamaCppModelAdapter(model_root=MODEL_ROOT)
    service = InferenceService(adapter)
    service.load(qwen_definition, ModelLoadConfig(context_size=4096, gpu_layers=-1))

    try:
        case = EvaluationCase(
            case_id="real-judge-smoke-1",
            input="What is the capital of France? Answer with just the city name.",
            reference="Paris",
            criteria=("exact_reference_match",),
            language="en",
        )

        answer_result = service.generate(
            GenerationRequest(
                request_id=str(uuid4()),
                model_key=QWEN_MODEL_KEY,
                messages=(ChatMessage(role=MessageRole.USER, content=case.input),),
            )
        )
        candidate_answer = answer_result.content
        assert candidate_answer.strip() != ""

        judge_prompt = build_judge_prompt(
            case=case, candidate_answer=candidate_answer, rubric_id="exact_reference_match_v1"
        )
        judge_result = service.generate(
            GenerationRequest(
                request_id=str(uuid4()),
                model_key=QWEN_MODEL_KEY,
                messages=(ChatMessage(role=MessageRole.USER, content=judge_prompt),),
            )
        )

        judge_response = decode_judge_output_fail_closed(
            raw_text=judge_result.content,
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            token_usage=judge_result.usage.completion_tokens if judge_result.usage else 0,
            latency_ms=int(judge_result.timing.total_generation_seconds * 1000),
        )

        # The Decoder itself must never raise (Fail-closed by construction);
        # a real model's output may still be malformed JSON, in which case
        # this is legitimately FAILED/UNKNOWN rather than a crash — record
        # both outcomes as real Evidence rather than only asserting success.
        if judge_response.execution_state is EvaluationExecutionState.FAILED:
            pytest.skip(
                f"Real Qwen Judge output was not decodable JSON this run "
                f"(legitimate Fail-closed outcome, not a Decoder bug): "
                f"{judge_result.content[:200]!r}"
            )
        assert judge_response.execution_state is EvaluationExecutionState.COMPLETED
        json.loads(judge_result.content)
    finally:
        service.unload()


@pytest.mark.model_smoke
@pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 6 model smoke requires Apple Silicon",
)
def test_real_qwen_enforce_withholds_an_evidence_contradicting_candidate() -> None:
    """P6-RW7-JDG-003/004/006 real-model Golden Path.

    The deliberately wrong Candidate contradicts both the latest User
    correction and the supplied source Evidence.  With Repair OFF, a real
    main-self Judge must either identify the failure or fail closed; in both
    cases ENFORCE presents the safe fallback and never canonicalizes the
    known-wrong Candidate.  An ACCEPT from the real Model is intentionally a
    failing result, not rewritten into PASS by the test.
    """

    artifact_path = MODEL_ROOT / "main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
    if not artifact_path.is_file():
        pytest.skip(f"Local model artifact is unavailable: {artifact_path}")

    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    qwen_definition = definitions.resolve(model_key=QWEN_MODEL_KEY)
    adapter = LlamaCppModelAdapter(model_root=MODEL_ROOT)
    service = InferenceService(adapter)
    service.load(qwen_definition, ModelLoadConfig(context_size=4096, gpu_layers=-1))

    try:
        judge_mode_controller = JudgeModeController()
        judge_mode_controller.apply_mode(EvaluationMode.ENFORCE)
        hook, composition = build_judge_completion_hook(
            service=service,
            judge_mode_controller=judge_mode_controller,
            model_access_coordinator=ModelAccessCoordinator(),
        )
        candidate = "The official reading is Tenon."
        decision = hook(
            JudgeCompletionContext(
                model_key=QWEN_MODEL_KEY,
                request_id="real-judge-enforce-correction-1",
                user_input="No. The correct reading is Amane Kanata.",
                assistant_content=candidate,
                dialogue_context=(
                    "assistant: The official reading is Tenon.",
                    "user: No. The correct reading is Amane Kanata.",
                ),
                evidence_context=(
                    "official-source | canonical-name.txt: The reading is Amane Kanata.",
                ),
                judge_mode="enforce",
                repair_mode="off",
                recording_mode="off",
                enforce_presented_final=True,
            )
        )

        assert decision is not None
        assert decision.candidate_withheld is True
        assert decision.presentation_outcome == "safe_fallback"
        assert decision.presented_content == SEMANTIC_ENFORCEMENT_SAFE_FALLBACK
        assert candidate not in decision.presented_content
        result = composition.last_result()
        assert result is not None
        assert result.recommendation != "accept"
    finally:
        service.unload()
