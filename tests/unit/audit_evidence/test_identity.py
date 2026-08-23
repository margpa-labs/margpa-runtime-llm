"""Typed opaque identity behavior for the audit/evidence domain."""

from __future__ import annotations

from typing import cast

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditCorrelationKind,
    AuditCorrelationRef,
    AuditEventId,
    AuditRunId,
    EvidenceReceiptId,
)


def test_identity_types_reject_mixing_by_class() -> None:
    run_id = AuditRunId(value="run-0001")
    event_id = AuditEventId(value="event-0001")

    assert isinstance(run_id, AuditRunId)
    assert not isinstance(run_id, AuditEventId)
    assert type(cast("object", run_id)) is not type(cast("object", event_id))
    # Equal string payload does not make the two identities equal.
    same_value_event = AuditEventId(value="run-0001")
    assert run_id.value == same_value_event.value
    assert cast("object", run_id) != cast("object", same_value_event)


@pytest.mark.parametrize("identity_cls", [AuditRunId, AuditEventId, EvidenceReceiptId])
def test_identity_rejects_empty_value(identity_cls: type) -> None:
    with pytest.raises(ValidationError):
        identity_cls(value="")


@pytest.mark.parametrize("identity_cls", [AuditRunId, AuditEventId, EvidenceReceiptId])
def test_identity_rejects_disallowed_characters(identity_cls: type) -> None:
    with pytest.raises(ValidationError):
        identity_cls(value="not a valid id!")


def test_identity_is_frozen() -> None:
    run_id = AuditRunId(value="run-0001")
    with pytest.raises(ValidationError):
        run_id.value = "run-0002"


def test_identity_rejects_unknown_field() -> None:
    with pytest.raises(ValidationError):
        AuditRunId(value="run-0001", unexpected="x")  # type: ignore[call-arg]


def test_correlation_ref_requires_declared_kind() -> None:
    ref = AuditCorrelationRef(kind=AuditCorrelationKind.CONVERSATION_ID, value="conv-0001")
    assert ref.kind is AuditCorrelationKind.CONVERSATION_ID

    with pytest.raises(ValidationError):
        AuditCorrelationRef(kind="not_a_real_kind", value="x")  # type: ignore[arg-type]
