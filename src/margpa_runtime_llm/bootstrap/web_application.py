"""Production composition root for the Phase 1-G web runtime."""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from pathlib import Path

from margpa_runtime_llm.adapters.runtime_observability.local_filesystem_recording_writer import (
    LocalFilesystemRecordingWriter,
)
from margpa_runtime_llm.modules.conversation.adapters import (
    LocalConversationPersistenceSettings,
)
from margpa_runtime_llm.modules.conversation.adapters.persistence_factory import (
    start_local_conversation_persistence,
)
from margpa_runtime_llm.modules.conversation.adapters.sqlite_conversation_store import (
    scope_directory_key,
)
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    GovernancePostHook,
    GuardrailPostHook,
    RuntimeGenerationSnapshot,
)
from margpa_runtime_llm.modules.conversation.application.persistent_conversation_service import (
    PersistentConversationService,
)
from margpa_runtime_llm.modules.conversation.domain import (
    ConversationStorageError,
    ConversationStorageErrorCode,
)
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DocumentationRagAvailability,
    DocumentationRagMode,
)
from margpa_runtime_llm.modules.documentation_rag.ports import (
    ContextualRagOrchestratorPort,
    RagOrchestratorPort,
)
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationRecommendation
from margpa_runtime_llm.modules.governance_definitions.runtime import (
    GovernanceDefinitionsRuntime,
)
from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.contracts.runtime import ModelRuntimeInfo
from margpa_runtime_llm.modules.inference.domain.cancellation import CancellationToken
from margpa_runtime_llm.modules.inference.domain.capabilities import CapabilityFeature
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.runtime_composition.application import ComponentRegistryService
from margpa_runtime_llm.modules.runtime_composition.contracts import (
    ComponentSideEffectLevel,
    ComponentState,
    build_component_descriptor,
)
from margpa_runtime_llm.modules.runtime_governance.domain import RuntimeCapabilitySnapshot
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.snapshot import RuntimeModelSnapshot
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.web.access_profiles import DocumentationRagEffectiveState
from margpa_runtime_llm.web.contracts import (
    DocumentationRagRuntimeSnapshot,
    RuntimeDefaults,
    SafeRuntimeSnapshot,
    WebRuntime,
)

from .audit_evidence import build_governance_observer
from .configuration_control import build_configuration_control
from .guardrail_governance import GuardrailGovernanceComposition, build_guardrail_hooks
from .judge_live_integration import build_judge_completion_hook
from .phase1_application import Phase1Application, build_phase1_application
from .recording_live_integration import (
    build_judge_evidence_recorder,
    build_recording_completion_hook,
)
from .repair_live_integration import RepairExecutionResult, attempt_live_repair
from .runtime_governance import (
    RuntimeGovernanceComposition,
    build_main_model_governance_hooks,
    default_authority,
    load_reference_descriptors,
)
from .runtime_model_control import build_runtime_model_controller

_logger = logging.getLogger(__name__)

TextTokenCounter = Callable[[str], int]
TextTokenCounterBinder = Callable[[TextTokenCounter], None]

# Conservative Phase 6 default (not yet exposed on any config surface, same
# status as the Judge/Repair Budget constants in judge_live_integration.py):
# per-scope local disk ceiling for Turn-level recordings and Judge Evidence,
# each in its own subdirectory below.
_DEFAULT_RECORDING_MAX_TOTAL_BYTES = 50_000_000


def _register_runtime_components(
    *,
    documentation_rag_effective_state: DocumentationRagEffectiveState,
    persistent_enabled: bool,
    configuration_control_enabled: bool,
) -> ComponentRegistryService:
    """Observe and describe the 3 existing components; grant no new authority.

    This registry does not replace any of the three components' own existing
    Local/Loopback/enable gates — it only projects the state each gate already
    resolved into a common, typed shape (Phase 2-E Runtime Composition
    Switchboard Foundation).
    """

    registry = ComponentRegistryService()
    registry.register(
        build_component_descriptor(
            component_key="documentation_rag",
            kind="feature",
            version="1",
            state=ComponentState(documentation_rag_effective_state.value),
            capabilities=(
                ("retrieval", "citation")
                if documentation_rag_effective_state is DocumentationRagEffectiveState.ENABLED
                else ()
            ),
            degraded_reasons=(
                ()
                if documentation_rag_effective_state
                in (DocumentationRagEffectiveState.ENABLED, DocumentationRagEffectiveState.DISABLED)
                else (documentation_rag_effective_state.value,)
            ),
            side_effect_level=ComponentSideEffectLevel.LOCAL_WRITE,
            restart_required=True,
        )
    )
    conversation_persistence_state = (
        ComponentState.ENABLED if persistent_enabled else ComponentState.DISABLED
    )
    registry.register(
        build_component_descriptor(
            component_key="conversation_persistence",
            kind="persistence",
            version="1",
            state=conversation_persistence_state,
            capabilities=("persistence",) if persistent_enabled else (),
            degraded_reasons=(),
            side_effect_level=ComponentSideEffectLevel.LOCAL_WRITE,
            restart_required=True,
        )
    )
    registry.register(
        build_component_descriptor(
            component_key="configuration_control",
            kind="control-surface",
            version="1",
            state=(
                ComponentState.ENABLED if configuration_control_enabled else ComponentState.DISABLED
            ),
            capabilities=("control",) if configuration_control_enabled else (),
            degraded_reasons=(),
            side_effect_level=ComponentSideEffectLevel.READ_ONLY,
            restart_required=True,
        )
    )
    return registry


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
    runtime_composition_inspection_enabled: bool = False,
    governance_definitions_runtime: GovernanceDefinitionsRuntime | None = None,
    runtime_governance_enabled: bool = False,
    runtime_governance_definitions_root: Path | None = None,
    guardrail_governance_enabled: bool = False,
    runtime_model_control_enabled: bool = False,
    feature_modes_enabled: bool = False,
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
        governance_pre_hook = None
        governance_post_hook = None
        runtime_governance_composition: RuntimeGovernanceComposition | None = None
        if runtime_governance_enabled:
            runtime_governance_capability = RuntimeCapabilitySnapshot(
                model_key=runtime_info.model_key,
                backend_kind=runtime_info.backend_key,
                supports_streaming=True,
                supports_thinking=thinking_control_available,
                max_context_tokens=runtime_info.loaded_context_size,
            )
            loaded_reference_descriptors = load_reference_descriptors(
                definitions_root=runtime_governance_definitions_root,
                capability=runtime_governance_capability,
                authority=default_authority(),
            )
            runtime_governance_composition = RuntimeGovernanceComposition(
                capability=runtime_governance_capability,
                descriptors=loaded_reference_descriptors.descriptors,
                descriptor_unavailable_reason_code=loaded_reference_descriptors.reason_code,
                source_plan_id=loaded_reference_descriptors.source_plan_id,
                source_plan_digest_sha512=loaded_reference_descriptors.source_plan_digest_sha512,
            )
            governance_observer = build_governance_observer(
                project_root=project_root,
                mode_provider=runtime_governance_composition.mode_controller.current_mode_value,
            )
            runtime_governance_composition.governance_observer = governance_observer
            governance_pre_hook, governance_post_hook = build_main_model_governance_hooks(
                composition=runtime_governance_composition,
                mode_provider=runtime_governance_composition.mode_controller.current_mode_value,
                governance_observer=governance_observer,
            )
        guardrail_pre_hook = None
        guardrail_post_hook = None
        guardrail_context_source_hook = None
        guardrail_governance_composition: GuardrailGovernanceComposition | None = None
        if guardrail_governance_enabled:
            guardrail_governance_composition = GuardrailGovernanceComposition()
            guardrail_pre_hook, guardrail_post_hook, guardrail_context_source_hook = (
                build_guardrail_hooks(
                    composition=guardrail_governance_composition,
                    mode_provider=(
                        guardrail_governance_composition.mode_controller.current_mode_value
                    ),
                )
            )
        judge_mode_control = JudgeModeController() if feature_modes_enabled else None
        repair_mode_control = RepairModeController() if feature_modes_enabled else None
        recording_mode_control = RecordingModeController() if feature_modes_enabled else None

        # Recording (P6-CODEX-011): two distinct, Composition-shared Writer
        # instances (one per subdirectory) so Turn-level records and Judge
        # Run Evidence never contend on the same files, and each is reused
        # across every call for that kind rather than a fresh instance per
        # call — the internal Lock this way actually serializes real
        # concurrent writers, closing the P6-CODEX-004/011 Quota-race gap. A
        # Recording root only exists when Conversation Persistence itself is
        # configured (the same `runtime_data_root`/scope hierarchy Recording
        # writes under); Ephemeral-only chat has no such root and Recording
        # is simply unavailable for it, never a fabricated Degraded state.
        recording_completion_hook = None
        recording_composition = None
        judge_evidence_recorder = None
        judge_evidence_recording_composition = None
        if (
            recording_mode_control is not None
            and conversation_persistence_settings is not None
            and conversation_persistence_settings.scope_id is not None
            and conversation_persistence_settings.runtime_data_root is not None
        ):
            recording_scope_dir = (
                conversation_persistence_settings.runtime_data_root
                / "persistent"
                / scope_directory_key(conversation_persistence_settings.scope_id)
            )
            # P6-CODEX-022: `containment_root` lets the Writer verify every
            # path component between the Authorized `runtime_data_root` and
            # its own `base_dir` — not only `base_dir` itself — is free of
            # a planted Symlink.
            evaluations_writer = LocalFilesystemRecordingWriter(
                base_dir=recording_scope_dir / "evaluations",
                max_total_bytes=_DEFAULT_RECORDING_MAX_TOTAL_BYTES,
                containment_root=conversation_persistence_settings.runtime_data_root,
            )
            evidence_writer = LocalFilesystemRecordingWriter(
                base_dir=recording_scope_dir / "evidence",
                max_total_bytes=_DEFAULT_RECORDING_MAX_TOTAL_BYTES,
                containment_root=conversation_persistence_settings.runtime_data_root,
            )
            recording_completion_hook, recording_composition = build_recording_completion_hook(
                recording_mode_controller=recording_mode_control,
                writer=evaluations_writer,
                # P6-CODEX-025 (Fourth Rework): sourced from this Attempt's
                # own Context, never the bootstrap-frozen `application.config`
                # / `runtime_info` closure values, which go stale across a
                # live Runtime Model Switch.
                metadata_fields_provider=lambda context: {
                    "model_identity": context.model_key,
                    "backend_key": (
                        context.model_runtime_info.backend_key
                        if context.model_runtime_info is not None
                        else "unavailable"
                    ),
                },
            )
            judge_evidence_recorder, judge_evidence_recording_composition = (
                build_judge_evidence_recorder(
                    writer=evidence_writer,
                )
            )

        model_access_coordinator = ModelAccessCoordinator()

        # Breaks the true circular dependency conversation -> judge_hook ->
        # persistent -> conversation (persistent is constructed from
        # `conversation` further below, but the Judge/Repair hook needs to be
        # built and bound into `conversation` *before* that). The Repair
        # Executor closure only ever reads `persistent_ref[0]` at call time
        # (i.e. from inside a real Turn's Judge/Repair Background Task, which
        # can only run after this whole function has already returned and
        # `persistent_ref[0]` has been filled in below), never at build time.
        persistent_ref: list[PersistentConversationService | None] = [None]

        # P6-CODEX-025 (Fourth Rework): same mutable-box pattern as
        # `persistent_ref` above, for the same reason — `conversation` needs
        # a `runtime_snapshot_provider` that reads the Runtime Model
        # Controller's live Snapshot, but the Controller itself is built
        # further below from `conversation` (it needs `conversation` for its
        # own Busy Gate). The provider closure only ever reads
        # `runtime_model_control_ref[0]` at call time (i.e. from inside a
        # real Turn, which can only start after this whole function has
        # already returned and the ref has been filled in below).
        runtime_model_control_ref: list[RuntimeModelController | None] = [None]

        def _runtime_snapshot_provider() -> RuntimeGenerationSnapshot:
            live_runtime_info = application.service.runtime_info
            controller = runtime_model_control_ref[0]
            if controller is None:
                return RuntimeGenerationSnapshot(
                    model_key=application.config.selected_model,
                    generation_defaults=application.config.generation,
                    effective_context_size=(
                        live_runtime_info.loaded_context_size
                        if live_runtime_info is not None
                        else runtime_info.loaded_context_size
                    ),
                    model_runtime_info=live_runtime_info,
                )
            model_snapshot = controller.snapshot()
            return RuntimeGenerationSnapshot(
                model_key=model_snapshot.selected_model_key,
                generation_defaults=application.config.generation.model_copy(
                    update={"max_new_tokens": model_snapshot.current_max_new_tokens}
                ),
                effective_context_size=model_snapshot.loaded_context_size,
                model_runtime_info=live_runtime_info,
            )

        def _repair_executor(
            *,
            request_id: str,
            model_key: str,
            user_input: str,
            original_answer: str,
            before_recommendation: EvaluationRecommendation,
            judge_reasoning: str,
            governance_post_hook: GovernancePostHook | None,
            guardrail_post_hook: GuardrailPostHook | None,
            cancellation: CancellationToken | None,
            model_runtime_info: ModelRuntimeInfo | None = None,
            stage_hook: Callable[[str], None] | None = None,
        ) -> RepairExecutionResult | None:
            bound_persistent = persistent_ref[0]
            if bound_persistent is None:
                # Ephemeral chat (no persistence configured) has no Turn for
                # a Repair Attempt to attach to — genuinely not applicable,
                # never a fabricated failure.
                return None
            # P6-CODEX-025 (Fourth Rework): `model_key`/`model_runtime_info`
            # come from the caller's own per-Attempt Context now, never from
            # this closure's bootstrap-time `application.config`/`runtime_info`
            # — those go stale across a live Runtime Model Switch.
            return attempt_live_repair(
                service=application.service,
                model_key=model_key,
                persistent=bound_persistent,
                request_id=request_id,
                user_input=user_input,
                original_answer=original_answer,
                before_recommendation=before_recommendation,
                judge_reasoning=judge_reasoning,
                governance_post_hook=governance_post_hook,
                guardrail_post_hook=guardrail_post_hook,
                model_runtime_info=model_runtime_info,
                cancellation=cancellation,
                stage_hook=stage_hook,
            )

        judge_completion_hook = None
        judge_governance_composition = None
        if judge_mode_control is not None:
            judge_completion_hook, judge_governance_composition = build_judge_completion_hook(
                service=application.service,
                judge_mode_controller=judge_mode_control,
                model_access_coordinator=model_access_coordinator,
                repair_mode_controller=repair_mode_control,
                recording_mode_controller=recording_mode_control,
                governance_post_hook=governance_post_hook,
                guardrail_post_hook=guardrail_post_hook,
                repair_executor=_repair_executor,
                judge_evidence_recorder=judge_evidence_recorder,
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
            documentation_rag=documentation_rag,
            documentation_rag_availability=documentation_rag_availability,
            chat_prompt_token_counter=application.service.count_chat_prompt_tokens,
            text_token_counter=application.service.count_text_tokens,
            effective_context_size=runtime_info.loaded_context_size,
            model_runtime_info=runtime_info,
            governance_pre_hook=governance_pre_hook,
            governance_post_hook=governance_post_hook,
            guardrail_pre_hook=guardrail_pre_hook,
            guardrail_post_hook=guardrail_post_hook,
            guardrail_stream_guard_factory=(
                guardrail_governance_composition.new_stream_guard
                if guardrail_governance_composition is not None
                else None
            ),
            guardrail_context_source_hook=guardrail_context_source_hook,
            guardrail_stream_result_hook=(
                guardrail_governance_composition.record_stream_guard_summary
                if guardrail_governance_composition is not None
                else None
            ),
            judge_completion_hook=judge_completion_hook,
            recording_completion_hook=recording_completion_hook,
            model_access_coordinator=model_access_coordinator,
            runtime_snapshot_provider=_runtime_snapshot_provider,
        )
        persistent = None
        conversation_storage_backend: str | None = None
        conversation_storage_backend_version: str | None = None
        if conversation_persistence_settings is not None:
            try:
                composition = start_local_conversation_persistence(
                    conversation_persistence_settings,
                    generation_service=conversation,
                )
            except ConversationStorageError as exc:
                safe_message = (
                    exc.safe_message
                    if exc.code is ConversationStorageErrorCode.MIGRATION_REQUIRED
                    else "The persistent conversation store could not start safely."
                )
                raise InferenceError(
                    code=InferenceErrorCode.INVALID_CONFIGURATION,
                    safe_message=safe_message,
                ) from exc
            persistent = composition.service
            persistent_ref[0] = persistent
            conversation_storage_backend = composition.storage_backend_kind
            conversation_storage_backend_version = composition.storage_backend_version
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
                conversation_persistence_enabled=persistent is not None,
                conversation_storage_backend=conversation_storage_backend,
                conversation_storage_backend_version=conversation_storage_backend_version,
                governance_definitions_runtime=governance_definitions_runtime,
                runtime_governance_composition=runtime_governance_composition,
                guardrail_governance_composition=guardrail_governance_composition,
            )
            if configuration_control_enabled
            else None
        )
        runtime_composition = (
            _register_runtime_components(
                documentation_rag_effective_state=documentation_rag_effective_state,
                persistent_enabled=persistent is not None,
                configuration_control_enabled=configuration_control is not None,
            )
            if runtime_composition_inspection_enabled
            else None
        )

        def _rebind_runtime_governance_capability(snapshot: RuntimeModelSnapshot) -> None:
            """P6-CODEX-036 (Fifth Rework): fired by `RuntimeModelController`
            only after a Switch/Context Reload actually commits (never on
            Rollback/Failure — see `RuntimeModelController.begin_switch()`'s
            own `on_commit` contract). Rebuilds Runtime Governance's
            Capability from `application.service.runtime_info` — the live
            adapter-level property (P6-CODEX-025: `LlamaCppRuntimeModelBackend`
            wraps the same `application.adapter` a Switch's real Load call
            updates), never from the `snapshot` argument alone, since
            `RuntimeModelSnapshot` does not itself carry `effective_
            capabilities`. Before this fix, Runtime Governance's Capability
            (Model Key/Backend/Thinking Capability/Context Size) stayed
            frozen at whatever Model was loaded at Bootstrap, so a Switch to
            a different Model left Governance Binding/Evidence silently
            describing the old Model even though real Chat already used the
            new one."""
            if runtime_governance_composition is None:
                return
            del snapshot
            live_runtime_info = application.service.runtime_info
            if live_runtime_info is None:
                return
            runtime_governance_composition.rebind_capability(
                capability=RuntimeCapabilitySnapshot(
                    model_key=live_runtime_info.model_key,
                    backend_kind=live_runtime_info.backend_key,
                    supports_streaming=True,
                    supports_thinking=(
                        CapabilityFeature.THINKING_CONTROL
                        in live_runtime_info.effective_capabilities.features
                    ),
                    max_context_tokens=live_runtime_info.loaded_context_size,
                )
            )

        runtime_model_control = (
            build_runtime_model_controller(
                application=application,
                model_access_coordinator=model_access_coordinator,
                project_root=project_root,
                on_commit=_rebind_runtime_governance_capability,
            )
            if runtime_model_control_enabled
            else None
        )
        # Fills in the mutable box `_runtime_snapshot_provider` reads —
        # from this point on, every new Turn's `start()` call resolves the
        # live Controller Snapshot instead of the bootstrap fallback above.
        runtime_model_control_ref[0] = runtime_model_control

        def _close() -> None:
            # P6-CODEX-010/019: join any in-flight Judge/Repair Background
            # Task before the Model Adapter unloads, so shutdown can never
            # race a still-running background Model Call against
            # `Adapter.unload()`. `shutdown()` returning `False` means the
            # Background Thread did not actually terminate within its join
            # timeout — proceeding to `Adapter.unload()` in that case would
            # be exactly the race this exists to prevent, so it is skipped
            # and the anomaly is logged instead of silently continuing.
            shutdown_clean = model_access_coordinator.shutdown()
            if not shutdown_clean:
                _logger.error(
                    "web application close: model access coordinator did not shut "
                    "down cleanly; skipping model unload to avoid racing a live "
                    "background model call"
                )
                return
            application.close()

        return WebRuntime(
            conversation=conversation,
            snapshot=snapshot,
            close_callback=_close,
            persistent_conversation=persistent,
            configuration_control=configuration_control,
            runtime_composition=runtime_composition,
            runtime_governance_composition=runtime_governance_composition,
            guardrail_governance_composition=guardrail_governance_composition,
            runtime_model_control=runtime_model_control,
            judge_mode_control=judge_mode_control,
            repair_mode_control=repair_mode_control,
            recording_mode_control=recording_mode_control,
            judge_governance_composition=judge_governance_composition,
            recording_composition=recording_composition,
            judge_evidence_recording_composition=judge_evidence_recording_composition,
        )
    except BaseException:
        if application is not None:
            application.close()
        raise
