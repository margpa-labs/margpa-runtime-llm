"""Phase 9-2 R4-WU-04 / R5-WU-01,02: Top-level real Model Experiment Gate
(Handoff R4 SS7; R5 Handoff SS3/SS4).

Goes through the REAL Top-level path -- `build_phase1_web_runtime()` ->
`create_web_app()` -> `POST /plans` -> `POST /runs` -> `ExperimentRunWorker`
-> `LiveProductionTurnAdapter` -> Raw Evidence Persistence -> Evaluation ->
Comparison -> a fresh, independent `LocalFilesystemExperimentStore` read
(Runtime-reconstruction-then-Read) -- never the Direct Adapter call
(`test_real_local_experiment_production_variant_gate_smoke.py`, unchanged,
NOT re-run this Round; Handoff R4 SS3: "Direct LiveProductionTurnAdapter
SmokeをTop-level Experiment Runと呼ばない"). Each of the 3 scenarios is its
own independent real-hardware Trial (own Main Load, own Runtime, own
Worker) -- never two real Model backends loaded concurrently beyond the
one already-validated Main+Gemma pair.

Selene and DeepSeek Judge are never touched (out of this Round's scope).
Model quality FAIL / Judge-Repair non-dispatch / Guard non-dispatch are
never silently converted to a passing `pytest.skip()` -- a genuine Typed
Result (whatever it is) is asserted and printed, honestly.

R5-WU-01 (Controller IR-P9-2-R4-01 fix): `_restart_read()` now Hard
Asserts every object the R4/R5 Handoffs name -- Plan, this Variant's own
Desired Configuration (digest cross-checked against the Plan's own
`variant_configuration_digests`), the Run, its Frozen Configuration
Snapshot's `correlation` block (cross-checked against the Run/Plan's own
identities) and `provider_identity` block (cross-checked against the
caller-supplied expected Configured/Active/Expected-Executed selector per
Role -- never merely "the key is present"), Raw Evidence/Metric, and the
Comparison Report's own Row/Metric/Evaluation-Observation for this exact
`run_id` -- never a bare "Comparison is not None".

R5-WU-02 (Controller IR-P9-2-R4-02/03 fix): Scenario 2/3 now Hard Assert
`state == "completed"` ALONE (a `failed` real Run is a genuine Test
failure, never a silently-accepted alternative), plus Main/Judge
`called is True` for Scenario 2 and Main `called is True` for Scenario 3.
Guard's own `called is None` / `outcome == "unavailable_correlation"` is
asserted as exactly that -- Unavailable, honestly -- never reworded as
proof Guard was actually Dispatched (`ActorInvocationRecord.called=True`
proves a Call happened; it never by itself proves WHICH Provider executed
it, and Guard's own real Evidence source has no request-scoped
correlation to answer that at all this Round -- Handoff R5 SS4.2/SS5)."""

from __future__ import annotations

import asyncio
import json
import platform
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx
import pytest

from margpa_runtime_llm.adapters.experiment.local_filesystem_experiment_store import (
    LocalFilesystemExperimentStore,
)
from margpa_runtime_llm.bootstrap.web_application import build_phase1_web_runtime
from margpa_runtime_llm.modules.conversation.adapters import (
    LocalConversationPersistenceSettings,
)
from margpa_runtime_llm.modules.conversation.adapters.sqlite_conversation_store import (
    scope_directory_key,
)
from margpa_runtime_llm.modules.conversation.domain import ConversationScopeId
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationMode
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    ExperimentPlanBudget,
    VariantConfigurationRef,
    VariantDescriptor,
    build_experiment_plan,
)
from margpa_runtime_llm.modules.experiment.domain.provider_identity import (
    ProviderIdentityDetail,
    ProviderIdentityEnvelope,
)
from margpa_runtime_llm.modules.experiment.domain.run import RunState, VariantRun
from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairMode
from margpa_runtime_llm.modules.runtime_model_control.application.provider_selection_controller import (  # noqa: E501
    GEMMA_E2B_JUDGE,
    QWEN3_GUARD,
    QWEN_MAIN,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.web.access_profiles import WebExposureMode
from margpa_runtime_llm.web.app import create_web_app
from margpa_runtime_llm.web.auth import WebAccessPolicy, WebAuthMode
from margpa_runtime_llm.web.contracts import WebRuntime

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_ROOT = PROJECT_ROOT / "models"
QWEN_ARTIFACT_PATH = MODEL_ROOT / "main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf"
GEMMA_ARTIFACT_PATH = MODEL_ROOT / "judge/gemma-4-E2B_q4_0-it/gguf/gemma-4-E2B_q4_0-it.gguf"
GUARD_ARTIFACT_PATH = (
    MODEL_ROOT / "guard/qwen3guard-gen-0.6b/gguf/Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf"
)
REGISTRY_PATH = PROJECT_ROOT / "config/models/qwen3_4b_q4_k_m.toml"

_LOCAL_POLICY = WebAccessPolicy(exposure_mode=WebExposureMode.LOCAL, mode=WebAuthMode.DISABLED)
_REQUIRES_APPLE_SILICON = pytest.mark.skipif(
    platform.system() != "Darwin" or platform.machine() != "arm64",
    reason="The Phase 9-2 R4 Top-level Real Model Gate requires Apple Silicon",
)


def _build_real_runtime(tmp_path: Path, *, scope_name: str) -> tuple[WebRuntime, Path]:
    """The one real `build_phase1_web_runtime()` call every Scenario below
    shares the shape of -- `feature_modes_enabled`/`runtime_model_control_
    enabled`/`guardrail_governance_enabled`/`dedicated_model_authority_
    granted` are all `True` so Judge/Repair/Recording Mode, Provider
    Selection (needed for the Live Config Reader's own Main selector), and
    Guard are all genuinely wired -- and `conversation_persistence_
    settings` is what makes `build_phase1_web_runtime()` also construct
    `experiment_service`/`experiment_run_worker` (gated only on that
    Settings object, independent of any other flag here)."""

    runtime_data_root = tmp_path / "runtime-data"
    scope = ConversationScopeId(value=scope_name)
    persistence_settings = LocalConversationPersistenceSettings(
        enabled=True,
        runtime_data_root=runtime_data_root,
        scope_id=scope,
    )
    runtime = build_phase1_web_runtime(
        project_root=PROJECT_ROOT,
        profile_path=None,
        registry_path=REGISTRY_PATH,
        feature_modes_enabled=True,
        runtime_model_control_enabled=True,
        guardrail_governance_enabled=True,
        dedicated_model_authority_granted=True,
        conversation_persistence_settings=persistence_settings,
    )
    assert runtime.experiment_service is not None
    assert runtime.experiment_run_worker is not None
    assert runtime.production_turn_adapter is not None
    assert runtime.live_configuration_reader is not None
    assert runtime.experiment_configuration_lease is not None
    experiment_store_dir = (
        runtime_data_root / "persistent" / scope_directory_key(scope) / "experiments"
    )
    return runtime, experiment_store_dir


async def _wait_for_terminal(
    client: httpx.AsyncClient, run_id: str, *, timeout: float = 180.0
) -> dict[str, Any]:
    """A real Turn (real Model decode) is not instantaneous like a Fixture
    -- a generous ceiling, well above what even a slow real Load+Decode
    on Apple Silicon needs for a <=64-token Completion."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        response = await client.get(f"/api/v7/experiment/runs/{run_id}")
        body: dict[str, Any] = response.json()
        if body["run"]["state"] != "running":
            return body
        await asyncio.sleep(0.25)
    raise AssertionError(f"run {run_id!r} did not reach a terminal state in time")


@dataclass(frozen=True, slots=True)
class _IdentityExpectation:
    """One Role's expected Configured/Active/Expected-Executed selector,
    per Handoff R5 SS3 Hard Assert #6 -- all three are checked together,
    never merely "the field is present" (Controller IR-P9-2-R4-01)."""

    configured: str | None
    active: str | None
    expected_executed: str


def _assert_identity_detail(
    provider_identity: dict[str, Any], *, role_key: str, expectation: _IdentityExpectation
) -> None:
    detail = provider_identity[role_key]
    assert detail["component_key"] == role_key, detail
    assert detail["configured_selector_id"] == expectation.configured, detail
    assert detail["active_selector_id"] == expectation.active, detail
    assert detail["expected_executed_selector_id"] == expectation.expected_executed, detail


def _restart_read(
    experiment_store_dir: Path,
    *,
    experiment_id: str,
    variant_id: str,
    run_id: str,
    expected_main: _IdentityExpectation,
    expected_judge: _IdentityExpectation | None = None,
    expected_guard: _IdentityExpectation | None = None,
) -> None:
    """Handoff R4 SS7.3's own minimum bar: "最低1 ScenarioでRuntime再構成後
    もPlan/Desired/Frozen/Run/Raw Evidence/Evaluation/Comparisonを
    読めること" -- a FRESH `LocalFilesystemExperimentStore` instance,
    pointed at the SAME on-disk directory but never sharing the original
    process's in-memory state, proves genuine Restart-readability (never
    merely "the same Python object still holds it in memory").

    R5-WU-01 (Controller IR-P9-2-R4-01 fix, Handoff R5 SS3 Hard Asserts
    1-9): every named object is now Hard Asserted against its own
    identity-bearing fields -- never merely "load returned non-None" --
    and cross-checked against the other objects it must agree with
    (Plan's own Variant Configuration Digest vs. the persisted Desired
    Snapshot's own digest; Frozen Snapshot's `correlation` block vs. the
    Run/Plan's own identities; Frozen Snapshot's `provider_identity`
    block vs. the caller-supplied expected Configured/Active/Expected-
    Executed; the Comparison Report's own Row for this exact `run_id`
    against the Run/Plan's own `variant_id`/`case_id`)."""

    fresh_store = LocalFilesystemExperimentStore(base_dir=experiment_store_dir)

    # 1: Plan.
    plan = fresh_store.load_plan(experiment_id)
    assert plan is not None
    assert plan.experiment_id == experiment_id

    # 2/3: this Variant's own Desired Configuration, cross-checked against
    # the Plan's own `variant_configuration_digests` entry for it.
    desired = fresh_store.load_variant_desired_configuration(experiment_id, variant_id)
    assert desired is not None
    desired_digest = desired["configuration_digest_sha512"]
    plan_digest_for_variant = plan.configuration_digest_for(variant_id)
    assert plan_digest_for_variant is not None
    assert desired_digest == plan_digest_for_variant, (desired_digest, plan_digest_for_variant)

    # 4: Run.
    run = fresh_store.load_run(run_id)
    assert run is not None
    assert run.run_id == run_id
    assert run.experiment_id == experiment_id
    assert run.variant_id == variant_id
    assert run.state.value == "completed", run.state

    # 4/5/6: Frozen Configuration Snapshot -- `correlation` cross-checked
    # against the Run/Plan's own identities, `provider_identity`
    # cross-checked against the caller-supplied expectation (never merely
    # "the block exists").
    frozen_snapshot = fresh_store.load_run_configuration_snapshot(run_id)
    assert frozen_snapshot is not None
    correlation = frozen_snapshot.get("correlation")
    assert correlation is not None
    assert correlation["run_id"] == run_id, correlation
    assert correlation["experiment_id"] == experiment_id, correlation
    assert correlation["variant_id"] == variant_id, correlation
    assert correlation["case_digest_sha512"] == plan.case_digest_sha512, correlation
    assert correlation["plan_digest_sha512"] == plan.plan_digest_sha512, correlation
    provider_identity = frozen_snapshot.get("provider_identity")
    assert provider_identity is not None
    _assert_identity_detail(provider_identity, role_key="main", expectation=expected_main)
    if expected_judge is not None:
        _assert_identity_detail(provider_identity, role_key="judge", expectation=expected_judge)
    if expected_guard is not None:
        _assert_identity_detail(provider_identity, role_key="guard", expectation=expected_guard)

    # 7: Raw Evidence and its own Metric.
    raw_evidence = fresh_store.load_raw_evidence(run_id)
    assert raw_evidence is not None
    metric = raw_evidence.get("metric")
    assert metric is not None
    assert metric["run_id"] == run_id, metric
    assert metric["case_id"] == plan.case_id, metric
    assert metric["runtime_state"] == "completed", metric

    # 8/9: Comparison -- never merely "not None" -- this exact Run's own
    # Row, Metric, and (always exactly one, per `evaluate_case_outcome()`)
    # Evaluation Observation, all cross-checked against the same
    # Run/Plan identities above.
    comparison = fresh_store.load_comparison(experiment_id)
    assert comparison is not None
    assert comparison["experiment_id"] == experiment_id
    rows_for_run = [row for row in comparison["rows"] if row["run_id"] == run_id]
    assert len(rows_for_run) == 1, comparison["rows"]
    row = rows_for_run[0]
    assert row["variant_id"] == variant_id, row
    assert row["runtime_state"] == "completed", row
    assert row["metric"] is not None
    assert row["metric"]["run_id"] == run_id, row["metric"]
    assert len(row["observations"]) == 1, row["observations"]
    observation = row["observations"][0]
    assert observation["run_id"] == run_id, observation
    assert observation["case_id"] == plan.case_id, observation

    print(
        f"[restart-read] experiment_id={experiment_id!r} run_id={run_id!r} "
        f"plan_digest={plan.plan_digest_sha512[:16]}… "
        f"frozen_digest={frozen_snapshot.get('configuration_digest_sha512', '')[:16]}… "
        f"comparison_row_observation_outcome={observation['outcome']!r}"
    )


async def _run_one_scenario(
    runtime: WebRuntime, *, experiment_id: str, variant_id: str, run_id: str
) -> dict[str, Any]:
    app = create_web_app(runtime_factory=lambda: runtime, access_policy=_LOCAL_POLICY)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as client:
            presets_response = await client.get("/api/v7/experiment/presets")
            presets_body = presets_response.json()
            case_id = presets_body["cases"][0]["case_id"]
            plan_response = await client.post(
                "/api/v7/experiment/plans",
                json={
                    "experiment_id": experiment_id,
                    "case_id": case_id,
                    "variant_ids": [variant_id],
                    "execution_mode": "production",
                    "deadline_ms": 170_000,
                },
            )
            assert plan_response.status_code == 201, plan_response.text
            run_response = await client.post(
                "/api/v7/experiment/runs",
                json={"experiment_id": experiment_id, "variant_id": variant_id, "run_id": run_id},
            )
            assert run_response.status_code == 202, run_response.text
            run_body = await _wait_for_terminal(client, run_id)
            comparison_response = await client.get(
                f"/api/v7/experiment/experiments/{experiment_id}/comparison"
            )
            assert comparison_response.status_code == 200
            run_body["_comparison"] = comparison_response.json()
            return run_body


@pytest.mark.model_smoke
@_REQUIRES_APPLE_SILICON
def test_real_top_level_gate_scenario_1_main_qwen_only(tmp_path: Path) -> None:
    """Scenario 1 (Handoff R4 SS7.3): Main Qwen only, through the REAL
    Top-level path. This is the one Scenario this Round's own restart-read
    Hard Assert is checked against."""

    if not QWEN_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Main model artifact is unavailable: {QWEN_ARTIFACT_PATH}")
    runtime, experiment_store_dir = _build_real_runtime(
        tmp_path, scope_name="scope-real-r4-wu04-scenario-1"
    )
    try:
        run_body = asyncio.run(
            _run_one_scenario(
                runtime,
                experiment_id="exp-real-r4-1",
                variant_id="production-main-only-baseline",
                run_id="run-real-1",
            )
        )
        print(
            "[real-top-level-gate-1] "
            f"state={run_body['run']['state']!r} "
            f"failure_reason={run_body['run'].get('failure_reason')!r} "
            f"frozen_digest={run_body['run'].get('frozen_configuration_digest_sha512')!r} "
            f"content={run_body.get('assistant_content')!r}"
        )
        # Typed, honest outcome -- never fabricated. A real Main Load+Turn
        # through this exact Preset/Live combination is expected to
        # COMPLETE; if it does not, the real failure_reason is reported
        # as-is (never retried, never skipped).
        assert run_body["run"]["state"] == "completed", (
            f"real Top-level Scenario 1 did not COMPLETE: {run_body['run']}"
        )
        assert run_body["run"]["frozen_configuration_digest_sha512"] is not None
        invocation_by_key = {
            item["component_key"]: item for item in run_body["invocations"]
        }
        assert invocation_by_key["main"]["called"] is True
        _restart_read(
            experiment_store_dir,
            experiment_id="exp-real-r4-1",
            variant_id="production-main-only-baseline",
            run_id="run-real-1",
            expected_main=_IdentityExpectation(
                configured=QWEN_MAIN, active=QWEN_MAIN, expected_executed=QWEN_MAIN
            ),
        )
    finally:
        runtime.close()


@pytest.mark.model_smoke
@_REQUIRES_APPLE_SILICON
def test_real_top_level_gate_scenario_2_main_qwen_plus_gemma_judge_repair(
    tmp_path: Path,
) -> None:
    """Scenario 2 (Handoff R4 SS7.3): Main Qwen + Gemma Judge/Repair
    ENFORCE. Judge/Repair are Activated through the runtime's own real
    control surfaces (`role_provider_lifecycle.activate()`, `judge_mode_
    control.apply_mode()`, `repair_mode_control.apply_mode()`) -- the SAME
    surfaces `web/feature_modes_routes.py`/`web/provider_selection_routes.
    py` themselves call -- BEFORE the Experiment Run starts, exactly the
    real intended User workflow (re-configure ordinary Settings, then
    Run)."""

    if not QWEN_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Main model artifact is unavailable: {QWEN_ARTIFACT_PATH}")
    if not GEMMA_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Gemma model artifact is unavailable: {GEMMA_ARTIFACT_PATH}")
    runtime, experiment_store_dir = _build_real_runtime(
        tmp_path, scope_name="scope-real-r4-wu04-scenario-2"
    )
    try:
        assert runtime.role_provider_lifecycle is not None
        assert runtime.judge_mode_control is not None
        assert runtime.repair_mode_control is not None
        activated = runtime.role_provider_lifecycle.activate(role=ModelRole.JUDGE)
        judge_selection = next(
            item for item in activated.selections if item.role is ModelRole.JUDGE
        )
        print(f"[real-top-level-gate-2] judge activation: {judge_selection}")
        if judge_selection.active_provider is None:
            pytest.fail(
                f"Real Gemma Judge Activation did not settle Active: {judge_selection}"
            )
        runtime.judge_mode_control.apply_mode(EvaluationMode.ENFORCE)
        runtime.repair_mode_control.apply_mode(RepairMode.ENFORCE)

        run_body = asyncio.run(
            _run_one_scenario(
                runtime,
                experiment_id="exp-real-r4-2",
                variant_id="production-judge-repair-baseline",
                run_id="run-real-2",
            )
        )
        print(
            "[real-top-level-gate-2] "
            f"state={run_body['run']['state']!r} "
            f"failure_reason={run_body['run'].get('failure_reason')!r} "
            f"content={run_body.get('assistant_content')!r} "
            f"invocations={json.dumps(run_body['invocations'])}"
        )
        # R5-WU-02 (Controller IR-P9-2-R4-02 fix): `state == "completed"`
        # is now Hard Asserted ALONE -- a real `failed` outcome here
        # (e.g. a Live-Config mismatch, meaning real Judge Activation did
        # not settle at exactly the Provider identity this Preset
        # declares) is a genuine Test failure, never a silently-accepted
        # alternative terminal state.
        assert run_body["run"]["state"] == "completed", (
            f"real Top-level Scenario 2 did not COMPLETE: {run_body['run']}"
        )
        invocation_by_key = {item["component_key"]: item for item in run_body["invocations"]}
        assert invocation_by_key["main"]["called"] is True
        assert invocation_by_key["judge"]["called"] is True
        _restart_read(
            experiment_store_dir,
            experiment_id="exp-real-r4-2",
            variant_id="production-judge-repair-baseline",
            run_id="run-real-2",
            expected_main=_IdentityExpectation(
                configured=QWEN_MAIN, active=QWEN_MAIN, expected_executed=QWEN_MAIN
            ),
            expected_judge=_IdentityExpectation(
                configured=GEMMA_E2B_JUDGE,
                active=GEMMA_E2B_JUDGE,
                expected_executed=GEMMA_E2B_JUDGE,
            ),
        )
    finally:
        runtime.close()


@pytest.mark.model_smoke
@_REQUIRES_APPLE_SILICON
def test_real_top_level_gate_scenario_3_main_qwen_plus_qwen3guard(tmp_path: Path) -> None:
    """Scenario 3 (Handoff R4 SS7.3): Main Qwen + Qwen3Guard ENFORCE,
    Activated the same real way as Scenario 2's Judge."""

    if not QWEN_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Main model artifact is unavailable: {QWEN_ARTIFACT_PATH}")
    if not GUARD_ARTIFACT_PATH.is_file():
        pytest.skip(f"Local Qwen3Guard model artifact is unavailable: {GUARD_ARTIFACT_PATH}")
    runtime, experiment_store_dir = _build_real_runtime(
        tmp_path, scope_name="scope-real-r4-wu04-scenario-3"
    )
    try:
        assert runtime.role_provider_lifecycle is not None
        assert runtime.guardrail_governance_composition is not None
        activated = runtime.role_provider_lifecycle.activate(role=ModelRole.GUARD)
        guard_selection = next(
            item for item in activated.selections if item.role is ModelRole.GUARD
        )
        print(f"[real-top-level-gate-3] guard activation: {guard_selection}")
        if guard_selection.active_provider is None:
            pytest.fail(
                f"Real Qwen3Guard Activation did not settle Active: {guard_selection}"
            )
        runtime.guardrail_governance_composition.mode_controller.apply_mode(
            GovernanceMode.ENFORCE
        )

        run_body = asyncio.run(
            _run_one_scenario(
                runtime,
                experiment_id="exp-real-r4-3",
                variant_id="production-guard-baseline",
                run_id="run-real-3",
            )
        )
        print(
            "[real-top-level-gate-3] "
            f"state={run_body['run']['state']!r} "
            f"failure_reason={run_body['run'].get('failure_reason')!r} "
            f"content={run_body.get('assistant_content')!r} "
            f"invocations={json.dumps(run_body['invocations'])}"
        )
        # R5-WU-02 (Controller IR-P9-2-R4-02 fix): same Hard Assert as
        # Scenario 2 -- `completed` alone, never `completed | failed`.
        assert run_body["run"]["state"] == "completed", (
            f"real Top-level Scenario 3 did not COMPLETE: {run_body['run']}"
        )
        invocation_by_key = {item["component_key"]: item for item in run_body["invocations"]}
        assert invocation_by_key["main"]["called"] is True
        # R5-WU-03 (Controller IR-P9-2-R4-03 fix): Guard's own real
        # Evidence source has no request-scoped correlation this Round
        # (`experiment_production_turn_adapter.py`'s own documented,
        # unconditional `guard_called=None`/`guard_outcome=
        # "unavailable_correlation"`) -- asserted as exactly that,
        # honestly Unavailable, never reworded as proof Guard was
        # actually Dispatched for this real Turn.
        assert invocation_by_key["guard"]["called"] is None
        assert invocation_by_key["guard"]["outcome"] == "unavailable_correlation"
        _restart_read(
            experiment_store_dir,
            experiment_id="exp-real-r4-3",
            variant_id="production-guard-baseline",
            run_id="run-real-3",
            expected_main=_IdentityExpectation(
                configured=QWEN_MAIN, active=QWEN_MAIN, expected_executed=QWEN_MAIN
            ),
            expected_guard=_IdentityExpectation(
                configured=QWEN3_GUARD, active=QWEN3_GUARD, expected_executed=QWEN3_GUARD
            ),
        )
    finally:
        runtime.close()


def test_the_scenario_completion_oracle_rejects_a_failed_real_run() -> None:
    """R5-WU-02 SS4.3 (false-success regression): proves the strengthened
    Oracle above -- `assert run_body["run"]["state"] == "completed"` --
    genuinely rejects a `failed` outcome, rather than silently accepting
    it the way R4's own `in ("completed", "failed")` did. This is a pure,
    Fake-driven Assertion-logic Test (no real Model, no `model_smoke`
    marker, no Apple Silicon gate) -- it exercises the exact assertion
    expression Scenario 2/3 use, against a Fake `run_body` shaped like a
    genuinely-failed real Run, and confirms it raises `AssertionError`
    rather than passing."""

    fake_failed_run_body = {
        "run": {"state": "failed", "failure_reason": "live_config_mismatch"}
    }
    with pytest.raises(AssertionError):
        assert fake_failed_run_body["run"]["state"] == "completed", (
            f"real Top-level Scenario did not COMPLETE: {fake_failed_run_body['run']}"
        )


_FIXTURE_CASE_DIGEST = "7" * 128


def _write_restart_read_fixture(
    store: LocalFilesystemExperimentStore,
    *,
    experiment_id: str,
    variant_id: str,
    run_id: str,
    corrupt: str | None = None,
) -> None:
    """Builds a hand-populated, well-formed Store fixture matching the
    REAL persisted shape `experiment_routes.py` writes (Plan, Desired
    Configuration, Run, Frozen Configuration Snapshot with `correlation`/
    `provider_identity`, Raw Evidence, Comparison) -- entirely without a
    real Model, HTTP server, or `model_smoke` marker -- so `_restart_read()`
    itself can be Hard-Assert-tested fast and deterministically.

    `corrupt`, when given, introduces exactly ONE named defect into an
    otherwise well-formed fixture -- this is what the accompanying
    negative Tests use to confirm each new Hard Assert in `_restart_read()`
    genuinely rejects a broken Store, never merely "looks plausible"."""

    variant = VariantDescriptor(
        variant_id=variant_id,
        components=(
            ComponentSelection(
                component_key=ComponentKey.MAIN, selector_id=QWEN_MAIN, mode="active"
            ),
        ),
    )
    digest = "a" * 128
    plan = build_experiment_plan(
        experiment_id=experiment_id,
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_FIXTURE_CASE_DIGEST,
        variants=(variant,),
        execution_order=(variant_id,),
        budget=ExperimentPlanBudget(),
        variant_configuration_digests=(
            VariantConfigurationRef(variant_id=variant_id, configuration_digest_sha512=digest),
        ),
        execution_mode="production",
    )
    store.save_plan(plan)
    store.save_variant_desired_configuration(
        experiment_id,
        variant_id,
        {"configuration_digest_sha512": digest if corrupt != "desired_digest" else "b" * 128},
    )
    run = VariantRun(
        run_id=run_id,
        experiment_id=experiment_id,
        variant_id=variant_id,
        request_id="req-fixture-1",
        execution_mode="production",
        state=RunState.COMPLETED,
        generation=1,
        started_at="2026-01-01T00:00:00+00:00",
        completed_at="2026-01-01T00:00:01+00:00",
    )
    store.save_run(run)
    provider_identity = ProviderIdentityEnvelope(
        main=ProviderIdentityDetail(
            component_key=ComponentKey.MAIN,
            configured_selector_id=QWEN_MAIN,
            active_selector_id=(
                QWEN_MAIN if corrupt != "provider_identity_active" else "some-other-provider"
            ),
            expected_executed_selector_id=QWEN_MAIN,
        ),
        judge=ProviderIdentityDetail(component_key=ComponentKey.JUDGE),
        guard=ProviderIdentityDetail(component_key=ComponentKey.GUARD),
    ).model_dump(mode="json")
    correlation = {
        "run_id": run_id,
        "experiment_id": experiment_id,
        "variant_id": variant_id if corrupt != "correlation_variant_id" else "some-other-variant",
        "case_digest_sha512": plan.case_digest_sha512,
        "plan_digest_sha512": plan.plan_digest_sha512,
    }
    store.save_run_configuration_snapshot(
        run_id,
        {
            "configuration_digest_sha512": digest,
            "provider_identity": provider_identity,
            "correlation": correlation,
        },
    )
    store.save_raw_evidence(
        run_id,
        {
            "metric": {
                "run_id": run_id,
                "case_id": "case-a",
                "runtime_state": "completed",
            }
        },
    )
    rows: list[dict[str, Any]] = []
    if corrupt != "comparison_row_missing":
        rows.append(
            {
                "run_id": run_id,
                "variant_id": variant_id,
                "runtime_state": "completed",
                "metric": {"run_id": run_id, "case_id": "case-a", "runtime_state": "completed"},
                "observations": [
                    {"run_id": run_id, "case_id": "case-a", "outcome": "inconclusive"}
                ],
            }
        )
    store.save_comparison(experiment_id, {"experiment_id": experiment_id, "rows": rows})


def test_restart_read_oracle_passes_on_a_well_formed_store(tmp_path: Path) -> None:
    """R5-WU-01 happy-path proof: a hand-built Store fixture, shaped
    exactly like a real completed Production Run's own persisted objects,
    satisfies every one of `_restart_read()`'s new Hard Asserts."""

    store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    _write_restart_read_fixture(
        store, experiment_id="exp-fx", variant_id="v1", run_id="run-fx"
    )
    _restart_read(
        tmp_path,
        experiment_id="exp-fx",
        variant_id="v1",
        run_id="run-fx",
        expected_main=_IdentityExpectation(
            configured=QWEN_MAIN, active=QWEN_MAIN, expected_executed=QWEN_MAIN
        ),
    )


@pytest.mark.parametrize(
    "corrupt",
    [
        "desired_digest",
        "provider_identity_active",
        "correlation_variant_id",
        "comparison_row_missing",
    ],
)
def test_restart_read_oracle_rejects_each_named_defect(tmp_path: Path, corrupt: str) -> None:
    """R5-WU-01 (Controller IR-P9-2-R4-01 fix) false-success regression:
    each Hard Assert `_restart_read()` gained this Round is exercised
    against a Store fixture carrying exactly ONE of the defects the R4
    Oracle would have missed -- a Desired-Configuration digest that does
    not match the Plan's own reference, a Frozen `provider_identity`
    whose Active Selector does not match what was actually Live, a
    `correlation` block pointing at the wrong `variant_id`, and a
    Comparison Report with no Row at all for this `run_id`. Every one
    must raise `AssertionError`, never pass silently."""

    store = LocalFilesystemExperimentStore(base_dir=tmp_path)
    _write_restart_read_fixture(
        store, experiment_id="exp-fx", variant_id="v1", run_id="run-fx", corrupt=corrupt
    )
    with pytest.raises(AssertionError):
        _restart_read(
            tmp_path,
            experiment_id="exp-fx",
            variant_id="v1",
            run_id="run-fx",
            expected_main=_IdentityExpectation(
                configured=QWEN_MAIN, active=QWEN_MAIN, expected_executed=QWEN_MAIN
            ),
        )
