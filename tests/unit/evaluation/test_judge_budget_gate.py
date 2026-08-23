from margpa_runtime_llm.modules.evaluation.application.judge_budget_gate import (
    apply_judge_budget_gate,
)
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import (
    JudgeFailureReason,
    JudgeIndependenceClass,
    LlmJudgeResponse,
)
from margpa_runtime_llm.modules.evaluation.domain.run import EvaluationBudget

_BUDGET = EvaluationBudget(max_calls=1, max_tokens=500, max_wall_time_ms=5000)


def _completed_response(*, token_usage: int, latency_ms: int) -> LlmJudgeResponse:
    return LlmJudgeResponse(
        judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
        recommendation=EvaluationRecommendation.ACCEPT,
        confidence=0.9,
        token_usage=token_usage,
        latency_ms=latency_ms,
        execution_state=EvaluationExecutionState.COMPLETED,
    )


def test_within_budget_response_passes_through_unchanged() -> None:
    response = _completed_response(token_usage=100, latency_ms=1000)
    gated = apply_judge_budget_gate(budget=_BUDGET, response=response)
    assert gated == response


def test_exceeding_token_budget_downgrades_to_cost_limit_failure() -> None:
    response = _completed_response(token_usage=600, latency_ms=1000)
    gated = apply_judge_budget_gate(budget=_BUDGET, response=response)
    assert gated.execution_state is EvaluationExecutionState.FAILED
    assert gated.failure_reason is JudgeFailureReason.COST_LIMIT_EXCEEDED
    assert gated.recommendation is EvaluationRecommendation.UNKNOWN


def test_exceeding_wall_time_budget_downgrades_to_timeout() -> None:
    response = _completed_response(token_usage=100, latency_ms=9000)
    gated = apply_judge_budget_gate(budget=_BUDGET, response=response)
    assert gated.execution_state is EvaluationExecutionState.FAILED
    assert gated.failure_reason is JudgeFailureReason.TIMEOUT


def test_an_already_failed_response_is_not_reclassified_by_the_budget_gate() -> None:
    response = LlmJudgeResponse(
        judge_role=JudgeIndependenceClass.UNAVAILABLE,
        recommendation=EvaluationRecommendation.UNKNOWN,
        confidence=0.0,
        token_usage=0,
        latency_ms=0,
        execution_state=EvaluationExecutionState.FAILED,
        failure_reason=JudgeFailureReason.UNAVAILABLE,
    )
    gated = apply_judge_budget_gate(budget=_BUDGET, response=response)
    assert gated.failure_reason is JudgeFailureReason.UNAVAILABLE
