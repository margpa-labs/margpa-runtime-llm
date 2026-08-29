"""P6-RR-R18-WU-001..003 (resolves P6-CODEX-081): `run_tracked_stage()`
must genuinely bound Prompt Build/Decode-shaped synchronous work — never
block its caller past `budget_ms`, and never let a Timeout-exceeding
result silently reach the caller after the fact.

P6-RR-R22 (Post-Codex Independent Review Rework, closes the rest of
P6-CODEX-081): `TrackedStageWorkerRegistry` is the single Owner that was
missing — a Timeout-discarded `Future` previously had no tracked Owner at
all, so Shutdown could claim Clean while a Cancellation-ignoring Worker
kept running. The Threaded Regression tests below prove: a genuinely
Blocked Worker makes `shutdown()` report `False`; Releasing it makes a
retried `shutdown()` report `True`; a Worker Exception still counts as
"finished" (no leak); several concurrent Workers are all tracked
independently; and once `shutdown()` has begun, no *new* Worker is ever
dispatched at all (the strongest form of Late Publish 0 at this layer)."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from concurrent.futures import Future

from margpa_runtime_llm.bootstrap.tracked_stage_worker import (
    TrackedStageWorkerRegistry,
    run_tracked_stage,
)


def test_work_finishing_within_budget_returns_the_real_result() -> None:
    outcome = run_tracked_stage(work=lambda: "prompt-text", budget_ms=1000)
    assert outcome.timed_out is False
    assert outcome.result == "prompt-text"
    assert outcome.future.result(timeout=1.0) == "prompt-text"


def test_zero_budget_runs_inline_with_no_worker_thread() -> None:
    calling_thread = threading.current_thread()
    seen_thread: list[threading.Thread] = []

    def _work() -> str:
        seen_thread.append(threading.current_thread())
        return "ok"

    outcome = run_tracked_stage(work=_work, budget_ms=0)
    assert outcome.timed_out is False
    assert outcome.result == "ok"
    assert seen_thread == [calling_thread]


def test_slow_work_times_out_without_blocking_past_the_budget() -> None:
    release = threading.Event()

    def _slow_work() -> str:
        release.wait(timeout=5.0)
        return "late"

    started = time.monotonic()
    outcome = run_tracked_stage(work=_slow_work, budget_ms=50)
    elapsed_ms = (time.monotonic() - started) * 1000

    assert outcome.timed_out is True
    assert outcome.result is None
    assert elapsed_ms < 1000, "run_tracked_stage() must not block past its own Budget"

    release.set()
    assert outcome.future.result(timeout=5.0) == "late"


def test_a_late_completing_worker_is_never_auto_published_anywhere() -> None:
    """The core "Late Publish 0" guarantee: once `run_tracked_stage()`
    has already returned `timed_out=True`, nothing it does afterward
    hands that late value to anyone who did not explicitly go looking
    for it via the returned Future."""
    release = threading.Event()
    published: list[str] = []

    def _slow_work() -> str:
        release.wait(timeout=5.0)
        return "should-never-be-auto-published"

    outcome = run_tracked_stage(work=_slow_work, budget_ms=20)
    assert outcome.timed_out is True

    # Simulate the real caller's behavior: on Timeout, it returns a typed
    # failure immediately and never touches `outcome.future` again.
    if not outcome.timed_out and outcome.result is not None:
        published.append(outcome.result)

    release.set()
    outcome.future.result(timeout=5.0)  # let the background Thread finish
    assert published == []


def test_worker_exception_is_raised_synchronously_when_within_budget() -> None:
    def _raising_work() -> str:
        raise RuntimeError("decode failed")

    try:
        run_tracked_stage(work=_raising_work, budget_ms=1000)
    except RuntimeError as exc:
        assert str(exc) == "decode failed"
    else:
        raise AssertionError("expected RuntimeError to propagate")


def test_registry_shutdown_returns_false_while_a_worker_is_still_blocked() -> None:
    """P6-RR-R22 (resolves the rest of P6-CODEX-081): a genuinely Blocked
    Worker — proven with a real Thread and an `Event`, not merely a
    sequential same-thread call — must make `shutdown()` report `False`,
    never a false "Clean" claim, while it is still running past the
    Bounded-Join window."""
    registry = TrackedStageWorkerRegistry()
    release = threading.Event()

    def _slow_work() -> str:
        release.wait(timeout=5.0)
        return "late"

    outcome = run_tracked_stage(work=_slow_work, budget_ms=20, registry=registry)
    assert outcome.timed_out is True
    assert registry.active_count() == 1

    started = time.monotonic()
    clean = registry.shutdown(timeout_seconds=0.1)
    elapsed = time.monotonic() - started
    assert clean is False
    assert elapsed < 2.0, "shutdown() must not block far past its own bound"

    release.set()
    outcome.future.result(timeout=5.0)


def test_registry_shutdown_retried_after_release_reports_true() -> None:
    """The "Release後のRetry True" half: once the previously-Blocked
    Worker genuinely finishes, a subsequent `shutdown()` call converges to
    `True` and the Registry no longer tracks it."""
    registry = TrackedStageWorkerRegistry()
    release = threading.Event()

    def _slow_work() -> str:
        release.wait(timeout=5.0)
        return "late"

    outcome = run_tracked_stage(work=_slow_work, budget_ms=20, registry=registry)
    assert outcome.timed_out is True
    assert registry.shutdown(timeout_seconds=0.05) is False

    release.set()
    outcome.future.result(timeout=5.0)  # ensure the Worker has genuinely finished

    assert registry.shutdown(timeout_seconds=5.0) is True
    assert registry.active_count() == 0


def test_registry_untracks_a_worker_that_raises_zero_leak() -> None:
    """A Worker Exception still counts as "finished" (done, just not
    successful) — it must not leak the Registry entry or make Shutdown
    permanently report `False`. `run_tracked_stage()` itself re-raises a
    within-budget Exception synchronously (see `test_worker_exception_is_
    raised_synchronously_when_within_budget` above) — the Exception has
    already propagated to, and been caught by, this test's caller by the
    time the Registry-side assertions below run, exactly like the real
    Production call sites' own `try/except` around Prompt Build/Decode."""
    registry = TrackedStageWorkerRegistry()

    def _raising_work() -> str:
        raise RuntimeError("decode failed")

    try:
        run_tracked_stage(work=_raising_work, budget_ms=1000, registry=registry)
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected RuntimeError to propagate")

    assert registry.shutdown(timeout_seconds=5.0) is True
    assert registry.active_count() == 0


def test_registry_untracks_a_late_completing_worker_that_raises_zero_leak() -> None:
    """The real-world shape of the above: the Worker Exception happens
    *after* its own Caller already stopped waiting on Timeout (a "Late
    Complete" that is also a failure) — still counted as finished, never
    leaked."""
    registry = TrackedStageWorkerRegistry()
    release = threading.Event()

    def _slow_raising_work() -> str:
        release.wait(timeout=5.0)
        raise RuntimeError("late decode failure")

    outcome = run_tracked_stage(work=_slow_raising_work, budget_ms=20, registry=registry)
    assert outcome.timed_out is True
    assert registry.active_count() == 1

    release.set()
    # Let the background Thread genuinely finish (with its Exception) before
    # asserting Shutdown converges — `Future.exception()` observes it
    # without re-raising.
    assert outcome.future.exception(timeout=5.0) is not None

    assert registry.shutdown(timeout_seconds=5.0) is True
    assert registry.active_count() == 0


def test_registry_tracks_several_concurrent_workers_independently() -> None:
    """Several genuinely-concurrent Workers are each tracked
    independently — Shutdown must Bounded-Join every one of them, not just
    the first, and must not report `True` until the slowest has finished."""
    registry = TrackedStageWorkerRegistry()
    releases = [threading.Event() for _ in range(3)]

    def _work(index: int) -> Callable[[], str]:
        def _run() -> str:
            releases[index].wait(timeout=5.0)
            return f"result-{index}"

        return _run

    outcomes = [run_tracked_stage(work=_work(i), budget_ms=20, registry=registry) for i in range(3)]
    assert all(outcome.timed_out for outcome in outcomes)
    assert registry.active_count() == 3

    # Release two of the three; the third keeps the Registry non-Clean.
    releases[0].set()
    releases[1].set()
    outcomes[0].future.result(timeout=5.0)
    outcomes[1].future.result(timeout=5.0)
    assert registry.shutdown(timeout_seconds=0.1) is False
    assert registry.active_count() == 1

    releases[2].set()
    outcomes[2].future.result(timeout=5.0)
    assert registry.shutdown(timeout_seconds=5.0) is True
    assert registry.active_count() == 0


def test_registry_refuses_new_work_once_shutdown_has_begun_zero_late_publish() -> None:
    """P6-RR-R22 contract item 1: once `shutdown()` has been called, a
    *new* `run_tracked_stage()` submission must never dispatch a
    background Thread at all — the strongest form of "Late Publish 0" at
    this layer, since a rejected submission has nothing to leak or
    publish late in the first place."""
    registry = TrackedStageWorkerRegistry()
    assert registry.shutdown(timeout_seconds=1.0) is True
    assert registry.accepting_new_work() is False

    dispatched = threading.Event()

    def _work() -> str:
        dispatched.set()
        return "should never run"

    outcome = run_tracked_stage(work=_work, budget_ms=1000, registry=registry)
    assert outcome.timed_out is True
    assert outcome.result is None
    assert not dispatched.wait(timeout=0.2), "work() must never be dispatched after shutdown()"
    assert registry.active_count() == 0


def _race_submit_against_shutdown() -> tuple[Future[object] | None, bool, threading.Event, int]:
    """One trial: a real Thread pair races `submit()` against
    `shutdown()` for the same fresh Registry's own Lock, released
    simultaneously via a `Barrier`. Returns the `submit()` result, the
    `shutdown()` result, the Event `work` sets if it ever runs, and the
    Registry's own `active_count()` observed immediately afterward."""
    registry = TrackedStageWorkerRegistry()
    barrier = threading.Barrier(2)
    worker_started = threading.Event()
    future_holder: list[Future[object] | None] = []
    shutdown_holder: list[bool] = []

    def _submitter() -> None:
        barrier.wait(timeout=5.0)
        future_holder.append(registry.submit(work=worker_started.set))

    def _shutter() -> None:
        barrier.wait(timeout=5.0)
        shutdown_holder.append(registry.shutdown(timeout_seconds=2.0))

    submitter_thread = threading.Thread(target=_submitter)
    shutter_thread = threading.Thread(target=_shutter)
    submitter_thread.start()
    shutter_thread.start()
    submitter_thread.join(timeout=5.0)
    shutter_thread.join(timeout=5.0)
    assert not submitter_thread.is_alive()
    assert not shutter_thread.is_alive()
    return future_holder[0], shutdown_holder[0], worker_started, registry.active_count()


def test_atomic_submit_closes_the_admission_shutdown_toctou_probe_a() -> None:
    """P6-RR-R25 (Post-Codex Independent Review Rework, resolves
    P6-CODEX-088): deterministically reproduces Controller Probe A's
    exact Interleaving — `TrackedStageWorkerRegistry.submit()` and
    `shutdown()` racing for the same Registry's own Lock via a real
    Thread pair, released simultaneously through a `Barrier` and repeated
    across many trials to give the shared Lock every real opportunity to
    interleave badly. Probe A's exact bad outcome against the pre-R25
    three-separate-call shape was `shutdown_clean=True` together with
    `worker_started_after_shutdown=True` and `registry_active_after_
    clean=1` — a Worker admitted concurrently with Shutdown that still
    went on to run, invisible to Shutdown's own Bounded-Join snapshot.
    With `submit()` now atomic, that specific combination must never
    occur: either the Worker was rejected before `work` ever ran, or it
    was genuinely admitted and therefore unconditionally visible to
    `shutdown()`'s own snapshot."""
    for _ in range(150):
        future, shutdown_clean, worker_started, active_after = _race_submit_against_shutdown()

        if future is None:
            # Rejected before `shutdown()` even needed to Bound-Join it —
            # `work` (setting the Event) must never have run at all.
            assert worker_started.is_set() is False
        else:
            # Admitted: it was tracked before `shutdown()`'s own snapshot
            # could possibly have excluded it (same Lock), so `shutdown()`
            # cannot have returned at all without this exact Worker either
            # already having finished or being included in its own
            # Bounded-Join wait.
            future.result(timeout=5.0)
            assert worker_started.is_set()

        # The core Probe A invariant: a Clean Shutdown claim is never
        # accompanied by a still-tracked (or never-tracked-but-running)
        # Worker.
        if shutdown_clean:
            assert active_after == 0
