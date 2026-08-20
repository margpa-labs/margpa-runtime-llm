"""Safe field-source trace and bootstrap projection tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.bootstrap.config_loader import (
    load_application_config,
    load_deployment_profile,
    resolve_effective_config,
)
from margpa_runtime_llm.bootstrap.configuration_control import build_configuration_control
from margpa_runtime_llm.modules.configuration_control import (
    ApplyDisposition,
    ConfigurationSource,
)
from margpa_runtime_llm.web.access_profiles import DocumentationRagEffectiveState

PROJECT_ROOT = Path(__file__).resolve().parents[3]
APPLICATION_PATH = PROJECT_ROOT / "config/application.toml"
PROFILE_PATH = PROJECT_ROOT / "config/profiles/local_macos_arm64.toml"


def test_field_sources_follow_existing_precedence_without_exposing_input_names_or_values() -> None:
    application = load_application_config(APPLICATION_PATH)
    profile = load_deployment_profile(PROFILE_PATH).model_copy(
        update={
            "load_overrides": load_deployment_profile(PROFILE_PATH).load_overrides.model_copy(
                update={"context_size": 3072}
            )
        }
    )
    deployment = resolve_effective_config(
        application,
        profile,
        project_root=PROJECT_ROOT,
        environment={},
    )
    environment = resolve_effective_config(
        application,
        profile,
        project_root=PROJECT_ROOT,
        environment={
            "MARGPA_CONTEXT_SIZE": "2457",
            "MARGPA_MODEL_KEY": "sentinel.environment.model",
            "MARGPA_MAX_NEW_TOKENS": "91",
        },
    )
    explicit = resolve_effective_config(
        application,
        profile,
        project_root=PROJECT_ROOT,
        environment={"MARGPA_CONTEXT_SIZE": "2457"},
        cli_model_key="explicit.model",
        load_overrides={"context_size": 1024},
        generation_overrides={"max_new_tokens": 77},
    )

    assert deployment.field_sources.context_size is ConfigurationSource.DEPLOYMENT_PROFILE
    assert environment.field_sources.context_size is ConfigurationSource.ENVIRONMENT
    assert environment.field_sources.selected_model is ConfigurationSource.ENVIRONMENT
    assert environment.field_sources.max_new_tokens is ConfigurationSource.ENVIRONMENT
    assert explicit.field_sources.context_size is ConfigurationSource.EXPLICIT_CLI
    assert explicit.field_sources.selected_model is ConfigurationSource.EXPLICIT_CLI
    assert explicit.field_sources.max_new_tokens is ConfigurationSource.EXPLICIT_CLI
    trace = repr(environment.field_sources)
    assert "MARGPA_" not in trace
    assert "sentinel.environment.model" not in trace
    assert "2457" not in trace


@pytest.mark.parametrize(
    ("state", "expected_mode", "expected_available"),
    [
        (DocumentationRagEffectiveState.DISABLED, "disabled", True),
        (DocumentationRagEffectiveState.ENABLED, "enabled", True),
        (DocumentationRagEffectiveState.UNAVAILABLE, "disabled", False),
        (DocumentationRagEffectiveState.DENIED, "disabled", False),
    ],
)
def test_safe_bootstrap_projection_has_exact_allowlist_and_typed_hook_state_matrix(
    state: DocumentationRagEffectiveState,
    expected_mode: str,
    expected_available: bool,
) -> None:
    effective = resolve_effective_config(
        load_application_config(APPLICATION_PATH),
        load_deployment_profile(PROFILE_PATH),
        project_root=PROJECT_ROOT,
        environment={},
    )

    control = build_configuration_control(
        effective=effective,
        documentation_rag_state=state,
    )
    snapshot = control.effective()

    assert {item.key for item in snapshot.fields} == {
        "selected_model",
        "profile_key",
        "context_size",
        "backend_kind",
        "device_kind",
        "acceleration_api",
        "max_new_tokens",
        "research_developer_mode",
        "conversation_storage_kind",
        "conversation_storage_version",
    }
    assert snapshot.feature_hooks[0].component_key == "documentation_rag"
    assert snapshot.feature_hooks[0].current_mode.value == expected_mode
    assert snapshot.feature_hooks[0].available is expected_available
    assert snapshot.recording_hooks[0].component_key == "conversation_recording"
    assert snapshot.recording_hooks[0].current_mode.value == "off"


@pytest.mark.parametrize(
    (
        "persistence_enabled",
        "storage_backend",
        "storage_backend_version",
        "expected_kind",
        "expected_version",
    ),
    [
        (False, None, None, "disabled", "disabled"),
        (True, "sqlite", "3.45.1", "sqlite", "3.45.1"),
    ],
)
def test_conversation_storage_kind_and_version_reflect_the_actual_composed_backend(
    persistence_enabled: bool,
    storage_backend: str | None,
    storage_backend_version: str | None,
    expected_kind: str,
    expected_version: str,
) -> None:
    effective = resolve_effective_config(
        load_application_config(APPLICATION_PATH),
        load_deployment_profile(PROFILE_PATH),
        project_root=PROJECT_ROOT,
        environment={},
    )

    control = build_configuration_control(
        effective=effective,
        documentation_rag_state=DocumentationRagEffectiveState.UNAVAILABLE,
        conversation_persistence_enabled=persistence_enabled,
        conversation_storage_backend=storage_backend,
        conversation_storage_backend_version=storage_backend_version,
    )
    snapshot = control.effective()
    kind_field = next(item for item in snapshot.fields if item.key == "conversation_storage_kind")
    version_field = next(
        item for item in snapshot.fields if item.key == "conversation_storage_version"
    )

    assert kind_field.value == expected_kind
    assert kind_field.source is ConfigurationSource.COMPOSED_RUNTIME
    assert kind_field.apply_disposition is ApplyDisposition.READ_ONLY
    assert version_field.value == expected_version
    assert version_field.source is ConfigurationSource.COMPOSED_RUNTIME
    assert version_field.apply_disposition is ApplyDisposition.READ_ONLY
