"""Governance Mode Contract (architecture §8, P3-F-WU-001).

Phase 3's `enforce` is declared but permanently `unavailable` — never
silently downgraded to `observe`, never silently accepted as a Mutation.
`GovernanceModeSnapshot` mirrors Configuration Control's
Revision/Digest/CAS pattern so this mode can be exposed through the
existing `ConfigurationControlService` seam (P3-F-WU-002) rather than
inventing a parallel config surface.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.configuration_control import ApplyDisposition
from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class GovernanceMode(StrEnum):
    OFF = "off"
    OBSERVE = "observe"
    ENFORCE = "enforce"


class GovernanceModeAvailability(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DENIED = "denied"


class GovernanceModeDescriptor(ImmutableContract):
    mode: GovernanceMode
    availability: GovernanceModeAvailability
    apply_disposition: ApplyDisposition
    unavailable_reason_code: str | None = Field(
        default=None, max_length=64, pattern=_IDENTIFIER_PATTERN
    )


# Phase 3 Local Profile (architecture §8.1) — a fixed table, not computed,
# because Phase 3 has exactly one Profile and `enforce`'s unavailability is
# a Phase boundary (ADR-3-002), not a runtime condition to evaluate.
PHASE_3_MODE_DESCRIPTORS: tuple[GovernanceModeDescriptor, ...] = (
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
        availability=GovernanceModeAvailability.UNAVAILABLE,
        apply_disposition=ApplyDisposition.UNSUPPORTED,
        unavailable_reason_code="phase_4_binding_required",
    ),
)


class GovernanceModeSnapshot(ImmutableContract):
    revision: int = Field(ge=0)
    digest_sha512: str = Field(pattern=r"^[0-9a-f]{128}$")
    current_mode: GovernanceMode
    descriptors: tuple[GovernanceModeDescriptor, ...] = PHASE_3_MODE_DESCRIPTORS


def governance_mode_digest(*, revision: int, current_mode: GovernanceMode) -> str:
    payload = json.dumps(
        {"revision": revision, "current_mode": current_mode.value},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha512(payload).hexdigest()


def build_governance_mode_snapshot(
    *, revision: int, current_mode: GovernanceMode
) -> GovernanceModeSnapshot:
    return GovernanceModeSnapshot(
        revision=revision,
        digest_sha512=governance_mode_digest(revision=revision, current_mode=current_mode),
        current_mode=current_mode,
    )


class GovernanceModeTransitionError(Exception):
    def __init__(self, *, safe_message: str, requested_mode: GovernanceMode) -> None:
        super().__init__(safe_message)
        self.safe_message = safe_message
        self.requested_mode = requested_mode


def request_mode_transition(
    *, current_mode: GovernanceMode, requested_mode: GovernanceMode
) -> GovernanceMode:
    """The only mutation entry point: rejects `enforce` outright (never
    silently substitutes `observe`) and is a no-op when the requested mode
    already matches — never raises for a redundant request."""

    if requested_mode is current_mode:
        return current_mode
    descriptor = next(d for d in PHASE_3_MODE_DESCRIPTORS if d.mode is requested_mode)
    if descriptor.availability is not GovernanceModeAvailability.AVAILABLE:
        raise GovernanceModeTransitionError(
            safe_message=f"governance mode is unavailable: {descriptor.unavailable_reason_code}",
            requested_mode=requested_mode,
        )
    return requested_mode
