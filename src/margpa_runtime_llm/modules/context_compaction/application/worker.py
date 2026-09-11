"""Single-threaded background executor for Manual Compaction Attempts.

Deliberately simpler than `experiment.application.run_worker.
ExperimentRunWorker`: the Deterministic Extractive Builder never blocks on a
real Model/Network call (Model Call 0, in-process token counting only), so
there is no need for that Worker's Deadline-Timer-racing-a-blocking-call
machinery. What IS reused unchanged is its hard-won invariant: the in-flight
entry is registered BEFORE the Future is created, and removed in a
`finally` that fires whichever way the Task ends -- the exact ordering that
(this same project's own Phase 9-2 Rework history) prevents a stale
`_in_flight` entry surviving Cancel/Shutdown.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass


@dataclass(slots=True)
class _InFlightAttempt:
    future: Future[None] | None = None


class CompactionWorker:
    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="context-compaction")
        self._lock = threading.Lock()
        self._in_flight: dict[str, _InFlightAttempt] = {}
        self._shutdown = False

    def submit(self, attempt_id: str, fn: Callable[[], None]) -> bool:
        """Returns `False` (and never runs `fn`) once `shutdown()` has been
        called -- the caller is responsible for persisting a `failed`/
        `worker_shutdown` terminal Attempt state in that case, exactly like
        `ExperimentRunWorker.submit()`'s own post-shutdown contract."""

        def _task() -> None:
            try:
                fn()
            finally:
                with self._lock:
                    self._in_flight.pop(attempt_id, None)

        with self._lock:
            if self._shutdown:
                return False
            entry = _InFlightAttempt()
            self._in_flight[attempt_id] = entry
            entry.future = self._executor.submit(_task)
        return True

    def request_cancel(self, attempt_id: str) -> bool:
        """Best-effort: only succeeds while the Attempt is still genuinely
        queued (never started) on this single-worker Executor. A Cancel
        arriving once the Task has started relies on the Coordinator's own
        phase-boundary Cancel check inside the running pipeline, never on
        this method."""

        with self._lock:
            entry = self._in_flight.get(attempt_id)
        if entry is None or entry.future is None:
            return False
        cancelled = entry.future.cancel()
        if cancelled:
            with self._lock:
                self._in_flight.pop(attempt_id, None)
        return cancelled

    def shutdown(self, *, timeout: float | None = None) -> bool:
        with self._lock:
            self._shutdown = True
            in_flight = list(self._in_flight.values())
        for entry in in_flight:
            if entry.future is not None:
                entry.future.cancel()
        if timeout is None:
            self._executor.shutdown(wait=True, cancel_futures=False)
            return True
        finished = threading.Event()

        def _join() -> None:
            self._executor.shutdown(wait=True, cancel_futures=False)
            finished.set()

        threading.Thread(
            target=_join, daemon=True, name="context-compaction-worker-shutdown"
        ).start()
        return finished.wait(timeout=timeout)
