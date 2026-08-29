"""P6-RR-M-WU-002: Main Dropdown drives the real Runtime Switch Transaction.

Reproduces, and verifies the fix for, P6-CODEX-049 / Manual Check M-2
(`PUT /api/v6/provider-selection/main` previously changed only Provider
Selection's Configured value — Main/Sidebar/Model Status kept the old
model). Uses the same Fake backend/definitions pattern as
`test_runtime_model_control_mutation_routes.py` — no real model load.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
    GenerationRequest,
    GenerationStream,
    ThinkingMode,
)
from margpa_runtime_llm.modules.inference.contracts.response import ResponseLanguage
from margpa_runtime_llm.modules.inference.domain.capabilities import MODEL_REQUIRED_CAPABILITIES
from margpa_runtime_llm.modules.inference.domain.model_definition import (
    ModelArtifactDefinition,
    ModelBackendDefinition,
    ModelDefinition,
    ModelExpectedCapabilities,
    ModelMetadataDefinition,
    ModelOutputProtocolDefinition,
    ModelSourceDefinition,
    ModelVerificationDefinition,
    ThinkingOutputProtocolDefinition,
)
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.runtime_model_control.application import (
    DEEPSEEK_MAIN,
    QWEN_MAIN,
    ProviderSelectionController,
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
_LOCAL_POLICY = WebAccessPolicy(exposure_mode=WebExposureMode.LOCAL, mode=WebAuthMode.DISABLED)


class FakeInference:
    def stream(self, request: GenerationRequest) -> GenerationStream:
        raise NotImplementedError


def _conversation() -> ConversationGenerationService:
    presentation_policy = ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )
    return ConversationGenerationService(
        inference=FakeInference(),
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key=QWEN_MAIN,
        generation_defaults=GenerationParameters(
            max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy,
        summarization=SummarizationConfig(),
    )


def _snapshot() -> SafeRuntimeSnapshot:
    return SafeRuntimeSnapshot(
        model_key=QWEN_MAIN,
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


class _FakeBackend:
    def probe_capability(self, *, definition: ModelDefinition) -> CapabilityProbeResult:
        return CapabilityProbeResult(
            native_context_limit=definition.model.native_context_limit,
            backend_context_limit=definition.model.native_context_limit,
            deployment_verified_context_limit=8192,
            max_output_token_limit=8191,
            capability_digest=_SHA512_FILLER,
        )

    def load(self, *, definition: ModelDefinition, context_size: int) -> LoadedModelHandle:
        return LoadedModelHandle(
            backend_identity="llama_cpp",
            artifact_digest=_SHA512_FILLER,
            loaded_context_size=context_size,
            capability=CapabilityProbeResult(
                native_context_limit=8192,
                backend_context_limit=8192,
                deployment_verified_context_limit=8192,
                max_output_token_limit=2048,
                capability_digest=_SHA512_FILLER,
            ),
        )

    def unload(self) -> None:
        return None


class _FakeAccessLease:
    def try_acquire_switch_lease(self, *, task_id: str) -> bool:
        return True

    def release_switch_lease(self, *, task_id: str) -> None:
        pass


def _make_model_definition(*, model_key: str, native_context_limit: int = 8192) -> ModelDefinition:
    return ModelDefinition(
        model_key=model_key,
        logical_role="main",
        enabled=True,
        source=ModelSourceDefinition(
            provider="huggingface",
            distribution_repository="test-org/test-model",
            upstream_model="test-model",
        ),
        artifact=ModelArtifactDefinition(
            relative_path=Path(f"main/{model_key}/gguf/{model_key}.gguf"),
            file_name=f"{model_key}.gguf",
            format="gguf",
            quantization="Q4_K_M",
            size_bytes=1,
            sha512=_SHA512_FILLER,
        ),
        backend=ModelBackendDefinition(backend_key="llama_cpp", required_version=">=0.3.0"),
        model=ModelMetadataDefinition(
            architecture="test-arch",
            native_context_limit=native_context_limit,
            chat_template_source="embedded",
        ),
        capabilities=ModelExpectedCapabilities(required_features=MODEL_REQUIRED_CAPABILITIES),
        verification=ModelVerificationDefinition(state="verified", provenance_complete=True),
        output_protocol=ModelOutputProtocolDefinition(
            thinking=ThinkingOutputProtocolDefinition(parser_key="plain_text_v1")
        ),
        definition_file_sha512=_SHA512_FILLER,
    )


class _FakeDefinitionResolver:
    """Registers only the model_keys listed in `registered` — mirrors a
    real Registry where Provider Selection's static Option list and
    `config/models/*.toml` can genuinely diverge (P6-RR-K Recovery Index)."""

    def __init__(self, *, registered: tuple[str, ...]) -> None:
        self._registered = registered

    def resolve(self, *, model_key: str) -> ModelDefinition:
        if model_key not in self._registered:
            from margpa_runtime_llm.adapters.runtime_model_control.model_definition_registry import (  # noqa: E501
                ModelDefinitionNotRegistered,
            )

            raise ModelDefinitionNotRegistered(model_key=model_key)
        return _make_model_definition(model_key=model_key)

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return tuple(_make_model_definition(model_key=key) for key in self._registered)


def _initial_snapshot() -> RuntimeModelSnapshot:
    binding = RoleBinding(
        role=ModelRole.MAIN,
        model_identity=QWEN_MAIN,
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=_SHA512_FILLER,
    )
    digest = compute_runtime_model_snapshot_digest(
        revision=0,
        selected_model_key=QWEN_MAIN,
        role_bindings=(binding,),
        artifact_identity=QWEN_MAIN,
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=4096,
        current_max_new_tokens=2048,
    )
    return RuntimeModelSnapshot(
        revision=0,
        digest_sha512=digest,
        selected_model_key=QWEN_MAIN,
        role_bindings=(binding,),
        artifact_identity=QWEN_MAIN,
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=4096,
        model_native_context_limit=32768,
        backend_context_limit=32768,
        deployment_verified_context_limit=8192,
        max_output_token_limit=8191,
        current_max_new_tokens=2048,
        last_transition_receipt=None,
    )


def _runtime(*, registered_targets: tuple[str, ...]) -> WebRuntime:
    runtime_model_control = RuntimeModelController(
        initial_snapshot=_initial_snapshot(),
        backend=_FakeBackend(),
        access_lease=_FakeAccessLease(),
        definitions=_FakeDefinitionResolver(registered=registered_targets),
    )
    return WebRuntime(
        conversation=_conversation(),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        runtime_model_control=runtime_model_control,
        provider_selection_control=ProviderSelectionController(current_main_provider=QWEN_MAIN),
    )


def fully_registered_runtime() -> WebRuntime:
    return _runtime(registered_targets=(QWEN_MAIN, DEEPSEEK_MAIN))


def deepseek_unregistered_runtime() -> WebRuntime:
    return _runtime(registered_targets=(QWEN_MAIN,))


def unbound_runtime_model_control() -> WebRuntime:
    return WebRuntime(
        conversation=_conversation(),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        runtime_model_control=None,
        provider_selection_control=ProviderSelectionController(current_main_provider=QWEN_MAIN),
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
async def test_main_dropdown_success_converges_configured_active_and_real_switch() -> None:
    app = create_web_app(runtime_factory=fully_registered_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        before = (await client.get("/api/v6/provider-selection")).json()
        response = await client.put(
            "/api/v6/provider-selection/main",
            json={
                "provider_id": DEEPSEEK_MAIN,
                "expected_revision": before["revision"],
                "expected_digest": before["digest_sha512"],
            },
        )
        model_status = await client.get("/api/v4/runtime-model/status")
    assert response.status_code == 200
    body = response.json()
    main = next(item for item in body["selections"] if item["role"] == "main")
    assert main["configured_provider"] == DEEPSEEK_MAIN
    assert main["active_provider"] == DEEPSEEK_MAIN
    assert main["state"] == "active"
    assert model_status.json()["main_model"]["model_key"] == DEEPSEEK_MAIN


@pytest.mark.asyncio
async def test_main_dropdown_failure_keeps_old_active_and_reports_exact_reason() -> None:
    """P6-CODEX-049/P6-DELTA-002: Provider Selection's static Option list
    (QWEN_MAIN/DEEPSEEK_MAIN) can diverge from what `RuntimeModelController`
    actually has registered — the failure must not silently leave a stale
    Configured value with no explanation, and Main/Sidebar/Model Status
    must keep reporting the model that is genuinely still running."""
    app = create_web_app(runtime_factory=deepseek_unregistered_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        before = (await client.get("/api/v6/provider-selection")).json()
        response = await client.put(
            "/api/v6/provider-selection/main",
            json={
                "provider_id": DEEPSEEK_MAIN,
                "expected_revision": before["revision"],
                "expected_digest": before["digest_sha512"],
            },
        )
        canonical = await client.get("/api/v6/provider-selection")
        model_status = await client.get("/api/v4/runtime-model/status")
    assert response.status_code == 409
    assert response.json()["code"] == "provider_selection_activation_failed"
    main = next(item for item in canonical.json()["selections"] if item["role"] == "main")
    assert main["configured_provider"] == DEEPSEEK_MAIN
    assert main["active_provider"] == QWEN_MAIN
    assert main["state"] == "unavailable"
    assert main["failure_reason"] == "main_switch_failed:RuntimeModelTargetNotRegistered"
    assert model_status.json()["main_model"]["model_key"] == QWEN_MAIN


@pytest.mark.asyncio
async def test_main_dropdown_reselecting_current_model_is_a_no_op_switch() -> None:
    app = create_web_app(runtime_factory=fully_registered_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        before = (await client.get("/api/v6/provider-selection")).json()
        response = await client.put(
            "/api/v6/provider-selection/main",
            json={
                "provider_id": QWEN_MAIN,
                "expected_revision": before["revision"],
                "expected_digest": before["digest_sha512"],
            },
        )
    assert response.status_code == 200
    main = next(item for item in response.json()["selections"] if item["role"] == "main")
    assert main["configured_provider"] == QWEN_MAIN
    assert main["active_provider"] == QWEN_MAIN
    assert main["state"] == "active"


@pytest.mark.asyncio
async def test_main_dropdown_without_runtime_model_control_reports_unavailable() -> None:
    app = create_web_app(runtime_factory=unbound_runtime_model_control, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        before = (await client.get("/api/v6/provider-selection")).json()
        response = await client.put(
            "/api/v6/provider-selection/main",
            json={
                "provider_id": DEEPSEEK_MAIN,
                "expected_revision": before["revision"],
                "expected_digest": before["digest_sha512"],
            },
        )
    assert response.status_code == 409
    assert response.json()["code"] == "provider_selection_activation_failed"
