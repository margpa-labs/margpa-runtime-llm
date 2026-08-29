"""Real, preemptive per-Stage Deadline Owner (P6-RR-R14-WU-001..005, Post-
Claude Independent Review Rework, resolves P6-CODEX-075).

Shared between `judge_live_integration.py` (Judge Inference) and
`repair_live_integration.py` (Repair Generation, Rejudge) — the three real
Model Calls a Stage Budget must bound — kept in its own module rather than
either of those two so neither creates a circular import on the other.
"""

from __future__ import annotations

import contextlib
import threading
from collections.abc import Callable, Iterator

from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken


@contextlib.contextmanager
def stage_deadline(
    *, cancellation: CancellationToken, budget_ms: int
) -> Iterator[Callable[[], bool]]:
    """Starts a Timer that Cancels the shared Cancellation Token if THIS
    Stage's own Budget is exceeded while the Stage is still in flight —
    never only measuring elapsed time after the Stage has already
    returned (the previous "後検査" pattern this Rework replaces). Yields
    a Callable that reports whether this specific Timer (never an
    external Cancellation, e.g. Main-priority preemption) is what fired,
    so a caller can attribute the correct Failure Reason instead of
    always reporting the external-preemption reason. The Timer is always
    cancelled on exit — a Stage that finishes within Budget never fires
    it. `budget_ms <= 0` never starts a Timer (matches a Provider, e.g.
    Built-in, that performs no bounded work at all).

    Prompt Build and Decode are still never wrapped by this specific
    primitive: both are synchronous, in-thread CPU-bound calls with no
    Cancellation parameter and no I/O to interrupt — a Timer firing
    `cancellation.cancel()` from another Thread cannot preempt Python
    code already running synchronously in this one, a CPython-level
    constraint this primitive cannot work around. P6-RR-R18-WU-001..003
    (resolves P6-CODEX-081) gives those two Stages a real Terminal-owner
    boundary of their own instead — see `tracked_stage_worker.py`'s
    `run_tracked_stage()`, which runs the call on its own Thread and
    bounds the *caller's wait*, rather than trying to preempt the call
    itself.
    """
    exceeded = threading.Event()
    if budget_ms <= 0:
        yield exceeded.is_set
        return

    def _on_timeout() -> None:
        exceeded.set()
        cancellation.cancel()

    timer = threading.Timer(budget_ms / 1000, _on_timeout)
    timer.daemon = True
    timer.start()
    try:
        yield exceeded.is_set
    finally:
        timer.cancel()
