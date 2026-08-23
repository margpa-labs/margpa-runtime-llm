"""Model Access Coordinator (P6-CODEX-010 Second Rework, hardened P6-CODEX-019
Third Rework).

Serializes all access to the one shared Model Backend context between the
"main" Conversation Generation path and "background" internal consumers
(Judge, Repair) so a Background Task can never cause a genuine Main Turn to
fail with `model_busy` — the failure mode a Detached Daemon Thread produced
(see the Second Rework Handoff's P6-CODEX-010 finding).

Two Main Turns genuinely racing (e.g. two browser tabs sending at once)
still fail fast with `MODEL_BUSY` — that pre-existing, tested behavior is
preserved unchanged.

Main-priority preemption (P6-CODEX-019, Third Rework): a Background Task is
never allowed to make a genuine Main Turn wait an unbounded or merely
"generous" amount of time. As soon as `acquire_main()` observes a
Background Task holding access, it actively signals that Task's
Cancellation Token (see `inference.domain.cancellation.CancellationToken`)
so the Task's own in-flight Model Call stops at the next emitted token
(`LlamaCppModelAdapter`'s `stopping_criteria`-based cancellation), not only
when it eventually reaches its own budget's `max_new_tokens`. `acquire_main`
then waits — bounded by `main_wait_for_background_timeout_seconds` — for the
preempted Task to actually release the slot. This timeout is a genuine
backstop for a pathological case (a Background Task's own generate() call
somehow does not honor the Cancellation Token — e.g. it is not even a
`generate()` call, or the backend ignores `stopping_criteria`), never the
expected path: under normal operation the preempted Task should release the
slot within roughly one token-generation step. If even this backstop is
exhausted, `acquire_main` raises `INTERNAL_TASK_PREEMPTION_FAILED` — a
distinct error code from `MODEL_BUSY` — because the Return Contract this
module exists to satisfy ("an Internal Task never causes a Main Turn
`model_busy`") is specifically about the ordinary two-tasks-overlap case;
that contract does not, and cannot, extend to "a Task refuses to honor a
Cancellation Token it was given", which is a distinct internal fault, not a
capacity conflict.
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable
from typing import Literal

from ..domain.errors import InferenceError, InferenceErrorCode

_logger = logging.getLogger(__name__)

TaskKind = Literal["main", "background", "switch"]

_DEFAULT_MAIN_WAIT_FOR_BACKGROUND_TIMEOUT_SECONDS = 30.0


class ModelAccessCoordinator:
    def __init__(
        self,
        *,
        main_wait_for_background_timeout_seconds: float = (
            _DEFAULT_MAIN_WAIT_FOR_BACKGROUND_TIMEOUT_SECONDS
        ),
    ) -> None:
        self._condition = threading.Condition()
        self._current_kind: TaskKind | None = None
        self._current_task_id: str | None = None
        self._current_cancel: Callable[[], None] | None = None
        self._background_thread: threading.Thread | None = None
        self._shutting_down = False
        self._main_wait_timeout = main_wait_for_background_timeout_seconds

    def acquire_main(self, *, task_id: str) -> None:
        """Blocks briefly (bounded, and actively shortened by preempting any
        Background Task) only if a Background Task currently holds access;
        raises immediately for a genuine Main-vs-Main conflict, matching the
        pre-existing fail-fast contract. Raises immediately (never waits) if
        shutdown has already begun — a Main Turn arriving after `shutdown()`
        has no Model left to serve it.

        P6-CODEX-034 (Fifth Rework): also raises immediately (never waits,
        never preempts) if a Runtime Model Switch/Context Reload currently
        holds the exclusive `"switch"` lease — Architecture 5.1's own
        "Reload中は新Generationを受け付けず" (a Reload in progress does not
        accept new Generation). Unlike a Background Task, a Switch has no
        Cancellation Token to preempt (its Unload/Load cannot be safely
        interrupted partway through), so Main must fail fast and let the
        caller retry, exactly like the existing Main-vs-Main conflict."""
        with self._condition:
            if self._shutting_down:
                raise InferenceError(
                    code=InferenceErrorCode.MODEL_NOT_LOADED,
                    safe_message="The model is shutting down and cannot accept new requests.",
                    request_id=task_id,
                )
            if self._current_kind == "switch":
                raise InferenceError(
                    code=InferenceErrorCode.MODEL_BUSY,
                    safe_message="The model is being switched or reloaded.",
                    retryable=True,
                    request_id=task_id,
                )
            deadline = time.monotonic() + self._main_wait_timeout
            preempted = False
            while self._current_kind == "background":
                if not preempted:
                    # P6-CODEX-019: signal cancellation as soon as Main
                    # arrives, not only after this wait already times out —
                    # Main-priority Scheduling means Main is never made to
                    # queue behind a Background Task's own full budget.
                    if self._current_cancel is not None:
                        self._current_cancel()
                    preempted = True
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    _logger.error(
                        "model access coordinator: background task %r did not release "
                        "the shared model within %.1fs of being preempted for main "
                        "task %r",
                        self._current_task_id,
                        self._main_wait_timeout,
                        task_id,
                    )
                    raise InferenceError(
                        code=InferenceErrorCode.INTERNAL_TASK_PREEMPTION_FAILED,
                        safe_message=(
                            "An internal background task did not release the model in time."
                        ),
                        retryable=True,
                        request_id=task_id,
                    )
                self._condition.wait(timeout=remaining)
                # P6-CODEX-034: the instant Background released, a waiting
                # Switch lease acquisition could have won the race and
                # claimed "switch" before this thread woke up and
                # re-acquired the lock — re-check here too, never fall
                # through to claiming "main" over an active Switch. Read
                # into a local, explicitly widened, first: mypy otherwise
                # narrows `_current_kind` to Literal["background"] from the
                # `while` condition above, which does not account for
                # concurrent mutation of `self._current_kind` across
                # `wait()`.
                current_kind_after_wait: TaskKind | None = self._current_kind
                if current_kind_after_wait == "switch":
                    raise InferenceError(
                        code=InferenceErrorCode.MODEL_BUSY,
                        safe_message="The model is being switched or reloaded.",
                        retryable=True,
                        request_id=task_id,
                    )
            if self._current_kind == "main":
                raise InferenceError(
                    code=InferenceErrorCode.MODEL_BUSY,
                    safe_message="The model is already processing another request.",
                    retryable=True,
                    request_id=task_id,
                )
            self._current_kind = "main"
            self._current_task_id = task_id

    def release_main(self, *, task_id: str) -> None:
        with self._condition:
            if self._current_kind == "main" and self._current_task_id == task_id:
                self._current_kind = None
                self._current_task_id = None
                self._condition.notify_all()

    def start_background(
        self,
        *,
        task_id: str,
        target: Callable[[], None],
        cancel: Callable[[], None] | None = None,
    ) -> bool:
        """Starts `target` on an owned, tracked Thread only if nothing else
        is active and shutdown has not begun. Never queues, never waits —
        returns `False` immediately otherwise (the caller must treat that
        as "skip this Background Task for this Turn"). `cancel`, if given,
        is invoked by a subsequent `acquire_main()` from another thread to
        request this Task's own in-flight Model Call stop early
        (P6-CODEX-019); this module never depends on any particular
        cancellation mechanism, only on `cancel` being a zero-argument,
        idempotent, thread-safe callable.

        P6-CODEX-027 (Fourth Rework): the state check, `thread.start()`,
        and `self._background_thread` registration all happen inside the
        SAME held `self._condition` — not across two separate
        acquire/release windows. The previous version released the lock
        between claiming the slot and registering `_background_thread`,
        so a `shutdown()` landing in that exact window would read
        `_background_thread is None` and report a false clean shutdown
        while a Thread was still starting (or already running) and could
        go on to touch the Model after `Adapter.unload()`. `thread.start()`
        itself is a fast, non-blocking call (it does not wait for `target`
        to run), so holding the lock across it cannot deadlock against
        `_run`'s own lock use, which only happens in its `finally` block —
        strictly after `target()` (the actual, long-running Model Call)
        has already returned."""

        def _run() -> None:
            try:
                target()
            except Exception:
                # The slot is released regardless (see `finally` below); a
                # Background Task's own caller is responsible for recording
                # a Typed Failure Result (e.g. Judge does this itself). This
                # module only ensures an uncaught Background exception never
                # becomes an unlogged, unhandled Thread crash.
                _logger.exception("model access coordinator background task %r raised", task_id)
            finally:
                with self._condition:
                    self._current_kind = None
                    self._current_task_id = None
                    self._current_cancel = None
                    self._background_thread = None
                    self._condition.notify_all()

        thread = threading.Thread(
            target=_run, daemon=True, name=f"model-access-background-{task_id}"
        )
        with self._condition:
            if self._shutting_down or self._current_kind is not None:
                return False
            self._current_kind = "background"
            self._current_task_id = task_id
            self._current_cancel = cancel
            try:
                thread.start()
            except Exception:
                # P6-CODEX-019: a Thread that never started must not leave
                # the slot permanently claimed — roll back exactly as if
                # `start_background` had returned `False` to begin with.
                _logger.exception(
                    "model access coordinator failed to start background task %r", task_id
                )
                self._current_kind = None
                self._current_task_id = None
                self._current_cancel = None
                return False
            self._background_thread = thread
        return True

    def current_background_task_id(self) -> str | None:
        with self._condition:
            return self._current_task_id if self._current_kind == "background" else None

    def try_acquire_switch_lease(self, *, task_id: str) -> bool:
        """P6-CODEX-034 (Fifth Rework): atomically acquires the exclusive
        Runtime Model Switch/Context Reload lease — succeeds only if
        NOTHING (no Main Turn, no Background Judge/Repair Task) is
        currently active. Never waits, never preempts: unlike
        `acquire_main()`, a Switch has no ordering priority over an
        already-in-flight Main or Background Call, and its own Unload/Load
        cannot be safely interrupted once started, so the caller
        (`RuntimeModelController.begin_switch()`) must treat `False` as an
        outright Typed Busy/Conflict rejection with zero Unload/Load
        attempted — never a queue, never a retry loop here.

        Once acquired, `_current_kind == "switch"` is itself sufficient to
        block every other entry point: `start_background()`'s existing
        `self._current_kind is not None` check already refuses new
        Background Tasks, and `acquire_main()` now fails fast on
        `"switch"` too (see above) — so no in-flight Judge/Repair/Main can
        begin touching the Model while a Switch holds this lease, closing
        the exact race P6-CODEX-034 identified."""
        with self._condition:
            if self._shutting_down or self._current_kind is not None:
                return False
            self._current_kind = "switch"
            self._current_task_id = task_id
            return True

    def release_switch_lease(self, *, task_id: str) -> None:
        with self._condition:
            if self._current_kind == "switch" and self._current_task_id == task_id:
                self._current_kind = None
                self._current_task_id = None
                self._condition.notify_all()

    def shutdown(self, *, join_timeout_seconds: float = 30.0) -> bool:
        """Stops accepting new Background Tasks and joins any in-flight one
        before returning, so a caller's subsequent `Adapter.unload()` never
        races a live Judge/Repair Model Call (P6-CODEX-010).

        Returns `True` only if it is actually safe to proceed to unload the
        Adapter — i.e. no Background Task is still alive. Returns `False`
        (P6-CODEX-019) if the in-flight Background Thread did not terminate
        within `join_timeout_seconds`; a caller must not call
        `Adapter.unload()` in that case (it would race a Thread that may
        still be inside a live Model Call), and should instead log this as
        a genuine shutdown anomaly and let the process-level exit handle
        reclaiming resources."""
        with self._condition:
            self._shutting_down = True
            thread = self._background_thread
        if thread is None:
            return True
        thread.join(timeout=join_timeout_seconds)
        if thread.is_alive():
            _logger.error(
                "model access coordinator: background task %r still alive after "
                "%.1fs shutdown join timeout; refusing to report clean shutdown",
                self._current_task_id,
                join_timeout_seconds,
            )
            return False
        return True
