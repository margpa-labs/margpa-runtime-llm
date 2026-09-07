"""Phase 9-2 WU-F F1: Comparison Report."""

from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.experiment.local_filesystem_experiment_store import (
    LocalFilesystemExperimentStore,
)
from margpa_runtime_llm.modules.experiment.application.comparison_service import (
    build_comparison_report,
)
from margpa_runtime_llm.modules.experiment.application.experiment_service import (
    ExperimentService,
)
from margpa_runtime_llm.modules.experiment.domain.comparison_report import ComparisonRow
from margpa_runtime_llm.modules.experiment.domain.dataset import ObservationOutcome
from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.evaluation import (
    EvaluatorKind,
    MetricObservation,
    RuntimeOutcomeState,
    build_automated_observation,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    VariantDescriptor,
    build_experiment_plan,
)
from margpa_runtime_llm.modules.experiment.domain.run import RunState


def _plan_and_two_runs(tmp_path: Path) -> tuple[ExperimentService, str]:
    store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    service = ExperimentService(store=store)
    variant_a = VariantDescriptor(
        variant_id="baseline",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="off"),),
    )
    variant_b = VariantDescriptor(
        variant_id="judge-enforce",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),),
    )
    plan = build_experiment_plan(
        experiment_id="exp-cmp-1",
        case_id="case-1",
        case_revision="case-rev-1",
        case_digest_sha512="4" * 128,
        variants=(variant_a, variant_b),
        execution_order=("baseline", "judge-enforce"),
    )
    service.create_plan(plan)
    run_a = service.start_run(
        experiment_id="exp-cmp-1",
        variant_id="baseline",
        run_id="run-a",
        request_id="req-a",
        execution_mode="fixture",
    )
    service.publish_result(
        "run-a",
        generation=run_a.generation,
        target_state=RunState.COMPLETED,
        raw_evidence={
            "metric": {"run_id": "run-a", "case_id": "case-1", "runtime_state": "completed"}
        },
    )
    run_b = service.start_run(
        experiment_id="exp-cmp-1",
        variant_id="judge-enforce",
        run_id="run-b",
        request_id="req-b",
        execution_mode="fixture",
    )
    service.publish_result("run-b", generation=run_b.generation, target_state=RunState.FAILED)
    return service, "exp-cmp-1"


def test_comparison_report_aggregates_every_run_with_its_own_metric(tmp_path: Path) -> None:
    service, experiment_id = _plan_and_two_runs(tmp_path)
    report = build_comparison_report(
        experiment_id=experiment_id,
        case_revision="case-rev-1",
        store=service.store,
    )
    assert len(report.rows) == 2
    row_a = report.row("run-a")
    row_b = report.row("run-b")
    assert row_a is not None and row_a.runtime_state is RuntimeOutcomeState.COMPLETED
    assert row_a.metric is not None
    assert row_b is not None and row_b.runtime_state is RuntimeOutcomeState.FAILED
    assert row_b.metric is None


def test_comparison_report_is_persisted_and_restart_readable(tmp_path: Path) -> None:
    service, experiment_id = _plan_and_two_runs(tmp_path)
    build_comparison_report(
        experiment_id=experiment_id, case_revision="case-rev-1", store=service.store
    )
    fresh_store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    persisted = fresh_store.load_comparison(experiment_id)
    assert persisted is not None
    assert persisted["experiment_id"] == experiment_id


def test_comparison_report_carries_distinct_observations_per_run(tmp_path: Path) -> None:
    service, experiment_id = _plan_and_two_runs(tmp_path)
    observation = build_automated_observation(
        run_id="run-a",
        case_id="case-1",
        evaluator_kind=EvaluatorKind.INDEPENDENT_JUDGE,
        provider_identity="judge.gemma-4-e2b-it-q4-0",
        rubric_revision="case-rev-1",
        outcome=ObservationOutcome.PASS,
    )
    report = build_comparison_report(
        experiment_id=experiment_id,
        case_revision="case-rev-1",
        store=service.store,
        observations_by_run_id={"run-a": (observation,)},
    )
    row_a = report.row("run-a")
    assert row_a is not None
    assert row_a.observations == (observation,)
    row_b = report.row("run-b")
    assert row_b is not None
    assert row_b.observations == ()


def test_comparison_row_rejects_an_observation_for_a_different_run_id() -> None:
    """R1-WU-04 Hard Assert #7: an Observation whose own `run_id` does not
    match the Row it was filed under is a Typed Reject, not silently
    attached."""
    observation = build_automated_observation(
        run_id="a-different-run",
        case_id="case-1",
        evaluator_kind=EvaluatorKind.DETERMINISTIC,
        provider_identity="metric.deterministic-v1",
        rubric_revision="rubric-v1",
        outcome=ObservationOutcome.NOT_RUN,
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        ComparisonRow(
            variant_id="variant-a",
            run_id="run-x",
            runtime_state=RuntimeOutcomeState.FAILED,
            observations=(observation,),
            raw_evidence_pointer="run-x",
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.OBSERVATION_RUN_OR_CASE_MISMATCH


def test_comparison_row_rejects_an_observation_for_a_different_case_id_than_its_metric() -> None:
    observation = build_automated_observation(
        run_id="run-x",
        case_id="a-different-case",
        evaluator_kind=EvaluatorKind.DETERMINISTIC,
        provider_identity="metric.deterministic-v1",
        rubric_revision="rubric-v1",
        outcome=ObservationOutcome.NOT_RUN,
    )
    metric = MetricObservation(
        run_id="run-x", case_id="case-1", runtime_state=RuntimeOutcomeState.FAILED
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        ComparisonRow(
            variant_id="variant-a",
            run_id="run-x",
            runtime_state=RuntimeOutcomeState.FAILED,
            metric=metric,
            observations=(observation,),
            raw_evidence_pointer="run-x",
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.OBSERVATION_RUN_OR_CASE_MISMATCH


def test_comparison_row_rejects_a_pass_observation_on_a_non_completed_run() -> None:
    observation = build_automated_observation(
        run_id="run-x",
        case_id="case-1",
        evaluator_kind=EvaluatorKind.DETERMINISTIC,
        provider_identity="metric.deterministic-v1",
        rubric_revision="rubric-v1",
        outcome=ObservationOutcome.PASS,
    )
    with pytest.raises(ExperimentCoreError):
        ComparisonRow(
            variant_id="variant-a",
            run_id="run-x",
            runtime_state=RuntimeOutcomeState.FAILED,
            observations=(observation,),
            raw_evidence_pointer="run-x",
        )
