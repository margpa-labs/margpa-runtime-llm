"""Public-corpus composition retrieval and citation integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.bootstrap.documentation_rag import build_documentation_rag
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    LIGHTNING_PUBLIC_DOCUMENTATION_FILES,
    DocumentationRagRequestContext,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULTS = PROJECT_ROOT / "config/feature_profiles/documentation_rag_defaults.toml"
LIGHTNING_PROFILE = PROJECT_ROOT / "config/feature_profiles/lightning_public_documentation_rag.toml"


@pytest.mark.parametrize(
    ("query", "expected_path"),
    [
        ("公開統治境界の和文概要", "docs/public/overview_ja.md"),
        ("English public governance boundary overview", "docs/public/overview_en.md"),
    ],
)
def test_public_corpus_retrieves_ja_and_en_with_allowlisted_citations(
    tmp_path: Path,
    query: str,
    expected_path: str,
) -> None:
    project = tmp_path / "project"
    contents = {
        "docs/public/overview_ja.md": "# 公開概要\n\n公開統治境界の和文概要と安全な実行原則。",
        "docs/public/overview_en.md": (
            "# Public overview\n\nEnglish public governance boundary overview and safe runtime."
        ),
    }
    for ordinal, relative in enumerate(LIGHTNING_PUBLIC_DOCUMENTATION_FILES):
        target = project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            contents.get(relative, f"# Public document {ordinal}\n\nGeneral published material."),
            encoding="utf-8",
        )

    composition = build_documentation_rag(
        project_root=project,
        defaults_path=DEFAULTS,
        feature_path=LIGHTNING_PROFILE,
        access_mode="public_demo",
        platform_observation="linux-x86_64-container",
    )
    composition.bind_token_counter(len)

    result = composition.orchestrator.augment_with_context(
        query,
        DocumentationRagRequestContext(
            effective_context_size=4096,
            requested_max_new_tokens=512,
            system_history_current_prompt_tokens=128,
            prompt_token_count_exact=True,
        ),
    )

    assert result.should_generate is True
    assert result.citations
    assert result.citations[0].project_relative_path == expected_path
    assert {citation.project_relative_path for citation in result.citations} <= set(
        LIGHTNING_PUBLIC_DOCUMENTATION_FILES
    )
    assert all(not citation.project_relative_path.startswith("/") for citation in result.citations)
