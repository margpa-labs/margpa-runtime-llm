"""Semantic evaluation orchestration and structural/semantic composition."""

from __future__ import annotations

import threading
from dataclasses import dataclass

from ..domain import (
    BudgetSnapshot,
    ExecutionDescriptor,
    Observation,
    ObservationOutcome,
    SemanticActionDecision,
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticDeferredReason,
    SemanticEvaluationRequest,
    SemanticEvaluationResponse,
    SemanticEvaluationStage,
    SemanticFinalDisposition,
    SemanticProviderState,
    SemanticRuntimeEvidence,
    SemanticTurnSnapshot,
    Severity,
    semantic_contract_digest,
)
from ..ports import DeterministicEvaluatorPort, SemanticEvaluatorPort


@dataclass(frozen=True, slots=True)
class FrozenSemanticTurn:
    snapshot: SemanticTurnSnapshot
    initially_deferred: tuple[SemanticCriterionResult, ...]


def freeze_semantic_turn(
    *,
    request_id: str,
    generation: int,
    criteria: tuple[SemanticCriterion, ...],
    language: str,
    main_mode: str,
    judge_mode: str,
    repair_mode: str,
    configured_provider: str,
    active_provider: str | None,
    provider_state: SemanticProviderState,
    budget_profile: str,
    max_criteria: int,
) -> FrozenSemanticTurn:
    """Capture every mutable semantic input once at the Main pre boundary."""

    applicable = tuple(
        sorted(
            (
                item
                for item in criteria
                if item.evaluation_stage
                in (SemanticEvaluationStage.POST, SemanticEvaluationStage.BOTH)
            ),
            key=lambda item: item.criterion_id,
        )
    )
    selected = applicable[:max_criteria]
    deferred = tuple(
        SemanticCriterionResult(
            criterion_id=item.criterion_id,
            descriptor_id=item.descriptor_id,
            disposition=SemanticCriterionDisposition.DEFERRED,
            reason_code=SemanticDeferredReason.BUDGET_EXHAUSTED.value,
        )
        for item in applicable[max_criteria:]
    )
    batch_digest = semantic_contract_digest(
        {
            "stage": SemanticEvaluationStage.POST.value,
            "selected": [item.criterion_id for item in selected],
            "deferred": [item.criterion_id for item in deferred],
        }
    )
    payload = {
        "request_id": request_id,
        "generation": generation,
        "language": language,
        "main_mode": main_mode,
        "judge_mode": judge_mode,
        "repair_mode": repair_mode,
        "configured_provider": configured_provider,
        "active_provider": active_provider,
        "provider_state": provider_state.value,
        "budget_profile": budget_profile,
        "max_criteria": max_criteria,
        "criterion_ids": [item.criterion_id for item in selected],
        "deferred_criteria_count": len(deferred),
        "batch_digest": batch_digest,
    }
    snapshot = SemanticTurnSnapshot(
        request_id=request_id,
        generation=generation,
        language=language,
        frozen_main_mode=main_mode,
        frozen_judge_mode=judge_mode,
        frozen_repair_mode=repair_mode,
        configured_provider=configured_provider,
        active_provider=active_provider,
        provider_state=provider_state,
        budget_profile=budget_profile,
        max_criteria=max_criteria,
        criteria=selected,
        deferred_criteria_count=len(deferred),
        batch_digest_sha512=batch_digest,
        frozen_digest_sha512=semantic_contract_digest(payload),
    )
    return FrozenSemanticTurn(snapshot=snapshot, initially_deferred=deferred)


def merge_structural_and_semantic_observations(
    *,
    structural: tuple[Observation, ...],
    criteria: tuple[SemanticCriterion, ...],
    semantic_results: tuple[SemanticCriterionResult, ...],
) -> tuple[Observation, ...]:
    """Replace semantic placeholders, retaining independent structural checks.

    A criterion/result identity may occur only once.  Duplicate provider output
    is rejected instead of being recorded twice or silently last-write-wins.
    """

    criteria_by_id = {item.criterion_id: item for item in criteria}
    if len(criteria_by_id) != len(criteria):
        raise ValueError("duplicate semantic criterion identity")
    result_ids = [item.criterion_id for item in semantic_results]
    if len(set(result_ids)) != len(result_ids):
        raise ValueError("duplicate semantic criterion result")

    semantic_by_descriptor: dict[str, Observation] = {}
    for result in semantic_results:
        criterion = criteria_by_id.get(result.criterion_id)
        if criterion is None or criterion.descriptor_id != result.descriptor_id:
            raise ValueError("semantic result identity does not match the frozen criterion")
        if criterion.descriptor_id in semantic_by_descriptor:
            raise ValueError("multiple semantic results target one descriptor")
        semantic_by_descriptor[criterion.descriptor_id] = _semantic_observation(
            criterion=criterion, result=result
        )

    merged: dict[str, Observation] = {}
    for observation in structural:
        if (
            observation.descriptor_id in semantic_by_descriptor
            and observation.outcome is ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR
        ):
            continue
        if observation.descriptor_id in merged:
            raise ValueError("duplicate structural observation identity")
        merged[observation.descriptor_id] = observation
    merged.update(semantic_by_descriptor)
    return tuple(merged[key] for key in sorted(merged))


def _semantic_observation(
    *, criterion: SemanticCriterion, result: SemanticCriterionResult
) -> Observation:
    outcome = {
        SemanticCriterionDisposition.PASS: ObservationOutcome.PASS,
        SemanticCriterionDisposition.DEVIATION: ObservationOutcome.DEVIATION,
        SemanticCriterionDisposition.UNKNOWN: ObservationOutcome.UNKNOWN,
        SemanticCriterionDisposition.DEFERRED: (ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR),
        SemanticCriterionDisposition.NOT_APPLICABLE: (
            ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR
        ),
    }[result.disposition]
    severity = (
        Severity(criterion.severity_policy)
        if result.disposition is SemanticCriterionDisposition.DEVIATION
        else Severity.NONE
    )
    return Observation(
        descriptor_id=criterion.descriptor_id,
        evaluation_method=criterion.evaluation_method.value,
        outcome=outcome,
        detail_code=result.reason_code or result.disposition.value,
        severity=severity,
        recommended_action_id=(
            "warn" if result.disposition is SemanticCriterionDisposition.DEVIATION else None
        ),
    )


def resolve_semantic_action(
    *, snapshot: SemanticTurnSnapshot, results: tuple[SemanticCriterionResult, ...]
) -> SemanticActionDecision:
    """Resolve recommendation separately from the authority-owned action."""

    if not results:
        return SemanticActionDecision(
            recommended_disposition=SemanticFinalDisposition.NOT_EVALUATED,
            executed_disposition=SemanticFinalDisposition.NOT_EVALUATED,
            repair_eligible=False,
            reason_code="no_semantic_result",
        )
    has_deviation = any(
        item.disposition is SemanticCriterionDisposition.DEVIATION for item in results
    )
    has_uncertain = any(
        item.disposition
        in (SemanticCriterionDisposition.UNKNOWN, SemanticCriterionDisposition.DEFERRED)
        for item in results
    )
    if snapshot.frozen_main_mode != "enforce":
        return SemanticActionDecision(
            recommended_disposition=(
                SemanticFinalDisposition.REPAIR_REQUESTED
                if has_deviation
                else SemanticFinalDisposition.NOT_EVALUATED
                if has_uncertain
                else SemanticFinalDisposition.CANDIDATE_ACCEPTED
            ),
            executed_disposition=SemanticFinalDisposition.OBSERVED,
            repair_eligible=has_deviation,
            reason_code="observe_non_intervening",
        )
    if (
        snapshot.frozen_judge_mode != "enforce"
        or snapshot.provider_state is not SemanticProviderState.ACTIVE
        or snapshot.active_provider is None
    ):
        return SemanticActionDecision(
            recommended_disposition=SemanticFinalDisposition.NOT_EVALUATED,
            executed_disposition=SemanticFinalDisposition.SAFE_FALLBACK,
            repair_eligible=False,
            reason_code="false_enforce_prevented",
        )
    if has_uncertain:
        return SemanticActionDecision(
            recommended_disposition=SemanticFinalDisposition.SAFE_FALLBACK,
            executed_disposition=SemanticFinalDisposition.SAFE_FALLBACK,
            repair_eligible=False,
            reason_code="semantic_result_inconclusive",
        )
    if has_deviation:
        repair_eligible = snapshot.frozen_repair_mode == "enforce"
        return SemanticActionDecision(
            recommended_disposition=SemanticFinalDisposition.REPAIR_REQUESTED,
            executed_disposition=(
                SemanticFinalDisposition.REPAIR_REQUESTED
                if repair_eligible
                else SemanticFinalDisposition.SAFE_FALLBACK
            ),
            repair_eligible=repair_eligible,
            reason_code=("repair_authorized" if repair_eligible else "repair_unavailable"),
        )
    return SemanticActionDecision(
        recommended_disposition=SemanticFinalDisposition.CANDIDATE_ACCEPTED,
        executed_disposition=SemanticFinalDisposition.CANDIDATE_ACCEPTED,
        repair_eligible=False,
        reason_code="all_selected_criteria_passed",
    )


class CompositeSemanticEvaluator:
    """Runs structural and semantic ports once and merges their identities."""

    def __init__(
        self,
        *,
        structural_evaluator: DeterministicEvaluatorPort,
        semantic_evaluator: SemanticEvaluatorPort,
    ) -> None:
        self._structural = structural_evaluator
        self._semantic = semantic_evaluator

    def evaluate(
        self,
        *,
        descriptors: tuple[ExecutionDescriptor, ...],
        stage: str,
        structural_snapshot: str,
        structural_budget: BudgetSnapshot,
        semantic_request: SemanticEvaluationRequest,
    ) -> tuple[SemanticEvaluationResponse, tuple[Observation, ...]]:
        structural = self._structural.evaluate(
            descriptors=descriptors,
            stage=stage,
            snapshot=structural_snapshot,
            budget=structural_budget,
        )
        response = self._semantic.evaluate(request=semantic_request)
        return response, merge_structural_and_semantic_observations(
            structural=structural,
            criteria=semantic_request.snapshot.criteria,
            semantic_results=response.results,
        )


class SemanticRuntimeCoordinator:
    """Process-local current/history store with generation-safe publication."""

    def __init__(self, *, criteria: tuple[SemanticCriterion, ...]) -> None:
        self._lock = threading.Lock()
        self._criteria = criteria
        self._generation = 0
        self._current: FrozenSemanticTurn | None = None
        self._history: dict[str, SemanticRuntimeEvidence] = {}
        self._recorded_criterion_keys: set[tuple[str, int, str]] = set()

    def begin(
        self,
        *,
        request_id: str,
        language: str,
        main_mode: str,
        judge_mode: str,
        repair_mode: str,
        configured_provider: str,
        active_provider: str | None,
        provider_state: SemanticProviderState,
        budget_profile: str,
        max_criteria: int,
    ) -> SemanticTurnSnapshot:
        with self._lock:
            self._generation += 1
            frozen = freeze_semantic_turn(
                request_id=request_id,
                generation=self._generation,
                criteria=self._criteria,
                language=language,
                main_mode=main_mode,
                judge_mode=judge_mode,
                repair_mode=repair_mode,
                configured_provider=configured_provider,
                active_provider=active_provider,
                provider_state=provider_state,
                budget_profile=budget_profile,
                max_criteria=max_criteria,
            )
            self._current = frozen
            return frozen.snapshot

    def current_snapshot(self) -> SemanticTurnSnapshot | None:
        with self._lock:
            return self._current.snapshot if self._current is not None else None

    def snapshot_for(self, *, request_id: str) -> SemanticTurnSnapshot | None:
        with self._lock:
            if self._current is None or self._current.snapshot.request_id != request_id:
                return None
            return self._current.snapshot

    def record_response(
        self,
        *,
        response: SemanticEvaluationResponse,
        structural: tuple[Observation, ...],
    ) -> SemanticRuntimeEvidence | None:
        with self._lock:
            current = self._current
            if (
                current is None
                or response.request_id != current.snapshot.request_id
                or response.generation != current.snapshot.generation
            ):
                return None
            provider_results = _complete_provider_results(
                criteria=current.snapshot.criteria,
                results=response.results,
                missing_result_reason=_missing_result_reason(response.provider_state),
            )
            results = (*provider_results, *current.initially_deferred)
            keys = {
                (response.request_id, response.generation, item.criterion_id) for item in results
            }
            if len(keys) != len(results) or keys & self._recorded_criterion_keys:
                return None
            merged = merge_structural_and_semantic_observations(
                structural=structural,
                criteria=current.snapshot.criteria,
                semantic_results=provider_results,
            )
            action = resolve_semantic_action(snapshot=current.snapshot, results=results)
            payload = {
                "snapshot": current.snapshot.frozen_digest_sha512,
                "provider": response.provider_id,
                "provider_state": response.provider_state.value,
                "results": [item.model_dump(mode="json") for item in results],
                "merged": [item.model_dump(mode="json") for item in merged],
                "action": action.model_dump(mode="json"),
            }
            evidence = SemanticRuntimeEvidence(
                request_id=response.request_id,
                generation=response.generation,
                frozen_snapshot_digest_sha512=current.snapshot.frozen_digest_sha512,
                configured_provider=current.snapshot.configured_provider,
                active_provider=current.snapshot.active_provider,
                provider_state=response.provider_state,
                criterion_results=tuple(results),
                merged_observations=merged,
                action=action,
                evidence_digest_sha512=semantic_contract_digest(payload),
            )
            self._recorded_criterion_keys.update(keys)
            self._history[response.request_id] = evidence
            return evidence

    def record_deferred(
        self,
        *,
        request_id: str,
        reason: SemanticDeferredReason,
        structural: tuple[Observation, ...] = (),
    ) -> SemanticRuntimeEvidence | None:
        snapshot = self.snapshot_for(request_id=request_id)
        if snapshot is None:
            return None
        response = SemanticEvaluationResponse(
            request_id=request_id,
            generation=snapshot.generation,
            provider_id=snapshot.configured_provider,
            provider_state=snapshot.provider_state,
            results=tuple(
                SemanticCriterionResult(
                    criterion_id=item.criterion_id,
                    descriptor_id=item.descriptor_id,
                    disposition=SemanticCriterionDisposition.DEFERRED,
                    reason_code=reason.value,
                )
                for item in snapshot.criteria
            ),
            latency_ms=0,
            failure_reason=reason.value,
        )
        return self.record_response(response=response, structural=structural)

    def evidence_for(self, *, request_id: str) -> SemanticRuntimeEvidence | None:
        with self._lock:
            return self._history.get(request_id)

    def latest_evidence(self) -> SemanticRuntimeEvidence | None:
        with self._lock:
            if self._current is None:
                return None
            return self._history.get(self._current.snapshot.request_id)


def _complete_provider_results(
    *,
    criteria: tuple[SemanticCriterion, ...],
    results: tuple[SemanticCriterionResult, ...],
    missing_result_reason: SemanticDeferredReason,
) -> tuple[SemanticCriterionResult, ...]:
    expected = {item.criterion_id: item for item in criteria}
    supplied: dict[str, SemanticCriterionResult] = {}
    for result in results:
        criterion = expected.get(result.criterion_id)
        if (
            criterion is None
            or criterion.descriptor_id != result.descriptor_id
            or result.criterion_id in supplied
        ):
            raise ValueError("provider returned an unexpected or duplicate criterion result")
        supplied[result.criterion_id] = result
    return tuple(
        supplied.get(item.criterion_id)
        or SemanticCriterionResult(
            criterion_id=item.criterion_id,
            descriptor_id=item.descriptor_id,
            disposition=SemanticCriterionDisposition.UNKNOWN,
            reason_code=missing_result_reason.value,
        )
        for item in criteria
    )


def _missing_result_reason(provider_state: SemanticProviderState) -> SemanticDeferredReason:
    return {
        SemanticProviderState.ACTIVE: SemanticDeferredReason.MALFORMED_RESULT,
        SemanticProviderState.NONE: SemanticDeferredReason.PROVIDER_NONE,
        SemanticProviderState.UNAVAILABLE: SemanticDeferredReason.PROVIDER_UNAVAILABLE,
        SemanticProviderState.FAILED: SemanticDeferredReason.PROVIDER_FAILURE,
    }[provider_state]
