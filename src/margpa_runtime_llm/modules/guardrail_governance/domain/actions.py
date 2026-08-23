"""Guardrail Action identity/registry (P5-MOD-005).

Only Actions in this Enum can ever be Recommended/Executed by Phase 5 —
`repair`/`regenerate`/any Tool/Agent/External Side Effect is explicitly
Non-scope (P5-MOD-007/P5-AUT-005) and never appears here.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identities import IDENTIFIER_PATTERN


class ActionId(StrEnum):
    ALLOW = "allow"
    WARN = "warn"
    REJECT_INPUT = "reject_input"
    STOP_BEFORE_GENERATION = "stop_before_generation"
    SUPPRESS_STREAM_CANDIDATE = "suppress_stream_candidate"
    REJECT_OUTPUT = "reject_output"
    REDACT_TYPED_SECRET = "redact_typed_secret"
    REDACT_TYPED_PII = "redact_typed_pii"
    REQUIRE_APPROVAL = "require_approval"


# `allow` and `require_approval` are never independently Executable —
# `allow` is the absence of intervention (never an Adapter call), and
# `require_approval` only ever produces a Status/ApprovalState, never an
# AI-issued Approval (ADR-5-005/P5-AUT-005).
NOT_EXECUTABLE_ACTION_IDS = frozenset({ActionId.ALLOW.value, ActionId.REQUIRE_APPROVAL.value})


class NotExecutedReason(StrEnum):
    MODE_NOT_ENFORCE = "mode_not_enforce"
    BINDING_UNAVAILABLE = "binding_unavailable"
    BINDING_STALE = "binding_stale"
    NOT_EXECUTABLE_ACTION_CLASS = "not_executable_action_class"
    ACTION_NOT_REGISTERED = "action_not_registered"
    ACTION_NOT_ALLOWED_AT_POINT = "action_not_allowed_at_point"
    AUTHORITY_MISSING = "authority_missing"
    APPROVAL_PENDING = "approval_pending"
    APPROVAL_MISSING = "approval_missing"
    POLICY_NOT_APPLICABLE = "policy_not_applicable"
    CONFLICT_UNRESOLVED = "conflict_unresolved"
    SUPERSEDED_BY_HIGHER_PRIORITY_ACTION = "superseded_by_higher_priority_action"
    SPAN_UNVERIFIED = "span_unverified"
    ADAPTER_FAILURE = "adapter_failure"


class ActionRegistryEntry(ImmutableContract):
    action_id: ActionId
    allowed_points: tuple[str, ...] = Field(min_length=1, max_length=16)
    side_effect_class: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
