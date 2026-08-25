from margpa_runtime_llm.adapters.runtime_model_control.llama_cpp_backend import (
    LlamaCppRuntimeModelBackend,
)
from margpa_runtime_llm.modules.inference.contracts.messages import MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    GpuOffloadEvidence,
    ModelCapabilities,
    ModelDigest,
    ModelLoadConfig,
    ModelRuntimeInfo,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import CapabilityFeature
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition

from .conftest import make_model_definition

_ARTIFACT_DIGEST_VALUE = "d" * 128


class _FakeLlamaCppModelAdapter:
    """Stands in for the real LlamaCppModelAdapter (no real llama_cpp.Llama construction)."""

    def __init__(self) -> None:
        self.load_calls: list[tuple[str, int]] = []
        self.unload_calls = 0

    def load(self, definition: ModelDefinition, config: ModelLoadConfig) -> ModelRuntimeInfo:
        self.load_calls.append((definition.model_key, config.context_size))
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
            loaded_context_size=config.context_size,
            effective_capabilities=ModelCapabilities(
                features=frozenset({CapabilityFeature.CHAT}),
                native_context_limit=definition.model.native_context_limit,
                loaded_context_size=config.context_size,
                supported_message_roles=frozenset({MessageRole.USER, MessageRole.ASSISTANT}),
            ),
            chat_template_source=definition.model.chat_template_source,
            chat_template_digest=ModelDigest(value=_ARTIFACT_DIGEST_VALUE),
            device="cpu",
            device_kind="cpu",
            acceleration_api="none",
            gpu_offload=False,
            gpu_offload_evidence=GpuOffloadEvidence(
                supported=False,
                requested=False,
                observed=False,
                observation_source="not_requested",
            ),
        )

    def unload(self) -> None:
        self.unload_calls += 1


def _backend(*, fake_adapter: _FakeLlamaCppModelAdapter) -> LlamaCppRuntimeModelBackend:
    return LlamaCppRuntimeModelBackend(
        adapter=fake_adapter,  # type: ignore[arg-type]
        base_load_config=ModelLoadConfig(context_size=4096),
    )


def test_probe_capability_reports_declared_limits_without_loading() -> None:
    fake_adapter = _FakeLlamaCppModelAdapter()
    backend = _backend(fake_adapter=fake_adapter)
    definition = make_model_definition(model_key="main.qwen3-4b-q4-k-m", native_context_limit=8192)

    result = backend.probe_capability(definition=definition)

    assert result.native_context_limit == 8192
    assert result.deployment_verified_context_limit == 4096  # min(8192, base 4096)
    assert result.backend_context_limit == 8192
    assert result.effective_context_limit == 4096
    assert result.context_limit_reason_code == "deployment_hardware_verified_limit"
    assert result.max_output_token_limit == 4095
    assert fake_adapter.load_calls == []


def test_load_overrides_context_size_and_reports_measured_capability() -> None:
    fake_adapter = _FakeLlamaCppModelAdapter()
    backend = _backend(fake_adapter=fake_adapter)
    definition = make_model_definition(model_key="main.qwen3-4b-q4-k-m", native_context_limit=8192)

    handle = backend.load(definition=definition, context_size=8192)

    assert fake_adapter.load_calls == [("main.qwen3-4b-q4-k-m", 8192)]
    assert handle.loaded_context_size == 8192
    assert handle.artifact_digest == _ARTIFACT_DIGEST_VALUE
    assert handle.backend_identity == "llama_cpp:0.3.34"
    # A direct adapter Load can allocate a size above the tracked profile,
    # but it must not promote that one allocation into Deployment Evidence.
    # RuntimeModelController prevents such a request before Unload/Load.
    assert handle.capability.deployment_verified_context_limit == 4096


def test_unload_delegates_to_the_wrapped_adapter() -> None:
    fake_adapter = _FakeLlamaCppModelAdapter()
    backend = _backend(fake_adapter=fake_adapter)

    backend.unload()

    assert fake_adapter.unload_calls == 1
