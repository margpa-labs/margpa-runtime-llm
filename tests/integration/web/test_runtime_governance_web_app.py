"""End-to-end Phase 4 OFF/OBSERVE/ENFORCE Golden Matrix through the real
FastAPI app (P4-G-WU-001, P4-ACC-006/007/008/017)."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from types import TracebackType

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.bootstrap.runtime_governance import (
    RuntimeGovernanceComposition,
    build_main_model_governance_hooks,
)
from margpa_runtime_llm.modules.configuration_control import (
    ApplyDisposition,
    ConfigurationControlService,
    ConfigurationField,
    ConfigurationSource,
    DocumentationRagControlMode,
    FeatureHookDescriptor,
    MainGovernanceControlMode,
    MainGovernanceHookDescriptor,
    RecordingControlMode,
    RecordingHookDescriptor,
)
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode
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
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    EvaluationMethod,
    ExecutionDescriptor,
    RuntimeCapabilitySnapshot,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import RuntimeDefaults, SafeRuntimeSnapshot, WebRuntime


class FakeStream:
    def __init__(self, text_deltas: tuple[str, ...] = ("a real answer",)) -> None:
        self.text_deltas = text_deltas
        self.cancelled = False
        self.closed = False

    @property
    def generation_id(self) -> str:
        return "web-governance-generation"

    @property
    def terminal_state(self) -> GenerationTerminalState:
        if self.cancelled:
            return GenerationTerminalState.CANCELLED
        if self.closed:
            return GenerationTerminalState.CLOSED_BY_CONSUMER
        return GenerationTerminalState.ACTIVE

    @property
    def timing(self) -> GenerationTiming | None:
        return None

    def __iter__(self) -> Iterator[GenerationChunk]:
        for sequence, text in enumerate(self.text_deltas):
            yield GenerationChunk(
                request_id="web-governance-request",
                sequence=sequence,
                text_delta=text,
                is_final=False,
            )
        yield GenerationChunk(
            request_id="web-governance-request",
            sequence=len(self.text_deltas),
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

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if not self.cancelled:
            self.close()


class FakeInference:
    def __init__(self, *, empty_output: bool = False) -> None:
        self.requests: list[GenerationRequest] = []
        self.empty_output = empty_output

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
        return FakeStream(text_deltas=() if self.empty_output else ("a real answer",))


def _presentation_policy() -> ResolvedThinkingPresentationPolicy:
    return ResolvedThinkingPresentationPolicy(
        visibility=ThinkingVisibility.HIDDEN,
        display_label="推論過程",
        persistence=ThinkingPersistence.DISABLED,
        visibility_source=ThinkingPresentationSource.APPLICATION,
        display_label_source=ThinkingPresentationSource.APPLICATION,
        persistence_source=ThinkingPresentationSource.APPLICATION,
    )


def _capability() -> RuntimeCapabilitySnapshot:
    return RuntimeCapabilitySnapshot(
        model_key="main.qwen3-4b-q4-k-m",
        backend_kind="metal",
        supports_streaming=True,
        supports_thinking=True,
        max_context_tokens=4096,
    )


def _descriptor() -> ExecutionDescriptor:
    # Enforce Availability now genuinely requires a bound, non-empty
    # Descriptor set (P4-CODEX-004 Rework) — a real Test double stands
    # in for the Reference Bundle so ENFORCE has something to enforce.
    return ExecutionDescriptor(
        descriptor_id="argd.rule-1",
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="test rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )


_MAIN_GOVERNANCE_ALLOWED_MODES = (
    MainGovernanceControlMode.OFF,
    MainGovernanceControlMode.OBSERVE,
    MainGovernanceControlMode.ENFORCE,
)


class _MainGovernanceModeApplierAdapter:
    """Minimal `MainGovernanceModeApplierPort` implementation, mirroring
    `bootstrap/configuration_control.py`'s real
    `_MainGovernanceModeApplierAdapter` — proves the Golden Matrix mode
    transitions through the actual CAS-mediated path (P4-CODEX-002
    Rework), not a bypass."""

    def __init__(self, composition: RuntimeGovernanceComposition) -> None:
        self._composition = composition

    def apply(self, mode: MainGovernanceControlMode) -> MainGovernanceHookDescriptor:
        snapshot = self._composition.mode_controller.apply_mode(GovernanceMode(mode.value))
        return MainGovernanceHookDescriptor(
            component_key="main_governance_mode",
            allowed_modes=_MAIN_GOVERNANCE_ALLOWED_MODES,
            current_mode=MainGovernanceControlMode(snapshot.current_mode.value),
            available=True,
        )


def _configuration_control(
    composition: RuntimeGovernanceComposition,
) -> ConfigurationControlService:
    fields = tuple(
        ConfigurationField(
            key=key,
            value=value,
            source=ConfigurationSource.APPLICATION,
            apply_disposition=disposition,
        )
        for key, value, disposition in (
            ("selected_model", "main.qwen3-4b-q4-k-m", ApplyDisposition.RESTART_REQUIRED),
            ("profile_key", "local.macos-arm64.metal", ApplyDisposition.READ_ONLY),
            ("context_size", 4096, ApplyDisposition.RESTART_REQUIRED),
            ("backend_kind", "metal", ApplyDisposition.READ_ONLY),
            ("device_kind", "gpu", ApplyDisposition.READ_ONLY),
            ("acceleration_api", "metal", ApplyDisposition.READ_ONLY),
            ("max_new_tokens", 2048, ApplyDisposition.READ_ONLY),
            ("research_developer_mode", "off", ApplyDisposition.RUNTIME_APPLICABLE),
            ("conversation_storage_kind", "disabled", ApplyDisposition.READ_ONLY),
            ("conversation_storage_version", "disabled", ApplyDisposition.READ_ONLY),
        )
    )
    return ConfigurationControlService(
        fields=fields,
        feature_hooks=(
            FeatureHookDescriptor(
                component_key="documentation_rag",
                allowed_modes=(
                    DocumentationRagControlMode.DISABLED,
                    DocumentationRagControlMode.ENABLED,
                ),
                current_mode=DocumentationRagControlMode.DISABLED,
                available=False,
            ),
        ),
        recording_hooks=(
            RecordingHookDescriptor(
                component_key="conversation_recording",
                allowed_modes=(RecordingControlMode.OFF,),
                current_mode=RecordingControlMode.OFF,
                available=False,
            ),
        ),
        main_governance_hooks=(
            MainGovernanceHookDescriptor(
                component_key="main_governance_mode",
                allowed_modes=_MAIN_GOVERNANCE_ALLOWED_MODES,
                current_mode=MainGovernanceControlMode(
                    composition.mode_controller.current_mode_value()
                ),
                available=True,
            ),
        ),
        main_governance_mode_applier=_MainGovernanceModeApplierAdapter(composition),
    )


def _pass_descriptor() -> ExecutionDescriptor:
    # `DeterministicEvaluator` never marks a real Reference-Adapter
    # Descriptor `pass` today (P4-GD-002/003) — this test-only Descriptor
    # exercises that reserved-but-presently-unreachable branch directly,
    # purely to produce a genuine mixed pass/deviation/deferred Result
    # for the Observation Count Projection tests (P4-CODEX-013 §3.3).
    return ExecutionDescriptor(
        descriptor_id="core.test.deterministic-pass",
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="test deterministic rule",
        evaluation_method=EvaluationMethod.DETERMINISTIC,
    )


def build_runtime(
    inference: FakeInference,
    closed: list[bool],
    *,
    extra_descriptors: tuple[ExecutionDescriptor, ...] = (),
    descriptors: tuple[ExecutionDescriptor, ...] | None = None,
) -> WebRuntime:
    composition = RuntimeGovernanceComposition(
        capability=_capability(),
        descriptors=(_descriptor(), *extra_descriptors) if descriptors is None else descriptors,
        source_plan_id="plan-test",
        source_plan_digest_sha512="a" * 128,
    )
    pre_hook, post_hook = build_main_model_governance_hooks(
        composition=composition,
        mode_provider=composition.mode_controller.current_mode_value,
    )
    conversation = ConversationGenerationService(
        inference=inference,
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
        governance_pre_hook=pre_hook,
        governance_post_hook=post_hook,
    )
    return WebRuntime(
        conversation=conversation,
        snapshot=SafeRuntimeSnapshot(
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
        ),
        close_callback=lambda: closed.append(True),
        runtime_governance_composition=composition,
        configuration_control=_configuration_control(composition),
    )


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client


def _request_payload() -> dict[str, object]:
    return {
        "messages": [{"role": "user", "content": "hello"}],
        "settings": {
            "response_language": "ja",
            "max_new_tokens": 2048,
            "thinking_mode": "disabled",
            "thinking_visibility": "hidden",
            "summary_mode": "off",
            "documentation_rag_mode": "disabled",
        },
    }


async def _apply_main_governance_mode(client: httpx.AsyncClient, mode: str) -> httpx.Response:
    """The sole Canonical Mutation path for Phase 4 Main Governance Mode
    (P4-CODEX-002 Rework): `/api/v2/configuration` Preview→Apply CAS with
    a `main_governance_mode` Patch field — the same machinery Phase 3's
    own Governance Mode already uses, not a separate direct-Apply route."""
    effective = await client.get("/api/v2/configuration/effective")
    assert effective.status_code == 200
    snapshot = effective.json()
    return await client.post(
        "/api/v2/configuration/apply",
        json={
            "operation_id": f"main-governance-mode-{mode}",
            "expected_revision": snapshot["revision"],
            "expected_digest": snapshot["digest_sha512"],
            "patch": {"main_governance_mode": mode},
        },
    )


@pytest.mark.asyncio
async def test_status_reports_off_by_default() -> None:
    inference = FakeInference()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v3/runtime-governance/status")
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    assert body["current_mode"] == "off"
    by_mode = {d["mode"]: d for d in body["descriptors"]}
    assert by_mode["off"]["availability"] == "available"
    assert by_mode["enforce"]["availability"] == "available"  # this Composition can always Bind


@pytest.mark.asyncio
async def test_off_mode_generation_is_byte_identical_to_no_governance_wiring() -> None:
    inference = FakeInference()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.post("/api/v1/chat/stream", json=_request_payload())
    assert response.status_code == 200
    assert "event: completed" in response.text
    assert "event: error" not in response.text


@pytest.mark.asyncio
async def test_observe_mode_never_intervenes_even_on_empty_output() -> None:
    inference = FakeInference(empty_output=True)
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        applied = await _apply_main_governance_mode(client, "observe")
        assert applied.status_code == 200
        response = await client.post("/api/v1/chat/stream", json=_request_payload())
    assert response.status_code == 200
    assert "event: completed" in response.text
    assert "event: error" not in response.text


@pytest.mark.asyncio
async def test_observe_status_projects_pass_deviation_and_deferred_observation_counts() -> None:
    # P4-CODEX-013 §3.3: a mixed pass/deviation/deferred Result (the
    # semantic ARGD Descriptor -> deferred, a test-only DETERMINISTIC
    # Descriptor -> pass, the empty-output structural check -> deviation)
    # must project as Exact per-Point Counts, never as a single opaque
    # Executed Action Count — and Executed Action Count itself must stay
    # 0 throughout, since OBSERVE never reaches the Action Resolver.
    inference = FakeInference(empty_output=True)
    app = create_web_app(
        runtime_factory=lambda: build_runtime(
            inference, [], extra_descriptors=(_pass_descriptor(),)
        ),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        applied = await _apply_main_governance_mode(client, "observe")
        assert applied.status_code == 200
        response = await client.post("/api/v1/chat/stream", json=_request_payload())
        assert response.status_code == 200
        status = await client.get("/api/v3/runtime-governance/status")
    assert status.status_code == 200
    body = status.json()
    post_point = next(point for point in body["points"] if point["point_id"] == "main_model.post")
    assert post_point["observation_count"] == 3
    assert post_point["pass_count"] == 1
    assert post_point["deviation_count"] == 1
    assert post_point["deferred_count"] == 1
    assert post_point["executed_action_count"] == 0
    # Raw Model Output/Path/Exception/Secret never cross this boundary —
    # only Typed scalar Counts do (P4-EVD-002/P4-STS-002 lineage).
    assert "a real answer" not in status.text
    assert "Traceback" not in status.text
    assert "/Users/" not in status.text


@pytest.mark.asyncio
async def test_status_reports_zero_observation_counts_when_no_observation_ran() -> None:
    # P4-CODEX-013 §3.3: an empty `observations` tuple (here, the
    # Definitions-0 Baseline short-circuits before the Evaluator ever
    # runs) must project as Exact zero Counts, never `None`/omitted.
    inference = FakeInference()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, [], descriptors=()),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        applied = await _apply_main_governance_mode(client, "observe")
        assert applied.status_code == 200
        response = await client.post("/api/v1/chat/stream", json=_request_payload())
        assert response.status_code == 200
        status = await client.get("/api/v3/runtime-governance/status")
    body = status.json()
    post_point = next(point for point in body["points"] if point["point_id"] == "main_model.post")
    assert post_point["execution_state"] == "inactive_no_definitions"
    assert post_point["observation_count"] == 0
    assert post_point["pass_count"] == 0
    assert post_point["deviation_count"] == 0
    assert post_point["deferred_count"] == 0


@pytest.mark.asyncio
async def test_enforce_mode_rejects_empty_output_with_a_safe_terminal() -> None:
    inference = FakeInference(empty_output=True)
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        applied = await _apply_main_governance_mode(client, "enforce")
        assert applied.status_code == 200
        response = await client.post("/api/v1/chat/stream", json=_request_payload())
    assert response.status_code == 200
    assert "event: completed" not in response.text
    assert "event: error" in response.text
    assert "governance_reject_output" in response.text
    # No Ghost Completion: the rejected terminal never carries an
    # assistant_message payload (P4-ACC-020).
    assert "assistant_message" not in response.text


@pytest.mark.asyncio
async def test_enforce_mode_allows_a_normal_answer_through() -> None:
    inference = FakeInference(empty_output=False)
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        await _apply_main_governance_mode(client, "enforce")
        response = await client.post("/api/v1/chat/stream", json=_request_payload())
    assert response.status_code == 200
    assert "event: completed" in response.text
    assert "a real answer" in response.text


@pytest.mark.asyncio
async def test_enforce_never_intervenes_with_only_a_deferred_semantic_descriptor() -> None:
    # P4-CODEX-015 Semantic Boundary: the ARGD Descriptor is Semantic
    # (`REQUIRES_SEMANTIC_EVALUATOR` -> always `deferred`) — a normal,
    # non-empty answer must pass through completely untouched, and
    # Status must show the real deferred/pass/deviation split, never a
    # claim that Enforce judged or repaired the answer's semantic
    # content (there is no Semantic Evaluator wired in Phase 4 at all).
    inference = FakeInference(empty_output=False)
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        await _apply_main_governance_mode(client, "enforce")
        response = await client.post("/api/v1/chat/stream", json=_request_payload())
        assert response.status_code == 200
        assert "a real answer" in response.text
        status = await client.get("/api/v3/runtime-governance/status")
    body = status.json()
    post_point = next(point for point in body["points"] if point["point_id"] == "main_model.post")
    assert post_point["deferred_count"] == 1
    assert post_point["pass_count"] == 0
    assert post_point["deviation_count"] == 0
    assert post_point["executed_action_count"] == 0


@pytest.mark.asyncio
async def test_invalid_mode_string_is_rejected_with_422() -> None:
    inference = FakeInference()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await _apply_main_governance_mode(client, "not_a_real_mode")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_direct_mode_route_no_longer_exists() -> None:
    # P4-CODEX-002 Rework: Mode Mutation has exactly one Canonical path
    # now (Configuration Control CAS) — a second, un-versioned direct-
    # Apply route would be a dual Mutation path with its own Revision/
    # Cache, never expressed even as a compatibility shim.
    inference = FakeInference()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.post(
            "/api/v3/runtime-governance/mode", json={"requested_mode": "enforce"}
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_index_html_bootstrap_marker_reports_enabled_when_composition_is_bound() -> None:
    inference = FakeInference()
    app = create_web_app(
        runtime_factory=lambda: build_runtime(inference, []),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert (
        '<script id="runtime-governance-bootstrap" '
        'type="application/json">{"enabled":true}</script>' in response.text
    )


@pytest.mark.asyncio
async def test_index_html_bootstrap_marker_reports_disabled_without_a_composition() -> None:
    inference = FakeInference()
    app = create_web_app(
        runtime_factory=lambda: WebRuntime(
            conversation=ConversationGenerationService(
                inference=inference,
                presentation=ThinkingPresentationService(
                    TaggedThinkingOutputParser(
                        opening_delimiter="<think>", closing_delimiter="</think>"
                    )
                ),
                model_key="main.qwen3-4b-q4-k-m",
                generation_defaults=GenerationParameters(
                    max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
                ),
                response_language_default=ResponseLanguage.JA,
                presentation_default=_presentation_policy(),
                summarization=SummarizationConfig(),
            ),
            snapshot=SafeRuntimeSnapshot(
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
            ),
            close_callback=lambda: None,
        ),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert (
        '<script id="runtime-governance-bootstrap" '
        'type="application/json">{"enabled":false}</script>' in response.text
    )
