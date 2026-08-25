"""Runtime Model Control CAS-guarded Mutation routes (Phase 6-G-WU-003).

`/api/v4/runtime-model/context` and `/max-new-tokens` — success, stale CAS
(409), and limit-exceeded (422) paths, against a Fake backend/controller
(no real model load; that stays reserved for 6-I).
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
        model_key="main.qwen3-4b-q4-k-m",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy,
        summarization=SummarizationConfig(),
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


class _FakeBackend:
    def __init__(self) -> None:
        self.load_calls: list[tuple[str, int]] = []
        self.unload_calls = 0

    def probe_capability(self, *, definition: ModelDefinition) -> CapabilityProbeResult:
        return CapabilityProbeResult(
            native_context_limit=definition.model.native_context_limit,
            backend_context_limit=definition.model.native_context_limit,
            deployment_verified_context_limit=8192,
            max_output_token_limit=8191,
            capability_digest=_SHA512_FILLER,
        )

    def load(self, *, definition: ModelDefinition, context_size: int) -> LoadedModelHandle:
        self.load_calls.append((definition.model_key, context_size))
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
        self.unload_calls += 1


class _FakeAccessLease:
    """P6-CODEX-034 (Fifth Rework): replaces the retired `_FakeBusyGate` —
    mirrors the real `ModelAccessCoordinator`'s exclusive-lease Port."""

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
    def resolve(self, *, model_key: str) -> ModelDefinition:
        return _make_model_definition(model_key=model_key)

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return (
            _make_model_definition(model_key="main.qwen3-4b-q4-k-m", native_context_limit=32768),
            _make_model_definition(model_key="main.deepseek-test", native_context_limit=131072),
        )


def _initial_snapshot() -> RuntimeModelSnapshot:
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
    return RuntimeModelSnapshot(
        revision=0,
        digest_sha512=digest,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=(binding,),
        artifact_identity="main.qwen3-4b-q4-k-m",
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


def bound_runtime() -> WebRuntime:
    controller = RuntimeModelController(
        initial_snapshot=_initial_snapshot(),
        backend=_FakeBackend(),
        access_lease=_FakeAccessLease(),
        definitions=_FakeDefinitionResolver(),
    )
    return WebRuntime(
        conversation=_conversation(),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        runtime_model_control=controller,
    )


def unbound_runtime() -> WebRuntime:
    return WebRuntime(
        conversation=_conversation(),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        runtime_model_control=None,
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
async def test_context_change_succeeds_and_reflects_in_the_next_status() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        status_before = await client.get("/api/v4/runtime-model/status")
        body_before = status_before.json()
        response = await client.post(
            "/api/v4/runtime-model/context",
            json={
                "expected_revision": body_before["revision"],
                "expected_digest": body_before["digest_sha512"],
                "requested_context_size": 8192,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["loaded_context_size"] == 8192
    assert body["revision"] == body_before["revision"] + 1


@pytest.mark.asyncio
async def test_context_change_with_a_stale_digest_is_a_409_conflict() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.post(
            "/api/v4/runtime-model/context",
            json={
                "expected_revision": 0,
                "expected_digest": "0" * 128,
                "requested_context_size": 8192,
            },
        )
    assert response.status_code == 409
    assert response.json()["code"] == "runtime_model_revision_conflict"


@pytest.mark.asyncio
async def test_context_change_above_the_effective_max_is_a_422() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        status_before = await client.get("/api/v4/runtime-model/status")
        body_before = status_before.json()
        response = await client.post(
            "/api/v4/runtime-model/context",
            json={
                "expected_revision": body_before["revision"],
                "expected_digest": body_before["digest_sha512"],
                "requested_context_size": 999999,
            },
        )
    assert response.status_code == 422
    assert response.json()["code"] == "runtime_model_limit_exceeded"


@pytest.mark.asyncio
async def test_max_new_tokens_change_succeeds() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        status_before = await client.get("/api/v4/runtime-model/status")
        body_before = status_before.json()
        response = await client.post(
            "/api/v4/runtime-model/max-new-tokens",
            json={
                "expected_revision": body_before["revision"],
                "expected_digest": body_before["digest_sha512"],
                "requested_max_new_tokens": 1024,
            },
        )
    assert response.status_code == 200
    assert response.json()["current_max_new_tokens"] == 1024


@pytest.mark.asyncio
async def test_max_new_tokens_above_the_limit_is_a_422() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        status_before = await client.get("/api/v4/runtime-model/status")
        body_before = status_before.json()
        response = await client.post(
            "/api/v4/runtime-model/max-new-tokens",
            json={
                "expected_revision": body_before["revision"],
                "expected_digest": body_before["digest_sha512"],
                "requested_max_new_tokens": 999999,
            },
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_status_lists_available_models_from_the_registry() -> None:
    """P6-CODEX-026 (Fourth Rework): the Switch surface's candidate list
    comes from `RuntimeModelController.available_models()`, not a
    hardcoded UI list."""
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v4/runtime-model/status")
    body = response.json()
    assert {entry["model_key"] for entry in body["available_models"]} == {
        "main.qwen3-4b-q4-k-m",
        "main.deepseek-test",
    }
    by_key = {entry["model_key"]: entry for entry in body["available_models"]}
    assert by_key["main.qwen3-4b-q4-k-m"]["native_context_limit"] == 32768
    assert by_key["main.deepseek-test"]["native_context_limit"] == 131072
    assert {entry["effective_context_limit"] for entry in body["available_models"]} == {8192}
    assert body["effective_context_limit"] == 8192
    assert body["minimum_context_size"] == 512
    assert body["context_limit_reason_code"] == "deployment_hardware_verified_limit"


@pytest.mark.asyncio
async def test_switch_succeeds_and_updates_the_selected_model() -> None:
    """P6-CODEX-025/026 (Fourth Rework): the central regression this whole
    Rework exists to close — a successful `/switch` must both update the
    Snapshot's `selected_model_key` AND (verified separately at the
    `ConversationGenerationService` unit level, see
    `test_conversation_generation_runtime_snapshot.py`) make the next real
    Turn's `GenerationRequest.model_key` follow it, never staying frozen at
    the old value."""
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        status_before = await client.get("/api/v4/runtime-model/status")
        body_before = status_before.json()
        response = await client.post(
            "/api/v4/runtime-model/switch",
            json={
                "expected_revision": body_before["revision"],
                "expected_digest": body_before["digest_sha512"],
                "target_model_key": "main.deepseek-test",
                "requested_context_size": 4096,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert body["main_model"]["model_key"] == "main.deepseek-test"
    assert body["revision"] == body_before["revision"] + 1


@pytest.mark.asyncio
async def test_switch_to_an_unregistered_target_is_a_404_not_a_fabricated_load() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        status_before = await client.get("/api/v4/runtime-model/status")
        body_before = status_before.json()
        response = await client.post(
            "/api/v4/runtime-model/switch",
            json={
                "expected_revision": body_before["revision"],
                "expected_digest": body_before["digest_sha512"],
                "target_model_key": "main.does-not-exist",
                "requested_context_size": 4096,
            },
        )
    assert response.status_code == 404
    assert response.json()["code"] == "runtime_model_target_not_registered"


@pytest.mark.asyncio
async def test_switch_with_a_stale_digest_is_a_409_conflict() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.post(
            "/api/v4/runtime-model/switch",
            json={
                "expected_revision": 0,
                "expected_digest": "0" * 128,
                "target_model_key": "main.deepseek-test",
                "requested_context_size": 4096,
            },
        )
    assert response.status_code == 409
    assert response.json()["code"] == "runtime_model_revision_conflict"


@pytest.mark.asyncio
async def test_mutation_on_an_unbound_runtime_is_a_404_not_a_500() -> None:
    app = create_web_app(runtime_factory=unbound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.post(
            "/api/v4/runtime-model/context",
            json={
                "expected_revision": 0,
                "expected_digest": "0" * 128,
                "requested_context_size": 4096,
            },
        )
    assert response.status_code == 404
    assert response.json()["code"] == "runtime_model_control_not_enabled"
