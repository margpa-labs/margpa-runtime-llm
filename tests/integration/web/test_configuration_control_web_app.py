"""Local configuration-control API and exposure integration tests."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.modules.configuration_control import (
    ApplyDisposition,
    ConfigurationControlService,
    ConfigurationField,
    ConfigurationSource,
    DocumentationRagControlMode,
    FeatureHookDescriptor,
    RecordingControlMode,
    RecordingHookDescriptor,
)
from margpa_runtime_llm.web.access_profiles import WebExposureMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import SafeRuntimeSnapshot, WebRuntime


class NullConversation:
    def shutdown(self, timeout: float) -> bool:
        del timeout
        return True


def configuration_service() -> ConfigurationControlService:
    values: tuple[tuple[str, str | int, ApplyDisposition], ...] = (
        ("selected_model", "main.model", ApplyDisposition.RESTART_REQUIRED),
        ("profile_key", "local.profile", ApplyDisposition.READ_ONLY),
        ("context_size", 4096, ApplyDisposition.RESTART_REQUIRED),
        ("backend_kind", "metal", ApplyDisposition.READ_ONLY),
        ("device_kind", "gpu", ApplyDisposition.READ_ONLY),
        ("acceleration_api", "metal", ApplyDisposition.READ_ONLY),
        ("max_new_tokens", 2048, ApplyDisposition.READ_ONLY),
        ("research_developer_mode", "off", ApplyDisposition.RUNTIME_APPLICABLE),
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
    )


def runtime(*, bound: bool) -> WebRuntime:
    return WebRuntime(
        conversation=cast(object, NullConversation()),  # type: ignore[arg-type]
        snapshot=SafeRuntimeSnapshot.model_construct(),
        close_callback=lambda: None,
        configuration_control=configuration_service() if bound else None,
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
async def test_unbound_routes_are_safe_404_and_root_bootstrap_is_disabled() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(bound=False),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        unavailable = await client.get("/api/v2/configuration/runtime")
        root = await client.get("/")

    assert unavailable.status_code == 404
    assert unavailable.json() == {
        "code": "configuration_control_unavailable",
        "message": "Configuration control is unavailable.",
    }
    assert '{"enabled":false}' in root.text
    assert "digest_sha512" not in root.text


@pytest.mark.asyncio
async def test_local_bound_runtime_projects_safe_state_and_applies_live_mode() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        root = await client.get("/")
        capability = await client.get("/api/v2/configuration/runtime")
        effective = await client.get("/api/v2/configuration/effective")
        snapshot = effective.json()
        preview = await client.post(
            "/api/v2/configuration/preview",
            json={"patch": {"selected_model": "candidate.model"}},
        )
        apply = await client.post(
            "/api/v2/configuration/apply",
            json={
                "operation_id": "apply-research",
                "expected_revision": snapshot["revision"],
                "expected_digest": snapshot["digest_sha512"],
                "patch": {"research_developer_mode": "on"},
            },
        )

    assert '{"enabled":true}' in root.text
    assert "digest_sha512" not in root.text
    assert capability.json()["non_persistent"] is True
    assert effective.status_code == 200
    assert len(snapshot["digest_sha512"]) == 128
    assert {item["key"] for item in snapshot["fields"]} == {
        "selected_model",
        "profile_key",
        "context_size",
        "backend_kind",
        "device_kind",
        "acceleration_api",
        "max_new_tokens",
        "research_developer_mode",
    }
    assert preview.json()["outcome"] == "restart_required"
    assert apply.json()["outcome"] == "applied"
    projection = str(snapshot)
    assert "secret" not in projection.casefold()
    assert "/private/" not in projection


@pytest.mark.asyncio
async def test_conflict_duplicate_invalid_and_restart_apply_are_safe_and_atomic() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        initial = (await client.get("/api/v2/configuration/effective")).json()
        restart = await client.post(
            "/api/v2/configuration/apply",
            json={
                "operation_id": "restart-only",
                "expected_revision": initial["revision"],
                "expected_digest": initial["digest_sha512"],
                "patch": {
                    "research_developer_mode": "on",
                    "context_size": 8192,
                },
            },
        )
        unchanged = (await client.get("/api/v2/configuration/effective")).json()
        applied = await client.post(
            "/api/v2/configuration/apply",
            json={
                "operation_id": "live",
                "expected_revision": initial["revision"],
                "expected_digest": initial["digest_sha512"],
                "patch": {"research_developer_mode": "on"},
            },
        )
        current = (await client.get("/api/v2/configuration/effective")).json()
        duplicate = await client.post(
            "/api/v2/configuration/apply",
            json={
                "operation_id": "live",
                "expected_revision": current["revision"],
                "expected_digest": current["digest_sha512"],
                "patch": {"research_developer_mode": "off"},
            },
        )
        stale = await client.post(
            "/api/v2/configuration/apply",
            json={
                "operation_id": "stale",
                "expected_revision": initial["revision"],
                "expected_digest": initial["digest_sha512"],
                "patch": {"research_developer_mode": "off"},
            },
        )
        protected = await client.post(
            "/api/v2/configuration/preview",
            json={"patch": {"protected_capture": True}},
        )

    assert restart.json()["outcome"] == "restart_required"
    assert unchanged == initial
    assert applied.json()["outcome"] == "applied"
    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "operation_already_applied"
    assert stale.status_code == 409
    assert stale.json()["code"] == "configuration_conflict"
    assert protected.status_code == 422


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
async def test_shared_exposure_rejects_accidental_control_binding(policy: WebAccessPolicy) -> None:
    app = create_web_app(runtime_factory=lambda: runtime(bound=True), access_policy=policy)

    with pytest.raises(RuntimeError, match="Configuration control requires local"):
        async with app.router.lifespan_context(app):
            pass
