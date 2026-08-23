"""Public/Basic Private Runtime Model Control Call-0 regression (Phase 6-G-WU-001).

Mirrors test_runtime_governance_public_basic_call0.py's two invariants for
the new `/api/v4/runtime-model/*` routes:

1. Binding `runtime_model_control` under a non-local exposure mode must
   refuse App startup rather than silently exposing it.
2. In the actual Call-0 state (no Runtime Model Control wiring, which is
   what every current entrypoint produces today since the feature is
   Opt-in/Default-False), the route degrades to a safe `enabled: false`
   response instead of 500ing or leaking internals.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.inference.contracts.generation import (
    FinishReason,
    GenerationChunk,
    GenerationParameters,
    GenerationRequest,
    GenerationStream,
    GenerationTerminalState,
    GenerationTiming,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
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
from margpa_runtime_llm.modules.runtime_model_control.ports import (
    CapabilityProbeResult,
    LoadedModelHandle,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode
from margpa_runtime_llm.web.access_profiles import WebExposureMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import RuntimeDefaults, SafeRuntimeSnapshot, WebRuntime

_SHA512_FILLER = "a" * 128


class FakeStream:
    def __init__(self) -> None:
        self.cancelled = False
        self.closed = False

    @property
    def generation_id(self) -> str:
        return "rmc-call0-generation"

    @property
    def terminal_state(self) -> GenerationTerminalState:
        return GenerationTerminalState.ACTIVE

    @property
    def timing(self) -> GenerationTiming | None:
        return None

    def __iter__(self) -> Iterator[GenerationChunk]:
        yield GenerationChunk(
            request_id="rmc-call0-request",
            sequence=0,
            text_delta="",
            is_final=True,
            finish_reason=FinishReason.STOP,
        )

    def cancel(self) -> None:
        self.cancelled = True

    def close(self) -> None:
        self.closed = True

    def __enter__(self) -> FakeStream:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class FakeInference:
    def stream(self, request: GenerationRequest) -> GenerationStream:
        return FakeStream()


def _presentation_policy() -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def _snapshot() -> SafeRuntimeSnapshot:
    return SafeRuntimeSnapshot(
        model_key="main.qwen3-4b-q4-k-m",
        profile_key="local.macos-arm64.metal",
        device_kind="gpu",
        acceleration_api="metal",
        defaults=RuntimeDefaults(
            response_language=ResponseLanguage.JA,
            max_new_tokens=2048,
            thinking_mode=ThinkingMode.DISABLED,
            thinking_visibility=ThinkingVisibility.HIDDEN,
            thinking_display_label="推論過程",
            thinking_control_available=True,
            summary_mode=SummaryMode.OFF,
        ),
    )


def _conversation() -> ConversationGenerationService:
    return ConversationGenerationService(
        inference=FakeInference(),
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key="main.qwen3-4b-q4-k-m",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=_presentation_policy(),
        summarization=SummarizationConfig(),
    )


class _FakeBackend:
    def probe_capability(self, *, definition: ModelDefinition) -> CapabilityProbeResult:
        raise NotImplementedError

    def load(self, *, definition: ModelDefinition, context_size: int) -> LoadedModelHandle:
        raise NotImplementedError

    def unload(self) -> None:
        pass


class _FakeAccessLease:
    """P6-CODEX-034 (Fifth Rework): replaces the retired `_FakeBusyGate` —
    mirrors the real `ModelAccessCoordinator`'s exclusive-lease Port."""

    def try_acquire_switch_lease(self, *, task_id: str) -> bool:
        return True

    def release_switch_lease(self, *, task_id: str) -> None:
        pass


class _FakeDefinitionResolver:
    def resolve(self, *, model_key: str) -> ModelDefinition:
        raise NotImplementedError

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return ()


def _runtime_model_controller() -> RuntimeModelController:
    binding = RoleBinding(
        role=ModelRole.MAIN,
        model_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=_SHA512_FILLER,
    )
    digest = compute_runtime_model_snapshot_digest(
        revision=0,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=(binding,),
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_FILLER,
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
        artifact_digest=_SHA512_FILLER,
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
    return RuntimeModelController(
        initial_snapshot=snapshot,
        backend=_FakeBackend(),
        access_lease=_FakeAccessLease(),
        definitions=_FakeDefinitionResolver(),
    )


def call0_runtime() -> WebRuntime:
    """Mirrors what every current entrypoint invocation actually builds:
    Runtime Model Control is Opt-in/Default-False, never wired at all."""
    return WebRuntime(
        conversation=_conversation(),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        runtime_model_control=None,
    )


def bound_runtime() -> WebRuntime:
    """A hypothetical misconfiguration: bound even under a shared exposure mode."""
    return WebRuntime(
        conversation=_conversation(),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        runtime_model_control=_runtime_model_controller(),
    )


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client


@pytest.fixture(
    params=[
        WebAccessPolicy(exposure_mode=WebExposureMode.LOCAL, mode=WebAuthMode.DISABLED),
    ]
)
def local_policy(request: pytest.FixtureRequest) -> WebAccessPolicy:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture(
    params=[
        WebAccessPolicy(
            mode=WebAuthMode.DISABLED,
            exposure_mode=WebExposureMode.PUBLIC_DEMO,
            non_loopback_allowed=True,
        ),
        WebAccessPolicy(
            mode=WebAuthMode.BASIC,
            exposure_mode=WebExposureMode.BASIC_PREVIEW,
            non_loopback_allowed=True,
            username="user",
            password="password",
        ),
    ]
)
def non_local_policy(request: pytest.FixtureRequest) -> WebAccessPolicy:
    return request.param  # type: ignore[no-any-return]


@pytest.mark.asyncio
async def test_status_degrades_safely_when_not_bound(local_policy: WebAccessPolicy) -> None:
    app = create_web_app(runtime_factory=call0_runtime, access_policy=local_policy)
    async with client_for(app) as client:
        response = await client.get("/api/v4/runtime-model/status")
    assert response.status_code == 200
    assert response.json() == {
        "enabled": False,
        "revision": None,
        "digest_sha512": None,
        "runtime_state": None,
        "loaded_context_size": None,
        "model_native_context_limit": None,
        "backend_context_limit": None,
        "deployment_verified_context_limit": None,
        "max_output_token_limit": None,
        "current_max_new_tokens": None,
        "main_model": None,
        "judge_model": None,
        "guard_model": None,
        "governance_layer": None,
        "available_models": [],
    }


@pytest.mark.asyncio
async def test_status_reports_the_bound_snapshot_under_local_exposure(
    local_policy: WebAccessPolicy,
) -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=local_policy)
    async with client_for(app) as client:
        response = await client.get("/api/v4/runtime-model/status")
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    assert body["main_model"]["model_key"] == "main.qwen3-4b-q4-k-m"
    assert body["main_model"]["state"] == "active"
    assert body["judge_model"]["model_key"] is None
    assert body["judge_model"]["state"] == "none"


@pytest.mark.asyncio
async def test_binding_under_non_local_exposure_refuses_to_start(
    non_local_policy: WebAccessPolicy,
) -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=non_local_policy)
    with pytest.raises(RuntimeError, match="local loopback"):
        async with client_for(app):
            pass
