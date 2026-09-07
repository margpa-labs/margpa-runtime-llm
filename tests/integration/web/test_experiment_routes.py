"""Phase 9-2 WU-A A4/WU-E E4 (R1-WU-03/04/05): `/api/v7/experiment` routes.

The Minimal Experiment screen's own Backend surface: Presets, Plan
creation, async Run start/Cancel, single-Run read, per-Experiment Run
listing, and the Comparison Report projection."""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.experiment.local_filesystem_experiment_store import (
    LocalFilesystemExperimentStore,
)
from margpa_runtime_llm.adapters.output_protocols.tagged_thinking import (
    TaggedThinkingOutputParser,
)
from margpa_runtime_llm.modules.conversation.public import ConversationGenerationService
from margpa_runtime_llm.modules.experiment.application.configuration_lease import (
    ExperimentConfigurationLease,
)
from margpa_runtime_llm.modules.experiment.application.experiment_service import (
    ExperimentService,
)
from margpa_runtime_llm.modules.experiment.application.production_turn_runner import (
    ProductionTurnObservation,
)
from margpa_runtime_llm.modules.experiment.application.run_worker import ExperimentRunWorker
from margpa_runtime_llm.modules.experiment.domain.case_pack import build_case_pack
from margpa_runtime_llm.modules.experiment.domain.config_snapshot import (
    build_effective_configuration_snapshot,
)
from margpa_runtime_llm.modules.experiment.domain.dataset import EvaluationCaseManifest
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    VariantDescriptor,
)
from margpa_runtime_llm.modules.experiment.domain.provider_identity import (
    ProviderIdentityDetail,
    ProviderIdentityEnvelope,
)
from margpa_runtime_llm.modules.experiment.domain.run import RunState
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
from margpa_runtime_llm.modules.runtime_model_control.application.provider_selection_controller import (  # noqa: E501
    GEMMA_E2B_JUDGE,
    QWEN3_GUARD,
    QWEN_MAIN,
)
from margpa_runtime_llm.modules.summarization.public import SummarizationConfig, SummaryMode
from margpa_runtime_llm.web import experiment_routes
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


def _unbound_runtime() -> WebRuntime:
    return WebRuntime(
        conversation=_conversation(), snapshot=_snapshot(), close_callback=lambda: None
    )


def _bound_runtime(tmp_path: Path) -> WebRuntime:
    runtime = _unbound_runtime()
    runtime.experiment_service = ExperimentService(
        store=LocalFilesystemExperimentStore(base_dir=tmp_path)
    )
    runtime.experiment_run_worker = ExperimentRunWorker()
    return runtime


async def _wait_for_terminal_run(
    client: httpx.AsyncClient, run_id: str, *, timeout: float = 2.0
) -> dict[str, Any]:
    """R1-WU-05: `POST /runs` now returns `state="running"` immediately --
    every caller that needs the eventual outcome polls `GET /runs/{id}`,
    exactly like a real Frontend would."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = await client.get(f"/api/v7/experiment/runs/{run_id}")
        body: dict[str, Any] = response.json()
        if body["run"]["state"] != "running":
            return body
        await asyncio.sleep(0.01)
    raise AssertionError(f"run {run_id!r} did not reach a terminal state in time")


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client


@pytest.mark.asyncio
async def test_presets_degrades_safely_when_unbound() -> None:
    app = create_web_app(runtime_factory=_unbound_runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        response = await client.get("/api/v7/experiment/presets")
    assert response.status_code == 200
    assert response.json() == {"enabled": False, "cases": [], "variants": []}


@pytest.mark.asyncio
async def test_presets_lists_case_pack_and_preset_variants_when_bound(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime(tmp_path), access_policy=_LOCAL_POLICY
    )
    async with client_for(app) as client:
        response = await client.get("/api/v7/experiment/presets")
    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    assert len(body["cases"]) > 0
    variant_ids = {variant["variant_id"] for variant in body["variants"]}
    assert variant_ids == {
        "baseline-all-off",
        "judge-observe",
        "judge-enforce-repair",
        "production-main-only-baseline",
        "production-judge-repair-baseline",
        "production-guard-baseline",
    }


@pytest.mark.asyncio
async def test_full_plan_run_and_list_lifecycle(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime(tmp_path), access_policy=_LOCAL_POLICY
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]

        plan_response = await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-1",
                "case_id": case_id,
                "variant_ids": ["baseline-all-off", "judge-observe"],
            },
        )
        assert plan_response.status_code == 201
        plan_body = plan_response.json()
        assert plan_body["experiment_id"] == "exp-1"
        assert set(plan_body["variant_ids"]) == {"baseline-all-off", "judge-observe"}

        run_response = await client.post(
            "/api/v7/experiment/runs",
            json={"experiment_id": "exp-1", "variant_id": "judge-observe", "run_id": "run-1"},
        )
        # R1-WU-05: the Actor Call runs on the Tracked Worker, off this
        # request's own Thread -- the immediate Response is always
        # `running`, never a synchronously-completed outcome.
        assert run_response.status_code == 202
        assert run_response.json()["state"] == "running"
        assert run_response.json()["fixture_only"] is True

        run_body = await _wait_for_terminal_run(client, "run-1")
        assert run_body["run"]["state"] == "completed"
        assert run_body["run"]["fixture_only"] is True
        invocation_by_key = {item["component_key"]: item for item in run_body["invocations"]}
        assert invocation_by_key["judge"]["called"] is True
        assert invocation_by_key["main"]["called"] is False

        get_response = await client.get("/api/v7/experiment/runs/run-1")
        assert get_response.status_code == 200
        assert get_response.json()["run"]["state"] == "completed"

        list_response = await client.get("/api/v7/experiment/experiments/exp-1/runs")
        assert list_response.status_code == 200
        run_ids = {item["run_id"] for item in list_response.json()["runs"]}
        assert run_ids == {"run-1"}

        comparison_response = await client.get("/api/v7/experiment/experiments/exp-1/comparison")
        assert comparison_response.status_code == 200
        comparison_body = comparison_response.json()
        assert comparison_body["case_id"] == case_id
        rows_by_run_id = {row["run_id"]: row for row in comparison_body["rows"]}
        assert rows_by_run_id["run-1"]["runtime_state"] == "completed"
        assert len(rows_by_run_id["run-1"]["observations"]) == 1


@pytest.mark.asyncio
async def test_start_run_rejects_unknown_variant_id(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime(tmp_path), access_policy=_LOCAL_POLICY
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-2",
                "case_id": case_id,
                "variant_ids": ["baseline-all-off"],
            },
        )
        response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-2",
                "variant_id": "not-a-real-variant",
                "run_id": "run-1",
            },
        )
    assert response.status_code == 404
    # R1-WU-02 (IR-P9-2-03 fix): the rejection now comes from the Frozen
    # Plan's own `variant()` lookup (Core code `unknown_variant`), not a
    # route-local `_PRESET_VARIANTS` membership check (`unknown_variant_id`).
    assert response.json()["code"] == "unknown_variant"


@pytest.mark.asyncio
async def test_cancel_a_completed_run_is_rejected(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime(tmp_path), access_policy=_LOCAL_POLICY
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-3",
                "case_id": case_id,
                "variant_ids": ["baseline-all-off"],
            },
        )
        await client.post(
            "/api/v7/experiment/runs",
            json={"experiment_id": "exp-3", "variant_id": "baseline-all-off", "run_id": "run-1"},
        )
        await _wait_for_terminal_run(client, "run-1")
        response = await client.post("/api/v7/experiment/runs/run-1/cancel")
    assert response.status_code == 409
    assert response.json()["code"] == "terminal_already_published"


@pytest.mark.asyncio
async def test_cancel_is_idempotent_when_the_runs_own_cancel_hook_wins_the_race(
    tmp_path: Path,
) -> None:
    """R2-WU-04 (IR-P9-2-R1-06 fix): if the Run's own Cancel Hook (fired by
    `request_cancel()` at the top of the Cancel route) races ahead and
    publishes `CANCELLED` through the Worker's own Task BEFORE this SAME
    Cancel request's subsequent `service.cancel_run()` call runs, that is
    THIS Cancel succeeding via a different path -- never a false 409.
    Simulated directly (deterministically) here: the Run is manually
    published `CANCELLED` before the Cancel route is even called, exactly
    the state such a race would leave behind."""

    runtime = _bound_runtime(tmp_path)
    app = create_web_app(runtime_factory=lambda: runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-race-1",
                "case_id": case_id,
                "variant_ids": ["baseline-all-off"],
            },
        )
        service = runtime.experiment_service
        assert service is not None
        run = service.start_run(
            experiment_id="exp-race-1",
            variant_id="baseline-all-off",
            run_id="run-1",
            request_id="req-race-1",
            execution_mode="fixture",
        )
        # Simulates the Worker's own cancel-triggered publish winning the
        # race -- never actually submitted to the Worker in this test, so
        # `request_cancel()` inside the Cancel route below finds nothing
        # in-flight (a harmless, best-effort `False`) and proceeds
        # straight to `service.cancel_run()`, which is exactly the
        # code path this test exercises.
        service.publish_result(
            run.run_id, generation=run.generation, target_state=RunState.CANCELLED
        )

        response = await client.post("/api/v7/experiment/runs/run-1/cancel")
    assert response.status_code == 200
    assert response.json()["state"] == "cancelled"


@pytest.mark.asyncio
async def test_cancel_still_409s_when_the_run_finished_for_an_unrelated_reason(
    tmp_path: Path,
) -> None:
    """The idempotency fix above must not paper over a genuinely too-late
    Cancel -- a Run that reached a DIFFERENT terminal state (`COMPLETED`,
    for a reason unrelated to this Cancel) still 409s."""

    runtime = _bound_runtime(tmp_path)
    app = create_web_app(runtime_factory=lambda: runtime, access_policy=_LOCAL_POLICY)
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-race-2",
                "case_id": case_id,
                "variant_ids": ["baseline-all-off"],
            },
        )
        service = runtime.experiment_service
        assert service is not None
        run = service.start_run(
            experiment_id="exp-race-2",
            variant_id="baseline-all-off",
            run_id="run-1",
            request_id="req-race-2",
            execution_mode="fixture",
        )
        service.publish_result(
            run.run_id, generation=run.generation, target_state=RunState.COMPLETED
        )

        response = await client.post("/api/v7/experiment/runs/run-1/cancel")
    assert response.status_code == 409
    assert response.json()["code"] == "terminal_already_published"


@dataclass
class FakeProductionTurnPort:
    """R1-WU-03: a Fake standing in for `LiveProductionTurnAdapter` at the
    Web-route layer -- exercises the real `execution_mode="production"`
    wiring without ever touching a real Model."""

    request_id: str
    main_outcome: str = "completed"
    assistant_content: str | None = "Paris."
    calls: list[str] = field(default_factory=list)
    release: threading.Event | None = None
    mutate_live_config: Callable[[], None] | None = None

    def run_turn(
        self, *, user_input: str, on_request_id: Callable[[str], None] | None = None
    ) -> ProductionTurnObservation:
        self.calls.append(user_input)
        if on_request_id is not None:
            on_request_id(self.request_id)
        if self.release is not None:
            self.release.wait(timeout=2.0)
        if self.mutate_live_config is not None:
            # R2-WU-01: simulates a real Live Judge/Guard/Provider Mode
            # change happening WHILE this real Turn was still executing --
            # the Route's own post-hoc re-check (its bounded "Lease"
            # Fallback) must catch this, never report a trustworthy
            # `COMPLETED`.
            self.mutate_live_config()
        return ProductionTurnObservation(
            request_id=self.request_id,
            main_called=True,
            main_outcome=self.main_outcome,
            judge_called=False,
            judge_outcome="off",
            guard_called=False,
            guard_outcome="off",
            repair_called=False,
            repair_outcome="off",
            repair_adopted=None,
            final_disposition="candidate_accepted"
            if self.main_outcome == "completed"
            else self.main_outcome,
            assistant_content=self.assistant_content,
        )


@dataclass(frozen=True)
class FakeLiveConfigurationPort:
    """R2-WU-01: a stable, constant `LiveConfigurationPort` Fake -- Plan
    creation and Run start each call `.snapshot()` independently, but
    since this Fake always returns the identical Snapshot, their digests
    always match (no real drift to detect in these Fixture-level tests).
    Defaults to a Configuration `judge-observe` (JUDGE `mode="observe"`,
    every other slot absent from that Variant's own declared Components
    and therefore never checked) can actually satisfy.

    R4-WU-01: `main_selector` defaults to the SAME `QWEN_MAIN` constant
    the Production Presets now declare (Handoff R4 SS4.1.1), so every
    pre-existing Production test keeps matching Main's Provider identity
    without needing its own explicit override -- only a test that
    deliberately wants a Provider mismatch passes a different value."""

    judge_mode: str = "observe"
    guard_mode: str = "off"
    main_governance_mode: str = "off"
    repair_mode: str = "off"
    recording_mode: str = "off"
    main_selector: str | None = QWEN_MAIN
    judge_selector: str | None = None
    guard_selector: str | None = None

    def snapshot(self) -> Any:
        return build_effective_configuration_snapshot(
            main=ComponentSelection(
                component_key=ComponentKey.MAIN, selector_id=self.main_selector, mode="active"
            ),
            judge=ComponentSelection(
                component_key=ComponentKey.JUDGE,
                selector_id=self.judge_selector,
                mode=self.judge_mode,
            ),
            guard=ComponentSelection(
                component_key=ComponentKey.GUARD,
                selector_id=self.guard_selector,
                mode=self.guard_mode,
            ),
            main_governance=ComponentSelection(
                component_key=ComponentKey.MAIN_GOVERNANCE, mode=self.main_governance_mode
            ),
            definition_set=ComponentSelection(component_key=ComponentKey.DEFINITION_SET),
            rag=ComponentSelection(component_key=ComponentKey.RAG),
            repair=ComponentSelection(component_key=ComponentKey.REPAIR, mode=self.repair_mode),
            recording=ComponentSelection(
                component_key=ComponentKey.RECORDING, mode=self.recording_mode
            ),
            presentation=ComponentSelection(component_key=ComponentKey.PRESENTATION),
        )

    def provider_identity(self) -> ProviderIdentityEnvelope:
        return ProviderIdentityEnvelope(
            main=ProviderIdentityDetail(
                component_key=ComponentKey.MAIN,
                configured_selector_id=self.main_selector,
                active_selector_id=self.main_selector,
                artifact_digest_sha512="a" * 128 if self.main_selector is not None else None,
            ),
            judge=ProviderIdentityDetail(
                component_key=ComponentKey.JUDGE,
                configured_selector_id=self.judge_selector,
                active_selector_id=self.judge_selector if self.judge_mode != "off" else None,
                artifact_digest_sha512=(
                    "b" * 128
                    if self.judge_selector is not None and self.judge_mode != "off"
                    else None
                ),
            ),
            guard=ProviderIdentityDetail(
                component_key=ComponentKey.GUARD,
                configured_selector_id=self.guard_selector,
                active_selector_id=self.guard_selector if self.guard_mode != "off" else None,
                artifact_digest_sha512=(
                    "c" * 128
                    if self.guard_selector is not None and self.guard_mode != "off"
                    else None
                ),
            ),
        )


@dataclass
class MutableLiveConfigurationPort:
    """A `LiveConfigurationPort` Fake whose Snapshot can change BETWEEN
    two `.snapshot()` calls -- simulates a real live Judge/Guard/Provider
    Mode change happening between Plan creation and Run start (Handoff
    R2 SS4.3: "Plan作成後のUI Mode/Provider変更をRunへ混入させない")."""

    current: FakeLiveConfigurationPort

    def snapshot(self) -> Any:
        return self.current.snapshot()

    def provider_identity(self) -> ProviderIdentityEnvelope:
        return self.current.provider_identity()


_UNSET: Any = object()
"""Distinguishes "caller did not pass `live_configuration_reader` at all"
(auto-fill a default Fake when an `adapter` is given) from an explicit
`live_configuration_reader=None` (force it absent, e.g. to test the
`live_config_unavailable` rejection) -- a plain `None` default cannot
tell these two callers apart."""


def _bound_runtime_with_production(
    tmp_path: Path,
    adapter: FakeProductionTurnPort | None,
    *,
    live_configuration_reader: Any = _UNSET,
    experiment_configuration_lease: Any = _UNSET,
) -> WebRuntime:
    """R4-WU-02 (Handoff R4 SS5.1's Lease-unavailable Hard Assert): the
    real `build_phase1_web_runtime()` always constructs `Experiment
    ConfigurationLease()` alongside `production_turn_adapter`/
    `live_configuration_reader` -- unconditionally, in the same wiring
    block (`bootstrap/web_application.py`). This Fake mirrors that
    coupling by default so every pre-existing Production test genuinely
    exercises the Lease-protected path, not an unprotected one
    `WebRuntime`'s own bare default (`None`) would otherwise leave in
    place; pass `experiment_configuration_lease=None` explicitly only to
    test the dedicated "Lease unavailable" Typed Call 0 rejection."""

    runtime = _bound_runtime(tmp_path)
    runtime.production_turn_adapter = adapter
    if live_configuration_reader is _UNSET:
        runtime.live_configuration_reader = (
            FakeLiveConfigurationPort() if adapter is not None else None
        )
    else:
        runtime.live_configuration_reader = live_configuration_reader
    if experiment_configuration_lease is _UNSET:
        runtime.experiment_configuration_lease = (
            ExperimentConfigurationLease() if adapter is not None else None
        )
    else:
        runtime.experiment_configuration_lease = experiment_configuration_lease
    return runtime


@pytest.mark.asyncio
async def test_start_run_rejects_production_mode_when_adapter_unavailable(
    tmp_path: Path,
) -> None:
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(tmp_path, None),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-4",
                "case_id": case_id,
                "variant_ids": ["judge-observe"],
                "execution_mode": "production",
            },
        )
        response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-4",
                "variant_id": "judge-observe",
                "run_id": "run-1",
            },
        )
    assert response.status_code == 503
    assert response.json()["code"] == "production_adapter_unavailable"


@pytest.mark.asyncio
async def test_a_production_run_completes_with_fixture_only_false(tmp_path: Path) -> None:
    adapter = FakeProductionTurnPort(request_id="real-req-1")
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(tmp_path, adapter),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        case_input = presets["cases"][0]["input"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-5",
                "case_id": case_id,
                "variant_ids": ["judge-observe"],
                "execution_mode": "production",
            },
        )
        start_response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-5",
                "variant_id": "judge-observe",
                "run_id": "run-1",
            },
        )
        assert start_response.status_code == 202
        assert start_response.json()["fixture_only"] is False
        run_body = await _wait_for_terminal_run(client, "run-1")
    assert run_body["run"]["state"] == "completed"
    assert run_body["run"]["fixture_only"] is False
    # `run.request_id` stays the Experiment-side id assigned at Run start
    # (server-generated here, since the client did not supply one) --
    # the REAL Phase 9-1 Turn's own internal request_id is a distinct,
    # additional field.
    assert run_body["run"]["request_id"]
    assert run_body["production_request_id"] == "real-req-1"
    assert run_body["assistant_content"] == "Paris."
    assert adapter.calls == [case_input]


@pytest.mark.asyncio
async def test_cancel_reaches_an_in_flight_production_run(tmp_path: Path) -> None:
    """R1-WU-05 Hard Assert: Cancel reaches a real Cancellation hook for an
    in-flight Run, never only a Fixture-fast one."""
    release = threading.Event()
    adapter = FakeProductionTurnPort(request_id="real-req-2", release=release)
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(tmp_path, adapter),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-6",
                "case_id": case_id,
                "variant_ids": ["judge-observe"],
                "execution_mode": "production",
            },
        )
        await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-6",
                "variant_id": "judge-observe",
                "run_id": "run-1",
            },
        )
        await asyncio.sleep(0.05)
        cancel_response = await client.post("/api/v7/experiment/runs/run-1/cancel")
        assert cancel_response.status_code == 200
        assert cancel_response.json()["state"] == "cancelled"
        release.set()
    assert adapter.calls == [presets["cases"][0]["input"]]


@pytest.mark.asyncio
async def test_a_preset_change_after_plan_creation_never_affects_the_frozen_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R1 9.1 Hard Assert #2 ("Plan作成後にPresetが変わってもFrozen Variant
    を実行する"): mutates the route's own `_PRESET_VARIANTS` AFTER a Plan
    already froze `judge-observe` as JUDGE-only -- the Run started against
    that Plan must still execute exactly the Frozen Variant, never the
    mutated live Preset (which here adds a REPAIR Component the Frozen
    Variant never had)."""
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime(tmp_path), access_policy=_LOCAL_POLICY
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={"experiment_id": "exp-7", "case_id": case_id, "variant_ids": ["judge-observe"]},
        )

        mutated_variant = VariantDescriptor(
            variant_id="judge-observe",
            components=(
                ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),
                ComponentSelection(component_key=ComponentKey.REPAIR, mode="enforce"),
            ),
        )
        monkeypatch.setattr(
            experiment_routes,
            "_PRESET_VARIANTS",
            tuple(
                mutated_variant if item.variant_id == "judge-observe" else item
                for item in experiment_routes._PRESET_VARIANTS
            ),
        )

        await client.post(
            "/api/v7/experiment/runs",
            json={"experiment_id": "exp-7", "variant_id": "judge-observe", "run_id": "run-1"},
        )
        run_body = await _wait_for_terminal_run(client, "run-1")
    assert run_body["run"]["state"] == "completed"
    invocation_by_key = {item["component_key"]: item for item in run_body["invocations"]}
    # The Frozen Variant never declared REPAIR at all -- if the mutated
    # live Preset had been used instead, REPAIR would show `called=True`.
    assert invocation_by_key["repair"]["called"] is False
    assert invocation_by_key["repair"]["outcome"] == "absent"
    assert invocation_by_key["judge"]["called"] is True


@pytest.mark.asyncio
async def test_a_case_pack_content_change_after_plan_creation_rejects_the_run_before_any_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """R1 9.1 Hard Assert #4 ("Case...Digest不一致はActor Call 0"): after a
    Plan freezes a Case's content Digest, the live Case Pack changing the
    SAME `case_id`'s `input` text must reject the Run before any Actor is
    ever invoked -- never silently use the new content under the old id."""
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime(tmp_path), access_policy=_LOCAL_POLICY
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={"experiment_id": "exp-8", "case_id": case_id, "variant_ids": ["judge-observe"]},
        )

        original_pack = build_case_pack()
        tampered_pack = tuple(
            (
                EvaluationCaseManifest(
                    case_id=item.case_id,
                    revision=item.revision,
                    input="a tampered input the Plan never froze",
                    evidence_refs=item.evidence_refs,
                    expected_observations=item.expected_observations,
                    acceptable_outcomes=item.acceptable_outcomes,
                    requires_human_review=item.requires_human_review,
                )
                if item.case_id == case_id
                else item
            )
            for item in original_pack
        )
        monkeypatch.setattr(experiment_routes, "build_case_pack", lambda: tampered_pack)

        response = await client.post(
            "/api/v7/experiment/runs",
            json={"experiment_id": "exp-8", "variant_id": "judge-observe", "run_id": "run-1"},
        )
    assert response.status_code == 409
    assert response.json()["code"] == "case_digest_mismatch"


@pytest.mark.asyncio
async def test_production_run_rejects_when_no_live_configuration_reader_wired(
    tmp_path: Path,
) -> None:
    """R2-WU-01 (IR-P9-2-R1-01 fix): a Production Run with no Live
    Configuration Reader wired has nothing to Freeze-vs-Live-compare
    against -- Typed Call 0, never a silent skip of the check."""

    adapter = FakeProductionTurnPort(request_id="real-req-9")
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path, adapter, live_configuration_reader=None
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-9",
                "case_id": case_id,
                "variant_ids": ["judge-observe"],
                "execution_mode": "production",
            },
        )
        response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-9",
                "variant_id": "judge-observe",
                "run_id": "run-1",
            },
        )
    assert response.status_code == 409
    assert response.json()["code"] == "live_config_unavailable"
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_production_run_rejects_a_declared_variant_live_cannot_satisfy(
    tmp_path: Path,
) -> None:
    """R2-WU-01 (IR-P9-2-R1-01 fix): `production-guard-baseline` declares
    `guard` `mode="enforce"` -- if Live Guard is actually `off`, this is a
    genuinely impossible Preset for THIS Live Configuration, Typed Call 0
    before any Actor is ever invoked."""

    adapter = FakeProductionTurnPort(request_id="real-req-10")
    live_reader = FakeLiveConfigurationPort(guard_mode="off")
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path, adapter, live_configuration_reader=live_reader
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-10",
                "case_id": case_id,
                "variant_ids": ["production-guard-baseline"],
                "execution_mode": "production",
            },
        )
        response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-10",
                "variant_id": "production-guard-baseline",
                "run_id": "run-1",
            },
        )
    assert response.status_code == 409
    assert response.json()["code"] == "live_config_mismatch"
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_production_run_rejects_when_live_config_drifted_since_plan_creation(
    tmp_path: Path,
) -> None:
    """R2-WU-01 (IR-P9-2-R1-01 fix, Handoff R2 SS4.3): "Plan作成後のUI
    Mode/Provider変更をRunへ混入させない" -- a live Judge Mode change AFTER
    a Plan froze its own Configuration Snapshot must reject the Run
    before any Actor is ever invoked, even though `judge-observe` itself
    is a perfectly satisfiable Preset in the ABSTRACT."""

    adapter = FakeProductionTurnPort(request_id="real-req-11")
    live_reader = MutableLiveConfigurationPort(
        current=FakeLiveConfigurationPort(judge_mode="observe")
    )
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path, adapter, live_configuration_reader=live_reader
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-11",
                "case_id": case_id,
                "variant_ids": ["judge-observe"],
                "execution_mode": "production",
            },
        )
        # A live Judge Mode change AFTER Plan creation -- e.g. the User
        # switched Judge to ENFORCE via the ordinary Settings/Feature-
        # Modes UI in between.
        live_reader.current = FakeLiveConfigurationPort(judge_mode="enforce")
        response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-11",
                "variant_id": "judge-observe",
                "run_id": "run-1",
            },
        )
        assert response.status_code == 409
        assert response.json()["code"] == "live_config_mismatch"
        assert adapter.calls == []
        # No Run object was ever created for this rejected attempt.
        get_response = await client.get("/api/v7/experiment/runs/run-1")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_production_run_allows_drift_in_a_slot_the_variant_never_declared(
    tmp_path: Path,
) -> None:
    """R3-WU-01 (IR-P9-2-R2-01 CRITICAL fix): a live Guard Mode change
    AFTER Plan creation must NOT reject a `judge-observe` Run, since that
    Variant never declares `guard` at all -- `find_mismatched_slots()`
    (a per-DECLARED-slot check) is now the SOLE Call-0 gate for a
    Production Run. This test used to assert the OPPOSITE (a whole-
    Snapshot digest-equality check rejected ANY drift, declared or not) --
    the Controller's Independent Review confirmed that older behavior is
    exactly what makes running two different Production Variants against
    the same Plan structurally impossible (IR-P9-2-R2-01): it forced Live
    to stay bit-for-bit identical, in every slot, for every Variant's own
    Run, which is precisely what the User must be free to change BETWEEN
    two Variant Runs of the same Plan (Handoff R3 SS4.2 Option A)."""

    adapter = FakeProductionTurnPort(request_id="real-req-13")
    live_reader = MutableLiveConfigurationPort(
        current=FakeLiveConfigurationPort(judge_mode="observe", guard_mode="off")
    )
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path, adapter, live_configuration_reader=live_reader
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        case_input = presets["cases"][0]["input"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-13",
                "case_id": case_id,
                "variant_ids": ["judge-observe"],
                "execution_mode": "production",
            },
        )
        # `judge-observe` never declares `guard` at all -- this drift must
        # never block it.
        live_reader.current = FakeLiveConfigurationPort(judge_mode="observe", guard_mode="enforce")
        response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-13",
                "variant_id": "judge-observe",
                "run_id": "run-1",
            },
        )
        assert response.status_code == 202
        run_body = await _wait_for_terminal_run(client, "run-1")
    assert run_body["run"]["state"] == "completed"
    assert adapter.calls == [case_input]


@pytest.mark.asyncio
async def test_two_different_production_variants_execute_and_compare_in_the_same_plan(
    tmp_path: Path,
) -> None:
    """R3-WU-01 Hard Assert (Handoff R3 SS4.3): "同一Planの相互に異なる2
    Variantが両方Run可能" / "Variant AのFrozen ConfigとVariant BのFrozen
    Config Digestが異なる" -- the CENTRAL requirement the Controller's
    Independent Review confirmed R2 never actually met (IR-P9-2-R2-01
    CRITICAL). Main-only and Judge/Repair-ENFORCE, run sequentially
    against the SAME Plan, with the User explicitly re-configuring Live
    Settings between the two Runs (Handoff R3 SS4.2 Option A's own
    intended workflow)."""

    adapter = FakeProductionTurnPort(request_id="real-req-multi")
    live_reader = MutableLiveConfigurationPort(
        current=FakeLiveConfigurationPort(judge_mode="off", repair_mode="off")
    )
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path, adapter, live_configuration_reader=live_reader
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        case_input = presets["cases"][0]["input"]
        plan_response = await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-multi",
                "case_id": case_id,
                "variant_ids": [
                    "production-main-only-baseline",
                    "production-judge-repair-baseline",
                ],
                "execution_mode": "production",
            },
        )
        assert plan_response.status_code == 201
        plan_body = plan_response.json()
        desired_by_variant = {
            item["variant_id"]: item["desired_configuration_digest_sha512"]
            for item in plan_body["variant_configurations"]
        }
        # CRITICAL Hard Assert: two Variants that declare different
        # Components get different Desired digests -- never the same Live
        # Snapshot digest copied across both (IR-P9-2-R2-01).
        assert (
            desired_by_variant["production-main-only-baseline"]
            != desired_by_variant["production-judge-repair-baseline"]
        )

        # Live is already satisfiable for Main-only (Judge/Repair both off).
        run_a = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-multi",
                "variant_id": "production-main-only-baseline",
                "run_id": "run-a",
            },
        )
        assert run_a.status_code == 202
        run_a_body = await _wait_for_terminal_run(client, "run-a")
        assert run_a_body["run"]["state"] == "completed"

        # The User now explicitly re-configures Settings for the second
        # Variant (Handoff R3 SS4.2 Option A) -- Judge/Repair both ENFORCE,
        # with the Gemma Judge Provider this Preset itself declares
        # (R4-WU-01: Presets now pin Provider identity, not just Mode).
        live_reader.current = FakeLiveConfigurationPort(
            judge_mode="enforce", repair_mode="enforce", judge_selector=GEMMA_E2B_JUDGE
        )
        run_b = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-multi",
                "variant_id": "production-judge-repair-baseline",
                "run_id": "run-b",
            },
        )
        assert run_b.status_code == 202
        run_b_body = await _wait_for_terminal_run(client, "run-b")
        assert run_b_body["run"]["state"] == "completed"

        # CRITICAL Hard Assert: the two Runs' own genuine Frozen
        # Configuration digests (captured fresh, at each Run's own Call-0
        # check) are different -- never the same value copied across Runs.
        frozen_a = run_a_body["run"]["frozen_configuration_digest_sha512"]
        frozen_b = run_b_body["run"]["frozen_configuration_digest_sha512"]
        assert frozen_a is not None
        assert frozen_b is not None
        assert frozen_a != frozen_b

        comparison_response = await client.get(
            "/api/v7/experiment/experiments/exp-multi/comparison"
        )
        comparison_body = comparison_response.json()
        rows_by_run_id = {row["run_id"]: row for row in comparison_body["rows"]}
        assert rows_by_run_id["run-a"]["frozen_configuration_digest_sha512"] == frozen_a
        assert rows_by_run_id["run-b"]["frozen_configuration_digest_sha512"] == frozen_b
        assert (
            rows_by_run_id["run-a"]["frozen_configuration_digest_sha512"]
            != rows_by_run_id["run-b"]["frozen_configuration_digest_sha512"]
        )
    assert adapter.calls == [case_input, case_input]


@pytest.mark.asyncio
async def test_production_run_downgrades_to_failed_when_live_config_changes_during_the_turn(
    tmp_path: Path,
) -> None:
    """R2-WU-01's bounded "Lease" Fallback (Handoff R2 SS4.2 Option 3):
    Live Configuration matched at Call 0, but changed WHILE the real Turn
    was still executing -- the Run must never be reported as a
    trustworthy `COMPLETED`, since nothing observed during it can be
    vouched for under a single, stable Configuration throughout."""

    live_reader = MutableLiveConfigurationPort(
        current=FakeLiveConfigurationPort(judge_mode="observe")
    )

    def _drift() -> None:
        live_reader.current = FakeLiveConfigurationPort(judge_mode="enforce")

    adapter = FakeProductionTurnPort(request_id="real-req-12", mutate_live_config=_drift)
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path, adapter, live_configuration_reader=live_reader
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-12",
                "case_id": case_id,
                "variant_ids": ["judge-observe"],
                "execution_mode": "production",
            },
        )
        start_response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-12",
                "variant_id": "judge-observe",
                "run_id": "run-1",
            },
        )
        assert start_response.status_code == 202
        run_body = await _wait_for_terminal_run(client, "run-1")
    assert run_body["run"]["state"] == "failed"
    assert run_body["run"]["failure_reason"] == "live_config_changed_during_run"
    assert adapter.calls == [presets["cases"][0]["input"]]


@pytest.mark.asyncio
async def test_production_run_rejects_a_wrong_main_provider_even_with_matching_mode(
    tmp_path: Path,
) -> None:
    """R4-WU-01 Hard Assert (Handoff R4 SS4.2): `production-main-only-
    baseline` now declares `main` `selector_id=QWEN_MAIN` -- Live Main
    being a DIFFERENT Provider, with the identical `mode="active"`, is
    still a genuine Call-0 mismatch, never passed just because Mode
    agrees."""

    adapter = FakeProductionTurnPort(request_id="real-req-wrong-main")
    live_reader = FakeLiveConfigurationPort(main_selector="main.deepseek-r1-0528-qwen3-8b-q4-k-m")
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path, adapter, live_configuration_reader=live_reader
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-wrong-main",
                "case_id": case_id,
                "variant_ids": ["production-main-only-baseline"],
                "execution_mode": "production",
            },
        )
        response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-wrong-main",
                "variant_id": "production-main-only-baseline",
                "run_id": "run-1",
            },
        )
    assert response.status_code == 409
    assert response.json()["code"] == "live_config_mismatch"
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_production_run_rejects_a_wrong_judge_provider_even_with_matching_mode(
    tmp_path: Path,
) -> None:
    """R4-WU-01 Hard Assert: `production-judge-repair-baseline` declares
    `judge` `selector_id=GEMMA_E2B_JUDGE` `mode="enforce"` -- Live Judge
    being the Main-shared Qwen Provider, ALSO `mode="enforce"`, is still a
    genuine Provider mismatch."""

    adapter = FakeProductionTurnPort(request_id="real-req-wrong-judge")
    live_reader = FakeLiveConfigurationPort(
        judge_mode="enforce", repair_mode="enforce", judge_selector=QWEN_MAIN
    )
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path, adapter, live_configuration_reader=live_reader
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-wrong-judge",
                "case_id": case_id,
                "variant_ids": ["production-judge-repair-baseline"],
                "execution_mode": "production",
            },
        )
        response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-wrong-judge",
                "variant_id": "production-judge-repair-baseline",
                "run_id": "run-1",
            },
        )
    assert response.status_code == 409
    assert response.json()["code"] == "live_config_mismatch"
    assert adapter.calls == []


@pytest.mark.asyncio
async def test_production_run_rejects_a_wrong_guard_provider_even_with_matching_mode(
    tmp_path: Path,
) -> None:
    """R4-WU-01 Hard Assert: `production-guard-baseline` declares `guard`
    `selector_id=QWEN3_GUARD` `mode="enforce"` -- Live Guard being a
    different (hypothetical) Provider, ALSO `mode="enforce"`, is still a
    genuine Provider mismatch."""

    adapter = FakeProductionTurnPort(request_id="real-req-wrong-guard")
    live_reader = FakeLiveConfigurationPort(guard_mode="enforce", guard_selector="guard.other")
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path, adapter, live_configuration_reader=live_reader
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-wrong-guard",
                "case_id": case_id,
                "variant_ids": ["production-guard-baseline"],
                "execution_mode": "production",
            },
        )
        response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-wrong-guard",
                "variant_id": "production-guard-baseline",
                "run_id": "run-1",
            },
        )
    assert response.status_code == 409
    assert response.json()["code"] == "live_config_mismatch"
    assert adapter.calls == []
    # Sanity: the Preset's own declared Guard Provider is QWEN3_GUARD, not
    # the mismatched Live value this test injected.
    assert QWEN3_GUARD != "guard.other"


@pytest.mark.asyncio
async def test_production_run_typed_call_zero_when_the_configuration_lease_is_unavailable(
    tmp_path: Path,
) -> None:
    """R4-WU-02 Hard Assert (Handoff R4 SS5.1): "Lease取得不能...なら
    無保護実行へFallbackせずTyped Call 0とする" -- a Production Composition
    with no Configuration Lease wired at all must never fall back to
    running the real Actor unprotected; it must Typed-Call-0 FAIL instead,
    saved as a genuine Typed Result in the same Experiment Identity Chain
    (never a `pytest.skip`-shaped silent success)."""

    adapter = FakeProductionTurnPort(request_id="real-req-no-lease")
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path, adapter, experiment_configuration_lease=None
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        case_input = presets["cases"][0]["input"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-no-lease",
                "case_id": case_id,
                "variant_ids": ["judge-observe"],
                "execution_mode": "production",
            },
        )
        start_response = await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-no-lease",
                "variant_id": "judge-observe",
                "run_id": "run-1",
            },
        )
        assert start_response.status_code == 202
        run_body = await _wait_for_terminal_run(client, "run-1")
    # Genuine Call 0: the real Adapter's `run_turn()` was NEVER invoked.
    assert adapter.calls == []
    assert case_input  # sanity: a real Case Input existed to (never) send
    assert run_body["run"]["state"] == "failed"
    assert run_body["run"]["failure_reason"] == "configuration_lease_unavailable"
    invocation_by_key = {item["component_key"]: item for item in run_body["invocations"]}
    assert invocation_by_key["main"]["called"] is False
    assert invocation_by_key["main"]["mutation_count"] == 0
    assert invocation_by_key["judge"]["called"] is False
    assert invocation_by_key["guard"]["called"] is False
    assert invocation_by_key["repair"]["called"] is False


@dataclass
class LeaseObservingLiveConfigurationPort:
    """R4-WU-02 Deterministic Race Test: records whether the Configuration
    Lease was already held at the exact moment `.snapshot()` (the FINAL,
    authoritative Live read used for the Call-0 match) was called --
    proving that read happens strictly INSIDE the Lease's own protected
    window, never before it acquires. If the R4-WU-02 fix were reverted
    (the final match moved back to before `worker.submit()`, R3's own
    shape), this would record `False` for that first call instead."""

    lease: ExperimentConfigurationLease
    inner: FakeLiveConfigurationPort
    held_during_snapshot: list[bool] = field(default_factory=list)

    def snapshot(self) -> Any:
        self.held_during_snapshot.append(self.lease.is_held())
        return self.inner.snapshot()

    def provider_identity(self) -> ProviderIdentityEnvelope:
        return self.inner.provider_identity()


@pytest.mark.asyncio
async def test_the_final_live_match_happens_strictly_inside_the_lease_window(
    tmp_path: Path,
) -> None:
    """R4-WU-02 Deterministic Race Test (Handoff R4 SS5.2, first bullet):
    "Snapshot読取直後/Lease取得直前へBarrierを置き、Settings変更を試みても
    Actorが誤構成で呼ばれない" -- the direct, deterministic proof that the
    Live read this Round's Call-0 gate depends on is never taken before
    the Lease that is supposed to protect it is actually held."""

    lease = ExperimentConfigurationLease()
    adapter = FakeProductionTurnPort(request_id="real-req-race")
    live_reader = LeaseObservingLiveConfigurationPort(
        lease=lease, inner=FakeLiveConfigurationPort()
    )
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(
            tmp_path,
            adapter,
            live_configuration_reader=live_reader,
            experiment_configuration_lease=lease,
        ),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-race-lease",
                "case_id": case_id,
                "variant_ids": ["judge-observe"],
                "execution_mode": "production",
            },
        )
        await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-race-lease",
                "variant_id": "judge-observe",
                "run_id": "run-1",
            },
        )
        run_body = await _wait_for_terminal_run(client, "run-1")
    assert run_body["run"]["state"] == "completed"
    # Earlier `.snapshot()` calls (Plan-creation's own Desired-Configuration
    # read, and `start_run()`'s own fast, advisory, UN-Leased pre-check) are
    # legitimately NOT Lease-protected -- only the LAST TWO calls, both
    # made from strictly inside `_invoke_production` (the final,
    # authoritative match, then the post-Turn detective re-check), are the
    # ones this Hard Assert actually covers, and both must observe the
    # Lease already held.
    assert len(live_reader.held_during_snapshot) >= 2
    assert live_reader.held_during_snapshot[-2:] == [True, True]


@pytest.mark.asyncio
async def test_settings_mutation_routes_409_while_the_lease_is_held_and_recover_after(
    tmp_path: Path,
) -> None:
    """R4-WU-02 Deterministic Race Test (Handoff R4 SS5.2): "Actor実行中の
    Judge Mode...が409" / "Actor終了後は同じRouteが通常どおり使える" --
    exercised through the REAL HTTP middleware (`web/app.py`'s
    `secure_requests`), not just the Lease object in isolation. The
    gated route's own body/Controller-wiring is irrelevant here -- the
    Lease check runs in middleware, BEFORE the request ever reaches a
    route handler, so an empty body still proves the gate."""

    release = threading.Event()
    adapter = FakeProductionTurnPort(request_id="real-req-lease-http", release=release)
    app = create_web_app(
        runtime_factory=lambda: _bound_runtime_with_production(tmp_path, adapter),
        access_policy=_LOCAL_POLICY,
    )
    async with client_for(app) as client:
        presets = (await client.get("/api/v7/experiment/presets")).json()
        case_id = presets["cases"][0]["case_id"]
        await client.post(
            "/api/v7/experiment/plans",
            json={
                "experiment_id": "exp-lease-http",
                "case_id": case_id,
                "variant_ids": ["judge-observe"],
                "execution_mode": "production",
            },
        )
        await client.post(
            "/api/v7/experiment/runs",
            json={
                "experiment_id": "exp-lease-http",
                "variant_id": "judge-observe",
                "run_id": "run-1",
            },
        )
        # Give the Worker a moment to actually start the Task and acquire
        # the Lease (it now holds it across the final Live-match AND the
        # real Actor Call, per R4-WU-02).
        await asyncio.sleep(0.05)
        held_response = await client.post("/api/v5/feature-modes/judge", json={})
        assert held_response.status_code == 409
        assert held_response.json()["code"] == "experiment_configuration_lease_held"

        release.set()
        await _wait_for_terminal_run(client, "run-1")

        released_response = await client.post("/api/v5/feature-modes/judge", json={})
        assert released_response.status_code != 409 or (
            released_response.json().get("code") != "experiment_configuration_lease_held"
        )
