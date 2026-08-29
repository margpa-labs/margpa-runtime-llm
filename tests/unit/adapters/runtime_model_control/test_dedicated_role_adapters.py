"""P6-RR-L: Production dedicated-role Factory Authority-gate and dispatch.

Deliberately never constructs a real `LlamaCppModelAdapter` against the
Project's actual (symlinked, Project-Root-external) `models/` path — no
Exact Model Authority Receipt for Selene/Qwen3Guard exists in this Cycle
(Base Exact Handoff §8.1). Every fixture path below is a `tmp_path` the
Authority-gate itself proves is never reached.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.runtime_model_control.dedicated_role_adapters import (
    MainSharedJudgeRoleAdapter,
    ProductionRoleAdapterFactory,
    Qwen3GuardRoleAdapter,
    SeleneRoleAdapter,
)
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    ModelDefinitionNotRegistered,
)
from margpa_runtime_llm.adapters.runtime_model_control.unavailable_role_adapters import (
    UnavailableRoleProviderAdapter,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition
from margpa_runtime_llm.modules.runtime_model_control.application import (
    DEEPSEEK_MAIN,
    QWEN3_GUARD,
    QWEN_MAIN,
    SELENE_JUDGE,
    default_provider_options,
)
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderKind,
    ProviderOption,
)


class _NullDefinitionResolver:
    """Never resolves anything — proves the Authority gate short-circuits
    *before* this Port is even consulted."""

    def resolve(self, *, model_key: str) -> ModelDefinition:
        raise AssertionError(f"definitions.resolve() must not be reached: {model_key}")

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return ()


class _FakeDefinitionResolver:
    def __init__(self, definitions: dict[str, ModelDefinition]) -> None:
        self._definitions = definitions

    def resolve(self, *, model_key: str) -> ModelDefinition:
        try:
            return self._definitions[model_key]
        except KeyError:
            raise ModelDefinitionNotRegistered(model_key=model_key) from None

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return tuple(self._definitions.values())


def _option_for(role: ModelRole, provider_id: str) -> ProviderOption:
    return next(
        item
        for item in default_provider_options()
        if item.role is role and item.provider_id == provider_id
    )


class _FakeRuntimeModelSnapshot:
    def __init__(self, *, selected_model_key: str) -> None:
        self.selected_model_key = selected_model_key


class _FakeRuntimeModelController:
    def __init__(self, *, selected_model_key: str) -> None:
        self._selected_model_key = selected_model_key

    def snapshot(self) -> _FakeRuntimeModelSnapshot:
        return _FakeRuntimeModelSnapshot(selected_model_key=self._selected_model_key)


def test_selene_preflight_fails_closed_without_authority_and_touches_nothing(
    tmp_path: Path,
) -> None:
    adapter = SeleneRoleAdapter(
        provider_id=SELENE_JUDGE,
        definitions=_NullDefinitionResolver(),
        model_root=tmp_path / "unused-models-root",
        load_config=ModelLoadConfig(),
        authority_granted=False,
        prompt_manifest_path=tmp_path / "unused-manifest.json",
    )
    ready, reason = adapter.preflight()
    assert ready is False
    assert reason == "dedicated_model_authority_unavailable"
    assert adapter.semantic_evaluator is None


def test_qwen3guard_preflight_fails_closed_without_authority_and_touches_nothing(
    tmp_path: Path,
) -> None:
    adapter = Qwen3GuardRoleAdapter(
        provider_id=QWEN3_GUARD,
        definitions=_NullDefinitionResolver(),
        model_root=tmp_path / "unused-models-root",
        load_config=ModelLoadConfig(),
        authority_granted=False,
        contract_manifest_path=tmp_path / "unused-manifest.json",
    )
    ready, reason = adapter.preflight()
    assert ready is False
    assert reason == "dedicated_model_authority_unavailable"
    assert adapter.guard_adapter is None


def test_selene_preflight_with_authority_but_unregistered_definition(tmp_path: Path) -> None:
    adapter = SeleneRoleAdapter(
        provider_id=SELENE_JUDGE,
        definitions=_FakeDefinitionResolver({}),
        model_root=tmp_path,
        load_config=ModelLoadConfig(),
        authority_granted=True,
        prompt_manifest_path=tmp_path / "unused-manifest.json",
    )
    ready, reason = adapter.preflight()
    assert ready is False
    assert reason == "dedicated_model_definition_not_registered"


def test_load_before_preflight_raises() -> None:
    adapter = SeleneRoleAdapter(
        provider_id=SELENE_JUDGE,
        definitions=_NullDefinitionResolver(),
        model_root=Path("unused"),
        load_config=ModelLoadConfig(),
        authority_granted=False,
        prompt_manifest_path=Path("unused-manifest.json"),
    )
    with pytest.raises(RuntimeError, match="preflight must succeed"):
        adapter.load()


def test_main_shared_judge_activates_only_when_main_is_currently_that_model() -> None:
    ref: list[object] = [_FakeRuntimeModelController(selected_model_key=QWEN_MAIN)]
    matching = MainSharedJudgeRoleAdapter(
        provider_id=QWEN_MAIN,
        runtime_model_control_ref=ref,  # type: ignore[arg-type]
    )
    ready, reason = matching.preflight()
    assert ready is True
    assert reason is None
    matching.load()
    matching.unload()

    mismatched = MainSharedJudgeRoleAdapter(
        provider_id=DEEPSEEK_MAIN,
        runtime_model_control_ref=ref,  # type: ignore[arg-type]
    )
    ready, reason = mismatched.preflight()
    assert ready is False
    assert reason == "main_model_mismatch_requires_main_switch"


def test_main_shared_judge_unavailable_when_runtime_model_control_not_built() -> None:
    ref: list[RuntimeModelController | None] = [None]
    adapter = MainSharedJudgeRoleAdapter(provider_id=QWEN_MAIN, runtime_model_control_ref=ref)
    ready, reason = adapter.preflight()
    assert ready is False
    assert reason == "main_runtime_model_control_unavailable"


def test_factory_dispatches_selene_and_qwen3guard_to_dedicated_adapters(tmp_path: Path) -> None:
    factory = ProductionRoleAdapterFactory(
        definitions=_NullDefinitionResolver(),
        model_root=tmp_path,
        load_config=ModelLoadConfig(),
        runtime_model_control_ref=[
            _FakeRuntimeModelController(  # type: ignore[list-item]
                selected_model_key=QWEN_MAIN
            )
        ],
        selene_prompt_manifest_path=tmp_path / "manifest.json",
        qwen3guard_contract_manifest_path=tmp_path / "qwen3guard_manifest.json",
    )
    selene = factory.create(role=ModelRole.JUDGE, option=_option_for(ModelRole.JUDGE, SELENE_JUDGE))
    assert isinstance(selene, SeleneRoleAdapter)
    guard = factory.create(role=ModelRole.GUARD, option=_option_for(ModelRole.GUARD, QWEN3_GUARD))
    assert isinstance(guard, Qwen3GuardRoleAdapter)


def test_factory_dispatches_explicit_main_judge_to_shared_adapter(tmp_path: Path) -> None:
    factory = ProductionRoleAdapterFactory(
        definitions=_NullDefinitionResolver(),
        model_root=tmp_path,
        load_config=ModelLoadConfig(),
        runtime_model_control_ref=[
            _FakeRuntimeModelController(  # type: ignore[list-item]
                selected_model_key=QWEN_MAIN
            )
        ],
        selene_prompt_manifest_path=tmp_path / "manifest.json",
        qwen3guard_contract_manifest_path=tmp_path / "qwen3guard_manifest.json",
    )
    judge_qwen = factory.create(
        role=ModelRole.JUDGE, option=_option_for(ModelRole.JUDGE, QWEN_MAIN)
    )
    assert isinstance(judge_qwen, MainSharedJudgeRoleAdapter)
    ready, _ = judge_qwen.preflight()
    assert ready is True

    judge_deepseek = factory.create(
        role=ModelRole.JUDGE, option=_option_for(ModelRole.JUDGE, DEEPSEEK_MAIN)
    )
    assert isinstance(judge_deepseek, MainSharedJudgeRoleAdapter)
    ready, reason = judge_deepseek.preflight()
    assert ready is False
    assert reason == "main_model_mismatch_requires_main_switch"


def test_factory_falls_back_to_unavailable_for_unregistered_provider(tmp_path: Path) -> None:
    factory = ProductionRoleAdapterFactory(
        definitions=_NullDefinitionResolver(),
        model_root=tmp_path,
        load_config=ModelLoadConfig(),
        runtime_model_control_ref=[
            _FakeRuntimeModelController(  # type: ignore[list-item]
                selected_model_key=QWEN_MAIN
            )
        ],
        selene_prompt_manifest_path=tmp_path / "manifest.json",
        qwen3guard_contract_manifest_path=tmp_path / "qwen3guard_manifest.json",
    )
    unknown_option = ProviderOption(
        provider_id="guard.unregistered-future-provider",
        role=ModelRole.GUARD,
        kind=ProviderKind.MODEL,
        display_name="Unregistered Future Provider",
    )
    adapter = factory.create(role=ModelRole.GUARD, option=unknown_option)
    assert isinstance(adapter, UnavailableRoleProviderAdapter)
