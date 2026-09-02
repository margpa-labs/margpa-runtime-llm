"""Production composition root for the Phase 1-G web runtime."""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import cast

from margpa_runtime_llm.adapters.guardrail_governance.qwen3guard_detector_adapter import (
    Qwen3GuardRoleTurn,
)
from margpa_runtime_llm.adapters.runtime_model_control.dedicated_role_adapters import (
    ProductionRoleAdapterFactory,
    Qwen3GuardRoleAdapter,
)
from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (
    DirectoryModelDefinitionRegistry,
)
from margpa_runtime_llm.adapters.runtime_observability.local_filesystem_recording_writer import (
    LocalFilesystemRecordingWriter,
)
from margpa_runtime_llm.modules.constitution import ConstitutionMode, ConstitutionProviderPort
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
    JudgeExecutionModeSnapshot,
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
from margpa_runtime_llm.modules.data_controls.ports import DataControlConsentStorePort
from margpa_runtime_llm.modules.dev_agent import DevAgentRunService
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DocumentationRagAvailability,
    DocumentationRagMode,
)
from margpa_runtime_llm.modules.documentation_rag.local_corpus_ports import (
    LocalCorpusRegistryPort,
)
from margpa_runtime_llm.modules.documentation_rag.ports import (
    ContextualRagOrchestratorPort,
    RagOrchestratorPort,
)
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationRecommendation
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass
from margpa_runtime_llm.modules.evaluation.domain.stage_budget import (
    LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET,
    StageBudgetProfile,
)
from margpa_runtime_llm.modules.governance_definitions.runtime import (
    GovernanceDefinitionsRuntime,
)
from margpa_runtime_llm.modules.inference.application.inference_service import InferenceService
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
from margpa_runtime_llm.modules.runtime_governance.domain import (
    RuntimeCapabilitySnapshot,
    SemanticProviderState,
)
from margpa_runtime_llm.modules.runtime_model_control.application import (
    BUILT_IN_JUDGE,
    ProviderSelectionController,
    RoleProviderLifecycleManager,
    RoleTurnLease,
)
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderRuntimeState,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.snapshot import RuntimeModelSnapshot
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.modules.web_knowledge.application import WebKnowledgeService
from margpa_runtime_llm.modules.web_knowledge.contracts import WebEvidenceGovernanceMode
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
from .request_correlation_registry import RequestCorrelationRegistry
from .runtime_governance import (
    RuntimeGovernanceComposition,
    SemanticRuntimeBindingContext,
    build_main_model_governance_hooks,
    default_authority,
    load_reference_descriptors,
)
from .runtime_model_control import DEFAULT_MODEL_REGISTRY_DIR, build_runtime_model_controller
from .tracked_stage_worker import TrackedStageWorkerRegistry

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
    dedicated_model_authority_granted: bool = False,
    local_corpus_registry: LocalCorpusRegistryPort | None = None,
    web_knowledge_service: WebKnowledgeService | None = None,
    web_search_governance_mode: WebEvidenceGovernanceMode = WebEvidenceGovernanceMode.OFF,
    data_controls_store: DataControlConsentStorePort | None = None,
    constitution_provider: ConstitutionProviderPort | None = None,
    constitution_mode: ConstitutionMode = ConstitutionMode.OFF,
    dev_agent_run_service: DevAgentRunService | None = None,
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
        tracked_stage_registry = TrackedStageWorkerRegistry() if feature_modes_enabled else None
        # P6-RR-O-WU-002 (Production Wiring Delta): `RoleProviderLifecycle
        # Manager` is only built further below (it needs `provider_selection
        # _control`, built after this point) — same mutable-box idiom as
        # `role_provider_runtime_model_control_ref`. The additive Qwen3Guard
        # Detector reads this box fresh on every real `detect()` call, never
        # during bootstrap.
        role_provider_lifecycle_ref: list[RoleProviderLifecycleManager | None] = [None]

        def _qwen3guard_begin_role_turn(
            cancellation: CancellationToken,
        ) -> Qwen3GuardRoleTurn | None:
            # P6-RR-R21 (resolves P6-CODEX-086): Adapter resolution and
            # Turn Lease acquisition happen together, inside
            # `RoleProviderLifecycleManager.begin_role_turn()`'s single
            # Lock acquisition — never a bare `active_adapter()` read with
            # no Lease at all (the previous shape here). A non-Qwen3Guard
            # Adapter handed back for `ModelRole.GUARD` (should not happen
            # in practice, but defensively handled rather than assumed)
            # releases its just-acquired Lease immediately rather than
            # leaking it into a discarded `None`.
            lifecycle = role_provider_lifecycle_ref[0]
            if lifecycle is None:
                return None
            handle = lifecycle.begin_role_turn(
                role=ModelRole.GUARD,
                cancellation=cancellation,
            )
            if handle is None:
                return None
            # `Qwen3GuardRoleAdapter.guard_adapter` is `None` until
            # `.load()` populates it — by construction that has already
            # happened for any Adapter `begin_role_turn()` can hand back
            # (`RoleProviderLifecycleManager._active_adapters` is only
            # populated *after* a successful `candidate.load()`), but the
            # type itself does not encode that invariant; handled
            # defensively rather than asserted.
            if (
                isinstance(handle.adapter, Qwen3GuardRoleAdapter)
                and handle.adapter.guard_adapter is not None
            ):
                return Qwen3GuardRoleTurn(adapter=handle.adapter.guard_adapter, lease=handle.lease)
            lifecycle.end_turn(handle.lease)
            return None

        def _qwen3guard_end_role_turn(lease: object) -> None:
            lifecycle = role_provider_lifecycle_ref[0]
            if lifecycle is not None:
                lifecycle.end_turn(cast(RoleTurnLease, lease))

        if guardrail_governance_enabled:
            guardrail_governance_composition = GuardrailGovernanceComposition(
                qwen3guard_begin_role_turn_with_cancellation=_qwen3guard_begin_role_turn,
                qwen3guard_end_role_turn=_qwen3guard_end_role_turn,
                tracked_stage_registry=tracked_stage_registry,
            )
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
        # P6-RR-R19-WU-001..004 (Post-Claude Independent Review Rework,
        # resolves P6-CODEX-082): one Registry per Runtime, shared by
        # every Turn `ConversationGenerationService` starts — same
        # lifetime/sharing model as `judge_governance_composition`/
        # `recording_composition` below.
        request_correlation_registry = (
            RequestCorrelationRegistry() if feature_modes_enabled else None
        )
        # P6-RR-R22 (Post-Codex Independent Review Rework, resolves the
        # rest of P6-CODEX-081): one Registry per Runtime, shared by every
        # Judge Run's Prompt Build/Decode and Qwen3Guard bounded inference
        # Tracked Stage submission. `WebRuntime.close()` Bounded-Joins it,
        # before Model Unload, via the `tracked_stage_registry=` wiring
        # below.
        provider_selection_control = (
            ProviderSelectionController(current_main_provider=runtime_info.model_key)
            if runtime_model_control_enabled or feature_modes_enabled
            else None
        )
        # P6-RR-M-WU-001 (Production Wiring Delta): same mutable-box idiom as
        # `runtime_model_control_ref` further below — `ProductionRoleAdapter
        # Factory`'s Main-shared-Judge branch needs the live Runtime Model
        # Controller Snapshot, but that Controller is only built later (it
        # needs `conversation`/`model_access_coordinator`, both built after
        # this point). The Factory only ever reads this box at real
        # Activation time, never during bootstrap itself.
        role_provider_runtime_model_control_ref: list[RuntimeModelController | None] = [None]
        role_provider_lifecycle = (
            RoleProviderLifecycleManager(
                selections=provider_selection_control,
                # Selene/Qwen3Guard are real, but Fail-closed without a
                # separately human-granted Exact Model Authority Receipt
                # (Base Exact Handoff §8.1). `dedicated_model_authority_
                # granted` defaults to False here (P9-CODEX-001: the CLI's
                # `--phase-6-dedicated-model-authority` opt-in is the only
                # caller that can raise it — see `entrypoints/web/main.py`).
                # Raising it alone never Loads a Dedicated Model: this
                # value only lets `preflight()` proceed past its own
                # Fail-closed gate the *next* time a caller explicitly
                # selects and activates Selene/Qwen3Guard (Mode Transition
                # ON) — see `dedicated_role_adapters.py`'s `_run_dedicated_
                # preflight()`. An explicit Main-model Judge selection is
                # routed to Main's own already-loaded runtime instead of a
                # second concurrent Load, unaffected by this flag.
                factory=ProductionRoleAdapterFactory(
                    definitions=DirectoryModelDefinitionRegistry(
                        registry_dir=project_root / DEFAULT_MODEL_REGISTRY_DIR
                    ),
                    model_root=application.config.model_root,
                    load_config=application.config.load,
                    runtime_model_control_ref=role_provider_runtime_model_control_ref,
                    dedicated_model_authority_granted=dedicated_model_authority_granted,
                    selene_prompt_manifest_path=(
                        project_root / "config/judge_templates/selene/manifest.json"
                    ),
                    # P6-RR-R23 (resolves P6-CODEX-087): checked-in Official
                    # Contract Manifest, fetched Read-only from Qwen's own
                    # Hugging Face/GitHub Repositories under this specific
                    # Package's Network Authority grant.
                    qwen3guard_contract_manifest_path=(
                        project_root / "config/guardrail/qwen3guard/manifest.json"
                    ),
                    tracked_stage_registry=tracked_stage_registry,
                ),
            )
            if provider_selection_control is not None
            else None
        )
        role_provider_lifecycle_ref[0] = role_provider_lifecycle

        if runtime_governance_composition is not None:

            def _semantic_runtime_context() -> SemanticRuntimeBindingContext:
                judge_mode = (
                    judge_mode_control.mode_snapshot().current_mode.value
                    if judge_mode_control is not None
                    else "off"
                )
                repair_mode = (
                    repair_mode_control.mode_snapshot().current_mode.value
                    if repair_mode_control is not None
                    else "off"
                )
                if provider_selection_control is None:
                    return SemanticRuntimeBindingContext(
                        language=application.config.response.language.value,
                        judge_mode=judge_mode,
                        repair_mode=repair_mode,
                    )
                judge = provider_selection_control.selection_for(ModelRole.JUDGE)
                provider_state = (
                    SemanticProviderState.ACTIVE
                    if judge.state is ProviderRuntimeState.ACTIVE
                    else SemanticProviderState.NONE
                    if judge.state is ProviderRuntimeState.NONE
                    else SemanticProviderState.FAILED
                    if judge.state is ProviderRuntimeState.FAILED
                    else SemanticProviderState.UNAVAILABLE
                )
                return SemanticRuntimeBindingContext(
                    language=application.config.response.language.value,
                    judge_mode=judge_mode,
                    repair_mode=repair_mode,
                    configured_provider=judge.configured_provider,
                    active_provider=judge.active_provider,
                    provider_state=provider_state,
                )

            runtime_governance_composition.set_semantic_context_provider(_semantic_runtime_context)
            runtime_governance_composition.mode_controller.set_semantic_enforce_gate(
                runtime_governance_composition.semantic_enforce_readiness
            )

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
            dialogue_context: tuple[str, ...],
            evidence_context: tuple[str, ...],
            governance_post_hook: GovernancePostHook | None,
            guardrail_post_hook: GuardrailPostHook | None,
            cancellation: CancellationToken | None,
            model_runtime_info: ModelRuntimeInfo | None = None,
            stage_hook: Callable[[str], None] | None = None,
            persist_accepted_attempt: bool = True,
            stage_budget: StageBudgetProfile = LOCAL_MACOS_MAIN_SELF_JUDGE_BUDGET,
            rejudge_service: InferenceService | None = None,
            rejudge_model_key: str | None = None,
            rejudge_role: JudgeIndependenceClass = JudgeIndependenceClass.MAIN_SELF,
            language: str = "en",
        ) -> RepairExecutionResult | None:
            bound_persistent = persistent_ref[0]
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
                dialogue_context=dialogue_context,
                evidence_context=evidence_context,
                governance_post_hook=governance_post_hook,
                guardrail_post_hook=guardrail_post_hook,
                model_runtime_info=model_runtime_info,
                stage_budget=stage_budget,
                rejudge_service=rejudge_service,
                rejudge_model_key=rejudge_model_key,
                rejudge_role=rejudge_role,
                cancellation=cancellation,
                stage_hook=stage_hook,
                persist_accepted_attempt=persist_accepted_attempt,
                language=language,
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
                semantic_snapshot_provider=(
                    lambda request_id: (
                        runtime_governance_composition.semantic_runtime.snapshot_for(
                            request_id=request_id
                        )
                        if runtime_governance_composition is not None
                        else None
                    )
                ),
                semantic_result_recorder=(
                    (
                        lambda response: runtime_governance_composition.record_semantic_response(
                            response=response
                        )
                    )
                    if runtime_governance_composition is not None
                    else None
                ),
                semantic_deferred_recorder=(
                    (
                        lambda request_id, reason: (
                            runtime_governance_composition.record_semantic_deferred(
                                request_id=request_id, reason=reason
                            )
                        )
                    )
                    if runtime_governance_composition is not None
                    else None
                ),
                # P6-RR-N-WU-001 (Production Wiring Delta): reads the same
                # Provider Selection Controller the Advanced Mode panel
                # reads, at real Turn/Run time only (never during
                # bootstrap) — `_judge_provider_is_built_in()` inside the
                # Hook itself already wraps this in try/except and freezes
                # it once per Run, alongside judge_mode/repair_mode/
                # recording_mode.
                judge_provider_is_built_in=(
                    (
                        lambda: (
                            provider_selection_control.selection_for(
                                ModelRole.JUDGE
                            ).active_provider
                            == BUILT_IN_JUDGE
                        )
                    )
                    if provider_selection_control is not None
                    else None
                ),
                # P6-RR-O-WU-004 (Production Wiring Delta): reads the real
                # Guardrail Mode Controller, at real Turn/Run time only —
                # resolves P6-CODEX-053/061's `frozen_guard_mode=None`
                # literal into the actual Mode this Turn ran under.
                guardrail_mode_resolver=(
                    guardrail_governance_composition.mode_controller.current_mode_value
                    if guardrail_governance_composition is not None
                    else None
                ),
                # P6-RR-R2-WU-001 (Post-Claude Independent Review Rework,
                # resolves P6-CODEX-063): reads the same Role Provider
                # Lifecycle Manager the Qwen3Guard Detector Adapter already
                # reads (`_qwen3guard_begin_role_turn` above), at real
                # Turn/Run time only — lets the Judge Hook dispatch to
                # whichever Adapter (Built-in handled separately, Selene,
                # or an explicit Main-shared selection) is genuinely
                # Active, instead of unconditionally assuming Main-self.
                #
                # P6-RR-R21 (resolves P6-CODEX-086): `begin_role_turn`
                # atomically pairs this same Adapter resolution with a
                # genuine Turn Lease (single Lock acquisition inside
                # `RoleProviderLifecycleManager`) — the previous
                # `active_adapter()`-only resolver never acquired any
                # Lease, so a concurrent Provider switch/Mode OFF/Shutdown
                # could Unload the Adapter while a real Judge Model Call
                # was still in flight against it.
                begin_judge_role_turn_with_cancellation=(
                    (
                        lambda cancellation: role_provider_lifecycle.begin_role_turn(
                            role=ModelRole.JUDGE,
                            cancellation=cancellation,
                        )
                    )
                    if role_provider_lifecycle is not None
                    else None
                ),
                end_judge_role_turn=(
                    (lambda lease: role_provider_lifecycle.end_turn(cast(RoleTurnLease, lease)))
                    if role_provider_lifecycle is not None
                    else None
                ),
                # P6-RR-R22 (resolves the rest of P6-CODEX-081): the same
                # Registry `WebRuntime.close()` Bounded-Joins before Model
                # Unload — every Prompt Build/Decode Tracked Stage Worker
                # this Hook's Judge Runs ever dispatch registers here.
                tracked_stage_registry=tracked_stage_registry,
            )

        def _judge_execution_mode_snapshot() -> JudgeExecutionModeSnapshot:
            return JudgeExecutionModeSnapshot(
                judge_mode=(
                    judge_mode_control.mode_snapshot().current_mode.value
                    if judge_mode_control is not None
                    else "off"
                ),
                repair_mode=(
                    repair_mode_control.mode_snapshot().current_mode.value
                    if repair_mode_control is not None
                    else None
                ),
                recording_mode=(
                    recording_mode_control.mode_snapshot().current_mode.value
                    if recording_mode_control is not None
                    else None
                ),
            )

        def _begin_request_correlation(request_id: str, started_at: str) -> None:
            assert request_correlation_registry is not None
            request_correlation_registry.begin(request_id=request_id, started_at=started_at)

        def _mark_request_correlation_terminal(
            request_id: str, status: str, completed_at: str
        ) -> None:
            assert request_correlation_registry is not None
            request_correlation_registry.mark_terminal(
                request_id=request_id, status=status, completed_at=completed_at
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
            web_knowledge_service=web_knowledge_service,
            web_search_governance_mode=web_search_governance_mode,
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
            judge_mode_snapshot_provider=_judge_execution_mode_snapshot,
            recording_completion_hook=recording_completion_hook,
            model_access_coordinator=model_access_coordinator,
            runtime_snapshot_provider=_runtime_snapshot_provider,
            request_correlation_begin=(
                _begin_request_correlation if request_correlation_registry is not None else None
            ),
            request_correlation_terminal=(
                _mark_request_correlation_terminal
                if request_correlation_registry is not None
                else None
            ),
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
                role_provider_lifecycle=role_provider_lifecycle,
                judge_mode_control=judge_mode_control,
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
        role_provider_runtime_model_control_ref[0] = runtime_model_control

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
            provider_selection_control=provider_selection_control,
            role_provider_lifecycle=role_provider_lifecycle,
            judge_mode_control=judge_mode_control,
            repair_mode_control=repair_mode_control,
            recording_mode_control=recording_mode_control,
            judge_governance_composition=judge_governance_composition,
            recording_composition=recording_composition,
            judge_evidence_recording_composition=judge_evidence_recording_composition,
            request_correlation_registry=request_correlation_registry,
            tracked_stage_registry=tracked_stage_registry,
            local_corpus_registry=local_corpus_registry,
            web_knowledge_service=web_knowledge_service,
            web_search_governance_mode=web_search_governance_mode,
            data_controls_store=data_controls_store,
            constitution_provider=constitution_provider,
            constitution_mode=constitution_mode,
            dev_agent_run_service=dev_agent_run_service,
        )
    except BaseException:
        if application is not None:
            application.close()
        raise
