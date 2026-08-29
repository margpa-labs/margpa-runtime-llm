"""Main Governance Mode Controller (P4-F-WU-002, P4-MOD-004..006).

Process-local, non-persistent, mirroring the Revision/Digest pattern
already established for Phase 3's Governance Mode
(`governance_definitions.domain.mode`) — but `enforce`'s availability is
computed once at construction from whether this process's Runtime
Governance Composition is actually usable (`enforce_ready`), never a
fixed unavailable table (P4-MOD-004). A requested Mode that is not
`available` always raises rather than silently substituting a lower Mode
(P4-MOD-005) — this mirrors `governance_definitions.domain.mode.
request_mode_transition`'s own contract.
"""

from __future__ import annotations

import threading
from collections.abc import Callable

from margpa_runtime_llm.modules.governance_definitions.domain import (
    GovernanceMode,
    GovernanceModeAvailability,
    GovernanceModeSnapshot,
    GovernanceModeTransitionError,
    build_governance_mode_snapshot,
)

from ..domain import build_main_governance_mode_descriptors


class MainGovernanceModeController:
    def __init__(self, *, enforce_ready: bool) -> None:
        self._lock = threading.Lock()
        self._enforce_ready = enforce_ready
        self._current_mode = GovernanceMode.OFF
        self._revision = 1
        self._semantic_enforce_gate: Callable[[], tuple[bool, str | None]] | None = None

    def set_semantic_enforce_gate(self, gate: Callable[[], tuple[bool, str | None]]) -> None:
        """Bind the live Judge/provider readiness gate used by ENFORCE.

        This is installed after independent feature/provider controllers are
        composed.  It is evaluated on every transition, including an
        idempotent ENFORCE request, so stale startup readiness cannot create
        false ENFORCE.
        """
        with self._lock:
            self._semantic_enforce_gate = gate

    def mode_snapshot(self) -> GovernanceModeSnapshot:
        with self._lock:
            return self._snapshot()

    def apply_mode(self, requested_mode: GovernanceMode) -> GovernanceModeSnapshot:
        with self._lock:
            enforce_ready, reason = self._enforce_availability()
            descriptor = next(
                item
                for item in build_main_governance_mode_descriptors(
                    enforce_ready=enforce_ready,
                    enforce_unavailable_reason_code=reason,
                )
                if item.mode is requested_mode
            )
            if descriptor.availability is not GovernanceModeAvailability.AVAILABLE:
                raise GovernanceModeTransitionError(
                    safe_message=(
                        f"main governance mode is unavailable: {descriptor.unavailable_reason_code}"
                    ),
                    requested_mode=requested_mode,
                )
            if requested_mode is self._current_mode:
                return self._snapshot()
            self._current_mode = requested_mode
            self._revision += 1
            return self._snapshot()

    def current_mode_value(self) -> str:
        with self._lock:
            return self._current_mode.value

    def _snapshot(self) -> GovernanceModeSnapshot:
        enforce_ready, reason = self._enforce_availability()
        base = build_governance_mode_snapshot(
            revision=self._revision, current_mode=self._current_mode
        )
        return base.model_copy(
            update={
                "descriptors": build_main_governance_mode_descriptors(
                    enforce_ready=enforce_ready,
                    enforce_unavailable_reason_code=reason,
                )
            }
        )

    def _enforce_availability(self) -> tuple[bool, str | None]:
        if not self._enforce_ready:
            return False, "binding_or_authority_unavailable"
        if self._semantic_enforce_gate is None:
            return True, None
        try:
            ready, reason = self._semantic_enforce_gate()
        except Exception:
            return False, "semantic_enforce_gate_unavailable"
        return (True, None) if ready else (False, reason or "semantic_judge_unavailable")
