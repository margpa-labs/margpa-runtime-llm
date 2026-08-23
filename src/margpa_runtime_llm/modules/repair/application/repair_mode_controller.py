"""Repair Mode Controller (Phase 6-G-WU-004, Acceptance P6-ACC-025).

Independent Process-local State from Judge/Guardrail/Main Governance's own
Mode Controllers. Mirrors GuardrailModeController's shape (lock + revision
+ current_mode, unconditional apply) native to RepairMode.
"""

import threading
from dataclasses import dataclass

from ..domain.identifiers import RepairMode


@dataclass(frozen=True, slots=True)
class RepairModeSnapshot:
    revision: int
    current_mode: RepairMode


class RepairModeController:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current_mode = RepairMode.OFF
        self._revision = 1

    def mode_snapshot(self) -> RepairModeSnapshot:
        with self._lock:
            return RepairModeSnapshot(revision=self._revision, current_mode=self._current_mode)

    def apply_mode(self, requested_mode: RepairMode) -> RepairModeSnapshot:
        with self._lock:
            if requested_mode is not self._current_mode:
                self._current_mode = requested_mode
                self._revision += 1
            return RepairModeSnapshot(revision=self._revision, current_mode=self._current_mode)
