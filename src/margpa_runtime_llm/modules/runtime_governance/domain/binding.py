"""Bound Governance Plan (architecture §3.1, ADR-4-003, P4-BND-001..004).

An Immutable Artifact distinct from Phase 3's Unbound Compiled Plan —
Binding never mutates or re-saves the Unbound Plan (P4-BND-001); it is a
new derived object keyed by every Integrity Input whose change must
invalidate a stale Bind (P4-BND-003).
"""

from __future__ import annotations

import hashlib
import json

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
_SHA512_HEX_PATTERN = r"^[0-9a-f]{128}$"


class BoundGovernancePlan(ImmutableContract):
    binding_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    point_id: str = Field(min_length=1, max_length=128)
    source_plan_id: str | None = Field(default=None, max_length=128, pattern=_IDENTIFIER_PATTERN)
    source_plan_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    selected_descriptor_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=4096)
    capability_snapshot_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)
    authority_snapshot_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)
    policy_snapshot_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)
    budget_snapshot_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)
    action_registry_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)
    unresolved_descriptor_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=4096)
    # `executable=true` is not a blanket safety claim (architecture §3.1) —
    # every Invocation still re-checks live Mode/Authority/Capability/Budget.
    executable: bool
    # Populated whenever `executable=False` — Typed, Safe-projectable
    # (e.g. `no_definitions`, `invalid_bundle`, `unresolved_dependency`),
    # never a raw exception or Definition-specific vocabulary (P4-CODEX-004).
    unavailable_reason_code: str | None = Field(default=None, max_length=64)
    binding_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)


def binding_payload_for_digest(
    *,
    point_id: str,
    source_plan_id: str | None,
    source_plan_digest_sha512: str | None,
    selected_descriptor_ids: tuple[str, ...],
    capability_snapshot_digest_sha512: str,
    authority_snapshot_digest_sha512: str,
    policy_snapshot_digest_sha512: str,
    budget_snapshot_digest_sha512: str,
    action_registry_digest_sha512: str,
    unresolved_descriptor_ids: tuple[str, ...],
    executable: bool,
    unavailable_reason_code: str | None = None,
) -> dict[str, object]:
    return {
        "point_id": point_id,
        "source_plan_id": source_plan_id,
        "source_plan_digest_sha512": source_plan_digest_sha512,
        "selected_descriptor_ids": sorted(selected_descriptor_ids),
        "capability_snapshot_digest_sha512": capability_snapshot_digest_sha512,
        "authority_snapshot_digest_sha512": authority_snapshot_digest_sha512,
        "policy_snapshot_digest_sha512": policy_snapshot_digest_sha512,
        "budget_snapshot_digest_sha512": budget_snapshot_digest_sha512,
        "action_registry_digest_sha512": action_registry_digest_sha512,
        "unresolved_descriptor_ids": sorted(unresolved_descriptor_ids),
        "executable": executable,
        # P4-CODEX-008: `no_provider`/`provider_failure`/`invalid_bundle`
        # all produce identical empty Descriptors/Digests otherwise —
        # without this field they collide on the same Binding Digest,
        # violating "any changed Integrity Input invalidates a stale
        # Binding" (P4-BND-002/003).
        "unavailable_reason_code": unavailable_reason_code,
    }


def binding_digest_sha512(payload: dict[str, object]) -> str:
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()
