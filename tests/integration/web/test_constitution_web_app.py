"""Constitution (`/api/v2/constitution`) API integration tests (P8-C)."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import cast

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.constitution import JsonFileConstitutionProvider
from margpa_runtime_llm.modules.constitution import (
    ConstitutionMode,
    ConstitutionProviderPort,
    ConstitutionRule,
    compute_manifest_digest,
)
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import SafeRuntimeSnapshot, WebRuntime


class NullConversation:
    def shutdown(self, timeout: float) -> bool:
        del timeout
        return True


def _write_manifest(project_root: Path) -> None:
    rule = ConstitutionRule(
        rule_id="test-only-rule",
        revision=1,
        title="Test-only Rule",
        summary="A minimal Rule used only by this integration Test.",
        applies_to=("chat", "agent"),
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
    provider: ConstitutionProviderPort | None,
    mode: ConstitutionMode = ConstitutionMode.OFF,
) -> WebRuntime:
    return WebRuntime(
        conversation=cast(object, NullConversation()),  # type: ignore[arg-type]
        snapshot=SafeRuntimeSnapshot.model_construct(),
        close_callback=lambda: None,
        constitution_provider=provider,
        constitution_mode=mode,
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
async def test_unbound_provider_is_safe_404() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=None),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/runtime")

    assert response.status_code == 404
    assert response.json() == {
        "code": "constitution_unavailable",
        "message": "The Provisional Runtime Constitution is unavailable.",
    }


@pytest.mark.asyncio
async def test_missing_manifest_file_is_also_a_safe_404(tmp_path: Path) -> None:
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=provider),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/runtime")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_bound_provider_returns_per_view_capability_at_off_mode(tmp_path: Path) -> None:
    _write_manifest(tmp_path)
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=provider, mode=ConstitutionMode.OFF),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/runtime")

    body = response.json()
    assert body["revision"] == 1
    assert body["rule_count"] == 1
    views = {item["view"]: item for item in body["views"]}
    assert set(views) == {"chat", "agent", "tool"}
    # P8-REQ-016/P8-ACC-021: OFF is its own visible value, distinct from
    # ENFORCE/OBSERVE — never silently omitted.
    assert views["chat"]["mode"] == "off"
    assert views["chat"]["rule_ids"] == ["test-only-rule"]
    assert views["agent"]["rule_ids"] == ["test-only-rule"]
    # The Rule's own `applies_to` never included "tool".
    assert views["tool"]["rule_ids"] == []


@pytest.mark.asyncio
async def test_off_mode_never_reports_enforced_or_observed_even_when_bound(tmp_path: Path) -> None:
    """P8-REQ-016: binding a real Provider and having real applicable Rules
    must still never make OFF look like `allow all`/an active decision."""

    _write_manifest(tmp_path)
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=provider, mode=ConstitutionMode.OFF),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/runtime")

    body = response.json()
    for view in body["views"]:
        assert view["mode"] == "off"


@pytest.mark.asyncio
async def test_tampered_manifest_digest_is_a_safe_404_not_a_500(tmp_path: Path) -> None:
    """P8-REQ-018/P8-ACC-024: a Digest mismatch converges to the same
    honest `constitution_unavailable` Result, never an unhandled crash."""

    manifest_dir = tmp_path / "constitution"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(
        json.dumps({"revision": 1, "digest_sha512": "f" * 128, "rules": []}), encoding="utf-8"
    )
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=provider),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/runtime")

    assert response.status_code == 404
    assert response.json()["code"] == "constitution_unavailable"


# -- P8-RW6-D (P8-CODEX-008): Constitution Mode Comparison Preview ----------


@pytest.mark.asyncio
async def test_preview_unbound_provider_is_safe_404() -> None:
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=None),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/preview")

    assert response.status_code == 404
    assert response.json()["code"] == "constitution_unavailable"


@pytest.mark.asyncio
async def test_preview_compares_all_three_modes_for_all_three_views(tmp_path: Path) -> None:
    _write_manifest(tmp_path)
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=provider, mode=ConstitutionMode.OFF),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/preview")

    assert response.status_code == 200
    body = response.json()
    assert body["is_preview"] is True
    assert body["revision"] == 1
    views = {item["view"]: item for item in body["views"]}
    assert set(views) == {"chat", "agent", "tool"}
    for view_body in views.values():
        modes = [entry["mode"] for entry in view_body["modes"]]
        assert modes == ["off", "observe", "enforce"]


@pytest.mark.asyncio
async def test_preview_never_changes_the_active_production_mode(tmp_path: Path) -> None:
    """P8-CODEX-008's core requirement: the Preview Response must carry
    `active_production_mode` unchanged (still `off`, this Bounded Task's
    hard-locked value), regardless of what OBSERVE/ENFORCE show in
    `views` — and a subsequent `/runtime` call must still see the same
    unchanged `off` Active Mode too, proving the Preview call itself never
    mutated anything."""

    _write_manifest(tmp_path)
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=provider, mode=ConstitutionMode.OFF),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        preview_response = await client.get("/api/v2/constitution/preview")
        assert preview_response.json()["active_production_mode"] == "off"

        runtime_response = await client.get("/api/v2/constitution/runtime")
        assert all(view["mode"] == "off" for view in runtime_response.json()["views"])


@pytest.mark.asyncio
async def test_preview_off_entry_never_reports_enforced_or_observed(tmp_path: Path) -> None:
    _write_manifest(tmp_path)
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=provider, mode=ConstitutionMode.OFF),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/preview")

    body = response.json()
    for view_body in body["views"]:
        off_entry = next(entry for entry in view_body["modes"] if entry["mode"] == "off")
        assert all(d["outcome"] == "not_evaluated" for d in off_entry["decisions"])


@pytest.mark.asyncio
async def test_preview_entries_expose_the_three_axis_comparison(tmp_path: Path) -> None:
    """P8-RW7-A (P8-CODEX-012): the Response's `evaluation_disposition`/
    `action_permission`/`violation_presentation` must be present and
    converge to the Exact Handoff's fixed per-Mode values — the Finding
    this Package resolves was that the API only ever exposed `decisions`
    (bare Outcome strings), never this 3-axis comparison."""

    _write_manifest(tmp_path)
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=provider, mode=ConstitutionMode.OFF),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/preview")

    body = response.json()
    for view_body in body["views"]:
        by_mode = {entry["mode"]: entry for entry in view_body["modes"]}

        assert by_mode["off"]["evaluation_disposition"] == "not_evaluated"
        assert by_mode["off"]["action_permission"] == "no_constitution_action"
        assert by_mode["off"]["violation_presentation"] == "not_evaluated"

        assert by_mode["observe"]["evaluation_disposition"] == "evaluate_record_only"
        assert by_mode["observe"]["action_permission"] == "no_block_no_authority_change"

        assert by_mode["enforce"]["evaluation_disposition"] == "evaluate_and_apply_supported_action"
        assert (
            by_mode["enforce"]["action_permission"]
            == "supported_actions_only_no_authority_expansion"
        )


@pytest.mark.asyncio
async def test_preview_violation_presentation_is_honest_for_the_real_manifest(
    tmp_path: Path,
) -> None:
    """`_write_manifest()` scopes its one Rule to `chat`/`agent` only, so
    `tool` has zero applicable Rules; and the Production Route never passes
    `supported_rule_ids`. Both facts must show up honestly: `tool` is
    `not_evaluated` (nothing to present), `chat`/`agent` are
    `typed_unsupported` (a real Rule this Task cannot yet act on) — never a
    fabricated `observation_only`/`enforced`."""

    _write_manifest(tmp_path)
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=provider, mode=ConstitutionMode.OFF),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/preview")

    body = response.json()
    views = {item["view"]: item for item in body["views"]}

    for view_name in ("chat", "agent"):
        by_mode = {entry["mode"]: entry for entry in views[view_name]["modes"]}
        assert by_mode["observe"]["violation_presentation"] == "typed_unsupported"
        assert by_mode["enforce"]["violation_presentation"] == "typed_unsupported"

    by_mode_tool = {entry["mode"]: entry for entry in views["tool"]["modes"]}
    assert by_mode_tool["observe"]["rule_ids"] == []
    assert by_mode_tool["observe"]["violation_presentation"] == "not_evaluated"
    assert by_mode_tool["enforce"]["violation_presentation"] == "not_evaluated"


@pytest.mark.asyncio
async def test_preview_tampered_manifest_digest_is_a_safe_404_not_a_500(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "constitution"
    manifest_dir.mkdir(parents=True)
    (manifest_dir / "manifest.json").write_text(
        json.dumps({"revision": 1, "digest_sha512": "f" * 128, "rules": []}), encoding="utf-8"
    )
    provider = JsonFileConstitutionProvider(project_root=tmp_path)
    app = create_web_app(
        runtime_factory=lambda: runtime(provider=provider),
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    async with client_for(app) as client:
        response = await client.get("/api/v2/constitution/preview")

    assert response.status_code == 404
    assert response.json()["code"] == "constitution_unavailable"
