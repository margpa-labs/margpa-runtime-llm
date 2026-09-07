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
from .dataset import EvaluationCaseManifest, ObservationOutcome
from .freshness import FreshnessCase, SourceRevisionState
from .retrieval_case import NoHitStrategy, RetrievalCase, RetrievalMode

CASE_PACK_REVISION = "phase-9-2-semantic-research-case-pack-rev-1"

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
)


def build_case_pack() -> tuple[EvaluationCaseManifest, ...]:
    """WU-D: the Case Manifests suitable for direct use as
    `ExperimentPlan.case_revision`-scoped `EvaluationCaseManifest`
    entries. The Freshness/Retrieval/Belief-Revision domain objects
    above are the richer, category-specific Fixtures a Variant Actor
    checks its own output against -- they are not `EvaluationCaseManifest`
    instances themselves (their shape is different per category), so
    this function only returns the generic-Manifest-shaped subset."""

    return (
        EvaluationCaseManifest(
            case_id="case-freshness-alpha-15",
            revision=CASE_PACK_REVISION,
            input="What is the current confirmed value of ALPHA-15?",
            expected_observations=("current_fact_used",),
        ),
        EvaluationCaseManifest(
            case_id="case-retrieval-strict-no-hit",
            revision=CASE_PACK_REVISION,
            input="What is GAMMA-99's confirmed value?",
            expected_observations=("honest_insufficient_evidence", "model_call_zero"),
        ),
        FALSE_IMPROVEMENT_CASE,
    )
