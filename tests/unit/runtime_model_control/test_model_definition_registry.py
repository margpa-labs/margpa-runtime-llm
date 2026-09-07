from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
    ModelDefinitionNotRegistered,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_REAL_REGISTRY_DIR = _PROJECT_ROOT / "config" / "models"


def test_resolves_the_real_qwen_registry_entry_by_model_key() -> None:
    registry = DirectoryModelDefinitionRegistry(registry_dir=_REAL_REGISTRY_DIR)
    definition = registry.resolve(model_key="main.qwen3-4b-q4-k-m")
    assert definition.model_key == "main.qwen3-4b-q4-k-m"
    assert definition.enabled is True


def test_resolves_the_real_deepseek_registry_entry_by_model_key() -> None:
    """P6-CODEX-026 (Fourth Rework): the DeepSeek Q4_K_M Model Definition is
    now registered alongside Qwen, not merely present as an unregistered
    artifact on disk."""
    registry = DirectoryModelDefinitionRegistry(registry_dir=_REAL_REGISTRY_DIR)
    definition = registry.resolve(model_key="main.deepseek-r1-0528-qwen3-8b-q4-k-m")
    assert definition.model_key == "main.deepseek-r1-0528-qwen3-8b-q4-k-m"
    assert definition.enabled is True
    assert definition.model.architecture == "qwen3"


def test_raises_a_typed_error_for_an_unregistered_model_key() -> None:
    registry = DirectoryModelDefinitionRegistry(registry_dir=_REAL_REGISTRY_DIR)
    with pytest.raises(ModelDefinitionNotRegistered) as excinfo:
        registry.resolve(model_key="main.does-not-exist")
    assert excinfo.value.model_key == "main.does-not-exist"


def test_all_definitions_lists_every_registered_toml_file() -> None:
    registry = DirectoryModelDefinitionRegistry(registry_dir=_REAL_REGISTRY_DIR)
    definitions = registry.all_definitions()
    assert len(definitions) == len(list(_REAL_REGISTRY_DIR.glob("*.toml")))
    assert {definition.model_key for definition in definitions} == {
        "main.qwen3-4b-q4-k-m",
        "main.deepseek-r1-0528-qwen3-8b-q4-k-m",
        "judge.selene-1-mini-llama-3.1-8b-q5-k-m",
        "judge.gemma-4-e2b-it-q4-0",
        "guard.qwen3guard-gen-0.6b-q8-0",
    }


def test_resolves_the_real_gemma_4_e2b_lightweight_judge_registry_entry_by_model_key() -> None:
    """P9-1 Package 1: the lightweight independent Judge candidate (Gemma 4 E2B,
    official google/gemma-4-E2B-it-qat-q4_0-gguf) is registered as Model
    Definition data alongside Selene, but is not yet wired into any Provider
    Selection Catalog, Stage Budget or Judge Template — that wiring is
    Package 2 scope."""
    registry = DirectoryModelDefinitionRegistry(registry_dir=_REAL_REGISTRY_DIR)
    definition = registry.resolve(model_key="judge.gemma-4-e2b-it-q4-0")
    assert definition.model_key == "judge.gemma-4-e2b-it-q4-0"
    assert definition.logical_role == "judge"
    assert definition.enabled is True
    assert definition.model.architecture == "gemma4"
    assert definition.artifact.size_bytes == 3349516256
    assert definition.artifact.sha512 == (
        "54b1e06eea3bcfd2f94d2a0195366830d25d63dc15dd2484fa7cd35f82cfd4b"
        "8503702ac3a1a3772775284e3d9a5531a54f1a9b8e3eaa16417d84eae360c76ad"
    )
