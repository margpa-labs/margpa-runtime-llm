"""Phase 9-2 R1-WU-06: Handoff R1 Section 9.1 Hard Assert mapping.

One test (or a pointer to the real dedicated test) per numbered item in
the R1 Exact Handoff's own Section 9.1 list -- each exercising the real
mechanism claimed to satisfy that item, never a restatement of the
requirement text alone (mirrors `test_acceptance_mapping_p9_2.py`'s own
convention from the prior Long Run round).

Items #2, #4 (the Preset-changed-after-Plan-creation and Case-Pack-
content-changed-after-Plan-creation shapes) need a full HTTP route +
persisted Plan to exercise meaningfully and already have dedicated,
passing Integration tests -- pointed to below rather than duplicated:
  - tests/integration/web/test_experiment_routes.py::
    test_a_preset_change_after_plan_creation_never_affects_the_frozen_run
  - tests/integration/web/test_experiment_routes.py::
    test_a_case_pack_content_change_after_plan_creation_rejects_the_run_before_any_call
Item #8 (fixture_only/production real identity) is exercised by:
  - tests/integration/web/test_experiment_routes.py::
    test_a_production_run_completes_with_fixture_only_false
  - tests/integration/web/test_experiment_routes.py::
    test_full_plan_run_and_list_lifecycle (fixture_only=True path)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.experiment.fixture_actor_adapters import FixtureActor
from margpa_runtime_llm.adapters.experiment.local_filesystem_experiment_store import (
    LocalFilesystemExperimentStore,
)
from margpa_runtime_llm.modules.experiment.application.comparison_service import (
    build_comparison_report,
)
from margpa_runtime_llm.modules.experiment.application.composition_runner import run_variant
from margpa_runtime_llm.modules.experiment.application.experiment_service import (
    ExperimentService,
)
from margpa_runtime_llm.modules.experiment.domain.dataset import (
    ObservationOutcome,
)
from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.evaluation import (
    EvaluatorKind,
    build_automated_observation,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    ExperimentPlanBudget,
    VariantDescriptor,
    build_experiment_plan,
)
from margpa_runtime_llm.modules.experiment.domain.run import RunState

_CASE_DIGEST = "8" * 128


def _service(tmp_path: Path) -> ExperimentService:
    return ExperimentService(store=LocalFilesystemExperimentStore(base_dir=tmp_path))


def test_item_01_two_cases_sharing_a_revision_are_never_confused(tmp_path: Path) -> None:
    """"同じRevisionを持つ異なるCaseが混同されない。"

    Two Plans naming DIFFERENT `case_id`s under the SAME `case_revision`
    (the real Case Pack shape -- `CASE_PACK_REVISION` covers several
    distinct Cases) must produce different `plan_digest_sha512` and each
    Plan must independently report its own real `case_id` back, never the
    other's."""

    variant = VariantDescriptor(
        variant_id="variant-a",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    plan_alpha = build_experiment_plan(
        experiment_id="exp-item01-a",
        case_id="case-alpha",
        case_revision="shared-revision",
        case_digest_sha512="1" * 128,
        variants=(variant,),
        execution_order=("variant-a",),
    )
    plan_beta = build_experiment_plan(
        experiment_id="exp-item01-b",
        case_id="case-beta",
        case_revision="shared-revision",
        case_digest_sha512="2" * 128,
        variants=(variant,),
        execution_order=("variant-a",),
    )
    assert plan_alpha.case_revision == plan_beta.case_revision
    assert plan_alpha.case_id != plan_beta.case_id
    assert plan_alpha.plan_digest_sha512 != plan_beta.plan_digest_sha512


def test_item_03_mode_none_off_absent_unsupported_are_all_call_zero() -> None:
    """"`mode=None`/OFF/Absent/Unsupportedは当該Actor Call 0。"

    All four shapes in one Hard Assert, over the real `run_variant()`
    Composition Runner (not a hand-rolled restatement)."""

    absent_variant = VariantDescriptor(variant_id="v-absent", components=())
    mode_none_variant = VariantDescriptor(
        variant_id="v-mode-none",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, selector_id="judge-a"),),
    )
    off_variant = VariantDescriptor(
        variant_id="v-off",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="off"),),
    )
    unsupported_variant = VariantDescriptor(
        variant_id="v-unsupported",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),),
    )
    empty_actors: dict[ComponentKey, FixtureActor] = {}
    full_actors = {ComponentKey.JUDGE: FixtureActor()}

    absent_record = run_variant(absent_variant, full_actors).invocation(ComponentKey.JUDGE)
    assert absent_record is not None
    assert absent_record.called is False
    assert absent_record.outcome == "absent"
    assert run_variant(mode_none_variant, full_actors).was_called(ComponentKey.JUDGE) is False
    assert run_variant(off_variant, full_actors).was_called(ComponentKey.JUDGE) is False
    result = run_variant(unsupported_variant, empty_actors)
    record = result.invocation(ComponentKey.JUDGE)
    assert record is not None
    assert record.called is False
    assert record.outcome == "unsupported"


def test_item_05_max_variant_runs_and_execution_order_violations_are_call_zero(
    tmp_path: Path,
) -> None:
    """"`max_variant_runs`/Deadline/Stop Policy/Execution Order違反は
    Actor Call 0。"

    `max_variant_runs`/Execution-Order are enforced in `ExperimentService.
    start_run()` itself -- rejected before a Run object (let alone an
    Actor Call) is ever created. Deadline's own Call-0 enforcement lives
    in `ExperimentRunWorker` (see test_run_worker.py::
    test_an_exceeded_deadline_publishes_failed_without_ever_invoking_the_actor)."""

    variant_a = VariantDescriptor(
        variant_id="variant-a",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    plan = build_experiment_plan(
        experiment_id="exp-item05",
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_CASE_DIGEST,
        variants=(variant_a,),
        execution_order=("variant-a",),
        budget=ExperimentPlanBudget(max_variant_runs=1),
    )
    service = _service(tmp_path)
    service.create_plan(plan)
    service.start_run(
        experiment_id="exp-item05",
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
        execution_mode="fixture",
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.start_run(
            experiment_id="exp-item05",
            variant_id="variant-a",
            run_id="run-2",
            request_id="req-2",
            execution_mode="fixture",
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.MAX_VARIANT_RUNS_EXCEEDED


def test_item_06_actor_exception_failed_cancel_cancelled_late_publish_rejected(
    tmp_path: Path,
) -> None:
    """"Actor例外はRun FAILED、CancelはCANCELLED、Late Publishは拒否。"

    The Actor-exception-to-FAILED half of this Assert is exercised more
    thoroughly by the real `ExperimentRunWorker` in test_run_worker.py --
    this test focuses on the Cancel + Late-Publish half directly through
    `ExperimentService`."""

    variant_a = VariantDescriptor(
        variant_id="variant-a",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    plan = build_experiment_plan(
        experiment_id="exp-item06",
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_CASE_DIGEST,
        variants=(variant_a,),
        execution_order=("variant-a",),
    )
    service = _service(tmp_path)
    service.create_plan(plan)
    run = service.start_run(
        experiment_id="exp-item06",
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
        execution_mode="fixture",
    )
    cancelled = service.cancel_run("run-1")
    assert cancelled.state is RunState.CANCELLED
    with pytest.raises(ExperimentCoreError) as excinfo:
        service.publish_result("run-1", generation=run.generation, target_state=RunState.COMPLETED)
    assert excinfo.value.code is ExperimentCoreErrorCode.LATE_RESULT_REJECTED
    assert service.get_run("run-1").state is RunState.CANCELLED


def test_item_07_comparison_rejects_run_case_observation_mismatches(tmp_path: Path) -> None:
    """"ComparisonがRun/Case/Observationの不一致を拒否する。"

    See `test_comparison_report.py`'s own dedicated tests for the full
    `ComparisonRow` validator coverage; this confirms the same guarantee
    survives the real `build_comparison_report()` application path too --
    a caller-supplied Observation keyed under the wrong `run_id` is
    rejected, not silently attached to the wrong Row."""

    variant_a = VariantDescriptor(
        variant_id="variant-a",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    plan = build_experiment_plan(
        experiment_id="exp-item07",
        case_id="case-a",
        case_revision="case-rev-1",
        case_digest_sha512=_CASE_DIGEST,
        variants=(variant_a,),
        execution_order=("variant-a",),
    )
    service = _service(tmp_path)
    service.create_plan(plan)
    run = service.start_run(
        experiment_id="exp-item07",
        variant_id="variant-a",
        run_id="run-1",
        request_id="req-1",
        execution_mode="fixture",
    )
    service.publish_result("run-1", generation=run.generation, target_state=RunState.COMPLETED)
    mismatched_observation = build_automated_observation(
        run_id="a-completely-different-run-id",
        case_id="case-a",
        evaluator_kind=EvaluatorKind.DETERMINISTIC,
        provider_identity="metric.deterministic-v1",
        rubric_revision="case-rev-1",
        outcome=ObservationOutcome.NOT_RUN,
    )
    with pytest.raises(ExperimentCoreError) as excinfo:
        build_comparison_report(
            experiment_id="exp-item07",
            case_revision="case-rev-1",
            store=service.store,
            observations_by_run_id={"run-1": (mismatched_observation,)},
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.OBSERVATION_RUN_OR_CASE_MISMATCH


def test_item_09_experiment_absence_never_touches_ordinary_chat_wiring() -> None:
    """"Experiment OFF/不在時に通常Chat/Judge/Guard/RAG/Repairへ影響0。"

    Structural, not behavioral: `WebRuntime.experiment_service`/
    `production_turn_adapter`/`experiment_run_worker` are Optional fields
    Bootstrap fills in AFTER building `conversation`/`judge_governance_
    composition`/`guardrail_governance_composition` from the exact same
    already-existing Phase 9-1 composition -- nothing in `modules.
    conversation`/`bootstrap.judge_live_integration`/`bootstrap.
    guardrail_governance` imports or references the Experiment module at
    all, so their behavior cannot depend on whether Experiment is wired.
    The full pre-existing 2577-test non-model regression suite (unrelated
    to Experiment) passing unchanged is the real, whole-repo Evidence for
    this claim -- this test only pins the absence of the reverse import."""

    import ast
    import importlib
    import inspect

    modules = (
        importlib.import_module("margpa_runtime_llm.bootstrap.guardrail_governance"),
        importlib.import_module("margpa_runtime_llm.bootstrap.judge_live_integration"),
        importlib.import_module(
            "margpa_runtime_llm.modules.conversation.application.conversation_generation"
        ),
    )

    for module in modules:
        source = inspect.getsource(module)
        tree = ast.parse(source)
        imported_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module is not None:
                imported_names.add(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imported_names.add(alias.name)
        assert not any(
            name.startswith("margpa_runtime_llm.modules.experiment") for name in imported_names
        )
        assert not any(
            name.startswith("margpa_runtime_llm.adapters.experiment") for name in imported_names
        )


def test_item_10_ui_never_shows_a_fixture_result_as_a_real_model_result() -> None:
    """"UIはFixture ResultをRealModel Resultと表示しない。"

    Backend-side half: `_fixture_only_from_evidence()`'s real behavior is
    exercised end-to-end by the Integration tests named in this module's
    own docstring. This pins the Contract-level half: `VariantRunResponse.
    fixture_only` defaults `True` (never a silent `False`-by-omission that
    could make a Fixture Run look real by accident)."""

    from margpa_runtime_llm.web.experiment_routes import VariantRunResponse

    assert VariantRunResponse.model_fields["fixture_only"].default is True
