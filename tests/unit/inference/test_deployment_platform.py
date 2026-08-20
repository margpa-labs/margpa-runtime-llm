"""Phase 1-C deployment, platform, acceleration, and validation tests."""

from __future__ import annotations

import platform
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

from margpa_runtime_llm.adapters.model_backends.llama_cpp.runtime_detection import (
    NVIDIA_PROCESS_MEMORY_COMMAND,
    NvidiaProcessMemoryObservation,
    detect_llama_cpp_build_variant,
    detect_llama_cpp_device,
    observe_nvidia_process_gpu_memory,
)
from margpa_runtime_llm.bootstrap import phase1_application as phase1_application_module
from margpa_runtime_llm.bootstrap.config_loader import (
    load_application_config,
    load_deployment_profile,
    resolve_effective_config,
)
from margpa_runtime_llm.bootstrap.model_registry_loader import load_model_definition
from margpa_runtime_llm.bootstrap.phase1_application import validate_loaded_deployment
from margpa_runtime_llm.bootstrap.profile_resolver import (
    PlatformAliasDefinition,
    PlatformDefaultDefinition,
    PlatformRegistry,
    build_runtime_observation,
    detect_execution_environment,
    detect_host_platform,
    load_platform_registry,
    normalize_architecture,
    normalize_execution_environment,
    normalize_operating_system,
    resolve_profile_path,
    validate_deployment_runtime,
    validate_preload_deployment,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationRequest,
    GenerationResult,
    GenerationStream,
)
from margpa_runtime_llm.modules.inference.contracts.messages import MessageRole
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    BackendRuntimeDefinition,
    ComputeTargetDefinition,
    DeploymentRequirements,
    FallbackPolicy,
    GpuOffloadEvidence,
    HostPlatformDefinition,
    ModelCapabilities,
    ModelDigest,
    ModelLoadConfig,
    ModelRuntimeInfo,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import (
    MODEL_REQUIRED_CAPABILITIES,
    CapabilityFeature,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.inference.domain.lifecycle import ModelLifecycleState
from margpa_runtime_llm.modules.inference.domain.model_definition import (
    ModelBackendDefinition,
    ModelDefinition,
)
from margpa_runtime_llm.modules.inference.ports.model_port import ModelPort

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROFILE_PATH = PROJECT_ROOT / "config/profiles/local_macos_arm64.toml"
APPLICATION_PATH = PROJECT_ROOT / "config/application.toml"
REGISTRY_PATH = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"
PLATFORM_REGISTRY_PATH = PROJECT_ROOT / "config/platforms/platform_registry.toml"
APPLICATION = load_application_config(APPLICATION_PATH)
PROFILE = load_deployment_profile(PROFILE_PATH)
DEFINITION = load_model_definition(REGISTRY_PATH)
PLATFORM_REGISTRY = load_platform_registry(PLATFORM_REGISTRY_PATH)


def make_runtime_info(
    *,
    features: frozenset[CapabilityFeature],
    device_kind: str = "gpu",
    acceleration_api: str = "metal",
    gpu_offload: bool = True,
) -> ModelRuntimeInfo:
    return ModelRuntimeInfo(
        load_instance_id="load-phase1c",
        model_key=DEFINITION.model_key,
        backend_key="llama_cpp",
        backend_version="0.3.34",
        model_architecture="qwen3",
        format="gguf",
        quantization="Q4_K_M",
        artifact_size_bytes=DEFINITION.artifact.size_bytes,
        artifact_digest=ModelDigest(value=DEFINITION.artifact.sha512),
        definition_file_sha512=DEFINITION.definition_file_sha512,
        loaded_context_size=4096,
        effective_capabilities=ModelCapabilities(
            features=features,
            native_context_limit=32768,
            loaded_context_size=4096,
            supported_message_roles=frozenset(
                {MessageRole.SYSTEM, MessageRole.USER, MessageRole.ASSISTANT}
            ),
        ),
        chat_template_source="gguf_metadata",
        chat_template_digest=ModelDigest(value="a" * 128),
        device=acceleration_api,
        device_kind=device_kind,
        acceleration_api=acceleration_api,
        gpu_offload=gpu_offload,
        gpu_offload_evidence=GpuOffloadEvidence(
            supported=gpu_offload,
            requested=gpu_offload,
            observed=gpu_offload,
            observation_source=("metal_model_load" if gpu_offload else "not_requested"),
        ),
    )


class LoadedRuntimePort:
    def __init__(self, runtime_info: ModelRuntimeInfo) -> None:
        self._state = ModelLifecycleState.LOADED
        self._runtime_info: ModelRuntimeInfo | None = runtime_info

    @property
    def state(self) -> ModelLifecycleState:
        return self._state

    @property
    def runtime_info(self) -> ModelRuntimeInfo | None:
        return self._runtime_info

    def load(self, definition: ModelDefinition, config: ModelLoadConfig) -> ModelRuntimeInfo:
        assert self._runtime_info is not None
        return self._runtime_info

    def unload(self) -> None:
        self._runtime_info = None
        self._state = ModelLifecycleState.UNLOADED

    def capabilities(self) -> ModelCapabilities:
        assert self._runtime_info is not None
        return self._runtime_info.effective_capabilities

    def generate(self, request: GenerationRequest) -> GenerationResult:
        raise AssertionError("generation is not used by this deployment test")

    def stream(self, request: GenerationRequest) -> GenerationStream:
        raise AssertionError("streaming is not used by this deployment test")


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [("Darwin", "macos"), ("Windows", "windows"), ("Linux", "linux")],
)
def test_operating_system_normalization(raw_value: str, expected: str) -> None:
    assert normalize_operating_system(raw_value, PLATFORM_REGISTRY) == expected


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [("arm64", "arm64"), ("aarch64", "arm64"), ("AMD64", "x86_64"), ("x86_64", "x86_64")],
)
def test_architecture_normalization(raw_value: str, expected: str) -> None:
    assert normalize_architecture(raw_value, PLATFORM_REGISTRY) == expected


@pytest.mark.parametrize(
    ("normalizer", "raw_value"),
    [(normalize_operating_system, "Plan9"), (normalize_architecture, "mips2371")],
)
def test_unknown_platform_values_are_not_guessed(
    normalizer: Callable[[str, PlatformRegistry], str], raw_value: str
) -> None:
    with pytest.raises(InferenceError) as captured:
        normalizer(raw_value, PLATFORM_REGISTRY)

    assert captured.value.code is InferenceErrorCode.UNSUPPORTED_PLATFORM


def test_profile_resolution_priority_is_explicit_then_environment_then_default() -> None:
    registry = PLATFORM_REGISTRY.model_copy(
        update={
            "profile_defaults": (
                PlatformDefaultDefinition(
                    operating_system_key="macos",
                    architecture_key="arm64",
                    execution_environment_key="native",
                    profile_path=Path("config/profiles/default.toml"),
                ),
            )
        }
    )
    explicit = resolve_profile_path(
        project_root=PROJECT_ROOT,
        explicit_path=Path("config/profiles/explicit.toml"),
        environment={"MARGPA_PROFILE": "config/profiles/environment.toml"},
        registry=registry,
        raw_system="Darwin",
        raw_machine="arm64",
        raw_execution_environment="native",
    )
    environment = resolve_profile_path(
        project_root=PROJECT_ROOT,
        explicit_path=None,
        environment={"MARGPA_PROFILE": "config/profiles/environment.toml"},
        registry=registry,
        raw_system="Darwin",
        raw_machine="arm64",
        raw_execution_environment="native",
    )
    platform_default = resolve_profile_path(
        project_root=PROJECT_ROOT,
        explicit_path=None,
        environment={},
        registry=registry,
        raw_system="Darwin",
        raw_machine="arm64",
        raw_execution_environment="native",
    )

    assert explicit.source == "explicit"
    assert explicit.path == (PROJECT_ROOT / "config/profiles/explicit.toml").resolve()
    assert environment.source == "environment"
    assert environment.path == (PROJECT_ROOT / "config/profiles/environment.toml").resolve()
    assert platform_default.source == "platform_default"
    assert platform_default.path == (PROJECT_ROOT / "config/profiles/default.toml").resolve()


def test_supported_host_without_default_requires_explicit_profile() -> None:
    with pytest.raises(InferenceError) as captured:
        resolve_profile_path(
            project_root=PROJECT_ROOT,
            explicit_path=None,
            environment={},
            registry=PLATFORM_REGISTRY,
            raw_system="Windows",
            raw_machine="AMD64",
        )

    assert captured.value.code is InferenceErrorCode.PROFILE_REQUIRED


def test_future_platform_alias_and_default_are_registry_only_extensions() -> None:
    registry = PlatformRegistry(
        execution_environment_keys=frozenset({"native"}),
        operating_system_aliases=(
            PlatformAliasDefinition(raw_value="FutureOS 2371", canonical_key="futureos"),
        ),
        architecture_aliases=(
            PlatformAliasDefinition(raw_value="FutureArch 2371", canonical_key="futurearch"),
        ),
        profile_defaults=(
            PlatformDefaultDefinition(
                operating_system_key="futureos",
                architecture_key="futurearch",
                execution_environment_key="native",
                profile_path=Path("config/profiles/future.toml"),
            ),
        ),
    )

    resolution = resolve_profile_path(
        project_root=PROJECT_ROOT,
        explicit_path=None,
        environment={},
        registry=registry,
        raw_system="FutureOS 2371",
        raw_machine="FutureArch 2371",
        raw_execution_environment="native",
    )

    assert resolution.detected_host.operating_system_key == "futureos"
    assert resolution.detected_host.architecture_key == "futurearch"
    assert resolution.path == (PROJECT_ROOT / "config/profiles/future.toml").resolve()


def test_execution_environment_detector_distinguishes_native_and_container() -> None:
    def no_marker(path: Path) -> bool:
        del path
        return False

    def docker_marker(path: Path) -> bool:
        return path == Path("/.dockerenv")

    assert (
        detect_execution_environment(
            registry=PLATFORM_REGISTRY,
            environment={},
            marker_path_exists=no_marker,
            cgroup_text="0::/user.slice",
        )
        == "native"
    )
    assert (
        detect_execution_environment(
            registry=PLATFORM_REGISTRY,
            environment={},
            marker_path_exists=docker_marker,
            cgroup_text="",
        )
        == "container"
    )
    assert (
        detect_execution_environment(
            registry=PLATFORM_REGISTRY,
            environment={},
            marker_path_exists=no_marker,
            cgroup_text="0::/docker/phase1f",
        )
        == "container"
    )
    assert normalize_execution_environment("Container", PLATFORM_REGISTRY) == "container"


def test_linux_container_host_evidence_includes_distribution() -> None:
    detected = detect_host_platform(
        registry=PLATFORM_REGISTRY,
        raw_system="Linux",
        raw_machine="x86_64",
        raw_execution_environment="container",
        raw_distribution="Ubuntu",
        environment={},
    )

    assert detected == HostPlatformDefinition(
        operating_system_key="linux",
        architecture_key="x86_64",
        execution_environment_key="container",
        distribution_key="ubuntu",
    )


def test_profile_host_mismatch_is_rejected_before_model_port_load(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter_constructed = False
    load_calls = 0

    class RecordingAdapter:
        def __init__(self, *, model_root: Path) -> None:
            nonlocal adapter_constructed
            adapter_constructed = True

        def load(self, definition: ModelDefinition, config: ModelLoadConfig) -> ModelRuntimeInfo:
            nonlocal load_calls
            load_calls += 1
            raise AssertionError("load must not be called for a mismatched host")

    monkeypatch.setattr(platform, "system", lambda: "Windows")
    monkeypatch.setattr(platform, "machine", lambda: "AMD64")
    monkeypatch.setattr(phase1_application_module, "LlamaCppModelAdapter", RecordingAdapter)

    with pytest.raises(InferenceError) as captured:
        phase1_application_module.build_phase1_application(
            project_root=PROJECT_ROOT,
            profile_path=PROFILE_PATH,
            registry_path=REGISTRY_PATH,
            environment={},
        )

    assert captured.value.code is InferenceErrorCode.UNSUPPORTED_PLATFORM
    assert not adapter_constructed
    assert load_calls == 0


def test_context_limit_is_rejected_before_native_adapter_construction(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    adapter_constructed = False
    application_path = tmp_path / "oversized-context.toml"
    application_path.write_text(
        APPLICATION_PATH.read_text(encoding="utf-8").replace(
            "context_size = 4096",
            "context_size = 40000",
            1,
        ),
        encoding="utf-8",
    )
    # The deployment profile's own [load_overrides] context_size takes precedence
    # over the application default, so it must also be pushed past the native
    # context limit for this scenario to exercise the oversized-context path.
    profile_path = tmp_path / "oversized-context-profile.toml"
    profile_path.write_text(
        PROFILE_PATH.read_text(encoding="utf-8").replace(
            "context_size = 8192",
            "context_size = 40000",
            1,
        ),
        encoding="utf-8",
    )

    class RecordingAdapter:
        def __init__(self, *, model_root: Path) -> None:
            nonlocal adapter_constructed
            adapter_constructed = True

    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    monkeypatch.setattr(platform, "machine", lambda: "arm64")
    monkeypatch.setattr(phase1_application_module, "LlamaCppModelAdapter", RecordingAdapter)

    with pytest.raises(InferenceError) as captured:
        phase1_application_module.build_phase1_application(
            project_root=PROJECT_ROOT,
            application_config_path=application_path,
            profile_path=profile_path,
            registry_path=REGISTRY_PATH,
            environment={},
        )

    assert captured.value.code is InferenceErrorCode.INVALID_CONFIGURATION
    assert not adapter_constructed


def test_unknown_output_parser_is_rejected_before_native_adapter_construction(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    adapter_constructed = False
    registry_path = tmp_path / "unknown-parser.toml"
    registry_path.write_text(
        REGISTRY_PATH.read_text(encoding="utf-8").replace(
            'parser_key = "tagged_thinking_v1"',
            'parser_key = "future_parser_v1"',
            1,
        ),
        encoding="utf-8",
    )

    class RecordingAdapter:
        def __init__(self, *, model_root: Path) -> None:
            nonlocal adapter_constructed
            adapter_constructed = True

    monkeypatch.setattr(platform, "system", lambda: "Darwin")
    monkeypatch.setattr(platform, "machine", lambda: "arm64")
    monkeypatch.setattr(phase1_application_module, "LlamaCppModelAdapter", RecordingAdapter)

    with pytest.raises(InferenceError) as captured:
        phase1_application_module.build_phase1_application(
            project_root=PROJECT_ROOT,
            profile_path=PROFILE_PATH,
            registry_path=registry_path,
            environment={},
        )

    assert captured.value.code is InferenceErrorCode.INVALID_MODEL_DEFINITION
    assert not adapter_constructed


def test_unimplemented_fallback_policy_is_rejected_before_load() -> None:
    with pytest.raises(InferenceError) as captured:
        validate_preload_deployment(
            expected_host=PROFILE.host,
            detected_host=PROFILE.host,
            requirements=DeploymentRequirements(fallback_policy=FallbackPolicy.WARN),
            deployment_backend=PROFILE.backend_runtime,
            model_backend=DEFINITION.backend,
            model_key=DEFINITION.model_key,
        )

    assert captured.value.code is InferenceErrorCode.INVALID_CONFIGURATION


def test_profile_and_model_backend_mismatch_is_rejected_before_load() -> None:
    with pytest.raises(InferenceError) as captured:
        validate_preload_deployment(
            expected_host=PROFILE.host,
            detected_host=PROFILE.host,
            requirements=PROFILE.runtime_requirements,
            deployment_backend=PROFILE.backend_runtime,
            model_backend=ModelBackendDefinition(
                backend_key="future_backend",
                required_version="2371",
            ),
            model_key=DEFINITION.model_key,
        )

    assert captured.value.code is InferenceErrorCode.INVALID_CONFIGURATION


def test_profile_distribution_mismatch_is_rejected_before_load() -> None:
    expected = HostPlatformDefinition(
        operating_system_key="linux",
        architecture_key="x86_64",
        execution_environment_key="container",
        distribution_key="ubuntu",
    )
    detected = expected.model_copy(update={"distribution_key": "debian"})

    with pytest.raises(InferenceError) as captured:
        validate_preload_deployment(
            expected_host=expected,
            detected_host=detected,
            requirements=DeploymentRequirements(),
            deployment_backend=PROFILE.backend_runtime,
            model_backend=DEFINITION.backend,
            model_key=DEFINITION.model_key,
        )

    assert captured.value.code is InferenceErrorCode.UNSUPPORTED_PLATFORM


def test_extensible_vendor_and_acceleration_keys_are_preserved() -> None:
    compute = ComputeTargetDefinition(
        compute_kind_key="npu",
        vendor_key="future_vendor_2371",
        acceleration_api_key="future_acceleration_2371",
        device_selector="auto",
        offload_policy_key="profile_defined",
    )

    assert compute.vendor_key == "future_vendor_2371"
    assert compute.acceleration_api_key == "future_acceleration_2371"


def test_mac_profile_requires_gpu_offload_but_model_definition_does_not() -> None:
    assert PROFILE.runtime_requirements.required_capabilities == {CapabilityFeature.GPU_OFFLOAD}
    assert CapabilityFeature.GPU_OFFLOAD not in DEFINITION.capabilities.required_features
    assert CapabilityFeature.GPU_OFFLOAD in DEFINITION.capabilities.optional_features


def test_cpu_deployment_contract_does_not_require_gpu_offload() -> None:
    host = HostPlatformDefinition(
        operating_system_key="windows",
        architecture_key="x86_64",
        execution_environment_key="native",
    )
    compute = ComputeTargetDefinition(
        compute_kind_key="cpu",
        acceleration_api_key="cpu_native",
        device_selector="auto",
        offload_policy_key="disabled",
    )
    backend = BackendRuntimeDefinition(
        backend_key="llama_cpp",
        required_version="0.3.34",
        build_variant_key="cpu",
        execution_mode_key="in_process",
    )
    observation = build_runtime_observation(
        host=host,
        backend=backend,
        runtime_info=make_runtime_info(
            features=MODEL_REQUIRED_CAPABILITIES,
            device_kind="cpu",
            acceleration_api="cpu_native",
            gpu_offload=False,
        ),
    )

    validate_deployment_runtime(
        compute=compute,
        backend=backend,
        requirements=DeploymentRequirements(),
        observation=observation,
        model_key=DEFINITION.model_key,
    )

    assert not observation.detected.gpu_offload
    assert observation.executed is None


def test_load_observation_does_not_claim_request_execution() -> None:
    runtime_info = make_runtime_info(
        features=MODEL_REQUIRED_CAPABILITIES | {CapabilityFeature.GPU_OFFLOAD}
    )

    observation = build_runtime_observation(
        host=PROFILE.host,
        backend=PROFILE.backend_runtime,
        runtime_info=runtime_info,
    )

    assert observation.detected.device_kind_key == "gpu"
    assert observation.detected.acceleration_api_key == "metal"
    assert observation.detected.gpu_offload
    assert observation.executed is None


def test_observed_build_variant_is_validated_against_profile() -> None:
    runtime_info = make_runtime_info(
        features=MODEL_REQUIRED_CAPABILITIES | {CapabilityFeature.GPU_OFFLOAD}
    ).model_copy(update={"backend_build_variant": "cuda"})
    observation = build_runtime_observation(
        host=PROFILE.host,
        backend=PROFILE.backend_runtime,
        runtime_info=runtime_info,
    )

    assert observation.detected.build_variant_source == "observed"
    assert not observation.observation_warnings
    with pytest.raises(InferenceError) as captured:
        validate_deployment_runtime(
            compute=PROFILE.compute,
            backend=PROFILE.backend_runtime,
            requirements=PROFILE.runtime_requirements,
            observation=observation,
            model_key=DEFINITION.model_key,
        )
    assert captured.value.details["field"] == "backend_build_variant"


def test_mac_deployment_capability_failure_unloads_runtime() -> None:
    runtime_info = make_runtime_info(features=MODEL_REQUIRED_CAPABILITIES)
    port = LoadedRuntimePort(runtime_info)
    service = InferenceService(cast(ModelPort, port))
    config = resolve_effective_config(
        APPLICATION,
        PROFILE,
        project_root=PROJECT_ROOT,
        environment={},
    )

    with pytest.raises(InferenceError) as captured:
        validate_loaded_deployment(service=service, config=config, detected_host=PROFILE.host)

    assert captured.value.code is InferenceErrorCode.UNSUPPORTED_CAPABILITY
    assert port.state is ModelLifecycleState.UNLOADED
    assert service.runtime_info is None


def test_llama_cpp_device_detector_separates_metal_and_cpu_execution() -> None:
    metal = detect_llama_cpp_device(
        system_info="MTL : EMBED_LIBRARY = 1",
        gpu_offload_supported=True,
        gpu_layers=-1,
    )
    cpu = detect_llama_cpp_device(
        system_info="MTL : EMBED_LIBRARY = 1",
        gpu_offload_supported=True,
        gpu_layers=0,
    )

    assert metal.device_kind == "gpu"
    assert metal.acceleration_api == "metal"
    assert metal.gpu_offload
    assert cpu.device_kind == "cpu"
    assert cpu.acceleration_api == "cpu_native"
    assert not cpu.gpu_offload


def test_llama_cpp_device_detector_separates_cuda_build_and_cpu_mode() -> None:
    cuda = detect_llama_cpp_device(
        system_info="AVX = 1 | GGML_CUDA = 1 | CUDA : ARCHS = 750",
        gpu_offload_supported=True,
        gpu_layers=-1,
        nvidia_process_memory=NvidiaProcessMemoryObservation(
            query_available=True,
            process_gpu_memory_bytes=512 * 1024 * 1024,
        ),
    )
    cpu_on_cuda = detect_llama_cpp_device(
        system_info="AVX = 1 | GGML_CUDA = 1 | CUDA : ARCHS = 750",
        gpu_offload_supported=True,
        gpu_layers=0,
    )

    assert (
        detect_llama_cpp_build_variant(
            system_info="GGML_CUDA = 1",
            gpu_offload_supported=True,
        )
        == "cuda"
    )
    assert cuda.build_variant == "cuda"
    assert cuda.device_kind == "gpu"
    assert cuda.acceleration_api == "cuda"
    assert cuda.gpu_offload
    assert cuda.observation_source == "nvidia_process_memory"
    assert cuda.process_gpu_memory_bytes == 512 * 1024 * 1024
    assert cpu_on_cuda.build_variant == "cuda"
    assert cpu_on_cuda.device_kind == "cpu"
    assert cpu_on_cuda.acceleration_api == "cpu_native"
    assert not cpu_on_cuda.gpu_offload


def test_llama_cpp_device_detector_reports_pure_cpu_without_acceleration() -> None:
    pure_cpu = detect_llama_cpp_device(
        system_info="AVX = 1 | AVX2 = 1",
        gpu_offload_supported=False,
        gpu_layers=0,
    )

    assert pure_cpu.build_variant == "cpu"
    assert pure_cpu.device == "cpu"
    assert pure_cpu.device_kind == "cpu"
    assert pure_cpu.acceleration_api == "none"
    assert pure_cpu.gpu_offload is False
    assert pure_cpu.gpu_offload_supported is False
    assert pure_cpu.gpu_offload_requested is False
    assert pure_cpu.observation_source == "not_requested"


def test_cuda_device_detector_fails_closed_without_process_memory_evidence() -> None:
    cuda = detect_llama_cpp_device(
        system_info="GGML_CUDA = 1",
        gpu_offload_supported=True,
        gpu_layers=-1,
    )

    assert cuda.build_variant == "cuda"
    assert cuda.gpu_offload_supported
    assert cuda.gpu_offload_requested
    assert not cuda.gpu_offload
    assert cuda.device_kind == "unknown"
    assert cuda.observation_source == "observation_unavailable"


def test_nvidia_process_memory_observation_is_scoped_to_current_process() -> None:
    completed = subprocess.CompletedProcess(
        args=NVIDIA_PROCESS_MEMORY_COMMAND,
        returncode=0,
        stdout="2371, 128\n99, 4096\n2371, 256\n",
        stderr="",
    )

    def run_command(command: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
        assert command == NVIDIA_PROCESS_MEMORY_COMMAND
        return completed

    observation = observe_nvidia_process_gpu_memory(
        process_id=2371,
        command_runner=run_command,
    )

    assert observation.query_available
    assert observation.process_gpu_memory_bytes == 384 * 1024 * 1024


def test_cuda_profile_rejects_cpu_runtime_instead_of_falling_back() -> None:
    cuda_profile = load_deployment_profile(
        PROJECT_ROOT / "config/profiles/lightning_linux_x86_64_cuda.toml"
    )
    observation = build_runtime_observation(
        host=cuda_profile.host,
        backend=cuda_profile.backend_runtime,
        runtime_info=make_runtime_info(
            features=MODEL_REQUIRED_CAPABILITIES,
            device_kind="cpu",
            acceleration_api="cpu_native",
            gpu_offload=False,
        ),
    )

    with pytest.raises(InferenceError) as captured:
        validate_deployment_runtime(
            compute=cuda_profile.compute,
            backend=cuda_profile.backend_runtime,
            requirements=cuda_profile.runtime_requirements,
            observation=observation,
            model_key=DEFINITION.model_key,
        )

    assert captured.value.code is InferenceErrorCode.UNSUPPORTED_CAPABILITY
