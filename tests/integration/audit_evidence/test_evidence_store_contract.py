"""Shared EvidenceStorePort contract: both adapters must behave equivalently
for append/duplicate/status/read, and never leak absolute paths or raw
exception text through their safe error surface (P3-B-WU-003)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.audit_evidence.local_jsonl_store import (
    LocalJsonlEvidenceStore,
)
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


@pytest.fixture(
    params=["in_memory", "local_jsonl"],
    ids=["InMemoryEvidenceStore", "LocalJsonlEvidenceStore"],
)
def evidence_store(request: pytest.FixtureRequest, tmp_path: Path) -> EvidenceStorePort:
    if request.param == "in_memory":
        return InMemoryEvidenceStore()
    return LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="evidence", scope="contract-test")


def test_fresh_store_has_zero_events(evidence_store: EvidenceStorePort) -> None:
    status = evidence_store.status()
    assert status.event_count == 0
    assert status.degraded is False


def test_append_then_status_and_read_agree(evidence_store: EvidenceStorePort) -> None:
    canonical = _canonical("event-0001")
    receipt = evidence_store.append(canonical)

    assert receipt.event_id == "event-0001"
    assert receipt.position == 0
    assert evidence_store.status().event_count == 1

    events = evidence_store.read_all(AuditRunId(value="run-0001"))
    assert [event.envelope.event_id.value for event in events] == ["event-0001"]


def test_duplicate_append_raises_typed_error_with_no_leaked_internals(
    evidence_store: EvidenceStorePort,
) -> None:
    evidence_store.append(_canonical("event-0001"))

    with pytest.raises(EvidenceStoreError) as excinfo:
        evidence_store.append(_canonical("event-0001"))

    error = excinfo.value
    assert error.code is EvidenceStoreErrorCode.DUPLICATE_EVENT
    safe_dict = error.to_safe_dict()
    rendered = repr(safe_dict) + error.safe_message
    assert "/" not in rendered  # no filesystem path of any kind
    assert "Traceback" not in rendered
    assert evidence_store.status().event_count == 1


def test_ordering_is_preserved_across_multiple_appends(
    evidence_store: EvidenceStorePort,
) -> None:
    positions = [evidence_store.append(_canonical(f"event-{i:04d}")).position for i in range(5)]
    assert positions == [0, 1, 2, 3, 4]
    events = evidence_store.read_all(AuditRunId(value="run-0001"))
    assert [event.envelope.event_id.value for event in events] == [
        f"event-{i:04d}" for i in range(5)
    ]
