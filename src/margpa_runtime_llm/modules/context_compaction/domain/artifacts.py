"""Required Artifacts (Canonical Design SS8.2/8.3/9).

Every Artifact here is an `ImmutableContract` (frozen, `extra="forbid"`,
carries `schema_version`) -- constructing one already satisfies the
"Schema Version" half of SS8.4's Persistence contract; Digest and Restart
Read live in the Store Adapter (`adapters/local_filesystem_store.py`), not
here, since Digest is a property of the *serialized bytes*, not the Domain
object.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.conversation.domain.identity import (
    ConversationId,
    ConversationMessageId,
    ConversationTurnId,
)
from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .budget import ContextBudgetSnapshot
from .identity import (
    CompactionAttemptId,
    CompactionPlanId,
    ContextActionId,
    ContextBranchId,
    HandoffArtifactId,
    RecoveryIndexId,
    SnapshotId,
    StructuredContextId,
)

DIGEST_PATTERN = r"^[a-f0-9]{128}$"


class ContextSourceTurnReference(ImmutableContract):
    """A pointer into the Canonical Conversation, never a content copy."""

    turn_id: ConversationTurnId
    message_id: ConversationMessageId
    source_conversation_revision: int = Field(ge=1)


class ContextSourceReference(ImmutableContract):
    """A pointer to non-Turn Evidence (e.g. an Experiment/Judge Artifact)."""

    description: str = Field(min_length=1, max_length=512)
    artifact_kind: str = Field(min_length=1, max_length=128)
    artifact_id: str = Field(min_length=1, max_length=256)
    digest_sha512: str | None = Field(default=None, pattern=DIGEST_PATTERN)


class RecentVerbatimTurn(ImmutableContract):
    source: ContextSourceTurnReference
    role: str = Field(min_length=1, max_length=32)
    content: str = Field(min_length=1, max_length=32_768)


class OmittedRange(ImmutableContract):
    first_source: ContextSourceTurnReference
    last_source: ContextSourceTurnReference
    turn_count: int = Field(ge=1)
    rehydratable: bool
    reason: str = Field(min_length=1, max_length=512)


class StructuredContextSections(ImmutableContract):
    """SS8.3's required Section set. Every fact here must trace to a
    `source` reference already present in the Canonical Conversation --
    Invariant 13/SS10.1's "Sourceに存在しないFactを...追加しない" is
    structural here: there is no free-text field without an adjacent
    `ContextSourceTurnReference`/`ContextSourceReference`.
    """

    current_objective: str = Field(min_length=1, max_length=4096)
    current_position: str = Field(min_length=1, max_length=4096)
    fixed_decisions: tuple[str, ...] = Field(default=())
    constraints: tuple[str, ...] = Field(default=())
    authority: tuple[str, ...] = Field(default=())
    completed: tuple[str, ...] = Field(default=())
    unfinished: tuple[str, ...] = Field(default=())
    deferred: tuple[str, ...] = Field(default=())
    blocked: tuple[str, ...] = Field(default=())
    known_failures: tuple[str, ...] = Field(default=())
    risks: tuple[str, ...] = Field(default=())
    recovery_points: tuple[str, ...] = Field(default=())
    important_facts: tuple[str, ...] = Field(default=())
    important_fact_sources: tuple[ContextSourceTurnReference, ...] = Field(default=())
    evidence_pointers: tuple[ContextSourceReference, ...] = Field(default=())
    exact_next_route: str = Field(min_length=1, max_length=4096)
    recent_verbatim_tail: tuple[RecentVerbatimTurn, ...] = Field(default=())
    omitted_ranges: tuple[OmittedRange, ...] = Field(default=())

    @model_validator(mode="after")
    def validate_fact_sources(self) -> StructuredContextSections:
        if len(self.important_fact_sources) != len(self.important_facts):
            raise ValueError(
                "every important fact requires exactly one source turn reference"
            )
        return self

    def source_summary_is_empty(self) -> bool:
        """True when no genuine Source content survived Compaction at all --
        the one shape Validation must reject outright (CL-P9-3-C.5)."""

        return not self.recent_verbatim_tail and not self.important_facts


class CompactionStrategy(StrEnum):
    DETERMINISTIC_EXTRACTIVE = "deterministic_extractive"
    """SS10.1's required, Model-Call-0 Baseline Builder."""
    STRUCTURED_LLM = "structured_llm"
    """SS10.2's Optional Provider-neutral Builder."""


class StructuredContextArtifact(ImmutableContract):
    structured_context_id: StructuredContextId
    conversation_id: ConversationId
    branch_id: ContextBranchId
    source_conversation_revision: int = Field(ge=1)
    configured_builder: CompactionStrategy
    executed_builder: CompactionStrategy | None = Field(default=None)
    """`None` until the Attempt that produced this Artifact actually ran a
    Builder Call (Invariant 18/SS10.2: Call 0 is never recorded as
    Completed) -- set only once, to the Strategy genuinely executed,
    which may differ from `configured_builder` when a Structured/LLM
    Builder became Unavailable and Deterministic ran instead (SS6.4)."""
    token_count: int = Field(ge=0)
    sections: StructuredContextSections
    created_at: datetime


class PreActionSnapshot(ImmutableContract):
    """The Rollback target: the Active Projection pointer state immediately
    before this Action's own Candidate work begins (Invariant 6)."""

    snapshot_id: SnapshotId
    action_id: ContextActionId
    conversation_id: ConversationId
    branch_id: ContextBranchId
    source_conversation_revision: int = Field(ge=1)
    previous_active_projection_revision: int = Field(ge=0)
    previous_structured_context_id: StructuredContextId | None = Field(default=None)
    captured_at: datetime


class CompactionPlan(ImmutableContract):
    """Frozen at plan time; never mutated afterward (SS9's `planned` state)."""

    plan_id: CompactionPlanId
    action_id: ContextActionId
    snapshot_id: SnapshotId
    conversation_id: ConversationId
    branch_id: ContextBranchId
    source_conversation_revision: int = Field(ge=1)
    budget: ContextBudgetSnapshot
    configured_builder: CompactionStrategy
    token_budget: int = Field(gt=0)
    deadline_at: datetime
    max_model_calls: int = Field(ge=0)
    frozen_at: datetime


class CompactionAttemptState(StrEnum):
    REQUESTED = "requested"
    PREFLIGHT = "preflight"
    SNAPSHOT_PERSISTED = "snapshot_persisted"
    PLANNED = "planned"
    CANDIDATE_BUILDING = "candidate_building"
    VALIDATING = "validating"
    CANDIDATE_PERSISTED = "candidate_persisted"
    ACTIVATING = "activating"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    CANCELLED = "cancelled"
    CONFLICTED = "conflicted"
    ROLLED_BACK = "rolled_back"
    INTERRUPTED_BY_RESTART = "interrupted_by_restart"


TERMINAL_ATTEMPT_STATES = frozenset(
    {
        CompactionAttemptState.COMPLETED,
        CompactionAttemptState.REJECTED,
        CompactionAttemptState.FAILED,
        CompactionAttemptState.CANCELLED,
        CompactionAttemptState.CONFLICTED,
        CompactionAttemptState.ROLLED_BACK,
        CompactionAttemptState.INTERRUPTED_BY_RESTART,
    }
)

_ALLOWED_ATTEMPT_TRANSITIONS: dict[CompactionAttemptState, frozenset[CompactionAttemptState]] = {
    CompactionAttemptState.REQUESTED: frozenset(
        {CompactionAttemptState.PREFLIGHT, CompactionAttemptState.REJECTED}
    ),
    CompactionAttemptState.PREFLIGHT: frozenset(
        {
            CompactionAttemptState.SNAPSHOT_PERSISTED,
            CompactionAttemptState.REJECTED,
            CompactionAttemptState.FAILED,
        }
    ),
    CompactionAttemptState.SNAPSHOT_PERSISTED: frozenset(
        {CompactionAttemptState.PLANNED, CompactionAttemptState.FAILED}
    ),
    CompactionAttemptState.PLANNED: frozenset(
        {CompactionAttemptState.CANDIDATE_BUILDING, CompactionAttemptState.FAILED}
    ),
    CompactionAttemptState.CANDIDATE_BUILDING: frozenset(
        {CompactionAttemptState.VALIDATING, CompactionAttemptState.FAILED}
    ),
    CompactionAttemptState.VALIDATING: frozenset(
        {
            CompactionAttemptState.CANDIDATE_PERSISTED,
            CompactionAttemptState.REJECTED,
            CompactionAttemptState.FAILED,
        }
    ),
    CompactionAttemptState.CANDIDATE_PERSISTED: frozenset(
        {CompactionAttemptState.ACTIVATING, CompactionAttemptState.FAILED}
    ),
    CompactionAttemptState.ACTIVATING: frozenset(
        {
            CompactionAttemptState.COMPLETED,
            CompactionAttemptState.CONFLICTED,
            CompactionAttemptState.FAILED,
        }
    ),
}
"""`cancelled` and `interrupted_by_restart` are deliberately NOT listed per
phase here -- both can legitimately interrupt an Attempt from ANY
non-terminal phase (a Cancel request racing an in-flight pipeline; a
process restart catching an Attempt mid-flight at any point), so
`validate_attempt_transition` below allows them universally from every
non-terminal state instead of duplicating them into each phase's own set."""

_UNIVERSAL_NON_TERMINAL_ESCAPES = frozenset(
    {CompactionAttemptState.CANCELLED, CompactionAttemptState.INTERRUPTED_BY_RESTART}
)


_ROLLBACK_EXCEPTION = (CompactionAttemptState.COMPLETED, CompactionAttemptState.ROLLED_BACK)
"""The one explicit exception to "a terminal state cannot transition": a
Completed (and therefore already-Activated) Attempt is the sole target
Rollback ever acts on, deliberately later than the Attempt's own original
Lifecycle -- SS9 lists `rolled_back` as one of the Attempt's own Terminal
states precisely so this stays Evidence on the Attempt itself, not only on
the separate `ActivationRecord`."""


def validate_attempt_transition(
    current: CompactionAttemptState, target: CompactionAttemptState
) -> None:
    if (current, target) == _ROLLBACK_EXCEPTION:
        return
    if current in TERMINAL_ATTEMPT_STATES:
        raise ValueError(f"a terminal attempt state ({current.value}) cannot transition")
    if target in _UNIVERSAL_NON_TERMINAL_ESCAPES:
        return
    if target not in _ALLOWED_ATTEMPT_TRANSITIONS.get(current, frozenset()):
        raise ValueError(f"attempt transition {current.value} -> {target.value} is not allowed")


class CompactionAttempt(ImmutableContract):
    attempt_id: CompactionAttemptId
    plan_id: CompactionPlanId
    action_id: ContextActionId
    snapshot_id: SnapshotId
    conversation_id: ConversationId
    branch_id: ContextBranchId
    state: CompactionAttemptState
    structured_context_id: StructuredContextId | None = Field(default=None)
    requested_at: datetime
    updated_at: datetime
    terminal_reason: str | None = Field(default=None, max_length=512)
    error_code: str | None = Field(default=None, max_length=128)

    @model_validator(mode="after")
    def validate_terminal_shape(self) -> CompactionAttempt:
        is_terminal = self.state in TERMINAL_ATTEMPT_STATES
        if is_terminal and self.terminal_reason is None:
            raise ValueError("a terminal compaction attempt requires terminal_reason")
        if not is_terminal and self.terminal_reason is not None:
            raise ValueError("a non-terminal compaction attempt must not carry terminal_reason")
        return self

    def transitioned(
        self,
        *,
        target: CompactionAttemptState,
        updated_at: datetime,
        structured_context_id: StructuredContextId | None = None,
        terminal_reason: str | None = None,
        error_code: str | None = None,
    ) -> CompactionAttempt:
        validate_attempt_transition(self.state, target)
        candidate = self.model_dump()
        candidate.update(
            {
                "state": target.value,
                "updated_at": updated_at,
                "structured_context_id": (
                    structured_context_id.model_dump()
                    if structured_context_id is not None
                    else (
                        self.structured_context_id.model_dump()
                        if self.structured_context_id is not None
                        else None
                    )
                ),
                "terminal_reason": terminal_reason,
                "error_code": error_code,
            }
        )
        return CompactionAttempt.model_validate(candidate)


class ActivationResult(StrEnum):
    ACTIVATED = "activated"
    ROLLED_BACK = "rolled_back"
    REJECTED_STALE_SOURCE_REVISION = "rejected_stale_source_revision"
    REJECTED_STALE_PROJECTION_REVISION = "rejected_stale_projection_revision"
    REJECTED_CONFLICT = "rejected_conflict"


class ActivationRecord(ImmutableContract):
    """Evidence of one CAS Activation or Rollback attempt -- recorded
    whether it succeeded or was rejected (Rollback itself is Evidence,
    per SS9's "Rollback自体もIdentity...をEvidence化する")."""

    attempt_id: CompactionAttemptId
    conversation_id: ConversationId
    branch_id: ContextBranchId
    expected_source_conversation_revision: int = Field(ge=1)
    observed_source_conversation_revision: int = Field(ge=1)
    expected_active_projection_revision: int = Field(ge=0)
    observed_active_projection_revision: int = Field(ge=0)
    result: ActivationResult
    new_active_projection_revision: int | None = Field(default=None, ge=0)
    recorded_at: datetime

    @model_validator(mode="after")
    def validate_result_shape(self) -> ActivationRecord:
        if (
            self.result in (ActivationResult.ACTIVATED, ActivationResult.ROLLED_BACK)
            and self.new_active_projection_revision is None
        ):
            raise ValueError("a successful activation/rollback requires the new revision")
        if (
            self.result
            not in (ActivationResult.ACTIVATED, ActivationResult.ROLLED_BACK)
            and self.new_active_projection_revision is not None
        ):
            raise ValueError("a rejected activation must not carry a new revision")
        return self


class ActiveContextProjection(ImmutableContract):
    """The CAS-guarded pointer: which `StructuredContextArtifact` (if any)
    is currently substituted for the original Generation-time projection.
    `structured_context_id is None` means "use the original, unmodified
    projection" -- the initial state of every Conversation/Branch, and the
    state any Rollback restores.
    """

    conversation_id: ConversationId
    branch_id: ContextBranchId
    active_projection_revision: int = Field(ge=0)
    structured_context_id: StructuredContextId | None = Field(default=None)
    source_conversation_revision: int = Field(ge=1)
    updated_at: datetime


class RecoveryIndexEntry(ImmutableContract):
    entry_id: str = Field(min_length=1, max_length=128)
    omitted_range: OmittedRange
    rehydration_token_estimate: int = Field(ge=0)


class RecoveryIndex(ImmutableContract):
    recovery_index_id: RecoveryIndexId
    structured_context_id: StructuredContextId
    conversation_id: ConversationId
    branch_id: ContextBranchId
    source_conversation_revision: int = Field(ge=1)
    entries: tuple[RecoveryIndexEntry, ...] = Field(default=())
    created_at: datetime

    @model_validator(mode="after")
    def validate_unique_entries(self) -> RecoveryIndex:
        ids = [entry.entry_id for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("recovery index entries must have unique identities")
        return self


class RehydrationFailureCode(StrEnum):
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    STALE = "stale"
    DIGEST_MISMATCH = "digest_mismatch"
    BUDGET_EXCEEDED = "budget_exceeded"


class SelectiveRehydrationRequest(ImmutableContract):
    recovery_index_id: RecoveryIndexId
    conversation_id: ConversationId
    branch_id: ContextBranchId
    requested_entry_ids: tuple[str, ...] = Field(min_length=1)
    token_budget: int = Field(gt=0)


class RehydratedTurn(ImmutableContract):
    entry_id: str = Field(min_length=1, max_length=128)
    source: ContextSourceTurnReference
    role: str = Field(min_length=1, max_length=32)
    content: str = Field(min_length=1, max_length=32_768)


class RehydrationFailure(ImmutableContract):
    entry_id: str = Field(min_length=1, max_length=128)
    code: RehydrationFailureCode
    safe_message: str = Field(min_length=1, max_length=512)


class SelectiveRehydrationResult(ImmutableContract):
    request: SelectiveRehydrationRequest
    rehydrated: tuple[RehydratedTurn, ...] = Field(default=())
    failures: tuple[RehydrationFailure, ...] = Field(default=())
    total_tokens_used: int = Field(ge=0)
    resolved_at: datetime


class ContextHandoffArtifact(ImmutableContract):
    """Built read-only from the Canonical Conversation; Active Context
    Mutation 0 (Invariant: Handoff生成でActive Context Mutation 0)."""

    handoff_artifact_id: HandoffArtifactId
    conversation_id: ConversationId
    branch_id: ContextBranchId
    source_conversation_revision: int = Field(ge=1)
    sections: StructuredContextSections
    created_at: datetime
