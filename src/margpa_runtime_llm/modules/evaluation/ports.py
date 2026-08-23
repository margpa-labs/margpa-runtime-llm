"""Ports for the Evaluation Domain (Architecture 6.2)."""

from typing import Protocol, runtime_checkable

from .domain.dataset import EvaluationCase
from .domain.llm_judge import LlmJudgeRequest, LlmJudgeResponse
from .domain.result import EvaluationResult
from .domain.run import EvaluationRun


@runtime_checkable
class DeterministicEvaluatorPort(Protocol):
    """A single interchangeable Deterministic Evaluator (Architecture 6.2/§6-C-WU-003)."""

    def evaluate(
        self, *, run: EvaluationRun, case: EvaluationCase, candidate_answer: str
    ) -> EvaluationResult: ...


@runtime_checkable
class LlmJudgePort(Protocol):
    """A dedicated or shared-artifact LLM-as-a-Judge (Architecture 6.2, Phase 6-D-WU-001).

    Any future dedicated Judge model (e.g. Selene-1-Mini-Llama-3.1-8B) can
    satisfy this Port without any Core change.
    """

    def judge(self, *, request: LlmJudgeRequest) -> LlmJudgeResponse: ...
