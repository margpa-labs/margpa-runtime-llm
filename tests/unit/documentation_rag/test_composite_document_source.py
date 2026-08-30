"""Phase 7 (P7-0/P7-B): `CompositeDocumentSource` merge/routing tests."""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.adapters.documentation_rag.composite_document_source import (
    CompositeDocumentSource,
)
from margpa_runtime_llm.adapters.documentation_rag.local_corpus_document_source import (
    LocalCorpusDocumentSource,
)
from margpa_runtime_llm.adapters.documentation_rag.local_corpus_registry import (
    JsonFileLocalCorpusRegistry,
)
from margpa_runtime_llm.adapters.documentation_rag.local_filesystem_source import (
    LocalMarkdownDocumentSource,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DOCUMENTATION_RAG_CITATION_SOURCE_CLASS,
    DocumentationChunkingConfig,
    DocumentationContextConfig,
    DocumentationCorpusConfig,
    DocumentationLimitsConfig,
    DocumentationRetrievalConfig,
    LocalDocumentationRagFeatureConfig,
)
from margpa_runtime_llm.modules.documentation_rag.local_corpus_contracts import (
    LOCAL_CORPUS_SOURCE_CLASS,
    LocalCorpusDocumentInput,
)


def _feature() -> LocalDocumentationRagFeatureConfig:
    return LocalDocumentationRagFeatureConfig(
        profile_key="local.documentation-rag.lexical",
        mode="enabled",
        provider_key="local_lexical",
        provider_display_name="Local Lexical RAG",
        active_phase="phase_7",
        corpus=DocumentationCorpusConfig(),
        limits=DocumentationLimitsConfig(),
        chunking=DocumentationChunkingConfig(),
        retrieval=DocumentationRetrievalConfig(),
        context=DocumentationContextConfig(),
    )


def _composite(tmp_path: Path) -> tuple[CompositeDocumentSource, JsonFileLocalCorpusRegistry]:
    feature = _feature()
    project = tmp_path / "project"
    docs_dir = project / "docs/project/current"
    docs_dir.mkdir(parents=True)
    (docs_dir / "project_ja.md").write_text("# Project概要\n\n本文です。\n", encoding="utf-8")
    project_source = LocalMarkdownDocumentSource(project_root=project, feature=feature)
    registry = JsonFileLocalCorpusRegistry(runtime_data_root=tmp_path / "runtime_data")
    local_corpus_source = LocalCorpusDocumentSource(registry=registry, project_root=project)
    composite = CompositeDocumentSource(
        sources_by_class={
            DOCUMENTATION_RAG_CITATION_SOURCE_CLASS: project_source,
            LOCAL_CORPUS_SOURCE_CLASS: local_corpus_source,
        }
    )
    return composite, registry


def test_manifest_combines_entries_from_both_sources(tmp_path: Path) -> None:
    composite, registry = _composite(tmp_path)
    registry.register(LocalCorpusDocumentInput(title="研究メモ", content="Local Corpusの本文。"))

    manifest = composite.load_manifest()

    classes = {entry.corpus_source_class for entry in manifest.entries}
    assert classes == {DOCUMENTATION_RAG_CITATION_SOURCE_CLASS, LOCAL_CORPUS_SOURCE_CLASS}
    assert len(manifest.entries) == 2


def test_manifest_digest_changes_when_local_corpus_changes_project_docs_unchanged(
    tmp_path: Path,
) -> None:
    composite, registry = _composite(tmp_path)
    before = composite.load_manifest().corpus_manifest_digest

    registry.register(LocalCorpusDocumentInput(title="t", content="c"))
    after = composite.load_manifest().corpus_manifest_digest

    assert before != after


def test_load_documents_routes_each_entry_back_to_its_owning_source(tmp_path: Path) -> None:
    composite, registry = _composite(tmp_path)
    registry.register(LocalCorpusDocumentInput(title="研究メモ", content="Local Corpusの本文。"))
    manifest = composite.load_manifest()

    documents, warnings = composite.load_documents(manifest)

    assert warnings == ()
    contents_by_class = {
        document.manifest.corpus_source_class: document.content for document in documents
    }
    assert contents_by_class[LOCAL_CORPUS_SOURCE_CLASS] == "Local Corpusの本文。"
    assert "Project概要" in contents_by_class[DOCUMENTATION_RAG_CITATION_SOURCE_CLASS]


def test_empty_local_corpus_still_composes_with_only_project_docs(tmp_path: Path) -> None:
    composite, _ = _composite(tmp_path)

    manifest = composite.load_manifest()
    documents, warnings = composite.load_documents(manifest)

    assert manifest.docs_present is True
    assert len(manifest.entries) == 1
    assert warnings == ()
    assert len(documents) == 1
