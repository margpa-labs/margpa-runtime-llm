"""Semantic Research Case Pack (Phase 9-2, WU-D).

The six scenario categories from Handoff §8, each expressed as a
neutral-named (`ALPHA`/`BETA`-prefixed, never a real specific person's
name) `EvaluationCaseManifest` plus the companion domain-specific Case
object (`FreshnessCase`/`RetrievalCase`/`BeliefRevisionObservation`) a
Variant Run can be checked against. `build_case_pack()` returns the
whole Pack as one frozen tuple, revision-pinned via each Case's own
`revision` field -- callers needing a `case_revision` for an
`ExperimentPlan` use this Pack's own fixed revision string, never a
wall-clock timestamp."""

from __future__ import annotations

from .belief_revision import BeliefRevisionObservation
from .dataset import EvaluationCaseManifest, ObservationOutcome, SemanticEvaluatorRoute
from .freshness import FreshnessCase, SourceRevisionState
from .retrieval_case import NoHitStrategy, RetrievalCase, RetrievalMode

CASE_PACK_REVISION = "phase-9-2-semantic-research-case-pack-rev-3"

# D1 -- Historical Claim vs. Current Source Revision.
FRESHNESS_HISTORICAL_VS_CURRENT = FreshnessCase(
    case_id="case-freshness-alpha-15",
    historical_claim="ALPHA-15 confirmed value: 000",
    historical_citation_digest_sha512="0" * 128,
    source_revision_state=SourceRevisionState.CURRENT,
    current_source_value="000",
)

# D1 -- Source updated/deleted after the historical Turn; a new Turn
# asking for the Current Fact must prefer Current Source.
FRESHNESS_SOURCE_UPDATED = FreshnessCase(
    case_id="case-freshness-alpha-15-updated",
    historical_claim="ALPHA-15 confirmed value: 000",
    historical_citation_digest_sha512="0" * 128,
    source_revision_state=SourceRevisionState.UPDATED,
    current_source_value="765",
)

FRESHNESS_SOURCE_DELETED = FreshnessCase(
    case_id="case-freshness-alpha-15-deleted",
    historical_claim="ALPHA-15 confirmed value: 000",
    historical_citation_digest_sha512="0" * 128,
    source_revision_state=SourceRevisionState.DELETED,
    current_source_value=None,
)

# D2 -- RAG OFF / Relevant Hit / Irrelevant Hit / NO_HIT.
RETRIEVAL_RAG_OFF = RetrievalCase(
    case_id="case-retrieval-rag-off", retrieval_mode=RetrievalMode.RAG_OFF
)
RETRIEVAL_RELEVANT_HIT = RetrievalCase(
    case_id="case-retrieval-relevant-hit",
    retrieval_mode=RetrievalMode.RELEVANT_HIT,
    relevant_source_value="ALPHA-22 project status: on track",
)
RETRIEVAL_IRRELEVANT_HIT = RetrievalCase(
    case_id="case-retrieval-irrelevant-hit", retrieval_mode=RetrievalMode.IRRELEVANT_HIT
)
RETRIEVAL_NO_HIT_MODEL_CALL = RetrievalCase(
    case_id="case-retrieval-no-hit-model-call",
    retrieval_mode=RetrievalMode.NO_HIT,
    no_hit_strategy=NoHitStrategy.MODEL_CALL_WITH_GOVERNANCE,
)
RETRIEVAL_STRICT_NO_HIT = RetrievalCase(
    case_id="case-retrieval-strict-no-hit",
    retrieval_mode=RetrievalMode.NO_HIT,
    no_hit_strategy=NoHitStrategy.STRICT_NO_HIT_MODEL_CALL_ZERO,
)

# D3 -- Source Authority/Provenance/User Correction/Belief Revision.
BELIEF_REVISION_CORRECTION = BeliefRevisionObservation(
    case_id="case-belief-revision-alpha-15",
    historical_claim="ALPHA-15 confirmed value: 000",
    current_source="ALPHA-15 confirmed value: 765",
    user_correction="765",
    final_claim="ALPHA-15 confirmed value: 765",
)

# D4 -- Runtime Repair success but Human Semantic Failure (False
# Improvement, reproducing UF-P9-013 as a neutral Case).
FALSE_IMPROVEMENT_CASE = EvaluationCaseManifest(
    case_id="case-false-improvement-beta-01",
    revision=CASE_PACK_REVISION,
    input="What is the correct reading of BETA-01?",
    expected_observations=("runtime_repair_accepted", "human_semantic_pass"),
    acceptable_outcomes=(ObservationOutcome.PASS,),
    requires_human_review=True,
    evaluator_route=SemanticEvaluatorRoute.FALSE_IMPROVEMENT,
)

COMPOSITION_MATRIX_CASE = EvaluationCaseManifest(
    case_id="case-composition-matrix-alpha-01",
    revision=CASE_PACK_REVISION,
    input="Execute the declared deterministic governance composition for ALPHA-01.",
    expected_observations=(
        "component_invocation",
        "definition_routing",
        "presentation_state",
        "call_zero_trace",
    ),
    acceptable_outcomes=(ObservationOutcome.INCONCLUSIVE,),
    evaluator_route=SemanticEvaluatorRoute.COMPOSITION_MATRIX,
)


FRESHNESS_CASES_BY_ID: dict[str, FreshnessCase] = {
    case.case_id: case
    for case in (
        FRESHNESS_HISTORICAL_VS_CURRENT,
        FRESHNESS_SOURCE_UPDATED,
        FRESHNESS_SOURCE_DELETED,
    )
}

RETRIEVAL_CASES_BY_ID: dict[str, RetrievalCase] = {
    case.case_id: case
    for case in (
        RETRIEVAL_RAG_OFF,
        RETRIEVAL_RELEVANT_HIT,
        RETRIEVAL_IRRELEVANT_HIT,
        RETRIEVAL_NO_HIT_MODEL_CALL,
        RETRIEVAL_STRICT_NO_HIT,
    )
}


def build_case_pack() -> tuple[EvaluationCaseManifest, ...]:
    """WU-D: the Case Manifests suitable for direct use as
    `ExperimentPlan.case_revision`-scoped `EvaluationCaseManifest`
    entries. Every required semantic scenario has its own Manifest and
    explicit evaluator route; the richer category-specific objects above
    remain the Adapter inputs for that Manifest."""

    return (
        EvaluationCaseManifest(
            case_id=FRESHNESS_HISTORICAL_VS_CURRENT.case_id,
            revision=CASE_PACK_REVISION,
            input="What is the current confirmed value of ALPHA-15?",
            expected_observations=("current_fact_used",),
            evaluator_route=SemanticEvaluatorRoute.FRESHNESS,
        ),
        EvaluationCaseManifest(
            case_id=FRESHNESS_SOURCE_UPDATED.case_id,
            revision=CASE_PACK_REVISION,
            input="What is the updated confirmed value of ALPHA-15?",
            expected_observations=("current_fact_used", "historical_citation_unchanged"),
            evaluator_route=SemanticEvaluatorRoute.FRESHNESS,
        ),
        EvaluationCaseManifest(
            case_id=FRESHNESS_SOURCE_DELETED.case_id,
            revision=CASE_PACK_REVISION,
            input="What current evidence remains for ALPHA-15?",
            expected_observations=("insufficient_evidence", "historical_citation_unchanged"),
            acceptable_outcomes=(ObservationOutcome.INCONCLUSIVE,),
            evaluator_route=SemanticEvaluatorRoute.FRESHNESS,
        ),
        EvaluationCaseManifest(
            case_id=RETRIEVAL_RAG_OFF.case_id,
            revision=CASE_PACK_REVISION,
            input="Answer ALPHA-22 without retrieval.",
            expected_observations=("ungrounded_model_knowledge",),
            acceptable_outcomes=(ObservationOutcome.INCONCLUSIVE,),
            evaluator_route=SemanticEvaluatorRoute.RETRIEVAL,
        ),
        EvaluationCaseManifest(
            case_id=RETRIEVAL_RELEVANT_HIT.case_id,
            revision=CASE_PACK_REVISION,
            input="Use the relevant source to report ALPHA-22 status.",
            expected_observations=("honest_grounded",),
            evaluator_route=SemanticEvaluatorRoute.RETRIEVAL,
        ),
        EvaluationCaseManifest(
            case_id=RETRIEVAL_IRRELEVANT_HIT.case_id,
            revision=CASE_PACK_REVISION,
            input="Report ALPHA-22 status when only an irrelevant hit was returned.",
            expected_observations=("false_grounding",),
            acceptable_outcomes=(ObservationOutcome.FAIL,),
            evaluator_route=SemanticEvaluatorRoute.RETRIEVAL,
        ),
        EvaluationCaseManifest(
            case_id=RETRIEVAL_NO_HIT_MODEL_CALL.case_id,
            revision=CASE_PACK_REVISION,
            input="Report ALPHA-22 status after NO_HIT with governed Model fallback.",
            expected_observations=("honest_insufficient_evidence", "model_call_observed"),
            evaluator_route=SemanticEvaluatorRoute.RETRIEVAL,
        ),
        EvaluationCaseManifest(
            case_id=RETRIEVAL_STRICT_NO_HIT.case_id,
            revision=CASE_PACK_REVISION,
            input="What is GAMMA-99's confirmed value?",
            expected_observations=("honest_insufficient_evidence", "model_call_zero"),
            evaluator_route=SemanticEvaluatorRoute.RETRIEVAL,
        ),
        EvaluationCaseManifest(
            case_id=BELIEF_REVISION_CORRECTION.case_id,
            revision=CASE_PACK_REVISION,
            input="Reconcile the corrected ALPHA-15 value with the historical claim.",
            expected_observations=("correction_accepted",),
            evaluator_route=SemanticEvaluatorRoute.BELIEF_REVISION,
        ),
        FALSE_IMPROVEMENT_CASE,
        COMPOSITION_MATRIX_CASE,
    )
