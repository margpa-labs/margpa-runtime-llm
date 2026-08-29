"""P6-RR-R3-WU-006 (Post-Claude Independent Review Rework): reproduces,
and verifies the fix for, part of P6-CODEX-064 / N-WU-004 — the Main
Governance Status route's `main_model.post` projection previously read
only the Structural-only `StandardGovernanceResult` frozen at Post-hook
time, which never updated again even after real Semantic evaluation
completed (P6-GOV-017's "Deferred (semantic evaluation pending) 109" that never resolves).
"""

from __future__ import annotations

from margpa_runtime_llm.bootstrap.runtime_governance import RuntimeGovernanceComposition
from margpa_runtime_llm.modules.runtime_governance.domain import (
    MAIN_MODEL_POST_POINT_ID,
    EvaluationMethod,
    ExecutionDescriptor,
    ExecutionState,
    Observation,
    ObservationOutcome,
    RuntimeCapabilitySnapshot,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticEvaluationResponse,
    SemanticProviderState,
    StandardGovernanceResult,
)
from margpa_runtime_llm.web.runtime_governance_routes import _point_status

_CAPABILITY = RuntimeCapabilitySnapshot(
    model_key="main.test-model",
    backend_kind="test",
    supports_streaming=True,
    supports_thinking=False,
    max_context_tokens=8192,
)
# `intp_interpretive_premises` is one of `semantic_criterion_adapter._ARGD_MAP`'s
# mapped keys (evaluation_stage=BOTH) — a real, compilable ARGD descriptor
# id, not a fabricated shape.
_DESCRIPTOR_ID = "argd.intp_interpretive_premises.1"


def _descriptor() -> ExecutionDescriptor:
    return ExecutionDescriptor(
        descriptor_id=_DESCRIPTOR_ID,
        source_definition_id="argd",
        source_pointer="/rules/intp/1",
        source_definition_digest_sha512="a" * 128,
        source_text_digest_sha512="a" * 128,
        summary="Do not contradict the user's own stated premises.",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )


def _deferred_structural_result() -> StandardGovernanceResult:
    return StandardGovernanceResult(
        invocation_id="invocation-1",
        point_id=MAIN_MODEL_POST_POINT_ID,
        stage="post",
        mode="observe",
        execution_state=ExecutionState.EVALUATED,
        observations=(
            Observation(
                descriptor_id=_DESCRIPTOR_ID,
                evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR.value,
                outcome=ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR,
                detail_code="deferred",
            ),
        ),
    )


def _composition() -> RuntimeGovernanceComposition:
    composition = RuntimeGovernanceComposition(capability=_CAPABILITY, descriptors=(_descriptor(),))
    assert len(composition.semantic_compile_result.criteria) == 1
    composition.record_result(
        point_id=MAIN_MODEL_POST_POINT_ID, result=_deferred_structural_result()
    )
    return composition


def test_before_semantic_evidence_status_reflects_the_frozen_structural_deferred_count() -> None:
    """Baseline (pre-Rework-identical): no Semantic evidence recorded yet
    -> the raw Structural-only observation set, still Deferred."""
    composition = _composition()

    status = _point_status(composition, point_id=MAIN_MODEL_POST_POINT_ID)

    assert status.observation_count == 1
    assert status.deferred_count == 1
    assert status.pass_count == 0


def test_after_semantic_evidence_status_projects_the_real_resolved_outcome() -> None:
    """The Fix: once real Semantic evaluation completes for the same Turn,
    the Status projection must show the resolved outcome instead of the
    permanently-frozen Deferred placeholder."""
    composition = _composition()
    criterion = composition.semantic_compile_result.criteria[0]

    snapshot = composition.semantic_runtime.begin(
        request_id="req-1",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="built_in.deterministic",
        active_provider="built_in.deterministic",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    assert snapshot.criteria == (criterion,)

    response = SemanticEvaluationResponse(
        request_id="req-1",
        generation=snapshot.generation,
        provider_id="built_in.deterministic",
        provider_state=SemanticProviderState.ACTIVE,
        results=(
            SemanticCriterionResult(
                criterion_id=criterion.criterion_id,
                descriptor_id=criterion.descriptor_id,
                disposition=SemanticCriterionDisposition.PASS,
                confidence=0.9,
            ),
        ),
        latency_ms=10,
    )
    evidence = composition.record_semantic_response(response=response)
    assert evidence is not None
    assert evidence.merged_observations[0].outcome is ObservationOutcome.PASS

    status = _point_status(composition, point_id=MAIN_MODEL_POST_POINT_ID)

    assert status.observation_count == 1
    assert status.pass_count == 1
    assert status.deferred_count == 0


def test_late_result_for_a_superseded_turn_never_overwrites_the_current_turn() -> None:
    """R3-WU-007: a Dispatch that completes for an older, superseded Turn
    must not clobber the Status projection for the Turn that is actually
    Current — `SemanticRuntimeCoordinator.record_response()`'s own
    request_id/generation guard (Package K, unchanged by this Rework) is
    what this test pins."""
    composition = _composition()
    criterion = composition.semantic_compile_result.criteria[0]

    first_snapshot = composition.semantic_runtime.begin(
        request_id="req-old",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="built_in.deterministic",
        active_provider="built_in.deterministic",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )
    # A newer Turn begins before the old Turn's (e.g. preempted)
    # evaluation ever reports back.
    composition.semantic_runtime.begin(
        request_id="req-new",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="built_in.deterministic",
        active_provider="built_in.deterministic",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="test",
        max_criteria=8,
    )

    late_response = SemanticEvaluationResponse(
        request_id="req-old",
        generation=first_snapshot.generation,
        provider_id="built_in.deterministic",
        provider_state=SemanticProviderState.ACTIVE,
        results=(
            SemanticCriterionResult(
                criterion_id=criterion.criterion_id,
                descriptor_id=criterion.descriptor_id,
                disposition=SemanticCriterionDisposition.PASS,
                confidence=0.9,
            ),
        ),
        latency_ms=10,
    )
    late_evidence = composition.record_semantic_response(response=late_response)

    assert late_evidence is None  # rejected: no longer the Current Turn
    # The Status projection for the (now-Current, unresolved) Turn must
    # still show the honest Deferred placeholder, never the late Turn's
    # PASS smuggled in.
    status = _point_status(composition, point_id=MAIN_MODEL_POST_POINT_ID)
    assert status.deferred_count == 1
    assert status.pass_count == 0
