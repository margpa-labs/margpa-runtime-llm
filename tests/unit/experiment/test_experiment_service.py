"""Phase 9-2 WU-A A4: ExperimentService Minimal API."""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Literal

import pytest

from margpa_runtime_llm.adapters.experiment.local_filesystem_experiment_store import (
    LocalFilesystemExperimentStore,
)
from margpa_runtime_llm.modules.experiment.application.experiment_service import (
    ExperimentService,
)
from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    ExperimentPlan,
    ExperimentPlanBudget,
    StopPolicy,
    VariantDescriptor,
    build_experiment_plan,
)
from margpa_runtime_llm.modules.experiment.domain.run import RunState


def _service(tmp_path: Path) -> ExperimentService:
    return ExperimentService(store=LocalFilesystemExperimentStore(base_dir=tmp_path))


_CASE_DIGEST = "3" * 128


def _plan(
    experiment_id: str = "exp-1",
    *,
    budget: ExperimentPlanBudget | None = None,
    execution_mode: Literal["fixture", "production"] = "fixture",
) -> ExperimentPlan:
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
        budget=budget,
        execution_mode=execution_mode,
    )


def test_create_plan_then_start_run_reaches_running(tmp_path: Path) -> None:
    service = _service(tmp_path)
    plan = service.create_plan(_plan())
    run = service.start_run(
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
    )
    assert run.state is RunState.RUNNING
    assert run.generation == 1
    assert run.request_id == "req-1"
    assert service.get_run("run-1") == run


@pytest.mark.parametrize("execution_mode", ["fixture", "production"])
def test_start_run_derives_execution_mode_only_from_the_persisted_plan_across_restart(
    tmp_path: Path, execution_mode: Literal["fixture", "production"]
) -> None:
    """IR-P9-2-WHOLE-R1-01: callers have no execution-mode input at Run
    start. Both initial and Restart reads must preserve Plan/Run equality,
    so neither a production-to-fixture downgrade nor the reverse exists."""

    service = _service(tmp_path)
    plan = service.create_plan(
        _plan(f"exp-{execution_mode}", execution_mode=execution_mode)
    )
    assert "execution_mode" not in inspect.signature(service.start_run).parameters

    run = service.start_run(
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        run_id=f"run-{execution_mode}",
        request_id=f"req-{execution_mode}",
    )
    assert run.execution_mode == plan.execution_mode == execution_mode

    restarted_store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    restarted_plan = restarted_store.load_plan(plan.experiment_id)
    restarted_run = restarted_store.load_run(run.run_id)
    assert restarted_plan is not None
    assert restarted_run is not None
    assert restarted_run.execution_mode == restarted_plan.execution_mode == execution_mode


def test_create_plan_rejects_duplicate_experiment_id(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.create_plan(_plan())
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.create_plan(_plan())
    assert excinfo.value.code is ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER


def test_start_run_rejects_unknown_variant(tmp_path: Path) -> None:
    service = _service(tmp_path)
    plan = service.create_plan(_plan())
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.start_run(
            experiment_id=plan.experiment_id,
            variant_id="no-such-variant",
            run_id="run-1",
            request_id="req-1",
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.UNKNOWN_VARIANT


def test_start_run_rejects_duplicate_run_id(tmp_path: Path) -> None:
    service = _service(tmp_path)
    plan = service.create_plan(_plan())
    service.start_run(
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.start_run(
            experiment_id=plan.experiment_id,
            variant_id="variant-a",
            run_id="run-1",
            request_id="req-1",
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.DUPLICATE_IDENTIFIER


def test_cancel_run_transitions_to_cancelled(tmp_path: Path) -> None:
    service = _service(tmp_path)
    plan = service.create_plan(_plan())
    service.start_run(
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
    )
    cancelled = service.cancel_run("run-1")
    assert cancelled.state is RunState.CANCELLED
    assert cancelled.completed_at is not None


def test_cancel_run_twice_is_rejected_as_terminal_already_published(tmp_path: Path) -> None:
    service = _service(tmp_path)
    plan = service.create_plan(_plan())
    service.start_run(
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
    )
    service.cancel_run("run-1")
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.cancel_run("run-1")
    assert excinfo.value.code is ExperimentCoreErrorCode.TERMINAL_ALREADY_PUBLISHED


def test_publish_result_records_raw_evidence_and_get_result_returns_it(tmp_path: Path) -> None:
    service = _service(tmp_path)
    plan = service.create_plan(_plan())
    run = service.start_run(
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
    )
    completed = service.publish_result(
        "run-1",
        generation=run.generation,
        target_state=RunState.COMPLETED,
        raw_evidence={"call_count": 4},
    )
    assert completed.state is RunState.COMPLETED
    result = service.get_result("run-1")
    assert result.run == completed
    assert result.raw_evidence == {"call_count": 4}


def test_publish_result_rejects_a_stale_generation_late_result(tmp_path: Path) -> None:
    """WU-A A3 Late-Result rejection: a Cancel bumps the generation, so an
    in-flight Call from before the Cancel that finishes afterward (still
    carrying the old generation) must not be able to overwrite the
    Cancelled outcome."""
    service = _service(tmp_path)
    plan = service.create_plan(_plan())
    run = service.start_run(
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
    )
    stale_generation = run.generation
    service.cancel_run("run-1")
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.publish_result(
            "run-1", generation=stale_generation, target_state=RunState.COMPLETED
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.LATE_RESULT_REJECTED
    # The Cancelled outcome must remain untouched by the rejected publish.
    assert service.get_run("run-1").state is RunState.CANCELLED


def test_publish_result_rejects_double_terminal_publish_even_at_the_current_generation(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    plan = service.create_plan(_plan())
    run = service.start_run(
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
    )
    service.publish_result("run-1", generation=run.generation, target_state=RunState.COMPLETED)
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.publish_result("run-1", generation=run.generation, target_state=RunState.FAILED)
    assert excinfo.value.code is ExperimentCoreErrorCode.LATE_RESULT_REJECTED


def test_get_run_raises_not_found_for_unknown_run_id(tmp_path: Path) -> None:
    service = _service(tmp_path)
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.get_run("no-such-run")
    assert excinfo.value.code is ExperimentCoreErrorCode.NOT_FOUND


def test_a_fresh_service_instance_over_the_same_store_sees_prior_runs_after_restart(
    tmp_path: Path,
) -> None:
    """WU-A A3: a Restart re-creates the Service (fresh in-memory
    generation table) over the same persisted Store -- an already-
    persisted Run must still be readable."""
    first = _service(tmp_path)
    plan = first.create_plan(_plan())
    first.start_run(
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
    )
    first.publish_result("run-1", generation=1, target_state=RunState.COMPLETED)

    second = ExperimentService(store=LocalFilesystemExperimentStore(base_dir=tmp_path))
    restarted_run = second.get_run("run-1")
    assert restarted_run.state is RunState.COMPLETED
    assert restarted_run.request_id == "req-1"
    assert second.list_runs(plan.experiment_id) == (restarted_run,)


def test_start_run_rejects_a_second_run_once_max_variant_runs_is_reached(
    tmp_path: Path,
) -> None:
    """R1-WU-02 (IR-P9-2-06 fix): `budget.max_variant_runs` is enforced as
    a real Runtime Contract -- a Plan capped at one Run must reject a
    second `start_run()` call before any Actor is ever invoked, not just
    document the limit."""
    service = _service(tmp_path)
    plan = service.create_plan(_plan(budget=ExperimentPlanBudget(max_variant_runs=1)))
    service.start_run(
        experiment_id=plan.experiment_id,
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.start_run(
            experiment_id=plan.experiment_id,
            variant_id="variant-a",
            run_id="run-2",
            request_id="req-2",
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.MAX_VARIANT_RUNS_EXCEEDED


def test_start_run_enforces_execution_order_when_a_stop_policy_is_set(tmp_path: Path) -> None:
    """R1-WU-02: with a `stop_policy` set, a later Variant in
    `execution_order` may not start before an earlier one has a Run at
    all -- Execution Order becomes a real pre-invocation Reject, not a
    Digest-only field."""
    variant_a = VariantDescriptor(
        variant_id="variant-a",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    variant_b = VariantDescriptor(
        variant_id="variant-b",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    plan = build_experiment_plan(
        experiment_id="exp-order-1",
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_CASE_DIGEST,
        variants=(variant_a, variant_b),
        execution_order=("variant-a", "variant-b"),
        budget=ExperimentPlanBudget(stop_policy=StopPolicy.CONTINUE_ON_FAILURE),
    )
    service = _service(tmp_path)
    service.create_plan(plan)
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.start_run(
            experiment_id="exp-order-1",
            variant_id="variant-b",
            run_id="run-b",
            request_id="req-b",
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.EXECUTION_ORDER_VIOLATION
    # The correct next Variant is still startable.
    started = service.start_run(
        experiment_id="exp-order-1",
        variant_id="variant-a",
        run_id="run-a",
        request_id="req-a",
    )
    assert started.variant_id == "variant-a"


def test_start_run_halts_further_variants_after_a_failure_under_halt_on_first_failure(
    tmp_path: Path,
) -> None:
    variant_a = VariantDescriptor(
        variant_id="variant-a",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    variant_b = VariantDescriptor(
        variant_id="variant-b",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    plan = build_experiment_plan(
        experiment_id="exp-order-2",
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_CASE_DIGEST,
        variants=(variant_a, variant_b),
        execution_order=("variant-a", "variant-b"),
        budget=ExperimentPlanBudget(stop_policy=StopPolicy.HALT_ON_FIRST_FAILURE),
    )
    service = _service(tmp_path)
    service.create_plan(plan)
    run_a = service.start_run(
        experiment_id="exp-order-2",
        variant_id="variant-a",
        run_id="run-a",
        request_id="req-a",
    )
    service.publish_result(
        "run-a", generation=run_a.generation, target_state=RunState.FAILED, failure_reason="x"
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.start_run(
            experiment_id="exp-order-2",
            variant_id="variant-b",
            run_id="run-b",
            request_id="req-b",
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.EXECUTION_ORDER_VIOLATION


def test_reconcile_orphaned_running_runs_cancels_running_and_planned_runs_left_by_a_prior_process(
    tmp_path: Path,
) -> None:
    """R2-WU-04 (IR-P9-2-R1-06 fix): a Run a PREVIOUS process left
    `planned`/`running` has no Task backing it in a freshly-constructed
    `ExperimentService` (this process's own `_generations` counter starts
    empty) -- without reconciliation it would show `running` forever."""

    store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    first_process = ExperimentService(store=store)
    first_process.create_plan(_plan("exp-restart-1"))
    running_run = first_process.start_run(
        experiment_id="exp-restart-1",
        variant_id="variant-a",
        run_id="run-orphan-running",
        request_id="req-1",
    )
    # A genuinely completed Run must never be touched by reconciliation.
    completed_run = first_process.start_run(
        experiment_id="exp-restart-1",
        variant_id="variant-a",
        run_id="run-genuinely-completed",
        request_id="req-2",
    )
    first_process.publish_result(
        completed_run.run_id, generation=completed_run.generation, target_state=RunState.COMPLETED
    )
    del first_process  # simulates the process exiting without a clean shutdown

    second_process = ExperimentService(store=store)  # simulates a Restart
    reconciled = second_process.reconcile_orphaned_running_runs()
    assert {run.run_id for run in reconciled} == {running_run.run_id}
    orphan_after = second_process.get_run(running_run.run_id)
    assert orphan_after.state is RunState.CANCELLED
    assert orphan_after.failure_reason == "interrupted_by_restart"
    completed_after = second_process.get_run(completed_run.run_id)
    assert completed_after.state is RunState.COMPLETED
    assert completed_after.failure_reason is None

    # Idempotent: a second reconciliation call finds nothing left to do --
    # the Run is already terminal.
    assert second_process.reconcile_orphaned_running_runs() == ()
