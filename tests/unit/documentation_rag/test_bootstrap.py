"""Typed local documentation RAG profile and composition tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.bootstrap.documentation_rag import (
    build_documentation_rag,
    build_local_documentation_rag,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    LIGHTNING_PUBLIC_DOCUMENTATION_FILES,
    DocumentationGroundingState,
    DocumentationMeasurementUnit,
    DocumentationRagRequestContext,
)
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULTS = PROJECT_ROOT / "config/feature_profiles/documentation_rag_defaults.toml"
LOCAL_PROFILE = PROJECT_ROOT / "config/feature_profiles/local_documentation_rag.toml"
LIGHTNING_PROFILE = PROJECT_ROOT / "config/feature_profiles/lightning_public_documentation_rag.toml"


def test_tracked_profiles_compose_without_scanning_or_writing_corpus() -> None:
    composition = build_local_documentation_rag(
        project_root=PROJECT_ROOT,
        defaults_path=DEFAULTS,
        feature_path=LOCAL_PROFILE,
    )

    assert composition.defaults.default_mode.value == "disabled"
    assert composition.feature.provider_key == "local_lexical"
    assert composition.feature.active_phase == "phase_1_ex"
    assert composition.feature.corpus.include_history is False
    assert composition.feature.corpus.include_lossless is False


@pytest.mark.parametrize("access_mode", ["basic_preview", "public_demo"])
def test_tracked_lightning_profile_composes_for_both_public_access_modes(
    access_mode: str,
) -> None:
    composition = build_documentation_rag(
        project_root=PROJECT_ROOT,
        defaults_path=DEFAULTS,
        feature_path=LIGHTNING_PROFILE,
        access_mode=access_mode,
        platform_observation="linux-x86_64-container",
    )

    assert composition.defaults.default_mode.value == "disabled"
    assert composition.feature.schema_version == "2"
    assert composition.feature.provider_key == "project_filesystem_lexical"
    assert composition.feature.corpus.files == LIGHTNING_PUBLIC_DOCUMENTATION_FILES
    assert composition.feature.corpus.include_history is False
    assert composition.feature.corpus.include_lossless is False


@pytest.mark.parametrize(
    ("feature_path", "access_mode", "platform_observation"),
    [
        (LOCAL_PROFILE, "public_demo", "linux-x86_64-container"),
        (LIGHTNING_PROFILE, "local", "linux-x86_64-container"),
        (LIGHTNING_PROFILE, "public_demo", "macos-arm64"),
    ],
)
def test_incompatible_access_or_platform_profile_fails_closed(
    feature_path: Path,
    access_mode: str,
    platform_observation: str,
) -> None:
    with pytest.raises(InferenceError) as captured:
        build_documentation_rag(
            project_root=PROJECT_ROOT,
            defaults_path=DEFAULTS,
            feature_path=feature_path,
            access_mode=access_mode,
            platform_observation=platform_observation,
        )

    assert captured.value.safe_message == "The documentation RAG configuration is invalid."
    assert str(feature_path) not in captured.value.safe_message


def test_invalid_profile_fails_closed_without_exposing_path(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.toml"
    invalid.write_text(
        'schema_version = "1"\nprofile_key = "wrong"\ndefault_mode = "disabled"\n',
        encoding="utf-8",
    )

    with pytest.raises(InferenceError) as captured:
        build_local_documentation_rag(
            project_root=PROJECT_ROOT,
            defaults_path=invalid,
            feature_path=LOCAL_PROFILE,
        )

    assert captured.value.safe_message == "The documentation RAG configuration is invalid."
    assert str(invalid) not in captured.value.safe_message


def test_deferred_model_counter_falls_back_then_uses_bound_exact_counter(
    tmp_path: Path,
) -> None:
    project = tmp_path / "project"
    target = project / "docs/project/current/project_ja.md"
    target.parent.mkdir(parents=True)
    target.write_text(
        "# Project概要\n\nNazuna Research Governance LLMの目的と安全境界です。\n",
        encoding="utf-8",
    )
    composition = build_local_documentation_rag(
        project_root=project,
        defaults_path=DEFAULTS,
        feature_path=LOCAL_PROFILE,
    )
    request_context = DocumentationRagRequestContext(
        effective_context_size=4096,
        requested_max_new_tokens=2048,
        system_history_current_prompt_tokens=300,
        prompt_token_count_exact=True,
    )

    fallback = composition.orchestrator.augment_with_context(
        "Nazuna Research Governance LLMの目的",
        request_context,
    )
    composition.bind_token_counter(len)
    exact = composition.orchestrator.augment_with_context(
        "Nazuna Research Governance LLMの目的",
        request_context,
    )

    assert fallback.reference_message is not None
    assert fallback.evidence.context_token_budget_used is False
    assert fallback.evidence.token_counter_fallback_used is True
    assert fallback.evidence.context_measurement_unit is (
        DocumentationMeasurementUnit.UNICODE_CHARACTERS
    )
    assert fallback.evidence.context_measurement_limit == 2400
    assert "documentation_token_counter_unavailable" in {
        warning.code for warning in fallback.warnings
    }
    fallback_evidence = fallback.evidence.model_dump(mode="json")
    assert fallback_evidence["context_budget_unit"] == "tokens"
    assert fallback_evidence["context_measurement_unit"] == "unicode_characters"
    assert fallback_evidence["context_measurement_limit"] == 2400
    assert exact.reference_message is not None
    assert exact.evidence.context_token_budget_used is True
    assert exact.evidence.token_counter_fallback_used is False
    assert exact.evidence.context_measurement_unit is DocumentationMeasurementUnit.TOKENS
    assert exact.evidence.context_measurement_limit == 768
    assert "documentation_token_counter_unavailable" not in {
        warning.code for warning in exact.warnings
    }
    exact_evidence = exact.evidence.model_dump(mode="json")
    assert exact_evidence["context_budget_unit"] == "tokens"
    assert exact_evidence["context_measurement_unit"] == "tokens"
    assert exact_evidence["context_measurement_limit"] == 768


def test_missing_exact_base_prompt_measurement_fails_closed_before_corpus_use(
    tmp_path: Path,
) -> None:
    composition = build_local_documentation_rag(
        project_root=tmp_path / "project-without-docs",
        defaults_path=DEFAULTS,
        feature_path=LOCAL_PROFILE,
    )

    result = composition.orchestrator.augment_with_context(
        "ARGDとは何ですか。",
        DocumentationRagRequestContext(
            effective_context_size=4096,
            requested_max_new_tokens=2048,
            system_history_current_prompt_tokens=None,
            prompt_token_count_exact=False,
        ),
    )

    assert result.should_generate is False
    assert result.reference_message is None
    assert result.evidence.base_prompt_used is None
    assert result.evidence.base_prompt_exact is False
    assert result.evidence.grounding_state is DocumentationGroundingState.UNAVAILABLE
    assert result.evidence.generation_allowed is False
    assert result.evidence.retrieved_chunk_count == 0
    assert result.evidence.assembled_block_count == 0
    assert [warning.code for warning in result.warnings] == [
        "documentation_prompt_measurement_unavailable"
    ]
