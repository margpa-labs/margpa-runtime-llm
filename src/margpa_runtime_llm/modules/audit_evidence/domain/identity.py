"""Opaque identities for the audit/evidence domain.

Each identity is its own Pydantic subclass (not a shared `str` alias) so that
passing an `AuditRunId` where an `AuditEventId` is expected is a type error,
not a silent same-shape string swap. `AuditCorrelationRef` carries a
`kind` alongside the value for identities audit_evidence does not own
(conversation, generation, definition/plan) so those spaces are not each
given a redundant local type.
"""

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class _OpaqueIdentifier(ImmutableContract):
    value: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)


class AuditRunId(_OpaqueIdentifier):
    """Identity of one process/runtime observation period."""


class AuditEventId(_OpaqueIdentifier):
    """Identity of one immutable audit event."""


class EvidenceReceiptId(_OpaqueIdentifier):
    """Identity of one append receipt returned by the evidence store."""


class AuditCorrelationKind(StrEnum):
    """The identity spaces an audit event may optionally reference.

    Definition/IR/Plan kinds are declared here (ahead of the
    governance_definitions module that will own those identities from
    Phase 3-C onward) purely as a closed vocabulary for correlation —
    audit_evidence does not construct or validate those identities itself.
    """

    CONVERSATION_ID = "conversation_id"
    CONVERSATION_SESSION_ID = "conversation_session_id"
    CONVERSATION_TURN_ID = "conversation_turn_id"
    GENERATION_REQUEST_ID = "generation_request_id"
    DEFINITION_PACKAGE_ID = "definition_package_id"
    DEFINITION_ID = "definition_id"
    DEFINITION_SOURCE_ID = "definition_source_id"
    NORMALIZED_IR_ID = "normalized_ir_id"
    COMPILED_PLAN_ID = "compiled_plan_id"
    GOVERNANCE_INVOCATION_ID = "governance_invocation_id"
    GOVERNANCE_BINDING_ID = "governance_binding_id"


class AuditCorrelationRef(ImmutableContract):
    """A typed, optional reference to an identity outside this domain.

    Existence of a correlation target is never inferred — callers only
    attach a ref when the referenced identity is already known.
    """

    kind: AuditCorrelationKind
    value: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
