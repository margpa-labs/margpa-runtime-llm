"""Web Search (`/api/v2/web-search`) API and exposure integration tests (P7-E/F)."""

from __future__ import annotations

import socket
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.bootstrap.web_knowledge import build_web_knowledge_service
from margpa_runtime_llm.modules.web_knowledge.contracts import WebEvidenceGovernanceMode
from margpa_runtime_llm.web.access_profiles import WebExposureMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import SafeRuntimeSnapshot, WebRuntime


class NullConversation:
    def shutdown(self, timeout: float) -> bool:
        del timeout
        return True


@pytest.fixture(autouse=True)
def _no_real_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, proto
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)


def runtime(
    *,
    bound: bool,
    governance_mode: WebEvidenceGovernanceMode = WebEvidenceGovernanceMode.OFF,
) -> WebRuntime:
    return WebRuntime(
        conversation=cast(object, NullConversation()),  # type: ignore[arg-type]
        snapshot=SafeRuntimeSnapshot.model_construct(),
        close_callback=lambda: None,
        web_knowledge_service=build_web_knowledge_service() if bound else None,
        web_search_governance_mode=governance_mode,
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
        unavailable = await client.post("/api/v2/web-search/search", json={"query": "python"})
        root = await client.get("/")

    assert unavailable.status_code == 404
    assert unavailable.json() == {
        "code": "web_search_unavailable",
        "message": "Web Search is unavailable.",
    }
    assert (
        '<script id="web-search-bootstrap" type="application/json">{"enabled":false}</script>'
        in (root.text)
    )


@pytest.mark.asyncio
async def test_bound_service_flips_root_bootstrap_to_enabled() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        root = await client.get("/")

    assert (
        '<script id="web-search-bootstrap" type="application/json">{"enabled":true}</script>'
        in (root.text)
    )


@pytest.mark.asyncio
async def test_disabled_activation_makes_zero_network_calls() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.post(
            "/api/v2/web-search/search",
            json={"query": "python", "activation": "disabled"},
        )

    body = response.json()
    assert body["network_calls_made"] == 0
    assert body["failure_reason"] == "search_disabled"
    assert body["evidence"] == []


@pytest.mark.asyncio
async def test_manual_search_golden_path_returns_fixture_evidence_and_citations() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.post(
            "/api/v2/web-search/search",
            json={"query": "python programming", "activation": "manual"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["should_generate_with_evidence"] is True
    assert len(body["evidence"]) >= 1
    assert len(body["citations"]) >= 1
    assert body["evidence"][0]["fetched"] is True
    assert body["network_calls_made"] >= 2


@pytest.mark.asyncio
async def test_automatic_activation_is_rejected_at_the_http_boundary() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.post(
            "/api/v2/web-search/search",
            json={"query": "python", "activation": "automatic"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_governance_mode_is_server_configured_not_client_supplied() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(
            bound=True, governance_mode=WebEvidenceGovernanceMode.ENFORCE
        ),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        runtime_status = await client.get("/api/v2/web-search/runtime")
        search = await client.post(
            "/api/v2/web-search/search",
            json={"query": "python", "activation": "manual", "governance_mode": "off"},
        )

    assert runtime_status.json()["governance_mode"] == "enforce"
    # The unknown `governance_mode` field in the request body is simply
    # rejected (extra="forbid"), proving the client cannot smuggle a
    # governance override through the request payload.
    assert search.status_code == 422


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
async def test_shared_exposure_rejects_accidental_web_search_binding(
    policy: WebAccessPolicy,
) -> None:
    app = create_web_app(runtime_factory=lambda: runtime(bound=True), access_policy=policy)

    with pytest.raises(RuntimeError, match="Web Search control requires local"):
        async with app.router.lifespan_context(app):
            pass
