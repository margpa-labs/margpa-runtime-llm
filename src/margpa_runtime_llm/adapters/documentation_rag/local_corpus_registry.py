"""Phase 7 (P7-B): private, single-JSON-file Local Corpus document registry.

Mirrors `sqlite_conversation_store.py`'s local-file safety discipline
(symlink rejection along the path chain, owner-only directory/file modes,
atomic replace) at a scale proportionate to a small, user-curated document
set (P7-A Sizing: MVP_ Text-only, no heavy Vector/Index dependency) rather
than reusing SQLite for what is, at this size, a single small JSON blob.
"""

from __future__ import annotations

import json
import os
import stat
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from margpa_runtime_llm.modules.documentation_rag.local_corpus_contracts import (
    MAX_ACTIVE_DOCUMENTS,
    MAX_CORPUS_TOTAL_CHARACTERS,
    LocalCorpusDocumentInput,
    LocalCorpusDocumentNotFound,
    LocalCorpusDocumentRecord,
    LocalCorpusDocumentRevision,
    LocalCorpusDocumentState,
    LocalCorpusLimitExceeded,
    content_digest,
)

_SCHEMA_VERSION = 1


class LocalCorpusRegistryUnsafePath(Exception):
    pass


class LocalCorpusRegistryCorrupt(Exception):
    """Fail-closed: a corrupt/tampered store file is never silently reset
    or partially trusted (never quietly loses a user's registered
    documents)."""


class JsonFileLocalCorpusRegistry:
    def __init__(self, *, runtime_data_root: Path, scope_key: str = "default") -> None:
        if not runtime_data_root.is_absolute():
            raise ValueError("runtime_data_root must be absolute")
        if not scope_key or "/" in scope_key or "\\" in scope_key or scope_key in {".", ".."}:
            raise ValueError("scope_key must be a safe single path segment")
        self._root = runtime_data_root
        self._dir = runtime_data_root / "persistent" / scope_key / "local_corpus"
        self._path = self._dir / "documents.json"
        self._lock = threading.Lock()

    @property
    def document_store_path(self) -> Path:
        """P7-RW5-C: same absolute Path this instance already reads/writes
        (`self._path`) - exposed read-only so a caller (`LocalCorpusDocument
        Source`) can derive a safe User-facing display value from the
        Active `runtime_data_root`/`scope_key` this Registry was actually
        constructed with, instead of a Hard-coded literal."""
        return self._path

    def list_active(self) -> tuple[LocalCorpusDocumentRecord, ...]:
        with self._lock:
            records = self._read()
            return tuple(
                record
                for record in records.values()
                if record.state is LocalCorpusDocumentState.ACTIVE
            )

    def list_all(self) -> tuple[LocalCorpusDocumentRecord, ...]:
        with self._lock:
            return tuple(self._read().values())

    def get(self, document_id: str) -> LocalCorpusDocumentRecord | None:
        with self._lock:
            return self._read().get(document_id)

    def register(self, document_input: LocalCorpusDocumentInput) -> LocalCorpusDocumentRecord:
        with self._lock:
            records = self._read()
            active_count = sum(
                1 for record in records.values() if record.state is LocalCorpusDocumentState.ACTIVE
            )
            if active_count + 1 > MAX_ACTIVE_DOCUMENTS:
                raise LocalCorpusLimitExceeded("local_corpus_document_limit_exceeded")
            active_total_characters = sum(
                len(record.content)
                for record in records.values()
                if record.state is LocalCorpusDocumentState.ACTIVE
            )
            if active_total_characters + len(document_input.content) > MAX_CORPUS_TOTAL_CHARACTERS:
                raise LocalCorpusLimitExceeded("local_corpus_total_size_limit_exceeded")
            now = datetime.now(UTC)
            document_id = uuid.uuid4().hex
            digest = content_digest(document_input.content)
            record = LocalCorpusDocumentRecord(
                document_id=document_id,
                state=LocalCorpusDocumentState.ACTIVE,
                title=document_input.title,
                content=document_input.content,
                content_sha512=digest,
                current_revision=1,
                revisions=(
                    LocalCorpusDocumentRevision(
                        revision=1,
                        title=document_input.title,
                        content_sha512=digest,
                        character_count=len(document_input.content),
                        recorded_at=now,
                    ),
                ),
                created_at=now,
                updated_at=now,
            )
            records[document_id] = record
            self._write(records)
            return record

    def update(
        self,
        document_id: str,
        document_input: LocalCorpusDocumentInput,
    ) -> LocalCorpusDocumentRecord:
        with self._lock:
            records = self._read()
            existing = records.get(document_id)
            if existing is None or existing.state is not LocalCorpusDocumentState.ACTIVE:
                raise LocalCorpusDocumentNotFound(document_id)
            active_total_characters = sum(
                len(record.content)
                for record in records.values()
                if record.state is LocalCorpusDocumentState.ACTIVE
                and record.document_id != document_id
            )
            if active_total_characters + len(document_input.content) > MAX_CORPUS_TOTAL_CHARACTERS:
                raise LocalCorpusLimitExceeded("local_corpus_total_size_limit_exceeded")
            now = datetime.now(UTC)
            digest = content_digest(document_input.content)
            next_revision = existing.current_revision + 1
            updated = LocalCorpusDocumentRecord(
                document_id=document_id,
                state=LocalCorpusDocumentState.ACTIVE,
                title=document_input.title,
                content=document_input.content,
                content_sha512=digest,
                current_revision=next_revision,
                revisions=(
                    *existing.revisions,
                    LocalCorpusDocumentRevision(
                        revision=next_revision,
                        title=document_input.title,
                        content_sha512=digest,
                        character_count=len(document_input.content),
                        recorded_at=now,
                    ),
                ),
                created_at=existing.created_at,
                updated_at=now,
            )
            records[document_id] = updated
            self._write(records)
            return updated

    def delete(self, document_id: str) -> LocalCorpusDocumentRecord:
        with self._lock:
            records = self._read()
            existing = records.get(document_id)
            if existing is None or existing.state is not LocalCorpusDocumentState.ACTIVE:
                raise LocalCorpusDocumentNotFound(document_id)
            deleted = existing.model_copy(
                update={"state": LocalCorpusDocumentState.DELETED, "updated_at": datetime.now(UTC)}
            )
            records[document_id] = deleted
            self._write(records)
            return deleted

    # -- private file I/O -------------------------------------------------

    def _read(self) -> dict[str, LocalCorpusDocumentRecord]:
        self._validate_path_chain()
        if not self._path.exists():
            return {}
        try:
            raw = self._path.read_text(encoding="utf-8")
            payload: Any = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LocalCorpusRegistryCorrupt(str(self._path)) from exc
        if not isinstance(payload, dict) or payload.get("schema_version") != _SCHEMA_VERSION:
            raise LocalCorpusRegistryCorrupt(str(self._path))
        documents = payload.get("documents")
        if not isinstance(documents, dict):
            raise LocalCorpusRegistryCorrupt(str(self._path))
        try:
            return {
                document_id: LocalCorpusDocumentRecord.model_validate(entry)
                for document_id, entry in documents.items()
            }
        except Exception as exc:  # pydantic ValidationError or shape mismatch
            raise LocalCorpusRegistryCorrupt(str(self._path)) from exc

    def _write(self, records: dict[str, LocalCorpusDocumentRecord]) -> None:
        self._ensure_private_directory()
        payload = {
            "schema_version": _SCHEMA_VERSION,
            "documents": {
                document_id: json.loads(record.model_dump_json())
                for document_id, record in records.items()
            },
        }
        tmp_path = self._path.with_name(f"{self._path.name}.{os.getpid()}.tmp")
        try:
            descriptor = os.open(tmp_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            os.chmod(tmp_path, 0o600)
            os.replace(tmp_path, self._path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    def _ensure_private_directory(self) -> None:
        missing: list[Path] = []
        current = self._dir
        while not current.exists():
            missing.append(current)
            if current == self._root:
                break
            current = current.parent
        if current.exists() and current.is_symlink():
            raise LocalCorpusRegistryUnsafePath(str(current))
        for path in reversed(missing):
            path.mkdir(mode=0o700)
            os.chmod(path, 0o700)

    def _validate_path_chain(self) -> None:
        current = self._root
        if current.exists() and current.is_symlink():
            raise LocalCorpusRegistryUnsafePath(str(current))
        try:
            relative_parts = self._dir.relative_to(self._root).parts
        except ValueError as exc:
            raise LocalCorpusRegistryUnsafePath(str(self._dir)) from exc
        for part in relative_parts:
            current = current / part
            if current.is_symlink():
                raise LocalCorpusRegistryUnsafePath(str(current))
            if not current.exists():
                return
            info = current.stat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
                raise LocalCorpusRegistryUnsafePath(str(current))
        if self._path.exists() and self._path.is_symlink():
            raise LocalCorpusRegistryUnsafePath(str(self._path))


__all__ = [
    "JsonFileLocalCorpusRegistry",
    "LocalCorpusRegistryCorrupt",
    "LocalCorpusRegistryUnsafePath",
]
