"""Guardrail Point Runtime (architecture §4, P5-MOD-002..004).

`GuardrailPointRuntime.invoke()` is the single Mode-routing entry point
every Guardrail Point call goes through:

- `off`   — never calls a Detector, the Policy Provider or the Action
            Resolver; Detector/Policy/Action Call 0 (P5-MOD-002).
- `observe` — runs Detectors and Policy evaluation, records
              Recommendations, but never calls the Action Resolver, so
              `executed_actions` is always empty and Input/Output/
              Stream/Persistence stay unchanged (P5-MOD-003).
- `enforce` — additionally resolves and executes Registered Actions
              within the current Authority/Approval/Registry
              intersection (P5-MOD-004).

Binding Identity Capture (P5-CODEX-007 Rework, Codex Second Independent
Review): every Point evaluation captures Policy/Authority/
Detector-Registry/Action-Registry Snapshots exactly once, at entry, from
the caller-supplied Provider Ports — this single "entry Binding" is what
every Detection/Decision/Result in this invocation is stamped against.
Before ever executing an Action (`enforce` only), this module calls
every one of those same four Provider Ports a *second*, fully
independent time ("resolution Binding") and fails the whole invocation
closed as `binding_stale` the moment any Snapshot kind is Stale/Unknown
at that second read, or its Digest no longer matches the entry read.
For today's Local Fixed Providers the two reads are always identical —
the mechanism is exercised live on every real `enforce` call rather than
only by a Direct Resolver unit test, and a Synthetic Provider that
returns a *different* Snapshot on its second call (used by the Rework's
own Test Matrix) proves the Fail-closed path is genuinely reachable
through this Runtime and `GuardrailGovernanceComposition`, not merely
asserted in isolation (Codex Second Review Probes A/B: a
directly-constructed `revision=0` Snapshot must never let an Action
execute, previously true only when the caller happened to also pass a
matching `expected_authority_digest_sha512` — now true unconditionally,
because the Runtime itself re-derives both Bindings from the Provider
Ports rather than trusting whatever single Snapshot value it was
initially handed)."""

from __future__ import annotations

import time
from typing import Protocol

from ..domain import (
    ActionRegistryEntry,
    AuthorityDecision,
    AuthorityOutcome,
    ContextSourceUnit,
    DetectionOutcome,
    ExecutedAction,
    ExecutionState,
    GuardrailResult,
    PolicyApplicability,
    PolicyDecision,
    RecommendedAction,
    Severity,
)
from ..ports import (
    ActionRegistryPort,
    ApprovalPort,
    AuthorityProviderPort,
    DetectorPort,
    DetectorRegistryPort,
    GuardActionAdapterPort,
    PolicyProviderPort,
)
from .action_resolver import resolve as resolve_actions

_SEVERITY_ORDER = (Severity.NONE, Severity.LOW, Severity.MODERATE, Severity.HIGH, Severity.CRITICAL)

_BINDING_STALE_REASON_CODE = "binding_stale"


def _max_severity(values: list[Severity]) -> Severity:
    highest = Severity.NONE
    for value in values:
        if _SEVERITY_ORDER.index(value) > _SEVERITY_ORDER.index(highest):
            highest = value
    return highest


class _StalenessCheckable(Protocol):
    @property
    def has_established_revision(self) -> bool: ...

    @property
    def is_expired(self) -> bool: ...


def _registry_is_stale(snapshot: _StalenessCheckable) -> bool:
    """Shared Staleness predicate (P5-CODEX-007): `PolicySnapshot`,
    `AuthoritySnapshot`, `DetectorRegistrySnapshot` and
    `ActionRegistrySnapshot` all expose the identical
    `has_established_revision`/`is_expired` shape — one function checks
    all four rather than four near-duplicate call sites drifting apart."""

    return not snapshot.has_established_revision or snapshot.is_expired


class _ScopedSnapshot(Protocol):
    @property
    def scope(self) -> str: ...


def _scope_consistent(*snapshots: _ScopedSnapshot) -> bool:
    """P5-CODEX-007 Rework (Codex Third Independent Review Probe A/B): a
    Snapshot Set where one member's declared `scope` disagrees with the
    others is not a single, coherent Current Binding — it is at best two
    different Bindings glued together, and must never be treated as
    Current. A previously-fixed Local Provider set always trivially
    agrees (`"process_local"` on all four); a Synthetic Provider
    returning a genuinely foreign `scope` on just one of the four is
    exactly Probe A/B's construction."""

    return len({snapshot.scope for snapshot in snapshots}) <= 1


class _PolicySnapshotLike(Protocol):
    @property
    def policy_revision(self) -> int: ...

    @property
    def digest_sha512(self) -> str: ...


def _policy_decisions_bound_to_snapshot(
    policy_decisions: tuple[PolicyDecision, ...], policy_snapshot: _PolicySnapshotLike
) -> bool:
    """P5-CODEX-007 Rework (Codex Third Independent Review Probe C): a
    `PolicyDecision` is only trustworthy if its own stamped
    `policy_revision`/`policy_digest_sha512` (set by whatever Policy
    Provider produced it) actually matches the Entry Binding's own
    `PolicySnapshot` — a Provider that evaluates against one Policy
    Identity but *claims* a different one on the Decisions it hands back
    must never let those Decisions drive an Action."""

    return all(
        decision.policy_revision == policy_snapshot.policy_revision
        and decision.policy_digest_sha512 == policy_snapshot.digest_sha512
        for decision in policy_decisions
    )


class GuardrailPointRuntime:
    def __init__(self, *, detectors: tuple[DetectorPort, ...]) -> None:
        self._detectors = detectors

    def invoke(
        self,
        *,
        invocation_id: str,
        point_id: str,
        mode: str,
        content: str,
        policy_provider: PolicyProviderPort,
        authority_provider: AuthorityProviderPort,
        approval_port: ApprovalPort,
        action_registry_provider: ActionRegistryPort,
        detector_registry_provider: DetectorRegistryPort,
        registry: dict[str, ActionRegistryEntry],
        adapters: dict[str, GuardActionAdapterPort],
        content_sources: tuple[ContextSourceUnit, ...] | None = None,
    ) -> GuardrailResult:
        if mode == "off":
            return GuardrailResult(
                invocation_id=invocation_id,
                point_id=point_id,
                mode=mode,
                execution_state=ExecutionState.NOT_EVALUATED,
            )

        started = time.monotonic()
        # Entry Binding (P5-CODEX-007): captured exactly once, used for
        # every Detection/Decision/Result stamp below, and as the
        # Expected baseline the resolution-time independent re-fetch
        # (further down, `enforce` only) is compared against.
        policy_snapshot = policy_provider.snapshot()
        authority = authority_provider.snapshot()
        detector_registry = detector_registry_provider.snapshot()
        action_registry = action_registry_provider.snapshot()

        if content_sources is not None:
            # P5-CODEX-006 Rework: Source-unit judgment before any
            # collapse into a single string — each Detector scans each
            # Source's own `content` independently, never a joined
            # mega-string, so a Safe aggregate Decision is made *after*
            # per-Source Detection, not before it.
            detections = tuple(
                detector.detect(content=source.content)
                for source in content_sources
                for detector in self._detectors
            )
            content_length = sum(len(source.content) for source in content_sources)
        else:
            detections = tuple(detector.detect(content=content) for detector in self._detectors)
            content_length = len(content)
        policy_decisions = policy_provider.evaluate(point_id=point_id, detections=detections)

        # Entry Binding cross-checks (P5-CODEX-007 Rework, Codex Third
        # Independent Review Probes A/B/C): the Revision/Expiry/Digest
        # checks above only ever verified each Snapshot kind against
        # *itself* across two reads — never that the four Snapshots
        # actually agree with each other (`scope`), nor that any of them
        # actually describes the real Runtime it is supposedly Binding
        # (the real wired Detector ids, the real registered Action ids,
        # the real stamped Policy Identity on each Decision). A
        # Provider that returns the *same* self-consistent-but-wrong
        # Snapshot twice defeats the entry/resolution re-fetch alone —
        # these three checks close exactly that gap.
        actual_detector_ids = frozenset(detector.detector_id for detector in self._detectors)
        actual_action_ids = frozenset(registry.keys())
        entry_binding_mismatch = (
            not _scope_consistent(policy_snapshot, authority, detector_registry, action_registry)
            or actual_detector_ids != frozenset(detector_registry.registered_detector_ids)
            or actual_action_ids != frozenset(action_registry.registered_action_ids)
            or not _policy_decisions_bound_to_snapshot(policy_decisions, policy_snapshot)
        )

        recommended: list[RecommendedAction] = []
        for detection, decision in zip(detections, policy_decisions, strict=True):
            if decision.applicability is not PolicyApplicability.APPLICABLE:
                continue
            for action_id in decision.recommended_action_ids:
                recommended.append(
                    RecommendedAction(
                        action_id=action_id,
                        reason_detection_id=detection.detection_id,
                        severity=detection.severity,
                    )
                )

        severity = _max_severity(
            [d.severity for d in detections if d.outcome is DetectionOutcome.MATCH]
        )

        # P5-AUT-003/P5-CODEX-002 Rework: stamp one AuthorityDecision per
        # distinct recommended Action id so Evidence/Status can show
        # exactly which Authority Snapshot Identity (revision/scope/
        # digest) granted or denied it — never left unrecorded. A
        # Snapshot with no established Revision or an expired one is
        # `stale`/`unknown` here too, mirroring the Resolver's own
        # fail-closed check exactly rather than drifting from it.
        authority_current = authority.has_established_revision and not authority.is_expired
        authority_decisions = tuple(
            AuthorityDecision(
                action_id=action_id,
                outcome=(
                    AuthorityOutcome.STALE
                    if not authority_current
                    else (
                        AuthorityOutcome.GRANTED
                        if action_id in authority.granted_action_ids
                        else AuthorityOutcome.DENIED
                    )
                ),
                authority_revision=authority.authority_revision,
                scope=authority.scope,
                authority_digest_sha512=authority.digest_sha512,
            )
            for action_id in dict.fromkeys(item.action_id for item in recommended)
        )

        executed_actions: tuple[ExecutedAction, ...] = ()
        execution_state = ExecutionState.EVALUATED
        degraded_reason_code: str | None = None
        unavailable_reason_code: str | None = None

        if mode == "enforce":
            # Resolution Binding (P5-CODEX-007): a second, independent
            # `.snapshot()` call on every one of the same four Provider
            # Ports, immediately before Action Resolution — never the
            # Entry Binding object referenced a second time. Only if
            # this genuinely separate read still agrees with the Entry
            # Binding (content and Digest) does Resolution proceed.
            resolution_policy = policy_provider.snapshot()
            resolution_authority = authority_provider.snapshot()
            resolution_detector_registry = detector_registry_provider.snapshot()
            resolution_action_registry = action_registry_provider.snapshot()
            binding_stale = (
                entry_binding_mismatch
                or _registry_is_stale(resolution_policy)
                or _registry_is_stale(resolution_authority)
                or _registry_is_stale(resolution_detector_registry)
                or _registry_is_stale(resolution_action_registry)
                or resolution_policy.digest_sha512 != policy_snapshot.digest_sha512
                or resolution_detector_registry.digest_sha512 != detector_registry.digest_sha512
                or resolution_action_registry.digest_sha512 != action_registry.digest_sha512
            )
            executed_actions = resolve_actions(
                recommended_actions=tuple(recommended),
                point_id=point_id,
                mode=mode,
                detections=detections,
                content_length=content_length,
                policy_decisions=policy_decisions,
                authority=resolution_authority,
                approval_port=approval_port,
                action_registry=resolution_action_registry,
                registry=registry,
                adapters=adapters,
                expected_authority_digest_sha512=authority.digest_sha512,
                binding_stale=binding_stale,
                expected_scope=policy_snapshot.scope,
            )
            if binding_stale:
                execution_state = ExecutionState.UNAVAILABLE
                unavailable_reason_code = _BINDING_STALE_REASON_CODE
        else:
            # `observe` (P5-CODEX-007): Content Mutation stays 0
            # regardless (the Action Resolver is never called either
            # way), but a Stale/Unknown Binding must still surface as
            # genuinely Degraded Evidence rather than a plain
            # `evaluated` Result indistinguishable from a healthy read
            # (Codex Second Review "OBSERVEはStale/Unknownでも
            # evaluatedのままで、Degraded/Unavailable Evidenceへ
            # 収束しない").
            observe_stale = (
                entry_binding_mismatch
                or _registry_is_stale(policy_snapshot)
                or _registry_is_stale(authority)
                or _registry_is_stale(detector_registry)
                or _registry_is_stale(action_registry)
            )
            if observe_stale:
                execution_state = ExecutionState.DEGRADED
                degraded_reason_code = _BINDING_STALE_REASON_CODE

        latency_ms = max(0, round((time.monotonic() - started) * 1000))
        return GuardrailResult(
            invocation_id=invocation_id,
            point_id=point_id,
            mode=mode,
            execution_state=execution_state,
            degraded_reason_code=degraded_reason_code,
            unavailable_reason_code=unavailable_reason_code,
            detector_registry_digest_sha512=detector_registry.digest_sha512,
            policy_snapshot_digest_sha512=policy_snapshot.digest_sha512,
            authority_snapshot_digest_sha512=authority.digest_sha512,
            action_registry_digest_sha512=action_registry.digest_sha512,
            detections=detections,
            policy_decisions=policy_decisions,
            authority_decisions=authority_decisions,
            severity=severity,
            recommended_actions=tuple(recommended),
            executed_actions=executed_actions,
            latency_ms=latency_ms,
            call_count=0,
        )
