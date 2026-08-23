"""Judge Failure/Cost Gate (Phase 6-D-WU-006).

Applies EvaluationBudget limits *after* a successful decode: a syntactically
well-formed Judge response that exceeds the caller's declared budget is
still not an Accepted result, it is a Cost-Limit failure. Unavailable,
Timeout, Context Overflow, Cancel, and Model Switch Conflict are represented
directly by JudgeFailureReason at the call site (the Port implementation),
not re-derived here.
"""

from ..domain.identifiers import EvaluationExecutionState, EvaluationRecommendation
from ..domain.llm_judge import JudgeFailureReason, LlmJudgeResponse
from ..domain.run import EvaluationBudget


def apply_judge_budget_gate(
    *, budget: EvaluationBudget, response: LlmJudgeResponse
) -> LlmJudgeResponse:
    if response.execution_state is not EvaluationExecutionState.COMPLETED:
        return response
    if response.token_usage > budget.max_tokens:
        return response.model_copy(
            update={
                "recommendation": EvaluationRecommendation.UNKNOWN,
                "execution_state": EvaluationExecutionState.FAILED,
                "failure_reason": JudgeFailureReason.COST_LIMIT_EXCEEDED,
            }
        )
    if response.latency_ms > budget.max_wall_time_ms:
        return response.model_copy(
            update={
                "recommendation": EvaluationRecommendation.UNKNOWN,
                "execution_state": EvaluationExecutionState.FAILED,
                "failure_reason": JudgeFailureReason.TIMEOUT,
            }
        )
    return response
