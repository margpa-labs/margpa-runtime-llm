"""Guardrail Action Resolver (architecture §4 ENFORCE, ADR-5-004/005/008).

Routing order (architecture §4):

```
detection
  -> policy applicability
  -> conflict resolution
  -> current authority
  -> approval state
  -> capability/budget (Registry allowed_points)
  -> registered action validation
  -> execute or typed not_executed
```

Terminal Conflict Resolution mirrors Phase 4's eligibility-first design
(P4-CODEX-010 lineage): every Terminal-class candidate's structural
eligibility (Policy-applicable, Authority-granted, Registered,
Point-allowed) is checked *before* a Severity-based winner is chosen —
never the first candidate found in iteration order.
"""

from __future__ import annotations

from ..domain import (
    NOT_EXECUTABLE_ACTION_IDS,
    ActionId,
    ActionRegistryEntry,
    ActionRegistrySnapshot,
    ApprovalOutcome,
    AuthoritySnapshot,
    ExecutedAction,
    GuardDetection,
    NotExecutedReason,
    PolicyApplicability,
    PolicyDecision,
    RecommendedAction,
    spans_are_verified,
)
from ..ports import ApprovalPort, GuardActionAdapterPort

_TERMINAL_ACTION_IDS = frozenset(
    {
        ActionId.REJECT_INPUT.value,
        ActionId.STOP_BEFORE_GENERATION.value,
        ActionId.SUPPRESS_STREAM_CANDIDATE.value,
        ActionId.REJECT_OUTPUT.value,
    }
)

_REDACT_ACTION_IDS = frozenset(
    {ActionId.REDACT_TYPED_SECRET.value, ActionId.REDACT_TYPED_PII.value}
)

_INTERVENING_ACTION_IDS = _TERMINAL_ACTION_IDS | _REDACT_ACTION_IDS


def _intervening(action_id: str) -> bool:
    return action_id in _INTERVENING_ACTION_IDS


def _not_executed(action_id: str, reason: NotExecutedReason) -> ExecutedAction:
    return ExecutedAction(
        action_id=action_id,
        executed=False,
        intervening=False,
        not_executed_reason_code=reason.value,
    )


def _severity_rank(severity: object) -> int:
    order = {"none": 0, "low": 1, "moderate": 2, "high": 3, "critical": 4}
    return order.get(getattr(severity, "value", str(severity)), 0)


def _policy_recommends(
    action_id: str, *, policy_decisions: tuple[PolicyDecision, ...]
) -> PolicyDecision | None:
    for decision in policy_decisions:
        if decision.applicability is PolicyApplicability.APPLICABLE and (
            action_id in decision.recommended_action_ids
        ):
            return decision
    return None


def _authority_is_current(authority: AuthoritySnapshot) -> bool:
    """P5-AUT-003/P5-CODEX-002 Rework: a Snapshot with no established
    Revision (`0`, "never established") or a past `expires_at` must
    never be treated as a valid grant, regardless of what
    `granted_action_ids` otherwise claims."""

    return authority.has_established_revision and not authority.is_expired


def _is_eligible(
    action_id: str,
    *,
    point_id: str,
    policy_decisions: tuple[PolicyDecision, ...],
    authority: AuthoritySnapshot,
    registry: dict[str, ActionRegistryEntry],
    adapters: dict[str, GuardActionAdapterPort],
) -> bool:
    """Structural eligibility only — Policy-applicable, Authority-
    granted, Registered, Point-allowed, Adapter-present. Never attempts
    execution; used solely to decide which Terminal candidate, if any,
    is even in contention before Severity breaks the tie."""

    if action_id in NOT_EXECUTABLE_ACTION_IDS:
        return False
    try:
        ActionId(action_id)
    except ValueError:
        return False
    if _policy_recommends(action_id, policy_decisions=policy_decisions) is None:
        return False
    if not _authority_is_current(authority) or action_id not in authority.granted_action_ids:
        return False
    entry = registry.get(action_id)
    if entry is None or point_id not in entry.allowed_points:
        return False
    return action_id in adapters


def resolve(
    *,
    recommended_actions: tuple[RecommendedAction, ...],
    point_id: str,
    mode: str,
    detections: tuple[GuardDetection, ...],
    content_length: int,
    policy_decisions: tuple[PolicyDecision, ...],
    authority: AuthoritySnapshot,
    approval_port: ApprovalPort,
    action_registry: ActionRegistrySnapshot,
    registry: dict[str, ActionRegistryEntry],
    adapters: dict[str, GuardActionAdapterPort],
    expected_authority_digest_sha512: str | None = None,
    binding_stale: bool = False,
    expected_scope: str | None = None,
) -> tuple[ExecutedAction, ...]:
    """`expected_authority_digest_sha512` (P5-AUT-003/P5-CODEX-002
    Rework): an optional pinned Authority Identity a caller captured
    earlier (e.g. at Policy-evaluation time) — when supplied and it no
    longer matches the *live* `authority.digest_sha512` passed into this
    same call, the Authority Snapshot backing this Resolution has
    genuinely changed identity since it was captured, and every
    candidate Action fails closed as `binding_stale` rather than
    silently resolving against whichever Snapshot happened to arrive.
    `None` (the default) means no cross-check was requested, preserving
    every pre-existing caller's behavior exactly.

    `binding_stale` (P5-CODEX-007, Codex Second Independent Review): the
    caller (`GuardrailPointRuntime.invoke()`) independently re-fetches
    Policy/Detector-Registry/Action-Registry Snapshots a second time,
    right before this call, from the same Provider Ports used to
    capture the entry-time Binding — `binding_stale=True` means that
    second, independent fetch came back Stale/Unknown/Expired or with a
    changed Digest versus the entry-time capture, for *any* of those
    four Snapshot kinds (not only Authority, which
    `expected_authority_digest_sha512` above already covers on its
    own), or that the Entry Binding's own internal cross-checks (Scope
    consistency, real Detector/Action id-set agreement, Policy Decision
    Stamp agreement — P5-CODEX-007 Codex Third Independent Review)
    already failed. This is deliberately a plain `bool` rather than
    every underlying Snapshot pair threaded through this function's
    signature — the caller owns the comparison, this function only owns
    the fail-closed consequence, exactly like
    `expected_authority_digest_sha512` already does for Authority alone.

    `expected_scope` (P5-CODEX-007, Codex Third Independent Review item
    5): the Entry Binding's own agreed `scope` (already Scope-consistency-
    checked by the caller) — an `ApprovalState` whose own `scope` doesn't
    match is Bound to a different Scope than the rest of this
    Resolution's Binding and must never be treated as a live grant
    either, mirroring the Authority/Registry Scope discipline exactly."""

    if mode != "enforce":
        return tuple(
            _not_executed(item.action_id, NotExecutedReason.MODE_NOT_ENFORCE)
            for item in recommended_actions
        )
    if not action_registry.registered_action_ids or not authority.granted_action_ids:
        return tuple(
            _not_executed(item.action_id, NotExecutedReason.BINDING_UNAVAILABLE)
            for item in recommended_actions
        )
    if (
        binding_stale
        or not _authority_is_current(authority)
        or (
            expected_authority_digest_sha512 is not None
            and expected_authority_digest_sha512 != authority.digest_sha512
        )
    ):
        return tuple(
            _not_executed(item.action_id, NotExecutedReason.BINDING_STALE)
            for item in recommended_actions
        )

    deduplicated: dict[str, RecommendedAction] = {}
    for item in recommended_actions:
        existing = deduplicated.get(item.action_id)
        if existing is None or _severity_rank(item.severity) > _severity_rank(existing.severity):
            deduplicated[item.action_id] = item

    detections_by_id = {detection.detection_id: detection for detection in detections}

    terminal_candidates = [aid for aid in deduplicated if aid in _TERMINAL_ACTION_IDS]
    eligible_terminals = [
        aid
        for aid in terminal_candidates
        if _is_eligible(
            aid,
            point_id=point_id,
            policy_decisions=policy_decisions,
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
            conflict_unresolved_ids = set(tied)

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
        item = deduplicated[action_id]
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
        policy_decision = _policy_recommends(action_id, policy_decisions=policy_decisions)
        if policy_decision is None:
            results.append(_not_executed(action_id, NotExecutedReason.POLICY_NOT_APPLICABLE))
            continue
        if not _authority_is_current(authority):
            results.append(_not_executed(action_id, NotExecutedReason.BINDING_STALE))
            continue
        if action_id not in authority.granted_action_ids:
            results.append(_not_executed(action_id, NotExecutedReason.AUTHORITY_MISSING))
            continue
        if policy_decision.approval_required:
            approval = approval_port.state_for(action_id=action_id)
            if approval.outcome is ApprovalOutcome.PENDING:
                results.append(_not_executed(action_id, NotExecutedReason.APPROVAL_PENDING))
                continue
            if approval.outcome is not ApprovalOutcome.APPROVED:
                results.append(_not_executed(action_id, NotExecutedReason.APPROVAL_MISSING))
                continue
            # P5-CODEX-007 Rework: an `approved` Outcome from a Stale or
            # never-Established `ApprovalState` (Revision `0`, or a past
            # `expires_at`) must never be treated as a live grant either
            # — mirrors `_authority_is_current()` exactly, applied to
            # Approval instead of Authority.
            if not approval.has_established_revision or approval.is_expired:
                results.append(_not_executed(action_id, NotExecutedReason.APPROVAL_MISSING))
                continue
            # P5-CODEX-007 Rework (Codex Third Independent Review item
            # 5): an `ApprovalState` Bound to a different Scope than the
            # rest of this Resolution's Binding is not a grant for *this*
            # Binding either, even if otherwise Current.
            if expected_scope is not None and approval.scope != expected_scope:
                results.append(_not_executed(action_id, NotExecutedReason.APPROVAL_MISSING))
                continue
        entry = registry.get(action_id)
        if entry is None:
            results.append(_not_executed(action_id, NotExecutedReason.ACTION_NOT_REGISTERED))
            continue
        if point_id not in entry.allowed_points:
            results.append(_not_executed(action_id, NotExecutedReason.ACTION_NOT_ALLOWED_AT_POINT))
            continue
        if action_id in _REDACT_ACTION_IDS:
            detection = (
                detections_by_id.get(item.reason_detection_id)
                if item.reason_detection_id is not None
                else None
            )
            spans = detection.typed_spans if detection is not None else ()
            if not spans or not spans_are_verified(spans, content_length=content_length):
                results.append(_not_executed(action_id, NotExecutedReason.SPAN_UNVERIFIED))
                continue
        adapter = adapters.get(action_id)
        if adapter is None:
            results.append(_not_executed(action_id, NotExecutedReason.ACTION_NOT_REGISTERED))
            continue
        try:
            executed = adapter.execute(action_id=typed_action_id.value, point_id=point_id)
        except Exception:
            results.append(_not_executed(action_id, NotExecutedReason.ADAPTER_FAILURE))
            continue
        if executed.executed and executed.intervening != _intervening(action_id):
            results.append(_not_executed(action_id, NotExecutedReason.ADAPTER_FAILURE))
            continue
        results.append(executed)
    return tuple(results)
