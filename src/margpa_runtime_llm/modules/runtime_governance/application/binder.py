"""Governance Binder (architecture §3.1, P4-B-WU-001..003).

`bind()` never mutates or re-saves the Phase 3 Unbound Plan (P4-BND-001)
— it only reads the caller-supplied digests/descriptors and produces a
new, content-addressed `BoundGovernancePlan`. The Binding's own identity
*is* its digest (`binding_id == binding_digest_sha512`), so an identical
set of inputs always yields the identical Binding — which is exactly
what `BoundGovernancePlanCache` uses as its Cache Key (P4-BND-003: any
changed Integrity Input produces a different digest, never a stale hit).
"""

from __future__ import annotations

import threading

from ..domain import (
    ActionRegistrySnapshot,
    AuthoritySnapshot,
    BoundGovernancePlan,
    BudgetSnapshot,
    ExecutionDescriptor,
    PolicySnapshot,
    RuntimeCapabilitySnapshot,
    binding_digest_sha512,
    binding_payload_for_digest,
)


def bind(
    *,
    point_id: str,
    source_plan_id: str | None,
    source_plan_digest_sha512: str | None,
    descriptors: tuple[ExecutionDescriptor, ...],
    capability: RuntimeCapabilitySnapshot,
    authority: AuthoritySnapshot,
    policy: PolicySnapshot,
    budget: BudgetSnapshot,
    action_registry: ActionRegistrySnapshot,
    descriptor_unavailable_reason_code: str | None = None,
) -> BoundGovernancePlan:
    selected_ids = tuple(descriptor.descriptor_id for descriptor in descriptors)
    unresolved = tuple(
        descriptor.descriptor_id
        for descriptor in descriptors
        if descriptor.recommended_action_id is not None
        and descriptor.recommended_action_id not in action_registry.registered_action_ids
    )
    # P4-CODEX-008: non-empty Descriptors alone is not enough — without a
    # real Phase 3 Source Plan Identity behind them, there is nothing a
    # Binding could ever be traced back to (P4-CODEX-007/008), so such a
    # Binding must stay non-Executable exactly like the empty-Descriptor
    # case does.
    has_source_plan = source_plan_id is not None and source_plan_digest_sha512 is not None
    # P4-B-WU-003/P4-CODEX-004: Unknown Rule/Action, missing Dependency,
    # unresolved Conflict, or *zero* validated Descriptors must never be
    # treated as Executable — a Binding with nothing bound to enforce is
    # exactly the `Definitions 0 + enforce: unsupported / mutation 0` and
    # `Invalid Bundle + enforce: unavailable` Frozen Acceptance Matrix
    # rows, not a green light for Core-only structural Actions to fire.
    executable = (
        bool(descriptors)
        and has_source_plan
        and bool(action_registry.registered_action_ids)
        and bool(authority.granted_action_ids)
        and not unresolved
    )
    unavailable_reason_code: str | None = None
    if not executable:
        if not descriptors:
            # `descriptor_unavailable_reason_code` lets a Composition Root
            # (which knows *why* — Provider absent, Provider failure, or
            # an Invalid/Quarantined Bundle) refine this beyond the
            # generic default, without Core importing any Definition-
            # specific vocabulary itself (ADR-4-006/P4-BND-005) — the
            # string is opaque to `bind()`, just passed through.
            unavailable_reason_code = descriptor_unavailable_reason_code or "no_definitions"
        elif not has_source_plan:
            unavailable_reason_code = "no_source_plan"
        elif unresolved:
            unavailable_reason_code = "unresolved_dependency"
        else:
            unavailable_reason_code = "registry_or_authority_empty"
    payload = binding_payload_for_digest(
        point_id=point_id,
        source_plan_id=source_plan_id,
        source_plan_digest_sha512=source_plan_digest_sha512,
        selected_descriptor_ids=selected_ids,
        capability_snapshot_digest_sha512=capability.digest_sha512,
        authority_snapshot_digest_sha512=authority.digest_sha512,
        policy_snapshot_digest_sha512=policy.digest_sha512,
        budget_snapshot_digest_sha512=budget.digest_sha512,
        action_registry_digest_sha512=action_registry.digest_sha512,
        unresolved_descriptor_ids=unresolved,
        executable=executable,
        unavailable_reason_code=unavailable_reason_code,
    )
    digest = binding_digest_sha512(payload)
    return BoundGovernancePlan(
        binding_id=digest,
        point_id=point_id,
        source_plan_id=source_plan_id,
        source_plan_digest_sha512=source_plan_digest_sha512,
        selected_descriptor_ids=selected_ids,
        capability_snapshot_digest_sha512=capability.digest_sha512,
        authority_snapshot_digest_sha512=authority.digest_sha512,
        policy_snapshot_digest_sha512=policy.digest_sha512,
        budget_snapshot_digest_sha512=budget.digest_sha512,
        action_registry_digest_sha512=action_registry.digest_sha512,
        unresolved_descriptor_ids=unresolved,
        executable=executable,
        unavailable_reason_code=unavailable_reason_code,
        binding_digest_sha512=digest,
    )


class BoundGovernancePlanCache:
    """Process-local cache keyed by the Binding's own content digest — a
    Cache Hit is only ever a byte-identical `bind()` result, so re-binding
    on a cache hit and returning the cached value are indistinguishable
    to a caller (P4-BND-003)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._entries: dict[str, BoundGovernancePlan] = {}

    def get(self, digest: str) -> BoundGovernancePlan | None:
        with self._lock:
            return self._entries.get(digest)

    def put(self, plan: BoundGovernancePlan) -> None:
        with self._lock:
            self._entries[plan.binding_digest_sha512] = plan

    def size(self) -> int:
        with self._lock:
            return len(self._entries)

    def clear(self) -> None:
        with self._lock:
            self._entries.clear()
