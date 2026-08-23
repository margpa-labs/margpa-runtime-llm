"""Repair Orchestrator (Architecture 7.1/7.2/8, Phase 6-E-WU-003).

Scope note: this drives the New Attempt -> Rejudge -> Accept/Reject cycle
purely in terms of the Repair/Evaluation domains already implemented. It
does NOT yet re-run the real Phase 4/5 Governance/Guardrail Points
(Acceptance P6-ACC-029 "Repair Candidate passes all Phase 4/5 Points again") — that
requires wiring into the actual ConversationGenerationService pre/post
hooks, which is a separate, higher-risk production-integration step
deferred to when this Orchestrator is actually connected to the real
generation flow.
"""

from margpa_runtime_llm.modules.evaluation.application.evaluation_orchestrator import (
    EvaluationOrchestrator,
)
from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.identifiers import EvaluationRecommendation
from margpa_runtime_llm.modules.evaluation.domain.run import EvaluationRun

from ..domain.identifiers import RepairState
from ..domain.plan import RepairAttempt, RepairPlan
from ..domain.result import RepairResult
from ..domain.state_machine import validate_repair_transition
from ..ports import RepairAttemptGeneratorPort
from .repair_success_evaluator import evaluate_repair_success, repair_should_be_accepted


def execute_repair_plan(
    *,
    plan: RepairPlan,
    attempt: RepairAttempt,
    structured_feedback: str,
    case: EvaluationCase,
    before_evaluation_run_ref: str,
    before_recommendation: EvaluationRecommendation,
    generator: RepairAttemptGeneratorPort,
    evaluator: EvaluationOrchestrator,
    rejudge_run: EvaluationRun,
) -> tuple[RepairResult, str]:
    """Returns (RepairResult, new_candidate_answer). Raises RepairIllegalTransition on misuse."""
    validate_repair_transition(current_state=plan.state, requested_state=RepairState.AUTHORIZED)
    validate_repair_transition(
        current_state=RepairState.AUTHORIZED, requested_state=RepairState.GENERATING_REPAIR
    )

    new_candidate_answer = generator.generate_repair_attempt(
        plan=plan, structured_feedback=structured_feedback
    )

    validate_repair_transition(
        current_state=RepairState.GENERATING_REPAIR, requested_state=RepairState.REJUDGING
    )
    after_result = evaluator.run(run=rejudge_run, case=case, candidate_answer=new_candidate_answer)
    after_recommendation = (
        after_result.recommendation
        if after_result is not None
        else EvaluationRecommendation.UNKNOWN
    )

    outcome = evaluate_repair_success(
        before_recommendation=before_recommendation, after_recommendation=after_recommendation
    )
    accepted = repair_should_be_accepted(outcome=outcome)
    final_state = RepairState.ACCEPTED if accepted else RepairState.REJECTED
    validate_repair_transition(current_state=RepairState.REJUDGING, requested_state=final_state)

    result = RepairResult(
        repair_plan_id=plan.repair_plan_id,
        attempt_id=attempt.attempt_id,
        before_evaluation_run_ref=before_evaluation_run_ref,
        after_evaluation_run_ref=rejudge_run.run_id,
        outcome=outcome,
        accepted=accepted,
        presented_answer_is_repair=accepted,
    )
    return result, new_candidate_answer
