"""Guardrail Result contracts (architecture §3, P5-RES-001/002).

Detection Fact, Policy Applicability, Authority Decision, Approval
State, Recommendation and Executed Action stay separate Identities —
never merged into one ambiguous list or a single opaque Score
(P5-RES-001/002).
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identities import IDENTIFIER_PATTERN
from .snapshots import is_expired
from .spans import TypedSpan

_SHA512_HEX_PATTERN = r"^[0-9a-f]{128}$"


def _canonical_digest(payload: object) -> str:
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()


class ExecutionState(StrEnum):
    NOT_EVALUATED = "not_evaluated"
    """Mode is OFF: this Point was never invoked (P5-MOD-002)."""

    EVALUATED = "evaluated"
    """The Point ran (observe or enforce) and this Result is its output."""

    DEGRADED = "degraded"
    """A component (Detector, Policy, Authority, Approval, Action)
    failed. Observe never mutates Input/Output/Stream even here."""

    UNAVAILABLE = "unavailable"
    """Enforce was requested but a required Policy/Authority/Registry
    input is missing or Stale — never silently downgraded to observe
    (P5-MOD-004, P5-ACC-014)."""


class Severity(StrEnum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionOutcome(StrEnum):
    CLEAR = "clear"
    MATCH = "match"
    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class ModelDetectionProvenance(ImmutableContract):
    """P6-RR-R27 (Post-Codex Independent Review Rework, resolves
    P6-CODEX-091): typed Identity for a Model-backed Detection — the
    exact `model_id`/upstream Revision/Artifact Digest/Contract Manifest
    Digest/Label Schema ID the real Model Call that produced this
    Detection actually ran under. Optional on `GuardDetection` and
    populated only by Model-backed Detectors (currently Qwen3Guard);
    every purely deterministic/pattern Detector leaves it at its default
    `None`, so this stays additive and never touches Generic Detector
    compatibility. `Qwen3GuardClassification` already carried every one
    of these fields — Codex's Review found `Qwen3GuardDetectorAdapter.
    detect()` discarded them when narrowing to the Generic `GuardDetection`
    shape, so real Provider Identity never reached the Guardrail Result/
    Evidence trail at all."""

    model_id: str = Field(min_length=1, max_length=128)
    exact_revision: str = Field(min_length=1, max_length=128)
    artifact_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    contract_manifest_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    label_schema_id: str = Field(min_length=1, max_length=128)


class GuardDetection(ImmutableContract):
    detection_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    detector_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    category_id: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    outcome: DetectionOutcome
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    severity: Severity = Severity.NONE
    # Optional, Ephemeral, Bounded — a Verified Span carries no raw
    # matched text, only Bounds (P5-EVD-002/ADR-5-007).
    typed_spans: tuple[TypedSpan, ...] = Field(default_factory=tuple, max_length=64)
    safe_reason_code: str | None = Field(default=None, max_length=64, pattern=IDENTIFIER_PATTERN)
    # P6-RR-R27 (resolves P6-CODEX-091): optional Typed Provenance — see
    # `ModelDetectionProvenance` above for why this stays additive.
    model_provenance: ModelDetectionProvenance | None = None


class PolicyApplicability(StrEnum):
    APPLICABLE = "applicable"
    NOT_APPLICABLE = "not_applicable"
    UNKNOWN = "unknown"


class PolicyDecision(ImmutableContract):
    policy_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    applicability: PolicyApplicability
    required_authority_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=32)
    approval_required: bool = False
    recommended_action_ids: tuple[str, ...] = Field(default_factory=tuple, max_length=32)
    # P5-AUT-003/P5-CODEX-002 Rework: which Policy Snapshot Identity this
    # Decision was actually evaluated against — `0`/`None` (the defaults)
    # mean "not stamped", preserving every pre-existing direct-construction
    # call site; a real Policy Provider always stamps its live values so
    # a Digest mismatch against the live Snapshot at Resolution time is
    # detectable rather than merely assumed consistent.
    policy_revision: int = Field(default=0, ge=0)
    policy_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)


class AuthorityOutcome(StrEnum):
    GRANTED = "granted"
    DENIED = "denied"
    UNKNOWN = "unknown"
    STALE = "stale"


class AuthorityDecision(ImmutableContract):
    action_id: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    outcome: AuthorityOutcome
    # Same Digest-mismatch-detectability rationale as `PolicyDecision`
    # above (P5-AUT-003, architecture §3.3's `authority_revision/scope/
    # digest`).
    authority_revision: int = Field(default=0, ge=0)
    scope: str = Field(default="process_local", min_length=1, max_length=64)
    authority_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)


class ApprovalOutcome(StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNAVAILABLE = "unavailable"
    EXPIRED = "expired"


class ApprovalState(ImmutableContract):
    action_id: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    outcome: ApprovalOutcome
    # Opaque, non-secret reference to an externally-issued Approval —
    # never generated by this process (ADR-5-005).
    approval_reference: str | None = Field(default=None, max_length=128)
    # P5-CODEX-007 Rework (Codex Second Independent Review): an
    # `ApprovalState` previously had no Revision/Scope/Digest/Source
    # Class/Expiry at all, unlike `PolicySnapshot`/`AuthoritySnapshot` —
    # an `approved` Outcome with no established Revision or a past
    # `expires_at` must never be treated as a live grant either, exactly
    # mirroring `AuthoritySnapshot`'s own Stale/Unknown discipline.
    approval_revision: int = Field(default=0, ge=0)
    scope: str = Field(default="process_local", min_length=1, max_length=64)
    source_class: str = Field(default="local_fixed_provider", min_length=1, max_length=64)
    expires_at: str | None = Field(default=None, max_length=40)

    @property
    def digest_sha512(self) -> str:
        return _canonical_digest(self.model_dump(mode="json"))

    @property
    def has_established_revision(self) -> bool:
        return self.approval_revision >= 1

    @property
    def is_expired(self) -> bool:
        return is_expired(self.expires_at)


class RecommendedAction(ImmutableContract):
    action_id: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    reason_detection_id: str | None = Field(
        default=None, max_length=128, pattern=IDENTIFIER_PATTERN
    )
    severity: Severity


class ExecutedAction(ImmutableContract):
    action_id: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    executed: bool
    # Whether this Action, when Executed, actually changed Input,
    # Stream, Output or Persistence — mirrors Phase 4's
    # `ExecutedAction.intervening` (P4-CODEX-006 lineage) so a Result can
    # never blur "something happened" with "was it enforced".
    intervening: bool
    not_executed_reason_code: str | None = Field(
        default=None, max_length=64, pattern=IDENTIFIER_PATTERN
    )


class GuardrailResult(ImmutableContract):
    invocation_id: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)
    point_id: str = Field(min_length=1, max_length=128)
    mode: str = Field(min_length=1, max_length=16, pattern=IDENTIFIER_PATTERN)
    execution_state: ExecutionState
    unavailable_reason_code: str | None = Field(
        default=None, max_length=64, pattern=IDENTIFIER_PATTERN
    )
    degraded_reason_code: str | None = Field(
        default=None, max_length=64, pattern=IDENTIFIER_PATTERN
    )
    detector_registry_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    policy_snapshot_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    authority_snapshot_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    action_registry_digest_sha512: str | None = Field(default=None, pattern=_SHA512_HEX_PATTERN)
    detections: tuple[GuardDetection, ...] = Field(default_factory=tuple, max_length=256)
    policy_decisions: tuple[PolicyDecision, ...] = Field(default_factory=tuple, max_length=64)
    authority_decisions: tuple[AuthorityDecision, ...] = Field(default_factory=tuple, max_length=64)
    approval_states: tuple[ApprovalState, ...] = Field(default_factory=tuple, max_length=64)
    severity: Severity = Severity.NONE
    recommended_actions: tuple[RecommendedAction, ...] = Field(default_factory=tuple, max_length=64)
    executed_actions: tuple[ExecutedAction, ...] = Field(default_factory=tuple, max_length=64)
    latency_ms: int = Field(ge=0, default=0)
    call_count: int = Field(ge=0, default=0)
