"""Typed, digest-bearing Snapshots consumed by the Governance Binder
(architecture §3.1/§9, P4-BND-002).

Each Snapshot is a finite Typed Allowlist of exactly the fields the
Binder/Point Runtime need — never an arbitrary Runtime object dump. Every
Snapshot exposes a canonical `digest_sha512` so `BoundGovernancePlan`'s
Cache Key can include it directly (P4-BND-003: any change to any input
invalidates a stale Binding, never silently reused).
"""

from __future__ import annotations

import hashlib
import json

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


def _canonical_digest(payload: object) -> str:
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()


class RuntimeCapabilitySnapshot(ImmutableContract):
    """What the currently loaded Model/Backend can actually do."""

    model_key: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    backend_kind: str = Field(min_length=1, max_length=64, pattern=_IDENTIFIER_PATTERN)
    supports_streaming: bool
    supports_thinking: bool
    max_context_tokens: int = Field(ge=0)

    @property
    def digest_sha512(self) -> str:
        return _canonical_digest(self.model_dump(mode="json"))


class AuthoritySnapshot(ImmutableContract):
    """What Actions this process is currently permitted to Execute.

    Authority is granted by this Snapshot, never inferred from a
    Definition or Model output — `executable=true` on a Binding still
    means nothing without a matching grant here at Invocation time.
    """

    authority_revision: int = Field(ge=0)
    granted_action_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=64)

    @property
    def digest_sha512(self) -> str:
        return _canonical_digest(self.model_dump(mode="json"))


class PolicySnapshot(ImmutableContract):
    policy_revision: int = Field(ge=0)
    profile: str = Field(min_length=1, max_length=64, pattern=_IDENTIFIER_PATTERN)

    @property
    def digest_sha512(self) -> str:
        return _canonical_digest(self.model_dump(mode="json"))


class BudgetSnapshot(ImmutableContract):
    max_calls_per_invocation: int = Field(ge=0)
    max_latency_ms: int = Field(ge=0)
    max_snapshot_chars: int = Field(ge=0)
    allowed_generation_config_fields: tuple[str, ...] = Field(default_factory=tuple, max_length=32)

    @property
    def digest_sha512(self) -> str:
        return _canonical_digest(self.model_dump(mode="json"))


class ActionRegistrySnapshot(ImmutableContract):
    registry_revision: int = Field(ge=0)
    registered_action_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=64)

    @property
    def digest_sha512(self) -> str:
        return _canonical_digest(self.model_dump(mode="json"))
