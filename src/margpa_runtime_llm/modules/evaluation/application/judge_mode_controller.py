"""Judge Mode Controller (Phase 6-G-WU-004, Acceptance P6-ACC-025).

Independent Process-local State from Guardrail/Main Governance's own Mode
Controllers (Acceptance "Judge Mode and Repair Mode are independent, Default OFF") — a
separate instance, separate revision counter, separate current Mode.
Mirrors GuardrailModeController's shape (lock + revision + current_mode,
unconditional apply — no CAS token from the caller) but native to
EvaluationMode rather than reusing GovernanceMode, since Judge/Repair
Modes are a distinct domain concept from Main/Guardrail Governance Mode.
"""

import threading
from dataclasses import dataclass

from ..domain.identifiers import EvaluationMode


@dataclass(frozen=True, slots=True)
class JudgeModeSnapshot:
    revision: int
    current_mode: EvaluationMode


class JudgeModeController:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current_mode = EvaluationMode.OFF
        self._revision = 1

    def mode_snapshot(self) -> JudgeModeSnapshot:
        with self._lock:
            return JudgeModeSnapshot(revision=self._revision, current_mode=self._current_mode)

    def apply_mode(self, requested_mode: EvaluationMode) -> JudgeModeSnapshot:
        with self._lock:
            if requested_mode is not self._current_mode:
                self._current_mode = requested_mode
                self._revision += 1
            return JudgeModeSnapshot(revision=self._revision, current_mode=self._current_mode)
