"""Safe HTTP response contracts for the Phase 1-G web adapter."""

import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pydantic import Field, field_validator

from margpa_runtime_llm.modules.configuration_control import ConfigurationControlService
from margpa_runtime_llm.modules.conversation.application import PersistentConversationService
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
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
    max_new_tokens: int = Field(gt=0, le=2048)
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
    _close_lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

    def close(self, timeout: float = 10.0) -> None:
        with self._close_lock:
            if self._closed:
                return
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
