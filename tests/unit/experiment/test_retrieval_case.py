"""Phase 9-2 WU-D D2: RAG Grounding / Strict NO_HIT classification."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.experiment.domain.retrieval_case import (
    GroundingOutcome,
    NoHitStrategy,
    RetrievalCase,
    RetrievalMode,
    classify_grounding,
    expected_call_count_for_no_hit_strategy,
)


def test_rag_off_is_always_ungrounded_model_knowledge_even_with_a_claimed_citation() -> None:
    case = RetrievalCase(case_id="c1", retrieval_mode=RetrievalMode.RAG_OFF)
    outcome = classify_grounding(
        case=case, answer="Per my training data...", answer_claims_citation=True
    )
    assert outcome is GroundingOutcome.UNGROUNDED_MODEL_KNOWLEDGE


def test_relevant_hit_cited_correctly_is_honest_grounded() -> None:
    case = RetrievalCase(
        case_id="c2", retrieval_mode=RetrievalMode.RELEVANT_HIT, relevant_source_value="on track"
    )
    outcome = classify_grounding(
        case=case, answer="The ALPHA project is on track.", answer_claims_citation=True
    )
    assert outcome is GroundingOutcome.HONEST_GROUNDED


def test_relevant_hit_not_actually_quoted_is_false_grounding() -> None:
    case = RetrievalCase(
        case_id="c3", retrieval_mode=RetrievalMode.RELEVANT_HIT, relevant_source_value="on track"
    )
    outcome = classify_grounding(
        case=case, answer="The ALPHA project is delayed.", answer_claims_citation=True
    )
    assert outcome is GroundingOutcome.FALSE_GROUNDING


def test_irrelevant_hit_cited_as_if_relevant_is_false_grounding() -> None:
    case = RetrievalCase(case_id="c4", retrieval_mode=RetrievalMode.IRRELEVANT_HIT)
    outcome = classify_grounding(
        case=case, answer="According to the retrieved document...", answer_claims_citation=True
    )
    assert outcome is GroundingOutcome.FALSE_GROUNDING


def test_irrelevant_hit_honestly_declined_is_honest_insufficient_evidence() -> None:
    case = RetrievalCase(case_id="c5", retrieval_mode=RetrievalMode.IRRELEVANT_HIT)
    outcome = classify_grounding(
        case=case,
        answer="The retrieved document does not address this.",
        answer_claims_citation=False,
    )
    assert outcome is GroundingOutcome.HONEST_INSUFFICIENT_EVIDENCE


def test_no_hit_with_a_fabricated_citation_is_false_grounding() -> None:
    case = RetrievalCase(
        case_id="c6",
        retrieval_mode=RetrievalMode.NO_HIT,
        no_hit_strategy=NoHitStrategy.MODEL_CALL_WITH_GOVERNANCE,
    )
    outcome = classify_grounding(
        case=case, answer="Per the source document...", answer_claims_citation=True
    )
    assert outcome is GroundingOutcome.FALSE_GROUNDING


def test_no_hit_case_requires_a_no_hit_strategy() -> None:
    with pytest.raises(ValidationError):
        RetrievalCase(case_id="c7", retrieval_mode=RetrievalMode.NO_HIT)


def test_non_no_hit_case_rejects_a_no_hit_strategy() -> None:
    with pytest.raises(ValidationError):
        RetrievalCase(
            case_id="c8",
            retrieval_mode=RetrievalMode.RAG_OFF,
            no_hit_strategy=NoHitStrategy.STRICT_NO_HIT_MODEL_CALL_ZERO,
        )


def test_expected_call_count_is_exactly_zero_for_strict_no_hit_and_unfixed_otherwise() -> None:
    assert expected_call_count_for_no_hit_strategy(NoHitStrategy.STRICT_NO_HIT_MODEL_CALL_ZERO) == 0
    assert expected_call_count_for_no_hit_strategy(NoHitStrategy.MODEL_CALL_WITH_GOVERNANCE) is None
