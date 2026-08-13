from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSnapshot,
    ConversationState,
    ConversationStorageError,
    ConversationStorageErrorCode,
    ConversationSummary,
    StorageMutationOutcome,
)
from margpa_runtime_llm.modules.conversation.ports import (
    CommitConversation,
    ConversationCommitReceipt,
    ConversationListQuery,
    ConversationPage,
    ConversationRepositoryPort,
    ConversationStorageSchemaStatus,
    MigrationPlan,
    StorageReadiness,
    StoredConversation,
)

NOW = datetime(2026, 8, 12, 0, 0, tzinfo=UTC)


def scope(value: str = "scope-1") -> ConversationScopeId:
    return ConversationScopeId(value=value)


def conversation_id(value: str = "conversation-1") -> ConversationId:
    return ConversationId(value=value)


def operation_id(value: str) -> ConversationOperationId:
    return ConversationOperationId(value=value)


def snapshot(
    identity: str = "conversation-1",
    *,
    scope_value: str = "scope-1",
    minute: int = 0,
) -> ConversationSnapshot:
    return ConversationSnapshot(
        scope_id=scope(scope_value),
        conversation_id=conversation_id(identity),
        state=ConversationState.ACTIVE,
        created_at=NOW,
        updated_at=NOW + timedelta(minutes=minute),
    )


class MemoryConversationRepository:
    """Contract double only; it is never registered as a production adapter."""

    def __init__(self) -> None:
        self.records: dict[tuple[str, str], StoredConversation] = {}
        self.receipts: dict[tuple[str, str], ConversationCommitReceipt] = {}
        self.commands: dict[tuple[str, str], CommitConversation] = {}

    def get(
        self,
        scope_id: ConversationScopeId,
        conversation_id: ConversationId,
    ) -> StoredConversation | None:
        return self.records.get((scope_id.value, conversation_id.value))

    def get_commit_receipt(
        self,
        scope_id: ConversationScopeId,
        operation_id: ConversationOperationId,
    ) -> ConversationCommitReceipt | None:
        return self.receipts.get((scope_id.value, operation_id.value))

    def commit(self, command: CommitConversation) -> ConversationCommitReceipt:
        operation_key = (command.scope_id.value, command.operation_id.value)
        prior_command = self.commands.get(operation_key)
        if prior_command is not None:
            if prior_command == command:
                return self.receipts[operation_key]
            raise self._conflict(command, actual_revision=None)

        record_key = (
            command.scope_id.value,
            command.conversation.conversation_id.value,
        )
        current = self.records.get(record_key)
        actual_revision = current.storage_revision if current is not None else None
        if command.expected_revision != actual_revision:
            raise self._conflict(command, actual_revision=actual_revision)

        committed_revision = 1 if actual_revision is None else actual_revision + 1
        receipt = ConversationCommitReceipt(
            scope_id=command.scope_id,
            conversation_id=command.conversation.conversation_id,
            operation_id=command.operation_id,
            previous_revision=actual_revision,
            committed_revision=committed_revision,
        )
        self.records[record_key] = StoredConversation(
            conversation=command.conversation,
            storage_format_version="1",
            storage_revision=committed_revision,
            last_operation_id=command.operation_id,
        )
        self.commands[operation_key] = command
        self.receipts[operation_key] = receipt
        return receipt

    def list(self, query: ConversationListQuery) -> ConversationPage:
        summaries = [
            ConversationSummary(
                scope_id=record.conversation.scope_id,
                conversation_id=record.conversation.conversation_id,
                state=record.conversation.state,
                head_turn_id=record.conversation.head_turn_id,
                created_at=record.conversation.created_at,
                updated_at=record.conversation.updated_at,
            )
            for (scope_value, _), record in self.records.items()
            if scope_value == query.scope_id.value
            and (not query.states or record.conversation.state in query.states)
        ]
        summaries.sort(key=lambda item: (-item.updated_at.timestamp(), item.conversation_id.value))
        offset = int(query.cursor) if query.cursor is not None else 0
        page = summaries[offset : offset + query.limit]
        next_offset = offset + len(page)
        next_cursor = str(next_offset) if next_offset < len(summaries) else None
        return ConversationPage(
            scope_id=query.scope_id,
            items=tuple(page),
            next_cursor=next_cursor,
        )

    @staticmethod
    def _conflict(
        command: CommitConversation,
        *,
        actual_revision: int | None,
    ) -> ConversationStorageError:
        return ConversationStorageError(
            code=ConversationStorageErrorCode.CONFLICT,
            safe_message="The conversation changed before it could be saved.",
            retryable=True,
            mutation_outcome=StorageMutationOutcome.NOT_APPLIED,
            conversation_id=command.conversation.conversation_id.value,
            operation_id=command.operation_id.value,
            expected_revision=command.expected_revision,
            actual_revision=actual_revision,
        )


def test_memory_double_satisfies_repository_protocol() -> None:
    assert isinstance(MemoryConversationRepository(), ConversationRepositoryPort)


def test_create_update_and_read_your_writes() -> None:
    repository = MemoryConversationRepository()
    create = CommitConversation(
        scope_id=scope(),
        operation_id=operation_id("operation-create"),
        conversation=snapshot(),
    )
    created = repository.commit(create)
    assert created.previous_revision is None
    assert created.committed_revision == 1
    assert repository.get(scope(), conversation_id()) is not None

    update = CommitConversation(
        scope_id=scope(),
        operation_id=operation_id("operation-update"),
        expected_revision=1,
        conversation=snapshot(minute=1),
    )
    updated = repository.commit(update)
    assert updated.previous_revision == 1
    assert updated.committed_revision == 2
    assert repository.get(scope(), conversation_id()).storage_revision == 2  # type: ignore[union-attr]


def test_duplicate_operation_is_idempotent_only_for_identical_command() -> None:
    repository = MemoryConversationRepository()
    command = CommitConversation(
        scope_id=scope(),
        operation_id=operation_id("operation-1"),
        conversation=snapshot(),
    )
    first = repository.commit(command)
    assert repository.commit(command) == first
    assert repository.get_commit_receipt(scope(), operation_id("operation-1")) == first

    changed = CommitConversation(
        scope_id=scope(),
        operation_id=operation_id("operation-1"),
        expected_revision=1,
        conversation=snapshot(minute=1),
    )
    with pytest.raises(ConversationStorageError) as captured:
        repository.commit(changed)
    assert captured.value.code is ConversationStorageErrorCode.CONFLICT
    assert captured.value.mutation_outcome is StorageMutationOutcome.NOT_APPLIED


def test_stale_revision_fails_without_mutation() -> None:
    repository = MemoryConversationRepository()
    repository.commit(
        CommitConversation(
            scope_id=scope(),
            operation_id=operation_id("operation-create"),
            conversation=snapshot(),
        )
    )
    with pytest.raises(ConversationStorageError) as captured:
        repository.commit(
            CommitConversation(
                scope_id=scope(),
                operation_id=operation_id("operation-stale"),
                expected_revision=2,
                conversation=snapshot(minute=1),
            )
        )
    assert captured.value.actual_revision == 1
    assert repository.get(scope(), conversation_id()).storage_revision == 1  # type: ignore[union-attr]


def test_scope_isolation_applies_to_get_list_and_operation_receipt() -> None:
    repository = MemoryConversationRepository()
    receipt = repository.commit(
        CommitConversation(
            scope_id=scope("scope-a"),
            operation_id=operation_id("operation-1"),
            conversation=snapshot(scope_value="scope-a"),
        )
    )
    assert receipt.scope_id == scope("scope-a")
    assert repository.get(scope("scope-b"), conversation_id()) is None
    assert repository.get_commit_receipt(scope("scope-b"), operation_id("operation-1")) is None
    assert repository.list(ConversationListQuery(scope_id=scope("scope-b"))).items == ()


def test_list_is_stably_ordered_paginated_and_contains_no_message_content() -> None:
    repository = MemoryConversationRepository()
    for identity, minute in (("conversation-b", 1), ("conversation-a", 1), ("conversation-c", 0)):
        repository.commit(
            CommitConversation(
                scope_id=scope(),
                operation_id=operation_id(f"operation-{identity}"),
                conversation=snapshot(identity, minute=minute),
            )
        )

    first = repository.list(ConversationListQuery(scope_id=scope(), limit=2))
    assert [item.conversation_id.value for item in first.items] == [
        "conversation-a",
        "conversation-b",
    ]
    assert first.next_cursor == "2"
    second = repository.list(
        ConversationListQuery(scope_id=scope(), limit=2, cursor=first.next_cursor)
    )
    assert [item.conversation_id.value for item in second.items] == ["conversation-c"]
    assert "content" not in ConversationSummary.model_fields


def test_commit_rejects_scope_mismatch() -> None:
    with pytest.raises(ValidationError, match="commit scope"):
        CommitConversation(
            scope_id=scope("scope-a"),
            operation_id=operation_id("operation-1"),
            conversation=snapshot(scope_value="scope-b"),
        )


def test_commit_receipt_requires_exact_revision_step() -> None:
    with pytest.raises(ValidationError, match="advance exactly once"):
        ConversationCommitReceipt(
            scope_id=scope(),
            conversation_id=conversation_id(),
            operation_id=operation_id("operation-1"),
            previous_revision=1,
            committed_revision=3,
        )


def test_schema_readiness_fails_closed() -> None:
    with pytest.raises(ValidationError, match="writes require ready"):
        ConversationStorageSchemaStatus(
            readiness=StorageReadiness.MIGRATION_REQUIRED,
            storage_schema_version="1",
            domain_schema_version="1",
            write_enabled=True,
        )
    with pytest.raises(ValidationError, match="active_migration_id"):
        ConversationStorageSchemaStatus(
            readiness=StorageReadiness.MIGRATION_INCOMPLETE,
            storage_schema_version="1",
            domain_schema_version="1",
            write_enabled=False,
        )
    with pytest.raises(ValidationError, match="explicit schema versions"):
        ConversationStorageSchemaStatus(
            readiness=StorageReadiness.READY,
            write_enabled=True,
        )


def test_page_rejects_cross_scope_items() -> None:
    summary = ConversationSummary(
        scope_id=scope("scope-b"),
        conversation_id=conversation_id(),
        state=ConversationState.ACTIVE,
        created_at=NOW,
        updated_at=NOW,
    )
    with pytest.raises(ValidationError, match="another scope"):
        ConversationPage(scope_id=scope("scope-a"), items=(summary,))


def test_migration_plan_requires_explicit_unique_steps_and_version_change() -> None:
    with pytest.raises(ValidationError):
        MigrationPlan(
            plan_id="plan-1",
            source_storage_version="1",
            target_storage_version="1",
            step_ids=("step-1",),
            rollback_supported=True,
        )
    with pytest.raises(ValidationError, match="unique"):
        MigrationPlan(
            plan_id="plan-1",
            source_storage_version="1",
            target_storage_version="2",
            step_ids=("step-1", "step-1"),
            rollback_supported=True,
        )


def test_storage_error_public_shape_exposes_only_safe_fields() -> None:
    error = ConversationStorageError(
        code=ConversationStorageErrorCode.STORAGE_TIMEOUT,
        safe_message="The conversation store timed out.",
        retryable=True,
        mutation_outcome=StorageMutationOutcome.UNKNOWN,
        conversation_id="conversation-1",
        operation_id="operation-1",
    )
    payload = error.to_safe_dict()
    assert payload["mutation_outcome"] == "unknown"
    assert "path" not in payload
    assert "content" not in payload
