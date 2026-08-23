"""Public/Basic Private Guardrail Control Call-0 regression (P5-F-WU-005,
mirrors `test_runtime_governance_public_basic_call0.py`).

Two invariants are locked down here:

1. If a `WebRuntime` is ever bound with a `guardrail_governance_composition`
   under a non-local exposure mode, the App must refuse to start rather
   than silently exposing Private Guardrail Control — mirroring the
   existing `configuration_control` / `runtime_governance_composition`
   guards in `web/app.py`.
2. In the actual Call-0 state (no Guardrail Governance wiring at all,
   which is what every current entrypoint invocation produces for
   Public/Basic profiles today), the pre-existing `/api/v1/chat/stream`
   behavior is completely unaffected, and the new
   `/api/v3/guardrail-governance/*` routes degrade to a safe, non-leaking
   "unavailable" response instead of 500ing or exposing internals.
"""

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
from margpa_runtime_llm.bootstrap.guardrail_governance import GuardrailGovernanceComposition
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
from margpa_runtime_llm.modules.presentation.application.thinking_presentation_service import (
    ThinkingPresentationService,
)
from margpa_runtime_llm.modules.presentation.contracts.thinking import (
    ResolvedThinkingPresentationPolicy,
    ThinkingPersistence,
    ThinkingPresentationSource,
    ThinkingVisibility,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode
from margpa_runtime_llm.web.access_profiles import WebExposureMode
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
        return "public-basic-call0-generation"

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
                request_id="public-basic-call0-request",
                sequence=sequence,
                text_delta=text,
                is_final=False,
            )
        yield GenerationChunk(
            request_id="public-basic-call0-request",
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
    def __init__(self) -> None:
        self.requests: list[GenerationRequest] = []

    def stream(self, request: GenerationRequest) -> GenerationStream:
        self.requests.append(request)
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


def _conversation(inference: FakeInference) -> ConversationGenerationService:
    return ConversationGenerationService(
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
    )


def call0_runtime(inference: FakeInference) -> WebRuntime:
    """Mirrors what every current entrypoint invocation actually builds for
    Public/Basic: Guardrail Governance is never wired at all."""
    return WebRuntime(
        conversation=_conversation(inference),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        guardrail_governance_composition=None,
    )


def bound_guardrail_runtime(inference: FakeInference) -> WebRuntime:
    """A hypothetical misconfiguration: Guardrail Governance wired even
    though the App is about to be started under a shared exposure mode."""
    return WebRuntime(
        conversation=_conversation(inference),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        guardrail_governance_composition=GuardrailGovernanceComposition(),
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "policy",
    [
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
    ],
)
async def test_shared_exposure_refuses_to_start_with_bound_guardrail_governance(
    policy: WebAccessPolicy,
) -> None:
    inference = FakeInference()
    app = create_web_app(
        runtime_factory=lambda: bound_guardrail_runtime(inference), access_policy=policy
    )
    with pytest.raises(RuntimeError, match="Guardrail governance control requires local"):
        async with app.router.lifespan_context(app):
            pass


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "policy",
    [
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
    ],
)
async def test_public_basic_chat_is_unaffected_by_guardrail_wiring_gap(
    policy: WebAccessPolicy,
) -> None:
    inference = FakeInference()
    app = create_web_app(runtime_factory=lambda: call0_runtime(inference), access_policy=policy)
    async with client_for(app) as client:
        response = await client.post(
            "/api/v1/chat/stream",
            json=_request_payload(),
            auth=("user", "password")
            if policy.mode is WebAuthMode.BASIC
            else httpx.USE_CLIENT_DEFAULT,
        )
    assert response.status_code == 200
    assert "event: completed" in response.text
    assert "a real answer" in response.text
    # Exactly one real Inference call was made — Guardrail added no retry,
    # no pre-flight probe, and no extra call of any kind (P5-MOD-002).
    assert len(inference.requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "policy",
    [
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
    ],
)
async def test_guardrail_governance_routes_degrade_safely_without_leaking(
    policy: WebAccessPolicy,
) -> None:
    inference = FakeInference()
    app = create_web_app(runtime_factory=lambda: call0_runtime(inference), access_policy=policy)
    auth = ("user", "password") if policy.mode is WebAuthMode.BASIC else None
    async with client_for(app) as client:
        status = await client.get("/api/v3/guardrail-governance/status", auth=auth)
    assert status.status_code == 200
    body = status.json()
    assert body == {
        "enabled": False,
        "revision": None,
        "current_mode": None,
        "descriptors": [],
        "points": [],
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "policy",
    [
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
    ],
)
async def test_index_html_never_auto_binds_the_guardrail_bootstrap_without_a_composition(
    policy: WebAccessPolicy,
) -> None:
    inference = FakeInference()
    app = create_web_app(runtime_factory=lambda: call0_runtime(inference), access_policy=policy)
    auth = ("user", "password") if policy.mode is WebAuthMode.BASIC else None
    async with client_for(app) as client:
        response = await client.get("/", auth=auth)
    assert response.status_code == 200
    assert (
        '<script id="guardrail-bootstrap" type="application/json">{"enabled":false}</script>'
        in response.text
    )
