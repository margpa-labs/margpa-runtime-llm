"""Automated Local UX / Recovery Verification (P3-G-WU-002).

A tmp_path-rooted OFF -> OBSERVE -> Evidence -> OFF -> "restart" cycle
against the real Governance Definitions Runtime, the real Reference
Bundle, and a real (JSONL) Evidence Store — no real user Conversation DB
and no real Model are ever touched.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import cast
from uuid import uuid4

import httpx
import pytest
from fastapi import FastAPI

from margpa_runtime_llm.adapters.audit_evidence.evidence_generation_observer import (
    EvidenceGenerationObserver,
)
from margpa_runtime_llm.adapters.audit_evidence.local_jsonl_store import LocalJsonlEvidenceStore
from margpa_runtime_llm.bootstrap.governance_definitions import (
    build_governance_definitions_runtime,
)
from margpa_runtime_llm.modules.audit_evidence.domain import AuditRunId, verify_canonical_event
from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import SafeRuntimeSnapshot, WebRuntime

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITIONS_ROOT = PROJECT_ROOT / "definitions"


class _NullConversation:
    def shutdown(self, timeout: float) -> bool:
        del timeout
        return True


def _web_runtime() -> WebRuntime:
    return WebRuntime(
        conversation=cast(object, _NullConversation()),  # type: ignore[arg-type]
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


def test_off_boot_observe_apply_evidence_off_revert_and_restart_recovery(
    tmp_path: Path,
) -> None:
    evidence_root = tmp_path / "audit_evidence"

    # --- Boot: OFF ---
    governance_runtime = build_governance_definitions_runtime(definitions_root=DEFINITIONS_ROOT)
    boot_snapshot = governance_runtime.mode_snapshot()
    assert boot_snapshot.current_mode is GovernanceMode.OFF
    enforce_descriptor = next(
        d for d in boot_snapshot.descriptors if d.mode is GovernanceMode.ENFORCE
    )
    # Enforce must be visible in the descriptor list, marked unavailable —
    # never simply omitted (architecture §9.3 "表示するがDisabled、理由を明示").
    assert enforce_descriptor.availability.value == "unavailable"
    assert enforce_descriptor.unavailable_reason_code is not None

    run_id = AuditRunId(value=str(uuid4()))
    observer = EvidenceGenerationObserver(
        store_factory=lambda: LocalJsonlEvidenceStore(
            anchor=tmp_path, relative_root="audit_evidence", scope="ux_recovery"
        ),
        run_id=run_id,
        source_component="test.local_ux_recovery",
        mode_provider=lambda: governance_runtime.mode_snapshot().current_mode.value,
    )

    # OFF中: is_active()がFalseであることを確認し、実際の呼出元(web層)と同じく
    # is_active()==Falseの場合はobserve_generation_*を一切呼ばない
    # (P3-CODEX-002 "Governance Hook Call 0")。Storeのlazy生成も未実施のまま。
    assert observer.is_active() is False
    assert not evidence_root.exists()  # Store Directory自体が未生成(Lazy)

    # --- Apply OBSERVE: Catalog / Plan ---
    observe_snapshot = governance_runtime.apply_mode(GovernanceMode.OBSERVE)
    assert observe_snapshot.current_mode is GovernanceMode.OBSERVE
    status = governance_runtime.status()
    assert status.observe_summary is not None
    assert status.observe_summary.package_found is True
    assert status.observe_summary.definition_count == 18
    assert status.observe_summary.valid_definition_count == 18
    assert status.observe_summary.compiled_plan_id is not None

    # --- Evidence: OBSERVE中はis_active()==True、実際に書き込まれる ---
    assert observer.is_active() is True
    observer.observe_generation_started(request_id="req-ux-1", profile_key="local.fixture")
    observer.observe_generation_terminal(
        request_id="req-ux-1",
        stop_reason="stop",
        token_count=12,
        latency_ms=34,
        warning_count=0,
        error_count=0,
    )
    store_1 = LocalJsonlEvidenceStore(
        anchor=tmp_path, relative_root="audit_evidence", scope="ux_recovery"
    )
    assert store_1.status().event_count == 2
    written = store_1.read_all(run_id)
    assert len(written) == 2
    assert all(verify_canonical_event(event) for event in written)

    # --- OFF復帰 ---
    off_again = governance_runtime.apply_mode(GovernanceMode.OFF)
    assert off_again.current_mode is GovernanceMode.OFF
    assert governance_runtime.status().observe_summary is None
    assert observer.is_active() is False  # 復帰後、Web層ならここでobserve_*を呼ばない
    assert store_1.status().event_count == 2  # OFF復帰後は追加0のまま

    # --- Restart Recovery: 完全に新しいRuntime/Store Instanceで同じRootを再Open ---
    governance_runtime_2 = build_governance_definitions_runtime(definitions_root=DEFINITIONS_ROOT)
    # Modeはprocess-local(Evidenceのみ永続。Mode自体はRestartでOFFへ戻る設計、
    # architecture 1章の governance.mode Explicit Runtime Configuration)。
    assert governance_runtime_2.mode_snapshot().current_mode is GovernanceMode.OFF

    store_2 = LocalJsonlEvidenceStore(
        anchor=tmp_path, relative_root="audit_evidence", scope="ux_recovery"
    )
    assert store_2.status().event_count == 2  # 再OpenしてもEvidence Fileは存続
    reread = store_2.read_all(run_id)
    assert len(reread) == 2
    assert [event.envelope.event_kind.value for event in reread] == [
        "generation_started",
        "generation_terminal",
    ]

    # Restart後もPipelineが健全であること(再度OBSERVEへ正しく遷移できる)。
    governance_runtime_2.apply_mode(GovernanceMode.OBSERVE)
    assert governance_runtime_2.status().observe_summary is not None
    governance_runtime_2.apply_mode(GovernanceMode.OFF)


@pytest.mark.asyncio
async def test_server_boots_and_shuts_down_cleanly_with_governance_wired(
    tmp_path: Path,
) -> None:
    governance_runtime = build_governance_definitions_runtime(definitions_root=DEFINITIONS_ROOT)
    observer = EvidenceGenerationObserver(
        store_factory=lambda: LocalJsonlEvidenceStore(
            anchor=tmp_path, relative_root="audit_evidence", scope="ux_recovery_web"
        ),
        run_id=AuditRunId(value=str(uuid4())),
        source_component="test.local_ux_recovery",
        mode_provider=lambda: governance_runtime.mode_snapshot().current_mode.value,
    )

    app = create_web_app(
        runtime_factory=_web_runtime,
        access_policy=WebAccessPolicy(mode=WebAuthMode.DISABLED),
    )
    app.state.governance_definitions_runtime = governance_runtime
    app.state.generation_observer = observer

    async with client_for(app) as client:
        status_response = await client.get("/api/v3/governance/runtime")
        assert status_response.status_code == 200
        body = status_response.json()
        assert body["mode"]["current_mode"] == "off"
        by_mode = {d["mode"]: d for d in body["mode"]["descriptors"]}
        assert by_mode["enforce"]["availability"] == "unavailable"
        assert by_mode["enforce"]["unavailable_reason_code"] is not None

        # P3-CODEX-001: this Read-only Status Surface no longer accepts a
        # Mode Mutation — that authority moved to Configuration Control's
        # Preview/Apply (proven end-to-end in
        # test_governance_definitions_web_app.py). Confirm it stays gone.
        mutation_attempt = await client.post(
            "/api/v3/governance/mode", json={"requested_mode": "observe"}
        )
        assert mutation_attempt.status_code in (404, 405)
    # The `async with` block above exercises the full FastAPI lifespan
    # startup/shutdown; reaching here without an exception is the clean
    # shutdown assertion.
