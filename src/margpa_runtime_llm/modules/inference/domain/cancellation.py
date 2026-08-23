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


class CancellationToken:
    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()
