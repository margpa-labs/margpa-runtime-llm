"""Evidence store port: append/read/status/receipt, adapter-independent.

Architecture §4: the Definition Pipeline and Evidence Pipeline are loosely
coupled — this port only knows about `CanonicalAuditEvent`, never about
filesystem paths, SQLite, or any other adapter-specific detail.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .domain import (
    IDENTIFIER_PATTERN,
    AuditRunId,
    CanonicalAuditEvent,
    EvidenceReceiptId,
)


class EvidenceReceipt(ImmutableContract):
    """Returned by a successful append; callers can use it to verify
    positional/segment placement without re-reading the store."""

    receipt_id: EvidenceReceiptId
    event_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    event_digest_sha512: str = Field(pattern=r"^[0-9a-f]{128}$")
    segment: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    position: int = Field(ge=0)


class EvidenceStoreStatus(ImmutableContract):
    """Safe, aggregate-only status — never a dump of stored event content."""

    event_count: int = Field(ge=0)
    degraded: bool = False
    degraded_reason_code: str | None = Field(
        default=None, max_length=64, pattern=IDENTIFIER_PATTERN
    )


@runtime_checkable
class EvidenceStorePort(Protocol):
    def append(self, canonical: CanonicalAuditEvent) -> EvidenceReceipt: ...

    def read_all(self, run_id: AuditRunId) -> tuple[CanonicalAuditEvent, ...]: ...

    def status(self) -> EvidenceStoreStatus: ...
