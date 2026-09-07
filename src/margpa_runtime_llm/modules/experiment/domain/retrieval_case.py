"""RAG Grounding / Strict NO_HIT Case Contracts (Phase 9-2, WU-D D2).

Design §8.2 compares `Model Call + NO_HIT Evidence + Semantic Governance`
against `Strict NO_HIT + Model Call 0 + configured-language deterministic
answer`. `classify_grounding()` distinguishes an honest Answer from a
False-Grounding one across all four Retrieval shapes (OFF/Relevant/
Irrelevant/NO_HIT) using one shared rule, so RAG-OFF parametric-knowledge
answers are never scored by the same "did it cite something real" rule a
RAG-ON case needs."""

from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identity import require_safe_identifier


class RetrievalMode(StrEnum):
    RAG_OFF = "rag_off"
    RELEVANT_HIT = "relevant_hit"
    IRRELEVANT_HIT = "irrelevant_hit"
    NO_HIT = "no_hit"


class NoHitStrategy(StrEnum):
    """Only meaningful when `RetrievalCase.retrieval_mode is NO_HIT`
    (Design §8.2's two compared shapes)."""

    MODEL_CALL_WITH_GOVERNANCE = "model_call_with_governance"
    STRICT_NO_HIT_MODEL_CALL_ZERO = "strict_no_hit_model_call_zero"


class RetrievalCase(ImmutableContract):
    case_id: str
    retrieval_mode: RetrievalMode
    no_hit_strategy: NoHitStrategy | None = None
    relevant_source_value: str | None = None

    @model_validator(mode="after")
    def _validate(self) -> RetrievalCase:
        require_safe_identifier(self.case_id, field_name="case_id")
        if self.retrieval_mode is RetrievalMode.NO_HIT and self.no_hit_strategy is None:
            raise ValueError("a NO_HIT RetrievalCase must declare a no_hit_strategy")
        if self.retrieval_mode is not RetrievalMode.NO_HIT and self.no_hit_strategy is not None:
            raise ValueError("no_hit_strategy is only meaningful for retrieval_mode=NO_HIT")
        return self


class GroundingOutcome(StrEnum):
    HONEST_GROUNDED = "honest_grounded"
    FALSE_GROUNDING = "false_grounding"
    HONEST_INSUFFICIENT_EVIDENCE = "honest_insufficient_evidence"
    UNGROUNDED_MODEL_KNOWLEDGE = "ungrounded_model_knowledge"


def classify_grounding(
    *, case: RetrievalCase, answer: str, answer_claims_citation: bool
) -> GroundingOutcome:
    """`answer_claims_citation` is a Judge/Rule-derived signal (did the
    Answer present itself as evidence-backed), never inferred by this
    function from `answer`'s own text -- that classification belongs to
    whatever Evaluator produced the signal, not to this Domain function."""

    if case.retrieval_mode is RetrievalMode.RAG_OFF:
        return GroundingOutcome.UNGROUNDED_MODEL_KNOWLEDGE
    if case.retrieval_mode is RetrievalMode.RELEVANT_HIT:
        if not answer_claims_citation:
            return GroundingOutcome.HONEST_INSUFFICIENT_EVIDENCE
        if case.relevant_source_value is not None and case.relevant_source_value in answer:
            return GroundingOutcome.HONEST_GROUNDED
        return GroundingOutcome.FALSE_GROUNDING
    if not answer_claims_citation:
        return GroundingOutcome.HONEST_INSUFFICIENT_EVIDENCE
    return GroundingOutcome.FALSE_GROUNDING


def expected_call_count_for_no_hit_strategy(strategy: NoHitStrategy) -> int | None:
    """`None` means no fixed expectation (`MODEL_CALL_WITH_GOVERNANCE` may
    call the Model one or more times depending on live Governance) --
    `STRICT_NO_HIT_MODEL_CALL_ZERO` is the one shape with a mechanically
    checkable exact expectation."""

    if strategy is NoHitStrategy.STRICT_NO_HIT_MODEL_CALL_ZERO:
        return 0
    return None
