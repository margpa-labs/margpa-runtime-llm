"""Dev Agent (`/api/v2/dev-agent`) API integration tests (P8-D/P8-E/P8-CR)."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Event
from typing import cast

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.constitution import JsonFileConstitutionProvider
from margpa_runtime_llm.adapters.dev_agent import FakeToolPort, JsonFileDevAgentRunStore
from margpa_runtime_llm.bootstrap.dev_agent import build_dev_agent_run_service
from margpa_runtime_llm.modules.constitution import (
    ConstitutionMode,
    ConstitutionProviderPort,
    ConstitutionRule,
    compute_manifest_digest,
)
from margpa_runtime_llm.modules.dev_agent import (
    DevAgentRunService,
    DevAgentRunStorePort,
    ImportantGateReason,
    ToolDescriptor,
    ToolExecutionOutcome,
    ToolExecutionSucceeded,
    ToolRegistry,
)
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import SafeRuntimeSnapshot, WebRuntime


class BlockingCountingPort:
    """P8-CR1 REST Focused Test double: blocks inside `execute()` until
    released, so a Test can force two REST `advance` requests to genuinely
    overlap through the real `asyncio.to_thread()` Route dispatch."""

    def __init__(self) -> None:
        self.calls = 0
        self.entered = Event()
        self._release = Event()

    def execute(self, tool_id: str, input: Mapping[str, object]) -> ToolExecutionOutcome:
        del tool_id, input
        self.calls += 1
        self.entered.set()
        self._release.wait(timeout=5)
        return ToolExecutionSucceeded(output={"ok": True})

    def release(self) -> None:
        self._release.set()


class NullConversation:
    def shutdown(self, timeout: float) -> bool:
        del timeout
        return True


def _registry() -> ToolRegistry:
    registry = ToolRegistry()
    fake_tool = FakeToolPort()
    registry.register(
        ToolDescriptor(tool_id="list_files", name="List", description="List."),
        fake_tool,
    )
    registry.register(
        ToolDescriptor(
            tool_id="write_note",
            name="Write",
            description="Write.",
            important_gate_reason=ImportantGateReason.EXTERNAL_WRITE,
        ),
        fake_tool,
    )
    return registry


def _write_constitution_manifest(project_root: Path) -> None:
    rule = ConstitutionRule(
        rule_id="test-only-rule",
        revision=1,
        title="Test-only Rule",
        summary="A minimal Rule used only by this integration Test.",
        applies_to=("agent",),
        source_pointer="rules/test-only-rule.md",
    )
    manifest_dir = project_root / "constitution"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "revision": 1,
        "digest_sha512": compute_manifest_digest((rule,)),
        "rules": [json.loads(rule.model_dump_json())],
    }
    (manifest_dir / "manifest.json").write_text(json.dumps(payload), encoding="utf-8")


def runtime(
    *,
    service: DevAgentRunService | None,
    constitution_provider: ConstitutionProviderPort | None = None,
    constitution_mode: ConstitutionMode = ConstitutionMode.OBSERVE,
) -> WebRuntime:
    return WebRuntime(
        conversation=cast(object, NullConversation()),  # type: ignore[arg-type]
        snapshot=SafeRuntimeSnapshot.model_construct(),
        close_callback=lambda: None,
        dev_agent_run_service=service,
        constitution_provider=constitution_provider,
        constitution_mode=constitution_mode,
    )


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client


def _app(
    service: DevAgentRunService | None,
    *,
    constitution_provider: ConstitutionProviderPort | None = None,
) -> FastAPI:
    return create_web_app(
        runtime_factory=lambda: runtime(
            service=service, constitution_provider=constitution_provider
        ),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )


@pytest.mark.asyncio
async def test_unbound_service_is_safe_404() -> None:
    app = _app(None)
    async with client_for(app) as client:
        response = await client.get("/api/v2/dev-agent/runs/does-not-exist")

    assert response.status_code == 404
    assert response.json()["code"] == "dev_agent_unavailable"


@pytest.mark.asyncio
async def test_capabilities_lists_chat_and_dev_agent() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        response = await client.get("/api/v2/dev-agent/capabilities")

    assert response.status_code == 200
    ids = {row["capability_id"] for row in response.json()}
    assert ids == {"chat", "dev_agent"}


@pytest.mark.asyncio
async def test_tools_lists_registered_descriptors() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        response = await client.get("/api/v2/dev-agent/tools")

    assert response.status_code == 200
    body = {row["tool_id"]: row for row in response.json()}
    assert body["list_files"]["important_gate_reason"] is None
    assert body["write_note"]["important_gate_reason"] == "external_write"


@pytest.mark.asyncio
async def test_golden_path_via_rest_completes() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [{"step_id": "list", "tool_id": "list_files", "input": {}}],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )
        assert started.status_code == 200
        run_id = started.json()["run_id"]

        advanced = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        assert advanced.json()["state"] == "running"
        awaiting_completion = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        assert awaiting_completion.json()["state"] == "awaiting_completion_approval"

        approved_completion = await client.post(
            f"/api/v2/dev-agent/runs/{run_id}/completion-approval",
            json={"decision": "approved"},
        )
        assert approved_completion.json()["state"] == "running"
        finalized = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        assert finalized.json()["state"] == "completed"

        fetched = await client.get(f"/api/v2/dev-agent/runs/{run_id}")
        assert fetched.json()["state"] == "completed"


@pytest.mark.asyncio
async def test_important_gate_only_golden_path_via_rest() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [
                    {
                        "step_id": "write",
                        "tool_id": "write_note",
                        "input": {"path": "a", "content": "b"},
                    }
                ],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )
        run_id = started.json()["run_id"]

        awaiting = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        assert awaiting.json()["state"] == "awaiting_approval"

        approved = await client.post(
            f"/api/v2/dev-agent/runs/{run_id}/approvals",
            json={"step_id": "write", "decision": "approved"},
        )
        assert approved.json()["state"] == "running"

        step_done = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        assert step_done.json()["steps"][0]["state"] == "succeeded"
        awaiting_completion = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        assert awaiting_completion.json()["state"] == "awaiting_completion_approval"

        approved_completion = await client.post(
            f"/api/v2/dev-agent/runs/{run_id}/completion-approval",
            json={"decision": "approved"},
        )
        assert approved_completion.json()["state"] == "running"
        finalized = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        assert finalized.json()["state"] == "completed"


@pytest.mark.asyncio
async def test_informed_approval_shows_the_real_input_before_and_output_after(
    tmp_path: Path,
) -> None:
    """P8-MR5 (P8-MANUAL-005): the exact Blind Approval gap the User
    reported — before Approval, the Step's real `input` (Target Path/Write
    Content) must be visible via REST; after Approval, the real `output`
    (Digest/Overwrite/Written At) must be visible too. Uses the real
    Production Composition (`build_dev_agent_run_service`) against a Temp
    Root — never the User's actual `runtime_data/` — so this Test also
    proves the traceable real-File Fixture Workspace Adapter is genuinely
    wired end-to-end through REST, not just at the unit level."""

    service = build_dev_agent_run_service(runtime_data_root=tmp_path, scope_key="default")
    app = _app(service)
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [
                    {
                        "step_id": "write",
                        "tool_id": "write_note",
                        "input": {"path": "notes/new.md", "content": "Hello from the Test."},
                    }
                ],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )
        run_id = started.json()["run_id"]

        awaiting = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        awaiting_body = awaiting.json()
        assert awaiting_body["state"] == "awaiting_approval"
        # Informed Approval: the real intended Action is visible BEFORE the
        # User ever approves it.
        pending_step = awaiting_body["steps"][0]
        assert pending_step["input"] == {"path": "notes/new.md", "content": "Hello from the Test."}
        assert pending_step["output"] is None
        # Resource Scope / Gate Reason are visible from the Envelope too.
        assert awaiting_body["envelope"]["resource_scope"] == "fixture_only"
        assert awaiting_body["envelope"]["gate_reasons"] == ["external_write"]

        approved = await client.post(
            f"/api/v2/dev-agent/runs/{run_id}/approvals",
            json={"step_id": "write", "decision": "approved"},
        )
        assert approved.json()["state"] == "running"

        step_done = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        done_step = step_done.json()["steps"][0]
        assert done_step["state"] == "succeeded"
        # The real Result — Digest, Overwrite, Written At — is visible
        # AFTER Approval too, never just "succeeded" with no detail.
        output = done_step["output"]
        assert output["path"] == "notes/new.md"
        assert output["written"] is True
        assert output["overwrite"] is False
        assert isinstance(output["content_sha512"], str) and len(output["content_sha512"]) == 128
        assert isinstance(output["written_at"], str)

        # The Write genuinely landed on real disk, confined to the Fixture
        # Workspace — not merely reported as succeeded.
        written_path = (
            tmp_path
            / "persistent"
            / "default"
            / "dev_agent"
            / "fixture_workspace"
            / "notes"
            / "new.md"
        )
        assert written_path.is_file()
        assert written_path.read_text(encoding="utf-8") == "Hello from the Test."


@pytest.mark.asyncio
async def test_denied_write_never_touches_the_real_fixture_workspace(tmp_path: Path) -> None:
    """P8-MR5 Required Test: an unapproved/Denied/Cancelled Write must never
    create `notes/new.md` — proven against the real Adapter, not the
    in-memory Fake."""

    service = build_dev_agent_run_service(runtime_data_root=tmp_path, scope_key="default")
    app = _app(service)
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [
                    {
                        "step_id": "write",
                        "tool_id": "write_note",
                        "input": {"path": "notes/new.md", "content": "must never be written"},
                    }
                ],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )
        run_id = started.json()["run_id"]
        await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        denied = await client.post(
            f"/api/v2/dev-agent/runs/{run_id}/approvals",
            json={"step_id": "write", "decision": "denied"},
        )
        assert denied.json()["steps"][0]["state"] == "denied"

    written_path = (
        tmp_path / "persistent" / "default" / "dev_agent" / "fixture_workspace" / "notes" / "new.md"
    )
    assert not written_path.exists()


@pytest.mark.asyncio
async def test_run_not_found_is_safe_404() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        response = await client.post("/api/v2/dev-agent/runs/does-not-exist/advance")

    assert response.status_code == 404
    assert response.json()["code"] == "dev_agent_run_not_found"


@pytest.mark.asyncio
async def test_approval_on_wrong_step_is_safe_409_not_500() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [
                    {
                        "step_id": "write",
                        "tool_id": "write_note",
                        "input": {"path": "a", "content": "b"},
                    }
                ],
                "approval_profile": "manual",
                "max_steps": 5,
            },
        )
        run_id = started.json()["run_id"]
        await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")

        response = await client.post(
            f"/api/v2/dev-agent/runs/{run_id}/approvals",
            json={"step_id": "not-the-real-step", "decision": "approved"},
        )

    assert response.status_code == 409
    assert response.json()["code"] == "dev_agent_invalid_transition"


@pytest.mark.asyncio
async def test_cancel_via_rest_finalizes_run() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [{"step_id": "list", "tool_id": "list_files", "input": {}}],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )
        run_id = started.json()["run_id"]

        cancelled = await client.post(f"/api/v2/dev-agent/runs/{run_id}/cancel")

    assert cancelled.status_code == 200
    assert cancelled.json()["state"] == "cancelled"
    assert cancelled.json()["completion"]["outcome"] == "cancelled"


@pytest.mark.asyncio
async def test_start_run_correlates_with_the_bound_constitution(tmp_path: Path) -> None:
    _write_constitution_manifest(tmp_path)
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = _app(DevAgentRunService(tool_registry=_registry()), constitution_provider=provider)
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [{"step_id": "list", "tool_id": "list_files", "input": {}}],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )

    body = started.json()
    assert body["constitution_mode"] == "observe"
    assert body["constitution_rule_ids"] == ["test-only-rule"]


@pytest.mark.asyncio
async def test_start_run_without_a_bound_constitution_is_honestly_none() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [{"step_id": "list", "tool_id": "list_files", "input": {}}],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )

    body = started.json()
    assert body["constitution_mode"] is None
    assert body["constitution_rule_ids"] is None


@pytest.mark.asyncio
async def test_restart_recovers_a_run_across_two_independent_apps(tmp_path: Path) -> None:
    """Models a real process Restart end to end: a Run started against one
    App/Service pair must be visible, and resumable, from a second
    App/Service pair reading the same on-disk Run Store."""

    store: DevAgentRunStorePort = JsonFileDevAgentRunStore(
        runtime_data_root=tmp_path, scope_key="default"
    )
    first_app = _app(DevAgentRunService(tool_registry=_registry(), run_store=store))
    async with client_for(first_app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [{"step_id": "list", "tool_id": "list_files", "input": {}}],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )
        run_id = started.json()["run_id"]
        await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")

    second_app = _app(DevAgentRunService(tool_registry=_registry(), run_store=store))
    async with client_for(second_app) as client:
        recovered = await client.get(f"/api/v2/dev-agent/runs/{run_id}")
        assert recovered.status_code == 200
        assert recovered.json()["steps"][0]["state"] == "succeeded"

        awaiting_completion = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        assert awaiting_completion.json()["state"] == "awaiting_completion_approval"
        approved_completion = await client.post(
            f"/api/v2/dev-agent/runs/{run_id}/completion-approval",
            json={"decision": "approved"},
        )
        assert approved_completion.json()["state"] == "running"
        finalized = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        assert finalized.json()["state"] == "completed"


@pytest.mark.asyncio
async def test_plan_only_profile_via_rest_never_executes() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [{"step_id": "list", "tool_id": "list_files", "input": {}}],
                "approval_profile": "plan_only",
                "max_steps": 5,
            },
        )
        run_id = started.json()["run_id"]

        finalized = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")

    assert finalized.json()["state"] == "completed"
    assert finalized.json()["completion"]["outcome"] == "plan_only"
    assert finalized.json()["steps"][0]["state"] == "pending"


@pytest.mark.asyncio
async def test_start_run_issues_an_authorization_envelope_via_rest() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [
                    {
                        "step_id": "write",
                        "tool_id": "write_note",
                        "input": {"path": "a", "content": "b"},
                    }
                ],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )

    body = started.json()
    envelope = body["envelope"]
    assert envelope is not None
    assert envelope["run_id"] == body["run_id"]
    assert envelope["allowed_step_ids"] == ["write"]
    assert envelope["allowed_tool_ids"] == ["write_note"]
    assert envelope["resource_scope"] == "fixture_only"
    assert envelope["gate_reasons"] == ["external_write"]
    assert body["approvals"] == []


@pytest.mark.asyncio
async def test_start_run_issues_a_default_budget_limit_via_rest() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [{"step_id": "list", "tool_id": "list_files", "input": {}}],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )

    body = started.json()
    assert body["budget_limit"] == 100
    assert body["budget_consumed"] == 0


@pytest.mark.asyncio
async def test_budget_exceeded_via_rest_never_executes_the_tool() -> None:
    """P8-RW6-B (P8-CODEX-006): a caller-supplied low `budget_limit`
    exceeded by the Plan's own Tool cost converges to `budget_exceeded`
    through the real REST path, Tool never executed."""

    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [
                    {"step_id": "step-a", "tool_id": "list_files", "input": {}},
                    {"step_id": "step-b", "tool_id": "list_files", "input": {}},
                ],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
                "budget_limit": 1,
            },
        )
        run_id = started.json()["run_id"]
        first_step = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        assert first_step.json()["steps"][0]["state"] == "succeeded"
        exceeded = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")

    assert exceeded.json()["state"] == "failed"
    assert exceeded.json()["completion"]["outcome"] == "budget_exceeded"
    assert exceeded.json()["steps"][1]["output"] is None


@pytest.mark.asyncio
async def test_approval_evidence_is_returned_via_rest_and_survives_restart(
    tmp_path: Path,
) -> None:
    store: DevAgentRunStorePort = JsonFileDevAgentRunStore(
        runtime_data_root=tmp_path, scope_key="default"
    )
    first_app = _app(DevAgentRunService(tool_registry=_registry(), run_store=store))
    async with client_for(first_app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [
                    {
                        "step_id": "write",
                        "tool_id": "write_note",
                        "input": {"path": "a", "content": "b"},
                    }
                ],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )
        run_id = started.json()["run_id"]
        await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
        approved = await client.post(
            f"/api/v2/dev-agent/runs/{run_id}/approvals",
            json={"step_id": "write", "decision": "approved"},
        )
    assert len(approved.json()["approvals"]) == 1
    assert approved.json()["approvals"][0]["decision"] == "approved"
    assert approved.json()["approvals"][0]["gate_reason"] == "external_write"

    second_app = _app(DevAgentRunService(tool_registry=_registry(), run_store=store))
    async with client_for(second_app) as client:
        recovered = await client.get(f"/api/v2/dev-agent/runs/{run_id}")
        assert recovered.status_code == 200
        recovered_body = recovered.json()
        assert len(recovered_body["approvals"]) == 1
        assert recovered_body["approvals"][0]["step_id"] == "write"
        assert recovered_body["envelope"] is not None

        finalized = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")
    assert finalized.json()["steps"][0]["state"] == "succeeded"


@pytest.mark.asyncio
async def test_concurrent_advance_via_rest_executes_tool_exactly_once() -> None:
    """P8-CODEX-001 REST-level Evidence: two concurrent `POST .../advance`
    requests, dispatched exactly the way Production Routes dispatch them
    (`asyncio.to_thread()` against one shared `DevAgentRunService`), must
    still result in exactly one Tool execution — the same Atomic Boundary
    `test_concurrent_advance_executes_tool_exactly_once` (Unit level)
    proves is real, now exercised through the actual REST path."""

    registry = ToolRegistry()
    port = BlockingCountingPort()
    registry.register(ToolDescriptor(tool_id="slow", name="Slow", description="Slow."), port)
    app = _app(DevAgentRunService(tool_registry=registry))

    async def _release_once_entered() -> None:
        await asyncio.to_thread(port.entered.wait, 5)
        await asyncio.sleep(0.05)
        port.release()

    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [{"step_id": "only", "tool_id": "slow", "input": {}}],
                "approval_profile": "important_gate_only",
                "max_steps": 5,
            },
        )
        run_id = started.json()["run_id"]

        first, second, _ = await asyncio.gather(
            client.post(f"/api/v2/dev-agent/runs/{run_id}/advance"),
            client.post(f"/api/v2/dev-agent/runs/{run_id}/advance"),
            _release_once_entered(),
        )

    assert port.calls == 1
    states = {first.json()["state"], second.json()["state"]}
    # P8-RW6-C: `important_gate_only` gates Completion itself, so the second
    # (post-execution) `advance()` lands on `awaiting_completion_approval`,
    # not `completed` — the exactly-once execution guarantee is what this
    # Test actually verifies (`port.calls == 1`, above).
    assert states <= {"running", "awaiting_completion_approval"}
    assert "running" in states or "awaiting_completion_approval" in states


@pytest.mark.asyncio
async def test_a_legacy_run_without_an_envelope_is_still_advanceable_via_rest(
    tmp_path: Path,
) -> None:
    """Backward Compatibility via REST: a Run Store file written before
    P8-CR2 existed (no `envelope`/`approvals` keys) must still be readable
    and advanceable through the real API, not rejected as Corrupt."""

    run_dir = tmp_path / "persistent" / "default" / "dev_agent" / "runs"
    run_dir.mkdir(parents=True)
    legacy_payload = {
        "schema_version": 1,
        "run": {
            "schema_version": "1",
            "run_id": "legacy-run",
            "capability_id": "dev_agent",
            "plan": {
                "schema_version": "1",
                "steps": [
                    {
                        "schema_version": "1",
                        "step_id": "list",
                        "tool_id": "list_files",
                        "input": {},
                    }
                ],
            },
            "approval_profile": "important_gate_only",
            "retry_policy": {"schema_version": "1", "max_attempts": 1},
            "max_steps": 5,
            "state": "running",
            "steps": [
                {
                    "schema_version": "1",
                    "step_id": "list",
                    "tool_id": "list_files",
                    "state": "pending",
                    "attempt_count": 0,
                    "output": None,
                    "error": None,
                    "completed_at": None,
                    "approved": False,
                }
            ],
            "created_at": "2026-08-30T00:00:00+00:00",
            "deadline_at": None,
            "completion": None,
            "constitution_mode": None,
            "constitution_rule_ids": None,
        },
    }
    (run_dir / "legacy-run.json").write_text(json.dumps(legacy_payload), encoding="utf-8")

    store: DevAgentRunStorePort = JsonFileDevAgentRunStore(
        runtime_data_root=tmp_path, scope_key="default"
    )
    app = _app(DevAgentRunService(tool_registry=_registry(), run_store=store))
    async with client_for(app) as client:
        recovered = await client.get("/api/v2/dev-agent/runs/legacy-run")
        assert recovered.status_code == 200
        assert recovered.json()["envelope"] is None
        assert recovered.json()["approvals"] == []

        advanced = await client.post("/api/v2/dev-agent/runs/legacy-run/advance")
    assert advanced.json()["steps"][0]["state"] == "succeeded"


@pytest.mark.asyncio
async def test_risk_based_profile_via_rest_gates_important_tools() -> None:
    app = _app(DevAgentRunService(tool_registry=_registry()))
    async with client_for(app) as client:
        started = await client.post(
            "/api/v2/dev-agent/runs",
            json={
                "capability_id": "dev_agent",
                "steps": [
                    {
                        "step_id": "write",
                        "tool_id": "write_note",
                        "input": {"path": "a", "content": "b"},
                    }
                ],
                "approval_profile": "risk_based",
                "max_steps": 5,
            },
        )
        run_id = started.json()["run_id"]

        awaiting = await client.post(f"/api/v2/dev-agent/runs/{run_id}/advance")

    assert awaiting.json()["state"] == "awaiting_approval"
