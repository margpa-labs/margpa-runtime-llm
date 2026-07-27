"""Production composition root for the Phase 1-G web runtime."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.inference.domain.capabilities import CapabilityFeature
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.web.contracts import (
    RuntimeDefaults,
    SafeRuntimeSnapshot,
    WebRuntime,
)

from .phase1_application import Phase1Application, build_phase1_application


def build_phase1_web_runtime(
    *,
    project_root: Path,
    profile_path: Path | None,
    registry_path: Path,
    application_config_path: Path | None = None,
    environment: Mapping[str, str] | None = None,
    cli_model_root: Path | None = None,
    cli_model_key: str | None = None,
    load_overrides: Mapping[str, object] | None = None,
) -> WebRuntime:
    application: Phase1Application | None = None
    try:
        application = build_phase1_application(
            project_root=project_root,
            profile_path=profile_path,
            registry_path=registry_path,
            application_config_path=application_config_path,
            environment=environment,
            cli_model_root=cli_model_root,
            cli_model_key=cli_model_key,
            load_overrides=load_overrides,
        )
        runtime_info = application.service.runtime_info
        if runtime_info is None:
            raise InferenceError(
                code=InferenceErrorCode.MODEL_NOT_LOADED,
                safe_message="The model runtime information is unavailable.",
            )
        thinking_control_available = (
            CapabilityFeature.THINKING_CONTROL in runtime_info.effective_capabilities.features
        )
        conversation = ConversationGenerationService(
            inference=application.service,
            presentation=application.presentation_service,
            model_key=application.config.selected_model,
            generation_defaults=application.config.generation,
            response_language_default=application.config.response.language,
            presentation_default=application.config.presentation,
            summarization=application.config.summarization,
            thinking_control_available=thinking_control_available,
        )
        snapshot = SafeRuntimeSnapshot(
            model_key=runtime_info.model_key,
            profile_key=application.config.profile_key,
            device_kind=runtime_info.device_kind,
            acceleration_api=runtime_info.acceleration_api,
            defaults=RuntimeDefaults(
                response_language=application.config.response.language,
                max_new_tokens=application.config.generation.max_new_tokens,
                thinking_mode=application.config.generation.thinking_mode,
                thinking_visibility=application.config.presentation.visibility,
                thinking_display_label=application.config.presentation.display_label,
                thinking_control_available=thinking_control_available,
                summary_mode=application.config.summarization.mode,
            ),
        )
        return WebRuntime(
            conversation=conversation,
            snapshot=snapshot,
            close_callback=application.close,
        )
    except BaseException:
        if application is not None:
            application.close()
        raise
