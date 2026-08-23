"""Guardrail Mode Controller (P5-MOD-001, ADR-5-003, P5-F-WU-002).

Independent Process-local State from Phase 3/4's own Mode Controllers —
a separate instance, separate Revision counter, separate current Mode —
though it reuses the same Provider-neutral `off/observe/enforce`
primitive `governance_definitions.domain.mode` already exposes (a
Program-wide Invariant, not a Phase 3/4-specific coupling). Guardrail's
`enforce` never depends on an external Binding the way Phase 4's does —
the Core Policy/Authority/Registry are always locally available — so all
three Modes are always `available` (P5-MOD-001 Default `off`).
"""

from __future__ import annotations

import threading

from margpa_runtime_llm.modules.configuration_control import ApplyDisposition
from margpa_runtime_llm.modules.governance_definitions.domain import (
    GovernanceMode,
    GovernanceModeAvailability,
    GovernanceModeDescriptor,
    GovernanceModeSnapshot,
    GovernanceModeTransitionError,
    build_governance_mode_snapshot,
)


def build_guardrail_mode_descriptors() -> tuple[GovernanceModeDescriptor, ...]:
    return tuple(
        GovernanceModeDescriptor(
            mode=mode,
            availability=GovernanceModeAvailability.AVAILABLE,
            apply_disposition=ApplyDisposition.RUNTIME_APPLICABLE,
        )
        for mode in (GovernanceMode.OFF, GovernanceMode.OBSERVE, GovernanceMode.ENFORCE)
    )


class GuardrailModeController:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._current_mode = GovernanceMode.OFF
        self._revision = 1

    def mode_snapshot(self) -> GovernanceModeSnapshot:
        with self._lock:
            return self._snapshot()

    def apply_mode(self, requested_mode: GovernanceMode) -> GovernanceModeSnapshot:
        with self._lock:
            if requested_mode is self._current_mode:
                return self._snapshot()
            descriptor = next(
                item for item in build_guardrail_mode_descriptors() if item.mode is requested_mode
            )
            if descriptor.availability is not GovernanceModeAvailability.AVAILABLE:
                reason = descriptor.unavailable_reason_code
                raise GovernanceModeTransitionError(
                    safe_message=f"guardrail mode is unavailable: {reason}",
                    requested_mode=requested_mode,
                )
            self._current_mode = requested_mode
            self._revision += 1
            return self._snapshot()

    def current_mode_value(self) -> str:
        with self._lock:
            return self._current_mode.value

    def _snapshot(self) -> GovernanceModeSnapshot:
        base = build_governance_mode_snapshot(
            revision=self._revision, current_mode=self._current_mode
        )
        return base.model_copy(update={"descriptors": build_guardrail_mode_descriptors()})
