"""Local runtime-composition inspection API and Public/Basic zero-binding tests."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import cast

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.modules.runtime_composition.application import ComponentRegistryService
from margpa_runtime_llm.modules.runtime_composition.contracts import (
    ComponentState,
    build_component_descriptor,
)
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import SafeRuntimeSnapshot, WebRuntime


class NullConversation:
    def shutdown(self, timeout: float) -> bool:
        del timeout
        return True


def registry() -> ComponentRegistryService:
    service = ComponentRegistryService()
    service.register(
        build_component_descriptor(
            component_key="documentation_rag",
            kind="feature",
            version="1",
            state=ComponentState.ENABLED,
            capabilities=("retrieval", "citation"),
        )
    )
    service.register(
        build_component_descriptor(
            component_key="conversation_persistence",
            kind="persistence",
            version="1",
            state=ComponentState.DISABLED,
        )
    )
    return service


def runtime(*, bound: bool) -> WebRuntime:
    return WebRuntime(
        conversation=cast(object, NullConversation()),  # type: ignore[arg-type]
        snapshot=SafeRuntimeSnapshot.model_construct(),
        close_callback=lambda: None,
        runtime_composition=registry() if bound else None,
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
async def test_unbound_route_is_safe_404_with_no_path_or_source_leak() -> None:
    """Public/Basic Preview and any un-opted-in Local run: zero-binding."""

    app = create_web_app(
        runtime_factory=lambda: runtime(bound=False),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        unavailable = await client.get("/api/v2/runtime/components")
    assert unavailable.status_code == 404
    assert unavailable.json() == {
        "code": "runtime_composition_unavailable",
        "message": "Runtime composition inspection is unavailable.",
    }


@pytest.mark.asyncio
async def test_bound_runtime_reports_registered_component_states() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/runtime/components")
    assert response.status_code == 200
    body = response.json()
    by_key = {item["component_key"]: item for item in body["components"]}
    assert by_key["documentation_rag"]["state"] == "enabled"
    assert by_key["documentation_rag"]["capabilities"] == ["retrieval", "citation"]
    assert by_key["conversation_persistence"]["state"] == "disabled"
    assert by_key["conversation_persistence"]["capabilities"] == []
    # The registry describes state; it must not itself expose an execution/authority field.
    assert "execute" not in by_key["documentation_rag"]
    assert "authority" not in by_key["documentation_rag"]
    # P2E-CODEX-002: every registered component projects a real, non-empty digest.
    for item in body["components"]:
        assert len(item["canonical_digest"]) == 128
        int(item["canonical_digest"], 16)  # must be valid hex
    assert (
        by_key["documentation_rag"]["canonical_digest"]
        != by_key["conversation_persistence"]["canonical_digest"]
    )
