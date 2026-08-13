"""Production composition root for the Phase 1-G web runtime."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path

from margpa_runtime_llm.modules.conversation.adapters import (
    LocalConversationPersistenceSettings,
)
from margpa_runtime_llm.modules.conversation.adapters.persistence_factory import (
    start_local_conversation_persistence,
)
from margpa_runtime_llm.modules.conversation.domain import ConversationStorageError
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DocumentationRagAvailability,
    DocumentationRagMode,
)
from margpa_runtime_llm.modules.documentation_rag.ports import (
    ContextualRagOrchestratorPort,
    RagOrchestratorPort,
)
from margpa_runtime_llm.modules.inference.domain.capabilities import CapabilityFeature
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.web.access_profiles import DocumentationRagEffectiveState
from margpa_runtime_llm.web.contracts import (
    DocumentationRagRuntimeSnapshot,
    RuntimeDefaults,
    SafeRuntimeSnapshot,
    WebRuntime,
)

from .configuration_control import build_configuration_control
from .phase1_application import Phase1Application, build_phase1_application

TextTokenCounter = Callable[[str], int]
TextTokenCounterBinder = Callable[[TextTokenCounter], None]


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
    documentation_rag: RagOrchestratorPort | ContextualRagOrchestratorPort | None = None,
    documentation_rag_availability: DocumentationRagAvailability = (
        DocumentationRagAvailability.UNAVAILABLE
    ),
    documentation_rag_effective_state: DocumentationRagEffectiveState = (
        DocumentationRagEffectiveState.UNAVAILABLE
    ),
    documentation_rag_default_mode: DocumentationRagMode = DocumentationRagMode.DISABLED,
    documentation_rag_provider_display_name: str | None = None,
    documentation_rag_token_counter_binder: TextTokenCounterBinder | None = None,
    conversation_persistence_settings: LocalConversationPersistenceSettings | None = None,
    configuration_control_enabled: bool = False,
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
        if documentation_rag is not None and documentation_rag_token_counter_binder is not None:
            documentation_rag_token_counter_binder(application.service.count_text_tokens)
        conversation = ConversationGenerationService(
            inference=application.service,
            presentation=application.presentation_service,
            model_key=application.config.selected_model,
            generation_defaults=application.config.generation,
            response_language_default=application.config.response.language,
            presentation_default=application.config.presentation,
            summarization=application.config.summarization,
            thinking_control_available=thinking_control_available,
            documentation_rag=documentation_rag,
            documentation_rag_availability=documentation_rag_availability,
            chat_prompt_token_counter=(
                application.service.count_chat_prompt_tokens
                if documentation_rag is not None
                else None
            ),
            effective_context_size=runtime_info.loaded_context_size,
        )
        persistent = None
        if conversation_persistence_settings is not None:
            try:
                composition = start_local_conversation_persistence(
                    conversation_persistence_settings,
                    generation_service=conversation,
                )
            except ConversationStorageError as exc:
                raise InferenceError(
                    code=InferenceErrorCode.INVALID_CONFIGURATION,
                    safe_message="The persistent conversation store could not start safely.",
                ) from exc
            persistent = composition.service
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
                documentation_rag_mode=documentation_rag_default_mode,
            ),
            documentation_rag=DocumentationRagRuntimeSnapshot(
                effective_state=documentation_rag_effective_state,
                control_available=(
                    documentation_rag_availability is DocumentationRagAvailability.AVAILABLE
                ),
                provider_display_name=documentation_rag_provider_display_name,
                default_mode=documentation_rag_default_mode,
            ),
        )
        configuration_control = (
            build_configuration_control(
                effective=application.config,
                documentation_rag_state=documentation_rag_effective_state,
            )
            if configuration_control_enabled
            else None
        )
        return WebRuntime(
            conversation=conversation,
            snapshot=snapshot,
            close_callback=application.close,
            persistent_conversation=persistent,
            configuration_control=configuration_control,
        )
    except BaseException:
        if application is not None:
            application.close()
        raise
