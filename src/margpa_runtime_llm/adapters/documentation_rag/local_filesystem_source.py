"""Secure, deterministic Markdown corpus discovery below an injected project root."""

from __future__ import annotations

import hashlib
from collections import Counter
from pathlib import Path

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CorpusManifest,
    CorpusPriority,
    DocumentationLimitsConfig,
    DocumentationWarning,
    DocumentManifestEntry,
    DocumentSource,
    LightningPublicDocumentationRagFeatureConfig,
    LocalDocumentationRagFeatureConfig,
)
from margpa_runtime_llm.modules.documentation_rag.ports import CancellationCheck

EMPTY_MANIFEST_DIGEST = hashlib.sha512(b"").hexdigest()
_BACKUP_SUFFIXES = (".bak", ".backup", ".orig", ".rej", ".tmp", ".temp", "~")
_BACKUP_NAME_PARTS = (".archive.", ".backup.", ".temporary.")


class _ProjectMarkdownDocumentSource:
    def __init__(
        self,
        *,
        project_root: Path,
        limits: DocumentationLimitsConfig,
    ) -> None:
        if not project_root.is_absolute():
            raise ValueError("project root must be absolute")
        if project_root.is_symlink():
            raise ValueError("project root must not be a symbolic link")
        self._project_root = project_root
        self._limits = limits

    def load_manifest(self) -> CorpusManifest:
        docs_root = self._project_root / "docs"
        if not docs_root.is_dir() or docs_root.is_symlink():
            return CorpusManifest(
                docs_present=False,
                corpus_manifest_digest=EMPTY_MANIFEST_DIGEST,
                total_bytes=0,
            )

        candidates = self._candidate_paths()
        warning_counts: Counter[str] = Counter()
        if len(candidates) > self._limits.max_documents:
            warning_counts["documentation_document_limit_exceeded"] += (
                len(candidates) - self._limits.max_documents
            )
            candidates = candidates[: self._limits.max_documents]

        entries: list[DocumentManifestEntry] = []
        total_bytes = 0
        for candidate, priority in candidates:
            if not candidate.exists() and not candidate.is_symlink():
                missing_warning = self._missing_warning_code()
                if missing_warning is not None:
                    warning_counts[missing_warning] += 1
                continue
            safe_path = self._safe_candidate(candidate)
            if safe_path is None:
                warning_counts["documentation_path_rejected"] += 1
                continue
            try:
                stat = safe_path.stat()
            except OSError:
                warning_counts["documentation_file_unreadable"] += 1
                continue
            if stat.st_size > self._limits.max_file_bytes:
                warning_counts["documentation_file_limit_exceeded"] += 1
                continue
            if total_bytes + stat.st_size > self._limits.max_corpus_bytes:
                warning_counts["documentation_corpus_limit_exceeded"] += 1
                continue
            try:
                payload = safe_path.read_bytes()
            except OSError:
                warning_counts["documentation_file_unreadable"] += 1
                continue
            if len(payload) != stat.st_size:
                warning_counts["documentation_file_changed"] += 1
                continue
            try:
                payload.decode("utf-8")
            except UnicodeDecodeError:
                warning_counts["documentation_utf8_decode_failed"] += 1
                continue
            relative_path = safe_path.relative_to(self._project_root).as_posix()
            document_digest = hashlib.sha512(payload).hexdigest()
            source_id = _digest(f"{relative_path}\0{document_digest}")
            entries.append(
                DocumentManifestEntry(
                    source_id=source_id,
                    project_relative_path=relative_path,
                    corpus_priority=priority,
                    document_sha512=document_digest,
                    size_bytes=len(payload),
                    modified_time_ns=stat.st_mtime_ns,
                )
            )
            total_bytes += len(payload)

        entries.sort(key=lambda entry: entry.project_relative_path)
        manifest_digest = _manifest_digest(tuple(entries))
        return CorpusManifest(
            docs_present=True,
            entries=tuple(entries),
            corpus_manifest_digest=manifest_digest,
            total_bytes=total_bytes,
            warnings=_warnings(warning_counts),
        )

    def load_documents(
        self,
        manifest: CorpusManifest,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> tuple[tuple[DocumentSource, ...], tuple[DocumentationWarning, ...]]:
        documents: list[DocumentSource] = []
        warning_counts: Counter[str] = Counter()
        for entry in manifest.entries:
            if cancelled is not None and cancelled():
                break
            candidate = self._project_root / entry.project_relative_path
            safe_path = self._safe_candidate(candidate)
            if safe_path is None:
                warning_counts["documentation_path_rejected"] += 1
                continue
            try:
                payload = safe_path.read_bytes()
            except OSError:
                warning_counts["documentation_file_unreadable"] += 1
                continue
            if len(payload) != entry.size_bytes or hashlib.sha512(payload).hexdigest() != (
                entry.document_sha512
            ):
                warning_counts["documentation_file_changed"] += 1
                continue
            try:
                content = payload.decode("utf-8")
            except UnicodeDecodeError:
                warning_counts["documentation_utf8_decode_failed"] += 1
                continue
            documents.append(DocumentSource(manifest=entry, content=content))
        return tuple(documents), tuple(_warnings(warning_counts))

    def _candidate_paths(self) -> list[tuple[Path, CorpusPriority]]:
        raise NotImplementedError

    def _missing_warning_code(self) -> str | None:
        return None

    def _safe_candidate(self, candidate: Path) -> Path | None:
        lexical_relative = _lexical_relative(candidate, self._project_root)
        if lexical_relative is None:
            return None
        relative = Path(lexical_relative)
        if relative.suffix.lower() != ".md" or _excluded(relative):
            return None
        current = self._project_root
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                return None
        try:
            resolved_root = self._project_root.resolve(strict=True)
            resolved_candidate = candidate.resolve(strict=True)
            resolved_candidate.relative_to(resolved_root)
        except (OSError, ValueError):
            return None
        if not resolved_candidate.is_file():
            return None
        return candidate


class LocalMarkdownDocumentSource(_ProjectMarkdownDocumentSource):
    schema_version = "1"

    def __init__(
        self,
        *,
        project_root: Path,
        feature: LocalDocumentationRagFeatureConfig,
    ) -> None:
        super().__init__(project_root=project_root, limits=feature.limits)
        self._feature = feature

    def _candidate_paths(self) -> list[tuple[Path, CorpusPriority]]:
        docs_root = self._project_root / "docs"
        candidates: dict[str, tuple[Path, CorpusPriority]] = {}

        def add_tree(root: Path, priority: CorpusPriority, pattern: str) -> None:
            if not root.is_dir() or root.is_symlink():
                return
            for candidate in root.rglob(pattern):
                relative = _lexical_relative(candidate, self._project_root)
                if relative is None:
                    continue
                if _excluded(Path(relative)):
                    continue
                current = candidates.get(relative)
                if current is None or priority < current[1]:
                    candidates[relative] = (candidate, priority)

        corpus = self._feature.corpus
        if corpus.include_current:
            add_tree(docs_root / "project/current", CorpusPriority.CURRENT, "*.md")
        if corpus.include_public:
            add_tree(docs_root / "public", CorpusPriority.PUBLIC, "*.md")
        if corpus.include_active_phase_index:
            candidate = (
                docs_root / "project/phases" / self._feature.active_phase / "phase_index_ja.md"
            )
            if candidate.exists() or candidate.is_symlink():
                relative = _lexical_relative(candidate, self._project_root)
                if relative is not None:
                    candidates[relative] = (candidate, CorpusPriority.ACTIVE_PHASE_INDEX)
        if corpus.include_completed_phase_stable:
            for phase in self._feature.completed_phases:
                add_tree(
                    docs_root / "project/phases" / phase,
                    CorpusPriority.COMPLETED_PHASE,
                    "*_ja.md",
                )
        return [candidates[key] for key in sorted(candidates)]


class ExplicitMarkdownDocumentSource(_ProjectMarkdownDocumentSource):
    """Read only a validated, ordered set of project-relative public documents."""

    schema_version = "2"

    def __init__(
        self,
        *,
        project_root: Path,
        feature: LightningPublicDocumentationRagFeatureConfig,
    ) -> None:
        super().__init__(project_root=project_root, limits=feature.limits)
        self._feature = feature

    def _candidate_paths(self) -> list[tuple[Path, CorpusPriority]]:
        return [
            (self._project_root / relative_path, CorpusPriority.PUBLIC)
            for relative_path in self._feature.corpus.files
        ]

    def _missing_warning_code(self) -> str | None:
        return "documentation_expected_file_missing"


def _excluded(relative: Path) -> bool:
    lower_parts = tuple(part.casefold() for part in relative.parts)
    if any(part.startswith(".") for part in relative.parts):
        return True
    if "history" in lower_parts or "lossless" in lower_parts:
        return True
    name = relative.name.casefold()
    return (
        name == ".ds_store"
        or name.endswith(_BACKUP_SUFFIXES)
        or any(fragment in name for fragment in _BACKUP_NAME_PARTS)
    )


def _lexical_relative(candidate: Path, root: Path) -> str | None:
    try:
        return candidate.relative_to(root).as_posix()
    except ValueError:
        return None


def _manifest_digest(entries: tuple[DocumentManifestEntry, ...]) -> str:
    if not entries:
        return EMPTY_MANIFEST_DIGEST
    canonical = "\n".join(
        f"{entry.project_relative_path}\0{entry.size_bytes}\0{entry.document_sha512}"
        for entry in entries
    )
    return _digest(canonical)


def _warnings(counts: Counter[str]) -> tuple[DocumentationWarning, ...]:
    messages = {
        "documentation_document_limit_exceeded": "Project Docsの文書数上限を超えました。",
        "documentation_file_limit_exceeded": "Project DocsのFile Size上限を超えました。",
        "documentation_corpus_limit_exceeded": "Project DocsのCorpus Size上限を超えました。",
        "documentation_path_rejected": "安全境界外のDocument Pathを拒否しました。",
        "documentation_file_unreadable": "一部のProject Docsを読み取れませんでした。",
        "documentation_file_changed": "読取中に変更されたProject Docsを除外しました。",
        "documentation_utf8_decode_failed": "UTF-8ではないProject Docsを除外しました。",
        "documentation_expected_file_missing": "予定した公開Documentが一部配置されていません。",
    }
    return tuple(
        DocumentationWarning(code=code, message=messages[code], count=count)
        for code, count in sorted(counts.items())
        if count
    )


def _digest(value: str) -> str:
    return hashlib.sha512(value.encode("utf-8")).hexdigest()
