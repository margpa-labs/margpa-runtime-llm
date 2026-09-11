"""Opaque identities for the Context Compaction domain.

`ConversationId`/`ConversationScopeId` are intentionally re-used from the
Conversation module (Canonical Design SS8.1) rather than re-declared here --
Compaction Artifacts reference the same Conversation identity, never a
duplicate/parallel one.
"""

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class _OpaqueIdentifier(ImmutableContract):
    value: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)


class ContextBranchId(_OpaqueIdentifier):
    """Identity of one linear Turn lineage within a Conversation.

    The Conversation module has no persisted multi-branch concept today
    (`project_generation_history()` walks a single `head_turn_id` ->
    `parent_turn_id` chain) -- every Conversation currently has exactly one
    live branch. This identity exists so the Identity Chain and Artifact
    schema are forward-compatible with a future multi-branch Conversation
    feature without a schema break; until that exists, every caller uses
    the single `DEFAULT_BRANCH_ID` constant below.
    """


DEFAULT_BRANCH_ID = ContextBranchId(value="main")


class ContextActionId(_OpaqueIdentifier):
    """Identity of one Manual/Preview/Auto Compaction Action request."""


class SnapshotId(_OpaqueIdentifier):
    """Identity of one Pre-action Snapshot."""


class CompactionPlanId(_OpaqueIdentifier):
    """Identity of one Frozen Compaction Plan."""


class CompactionAttemptId(_OpaqueIdentifier):
    """Identity of one Compaction Attempt (one Plan may be attempted once)."""


class StructuredContextId(_OpaqueIdentifier):
    """Identity of one Structured Context Artifact (a Candidate or Active one)."""


class RecoveryIndexId(_OpaqueIdentifier):
    """Identity of one Recovery Index."""


class HandoffArtifactId(_OpaqueIdentifier):
    """Identity of one Context Handoff Artifact."""
