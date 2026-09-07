"""P9-1 Package 2 OF-P2-003: `SystemMemoryRoleResourceGate` fixture-level
arithmetic/wiring proof (no real Model Load, no real `psutil` reading --
both are injected fakes so every scenario is deterministic).

Real-hardware confirmation that this Gate actually refuses activation
under real, current, tight memory conditions on the deployment Mac lives
in `tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.runtime_model_control.memory_resource_gate import (
    ROLE_MEMORY_SAFETY_MARGIN_BYTES,
    SystemMemoryRoleResourceGate,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import MODEL_REQUIRED_CAPABILITIES
from margpa_runtime_llm.modules.inference.domain.model_definition import (
    ModelArtifactDefinition,
    ModelBackendDefinition,
    ModelDefinition,
    ModelExpectedCapabilities,
    ModelMetadataDefinition,
    ModelOutputProtocolDefinition,
    ModelSourceDefinition,
    ModelVerificationDefinition,
    ThinkingOutputProtocolDefinition,
)
from margpa_runtime_llm.modules.runtime_model_control.application import (
    DEEPSEEK_MAIN,
    QWEN_MAIN,
    SELENE_JUDGE,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    ModelRole,
    RuntimeState,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderKind,
    ProviderOption,
)

_SHA512_FILLER = "a" * 128
_MAIN_MODEL_KEY = "main.fake-main-q4"


def _definition(*, model_key: str, size_bytes: int) -> ModelDefinition:
    return ModelDefinition(
        model_key=model_key,
        logical_role="main" if model_key.startswith("main.") else "dedicated",
        enabled=True,
        source=ModelSourceDefinition(
            provider="huggingface",
            distribution_repository="test-org/test-model",
            upstream_model="test-model",
        ),
        artifact=ModelArtifactDefinition(
            relative_path=Path(f"models/{model_key}/gguf/{model_key}.gguf"),
            file_name=f"{model_key}.gguf",
            format="gguf",
            quantization="Q4_K_M",
            size_bytes=size_bytes,
            sha512=_SHA512_FILLER,
        ),
        backend=ModelBackendDefinition(backend_key="llama_cpp", required_version=">=0.3.0"),
        model=ModelMetadataDefinition(
            architecture="test-arch",
            native_context_limit=8192,
            chat_template_source="embedded",
        ),
        capabilities=ModelExpectedCapabilities(required_features=MODEL_REQUIRED_CAPABILITIES),
        verification=ModelVerificationDefinition(state="verified", provenance_complete=True),
        output_protocol=ModelOutputProtocolDefinition(
            thinking=ThinkingOutputProtocolDefinition(parser_key="plain_text_v1")
        ),
        definition_file_sha512=_SHA512_FILLER,
    )


class _FakeDefinitionResolver:
    def __init__(self, definitions: dict[str, ModelDefinition]) -> None:
        self._definitions = definitions

    def resolve(self, *, model_key: str) -> ModelDefinition:
        return self._definitions[model_key]

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return tuple(self._definitions.values())


class _RaisingDefinitionResolver:
    def resolve(self, *, model_key: str) -> ModelDefinition:
        raise RuntimeError(f"unregistered: {model_key}")

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return ()


class _FakeSnapshot:
    def __init__(self, *, selected_model_key: str, runtime_state: RuntimeState) -> None:
        self.selected_model_key = selected_model_key
        self.runtime_state = runtime_state


class _FakeRuntimeModelController:
    def __init__(self, *, selected_model_key: str, runtime_state: RuntimeState) -> None:
        self._snapshot = _FakeSnapshot(
            selected_model_key=selected_model_key, runtime_state=runtime_state
        )

    def snapshot(self) -> _FakeSnapshot:
        return self._snapshot


def _judge_model_option(
    *, provider_id: str = SELENE_JUDGE, model_key: str | None = SELENE_JUDGE
) -> ProviderOption:
    return ProviderOption(
        provider_id=provider_id,
        role=ModelRole.JUDGE,
        kind=ProviderKind.MODEL,
        display_name="Fake Judge",
        model_key=model_key,
    )


def test_allows_non_model_kind_options_unconditionally() -> None:
    gate = SystemMemoryRoleResourceGate(
        definitions=_FakeDefinitionResolver({}),
        runtime_model_control_ref=[None],
        available_memory_probe=lambda: 0,
    )
    built_in = ProviderOption(
        provider_id="judge.built-in",
        role=ModelRole.JUDGE,
        kind=ProviderKind.BUILT_IN,
        display_name="Built-in",
    )
    none_option = ProviderOption(
        provider_id="none", role=ModelRole.JUDGE, kind=ProviderKind.NONE, display_name="None"
    )
    assert gate.allow_activation(role=ModelRole.JUDGE, option=built_in) == (True, None)
    assert gate.allow_activation(role=ModelRole.JUDGE, option=none_option) == (True, None)


@pytest.mark.parametrize("main_shared_provider_id", [QWEN_MAIN, DEEPSEEK_MAIN])
def test_allows_main_shared_judge_selection_unconditionally_even_with_zero_available_memory(
    main_shared_provider_id: str,
) -> None:
    gate = SystemMemoryRoleResourceGate(
        definitions=_FakeDefinitionResolver({}),
        runtime_model_control_ref=[None],
        available_memory_probe=lambda: 0,
    )
    option = _judge_model_option(
        provider_id=main_shared_provider_id, model_key=main_shared_provider_id
    )
    assert gate.allow_activation(role=ModelRole.JUDGE, option=option) == (True, None)


def test_denies_when_candidate_plus_active_main_plus_margin_exceeds_available_memory() -> None:
    candidate_bytes = 5_000_000_000
    main_bytes = 2_000_000_000
    gate = SystemMemoryRoleResourceGate(
        definitions=_FakeDefinitionResolver(
            {
                SELENE_JUDGE: _definition(model_key=SELENE_JUDGE, size_bytes=candidate_bytes),
                _MAIN_MODEL_KEY: _definition(model_key=_MAIN_MODEL_KEY, size_bytes=main_bytes),
            }
        ),
        runtime_model_control_ref=[
            _FakeRuntimeModelController(  # type: ignore[list-item]
                selected_model_key=_MAIN_MODEL_KEY, runtime_state=RuntimeState.ACTIVE
            )
        ],
        available_memory_probe=lambda: (
            candidate_bytes + main_bytes + ROLE_MEMORY_SAFETY_MARGIN_BYTES - 1
        ),
    )
    allowed, reason = gate.allow_activation(role=ModelRole.JUDGE, option=_judge_model_option())
    assert allowed is False
    assert reason is not None
    assert reason.startswith("resource_gate_denied:")


def test_allows_when_candidate_plus_active_main_plus_margin_fits_available_memory() -> None:
    candidate_bytes = 5_000_000_000
    main_bytes = 2_000_000_000
    gate = SystemMemoryRoleResourceGate(
        definitions=_FakeDefinitionResolver(
            {
                SELENE_JUDGE: _definition(model_key=SELENE_JUDGE, size_bytes=candidate_bytes),
                _MAIN_MODEL_KEY: _definition(model_key=_MAIN_MODEL_KEY, size_bytes=main_bytes),
            }
        ),
        runtime_model_control_ref=[
            _FakeRuntimeModelController(  # type: ignore[list-item]
                selected_model_key=_MAIN_MODEL_KEY, runtime_state=RuntimeState.ACTIVE
            )
        ],
        available_memory_probe=lambda: (
            candidate_bytes + main_bytes + ROLE_MEMORY_SAFETY_MARGIN_BYTES + 1
        ),
    )
    assert gate.allow_activation(role=ModelRole.JUDGE, option=_judge_model_option()) == (
        True,
        None,
    )


def _active_main_ref(
    *, model_key: str = _MAIN_MODEL_KEY, runtime_state: RuntimeState = RuntimeState.ACTIVE
) -> list[object]:
    return [_FakeRuntimeModelController(selected_model_key=model_key, runtime_state=runtime_state)]


def test_allows_unconditionally_when_main_is_not_active_even_with_zero_available_memory() -> None:
    """The short-circuit itself: main_bytes == 0 must skip straight to
    `True, None` without ever consulting candidate size or the memory
    probe — proven here by an available-memory reading of 0, which would
    fail every other scenario in this file."""
    gate = SystemMemoryRoleResourceGate(
        definitions=_FakeDefinitionResolver(
            {
                SELENE_JUDGE: _definition(model_key=SELENE_JUDGE, size_bytes=10**12),
                _MAIN_MODEL_KEY: _definition(model_key=_MAIN_MODEL_KEY, size_bytes=10**12),
            }
        ),
        runtime_model_control_ref=_active_main_ref(runtime_state=RuntimeState.UNAVAILABLE),  # type: ignore[arg-type]
        available_memory_probe=lambda: 0,
    )
    assert gate.allow_activation(role=ModelRole.JUDGE, option=_judge_model_option()) == (
        True,
        None,
    )


def test_allows_unconditionally_when_runtime_model_control_ref_not_yet_populated() -> None:
    gate = SystemMemoryRoleResourceGate(
        definitions=_FakeDefinitionResolver(
            {SELENE_JUDGE: _definition(model_key=SELENE_JUDGE, size_bytes=10**12)}
        ),
        runtime_model_control_ref=[None],
        available_memory_probe=lambda: 0,
    )
    assert gate.allow_activation(role=ModelRole.JUDGE, option=_judge_model_option()) == (
        True,
        None,
    )


def test_fails_open_when_candidate_definition_cannot_be_resolved() -> None:
    """Main is genuinely ACTIVE here (main_bytes != 0) so the candidate
    resolve is actually reached, rather than being short-circuited away
    before this Gate's own error-handling is ever exercised."""
    gate = SystemMemoryRoleResourceGate(
        definitions=_RaisingDefinitionResolver(),
        runtime_model_control_ref=_active_main_ref(),  # type: ignore[arg-type]
        available_memory_probe=lambda: 0,
    )
    assert gate.allow_activation(role=ModelRole.JUDGE, option=_judge_model_option()) == (
        True,
        None,
    )


def test_allows_when_main_definition_cannot_be_resolved_even_though_main_reports_active() -> None:
    """`selected_model_key` resolves to nothing (an inconsistent Registry
    state) -- `_active_main_bytes()` fails open to 0, which now also means
    the whole Gate short-circuits to allow, exactly like Main genuinely
    being inactive. This Gate never blocks Judge/Guard activation over an
    unrelated Registry inconsistency it cannot itself resolve."""
    gate = SystemMemoryRoleResourceGate(
        definitions=_FakeDefinitionResolver(
            {SELENE_JUDGE: _definition(model_key=SELENE_JUDGE, size_bytes=5_000_000_000)}
        ),
        runtime_model_control_ref=_active_main_ref(model_key="main.unregistered"),  # type: ignore[arg-type]
        available_memory_probe=lambda: 0,
    )
    assert gate.allow_activation(role=ModelRole.JUDGE, option=_judge_model_option()) == (
        True,
        None,
    )


def test_fails_open_when_memory_probe_itself_raises() -> None:
    """Main is genuinely ACTIVE here so the probe is actually reached."""

    def _broken_probe() -> int:
        raise RuntimeError("psutil unavailable in this sandbox")

    gate = SystemMemoryRoleResourceGate(
        definitions=_FakeDefinitionResolver(
            {
                SELENE_JUDGE: _definition(model_key=SELENE_JUDGE, size_bytes=10**12),
                _MAIN_MODEL_KEY: _definition(model_key=_MAIN_MODEL_KEY, size_bytes=10**12),
            }
        ),
        runtime_model_control_ref=_active_main_ref(),  # type: ignore[arg-type]
        available_memory_probe=_broken_probe,
    )
    assert gate.allow_activation(role=ModelRole.JUDGE, option=_judge_model_option()) == (
        True,
        None,
    )


def test_allows_when_option_model_key_is_none() -> None:
    """Main is genuinely ACTIVE here so this path (rather than the
    Main-not-active short-circuit) is what actually allows it."""
    gate = SystemMemoryRoleResourceGate(
        definitions=_FakeDefinitionResolver(
            {_MAIN_MODEL_KEY: _definition(model_key=_MAIN_MODEL_KEY, size_bytes=10**12)}
        ),
        runtime_model_control_ref=_active_main_ref(),  # type: ignore[arg-type]
        available_memory_probe=lambda: 0,
    )
    option = _judge_model_option(provider_id="judge.no-model-key", model_key=None)
    assert gate.allow_activation(role=ModelRole.JUDGE, option=option) == (True, None)
