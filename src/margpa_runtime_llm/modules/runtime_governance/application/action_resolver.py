"""Action Resolver (architecture §4 ENFORCE, P4-E-WU-001/003, ADR-4-005,
P4-CODEX-006/010 Rework).

Routing order is fixed (architecture §4):

```
conflict resolution
  -> mode
  -> authority / policy
  -> capability
  -> budget
  -> registered adapter validation
  -> execute or explicit not_executed reason
```

Every step that fails closes the loop with a Typed `NotExecutedReason` —
never a silent skip and never a raised exception for a routine refusal.
`capability`/`policy`/`budget`/`authority` are re-verified as one
Binding-staleness check: this Resolve call happens *after* the Binding
was cached, so the live Capability/Authority/Policy/Budget/Registry
Snapshot may have moved on since Bind time (architecture §9) — a real,
honest MVP substance for those routing steps, not a placeholder that
always passes (P4-CODEX-010: Authority Revision/Grant-set changes now
invalidate a cached Binding exactly like the other four dimensions did
already).

Terminal Conflict Resolution (P4-CODEX-010 Rework) evaluates every
Terminal-class candidate (`stop_before_generation`/`reject_output`) for
Point/Stage/Registry/Authority *eligibility* before choosing a winner by
Severity — never the first Terminal candidate found in iteration order.
An ineligible Terminal candidate keeps its own genuine rejection reason
(it was never going to execute regardless) rather than being mislabeled
`superseded` by a winner it never actually competed with.
"""

from __future__ import annotations

from ..domain import (
    NOT_EXECUTABLE_ACTION_IDS,
    ActionId,
    ActionRegistryEntry,
    ActionRegistrySnapshot,
    AuthoritySnapshot,
    BoundGovernancePlan,
    BudgetSnapshot,
    ExecutedAction,
    NotExecutedReason,
    PolicySnapshot,
    RecommendedAction,
    RuntimeCapabilitySnapshot,
)
from ..ports import ActionAdapterPort

# Actions that definitively end the flow before/at this Point — once one
# fires, every other recommended Action in the same Invocation is moot
# (architecture §4 "conflict resolution" step). Non-terminal Actions
# (`warn`, `constrain_generation_config`, `recommend_only`, `pass`) never
# suppress each other; only a Terminal Action supersedes.
_TERMINAL_ACTION_IDS = frozenset(
    {ActionId.STOP_BEFORE_GENERATION.value, ActionId.REJECT_OUTPUT.value}
)

_INTERVENING_ACTION_IDS = frozenset(
    {
        ActionId.STOP_BEFORE_GENERATION.value,
        ActionId.REJECT_OUTPUT.value,
        ActionId.CONSTRAIN_GENERATION_CONFIG.value,
    }
)


def _intervening(action_id: str) -> bool:
    return action_id in _INTERVENING_ACTION_IDS


def _not_executed(action_id: str, reason: NotExecutedReason) -> ExecutedAction:
    return ExecutedAction(
        action_id=action_id,
        executed=False,
        intervening=False,
        not_executed_reason_code=reason.value,
    )


def _binding_is_stale(
    binding: BoundGovernancePlan,
    *,
    capability: RuntimeCapabilitySnapshot,
    authority: AuthoritySnapshot,
    policy: PolicySnapshot,
    budget: BudgetSnapshot,
    registry: ActionRegistrySnapshot,
) -> bool:
    return (
        binding.capability_snapshot_digest_sha512 != capability.digest_sha512
        or binding.authority_snapshot_digest_sha512 != authority.digest_sha512
        or binding.policy_snapshot_digest_sha512 != policy.digest_sha512
        or binding.budget_snapshot_digest_sha512 != budget.digest_sha512
        or binding.action_registry_digest_sha512 != registry.digest_sha512
    )


def _is_eligible(
    action_id: str,
    *,
    point_id: str,
    stage: str,
    authority: AuthoritySnapshot,
    registry: dict[str, ActionRegistryEntry],
    adapters: dict[str, ActionAdapterPort],
) -> bool:
    """Structural eligibility only — Point/Stage/Registry/Authority
    membership. Does not attempt Adapter execution (a runtime concern
    checked later); used solely to decide which Terminal candidate, if
    any, is even in contention before Severity breaks the tie."""

    if action_id in NOT_EXECUTABLE_ACTION_IDS:
        return False
    try:
        ActionId(action_id)
    except ValueError:
        return False
    if action_id not in authority.granted_action_ids:
        return False
    entry = registry.get(action_id)
    if entry is None:
        return False
    if point_id not in entry.allowed_points or stage not in entry.allowed_stages:
        return False
    return action_id in adapters


def resolve(
    *,
    recommended_actions: tuple[RecommendedAction, ...],
    point_id: str,
    stage: str,
    mode: str,
    binding: BoundGovernancePlan,
    capability: RuntimeCapabilitySnapshot,
    authority: AuthoritySnapshot,
    policy: PolicySnapshot,
    budget: BudgetSnapshot,
    action_registry: ActionRegistrySnapshot,
    registry: dict[str, ActionRegistryEntry],
    adapters: dict[str, ActionAdapterPort],
) -> tuple[ExecutedAction, ...]:
    if mode != "enforce":
        return tuple(
            _not_executed(item.action_id, NotExecutedReason.MODE_NOT_ENFORCE)
            for item in recommended_actions
        )
    if not binding.executable:
        return tuple(
            _not_executed(item.action_id, NotExecutedReason.BINDING_UNAVAILABLE)
            for item in recommended_actions
        )

    # Highest Severity recommendation for a given Action wins when the
    # same Action is recommended more than once in this Invocation
    # (architecture §30 axis 4 "Safety Criticality") — a simple, explicit
    # Conflict Rule rather than an unresolved duplicate execution.
    deduplicated: dict[str, RecommendedAction] = {}
    for item in recommended_actions:
        existing = deduplicated.get(item.action_id)
        if existing is None or _severity_rank(item.severity) > _severity_rank(existing.severity):
            deduplicated[item.action_id] = item

    if _binding_is_stale(
        binding,
        capability=capability,
        authority=authority,
        policy=policy,
        budget=budget,
        registry=action_registry,
    ):
        return tuple(
            _not_executed(action_id, NotExecutedReason.BINDING_STALE) for action_id in deduplicated
        )

    # Terminal Conflict Resolution (P4-CODEX-010): evaluate every Terminal
    # candidate's structural eligibility *before* Severity chooses a
    # winner — never the first one found in iteration/insertion order.
    terminal_candidates = [
        action_id for action_id in deduplicated if action_id in _TERMINAL_ACTION_IDS
    ]
    eligible_terminals = [
        action_id
        for action_id in terminal_candidates
        if _is_eligible(
            action_id,
            point_id=point_id,
            stage=stage,
            authority=authority,
            registry=registry,
            adapters=adapters,
        )
    ]
    terminal_action_id: str | None = None
    conflict_unresolved_ids: set[str] = set()
    if len(eligible_terminals) == 1:
        terminal_action_id = eligible_terminals[0]
    elif len(eligible_terminals) >= 2:
        top_rank = max(_severity_rank(deduplicated[aid].severity) for aid in eligible_terminals)
        tied = [
            aid
            for aid in eligible_terminals
            if _severity_rank(deduplicated[aid].severity) == top_rank
        ]
        if len(tied) == 1:
            terminal_action_id = tied[0]
        else:
            # Two-or-more eligible Terminal candidates at the same
            # Severity — genuinely undecidable, never let iteration
            # order silently pick one (architecture §4 "conflict
            # resolution"). Every tied candidate is Action 0.
            conflict_unresolved_ids = set(tied)

    # Only actions that a winning Terminal genuinely supersedes — every
    # non-Terminal candidate, plus any *eligible* (but lower-Severity)
    # Terminal candidate. An *ineligible* Terminal candidate (wrong
    # Point/Stage, unauthorized, unregistered) was never in contention
    # and keeps its own genuine rejection reason below, rather than being
    # mislabeled `superseded` by a winner it never competed with.
    superseded_ids: set[str] = set()
    if terminal_action_id is not None:
        for action_id in deduplicated:
            if action_id == terminal_action_id:
                continue
            if action_id in _TERMINAL_ACTION_IDS and action_id not in eligible_terminals:
                continue
            superseded_ids.add(action_id)

    results: list[ExecutedAction] = []
    for action_id in deduplicated:
        if action_id in conflict_unresolved_ids:
            results.append(_not_executed(action_id, NotExecutedReason.CONFLICT_UNRESOLVED))
            continue
        if action_id in superseded_ids:
            results.append(
                _not_executed(action_id, NotExecutedReason.SUPERSEDED_BY_HIGHER_PRIORITY_ACTION)
            )
            continue
        if action_id in NOT_EXECUTABLE_ACTION_IDS:
            results.append(_not_executed(action_id, NotExecutedReason.NOT_EXECUTABLE_ACTION_CLASS))
            continue
        try:
            typed_action_id = ActionId(action_id)
        except ValueError:
            results.append(_not_executed(action_id, NotExecutedReason.ACTION_NOT_REGISTERED))
            continue
        if action_id not in authority.granted_action_ids:
            results.append(_not_executed(action_id, NotExecutedReason.AUTHORITY_MISSING))
            continue
        entry = registry.get(action_id)
        if entry is None:
            results.append(_not_executed(action_id, NotExecutedReason.ACTION_NOT_REGISTERED))
            continue
        if point_id not in entry.allowed_points or stage not in entry.allowed_stages:
            results.append(_not_executed(action_id, NotExecutedReason.ACTION_NOT_ALLOWED_AT_POINT))
            continue
        adapter = adapters.get(action_id)
        if adapter is None:
            results.append(_not_executed(action_id, NotExecutedReason.ACTION_NOT_REGISTERED))
            continue
        try:
            executed = adapter.execute(
                action_id=typed_action_id.value, point_id=point_id, stage=stage
            )
        except Exception:
            results.append(_not_executed(action_id, NotExecutedReason.ADAPTER_FAILURE))
            continue
        if executed.executed and executed.intervening != _intervening(action_id):
            # An Adapter must never misreport whether it actually changed
            # Model I/O/Config/Persistence — treat a mismatched claim as a
            # Fault, not as executed success (P4-PNT-006).
            results.append(_not_executed(action_id, NotExecutedReason.ADAPTER_FAILURE))
            continue
        results.append(executed)
    return tuple(results)


def _severity_rank(severity: object) -> int:
    order = {"none": 0, "low": 1, "moderate": 2, "high": 3, "critical": 4}
    return order.get(getattr(severity, "value", str(severity)), 0)
