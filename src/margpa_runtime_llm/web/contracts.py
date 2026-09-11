"""Safe HTTP response contracts for the Phase 1-G web adapter."""

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pydantic import Field, field_validator

from margpa_runtime_llm.modules.configuration_control import ConfigurationControlService
from margpa_runtime_llm.modules.constitution import ConstitutionMode, ConstitutionProviderPort
from margpa_runtime_llm.modules.context_compaction.application.auto_policy import (
    AutoCompactionPolicyController,
)
from margpa_runtime_llm.modules.context_compaction.application.coordinator import (
    CompactionCoordinator,
)
from margpa_runtime_llm.modules.context_compaction.application.worker import CompactionWorker
from margpa_runtime_llm.modules.conversation.application import PersistentConversationService
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.data_controls.ports import DataControlConsentStorePort
from margpa_runtime_llm.modules.dev_agent import DevAgentRunService
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.documentation_rag.local_corpus_ports import (
    LocalCorpusRegistryPort,
)
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.experiment.application.configuration_lease import (
    ExperimentConfigurationLease,
)
from margpa_runtime_llm.modules.experiment.application.experiment_service import (
    ExperimentService,
)
from margpa_runtime_llm.modules.experiment.application.live_configuration_port import (
    LiveConfigurationPort,
)
from margpa_runtime_llm.modules.experiment.application.production_turn_runner import (
    ProductionTurnPort,
)
from margpa_runtime_llm.modules.experiment.application.run_worker import ExperimentRunWorker
from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.runtime_composition.application import ComponentRegistryService
from margpa_runtime_llm.modules.runtime_model_control.application import (
    ProviderSelectionController,
    RoleProviderLifecycleManager,
)
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.modules.summarization.public import SummaryMode
from margpa_runtime_llm.modules.web_knowledge.application import WebKnowledgeService
from margpa_runtime_llm.modules.web_knowledge.contracts import WebEvidenceGovernanceMode

if TYPE_CHECKING:
    # Import-time only: `bootstrap/` composes `web/`, not the reverse.
    # This forward reference avoids a real dependency inversion while
    # still letting `WebRuntime.runtime_governance_composition` be
    # precisely typed for the Status route (P4-F-WU-003).
    from margpa_runtime_llm.bootstrap.guardrail_governance import GuardrailGovernanceComposition
    from margpa_runtime_llm.bootstrap.judge_live_integration import JudgeGovernanceComposition
    from margpa_runtime_llm.bootstrap.recording_live_integration import RecordingCompositionState
    from margpa_runtime_llm.bootstrap.request_correlation_registry import (
        RequestCorrelationRegistry,
    )
    from margpa_runtime_llm.bootstrap.runtime_governance import RuntimeGovernanceComposition
    from margpa_runtime_llm.bootstrap.tracked_stage_worker import TrackedStageWorkerRegistry

from .access_profiles import DocumentationRagEffectiveState


class RuntimeDefaults(ImmutableContract):
    response_language: ResponseLanguage
    # P9-1 Package 3: raised from 2048 to 8192, matching the new
    # Deployment/Application Profile Output Ceiling
    # (`ModelLoadConfig.max_output_tokens_ceiling`) — a defensive type-level
    # bound on the reported value, not the source of truth (that flows from
    # Config -> Resolver -> Capability -> this Snapshot field).
    max_new_tokens: int = Field(gt=0, le=8192)
    thinking_mode: ThinkingMode
    thinking_visibility: ThinkingVisibility
    thinking_display_label: str
    thinking_control_available: bool
    summary_mode: SummaryMode
    documentation_rag_mode: DocumentationRagMode = DocumentationRagMode.DISABLED


class DocumentationRagRuntimeSnapshot(ImmutableContract):
    effective_state: DocumentationRagEffectiveState
    control_available: bool
    provider_display_name: str | None = None
    default_mode: DocumentationRagMode = DocumentationRagMode.DISABLED


class SafeRuntimeSnapshot(ImmutableContract):
    model_key: str
    profile_key: str
    device_kind: str
    acceleration_api: str
    defaults: RuntimeDefaults
    documentation_rag: DocumentationRagRuntimeSnapshot = DocumentationRagRuntimeSnapshot(
        effective_state=DocumentationRagEffectiveState.UNAVAILABLE,
        control_available=False,
    )


class StopGenerationRequest(ImmutableContract):
    request_id: str = Field(min_length=1, max_length=128)

    @field_validator("request_id")
    @classmethod
    def validate_request_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("request id must not be blank")
        return value


@dataclass(slots=True)
class WebRuntime:
    conversation: ConversationGenerationService
    snapshot: SafeRuntimeSnapshot
    close_callback: Callable[[], None]
    persistent_conversation: PersistentConversationService | None = None
    configuration_control: ConfigurationControlService | None = None
    runtime_composition: ComponentRegistryService | None = None
    runtime_governance_composition: "RuntimeGovernanceComposition | None" = None
    guardrail_governance_composition: "GuardrailGovernanceComposition | None" = None
    runtime_model_control: RuntimeModelController | None = None
    provider_selection_control: ProviderSelectionController | None = None
    role_provider_lifecycle: RoleProviderLifecycleManager | None = None
    judge_mode_control: JudgeModeController | None = None
    repair_mode_control: RepairModeController | None = None
    recording_mode_control: RecordingModeController | None = None
    judge_governance_composition: "JudgeGovernanceComposition | None" = None
    recording_composition: "RecordingCompositionState | None" = None
    judge_evidence_recording_composition: "RecordingCompositionState | None" = None
    request_correlation_registry: "RequestCorrelationRegistry | None" = None
    tracked_stage_registry: "TrackedStageWorkerRegistry | None" = None
    local_corpus_registry: LocalCorpusRegistryPort | None = None
    web_knowledge_service: WebKnowledgeService | None = None
    web_search_governance_mode: WebEvidenceGovernanceMode = WebEvidenceGovernanceMode.OFF
    data_controls_store: DataControlConsentStorePort | None = None
    constitution_provider: ConstitutionProviderPort | None = None
    constitution_mode: ConstitutionMode = ConstitutionMode.OFF
    dev_agent_run_service: DevAgentRunService | None = None
    experiment_service: ExperimentService | None = None
    """Phase 9-2 WU-A/E: `None` unless the explicit, default-OFF Experiment
    Runtime gate wires a Filesystem-backed `ExperimentService` -- absent, this
    routes to `experiment_routes.py`'s own disabled-response shape,
    exactly like every other Optional `WebRuntime` field, and never
    forces itself into the ordinary Chat/Judge/Guard request path."""
    production_turn_adapter: ProductionTurnPort | None = None
    """Phase 9-2 R1-WU-03: `None` unless the Experiment Runtime gate wires a
    `LiveProductionTurnAdapter` over this same `WebRuntime`'s own
    `conversation`/`judge_governance_composition`/
    `guardrail_governance_composition` -- absent, `execution_mode=
    "production"` Experiment Runs are rejected as
    `production_adapter_unavailable` rather than silently falling back to
    a Fixture (a Fixture Result is never substituted for a requested real
    one)."""
    experiment_run_worker: ExperimentRunWorker | None = None
    """Phase 9-2 R1-WU-05: the single-threaded Tracked Worker every
    `/api/v7/experiment/runs` start hands its Actor Call to -- `None`
    exactly when `experiment_service` is also `None` (constructed
    together in Bootstrap). Shut down in `close()` below, before the
    ordinary Chat/Judge/Guard drain, so an in-flight Experiment Run never
    outlives the real Model backends its own Production Adapter reads."""
    live_configuration_reader: LiveConfigurationPort | None = None
    """Phase 9-2 R2-WU-01: `None` unless the Experiment Runtime gate wires a
    `BootstrapLiveConfigurationReader` reading this SAME `WebRuntime`'s
    own Judge/Guard/Main-Governance/Repair/Recording/Main Controllers --
    absent, a Production Run's Frozen-vs-Live Config comparison can never
    be attempted, and `execution_mode="production"` Runs are rejected as
    `live_config_unavailable` rather than silently skipping the check."""
    experiment_configuration_lease: ExperimentConfigurationLease | None = None
    """Phase 9-2 R3-WU-01 (Handoff R3 SS4.2 Option A): `None` while the
    Experiment Runtime gate is OFF. When the gate is ON, Bootstrap wires one
    alongside `live_configuration_reader`; `web/app.py`'s `secure_requests` middleware
    atomically acquires/releases a mutation side lease around the full
    handling of a fixed allowlist of Settings-mutation routes
    (Judge/Repair/Recording Mode, Provider Selection, Runtime Model
    context/max-new-tokens/switch, the Guard/Main-Governance
    Configuration Preview->Apply CAS path), and
    `application.run_worker.ExperimentRunWorker` is the only caller of
    `acquire()`/`release()`, held only for the duration of one real
    Production Turn's own `invoke()` call. Never touches any Controller's
    own contract."""
    context_compaction_coordinator: CompactionCoordinator | None = None
    """Phase 9-3 CL-P9-3-F: `None` unless Persistent Conversation is enabled
    -- Compaction Core structurally requires a Canonical Conversation to
    Snapshot/Compact against (SS5.1 `core_state=unavailable` otherwise, not
    a disabled Mode). Never gated behind its own opt-in flag, unlike the
    Phase 9-2 Experiment Runtime -- Compaction Core is meant to be always
    available once Persistence itself is."""
    context_compaction_worker: CompactionWorker | None = None
    """Shut down in `close()` below, before the ordinary Chat/Judge/Guard
    drain -- mirrors `experiment_run_worker`'s own placement."""
    context_compaction_auto_policy: AutoCompactionPolicyController | None = None
    _close_lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

    def close(self, timeout: float = 10.0) -> None:
        with self._close_lock:
            if self._closed:
                return
            if (
                self.context_compaction_worker is not None
                and not self.context_compaction_worker.shutdown(timeout=timeout)
            ):
                raise RuntimeError(
                    "An in-flight Context Compaction Attempt did not stop during shutdown."
                )
            if self.experiment_run_worker is not None and not self.experiment_run_worker.shutdown(
                timeout=timeout
            ):
                raise RuntimeError(
                    "An in-flight Experiment Run did not stop during shutdown."
                )
            if not self.conversation.shutdown(timeout):
                raise RuntimeError("The active generation did not stop during shutdown.")
            # P6-RR-R22 (Post-Codex Independent Review Rework, resolves the
            # rest of P6-CODEX-081): a Prompt Build/Decode Tracked Stage
            # Worker that ignored its own Turn's Budget (and so kept
            # running after that Turn's own `_run_judge` already returned)
            # is invisible to `self.conversation.shutdown()` above — that
            # only drains the outer Judge Background Task, never the inner
            # Stage Workers it may have dispatched. Checked, and honored,
            # *before* the two Unload calls below: a False-clean result
            # here must stop this method from proceeding to Unload, the
            # exact ordering P6-CODEX-081 requires.
            if self.tracked_stage_registry is not None and not self.tracked_stage_registry.shutdown(
                timeout_seconds=timeout
            ):
                raise RuntimeError(
                    "A tracked Prompt Build/Decode stage worker did not stop during shutdown."
                )
            if (
                self.role_provider_lifecycle is not None
                and not self.role_provider_lifecycle.shutdown()
            ):
                raise RuntimeError("A dedicated role provider did not stop during shutdown.")
            self.close_callback()
            self._closed = True
