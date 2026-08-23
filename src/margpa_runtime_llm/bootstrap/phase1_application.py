"""Phase 1 composition root for the selected deployment profile."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType

from margpa_runtime_llm.adapters.model_backends.llama_cpp.adapter import LlamaCppModelAdapter
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.contracts.runtime import (
    HostPlatformDefinition,
    RuntimeObservation,
)
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility

from .config_loader import (
    EffectivePhase1Config,
    load_application_config,
    load_deployment_profile,
    resolve_effective_config,
)
from .model_registry_loader import load_model_definition
from .output_parser_registry import build_output_parser
from .profile_resolver import (
    build_runtime_observation,
    load_platform_registry,
    resolve_profile_path,
    validate_deployment_runtime,
    validate_preload_deployment,
)

DEFAULT_PLATFORM_REGISTRY = Path("config/platforms/platform_registry.toml")
DEFAULT_APPLICATION_CONFIG = Path("config/application.toml")


@dataclass(slots=True)
class Phase1Application:
    service: InferenceService
    definition: ModelDefinition
    config: EffectivePhase1Config
    runtime_observation: RuntimeObservation
    presentation_service: ThinkingPresentationService
    adapter: LlamaCppModelAdapter

    def close(self) -> None:
        self.service.unload()

    def __enter__(self) -> Phase1Application:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()


def build_phase1_application(
    *,
    project_root: Path,
    profile_path: Path | None,
    registry_path: Path,
    application_config_path: Path | None = None,
    environment: Mapping[str, str] | None = None,
    cli_model_root: Path | None = None,
    cli_model_key: str | None = None,
    generation_overrides: Mapping[str, object] | None = None,
    load_overrides: Mapping[str, object] | None = None,
    response_language: ResponseLanguage | str | None = None,
    thinking_visibility: ThinkingVisibility | str | None = None,
    thinking_label: str | None = None,
) -> Phase1Application:
    application_path = application_config_path or DEFAULT_APPLICATION_CONFIG
    if not application_path.is_absolute():
        application_path = project_root / application_path
    application = load_application_config(application_path)
    platform_registry = load_platform_registry(project_root / DEFAULT_PLATFORM_REGISTRY)
    profile_resolution = resolve_profile_path(
        project_root=project_root,
        explicit_path=profile_path,
        environment=environment,
        registry=platform_registry,
    )
    profile = load_deployment_profile(profile_resolution.path)
    effective_config = resolve_effective_config(
        application,
        profile,
        project_root=project_root,
        environment=environment,
        cli_model_root=cli_model_root,
        cli_model_key=cli_model_key,
        generation_overrides=generation_overrides,
        load_overrides=load_overrides,
        response_language=response_language,
        thinking_visibility=thinking_visibility,
        thinking_label=thinking_label,
        profile_resolution_source=profile_resolution.source,
    )
    definition = load_model_definition(registry_path)
    presentation_service = ThinkingPresentationService(
        build_output_parser(definition.output_protocol.thinking)
    )
    if definition.model_key != effective_config.selected_model:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The selected model does not match the supplied registry definition.",
            model_key=effective_config.selected_model,
        )
    if effective_config.load.context_size > definition.model.native_context_limit:
        raise InferenceError(
            code=InferenceErrorCode.INVALID_CONFIGURATION,
            safe_message="The effective context size exceeds the model native limit.",
            model_key=effective_config.selected_model,
        )
    validate_preload_deployment(
        expected_host=effective_config.host,
        detected_host=profile_resolution.detected_host,
        requirements=effective_config.runtime_requirements,
        deployment_backend=effective_config.backend_runtime,
        model_backend=definition.backend,
        model_key=effective_config.selected_model,
    )

    adapter = LlamaCppModelAdapter(model_root=effective_config.model_root)
    service = InferenceService(adapter)
    service.load(definition, effective_config.load)
    runtime_observation = validate_loaded_deployment(
        service=service,
        config=effective_config,
        detected_host=profile_resolution.detected_host,
    )
    return Phase1Application(
        service=service,
        definition=definition,
        config=effective_config,
        runtime_observation=runtime_observation,
        presentation_service=presentation_service,
        adapter=adapter,
    )


def validate_loaded_deployment(
    *,
    service: InferenceService,
    config: EffectivePhase1Config,
    detected_host: HostPlatformDefinition,
) -> RuntimeObservation:
    runtime_info = service.runtime_info
    if runtime_info is None:
        raise InferenceError(
            code=InferenceErrorCode.MODEL_NOT_LOADED,
            safe_message="The model runtime information is unavailable.",
            model_key=config.selected_model,
        )
    observation = build_runtime_observation(
        host=detected_host,
        backend=config.backend_runtime,
        runtime_info=runtime_info,
    )
    try:
        validate_deployment_runtime(
            compute=config.compute,
            backend=config.backend_runtime,
            requirements=config.runtime_requirements,
            observation=observation,
            model_key=config.selected_model,
        )
    except InferenceError:
        service.unload()
        raise
    return observation
