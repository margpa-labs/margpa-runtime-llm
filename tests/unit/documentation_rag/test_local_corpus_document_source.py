"""Phase 7 (P7-B/C): `LocalCorpusDocumentSource` manifest/document contract tests."""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.adapters.documentation_rag.local_corpus_document_source import (
    LocalCorpusDocumentSource,
)
from margpa_runtime_llm.adapters.documentation_rag.local_corpus_registry import (
    JsonFileLocalCorpusRegistry,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import CorpusPriority
from margpa_runtime_llm.modules.documentation_rag.local_corpus_contracts import (
    LOCAL_CORPUS_SOURCE_CLASS,
    LocalCorpusDocumentInput,
)


def _source(
    tmp_path: Path, *, scope_key: str = "default"
) -> tuple[LocalCorpusDocumentSource, JsonFileLocalCorpusRegistry]:
    registry = JsonFileLocalCorpusRegistry(
        runtime_data_root=tmp_path / "runtime_data", scope_key=scope_key
    )
    return LocalCorpusDocumentSource(registry=registry, project_root=tmp_path), registry


def test_empty_registry_yields_a_present_but_empty_manifest(tmp_path: Path) -> None:
    source, _ = _source(tmp_path)

    manifest = source.load_manifest()

    assert manifest.docs_present is True
    assert manifest.entries == ()
    assert manifest.total_bytes == 0


def test_active_document_appears_with_local_corpus_tagging(tmp_path: Path) -> None:
    source, registry = _source(tmp_path)
    registry.register(LocalCorpusDocumentInput(title="研究メモ", content="研究メモの本文です。"))

    manifest = source.load_manifest()

    assert len(manifest.entries) == 1
    entry = manifest.entries[0]
    assert entry.corpus_source_class == LOCAL_CORPUS_SOURCE_CLASS
    assert entry.corpus_priority is CorpusPriority.CURRENT
    assert entry.project_relative_path.startswith("local-corpus/")
    assert entry.project_relative_path.endswith(".md")


def test_manifest_entry_carries_the_registered_title_and_real_storage_path(
    tmp_path: Path,
) -> None:
    """P7-RW5-B (P7-CODEX-015)/P7-RW5-C (P7-CODEX-016): the registered
    Document's own `title` and the real backing JSON store's Path -
    Project-relative here since `runtime_data_root` (`tmp_path/
    "runtime_data"`) is nested inside `project_root` (`tmp_path`), matching
    the documented default User Profile - flow onto the Manifest Entry,
    never a Synthetic literal or a Hard-coded `mac-local-primary`/
    `runtime_data` string."""
    source, registry = _source(tmp_path)
    registry.register(LocalCorpusDocumentInput(title="研究メモ", content="研究メモの本文です。"))

    entry = source.load_manifest().entries[0]

    assert entry.document_title == "研究メモ"
    assert (
        entry.storage_display_path == "runtime_data/persistent/default/local_corpus/documents.json"
    )


def test_storage_display_path_follows_the_active_scope_key(tmp_path: Path) -> None:
    """P7-RW5-C (ACC-006/ACC-009): a different Active Scope dynamically
    changes the displayed Path - never a fixed string."""
    source, registry = _source(tmp_path, scope_key="another-scope")
    registry.register(LocalCorpusDocumentInput(title="t", content="c"))

    entry = source.load_manifest().entries[0]

    assert (
        entry.storage_display_path
        == "runtime_data/persistent/another-scope/local_corpus/documents.json"
    )


def test_deleted_document_is_excluded_from_the_manifest(tmp_path: Path) -> None:
    source, registry = _source(tmp_path)
    record = registry.register(LocalCorpusDocumentInput(title="t", content="c"))
    registry.delete(record.document_id)

    manifest = source.load_manifest()

    assert manifest.entries == ()


def test_load_documents_returns_content_matching_the_manifest_digest(tmp_path: Path) -> None:
    source, registry = _source(tmp_path)
    registry.register(LocalCorpusDocumentInput(title="t", content="本文テキスト"))
    manifest = source.load_manifest()

    documents, warnings = source.load_documents(manifest)

    assert warnings == ()
    assert len(documents) == 1
    assert documents[0].content == "本文テキスト"
    assert documents[0].manifest == manifest.entries[0]


def test_load_documents_drops_entries_that_changed_since_the_manifest_was_built(
    tmp_path: Path,
) -> None:
    source, registry = _source(tmp_path)
    record = registry.register(LocalCorpusDocumentInput(title="t", content="original"))
    manifest = source.load_manifest()
    registry.update(record.document_id, LocalCorpusDocumentInput(title="t", content="changed"))

    documents, warnings = source.load_documents(manifest)

    assert documents == ()
    assert [warning.code for warning in warnings] == ["local_corpus_document_changed"]


def test_load_documents_respects_cancellation(tmp_path: Path) -> None:
    source, registry = _source(tmp_path)
    registry.register(LocalCorpusDocumentInput(title="t", content="c"))
    manifest = source.load_manifest()

    documents, _ = source.load_documents(manifest, cancelled=lambda: True)

    assert documents == ()


def test_storage_display_path_never_leaks_a_host_absolute_path_outside_project_root(
    tmp_path: Path,
) -> None:
    """P7-RW5-C §4.3: `runtime_data_root` configured outside the Project
    Root must never leak the Host absolute Path or User name through the
    Citation Path display - only the Scope-relative suffix from
    `persistent/` onward, which still varies with the Active Scope."""
    project_root = tmp_path / "project"
    project_root.mkdir()
    # A sibling of `project_root` (both directly under `tmp_path`, which
    # pytest's `tmp_path` fixture already created) - `JsonFileLocalCorpus
    # Registry` itself only creates directories from `runtime_data_root`
    # downward, so `runtime_data_root`'s own parent must already exist.
    outside_runtime_data = tmp_path / "elsewhere_runtime_data"
    registry = JsonFileLocalCorpusRegistry(
        runtime_data_root=outside_runtime_data, scope_key="outside-scope"
    )
    source = LocalCorpusDocumentSource(registry=registry, project_root=project_root)
    registry.register(LocalCorpusDocumentInput(title="t", content="c"))

    entry = source.load_manifest().entries[0]

    assert entry.storage_display_path == "persistent/outside-scope/local_corpus/documents.json"
    assert str(tmp_path) not in entry.storage_display_path
    assert "elsewhere" not in entry.storage_display_path
