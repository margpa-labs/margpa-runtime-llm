"""Recording Mode Controller (Phase 6-G-WU-004, Architecture 10).

Independent Process-local State, mirrors GuardrailModeController's shape
(lock + revision + current_mode, unconditional apply) native to
RecordingMode (OFF/METADATA/FULL). Toggling this Controller's Mode does
not itself build or call a RecordingService/Writer — RecordingService
always reads whatever Mode it is constructed with (Phase 6-F-WU-005); a
live Mode change here only takes effect on the next RecordingService a
caller constructs with this Controller's current mode.
"""

import threading
from dataclasses import dataclass

from ..domain.recording import RecordingMode


@dataclass(frozen=True, slots=True)
class RecordingModeSnapshot:
    revision: int
    current_mode: RecordingMode


class RecordingModeController:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current_mode = RecordingMode.OFF
        self._revision = 1

    def mode_snapshot(self) -> RecordingModeSnapshot:
        with self._lock:
            return RecordingModeSnapshot(revision=self._revision, current_mode=self._current_mode)

    def apply_mode(self, requested_mode: RecordingMode) -> RecordingModeSnapshot:
        with self._lock:
            if requested_mode is not self._current_mode:
                self._current_mode = requested_mode
                self._revision += 1
            return RecordingModeSnapshot(revision=self._revision, current_mode=self._current_mode)
