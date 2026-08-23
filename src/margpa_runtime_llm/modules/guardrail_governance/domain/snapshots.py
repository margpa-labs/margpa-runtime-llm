"""Typed, digest-bearing Snapshots for the Guardrail Action Resolver
(architecture §3.1/§3.3, P5-AUT-003, P5-CODEX-002 Rework) — mirrors
Phase 4's `runtime_governance/domain/snapshots.py` pattern, extended
with the Scope/Source Class/Expiry fields P5-AUT-003 requires that
Phase 4's own equivalent never needed (Phase 4 has no Approval/Expiry
concept at all).

`Stale/Unknown を Current として再利用しない` (P5-AUT-003): a Snapshot's
`authority_revision`/`policy_revision` of `0` is a genuine sentinel for
"never established" — never treated as a valid grant regardless of what
else the Snapshot claims — and a populated `expires_at` in the past
means the Snapshot must be treated as Stale even though its shape is
otherwise well-formed. See `is_expired()`/`has_established_revision()`
below, consumed by the Action Resolver's Authority check.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


def _canonical_digest(payload: object) -> str:
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()


def is_expired(expires_at: str | None, *, now: datetime | None = None) -> bool:
    """`None` means non-expiring (P5-AUT-003's "Expiry/Non-expiring
    表現") — never Expired. A malformed timestamp fails closed as
    Expired rather than raising or silently passing."""

    if expires_at is None:
        return False
    try:
        parsed = datetime.fromisoformat(expires_at)
    except ValueError:
        return True
    current = now if now is not None else datetime.now(UTC)
    return parsed <= current


class PolicySnapshot(ImmutableContract):
    policy_revision: int = Field(ge=0)
    profile: str = Field(min_length=1, max_length=64, pattern=_IDENTIFIER_PATTERN)
    scope: str = Field(default="process_local", min_length=1, max_length=64)
    source_class: str = Field(default="local_fixed_provider", min_length=1, max_length=64)
    expires_at: str | None = Field(default=None, max_length=40)

    @property
    def digest_sha512(self) -> str:
        return _canonical_digest(self.model_dump(mode="json"))

    @property
    def has_established_revision(self) -> bool:
        return self.policy_revision >= 1

    @property
    def is_expired(self) -> bool:
        return is_expired(self.expires_at)


class AuthoritySnapshot(ImmutableContract):
    """What Actions this process is currently permitted to Execute.

    Never inferred from a Detector, Model or Definition output —
    `granted_action_ids` is the only Source of Authority (ADR-5-005).
    """

    authority_revision: int = Field(ge=0)
    granted_action_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=64)
    scope: str = Field(default="process_local", min_length=1, max_length=64)
    source_class: str = Field(default="local_fixed_provider", min_length=1, max_length=64)
    expires_at: str | None = Field(default=None, max_length=40)

    @property
    def digest_sha512(self) -> str:
        return _canonical_digest(self.model_dump(mode="json"))

    @property
    def has_established_revision(self) -> bool:
        return self.authority_revision >= 1

    @property
    def is_expired(self) -> bool:
        return is_expired(self.expires_at)


class DetectorRegistrySnapshot(ImmutableContract):
    registry_revision: int = Field(ge=0)
    registered_detector_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=64)
    scope: str = Field(default="process_local", min_length=1, max_length=64)
    source_class: str = Field(default="local_fixed_provider", min_length=1, max_length=64)
    expires_at: str | None = Field(default=None, max_length=40)

    @property
    def digest_sha512(self) -> str:
        return _canonical_digest(self.model_dump(mode="json"))

    @property
    def has_established_revision(self) -> bool:
        return self.registry_revision >= 1

    @property
    def is_expired(self) -> bool:
        return is_expired(self.expires_at)


class ActionRegistrySnapshot(ImmutableContract):
    registry_revision: int = Field(ge=0)
    registered_action_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=64)
    scope: str = Field(default="process_local", min_length=1, max_length=64)
    source_class: str = Field(default="local_fixed_provider", min_length=1, max_length=64)
    expires_at: str | None = Field(default=None, max_length=40)

    @property
    def digest_sha512(self) -> str:
        return _canonical_digest(self.model_dump(mode="json"))

    @property
    def has_established_revision(self) -> bool:
        return self.registry_revision >= 1

    @property
    def is_expired(self) -> bool:
        return is_expired(self.expires_at)
