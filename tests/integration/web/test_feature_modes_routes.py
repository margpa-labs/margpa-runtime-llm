"""Feature Modes (Judge/Repair/Recording) routes (Phase 6-G-WU-004).

Each Mode Controller is independent (Acceptance P6-ACC-025): applying one
must never move another. All three Default OFF.
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
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
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
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode
from margpa_runtime_llm.web.access_profiles import WebExposureMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import RuntimeDefaults, SafeRuntimeSnapshot, WebRuntime

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


def bound_runtime() -> WebRuntime:
    return WebRuntime(
        conversation=_conversation(),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        judge_mode_control=JudgeModeController(),
        repair_mode_control=RepairModeController(),
        recording_mode_control=RecordingModeController(),
    )


def unbound_runtime() -> WebRuntime:
    return WebRuntime(
        conversation=_conversation(), snapshot=_snapshot(), close_callback=lambda: None
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
async def test_status_degrades_safely_when_unbound() -> None:
    app = create_web_app(runtime_factory=unbound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v5/feature-modes/status")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "judge": {
            "enabled": False,
            "revision": None,
            "current_mode": None,
            "state": None,
            "current_request_id": None,
            "last_result": None,
        },
        "repair": {"enabled": False, "revision": None, "current_mode": None},
        "recording": {
            "enabled": False,
            "revision": None,
            "current_mode": None,
            "last_outcome": None,
            "judge_evidence_last_outcome": None,
        },
    }


@pytest.mark.asyncio
async def test_all_three_modes_default_off_when_bound() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v5/feature-modes/status")
    body = response.json()
    assert body["judge"]["current_mode"] == "off"
    assert body["repair"]["current_mode"] == "off"
    assert body["recording"]["current_mode"] == "off"


@pytest.mark.asyncio
async def test_applying_judge_mode_never_moves_repair_or_recording() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.post(
            "/api/v5/feature-modes/judge", json={"requested_mode": "enforce"}
        )
    body = response.json()
    assert body["judge"]["current_mode"] == "enforce"
    assert body["judge"]["revision"] == 2
    assert body["repair"]["current_mode"] == "off"
    assert body["recording"]["current_mode"] == "off"


@pytest.mark.asyncio
async def test_applying_repair_mode_never_moves_judge_or_recording() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.post(
            "/api/v5/feature-modes/repair", json={"requested_mode": "observe"}
        )
    body = response.json()
    assert body["repair"]["current_mode"] == "observe"
    assert body["judge"]["current_mode"] == "off"
    assert body["recording"]["current_mode"] == "off"


@pytest.mark.asyncio
async def test_applying_recording_mode_never_moves_judge_or_repair() -> None:
    app = create_web_app(runtime_factory=bound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.post(
            "/api/v5/feature-modes/recording", json={"requested_mode": "full"}
        )
    body = response.json()
    assert body["recording"]["current_mode"] == "full"
    assert body["judge"]["current_mode"] == "off"
    assert body["repair"]["current_mode"] == "off"


@pytest.mark.asyncio
async def test_apply_on_an_unbound_controller_is_a_no_op_not_a_500() -> None:
    app = create_web_app(runtime_factory=unbound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.post(
            "/api/v5/feature-modes/judge", json={"requested_mode": "enforce"}
        )
    assert response.status_code == 200
    assert response.json()["judge"]["enabled"] is False


@pytest.mark.asyncio
async def test_status_projects_a_real_judge_result_including_repair_fields() -> None:
    """P6-CODEX-012 (Second Rework): the Frontend contract must actually
    carry Repair Outcome/Acceptance/new-Turn correlation and the Current
    Request state — not just the pre-existing bare Recommendation fields."""
    from margpa_runtime_llm.bootstrap.judge_live_integration import (
        JudgeGovernanceComposition,
        LiveJudgeResult,
    )
    from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass

    composition = JudgeGovernanceComposition()
    composition.mark_running(request_id="req-42")
    composition.record_result(
        LiveJudgeResult(
            request_id="req-42",
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            recommendation="needs_repair",
            confidence=0.4,
            execution_state="completed",
            failure_reason=None,
            repair_eligibility="eligible",
            repair_outcome="improved",
            repair_accepted=True,
            repair_new_turn_id="turn-repaired-1",
        )
    )

    def runtime_factory() -> WebRuntime:
        runtime = bound_runtime()
        runtime.judge_governance_composition = composition
        return runtime

    app = create_web_app(runtime_factory=runtime_factory, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v5/feature-modes/status")
    body = response.json()

    judge = body["judge"]
    assert judge["state"] == "completed"
    assert judge["current_request_id"] == "req-42"
    result = judge["last_result"]
    assert result["recommendation"] == "needs_repair"
    assert result["repair_eligibility"] == "eligible"
    assert result["repair_outcome"] == "improved"
    assert result["repair_accepted"] is True
    assert result["repair_new_turn_id"] == "turn-repaired-1"


@pytest.mark.asyncio
async def test_status_projects_real_recording_outcomes_for_both_writers() -> None:
    from margpa_runtime_llm.bootstrap.recording_live_integration import (
        RecordingCompositionState,
    )

    recording_composition = RecordingCompositionState()
    recording_composition.record_ok(request_id="req-1")
    judge_evidence_composition = RecordingCompositionState()
    judge_evidence_composition.record_degraded(
        request_id="req-1-judge-evidence", reason="RecordingQuotaExceeded: over limit"
    )

    def runtime_factory() -> WebRuntime:
        runtime = bound_runtime()
        runtime.recording_composition = recording_composition
        runtime.judge_evidence_recording_composition = judge_evidence_composition
        return runtime

    app = create_web_app(runtime_factory=runtime_factory, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v5/feature-modes/status")
    body = response.json()

    recording = body["recording"]
    assert recording["last_outcome"] == {
        "request_id": "req-1",
        "ok": True,
        "degraded_reason": None,
    }
    assert recording["judge_evidence_last_outcome"] == {
        "request_id": "req-1-judge-evidence",
        "ok": False,
        "degraded_reason": "RecordingQuotaExceeded: over limit",
    }
