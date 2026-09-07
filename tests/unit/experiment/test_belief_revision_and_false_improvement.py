"""Phase 9-2 WU-D D3/D4: Belief Revision and Runtime-vs-Human Semantic Success."""

from __future__ import annotations

from margpa_runtime_llm.modules.experiment.domain.belief_revision import (
    BeliefRevisionObservation,
    BeliefRevisionOutcome,
    classify_belief_revision,
)
from margpa_runtime_llm.modules.experiment.domain.dataset import ObservationOutcome
from margpa_runtime_llm.modules.experiment.domain.false_improvement import (
    RepairSemanticOutcome,
    classify_repair_semantic_outcome,
)


def test_no_user_correction_needs_no_revision() -> None:
    observation = BeliefRevisionObservation(
        case_id="c1", historical_claim="000", final_claim="000"
    )
    assert classify_belief_revision(observation) is BeliefRevisionOutcome.NO_CORRECTION_NEEDED


def test_final_claim_matching_the_correction_is_accepted() -> None:
    observation = BeliefRevisionObservation(
        case_id="c2",
        historical_claim="ALPHA-15 confirmed value: 000",
        user_correction="765",
        final_claim="ALPHA-15 confirmed value: 765",
    )
    assert classify_belief_revision(observation) is BeliefRevisionOutcome.CORRECTION_ACCEPTED


def test_final_claim_still_matching_the_historical_claim_is_ignored() -> None:
    observation = BeliefRevisionObservation(
        case_id="c3",
        historical_claim="ALPHA-15 confirmed value: 000",
        user_correction="765",
        final_claim="ALPHA-15 confirmed value: 000",
    )
    assert classify_belief_revision(observation) is BeliefRevisionOutcome.CORRECTION_IGNORED


def test_final_claim_matching_neither_is_overcorrected() -> None:
    observation = BeliefRevisionObservation(
        case_id="c4",
        historical_claim="ALPHA-15 confirmed value: 000",
        user_correction="765",
        final_claim="ALPHA-15 confirmed value: 999",
    )
    assert classify_belief_revision(observation) is BeliefRevisionOutcome.OVERCORRECTED


def test_runtime_accepted_and_human_pass_is_genuine_improvement() -> None:
    outcome = classify_repair_semantic_outcome(
        runtime_repair_accepted=True, human_outcome=ObservationOutcome.PASS
    )
    assert outcome is RepairSemanticOutcome.GENUINE_IMPROVEMENT


def test_runtime_accepted_but_human_fail_is_false_improvement() -> None:
    """Reproduces Phase 9-1's UF-P9-013 as a neutral, comparable Case
    shape: the mechanical Repair path succeeded, but a real Human Review
    Observation says it is semantically wrong."""
    outcome = classify_repair_semantic_outcome(
        runtime_repair_accepted=True, human_outcome=ObservationOutcome.FAIL
    )
    assert outcome is RepairSemanticOutcome.FALSE_IMPROVEMENT


def test_runtime_not_accepted_and_human_pass_is_genuine_no_change() -> None:
    outcome = classify_repair_semantic_outcome(
        runtime_repair_accepted=False, human_outcome=ObservationOutcome.PASS
    )
    assert outcome is RepairSemanticOutcome.GENUINE_NO_CHANGE


def test_runtime_not_accepted_and_human_fail_is_genuine_worse() -> None:
    outcome = classify_repair_semantic_outcome(
        runtime_repair_accepted=False, human_outcome=ObservationOutcome.FAIL
    )
    assert outcome is RepairSemanticOutcome.GENUINE_WORSE


def test_missing_human_review_is_unknown_never_silently_treated_as_pass() -> None:
    for accepted in (True, False):
        outcome = classify_repair_semantic_outcome(
            runtime_repair_accepted=accepted, human_outcome=ObservationOutcome.NOT_RUN
        )
        assert outcome is RepairSemanticOutcome.UNKNOWN
