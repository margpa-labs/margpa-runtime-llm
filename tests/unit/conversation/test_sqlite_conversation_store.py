"""P2B-STO-001..005, P2B-CAS-001..004, and P2B-FAL-001..002."""

import hashlib
import json
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from margpa_runtime_llm.modules.conversation.adapters.sqlite_conversation_store import (
    SQLiteConversationStore,
    scope_directory_key,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSnapshot,
    ConversationState,
    ConversationStorageError,
    ConversationStorageErrorCode,
)
from margpa_runtime_llm.modules.conversation.ports import (
    CommitConversation,
    ConversationListQuery,
    StorageReadiness,
)

NOW = datetime(2026, 8, 14, tzinfo=UTC)


def scope(value: str = "scope-private") -> ConversationScopeId:
    return ConversationScopeId(value=value)


def snapshot(identity: str = "conversation-1", *, minute: int = 0) -> ConversationSnapshot:
    return ConversationSnapshot(
        scope_id=scope(),
        conversation_id=ConversationId(value=identity),
        state=ConversationState.ACTIVE,
        created_at=NOW,
        updated_at=NOW + timedelta(minutes=minute),
    )


def operation(value: str) -> ConversationOperationId:
    return ConversationOperationId(value=value)


def initialized(tmp_path: Path) -> SQLiteConversationStore:
    root = tmp_path / "runtime-data"
    store = SQLiteConversationStore(runtime_data_root=root, bound_scope_id=scope())
    store.initialize_new_store()
    return store


def test_inspect_and_construction_are_write_free_until_explicit_initialize(
    tmp_path: Path,
) -> None:
    root = tmp_path / "runtime-data"
    store = SQLiteConversationStore(runtime_data_root=root, bound_scope_id=scope())
    assert not root.exists()
    assert store.inspect_schema().readiness is StorageReadiness.EMPTY
    assert not root.exists()
    store.initialize_new_store()
    assert store.inspect_schema().readiness is StorageReadiness.READY
    assert store.database_path.stat().st_mode & 0o777 == 0o600
    assert all(
        path.stat().st_mode & 0o777 == 0o700
        for path in store.database_path.parents
        if path == root or root in path.parents
    )


def test_scope_text_never_appears_in_physical_path(tmp_path: Path) -> None:
    sensitive_scope = scope("tenant-private-name")
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=sensitive_scope,
    )
    assert sensitive_scope.value not in str(store.database_path)
    assert scope_directory_key(sensitive_scope) in str(store.database_path)


def test_unsafe_directory_and_symlink_are_rejected_without_repair(tmp_path: Path) -> None:
    root = tmp_path / "unsafe"
    root.mkdir(mode=0o777)
    root.chmod(0o777)
    store = SQLiteConversationStore(runtime_data_root=root, bound_scope_id=scope())
    with pytest.raises(ConversationStorageError) as captured:
        store.inspect_schema()
    assert captured.value.code is ConversationStorageErrorCode.PERMISSION_DENIED
    assert root.stat().st_mode & 0o777 == 0o777

    safe = tmp_path / "safe"
    safe.mkdir(mode=0o700)
    (safe / "persistent").symlink_to(tmp_path / "elsewhere")
    linked = SQLiteConversationStore(runtime_data_root=safe, bound_scope_id=scope())
    with pytest.raises(ConversationStorageError):
        linked.inspect_schema()


def test_create_update_idempotency_and_two_instance_cas(tmp_path: Path) -> None:
    first = initialized(tmp_path)
    second = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=scope(),
    )
    create = CommitConversation(
        scope_id=scope(),
        operation_id=operation("create"),
        conversation=snapshot(),
    )
    receipt = first.commit(create)
    assert receipt.committed_revision == 1
    assert first.commit(create) == receipt
    assert second.get(scope(), ConversationId(value="conversation-1")).storage_revision == 1  # type: ignore[union-attr]

    update = CommitConversation(
        scope_id=scope(),
        operation_id=operation("update"),
        expected_revision=1,
        conversation=snapshot(minute=1),
    )
    assert second.commit(update).committed_revision == 2
    with pytest.raises(ConversationStorageError) as captured:
        first.commit(
            CommitConversation(
                scope_id=scope(),
                operation_id=operation("stale"),
                expected_revision=1,
                conversation=snapshot(minute=2),
            )
        )
    assert captured.value.code is ConversationStorageErrorCode.CONFLICT
    assert first.get(scope(), ConversationId(value="conversation-1")).storage_revision == 2  # type: ignore[union-attr]


def test_same_operation_with_different_command_is_not_applied(tmp_path: Path) -> None:
    store = initialized(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=scope(),
            operation_id=operation("same"),
            conversation=snapshot(),
        )
    )
    with pytest.raises(ConversationStorageError) as captured:
        store.commit(
            CommitConversation(
                scope_id=scope(),
                operation_id=operation("same"),
                expected_revision=1,
                conversation=snapshot(minute=1),
            )
        )
    assert captured.value.code is ConversationStorageErrorCode.CONFLICT
    assert captured.value.mutation_outcome.value == "not_applied"


def test_list_uses_stable_keyset_cursor_and_never_projects_content(tmp_path: Path) -> None:
    store = initialized(tmp_path)
    for identity, minute in (("conversation-b", 1), ("conversation-a", 1), ("conversation-c", 0)):
        store.commit(
            CommitConversation(
                scope_id=scope(),
                operation_id=operation(f"create-{identity}"),
                conversation=snapshot(identity, minute=minute),
            )
        )
    first = store.list(ConversationListQuery(scope_id=scope(), limit=2))
    assert [item.conversation_id.value for item in first.items] == [
        "conversation-a",
        "conversation-b",
    ]
    assert first.next_cursor is not None
    assert "conversation-b" not in first.next_cursor
    second = store.list(ConversationListQuery(scope_id=scope(), limit=2, cursor=first.next_cursor))
    assert [item.conversation_id.value for item in second.items] == ["conversation-c"]
    assert all("content" not in item.model_dump() for item in first.items)


def test_cursor_and_scope_isolation_fail_closed(tmp_path: Path) -> None:
    store = initialized(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=scope(),
            operation_id=operation("create"),
            conversation=snapshot(),
        )
    )
    other = scope("other-scope")
    assert store.get(other, ConversationId(value="conversation-1")) is None
    assert store.get_commit_receipt(other, operation("create")) is None
    assert store.list(ConversationListQuery(scope_id=other)).items == ()
    with pytest.raises(ConversationStorageError) as captured:
        store.commit(
            CommitConversation(
                scope_id=other,
                operation_id=operation("other"),
                conversation=snapshot().model_copy(update={"scope_id": other}),
            )
        )
    assert captured.value.code is ConversationStorageErrorCode.PERMISSION_DENIED
    with pytest.raises(ConversationStorageError) as invalid:
        store.list(ConversationListQuery(scope_id=scope(), cursor="not-base64"))
    assert invalid.value.code is ConversationStorageErrorCode.INVALID_RECORD


def test_digest_and_metadata_tampering_are_rejected(tmp_path: Path) -> None:
    store = initialized(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=scope(),
            operation_id=operation("create"),
            conversation=snapshot(),
        )
    )
    import sqlite3

    with sqlite3.connect(store.database_path) as connection:
        connection.execute("UPDATE conversations SET snapshot_sha512 = ?", ("0" * 128,))
    with pytest.raises(ConversationStorageError) as captured:
        store.get(scope(), ConversationId(value="conversation-1"))
    assert captured.value.code is ConversationStorageErrorCode.CORRUPT_DATA
    assert str(store.database_path) not in captured.value.safe_message


def test_unknown_store_and_malformed_database_fail_closed(tmp_path: Path) -> None:
    root = tmp_path / "runtime-data"
    store = SQLiteConversationStore(runtime_data_root=root, bound_scope_id=scope())
    store.database_path.parent.mkdir(parents=True, mode=0o700)
    store.database_path.write_bytes(b"not sqlite")
    store.database_path.chmod(0o600)
    assert store.inspect_schema().readiness is StorageReadiness.CORRUPT
    with pytest.raises(ConversationStorageError) as captured:
        store.get(scope(), ConversationId(value="conversation-1"))
    assert captured.value.code is ConversationStorageErrorCode.CORRUPT_DATA
    safe = captured.value.to_safe_dict()
    assert "sqlite" not in str(safe).lower()
    assert str(tmp_path) not in str(safe)


def test_schema_readiness_distinguishes_required_incomplete_and_unsupported(
    tmp_path: Path,
) -> None:
    for name in ("required", "unsupported", "incomplete"):
        (tmp_path / name).mkdir(mode=0o700)
    required = initialized(tmp_path / "required")
    with sqlite3.connect(required.database_path) as connection:
        connection.execute("UPDATE store_metadata SET storage_schema_version = 'legacy-fixture-1'")
    registered = SQLiteConversationStore(
        runtime_data_root=tmp_path / "required" / "runtime-data",
        bound_scope_id=scope(),
        known_legacy_versions=("legacy-fixture-1",),
    )
    assert registered.inspect_schema().readiness is StorageReadiness.MIGRATION_REQUIRED

    unsupported = initialized(tmp_path / "unsupported")
    with sqlite3.connect(unsupported.database_path) as connection:
        connection.execute("UPDATE store_metadata SET storage_schema_version = 'future-99'")
    assert unsupported.inspect_schema().readiness is StorageReadiness.UNSUPPORTED

    incomplete = initialized(tmp_path / "incomplete")
    marker_dir = incomplete.migration_marker_directory
    marker_dir.mkdir(parents=True, mode=0o700)
    marker = marker_dir / "migration.json"
    marker.write_text(
        '{"migration_id":"migration-1","state":"in_progress"}',
        encoding="utf-8",
    )
    marker.chmod(0o600)
    status = incomplete.inspect_schema()
    assert status.readiness is StorageReadiness.MIGRATION_INCOMPLETE
    assert status.active_migration_id == "migration-1"


def test_unknown_envelope_field_and_domain_mismatch_are_rejected(tmp_path: Path) -> None:
    store = initialized(tmp_path)
    store.commit(
        CommitConversation(
            scope_id=scope(),
            operation_id=operation("create"),
            conversation=snapshot(),
        )
    )
    with sqlite3.connect(store.database_path) as connection:
        row = connection.execute("SELECT snapshot_json FROM conversations").fetchone()
        value = json.loads(bytes(row[0]).decode("utf-8"))
        value["unknown"] = True
        payload = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        connection.execute(
            "UPDATE conversations SET snapshot_json = ?, snapshot_sha512 = ?",
            (payload, hashlib.sha512(payload).hexdigest()),
        )
    with pytest.raises(ConversationStorageError) as captured:
        store.get(scope(), ConversationId(value="conversation-1"))
    assert captured.value.code is ConversationStorageErrorCode.INVALID_RECORD


def test_lock_timeout_is_bounded_and_reported_without_raw_driver_text(tmp_path: Path) -> None:
    store = initialized(tmp_path)
    contender = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=scope(),
        busy_timeout_ms=1,
    )
    lock = sqlite3.connect(store.database_path, isolation_level=None)
    lock.execute("BEGIN IMMEDIATE")
    try:
        with pytest.raises(ConversationStorageError) as captured:
            contender.commit(
                CommitConversation(
                    scope_id=scope(),
                    operation_id=operation("locked"),
                    conversation=snapshot(),
                )
            )
    finally:
        lock.rollback()
        lock.close()
    assert captured.value.code is ConversationStorageErrorCode.STORAGE_TIMEOUT
    assert "locked" not in captured.value.safe_message.lower()


class _CommitThenLoseResponse:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def __getattr__(self, name: str) -> object:
        return getattr(self._connection, name)

    def commit(self) -> None:
        self._connection.commit()
        raise sqlite3.OperationalError("simulated response loss")


class _ResponseLossStore(SQLiteConversationStore):
    def _connect(self, *, read_only: bool) -> sqlite3.Connection:
        connection = super()._connect(read_only=read_only)
        if read_only:
            return connection
        return _CommitThenLoseResponse(connection)  # type: ignore[return-value]


def test_commit_response_loss_reports_unknown_and_receipt_converges(tmp_path: Path) -> None:
    normal = initialized(tmp_path)
    lossy = _ResponseLossStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=scope(),
    )
    command = CommitConversation(
        scope_id=scope(),
        operation_id=operation("response-loss"),
        conversation=snapshot(),
    )
    with pytest.raises(ConversationStorageError) as captured:
        lossy.commit(command)
    assert captured.value.code is ConversationStorageErrorCode.ATOMIC_COMMIT_FAILED
    assert captured.value.mutation_outcome.value == "unknown"
    receipt = normal.get_commit_receipt(scope(), operation("response-loss"))
    assert receipt is not None and receipt.committed_revision == 1
    assert normal.commit(command) == receipt


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (sqlite3.OperationalError("attempt to write a readonly database"), "read_only"),
        (sqlite3.OperationalError("database or disk is full"), "capacity_exceeded"),
        (PermissionError("permission denied"), "permission_denied"),
    ],
)
def test_write_failures_are_normalized_without_sensitive_details(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    error: BaseException,
    expected: str,
) -> None:
    store = initialized(tmp_path)

    def fail_connect(*, read_only: bool) -> sqlite3.Connection:
        if read_only:
            return SQLiteConversationStore._connect(store, read_only=True)
        raise error

    monkeypatch.setattr(store, "_connect", fail_connect)
    with pytest.raises(ConversationStorageError) as captured:
        store.commit(
            CommitConversation(
                scope_id=scope(),
                operation_id=operation("failure"),
                conversation=snapshot(),
            )
        )
    assert captured.value.code.value == expected
    payload = str(captured.value.to_safe_dict()).lower()
    assert str(tmp_path).lower() not in payload
    assert "permission denied" not in payload
