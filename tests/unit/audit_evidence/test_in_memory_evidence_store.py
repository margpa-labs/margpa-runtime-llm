"""In-memory reference EvidenceStorePort: append-only, duplicate rejection,
receipt consistency, typed failure."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from margpa_runtime_llm.modules.audit_evidence.application import InMemoryEvidenceStore
from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditEventEnvelope,
    AuditEventId,
    AuditEventKind,
    AuditEventProvenance,
    AuditRunId,
    CanonicalAuditEvent,
    EmptyEventPayload,
    EvidenceStoreError,
    EvidenceStoreErrorCode,
    canonicalize_event,
)
from margpa_runtime_llm.modules.audit_evidence.ports import EvidenceStorePort

UTC_NOW = datetime(2026, 8, 21, 12, 0, 0, tzinfo=UTC)


def _canonical(event_id: str, run_id: str = "run-0001") -> CanonicalAuditEvent:
    envelope = AuditEventEnvelope(
        event_id=AuditEventId(value=event_id),
        run_id=AuditRunId(value=run_id),
        occurred_at_utc=UTC_NOW,
        source_component="conversation.generation",
        event_kind=AuditEventKind.RUNTIME_STARTED,
        provenance=AuditEventProvenance.SYSTEM_TRACE,
        safe_payload=EmptyEventPayload(),
    )
    return canonicalize_event(envelope)


def test_store_satisfies_the_port_protocol() -> None:
    assert isinstance(InMemoryEvidenceStore(), EvidenceStorePort)


def test_append_returns_receipt_matching_the_event() -> None:
    store = InMemoryEvidenceStore()
    canonical = _canonical("event-0001")

    receipt = store.append(canonical)

    assert receipt.event_id == "event-0001"
    assert receipt.event_digest_sha512 == canonical.event_digest_sha512
    assert receipt.position == 0


def test_append_is_append_only_and_preserves_order() -> None:
    store = InMemoryEvidenceStore()
    first = _canonical("event-0001")
    second = _canonical("event-0002")

    receipt_first = store.append(first)
    receipt_second = store.append(second)

    assert receipt_first.position == 0
    assert receipt_second.position == 1
    stored = store.read_all(AuditRunId(value="run-0001"))
    assert [event.envelope.event_id.value for event in stored] == [
        "event-0001",
        "event-0002",
    ]


def test_append_rejects_duplicate_event_id_with_typed_failure() -> None:
    store = InMemoryEvidenceStore()
    store.append(_canonical("event-0001"))

    with pytest.raises(EvidenceStoreError) as excinfo:
        store.append(_canonical("event-0001"))

    assert excinfo.value.code is EvidenceStoreErrorCode.DUPLICATE_EVENT
    assert excinfo.value.event_id == "event-0001"
    # Duplicate rejection must not silently drop the original event.
    assert store.status().event_count == 1


def test_read_all_scopes_to_the_requested_run_id() -> None:
    store = InMemoryEvidenceStore()
    store.append(_canonical("event-0001", run_id="run-a"))
    store.append(_canonical("event-0002", run_id="run-b"))

    run_a_events = store.read_all(AuditRunId(value="run-a"))
    run_b_events = store.read_all(AuditRunId(value="run-b"))
    run_c_events = store.read_all(AuditRunId(value="run-c"))

    assert [event.envelope.event_id.value for event in run_a_events] == ["event-0001"]
    assert [event.envelope.event_id.value for event in run_b_events] == ["event-0002"]
    assert run_c_events == ()


def test_status_reports_safe_aggregate_only() -> None:
    store = InMemoryEvidenceStore()
    assert store.status().event_count == 0
    assert store.status().degraded is False

    store.append(_canonical("event-0001"))
    status = store.status()
    assert status.event_count == 1
    assert status.degraded is False
    assert status.degraded_reason_code is None
