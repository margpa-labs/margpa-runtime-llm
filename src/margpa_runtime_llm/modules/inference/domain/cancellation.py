"""Cooperative Model Call Cancellation (P6-CODEX-019, Third Rework).

A `CancellationToken` lets a caller that owns a Background Model Call (Judge,
Repair) be asked to stop early by someone else (a Main Turn that needs the
shared Model right now) without the two ever touching a shared Lock or
knowing about each other's identity — the same anonymous-caller decoupling
`ModelAccessCoordinator` already uses.

This is deliberately a plain `threading.Event` wrapper, not a Pydantic
Contract: it is a transient synchronization primitive for one in-process
Model Call, never serialized, never part of a Request/Result data shape.
"""

from __future__ import annotations

import threading
import time


class CancellationToken:
    """One cooperative cancellation source, optionally linked to a parent.

    A child token owns only its local cancellation (for example, a stage
    deadline).  It still observes its parent (for example, a turn stop), so
    an internal deadline never mutates unrelated work that shares the turn.
    """

    def __init__(self, *, parent: CancellationToken | None = None) -> None:
        self._event = threading.Event()
        self._parent = parent

    @classmethod
    def linked_to(cls, parent: CancellationToken | None) -> CancellationToken:
        """Create a call-local token that observes ``parent`` cancellation."""

        return cls(parent=parent)

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set() or (
            self._parent is not None and self._parent.is_cancelled()
        )

    def wait(self, timeout: float | None = None) -> bool:
        """Wait until cancellation is requested or ``timeout`` elapses."""

        if self.is_cancelled():
            return True
        if self._parent is None:
            return self._event.wait(timeout)

        deadline = None if timeout is None else time.monotonic() + max(0.0, timeout)
        while True:
            if self.is_cancelled():
                return True
            remaining = None if deadline is None else deadline - time.monotonic()
            if remaining is not None and remaining <= 0:
                return False
            self._event.wait(timeout=0.01 if remaining is None else min(0.01, remaining))
