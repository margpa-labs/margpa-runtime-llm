"""Canonical JSON form and SHA-512 digest determinism for audit events."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditEventEnvelope,
    AuditEventId,
    AuditEventKind,
    AuditEventProvenance,
    AuditRunId,
    EmptyEventPayload,
    GenerationTerminalPayload,
)
from margpa_runtime_llm.modules.audit_evidence.domain.canonicalization import (
    canonical_event_json,
    canonical_json_bytes,
    canonicalize_event,
    event_digest_sha512,
    verify_canonical_event,
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


def test_digest_is_independent_of_python_dict_construction_order() -> None:
    # dict literal order differs but is semantically identical; canonical
    # JSON key-sorts before hashing, so digests must match exactly.
    payload_a = {"b": 2, "a": 1, "c": {"y": 2, "x": 1}}
    payload_b = {"a": 1, "c": {"x": 1, "y": 2}, "b": 2}
    assert canonical_json_bytes(payload_a) == canonical_json_bytes(payload_b)


def test_digest_changes_when_payload_differs() -> None:
    base = _envelope()
    changed = _envelope(source_component="documentation_rag.retrieval")
    assert event_digest_sha512(base) != event_digest_sha512(changed)


def test_digest_changes_when_event_kind_and_safe_payload_differ() -> None:
    base = _envelope()
    changed = _envelope(
        event_kind=AuditEventKind.GENERATION_TERMINAL,
        safe_payload=GenerationTerminalPayload(
            stop_reason="completed", token_count=10, latency_ms=500
        ),
    )
    assert event_digest_sha512(base) != event_digest_sha512(changed)


def test_digest_is_deterministic_for_identical_semantic_content() -> None:
    first = event_digest_sha512(_envelope())
    second = event_digest_sha512(_envelope())
    assert first == second
    assert len(first) == 128


def test_canonical_json_is_unicode_deterministic_not_ascii_escaped() -> None:
    payload: dict[str, object] = {"label": "日本語のLabel"}
    encoded = canonical_json_bytes(payload)
    assert "日本語のLabel".encode() in encoded
    assert b"\\u" not in encoded


def test_canonical_json_rejects_nan_and_infinity() -> None:
    with pytest.raises(ValueError, match="non-finite"):
        canonical_json_bytes({"score": float("nan")})
    with pytest.raises(ValueError, match="non-finite"):
        canonical_json_bytes({"score": float("inf")})
    with pytest.raises(ValueError, match="non-finite"):
        canonical_json_bytes({"score": float("-inf")})


def test_canonicalize_event_digest_excludes_itself_from_its_own_input() -> None:
    envelope = _envelope()
    canonical = canonicalize_event(envelope)

    # The digest is computed purely from the envelope; wrapping it inside
    # CanonicalAuditEvent (which adds the digest field alongside it) must
    # not change what was hashed.
    assert canonical.event_digest_sha512 == event_digest_sha512(envelope)
    assert canonical.event_digest_sha512 not in canonical_event_json(envelope).decode()
    assert verify_canonical_event(canonical) is True


def test_verify_canonical_event_detects_tampering() -> None:
    canonical = canonicalize_event(_envelope())
    tampered = canonical.model_copy(update={"event_digest_sha512": "0" * 128})
    assert verify_canonical_event(tampered) is False
