from pathlib import Path

import pytest

from margpa_runtime_llm.bootstrap.model_registry_loader import load_model_definition
from margpa_runtime_llm.modules.runtime_model_control.application import (
    BUILT_IN_GUARD,
    DEEPSEEK_MAIN,
    QWEN3_GUARD,
    QWEN_MAIN,
    SELENE_JUDGE,
    ProviderSelectionController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderRuntimeState,
    ProviderSelectionError,
    ProviderSelectionErrorCode,
)


def test_defaults_are_independent_and_dedicated_roles_are_not_loaded() -> None:
    snapshot = ProviderSelectionController().snapshot()
    by_role = {item.role: item for item in snapshot.selections}
    assert by_role[ModelRole.MAIN].configured_provider == QWEN_MAIN
    assert by_role[ModelRole.MAIN].active_provider == QWEN_MAIN
    assert by_role[ModelRole.GUARD].configured_provider == QWEN3_GUARD
    assert by_role[ModelRole.GUARD].active_provider is None
    assert by_role[ModelRole.JUDGE].configured_provider == SELENE_JUDGE
    assert by_role[ModelRole.JUDGE].active_provider is None
    assert by_role[ModelRole.GUARD].state is ProviderRuntimeState.CONFIGURED
    assert by_role[ModelRole.JUDGE].state is ProviderRuntimeState.CONFIGURED


def test_role_mismatch_is_rejected() -> None:
    controller = ProviderSelectionController()
    before = controller.snapshot()
    with pytest.raises(ProviderSelectionError) as raised:
        controller.select(
            role=ModelRole.JUDGE,
            provider_id=BUILT_IN_GUARD,
            expected_revision=before.revision,
            expected_digest=before.digest_sha512,
        )
    assert raised.value.code is ProviderSelectionErrorCode.ROLE_MISMATCH


def test_stale_cas_does_not_overwrite_newer_selection() -> None:
    controller = ProviderSelectionController()
    initial = controller.snapshot()
    changed = controller.select(
        role=ModelRole.MAIN,
        provider_id=DEEPSEEK_MAIN,
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
    )
    with pytest.raises(ProviderSelectionError) as raised:
        controller.select(
            role=ModelRole.MAIN,
            provider_id=QWEN_MAIN,
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
        )
    assert raised.value.code is ProviderSelectionErrorCode.REVISION_CONFLICT
    assert raised.value.current_snapshot == changed


def test_selection_does_not_implicitly_activate_or_fallback() -> None:
    controller = ProviderSelectionController()
    initial = controller.snapshot()
    changed = controller.select(
        role=ModelRole.JUDGE,
        provider_id=QWEN_MAIN,
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
    )
    judge = next(item for item in changed.selections if item.role is ModelRole.JUDGE)
    assert judge.configured_provider == QWEN_MAIN
    assert judge.active_provider is None
    assert judge.state is ProviderRuntimeState.CONFIGURED
    assert judge.independence.value == "self"


@pytest.mark.parametrize(
    ("file_name", "model_key", "role", "digest"),
    (
        (
            "selene_1_mini_llama_3_1_8b_q5_k_m.toml",
            SELENE_JUDGE,
            "judge",
            "6d5472911fc347d51a73e57077dd34353c3e134a0af67b0dbe4e4df7d980e3246"
            "f0253ee16e5a241a41904d37e73ab3ba11ce5d800de37b9adddb2ada9b6c50d",
        ),
        (
            "qwen3guard_gen_0_6b_q8_0.toml",
            QWEN3_GUARD,
            "guard",
            "0b8d213fd487980ce2667acaaf042d228486d9b467cd90ab6bfbe490527fa1b51"
            "d7a318af593bc920d59f5b22759196c09eaf8cba1974766ab170e6d6f6c19cb",
        ),
    ),
)
def test_dedicated_model_definition_identity(
    file_name: str, model_key: str, role: str, digest: str
) -> None:
    definition = load_model_definition(Path("config/models") / file_name)
    assert definition.model_key == model_key
    assert definition.logical_role == role
    assert definition.artifact.sha512 == digest
