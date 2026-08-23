"""P6-CODEX-014 (Second Rework): `/api/v4/runtime-model/status`'s
`governance_layer` field must reflect the real, currently-bound Phase 4
Runtime Governance (`WebRuntime.runtime_governance_composition`), never the
independent Phase 3 `governance_definitions` package-browse control
surface. The regression this guards against: a real Phase 4 binding
(`source_plan_id`/`source_plan_digest_sha512` set) used to be reported as
`None`/`state=none` whenever nothing had been separately stashed on
`app.state.governance_definitions_runtime` — a fabricated absence hiding a
real, active binding.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.bootstrap.runtime_governance import RuntimeGovernanceComposition
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
    GenerationStream,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.runtime_governance.domain import RuntimeCapabilitySnapshot
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    BindingState,
    IndependenceClass,
    ModelRole,
    RuntimeState,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.snapshot import (
    RoleBinding,
    RuntimeModelSnapshot,
    compute_runtime_model_snapshot_digest,
)
from margpa_runtime_llm.modules.summarization.public import SummaryMode
from margpa_runtime_llm.web.access_profiles import WebExposureMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import RuntimeDefaults, SafeRuntimeSnapshot, WebRuntime

_SHA512_A = "a" * 128
_SHA512_B = "b" * 128
_LOCAL_POLICY = WebAccessPolicy(exposure_mode=WebExposureMode.LOCAL, mode=WebAuthMode.DISABLED)


class _FakeInference:
    def stream(self, request: GenerationRequest) -> GenerationStream:
        raise NotImplementedError


def _conversation() -> ConversationGenerationService:
    return ConversationGenerationService(
        inference=_FakeInference(),
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key="main.model",
        generation_defaults=GenerationParameters(),
        response_language_default=ResponseLanguage.JA,
        presentation_default=ResolvedThinkingPresentationPolicy(
            visibility=ThinkingVisibility.HIDDEN,
            display_label="推論過程",
            persistence=ThinkingPersistence.DISABLED,
            visibility_source=ThinkingPresentationSource.APPLICATION,
            display_label_source=ThinkingPresentationSource.APPLICATION,
            persistence_source=ThinkingPresentationSource.APPLICATION,
        ),
    )


def _snapshot() -> SafeRuntimeSnapshot:
    return SafeRuntimeSnapshot(
        model_key="main.model",
        profile_key="test",
        device_kind="cpu",
        acceleration_api="none",
        defaults=RuntimeDefaults(
            response_language=ResponseLanguage.JA,
            max_new_tokens=128,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            thinking_display_label="推論過程",
            thinking_control_available=False,
            summary_mode=SummaryMode.OFF,
        ),
    )


def _runtime_model_control() -> RuntimeModelController:
    binding = RoleBinding(
        role=ModelRole.MAIN,
        model_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_A,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=_SHA512_A,
    )
    digest = compute_runtime_model_snapshot_digest(
        revision=0,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=(binding,),
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_A,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=4096,
        current_max_new_tokens=2048,
    )
    snapshot = RuntimeModelSnapshot(
        revision=0,
        digest_sha512=digest,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=(binding,),
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_A,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=4096,
        model_native_context_limit=8192,
        backend_context_limit=8192,
        deployment_verified_context_limit=8192,
        max_output_token_limit=2048,
        current_max_new_tokens=2048,
        last_transition_receipt=None,
    )

    class _NullBackend:
        pass

    class _NullAccessLease:
        def try_acquire_switch_lease(self, *, task_id: str) -> bool:
            return True

        def release_switch_lease(self, *, task_id: str) -> None:
            pass

    class _NullDefinitions:
        def resolve(self, *, model_key: str) -> None:
            raise NotImplementedError

        def all_definitions(self) -> tuple[object, ...]:
            return ()

    return RuntimeModelController(
        initial_snapshot=snapshot,
        backend=_NullBackend(),  # type: ignore[arg-type]
        access_lease=_NullAccessLease(),
        definitions=_NullDefinitions(),  # type: ignore[arg-type]
    )


def _bound_runtime_governance_composition() -> RuntimeGovernanceComposition:
    return RuntimeGovernanceComposition(
        capability=RuntimeCapabilitySnapshot(
            model_key="main.qwen3-4b-q4-k-m",
            backend_kind="llama_cpp",
            supports_streaming=True,
            supports_thinking=False,
            max_context_tokens=4096,
        ),
        descriptors=(),
        source_plan_id="core-governance-plan-v1",
        source_plan_digest_sha512=_SHA512_B,
    )


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client


@pytest.mark.asyncio
async def test_status_reflects_the_real_phase4_binding_with_zero_phase3_state() -> None:
    """The exact regression: no `app.state.governance_definitions_runtime`
    is ever set anywhere in this test, yet a real Phase 4 binding must
    still be reported as ACTIVE with its true package_id/digest."""

    def runtime_factory() -> WebRuntime:
        return WebRuntime(
            conversation=_conversation(),
            snapshot=_snapshot(),
            close_callback=lambda: None,
            runtime_model_control=_runtime_model_control(),
            runtime_governance_composition=_bound_runtime_governance_composition(),
        )

    app = create_web_app(runtime_factory=runtime_factory, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v4/runtime-model/status")
        body = response.json()

    assert response.status_code == 200
    governance_layer = body["governance_layer"]
    assert governance_layer["package_id"] == "core-governance-plan-v1"
    assert governance_layer["manifest_digest_sha512"] == _SHA512_B
    assert governance_layer["state"] == "active"


@pytest.mark.asyncio
async def test_status_reports_none_when_phase4_governance_is_not_enabled_at_all() -> None:
    def runtime_factory() -> WebRuntime:
        return WebRuntime(
            conversation=_conversation(),
            snapshot=_snapshot(),
            close_callback=lambda: None,
            runtime_model_control=_runtime_model_control(),
            runtime_governance_composition=None,
        )

    app = create_web_app(runtime_factory=runtime_factory, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v4/runtime-model/status")
        body = response.json()

    assert response.status_code == 200
    governance_layer = body["governance_layer"]
    assert governance_layer["package_id"] is None
    assert governance_layer["state"] == "none"
