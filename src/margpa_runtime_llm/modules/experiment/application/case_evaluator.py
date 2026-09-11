"""Deterministic Case Evaluator (Phase 9-2 R2, WU-03).

Replaces R1's `_observation_for_row()` "`completed` => `PASS`" Oracle,
the IR-P9-2-R1-03 BLOCKER the Controller's Independent Review confirmed:
a Run reaching `RunState.COMPLETED` was, by itself, previously enough to
credit a Case with `PASS`, without ever consulting the Case's own
`expected_observations`, Actual Output, or Actual Evidence.

This module instead dispatches by `case_id` to the already-built Domain
Classifiers (`freshness.classify_freshness_answer`, `retrieval_case.
expected_call_count_for_no_hit_strategy`) that Phase 9-2 WU-D built for
exactly this purpose but WU-E/R1 never wired into the Web/Comparison
path (the Controller's own confirmed finding). Handoff R2 SS6: "評価に
必要なEvidenceがない場合はINCONCLUSIVE、NOT_RUNまたはUNAVAILABLEであり、
PASSではない" -- every branch below either resolves a genuine, Evidence-
backed verdict or returns one of those three honest non-PASS outcomes,
never a guess."""

from __future__ import annotations

from ..domain.belief_revision import BeliefRevisionOutcome, classify_belief_revision
from ..domain.case_pack import FRESHNESS_CASES_BY_ID, RETRIEVAL_CASES_BY_ID
from ..domain.dataset import (
    EvaluationCaseManifest,
    ObservationOutcome,
    SemanticEvaluatorRoute,
)
from ..domain.evaluation import (
    EvaluationObservation,
    EvaluatorKind,
    build_automated_observation,
    is_successful_runtime_state,
)
from ..domain.freshness import FreshnessOutcome, classify_freshness_answer
from ..domain.identity import ComponentKey
from ..domain.retrieval_case import (
    GroundingOutcome,
    NoHitStrategy,
    RetrievalMode,
    classify_grounding,
    expected_call_count_for_no_hit_strategy,
)
from ..domain.run import VariantRun
from ..domain.semantic_evidence import CaseSemanticEvidence
from .comparison_service import runtime_state_for_run

_PROVIDER_IDENTITY = "metric.deterministic-v1"

_FRESHNESS_OUTCOME_TO_OBSERVATION: dict[FreshnessOutcome, ObservationOutcome] = {
    FreshnessOutcome.CURRENT_FACT_USED: ObservationOutcome.PASS,
    FreshnessOutcome.STALE_FACT_REPEATED: ObservationOutcome.FAIL,
    FreshnessOutcome.HISTORICAL_CITATION_ALTERED: ObservationOutcome.FAIL,
    FreshnessOutcome.INSUFFICIENT_EVIDENCE: ObservationOutcome.INCONCLUSIVE,
}


def _semantic_evidence(
    raw_evidence: dict[str, object] | None, case: EvaluationCaseManifest
) -> CaseSemanticEvidence | None:
    payload = raw_evidence.get("semantic_evidence") if raw_evidence is not None else None
    if not isinstance(payload, dict):
        return None
    evidence = CaseSemanticEvidence.model_validate(payload)
    if evidence.case_id != case.case_id or evidence.case_revision != case.revision:
        return None
    return evidence


def _main_call_count(invocations: list[object]) -> int | None:
    """`None` means "MAIN's own Call status is not confirmed" -- either
    its Invocation Record was never observed at all (no Raw Evidence, or
    an Evidence shape from before this Round), or (R3-WU-02, tri-state
    Evidence) it WAS observed but `called=None` (this Round's Evidence
    source genuinely cannot tell). Both are honestly "unknown", distinct
    from `0`, a genuine CONFIRMED Main-Call-Zero (`called=False`)."""

    count = 0
    saw_main = False
    for item in invocations:
        if not isinstance(item, dict):
            continue
        if item.get("component_key") == ComponentKey.MAIN.value:
            saw_main = True
            called = item.get("called")
            if called is None:
                return None
            if called:
                count += 1
    return count if saw_main else None


def evaluate_case_outcome(
    *,
    case: EvaluationCaseManifest,
    run: VariantRun,
    raw_evidence: dict[str, object] | None,
) -> EvaluationObservation:
    """The one Deterministic Evaluator every `execution_mode` and every
    `case_id` in `case_pack.build_case_pack()` goes through -- computed
    fresh from `(case, run, raw_evidence)` every time, never persisted
    separately from the `EvaluationObservation` it returns (there is
    nothing else to keep in sync)."""

    def _observation(outcome: ObservationOutcome, reason: str) -> EvaluationObservation:
        return build_automated_observation(
            run_id=run.run_id,
            case_id=case.case_id,
            evaluator_kind=EvaluatorKind.DETERMINISTIC,
            provider_identity=_PROVIDER_IDENTITY,
            rubric_revision=case.revision,
            outcome=outcome,
            reason=reason,
        )

    if not is_successful_runtime_state(runtime_state_for_run(run)):
        return _observation(ObservationOutcome.NOT_RUN, "run_not_completed")
    semantic = _semantic_evidence(raw_evidence, case)
    if case.requires_human_review:
        # WU-B B3 / R1-WU-04 (unchanged by R2): Human Review absence is
        # never silently upgraded to an automated PASS.
        return _observation(ObservationOutcome.NOT_RUN, "human_review_pending")

    if case.evaluator_route is SemanticEvaluatorRoute.FRESHNESS:
        freshness_case = FRESHNESS_CASES_BY_ID.get(case.case_id)
        if freshness_case is None or semantic is None:
            return _observation(ObservationOutcome.UNAVAILABLE, "freshness_evidence_not_observed")
        assistant_content = semantic.assistant_content
        if not isinstance(assistant_content, str) or not assistant_content:
            return _observation(ObservationOutcome.UNAVAILABLE, "assistant_content_not_observed")
        historical_digest = semantic.historical_turn_citation_digest_after_answer
        if historical_digest is None:
            return _observation(
                ObservationOutcome.UNAVAILABLE,
                "historical_citation_digest_not_observed",
            )
        freshness_outcome = classify_freshness_answer(
            case=freshness_case,
            new_turn_answer=assistant_content,
            historical_turn_citation_digest_after_answer=historical_digest,
            current_value_adopted=semantic.answer_adopts_current_value,
        )
        return _observation(
            _FRESHNESS_OUTCOME_TO_OBSERVATION[freshness_outcome], freshness_outcome.value
        )

    if case.evaluator_route is SemanticEvaluatorRoute.RETRIEVAL:
        retrieval_case = RETRIEVAL_CASES_BY_ID.get(case.case_id)
        if retrieval_case is None or semantic is None:
            return _observation(ObservationOutcome.UNAVAILABLE, "retrieval_evidence_not_observed")
        if semantic.assistant_content is None or semantic.answer_claims_citation is None:
            return _observation(ObservationOutcome.UNAVAILABLE, "grounding_signal_not_observed")
        invocations_raw = raw_evidence.get("invocations") if raw_evidence is not None else None
        invocations = invocations_raw if isinstance(invocations_raw, list) else []
        main_calls = _main_call_count(invocations)
        if retrieval_case.retrieval_mode is RetrievalMode.NO_HIT:
            if main_calls is None:
                return _observation(
                    ObservationOutcome.UNAVAILABLE,
                    "main_call_count_not_observed",
                )
            expected = expected_call_count_for_no_hit_strategy(
                retrieval_case.no_hit_strategy or NoHitStrategy.MODEL_CALL_WITH_GOVERNANCE
            )
            if expected is not None and main_calls != expected:
                return _observation(
                    ObservationOutcome.FAIL,
                    "strict_no_hit_violated_model_called",
                )
            if (
                retrieval_case.no_hit_strategy is NoHitStrategy.MODEL_CALL_WITH_GOVERNANCE
                and main_calls == 0
            ):
                return _observation(
                    ObservationOutcome.FAIL,
                    "no_hit_governed_model_call_not_observed",
                )
        grounding_outcome = classify_grounding(
            case=retrieval_case,
            answer=semantic.assistant_content,
            answer_claims_citation=semantic.answer_claims_citation,
        )
        if grounding_outcome is GroundingOutcome.HONEST_GROUNDED:
            outcome = ObservationOutcome.PASS
        elif grounding_outcome is GroundingOutcome.FALSE_GROUNDING:
            outcome = ObservationOutcome.FAIL
        elif grounding_outcome is GroundingOutcome.HONEST_INSUFFICIENT_EVIDENCE:
            outcome = (
                ObservationOutcome.PASS
                if retrieval_case.retrieval_mode
                in (RetrievalMode.IRRELEVANT_HIT, RetrievalMode.NO_HIT)
                else ObservationOutcome.INCONCLUSIVE
            )
        else:
            outcome = ObservationOutcome.INCONCLUSIVE
        return _observation(outcome, grounding_outcome.value)

    if case.evaluator_route is SemanticEvaluatorRoute.BELIEF_REVISION:
        if semantic is None or semantic.belief_revision is None:
            return _observation(ObservationOutcome.UNAVAILABLE, "belief_revision_not_observed")
        belief = semantic.belief_revision
        if belief.case_id != case.case_id:
            return _observation(ObservationOutcome.UNAVAILABLE, "belief_case_identity_mismatch")
        revision_outcome = classify_belief_revision(belief)
        outcome = (
            ObservationOutcome.PASS
            if revision_outcome is BeliefRevisionOutcome.CORRECTION_ACCEPTED
            else ObservationOutcome.FAIL
        )
        return _observation(outcome, revision_outcome.value)

    if case.evaluator_route is SemanticEvaluatorRoute.COMPOSITION_MATRIX:
        if semantic is None:
            return _observation(ObservationOutcome.UNAVAILABLE, "composition_evidence_not_observed")
        return _observation(
            ObservationOutcome.INCONCLUSIVE,
            "structural_comparison_evidence_recorded",
        )

    return _observation(ObservationOutcome.INCONCLUSIVE, "no_deterministic_evaluator_for_case")
