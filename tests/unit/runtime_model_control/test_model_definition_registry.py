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
    }
