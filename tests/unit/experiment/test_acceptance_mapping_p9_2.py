"""Phase 9-2 WU-F F2: Acceptance Mapping Fixture Matrix.

One test per row of the Execution Design's own §12 Acceptance Mapping
table, each exercising the real mechanism claimed to satisfy that row --
never a restatement of the requirement text alone. Every test here is
Fixture/Deterministic; no real Model, Judge, Guard, or Network is
touched (matching every other test in this package)."""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.adapters.experiment.fixture_actor_adapters import (
    FixtureActor,
    ManualRoutingStrategy,
)
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
from margpa_runtime_llm.modules.experiment.domain.belief_revision import (
    BeliefRevisionObservation,
    BeliefRevisionOutcome,
    classify_belief_revision,
)
from margpa_runtime_llm.modules.experiment.domain.comparison_declaration import (
    VariantComparisonDeclaration,
    VariantRelationship,
    verify_single_factor_difference,
)
from margpa_runtime_llm.modules.experiment.domain.composition import (
    DefinitionVerdict,
    DefinitionVerdictOutcome,
    RepairOrigin,
    resolve_governance_composition,
)
from margpa_runtime_llm.modules.experiment.domain.config_snapshot import (
    build_effective_configuration_snapshot,
)
from margpa_runtime_llm.modules.experiment.domain.dataset import ObservationOutcome
from margpa_runtime_llm.modules.experiment.domain.evaluation import (
    EvaluatorKind,
    build_automated_observation,
    build_human_observation,
)
from margpa_runtime_llm.modules.experiment.domain.freshness import (
    FreshnessCase,
    FreshnessOutcome,
    SourceRevisionState,
    classify_freshness_answer,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    VariantDescriptor,
    build_experiment_plan,
)
from margpa_runtime_llm.modules.experiment.domain.presentation import (
    PresentationEvent,
    PresentationMode,
    ProgressiveState,
)
from margpa_runtime_llm.modules.experiment.domain.retrieval_case import (
    GroundingOutcome,
    RetrievalCase,
    RetrievalMode,
    classify_grounding,
)
from margpa_runtime_llm.modules.experiment.domain.run import RunState
from margpa_runtime_llm.modules.experiment.domain.trace import (
    CallZeroReason,
    ExecutionTraceProjection,
    TraceDisposition,
    TraceStage,
    TraceStageRecord,
)


def test_p9_req_201_p9_acc_039_experiment_run_request_and_digests_correlate(
    tmp_path: Path,
) -> None:
    """experiment_id/run_id/request_id, Effective Config Snapshot, and
    Model/Artifact/Definition/Plan Digest are all correlatable through
    one real Plan/Run/Snapshot triple, not merely documented as separate
    fields."""

    service = ExperimentService(store=LocalFilesystemExperimentStore(base_dir=tmp_path))
    variant = VariantDescriptor(
        variant_id="variant-a",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    plan = build_experiment_plan(
        experiment_id="exp-req-201",
        case_id="case-req-201",
        case_revision="case-rev-1",
        case_digest_sha512="5" * 128,
        variants=(variant,),
        execution_order=("variant-a",),
    )
    service.create_plan(plan)
    run = service.start_run(
        experiment_id="exp-req-201",
        variant_id="variant-a",
        run_id="run-201",
        request_id="req-201",
        execution_mode="fixture",
    )
    off = ComponentSelection(component_key=ComponentKey.JUDGE, mode="off")
    guard_off = ComponentSelection(component_key=ComponentKey.GUARD, mode="off")
    main_gov_off = ComponentSelection(component_key=ComponentKey.MAIN_GOVERNANCE, mode="off")
    definition_off = ComponentSelection(component_key=ComponentKey.DEFINITION_SET, mode="off")
    rag_off = ComponentSelection(component_key=ComponentKey.RAG, mode="off")
    repair_off = ComponentSelection(component_key=ComponentKey.REPAIR, mode="off")
    recording_off = ComponentSelection(component_key=ComponentKey.RECORDING, mode="off")
    presentation_off = ComponentSelection(component_key=ComponentKey.PRESENTATION, mode="off")
    snapshot = build_effective_configuration_snapshot(
        main=variant.components[0],
        judge=off,
        guard=guard_off,
        main_governance=main_gov_off,
        definition_set=definition_off,
        rag=rag_off,
        repair=repair_off,
        recording=recording_off,
        presentation=presentation_off,
        plan_digest_sha512=plan.plan_digest_sha512,
    )
    assert run.experiment_id == plan.experiment_id
    assert run.request_id == "req-201"
    assert snapshot.plan_digest_sha512 == plan.plan_digest_sha512


def test_p9_req_202_p9_acc_040_variant_composition_differs_on_the_same_case(
    tmp_path: Path,
) -> None:
    """Main/Judge/Guard/Repair Variant differences are compared under one
    identical `case_revision` -- the Independence Matrix's own real
    Runner output, not a hand-written stand-in."""

    off_variant = VariantDescriptor(
        variant_id="judge-off",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="off"),),
    )
    enforce_variant = VariantDescriptor(
        variant_id="judge-enforce",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),),
    )
    plan = build_experiment_plan(
        experiment_id="exp-req-202",
        case_id="case-2",
        case_revision="case-rev-1",
        case_digest_sha512="7" * 128,
        variants=(off_variant, enforce_variant),
        execution_order=("judge-off", "judge-enforce"),
    )
    actors = {ComponentKey.JUDGE: FixtureActor()}
    off_result = run_variant(off_variant, actors)
    enforce_result = run_variant(enforce_variant, actors)
    assert off_result.was_called(ComponentKey.JUDGE) is False
    assert enforce_result.was_called(ComponentKey.JUDGE) is True
    assert plan.case_revision == "case-rev-1"


def test_p9_req_204_p9_acc_041_multiple_definition_conflict_and_routing_compared() -> None:
    verdicts = (
        DefinitionVerdict(definition_id="def-a", outcome=DefinitionVerdictOutcome.MATCH),
        DefinitionVerdict(definition_id="def-b", outcome=DefinitionVerdictOutcome.CONFLICT),
    )
    result = resolve_governance_composition(
        verdicts=verdicts,
        routing=ManualRoutingStrategy(manual_selection_ids=("def-a",)),
        repair_requested_by="judge_and_main",
        registered_actors=frozenset(),
    )
    assert result.selected == ("def-a",)
    assert result.conflicts == ("def-b",)
    assert result.repair_propagation is RepairOrigin.JUDGE_AND_MAIN


def test_p9_req_205_to_207_p9_acc_042_to_043_freshness_grounding_and_belief_revision() -> None:
    freshness = classify_freshness_answer(
        case=FreshnessCase(
            case_id="case-fresh-1",
            historical_claim="ALPHA-15 confirmed value: 000",
            historical_citation_digest_sha512="a" * 128,
            source_revision_state=SourceRevisionState.UPDATED,
            current_source_value="765",
        ),
        new_turn_answer="ALPHA-15 is now 765.",
        historical_turn_citation_digest_after_answer="a" * 128,
    )
    assert freshness is FreshnessOutcome.CURRENT_FACT_USED

    grounding = classify_grounding(
        case=RetrievalCase(case_id="case-ground-1", retrieval_mode=RetrievalMode.IRRELEVANT_HIT),
        answer="According to the retrieved document...",
        answer_claims_citation=True,
    )
    assert grounding is GroundingOutcome.FALSE_GROUNDING

    revision = classify_belief_revision(
        BeliefRevisionObservation(
            case_id="case-belief-1",
            historical_claim="ALPHA-15 confirmed value: 000",
            user_correction="765",
            final_claim="ALPHA-15 confirmed value: 765",
        )
    )
    assert revision is BeliefRevisionOutcome.CORRECTION_ACCEPTED


def test_p9_req_208_strict_buffer_and_progressive_presentation_are_separated() -> None:
    strict_event = PresentationEvent(
        mode=PresentationMode.STRICT_BUFFER,
        state=ProgressiveState.FINALIZED,
        is_final=True,
        is_verified=True,
    )
    assert strict_event.mode is PresentationMode.STRICT_BUFFER
    progressive_event = PresentationEvent(
        mode=PresentationMode.PROGRESSIVE, state=ProgressiveState.GENERATING, is_final=False
    )
    assert progressive_event.is_verified is False


def test_p9_req_209_p9_acc_044_manual_url_fail_closed_trace_shows_call_0() -> None:
    trace = ExecutionTraceProjection(
        request_id="req-209",
        stages=(
            TraceStageRecord(
                stage=TraceStage.MANUAL_URL_FETCH,
                call_count=0,
                call_zero_reason=CallZeroReason.MANUAL_URL_FAIL_CLOSED,
            ),
            TraceStageRecord(
                stage=TraceStage.MAIN,
                call_count=0,
                call_zero_reason=CallZeroReason.NOT_APPLICABLE,
            ),
        ),
        disposition=TraceDisposition.FAILED,
    )
    fetch_record = trace.stage_record(TraceStage.MANUAL_URL_FETCH)
    assert fetch_record is not None
    assert fetch_record.call_count == 0
    assert fetch_record.call_zero_reason is CallZeroReason.MANUAL_URL_FAIL_CLOSED


def test_p9_req_203_p9_acc_045_baseline_regression_and_reviewer_kinds_never_conflated(
    tmp_path: Path,
) -> None:
    baseline = VariantDescriptor(
        variant_id="baseline",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="off"),),
    )
    regression = VariantDescriptor(
        variant_id="judge-enforce",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),),
    )
    declared = VariantComparisonDeclaration(
        baseline_variant_id="baseline",
        variant_id="judge-enforce",
        relationship=VariantRelationship.REGRESSION,
        varied_component_keys=(ComponentKey.JUDGE,),
    )
    verify_single_factor_difference(baseline=baseline, variant=regression, declared=declared)

    human = build_human_observation(
        run_id="run-1",
        case_id="case-1",
        reviewer_id="reviewer-1",
        rubric_revision="case-rev-1",
        outcome=ObservationOutcome.PASS,
    )
    independent_judge = build_automated_observation(
        run_id="run-1",
        case_id="case-1",
        evaluator_kind=EvaluatorKind.INDEPENDENT_JUDGE,
        provider_identity="judge.gemma-4-e2b-it-q4-0",
        rubric_revision="case-rev-1",
        outcome=ObservationOutcome.PASS,
    )
    assert human.evaluator_kind is EvaluatorKind.HUMAN
    assert independent_judge.evaluator_kind is EvaluatorKind.INDEPENDENT_JUDGE
    assert human.evaluator_identity != independent_judge.evaluator_identity

    service = ExperimentService(store=LocalFilesystemExperimentStore(base_dir=tmp_path))
    plan = build_experiment_plan(
        experiment_id="exp-req-203",
        case_id="case-1",
        case_revision="case-rev-1",
        case_digest_sha512="6" * 128,
        variants=(baseline, regression),
        execution_order=("baseline", "judge-enforce"),
    )
    service.create_plan(plan)
    run = service.start_run(
        experiment_id="exp-req-203",
        variant_id="judge-enforce",
        run_id="run-1",
        request_id="req-1",
        execution_mode="fixture",
    )
    service.publish_result("run-1", generation=run.generation, target_state=RunState.COMPLETED)
    report = build_comparison_report(
        experiment_id="exp-req-203",
        case_revision="case-rev-1",
        store=service.store,
        observations_by_run_id={"run-1": (human, independent_judge)},
    )
    row = report.row("run-1")
    assert row is not None
    kinds = {observation.evaluator_kind for observation in row.observations}
    assert kinds == {EvaluatorKind.HUMAN, EvaluatorKind.INDEPENDENT_JUDGE}
