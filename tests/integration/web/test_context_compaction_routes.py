"""Phase 9-3 CL-P9-3-F: `/api/v8/context-compaction` Local API -- proves the
Coordinator is genuinely reachable through the real FastAPI app, not only
through direct Python calls (the same Top-level posture `test_experiment_
routes.py` established for Phase 9-2)."""

from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.context_compaction.local_filesystem_compaction_store import (
    LocalFilesystemCompactionStore,
)
from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import TaggedThinkingOutputParser
from margpa_runtime_llm.modules.context_compaction.application.auto_policy import (
    AutoCompactionPolicyController,
)
from margpa_runtime_llm.modules.context_compaction.application.budget_service import (
    ContextBudgetService,
    ReserveConfig,
)
from margpa_runtime_llm.modules.context_compaction.application.coordinator import (
    CompactionCoordinator,
)
from margpa_runtime_llm.modules.context_compaction.application.deterministic_builder import (
    DeterministicExtractiveBuilder,
)
from margpa_runtime_llm.modules.context_compaction.application.worker import CompactionWorker
from margpa_runtime_llm.modules.context_compaction.domain import DEFAULT_BRANCH_ID, ThresholdConfig
from margpa_runtime_llm.modules.context_compaction.ports.context_source import (
    ConversationSourceProjection,
    SourceConversationTurn,
)
from margpa_runtime_llm.modules.conversation.domain.identity import (
    ConversationId,
    ConversationMessageId,
    ConversationTurnId,
)
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationParameters,
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
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode
from margpa_runtime_llm.web.access_profiles import WebExposureMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import RuntimeDefaults, SafeRuntimeSnapshot, WebRuntime

_LOCAL_POLICY = WebAccessPolicy(exposure_mode=WebExposureMode.LOCAL, mode=WebAuthMode.DISABLED)


class _FakeInference:
    def stream(self, request: object) -> GenerationStream:
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
        inference=_FakeInference(),
        presentation=ThinkingPresentationService(
            TaggedThinkingOutputParser(opening_delimiter="<think>", closing_delimiter="</think>")
        ),
        model_key="main.fixture",
        generation_defaults=GenerationParameters(
            max_new_tokens=2048, thinking_mode=ThinkingMode.DISABLED
        ),
        response_language_default=ResponseLanguage.JA,
        presentation_default=presentation_policy,
        summarization=SummarizationConfig(),
    )


def _snapshot() -> SafeRuntimeSnapshot:
    return SafeRuntimeSnapshot(
        model_key="main.fixture",
        profile_key="test.fixture",
        device_kind="cpu",
        acceleration_api="fixture",
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


class FakeSource:
    def __init__(self, turn_count: int = 20, revision: int = 20) -> None:
        self.turn_count = turn_count
        self.revision = revision

    def read(self, conversation_id: ConversationId) -> ConversationSourceProjection | None:
        turns = tuple(
            SourceConversationTurn(
                turn_id=ConversationTurnId(value=f"turn-{i}"),
                sequence=i,
                user_message_id=ConversationMessageId(value=f"user-{i}"),
                user_content=f"User turn {i} content padded out a bit for token counting.",
                assistant_message_id=ConversationMessageId(value=f"assistant-{i}"),
                assistant_content=f"Assistant reply {i} content padded out a bit as well here.",
            )
            for i in range(self.turn_count)
        )
        return ConversationSourceProjection(
            conversation_id=conversation_id,
            branch_id=DEFAULT_BRANCH_ID,
            source_conversation_revision=self.revision,
            turns=turns,
        )


class FakeModelContext:
    def loaded_context_capacity(self) -> int | None:
        return 4096

    def loaded_model_identity(self) -> str | None:
        return "fixture-model"

    def count_text_tokens(self, text: str) -> int | None:
        return max(1, len(text) // 4)


def _bound_runtime(tmp_path: Path) -> WebRuntime:
    source = FakeSource()
    model_context = FakeModelContext()
    budget_service = ContextBudgetService(
        source=source, model_context=model_context, reserves=ReserveConfig()
    )
    worker = CompactionWorker()
    auto_policy = AutoCompactionPolicyController(enabled=True)
    coordinator = CompactionCoordinator(
        store=LocalFilesystemCompactionStore(base_dir=tmp_path),
        budget_service=budget_service,
        builder=DeterministicExtractiveBuilder(model_context=model_context),
        auto_policy=auto_policy,
        worker=worker,
        thresholds=ThresholdConfig(
            advisory_remaining_budget_floor=100_000, auto_trigger_remaining_budget_floor=100_000
        ),
        token_budget=250,
    )
    return WebRuntime(
        conversation=_conversation(),
        snapshot=_snapshot(),
        close_callback=lambda: None,
        context_compaction_coordinator=coordinator,
        context_compaction_worker=worker,
        context_compaction_auto_policy=auto_policy,
    )


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client


async def _poll_terminal(client: httpx.AsyncClient, attempt_id: str) -> dict[str, object]:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        response = await client.get(f"/api/v8/context-compaction/attempts/{attempt_id}")
        body: dict[str, object] = response.json()
        if body["is_terminal"]:
            return body
        time.sleep(0.02)
    raise AssertionError("attempt did not reach a terminal state in time")


@pytest.mark.asyncio
async def test_status_reports_disabled_when_unbound() -> None:
    app = create_web_app(
        runtime_factory=lambda: WebRuntime(
            conversation=_conversation(), snapshot=_snapshot(), close_callback=lambda: None
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        response = await client.get("/api/v8/context-compaction/status")
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is False
    assert body["auto_compaction_enabled"] is None


@pytest.mark.asyncio
async def test_disabled_routes_return_the_disabled_contract(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: WebRuntime(
            conversation=_conversation(), snapshot=_snapshot(), close_callback=lambda: None
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        budget = await client.get("/api/v8/context-compaction/conv-1/budget")
        compact = await client.post("/api/v8/context-compaction/conv-1/compact")
    for response in (budget, compact):
        assert response.status_code == 503
        assert response.json()["code"] == "context_compaction_unavailable"


@pytest.mark.asyncio
async def test_full_budget_preview_compact_rollback_lifecycle_over_http(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime(tmp_path), access_policy=_LOCAL_POLICY
    )
    cid = "conv-http-1"
    async with client_for(app) as client:
        status = await client.get("/api/v8/context-compaction/status")
        assert status.json()["enabled"] is True
        assert status.json()["auto_compaction_enabled"] is True

        budget = await client.get(f"/api/v8/context-compaction/{cid}/budget")
        assert budget.status_code == 200
        assert budget.json()["pressure"] in {
            "normal",
            "approaching_auto_trigger",
            "auto_compaction_required",
            "hard_reserve_protected",
        }

        preview = await client.post(f"/api/v8/context-compaction/{cid}/preview")
        assert preview.status_code == 200
        assert preview.json()["feasible"] is True

        compact = await client.post(f"/api/v8/context-compaction/{cid}/compact")
        assert compact.status_code == 202
        attempt_id = compact.json()["attempt_id"]
        final = await _poll_terminal(client, attempt_id)
        assert final["state"] == "completed"
        assert final["structured_context_id"] is not None

        rollback = await client.post(f"/api/v8/context-compaction/attempts/{attempt_id}/rollback")
        assert rollback.status_code == 200
        assert rollback.json()["result"] == "rolled_back"

        handoff = await client.get(f"/api/v8/context-compaction/{cid}/handoff")
        assert handoff.status_code == 200
        assert handoff.json()["current_objective"]


@pytest.mark.asyncio
async def test_auto_policy_toggle_over_http(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime(tmp_path), access_policy=_LOCAL_POLICY
    )
    async with client_for(app) as client:
        off = await client.put(
            "/api/v8/context-compaction/auto-policy", json={"enabled": False}
        )
        assert off.status_code == 200
        assert off.json()["auto_compaction_enabled"] is False
        status = await client.get("/api/v8/context-compaction/status")
        assert status.json()["auto_compaction_enabled"] is False
