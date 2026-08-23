"""Evaluation Mode Gate (Architecture 6.3): OFF guarantees zero Evaluator calls.

OBSERVE and ENFORCE both invoke the Evaluator identically at this layer;
the distinction between "evaluate only" and "may drive Repair Eligibility"
is a downstream Action Resolver concern (Phase 6-E), not something this
Domain/Ports layer decides.
"""

from ..domain.dataset import EvaluationCase
from ..domain.identifiers import EvaluationMode
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
