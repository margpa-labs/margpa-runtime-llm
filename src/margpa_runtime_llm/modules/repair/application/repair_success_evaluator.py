"""Before/After Success Evaluation (Phase 6-E-WU-005, Architecture 7.1/8).

Worse/Unknown/Failure are never coerced into Success (Execution Plan's
explicit prohibition): only a clean NEEDS_REPAIR -> ACCEPT transition, with
neither side UNKNOWN, is reported as IMPROVED and eligible for acceptance.
"""

from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationRecommendation

from ..domain.identifiers import RepairOutcome


def evaluate_repair_success(
    *,
    before_recommendation: EvaluationRecommendation,
    after_recommendation: EvaluationRecommendation,
) -> RepairOutcome:
    if (
        before_recommendation is EvaluationRecommendation.UNKNOWN
        or after_recommendation is EvaluationRecommendation.UNKNOWN
    ):
        return RepairOutcome.UNKNOWN
    if (
        before_recommendation is EvaluationRecommendation.NEEDS_REPAIR
        and after_recommendation is EvaluationRecommendation.ACCEPT
    ):
        return RepairOutcome.IMPROVED
    if (
        before_recommendation is EvaluationRecommendation.ACCEPT
        and after_recommendation is EvaluationRecommendation.NEEDS_REPAIR
    ):
        return RepairOutcome.WORSE
    return RepairOutcome.NO_CHANGE


def repair_should_be_accepted(*, outcome: RepairOutcome) -> bool:
    """Only IMPROVED may become the Presented Answer (Architecture 8)."""
    return outcome is RepairOutcome.IMPROVED
