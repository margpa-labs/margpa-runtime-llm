from margpa_runtime_llm.adapters.evaluation.deterministic.evaluators import (
    ContradictionMarkerEvaluator,
    ExactReferenceMatchEvaluator,
    FormatComplianceEvaluator,
    RequiredFieldPresenceEvaluator,
    UnsupportedClaimCandidateEvaluator,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationMode,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.evaluation.ports import DeterministicEvaluatorPort

from .conftest import make_case, make_run

_RUN = make_run(mode=EvaluationMode.ENFORCE)


def test_exact_reference_match_accepts_a_correct_answer() -> None:
    evaluator = ExactReferenceMatchEvaluator()
    result = evaluator.evaluate(run=_RUN, case=make_case(), candidate_answer="The answer is Paris.")
    assert result.recommendation is EvaluationRecommendation.ACCEPT
    assert result.call_count == 0


def test_exact_reference_match_flags_a_wrong_answer() -> None:
    evaluator = ExactReferenceMatchEvaluator()
    result = evaluator.evaluate(run=_RUN, case=make_case(), candidate_answer="The answer is Lyon.")
    assert result.recommendation is EvaluationRecommendation.NEEDS_REPAIR


def test_exact_reference_match_is_unknown_without_a_reference() -> None:
    case = make_case().model_copy(update={"reference": None})
    evaluator = ExactReferenceMatchEvaluator()
    result = evaluator.evaluate(run=_RUN, case=case, candidate_answer="anything")
    assert result.recommendation is EvaluationRecommendation.UNKNOWN
    assert result.execution_state is EvaluationExecutionState.COMPLETED
    assert result.failure_reason is not None


def test_required_field_presence_detects_missing_fields() -> None:
    evaluator = RequiredFieldPresenceEvaluator(required_substrings=("capital", "France"))
    result = evaluator.evaluate(run=_RUN, case=make_case(), candidate_answer="Paris is a city.")
    assert result.recommendation is EvaluationRecommendation.NEEDS_REPAIR
    assert set(result.contradictions) == {"capital", "France"}


def test_required_field_presence_passes_when_all_fields_present() -> None:
    evaluator = RequiredFieldPresenceEvaluator(required_substrings=("Paris",))
    result = evaluator.evaluate(
        run=_RUN, case=make_case(), candidate_answer="The capital is Paris."
    )
    assert result.recommendation is EvaluationRecommendation.ACCEPT


def test_contradiction_marker_flags_a_declared_marker_phrase() -> None:
    evaluator = ContradictionMarkerEvaluator(contradiction_markers=("is not the capital",))
    result = evaluator.evaluate(
        run=_RUN, case=make_case(), candidate_answer="Paris is not the capital of France."
    )
    assert result.recommendation is EvaluationRecommendation.NEEDS_REPAIR
    assert result.contradictions == ("is not the capital",)


def test_unsupported_claim_candidate_flags_an_absolute_claim_not_in_reference() -> None:
    evaluator = UnsupportedClaimCandidateEvaluator(absolute_claim_markers=("always", "never"))
    result = evaluator.evaluate(
        run=_RUN, case=make_case(), candidate_answer="Paris has always been the capital."
    )
    assert result.unsupported_claims == ("always",)
    assert result.recommendation is EvaluationRecommendation.NEEDS_REPAIR


def test_unsupported_claim_candidate_allows_a_marker_that_is_also_in_the_reference() -> None:
    case = make_case().model_copy(update={"reference": "Paris always has been the capital"})
    evaluator = UnsupportedClaimCandidateEvaluator(absolute_claim_markers=("always",))
    result = evaluator.evaluate(
        run=_RUN, case=case, candidate_answer="Paris has always been the capital."
    )
    assert result.unsupported_claims == ()
    assert result.recommendation is EvaluationRecommendation.ACCEPT


def test_format_compliance_checks_a_declared_regex() -> None:
    evaluator = FormatComplianceEvaluator(pattern=r"^Answer: .+$")
    passing = evaluator.evaluate(run=_RUN, case=make_case(), candidate_answer="Answer: Paris")
    failing = evaluator.evaluate(run=_RUN, case=make_case(), candidate_answer="Paris")
    assert passing.recommendation is EvaluationRecommendation.ACCEPT
    assert failing.recommendation is EvaluationRecommendation.NEEDS_REPAIR


def test_no_deterministic_evaluator_reports_any_model_call() -> None:
    evaluators: list[DeterministicEvaluatorPort] = [
        ExactReferenceMatchEvaluator(),
        RequiredFieldPresenceEvaluator(required_substrings=("Paris",)),
        ContradictionMarkerEvaluator(contradiction_markers=("never",)),
        UnsupportedClaimCandidateEvaluator(absolute_claim_markers=("always",)),
        FormatComplianceEvaluator(pattern=r".+"),
    ]
    for evaluator in evaluators:
        result = evaluator.evaluate(run=_RUN, case=make_case(), candidate_answer="Paris")
        assert result.call_count == 0
        assert result.token_usage == 0
