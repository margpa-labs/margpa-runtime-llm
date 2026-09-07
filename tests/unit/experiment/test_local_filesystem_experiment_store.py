"""Phase 9-2 WU-A A3: LocalFilesystemExperimentStore Restart-readability.

Uses `tmp_path` exclusively (WU-A A3: "Testでは`tmp_path`を使い、Userの実
`runtime_data`へ書かない") -- never the real `runtime_data/` tree."""

from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.experiment.local_filesystem_experiment_store import (
    ExperimentStorePathRejected,
    LocalFilesystemExperimentStore,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    ExperimentPlan,
    VariantDescriptor,
    build_experiment_plan,
)
from margpa_runtime_llm.modules.experiment.domain.run import RunState, VariantRun

_CASE_DIGEST = "1" * 128


def _plan(experiment_id: str = "exp-store-1") -> ExperimentPlan:
    variant = VariantDescriptor(
        variant_id="variant-a",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    return build_experiment_plan(
        experiment_id=experiment_id,
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_CASE_DIGEST,
        variants=(variant,),
        execution_order=("variant-a",),
    )


def test_save_and_load_plan_round_trips(tmp_path: Path) -> None:
    store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    plan = _plan()
    assert store.load_plan(plan.experiment_id) is None
    store.save_plan(plan)
    loaded = store.load_plan(plan.experiment_id)
    assert loaded == plan


def test_a_fresh_store_instance_reads_what_a_prior_instance_wrote(tmp_path: Path) -> None:
    """Simulates a process Restart: a brand-new Store object pointed at the
    same `base_dir` must read everything the previous instance wrote."""
    first = LocalFilesystemExperimentStore(base_dir=tmp_path)
    plan = _plan()
    first.save_plan(plan)
    run = VariantRun(
        run_id="run-1",
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        request_id="req-1",
        execution_mode="fixture",
        state=RunState.RUNNING,
        generation=1,
        started_at="2026-09-06T00:00:00+00:00",
    )
    first.save_run(run)
    first.save_raw_evidence("run-1", {"observed": "value"})
    first.save_comparison(plan.experiment_id, {"summary": "ok"})

    second = LocalFilesystemExperimentStore(base_dir=tmp_path)
    assert second.load_plan(plan.experiment_id) == plan
    assert second.load_run("run-1") == run
    assert second.load_raw_evidence("run-1") == {"observed": "value"}
    assert second.load_comparison(plan.experiment_id) == {"summary": "ok"}


def test_list_runs_filters_by_experiment_id(tmp_path: Path) -> None:
    store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    plan_a = _plan("exp-a")
    plan_b = _plan("exp-b")
    store.save_plan(plan_a)
    store.save_plan(plan_b)
    run_a = VariantRun(
        run_id="run-a", experiment_id="exp-a", variant_id="variant-a",
        request_id="req-a", execution_mode="fixture", state=RunState.RUNNING, generation=1,
    )
    run_b = VariantRun(
        run_id="run-b", experiment_id="exp-b", variant_id="variant-a",
        request_id="req-b", execution_mode="fixture", state=RunState.RUNNING, generation=1,
    )
    store.save_run(run_a)
    store.save_run(run_b)
    assert store.list_runs("exp-a") == (run_a,)
    assert store.list_runs("exp-b") == (run_b,)
    assert store.list_runs("exp-does-not-exist") == ()


def test_save_run_overwrites_atomically_for_the_same_run_id(tmp_path: Path) -> None:
    store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    run = VariantRun(
        run_id="run-1", experiment_id="exp-1", variant_id="variant-a",
        request_id="req-1", execution_mode="fixture", state=RunState.RUNNING, generation=1,
    )
    store.save_run(run)
    updated = run.model_copy(update={"state": RunState.COMPLETED, "completed_at": "now"})
    store.save_run(updated)
    assert store.load_run("run-1") == updated
    # Exactly one target file -- no stray `.tmp` left behind after replace.
    files = list((tmp_path / "runs").glob("*"))
    assert files == [tmp_path / "runs" / "run-1.json"]


@pytest.mark.parametrize("unsafe_id", ["../escape", "a/b", ""])
def test_unsafe_identifiers_are_rejected_before_any_filesystem_write(
    tmp_path: Path, unsafe_id: str
) -> None:
    store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    with pytest.raises(ExperimentStorePathRejected):
        store.load_run(unsafe_id)
    assert not tmp_path.exists() or list(tmp_path.iterdir()) == []


def test_run_configuration_snapshot_round_trips_and_survives_restart(tmp_path: Path) -> None:
    """R3-WU-01 (IR-P9-2-R2-03 MAJOR fix): a Run's own genuine Frozen
    Configuration Snapshot -- restart-readable exactly like every other
    Experiment Core artifact."""

    first = LocalFilesystemExperimentStore(base_dir=tmp_path)
    assert first.load_run_configuration_snapshot("run-1") is None
    snapshot = {"configuration_digest_sha512": "a" * 128, "main": {"mode": "active"}}
    first.save_run_configuration_snapshot("run-1", snapshot)
    assert first.load_run_configuration_snapshot("run-1") == snapshot

    second = LocalFilesystemExperimentStore(base_dir=tmp_path)
    assert second.load_run_configuration_snapshot("run-1") == snapshot


def test_variant_desired_configuration_round_trips_and_is_scoped_per_experiment(
    tmp_path: Path,
) -> None:
    """Two different `experiment_id`s must never collide on the same
    `variant_id` -- each Plan's own Desired Configuration is scoped to
    its own Experiment."""

    store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    assert store.load_variant_desired_configuration("exp-a", "variant-x") is None
    snapshot_a = {"configuration_digest_sha512": "a" * 128}
    snapshot_b = {"configuration_digest_sha512": "b" * 128}
    store.save_variant_desired_configuration("exp-a", "variant-x", snapshot_a)
    store.save_variant_desired_configuration("exp-b", "variant-x", snapshot_b)
    assert store.load_variant_desired_configuration("exp-a", "variant-x") == snapshot_a
    assert store.load_variant_desired_configuration("exp-b", "variant-x") == snapshot_b

    second = LocalFilesystemExperimentStore(base_dir=tmp_path)
    assert second.load_variant_desired_configuration("exp-a", "variant-x") == snapshot_a
