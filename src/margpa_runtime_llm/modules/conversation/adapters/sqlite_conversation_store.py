"""Fail-closed SQLite implementation of the conversation repository port."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import sqlite3
import stat
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CITATION_EVIDENCE_SCHEMA_VERSION,
    CitationUnavailable,
    PersistedTurnCitationEvidence,
)

from ..domain import (
    ConversationId,
    ConversationOperationId,
    ConversationScopeId,
    ConversationSnapshot,
    ConversationState,
    ConversationStorageError,
    ConversationStorageErrorCode,
    ConversationSummary,
    ConversationTurnId,
    StorageMutationOutcome,
)
from ..ports import (
    CommitConversation,
    ConversationCommitReceipt,
    ConversationListQuery,
    ConversationPage,
    ConversationStorageSchemaStatus,
    StorageReadiness,
    StoredConversation,
)

APPLICATION_ID = "margpa-runtime-llm"
STORAGE_BACKEND_KIND = "sqlite"
STORAGE_SCHEMA_VERSION = "sqlite-3"
STORAGE_FORMAT_VERSION = "sqlite-json-1"
DOMAIN_SCHEMA_VERSION = "1"
_CURSOR_VERSION = "1"
_SCOPE_DOMAIN = b"margpa-conversation-scope-v1\0"
_COMMAND_DOMAIN = b"margpa-conversation-command-v1\0"
_EXPECTED_TABLES = frozenset(
    {"store_metadata", "conversations", "commit_operations", "turn_citations"}
)
_CITATION_STORAGE_FORMAT_VERSION = "sqlite-citation-json-1"


def scope_directory_key(scope_id: ConversationScopeId) -> str:
    return hashlib.sha512(_SCOPE_DOMAIN + scope_id.value.encode("utf-8")).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha512(value: bytes) -> str:
    return hashlib.sha512(value).hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError("duplicate JSON key")
        output[key] = value
    return output


def _updated_at_us(value: datetime) -> int:
    return int(value.timestamp() * 1_000_000)


class SQLiteConversationStore:
    """One-bound-scope repository with explicit, mutation-free construction."""

    def __init__(
        self,
        *,
        runtime_data_root: Path,
        bound_scope_id: ConversationScopeId,
        busy_timeout_ms: int = 5_000,
        known_legacy_versions: Iterable[str] = (),
    ) -> None:
        if not runtime_data_root.is_absolute():
            raise ValueError("runtime_data_root must be absolute")
        if isinstance(busy_timeout_ms, bool) or not 1 <= busy_timeout_ms <= 60_000:
            raise ValueError("busy_timeout_ms must be between 1 and 60000")
        self._root = runtime_data_root
        self._scope_id = bound_scope_id
        self._scope_key = scope_directory_key(bound_scope_id)
        self._busy_timeout_ms = busy_timeout_ms
        self._known_legacy_versions = frozenset(known_legacy_versions)
        self._db_path = (
            runtime_data_root
            / "persistent"
            / self._scope_key
            / "conversations"
            / "conversations.sqlite3"
        )
        self._marker_dir = (
            runtime_data_root / "recovery" / "migrations" / self._scope_key / "conversations"
        )

    @property
    def database_path(self) -> Path:
        return self._db_path

    @property
    def bound_scope_id(self) -> ConversationScopeId:
        return self._scope_id

    @property
    def runtime_data_root(self) -> Path:
        return self._root

    @property
    def migration_checkpoint_directory(self) -> Path:
        return self._root / "recovery" / "checkpoints" / self._scope_key / "conversations"

    @property
    def migration_marker_directory(self) -> Path:
        return self._marker_dir

    @property
    def backend_version(self) -> str:
        """The linked storage engine's own version (not the Project's storage_schema_version)."""

        return sqlite3.sqlite_version

    def inspect_schema(self) -> ConversationStorageSchemaStatus:
        self._validate_existing_path_chain()
        active_marker = self._active_marker_id()
        if active_marker is not None:
            return ConversationStorageSchemaStatus(
                readiness=StorageReadiness.MIGRATION_INCOMPLETE,
                active_migration_id=active_marker,
                write_enabled=False,
            )
        if not self._db_path.exists():
            return ConversationStorageSchemaStatus(
                readiness=StorageReadiness.EMPTY,
                write_enabled=False,
            )
        self._validate_owned_file(self._db_path)
        try:
            with self._connect(read_only=True) as connection:
                tables = {
                    str(row[0])
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }
                if "store_metadata" not in tables:
                    return self._status(StorageReadiness.CORRUPT)
                row = connection.execute(
                    "SELECT application_id, storage_schema_version, "
                    "domain_schema_version, migration_state, active_migration_id "
                    "FROM store_metadata WHERE singleton = 1"
                ).fetchone()
        except sqlite3.DatabaseError:
            return self._status(StorageReadiness.CORRUPT)
        if row is None or row[0] != APPLICATION_ID:
            return self._status(StorageReadiness.CORRUPT)
        storage_version, domain_version = str(row[1]), str(row[2])
        if row[3] != "ready" or row[4] is not None:
            return ConversationStorageSchemaStatus(
                readiness=StorageReadiness.MIGRATION_INCOMPLETE,
                storage_schema_version=storage_version,
                domain_schema_version=domain_version,
                active_migration_id=str(row[4] or "unknown-migration"),
                write_enabled=False,
            )
        if storage_version != STORAGE_SCHEMA_VERSION:
            # A store honestly at an older, known-legacy version is not expected to
            # already have the current version's full table set (that is exactly
            # what MIGRATION_REQUIRED -> migrate() adds); only a store that claims
            # to already be at the current version must have every expected table.
            readiness = (
                StorageReadiness.MIGRATION_REQUIRED
                if storage_version in self._known_legacy_versions
                else StorageReadiness.UNSUPPORTED
            )
            return ConversationStorageSchemaStatus(
                readiness=readiness,
                storage_schema_version=storage_version,
                domain_schema_version=domain_version,
                write_enabled=False,
            )
        if not _EXPECTED_TABLES.issubset(tables):
            return self._status(StorageReadiness.CORRUPT)
        if domain_version != DOMAIN_SCHEMA_VERSION:
            return ConversationStorageSchemaStatus(
                readiness=StorageReadiness.UNSUPPORTED,
                storage_schema_version=storage_version,
                domain_schema_version=domain_version,
                write_enabled=False,
            )
        return ConversationStorageSchemaStatus(
            readiness=StorageReadiness.READY,
            storage_schema_version=storage_version,
            domain_schema_version=domain_version,
            write_enabled=True,
        )

    def initialize_new_store(self) -> None:
        status = self.inspect_schema()
        if status.readiness is not StorageReadiness.EMPTY:
            raise self._error(
                ConversationStorageErrorCode.CONFLICT,
                "The conversation store cannot be initialized in its current state.",
            )
        self._create_private_directories(self._db_path.parent)
        connection: sqlite3.Connection | None = None
        try:
            descriptor = os.open(self._db_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.close(descriptor)
            connection = self._connect(read_only=False)
            os.chmod(self._db_path, 0o600)
            connection.executescript(
                """
                BEGIN IMMEDIATE;
                CREATE TABLE store_metadata (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    application_id TEXT NOT NULL,
                    storage_schema_version TEXT NOT NULL,
                    domain_schema_version TEXT NOT NULL,
                    migration_state TEXT NOT NULL,
                    active_migration_id TEXT
                );
                CREATE TABLE conversations (
                    scope_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    storage_revision INTEGER NOT NULL CHECK (storage_revision >= 1),
                    last_operation_id TEXT NOT NULL,
                    storage_format_version TEXT NOT NULL,
                    snapshot_json BLOB NOT NULL,
                    snapshot_sha512 TEXT NOT NULL,
                    state TEXT NOT NULL,
                    head_turn_id TEXT,
                    created_at_utc TEXT NOT NULL,
                    updated_at_utc TEXT NOT NULL,
                    updated_at_us INTEGER NOT NULL,
                    title TEXT,
                    PRIMARY KEY (scope_id, conversation_id)
                );
                CREATE TABLE commit_operations (
                    scope_id TEXT NOT NULL,
                    operation_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    command_sha512 TEXT NOT NULL,
                    expected_revision INTEGER,
                    previous_revision INTEGER,
                    committed_revision INTEGER NOT NULL,
                    receipt_json BLOB NOT NULL,
                    committed_at_utc TEXT NOT NULL,
                    PRIMARY KEY (scope_id, operation_id)
                );
                CREATE TABLE turn_citations (
                    scope_id TEXT NOT NULL,
                    conversation_id TEXT NOT NULL,
                    turn_id TEXT NOT NULL,
                    citation_schema_version INTEGER NOT NULL,
                    citations_json BLOB NOT NULL,
                    citations_sha512 TEXT NOT NULL,
                    operation_id TEXT NOT NULL,
                    committed_at_utc TEXT NOT NULL,
                    PRIMARY KEY (scope_id, conversation_id, turn_id)
                );
                CREATE INDEX conversations_list_idx
                  ON conversations(scope_id, updated_at_us DESC, conversation_id ASC);
                INSERT INTO store_metadata VALUES (
                    1, 'margpa-runtime-llm', 'sqlite-3', '1', 'ready', NULL
                );
                COMMIT;
                """
            )
        except (OSError, sqlite3.Error) as exc:
            if connection is not None:
                try:
                    connection.rollback()
                except sqlite3.Error:
                    pass
            raise self._map_error(exc) from None
        finally:
            if connection is not None:
                connection.close()
        self._validate_owned_file(self._db_path)

    def open_ready_store(self) -> SQLiteConversationStore:
        self._require_ready()
        return self

    def get(
        self,
        scope_id: ConversationScopeId,
        conversation_id: ConversationId,
    ) -> StoredConversation | None:
        if scope_id != self._scope_id:
            return None
        self._require_ready()
        try:
            with self._connect(read_only=True) as connection:
                row = connection.execute(
                    "SELECT storage_revision, last_operation_id, storage_format_version, "
                    "snapshot_json, snapshot_sha512, state, head_turn_id, created_at_utc, "
                    "updated_at_utc, updated_at_us, title FROM conversations "
                    "WHERE scope_id = ? AND conversation_id = ?",
                    (scope_id.value, conversation_id.value),
                ).fetchone()
        except sqlite3.Error as exc:
            raise self._map_error(exc) from None
        return None if row is None else self._stored_from_row(row, conversation_id)

    def get_commit_receipt(
        self,
        scope_id: ConversationScopeId,
        operation_id: ConversationOperationId,
    ) -> ConversationCommitReceipt | None:
        if scope_id != self._scope_id:
            return None
        self._require_ready()
        try:
            with self._connect(read_only=True) as connection:
                row = connection.execute(
                    "SELECT receipt_json FROM commit_operations "
                    "WHERE scope_id = ? AND operation_id = ?",
                    (scope_id.value, operation_id.value),
                ).fetchone()
        except sqlite3.Error as exc:
            raise self._map_error(exc) from None
        if row is None:
            return None
        return self._decode_receipt(bytes(row[0]))

    def commit(self, command: CommitConversation) -> ConversationCommitReceipt:
        if command.scope_id != self._scope_id:
            raise self._error(
                ConversationStorageErrorCode.PERMISSION_DENIED,
                "The conversation scope is not available.",
                command=command,
            )
        self._require_ready()
        command_digest = self._command_digest(command)
        connection: sqlite3.Connection | None = None
        transaction_started = False
        commit_attempted = False
        try:
            connection = self._connect(read_only=False)
            connection.execute("BEGIN IMMEDIATE")
            transaction_started = True
            metadata = connection.execute(
                "SELECT storage_schema_version, domain_schema_version, migration_state, "
                "active_migration_id FROM store_metadata WHERE singleton = 1"
            ).fetchone()
            if metadata is None:
                connection.rollback()
                transaction_started = False
                raise self._error(
                    ConversationStorageErrorCode.CORRUPT_DATA,
                    "The conversation store is corrupt.",
                    command=command,
                )
            if metadata[2] != "ready" or metadata[3] is not None:
                connection.rollback()
                transaction_started = False
                raise self._error(
                    ConversationStorageErrorCode.MIGRATION_INCOMPLETE,
                    "A conversation store migration is incomplete.",
                    command=command,
                )
            if metadata[0] != STORAGE_SCHEMA_VERSION or metadata[1] != DOMAIN_SCHEMA_VERSION:
                connection.rollback()
                transaction_started = False
                raise self._error(
                    ConversationStorageErrorCode.UNSUPPORTED_SCHEMA,
                    "The conversation store schema is unsupported.",
                    command=command,
                )
            operation = connection.execute(
                "SELECT command_sha512, receipt_json FROM commit_operations "
                "WHERE scope_id = ? AND operation_id = ?",
                (command.scope_id.value, command.operation_id.value),
            ).fetchone()
            if operation is not None:
                if operation[0] == command_digest:
                    receipt = self._decode_receipt(bytes(operation[1]))
                    connection.rollback()
                    return receipt
                connection.rollback()
                raise self._error(
                    ConversationStorageErrorCode.CONFLICT,
                    "The conversation operation identity was already used.",
                    command=command,
                )
            current = connection.execute(
                "SELECT storage_revision FROM conversations "
                "WHERE scope_id = ? AND conversation_id = ?",
                (command.scope_id.value, command.conversation.conversation_id.value),
            ).fetchone()
            actual_revision = int(current[0]) if current is not None else None
            if command.expected_revision != actual_revision:
                connection.rollback()
                raise self._error(
                    ConversationStorageErrorCode.CONFLICT,
                    "The conversation changed before it could be saved.",
                    command=command,
                    actual_revision=actual_revision,
                )
            previous_revision = actual_revision
            committed_revision = 1 if actual_revision is None else actual_revision + 1
            snapshot_bytes, snapshot_digest = self._encode_snapshot(command.conversation)
            values = self._conversation_values(
                command,
                committed_revision,
                snapshot_bytes,
                snapshot_digest,
            )
            if actual_revision is None:
                connection.execute(
                    "INSERT INTO conversations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    values,
                )
            else:
                cursor = connection.execute(
                    "UPDATE conversations SET storage_revision = ?, last_operation_id = ?, "
                    "storage_format_version = ?, snapshot_json = ?, snapshot_sha512 = ?, "
                    "state = ?, head_turn_id = ?, created_at_utc = ?, updated_at_utc = ?, "
                    "updated_at_us = ?, title = ? WHERE scope_id = ? AND conversation_id = ? "
                    "AND storage_revision = ?",
                    (
                        committed_revision,
                        *values[3:],
                        command.scope_id.value,
                        command.conversation.conversation_id.value,
                        actual_revision,
                    ),
                )
                if cursor.rowcount != 1:
                    connection.rollback()
                    raise self._error(
                        ConversationStorageErrorCode.CONFLICT,
                        "The conversation changed before it could be saved.",
                        command=command,
                    )
            if command.citation_evidence is not None:
                citation_bytes, citation_digest = self._encode_citation_evidence(
                    command.citation_evidence
                )
                connection.execute(
                    "INSERT INTO turn_citations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        command.scope_id.value,
                        command.conversation.conversation_id.value,
                        command.citation_evidence.turn_id,
                        command.citation_evidence.citation_schema_version,
                        citation_bytes,
                        citation_digest,
                        command.operation_id.value,
                        command.conversation.updated_at.isoformat(),
                    ),
                )
            receipt = ConversationCommitReceipt(
                scope_id=command.scope_id,
                conversation_id=command.conversation.conversation_id,
                operation_id=command.operation_id,
                previous_revision=previous_revision,
                committed_revision=committed_revision,
            )
            receipt_bytes = _canonical_bytes(receipt.model_dump(mode="json"))
            connection.execute(
                "INSERT INTO commit_operations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    command.scope_id.value,
                    command.operation_id.value,
                    command.conversation.conversation_id.value,
                    command_digest,
                    command.expected_revision,
                    previous_revision,
                    committed_revision,
                    receipt_bytes,
                    command.conversation.updated_at.isoformat(),
                ),
            )
            commit_attempted = True
            connection.commit()
            transaction_started = False
            return receipt
        except ConversationStorageError:
            raise
        except (OSError, sqlite3.Error) as exc:
            if connection is not None and transaction_started:
                try:
                    connection.rollback()
                    transaction_started = False
                except sqlite3.Error:
                    pass
            outcome = (
                StorageMutationOutcome.UNKNOWN
                if commit_attempted
                else StorageMutationOutcome.NOT_APPLIED
            )
            raise self._map_error(exc, command=command, outcome=outcome) from None
        finally:
            if connection is not None:
                connection.close()

    def list(self, query: ConversationListQuery) -> ConversationPage:
        if query.scope_id != self._scope_id:
            return ConversationPage(scope_id=query.scope_id, items=())
        self._require_ready()
        cursor_time: int | None = None
        cursor_id: str | None = None
        if query.cursor is not None:
            cursor_time, cursor_id = self._decode_cursor(query.cursor)
        where = ["scope_id = ?"]
        values: list[object] = [query.scope_id.value]
        if query.states:
            placeholders = ",".join("?" for _ in query.states)
            where.append(f"state IN ({placeholders})")
            values.extend(sorted(state.value for state in query.states))
        if cursor_time is not None and cursor_id is not None:
            where.append("(updated_at_us < ? OR (updated_at_us = ? AND conversation_id > ?))")
            values.extend((cursor_time, cursor_time, cursor_id))
        values.append(query.limit + 1)
        sql = (
            "SELECT conversation_id, state, head_turn_id, created_at_utc, updated_at_utc, "
            "updated_at_us, title, EXISTS(SELECT 1 FROM json_each(snapshot_json, "
            "'$.conversation.sessions') WHERE json_extract(value, '$.state') = 'active') "
            "AS has_active_session FROM conversations WHERE "
            + " AND ".join(where)
            + " ORDER BY updated_at_us DESC, conversation_id ASC LIMIT ?"
        )
        try:
            with self._connect(read_only=True) as connection:
                rows = connection.execute(sql, values).fetchall()
        except sqlite3.Error as exc:
            raise self._map_error(exc) from None
        has_more = len(rows) > query.limit
        rows = rows[: query.limit]
        items = tuple(self._summary_from_row(row) for row in rows)
        next_cursor = None
        if has_more and rows:
            last = rows[-1]
            next_cursor = self._encode_cursor(int(last[5]), str(last[0]))
        return ConversationPage(scope_id=query.scope_id, items=items, next_cursor=next_cursor)

    def _require_ready(self) -> None:
        status = self.inspect_schema()
        if status.readiness is StorageReadiness.READY:
            return
        codes = {
            StorageReadiness.MIGRATION_REQUIRED: ConversationStorageErrorCode.MIGRATION_REQUIRED,
            StorageReadiness.MIGRATION_INCOMPLETE: (
                ConversationStorageErrorCode.MIGRATION_INCOMPLETE
            ),
            StorageReadiness.UNSUPPORTED: ConversationStorageErrorCode.UNSUPPORTED_SCHEMA,
            StorageReadiness.CORRUPT: ConversationStorageErrorCode.CORRUPT_DATA,
        }
        raise self._error(
            codes.get(status.readiness, ConversationStorageErrorCode.STORAGE_UNAVAILABLE),
            "The conversation store is not ready.",
        )

    def _connect(self, *, read_only: bool) -> sqlite3.Connection:
        if read_only:
            uri = f"{self._db_path.as_uri()}?mode=ro"
            connection = sqlite3.connect(
                uri,
                uri=True,
                timeout=self._busy_timeout_ms / 1_000,
                isolation_level=None,
            )
        else:
            connection = sqlite3.connect(
                self._db_path,
                timeout=self._busy_timeout_ms / 1_000,
                isolation_level=None,
            )
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA trusted_schema = OFF")
        connection.execute(f"PRAGMA busy_timeout = {self._busy_timeout_ms}")
        if not read_only:
            connection.execute("PRAGMA journal_mode = DELETE")
            connection.execute("PRAGMA synchronous = FULL")
        return connection

    def _validate_existing_path_chain(self) -> None:
        current = Path(self._root.anchor)
        for part in self._root.parts[1:]:
            current /= part
            if current.is_symlink():
                raise self._error(
                    ConversationStorageErrorCode.PERMISSION_DENIED,
                    "The conversation data root is unsafe.",
                )
            if not current.exists():
                break
        if self._root.exists():
            self._validate_owned_directory(self._root)
        current = self._root
        for part in self._db_path.relative_to(self._root).parts[:-1]:
            current /= part
            if current.is_symlink():
                raise self._error(
                    ConversationStorageErrorCode.PERMISSION_DENIED,
                    "The conversation data path is unsafe.",
                )
            if not current.exists():
                break
            self._validate_owned_directory(current)
        if self._db_path.exists() and self._db_path.is_symlink():
            raise self._error(
                ConversationStorageErrorCode.PERMISSION_DENIED,
                "The conversation data path is unsafe.",
            )

    def _create_private_directories(self, target: Path) -> None:
        missing: list[Path] = []
        current = target
        while not current.exists():
            missing.append(current)
            if current == self._root:
                break
            current = current.parent
        if current.exists() and current.is_symlink():
            raise self._error(
                ConversationStorageErrorCode.PERMISSION_DENIED,
                "The conversation data root is unsafe.",
            )
        for path in reversed(missing):
            path.mkdir(mode=0o700)
            os.chmod(path, 0o700)
        self._validate_existing_path_chain()

    @staticmethod
    def _validate_owned_directory(path: Path) -> None:
        info = path.stat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022:
            raise SQLiteConversationStore._error(
                ConversationStorageErrorCode.PERMISSION_DENIED,
                "The conversation data directory is unsafe.",
            )

    @staticmethod
    def _validate_owned_file(path: Path) -> None:
        info = path.stat()
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_mode & 0o777 != 0o600
        ):
            raise SQLiteConversationStore._error(
                ConversationStorageErrorCode.PERMISSION_DENIED,
                "The conversation data file is unsafe.",
            )

    def _active_marker_id(self) -> str | None:
        if not self._marker_dir.exists():
            return None
        if self._marker_dir.is_symlink():
            raise self._error(
                ConversationStorageErrorCode.PERMISSION_DENIED,
                "The migration state path is unsafe.",
            )
        for path in sorted(self._marker_dir.glob("*.json")):
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                return "unknown-migration"
            if isinstance(value, dict) and value.get("state") != "completed":
                return str(value.get("migration_id") or "unknown-migration")
        return None

    @staticmethod
    def _status(readiness: StorageReadiness) -> ConversationStorageSchemaStatus:
        return ConversationStorageSchemaStatus(readiness=readiness, write_enabled=False)

    @staticmethod
    def _encode_snapshot(snapshot: ConversationSnapshot) -> tuple[bytes, str]:
        envelope = {
            "storage_format_version": STORAGE_FORMAT_VERSION,
            "domain_schema_version": DOMAIN_SCHEMA_VERSION,
            "conversation": snapshot.model_dump(mode="json"),
        }
        payload = _canonical_bytes(envelope)
        return payload, _sha512(payload)

    @staticmethod
    def _decode_snapshot(payload: bytes, digest: str) -> ConversationSnapshot:
        if _sha512(payload) != digest:
            raise SQLiteConversationStore._error(
                ConversationStorageErrorCode.CORRUPT_DATA,
                "The conversation record failed integrity validation.",
            )
        try:
            value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
        except (UnicodeDecodeError, ValueError, TypeError):
            raise SQLiteConversationStore._error(
                ConversationStorageErrorCode.CORRUPT_DATA,
                "The conversation record could not be decoded.",
            ) from None
        if not isinstance(value, dict) or set(value) != {
            "storage_format_version",
            "domain_schema_version",
            "conversation",
        }:
            raise SQLiteConversationStore._error(
                ConversationStorageErrorCode.INVALID_RECORD,
                "The conversation record is invalid.",
            )
        if (
            value["storage_format_version"] != STORAGE_FORMAT_VERSION
            or value["domain_schema_version"] != DOMAIN_SCHEMA_VERSION
        ):
            raise SQLiteConversationStore._error(
                ConversationStorageErrorCode.UNSUPPORTED_SCHEMA,
                "The conversation record schema is unsupported.",
            )
        try:
            return ConversationSnapshot.model_validate(value["conversation"])
        except ValidationError:
            raise SQLiteConversationStore._error(
                ConversationStorageErrorCode.INVALID_RECORD,
                "The conversation record is invalid.",
            ) from None

    def _stored_from_row(
        self,
        row: sqlite3.Row | tuple[Any, ...],
        conversation_id: ConversationId,
    ) -> StoredConversation:
        snapshot = self._decode_snapshot(bytes(row[3]), str(row[4]))
        if (
            snapshot.scope_id != self._scope_id
            or snapshot.conversation_id != conversation_id
            or snapshot.state.value != row[5]
            or (snapshot.head_turn_id.value if snapshot.head_turn_id else None) != row[6]
            or snapshot.created_at.isoformat() != row[7]
            or snapshot.updated_at.isoformat() != row[8]
            or _updated_at_us(snapshot.updated_at) != row[9]
            or row[2] != STORAGE_FORMAT_VERSION
            or snapshot.title != row[10]
        ):
            raise self._error(
                ConversationStorageErrorCode.INVALID_RECORD,
                "The conversation record metadata is invalid.",
            )
        try:
            return StoredConversation(
                conversation=snapshot,
                storage_format_version=str(row[2]),
                storage_revision=int(row[0]),
                last_operation_id=ConversationOperationId(value=str(row[1])),
            )
        except ValidationError:
            raise self._error(
                ConversationStorageErrorCode.INVALID_RECORD,
                "The conversation record metadata is invalid.",
            ) from None

    def _conversation_values(
        self,
        command: CommitConversation,
        revision: int,
        snapshot_bytes: bytes,
        snapshot_digest: str,
    ) -> tuple[object, ...]:
        snapshot = command.conversation
        return (
            command.scope_id.value,
            snapshot.conversation_id.value,
            revision,
            command.operation_id.value,
            STORAGE_FORMAT_VERSION,
            snapshot_bytes,
            snapshot_digest,
            snapshot.state.value,
            snapshot.head_turn_id.value if snapshot.head_turn_id else None,
            snapshot.created_at.isoformat(),
            snapshot.updated_at.isoformat(),
            _updated_at_us(snapshot.updated_at),
            snapshot.title,
        )

    def _command_digest(self, command: CommitConversation) -> str:
        value = {
            "scope_id": command.scope_id.value,
            "operation_id": command.operation_id.value,
            "expected_revision": command.expected_revision,
            "conversation": command.conversation.model_dump(mode="json"),
            "citation_evidence": (
                None
                if command.citation_evidence is None
                else command.citation_evidence.model_dump(mode="json")
            ),
        }
        return _sha512(_COMMAND_DOMAIN + _canonical_bytes(value))

    @staticmethod
    def _encode_citation_evidence(
        evidence: PersistedTurnCitationEvidence,
    ) -> tuple[bytes, str]:
        envelope = {
            "citation_storage_format_version": _CITATION_STORAGE_FORMAT_VERSION,
            "citation_evidence": evidence.model_dump(mode="json"),
        }
        payload = _canonical_bytes(envelope)
        return payload, _sha512(payload)

    @staticmethod
    def _decode_citation_evidence(
        turn_id: str,
        schema_version: object,
        payload: bytes,
        digest: str,
    ) -> PersistedTurnCitationEvidence | CitationUnavailable:
        # `schema_version` is the raw DB column value, passed through unconverted by the
        # caller (P2E-CODEX-005): SQLite's permissive type affinity can store non-numeric
        # TEXT even in an INTEGER-declared column, so any int()-conversion must happen in
        # here, guarded, rather than in the caller where a ValueError would escape this
        # fail-closed boundary and break the whole conversation fetch.
        if isinstance(schema_version, bool) or not isinstance(schema_version, int):
            return CitationUnavailable(turn_id=turn_id, reason="corrupt_record")
        if schema_version < 1 or schema_version > CITATION_EVIDENCE_SCHEMA_VERSION:
            return CitationUnavailable(turn_id=turn_id, reason="unsupported_schema_version")
        if _sha512(payload) != digest:
            return CitationUnavailable(turn_id=turn_id, reason="corrupt_record")
        try:
            value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
        except (UnicodeDecodeError, ValueError, TypeError):
            return CitationUnavailable(turn_id=turn_id, reason="corrupt_record")
        if not isinstance(value, dict) or set(value) != {
            "citation_storage_format_version",
            "citation_evidence",
        }:
            return CitationUnavailable(turn_id=turn_id, reason="corrupt_record")
        if value["citation_storage_format_version"] != _CITATION_STORAGE_FORMAT_VERSION:
            return CitationUnavailable(turn_id=turn_id, reason="unsupported_schema_version")
        citation_payload = value["citation_evidence"]
        if not isinstance(citation_payload, dict):
            return CitationUnavailable(turn_id=turn_id, reason="corrupt_record")
        embedded_version = citation_payload.get("citation_schema_version")
        # The database column is the trusted, independently-stored version marker.
        # A mismatching or unrecognized value embedded inside the JSON payload
        # itself must never be silently accepted as if it were the column value.
        if embedded_version != schema_version:
            return CitationUnavailable(turn_id=turn_id, reason="unsupported_schema_version")
        try:
            return PersistedTurnCitationEvidence.model_validate(citation_payload)
        except ValidationError:
            return CitationUnavailable(turn_id=turn_id, reason="corrupt_record")

    def get_turn_citations(
        self,
        conversation_id: str,
        turn_id: str,
    ) -> PersistedTurnCitationEvidence | CitationUnavailable:
        self._require_ready()
        try:
            with self._connect(read_only=True) as connection:
                row = connection.execute(
                    "SELECT turn_id, citation_schema_version, citations_json, citations_sha512 "
                    "FROM turn_citations WHERE scope_id = ? AND conversation_id = ? "
                    "AND turn_id = ?",
                    (self._scope_id.value, conversation_id, turn_id),
                ).fetchone()
        except sqlite3.Error as exc:
            raise self._map_error(exc) from None
        if row is None:
            return CitationUnavailable(turn_id=turn_id, reason="not_present")
        return self._decode_citation_evidence(str(row[0]), row[1], bytes(row[2]), str(row[3]))

    def get_conversation_citations(
        self,
        conversation_id: str,
    ) -> dict[str, PersistedTurnCitationEvidence | CitationUnavailable]:
        self._require_ready()
        try:
            with self._connect(read_only=True) as connection:
                rows = connection.execute(
                    "SELECT turn_id, citation_schema_version, citations_json, citations_sha512 "
                    "FROM turn_citations WHERE scope_id = ? AND conversation_id = ?",
                    (self._scope_id.value, conversation_id),
                ).fetchall()
        except sqlite3.Error as exc:
            raise self._map_error(exc) from None
        return {
            str(row[0]): self._decode_citation_evidence(
                str(row[0]), row[1], bytes(row[2]), str(row[3])
            )
            for row in rows
        }

    def _summary_from_row(self, row: tuple[Any, ...]) -> ConversationSummary:
        try:
            return ConversationSummary(
                scope_id=self._scope_id,
                conversation_id=ConversationId(value=str(row[0])),
                state=ConversationState(str(row[1])),
                title=(None if row[6] is None else str(row[6])),
                head_turn_id=(None if row[2] is None else ConversationTurnId(value=str(row[2]))),
                created_at=datetime.fromisoformat(str(row[3])),
                updated_at=datetime.fromisoformat(str(row[4])),
                has_active_session=bool(row[7]),
            )
        except (ValueError, ValidationError):
            raise self._error(
                ConversationStorageErrorCode.INVALID_RECORD,
                "The conversation list record is invalid.",
            ) from None

    def _encode_cursor(self, updated_at_us: int, conversation_id: str) -> str:
        value = {
            "version": _CURSOR_VERSION,
            "scope": self._scope_key,
            "updated_at_us": updated_at_us,
            "conversation_id": conversation_id,
        }
        return base64.urlsafe_b64encode(_canonical_bytes(value)).decode("ascii").rstrip("=")

    def _decode_cursor(self, cursor: str) -> tuple[int, str]:
        try:
            padding = "=" * (-len(cursor) % 4)
            payload = base64.b64decode(cursor + padding, altchars=b"-_", validate=True)
            value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
            if not isinstance(value, dict) or set(value) != {
                "version",
                "scope",
                "updated_at_us",
                "conversation_id",
            }:
                raise ValueError
            if value["version"] != _CURSOR_VERSION or value["scope"] != self._scope_key:
                raise ValueError
            updated = value["updated_at_us"]
            identity = value["conversation_id"]
            if isinstance(updated, bool) or not isinstance(updated, int) or updated < 0:
                raise ValueError
            ConversationId(value=identity)
            return updated, identity
        except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError, ValidationError):
            raise self._error(
                ConversationStorageErrorCode.INVALID_RECORD,
                "The conversation list cursor is invalid.",
            ) from None

    @staticmethod
    def _decode_receipt(payload: bytes) -> ConversationCommitReceipt:
        try:
            value = json.loads(payload.decode("utf-8"), object_pairs_hook=_reject_duplicate_keys)
            return ConversationCommitReceipt.model_validate(value)
        except (UnicodeDecodeError, ValueError, TypeError, ValidationError):
            raise SQLiteConversationStore._error(
                ConversationStorageErrorCode.CORRUPT_DATA,
                "The conversation operation receipt is invalid.",
            ) from None

    @staticmethod
    def _error(
        code: ConversationStorageErrorCode,
        message: str,
        *,
        command: CommitConversation | None = None,
        actual_revision: int | None = None,
        outcome: StorageMutationOutcome = StorageMutationOutcome.NOT_APPLIED,
    ) -> ConversationStorageError:
        return ConversationStorageError(
            code=code,
            safe_message=message,
            retryable=code
            in {
                ConversationStorageErrorCode.CONFLICT,
                ConversationStorageErrorCode.STORAGE_TIMEOUT,
            },
            mutation_outcome=outcome,
            conversation_id=(
                command.conversation.conversation_id.value if command is not None else None
            ),
            operation_id=command.operation_id.value if command is not None else None,
            expected_revision=command.expected_revision if command is not None else None,
            actual_revision=actual_revision,
        )

    @classmethod
    def _map_error(
        cls,
        error: BaseException,
        *,
        command: CommitConversation | None = None,
        outcome: StorageMutationOutcome = StorageMutationOutcome.NOT_APPLIED,
    ) -> ConversationStorageError:
        text = str(error).lower()
        if "locked" in text or "busy" in text:
            code = ConversationStorageErrorCode.STORAGE_TIMEOUT
            message = "The conversation store timed out."
        elif "readonly" in text or "read-only" in text:
            code = ConversationStorageErrorCode.READ_ONLY
            message = "The conversation store is read-only."
        elif "full" in text:
            code = ConversationStorageErrorCode.CAPACITY_EXCEEDED
            message = "The conversation store has insufficient capacity."
        elif isinstance(error, PermissionError) or "permission" in text:
            code = ConversationStorageErrorCode.PERMISSION_DENIED
            message = "The conversation store permission was denied."
        elif outcome is StorageMutationOutcome.UNKNOWN:
            code = ConversationStorageErrorCode.ATOMIC_COMMIT_FAILED
            message = "The conversation commit outcome is unknown."
        elif isinstance(error, sqlite3.DatabaseError):
            code = ConversationStorageErrorCode.CORRUPT_DATA
            message = "The conversation store is corrupt."
        else:
            code = ConversationStorageErrorCode.STORAGE_UNAVAILABLE
            message = "The conversation store is unavailable."
        return cls._error(code, message, command=command, outcome=outcome)
