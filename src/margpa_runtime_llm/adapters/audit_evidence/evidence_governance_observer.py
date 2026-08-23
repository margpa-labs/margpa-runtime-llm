"""`GovernanceObserverPort` adapter that appends to an Evidence Store
(P4-EVD-001, P4-CODEX-003 Rework, mirrors `evidence_generation_observer.
py`'s established P3-CODEX-002 pattern).

Every public method swallows all exceptions internally — construction
failure, a rejected payload, and any Evidence Store write failure alike.
An Evidence Write failure degrades the Evidence Store, never the
Governance Point's own Stop/Reject decision; this adapter is the
boundary that turns "the store raised" into "nothing observably
happened" from the Governance Point's perspective.

Uses its own `scope` (`_EVIDENCE_SCOPE`), separate from the Generation
Observer's `web_preview` scope, so a write failure on one side never
degrades the other (`LocalJsonlEvidenceStore`'s `_active_segment_
degraded` flag is per-instance and never clears without a restart).

`mode_provider` mirrors the Generation Observer's own binding: a
Callable, not a `GovernanceMode` import, so this adapter stays decoupled
from `runtime_governance`'s domain types. `observe_point_started`/
`observe_point_terminal` themselves never re-check Mode per call — only
the caller's binding-time `is_active()` check gates whether an
Invocation is observed at all, mirroring P3-CODEX-002's rationale.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditCorrelationKind,
    AuditCorrelationRef,
    AuditEventEnvelope,
    AuditEventId,
    AuditEventKind,
    AuditEventProvenance,
    AuditRunId,
    GovernancePointStartedPayload,
    GovernancePointTerminalPayload,
    SafeExecutedActionRecord,
    SafeObservationRecord,
    SafeRecommendedActionRecord,
    canonicalize_event,
)
from margpa_runtime_llm.modules.audit_evidence.governance_observation import (
    GovernanceObserverStatus,
)
from margpa_runtime_llm.modules.audit_evidence.ports import EvidenceStorePort

_ACTIVE_MODES = frozenset({"observe", "enforce"})
_DEGRADED_REASON_CODE = "evidence_write_failed"


class EvidenceGovernanceObserver:
    def __init__(
        self,
        *,
        store_factory: Callable[[], EvidenceStorePort],
        run_id: AuditRunId,
        source_component: str,
        mode_provider: Callable[[], str],
    ) -> None:
        self._store_factory = store_factory
        self._store: EvidenceStorePort | None = None
        self._store_lock = threading.Lock()
        self._run_id = run_id
        self._source_component = source_component
        self._mode_provider = mode_provider
        self._status_lock = threading.Lock()
        self._degraded = False
        self._degraded_event_count = 0

    def is_active(self) -> bool:
        try:
            return self._mode_provider() in _ACTIVE_MODES
        except Exception:
            return False

    def status(self) -> GovernanceObserverStatus:
        with self._status_lock:
            return GovernanceObserverStatus(
                degraded=self._degraded,
                degraded_reason_code=_DEGRADED_REASON_CODE if self._degraded else None,
                degraded_event_count=self._degraded_event_count,
            )

    def observe_point_started(
        self, *, invocation_id: str, point_id: str, stage: str, mode: str
    ) -> None:
        try:
            self._append(
                event_kind=AuditEventKind.GOVERNANCE_POINT_STARTED,
                payload=GovernancePointStartedPayload(point_id=point_id, stage=stage, mode=mode),
                invocation_id=invocation_id,
            )
        except Exception:
            self._mark_degraded()

    def observe_point_terminal(
        self,
        *,
        invocation_id: str,
        point_id: str,
        stage: str,
        mode: str,
        execution_state: str,
        severity: str,
        selected_descriptor_ids: tuple[str, ...],
        observations: tuple[SafeObservationRecord, ...],
        recommended_actions: tuple[SafeRecommendedActionRecord, ...],
        executed_actions: tuple[SafeExecutedActionRecord, ...],
        unavailable_reason_code: str | None,
        degraded_reason_code: str | None,
        binding_digest_sha512: str | None,
        source_plan_id: str | None,
        source_plan_digest_sha512: str | None,
        capability_snapshot_digest_sha512: str | None,
        authority_snapshot_digest_sha512: str | None,
        policy_snapshot_digest_sha512: str | None,
        budget_snapshot_digest_sha512: str | None,
        action_registry_digest_sha512: str | None,
        latency_ms: int,
        call_count: int,
    ) -> None:
        try:
            self._append(
                event_kind=AuditEventKind.GOVERNANCE_POINT_TERMINAL,
                payload=GovernancePointTerminalPayload(
                    point_id=point_id,
                    stage=stage,
                    mode=mode,
                    execution_state=execution_state,
                    severity=severity,
                    selected_descriptor_ids=selected_descriptor_ids,
                    observations=observations,
                    recommended_actions=recommended_actions,
                    executed_actions=executed_actions,
                    unavailable_reason_code=unavailable_reason_code,
                    degraded_reason_code=degraded_reason_code,
                    binding_digest_sha512=binding_digest_sha512,
                    source_plan_id=source_plan_id,
                    source_plan_digest_sha512=source_plan_digest_sha512,
                    capability_snapshot_digest_sha512=capability_snapshot_digest_sha512,
                    authority_snapshot_digest_sha512=authority_snapshot_digest_sha512,
                    policy_snapshot_digest_sha512=policy_snapshot_digest_sha512,
                    budget_snapshot_digest_sha512=budget_snapshot_digest_sha512,
                    action_registry_digest_sha512=action_registry_digest_sha512,
                    latency_ms=latency_ms,
                    call_count=call_count,
                ),
                invocation_id=invocation_id,
            )
        except Exception:
            self._mark_degraded()

    def _mark_degraded(self) -> None:
        with self._status_lock:
            self._degraded = True
            self._degraded_event_count += 1

    def _resolve_store(self) -> EvidenceStorePort:
        with self._store_lock:
            if self._store is None:
                self._store = self._store_factory()
            return self._store

    def _append(
        self,
        *,
        event_kind: AuditEventKind,
        payload: GovernancePointStartedPayload | GovernancePointTerminalPayload,
        invocation_id: str,
    ) -> None:
        envelope = AuditEventEnvelope(
            event_id=AuditEventId(value=str(uuid4())),
            run_id=self._run_id,
            occurred_at_utc=datetime.now(UTC),
            source_component=self._source_component,
            event_kind=event_kind,
            provenance=AuditEventProvenance.SYSTEM_TRACE,
            correlation_refs=(
                AuditCorrelationRef(
                    kind=AuditCorrelationKind.GOVERNANCE_INVOCATION_ID,
                    value=invocation_id,
                ),
            ),
            safe_payload=payload,
        )
        self._resolve_store().append(canonicalize_event(envelope))
