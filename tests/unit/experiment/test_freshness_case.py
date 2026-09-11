"""Phase 9-2 WU-D D1: Freshness classification."""

from __future__ import annotations

from margpa_runtime_llm.modules.experiment.domain.freshness import (
    FreshnessCase,
    FreshnessOutcome,
    SourceRevisionState,
    classify_freshness_answer,
)

_DIGEST = "a" * 128


def _case(state: SourceRevisionState, current_value: str | None) -> FreshnessCase:
    return FreshnessCase(
        case_id="case-1",
        historical_claim="ALPHA-15 confirmed value: 000",
        historical_citation_digest_sha512=_DIGEST,
        source_revision_state=state,
        current_source_value=current_value,
    )


def test_current_source_state_counts_only_an_answer_using_the_current_value() -> None:
    case = _case(SourceRevisionState.CURRENT, "000")
    outcome = classify_freshness_answer(
        case=case,
        new_turn_answer="ALPHA-15 is 000.",
        historical_turn_citation_digest_after_answer=_DIGEST,
        current_value_adopted=True,
    )
    assert outcome is FreshnessOutcome.CURRENT_FACT_USED


def test_current_source_state_rejects_an_unrelated_or_empty_answer() -> None:
    case = _case(SourceRevisionState.CURRENT, "000")
    for answer in ("I am not sure.", ""):
        outcome = classify_freshness_answer(
            case=case,
            new_turn_answer=answer,
            historical_turn_citation_digest_after_answer=_DIGEST,
        )
        assert outcome is FreshnessOutcome.INSUFFICIENT_EVIDENCE


def test_current_source_value_mentioned_as_denial_or_quote_is_not_adopted() -> None:
    case = _case(SourceRevisionState.CURRENT, "000")
    for answer in (
        "000 is not the current value; 765 is current.",
        "The historical note quoted 000; it is not established as current.",
    ):
        outcome = classify_freshness_answer(
            case=case,
            new_turn_answer=answer,
            historical_turn_citation_digest_after_answer=_DIGEST,
        )
        assert outcome is FreshnessOutcome.INSUFFICIENT_EVIDENCE


def test_updated_source_using_the_new_value_is_current_fact_used() -> None:
    case = _case(SourceRevisionState.UPDATED, "765")
    outcome = classify_freshness_answer(
        case=case,
        new_turn_answer="ALPHA-15 is now 765.",
        historical_turn_citation_digest_after_answer=_DIGEST,
        current_value_adopted=True,
    )
    assert outcome is FreshnessOutcome.CURRENT_FACT_USED


def test_updated_source_repeating_the_old_value_is_stale_fact_repeated() -> None:
    case = _case(SourceRevisionState.UPDATED, "765")
    outcome = classify_freshness_answer(
        case=case,
        new_turn_answer="ALPHA-15 confirmed value: 000",
        historical_turn_citation_digest_after_answer=_DIGEST,
    )
    assert outcome is FreshnessOutcome.STALE_FACT_REPEATED


def test_deleted_source_with_neither_value_present_is_insufficient_evidence() -> None:
    case = _case(SourceRevisionState.DELETED, None)
    outcome = classify_freshness_answer(
        case=case,
        new_turn_answer="I do not have current evidence for ALPHA-15.",
        historical_turn_citation_digest_after_answer=_DIGEST,
    )
    assert outcome is FreshnessOutcome.INSUFFICIENT_EVIDENCE


def test_a_mutated_historical_citation_digest_is_always_the_worst_outcome() -> None:
    """Even when the new answer correctly uses Current Source, a changed
    PAST Turn citation digest must still be flagged -- Freshness Governance
    must never come at the cost of retroactively editing history."""
    case = _case(SourceRevisionState.UPDATED, "765")
    outcome = classify_freshness_answer(
        case=case,
        new_turn_answer="ALPHA-15 is now 765.",
        historical_turn_citation_digest_after_answer="b" * 128,
        current_value_adopted=True,
    )
    assert outcome is FreshnessOutcome.HISTORICAL_CITATION_ALTERED
