"""Explicit public-corpus selection and boundary tests."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.adapters.documentation_rag import ExplicitMarkdownDocumentSource
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    LIGHTNING_PUBLIC_DOCUMENTATION_FILES,
    LightningPublicDocumentationRagFeatureConfig,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LIGHTNING_PROFILE = PROJECT_ROOT / "config/feature_profiles/lightning_public_documentation_rag.toml"


def feature() -> LightningPublicDocumentationRagFeatureConfig:
    with LIGHTNING_PROFILE.open("rb") as profile_file:
        return LightningPublicDocumentationRagFeatureConfig.model_validate(
            tomllib.load(profile_file)
        )


def write_document(project: Path, relative: str, content: str) -> Path:
    target = project / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return target


def test_explicit_source_reads_only_the_eight_allowlisted_public_paths(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    for ordinal, relative in enumerate(LIGHTNING_PUBLIC_DOCUMENTATION_FILES):
        write_document(project, relative, f"# Public {ordinal}\n\nAllowed content {ordinal}")
    write_document(project, "docs/public/not_allowlisted.md", "# Extra")
    write_document(project, "docs/project/current/internal_ja.md", "# Internal")
    write_document(project, "docs/project/shared/internal_ja.md", "# Shared")
    write_document(project, "docs/project/phases/phase_1_ex/history/secret.md", "# History")

    manifest = ExplicitMarkdownDocumentSource(
        project_root=project,
        feature=feature(),
    ).load_manifest()

    assert {entry.project_relative_path for entry in manifest.entries} == set(
        LIGHTNING_PUBLIC_DOCUMENTATION_FILES
    )
    assert manifest.warnings == ()


def test_partial_corpus_reports_present_and_missing_counts(tmp_path: Path) -> None:
    project = tmp_path / "project"
    for relative in LIGHTNING_PUBLIC_DOCUMENTATION_FILES[:2]:
        write_document(project, relative, f"# {relative}")

    manifest = ExplicitMarkdownDocumentSource(
        project_root=project,
        feature=feature(),
    ).load_manifest()

    missing = next(
        warning
        for warning in manifest.warnings
        if warning.code == "documentation_expected_file_missing"
    )
    assert len(LIGHTNING_PUBLIC_DOCUMENTATION_FILES) == 8
    assert len(manifest.entries) == 2
    assert missing.count == 6


def test_symlink_is_rejected_and_manifest_digest_tracks_content(tmp_path: Path) -> None:
    project = tmp_path / "project"
    first = write_document(
        project,
        LIGHTNING_PUBLIC_DOCUMENTATION_FILES[0],
        "# Overview\n\nInitial",
    )
    outside = write_document(tmp_path, "outside.md", "# Outside")
    symlink = project / LIGHTNING_PUBLIC_DOCUMENTATION_FILES[1]
    symlink.parent.mkdir(parents=True, exist_ok=True)
    symlink.symlink_to(outside)
    source = ExplicitMarkdownDocumentSource(project_root=project, feature=feature())

    before = source.load_manifest()
    first.write_text("# Overview\n\nChanged", encoding="utf-8")
    after = source.load_manifest()

    assert before.corpus_manifest_digest != after.corpus_manifest_digest
    warning_counts = {warning.code: warning.count for warning in before.warnings}
    assert warning_counts == {
        "documentation_expected_file_missing": 6,
        "documentation_path_rejected": 1,
    }
    assert [entry.project_relative_path for entry in before.entries] == [
        LIGHTNING_PUBLIC_DOCUMENTATION_FILES[0]
    ]


@pytest.mark.parametrize(
    "unsafe_files",
    [
        [*LIGHTNING_PUBLIC_DOCUMENTATION_FILES[:-1], "/absolute.md"],
        [*LIGHTNING_PUBLIC_DOCUMENTATION_FILES[:-1], "docs/public/../escape.md"],
        [*LIGHTNING_PUBLIC_DOCUMENTATION_FILES[:-1], "docs\\public\\escape.md"],
        [*LIGHTNING_PUBLIC_DOCUMENTATION_FILES[:-1], "docs/public/escape\n.md"],
        [*LIGHTNING_PUBLIC_DOCUMENTATION_FILES[:-1], LIGHTNING_PUBLIC_DOCUMENTATION_FILES[0]],
    ],
)
def test_unsafe_or_duplicate_profile_paths_fail_closed(unsafe_files: list[str]) -> None:
    data = feature().model_dump(mode="python")
    data["corpus"]["files"] = unsafe_files

    with pytest.raises(ValidationError):
        LightningPublicDocumentationRagFeatureConfig.model_validate(data)
