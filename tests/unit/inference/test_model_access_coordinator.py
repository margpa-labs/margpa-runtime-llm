"""P6-CODEX-010 (Second Rework), hardened P6-CODEX-019 (Third Rework):
ModelAccessCoordinator's own contract, independent of any Judge/Repair/
Conversation caller.

Covers: Main-vs-Main fail-fast (preserves the pre-existing tested
model_busy contract for two concurrent user tabs); Main actively preempts
(via a caller-supplied `cancel` callback) and then waits bounded for a
Background Task, rather than failing with `model_busy`; a Background Task
that never honors preemption produces a distinct
`INTERNAL_TASK_PREEMPTION_FAILED` (never `MODEL_BUSY` — that code is
reserved for genuine Main-vs-Main conflicts); start_background never queues
(returns False outright when anything else is active) and rolls back the
claimed slot if the Thread itself fails to start; and shutdown stops
accepting new Background Tasks, joins the in-flight one before returning,
reports via its return value whether that join actually succeeded, and
causes any late `acquire_main()` to fail fast instead of waiting.
"""

from __future__ import annotations

import threading
import time

import pytest

from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError, InferenceErrorCode


def _wait_for_event(event: threading.Event) -> None:
    event.wait()


def test_main_vs_main_fails_fast_without_waiting() -> None:
    coordinator = ModelAccessCoordinator()
    coordinator.acquire_main(task_id="main-1")

    started = time.monotonic()
    with pytest.raises(InferenceError) as excinfo:
        coordinator.acquire_main(task_id="main-2")
    elapsed = time.monotonic() - started

    assert excinfo.value.code is InferenceErrorCode.MODEL_BUSY
    assert elapsed < 1.0  # fails fast, never waits out the background timeout


def test_release_main_only_releases_the_owning_task() -> None:
    coordinator = ModelAccessCoordinator()
    coordinator.acquire_main(task_id="main-1")

    coordinator.release_main(task_id="a-different-task-id")
    with pytest.raises(InferenceError):
        coordinator.acquire_main(task_id="main-2")

    coordinator.release_main(task_id="main-1")
    coordinator.acquire_main(task_id="main-2")  # no longer raises


def test_start_background_returns_false_and_never_queues_when_main_is_active() -> None:
    coordinator = ModelAccessCoordinator()
    coordinator.acquire_main(task_id="main-1")

    calls = 0

    def _target() -> None:
        nonlocal calls
        calls += 1

    started = coordinator.start_background(task_id="bg-1", target=_target)

    assert started is False
    time.sleep(0.05)
    assert calls == 0  # never queued for later


def test_start_background_returns_false_when_another_background_task_is_active() -> None:
    coordinator = ModelAccessCoordinator()
    release_gate = threading.Event()

    coordinator.start_background(task_id="bg-1", target=lambda: _wait_for_event(release_gate))
    second_started = coordinator.start_background(task_id="bg-2", target=lambda: None)

    assert second_started is False
    release_gate.set()


def test_main_waits_bounded_for_an_in_flight_background_task_then_proceeds() -> None:
    coordinator = ModelAccessCoordinator(main_wait_for_background_timeout_seconds=2.0)
    release_gate = threading.Event()
    assert coordinator.start_background(
        task_id="bg-1", target=lambda: _wait_for_event(release_gate)
    )

    def _release_shortly() -> None:
        time.sleep(0.1)
        release_gate.set()

    threading.Thread(target=_release_shortly, daemon=True).start()

    started = time.monotonic()
    coordinator.acquire_main(task_id="main-1")  # must not raise
    elapsed = time.monotonic() - started

    assert elapsed >= 0.1
    assert elapsed < 2.0
    coordinator.release_main(task_id="main-1")


def test_main_actively_preempts_the_background_task_via_its_cancel_callback() -> None:
    """P6-CODEX-019: acquire_main must not merely wait — it must call the
    Background Task's own `cancel` as soon as it observes the conflict, so a
    well-behaved Task (one that actually checks its Cancellation Token, as
    the real `LlamaCppModelAdapter` cancellable path does) releases quickly
    regardless of its own nominal budget."""
    coordinator = ModelAccessCoordinator(main_wait_for_background_timeout_seconds=2.0)
    release_gate = threading.Event()
    cancel_called = threading.Event()

    def _cancel() -> None:
        cancel_called.set()
        release_gate.set()

    assert coordinator.start_background(
        task_id="bg-1", target=lambda: _wait_for_event(release_gate), cancel=_cancel
    )

    started = time.monotonic()
    coordinator.acquire_main(task_id="main-1")
    elapsed = time.monotonic() - started

    assert cancel_called.is_set()
    assert elapsed < 1.0  # released promptly once preempted, not the full 2.0s budget
    coordinator.release_main(task_id="main-1")


def test_main_raises_distinct_preemption_error_if_background_never_honors_cancel() -> None:
    """A Task that ignores its Cancellation Token entirely is a genuine
    internal fault, not an ordinary capacity conflict — it must never be
    reported as MODEL_BUSY (P6-CODEX-019's Return Contract is specifically
    that an Internal Task never causes a Main Turn model_busy)."""
    coordinator = ModelAccessCoordinator(main_wait_for_background_timeout_seconds=0.1)
    release_gate = threading.Event()
    assert coordinator.start_background(
        task_id="bg-1", target=lambda: _wait_for_event(release_gate), cancel=lambda: None
    )

    with pytest.raises(InferenceError) as excinfo:
        coordinator.acquire_main(task_id="main-1")

    assert excinfo.value.code is InferenceErrorCode.INTERNAL_TASK_PREEMPTION_FAILED
    release_gate.set()


def test_main_raises_preemption_error_without_cancel_callback_too() -> None:
    coordinator = ModelAccessCoordinator(main_wait_for_background_timeout_seconds=0.1)
    release_gate = threading.Event()
    assert coordinator.start_background(
        task_id="bg-1", target=lambda: _wait_for_event(release_gate)
    )

    with pytest.raises(InferenceError) as excinfo:
        coordinator.acquire_main(task_id="main-1")

    assert excinfo.value.code is InferenceErrorCode.INTERNAL_TASK_PREEMPTION_FAILED
    release_gate.set()


def test_background_task_releases_the_slot_on_completion() -> None:
    coordinator = ModelAccessCoordinator()
    done = threading.Event()
    assert coordinator.start_background(task_id="bg-1", target=done.set)

    deadline = time.monotonic() + 2.0
    while coordinator.current_background_task_id() is not None and time.monotonic() < deadline:
        time.sleep(0.005)

    assert coordinator.current_background_task_id() is None
    coordinator.acquire_main(task_id="main-1")  # proves the slot is truly free


def test_background_task_releases_the_slot_even_if_target_raises() -> None:
    coordinator = ModelAccessCoordinator()

    def _raising() -> None:
        raise RuntimeError("boom")

    assert coordinator.start_background(task_id="bg-1", target=_raising)

    deadline = time.monotonic() + 2.0
    while coordinator.current_background_task_id() is not None and time.monotonic() < deadline:
        time.sleep(0.005)

    assert coordinator.current_background_task_id() is None


def test_start_background_rolls_back_the_slot_if_thread_start_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P6-CODEX-019: a Thread that fails to start must not leave the slot
    permanently claimed — a subsequent caller must see the same `False` it
    would see for any other "nothing started" outcome, and the slot must be
    genuinely free afterward."""

    class _FailingThread:
        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def start(self) -> None:
            raise RuntimeError("could not start thread")

    monkeypatch.setattr(threading, "Thread", _FailingThread)
    coordinator = ModelAccessCoordinator()

    started = coordinator.start_background(task_id="bg-1", target=lambda: None)

    assert started is False
    assert coordinator.current_background_task_id() is None
    coordinator.acquire_main(task_id="main-1")  # slot is genuinely free


def test_shutdown_cannot_observe_a_claimed_slot_with_no_registered_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P6-CODEX-027 (Fourth Rework) regression: the previous implementation
    released `self._condition` between claiming the slot
    (`_current_kind = "background"`) and registering `_background_thread`,
    so a concurrent `shutdown()` could land in that exact window, observe
    `_background_thread is None`, and report a false clean shutdown while
    the Task was still starting (or already running) and could go on to
    touch the Model after the caller's subsequent `Adapter.unload()`. The
    fix folds the state check, `thread.start()`, and `_background_thread`
    registration into one held `self._condition` acquisition, so no
    interleaving `shutdown()` call can ever observe that intermediate
    state — proven here by forcing `Thread.start()` itself to block, then
    asserting a concurrent `shutdown()` call blocks too rather than racing
    ahead."""
    thread_start_called = threading.Event()
    allow_thread_start_to_proceed = threading.Event()
    # Captured before patching, so the driver threads below (which must run
    # immediately, not block) can construct plain, un-patched Threads.
    real_thread_class = threading.Thread

    class _BlockingThread(threading.Thread):
        def start(self) -> None:
            thread_start_called.set()
            allow_thread_start_to_proceed.wait(timeout=5.0)
            super().start()

    monkeypatch.setattr(threading, "Thread", _BlockingThread)
    coordinator = ModelAccessCoordinator()
    task_started = threading.Event()

    # These two driver threads use the captured, un-patched Thread class
    # directly — only the Coordinator's *own* internal `threading.Thread(
    # target=_run, ...)` construction (inside `start_background`) should
    # resolve to `_BlockingThread`; the test's own driver threads must run
    # immediately so they can actually observe the Coordinator's internal
    # lock-holding behavior instead of also blocking on `allow_thread_
    # start_to_proceed` themselves.
    starter = real_thread_class(
        target=lambda: coordinator.start_background(task_id="bg-1", target=task_started.set)
    )
    starter.start()

    assert thread_start_called.wait(timeout=5.0)

    shutdown_result: list[bool] = []
    shutdown_thread = real_thread_class(
        target=lambda: shutdown_result.append(coordinator.shutdown(join_timeout_seconds=5.0))
    )
    shutdown_thread.start()

    # start_background() is still holding the lock (blocked inside
    # Thread.start()) — a concurrent shutdown() must block on that same
    # lock too, never race ahead and see `_background_thread is None`.
    time.sleep(0.1)
    assert shutdown_thread.is_alive(), (
        "shutdown() returned before start_background() released the lock "
        "— the P6-CODEX-027 race window is still open"
    )

    allow_thread_start_to_proceed.set()
    starter.join(timeout=5.0)
    shutdown_thread.join(timeout=5.0)

    assert task_started.wait(timeout=5.0)
    assert shutdown_result == [True]


def test_shutdown_joins_the_in_flight_background_task_before_returning() -> None:
    coordinator = ModelAccessCoordinator()
    finished = threading.Event()

    def _slow_task() -> None:
        time.sleep(0.15)
        finished.set()

    assert coordinator.start_background(task_id="bg-1", target=_slow_task)

    clean = coordinator.shutdown(join_timeout_seconds=2.0)

    assert finished.is_set()
    assert clean is True


def test_shutdown_cancels_the_in_flight_background_task_before_joining() -> None:
    """RW8-A: shutdown must actively signal the tracked Worker."""

    coordinator = ModelAccessCoordinator()
    release_gate = threading.Event()
    cancel_called = threading.Event()

    def _cancel() -> None:
        cancel_called.set()
        release_gate.set()

    assert coordinator.start_background(
        task_id="bg-cancellable",
        target=lambda: _wait_for_event(release_gate),
        cancel=_cancel,
    )

    clean = coordinator.shutdown(join_timeout_seconds=2.0)

    assert cancel_called.is_set()
    assert clean is True


def test_shutdown_returns_false_if_background_task_outlives_join_timeout() -> None:
    """P6-CODEX-019: a caller (e.g. `web_application._close()`) must be able
    to tell a genuinely clean shutdown apart from one where the Background
    Thread did not actually terminate, so it can skip `Adapter.unload()`
    rather than racing a Thread that may still be inside a live Model
    Call."""
    coordinator = ModelAccessCoordinator()
    release_gate = threading.Event()
    assert coordinator.start_background(
        task_id="bg-1", target=lambda: _wait_for_event(release_gate)
    )

    clean = coordinator.shutdown(join_timeout_seconds=0.05)

    assert clean is False
    release_gate.set()


def test_auxiliary_task_is_tracked_but_never_owns_the_model_lease() -> None:
    coordinator = ModelAccessCoordinator(main_wait_for_background_timeout_seconds=0.01)
    entered = threading.Event()
    release_gate = threading.Event()

    def _auxiliary() -> None:
        entered.set()
        _wait_for_event(release_gate)

    assert coordinator.start_auxiliary(task_id="evidence-1", target=_auxiliary)
    assert entered.wait(timeout=2.0)
    assert coordinator.current_auxiliary_task_ids() == ("evidence-1",)

    # No INTERNAL_TASK_PREEMPTION_FAILED: auxiliary work is deliberately
    # outside the model-access lease even while it remains lifecycle-owned.
    coordinator.acquire_main(task_id="main-during-evidence")
    coordinator.release_main(task_id="main-during-evidence")

    release_gate.set()
    assert coordinator.shutdown(join_timeout_seconds=2.0) is True
    assert coordinator.current_auxiliary_task_ids() == ()


def test_shutdown_refuses_false_clean_while_auxiliary_task_is_blocked() -> None:
    coordinator = ModelAccessCoordinator()
    entered = threading.Event()
    release_gate = threading.Event()

    def _auxiliary() -> None:
        entered.set()
        _wait_for_event(release_gate)

    assert coordinator.start_auxiliary(task_id="evidence-blocked", target=_auxiliary)
    assert entered.wait(timeout=2.0)

    assert coordinator.shutdown(join_timeout_seconds=0.01) is False
    assert coordinator.current_auxiliary_task_ids() == ("evidence-blocked",)

    release_gate.set()
    assert coordinator.shutdown(join_timeout_seconds=2.0) is True
    assert coordinator.current_auxiliary_task_ids() == ()


def test_shutdown_rejects_new_background_tasks() -> None:
    coordinator = ModelAccessCoordinator()
    coordinator.shutdown(join_timeout_seconds=1.0)

    started = coordinator.start_background(task_id="bg-1", target=lambda: None)

    assert started is False


def test_shutdown_causes_acquire_main_to_fail_fast_instead_of_waiting() -> None:
    """P6-CODEX-019: a Main Turn arriving after shutdown has begun has no
    Model left to serve it and must fail immediately, never wait."""
    coordinator = ModelAccessCoordinator(main_wait_for_background_timeout_seconds=5.0)
    coordinator.shutdown(join_timeout_seconds=1.0)

    started = time.monotonic()
    with pytest.raises(InferenceError) as excinfo:
        coordinator.acquire_main(task_id="main-1")
    elapsed = time.monotonic() - started

    assert excinfo.value.code is InferenceErrorCode.MODEL_NOT_LOADED
    assert elapsed < 1.0
