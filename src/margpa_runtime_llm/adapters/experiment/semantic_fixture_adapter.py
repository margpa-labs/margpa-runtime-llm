"""Deterministic top-level Fixture semantics for Phase 9-2 cases.

This Adapter owns every case-specific answer, retrieval signal, routing
fixture, presentation sequence, and Call-0 scenario.  Experiment Core
only receives typed Evidence and declarations; no Model/Provider/case
special case is embedded in the Core services.
"""

from __future__ import annotations

from dataclasses import dataclass

from margpa_runtime_llm.modules.experiment.application.composition_runner import run_variant
from margpa_runtime_llm.modules.experiment.domain.belief_revision import (
    BeliefRevisionObservation,
    classify_belief_revision,
)
from margpa_runtime_llm.modules.experiment.domain.case_pack import (
    BELIEF_REVISION_CORRECTION,
    FRESHNESS_CASES_BY_ID,
    RETRIEVAL_CASES_BY_ID,
)
from margpa_runtime_llm.modules.experiment.domain.comparison_declaration import (
    VariantComparisonDeclaration,
    VariantRelationship,
    verify_single_factor_difference,
)
from margpa_runtime_llm.modules.experiment.domain.composition import (
    ActorInvocationRecord,
    DefinitionVerdict,
    DefinitionVerdictOutcome,
    GovernanceCompositionResult,
    RepairOrigin,
    RoutingStrategyPort,
    VariantExecutionResult,
    resolve_governance_composition,
)
from margpa_runtime_llm.modules.experiment.domain.dataset import (
    EvaluationCaseManifest,
    ObservationOutcome,
    SemanticEvaluatorRoute,
)
from margpa_runtime_llm.modules.experiment.domain.freshness import (
    SourceRevisionState,
    classify_freshness_answer,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ExperimentPlan,
    VariantDescriptor,
)
from margpa_runtime_llm.modules.experiment.domain.presentation import (
    PresentationEvent,
    PresentationMode,
    ProgressiveState,
)
from margpa_runtime_llm.modules.experiment.domain.retrieval_case import (
    NoHitStrategy,
    RetrievalMode,
    classify_grounding,
)
from margpa_runtime_llm.modules.experiment.domain.semantic_evidence import CaseSemanticEvidence
from margpa_runtime_llm.modules.experiment.domain.trace import (
    CallZeroReason,
    ExecutionTraceProjection,
    TraceDisposition,
    TraceStage,
    TraceStageRecord,
)

from .fixture_actor_adapters import (
    DynamicRoutingStrategy,
    FixtureActor,
    ManualRoutingStrategy,
    StaticRoutingStrategy,
)

FIXTURE_MAIN_NEGATED_CURRENT_MODE = "negated_current_value"
FIXTURE_MAIN_MANUAL_URL_FAIL_CLOSED_MODE = "manual_url_fail_closed"
FIXTURE_GUARD_SHORT_CIRCUIT_MODE = "short_circuit"
FIXTURE_JUDGE_REPAIR_REQUEST_MODE = "enforce_repair_requested"
FIXTURE_MAIN_GOVERNANCE_REPAIR_REQUEST_MODE = "strict_repair_requested"


@dataclass(frozen=True, slots=True)
class FixtureCaseExecution:
    execution: VariantExecutionResult
    semantic_evidence: CaseSemanticEvidence


_SINGLE_FACTOR_RELATIONSHIPS: dict[str, tuple[str, VariantRelationship]] = {
    "fixture-main-active": ("baseline-all-off", VariantRelationship.REGRESSION),
    "fixture-judge-observe": ("baseline-all-off", VariantRelationship.REGRESSION),
    "fixture-guard-enforce": ("baseline-all-off", VariantRelationship.REGRESSION),
    "fixture-main-governance-strict": (
        "baseline-all-off",
        VariantRelationship.REGRESSION,
    ),
    "fixture-definition-manual": ("baseline-all-off", VariantRelationship.REGRESSION),
    "fixture-definition-static": ("baseline-all-off", VariantRelationship.REGRESSION),
    "fixture-definition-dynamic": ("baseline-all-off", VariantRelationship.REGRESSION),
    "fixture-definition-manual-with-repair": (
        "fixture-definition-manual-judge-request",
        VariantRelationship.REGRESSION,
    ),
    "fixture-rag-relevant": ("fixture-main-active", VariantRelationship.REGRESSION),
    "fixture-rag-no-hit": ("fixture-main-active", VariantRelationship.REGRESSION),
    "fixture-rag-strict-no-hit": (
        "fixture-main-active",
        VariantRelationship.REGRESSION,
    ),
    "fixture-repair-enforce": ("baseline-all-off", VariantRelationship.REGRESSION),
    "fixture-main-governance-with-repair": (
        "fixture-main-governance-request-no-repair",
        VariantRelationship.REGRESSION,
    ),
    "fixture-presentation-strict": ("baseline-all-off", VariantRelationship.REGRESSION),
    "fixture-presentation-progressive": (
        "baseline-all-off",
        VariantRelationship.REGRESSION,
    ),
    "fixture-recording-active": ("baseline-all-off", VariantRelationship.REGRESSION),
    "fixture-manual-url-fail-closed": (
        "fixture-main-active",
        VariantRelationship.REGRESSION,
    ),
    "fixture-guard-short-circuit": (
        "fixture-main-active",
        VariantRelationship.REGRESSION,
    ),
    "fixture-judge-enforce-no-repair": (
        "judge-enforce-repair",
        VariantRelationship.ABLATION,
    ),
}


def fixture_comparison_declarations(
    plan: ExperimentPlan,
) -> tuple[VariantComparisonDeclaration, ...]:
    """Derive only registered, mechanically verified single-factor claims."""

    variants = {variant.variant_id: variant for variant in plan.variants}
    relevant = {
        variant_id: pair
        for variant_id, pair in _SINGLE_FACTOR_RELATIONSHIPS.items()
        if variant_id in variants and pair[0] in variants
    }
    baseline_ids = sorted({baseline_id for baseline_id, _ in relevant.values()})
    declarations: list[VariantComparisonDeclaration] = []
    for baseline_id in baseline_ids:
        declaration = VariantComparisonDeclaration(
            baseline_variant_id=baseline_id,
            variant_id=baseline_id,
            relationship=VariantRelationship.BASELINE,
        )
        verify_single_factor_difference(
            baseline=variants[baseline_id],
            variant=variants[baseline_id],
            declared=declaration,
        )
        declarations.append(declaration)
    for variant_id in sorted(relevant):
        baseline_id, relationship = relevant[variant_id]
        baseline = variants[baseline_id]
        variant = variants[variant_id]
        differing = tuple(
            key for key in ComponentKey if baseline.component(key) != variant.component(key)
        )
        declaration = VariantComparisonDeclaration(
            baseline_variant_id=baseline_id,
            variant_id=variant_id,
            relationship=relationship,
            varied_component_keys=differing,
        )
        verify_single_factor_difference(
            baseline=baseline,
            variant=variant,
            declared=declaration,
        )
        declarations.append(declaration)
    return tuple(declarations)


def _called(execution: VariantExecutionResult, key: ComponentKey) -> bool:
    invocation = execution.invocation(key)
    return invocation is not None and invocation.called is True


def _is_strict_no_hit_case(case: EvaluationCaseManifest) -> bool:
    retrieval_case = RETRIEVAL_CASES_BY_ID.get(case.case_id)
    return bool(
        retrieval_case is not None
        and retrieval_case.no_hit_strategy
        is NoHitStrategy.STRICT_NO_HIT_MODEL_CALL_ZERO
    )


def _declared_repair_requesters(variant: VariantDescriptor) -> tuple[ComponentKey, ...]:
    requesters: list[ComponentKey] = []
    judge = variant.component(ComponentKey.JUDGE)
    if judge is not None and judge.mode == FIXTURE_JUDGE_REPAIR_REQUEST_MODE:
        requesters.append(ComponentKey.JUDGE)
    main_governance = variant.component(ComponentKey.MAIN_GOVERNANCE)
    if (
        main_governance is not None
        and main_governance.mode == FIXTURE_MAIN_GOVERNANCE_REPAIR_REQUEST_MODE
    ):
        requesters.append(ComponentKey.MAIN_GOVERNANCE)
    return tuple(requesters)


def _observed_repair_origin(
    variant: VariantDescriptor, execution: VariantExecutionResult
) -> RepairOrigin | None:
    observed = {
        key
        for key in _declared_repair_requesters(variant)
        if _called(execution, key)
    }
    if observed == {ComponentKey.JUDGE, ComponentKey.MAIN_GOVERNANCE}:
        return RepairOrigin.JUDGE_AND_MAIN
    if observed == {ComponentKey.JUDGE}:
        return RepairOrigin.JUDGE
    if observed == {ComponentKey.MAIN_GOVERNANCE}:
        return RepairOrigin.MAIN_GOVERNANCE
    return None


def _execute_components(
    case: EvaluationCaseManifest, variant: VariantDescriptor
) -> VariantExecutionResult:
    main_selection = variant.component(ComponentKey.MAIN)
    guard_selection = variant.component(ComponentKey.GUARD)
    short_circuit_main = (
        _is_strict_no_hit_case(case)
        or (
            main_selection is not None
            and main_selection.mode == FIXTURE_MAIN_MANUAL_URL_FAIL_CLOSED_MODE
        )
        or (
            guard_selection is not None
            and guard_selection.mode == FIXTURE_GUARD_SHORT_CIRCUIT_MODE
        )
    )
    actors: dict[ComponentKey, FixtureActor] = {
        key: FixtureActor(mutation_count=1, evidence_count=1, authority_exercised=True)
        for key in ComponentKey
        if not (short_circuit_main and key is ComponentKey.MAIN)
        and key is not ComponentKey.REPAIR
    }
    execution = run_variant(variant, actors)
    repair_selection = variant.component(ComponentKey.REPAIR)
    repair_enabled = bool(
        repair_selection is not None
        and repair_selection.mode not in (None, "off")
    )
    if not short_circuit_main and not repair_enabled:
        return execution
    replacements: dict[ComponentKey, ActorInvocationRecord] = {}
    if short_circuit_main:
        if _is_strict_no_hit_case(case):
            outcome = "call_zero:strict_no_hit"
        elif (
            main_selection is not None
            and main_selection.mode == FIXTURE_MAIN_MANUAL_URL_FAIL_CLOSED_MODE
        ):
            outcome = "call_zero:manual_url_fail_closed"
        else:
            outcome = "call_zero:guard_input_short_circuit"
        replacements[ComponentKey.MAIN] = ActorInvocationRecord(
            component_key=ComponentKey.MAIN,
            called=False,
            outcome=outcome,
        )
    if repair_enabled:
        repair_requested_by = _observed_repair_origin(variant, execution)
        if repair_requested_by is None:
            replacements[ComponentKey.REPAIR] = ActorInvocationRecord(
                component_key=ComponentKey.REPAIR,
                called=False,
                outcome="call_zero:no_eligible_repair_requester",
            )
        else:
            assert repair_selection is not None
            replacements[ComponentKey.REPAIR] = FixtureActor(
                mutation_count=1,
                evidence_count=1,
                authority_exercised=True,
            ).invoke(
                component_key=ComponentKey.REPAIR,
                mode=repair_selection.mode,
            )
    return VariantExecutionResult(
        variant_id=execution.variant_id,
        invocations=tuple(
            replacements.get(item.component_key, item)
            for item in execution.invocations
        ),
    )


def _trace_for(
    case: EvaluationCaseManifest,
    variant: VariantDescriptor,
    execution: VariantExecutionResult,
) -> ExecutionTraceProjection:
    records: list[TraceStageRecord] = []
    main_selection = variant.component(ComponentKey.MAIN)
    guard_selection = variant.component(ComponentKey.GUARD)
    manual_url_fail_closed = (
        main_selection is not None
        and main_selection.mode == FIXTURE_MAIN_MANUAL_URL_FAIL_CLOSED_MODE
    )
    guard_short_circuit = (
        guard_selection is not None
        and guard_selection.mode == FIXTURE_GUARD_SHORT_CIRCUIT_MODE
    )
    if manual_url_fail_closed:
        records.append(
            TraceStageRecord(
                stage=TraceStage.MANUAL_URL_FETCH,
                call_count=0,
                call_zero_reason=CallZeroReason.MANUAL_URL_FAIL_CLOSED,
            )
        )
    stage_keys = (
        (TraceStage.MAIN, ComponentKey.MAIN),
        (TraceStage.JUDGE, ComponentKey.JUDGE),
        (TraceStage.REPAIR, ComponentKey.REPAIR),
        (TraceStage.GUARD, ComponentKey.GUARD),
    )
    for stage, key in stage_keys:
        invocation = execution.invocation(key)
        called = invocation is not None and invocation.called is True
        if called:
            records.append(TraceStageRecord(stage=stage, call_count=1))
            continue
        reason = CallZeroReason.NOT_APPLICABLE
        if key is ComponentKey.MAIN and _is_strict_no_hit_case(case):
            reason = CallZeroReason.STRICT_NO_HIT
        elif key is ComponentKey.MAIN and guard_short_circuit:
            reason = CallZeroReason.GUARD_INPUT_SHORT_CIRCUIT
        elif (
            key is ComponentKey.REPAIR
            and (selection := variant.component(ComponentKey.REPAIR)) is not None
            and selection.mode not in (None, "off")
            and _observed_repair_origin(variant, execution) is None
        ):
            reason = CallZeroReason.NO_ELIGIBLE_REPAIR_REQUESTER
        records.append(TraceStageRecord(stage=stage, call_count=0, call_zero_reason=reason))
    disposition = TraceDisposition.CANDIDATE_ACCEPTED
    if manual_url_fail_closed:
        disposition = TraceDisposition.FAILED
    elif _is_strict_no_hit_case(case):
        disposition = TraceDisposition.SAFE_FALLBACK
    elif guard_short_circuit:
        disposition = TraceDisposition.BLOCKED
    elif _called(execution, ComponentKey.REPAIR):
        disposition = TraceDisposition.REPAIR_ACCEPTED
    return ExecutionTraceProjection(
        request_id=f"trace-{variant.variant_id}",
        stages=tuple(records),
        disposition=disposition,
    )


def _presentation_for(variant: VariantDescriptor) -> tuple[PresentationEvent, ...]:
    selection = variant.component(ComponentKey.PRESENTATION)
    if selection is None or selection.mode in (None, "off"):
        return ()
    if selection.mode == PresentationMode.STRICT_BUFFER.value:
        return (
            PresentationEvent(
                mode=PresentationMode.STRICT_BUFFER,
                state=ProgressiveState.FINALIZED,
                is_final=True,
                is_verified=True,
            ),
        )
    if selection.mode == PresentationMode.PROGRESSIVE.value:
        return (
            PresentationEvent(mode=PresentationMode.PROGRESSIVE, state=ProgressiveState.STARTED),
            PresentationEvent(
                mode=PresentationMode.PROGRESSIVE,
                state=ProgressiveState.GENERATING,
            ),
            PresentationEvent(
                mode=PresentationMode.PROGRESSIVE,
                state=ProgressiveState.EVALUATING,
            ),
            PresentationEvent(
                mode=PresentationMode.PROGRESSIVE,
                state=ProgressiveState.FINALIZED,
                is_final=True,
                is_verified=True,
            ),
        )
    return ()


def _governance_for(
    variant: VariantDescriptor,
    repair_requested_by: RepairOrigin | None,
) -> GovernanceCompositionResult | None:
    selection = variant.component(ComponentKey.DEFINITION_SET)
    if selection is None or selection.mode in (None, "off"):
        return None
    verdicts = (
        DefinitionVerdict(
            definition_id="definition-alpha",
            outcome=DefinitionVerdictOutcome.MATCH,
            authority_weight=1,
        ),
        DefinitionVerdict(
            definition_id="definition-beta",
            outcome=DefinitionVerdictOutcome.MATCH,
            authority_weight=5,
        ),
        DefinitionVerdict(
            definition_id="definition-conflict",
            outcome=DefinitionVerdictOutcome.CONFLICT,
        ),
    )
    routing: RoutingStrategyPort
    if selection.mode == "manual":
        routing = ManualRoutingStrategy(manual_selection_ids=("definition-alpha",))
    elif selection.mode == "dynamic":
        routing = DynamicRoutingStrategy()
    else:
        routing = StaticRoutingStrategy()
    return resolve_governance_composition(
        verdicts=verdicts,
        routing=routing,
        repair_requested_by=(
            repair_requested_by.value if repair_requested_by is not None else None
        ),
        registered_actors=frozenset(),
    )


def execute_fixture_case(
    *, case: EvaluationCaseManifest, variant: VariantDescriptor
) -> FixtureCaseExecution:
    execution = _execute_components(case, variant)
    repair_requested_by = _observed_repair_origin(variant, execution)
    repair_called = _called(execution, ComponentKey.REPAIR)
    evidence_values: dict[str, object] = {
        "case_id": case.case_id,
        "case_revision": case.revision,
        "repair_requested_by": repair_requested_by,
        "runtime_repair_accepted": repair_called,
        "execution_trace": _trace_for(case, variant, execution),
        "presentation_events": _presentation_for(variant),
        "governance_composition": _governance_for(variant, repair_requested_by),
    }

    if case.evaluator_route is SemanticEvaluatorRoute.FRESHNESS:
        freshness_case = FRESHNESS_CASES_BY_ID[case.case_id]
        main_selection = variant.component(ComponentKey.MAIN)
        negates_current = (
            main_selection is not None
            and main_selection.mode == FIXTURE_MAIN_NEGATED_CURRENT_MODE
        )
        if _called(execution, ComponentKey.MAIN):
            if negates_current:
                answer = (
                    f"{freshness_case.current_source_value} is not the current value; "
                    "765 is current."
                )
            elif freshness_case.source_revision_state is SourceRevisionState.DELETED:
                answer = "No current source evidence remains for ALPHA-15."
            else:
                answer = f"The current confirmed value is {freshness_case.current_source_value}."
        elif freshness_case.source_revision_state is SourceRevisionState.CURRENT:
            answer = "I am not sure."
        else:
            answer = freshness_case.historical_claim
        digest = freshness_case.historical_citation_digest_sha512
        adopts_current = bool(
            _called(execution, ComponentKey.MAIN)
            and not negates_current
            and freshness_case.current_source_value is not None
        )
        evidence_values.update(
            assistant_content=answer,
            answer_adopts_current_value=adopts_current,
            historical_turn_citation_digest_after_answer=digest,
            freshness_outcome=classify_freshness_answer(
                case=freshness_case,
                new_turn_answer=answer,
                historical_turn_citation_digest_after_answer=digest,
                current_value_adopted=adopts_current,
            ),
        )

    elif case.evaluator_route is SemanticEvaluatorRoute.RETRIEVAL:
        retrieval_case = RETRIEVAL_CASES_BY_ID[case.case_id]
        rag_called = _called(execution, ComponentKey.RAG)
        if retrieval_case.retrieval_mode is RetrievalMode.RELEVANT_HIT and rag_called:
            answer = retrieval_case.relevant_source_value or ""
            claims_citation = True
        elif retrieval_case.retrieval_mode is RetrievalMode.IRRELEVANT_HIT and rag_called:
            answer = "According to the unrelated retrieved document, ALPHA-22 is delayed."
            claims_citation = True
        elif retrieval_case.retrieval_mode is RetrievalMode.RAG_OFF:
            answer = "A parametric answer without retrieved evidence."
            claims_citation = False
        else:
            answer = "There is insufficient retrieved evidence to answer."
            claims_citation = False
        evidence_values.update(
            assistant_content=answer,
            answer_claims_citation=claims_citation,
            grounding_outcome=classify_grounding(
                case=retrieval_case,
                answer=answer,
                answer_claims_citation=claims_citation,
            ),
        )

    elif case.evaluator_route is SemanticEvaluatorRoute.BELIEF_REVISION:
        observation = BeliefRevisionObservation(
            case_id=case.case_id,
            historical_claim=BELIEF_REVISION_CORRECTION.historical_claim,
            current_source=BELIEF_REVISION_CORRECTION.current_source,
            user_correction=BELIEF_REVISION_CORRECTION.user_correction,
            final_claim=(
                BELIEF_REVISION_CORRECTION.final_claim
                if repair_called
                else BELIEF_REVISION_CORRECTION.historical_claim
            ),
        )
        evidence_values.update(
            belief_revision=observation,
            belief_revision_outcome=classify_belief_revision(observation),
        )

    elif case.evaluator_route is SemanticEvaluatorRoute.FALSE_IMPROVEMENT:
        fixture_outcome = (
            ObservationOutcome.FAIL if repair_called else ObservationOutcome.PASS
        )
        evidence_values.update(
            runtime_repair_accepted=repair_called,
            fixture_semantic_outcome=fixture_outcome,
        )

    return FixtureCaseExecution(
        execution=execution,
        semantic_evidence=CaseSemanticEvidence.model_validate(evidence_values),
    )
