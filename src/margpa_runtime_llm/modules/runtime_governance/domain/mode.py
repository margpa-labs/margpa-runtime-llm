"""Phase 4 Main Governance Mode availability (P4-MOD-004/005, ADR-4-007).

Reuses `GovernanceMode` (off/observe/enforce) and `GovernanceModeDescriptor`
from `governance_definitions` (Program-wide Invariant #5: "off/observe/
enforceを共通Modeとする") — but unlike Phase 3's fixed
`PHASE_3_MODE_DESCRIPTORS` (`enforce` permanently unavailable),
Phase 4 computes `enforce`'s availability dynamically from whether a
usable Binding, at least one registered Action, Authority and Budget are
all currently present. `enforce` never gets silently downgraded to
`observe` when it is requested but unavailable — the caller must see an
explicit `unavailable`, never a substituted lower Mode.
"""

from __future__ import annotations

from margpa_runtime_llm.modules.configuration_control import ApplyDisposition
from margpa_runtime_llm.modules.governance_definitions.domain import (
    GovernanceMode,
    GovernanceModeAvailability,
    GovernanceModeDescriptor,
)


def build_main_governance_mode_descriptors(
    *,
    enforce_ready: bool,
    enforce_unavailable_reason_code: str | None = None,
) -> tuple[GovernanceModeDescriptor, ...]:
    return (
        GovernanceModeDescriptor(
            mode=GovernanceMode.OFF,
            availability=GovernanceModeAvailability.AVAILABLE,
            apply_disposition=ApplyDisposition.RUNTIME_APPLICABLE,
        ),
        GovernanceModeDescriptor(
            mode=GovernanceMode.OBSERVE,
            availability=GovernanceModeAvailability.AVAILABLE,
            apply_disposition=ApplyDisposition.RUNTIME_APPLICABLE,
        ),
        GovernanceModeDescriptor(
            mode=GovernanceMode.ENFORCE,
            availability=(
                GovernanceModeAvailability.AVAILABLE
                if enforce_ready
                else GovernanceModeAvailability.UNAVAILABLE
            ),
            apply_disposition=(
                ApplyDisposition.RUNTIME_APPLICABLE
                if enforce_ready
                else ApplyDisposition.UNSUPPORTED
            ),
            unavailable_reason_code=(
                None
                if enforce_ready
                else (enforce_unavailable_reason_code or "binding_or_authority_unavailable")
            ),
        ),
    )
