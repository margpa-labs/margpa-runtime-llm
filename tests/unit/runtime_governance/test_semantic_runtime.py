from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.governance_definitions.domain import (
    GovernanceMode,
    GovernanceModeTransitionError,
)
from margpa_runtime_llm.modules.runtime_governance.application import (
    MainGovernanceModeController,
    SemanticRuntimeCoordinator,
    freeze_semantic_turn,
    merge_structural_and_semantic_observations,
    resolve_semantic_action,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    Observation,
    ObservationOutcome,
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticDeferredReason,
    SemanticEvaluationMethod,
    SemanticEvaluationResponse,
    SemanticEvaluationStage,
    SemanticFinalDisposition,
    SemanticProviderState,
    Severity,
)

_DIGEST = "a" * 128


def _criterion(index: int = 1) -> SemanticCriterion:
    return SemanticCriterion(
        criterion_id=f"semantic.argd.rule.{index}",
        descriptor_id=f"argd.rule.{index}",
        source_definition_id="argd",
        source_definition_digest_sha512=_DIGEST,
        source_pointer=f"/rules/{index}",
        source_text_digest_sha512=_DIGEST,
        instruction="Do not contradict the supplied evidence.",
        governance_point="main_model.semantic",
        evaluation_stage=SemanticEvaluationStage.POST,
        evaluation_method=SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        severity_policy="high",
        recommended_action_policy="repair_or_safe_fallback",
        evidence_requirements=("request_identity",),
    )


def _result(
    criterion: SemanticCriterion,
    disposition: SemanticCriterionDisposition,
    *,
    reason: str | None = None,
) -> SemanticCriterionResult:
    return SemanticCriterionResult(
        criterion_id=criterion.criterion_id,
        descriptor_id=criterion.descriptor_id,
        disposition=disposition,
        confidence=0.9,
        reason_code=reason,
    )


def test_structural_placeholder_is_replaced_but_core_observation_is_retained() -> None:
    criterion = _criterion()
    merged = merge_structural_and_semantic_observations(
        structural=(
            Observation(
                descriptor_id=criterion.descriptor_id,
                evaluation_method="requires_semantic_evaluator",
                outcome=ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR,
            ),
            Observation(
                descriptor_id="core.structural.empty_output",
                evaluation_method="deterministic",
                outcome=ObservationOutcome.DEVIATION,
                severity=Severity.HIGH,
                detail_code="empty_output",
            ),
        ),
        criteria=(criterion,),
        semantic_results=(_result(criterion, SemanticCriterionDisposition.PASS),),
    )
    assert [item.descriptor_id for item in merged] == [
        criterion.descriptor_id,
        "core.structural.empty_output",
    ]
    assert merged[0].outcome is ObservationOutcome.PASS
    assert merged[1].outcome is ObservationOutcome.DEVIATION


def test_duplicate_criterion_result_is_rejected_not_double_recorded() -> None:
    criterion = _criterion()
    result = _result(criterion, SemanticCriterionDisposition.PASS)
    with pytest.raises(ValueError, match="duplicate semantic criterion result"):
        merge_structural_and_semantic_observations(
            structural=(), criteria=(criterion,), semantic_results=(result, result)
        )


def test_turn_snapshot_freezes_provider_budget_language_and_modes() -> None:
    frozen = freeze_semantic_turn(
        request_id="req-1",
        generation=1,
        criteria=(_criterion(1), _criterion(2)),
        language="ja",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=1,
    )
    assert frozen.snapshot.language == "ja"
    assert frozen.snapshot.configured_provider == "judge.selene"
    assert len(frozen.snapshot.criteria) == 1
    assert frozen.initially_deferred[0].reason_code == "budget_exhausted"


def test_coordinator_rejects_duplicate_and_late_publication() -> None:
    criterion = _criterion()
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
    first = coordinator.begin(
        request_id="req-1",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    response = SemanticEvaluationResponse(
        request_id="req-1",
        generation=first.generation,
        provider_id="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        results=(_result(criterion, SemanticCriterionDisposition.PASS),),
        latency_ms=1,
    )
    assert coordinator.record_response(response=response, structural=()) is not None
    assert coordinator.record_response(response=response, structural=()) is None
    coordinator.begin(
        request_id="req-2",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    assert coordinator.record_response(response=response, structural=()) is None


def test_provider_short_result_becomes_typed_unknown_not_pass() -> None:
    criteria = (_criterion(1), _criterion(2))
    coordinator = SemanticRuntimeCoordinator(criteria=criteria)
    snapshot = coordinator.begin(
        request_id="req-1",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    evidence = coordinator.record_response(
        response=SemanticEvaluationResponse(
            request_id="req-1",
            generation=snapshot.generation,
            provider_id="judge.selene",
            provider_state=SemanticProviderState.ACTIVE,
            results=(_result(criteria[0], SemanticCriterionDisposition.PASS),),
            latency_ms=1,
        ),
        structural=(),
    )
    assert evidence is not None
    assert [item.disposition for item in evidence.criterion_results] == [
        SemanticCriterionDisposition.PASS,
        SemanticCriterionDisposition.UNKNOWN,
    ]
    assert evidence.criterion_results[1].reason_code == "malformed_result"


def test_live_turn_covers_all_109_criteria_with_selected_and_budget_deferred_counts() -> None:
    criteria = tuple(_criterion(index) for index in range(1, 110))
    coordinator = SemanticRuntimeCoordinator(criteria=criteria)
    snapshot = coordinator.begin(
        request_id="req-109",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=32,
    )
    assert len(snapshot.criteria) == 32
    assert snapshot.deferred_criteria_count == 77
    evidence = coordinator.record_response(
        response=SemanticEvaluationResponse(
            request_id="req-109",
            generation=snapshot.generation,
            provider_id="judge.selene",
            provider_state=SemanticProviderState.ACTIVE,
            results=tuple(
                _result(item, SemanticCriterionDisposition.PASS) for item in snapshot.criteria
            ),
            latency_ms=1,
        ),
        structural=(),
    )
    assert evidence is not None
    assert len(evidence.criterion_results) == 109
    assert (
        sum(
            item.disposition is SemanticCriterionDisposition.PASS
            for item in evidence.criterion_results
        )
        == 32
    )
    deferred = tuple(
        item
        for item in evidence.criterion_results
        if item.disposition is SemanticCriterionDisposition.DEFERRED
    )
    assert len(deferred) == 77
    assert {item.reason_code for item in deferred} == {"budget_exhausted"}


def test_provider_failure_is_not_mislabeled_as_malformed_result() -> None:
    criteria = (_criterion(1), _criterion(2))
    coordinator = SemanticRuntimeCoordinator(criteria=criteria)
    snapshot = coordinator.begin(
        request_id="req-provider-failure",
        language="en",
        main_mode="observe",
        judge_mode="observe",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    evidence = coordinator.record_response(
        response=SemanticEvaluationResponse(
            request_id="req-provider-failure",
            generation=snapshot.generation,
            provider_id="judge.selene",
            provider_state=SemanticProviderState.FAILED,
            results=(),
            latency_ms=1,
            failure_reason="provider_transport_failed",
        ),
        structural=(),
    )
    assert evidence is not None
    assert all(
        item.disposition is SemanticCriterionDisposition.UNKNOWN
        and item.reason_code == "provider_failure"
        for item in evidence.criterion_results
    )


def test_main_enforce_activation_is_rejected_without_active_enforcing_judge() -> None:
    controller = MainGovernanceModeController(enforce_ready=True)
    controller.set_semantic_enforce_gate(lambda: (False, "judge_enforce_required"))
    with pytest.raises(GovernanceModeTransitionError, match="judge_enforce_required"):
        controller.apply_mode(GovernanceMode.ENFORCE)


def test_action_resolver_keeps_recommendation_separate_from_execution() -> None:
    criterion = _criterion()
    frozen = freeze_semantic_turn(
        request_id="req-1",
        generation=1,
        criteria=(criterion,),
        language="en",
        main_mode="observe",
        judge_mode="enforce",
        repair_mode="enforce",
        configured_provider="judge.selene",
        active_provider="judge.selene",
        provider_state=SemanticProviderState.ACTIVE,
        budget_profile="local",
        max_criteria=8,
    )
    decision = resolve_semantic_action(
        snapshot=frozen.snapshot,
        results=(_result(criterion, SemanticCriterionDisposition.DEVIATION),),
    )
    assert decision.recommended_disposition is SemanticFinalDisposition.REPAIR_REQUESTED
    assert decision.executed_disposition is SemanticFinalDisposition.OBSERVED


def test_judge_off_is_recorded_per_criterion_with_reason() -> None:
    criterion = _criterion()
    coordinator = SemanticRuntimeCoordinator(criteria=(criterion,))
    coordinator.begin(
        request_id="req-off",
        language="en",
        main_mode="observe",
        judge_mode="off",
        repair_mode="off",
        configured_provider="judge.selene",
        active_provider=None,
        provider_state=SemanticProviderState.NONE,
        budget_profile="local",
        max_criteria=8,
    )
    evidence = coordinator.record_deferred(
        request_id="req-off", reason=SemanticDeferredReason.JUDGE_OFF
    )
    assert evidence is not None
    assert evidence.criterion_results[0].reason_code == "judge_off"
    assert evidence.criterion_results[0].disposition is SemanticCriterionDisposition.DEFERRED
