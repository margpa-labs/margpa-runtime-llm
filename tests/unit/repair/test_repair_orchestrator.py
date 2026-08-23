from margpa_runtime_llm.modules.evaluation.application.evaluation_orchestrator import (
    EvaluationOrchestrator,
)
from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationMode,
    EvaluationRecommendation,
    EvaluatorClass,
)
from margpa_runtime_llm.modules.evaluation.domain.result import EvaluationResult
from margpa_runtime_llm.modules.evaluation.domain.run import (
    EvaluationBudget,
    EvaluationRun,
    EvaluatorBinding,
)
from margpa_runtime_llm.modules.repair.application.repair_orchestrator import execute_repair_plan
from margpa_runtime_llm.modules.repair.domain.identifiers import RepairOutcome, RepairState
from margpa_runtime_llm.modules.repair.domain.plan import RepairAttempt, RepairPlan

from .test_repair_domain import _plan

_SHA512_FILLER = "f" * 128


def make_case() -> EvaluationCase:
    return EvaluationCase(
        case_id="case-1",
        input="What is the capital of France?",
        reference="Paris",
        criteria=("exact_reference_match",),
        language="en",
    )


def make_run(*, mode: EvaluationMode, run_id: str = "run-1") -> EvaluationRun:
    return EvaluationRun(
        run_id=run_id,
        request_id="req-1",
        dataset_id="dataset-1",
        case_id="case-1",
        criteria=("exact_reference_match",),
        evaluator_binding=EvaluatorBinding(
            evaluator_id="exact_reference_match_v1", evaluator_class=EvaluatorClass.DETERMINISTIC
        ),
        mode=mode,
        config_digest=_SHA512_FILLER,
        budget=EvaluationBudget(max_calls=1, max_tokens=1000, max_wall_time_ms=5000),
    )


class _FixedRecommendationEvaluator:
    def __init__(self, *, recommendation: EvaluationRecommendation) -> None:
        self._recommendation = recommendation

    def evaluate(
        self, *, run: EvaluationRun, case: EvaluationCase, candidate_answer: str
    ) -> EvaluationResult:
        return EvaluationResult(
            run_id=run.run_id,
            confidence=1.0,
            recommendation=self._recommendation,
            token_usage=10,
            latency_ms=100,
            call_count=1,
            execution_state=EvaluationExecutionState.COMPLETED,
        )


class _FixedGenerator:
    def __init__(self, *, answer: str) -> None:
        self._answer = answer
        self.calls = 0

    def generate_repair_attempt(self, *, plan: RepairPlan, structured_feedback: str) -> str:
        self.calls += 1
        return self._answer


def _attempt() -> RepairAttempt:
    return RepairAttempt(
        attempt_id="attempt-2",
        repair_plan_id="plan-1",
        attempt_number=2,
        original_attempt_ref="attempt-1",
        state=RepairState.PLANNED,
    )


def test_successful_repair_reaches_accepted_and_marks_the_answer_as_the_repair() -> None:
    evaluator = EvaluationOrchestrator(
        mode=EvaluationMode.ENFORCE,
        evaluator=_FixedRecommendationEvaluator(recommendation=EvaluationRecommendation.ACCEPT),
    )
    generator = _FixedGenerator(answer="Paris")

    result, new_answer = execute_repair_plan(
        plan=_plan(),
        attempt=_attempt(),
        structured_feedback="Please state the capital explicitly.",
        case=make_case(),
        before_evaluation_run_ref="eval-run-before",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        generator=generator,
        evaluator=evaluator,
        rejudge_run=make_run(mode=EvaluationMode.ENFORCE, run_id="eval-run-after"),
    )

    assert result.outcome is RepairOutcome.IMPROVED
    assert result.accepted is True
    assert result.presented_answer_is_repair is True
    assert new_answer == "Paris"
    assert generator.calls == 1


def test_no_change_repair_reaches_rejected_and_never_becomes_the_presented_answer() -> None:
    evaluator = EvaluationOrchestrator(
        mode=EvaluationMode.ENFORCE,
        evaluator=_FixedRecommendationEvaluator(
            recommendation=EvaluationRecommendation.NEEDS_REPAIR
        ),
    )
    generator = _FixedGenerator(answer="Still wrong")

    result, _ = execute_repair_plan(
        plan=_plan(),
        attempt=_attempt(),
        structured_feedback="Try again.",
        case=make_case(),
        before_evaluation_run_ref="eval-run-before",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        generator=generator,
        evaluator=evaluator,
        rejudge_run=make_run(mode=EvaluationMode.ENFORCE, run_id="eval-run-after"),
    )

    assert result.outcome is RepairOutcome.NO_CHANGE
    assert result.accepted is False
    assert result.presented_answer_is_repair is False


def test_before_and_after_evaluation_run_refs_are_kept_distinct() -> None:
    evaluator = EvaluationOrchestrator(
        mode=EvaluationMode.ENFORCE,
        evaluator=_FixedRecommendationEvaluator(recommendation=EvaluationRecommendation.ACCEPT),
    )
    result, _ = execute_repair_plan(
        plan=_plan(),
        attempt=_attempt(),
        structured_feedback="feedback",
        case=make_case(),
        before_evaluation_run_ref="eval-run-before",
        before_recommendation=EvaluationRecommendation.NEEDS_REPAIR,
        generator=_FixedGenerator(answer="Paris"),
        evaluator=evaluator,
        rejudge_run=make_run(mode=EvaluationMode.ENFORCE, run_id="eval-run-after"),
    )
    assert result.before_evaluation_run_ref == "eval-run-before"
    assert result.after_evaluation_run_ref == "eval-run-after"
