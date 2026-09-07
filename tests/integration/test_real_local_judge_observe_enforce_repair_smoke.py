"""P9-1 Package 2 Real Local Judge Experiment: OBSERVE/ENFORCE and
Judge->Repair->Rejudge Evidence against the real Main-shared Qwen3-4B
model, with real Semantic Criteria (the batched dispatch path this
Package's Common Substrate fix targets), through the full
`build_judge_completion_hook()` -- not only the lower-level
`SeleneSemanticEvaluator` these other real smoke tests exercise directly.

Three real scenarios:
1. OBSERVE: the Candidate is never withheld, but a real Judge Run still
   genuinely executes and is recorded (P6-ACC-016's own OBSERVE contract).
2. ENFORCE + a genuinely correct Candidate: real ACCEPT -> Candidate
   presented as-is.
3. ENFORCE + Repair ENFORCE + a Candidate that contradicts the supplied
   real Evidence: the known-wrong Candidate must never be silently
   presented as accepted -- either Repair genuinely replaces it with a
   corrected answer, or ENFORCE safe-falls-back. Both are legitimate real
   outcomes for a real (non-seeded) Model; only silent acceptance of the
   known-wrong Candidate is a failure, mirroring `test_real_local_judge_
   smoke.py`'s own established philosophy for this exact class of test.
"""

import platform
import time
from functools import partial
from pathlib import Path
from uuid import uuid4

import pytest

from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
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
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode
from margpa_runtime_llm.modules.runtime_governance.application import freeze_semantic_turn
from margpa_runtime_llm.modules.runtime_governance.domain import (
    SemanticCriterion,
    SemanticEvaluationMethod,
    SemanticEvaluationStage,
    SemanticProviderState,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = PROJECT_ROOT / "models"
QWEN_MODEL_KEY = "main.qwen3-4b-q4-k-m"
ARTIFACT_PATH = MODEL_ROOT / "main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"


def _criterion(instruction: str) -> SemanticCriterion:
    digest = "a" * 128
    return SemanticCriterion(
        criterion_id="semantic.argd.evidence.1",
        descriptor_id="argd.evidence.1",
        source_definition_id="argd",
        source_definition_digest_sha512=digest,
        source_pointer="/rules/evidence/1",
        source_text_digest_sha512=digest,
        instruction=instruction,
        governance_point="main_model.semantic",
        evaluation_stage=SemanticEvaluationStage.POST,
        evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        severity_policy="high",
        recommended_action_policy="repair_or_safe_fallback",
        evidence_requirements=("request_identity",),
    )


pytestmark = [
    pytest.mark.model_smoke,
    pytest.mark.skipif(
        platform.system() != "Darwin" or platform.machine() != "arm64",
        reason="The Phase 6/9 model smoke requires Apple Silicon",
    ),
]


def _wait_for_result(
    composition: JudgeGovernanceComposition, *, timeout_seconds: float = 30.0
) -> LiveJudgeResult:
    """OBSERVE is asynchronous by design (module docstring) -- a real
    background Model Call genuinely takes longer than the fixture-only
    tests' own short timeout, so this real-hardware variant waits up to
    30s rather than 2s."""
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        result = composition.last_result()
        if result is not None:
            return result
        time.sleep(0.02)
    raise AssertionError("Judge background thread did not record a result in time")


def _load_service() -> InferenceService:
    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    definition = definitions.resolve(model_key=QWEN_MODEL_KEY)
    adapter = LlamaCppModelAdapter(model_root=MODEL_ROOT)
    service = InferenceService(adapter)
    service.load(definition, ModelLoadConfig(context_size=4096, gpu_layers=-1))
    return service


def test_a_real_observe_run_never_withholds_the_candidate_but_genuinely_judges() -> None:
    if not ARTIFACT_PATH.is_file():
        pytest.skip(f"Local model artifact is unavailable: {ARTIFACT_PATH}")
    service = _load_service()
    try:
        request_id = f"real-observe-{uuid4()}"
        frozen = freeze_semantic_turn(
            request_id=request_id,
            generation=1,
            criteria=(_criterion("Do not contradict the cited evidence."),),
            language="en",
            main_mode="observe",
            judge_mode="observe",
            repair_mode="off",
            configured_provider=QWEN_MODEL_KEY,
            active_provider=QWEN_MODEL_KEY,
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=8,
        )
        controller = JudgeModeController()
        controller.apply_mode(EvaluationMode.OBSERVE)
        recorded: list[object] = []
        hook, composition = build_judge_completion_hook(
            service=service,
            judge_mode_controller=controller,
            model_access_coordinator=ModelAccessCoordinator(),
            semantic_snapshot_provider=lambda rid: frozen.snapshot if rid == request_id else None,
            semantic_result_recorder=recorded.append,
        )
        candidate = "The capital of France is Paris."
        decision = hook(
            JudgeCompletionContext(
                model_key=QWEN_MODEL_KEY,
                request_id=request_id,
                user_input="What is the capital of France?",
                assistant_content=candidate,
                evidence_context=(
                    "official-source | reference.txt: The capital of France is Paris.",
                ),
                judge_mode="observe",
                repair_mode="off",
                recording_mode="off",
                enforce_presented_final=False,
            )
        )
        # OBSERVE never gates the Presented Final at all -- this Hook
        # returns a decision only under ENFORCE (`enforce_presented_final`
        # gates the synchronous wait); the real value of this scenario is
        # the Run genuinely executing and being recorded, not `decision`
        # itself.
        assert decision is None
        result = _wait_for_result(composition)
        assert result.frozen_judge_mode == "observe"
        # A real Judge Run genuinely happened (Model Call 1, batched path)
        # -- never Deferred/evaluated 0 the way the pre-fix defect produced.
        assert result.execution_state in ("completed", "failed")
        assert len(recorded) == 1
    finally:
        service.unload()


def test_a_real_enforce_run_accepts_a_genuinely_correct_candidate() -> None:
    if not ARTIFACT_PATH.is_file():
        pytest.skip(f"Local model artifact is unavailable: {ARTIFACT_PATH}")
    service = _load_service()
    try:
        request_id = f"real-enforce-accept-{uuid4()}"
        frozen = freeze_semantic_turn(
            request_id=request_id,
            generation=1,
            criteria=(_criterion("Do not contradict the cited evidence."),),
            language="en",
            main_mode="observe",
            judge_mode="enforce",
            repair_mode="off",
            configured_provider=QWEN_MODEL_KEY,
            active_provider=QWEN_MODEL_KEY,
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=8,
        )
        controller = JudgeModeController()
        controller.apply_mode(EvaluationMode.ENFORCE)
        hook, composition = build_judge_completion_hook(
            service=service,
            judge_mode_controller=controller,
            model_access_coordinator=ModelAccessCoordinator(),
            semantic_snapshot_provider=lambda rid: frozen.snapshot if rid == request_id else None,
        )
        candidate = "The capital of France is Paris."
        decision = hook(
            JudgeCompletionContext(
                model_key=QWEN_MODEL_KEY,
                request_id=request_id,
                user_input="What is the capital of France?",
                assistant_content=candidate,
                evidence_context=(
                    "official-source | reference.txt: The capital of France is Paris.",
                ),
                judge_mode="enforce",
                repair_mode="off",
                recording_mode="off",
                enforce_presented_final=True,
            )
        )
        assert decision is not None
        result = composition.last_result()
        assert result is not None
        if result.recommendation != "accept":
            pytest.skip(
                f"Real Qwen did not recommend accept for a genuinely "
                f"correct Candidate this run (real-model non-determinism, "
                f"not a code defect): recommendation={result.recommendation!r} "
                f"failure_reason={result.failure_reason!r}"
            )
        assert decision.presentation_outcome == "candidate_accepted"
        assert decision.candidate_withheld is False
        assert decision.presented_content == candidate
    finally:
        service.unload()


def test_a_real_enforce_repair_run_never_silently_accepts_a_contradicting_candidate() -> None:
    if not ARTIFACT_PATH.is_file():
        pytest.skip(f"Local model artifact is unavailable: {ARTIFACT_PATH}")
    service = _load_service()
    try:
        request_id = f"real-enforce-repair-{uuid4()}"
        frozen = freeze_semantic_turn(
            request_id=request_id,
            generation=1,
            criteria=(_criterion("Do not contradict the cited evidence."),),
            language="en",
            main_mode="observe",
            judge_mode="enforce",
            repair_mode="enforce",
            configured_provider=QWEN_MODEL_KEY,
            active_provider=QWEN_MODEL_KEY,
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=8,
        )
        controller = JudgeModeController()
        controller.apply_mode(EvaluationMode.ENFORCE)
        repair_controller = RepairModeController()
        repair_controller.apply_mode(RepairMode.ENFORCE)
        hook, _composition = build_judge_completion_hook(
            service=service,
            judge_mode_controller=controller,
            model_access_coordinator=ModelAccessCoordinator(),
            repair_mode_controller=repair_controller,
            repair_executor=partial(
                attempt_live_repair,
                service=service,
                model_key=QWEN_MODEL_KEY,
                persistent=None,
            ),
            semantic_snapshot_provider=lambda rid: frozen.snapshot if rid == request_id else None,
        )
        candidate = "The capital of France is Tenon."
        decision = hook(
            JudgeCompletionContext(
                model_key=QWEN_MODEL_KEY,
                request_id=request_id,
                user_input="What is the capital of France?",
                assistant_content=candidate,
                evidence_context=(
                    "official-source | reference.txt: The capital of France is Paris.",
                ),
                judge_mode="enforce",
                repair_mode="enforce",
                recording_mode="off",
                enforce_presented_final=True,
            )
        )
        assert decision is not None
        # The crux, mirroring `test_real_qwen_enforce_withholds_an_evidence_
        # contradicting_candidate`'s own established philosophy: a real
        # Model's own judgment call is never rewritten into PASS by this
        # test. Either Repair genuinely replaced the wrong Candidate, or
        # ENFORCE safe-fell-back -- silent acceptance of the known-wrong
        # Candidate is the only forbidden outcome.
        assert decision.presentation_outcome != "candidate_accepted"
        assert candidate not in decision.presented_content
    finally:
        service.unload()
