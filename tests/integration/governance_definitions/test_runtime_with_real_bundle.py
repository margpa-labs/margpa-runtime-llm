"""GovernanceDefinitionsRuntime end-to-end against the real Reference
Bundle, via the bootstrap composition function (P3-F-WU-002)."""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.bootstrap.governance_definitions import (
    build_governance_definitions_runtime,
)
from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITIONS_ROOT = PROJECT_ROOT / "definitions"


def test_empty_bootstrap_stays_off_and_empty() -> None:
    runtime = build_governance_definitions_runtime()
    assert runtime.mode_snapshot().current_mode is GovernanceMode.OFF


def test_real_bundle_bootstrap_observe_compiles_all_eighteen_definitions() -> None:
    runtime = build_governance_definitions_runtime(definitions_root=DEFINITIONS_ROOT)
    snapshot = runtime.apply_mode(GovernanceMode.OBSERVE)
    assert snapshot.current_mode is GovernanceMode.OBSERVE

    status = runtime.status()
    assert status.observe_summary is not None
    assert status.observe_summary.package_found is True
    assert status.observe_summary.definition_count == 18
    assert status.observe_summary.valid_definition_count == 18
    assert status.observe_summary.invalid_definition_count == 0
    assert status.observe_summary.unsupported_definition_count == 0
    assert status.observe_summary.compiled_plan_id is not None


def test_real_bundle_off_to_observe_to_off_round_trip() -> None:
    runtime = build_governance_definitions_runtime(definitions_root=DEFINITIONS_ROOT)
    runtime.apply_mode(GovernanceMode.OBSERVE)
    assert runtime.status().observe_summary is not None

    runtime.apply_mode(GovernanceMode.OFF)
    assert runtime.status().observe_summary is None
    assert runtime.mode_snapshot().current_mode is GovernanceMode.OFF


def test_observe_to_off_clears_the_plan_cache_p3_codex_006() -> None:
    runtime = build_governance_definitions_runtime(definitions_root=DEFINITIONS_ROOT)
    runtime.apply_mode(GovernanceMode.OBSERVE)
    # White-box: architecture §8.2 requires the process-local Plan Cache
    # to be cleared on observe -> off — verified directly since there is
    # no purely-black-box observable difference between "cleared and
    # deterministically recompiled" and "reused" when content hasn't
    # changed (P3-CODEX-006).
    assert runtime._plan_cache.size() == 1

    runtime.apply_mode(GovernanceMode.OFF)
    assert runtime._plan_cache.size() == 0

    status = runtime.apply_mode(GovernanceMode.OBSERVE)
    assert status.current_mode is GovernanceMode.OBSERVE
    assert runtime._plan_cache.size() == 1
    observe_summary = runtime.status().observe_summary
    assert observe_summary is not None
    assert observe_summary.compiled_plan_id is not None
