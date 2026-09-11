"""Comparison Report builder (Phase 9-2, WU-F F1).

Reads every persisted `VariantRun` for an Experiment back out of the
`ExperimentStorePort` (never a separate, parallel bookkeeping structure)
and assembles one `ComparisonReport`, persisting it via the same Port's
`save_comparison()` -- Restart-readable, exactly like every other
Experiment Core artifact (WU-A A3)."""

from __future__ import annotations

from collections.abc import Mapping

from ..domain.comparison_declaration import (
    VariantComparisonDeclaration,
    verify_single_factor_difference,
)
from ..domain.comparison_report import ComparisonReport, ComparisonRow
from ..domain.errors import ExperimentCoreError, ExperimentCoreErrorCode
from ..domain.evaluation import EvaluationObservation, MetricObservation, RuntimeOutcomeState
from ..domain.run import RunState, VariantRun
from ..domain.semantic_evidence import CaseSemanticEvidence
from ..ports import ExperimentStorePort

_RUN_STATE_TO_RUNTIME_STATE: dict[RunState, RuntimeOutcomeState] = {
    RunState.COMPLETED: RuntimeOutcomeState.COMPLETED,
    RunState.FAILED: RuntimeOutcomeState.FAILED,
    RunState.CANCELLED: RuntimeOutcomeState.CANCELLED,
    RunState.PLANNED: RuntimeOutcomeState.NOT_RUN,
    RunState.RUNNING: RuntimeOutcomeState.NOT_RUN,
}


def runtime_state_for_run(run: VariantRun) -> RuntimeOutcomeState:
    """Public (R2-WU-03): also used by `case_evaluator.evaluate_case_
    outcome()` so it can resolve the same `RuntimeOutcomeState` this
    module uses for a `ComparisonRow`, without needing a `ComparisonRow`
    to already exist -- letting the caller (`web/experiment_routes.py`'s
    `get_comparison()`) compute every real `EvaluationObservation` in ONE
    pass over `service.list_runs()`, before ever calling `build_
    comparison_report()`, so the Observations that get persisted and the
    ones returned in the HTTP Response are always the exact same objects
    (IR-P9-2-R1-04 fix)."""

    return _RUN_STATE_TO_RUNTIME_STATE[run.state]


def _metric_for(
    raw_evidence: dict[str, object] | None,
    *,
    authoritative_state: RuntimeOutcomeState,
) -> MetricObservation | None:
    if raw_evidence is None:
        return None
    metric_payload = raw_evidence.get("metric")
    if metric_payload is None:
        return None
    metric = MetricObservation.model_validate(metric_payload)
    # A terminal Run save can fail after Raw Evidence was saved. On the
    # next read that stale metric must never contradict the authoritative
    # persisted Run state; expose it honestly as unavailable instead.
    if metric.runtime_state is not authoritative_state:
        return None
    return metric


def _semantic_evidence_for(
    raw_evidence: dict[str, object] | None,
) -> CaseSemanticEvidence | None:
    if raw_evidence is None:
        return None
    if raw_evidence.get("execution_mode") != "fixture":
        return None
    payload = raw_evidence.get("semantic_evidence")
    if not isinstance(payload, dict):
        return None
    return CaseSemanticEvidence.model_validate(payload)


def build_comparison_report(
    *,
    experiment_id: str,
    store: ExperimentStorePort,
    observations_by_run_id: Mapping[str, tuple[EvaluationObservation, ...]] | None = None,
    variant_relationships: tuple[VariantComparisonDeclaration, ...] = (),
) -> ComparisonReport:
    observations_map = observations_by_run_id or {}
    plan = store.load_plan(experiment_id)
    if plan is None:
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.NOT_FOUND,
            safe_message=f"experiment_id {experiment_id!r} has no Plan",
        )
    for declaration in variant_relationships:
        verify_single_factor_difference(
            baseline=plan.variant(declaration.baseline_variant_id),
            variant=plan.variant(declaration.variant_id),
            declared=declaration,
        )
    runs = store.list_runs(experiment_id)
    rows_list: list[ComparisonRow] = []
    for run in runs:
        raw_evidence = store.load_raw_evidence(run.run_id)
        rows_list.append(
            ComparisonRow(
                variant_id=run.variant_id,
                run_id=run.run_id,
                runtime_state=runtime_state_for_run(run),
                metric=_metric_for(
                    raw_evidence,
                    authoritative_state=runtime_state_for_run(run),
                ),
                observations=observations_map.get(run.run_id, ()),
                failure_reason=run.failure_reason,
                raw_evidence_pointer=run.run_id,
                semantic_evidence=_semantic_evidence_for(raw_evidence),
            )
        )
    rows = tuple(rows_list)
    report = ComparisonReport(
        experiment_id=experiment_id,
        case_id=plan.case_id,
        case_revision=plan.case_revision,
        variant_relationships=variant_relationships,
        rows=rows,
    )
    store.save_comparison(experiment_id, report.model_dump(mode="json"))
    return report
