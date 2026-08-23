"""AuditEventEnvelope contract behavior: kind/payload matching, UTC timestamps,
rejection of unknown kinds and raw arbitrary payload objects."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditDomainError,
    AuditEventEnvelope,
    AuditEventId,
    AuditEventKind,
    AuditEventProvenance,
    AuditRunId,
    EmptyEventPayload,
    GenerationTerminalPayload,
    require_known_event_kind,
)

UTC_NOW = datetime(2026, 8, 21, 12, 0, 0, tzinfo=UTC)


def _envelope(**overrides: object) -> AuditEventEnvelope:
    fields: dict[str, object] = {
        "event_id": AuditEventId(value="event-0001"),
        "run_id": AuditRunId(value="run-0001"),
        "occurred_at_utc": UTC_NOW,
        "source_component": "conversation.generation",
        "event_kind": AuditEventKind.RUNTIME_STARTED,
        "provenance": AuditEventProvenance.SYSTEM_TRACE,
        "safe_payload": EmptyEventPayload(),
    }
    fields.update(overrides)
    return AuditEventEnvelope(**fields)  # type: ignore[arg-type]


def test_envelope_accepts_matching_kind_and_payload() -> None:
    envelope = _envelope(
        event_kind=AuditEventKind.GENERATION_TERMINAL,
        safe_payload=GenerationTerminalPayload(
            stop_reason="completed", token_count=42, latency_ms=1200
        ),
    )
    assert envelope.event_kind is AuditEventKind.GENERATION_TERMINAL
    assert envelope.canonicalization_version == "1"


def test_envelope_rejects_payload_kind_mismatch() -> None:
    with pytest.raises(ValidationError):
        _envelope(
            event_kind=AuditEventKind.GENERATION_TERMINAL,
            safe_payload=EmptyEventPayload(),
        )


def test_envelope_rejects_non_utc_timestamp() -> None:
    naive = datetime(2026, 8, 21, 12, 0, 0)
    with pytest.raises(ValidationError):
        _envelope(occurred_at_utc=naive)

    non_utc = datetime(2026, 8, 21, 21, 0, 0, tzinfo=timezone(timedelta(hours=9)))
    with pytest.raises(ValidationError):
        _envelope(occurred_at_utc=non_utc)


def test_envelope_rejects_unknown_event_kind_string() -> None:
    with pytest.raises(ValidationError):
        _envelope(event_kind="not_a_real_kind")


def test_envelope_rejects_raw_arbitrary_payload_object() -> None:
    with pytest.raises(ValidationError):
        _envelope(safe_payload={"anything": "goes"})

    with pytest.raises(ValidationError):
        _envelope(safe_payload=object())


def test_envelope_is_frozen_and_rejects_unknown_field() -> None:
    envelope = _envelope()
    with pytest.raises(ValidationError):
        envelope.source_component = "changed"
    with pytest.raises(ValidationError):
        _envelope(unexpected_field="x")


def test_require_known_event_kind_accepts_valid_value() -> None:
    assert require_known_event_kind("runtime_started") is AuditEventKind.RUNTIME_STARTED


def test_require_known_event_kind_rejects_unknown_value() -> None:
    with pytest.raises(AuditDomainError):
        require_known_event_kind("definitely_not_a_kind")
