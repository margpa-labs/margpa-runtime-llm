"""Security and determinism tests for the local Markdown source adapter."""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.adapters.documentation_rag.local_filesystem_source import (
    LocalMarkdownDocumentSource,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    LocalDocumentationRagFeatureConfig,
)


def feature(**limit_overrides: int) -> LocalDocumentationRagFeatureConfig:
    limits = {
        "max_documents": 512,
        "max_file_bytes": 4 * 1024 * 1024,
        "max_corpus_bytes": 32 * 1024 * 1024,
        "max_chunks": 20_000,
        **limit_overrides,
    }
    return LocalDocumentationRagFeatureConfig.model_validate(
        {
            "profile_key": "local.documentation-rag.lexical",
            "mode": "enabled",
            "provider_key": "local_lexical",
            "provider_display_name": "Local lexical documentation",
            "active_phase": "phase_1_ex",
            "completed_phases": ["phase_1"],
            "corpus": {},
            "limits": limits,
            "chunking": {},
            "retrieval": {},
            "context": {},
        }
    )


def write_document(project: Path, relative: str, content: str) -> Path:
    target = project / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def test_manifest_is_sorted_deterministic_and_changes_with_content(tmp_path: Path) -> None:
    project = tmp_path / "project"
    first = write_document(project, "docs/project/current/zeta_ja.md", "# Zeta\nvalue")
    write_document(project, "docs/public/alpha_ja.md", "# Alpha\nvalue")
    write_document(
        project,
        "docs/project/phases/phase_1_ex/phase_index_ja.md",
        "# Active\nvalue",
    )
    source = LocalMarkdownDocumentSource(project_root=project, feature=feature())

    before = source.load_manifest()
    repeated = source.load_manifest()
    assert before == repeated
    assert [entry.project_relative_path for entry in before.entries] == sorted(
        entry.project_relative_path for entry in before.entries
    )
    assert all(not entry.project_relative_path.startswith("/") for entry in before.entries)

    first.write_text("# Zeta\nchanged", encoding="utf-8")
    after = source.load_manifest()
    assert after.corpus_manifest_digest != before.corpus_manifest_digest


def test_exclusions_symlink_and_root_escape_are_rejected_without_path_exposure(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    write_document(project, "docs/project/current/keep_ja.md", "# Keep")
    write_document(project, "docs/project/current/history/old_ja.md", "# Old")
    write_document(project, "docs/project/current/lossless/raw_ja.md", "# Raw")
    write_document(project, "docs/project/current/.hidden_ja.md", "# Hidden")
    write_document(project, "docs/project/current/draft_ja.md.bak", "# Backup")
    write_document(project, "docs/project/current/draft.archive.md", "# Archive")
    write_document(project, "docs/project/current/draft.backup.md", "# Backup")
    write_document(project, "docs/project/current/draft.temporary.md", "# Temporary")
    write_document(project, "docs/project/shared/not_allowed_ja.md", "# Not allowed")
    outside = write_document(tmp_path, "outside_ja.md", "# Outside")
    link = project / "docs/project/current/escape_ja.md"
    link.symlink_to(outside)

    manifest = LocalMarkdownDocumentSource(
        project_root=project,
        feature=feature(),
    ).load_manifest()

    paths = {entry.project_relative_path for entry in manifest.entries}
    assert paths == {"docs/project/current/keep_ja.md"}
    assert {warning.code for warning in manifest.warnings} == {"documentation_path_rejected"}
    serialized_warnings = " ".join(warning.message for warning in manifest.warnings)
    assert str(project) not in serialized_warnings
    assert str(outside) not in serialized_warnings


def test_utf8_and_size_limits_are_safe_warnings(tmp_path: Path) -> None:
    project = tmp_path / "project"
    write_document(project, "docs/project/current/valid_ja.md", "# Valid")
    invalid = project / "docs/project/current/invalid_ja.md"
    invalid.write_bytes(b"\xff\xfe")
    write_document(project, "docs/public/large_ja.md", "x" * 32)

    manifest = LocalMarkdownDocumentSource(
        project_root=project,
        feature=feature(max_file_bytes=16),
    ).load_manifest()

    codes = {warning.code for warning in manifest.warnings}
    assert "documentation_utf8_decode_failed" in codes
    assert "documentation_file_limit_exceeded" in codes
    assert [entry.project_relative_path for entry in manifest.entries] == [
        "docs/project/current/valid_ja.md"
    ]


def test_docs_missing_and_document_count_limit_are_explicit(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    source = LocalMarkdownDocumentSource(project_root=project, feature=feature())
    assert source.load_manifest().docs_present is False

    write_document(project, "docs/project/current/a_ja.md", "# A")
    write_document(project, "docs/project/current/b_ja.md", "# B")
    limited = LocalMarkdownDocumentSource(
        project_root=project,
        feature=feature(max_documents=1),
    ).load_manifest()
    assert len(limited.entries) == 1
    assert {warning.code for warning in limited.warnings} == {
        "documentation_document_limit_exceeded"
    }


def test_corpus_byte_limit_is_explicit_and_deterministic(tmp_path: Path) -> None:
    project = tmp_path / "project"
    write_document(project, "docs/project/current/a_ja.md", "# A\n1234")
    write_document(project, "docs/project/current/b_ja.md", "# B\n5678")

    limited = LocalMarkdownDocumentSource(
        project_root=project,
        feature=feature(max_corpus_bytes=10),
    ).load_manifest()

    assert [entry.project_relative_path for entry in limited.entries] == [
        "docs/project/current/a_ja.md"
    ]
    assert {warning.code for warning in limited.warnings} == {"documentation_corpus_limit_exceeded"}


def test_document_load_detects_manifest_drift(tmp_path: Path) -> None:
    project = tmp_path / "project"
    target = write_document(project, "docs/project/current/a_ja.md", "# A")
    source = LocalMarkdownDocumentSource(project_root=project, feature=feature())
    manifest = source.load_manifest()
    target.write_text("# Changed", encoding="utf-8")

    documents, warnings = source.load_documents(manifest)

    assert documents == ()
    assert {warning.code for warning in warnings} == {"documentation_file_changed"}
