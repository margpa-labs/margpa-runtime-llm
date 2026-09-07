"""Experiment Configuration Lease (Phase 9-2 R3, WU-01, Option A).

Handoff R3 SS4.2 Option A ("Explicit User-Gated Live Match + Lease"):
"一致後、実行中は関連Settings/Provider変更をLeaseで409拒否する。Terminal
/Cancel/Deadline後にLeaseをExactly-once解放する". This is the Lease --
a small, process-local, in-memory mutex the Web layer checks before letting
any ordinary Chat Settings-mutation route (Judge/Repair/Recording Mode,
Provider Selection, Runtime Model context/tokens/switch, the Guard/Main-
Governance Configuration Preview->Apply CAS path) proceed. It never touches
any Controller's own contract -- `web/app.py`'s existing `secure_requests`
middleware is the ONE place that reads `is_held()`, and `application.
run_worker.ExperimentRunWorker` is the ONE place that calls `acquire()`/
`release()`, both purely additive to code that already exists.

Held ONLY for the duration of one real Production Turn's own `invoke()`
call (acquired immediately before, released in a `finally` immediately
after, inside `ExperimentRunWorker._task()`) -- never for a Run's whole
Queued-to-Terminal lifetime, and never for a Fixture Run at all (Fixture
never reads or depends on Live Configuration). Since `ExperimentRunWorker`
itself is a single-worker-thread Executor, at most one real Production
Turn -- and therefore at most one Lease holder -- ever exists at a time;
this class's own `threading.Lock` exists to make `is_held()` safe to read
concurrently from an HTTP request's own thread while that is true, not to
arbitrate between multiple simultaneous acquirers (there are never any)."""

from __future__ import annotations

import threading


class ExperimentConfigurationLease:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._held = False

    def acquire(self) -> None:
        with self._lock:
            self._held = True

    def release(self) -> None:
        with self._lock:
            self._held = False

    def is_held(self) -> bool:
        with self._lock:
            return self._held
