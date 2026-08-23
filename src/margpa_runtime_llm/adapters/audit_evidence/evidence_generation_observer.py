"""`GenerationObserverPort` adapter that appends to an Evidence Store
(P3-F-WU-005, P3-CODEX-002 rework).

Every public method swallows all exceptions internally — construction
failure, a rejected payload, and any Evidence Store write failure alike.
Per architecture §4.5 (Failure Policy), an Evidence Write failure degrades
the Evidence Store, never Model generation; this adapter is the boundary
that turns "the store raised" into "nothing observably happened."

`mode_provider` ties `is_active()` to the live Governance Mode
(architecture §1's `governance.mode` → `evidence binding`): a Callable
rather than a `GovernanceMode` import, so this adapter stays decoupled
from the governance_definitions module's domain types (§4 "Definition
PipelineとEvidence Pipelineは疎結合"). Only the caller's *binding-time*
`is_active()` check gates whether a generation is observed at all —
`observe_generation_started`/`observe_generation_terminal` themselves no
longer re-check Mode per call, so a generation bound at start completes
its Start/Terminal pair even if Mode changes mid-stream, instead of
silently losing one side of the pair (P3-CODEX-002).

`store_factory` is resolved at most once, lazily, on the first actual
append — not at construction — so a process that stays `off` for its
whole lifetime never creates the Evidence Store's directory tree
(P3-CODEX-002 "Default OFF Bootの不要Filesystem Mutationを避ける").

A Write/Store/Payload failure inside `observe_generation_started`/
`observe_generation_terminal` never propagates or alters Model/SSE
behavior — but per P3-CODEX-009 it must not be silently invisible
either. `status()` exposes a Safe, aggregate-only snapshot (never a raw
exception, message, or path) that a caller can surface through the
existing Governance Status Surface."""

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
    GenerationStartedPayload,
    GenerationTerminalPayload,
    canonicalize_event,
)
from margpa_runtime_llm.modules.audit_evidence.generation_observation import (
    GenerationObserverStatus,
)
from margpa_runtime_llm.modules.audit_evidence.ports import EvidenceStorePort

_ACTIVE_MODE = "observe"
_DEGRADED_REASON_CODE = "evidence_write_failed"


class EvidenceGenerationObserver:
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
            return self._mode_provider() == _ACTIVE_MODE
        except Exception:
            return False

    def status(self) -> GenerationObserverStatus:
        with self._status_lock:
            return GenerationObserverStatus(
                degraded=self._degraded,
                degraded_reason_code=_DEGRADED_REASON_CODE if self._degraded else None,
                degraded_event_count=self._degraded_event_count,
            )

    def observe_generation_started(self, *, request_id: str, profile_key: str) -> None:
        try:
            self._append(
                event_kind=AuditEventKind.GENERATION_STARTED,
                payload=GenerationStartedPayload(profile_key=profile_key),
                request_id=request_id,
            )
        except Exception:
            self._mark_degraded()

    def observe_generation_terminal(
        self,
        *,
        request_id: str,
        stop_reason: str,
        token_count: int,
        latency_ms: int,
        warning_count: int,
        error_count: int,
    ) -> None:
        try:
            self._append(
                event_kind=AuditEventKind.GENERATION_TERMINAL,
                payload=GenerationTerminalPayload(
                    stop_reason=stop_reason,
                    token_count=token_count,
                    latency_ms=latency_ms,
                    warning_count=warning_count,
                    error_count=error_count,
                ),
                request_id=request_id,
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
        payload: GenerationStartedPayload | GenerationTerminalPayload,
        request_id: str,
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
                    kind=AuditCorrelationKind.GENERATION_REQUEST_ID,
                    value=request_id,
                ),
            ),
            safe_payload=payload,
        )
        self._resolve_store().append(canonicalize_event(envelope))
