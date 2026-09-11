"""Persistence port for every required Artifact (Canonical Design SS8.2/8.4).

`compare_and_swap_active_context_projection` is the one CAS-shaped method:
every other method is a plain, append-only or keyed save/load -- an
Attempt/Plan/Snapshot/StructuredContextArtifact is written exactly once and
never mutated in place, matching the project's existing Append-only Evidence
convention.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from margpa_runtime_llm.modules.conversation.domain.identity import ConversationId

from ..domain.artifacts import (
    ActivationRecord,
    ActiveContextProjection,
    CompactionAttempt,
    CompactionPlan,
    ContextHandoffArtifact,
    PreActionSnapshot,
    RecoveryIndex,
    StructuredContextArtifact,
)
from ..domain.identity import (
    CompactionAttemptId,
    CompactionPlanId,
    ContextBranchId,
    HandoffArtifactId,
    RecoveryIndexId,
    SnapshotId,
    StructuredContextId,
)


@runtime_checkable
class CompactionStorePort(Protocol):
    def save_pre_action_snapshot(self, snapshot: PreActionSnapshot) -> None: ...

    def load_pre_action_snapshot(self, snapshot_id: SnapshotId) -> PreActionSnapshot | None: ...

    def save_compaction_plan(self, plan: CompactionPlan) -> None: ...

    def load_compaction_plan(self, plan_id: CompactionPlanId) -> CompactionPlan | None: ...

    def save_compaction_attempt(self, attempt: CompactionAttempt) -> None:
        """Overwrites the single record for `attempt.attempt_id` -- an
        Attempt has one Identity across its whole Lifecycle (SS9); each
        state transition is still Evidence because `updated_at`, `state`
        and (for terminal states) `terminal_reason` are always written
        together, atomically, never partially."""
        ...

    def load_compaction_attempt(
        self, attempt_id: CompactionAttemptId
    ) -> CompactionAttempt | None: ...

    def list_non_terminal_attempts(
        self, conversation_id: ConversationId, branch_id: ContextBranchId
    ) -> tuple[CompactionAttempt, ...]:
        """Restart Read target: any Attempt found non-terminal here after a
        process restart is stale by construction (SS9's "Process再起動後の
        非Terminal Attemptを勝手に再実行せず") -- the Coordinator marks it
        `interrupted_by_restart` rather than resuming it."""
        ...

    def save_structured_context_artifact(self, artifact: StructuredContextArtifact) -> None: ...

    def load_structured_context_artifact(
        self, structured_context_id: StructuredContextId
    ) -> StructuredContextArtifact | None: ...

    def load_active_context_projection(
        self, conversation_id: ConversationId, branch_id: ContextBranchId
    ) -> ActiveContextProjection | None:
        """`None` means the Conversation/Branch has never had a Projection
        pointer written -- callers treat this identically to a Projection
        whose `structured_context_id is None` (use the original)."""
        ...

    def compare_and_swap_active_context_projection(
        self,
        *,
        conversation_id: ConversationId,
        branch_id: ContextBranchId,
        expected_active_projection_revision: int,
        new_projection: ActiveContextProjection,
    ) -> bool:
        """Atomically replaces the pointer only if the currently stored
        `active_projection_revision` equals `expected_active_projection_
        revision` (0 if no pointer has ever been written) -- returns
        `False` on any mismatch (Late Result, concurrent Attempt, double
        Terminal) without raising and without touching storage."""
        ...

    def save_activation_record(self, record: ActivationRecord) -> None: ...

    def save_recovery_index(self, index: RecoveryIndex) -> None: ...

    def load_recovery_index(self, recovery_index_id: RecoveryIndexId) -> RecoveryIndex | None: ...

    def save_handoff_artifact(self, artifact: ContextHandoffArtifact) -> None: ...

    def load_handoff_artifact(
        self, handoff_artifact_id: HandoffArtifactId
    ) -> ContextHandoffArtifact | None: ...
