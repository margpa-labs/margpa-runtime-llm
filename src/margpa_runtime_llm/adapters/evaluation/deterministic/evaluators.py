"""Interchangeable Deterministic Evaluators (Phase 6-C-WU-003).

Each evaluator is a small, independently-testable, model-free check. None
call any LLM/Judge Model — Model 0 call is guaranteed by construction, not
just by an OFF-mode gate (Acceptance P6-ACC-015 "Deterministic Judge is
model-count 0").
"""

import re
import time

from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.evaluation.domain.result import DimensionResult, EvaluationResult
from margpa_runtime_llm.modules.evaluation.domain.run import EvaluationRun


class ExactReferenceMatchEvaluator:
    """Case-insensitive substring match against `case.reference`.

    A missing reference is a legitimate Unknown outcome (Execution Plan
    6-C-WU-005 "Unknown Reference"), not an error: this evaluator cannot
    assert correctness without one and says so rather than guessing.
    """

    dimension = "exact_reference_match"

    def evaluate(
        self, *, run: EvaluationRun, case: EvaluationCase, candidate_answer: str
    ) -> EvaluationResult:
        started = time.monotonic()
        if case.reference is None:
            return EvaluationResult(
                run_id=run.run_id,
                dimension_results=(
                    DimensionResult(dimension=self.dimension, score=None, confidence=0.0),
                ),
                confidence=0.0,
                recommendation=EvaluationRecommendation.UNKNOWN,
                token_usage=0,
                latency_ms=int((time.monotonic() - started) * 1000),
                call_count=0,
                execution_state=EvaluationExecutionState.COMPLETED,
                failure_reason="case has no reference; exact match is undecidable",
            )
        matched = case.reference.strip().lower() in candidate_answer.strip().lower()
        return EvaluationResult(
            run_id=run.run_id,
            dimension_results=(
                DimensionResult(
                    dimension=self.dimension,
                    score=1.0 if matched else 0.0,
                    confidence=1.0,
                ),
            ),
            confidence=1.0,
            recommendation=(
                EvaluationRecommendation.ACCEPT
                if matched
                else EvaluationRecommendation.NEEDS_REPAIR
            ),
            token_usage=0,
            latency_ms=int((time.monotonic() - started) * 1000),
            call_count=0,
            execution_state=EvaluationExecutionState.COMPLETED,
        )


class RequiredFieldPresenceEvaluator:
    """All `required_substrings` must literally appear in the candidate answer."""

    dimension = "required_field_presence"

    def __init__(self, *, required_substrings: tuple[str, ...]) -> None:
        self._required_substrings = required_substrings

    def evaluate(
        self, *, run: EvaluationRun, case: EvaluationCase, candidate_answer: str
    ) -> EvaluationResult:
        started = time.monotonic()
        missing = tuple(
            field
            for field in self._required_substrings
            if field.lower() not in candidate_answer.lower()
        )
        passed = not missing
        return EvaluationResult(
            run_id=run.run_id,
            dimension_results=(
                DimensionResult(
                    dimension=self.dimension,
                    score=1.0 if passed else 0.0,
                    confidence=1.0,
                ),
            ),
            confidence=1.0,
            unsupported_claims=(),
            contradictions=missing,
            recommendation=(
                EvaluationRecommendation.ACCEPT if passed else EvaluationRecommendation.NEEDS_REPAIR
            ),
            token_usage=0,
            latency_ms=int((time.monotonic() - started) * 1000),
            call_count=0,
            execution_state=EvaluationExecutionState.COMPLETED,
        )


class ContradictionMarkerEvaluator:
    """Flags candidate answers containing any declared contradiction marker phrase."""

    dimension = "contradiction_marker"

    def __init__(self, *, contradiction_markers: tuple[str, ...]) -> None:
        self._contradiction_markers = contradiction_markers

    def evaluate(
        self, *, run: EvaluationRun, case: EvaluationCase, candidate_answer: str
    ) -> EvaluationResult:
        started = time.monotonic()
        found = tuple(
            marker
            for marker in self._contradiction_markers
            if marker.lower() in candidate_answer.lower()
        )
        passed = not found
        return EvaluationResult(
            run_id=run.run_id,
            dimension_results=(
                DimensionResult(
                    dimension=self.dimension,
                    score=1.0 if passed else 0.0,
                    confidence=1.0,
                ),
            ),
            confidence=1.0,
            contradictions=found,
            recommendation=(
                EvaluationRecommendation.ACCEPT if passed else EvaluationRecommendation.NEEDS_REPAIR
            ),
            token_usage=0,
            latency_ms=int((time.monotonic() - started) * 1000),
            call_count=0,
            execution_state=EvaluationExecutionState.COMPLETED,
        )


class UnsupportedClaimCandidateEvaluator:
    """Flags absolute-claim marker phrases that do not also appear in the reference.

    This is a candidate-flagging heuristic, not a proof of unsupportedness:
    it never asserts a claim IS unsupported, only that it is a Candidate for
    human/LLM-Judge review (Architecture 6.1 "unsupported_claims").
    """

    dimension = "unsupported_claim_candidate"

    def __init__(self, *, absolute_claim_markers: tuple[str, ...]) -> None:
        self._absolute_claim_markers = absolute_claim_markers

    def evaluate(
        self, *, run: EvaluationRun, case: EvaluationCase, candidate_answer: str
    ) -> EvaluationResult:
        started = time.monotonic()
        reference_text = (case.reference or "").lower()
        candidates = tuple(
            marker
            for marker in self._absolute_claim_markers
            if marker.lower() in candidate_answer.lower() and marker.lower() not in reference_text
        )
        return EvaluationResult(
            run_id=run.run_id,
            dimension_results=(
                DimensionResult(
                    dimension=self.dimension,
                    score=None,
                    confidence=1.0 if not candidates else 0.5,
                ),
            ),
            confidence=1.0 if not candidates else 0.5,
            unsupported_claims=candidates,
            recommendation=(
                EvaluationRecommendation.ACCEPT
                if not candidates
                else EvaluationRecommendation.NEEDS_REPAIR
            ),
            token_usage=0,
            latency_ms=int((time.monotonic() - started) * 1000),
            call_count=0,
            execution_state=EvaluationExecutionState.COMPLETED,
        )


class FormatComplianceEvaluator:
    """The candidate answer must match a declared regex (structural format check)."""

    dimension = "format_compliance"

    def __init__(self, *, pattern: str) -> None:
        self._pattern = re.compile(pattern, re.DOTALL)

    def evaluate(
        self, *, run: EvaluationRun, case: EvaluationCase, candidate_answer: str
    ) -> EvaluationResult:
        started = time.monotonic()
        matched = self._pattern.search(candidate_answer) is not None
        return EvaluationResult(
            run_id=run.run_id,
            dimension_results=(
                DimensionResult(
                    dimension=self.dimension,
                    score=1.0 if matched else 0.0,
                    confidence=1.0,
                ),
            ),
            confidence=1.0,
            recommendation=(
                EvaluationRecommendation.ACCEPT
                if matched
                else EvaluationRecommendation.NEEDS_REPAIR
            ),
            token_usage=0,
            latency_ms=int((time.monotonic() - started) * 1000),
            call_count=0,
            execution_state=EvaluationExecutionState.COMPLETED,
        )
