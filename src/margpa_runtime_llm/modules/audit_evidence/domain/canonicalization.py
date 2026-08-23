"""Canonical JSON form and SHA-512 digest for audit events.

Architecture §4.3: UTF-8, lexicographic key sort, `(",", ":")` separators,
NaN/Infinity rejected, UTC timestamps, explicit string enums, and the
digest field itself excluded from its own digest input (avoiding the
self-reference problem documented for Compaction Recovery Hash Manifests).
Schema version (`ImmutableContract.schema_version`) and
`canonicalization_version` are independent fields — bumping one does not
imply the other changed.
"""

from __future__ import annotations

import hashlib
import json

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .models import AuditEventEnvelope


def canonical_event_payload(envelope: AuditEventEnvelope) -> dict[str, object]:
    """The exact JSON-safe structure that is hashed — public so callers can
    verify a digest independently without re-deriving serialization rules."""

    return envelope.model_dump(mode="json")


def canonical_json_bytes(payload: dict[str, object]) -> bytes:
    """The shared canonical-JSON encoder: UTF-8, lexicographic key sort,
    compact separators, and NaN/Infinity rejected rather than silently
    emitted as non-standard JSON tokens. Exposed standalone so the
    non-finite-number guard is directly testable without needing a typed
    contract that happens to contain a `float` field."""

    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except ValueError as error:
        raise ValueError("payload contains a non-finite number") from error


def canonical_event_json(envelope: AuditEventEnvelope) -> bytes:
    return canonical_json_bytes(canonical_event_payload(envelope))


def event_digest_sha512(envelope: AuditEventEnvelope) -> str:
    return hashlib.sha512(canonical_event_json(envelope)).hexdigest()


class CanonicalAuditEvent(ImmutableContract):
    """An `AuditEventEnvelope` paired with its own digest, computed over the
    envelope alone — the digest field is never part of its own input."""

    envelope: AuditEventEnvelope
    event_digest_sha512: str = Field(pattern=r"^[0-9a-f]{128}$")


def canonicalize_event(envelope: AuditEventEnvelope) -> CanonicalAuditEvent:
    return CanonicalAuditEvent(
        envelope=envelope,
        event_digest_sha512=event_digest_sha512(envelope),
    )


def verify_canonical_event(canonical: CanonicalAuditEvent) -> bool:
    """Recompute the digest from the embedded envelope and compare —
    the stored digest field is excluded from the recomputation input by
    construction (it is derived only from `canonical.envelope`)."""

    return event_digest_sha512(canonical.envelope) == canonical.event_digest_sha512
