"""Filesystem-backed ModelDefinitionResolverPort (Phase 6-B-WU-002).

Scans a directory of Registry TOML files and indexes them by `model_key`,
reusing the existing single-file `load_model_definition` loader as-is
rather than reimplementing TOML parsing/hashing.
"""

from pathlib import Path

from margpa_runtime_llm.bootstrap.model_registry_loader import load_model_definition
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition


class ModelDefinitionNotRegistered(Exception):
    def __init__(self, *, model_key: str) -> None:
        self.model_key = model_key
        super().__init__(f"no registered model definition for model_key={model_key!r}")


class DirectoryModelDefinitionRegistry:
    """Resolves `model_key -> ModelDefinition` by scanning `*.toml` files in a directory."""

    def __init__(self, *, registry_dir: Path) -> None:
        self._registry_dir = registry_dir.expanduser().resolve()

    def resolve(self, *, model_key: str) -> ModelDefinition:
        for candidate_path in sorted(self._registry_dir.glob("*.toml")):
            definition = load_model_definition(candidate_path)
            if definition.model_key == model_key:
                return definition
        raise ModelDefinitionNotRegistered(model_key=model_key)

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return tuple(
            load_model_definition(candidate_path)
            for candidate_path in sorted(self._registry_dir.glob("*.toml"))
        )
