"""Storage-neutral ports for persistent conversations and schema maintenance."""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol, runtime_checkable

from pydantic import Field, field_validator, model_validator

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    PersistedTurnCitationEvidence,
)
from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract
from margpa_runtime_llm.modules.web_knowledge import PersistedTurnWebCitationEvidence

from ..domain.identity import (
    ConversationId,
    ConversationOperationId,
    ConversationScopeId,
)
from ..domain.models import (
    ConversationSnapshot,
    ConversationState,
    ConversationSummary,
    ConversationTurnState,
)

VERSION_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$"


class StoredConversation(ImmutableContract):
    conversation: ConversationSnapshot
    storage_format_version: str = Field(
        min_length=1,
        max_length=64,
        pattern=VERSION_PATTERN,
    )
    storage_revision: int = Field(strict=True, ge=1)
    last_operation_id: ConversationOperationId


class CommitConversation(ImmutableContract):
    scope_id: ConversationScopeId
    operation_id: ConversationOperationId
    expected_revision: int | None = Field(default=None, strict=True, ge=1)
    conversation: ConversationSnapshot
    citation_evidence: PersistedTurnCitationEvidence | None = None
    web_citation_evidence: PersistedTurnWebCitationEvidence | None = None
    """P8-A (P8-ACC-011): independent of `citation_evidence` above — a Turn
    may carry either, both, or neither, committed atomically alongside the
    same Turn either way."""

    @model_validator(mode="after")
    def validate_scope(self) -> CommitConversation:
        if self.scope_id != self.conversation.scope_id:
            raise ValueError("commit scope does not match the conversation scope")
        if self.citation_evidence is not None:
            if self.citation_evidence.conversation_id != self.conversation.conversation_id.value:
                raise ValueError("citation evidence conversation id does not match the commit")
            matching_turn = next(
                (
                    turn
                    for turn in self.conversation.turns
                    if turn.turn_id.value == self.citation_evidence.turn_id
                ),
                None,
            )
            if matching_turn is None or matching_turn.state is not ConversationTurnState.COMPLETED:
                raise ValueError("citation evidence must reference a completed turn in the commit")
        if self.web_citation_evidence is not None:
            if (
                self.web_citation_evidence.conversation_id
                != self.conversation.conversation_id.value
            ):
                raise ValueError("web citation evidence conversation id does not match the commit")
            matching_web_turn = next(
                (
                    turn
                    for turn in self.conversation.turns
                    if turn.turn_id.value == self.web_citation_evidence.turn_id
                ),
                None,
            )
            if matching_web_turn is None or matching_web_turn.state not in (
                ConversationTurnState.COMPLETED,
                # P8-MR7-2 (P8-CODEX-014): a Manual Web Evidence attempt
                # that ends the Turn in FAILED (Fail-closed Grounding,
                # P8-MR1's `web_evidence_fetch_failed`) is real Evidence —
                # the Fetch/Rejection genuinely happened — never only
                # attachable to a Turn that went on to produce an Assistant
                # Message. Documentation RAG's own `citation_evidence`
                # invariant just above is deliberately left COMPLETED-only
                # (out of this Package's scope; Documentation RAG's
                # analogous Fail-closed path is a separate, pre-existing
                # gap, not introduced here).
                ConversationTurnState.FAILED,
            ):
                raise ValueError(
                    "web citation evidence must reference a completed or failed turn in the commit"
                )
        return self


class ConversationCommitReceipt(ImmutableContract):
    scope_id: ConversationScopeId
    conversation_id: ConversationId
    operation_id: ConversationOperationId
    previous_revision: int | None = Field(default=None, strict=True, ge=1)
    committed_revision: int = Field(strict=True, ge=1)

    @model_validator(mode="after")
    def validate_revision_step(self) -> ConversationCommitReceipt:
        expected = 1 if self.previous_revision is None else self.previous_revision + 1
        if self.committed_revision != expected:
            raise ValueError("committed revision must advance exactly once")
        return self


class ConversationListQuery(ImmutableContract):
    scope_id: ConversationScopeId
    states: frozenset[ConversationState] = Field(default_factory=frozenset)
    limit: int = Field(default=50, strict=True, ge=1, le=100)
    cursor: str | None = Field(default=None, max_length=512)

    @field_validator("cursor")
    @classmethod
    def validate_cursor(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("conversation list cursor must not be blank")
        return value


class ConversationPage(ImmutableContract):
    scope_id: ConversationScopeId
    items: tuple[ConversationSummary, ...]
    next_cursor: str | None = Field(default=None, max_length=512)

    @field_validator("next_cursor")
    @classmethod
    def validate_next_cursor(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("conversation page cursor must not be blank")
        return value

    @model_validator(mode="after")
    def validate_stable_order(self) -> ConversationPage:
        if any(item.scope_id != self.scope_id for item in self.items):
            raise ValueError("conversation page contains an item from another scope")
        identities = [item.conversation_id.value for item in self.items]
        if len(identities) != len(set(identities)):
            raise ValueError("conversation page contains duplicate identities")
        expected = sorted(
            self.items,
            key=lambda item: (-item.updated_at.timestamp(), item.conversation_id.value),
        )
        if list(self.items) != expected:
            raise ValueError("conversation page items are not in stable order")
        return self


@runtime_checkable
class ConversationRepositoryPort(Protocol):
    def get(
        self,
        scope_id: ConversationScopeId,
        conversation_id: ConversationId,
    ) -> StoredConversation | None: ...

    def get_commit_receipt(
        self,
        scope_id: ConversationScopeId,
        operation_id: ConversationOperationId,
    ) -> ConversationCommitReceipt | None: ...

    def commit(self, command: CommitConversation) -> ConversationCommitReceipt: ...

    def list(self, query: ConversationListQuery) -> ConversationPage: ...


class StorageReadiness(StrEnum):
    EMPTY = "empty"
    READY = "ready"
    MIGRATION_REQUIRED = "migration_required"
    MIGRATION_INCOMPLETE = "migration_incomplete"
    UNSUPPORTED = "unsupported"
    CORRUPT = "corrupt"


class ConversationStorageSchemaStatus(ImmutableContract):
    readiness: StorageReadiness
    storage_schema_version: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        pattern=VERSION_PATTERN,
    )
    domain_schema_version: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        pattern=VERSION_PATTERN,
    )
    active_migration_id: str | None = Field(default=None, min_length=1, max_length=128)
    write_enabled: bool

    @model_validator(mode="after")
    def validate_readiness(self) -> ConversationStorageSchemaStatus:
        if self.readiness is not StorageReadiness.READY and self.write_enabled:
            raise ValueError("conversation storage writes require ready state")
        if self.readiness is StorageReadiness.READY and (
            self.storage_schema_version is None or self.domain_schema_version is None
        ):
            raise ValueError("ready conversation storage requires explicit schema versions")
        if (
            self.readiness is StorageReadiness.MIGRATION_INCOMPLETE
            and self.active_migration_id is None
        ):
            raise ValueError("incomplete migration requires active_migration_id")
        return self


class MigrationPlan(ImmutableContract):
    plan_id: str = Field(min_length=1, max_length=128)
    source_storage_version: str = Field(
        min_length=1,
        max_length=64,
        pattern=VERSION_PATTERN,
    )
    target_storage_version: str = Field(
        min_length=1,
        max_length=64,
        pattern=VERSION_PATTERN,
    )
    step_ids: tuple[str, ...] = Field(min_length=1)
    requires_exclusive_access: bool = True
    rollback_supported: bool

    @field_validator("step_ids")
    @classmethod
    def validate_step_ids(cls, values: tuple[str, ...]) -> tuple[str, ...]:
        if any(not value.strip() or len(value) > 128 for value in values):
            raise ValueError("migration step identity is invalid")
        if len(values) != len(set(values)):
            raise ValueError("migration step identities must be unique")
        return values

    @model_validator(mode="after")
    def validate_versions(self) -> MigrationPlan:
        if self.source_storage_version == self.target_storage_version:
            raise ValueError("migration source and target versions must differ")
        return self


class MigrationReceipt(ImmutableContract):
    migration_id: str = Field(min_length=1, max_length=128)
    plan_id: str = Field(min_length=1, max_length=128)
    checkpoint_id: str = Field(min_length=1, max_length=128)
    source_digest: str = Field(pattern=r"^[a-f0-9]{128}$")
    target_digest: str = Field(pattern=r"^[a-f0-9]{128}$")
    record_count: int = Field(strict=True, ge=0)


@runtime_checkable
class ConversationStorageMaintenancePort(Protocol):
    def inspect_schema(self) -> ConversationStorageSchemaStatus: ...

    def plan_migration(self, target_version: str) -> MigrationPlan: ...

    def migrate(self, plan: MigrationPlan, checkpoint_id: str) -> MigrationReceipt: ...

    def rollback(self, receipt: MigrationReceipt) -> None: ...
