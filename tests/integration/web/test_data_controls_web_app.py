"""Data Controls (`/api/v2/data-controls`) API and exposure integration tests (P7-G)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import cast

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.data_controls import JsonFileDataControlConsentStore
from margpa_runtime_llm.web.access_profiles import WebExposureMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import SafeRuntimeSnapshot, WebRuntime


class NullConversation:
    def shutdown(self, timeout: float) -> bool:
        del timeout
        return True


def runtime(*, tmp_path: Path, bound: bool) -> WebRuntime:
    store = (
        JsonFileDataControlConsentStore(runtime_data_root=tmp_path / "runtime_data")
        if bound
        else None
    )
    return WebRuntime(
        conversation=cast(object, NullConversation()),  # type: ignore[arg-type]
        snapshot=SafeRuntimeSnapshot.model_construct(),
        close_callback=lambda: None,
        data_controls_store=store,
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
async def test_unbound_routes_are_safe_404_and_root_bootstrap_is_disabled(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=False),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        unavailable = await client.get("/api/v2/data-controls/policy")
        root = await client.get("/")

    assert unavailable.status_code == 404
    assert unavailable.json() == {
        "code": "data_controls_unavailable",
        "message": "Data Controls is unavailable.",
    }
    assert (
        '<script id="data-controls-bootstrap" type="application/json">{"enabled":false}</script>'
        in root.text
    )


@pytest.mark.asyncio
async def test_bound_store_flips_root_bootstrap_to_enabled(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        root = await client.get("/")

    assert (
        '<script id="data-controls-bootstrap" type="application/json">{"enabled":true}</script>'
        in root.text
    )


@pytest.mark.asyncio
async def test_default_policy_has_all_consent_off_and_retention_facts(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/data-controls/policy")

    body = response.json()
    assert body["consent"]["feedback_research_use"] is False
    assert body["consent"]["synthetic_data_use"] is False
    assert body["consent"]["future_training_export"] is False
    assert body["consent"]["external_query_transmission_consent"] is False
    assert len(body["retention_facts"]) >= 3
    assert any(fact["source_class"] == "public_web" for fact in body["retention_facts"])


@pytest.mark.asyncio
async def test_update_consent_and_reset_round_trips(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        updated = await client.put(
            "/api/v2/data-controls/consent",
            json={"feedback_research_use": True},
        )
        after_update = await client.get("/api/v2/data-controls/policy")
        reset = await client.post("/api/v2/data-controls/reset")

    assert updated.json()["consent"]["feedback_research_use"] is True
    assert after_update.json()["consent"]["feedback_research_use"] is True
    assert reset.json()["consent"]["feedback_research_use"] is False


@pytest.mark.asyncio
async def test_saving_consent_never_claims_training_occurred(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.put(
            "/api/v2/data-controls/consent",
            json={"future_training_export": True},
        )

    projection = str(response.json())
    assert "training_complete" not in projection
    assert "trained" not in projection.casefold()


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
async def test_shared_exposure_rejects_accidental_data_controls_binding(
    policy: WebAccessPolicy,
    tmp_path: Path,
) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=True),
        access_policy=policy,
    )

    with pytest.raises(RuntimeError, match="Data Controls requires local"):
        async with app.router.lifespan_context(app):
            pass
