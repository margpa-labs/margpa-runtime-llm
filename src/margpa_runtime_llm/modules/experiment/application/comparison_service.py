"""Comparison Report builder (Phase 9-2, WU-F F1).

Reads every persisted `VariantRun` for an Experiment back out of the
`ExperimentStorePort` (never a separate, parallel bookkeeping structure)
and assembles one `ComparisonReport`, persisting it via the same Port's
`save_comparison()` -- Restart-readable, exactly like every other
Experiment Core artifact (WU-A A3)."""

from __future__ import annotations

from collections.abc import Mapping

from ..domain.comparison_report import ComparisonReport, ComparisonRow
from ..domain.evaluation import EvaluationObservation, MetricObservation, RuntimeOutcomeState
from ..domain.run import RunState, VariantRun
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


def _metric_for(raw_evidence: dict[str, object] | None) -> MetricObservation | None:
    if raw_evidence is None:
        return None
    metric_payload = raw_evidence.get("metric")
    if metric_payload is None:
        return None
    return MetricObservation.model_validate(metric_payload)


def build_comparison_report(
    *,
    experiment_id: str,
    case_revision: str,
    store: ExperimentStorePort,
    observations_by_run_id: Mapping[str, tuple[EvaluationObservation, ...]] | None = None,
) -> ComparisonReport:
    observations_map = observations_by_run_id or {}
    runs = store.list_runs(experiment_id)
    rows = tuple(
        ComparisonRow(
            variant_id=run.variant_id,
            run_id=run.run_id,
            runtime_state=runtime_state_for_run(run),
            metric=_metric_for(store.load_raw_evidence(run.run_id)),
            observations=observations_map.get(run.run_id, ()),
            failure_reason=run.failure_reason,
            raw_evidence_pointer=run.run_id,
        )
        for run in runs
    )
    report = ComparisonReport(experiment_id=experiment_id, case_revision=case_revision, rows=rows)
    store.save_comparison(experiment_id, report.model_dump(mode="json"))
    return report
