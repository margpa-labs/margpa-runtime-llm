"""Phase 9-2 R1-WU-05: ExperimentRunWorker."""

from __future__ import annotations

import threading
import time
from pathlib import Path

from margpa_runtime_llm.adapters.experiment.local_filesystem_experiment_store import (
    LocalFilesystemExperimentStore,
)
from margpa_runtime_llm.modules.experiment.application.configuration_lease import (
    ExperimentConfigurationLease,
)
from margpa_runtime_llm.modules.experiment.application.experiment_service import (
    ExperimentService,
)
from margpa_runtime_llm.modules.experiment.application.run_worker import ExperimentRunWorker
from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    ExperimentPlanBudget,
    VariantDescriptor,
    build_experiment_plan,
)
from margpa_runtime_llm.modules.experiment.domain.run import RunState, VariantRun

_CASE_DIGEST = "9" * 128


class CountingLease(ExperimentConfigurationLease):
    def __init__(self) -> None:
        super().__init__()
        self.acquire_count = 0
        self.release_count = 0

    def acquire(self) -> None:
        super().acquire()
        self.acquire_count += 1

    def release(self) -> None:
        self.release_count += 1
        super().release()


def _service(tmp_path: Path) -> ExperimentService:
    return ExperimentService(store=LocalFilesystemExperimentStore(base_dir=tmp_path))


def _plan_and_run(
    service: ExperimentService, *, budget: ExperimentPlanBudget | None = None
) -> VariantRun:
    variant = VariantDescriptor(
        variant_id="variant-a",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    plan = build_experiment_plan(
        experiment_id="exp-worker-1",
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_CASE_DIGEST,
        variants=(variant,),
        execution_order=("variant-a",),
        budget=budget or ExperimentPlanBudget(),
    )
    service.create_plan(plan)
    return service.start_run(
        experiment_id="exp-worker-1",
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
    )


def _start_run(service: ExperimentService, *, run_id: str) -> VariantRun:
    """Starts a SECOND Run against the same `variant-a` Plan `_plan_and_run`
    already created -- the Plan has no `stop_policy`, so a second Run
    against the same `variant_id` is always permitted."""

    return service.start_run(
        experiment_id="exp-worker-1",
        variant_id="variant-a",
        run_id=run_id,
        request_id=f"req-{run_id}",
    )


def _wait_until_terminal(service: ExperimentService, run_id: str, *, timeout: float = 2.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if service.get_run(run_id).state is not RunState.RUNNING:
            return
        time.sleep(0.01)
    raise AssertionError(f"run {run_id!r} did not reach a terminal state in time")


def test_a_successful_invocation_publishes_completed(tmp_path: Path) -> None:
    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    worker.submit(
        service=service,
        run=run,
        deadline_ms=None,
        invoke=lambda: (RunState.COMPLETED, {"ok": True}, None),
    )
    _wait_until_terminal(service, "run-1")
    result = service.get_result("run-1")
    assert result.run.state is RunState.COMPLETED
    assert result.raw_evidence == {"ok": True}
    worker.shutdown()


def test_an_actor_exception_publishes_failed_never_left_running(tmp_path: Path) -> None:
    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()

    def _boom() -> tuple[RunState, dict[str, object] | None, str | None]:
        raise ValueError("actor exploded")

    worker.submit(service=service, run=run, deadline_ms=None, invoke=_boom)
    _wait_until_terminal(service, "run-1")
    result = service.get_result("run-1")
    assert result.run.state is RunState.FAILED
    assert result.run.failure_reason is not None
    assert "ValueError" in result.run.failure_reason
    worker.shutdown()


def test_an_actor_domain_error_publishes_typed_failed_and_cleans_up_without_a_deadline(
    tmp_path: Path,
) -> None:
    """IR-P9-2-WHOLE-R1-02: invoke-origin ExperimentCoreError is an
    Actor failure, never a publish race that may be swallowed."""

    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    lease = ExperimentConfigurationLease()

    def _domain_failure() -> tuple[RunState, dict[str, object] | None, str | None]:
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.INVALID_STATE_TRANSITION,
            safe_message="sensitive diagnostic must not be persisted",
        )

    worker.submit(
        service=service,
        run=run,
        deadline_ms=None,
        invoke=_domain_failure,
        lease=lease,
    )
    _wait_until_terminal(service, "run-1")
    assert service.get_run("run-1").state is RunState.FAILED
    assert (
        service.get_run("run-1").failure_reason
        == "actor_domain_error:invalid_state_transition"
    )
    assert "sensitive diagnostic" not in (service.get_run("run-1").failure_reason or "")
    assert worker.shutdown(timeout=2.0) is True
    assert lease.is_held() is False
    assert worker.request_cancel("run-1") is False


def test_actor_domain_error_losing_to_cancel_preserves_terminal_and_releases_once(
    tmp_path: Path,
) -> None:
    """Only a durable Terminal publish winner makes the later Actor
    failure publish conflict harmless."""

    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    lease = CountingLease()
    entered = threading.Event()
    release_actor = threading.Event()

    def _domain_failure() -> tuple[RunState, dict[str, object] | None, str | None]:
        entered.set()
        release_actor.wait(timeout=2.0)
        raise ExperimentCoreError(
            code=ExperimentCoreErrorCode.INVALID_STATE_TRANSITION,
            safe_message="actor failed",
        )

    worker.submit(
        service=service,
        run=run,
        deadline_ms=None,
        invoke=_domain_failure,
        lease=lease,
    )
    assert entered.wait(timeout=1.0) is True
    service.cancel_run("run-1")
    release_actor.set()
    assert worker.shutdown(timeout=2.0) is True

    terminal = service.get_run("run-1")
    assert terminal.state is RunState.CANCELLED
    assert terminal.failure_reason is None
    assert lease.acquire_count == 1
    assert lease.release_count == 1
    assert lease.is_held() is False
    assert worker.request_cancel("run-1") is False


def test_an_exceeded_deadline_publishes_failed_without_ever_invoking_the_actor(
    tmp_path: Path,
) -> None:
    """R1-WU-02/06 Hard Assert: a Deadline violation is Actor Call 0."""
    service = _service(tmp_path)
    run = _plan_and_run(service, budget=ExperimentPlanBudget(deadline_ms=1))
    time.sleep(0.05)
    worker = ExperimentRunWorker()
    invoked: list[bool] = []

    def _invoke() -> tuple[RunState, dict[str, object] | None, str | None]:
        invoked.append(True)
        return (RunState.COMPLETED, None, None)

    worker.submit(service=service, run=run, deadline_ms=1, invoke=_invoke)
    _wait_until_terminal(service, "run-1")
    result = service.get_result("run-1")
    assert result.run.state is RunState.FAILED
    assert result.run.failure_reason == "deadline_exceeded"
    assert invoked == []
    worker.shutdown()


def test_request_cancel_calls_the_registered_hook_for_an_in_flight_run(tmp_path: Path) -> None:
    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    release = threading.Event()
    cancel_called = threading.Event()

    def _slow_invoke() -> tuple[RunState, dict[str, object] | None, str | None]:
        release.wait(timeout=2.0)
        return (RunState.CANCELLED, None, None)

    worker.submit(
        service=service,
        run=run,
        deadline_ms=None,
        invoke=_slow_invoke,
        cancel=cancel_called.set,
    )
    # Give the task a moment to actually start and register itself.
    time.sleep(0.05)
    found = worker.request_cancel("run-1")
    assert found is True
    assert cancel_called.wait(timeout=1.0) is True
    release.set()
    _wait_until_terminal(service, "run-1")
    worker.shutdown()


def test_request_cancel_returns_false_for_an_unknown_run_id() -> None:
    worker = ExperimentRunWorker()
    assert worker.request_cancel("no-such-run") is False
    worker.shutdown()


def test_a_deadline_exceeded_while_the_actor_is_still_running_publishes_failed(
    tmp_path: Path,
) -> None:
    """R2-WU-04 (IR-P9-2-R1-06 fix): the Deadline Timer binds the WHOLE
    Run, not only the instant before `invoke()` starts -- a Deadline that
    elapses WHILE a slow Actor Call is still in flight must still force
    `FAILED`/`deadline_exceeded` and call the real Cancel hook, without
    waiting for `invoke()` to return on its own."""

    service = _service(tmp_path)
    run = _plan_and_run(service, budget=ExperimentPlanBudget(deadline_ms=50))
    worker = ExperimentRunWorker()
    release = threading.Event()
    cancel_called = threading.Event()

    def _slow_invoke() -> tuple[RunState, dict[str, object] | None, str | None]:
        # Blocks well past the 50ms Deadline -- the Timer must fire
        # first, independent of when (or whether) this ever returns.
        release.wait(timeout=2.0)
        return (RunState.COMPLETED, {"late": True}, None)

    worker.submit(
        service=service,
        run=run,
        deadline_ms=50,
        invoke=_slow_invoke,
        cancel=cancel_called.set,
    )
    assert cancel_called.wait(timeout=1.0) is True
    _wait_until_terminal(service, "run-1")
    result = service.get_result("run-1")
    assert result.run.state is RunState.FAILED
    assert result.run.failure_reason == "deadline_exceeded"
    # The eventual, late `invoke()` result must never overwrite the
    # already-terminal Deadline outcome -- released only now, after the
    # terminal state is already confirmed above.
    release.set()
    time.sleep(0.05)
    assert service.get_run("run-1").state is RunState.FAILED
    assert service.get_run("run-1").failure_reason == "deadline_exceeded"
    worker.shutdown()


def test_submit_after_shutdown_force_publishes_failed_never_raises(tmp_path: Path) -> None:
    """R2-WU-04 (IR-P9-2-R1-06 fix): `submit()` genuinely never raises --
    a submission attempt after `shutdown()` force-publishes `FAILED`/
    `worker_shutdown` itself, since the caller already persisted this Run
    as `running` before ever reaching `submit()`."""

    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    worker.shutdown()

    worker.submit(
        service=service,
        run=run,
        deadline_ms=None,
        invoke=lambda: (RunState.COMPLETED, None, None),
    )
    result = service.get_result("run-1")
    assert result.run.state is RunState.FAILED
    assert result.run.failure_reason == "worker_shutdown"


def test_an_effectively_instantaneous_task_leaves_no_stale_in_flight_entry(
    tmp_path: Path,
) -> None:
    """R2-WU-04 (IR-P9-2-R1-06 fix): R1's own order (`executor.submit()`
    first, `_in_flight` dict insertion second) let a fast Fixture Task's
    own `finally`-block `pop()` race ahead of the registration and find
    nothing to remove -- leaving a stale entry for an already-finished Run
    forever. `request_cancel()` returning `False` after this Run is
    already terminal confirms no such entry survives."""

    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    worker.submit(
        service=service,
        run=run,
        deadline_ms=None,
        invoke=lambda: (RunState.COMPLETED, None, None),
    )
    _wait_until_terminal(service, "run-1")
    assert worker.request_cancel("run-1") is False
    worker.shutdown()


def test_a_cancelled_run_queued_behind_another_never_has_its_actor_invoked(
    tmp_path: Path,
) -> None:
    """R3-WU-03 (IR-P9-2-R2-06 MAJOR fix): Run A occupies the single
    worker thread; Run B is submitted (and queued) behind it; Run B is
    User-Cancelled WHILE still queued (before Run A ever releases); Run A
    then finishes. Run B's own Actor `invoke()` must NEVER be called --
    genuine Call 0, not merely a Late-Result its own eventual publish
    would have been rejected as."""

    service = _service(tmp_path)
    run_a = _plan_and_run(service)
    run_b = _start_run(service, run_id="run-2")
    worker = ExperimentRunWorker()

    a_release = threading.Event()

    def _slow_a() -> tuple[RunState, dict[str, object] | None, str | None]:
        a_release.wait(timeout=2.0)
        return (RunState.COMPLETED, {"which": "a"}, None)

    b_invoked = threading.Event()

    def _b_invoke() -> tuple[RunState, dict[str, object] | None, str | None]:
        b_invoked.set()
        return (RunState.COMPLETED, {"which": "b"}, None)

    worker.submit(service=service, run=run_a, deadline_ms=None, invoke=_slow_a)
    worker.submit(service=service, run=run_b, deadline_ms=None, invoke=_b_invoke)
    # Run B is now queued behind Run A on the single-worker Executor --
    # Cancel it while it is still genuinely queued (Run A has not
    # released yet).
    time.sleep(0.05)
    assert service.get_run("run-2").state is RunState.RUNNING
    service.cancel_run("run-2")

    a_release.set()
    _wait_until_terminal(service, "run-1")
    # Give the Executor a moment to actually dequeue and (attempt to)
    # run Run B's own Task after Run A releases.
    time.sleep(0.1)
    assert b_invoked.is_set() is False
    assert service.get_run("run-2").state is RunState.CANCELLED
    worker.shutdown()


def test_a_queued_futures_successful_cancel_cleans_up_in_flight_immediately(
    tmp_path: Path,
) -> None:
    """R4-WU-03 (Handoff R4 SS6.1/6.4): `request_cancel()` on a Run that is
    STILL genuinely queued (Run A occupies the single worker thread; this
    Run has never started) succeeds `Future.cancel()` -- `_task()` will now
    NEVER run for it, so its own `finally: self._in_flight.pop(...)`
    cleanup never fires either. Without R4-WU-03's own fix, this leaves a
    stale `_in_flight` entry behind, and a SECOND `request_cancel()` for
    the same, already-Terminal `run_id` would incorrectly still report
    `True`. The fix cleans up immediately, at the point `Future.cancel()`
    itself is learned to have succeeded -- a second call correctly reports
    `False`."""

    service = _service(tmp_path)
    run_a = _plan_and_run(service)
    run_b = _start_run(service, run_id="run-2")
    worker = ExperimentRunWorker()

    a_release = threading.Event()

    def _slow_a() -> tuple[RunState, dict[str, object] | None, str | None]:
        a_release.wait(timeout=2.0)
        return (RunState.COMPLETED, {"which": "a"}, None)

    b_invoked = threading.Event()

    def _b_invoke() -> tuple[RunState, dict[str, object] | None, str | None]:
        b_invoked.set()
        return (RunState.COMPLETED, {"which": "b"}, None)

    worker.submit(service=service, run=run_a, deadline_ms=None, invoke=_slow_a)
    worker.submit(service=service, run=run_b, deadline_ms=None, invoke=_b_invoke)
    time.sleep(0.05)
    # Run B is still genuinely queued behind Run A -- `Future.cancel()`
    # inside `request_cancel()` below succeeds.
    assert worker.request_cancel("run-2") is True
    service.cancel_run("run-2")

    # The FIX under test: the successful cancel above must have already,
    # immediately, popped Run B's own `_in_flight` entry -- a second call
    # for the same `run_id` must report `False`, never a stale `True`.
    assert worker.request_cancel("run-2") is False

    a_release.set()
    _wait_until_terminal(service, "run-1")
    time.sleep(0.1)
    assert b_invoked.is_set() is False
    assert service.get_run("run-2").state is RunState.CANCELLED
    worker.shutdown()


def test_a_deadline_exceeded_run_queued_behind_another_never_has_its_actor_invoked(
    tmp_path: Path,
) -> None:
    """R3-WU-03 (IR-P9-2-R2-06 MAJOR fix): same scenario as the Cancel
    variant above, but Run B reaches its own Deadline WHILE still queued
    behind Run A -- Run B's Actor must still never be invoked once the
    Executor gets to it."""

    service = _service(tmp_path)
    run_a = _plan_and_run(service)
    run_b = _start_run(service, run_id="run-2")
    worker = ExperimentRunWorker()

    a_release = threading.Event()

    def _slow_a() -> tuple[RunState, dict[str, object] | None, str | None]:
        a_release.wait(timeout=2.0)
        return (RunState.COMPLETED, {"which": "a"}, None)

    b_invoked = threading.Event()

    def _b_invoke() -> tuple[RunState, dict[str, object] | None, str | None]:
        b_invoked.set()
        return (RunState.COMPLETED, {"which": "b"}, None)

    worker.submit(service=service, run=run_a, deadline_ms=None, invoke=_slow_a)
    worker.submit(service=service, run=run_b, deadline_ms=30, invoke=_b_invoke)
    # Run B's own 30ms Deadline elapses while it is still queued behind
    # Run A (which is held open well past that).
    time.sleep(0.15)
    assert service.get_run("run-2").state is RunState.FAILED
    assert service.get_run("run-2").failure_reason == "deadline_exceeded"
    # R4-WU-03: `_on_deadline()`'s own successful `Future.cancel()` (Run B
    # was still genuinely queued) must have already, immediately, popped
    # its `_in_flight` entry -- `request_cancel()` for this same,
    # already-Terminal `run_id` must report `False`, never a stale `True`.
    assert worker.request_cancel("run-2") is False

    a_release.set()
    _wait_until_terminal(service, "run-1")
    time.sleep(0.1)
    assert b_invoked.is_set() is False
    # R5-WU-04 (Controller IR-P9-2-R4-04 fix, Handoff R5 SS6.5): the same
    # no-residual-entry guarantee, re-confirmed AFTER `shutdown()` itself
    # returns -- not only in the instant right after the Deadline fired.
    finished = worker.shutdown(timeout=2.0)
    assert finished is True
    assert worker.request_cancel("run-2") is False
    assert b_invoked.is_set() is False


def test_a_queued_run_cancelled_before_shutdown_leaves_no_residual_entry_after_shutdown(
    tmp_path: Path,
) -> None:
    """R5-WU-04 (Controller IR-P9-2-R4-04 MODERATE fix, Handoff R5 SS6):
    the existing queued-Cancel Hard Asserts above all check state
    immediately after the Cancel itself -- none of them go on to call
    `shutdown()` and re-check afterward. This Test follows the Handoff's
    own exact sequence: Run A occupies the Worker; Run B is Queued behind
    it; Run B is Cancelled WHILE still queued (a genuine `Future.cancel()`
    success); Run A is released; the Worker is THEN shut down; and only
    AFTER `shutdown()` returns are Run B's own Actor-Call-0, Terminal
    State, and `request_cancel(run_b) is False` all (re-)asserted --
    proving no residual `_in_flight`/Timer entry survives a full
    Shutdown, not merely the instant right after the Cancel."""

    service = _service(tmp_path)
    run_a = _plan_and_run(service)
    run_b = _start_run(service, run_id="run-2")
    worker = ExperimentRunWorker()

    a_release = threading.Event()

    def _slow_a() -> tuple[RunState, dict[str, object] | None, str | None]:
        a_release.wait(timeout=2.0)
        return (RunState.COMPLETED, {"which": "a"}, None)

    b_invoked = threading.Event()

    def _b_invoke() -> tuple[RunState, dict[str, object] | None, str | None]:
        b_invoked.set()
        return (RunState.COMPLETED, {"which": "b"}, None)

    worker.submit(service=service, run=run_a, deadline_ms=None, invoke=_slow_a)
    worker.submit(service=service, run=run_b, deadline_ms=None, invoke=_b_invoke)
    time.sleep(0.05)
    # Run B is still genuinely queued behind Run A -- this Cancel's own
    # `Future.cancel()` succeeds.
    assert worker.request_cancel("run-2") is True
    service.cancel_run("run-2")

    a_release.set()
    _wait_until_terminal(service, "run-1")

    finished = worker.shutdown(timeout=2.0)

    # Every assertion below runs strictly AFTER `shutdown()` has returned.
    assert finished is True
    assert b_invoked.is_set() is False
    assert service.get_run("run-2").state is RunState.CANCELLED
    assert worker.request_cancel("run-2") is False


def test_lease_is_held_only_during_the_actual_invoke_call(tmp_path: Path) -> None:
    """R3-WU-01 (Handoff R3 SS4.2 Option A): the Lease is acquired
    immediately before `invoke()` and released in a `finally` immediately
    after -- never for the Run's whole Queued-to-Terminal lifetime."""

    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    lease = CountingLease()
    observed_held_during_invoke: list[bool] = []

    def _invoke() -> tuple[RunState, dict[str, object] | None, str | None]:
        observed_held_during_invoke.append(lease.is_held())
        return (RunState.COMPLETED, None, None)

    assert lease.is_held() is False
    worker.submit(service=service, run=run, deadline_ms=None, invoke=_invoke, lease=lease)
    _wait_until_terminal(service, "run-1")
    assert observed_held_during_invoke == [True]
    assert lease.is_held() is False
    assert worker.shutdown(timeout=2.0) is True
    assert lease.acquire_count == 1
    assert lease.release_count == 1


def test_lease_is_released_even_when_the_actor_raises(tmp_path: Path) -> None:
    """The Lease's own release must be Exactly-once and unconditional --
    an Actor exception must never leave it stuck held."""

    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    lease = CountingLease()

    def _boom() -> tuple[RunState, dict[str, object] | None, str | None]:
        raise ValueError("actor exploded")

    worker.submit(service=service, run=run, deadline_ms=None, invoke=_boom, lease=lease)
    _wait_until_terminal(service, "run-1")
    assert lease.is_held() is False
    assert worker.shutdown(timeout=2.0) is True
    assert lease.acquire_count == 1
    assert lease.release_count == 1


def test_failed_outcome_releases_the_lease_exactly_once(tmp_path: Path) -> None:
    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    lease = CountingLease()

    worker.submit(
        service=service,
        run=run,
        deadline_ms=None,
        invoke=lambda: (RunState.FAILED, None, "typed_failure"),
        lease=lease,
    )
    _wait_until_terminal(service, "run-1")
    assert worker.shutdown(timeout=2.0) is True
    assert service.get_run("run-1").state is RunState.FAILED
    assert lease.acquire_count == lease.release_count == 1
    assert lease.try_acquire_mutation() is True
    lease.release_mutation()


def test_deadline_and_shutdown_paths_release_the_lease_once_and_mutations_recover(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    run = _plan_and_run(service, budget=ExperimentPlanBudget(deadline_ms=50))
    worker = ExperimentRunWorker()
    lease = CountingLease()
    actor_entered = threading.Event()
    cancel_release = threading.Event()

    def _slow() -> tuple[RunState, dict[str, object] | None, str | None]:
        actor_entered.set()
        cancel_release.wait(timeout=2.0)
        # Let the Timer's terminal publish win before returning a late result.
        time.sleep(0.05)
        return (RunState.COMPLETED, None, None)

    worker.submit(
        service=service,
        run=run,
        deadline_ms=50,
        invoke=_slow,
        cancel=cancel_release.set,
        lease=lease,
    )
    assert actor_entered.wait(timeout=1.0) is True
    _wait_until_terminal(service, "run-1")
    assert service.get_run("run-1").failure_reason == "deadline_exceeded"
    assert worker.shutdown(timeout=2.0) is True
    assert lease.acquire_count == lease.release_count == 1
    assert lease.try_acquire_mutation() is True
    lease.release_mutation()


def test_shutdown_cancel_hook_releases_the_lease_once_and_mutations_recover(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    lease = CountingLease()
    actor_entered = threading.Event()
    shutdown_release = threading.Event()

    def _until_shutdown() -> tuple[RunState, dict[str, object] | None, str | None]:
        actor_entered.set()
        shutdown_release.wait(timeout=2.0)
        return (RunState.FAILED, None, "shutdown_cancelled_actor")

    worker.submit(
        service=service,
        run=run,
        deadline_ms=None,
        invoke=_until_shutdown,
        cancel=shutdown_release.set,
        lease=lease,
    )
    assert actor_entered.wait(timeout=1.0) is True
    assert worker.shutdown(timeout=2.0) is True
    assert service.get_run("run-1").state is RunState.FAILED
    assert lease.acquire_count == lease.release_count == 1
    assert lease.try_acquire_mutation() is True
    lease.release_mutation()


def test_shutdown_while_waiting_behind_a_mutation_is_call_zero_and_releases_once(
    tmp_path: Path,
) -> None:
    class WaitObservingLease(CountingLease):
        def __init__(self) -> None:
            super().__init__()
            self.acquire_started = threading.Event()

        def acquire(self) -> None:
            self.acquire_started.set()
            super().acquire()

    service = _service(tmp_path)
    run = _plan_and_run(service)
    worker = ExperimentRunWorker()
    lease = WaitObservingLease()
    invoked = threading.Event()
    assert lease.try_acquire_mutation() is True

    def _invoke() -> tuple[RunState, dict[str, object] | None, str | None]:
        invoked.set()
        return (RunState.COMPLETED, None, None)

    worker.submit(
        service=service,
        run=run,
        deadline_ms=None,
        invoke=_invoke,
        lease=lease,
    )
    assert lease.acquire_started.wait(timeout=1.0) is True
    # The Worker is blocked behind the earlier mutation; shutdown cannot
    # finish until that mutation releases, but it must prevent Actor entry.
    assert worker.shutdown(timeout=0.05) is False
    lease.release_mutation()

    _wait_until_terminal(service, "run-1")
    deadline = time.monotonic() + 1.0
    while worker.request_cancel("run-1") and time.monotonic() < deadline:
        time.sleep(0.01)
    assert worker.request_cancel("run-1") is False
    assert invoked.is_set() is False
    assert service.get_run("run-1").state is RunState.FAILED
    assert service.get_run("run-1").failure_reason == "worker_shutdown"
    assert lease.acquire_count == lease.release_count == 1
    assert lease.try_acquire_mutation() is True
    lease.release_mutation()
