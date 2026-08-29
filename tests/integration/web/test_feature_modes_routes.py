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
from margpa_runtime_llm.adapters.runtime_model_control.unavailable_role_adapters import (
    UnavailableRoleAdapterFactory,
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
from margpa_runtime_llm.modules.runtime_model_control.application import (
    BUILT_IN_JUDGE,
    ProviderSelectionController,
    RoleProviderLifecycleManager,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
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


def lifecycle_runtime(*, built_in_judge: bool) -> WebRuntime:
    runtime = bound_runtime()
    selections = ProviderSelectionController()
    if built_in_judge:
        snapshot = selections.snapshot()
        selections.select(
            role=ModelRole.JUDGE,
            provider_id=BUILT_IN_JUDGE,
            expected_revision=snapshot.revision,
            expected_digest=snapshot.digest_sha512,
        )
    runtime.provider_selection_control = selections
    runtime.role_provider_lifecycle = RoleProviderLifecycleManager(
        selections=selections,
        factory=UnavailableRoleAdapterFactory(reason="fixture_artifact_unavailable"),
    )
    return runtime


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
            "historical_last_result": None,
        },
        "repair": {"enabled": False, "revision": None, "current_mode": None},
        "recording": {
            "enabled": False,
            "revision": None,
            "current_mode": None,
            "last_outcome": None,
            "judge_evidence_last_outcome": None,
            "correlation": None,
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
async def test_judge_mode_activation_commits_only_after_selected_provider_is_active() -> None:
    app = create_web_app(
        runtime_factory=lambda: lifecycle_runtime(built_in_judge=True),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        enabled = await client.post(
            "/api/v5/feature-modes/judge", json={"requested_mode": "observe"}
        )
        disabled = await client.post("/api/v5/feature-modes/judge", json={"requested_mode": "off"})
    assert enabled.status_code == 200
    assert enabled.json()["judge"]["current_mode"] == "observe"
    assert disabled.status_code == 200
    assert disabled.json()["judge"]["current_mode"] == "off"


@pytest.mark.asyncio
async def test_unavailable_selected_judge_rejects_mode_activation_without_fallback() -> None:
    app = create_web_app(
        runtime_factory=lambda: lifecycle_runtime(built_in_judge=False),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        response = await client.post(
            "/api/v5/feature-modes/judge", json={"requested_mode": "enforce"}
        )
        status = await client.get("/api/v5/feature-modes/status")
    assert response.status_code == 409
    assert response.json()["code"] == "provider_selection_activation_failed"
    assert status.json()["judge"]["current_mode"] == "off"


@pytest.mark.asyncio
async def test_provider_selection_get_exposes_three_roles_options_state_and_budget() -> None:
    app = create_web_app(
        runtime_factory=lambda: lifecycle_runtime(built_in_judge=False),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        response = await client.get("/api/v6/provider-selection")
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    assert {item["role"] for item in body["selections"]} == {"main", "guard", "judge"}
    assert {(item["role"], item["provider_id"]) for item in body["options"]} >= {
        ("main", "main.qwen3-4b-q4-k-m"),
        ("guard", "none"),
        ("guard", "built_in.rule_pattern"),
        ("guard", "guard.qwen3guard-gen-0.6b-q8-0"),
        ("judge", "none"),
        ("judge", "built_in.deterministic"),
        ("judge", "judge.selene-1-mini-llama-3.1-8b-q5-k-m"),
    }
    judge = next(item for item in body["selections"] if item["role"] == "judge")
    assert judge["configured_provider"] == "judge.selene-1-mini-llama-3.1-8b-q5-k-m"
    assert judge["active_provider"] is None
    assert judge["state"] == "configured"
    assert judge["independence"] == "independent_other_model"
    assert judge["budget"]["verification_state"] == "configured_not_hardware_verified"


@pytest.mark.asyncio
async def test_provider_selection_cas_rejects_stale_revision_without_rollback() -> None:
    app = create_web_app(
        runtime_factory=lambda: lifecycle_runtime(built_in_judge=False),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        initial = (await client.get("/api/v6/provider-selection")).json()
        applied = await client.put(
            "/api/v6/provider-selection/judge",
            json={
                "provider_id": "built_in.deterministic",
                "expected_revision": initial["revision"],
                "expected_digest": initial["digest_sha512"],
            },
        )
        stale = await client.put(
            "/api/v6/provider-selection/judge",
            json={
                "provider_id": "none",
                "expected_revision": initial["revision"],
                "expected_digest": initial["digest_sha512"],
            },
        )
        canonical = await client.get("/api/v6/provider-selection")
    assert applied.status_code == 200
    assert applied.json()["revision"] > initial["revision"]
    assert stale.status_code == 409
    assert stale.json()["code"] == "provider_selection_revision_conflict"
    judge = next(item for item in canonical.json()["selections"] if item["role"] == "judge")
    assert judge["configured_provider"] == "built_in.deterministic"
    assert judge["active_provider"] is None
    assert judge["state"] == "configured"


@pytest.mark.asyncio
async def test_provider_selection_invalid_role_and_unknown_provider_are_typed() -> None:
    app = create_web_app(
        runtime_factory=lambda: lifecycle_runtime(built_in_judge=False),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        initial = (await client.get("/api/v6/provider-selection")).json()
        invalid_role = await client.put(
            "/api/v6/provider-selection/not-a-role",
            json={
                "provider_id": "none",
                "expected_revision": initial["revision"],
                "expected_digest": initial["digest_sha512"],
            },
        )
        unknown = await client.put(
            "/api/v6/provider-selection/guard",
            json={
                "provider_id": "guard.unknown",
                "expected_revision": initial["revision"],
                "expected_digest": initial["digest_sha512"],
            },
        )
    assert invalid_role.status_code == 422
    assert invalid_role.json()["code"] == "provider_selection_role_mismatch"
    assert unknown.status_code == 404
    assert unknown.json()["code"] == "provider_selection_unknown_provider"


@pytest.mark.asyncio
async def test_status_projects_a_real_judge_result_including_repair_fields() -> None:
    """P6-CODEX-012 (Second Rework): the Frontend contract must actually
    carry Repair Outcome/Acceptance/new-Turn correlation and the Current
    Request state — not just the pre-existing bare Recommendation fields.

    Also closes P6-RR-ACC-035/P6-DELTA-016 item 7 (found as a genuine
    Coverage Gap during R20's own 66-Acceptance-ID Audit): `bound_
    runtime()` never applies a Mode, so Judge Mode is genuinely `off`
    here — the explicit `current_mode == "off"` assertion below, combined
    with the pre-existing `last_result is None` / populated `historical_
    last_result` assertions, is the literal OFF-state Current/Historical
    separation the requirement names, not just a mode-independent
    inference from the component's own logic."""
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
            presentation_outcome="repair_accepted",
            candidate_withheld=True,
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
    assert judge["current_mode"] == "off"
    assert judge["state"] == "completed"
    assert judge["current_request_id"] == "req-42"
    assert judge["last_result"] is None
    result = judge["historical_last_result"]
    assert result["recommendation"] == "needs_repair"
    assert result["repair_eligibility"] == "eligible"
    assert result["repair_outcome"] == "improved"
    assert result["repair_accepted"] is True
    assert result["repair_new_turn_id"] == "turn-repaired-1"
    assert result["presentation_outcome"] == "repair_accepted"
    assert result["candidate_withheld"] is True


@pytest.mark.asyncio
async def test_status_projects_real_recording_outcomes_for_both_writers() -> None:
    from margpa_runtime_llm.bootstrap.recording_live_integration import (
        RecordingCompositionState,
    )

    recording_composition = RecordingCompositionState()
    recording_composition.record_ok(request_id="req-1")
    judge_evidence_composition = RecordingCompositionState()
    judge_evidence_composition.record_degraded(
        request_id="req-1", reason="RecordingQuotaExceeded: over limit"
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
        "request_id": "req-1",
        "ok": False,
        "degraded_reason": "RecordingQuotaExceeded: over limit",
    }


@pytest.mark.asyncio
async def test_recording_correlation_anchors_on_its_own_turn_when_judge_never_ran() -> None:
    """P6-CODEX-077: Turn Recording fires unconditionally (ADR-6-013 Mode
    orthogonality) while Judge's own `current_request_id` never updates
    when Judge Mode is OFF. The Current-Turn anchor for Recording
    Correlation must therefore come from Recording's own last outcome, not
    from Judge — otherwise every Turn recorded while Judge is OFF is
    misclassified as historical/unmatched instead of the current Turn."""
    from margpa_runtime_llm.bootstrap.recording_live_integration import (
        RecordingCompositionState,
    )

    recording_composition = RecordingCompositionState()
    recording_composition.record_ok(request_id="req-99")

    def runtime_factory() -> WebRuntime:
        runtime = bound_runtime()
        # Judge composition intentionally left unset: Judge never ran.
        runtime.recording_composition = recording_composition
        return runtime

    app = create_web_app(runtime_factory=runtime_factory, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v5/feature-modes/status")
    body = response.json()

    assert body["judge"]["current_request_id"] is None
    correlation = body["recording"]["correlation"]
    assert correlation["request_id"] == "req-99"
    assert correlation["current_turn"] == {
        "request_id": "req-99",
        "ok": True,
        "degraded_reason": None,
    }
    assert correlation["current_judge_evidence"] is None
    assert correlation["historical_or_unmatched"] == []


@pytest.mark.asyncio
async def test_r19_a_current_turn_is_correct_before_recording_hook_ever_fires() -> None:
    """R19-A (P6-RR-R19-WU-001..004, resolves P6-CODEX-082): Judge OFF +
    Recording FULL, but the Turn is still *in flight* — its own Recording
    Hook has not written a record yet. `RequestCorrelationRegistry.
    begin()` alone must be enough to make this Turn Current; the old
    Recording-outcome-anchored design left the *previous* Turn shown as
    Current until this new one's own Hook eventually fired."""
    from margpa_runtime_llm.bootstrap.request_correlation_registry import (
        RequestCorrelationRegistry,
    )

    registry = RequestCorrelationRegistry()
    registry.begin(request_id="req-in-flight", started_at="2026-08-29T00:00:00Z")

    def runtime_factory() -> WebRuntime:
        runtime = bound_runtime()
        runtime.request_correlation_registry = registry
        return runtime

    app = create_web_app(runtime_factory=runtime_factory, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v5/feature-modes/status")
    correlation = response.json()["recording"]["correlation"]

    assert correlation["request_id"] == "req-in-flight"
    assert correlation["current"]["request_id"] == "req-in-flight"
    assert correlation["current"]["status"] == "pending"
    assert correlation["current"]["turn_recording"] is None
    assert correlation["current"]["judge_result"] is None


@pytest.mark.asyncio
async def test_r19_b_observe_background_pending_current_request() -> None:
    """R19-B: Judge OBSERVE still running in the background (no result
    yet) — Current must still correctly report `status: "pending"` with
    no `judge_result`, rather than showing nothing or a stale Turn."""
    from margpa_runtime_llm.bootstrap.judge_live_integration import JudgeGovernanceComposition
    from margpa_runtime_llm.bootstrap.request_correlation_registry import (
        RequestCorrelationRegistry,
    )

    registry = RequestCorrelationRegistry()
    registry.begin(request_id="req-observe-pending", started_at="t0")
    composition = JudgeGovernanceComposition()
    composition.mark_running(request_id="req-observe-pending")

    def runtime_factory() -> WebRuntime:
        runtime = bound_runtime()
        runtime.request_correlation_registry = registry
        runtime.judge_governance_composition = composition
        return runtime

    app = create_web_app(runtime_factory=runtime_factory, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v5/feature-modes/status")
    correlation = response.json()["recording"]["correlation"]

    assert correlation["current"]["request_id"] == "req-observe-pending"
    assert correlation["current"]["status"] == "pending"
    assert correlation["current"]["judge_result"] is None


@pytest.mark.asyncio
async def test_r19_c_completed_turn_joins_judge_result_and_both_recordings() -> None:
    """R19-C: once a Turn completes, its Judge Result and both Recording
    Outcomes must all appear together in the single `current` Summary,
    correctly correlated by the identical request_id."""
    from margpa_runtime_llm.bootstrap.judge_live_integration import (
        JudgeGovernanceComposition,
        LiveJudgeResult,
    )
    from margpa_runtime_llm.bootstrap.recording_live_integration import (
        RecordingCompositionState,
    )
    from margpa_runtime_llm.bootstrap.request_correlation_registry import (
        RequestCorrelationRegistry,
    )
    from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass

    registry = RequestCorrelationRegistry()
    registry.begin(request_id="req-complete-1", started_at="t0")
    registry.mark_terminal(request_id="req-complete-1", status="completed", completed_at="t1")

    judge_composition = JudgeGovernanceComposition()
    judge_composition.mark_running(request_id="req-complete-1")
    judge_composition.record_result(
        LiveJudgeResult(
            request_id="req-complete-1",
            judge_role=JudgeIndependenceClass.MAIN_SELF,
            recommendation="accept",
            confidence=1.0,
            execution_state="completed",
            failure_reason=None,
        )
    )
    recording_composition = RecordingCompositionState()
    recording_composition.record_ok(request_id="req-complete-1")
    judge_evidence_composition = RecordingCompositionState()
    judge_evidence_composition.record_ok(request_id="req-complete-1")

    def runtime_factory() -> WebRuntime:
        runtime = bound_runtime()
        runtime.request_correlation_registry = registry
        runtime.judge_governance_composition = judge_composition
        runtime.recording_composition = recording_composition
        runtime.judge_evidence_recording_composition = judge_evidence_composition
        return runtime

    app = create_web_app(runtime_factory=runtime_factory, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v5/feature-modes/status")
    correlation = response.json()["recording"]["correlation"]
    current = correlation["current"]

    assert current["request_id"] == "req-complete-1"
    assert current["status"] == "completed"
    assert current["completed_at"] == "t1"
    assert current["judge_result"]["recommendation"] == "accept"
    assert current["turn_recording"] == {
        "request_id": "req-complete-1",
        "ok": True,
        "degraded_reason": None,
    }
    assert current["judge_evidence_recording"] == {
        "request_id": "req-complete-1",
        "ok": True,
        "degraded_reason": None,
    }
    assert correlation["historical_or_unmatched"] == []


@pytest.mark.asyncio
async def test_r19_d_out_of_order_late_evidence_for_a_superseded_request_stays_historical() -> None:
    """R19-D: a new Turn (req-2) starts, becoming Current, while req-1's
    own Judge Evidence Recording only arrives *after* that — the late
    evidence must never overwrite Current; it must land in
    `historical_or_unmatched`."""
    from margpa_runtime_llm.bootstrap.recording_live_integration import (
        RecordingCompositionState,
    )
    from margpa_runtime_llm.bootstrap.request_correlation_registry import (
        RequestCorrelationRegistry,
    )

    registry = RequestCorrelationRegistry()
    registry.begin(request_id="req-1", started_at="t0")
    registry.mark_terminal(request_id="req-1", status="completed", completed_at="t1")
    registry.begin(request_id="req-2", started_at="t2")

    judge_evidence_composition = RecordingCompositionState()
    judge_evidence_composition.record_ok(request_id="req-1")  # arrives late, after req-2 started

    def runtime_factory() -> WebRuntime:
        runtime = bound_runtime()
        runtime.request_correlation_registry = registry
        runtime.judge_evidence_recording_composition = judge_evidence_composition
        return runtime

    app = create_web_app(runtime_factory=runtime_factory, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v5/feature-modes/status")
    correlation = response.json()["recording"]["correlation"]

    assert correlation["request_id"] == "req-2"
    assert correlation["current"]["request_id"] == "req-2"
    assert correlation["current"]["judge_evidence_recording"] is None
    assert correlation["current_judge_evidence"] is None
    assert correlation["historical_or_unmatched"] == [
        {"request_id": "req-1", "ok": True, "degraded_reason": None}
    ]
