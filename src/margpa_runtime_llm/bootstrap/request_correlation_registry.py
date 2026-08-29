"""Shared Request Correlation Registry (P6-RR-R19-WU-001..004, Post-Claude
Independent Review Rework, resolves P6-CODEX-082).

The previous "Current Turn" anchor (`RecordingCompositionState.last_
outcome()`, wired in R15) is only ever set *after* the Turn's Recording
Hook actually writes a record — i.e. after the Turn has already
completed. While a new Turn is in flight (User just sent a message, Main
is still generating, Judge/Recording have not run yet), that anchor still
points at the *previous* Turn, so a Status reader observes the old
Turn as Current until the new Turn's own Recording Hook eventually fires
(the exact "送信後に設定を開くと一つ前、開き直すと最新" lag a Controller
Review confirmed on real hardware).

This Registry fixes that at the root: `ConversationGenerationSession`
registers its own `request_id` here the instant a Turn *starts*
(`begin()`, called before Judge/Repair/Recording ever run) and marks it
Terminal (`mark_terminal()`) exactly once, from `events()`'s own
guaranteed `finally` block, regardless of which exit path a Turn takes.
`current_request_id()` is therefore valid — and correct — for the entire
lifetime of a Turn, not only after it completes.

This Registry intentionally does not duplicate Judge Result, Recording
Outcome, Provider, or Budget fields — those already have correct,
independently-frozen owners (`JudgeGovernanceComposition`,
`RecordingCompositionState` x2, `LiveJudgeResult`'s own frozen-mode
fields). The Server-side Summary a Status reader needs is built by
*joining* those existing sources against this Registry's own
`current_request_id()`/tracked entries — see `feature_modes_routes.py`.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, replace

_RETAIN_DEFAULT = 8


@dataclass(frozen=True, slots=True)
class RequestCorrelationEntry:
    request_id: str
    generation: int
    status: str  # "pending" | "completed" | "cancelled" | "failed"
    started_at: str
    completed_at: str | None = None


class RequestCorrelationRegistry:
    """Process-local, Thread-safe. One instance shared across every Turn a
    `WebRuntime` serves (matches `JudgeGovernanceComposition`/
    `RecordingCompositionState`'s own lifetime)."""

    def __init__(self, *, retain: int = _RETAIN_DEFAULT) -> None:
        self._lock = threading.Lock()
        self._entries: dict[str, RequestCorrelationEntry] = {}
        self._order: list[str] = []
        self._current_request_id: str | None = None
        self._generation = 0
        self._retain = retain

    def begin(self, *, request_id: str, started_at: str) -> None:
        with self._lock:
            self._generation += 1
            self._entries[request_id] = RequestCorrelationEntry(
                request_id=request_id,
                generation=self._generation,
                status="pending",
                started_at=started_at,
            )
            self._order.append(request_id)
            self._current_request_id = request_id
            while len(self._order) > self._retain:
                oldest = self._order.pop(0)
                self._entries.pop(oldest, None)

    def mark_terminal(self, *, request_id: str, status: str, completed_at: str) -> None:
        with self._lock:
            existing = self._entries.get(request_id)
            if existing is None:
                # Evicted (retention bound) or never registered (e.g. a
                # Turn started before this Registry existed) — nothing to
                # attach a Terminal transition to. Never fabricated.
                return
            self._entries[request_id] = replace(existing, status=status, completed_at=completed_at)

    def current_request_id(self) -> str | None:
        with self._lock:
            return self._current_request_id

    def entry_for(self, request_id: str) -> RequestCorrelationEntry | None:
        with self._lock:
            return self._entries.get(request_id)

    def entries(self) -> tuple[RequestCorrelationEntry, ...]:
        """Oldest first; bounded by `retain`."""
        with self._lock:
            return tuple(self._entries[rid] for rid in self._order if rid in self._entries)
