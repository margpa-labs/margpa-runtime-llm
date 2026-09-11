"""Atomic Experiment/Settings configuration arbitration (Phase 9-2).

Handoff R3 SS4.2 Option A ("Explicit User-Gated Live Match + Lease"):
"一致後、実行中は関連Settings/Provider変更をLeaseで409拒否する。Terminal
/Cancel/Deadline後にLeaseをExactly-once解放する". This is the Lease --
a small, process-local, in-memory read/write arbitration the Web layer holds while letting
any ordinary Chat Settings-mutation route (Judge/Repair/Recording Mode,
Provider Selection, Runtime Model context/tokens/switch, the Guard/Main-
Governance Configuration Preview->Apply CAS path) proceed. It never touches
any Controller's own contract -- `web/app.py`'s existing `secure_requests`
middleware is the ONE place that calls `try_acquire_mutation()`/
`release_mutation()`, and `application.run_worker.ExperimentRunWorker`
is the ONE place that calls `acquire()`/`release()`.

Held ONLY for the duration of one real Production Turn's own `invoke()`
call (acquired immediately before, released in a `finally` immediately
after, inside `ExperimentRunWorker._task()`) -- never for a Run's whole
Queued-to-Terminal lifetime, and never for a Fixture Run at all. A gated
mutation that wins first remains counted through its whole HTTP handling;
the Experiment waits. Once an Experiment is held or waiting, newly arriving
gated mutations are rejected at Call 0, preventing starvation and TOCTOU."""

from __future__ import annotations

import threading


class ExperimentConfigurationLease:
    def __init__(self) -> None:
        self._condition = threading.Condition()
        self._experiment_held = False
        self._experiment_waiters = 0
        self._mutations_in_flight = 0

    def acquire(self) -> None:
        """Wait until all earlier mutations finish, then hold exclusively."""

        with self._condition:
            self._experiment_waiters += 1
            try:
                while self._experiment_held or self._mutations_in_flight > 0:
                    self._condition.wait()
                self._experiment_held = True
            finally:
                self._experiment_waiters -= 1

    def release(self) -> None:
        with self._condition:
            if not self._experiment_held:
                raise RuntimeError("Experiment Configuration Lease is not held")
            self._experiment_held = False
            self._condition.notify_all()

    def try_acquire_mutation(self) -> bool:
        """Atomically admit one gated mutation or reject it at Call 0.

        Multiple ordinary mutations may overlap exactly as before. They
        collectively exclude the Experiment's protected final-snapshot and
        Actor interval; a waiting Experiment excludes new mutations so it
        can make progress as soon as earlier mutations complete.
        """

        with self._condition:
            if self._experiment_held or self._experiment_waiters > 0:
                return False
            self._mutations_in_flight += 1
            return True

    def release_mutation(self) -> None:
        with self._condition:
            if self._mutations_in_flight <= 0:
                raise RuntimeError("No Configuration mutation lease is held")
            self._mutations_in_flight -= 1
            if self._mutations_in_flight == 0:
                self._condition.notify_all()

    def is_held(self) -> bool:
        with self._condition:
            return self._experiment_held
