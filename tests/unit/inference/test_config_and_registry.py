"""TOML Registry and effective configuration tests."""

import hashlib
import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.bootstrap.config_loader import (
    ApplicationConfig,
    DeploymentProfile,
    load_application_config,
    load_deployment_profile,
    resolve_effective_config,
)
from margpa_runtime_llm.bootstrap.model_registry_loader import load_model_definition
from margpa_runtime_llm.bootstrap.profile_resolver import (
    PlatformRegistry,
    load_platform_registry,
)
from margpa_runtime_llm.modules.configuration_control import ConfigurationSource
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import (
    ResponseLanguage,
    ResponseLanguageSource,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelLoadConfig
from margpa_runtime_llm.modules.inference.domain.capabilities import CapabilityFeature
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    DEFAULT_THINKING_DISPLAY_LABEL,
    ThinkingPersistence,
    ThinkingPresentationConfig,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.summarization.public import (
    SummaryBackend,
    SummaryFailurePolicy,
    SummaryMode,
)
from margpa_runtime_llm.orchestration.thinking_presentation import (
    resolve_thinking_presentation_policy,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"
PROFILE_PATH = PROJECT_ROOT / "config/profiles/local_macos_arm64.toml"
APPLICATION_PATH = PROJECT_ROOT / "config/application.toml"
PLATFORM_REGISTRY_PATH = PROJECT_ROOT / "config/platforms/platform_registry.toml"
LIGHTNING_CUDA_PROFILE_PATH = PROJECT_ROOT / "config/profiles/lightning_linux_x86_64_cuda.toml"
LIGHTNING_CPU_PROFILE_PATH = PROJECT_ROOT / "config/profiles/lightning_linux_x86_64_cpu.toml"
LIGHTNING_CPU_NATIVE_PROFILE_PATH = (
    PROJECT_ROOT / "config/profiles/lightning_linux_x86_64_cpu_native.toml"
)


def test_registry_records_artifact_and_definition_digests() -> None:
    definition = load_model_definition(REGISTRY_PATH)

    assert definition.model_key == "main.qwen3-4b-q4-k-m"
    assert definition.source.revision is None
    assert not definition.verification.provenance_complete
    assert definition.artifact.size_bytes == 2_497_280_256
    assert definition.artifact.sha512.startswith("f182f1d40606")
    assert CapabilityFeature.GPU_OFFLOAD not in definition.capabilities.required_features
    assert CapabilityFeature.GPU_OFFLOAD in definition.capabilities.optional_features
    assert definition.schema_version == "2"
    assert definition.output_protocol.thinking.parser_key == "tagged_thinking_v1"
    assert definition.output_protocol.thinking.opening_delimiter == "<think>"
    assert definition.output_protocol.thinking.closing_delimiter == "</think>"
    assert (
        definition.definition_file_sha512 == hashlib.sha512(REGISTRY_PATH.read_bytes()).hexdigest()
    )


def test_project_metadata_supports_python_312_and_313_with_313_local_default() -> None:
    project = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert project["project"]["requires-python"] == ">=3.12,<3.14"
    assert project["tool"]["ruff"]["target-version"] == "py312"
    assert project["tool"]["mypy"]["python_version"] == "3.12"
    assert (PROJECT_ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.13.14"


def test_application_config_owns_common_phase1_defaults() -> None:
    application = load_application_config(APPLICATION_PATH)

    assert application.schema_version == "3"
    assert application.application_key == "default"
    assert application.selected_model == "main.qwen3-4b-q4-k-m"
    assert application.model_root.default == Path("models")
    assert application.load_defaults.context_size == 4096
    assert application.load_defaults.verify_artifact_hash
    assert application.generation.max_new_tokens == 2048
    assert application.generation.thinking_mode is ThinkingMode.DISABLED
    assert application.response.language is ResponseLanguage.JA
    assert application.presentation.thinking.visibility == "hidden"
    assert application.presentation.thinking.display_label == "推論過程"
    assert application.presentation.thinking.persistence == "disabled"
    assert application.layers.summarization.mode is SummaryMode.OFF
    assert application.layers.summarization.backend is SummaryBackend.MAIN_MODEL
    assert application.layers.summarization.max_new_tokens == 1024
    assert application.layers.summarization.thinking_mode is ThinkingMode.DISABLED
    assert application.layers.summarization.preserve_original is True
    assert application.layers.summarization.failure_policy is SummaryFailurePolicy.FALLBACK_ORIGINAL


def test_deployment_profile_owns_only_platform_and_hardware_overrides() -> None:
    profile = load_deployment_profile(PROFILE_PATH)

    assert profile.schema_version == "3"
    assert profile.verification_state == "native_verified"
    assert profile.host.operating_system_key == "macos"
    assert profile.host.architecture_key == "arm64"
    assert profile.compute.compute_kind_key == "gpu"
    assert profile.compute.acceleration_api_key == "metal"
    assert profile.backend_runtime.build_variant_key == "metal"
    assert profile.runtime_requirements.required_capabilities == {CapabilityFeature.GPU_OFFLOAD}
    assert profile.load_overrides.batch_size == 256
    assert profile.load_overrides.gpu_layers == -1

    raw_profile = tomllib.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    assert "selected_model" not in raw_profile
    assert "model_root" not in raw_profile
    assert "generation" not in raw_profile
    assert "response" not in raw_profile
    assert "presentation" not in raw_profile
    assert "layers" not in raw_profile
    assert "load" not in raw_profile


def test_platform_registry_owns_aliases_and_default_profile_mapping() -> None:
    registry = load_platform_registry(PLATFORM_REGISTRY_PATH)

    assert registry.schema_version == "2"
    assert registry.execution_environment_keys == {"native", "container"}
    assert {alias.raw_value for alias in registry.operating_system_aliases} >= {
        "darwin",
        "windows",
        "linux",
    }
    assert {alias.raw_value for alias in registry.architecture_aliases} >= {
        "arm64",
        "aarch64",
        "amd64",
        "x86_64",
    }
    assert len(registry.profile_defaults) == 1
    assert registry.profile_defaults[0].profile_path == PROFILE_PATH.relative_to(PROJECT_ROOT)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("operating_system_key", "macso"),
        ("architecture_key", "arm65"),
        ("execution_environment_key", "wsl"),
    ],
)
def test_platform_registry_rejects_unreachable_default_references(
    field_name: str,
    invalid_value: str,
) -> None:
    registry_data = tomllib.loads(PLATFORM_REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_data["profile_defaults"][0][field_name] = invalid_value

    with pytest.raises(ValidationError):
        PlatformRegistry.model_validate(registry_data)


@pytest.mark.parametrize(
    "alias_field",
    ["operating_system_aliases", "architecture_aliases"],
)
def test_platform_registry_rejects_empty_alias_sets(alias_field: str) -> None:
    registry_data = tomllib.loads(PLATFORM_REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_data[alias_field] = []

    with pytest.raises(ValidationError):
        PlatformRegistry.model_validate(registry_data)


def test_platform_registry_loader_maps_reference_error_to_safe_configuration_error(
    tmp_path: Path,
) -> None:
    registry_path = tmp_path / "invalid-platform-registry.toml"
    fixture = PLATFORM_REGISTRY_PATH.read_text(encoding="utf-8").replace(
        'operating_system_key = "macos"',
        'operating_system_key = "macso"',
        1,
    )
    registry_path.write_text(fixture, encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_platform_registry(registry_path)

    assert captured.value.code == "invalid_configuration"
    assert str(tmp_path) not in captured.value.safe_message


def test_application_cannot_disable_phase1b_artifact_hash_verification(tmp_path: Path) -> None:
    application_path = tmp_path / "hash-disabled.toml"
    fixture = APPLICATION_PATH.read_text(encoding="utf-8").replace(
        "verify_artifact_hash = true",
        "verify_artifact_hash = false",
    )
    parsed_fixture = tomllib.loads(fixture)
    assert fixture.count("verify_artifact_hash") == 1
    assert parsed_fixture["load_defaults"]["verify_artifact_hash"] is False
    application_path.write_text(fixture, encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_application_config(application_path)

    assert captured.value.code == "invalid_configuration"


def test_lightning_profiles_separate_cuda_and_cpu_without_silent_fallback() -> None:
    cuda = load_deployment_profile(LIGHTNING_CUDA_PROFILE_PATH)
    cpu = load_deployment_profile(LIGHTNING_CPU_PROFILE_PATH)

    for profile in (cuda, cpu):
        assert profile.verification_state == "defined"
        assert profile.host.operating_system_key == "linux"
        assert profile.host.architecture_key == "x86_64"
        assert profile.host.execution_environment_key == "container"
        assert profile.host.distribution_key == "ubuntu"
        assert profile.backend_runtime.build_variant_key == "cuda"
        assert profile.runtime_requirements.fallback_policy == "deny"
        assert profile.load_overrides.threads == 4

    assert cuda.compute.compute_kind_key == "gpu"
    assert cuda.compute.vendor_key == "nvidia"
    assert cuda.compute.acceleration_api_key == "cuda"
    assert cuda.runtime_requirements.required_capabilities == {CapabilityFeature.GPU_OFFLOAD}
    assert cuda.load_overrides.gpu_layers == -1

    assert cpu.compute.compute_kind_key == "cpu"
    assert cpu.compute.acceleration_api_key == "cpu_native"
    assert not cpu.runtime_requirements.required_capabilities
    assert cpu.load_overrides.gpu_layers == 0


def test_lightning_pure_cpu_profile_is_distinct_from_cuda_cpu_execution() -> None:
    cuda_cpu = load_deployment_profile(LIGHTNING_CPU_PROFILE_PATH)
    pure_cpu = load_deployment_profile(LIGHTNING_CPU_NATIVE_PROFILE_PATH)

    assert cuda_cpu.backend_runtime.build_variant_key == "cuda"
    assert cuda_cpu.compute.acceleration_api_key == "cpu_native"
    assert pure_cpu.profile_key == "external.lightning-linux-x86_64.cpu-native"
    assert pure_cpu.verification_state == "defined"
    assert pure_cpu.host.operating_system_key == "linux"
    assert pure_cpu.host.architecture_key == "x86_64"
    assert pure_cpu.host.execution_environment_key == "container"
    assert pure_cpu.compute.compute_kind_key == "cpu"
    assert pure_cpu.compute.vendor_key == "generic"
    assert pure_cpu.compute.acceleration_api_key == "none"
    assert pure_cpu.backend_runtime.build_variant_key == "cpu"
    assert pure_cpu.runtime_requirements.required_device_kind == "cpu"
    assert pure_cpu.runtime_requirements.required_acceleration_api == "none"
    assert not pure_cpu.runtime_requirements.required_capabilities
    assert pure_cpu.runtime_requirements.fallback_policy == "deny"
    assert pure_cpu.load_overrides.gpu_layers == 0


def test_model_load_contract_rejects_disabled_artifact_hash_verification() -> None:
    with pytest.raises(ValidationError):
        ModelLoadConfig.model_validate({"verify_artifact_hash": False})


def test_effective_config_applies_environment_then_cli() -> None:
    application = load_application_config(APPLICATION_PATH)
    profile = load_deployment_profile(PROFILE_PATH)
    effective = resolve_effective_config(
        application,
        profile,
        project_root=PROJECT_ROOT,
        environment={
            "MARGPA_MODEL_ROOT": "environment-models",
            "MARGPA_MAX_NEW_TOKENS": "64",
            "MARGPA_THINKING_MODE": "enabled",
            "MARGPA_CONTEXT_SIZE": "2048",
            "MARGPA_RESPONSE_LANGUAGE": "en",
            "MARGPA_THINKING_VISIBILITY": "visible",
            "MARGPA_THINKING_LABEL": "環境推論",
        },
        cli_model_root=Path("cli-models"),
        generation_overrides={"max_new_tokens": 32},
        load_overrides={"context_size": 1024},
        response_language=ResponseLanguage.AUTO,
        thinking_visibility=ThinkingVisibility.HIDDEN,
        thinking_label="明示推論",
    )

    assert effective.model_root == (PROJECT_ROOT / "cli-models").resolve()
    assert effective.generation.max_new_tokens == 32
    assert effective.generation.thinking_mode is ThinkingMode.ENABLED
    assert effective.load.context_size == 1024
    assert effective.response.language is ResponseLanguage.AUTO
    assert effective.response.source is ResponseLanguageSource.EXPLICIT
    assert effective.presentation.visibility is ThinkingVisibility.HIDDEN
    assert effective.presentation.display_label == "明示推論"
    assert effective.presentation.visibility_source is ThinkingPresentationSource.EXPLICIT
    assert effective.presentation.display_label_source is ThinkingPresentationSource.EXPLICIT
    assert effective.presentation.persistence_source is ThinkingPresentationSource.APPLICATION
    assert effective.applied_sources == (
        "built_in_defaults",
        "application",
        "deployment_profile",
        "environment",
        "cli_override",
    )


def test_load_composition_uses_field_specific_precedence() -> None:
    application = load_application_config(APPLICATION_PATH)
    profile = load_deployment_profile(PROFILE_PATH)
    profile = profile.model_copy(
        update={"load_overrides": profile.load_overrides.model_copy(update={"context_size": 3072})}
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
        environment={"MARGPA_CONTEXT_SIZE": "2048"},
    )
    explicit = resolve_effective_config(
        application,
        profile,
        project_root=PROJECT_ROOT,
        environment={"MARGPA_CONTEXT_SIZE": "2048"},
        load_overrides={"context_size": 1024},
    )

    assert application.load_defaults.context_size == 4096
    assert deployment.load.context_size == 3072
    assert environment.load.context_size == 2048
    assert explicit.load.context_size == 1024
    assert explicit.load.batch_size == 256
    assert not explicit.load.verbose_backend
    assert deployment.field_sources.context_size is ConfigurationSource.DEPLOYMENT_PROFILE
    assert environment.field_sources.context_size is ConfigurationSource.ENVIRONMENT
    assert explicit.field_sources.context_size is ConfigurationSource.EXPLICIT_CLI


def test_invalid_profile_is_mapped_to_safe_configuration_error(tmp_path: Path) -> None:
    profile_path = tmp_path / "invalid.toml"
    profile_path.write_text('unknown = "value"\n', encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_deployment_profile(profile_path)

    assert captured.value.code == "invalid_configuration"
    assert str(tmp_path) not in captured.value.safe_message


def test_profile_contract_rejects_unknown_fields_directly() -> None:
    profile_data = tomllib.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profile_data["generation"] = {"max_new_tokens": 2371}

    with pytest.raises(ValidationError):
        DeploymentProfile.model_validate(profile_data)


def test_deployment_profile_cannot_own_presentation() -> None:
    profile_data = tomllib.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profile_data["presentation"] = {"thinking": {"visibility": "visible"}}

    with pytest.raises(ValidationError):
        DeploymentProfile.model_validate(profile_data)


def test_old_mixed_profile_schema_is_not_accepted() -> None:
    profile_data = tomllib.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profile_data["schema_version"] = "2"
    profile_data["selected_model"] = "main.qwen3-4b-q4-k-m"

    with pytest.raises(ValidationError):
        DeploymentProfile.model_validate(profile_data)


def test_deployment_load_override_rejects_application_owned_fields() -> None:
    profile_data = tomllib.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    profile_data["load_overrides"]["verbose_backend"] = True

    with pytest.raises(ValidationError):
        DeploymentProfile.model_validate(profile_data)


def test_application_config_rejects_unknown_fields_and_unsafe_model_root() -> None:
    application_data = tomllib.loads(APPLICATION_PATH.read_text(encoding="utf-8"))
    application_data["unexpected"] = True

    with pytest.raises(ValidationError):
        ApplicationConfig.model_validate(application_data)

    application_data.pop("unexpected")
    application_data["model_root"]["default"] = "/Users/example/private-models"
    with pytest.raises(ValidationError):
        ApplicationConfig.model_validate(application_data)


def test_old_application_schema_is_not_silently_accepted(tmp_path: Path) -> None:
    application_path = tmp_path / "old-application.toml"
    fixture = APPLICATION_PATH.read_text(encoding="utf-8").replace(
        'schema_version = "3"',
        'schema_version = "2"',
        1,
    )
    application_path.write_text(fixture, encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_application_config(application_path)

    assert captured.value.code == "invalid_configuration"


def test_old_platform_registry_schema_is_not_silently_accepted(tmp_path: Path) -> None:
    registry_path = tmp_path / "old-platform-registry.toml"
    fixture = PLATFORM_REGISTRY_PATH.read_text(encoding="utf-8").replace(
        'schema_version = "2"',
        'schema_version = "1"',
        1,
    )
    registry_path.write_text(fixture, encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_platform_registry(registry_path)

    assert captured.value.code == "invalid_configuration"


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('visibility = "hidden"', 'visibility = "sometimes"'),
        ('display_label = "推論過程"', 'display_label = "<unsafe>"'),
        ('persistence = "disabled"', 'persistence = "enabled"'),
    ],
)
def test_application_loader_rejects_invalid_presentation(
    tmp_path: Path,
    old: str,
    new: str,
) -> None:
    application_path = tmp_path / "invalid-presentation.toml"
    fixture = APPLICATION_PATH.read_text(encoding="utf-8").replace(old, new, 1)
    application_path.write_text(fixture, encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_application_config(application_path)

    assert captured.value.code == "invalid_configuration"


def test_application_loader_maps_unknown_language_to_safe_configuration_error(
    tmp_path: Path,
) -> None:
    application_path = tmp_path / "invalid-language.toml"
    fixture = APPLICATION_PATH.read_text(encoding="utf-8").replace(
        'language = "ja"',
        'language = "jp"',
        1,
    )
    application_path.write_text(fixture, encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_application_config(application_path)

    assert captured.value.code == "invalid_configuration"
    assert str(tmp_path) not in captured.value.safe_message


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ('mode = "off"', 'mode = "on"'),
        ('backend = "main_model"', 'backend = "dedicated_model"'),
        ("max_new_tokens = 1024", "max_new_tokens = 512"),
        (
            'max_new_tokens = 1024\nthinking_mode = "disabled"',
            'max_new_tokens = 1024\nthinking_mode = "enabled"',
        ),
        ("preserve_original = true", "preserve_original = false"),
        ('failure_policy = "fallback_original"', 'failure_policy = "error"'),
    ],
)
def test_application_loader_rejects_invalid_summarization_policy(
    tmp_path: Path,
    old: str,
    new: str,
) -> None:
    application_path = tmp_path / "invalid-summarization.toml"
    fixture = APPLICATION_PATH.read_text(encoding="utf-8").replace(old, new, 1)
    application_path.write_text(fixture, encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_application_config(application_path)

    assert captured.value.code == "invalid_configuration"


def test_migration_preserves_previous_effective_macos_values() -> None:
    effective = resolve_effective_config(
        load_application_config(APPLICATION_PATH),
        load_deployment_profile(PROFILE_PATH),
        project_root=PROJECT_ROOT,
        environment={},
    )

    assert effective.selected_model == "main.qwen3-4b-q4-k-m"
    assert effective.model_root == (PROJECT_ROOT / "models").resolve()
    assert (
        effective.load.model_dump()
        == ModelLoadConfig(
            context_size=8192,
            batch_size=256,
            micro_batch_size=256,
            threads=6,
            threads_batch=6,
            gpu_layers=-1,
            use_mmap=True,
            use_mlock=False,
            verbose_backend=False,
            verify_artifact_hash=True,
        ).model_dump()
    )
    assert effective.generation.max_new_tokens == 2048
    assert effective.generation.temperature == 0.7
    assert effective.generation.top_p == 0.8
    assert effective.generation.thinking_mode is ThinkingMode.DISABLED
    assert effective.response.language is ResponseLanguage.JA
    assert effective.response.source is ResponseLanguageSource.APPLICATION
    assert effective.application_schema_version == "3"
    assert effective.summarization.mode is SummaryMode.OFF
    assert effective.summarization.max_new_tokens == 1024
    assert effective.presentation.visibility is ThinkingVisibility.HIDDEN
    assert effective.presentation.display_label == DEFAULT_THINKING_DISPLAY_LABEL
    assert effective.presentation.persistence is ThinkingPersistence.DISABLED
    assert effective.presentation.visibility_source is ThinkingPresentationSource.APPLICATION


def test_thinking_presentation_uses_field_specific_precedence_and_sources() -> None:
    built_in = resolve_thinking_presentation_policy(
        application_policy=None,
        environment={},
        explicit_visibility=None,
        explicit_display_label=None,
    )
    application = resolve_thinking_presentation_policy(
        application_policy=ThinkingPresentationConfig(
            visibility=ThinkingVisibility.VISIBLE,
            display_label="Application推論",
        ),
        environment={},
        explicit_visibility=None,
        explicit_display_label=None,
    )
    environment = resolve_thinking_presentation_policy(
        application_policy=ThinkingPresentationConfig(),
        environment={
            "MARGPA_THINKING_VISIBILITY": "visible",
            "MARGPA_THINKING_LABEL": "Environment推論",
            "MARGPA_THINKING_PERSISTENCE": "enabled",
        },
        explicit_visibility=None,
        explicit_display_label=None,
    )
    explicit = resolve_thinking_presentation_policy(
        application_policy=ThinkingPresentationConfig(),
        environment={
            "MARGPA_THINKING_VISIBILITY": "visible",
            "MARGPA_THINKING_LABEL": "Environment推論",
        },
        explicit_visibility=ThinkingVisibility.HIDDEN,
        explicit_display_label="Explicit推論",
    )

    assert built_in.visibility_source is ThinkingPresentationSource.BUILT_IN_DEFAULT
    assert built_in.display_label == DEFAULT_THINKING_DISPLAY_LABEL
    assert application.visibility_source is ThinkingPresentationSource.APPLICATION
    assert application.display_label == "Application推論"
    assert environment.visibility is ThinkingVisibility.VISIBLE
    assert environment.visibility_source is ThinkingPresentationSource.ENVIRONMENT
    assert environment.display_label_source is ThinkingPresentationSource.ENVIRONMENT
    assert environment.persistence is ThinkingPersistence.DISABLED
    assert environment.persistence_source is ThinkingPresentationSource.APPLICATION
    assert explicit.visibility is ThinkingVisibility.HIDDEN
    assert explicit.visibility_source is ThinkingPresentationSource.EXPLICIT
    assert explicit.display_label == "Explicit推論"
    assert explicit.display_label_source is ThinkingPresentationSource.EXPLICIT
    assert explicit.persistence is ThinkingPersistence.DISABLED
    assert explicit.persistence_source is ThinkingPresentationSource.APPLICATION


def test_invalid_presentation_environment_and_explicit_values_are_safe_errors() -> None:
    with pytest.raises(InferenceError) as environment_error:
        resolve_thinking_presentation_policy(
            application_policy=ThinkingPresentationConfig(),
            environment={"MARGPA_THINKING_VISIBILITY": "sometimes"},
            explicit_visibility=None,
            explicit_display_label=None,
        )
    assert environment_error.value.code == "invalid_configuration"

    with pytest.raises(InferenceError) as explicit_error:
        resolve_thinking_presentation_policy(
            application_policy=ThinkingPresentationConfig(),
            environment={},
            explicit_visibility=None,
            explicit_display_label="<unsafe>",
        )
    assert explicit_error.value.code == "invalid_request"


def test_invalid_registry_is_mapped_to_safe_definition_error(tmp_path: Path) -> None:
    registry_path = tmp_path / "invalid.toml"
    registry_path.write_text('model_key = "bad"\nunknown = true\n', encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_model_definition(registry_path)

    assert captured.value.code == "invalid_model_definition"
    assert str(tmp_path) not in captured.value.safe_message


def test_old_model_definition_schema_is_not_silently_accepted(tmp_path: Path) -> None:
    registry_path = tmp_path / "old-model-definition.toml"
    fixture = REGISTRY_PATH.read_text(encoding="utf-8").replace(
        'schema_version = "2"',
        'schema_version = "1"',
        1,
    )
    registry_path.write_text(fixture, encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_model_definition(registry_path)

    assert captured.value.code == "invalid_model_definition"


def test_model_definition_loader_rejects_invalid_protocol_safely(tmp_path: Path) -> None:
    registry_path = tmp_path / "invalid-protocol.toml"
    fixture = REGISTRY_PATH.read_text(encoding="utf-8").replace(
        'closing_delimiter = "</think>"',
        'closing_delimiter = "<think>"',
        1,
    )
    registry_path.write_text(fixture, encoding="utf-8")

    with pytest.raises(InferenceError) as captured:
        load_model_definition(registry_path)

    assert captured.value.code == "invalid_model_definition"
    assert str(tmp_path) not in captured.value.safe_message
