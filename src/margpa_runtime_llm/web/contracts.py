"""Safe HTTP response contracts for the Phase 1-G web adapter."""

import threading
from collections.abc import Callable
from dataclasses import dataclass, field

from pydantic import Field, field_validator

from margpa_runtime_llm.modules.configuration_control import ConfigurationControlService
from margpa_runtime_llm.modules.conversation.application import PersistentConversationService
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.documentation_rag.contracts import DocumentationRagMode
from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract
from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.contracts.thinking import ThinkingVisibility
from margpa_runtime_llm.modules.runtime_composition.application import ComponentRegistryService
from margpa_runtime_llm.modules.summarization.public import SummaryMode

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
    _close_lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _closed: bool = field(default=False, init=False, repr=False)

    def close(self, timeout: float = 10.0) -> None:
        with self._close_lock:
            if self._closed:
                return
            if not self.conversation.shutdown(timeout):
                raise RuntimeError("The active generation did not stop during shutdown.")
            self.close_callback()
            self._closed = True
