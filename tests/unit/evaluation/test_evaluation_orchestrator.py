from margpa_runtime_llm.modules.evaluation.application.evaluation_orchestrator import (
    EvaluationOrchestrator,
)
from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationMode,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.evaluation.domain.result import EvaluationResult
from margpa_runtime_llm.modules.evaluation.domain.run import EvaluationRun

from .conftest import make_case, make_run


class _RecordingEvaluator:
    def __init__(self) -> None:
        self.call_count = 0

    def evaluate(
        self, *, run: EvaluationRun, case: EvaluationCase, candidate_answer: str
    ) -> EvaluationResult:
        self.call_count += 1
        return EvaluationResult(
            run_id=run.run_id,
            confidence=1.0,
            recommendation=EvaluationRecommendation.ACCEPT,
            token_usage=0,
            latency_ms=1,
            call_count=1,
            execution_state=EvaluationExecutionState.COMPLETED,
        )


def test_off_mode_makes_zero_evaluator_calls() -> None:
    evaluator = _RecordingEvaluator()
    orchestrator = EvaluationOrchestrator(mode=EvaluationMode.OFF, evaluator=evaluator)

    result = orchestrator.run(
        run=make_run(mode=EvaluationMode.OFF), case=make_case(), candidate_answer="Paris"
    )

    assert result is None
    assert evaluator.call_count == 0


def test_observe_mode_evaluates_but_caller_owns_non_intervention() -> None:
    evaluator = _RecordingEvaluator()
    orchestrator = EvaluationOrchestrator(mode=EvaluationMode.OBSERVE, evaluator=evaluator)

    result = orchestrator.run(
        run=make_run(mode=EvaluationMode.OBSERVE), case=make_case(), candidate_answer="Paris"
    )

    assert result is not None
    assert evaluator.call_count == 1


def test_enforce_mode_evaluates_and_returns_a_recommendation() -> None:
    evaluator = _RecordingEvaluator()
    orchestrator = EvaluationOrchestrator(mode=EvaluationMode.ENFORCE, evaluator=evaluator)

    result = orchestrator.run(
        run=make_run(mode=EvaluationMode.ENFORCE), case=make_case(), candidate_answer="Paris"
    )

    assert result is not None
    assert result.recommendation is EvaluationRecommendation.ACCEPT
    assert evaluator.call_count == 1
