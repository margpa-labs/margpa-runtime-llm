"""Auto Compaction policy: an independent, process-lifetime Boolean.

Follows the SAME established pattern as `JudgeModeController`/
`RecordingModeController` (an in-memory Mode Controller, not persisted
config, mutated only through an authenticated Local API call) -- default
`True` per Canonical Design SS5.2, reset to that Default on every process
restart rather than silently inheriting a stale prior-run choice.
"""

from __future__ import annotations

from threading import Lock


class AutoCompactionPolicyController:
    def __init__(self, *, enabled: bool = True) -> None:
        self._lock = Lock()
        self._enabled = enabled

    def is_enabled(self) -> bool:
        with self._lock:
            return self._enabled

    def set_enabled(self, value: bool) -> None:
        """Effective for the next Turn/Action only (SS5.2's "進行中Attemptへ
        遡及させない") -- callers read `is_enabled()` fresh at the start of
        each Preflight/Action, never cache it across one."""

        with self._lock:
            self._enabled = value
