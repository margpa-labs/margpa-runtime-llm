"""Local Governance Definitions read-only status API, Public/Basic
zero-binding, and Configuration-Control-mediated Mode Apply integration
tests (P3-F-WU-003, P3-CODEX-001 rework)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import cast

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.bootstrap.governance_definitions import (
    build_governance_definitions_runtime,
)
from margpa_runtime_llm.modules.configuration_control import (
    ApplyDisposition,
    ConfigurationControlService,
    ConfigurationField,
    ConfigurationSource,
    DocumentationRagControlMode,
    FeatureHookDescriptor,
    GovernanceControlMode,
    GovernanceHookDescriptor,
    RecordingControlMode,
    RecordingHookDescriptor,
)
from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode
from margpa_runtime_llm.modules.governance_definitions.runtime import (
    GovernanceDefinitionsRuntime,
)
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import SafeRuntimeSnapshot, WebRuntime

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITIONS_ROOT = PROJECT_ROOT / "definitions"

_GOVERNANCE_ALLOWED_MODES = (GovernanceControlMode.OFF, GovernanceControlMode.OBSERVE)


class NullConversation:
    def shutdown(self, timeout: float) -> bool:
        del timeout
        return True


class _TestGovernanceModeApplier:
    """Minimal `GovernanceModeApplierPort` implementation bridging straight
    to a real `GovernanceDefinitionsRuntime`, mirroring the production
    `_GovernanceModeApplierAdapter` in `bootstrap/configuration_control.py`."""

    def __init__(self, runtime: GovernanceDefinitionsRuntime) -> None:
        self._runtime = runtime

    def apply(self, mode: GovernanceControlMode) -> GovernanceHookDescriptor:
        snapshot = self._runtime.apply_mode(GovernanceMode(mode.value))
        return GovernanceHookDescriptor(
            component_key="governance_mode",
            allowed_modes=_GOVERNANCE_ALLOWED_MODES,
            current_mode=GovernanceControlMode(snapshot.current_mode.value),
            available=True,
        )


def _configuration_service(
    governance_definitions_runtime: GovernanceDefinitionsRuntime,
) -> ConfigurationControlService:
    values: tuple[tuple[str, str | int, ApplyDisposition], ...] = (
        ("selected_model", "main.model", ApplyDisposition.RESTART_REQUIRED),
        ("profile_key", "local.profile", ApplyDisposition.READ_ONLY),
        ("context_size", 4096, ApplyDisposition.RESTART_REQUIRED),
        ("backend_kind", "metal", ApplyDisposition.READ_ONLY),
        ("device_kind", "gpu", ApplyDisposition.READ_ONLY),
        ("acceleration_api", "metal", ApplyDisposition.READ_ONLY),
        ("max_new_tokens", 2048, ApplyDisposition.READ_ONLY),
        ("research_developer_mode", "off", ApplyDisposition.RUNTIME_APPLICABLE),
        ("conversation_storage_kind", "sqlite", ApplyDisposition.READ_ONLY),
        ("conversation_storage_version", "3.45.1", ApplyDisposition.READ_ONLY),
    )
    return ConfigurationControlService(
        fields=tuple(
            ConfigurationField(
                key=key,
                value=value,
                source=ConfigurationSource.APPLICATION,
                apply_disposition=disposition,
            )
            for key, value, disposition in values
        ),
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
        governance_hooks=(
            GovernanceHookDescriptor(
                component_key="governance_mode",
                allowed_modes=_GOVERNANCE_ALLOWED_MODES,
                current_mode=GovernanceControlMode(
                    governance_definitions_runtime.mode_snapshot().current_mode.value
                ),
                available=True,
            ),
        ),
        governance_mode_applier=_TestGovernanceModeApplier(governance_definitions_runtime),
    )


def _web_runtime(governance_definitions_runtime: GovernanceDefinitionsRuntime) -> WebRuntime:
    return WebRuntime(
        conversation=cast(object, NullConversation()),  # type: ignore[arg-type]
        snapshot=SafeRuntimeSnapshot.model_construct(),
        close_callback=lambda: None,
        configuration_control=_configuration_service(governance_definitions_runtime),
    )


def _bare_web_runtime() -> WebRuntime:
    return WebRuntime(
        conversation=cast(object, NullConversation()),  # type: ignore[arg-type]
        snapshot=SafeRuntimeSnapshot.model_construct(),
        close_callback=lambda: None,
    )


@asynccontextmanager
async def client_for(app: FastAPI) -> AsyncIterator[httpx.AsyncClient]:
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            yield client


def _app(*, enabled: bool) -> FastAPI:
    governance_runtime = (
        build_governance_definitions_runtime(definitions_root=DEFINITIONS_ROOT) if enabled else None
    )
    app = create_web_app(
        runtime_factory=(
            (lambda: _web_runtime(cast(GovernanceDefinitionsRuntime, governance_runtime)))
            if enabled
            else _bare_web_runtime
        ),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    app.state.governance_definitions_runtime = governance_runtime
    return app


async def _apply_governance_mode(client: httpx.AsyncClient, requested_mode: str) -> httpx.Response:
    effective = await client.get("/api/v2/configuration/effective")
    body = effective.json()
    return await client.post(
        "/api/v2/configuration/apply",
        json={
            "operation_id": f"governance-apply-{requested_mode}",
            "expected_revision": body["revision"],
            "expected_digest": body["digest_sha512"],
            "patch": {"governance_mode": requested_mode},
        },
    )


@pytest.mark.asyncio
async def test_unbound_route_is_safe_404_public_basic_zero_binding() -> None:
    app = _app(enabled=False)
    async with client_for(app) as client:
        response = await client.get("/api/v3/governance/runtime")
    assert response.status_code == 404
    assert response.json() == {
        "code": "governance_definitions_unavailable",
        "message": "Phase 3 Governance Definitions is unavailable.",
    }


@pytest.mark.asyncio
async def test_status_reports_off_by_default() -> None:
    app = _app(enabled=True)
    async with client_for(app) as client:
        response = await client.get("/api/v3/governance/runtime")
    assert response.status_code == 200
    body = response.json()
    assert body["mode"]["current_mode"] == "off"
    by_mode = {d["mode"]: d for d in body["mode"]["descriptors"]}
    assert by_mode["off"]["availability"] == "available"
    assert by_mode["observe"]["availability"] == "available"
    assert by_mode["enforce"]["availability"] == "unavailable"
    assert body["observe_summary"] is None


@pytest.mark.asyncio
async def test_the_dedicated_mode_mutation_endpoint_no_longer_exists() -> None:
    """P3-CODEX-001: `/api/v3/governance/*` is Read-only now — Mode
    Mutation moved to Configuration Control's Preview/Apply."""

    app = _app(enabled=True)
    async with client_for(app) as client:
        response = await client.post("/api/v3/governance/mode", json={"requested_mode": "observe"})
    assert response.status_code in (404, 405)


@pytest.mark.asyncio
async def test_apply_observe_via_configuration_control_reflects_the_real_bundle() -> None:
    app = _app(enabled=True)
    async with client_for(app) as client:
        apply_response = await _apply_governance_mode(client, "observe")
        assert apply_response.status_code == 200
        assert apply_response.json()["outcome"] == "applied"

        status_response = await client.get("/api/v3/governance/runtime")
        effective_response = await client.get("/api/v2/configuration/effective")
    body = status_response.json()
    assert body["mode"]["current_mode"] == "observe"
    assert body["observe_summary"]["package_found"] is True
    assert body["observe_summary"]["definition_count"] == 18
    assert body["observe_summary"]["valid_definition_count"] == 18

    governance_hook = effective_response.json()["governance_hooks"][0]
    assert governance_hook["current_mode"] == "observe"


@pytest.mark.asyncio
async def test_apply_enforce_is_rejected_at_the_schema_level_not_silently_downgraded() -> None:
    app = _app(enabled=True)
    async with client_for(app) as client:
        response = await _apply_governance_mode(client, "enforce")
        assert response.status_code == 422  # not a member of GovernanceControlMode at all

        status_response = await client.get("/api/v3/governance/runtime")
    # The rejected request must not have silently landed on "observe".
    assert status_response.json()["mode"]["current_mode"] == "off"


@pytest.mark.asyncio
async def test_apply_unknown_mode_string_is_rejected_with_422() -> None:
    app = _app(enabled=True)
    async with client_for(app) as client:
        response = await _apply_governance_mode(client, "not_a_real_mode")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_a_stale_cas_token_is_rejected_with_409_not_silently_applied() -> None:
    app = _app(enabled=True)
    async with client_for(app) as client:
        response = await client.post(
            "/api/v2/configuration/apply",
            json={
                "operation_id": "governance-apply-stale",
                "expected_revision": 999,
                "expected_digest": "0" * 128,
                "patch": {"governance_mode": "observe"},
            },
        )
        assert response.status_code == 409

        status_response = await client.get("/api/v3/governance/runtime")
    assert status_response.json()["mode"]["current_mode"] == "off"


@pytest.mark.asyncio
async def test_response_never_leaks_absolute_source_path() -> None:
    app = _app(enabled=True)
    async with client_for(app) as client:
        await _apply_governance_mode(client, "observe")
        response = await client.get("/api/v3/governance/runtime")
    rendered = response.text
    assert str(PROJECT_ROOT) not in rendered
    assert "Traceback" not in rendered
