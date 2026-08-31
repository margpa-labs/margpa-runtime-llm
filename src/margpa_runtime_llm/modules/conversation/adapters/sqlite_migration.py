"""Explicit checkpoint-and-cutover migration engine for local SQLite stores."""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import stat
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from ..domain import ConversationStorageError, ConversationStorageErrorCode
from ..ports import (
    ConversationStorageSchemaStatus,
    MigrationPlan,
    MigrationReceipt,
)
from .sqlite_conversation_store import (
    STORAGE_FORMAT_VERSION,
    STORAGE_SCHEMA_VERSION,
    SQLiteConversationStore,
    _updated_at_us,
)

LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1 = "sqlite-1"
LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2 = "sqlite-2"
LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_3 = "sqlite-3"

MigrationTransform = Callable[[Path], None]
MigrationValidator = Callable[[Path], int]
_ARTIFACT_DOMAIN = b"margpa-conversation-migration-artifact-v1\0"
_TRANSIENT_ARTIFACT_KEY_HEX_LENGTH = 32


def _artifact_key(kind: str, identity: str) -> str:
    payload = _ARTIFACT_DOMAIN + kind.encode("ascii") + b"\0" + identity.encode("utf-8")
    return hashlib.sha512(payload).hexdigest()


def _transient_artifact_name(kind: str, identity: str, suffix: str) -> str:
    """Return a bounded same-directory name for atomic SQLite cutover artifacts.

    Checkpoints and markers retain the complete SHA-512 key. Transient files must live
    beside the active database for atomic ``os.replace``; using the complete key there
    can exceed SQLite's pathname limit when the authorized project root is already long.
    A domain-separated 128-bit prefix keeps the local collision bound negligible while
    leaving enough pathname budget for deeply scoped conversation stores.
    """

    key = _artifact_key(kind, identity)[:_TRANSIENT_ARTIFACT_KEY_HEX_LENGTH]
    return f".margpa-{kind}-{key}.{suffix}"


@dataclass(frozen=True, slots=True)
class SQLiteMigrationStep:
    step_id: str
    source_version: str
    target_version: str
    transform: MigrationTransform


class SQLiteMigrationEngine:
    """No production legacy steps are registered unless a caller supplies them."""

    def __init__(
        self,
        *,
        active_database: Path,
        checkpoint_directory: Path,
        marker_directory: Path,
        steps: tuple[SQLiteMigrationStep, ...] = (),
        validator: MigrationValidator | None = None,
        authorized_root: Path | None = None,
    ) -> None:
        self._active = active_database
        self._checkpoints = checkpoint_directory
        self._markers = marker_directory
        self._steps = steps
        self._validator = validator or self._validate_current_database
        common_root = Path(
            os.path.commonpath((active_database, checkpoint_directory, marker_directory))
        )
        self._authorized_root = authorized_root or common_root
        if not self._authorized_root.is_absolute():
            raise ValueError("migration authorized root must be absolute")

    def plan_migration(self, target_version: str) -> MigrationPlan:
        self._validate_boundaries()
        source = self._read_storage_version(self._active)
        selected: list[SQLiteMigrationStep] = []
        cursor = source
        visited: set[str] = set()
        while cursor != target_version:
            if cursor in visited:
                raise self._unsupported()
            visited.add(cursor)
            candidates = [step for step in self._steps if step.source_version == cursor]
            if len(candidates) != 1:
                raise self._unsupported()
            step = candidates[0]
            selected.append(step)
            cursor = step.target_version
        if not selected:
            raise self._unsupported()
        plan_text = "\0".join([source, target_version, *(step.step_id for step in selected)])
        return MigrationPlan(
            plan_id=hashlib.sha512(plan_text.encode("utf-8")).hexdigest()[:64],
            source_storage_version=source,
            target_storage_version=target_version,
            step_ids=tuple(step.step_id for step in selected),
            rollback_supported=True,
        )

    def migrate(
        self,
        plan: MigrationPlan,
        checkpoint_id: str,
        *,
        migration_id: str | None = None,
    ) -> MigrationReceipt:
        migration_id = migration_id or plan.plan_id
        self._validate_boundaries()
        if self._existing_incomplete_marker() is not None:
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.MIGRATION_INCOMPLETE,
                safe_message="A conversation store migration is incomplete.",
            )
        selected = self._resolve_plan(plan)
        if self._read_storage_version(self._active) != plan.source_storage_version:
            raise self._unsupported()
        self._make_private_directory(self._checkpoints)
        self._make_private_directory(self._markers)
        checkpoint = self._checkpoints / f"{_artifact_key('checkpoint', checkpoint_id)}.sqlite3"
        marker = self._markers / f"{_artifact_key('marker', migration_id)}.json"
        staging = self._active.with_name(
            _transient_artifact_name("staging", migration_id, "staging")
        )
        self._validate_artifact_path(checkpoint)
        self._validate_artifact_path(marker)
        self._validate_artifact_path(staging)
        if checkpoint.exists() or marker.exists() or staging.exists():
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.CONFLICT,
                safe_message="The migration identity is already in use.",
            )
        source_connection = sqlite3.connect(self._active, isolation_level=None, timeout=5.0)
        marker_created = False
        try:
            source_connection.execute("BEGIN EXCLUSIVE")
            source_digest = self._digest(self._active)
            self._exclusive_copy(self._active, checkpoint)
            self._write_marker(
                marker,
                {
                    "migration_id": migration_id,
                    "state": "in_progress",
                    "plan_id": plan.plan_id,
                    "checkpoint_id": checkpoint_id,
                    "source_digest": source_digest,
                },
            )
            marker_created = True
            source_connection.execute(
                "UPDATE store_metadata SET migration_state = ?, active_migration_id = ? "
                "WHERE singleton = 1 AND migration_state = 'ready' "
                "AND active_migration_id IS NULL",
                ("in_progress", migration_id),
            )
            if source_connection.total_changes != 1:
                raise ConversationStorageError(
                    code=ConversationStorageErrorCode.MIGRATION_INCOMPLETE,
                    safe_message="A conversation store migration is incomplete.",
                )
            source_connection.commit()
        except BaseException:
            try:
                source_connection.rollback()
            except sqlite3.Error:
                pass
            if checkpoint.exists() and not marker_created:
                checkpoint.unlink()
            if staging.exists():
                staging.unlink()
            raise
        finally:
            source_connection.close()
        try:
            self._exclusive_copy(self._active, staging)
            for step in selected:
                step.transform(staging)
            with sqlite3.connect(staging) as staging_connection:
                staging_connection.execute(
                    "UPDATE store_metadata SET migration_state = 'ready', "
                    "active_migration_id = NULL WHERE singleton = 1"
                )
            record_count = self._validator(staging)
            target_digest = self._digest(staging)
            self._fsync_file(staging)
            os.replace(staging, self._active)
            self._fsync_directory(self._active.parent)
            receipt = MigrationReceipt(
                migration_id=migration_id,
                plan_id=plan.plan_id,
                checkpoint_id=checkpoint_id,
                source_digest=source_digest,
                target_digest=target_digest,
                record_count=record_count,
            )
            self._write_marker(
                marker,
                {
                    "migration_id": migration_id,
                    "state": "completed",
                    "plan_id": plan.plan_id,
                    "checkpoint_id": checkpoint_id,
                    "source_digest": source_digest,
                    "target_digest": target_digest,
                    "record_count": record_count,
                },
            )
            return receipt
        except BaseException:
            if staging.exists():
                staging.unlink()
            self._restore_checkpoint_after_failure(checkpoint, migration_id)
            raise

    def rollback(self, receipt: MigrationReceipt) -> None:
        self._validate_boundaries()
        checkpoint = self._checkpoints / (
            f"{_artifact_key('checkpoint', receipt.checkpoint_id)}.sqlite3"
        )
        self._validate_artifact_path(checkpoint)
        if not checkpoint.is_file() or self._digest(self._active) != receipt.target_digest:
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.CONFLICT,
                safe_message="The migrated store cannot be rolled back automatically.",
            )
        restore = self._active.with_name(
            _transient_artifact_name("restore", receipt.migration_id, "rollback")
        )
        self._validate_artifact_path(restore)
        if restore.exists():
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.CONFLICT,
                safe_message="The migration restore path is already in use.",
            )
        self._exclusive_copy(checkpoint, restore)
        if self._digest(restore) != receipt.source_digest:
            restore.unlink()
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.CORRUPT_DATA,
                safe_message="The migration checkpoint failed integrity validation.",
            )
        self._fsync_file(restore)
        os.replace(restore, self._active)
        self._fsync_directory(self._active.parent)

    def _resolve_plan(self, plan: MigrationPlan) -> tuple[SQLiteMigrationStep, ...]:
        by_id = {step.step_id: step for step in self._steps}
        try:
            selected = tuple(by_id[step_id] for step_id in plan.step_ids)
        except KeyError:
            raise self._unsupported() from None
        cursor = plan.source_storage_version
        for step in selected:
            if step.source_version != cursor:
                raise self._unsupported()
            cursor = step.target_version
        if cursor != plan.target_storage_version:
            raise self._unsupported()
        return selected

    def _existing_incomplete_marker(self) -> Path | None:
        if not self._markers.exists():
            return None
        self._validate_directory(self._markers)
        for marker in self._markers.glob("*.json"):
            self._validate_artifact_path(marker)
            try:
                value = json.loads(marker.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return marker
            if value.get("state") != "completed":
                return marker
        return None

    @staticmethod
    def _read_storage_version(path: Path) -> str:
        try:
            uri = f"{path.as_uri()}?mode=ro"
            with sqlite3.connect(uri, uri=True) as connection:
                row = connection.execute(
                    "SELECT storage_schema_version FROM store_metadata WHERE singleton = 1"
                ).fetchone()
        except sqlite3.Error:
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.CORRUPT_DATA,
                safe_message="The conversation store is corrupt.",
            ) from None
        if row is None:
            raise SQLiteMigrationEngine._unsupported()
        return str(row[0])

    @staticmethod
    def _validate_current_database(path: Path) -> int:
        try:
            uri = f"{path.as_uri()}?mode=ro"
            with sqlite3.connect(uri, uri=True) as connection:
                integrity = connection.execute("PRAGMA integrity_check").fetchone()
                version = connection.execute(
                    "SELECT storage_schema_version FROM store_metadata WHERE singleton = 1"
                ).fetchone()
                rows = connection.execute(
                    "SELECT scope_id, conversation_id, storage_format_version, snapshot_json, "
                    "snapshot_sha512, state, head_turn_id, created_at_utc, updated_at_utc, "
                    "updated_at_us, title FROM conversations"
                ).fetchall()
        except sqlite3.Error:
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.CORRUPT_DATA,
                safe_message="The migrated conversation store is invalid.",
            ) from None
        if integrity != ("ok",) or version != (STORAGE_SCHEMA_VERSION,):
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.INVALID_RECORD,
                safe_message="The migrated conversation store is invalid.",
            )
        for row in rows:
            snapshot = SQLiteConversationStore._decode_snapshot(bytes(row[3]), str(row[4]))
            if (
                snapshot.scope_id.value != row[0]
                or snapshot.conversation_id.value != row[1]
                or row[2] != STORAGE_FORMAT_VERSION
                or snapshot.state.value != row[5]
                or (snapshot.head_turn_id.value if snapshot.head_turn_id else None) != row[6]
                or snapshot.created_at.isoformat() != row[7]
                or snapshot.updated_at.isoformat() != row[8]
                or _updated_at_us(snapshot.updated_at) != row[9]
                or snapshot.title != row[10]
            ):
                raise ConversationStorageError(
                    code=ConversationStorageErrorCode.INVALID_RECORD,
                    safe_message="The migrated conversation store is invalid.",
                )
        return len(rows)

    def _make_private_directory(self, path: Path) -> None:
        self._require_contained(path)
        missing: list[Path] = []
        cursor = path
        while not cursor.exists():
            missing.append(cursor)
            cursor = cursor.parent
        self._validate_directory(cursor)
        for directory in reversed(missing):
            directory.mkdir(mode=0o700)
            os.chmod(directory, 0o700)
        self._validate_directory(path)

    def _write_marker(self, path: Path, value: dict[str, object]) -> None:
        self._validate_artifact_path(path)
        if path.exists():
            self._validate_file(path)
        temporary = path.with_suffix(".tmp")
        self._validate_artifact_path(temporary)
        if temporary.exists() or temporary.is_symlink():
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.CONFLICT,
                safe_message="The migration marker path is already in use.",
            )
        payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
        descriptor = os.open(temporary, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            os.write(descriptor, payload)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        os.replace(temporary, path)
        self._fsync_directory(path.parent)

    def _validate_boundaries(self) -> None:
        self._validate_directory(self._authorized_root)
        self._require_contained(self._active)
        self._validate_file(self._active)
        for path in (self._checkpoints, self._markers):
            self._require_contained(path)
            self._validate_existing_chain(path)

    def _restore_checkpoint_after_failure(self, checkpoint: Path, migration_id: str) -> None:
        self._validate_artifact_path(checkpoint)
        restore = self._active.with_name(
            _transient_artifact_name("failure-restore", migration_id, "rollback")
        )
        self._validate_artifact_path(restore)
        if restore.exists():
            raise ConversationStorageError(
                code=ConversationStorageErrorCode.CONFLICT,
                safe_message="The migration recovery path is already in use.",
            )
        self._exclusive_copy(checkpoint, restore)
        self._fsync_file(restore)
        os.replace(restore, self._active)
        self._fsync_directory(self._active.parent)

    def _validate_artifact_path(self, path: Path) -> None:
        self._require_contained(path)
        self._validate_existing_chain(path.parent)
        if path.is_symlink():
            raise self._unsafe_path()
        if path.exists():
            self._validate_file(path)

    def _require_contained(self, path: Path) -> None:
        try:
            path.absolute().relative_to(self._authorized_root.absolute())
        except ValueError:
            raise self._unsafe_path() from None

    def _validate_existing_chain(self, path: Path) -> None:
        self._require_contained(path)
        cursor = self._authorized_root
        for part in path.absolute().relative_to(self._authorized_root.absolute()).parts:
            cursor /= part
            if cursor.is_symlink():
                raise self._unsafe_path()
            if not cursor.exists():
                break
            self._validate_directory(cursor)

    @staticmethod
    def _validate_directory(path: Path) -> None:
        if path.is_symlink() or not path.exists():
            raise SQLiteMigrationEngine._unsafe_path()
        info = path.stat()
        if (
            not stat.S_ISDIR(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_mode & 0o777 != 0o700
        ):
            raise SQLiteMigrationEngine._unsafe_path()

    @staticmethod
    def _validate_file(path: Path) -> None:
        if path.is_symlink() or not path.exists():
            raise SQLiteMigrationEngine._unsafe_path()
        info = path.stat()
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_mode & 0o777 != 0o600
        ):
            raise SQLiteMigrationEngine._unsafe_path()

    @staticmethod
    def _unsafe_path() -> ConversationStorageError:
        return ConversationStorageError(
            code=ConversationStorageErrorCode.PERMISSION_DENIED,
            safe_message="The migration storage path is unsafe.",
        )

    @staticmethod
    def _digest(path: Path) -> str:
        digest = hashlib.sha512()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _exclusive_copy(source: Path, target: Path) -> None:
        no_follow = getattr(os, "O_NOFOLLOW", 0)
        source_descriptor = os.open(source, os.O_RDONLY | no_follow)
        try:
            target_descriptor = os.open(
                target,
                os.O_CREAT | os.O_EXCL | os.O_WRONLY | no_follow,
                0o600,
            )
            try:
                while chunk := os.read(source_descriptor, 1024 * 1024):
                    view = memoryview(chunk)
                    while view:
                        written = os.write(target_descriptor, view)
                        view = view[written:]
                os.fsync(target_descriptor)
            finally:
                os.close(target_descriptor)
        finally:
            os.close(source_descriptor)

    @staticmethod
    def _fsync_file(path: Path) -> None:
        with path.open("rb") as handle:
            os.fsync(handle.fileno())

    @staticmethod
    def _fsync_directory(path: Path) -> None:
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    @staticmethod
    def _unsupported() -> ConversationStorageError:
        return ConversationStorageError(
            code=ConversationStorageErrorCode.UNSUPPORTED_SCHEMA,
            safe_message="No supported migration path is available.",
        )


def _add_turn_citations_table(path: Path) -> None:
    """Phase 2-E: add the (initially empty) persistent citation evidence table."""

    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS turn_citations (
                scope_id TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                turn_id TEXT NOT NULL,
                citation_schema_version INTEGER NOT NULL,
                citations_json BLOB NOT NULL,
                citations_sha512 TEXT NOT NULL,
                operation_id TEXT NOT NULL,
                committed_at_utc TEXT NOT NULL,
                PRIMARY KEY (scope_id, conversation_id, turn_id)
            )
            """
        )
        connection.execute(
            "UPDATE store_metadata SET storage_schema_version = ? WHERE singleton = 1",
            (LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2,),
        )


TURN_CITATIONS_MIGRATION_STEP = SQLiteMigrationStep(
    step_id="sqlite-1-to-sqlite-2-turn-citations",
    source_version=LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_1,
    target_version=LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2,
    transform=_add_turn_citations_table,
)


def _add_conversation_title_column(path: Path) -> None:
    """Phase 2-E-H: add the (initially NULL) conversation title column."""

    with sqlite3.connect(path) as connection:
        connection.execute("ALTER TABLE conversations ADD COLUMN title TEXT")
        connection.execute(
            "UPDATE store_metadata SET storage_schema_version = ? WHERE singleton = 1",
            (LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_3,),
        )


CONVERSATION_TITLE_MIGRATION_STEP = SQLiteMigrationStep(
    step_id="sqlite-2-to-sqlite-3-conversation-title",
    source_version=LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_2,
    # P8-A: pinned to the explicit legacy constant above rather than the
    # live `STORAGE_SCHEMA_VERSION` import - that import is bound once, at
    # this module's own import time, so a later schema bump (this Task's
    # own `sqlite-3` -> `sqlite-4`) would otherwise have silently changed
    # *this* step's `target_version` too, even though this step still only
    # ever adds the title column, never the new `turn_web_citations` table.
    target_version=LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_3,
    transform=_add_conversation_title_column,
)


def _add_turn_web_citations_table(path: Path) -> None:
    """P8-A: add the (initially empty) persistent Manual URL Fetch citation
    evidence table - mirrors `_add_turn_citations_table()` above exactly."""

    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS turn_web_citations (
                scope_id TEXT NOT NULL,
                conversation_id TEXT NOT NULL,
                turn_id TEXT NOT NULL,
                citation_schema_version INTEGER NOT NULL,
                citations_json BLOB NOT NULL,
                citations_sha512 TEXT NOT NULL,
                operation_id TEXT NOT NULL,
                committed_at_utc TEXT NOT NULL,
                PRIMARY KEY (scope_id, conversation_id, turn_id)
            )
            """
        )
        connection.execute(
            "UPDATE store_metadata SET storage_schema_version = ? WHERE singleton = 1",
            (STORAGE_SCHEMA_VERSION,),
        )


TURN_WEB_CITATIONS_MIGRATION_STEP = SQLiteMigrationStep(
    step_id="sqlite-3-to-sqlite-4-turn-web-citations",
    source_version=LEGACY_STORAGE_SCHEMA_VERSION_SQLITE_3,
    target_version=STORAGE_SCHEMA_VERSION,
    transform=_add_turn_web_citations_table,
)


class SQLiteConversationMaintenance:
    """Port-shaped maintenance boundary backed by an explicit migration engine."""

    def __init__(
        self,
        *,
        store: SQLiteConversationStore,
        steps: tuple[SQLiteMigrationStep, ...] = (),
        validator: MigrationValidator | None = None,
    ) -> None:
        self._store = store
        self._engine = SQLiteMigrationEngine(
            active_database=store.database_path,
            checkpoint_directory=store.migration_checkpoint_directory,
            marker_directory=store.migration_marker_directory,
            steps=steps,
            validator=validator,
            authorized_root=store.runtime_data_root,
        )

    def inspect_schema(self) -> ConversationStorageSchemaStatus:
        return self._store.inspect_schema()

    def plan_migration(self, target_version: str) -> MigrationPlan:
        return self._engine.plan_migration(target_version)

    def migrate(self, plan: MigrationPlan, checkpoint_id: str) -> MigrationReceipt:
        return self._engine.migrate(plan, checkpoint_id)

    def rollback(self, receipt: MigrationReceipt) -> None:
        self._engine.rollback(receipt)
