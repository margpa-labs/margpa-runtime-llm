"""Local Corpus (`/api/v2/local-corpus`) API and exposure integration tests (P7-B)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import cast

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.documentation_rag import JsonFileLocalCorpusRegistry
from margpa_runtime_llm.web.access_profiles import WebExposureMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import SafeRuntimeSnapshot, WebRuntime


class NullConversation:
    def shutdown(self, timeout: float) -> bool:
        del timeout
        return True


def runtime(*, tmp_path: Path, bound: bool) -> WebRuntime:
    registry = (
        JsonFileLocalCorpusRegistry(runtime_data_root=tmp_path / "runtime_data") if bound else None
    )
    return WebRuntime(
        conversation=cast(object, NullConversation()),  # type: ignore[arg-type]
        snapshot=SafeRuntimeSnapshot.model_construct(),
        close_callback=lambda: None,
        local_corpus_registry=registry,
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
        unavailable = await client.get("/api/v2/local-corpus/documents")
        root = await client.get("/")

    assert unavailable.status_code == 404
    assert unavailable.json() == {
        "code": "local_corpus_unavailable",
        "message": "Local Corpus document management is unavailable.",
    }
    assert (
        '<script id="local-corpus-bootstrap" type="application/json">{"enabled":false}</script>'
        in (root.text)
    )


@pytest.mark.asyncio
async def test_bound_registry_flips_root_bootstrap_to_enabled(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        root = await client.get("/")

    assert (
        '<script id="local-corpus-bootstrap" type="application/json">{"enabled":true}</script>'
        in (root.text)
    )


@pytest.mark.asyncio
async def test_register_update_list_get_delete_golden_path(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        registered = await client.post(
            "/api/v2/local-corpus/documents",
            json={"title": "研究メモ", "content": "本文テキストです。"},
        )
        document_id = registered.json()["document_id"]

        listed = await client.get("/api/v2/local-corpus/documents")
        fetched = await client.get(f"/api/v2/local-corpus/documents/{document_id}")
        updated = await client.put(
            f"/api/v2/local-corpus/documents/{document_id}",
            json={"title": "研究メモv2", "content": "更新後の本文です。"},
        )
        listed_after_update = await client.get("/api/v2/local-corpus/documents")
        deleted = await client.delete(f"/api/v2/local-corpus/documents/{document_id}")
        listed_after_delete = await client.get("/api/v2/local-corpus/documents")
        get_after_delete = await client.get(f"/api/v2/local-corpus/documents/{document_id}")

    assert registered.status_code == 201
    assert registered.json()["current_revision"] == 1
    assert listed.json()["documents"][0]["document_id"] == document_id
    assert fetched.json()["content"] == "本文テキストです。"
    assert updated.status_code == 200
    assert updated.json()["current_revision"] == 2
    assert updated.json()["content"] == "更新後の本文です。"
    assert listed_after_update.json()["documents"][0]["title"] == "研究メモv2"
    assert deleted.status_code == 200
    assert deleted.json()["state"] == "deleted"
    assert listed_after_delete.json()["documents"] == []
    assert get_after_delete.status_code == 404


@pytest.mark.asyncio
async def test_update_or_delete_unknown_document_is_safe_404(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        missing_id = "0" * 32
        update = await client.put(
            f"/api/v2/local-corpus/documents/{missing_id}",
            json={"title": "t", "content": "c"},
        )
        delete = await client.delete(f"/api/v2/local-corpus/documents/{missing_id}")

    assert update.status_code == 404
    assert update.json()["code"] == "local_corpus_document_not_found"
    assert delete.status_code == 404


@pytest.mark.asyncio
async def test_blank_content_is_rejected_before_reaching_the_registry(tmp_path: Path) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=True),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.post(
            "/api/v2/local-corpus/documents",
            json={"title": "t", "content": ""},
        )

    assert response.status_code == 422


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
async def test_shared_exposure_rejects_accidental_local_corpus_binding(
    policy: WebAccessPolicy,
    tmp_path: Path,
) -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(tmp_path=tmp_path, bound=True),
        access_policy=policy,
    )

    with pytest.raises(RuntimeError, match="Local Corpus control requires local"):
        async with app.router.lifespan_context(app):
            pass
