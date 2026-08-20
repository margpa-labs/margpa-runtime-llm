"""P2B integration: opt-in binding, durable lifecycle, and zero-write defaults."""

import sqlite3
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

import pytest

from margpa_runtime_llm.modules.conversation.adapters import (
    LocalConversationPersistenceSettings,
    SQLiteConversationStore,
    build_local_conversation_persistence,
)
from margpa_runtime_llm.modules.conversation.adapters.persistence_factory import (
    start_local_conversation_persistence,
)
from margpa_runtime_llm.modules.conversation.adapters.sqlite_migration import (
    LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1,
)
from margpa_runtime_llm.modules.conversation.application import (
    PersistentGenerationIdentities,
)
from margpa_runtime_llm.modules.conversation.contracts import (
    ConversationEvent,
    ConversationEventType,
    ConversationSettings,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationMessageId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSessionId,
    ConversationSnapshot,
    ConversationState,
    ConversationStorageError,
    ConversationStorageErrorCode,
    ConversationTurnId,
    ConversationTurnState,
)
from margpa_runtime_llm.modules.conversation.ports import CommitConversation
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.summarization.public import SummaryMode

SCOPE = ConversationScopeId(value="scope-private")
CID = ConversationId(value="conversation-1")


class FakeSession:
    request_id = "request-integration"
    documentation_augmentation = None

    def events(self) -> Iterator[ConversationEvent]:
        yield ConversationEvent(
            event=ConversationEventType.COMPLETED,
            data={
                "request_id": self.request_id,
                "assistant_message": {"role": "assistant", "content": "durable final"},
            },
        )


class FakeGeneration:
    def start(self, _: object) -> FakeSession:
        return FakeSession()


def op(value: str) -> ConversationOperationId:
    return ConversationOperationId(value=value)


def test_factory_is_write_free_and_disabled_by_default(tmp_path: Path) -> None:
    project_runtime = Path.cwd() / "runtime_data"
    project_state_before = project_runtime.exists()
    disabled = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert (
        not disabled.enabled
        and disabled.store is None
        and disabled.maintenance is None
        and disabled.service is None
    )

    root = tmp_path / "explicit-runtime"
    enabled = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(
            enabled=True,
            runtime_data_root=root,
            scope_id=SCOPE,
        ),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert (
        enabled.enabled
        and enabled.store is not None
        and enabled.maintenance is not None
        and enabled.service is not None
    )
    assert not root.exists()
    assert project_runtime.exists() is project_state_before


def test_durable_generation_survives_new_adapter_instance(tmp_path: Path) -> None:
    root = tmp_path / "explicit-runtime"
    built = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(
            enabled=True,
            runtime_data_root=root,
            scope_id=SCOPE,
        ),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert built.store is not None and built.service is not None
    built.store.initialize_new_store()
    service = built.service
    service.recover_incomplete_conversations()
    service.create_conversation(
        conversation_id=CID,
        session_id=ConversationSessionId(value="session-1"),
        operation_id=op("create"),
    )
    events = tuple(
        service.generate_turn(
            conversation_id=CID,
            content="user canonical",
            settings=ConversationSettings(
                response_language=ResponseLanguage.JA,
                max_new_tokens=128,
                thinking_mode=ThinkingMode.DISABLED,
                thinking_visibility=ThinkingVisibility.HIDDEN,
                summary_mode=SummaryMode.OFF,
                documentation_rag_mode=DocumentationRagMode.DISABLED,
            ),
            identities=PersistentGenerationIdentities(
                turn_id=ConversationTurnId(value="turn-1"),
                user_message_id=ConversationMessageId(value="message-user-1"),
                assistant_message_id=ConversationMessageId(value="message-assistant-1"),
                append_operation_id=op("append"),
                start_operation_id=op("start"),
                terminal_operation_id=op("complete"),
            ),
        )
    )
    assert events[-1].event is ConversationEventType.COMPLETED
    reopened = SQLiteConversationStore(runtime_data_root=root, bound_scope_id=SCOPE)
    stored = reopened.open_ready_store().get(SCOPE, CID)
    assert stored is not None
    assert stored.storage_revision == 4
    assert stored.conversation.turns[0].state is ConversationTurnState.COMPLETED
    assert [message.content for message in stored.conversation.messages] == [
        "user canonical",
        "durable final",
    ]


def test_restart_recovers_max_length_conversation_identity(tmp_path: Path) -> None:
    root = tmp_path / "explicit-runtime"
    long_conversation_id = ConversationId(value="c" * 128)
    built = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(
            enabled=True,
            runtime_data_root=root,
            scope_id=SCOPE,
        ),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert built.store is not None and built.service is not None
    built.store.initialize_new_store()
    built.service.recover_incomplete_conversations()
    built.service.create_conversation(
        conversation_id=long_conversation_id,
        session_id=ConversationSessionId(value="session-before-restart"),
        operation_id=op("create-before-restart"),
    )

    reopened = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(
            enabled=True,
            runtime_data_root=root,
            scope_id=SCOPE,
        ),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert reopened.store is not None and reopened.service is not None
    reopened.store.open_ready_store()
    result = reopened.service.recover_incomplete_conversations()

    assert result.recovered_conversations == 1
    stored = reopened.store.get(SCOPE, long_conversation_id)
    assert stored is not None
    assert stored.conversation.sessions[0].state.value == "interrupted"


def _downgrade_to_legacy_sqlite1(database_path: Path) -> None:
    """Make a freshly-initialized (current-schema) store look like a real pre-Phase-2-E store."""

    with sqlite3.connect(database_path) as connection:
        connection.execute("DROP TABLE turn_citations")
        connection.execute("ALTER TABLE conversations DROP COLUMN title")
        connection.execute(
            "UPDATE store_metadata SET storage_schema_version = ?",
            (LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1,),
        )


def _seed_one_conversation(store: SQLiteConversationStore) -> None:
    now = datetime.now(UTC)
    store.commit(
        CommitConversation(
            scope_id=SCOPE,
            operation_id=op("seed"),
            conversation=ConversationSnapshot(
                scope_id=SCOPE,
                conversation_id=CID,
                state=ConversationState.ACTIVE,
                created_at=now,
                updated_at=now,
            ),
        )
    )


def test_migration_required_store_fails_closed_without_explicit_opt_in(tmp_path: Path) -> None:
    """P2E-CODEX-001: an older-schema store must not start, or be migrated, without opt-in."""

    root = tmp_path / "explicit-runtime"
    built = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(enabled=True, runtime_data_root=root, scope_id=SCOPE),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert built.store is not None
    built.store.initialize_new_store()
    _seed_one_conversation(built.store)
    _downgrade_to_legacy_sqlite1(built.store.database_path)

    with pytest.raises(ConversationStorageError) as no_opt_in:
        start_local_conversation_persistence(
            LocalConversationPersistenceSettings(
                enabled=True, runtime_data_root=root, scope_id=SCOPE
            ),
            generation_service=FakeGeneration(),  # type: ignore[arg-type]
        )
    assert no_opt_in.value.code is ConversationStorageErrorCode.MIGRATION_REQUIRED

    # Fail-closed: the store itself must be unchanged after the refusal.
    unchanged = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(enabled=True, runtime_data_root=root, scope_id=SCOPE),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert unchanged.store is not None
    status = unchanged.store.inspect_schema()
    assert status.readiness.value == "migration_required"
    assert status.storage_schema_version == LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1


def test_explicit_migration_opt_in_upgrades_and_preserves_conversations(tmp_path: Path) -> None:
    """P2E-CODEX-001: explicit migrate -> restart -> existing conversations still load."""

    root = tmp_path / "explicit-runtime"
    built = build_local_conversation_persistence(
        LocalConversationPersistenceSettings(enabled=True, runtime_data_root=root, scope_id=SCOPE),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert built.store is not None
    built.store.initialize_new_store()
    _seed_one_conversation(built.store)
    _downgrade_to_legacy_sqlite1(built.store.database_path)

    composition = start_local_conversation_persistence(
        LocalConversationPersistenceSettings(
            enabled=True,
            runtime_data_root=root,
            scope_id=SCOPE,
            allow_migration=True,
        ),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert composition.store is not None and composition.service is not None
    status = composition.store.inspect_schema()
    assert status.readiness.value == "ready"
    assert status.storage_schema_version != LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1

    # Simulate a normal restart afterwards: no opt-in needed once already migrated.
    reopened = start_local_conversation_persistence(
        LocalConversationPersistenceSettings(enabled=True, runtime_data_root=root, scope_id=SCOPE),
        generation_service=FakeGeneration(),  # type: ignore[arg-type]
    )
    assert reopened.service is not None
    stored = reopened.service.get_conversation(CID)
    assert stored.conversation.conversation_id == CID


def test_allow_migration_without_enabled_is_rejected() -> None:
    with pytest.raises(ValueError, match="migration opt-in"):
        LocalConversationPersistenceSettings(enabled=False, allow_migration=True)
