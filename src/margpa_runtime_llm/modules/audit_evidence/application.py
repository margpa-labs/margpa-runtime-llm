"""In-memory reference Evidence Store adapter.

Reference/contract-test implementation of `EvidenceStorePort` — not the
Local JSONL Store (Phase 3-B). Append-only, rejects duplicate event IDs,
never mutates or reorders previously accepted events.
"""

from __future__ import annotations

import threading

from .domain import AuditRunId, CanonicalAuditEvent, EvidenceReceiptId
from .domain.errors import EvidenceStoreError, EvidenceStoreErrorCode
from .ports import EvidenceReceipt, EvidenceStoreStatus


class InMemoryEvidenceStore:
    """Process-local, non-persistent `EvidenceStorePort` implementation."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: list[CanonicalAuditEvent] = []
        self._segment = "in-memory"
        self._seen_event_ids: set[str] = set()

    def append(self, canonical: CanonicalAuditEvent) -> EvidenceReceipt:
        event_id = canonical.envelope.event_id.value
        with self._lock:
            if event_id in self._seen_event_ids:
                raise EvidenceStoreError(
                    code=EvidenceStoreErrorCode.DUPLICATE_EVENT,
                    safe_message="duplicate audit event id",
                    run_id=canonical.envelope.run_id.value,
                    event_id=event_id,
                )
            position = len(self._events)
            self._events.append(canonical)
            self._seen_event_ids.add(event_id)
            return EvidenceReceipt(
                receipt_id=EvidenceReceiptId(value=f"receipt-{position:012d}"),
                event_id=event_id,
                event_digest_sha512=canonical.event_digest_sha512,
                segment=self._segment,
                position=position,
            )

    def read_all(self, run_id: AuditRunId) -> tuple[CanonicalAuditEvent, ...]:
        with self._lock:
            return tuple(event for event in self._events if event.envelope.run_id == run_id)

    def status(self) -> EvidenceStoreStatus:
        with self._lock:
            return EvidenceStoreStatus(event_count=len(self._events))
