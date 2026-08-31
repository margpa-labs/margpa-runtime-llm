"""P2B-MIG-001..004 explicit migration, checkpoint, and rollback evidence."""

import hashlib
import os
import sqlite3
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import pytest

from margpa_runtime_llm.modules.conversation.adapters.sqlite_conversation_store import (
    STORAGE_SCHEMA_VERSION,
    SQLiteConversationStore,
)
from margpa_runtime_llm.modules.conversation.adapters.sqlite_migration import (
    CONVERSATION_TITLE_MIGRATION_STEP,
    LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1,
    LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2,
    TURN_CITATIONS_MIGRATION_STEP,
    TURN_WEB_CITATIONS_MIGRATION_STEP,
    SQLiteConversationMaintenance,
    SQLiteMigrationEngine,
    SQLiteMigrationStep,
    _artifact_key,
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
    MigrationPlan,
    StorageReadiness,
)


def digest(path: Path) -> str:
    return hashlib.sha512(path.read_bytes()).hexdigest()


def legacy_store(tmp_path: Path) -> tuple[SQLiteConversationStore, str]:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=ConversationScopeId(value="scope-private"),
        known_legacy_versions=("legacy-fixture-1",),
    )
    store.initialize_new_store()
    with sqlite3.connect(store.database_path) as connection:
        connection.execute("UPDATE store_metadata SET storage_schema_version = 'legacy-fixture-1'")
    return store, digest(store.database_path)


def promote(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE store_metadata SET storage_schema_version = ?",
            (STORAGE_SCHEMA_VERSION,),
        )


def engine(tmp_path: Path, store: SQLiteConversationStore) -> SQLiteMigrationEngine:
    return SQLiteMigrationEngine(
        active_database=store.database_path,
        checkpoint_directory=tmp_path / "checkpoints",
        marker_directory=tmp_path / "markers",
        steps=(
            SQLiteMigrationStep(
                step_id="fixture-promote",
                source_version="legacy-fixture-1",
                target_version=STORAGE_SCHEMA_VERSION,
                transform=promote,
            ),
        ),
    )


def test_explicit_migration_preserves_checkpoint_and_supports_exact_rollback(
    tmp_path: Path,
) -> None:
    store, source_digest = legacy_store(tmp_path)
    migration = engine(tmp_path, store)
    plan = migration.plan_migration(STORAGE_SCHEMA_VERSION)
    receipt = migration.migrate(
        plan,
        migration_id="migration-1",
        checkpoint_id="checkpoint-1",
    )
    assert receipt.source_digest == source_digest
    assert receipt.target_digest == digest(store.database_path)
    checkpoints = tuple((tmp_path / "checkpoints").glob("*.sqlite3"))
    assert len(checkpoints) == 1
    checkpoint = checkpoints[0]
    assert digest(checkpoint) == source_digest
    assert checkpoint.stat().st_mode & 0o777 == 0o600
    markers = tuple((tmp_path / "markers").glob("*.json"))
    assert len(markers) == 1 and markers[0].is_file()

    migration.rollback(receipt)
    assert digest(store.database_path) == source_digest


def test_transient_migration_paths_remain_openable_under_long_authorized_root(
    tmp_path: Path,
) -> None:
    root = tmp_path
    for index in range(8):
        candidate = SQLiteConversationStore(
            runtime_data_root=root / "runtime-data",
            bound_scope_id=ConversationScopeId(value="scope-private"),
            known_legacy_versions=("legacy-fixture-1",),
        )
        if len(os.fsencode(candidate.database_path)) >= 430:
            break
        root /= f"nested-{index}-" + ("x" * 32)
    else:  # pragma: no cover - defensive guard for unexpectedly tiny filesystem roots
        pytest.fail("could not construct a representative long authorized root")

    root.mkdir(mode=0o700, parents=True)
    store, _ = legacy_store(root)
    assert 430 <= len(os.fsencode(store.database_path)) < 480
    migration = engine(root, store)

    receipt = migration.migrate(
        migration.plan_migration(STORAGE_SCHEMA_VERSION),
        migration_id="long-path-migration",
        checkpoint_id="long-path-checkpoint",
    )

    assert receipt.target_digest == digest(store.database_path)
    migration.rollback(receipt)


def test_transform_failure_leaves_source_unchanged_and_incomplete_marker(
    tmp_path: Path,
) -> None:
    store, source_digest = legacy_store(tmp_path)

    def fail(_: Path) -> None:
        raise RuntimeError("fixture failure")

    migration = SQLiteMigrationEngine(
        active_database=store.database_path,
        checkpoint_directory=tmp_path / "checkpoints",
        marker_directory=tmp_path / "markers",
        steps=(
            SQLiteMigrationStep(
                step_id="fixture-fail",
                source_version="legacy-fixture-1",
                target_version=STORAGE_SCHEMA_VERSION,
                transform=fail,
            ),
        ),
    )
    plan = migration.plan_migration(STORAGE_SCHEMA_VERSION)
    with pytest.raises(RuntimeError, match="fixture failure"):
        migration.migrate(
            plan,
            migration_id="migration-failed",
            checkpoint_id="checkpoint-failed",
        )
    assert digest(store.database_path) == source_digest
    markers = tuple((tmp_path / "markers").glob("*.json"))
    assert len(markers) == 1
    marker = markers[0]
    assert '"state":"in_progress"' in marker.read_text(encoding="utf-8")
    with pytest.raises(ConversationStorageError) as captured:
        migration.migrate(
            plan,
            migration_id="migration-second",
            checkpoint_id="checkpoint-second",
        )
    assert captured.value.code is ConversationStorageErrorCode.MIGRATION_INCOMPLETE


def test_rollback_rejects_post_migration_write(tmp_path: Path) -> None:
    store, _ = legacy_store(tmp_path)
    migration = engine(tmp_path, store)
    receipt = migration.migrate(
        migration.plan_migration(STORAGE_SCHEMA_VERSION),
        migration_id="migration-1",
        checkpoint_id="checkpoint-1",
    )
    with sqlite3.connect(store.database_path) as connection:
        connection.execute("CREATE TABLE post_migration_write(value TEXT)")
    with pytest.raises(ConversationStorageError) as captured:
        migration.rollback(receipt)
    assert captured.value.code is ConversationStorageErrorCode.CONFLICT


def test_production_registry_starts_without_invented_legacy_steps(tmp_path: Path) -> None:
    store, _ = legacy_store(tmp_path)
    migration = SQLiteMigrationEngine(
        active_database=store.database_path,
        checkpoint_directory=tmp_path / "checkpoints",
        marker_directory=tmp_path / "markers",
    )
    with pytest.raises(ConversationStorageError) as captured:
        migration.plan_migration(STORAGE_SCHEMA_VERSION)
    assert captured.value.code is ConversationStorageErrorCode.UNSUPPORTED_SCHEMA


def test_turn_citations_migration_step_adds_the_table_additively(tmp_path: Path) -> None:
    """Phase 2-E: a real `sqlite-1` store gains `turn_citations` and stays readable."""

    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=ConversationScopeId(value="scope-private"),
        known_legacy_versions=(LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1,),
    )
    store.initialize_new_store()
    store.commit(
        CommitConversation(
            scope_id=ConversationScopeId(value="scope-private"),
            operation_id=ConversationOperationId(value="pre-migration-write"),
            conversation=empty_snapshot(),
        )
    )
    with sqlite3.connect(store.database_path) as connection:
        connection.execute("DROP TABLE turn_citations")
        connection.execute("ALTER TABLE conversations DROP COLUMN title")
        connection.execute(
            "UPDATE store_metadata SET storage_schema_version = ?",
            (LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1,),
        )
    assert store.inspect_schema().readiness is StorageReadiness.MIGRATION_REQUIRED

    maintenance = SQLiteConversationMaintenance(
        store=store,
        steps=(
            TURN_CITATIONS_MIGRATION_STEP,
            CONVERSATION_TITLE_MIGRATION_STEP,
            TURN_WEB_CITATIONS_MIGRATION_STEP,
        ),
    )
    plan = maintenance.plan_migration(STORAGE_SCHEMA_VERSION)
    receipt = maintenance.migrate(plan, checkpoint_id="turn-citations-checkpoint")
    assert receipt.record_count == 1

    status = store.inspect_schema()
    assert status.readiness is StorageReadiness.READY
    with sqlite3.connect(store.database_path) as connection:
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        columns = {row[1] for row in connection.execute("PRAGMA table_info(conversations)")}
    assert "turn_citations" in tables
    assert "turn_web_citations" in tables
    assert "title" in columns
    assert (
        store.get(
            ConversationScopeId(value="scope-private"),
            ConversationId(value="conversation-race"),
        )
        is not None
    )


def test_conversation_title_migration_step_adds_the_column_additively(tmp_path: Path) -> None:
    """Phase 2-E-H: a real `sqlite-2` store gains `title` and stays readable."""

    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=ConversationScopeId(value="scope-private"),
        known_legacy_versions=(LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2,),
    )
    store.initialize_new_store()
    store.commit(
        CommitConversation(
            scope_id=ConversationScopeId(value="scope-private"),
            operation_id=ConversationOperationId(value="pre-migration-write"),
            conversation=empty_snapshot(),
        )
    )
    with sqlite3.connect(store.database_path) as connection:
        connection.execute("ALTER TABLE conversations DROP COLUMN title")
        connection.execute(
            "UPDATE store_metadata SET storage_schema_version = ?",
            (LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2,),
        )
    assert store.inspect_schema().readiness is StorageReadiness.MIGRATION_REQUIRED

    maintenance = SQLiteConversationMaintenance(
        store=store,
        steps=(CONVERSATION_TITLE_MIGRATION_STEP, TURN_WEB_CITATIONS_MIGRATION_STEP),
    )
    plan = maintenance.plan_migration(STORAGE_SCHEMA_VERSION)
    receipt = maintenance.migrate(plan, checkpoint_id="title-column-checkpoint")
    assert receipt.record_count == 1

    status = store.inspect_schema()
    assert status.readiness is StorageReadiness.READY
    with sqlite3.connect(store.database_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(conversations)")}
        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
    assert "title" in columns
    assert "turn_web_citations" in tables
    stored = store.get(
        ConversationScopeId(value="scope-private"),
        ConversationId(value="conversation-race"),
    )
    assert stored is not None
    assert stored.conversation.title is None


def current_migration_engine(
    tmp_path: Path,
    store: SQLiteConversationStore,
    *,
    transform: Callable[[Path], None],
) -> SQLiteMigrationEngine:
    return SQLiteMigrationEngine(
        active_database=store.database_path,
        checkpoint_directory=tmp_path / "checkpoints",
        marker_directory=tmp_path / "markers",
        steps=(
            SQLiteMigrationStep(
                step_id="current-to-fixture-2",
                source_version=STORAGE_SCHEMA_VERSION,
                target_version="fixture-2",
                transform=transform,
            ),
        ),
        validator=lambda _: 0,
    )


def empty_snapshot() -> ConversationSnapshot:
    now = datetime.now(UTC)
    return ConversationSnapshot(
        scope_id=ConversationScopeId(value="scope-private"),
        conversation_id=ConversationId(value="conversation-race"),
        state=ConversationState.ACTIVE,
        created_at=now,
        updated_at=now,
    )


def test_writer_started_after_migration_gate_is_rejected_before_cutover(tmp_path: Path) -> None:
    store = SQLiteConversationStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=ConversationScopeId(value="scope-private"),
    )
    store.initialize_new_store()
    transform_started = threading.Event()
    release_transform = threading.Event()

    def paused_transform(path: Path) -> None:
        transform_started.set()
        assert release_transform.wait(5)
        with sqlite3.connect(path) as connection:
            connection.execute("UPDATE store_metadata SET storage_schema_version = 'fixture-2'")

    migration = current_migration_engine(tmp_path, store, transform=paused_transform)
    plan = migration.plan_migration("fixture-2")
    migration_error: list[BaseException] = []

    def run_migration() -> None:
        try:
            migration.migrate(plan, "checkpoint-race", migration_id="migration-race")
        except BaseException as exc:
            migration_error.append(exc)

    thread = threading.Thread(target=run_migration)
    thread.start()
    assert transform_started.wait(5)
    with pytest.raises(ConversationStorageError) as captured:
        store.commit(
            CommitConversation(
                scope_id=ConversationScopeId(value="scope-private"),
                operation_id=ConversationOperationId(value="writer-after-gate"),
                conversation=empty_snapshot(),
            )
        )
    assert captured.value.code is ConversationStorageErrorCode.MIGRATION_INCOMPLETE
    release_transform.set()
    thread.join(5)
    assert not thread.is_alive() and migration_error == []


class PausingWriterStore(SQLiteConversationStore):
    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.pause_writes = False
        self.writer_ready = threading.Event()
        self.release_writer = threading.Event()

    def _connect(self, *, read_only: bool) -> sqlite3.Connection:
        if not read_only and self.pause_writes:
            self.writer_ready.set()
            assert self.release_writer.wait(5)
        return super()._connect(read_only=read_only)


def test_writer_waiting_after_readiness_check_rechecks_database_gate(tmp_path: Path) -> None:
    store = PausingWriterStore(
        runtime_data_root=tmp_path / "runtime-data",
        bound_scope_id=ConversationScopeId(value="scope-private"),
    )
    store.initialize_new_store()
    store.pause_writes = True
    writer_error: list[BaseException] = []

    def run_writer() -> None:
        try:
            store.commit(
                CommitConversation(
                    scope_id=ConversationScopeId(value="scope-private"),
                    operation_id=ConversationOperationId(value="waiting-writer"),
                    conversation=empty_snapshot(),
                )
            )
        except BaseException as exc:
            writer_error.append(exc)

    writer = threading.Thread(target=run_writer)
    writer.start()
    assert store.writer_ready.wait(5)

    transform_started = threading.Event()
    release_transform = threading.Event()

    def paused_transform(path: Path) -> None:
        transform_started.set()
        assert release_transform.wait(5)
        with sqlite3.connect(path) as connection:
            connection.execute("UPDATE store_metadata SET storage_schema_version = 'fixture-2'")

    migration = current_migration_engine(tmp_path, store, transform=paused_transform)
    plan = migration.plan_migration("fixture-2")
    migration_error: list[BaseException] = []
    migrator = threading.Thread(
        target=lambda: _capture_migration(
            migration,
            plan,
            migration_error,
        )
    )
    migrator.start()
    assert transform_started.wait(5)
    store.release_writer.set()
    writer.join(5)
    assert len(writer_error) == 1
    assert isinstance(writer_error[0], ConversationStorageError)
    assert writer_error[0].code is ConversationStorageErrorCode.MIGRATION_INCOMPLETE
    release_transform.set()
    migrator.join(5)
    assert not migrator.is_alive() and migration_error == []


def _capture_migration(
    migration: SQLiteMigrationEngine,
    plan: MigrationPlan,
    errors: list[BaseException],
) -> None:
    try:
        migration.migrate(plan, "checkpoint-waiting", migration_id="migration-waiting")
    except BaseException as exc:
        errors.append(exc)


@pytest.mark.parametrize(
    ("migration_id", "checkpoint_id"),
    [
        ("../migration", "../../checkpoint"),
        ("/absolute-like", "/tmp/checkpoint"),
    ],
)
def test_external_identities_are_digest_mapped_inside_recovery_roots(
    tmp_path: Path,
    migration_id: str,
    checkpoint_id: str,
) -> None:
    store, _ = legacy_store(tmp_path)
    migration = engine(tmp_path, store)
    migration.migrate(
        migration.plan_migration(STORAGE_SCHEMA_VERSION),
        migration_id=migration_id,
        checkpoint_id=checkpoint_id,
    )
    assert len(tuple((tmp_path / "checkpoints").glob("*.sqlite3"))) == 1
    assert len(tuple((tmp_path / "markers").glob("*.json"))) == 1
    assert not (tmp_path.parent / "checkpoint.sqlite3").exists()
    assert all(".." not in path.name and "/" not in path.name for path in tmp_path.rglob("*"))


def test_symlink_unsafe_mode_and_outside_root_are_rejected_without_write(tmp_path: Path) -> None:
    store, _ = legacy_store(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir(mode=0o700)
    symlink = tmp_path / "checkpoint-link"
    symlink.symlink_to(outside, target_is_directory=True)
    linked_engine = SQLiteMigrationEngine(
        active_database=store.database_path,
        checkpoint_directory=symlink,
        marker_directory=tmp_path / "markers",
        authorized_root=tmp_path,
    )
    with pytest.raises(ConversationStorageError) as linked:
        linked_engine.plan_migration(STORAGE_SCHEMA_VERSION)
    assert linked.value.code is ConversationStorageErrorCode.PERMISSION_DENIED

    unsafe = tmp_path / "unsafe"
    unsafe.mkdir(mode=0o777)
    unsafe.chmod(0o777)
    unsafe_engine = SQLiteMigrationEngine(
        active_database=store.database_path,
        checkpoint_directory=unsafe,
        marker_directory=tmp_path / "markers",
        authorized_root=tmp_path,
    )
    with pytest.raises(ConversationStorageError) as mode:
        unsafe_engine.plan_migration(STORAGE_SCHEMA_VERSION)
    assert mode.value.code is ConversationStorageErrorCode.PERMISSION_DENIED
    assert unsafe.stat().st_mode & 0o777 == 0o777

    external = tmp_path.parent / "external-recovery"
    escaped_engine = SQLiteMigrationEngine(
        active_database=store.database_path,
        checkpoint_directory=external,
        marker_directory=tmp_path / "markers",
        authorized_root=tmp_path,
    )
    with pytest.raises(ConversationStorageError) as escaped:
        escaped_engine.plan_migration(STORAGE_SCHEMA_VERSION)
    assert escaped.value.code is ConversationStorageErrorCode.PERMISSION_DENIED
    assert not external.exists()


def test_existing_unsafe_checkpoint_artifact_is_not_repaired(tmp_path: Path) -> None:
    store, _ = legacy_store(tmp_path)
    migration = engine(tmp_path, store)
    checkpoint_root = tmp_path / "checkpoints"
    checkpoint_root.mkdir(mode=0o700)
    unsafe = checkpoint_root / f"{_artifact_key('checkpoint', 'checkpoint-unsafe')}.sqlite3"
    unsafe.write_bytes(b"unsafe")
    unsafe.chmod(0o644)
    with pytest.raises(ConversationStorageError) as captured:
        migration.migrate(
            migration.plan_migration(STORAGE_SCHEMA_VERSION),
            "checkpoint-unsafe",
            migration_id="migration-unsafe",
        )
    assert captured.value.code is ConversationStorageErrorCode.PERMISSION_DENIED
    assert unsafe.stat().st_mode & 0o777 == 0o644
