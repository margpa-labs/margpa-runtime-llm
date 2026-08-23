"""Repair Eligibility/Authority Resolver (Phase 6-E-WU-002, Architecture 7.2).

Repair Eligibility never overrides a Guardrail/Authority Deny (Governance's
"Safety Deny non-release"): a Deny always short-circuits to NOT_ELIGIBLE,
regardless of Mode, Judge Recommendation, or remaining Budget.
"""

from enum import StrEnum

from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationRecommendation

from ..domain.budget import RepairBudget, RepairBudgetUsage
from ..domain.errors import RepairBudgetExhausted
from ..domain.identifiers import RepairMode
from ..domain.state_machine import check_repair_budget


class RepairEligibility(StrEnum):
    ELIGIBLE = "eligible"
    NOT_ELIGIBLE_MODE_OFF = "not_eligible_mode_off"
    NOT_ELIGIBLE_GUARDRAIL_DENY = "not_eligible_guardrail_deny"
    NOT_ELIGIBLE_NO_REPAIR_RECOMMENDATION = "not_eligible_no_repair_recommendation"
    NOT_ELIGIBLE_BUDGET_EXHAUSTED = "not_eligible_budget_exhausted"


def resolve_repair_eligibility(
    *,
    mode: RepairMode,
    guardrail_denied: bool,
    judge_recommendation: EvaluationRecommendation,
    budget: RepairBudget,
    usage: RepairBudgetUsage,
) -> RepairEligibility:
    if guardrail_denied:
        return RepairEligibility.NOT_ELIGIBLE_GUARDRAIL_DENY
    if mode is RepairMode.OFF:
        return RepairEligibility.NOT_ELIGIBLE_MODE_OFF
    if judge_recommendation is not EvaluationRecommendation.NEEDS_REPAIR:
        return RepairEligibility.NOT_ELIGIBLE_NO_REPAIR_RECOMMENDATION
    try:
        check_repair_budget(budget=budget, usage=usage)
    except RepairBudgetExhausted:
        return RepairEligibility.NOT_ELIGIBLE_BUDGET_EXHAUSTED
    return RepairEligibility.ELIGIBLE
