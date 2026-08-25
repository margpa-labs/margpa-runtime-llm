from dataclasses import dataclass
from pathlib import Path

import pytest

from margpa_runtime_llm.bootstrap.runtime_model_control import build_runtime_model_controller
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.messages import MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    GpuOffloadEvidence,
    ModelCapabilities,
    ModelDigest,
    ModelLoadConfig,
    ModelRuntimeInfo,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import (
    MODEL_REQUIRED_CAPABILITIES,
    CapabilityFeature,
)
from margpa_runtime_llm.modules.inference.domain.errors import InferenceError
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
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    ModelRole,
    RuntimeState,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACT_DIGEST_VALUE = "e" * 128
_SHA512_FILLER = "a" * 128


def make_model_definition(*, model_key: str, native_context_limit: int = 8192) -> ModelDefinition:
    return ModelDefinition(
        model_key=model_key,
        logical_role="main",
        enabled=True,
        source=ModelSourceDefinition(
            provider="huggingface",
            distribution_repository="test-org/test-model",
            upstream_model="test-model",
        ),
        artifact=ModelArtifactDefinition(
            relative_path=Path(f"main/{model_key}/gguf/{model_key}.gguf"),
            file_name=f"{model_key}.gguf",
            format="gguf",
            quantization="Q4_K_M",
            size_bytes=1,
            sha512=_SHA512_FILLER,
        ),
        backend=ModelBackendDefinition(backend_key="llama_cpp", required_version=">=0.3.0"),
        model=ModelMetadataDefinition(
            architecture="test-arch",
            native_context_limit=native_context_limit,
            chat_template_source="embedded",
        ),
        capabilities=ModelExpectedCapabilities(required_features=MODEL_REQUIRED_CAPABILITIES),
        verification=ModelVerificationDefinition(state="verified", provenance_complete=True),
        output_protocol=ModelOutputProtocolDefinition(
            thinking=ThinkingOutputProtocolDefinition(parser_key="plain_text_v1")
        ),
        definition_file_sha512=_SHA512_FILLER,
    )


def _real_runtime_info(*, definition: ModelDefinition, context_size: int) -> ModelRuntimeInfo:
    return ModelRuntimeInfo(
        load_instance_id="instance-1",
        model_key=definition.model_key,
        backend_key="llama_cpp",
        backend_version="0.3.34",
        model_architecture=definition.model.architecture,
        format=definition.artifact.format,
        quantization=definition.artifact.quantization,
        artifact_size_bytes=definition.artifact.size_bytes,
        artifact_digest=ModelDigest(value=_ARTIFACT_DIGEST_VALUE),
        definition_file_sha512=definition.definition_file_sha512,
        loaded_context_size=context_size,
        effective_capabilities=ModelCapabilities(
            features=frozenset({CapabilityFeature.CHAT}),
            native_context_limit=definition.model.native_context_limit,
            loaded_context_size=context_size,
            supported_message_roles=frozenset({MessageRole.USER, MessageRole.ASSISTANT}),
        ),
        chat_template_source=definition.model.chat_template_source,
        chat_template_digest=ModelDigest(value=_ARTIFACT_DIGEST_VALUE),
        device="cpu",
        device_kind="cpu",
        acceleration_api="none",
        gpu_offload=False,
        gpu_offload_evidence=GpuOffloadEvidence(
            supported=False, requested=False, observed=False, observation_source="not_requested"
        ),
    )


@dataclass
class _FakeInferenceService:
    runtime_info: ModelRuntimeInfo | None


@dataclass
class _FakeGeneration:
    max_new_tokens: int = 2048


@dataclass
class _FakeConfig:
    load: ModelLoadConfig
    generation: _FakeGeneration


@dataclass
class _FakeApplication:
    service: _FakeInferenceService
    definition: object
    config: _FakeConfig
    adapter: object = None


def test_builds_a_controller_whose_initial_snapshot_matches_the_loaded_model() -> None:
    definition = make_model_definition(model_key="main.qwen3-4b-q4-k-m", native_context_limit=8192)
    runtime_info = _real_runtime_info(definition=definition, context_size=4096)
    application = _FakeApplication(
        service=_FakeInferenceService(runtime_info=runtime_info),
        definition=definition,
        config=_FakeConfig(load=ModelLoadConfig(context_size=4096), generation=_FakeGeneration()),
        adapter=object(),
    )

    controller = build_runtime_model_controller(
        application=application,  # type: ignore[arg-type]
        model_access_coordinator=ModelAccessCoordinator(),
        project_root=_PROJECT_ROOT,
    )
    snapshot = controller.snapshot()

    assert snapshot.selected_model_key == "main.qwen3-4b-q4-k-m"
    assert snapshot.revision == 0
    assert snapshot.runtime_state is RuntimeState.ACTIVE
    assert snapshot.loaded_context_size == 4096
    assert snapshot.model_native_context_limit == 8192
    assert snapshot.backend_context_limit == 8192
    assert snapshot.deployment_verified_context_limit == 4096
    assert snapshot.effective_context_limit == 4096
    assert snapshot.max_output_token_limit == 4095
    assert snapshot.current_max_new_tokens == 2048
    assert snapshot.role_bindings[0].role is ModelRole.MAIN
    assert snapshot.role_bindings[0].artifact_digest == _ARTIFACT_DIGEST_VALUE


def test_raises_when_the_application_has_no_loaded_runtime_info() -> None:
    definition = make_model_definition(model_key="main.qwen3-4b-q4-k-m")
    application = _FakeApplication(
        service=_FakeInferenceService(runtime_info=None),
        definition=definition,
        config=_FakeConfig(load=ModelLoadConfig(context_size=4096), generation=_FakeGeneration()),
    )

    with pytest.raises(InferenceError):
        build_runtime_model_controller(
            application=application,  # type: ignore[arg-type]
            model_access_coordinator=ModelAccessCoordinator(),
            project_root=_PROJECT_ROOT,
        )
