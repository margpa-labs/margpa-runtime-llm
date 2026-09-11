"""Experiment Run Worker (Phase 9-2 R1 WU-05; R2-WU-04 convergence).

Handoff R1 SS8: "Run開始APIは`running`を返し、実行をTracked Workerへ渡す".
`ExperimentRunWorker` is that Tracked Worker -- a single-threaded (never
concurrent, matching this Program's own "実ModelはMain Qwen/Gemma/Qwen3Guard
だけを逐次" discipline) background executor that runs one Variant's Actor
Call off the calling (HTTP request) thread, then publishes the real outcome
back through the same `ExperimentService.publish_result()` every other
publisher already uses -- Actor exceptions become `FAILED`, and a
`request_cancel()` reaching an in-flight Run's own `cancel` hook is a
best-effort attempt to interrupt a real, possibly slow, Production Turn
(Fixture invocations are effectively instantaneous, so their own `cancel`
hook is always a no-op -- nothing to interrupt).

R2-WU-04 (IR-P9-2-R1-06 fix) changes three things from R1:

1. Deadline now binds the WHOLE Run, not just the instant before `invoke()`
   is called: a `threading.Timer`, armed for the Run's own remaining budget,
   runs concurrently with the (possibly slow, blocking) `invoke()` call on
   the single worker thread -- if it fires first, it calls the Run's own
   `cancel` hook (best-effort, to actually try to unblock the worker thread)
   and force-publishes `FAILED`/`deadline_exceeded`. Whichever of the Timer
   or the eventual real `invoke()` result reaches `ExperimentService.
   publish_result()` first wins (that method's own generation/terminal
   check, `experiment_service.py`); the other's publish attempt is rejected
   as a Late Result -- never a double-publish, never silently dropped.
2. `submit()` genuinely never raises now: a submit attempt after `shutdown()`
   immediately force-publishes `FAILED`/`worker_shutdown` itself (the
   Run was already persisted `running` by the caller before `submit()` is
   ever reached) instead of raising `RuntimeError` and leaving that
   responsibility -- and a `running` Run with nothing to resolve it -- to
   the caller.
3. The in-flight registration itself happens BEFORE the Task is handed to
   the executor, both under the same lock acquisition -- R1's own order
   (`executor.submit()` first, dict insertion second) let an
   effectively-instantaneous Fixture Task's own `finally`-block `pop()`
   race ahead of the registration and find nothing to remove, leaving a
   stale, never-cleaned `_in_flight` entry for an already-finished Run
   behind forever.

R3-WU-03 (IR-P9-2-R2-06 MAJOR fix) adds one more guarantee: a Run that
reaches a Terminal state (`Cancel`/Deadline) WHILE still queued behind
another in-flight Run on this single-worker Executor must never have its
own Actor called at all once the Executor finally gets to it. `_task()`
now re-reads this Run's own CURRENT persisted state, fresh, the instant it
starts running -- before `invoke()` is ever called -- and short-circuits
(Actor Call 0) if it is already Terminal. `submit()` additionally makes a
best-effort attempt to cancel the underlying `Future` itself at Cancel/
Deadline time (effective only while the Task is still genuinely queued,
never once it has started) -- a cheap, purely additional layer on top of
the authoritative check, never a replacement for it (a `Future.cancel()`
racing the Executor's own dequeue can always lose).

R3-WU-01 also threads an optional `ExperimentConfigurationLease` through
`submit()`: acquired immediately before `invoke()` (only once the
authoritative Terminal Check above has passed) and released in a
`finally` immediately after -- never held for this Run's whole Queued-to-
Terminal lifetime, only for the real Actor Call's own duration."""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import UTC, datetime

from ..domain.errors import ExperimentCoreError, ExperimentCoreErrorCode
from ..domain.run import RunState, VariantRun, is_terminal
from .configuration_lease import ExperimentConfigurationLease
from .experiment_service import ExperimentService

_logger = logging.getLogger(__name__)

RunInvocation = Callable[[], tuple[RunState, dict[str, object] | None, str | None]]
"""Returns `(target_state, raw_evidence, failure_reason)` -- the Worker
never inspects the Actor's own internals, only this already-resolved
outcome triple."""


_TERMINAL_PUBLISH_CONFLICT_CODES = frozenset(
    {
        ExperimentCoreErrorCode.LATE_RESULT_REJECTED,
        ExperimentCoreErrorCode.TERMINAL_ALREADY_PUBLISHED,
    }
)


def _is_harmless_terminal_publish_conflict(
    *, service: ExperimentService, run_id: str, error: ExperimentCoreError
) -> bool:
    """Only a known publish race whose winner is durably Terminal is harmless."""

    if error.code not in _TERMINAL_PUBLISH_CONFLICT_CODES:
        return False
    try:
        return is_terminal(service.get_run(run_id).state)
    except ExperimentCoreError:
        return False


@dataclass(slots=True)
class _InFlightRun:
    cancel: Callable[[], None]
    timer: threading.Timer | None
    future: Future[None] | None = None
    """R3-WU-03: a best-effort cancellation handle -- `Future.cancel()`
    only ever succeeds while the Task is still genuinely queued (never
    started) on this single-worker Executor. Set AFTER this same entry is
    already registered in `_in_flight` (see `submit()`), never before --
    mutated in place rather than passed at construction so the R2-WU-04
    registration-before-submit ordering (dict insert, THEN `executor.
    submit()`) is preserved exactly."""


class ExperimentRunWorker:
    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="experiment-run")
        self._lock = threading.Lock()
        self._in_flight: dict[str, _InFlightRun] = {}
        self._shutdown = False

    def _cleanup_in_flight_if_cancelled_while_queued(
        self, run_id: str, entry: _InFlightRun | None
    ) -> None:
        """R4-WU-03 (Handoff R4 SS6.1): `Future.cancel()` succeeding means
        `_task()` will now NEVER run for this Run -- its own `finally:
        self._in_flight.pop(...)` cleanup therefore never fires either,
        which would otherwise leave a stale `_in_flight` entry (and an
        irrelevant Timer reference) behind forever, and would make a LATER
        `request_cancel()` for this same, already-Terminal `run_id`
        incorrectly report `True` again. Called from both `_on_deadline()`
        (inside `submit()`) and `request_cancel()` below, right after
        either learns a genuinely-queued Future's cancellation actually
        took effect. Safe even if both race to cancel the same Future:
        `dict.pop(..., None)` and `Timer.cancel()` are both idempotent, so
        whichever caller gets here first (or both) leaves the same,
        correct end state -- and a `Future` already running or finished by
        the time this runs simply reports `cancel() -> False`, leaving
        `_task()`'s own `finally` as the sole (unchanged) owner of
        cleanup for it."""

        if entry is None or entry.future is None:
            return
        if not entry.future.cancel():
            return
        with self._lock:
            self._in_flight.pop(run_id, None)
        if entry.timer is not None:
            entry.timer.cancel()

    def submit(
        self,
        *,
        service: ExperimentService,
        run: VariantRun,
        deadline_ms: int | None,
        invoke: RunInvocation,
        cancel: Callable[[], None] | None = None,
        lease: ExperimentConfigurationLease | None = None,
    ) -> None:
        """Schedules exactly one Run's Actor Call. Never raises -- a
        rejection here (the Worker is already shut down) is itself
        force-published as a `FAILED` Result, never left as a `running`
        Run with nothing left to resolve it.

        R3-WU-01: `lease`, when given, is acquired immediately before
        `invoke()` (only once `_task()`'s own authoritative Terminal
        Check below has passed) and released in a `finally` immediately
        after -- never for this Run's whole Queued-to-Terminal lifetime,
        only for the real Actor Call's own duration. Pass `None` for a
        Fixture invocation, which never reads or depends on Live
        Configuration."""

        cancel_hook = cancel or (lambda: None)

        def _publish_actor_failure(failure_reason: str) -> None:
            try:
                service.publish_result(
                    run.run_id,
                    generation=run.generation,
                    target_state=RunState.FAILED,
                    failure_reason=failure_reason,
                )
            except ExperimentCoreError as exc:
                if not _is_harmless_terminal_publish_conflict(
                    service=service, run_id=run.run_id, error=exc
                ):
                    raise

        def _on_deadline() -> None:
            cancel_hook()
            with self._lock:
                entry = self._in_flight.get(run.run_id)
            # R3-WU-03: best-effort -- succeeds only if `_task()` has not
            # started yet (still queued behind another in-flight Run); a
            # cheap additional layer on top of `_task()`'s own
            # authoritative Terminal Check, never a replacement for it.
            # R4-WU-03: and if it DOES succeed, clean up `_in_flight`/Timer
            # immediately -- `_task()` will now never run to do it itself.
            self._cleanup_in_flight_if_cancelled_while_queued(run.run_id, entry)
            try:
                service.publish_result(
                    run.run_id,
                    generation=run.generation,
                    target_state=RunState.FAILED,
                    failure_reason="deadline_exceeded",
                )
            except ExperimentCoreError as exc:
                # The real `invoke()` result (or a `cancel_run()`) already
                # published a Terminal state first -- this Deadline fire
                # lost the race, and that is fine: at most one Terminal
                # publish for this Run ever wins.
                if not _is_harmless_terminal_publish_conflict(
                    service=service, run_id=run.run_id, error=exc
                ):
                    raise

        def _task(timer: threading.Timer | None) -> None:
            try:
                # R3-WU-03 (IR-P9-2-R2-06 MAJOR fix): re-reads this Run's
                # OWN current persisted state, fresh, the instant this
                # Task actually starts running -- if a Cancel or Deadline
                # already reached it WHILE it was still queued behind
                # another in-flight Run on this single-worker Executor,
                # this is genuine Actor Call 0: `invoke()` (which for a
                # Production Run means a real Model Call and real Resource
                # consumption) must never run at all, and the outcome was
                # already published by whichever Publisher reached it
                # first -- nothing left for this Task to do.
                if is_terminal(service.get_run(run.run_id).state):
                    return
                with self._lock:
                    shutdown_requested = self._shutdown
                if shutdown_requested:
                    _publish_actor_failure("worker_shutdown")
                    return
                if lease is not None:
                    lease.acquire()
                try:
                    # `lease.acquire()` may have waited behind an earlier
                    # Settings mutation. Cancel/Deadline can win during
                    # that wait; re-read under the newly acquired lease so
                    # a now-Terminal Run remains genuine Actor Call 0.
                    if is_terminal(service.get_run(run.run_id).state):
                        return
                    with self._lock:
                        shutdown_requested = self._shutdown
                    if shutdown_requested:
                        _publish_actor_failure("worker_shutdown")
                        return
                    try:
                        target_state, raw_evidence, failure_reason = invoke()
                    except ExperimentCoreError as exc:
                        _logger.warning(
                            "experiment run worker: Actor invocation raised a domain error "
                            "for run_id=%r code=%s",
                            run.run_id,
                            exc.code.value,
                        )
                        _publish_actor_failure(f"actor_domain_error:{exc.code.value}")
                        return
                    except Exception as exc:
                        _logger.warning(
                            "experiment run worker: Actor invocation raised for run_id=%r",
                            run.run_id,
                            exc_info=True,
                        )
                        _publish_actor_failure(f"actor_exception:{exc.__class__.__name__}")
                        return
                finally:
                    if lease is not None:
                        lease.release()
                try:
                    service.publish_result(
                        run.run_id,
                        generation=run.generation,
                        target_state=target_state,
                        raw_evidence=raw_evidence,
                        failure_reason=failure_reason,
                    )
                except ExperimentCoreError as exc:
                    if not _is_harmless_terminal_publish_conflict(
                        service=service, run_id=run.run_id, error=exc
                    ):
                        raise
            finally:
                if timer is not None:
                    timer.cancel()
                with self._lock:
                    self._in_flight.pop(run.run_id, None)

        with self._lock:
            if self._shutdown:
                try:
                    service.publish_result(
                        run.run_id,
                        generation=run.generation,
                        target_state=RunState.FAILED,
                        failure_reason="worker_shutdown",
                    )
                except ExperimentCoreError:
                    pass
                return

            timer: threading.Timer | None = None
            if deadline_ms is not None:
                started = (
                    datetime.fromisoformat(run.started_at)
                    if run.started_at is not None
                    else datetime.now(UTC)
                )
                elapsed_ms = (datetime.now(UTC) - started).total_seconds() * 1000
                remaining_seconds = (deadline_ms - elapsed_ms) / 1000
                if remaining_seconds <= 0:
                    # R1's own fast path, preserved: a Deadline already
                    # exceeded before this Run was even scheduled is
                    # genuine Actor Call 0 -- `invoke()` must never run at
                    # all, not merely "probably lose a race" against a
                    # zero-or-negative Timer delay (`threading.Timer`
                    # gives no such guarantee: a `0`-second Timer and this
                    # Task's own near-instant `_task()` call are a real,
                    # non-deterministic race on a warm Thread Pool).
                    try:
                        service.publish_result(
                            run.run_id,
                            generation=run.generation,
                            target_state=RunState.FAILED,
                            failure_reason="deadline_exceeded",
                        )
                    except ExperimentCoreError:
                        pass
                    return
                # R2-WU-04: armed for the Run's own REMAINING budget (never
                # re-armed for the full `deadline_ms` again) and started
                # BEFORE the Task is handed to the executor -- it runs
                # concurrently with `invoke()` on its own Thread, so a
                # `deadline_ms` exceeded WHILE the single worker thread is
                # still blocked inside a slow real Production Turn is
                # caught too, not only one exceeded before `invoke()`
                # starts.
                timer = threading.Timer(remaining_seconds, _on_deadline)
                timer.daemon = True

            entry = _InFlightRun(cancel=cancel_hook, timer=timer)
            self._in_flight[run.run_id] = entry
            # R3-WU-03: the `Future` handle is attached to the ALREADY-
            # registered entry, still under this same lock -- the R2-WU-04
            # registration-before-submit ordering (dict insert strictly
            # before `executor.submit()`) is unchanged; this only adds a
            # cancellation handle a Cancel/Deadline can look up afterward.
            entry.future = self._executor.submit(_task, timer)
            if timer is not None:
                timer.start()

    def request_cancel(self, run_id: str) -> bool:
        """Best-effort: calls the in-flight Run's own `cancel` hook if one
        is registered, and (R3-WU-03) attempts to cancel its `Future` too
        -- effective only while the Task is still genuinely queued, never
        once it has started (in which case this is a harmless no-op; the
        authoritative Terminal Check inside `_task()` itself is what
        actually guarantees Actor Call 0 for an already-Cancelled queued
        Run). Returns `False` (never raises) when the Run is already
        finished or was never Worker-submitted -- the caller (the Web
        route) still separately transitions the persisted Run to
        `CANCELLED` via `ExperimentService.cancel_run()` regardless of
        this method's return value."""

        with self._lock:
            entry = self._in_flight.get(run_id)
        if entry is None:
            return False
        entry.cancel()
        # R4-WU-03: if this Run was still genuinely queued (never started),
        # `Future.cancel()` succeeding means `_task()` -- and therefore its
        # own `finally` cleanup -- will now never run for it; clean up the
        # `_in_flight` entry and Timer here instead, so a LATER call for
        # this same `run_id` correctly reports `False`, never a stale
        # `True` for an already-Terminal Run.
        self._cleanup_in_flight_if_cancelled_while_queued(run_id, entry)
        return True

    def shutdown(self, *, timeout: float | None = None) -> bool:
        """Stops accepting new Runs, best-effort-cancels every currently
        in-flight one (and its own Deadline Timer, if any), then waits up
        to `timeout` seconds (or forever, if `None`) for the underlying
        Thread to actually finish. Returns whether it finished within
        `timeout` -- like `RoleProviderLifecycleManager.shutdown()`/
        `TrackedStageWorkerRegistry.shutdown()` elsewhere in this codebase,
        a Python thread genuinely blocked inside a real Model Call cannot
        be forcibly killed, so a `False` here means the caller should treat
        this as an unclean shutdown (never proceed to unload a Model
        backend this Worker might still be using) rather than assume the
        Thread is actually gone."""

        with self._lock:
            self._shutdown = True
            in_flight = list(self._in_flight.values())
        for entry in in_flight:
            entry.cancel()
            if entry.timer is not None:
                entry.timer.cancel()
        if timeout is None:
            self._executor.shutdown(wait=True, cancel_futures=False)
            return True
        finished = threading.Event()

        def _join() -> None:
            self._executor.shutdown(wait=True, cancel_futures=False)
            finished.set()

        threading.Thread(target=_join, daemon=True, name="experiment-run-worker-shutdown").start()
        return finished.wait(timeout=timeout)
