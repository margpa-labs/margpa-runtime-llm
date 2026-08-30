"""Phase 7 (P7-B/C): `DocumentSourcePort` reading from the Local Corpus registry."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CorpusManifest,
    CorpusPriority,
    DocumentationWarning,
    DocumentManifestEntry,
    DocumentSource,
)
from margpa_runtime_llm.modules.documentation_rag.local_corpus_contracts import (
    LOCAL_CORPUS_SOURCE_CLASS,
    LocalCorpusDocumentRecord,
)
from margpa_runtime_llm.modules.documentation_rag.local_corpus_ports import (
    LocalCorpusRegistryPort,
)
from margpa_runtime_llm.modules.documentation_rag.ports import CancellationCheck

EMPTY_MANIFEST_DIGEST = hashlib.sha512(b"").hexdigest()


class LocalCorpusDocumentSource:
    """Feeds active (non-deleted) Local Corpus documents into the same
    `DocumentationRagApplicationService` pipeline Phase 2's fixed project
    documentation corpus already uses (see `CompositeDocumentSource`).

    Every document is scored with `CorpusPriority.CURRENT` (P7-0 Recovery
    §3.2: reusing an existing tier instead of adding a new `CorpusPriority`
    member, which would corrupt `bm25_retriever.py`'s `(3 - x) / 3` scoring
    formula for every other tier) and tagged
    `corpus_source_class=LOCAL_CORPUS_SOURCE_CLASS` so it is never confused
    with `documentation_rag_citation` chunks downstream (Guardrail judgment,
    Prompt Role mapping, Citation display).
    """

    schema_version = "local_corpus.1"

    def __init__(self, *, registry: LocalCorpusRegistryPort, project_root: Path) -> None:
        self._registry = registry
        # P7-RW5-C (P7-CODEX-016): resolved once from the Active Runtime
        # configuration this Registry was actually built with - never a
        # Hard-coded `mac-local-primary`/`runtime_data` literal. Constant
        # for every Document this Source produces (all Local Corpus
        # documents share the one JSON store `document_store_path` names).
        self._storage_display_path = _storage_display_path(
            project_root=project_root, store_path=registry.document_store_path
        )

    def load_manifest(self) -> CorpusManifest:
        records = self._registry.list_active()
        entries: list[DocumentManifestEntry] = []
        total_bytes = 0
        for record in records:
            payload = record.content.encode("utf-8")
            entries.append(_manifest_entry(record, payload, self._storage_display_path))
            total_bytes += len(payload)
        entries.sort(key=lambda entry: entry.project_relative_path)
        manifest_digest = _manifest_digest(tuple(entries))
        return CorpusManifest(
            docs_present=True,
            entries=tuple(entries),
            corpus_manifest_digest=manifest_digest,
            total_bytes=total_bytes,
        )

    def load_documents(
        self,
        manifest: CorpusManifest,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> tuple[tuple[DocumentSource, ...], tuple[DocumentationWarning, ...]]:
        # Re-read the registry rather than trust the (possibly now-stale)
        # `manifest` passed in — mirrors `_ProjectMarkdownDocumentSource.
        # load_documents()` re-reading disk and discarding entries whose
        # content changed since `load_manifest()` ran (TOCTOU-safe).
        current_by_id = {record.document_id: record for record in self._registry.list_active()}
        expected_by_path = {entry.project_relative_path: entry for entry in manifest.entries}
        documents: list[DocumentSource] = []
        warning_counts: Counter[str] = Counter()
        for record in current_by_id.values():
            if cancelled is not None and cancelled():
                break
            path = _relative_path(record)
            expected = expected_by_path.get(path)
            if expected is None:
                continue
            payload = record.content.encode("utf-8")
            if len(payload) != expected.size_bytes or (
                hashlib.sha512(payload).hexdigest() != expected.document_sha512
            ):
                warning_counts["local_corpus_document_changed"] += 1
                continue
            documents.append(DocumentSource(manifest=expected, content=record.content))
        return tuple(documents), tuple(_warnings(warning_counts))


def _relative_path(record: LocalCorpusDocumentRecord) -> str:
    return f"local-corpus/{record.path_slug}.md"


def _manifest_entry(
    record: LocalCorpusDocumentRecord, payload: bytes, storage_display_path: str
) -> DocumentManifestEntry:
    document_digest = hashlib.sha512(payload).hexdigest()
    relative_path = _relative_path(record)
    source_id = hashlib.sha512(f"{relative_path}\0{document_digest}".encode()).hexdigest()
    return DocumentManifestEntry(
        source_id=source_id,
        project_relative_path=relative_path,
        corpus_priority=CorpusPriority.CURRENT,
        corpus_source_class=LOCAL_CORPUS_SOURCE_CLASS,
        document_sha512=document_digest,
        size_bytes=len(payload),
        modified_time_ns=int(record.updated_at.timestamp() * 1_000_000_000),
        document_title=record.title,
        storage_display_path=storage_display_path,
    )


def _storage_display_path(*, project_root: Path, store_path: Path) -> str:
    """P7-RW5-C (P7-CODEX-016): a safe, User-facing display value for the
    real Filesystem location backing the Local Corpus store - never the
    Synthetic `local-corpus/<slug>.md` Citation identity, and never a raw
    Host absolute Path/User name.

    Inside the Project Root (the current default and documented User
    Profile: `runtime_data/persistent/<scope>/local_corpus/documents.json`)
    this is a plain Project-relative Path. If `runtime_data_root` is ever
    configured outside the Project Root, only the Scope-relative suffix
    from `persistent/` onward is shown - still dynamically derived from
    the Active Runtime configuration, but never the Host absolute Path
    that would otherwise leak the Project Root's own location or the
    User's directory structure.
    """

    try:
        return store_path.relative_to(project_root).as_posix()
    except ValueError:
        parts = store_path.parts
        if "persistent" in parts:
            start = len(parts) - 1 - parts[::-1].index("persistent")
            return Path(*parts[start:]).as_posix()
        return store_path.name


def _manifest_digest(entries: tuple[DocumentManifestEntry, ...]) -> str:
    if not entries:
        return EMPTY_MANIFEST_DIGEST
    canonical = "\n".join(
        f"{entry.project_relative_path}\0{entry.size_bytes}\0{entry.document_sha512}"
        for entry in entries
    )
    return hashlib.sha512(canonical.encode("utf-8")).hexdigest()


def _warnings(counts: Counter[str]) -> tuple[DocumentationWarning, ...]:
    messages = {
        "local_corpus_document_changed": "読取中に変更されたLocal Corpus Documentを除外しました。",
    }
    return tuple(
        DocumentationWarning(code=code, message=messages[code], count=count)
        for code, count in sorted(counts.items())
        if count
    )


__all__ = ["LocalCorpusDocumentSource"]
