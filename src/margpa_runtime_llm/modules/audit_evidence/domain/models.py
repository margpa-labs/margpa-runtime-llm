"""Audit event contracts: event kind, safe (typed-allowlist) payloads, envelope.

Phase 3 requirement P3-EVD-004 forbids Raw Chain of Thought, System Prompt,
Secret, Hidden Original, and full prompt/output content in ordinary
Evidence. `safe_payload` is therefore a closed union of small, explicitly
allowlisted payload models per `AuditEventKind` — never an open `dict`.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .errors import AuditDomainError, AuditDomainErrorCode
from .identity import IDENTIFIER_PATTERN, AuditCorrelationRef, AuditEventId, AuditRunId

_SHA512_HEX_PATTERN = r"^[0-9a-f]{128}$"


def _is_utc(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() == timedelta(0)


def _require_utc(value: datetime, *, field_name: str) -> datetime:
    if not _is_utc(value):
        raise ValueError(f"{field_name} must be timezone-aware UTC")
    return value


class AuditEventKind(StrEnum):
    RUNTIME_STARTED = "runtime_started"
    RUNTIME_STOPPED = "runtime_stopped"
    GENERATION_STARTED = "generation_started"
    GENERATION_TERMINAL = "generation_terminal"
    DEFINITION_PROVIDER_RESOLVED = "definition_provider_resolved"
    DEFINITION_SOURCE_LOADED = "definition_source_loaded"
    DEFINITION_VALIDATED = "definition_validated"
    DEFINITION_REJECTED = "definition_rejected"
    DEFINITION_NORMALIZED = "definition_normalized"
    GOVERNANCE_PLAN_COMPILED = "governance_plan_compiled"
    GOVERNANCE_MODE_CHANGED = "governance_mode_changed"
    GOVERNANCE_POINT_STARTED = "governance_point_started"
    GOVERNANCE_POINT_TERMINAL = "governance_point_terminal"
    AUDIT_WRITE_DEGRADED = "audit_write_degraded"


class AuditEventProvenance(StrEnum):
    """Keeps System Trace and Model Generated Explanation in separate,
    independently labeled fields/provenance, per architecture §4.1/§33.2."""

    SYSTEM_TRACE = "system_trace"
    MODEL_GENERATED_EXPLANATION = "model_generated_explanation"


class EmptyEventPayload(ImmutableContract):
    """No fields beyond the envelope itself (e.g. runtime_started/stopped)."""


class GenerationStartedPayload(ImmutableContract):
    profile_key: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)


class GenerationTerminalPayload(ImmutableContract):
    stop_reason: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    token_count: int = Field(ge=0)
    latency_ms: int = Field(ge=0)
    warning_count: int = Field(ge=0, default=0)
    error_count: int = Field(ge=0, default=0)


class DefinitionProviderResolvedPayload(ImmutableContract):
    provider_kind: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    repository_state: str = Field(min_length=1, max_length=32, pattern=IDENTIFIER_PATTERN)


class DefinitionSourceLoadedPayload(ImmutableContract):
    source_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    byte_length: int = Field(ge=0)
    content_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)


class DefinitionValidatedPayload(ImmutableContract):
    definition_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    definition_version: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)


class DefinitionRejectedPayload(ImmutableContract):
    source_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    reason_code: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)


class DefinitionNormalizedPayload(ImmutableContract):
    definition_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    ir_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)
    warning_count: int = Field(ge=0, default=0)


class GovernancePlanCompiledPayload(ImmutableContract):
    compiled_plan_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    binding_state: str = Field(min_length=1, max_length=32, pattern=IDENTIFIER_PATTERN)
    executable: bool


class GovernanceModeChangedPayload(ImmutableContract):
    previous_mode: str = Field(min_length=1, max_length=16, pattern=IDENTIFIER_PATTERN)
    new_mode: str = Field(min_length=1, max_length=16, pattern=IDENTIFIER_PATTERN)


class AuditWriteDegradedPayload(ImmutableContract):
    reason_code: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)


class GovernancePointStartedPayload(ImmutableContract):
    """Phase 4 Main Runtime Governance Point invocation start
    (P4-EVD-001). Carries only Typed identity/routing scalars — never a
    Snapshot, Rule text, or Model content (P4-EVD-002)."""

    point_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    stage: str = Field(min_length=1, max_length=32, pattern=IDENTIFIER_PATTERN)
    mode: str = Field(min_length=1, max_length=16, pattern=IDENTIFIER_PATTERN)


class SafeObservationRecord(ImmutableContract):
    """One `Observation` projected Safe (P4-CODEX-007): Typed identity/
    outcome/reason/severity only — never the Rule text or Model content
    that produced it."""

    descriptor_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    outcome: str = Field(min_length=1, max_length=32, pattern=IDENTIFIER_PATTERN)
    detail_code: str | None = Field(default=None, max_length=64, pattern=IDENTIFIER_PATTERN)
    severity: str = Field(min_length=1, max_length=16, pattern=IDENTIFIER_PATTERN)


class SafeRecommendedActionRecord(ImmutableContract):
    """One `RecommendedAction` projected Safe (P4-CODEX-007) — Recommended
    Actions are a Bounded Typed List of real identities, never compressed
    into an aggregate count."""

    action_id: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    reason_descriptor_id: str | None = Field(
        default=None, max_length=128, pattern=IDENTIFIER_PATTERN
    )
    severity: str = Field(min_length=1, max_length=16, pattern=IDENTIFIER_PATTERN)


class SafeExecutedActionRecord(ImmutableContract):
    """One `ExecutedAction` projected Safe (P4-CODEX-007) — Executed
    Actions are a Bounded Typed List of real identities/outcomes, never
    compressed into an aggregate count."""

    action_id: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    executed: bool
    intervening: bool
    not_executed_reason_code: str | None = Field(
        default=None, max_length=64, pattern=IDENTIFIER_PATTERN
    )


class GovernancePointTerminalPayload(ImmutableContract):
    """Phase 4 Main Runtime Governance Point invocation result
    (P4-EVD-001) — a Safe projection of `StandardGovernanceResult`:
    Typed reason codes, real Observation/Recommendation/Execution
    identities (never aggregate counts, P4-CODEX-007), and Digests —
    never raw Rule text, Model Input/Output, or an unredacted exception
    (P4-EVD-002/P4-STS-002)."""

    point_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    stage: str = Field(min_length=1, max_length=32, pattern=IDENTIFIER_PATTERN)
    mode: str = Field(min_length=1, max_length=16, pattern=IDENTIFIER_PATTERN)
    execution_state: str = Field(min_length=1, max_length=32, pattern=IDENTIFIER_PATTERN)
    severity: str = Field(min_length=1, max_length=16, pattern=IDENTIFIER_PATTERN)
    selected_descriptor_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=4096)
    observations: tuple[SafeObservationRecord, ...] = Field(default_factory=tuple, max_length=4096)
    recommended_actions: tuple[SafeRecommendedActionRecord, ...] = Field(
        default_factory=tuple, max_length=256
    )
    executed_actions: tuple[SafeExecutedActionRecord, ...] = Field(
        default_factory=tuple, max_length=256
    )
    unavailable_reason_code: str | None = Field(
        default=None, max_length=64, pattern=IDENTIFIER_PATTERN
    )
    degraded_reason_code: str | None = Field(
        default=None, max_length=64, pattern=IDENTIFIER_PATTERN
    )
    # P4-CODEX-007/008: traces this Result's Evidence back to the exact
    # Binding (and, transitively, the Phase 3 Source Plan and
    # Capability/Authority/Policy/Budget/Registry Snapshots) that
    # produced it — `None` whenever no Binding was involved (observe, or
    # a mode/evaluation failure before Bind).
    binding_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    source_plan_id: str | None = Field(default=None, max_length=128, pattern=IDENTIFIER_PATTERN)
    source_plan_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    capability_snapshot_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    authority_snapshot_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    policy_snapshot_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    budget_snapshot_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    action_registry_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    latency_ms: int = Field(ge=0)
    call_count: int = Field(ge=0, default=0)


type SafeEventPayload = (
    EmptyEventPayload
    | GenerationStartedPayload
    | GenerationTerminalPayload
    | DefinitionProviderResolvedPayload
    | DefinitionSourceLoadedPayload
    | DefinitionValidatedPayload
    | DefinitionRejectedPayload
    | DefinitionNormalizedPayload
    | GovernancePlanCompiledPayload
    | GovernanceModeChangedPayload
    | GovernancePointStartedPayload
    | GovernancePointTerminalPayload
    | AuditWriteDegradedPayload
)

_EVENT_KIND_PAYLOAD_TYPES: dict[AuditEventKind, type[ImmutableContract]] = {
    AuditEventKind.RUNTIME_STARTED: EmptyEventPayload,
    AuditEventKind.RUNTIME_STOPPED: EmptyEventPayload,
    AuditEventKind.GENERATION_STARTED: GenerationStartedPayload,
    AuditEventKind.GENERATION_TERMINAL: GenerationTerminalPayload,
    AuditEventKind.DEFINITION_PROVIDER_RESOLVED: DefinitionProviderResolvedPayload,
    AuditEventKind.DEFINITION_SOURCE_LOADED: DefinitionSourceLoadedPayload,
    AuditEventKind.DEFINITION_VALIDATED: DefinitionValidatedPayload,
    AuditEventKind.DEFINITION_REJECTED: DefinitionRejectedPayload,
    AuditEventKind.DEFINITION_NORMALIZED: DefinitionNormalizedPayload,
    AuditEventKind.GOVERNANCE_PLAN_COMPILED: GovernancePlanCompiledPayload,
    AuditEventKind.GOVERNANCE_MODE_CHANGED: GovernanceModeChangedPayload,
    AuditEventKind.GOVERNANCE_POINT_STARTED: GovernancePointStartedPayload,
    AuditEventKind.GOVERNANCE_POINT_TERMINAL: GovernancePointTerminalPayload,
    AuditEventKind.AUDIT_WRITE_DEGRADED: AuditWriteDegradedPayload,
}


class AuditEventEnvelope(ImmutableContract):
    """One immutable audit event, prior to canonicalization/digest (Phase 3-A-WU-002)."""

    canonicalization_version: str = Field(default="1", pattern=r"^[0-9]+$")
    event_id: AuditEventId
    run_id: AuditRunId
    occurred_at_utc: datetime
    source_component: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    event_kind: AuditEventKind
    provenance: AuditEventProvenance
    correlation_refs: tuple[AuditCorrelationRef, ...] = ()
    subject_refs: tuple[AuditCorrelationRef, ...] = ()
    safe_payload: SafeEventPayload

    @field_validator("occurred_at_utc")
    @classmethod
    def _validate_occurred_at(cls, value: datetime) -> datetime:
        return _require_utc(value, field_name="occurred_at_utc")

    @model_validator(mode="after")
    def _validate_payload_matches_kind(self) -> AuditEventEnvelope:
        expected = _EVENT_KIND_PAYLOAD_TYPES[self.event_kind]
        if type(self.safe_payload) is not expected:
            raise ValueError(
                f"safe_payload type {type(self.safe_payload).__name__} does not match "
                f"event_kind {self.event_kind.value} (expected {expected.__name__})"
            )
        return self


def require_known_event_kind(value: str) -> AuditEventKind:
    """Reject unknown event kinds explicitly rather than letting pydantic's
    generic enum-coercion error surface a raw payload value."""

    try:
        return AuditEventKind(value)
    except ValueError as error:
        raise AuditDomainError(
            code=AuditDomainErrorCode.INVALID_EVENT_KIND,
            safe_message="unknown audit event kind",
        ) from error
