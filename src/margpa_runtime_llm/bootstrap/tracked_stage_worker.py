"""Tracked Stage Worker (P6-RR-R18-WU-001..003, Post-Claude Independent
Review Rework, resolves P6-CODEX-081; extended P6-RR-R22, Post-Codex
Independent Review Rework, closes the rest of P6-CODEX-081).

`stage_deadline()` (`bootstrap/stage_deadline.py`) preemptively cancels a
Stage's own real Model Call by firing a shared `CancellationToken` from a
`threading.Timer` — that only works because the Model Call itself
cooperatively checks Cancellation. Prompt Build and Decode are genuinely
synchronous, non-I/O, CPU-bound Python calls with no Cancellation
parameter at all: a Timer firing from another Thread cannot preempt code
already running synchronously in this one (this is a Python/CPython
language-level constraint, not a design choice this module works around).

The only Terminal-owner boundary Python actually offers for that shape of
work is running it on its own Thread and having the *caller* stop
*waiting* at the Budget, rather than trying to stop the work itself. This
module is exactly that boundary: `run_tracked_stage()` submits `work` to a
dedicated single-use Thread and waits up to `budget_ms`. On Timeout it
returns immediately — the caller is never blocked past its own Budget —
but the background Thread is not (cannot safely be) killed; it keeps
running until it naturally finishes. The returned `TrackedStageOutcome.
future` is the caller's only handle onto that eventual completion — a
genuine "Late Publish rejection" is enforced simply by construction:
nothing in this module's own return path ever hands a Budget-exceeding
caller a result computed after its Timeout already fired, and nothing
here auto-publishes that late value anywhere else either.

P6-RR-R22 (resolves the rest of P6-CODEX-081): a bare `future.done()`
inspection by an interested caller was never actually wired to anything —
Codex's Independent Review found 0 Production callers that ever tracked
the `Future` a Timeout leaves behind, so a Cancellation-ignoring Prompt/
Decode Thread could keep running indefinitely while WebRuntime/Coordinator
Shutdown claimed Clean regardless. `TrackedStageWorkerRegistry` is this
Runtime's single Owner for every dispatched Worker: `run_tracked_stage()`
registers a Future with it (when a `registry` is supplied) the instant it
is submitted, and the Registry removes it again exactly once, via
`Future.add_done_callback` — the same callback fires whether the Thread
finishes normally, raises, or completes long after its own caller already
stopped waiting on Timeout (a "Late Complete"). `TrackedStageWorkerRegistry.
shutdown()` stops accepting new Stage submissions and Bounded-Joins every
still-tracked Worker; it returns `False` — never a false "Clean" claim —
if one or more Workers are still genuinely running once the bound expires.

P6-RR-R25 (Post-Codex Independent Review Rework, resolves P6-CODEX-088):
R22's own Admission was still a Check-to-Submit Race — `accepting_new_
work()`, `executor.submit(work)`, and `track(future)` were three
independent calls, each acquiring (or not) the Registry's Lock
separately. `shutdown()` could flip `_accepting` False and take its
Bounded-Join snapshot in the gap between the accepting-check passing and
the new Future actually being tracked, so `shutdown()` could genuinely
return `True` while a brand-new Worker — admitted a moment earlier —
started running completely outside that snapshot (Controller Probe A
reproduced exactly this: `shutdown_clean=True` with
`worker_started_after_shutdown=True`). `TrackedStageWorkerRegistry.
submit()` now performs the accepting-check, the Thread dispatch, and the
Registry registration as one atomic operation under a single acquisition
of this Registry's own Lock — the identical Lock `shutdown()` acquires to
flip `_accepting` and take its snapshot, so the two critical sections can
never interleave (see `submit()`'s own docstring for the full argument,
including why `add_done_callback` is deliberately registered *after*
that Lock is released, to avoid a same-Thread reentrant-Lock deadlock
when a Future happens to already be done by the time it is registered).
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class TrackedStageOutcome[T]:
    result: T | None
    timed_out: bool
    future: Future[T]


class TrackedStageWorkerRegistry:
    """P6-RR-R22 (resolves P6-CODEX-081): Lifecycle-owned Single Owner for
    every `run_tracked_stage()` background Thread this Runtime dispatches.
    One instance is shared for the Runtime's entire lifetime (mirrors
    `RequestCorrelationRegistry`'s own sharing model) — every Judge Run's
    Prompt Build and Decode Stage submissions register with the same
    instance, so `shutdown()` sees every Worker any Turn has ever
    dispatched, including one left running by a Turn whose own Budget
    already expired and moved on."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active: dict[int, Future[Any]] = {}
        self._next_key = 0
        self._accepting = True

    def accepting_new_work(self) -> bool:
        """`False` once `shutdown()` has been called — a caller must
        refuse to dispatch a *new* background Thread past this point
        (P6-RR-R22 contract item 1); an already-tracked, still-running
        Worker is unaffected and is instead Bounded-Joined by `shutdown()`
        itself."""
        with self._lock:
            return self._accepting

    def submit(self, *, work: Callable[[], Any]) -> Future[Any] | None:
        """Atomic Admission (P6-RR-R25, resolves P6-CODEX-088): the
        accepting-check, the Thread dispatch (`ThreadPoolExecutor.
        submit()`), and the Registry registration all happen under one
        acquisition of this Registry's own Lock — the identical Lock
        `shutdown()` acquires to flip `_accepting` False and take its
        Bounded-Join snapshot. A call here therefore either completes
        entirely *before* a concurrent `shutdown()`'s own critical section
        (the new Worker is unconditionally included in that Shutdown's
        snapshot) or observes `_accepting` already `False` and never
        dispatches `work` at all — never a third, in-between outcome
        where a Worker starts running outside of every snapshot Shutdown
        will ever take.

        Returns `None`, without ever invoking `work`, once Shutdown has
        already begun.

        `future.add_done_callback` is deliberately registered *after*
        this method's own Lock is released. `concurrent.futures.Future.
        add_done_callback` invokes its callback immediately, synchronously,
        on the calling Thread when the Future is already done at
        registration time — a real possibility here, since the backing
        pool Thread can finish `work` before this method's own `with
        self._lock:` block even exits. Registering the callback while
        still holding that Lock would let `_untrack`'s own `with self.
        _lock:` attempt to re-acquire an already-held, non-reentrant
        `threading.Lock` from that same Thread — a guaranteed deadlock
        (P6-RR-R25 contract item 5). Releasing the Lock first means the
        callback, however immediate, always acquires a Lock nothing else
        on this Thread is still holding."""
        with self._lock:
            if not self._accepting:
                return None
            executor = ThreadPoolExecutor(max_workers=1)
            future = executor.submit(work)
            # Never wait on Pool shutdown itself — see `run_tracked_stage`'s
            # own docstring for why.
            executor.shutdown(wait=False)
            key = self._next_key
            self._next_key += 1
            self._active[key] = future

        def _untrack(_: Future[Any], *, key: int = key) -> None:
            with self._lock:
                self._active.pop(key, None)

        future.add_done_callback(_untrack)
        return future

    def active_count(self) -> int:
        with self._lock:
            return len(self._active)

    def shutdown(self, *, timeout_seconds: float) -> bool:
        """Stop accepting new Tracked Stage submissions, then Bounded-Join
        every currently-tracked Worker up to `timeout_seconds` total
        (never per-Worker — several slow Workers cannot each consume the
        full bound). Returns `True` only when every Worker tracked at the
        moment this call started has genuinely finished (successfully or
        with an Exception — either way it is no longer running) within
        that bound; returns `False`, never a false "Clean" claim, when one
        or more Cancellation-ignoring Workers are still running once the
        bound expires — Python cannot forcibly kill a running Thread, so
        this is reported honestly rather than papered over."""
        with self._lock:
            self._accepting = False
            pending = list(self._active.values())
        if not pending:
            return True
        deadline = time.monotonic() + max(0.0, timeout_seconds)
        clean = True
        for future in pending:
            remaining = deadline - time.monotonic()
            if remaining <= 0 and not future.done():
                clean = False
                continue
            try:
                future.result(timeout=max(0.0, remaining))
            except FutureTimeoutError:
                clean = False
            except Exception:
                # The work itself raised — it still genuinely finished
                # (done), so it does not count against Clean; only
                # "still running past the bound" does.
                pass
        return clean


def run_tracked_stage[T](
    *,
    work: Callable[[], T],
    budget_ms: int,
    registry: TrackedStageWorkerRegistry | None = None,
) -> TrackedStageOutcome[T]:
    """Run `work` on a dedicated Thread, waiting at most `budget_ms`.

    `budget_ms <= 0` runs `work` inline with no Worker Thread at all —
    matches `stage_deadline()`'s own convention for a Provider (e.g.
    Built-in) that performs no bounded work whatsoever, and keeps a
    zero-Budget Stage genuinely synchronous rather than paying Thread
    hand-off overhead for no reason. Nothing is submitted to `registry`
    for this path — there is no background Thread for it to Own.

    When `registry` is supplied, Admission is entirely delegated to its
    own `submit()` (P6-RR-R25, resolves P6-CODEX-088) — the accepting-
    check, the Thread dispatch, and the Registry registration happen as
    one atomic operation there, never as separate calls this function
    could race against a concurrent `shutdown()` between. A `None` result
    (Shutdown already begun) is reported as the same typed Timeout-shaped
    Outcome a real Budget expiry would produce — `work` is simply never
    run.
    """
    if budget_ms <= 0:
        result = work()
        immediate: Future[T] = Future()
        immediate.set_result(result)
        return TrackedStageOutcome(result=result, timed_out=False, future=immediate)
    if registry is not None:
        submitted = registry.submit(work=work)
        if submitted is None:
            rejected: Future[T] = Future()
            rejected.set_exception(RuntimeError("tracked_stage_worker_registry_shutting_down"))
            return TrackedStageOutcome(result=None, timed_out=True, future=rejected)
        future = submitted
    else:
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(work)
        # Never wait on Pool shutdown itself — that would silently
        # reintroduce the exact unbounded wait this module exists to
        # avoid. The Thread backing `future` keeps running to completion
        # regardless; Python cannot safely kill it, and this module never
        # claims otherwise.
        executor.shutdown(wait=False)
    try:
        result = future.result(timeout=budget_ms / 1000)
    except FutureTimeoutError:
        return TrackedStageOutcome(result=None, timed_out=True, future=future)
    return TrackedStageOutcome(result=result, timed_out=False, future=future)
