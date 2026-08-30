"""Phase 7 (P7-0/P7-B): merge multiple `DocumentSourcePort`s into one.

Routes `load_documents()` back to the owning Source by
`DocumentManifestEntry.corpus_source_class` (never by path prefix, so this
stays correct regardless of what a Source's own path convention looks
like). Each `corpus_source_class` must be produced by exactly one composed
Source — enforced at construction, not silently at query time.
"""

from __future__ import annotations

import hashlib

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CorpusManifest,
    DocumentationWarning,
    DocumentManifestEntry,
    DocumentSource,
)
from margpa_runtime_llm.modules.documentation_rag.ports import CancellationCheck, DocumentSourcePort


class CompositeDocumentSource:
    def __init__(self, *, sources_by_class: dict[str, DocumentSourcePort]) -> None:
        if not sources_by_class:
            raise ValueError("composite document source requires at least one source")
        self._sources_by_class = dict(sources_by_class)

    @property
    def schema_version(self) -> str:
        return "+".join(
            f"{source_class}:{source.schema_version}"
            for source_class, source in sorted(self._sources_by_class.items())
        )

    def load_manifest(self) -> CorpusManifest:
        manifests = {
            source_class: source.load_manifest()
            for source_class, source in self._sources_by_class.items()
        }
        entries = tuple(
            entry
            for manifest in manifests.values()
            for entry in manifest.entries
            if entry.corpus_source_class in self._sources_by_class
        )
        entries = tuple(sorted(entries, key=lambda entry: entry.project_relative_path))
        warnings = tuple(
            warning for manifest in manifests.values() for warning in manifest.warnings
        )
        total_bytes = sum(manifest.total_bytes for manifest in manifests.values())
        docs_present = any(manifest.docs_present for manifest in manifests.values())
        return CorpusManifest(
            docs_present=docs_present,
            entries=entries,
            corpus_manifest_digest=_combined_digest(manifests),
            total_bytes=total_bytes,
            warnings=warnings,
        )

    def load_documents(
        self,
        manifest: CorpusManifest,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> tuple[tuple[DocumentSource, ...], tuple[DocumentationWarning, ...]]:
        entries_by_class: dict[str, list[DocumentManifestEntry]] = {
            key: [] for key in self._sources_by_class
        }
        for entry in manifest.entries:
            entries_by_class.setdefault(entry.corpus_source_class, []).append(entry)

        documents: list[DocumentSource] = []
        warnings: list[DocumentationWarning] = []
        for source_class, source in self._sources_by_class.items():
            own_entries = tuple(entries_by_class.get(source_class, ()))
            sub_manifest = manifest.model_copy(
                update={
                    "entries": own_entries,
                    "warnings": (),
                    "total_bytes": sum(entry.size_bytes for entry in own_entries),
                }
            )
            sub_documents, sub_warnings = source.load_documents(sub_manifest, cancelled=cancelled)
            documents.extend(sub_documents)
            warnings.extend(sub_warnings)
            if cancelled is not None and cancelled():
                break
        return tuple(documents), tuple(warnings)


def _combined_digest(manifests: dict[str, CorpusManifest]) -> str:
    canonical = "\n".join(
        f"{source_class}\0{manifest.corpus_manifest_digest}"
        for source_class, manifest in sorted(manifests.items())
    )
    return hashlib.sha512(canonical.encode("utf-8")).hexdigest()


__all__ = ["CompositeDocumentSource"]
