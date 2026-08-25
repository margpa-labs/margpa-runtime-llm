"""Evaluation Mode Gate and fail-closed Presented Final disposition.

OBSERVE and ENFORCE both invoke the Evaluator identically at this layer;
the distinction between "evaluate only" and "may drive Repair Eligibility"
is a downstream Action Resolver concern (Phase 6-E), not something this
Domain/Ports layer decides.
"""

from dataclasses import dataclass

from ..domain.dataset import EvaluationCase
from ..domain.identifiers import (
    EvaluationExecutionState,
    EvaluationMode,
    EvaluationRecommendation,
)
from ..domain.result import EvaluationResult
from ..domain.run import EvaluationRun
from ..ports import DeterministicEvaluatorPort


class EvaluationOrchestrator:
    def __init__(self, *, mode: EvaluationMode, evaluator: DeterministicEvaluatorPort) -> None:
        self._mode = mode
        self._evaluator = evaluator

    @property
    def mode(self) -> EvaluationMode:
        return self._mode

    def run(
        self, *, run: EvaluationRun, case: EvaluationCase, candidate_answer: str
    ) -> EvaluationResult | None:
        if self._mode is EvaluationMode.OFF:
            return None
        return self._evaluator.evaluate(run=run, case=case, candidate_answer=candidate_answer)


@dataclass(frozen=True, slots=True)
class EvaluationDisposition:
    candidate_may_be_presented: bool
    repair_requested: bool
    evaluation_action_performed: bool


def resolve_evaluation_disposition(
    *,
    mode: EvaluationMode,
    execution_state: EvaluationExecutionState,
    recommendation: EvaluationRecommendation,
) -> EvaluationDisposition:
    """Map a typed evaluation outcome to an action without fabricating PASS.

    OFF performs no evaluation action. OBSERVE always preserves the raw
    Candidate. ENFORCE permits it only after a completed ACCEPT; a completed
    NEEDS_REPAIR may enter the bounded Repair router, while UNKNOWN and every
    failure remain withheld and converge to the caller's safe fallback.
    """

    if mode is EvaluationMode.OFF:
        return EvaluationDisposition(
            candidate_may_be_presented=True,
            repair_requested=False,
            evaluation_action_performed=False,
        )
    if mode is EvaluationMode.OBSERVE:
        return EvaluationDisposition(
            candidate_may_be_presented=True,
            repair_requested=False,
            evaluation_action_performed=True,
        )
    completed = execution_state is EvaluationExecutionState.COMPLETED
    return EvaluationDisposition(
        candidate_may_be_presented=(
            completed and recommendation is EvaluationRecommendation.ACCEPT
        ),
        repair_requested=(completed and recommendation is EvaluationRecommendation.NEEDS_REPAIR),
        evaluation_action_performed=True,
    )
