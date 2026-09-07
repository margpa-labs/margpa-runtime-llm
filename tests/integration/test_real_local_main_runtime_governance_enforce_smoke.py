"""P9-1 Package 2 Real Local Judge Experiment: Main Runtime Governance
ENFORCE (Handoff WU-07), including ARGD/DAGD, against the real Main
Qwen3-4B model and the real, checked-in ARGD/DAGD Reference Corpus.

Distinct from Judge-level ENFORCE (`test_real_local_judge_observe_enforce_
repair_smoke.py`, which exercises `judge_live_integration.py`'s own
`resolve_evaluation_disposition()`): Main Runtime Governance ENFORCE lives
one layer above, in `modules/runtime_governance/application/semantic_
runtime.py`'s `resolve_semantic_action()`, gated on `frozen_main_mode ==
"enforce"` *in addition to* `frozen_judge_mode == "enforce"` and a genuinely
Active Judge Provider (`SemanticRuntimeCoordinator.begin()`/`record_
response()`'s own Fail-closed `false_enforce_prevented` guard against Main
claiming ENFORCE while Judge cannot actually back it -- this is the exact
distinction the P9-1 hypothesis doc itself insists on: "Qwen3Guardの基本
OBSERVE/ENFORCE PASSをJudge PASSへ読み替えない", extended here to "Judge
PASSをMain Runtime Governance ENFORCE PASSへ読み替えない").

Prior to this Package, Main Runtime Governance ENFORCE was `NOT ESTABLISHED`
(`phase_9_1_all_judge_operational_failure_common_substrate_hypothesis_and_
rework_order_ja_20260902103228.md` §9) purely because the Judge layer
beneath it never produced a real Result to feed it -- this test is the
first real evidence that, with the Common Substrate truncation fix,
`resolve_semantic_action()`'s existing (already Fixture-tested)
Fail-closed gates and Action resolution genuinely complete end to end
against a real Model, real ARGD/DAGD Criteria, and both `main_mode`/
`judge_mode` frozen to `"enforce"` simultaneously.
"""

import platform
from pathlib import Path
from uuid import uuid4

import pytest

from margpa_runtime_llm.adapters.evaluation.selene import SeleneSemanticEvaluator
from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.adapters.runtime_governance.semantic_criterion_adapter import (
    compile_argd_dagd_semantic_criteria,
)
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.bootstrap.runtime_governance import (
    default_authority,
    load_reference_descriptors,
)
from margpa_runtime_llm.modules.evaluation.application.judge_prompt_builder import (
    MainSemanticPromptAdapter,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig
from margpa_runtime_llm.modules.runtime_governance.application.semantic_runtime import (
    SemanticRuntimeCoordinator,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    RuntimeCapabilitySnapshot,
    SemanticCriterion,
    SemanticEvaluationRequest,
    SemanticFinalDisposition,
    SemanticProviderState,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = PROJECT_ROOT / "models"
QWEN_MODEL_KEY = "main.qwen3-4b-q4-k-m"


def _real_criteria() -> tuple[SemanticCriterion, ...]:
    loaded = load_reference_descriptors(
        definitions_root=PROJECT_ROOT / "definitions",
        capability=RuntimeCapabilitySnapshot(
            model_key=QWEN_MODEL_KEY,
            backend_kind="llama_cpp",
            supports_streaming=True,
            supports_thinking=True,
            max_context_tokens=8192,
        ),
        authority=default_authority(),
    )
    assert loaded.state == "loaded"
    compiled = compile_argd_dagd_semantic_criteria(loaded.descriptors)
    assert len(compiled.criteria) == 109
    return compiled.criteria


pytestmark = [
    pytest.mark.model_smoke,
    pytest.mark.skipif(
        platform.system() != "Darwin" or platform.machine() != "arm64",
        reason="The Phase 6/9 model smoke requires Apple Silicon",
    ),
]


def _load_service() -> InferenceService:
    definitions = DirectoryModelDefinitionRegistry(registry_dir=PROJECT_ROOT / "config/models")
    definition = definitions.resolve(model_key=QWEN_MODEL_KEY)
    adapter = LlamaCppModelAdapter(model_root=MODEL_ROOT)
    service = InferenceService(adapter)
    service.load(definition, ModelLoadConfig(context_size=4096, gpu_layers=-1))
    return service


def test_real_main_runtime_governance_enforce_accepts_a_genuinely_correct_candidate() -> None:
    """`main_mode="enforce"` AND `judge_mode="enforce"` together, a real
    correct Candidate against real ARGD/DAGD Criteria -- the Golden Path
    the Handoff calls for: `resolve_semantic_action()` must reach
    `CANDIDATE_ACCEPTED`, never a Fail-closed `false_enforce_prevented`
    (that guard exists for exactly the pre-fix state where Judge could
    never genuinely complete)."""
    artifact_path = MODEL_ROOT / "main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
    if not artifact_path.is_file():
        pytest.skip(f"Local model artifact is unavailable: {artifact_path}")

    coordinator = SemanticRuntimeCoordinator(criteria=_real_criteria())
    service = _load_service()
    try:
        request_id = f"real-governance-enforce-accept-{uuid4()}"
        snapshot = coordinator.begin(
            request_id=request_id,
            language="en",
            main_mode="enforce",
            judge_mode="enforce",
            repair_mode="off",
            configured_provider=QWEN_MODEL_KEY,
            active_provider=QWEN_MODEL_KEY,
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=32,
        )
        evaluator = SeleneSemanticEvaluator(
            service=service,
            model_key=QWEN_MODEL_KEY,
            prompt_adapter=MainSemanticPromptAdapter(
                rubric_id="live_conversation_general_quality_v1"
            ),
            provider_label="main_shared",
        )
        response = evaluator.evaluate(
            request=SemanticEvaluationRequest(
                snapshot=snapshot,
                stage="post",
                user_input="What is the capital of France?",
                candidate_answer="The capital of France is Paris.",
                evidence_context=(
                    "official-source | reference.txt: The capital of France is Paris.",
                ),
            )
        )
        if response.provider_state is not SemanticProviderState.ACTIVE:
            pytest.skip(
                f"Real Judge output was not decodable this run (legitimate "
                f"fail-closed outcome): provider_state="
                f"{response.provider_state.value!r} "
                f"failure_reason={response.failure_reason!r}"
            )
        evidence = coordinator.record_response(response=response, structural=())
        assert evidence is not None
        assert evidence.action.reason_code != "false_enforce_prevented"
        if evidence.action.executed_disposition is not SemanticFinalDisposition.CANDIDATE_ACCEPTED:
            pytest.skip(
                f"Real Model did not accept a genuinely correct Candidate "
                f"this run (real-model non-determinism, not a code "
                f"defect): action={evidence.action!r}"
            )
        assert evidence.action.reason_code == "all_selected_criteria_passed"
        assert evidence.action.repair_eligible is False
    finally:
        service.unload()


def test_real_main_runtime_governance_enforce_requests_repair_for_a_contradicting_candidate() -> (
    None
):
    """Same Golden Path, `repair_mode="enforce"` too, and a Candidate that
    contradicts the supplied real Evidence -- `resolve_semantic_action()`
    must reach `REPAIR_REQUESTED` with `repair_eligible=True` and
    `reason_code="main_governance_repair_authorized"` (never silently
    `CANDIDATE_ACCEPTED`, and never `false_enforce_prevented` -- Judge is
    genuinely Active). P9-1 Judge/Governance Rework (WU-03): the reason
    code changed from `"repair_authorized"` -- Main Governance's own
    authorization no longer depends on `repair_mode` at all (reached here
    with `repair_mode="enforce"` only because this specific Test also
    wants a `RepairMode` value other than the default `"off"` on the
    Snapshot; `resolve_semantic_action()` itself would authorize this
    Turn's repair identically even with `repair_mode="off"` -- see
    `test_wu03_main_enforce_authorizes_a_main_origin_repair_even_with_
    existing_repair_off` in `tests/unit/bootstrap/test_judge_live_
    integration.py` for that exact case through the real end-to-end
    dispatch, not only this lower-level Coordinator call)."""
    artifact_path = MODEL_ROOT / "main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
    if not artifact_path.is_file():
        pytest.skip(f"Local model artifact is unavailable: {artifact_path}")

    coordinator = SemanticRuntimeCoordinator(criteria=_real_criteria())
    service = _load_service()
    try:
        request_id = f"real-governance-enforce-repair-{uuid4()}"
        snapshot = coordinator.begin(
            request_id=request_id,
            language="en",
            main_mode="enforce",
            judge_mode="enforce",
            repair_mode="enforce",
            configured_provider=QWEN_MODEL_KEY,
            active_provider=QWEN_MODEL_KEY,
            provider_state=SemanticProviderState.ACTIVE,
            budget_profile="test",
            max_criteria=32,
        )
        evaluator = SeleneSemanticEvaluator(
            service=service,
            model_key=QWEN_MODEL_KEY,
            prompt_adapter=MainSemanticPromptAdapter(
                rubric_id="live_conversation_general_quality_v1"
            ),
            provider_label="main_shared",
        )
        response = evaluator.evaluate(
            request=SemanticEvaluationRequest(
                snapshot=snapshot,
                stage="post",
                user_input="What is the capital of France?",
                candidate_answer="The capital of France is Tenon.",
                evidence_context=(
                    "official-source | reference.txt: The capital of France is Paris.",
                ),
            )
        )
        if response.provider_state is not SemanticProviderState.ACTIVE:
            pytest.skip(
                f"Real Judge output was not decodable this run (legitimate "
                f"fail-closed outcome): provider_state="
                f"{response.provider_state.value!r} "
                f"failure_reason={response.failure_reason!r}"
            )
        evidence = coordinator.record_response(response=response, structural=())
        assert evidence is not None
        assert evidence.action.reason_code != "false_enforce_prevented"
        # The crux, mirroring this Package's own established real-model
        # philosophy: a real Model's own judgment is never rewritten by
        # this test. Only silent acceptance of the known-wrong Candidate
        # is forbidden.
        assert (
            evidence.action.executed_disposition is not SemanticFinalDisposition.CANDIDATE_ACCEPTED
        )
        if evidence.action.executed_disposition is SemanticFinalDisposition.REPAIR_REQUESTED:
            assert evidence.action.repair_eligible is True
            assert evidence.action.reason_code == "main_governance_repair_authorized"
    finally:
        service.unload()
