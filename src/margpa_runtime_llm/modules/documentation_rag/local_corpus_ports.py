"""Phase 7 (P7-B): replaceable storage boundary for Local Corpus documents."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from .local_corpus_contracts import (
    LocalCorpusDocumentInput,
    LocalCorpusDocumentRecord,
)


class LocalCorpusRegistryPort(Protocol):
    """CRUD boundary for user-registered Local Corpus documents.

    Every mutation is safe/atomic from the caller's point of view (a failed
    `register`/`update`/`delete` leaves the prior state fully intact — see
    `JsonFileLocalCorpusRegistry`'s temp-file-then-`os.replace` write path).
    """

    @property
    def document_store_path(self) -> Path:
        """P7-RW5-C (P7-CODEX-016): the real Filesystem location backing
        this Registry's single JSON store - derived from the Active
        Runtime `runtime_data_root`/`scope_key` this instance was built
        with, never a Hard-coded literal. Read-only, User-facing Citation
        Path display only; never used for I/O (the Registry's own
        internal read/write path is a private implementation detail)."""
        ...

    def list_active(self) -> tuple[LocalCorpusDocumentRecord, ...]: ...

    def list_all(self) -> tuple[LocalCorpusDocumentRecord, ...]:
        """Includes soft-deleted records (Historical Evidence, Architecture
        §3 Invariant 6) — never used to feed retrieval, only for Settings
        UI/Evidence listing."""
        ...

    def get(self, document_id: str) -> LocalCorpusDocumentRecord | None: ...

    def register(self, document_input: LocalCorpusDocumentInput) -> LocalCorpusDocumentRecord: ...

    def update(
        self,
        document_id: str,
        document_input: LocalCorpusDocumentInput,
    ) -> LocalCorpusDocumentRecord:
        """Raises `LocalCorpusDocumentNotFound` if absent or soft-deleted."""
        ...

    def delete(self, document_id: str) -> LocalCorpusDocumentRecord:
        """Soft-delete: raises `LocalCorpusDocumentNotFound` if absent or
        already deleted. The record and all its revisions are retained."""
        ...
