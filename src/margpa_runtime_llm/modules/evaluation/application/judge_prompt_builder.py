"""Bounded Typed Prompt construction for LLM-as-a-Judge (Phase 6-D-WU-003).

Deterministic given identical inputs: no randomness, no wall-clock content,
so a caller can compute a stable prompt_digest from the returned text
without storing the raw prompt itself as normal Evidence.
"""

from ..domain.dataset import EvaluationCase

_RESPONSE_FORMAT_INSTRUCTION = (
    "Respond with exactly one JSON object and nothing else, matching this schema: "
    '{"recommendation": "accept" | "needs_repair" | "unknown", '
    '"confidence": <number between 0.0 and 1.0>, '
    '"reasoning": "<short string>"}. '
    'Use "unknown" whenever the case reference is absent or insufficient to decide.'
)


def build_judge_prompt(*, case: EvaluationCase, candidate_answer: str, rubric_id: str) -> str:
    reference_line = (
        f"Reference answer: {case.reference}"
        if case.reference is not None
        else "Reference answer: (none provided)"
    )
    criteria_line = "Criteria: " + ", ".join(case.criteria)
    return (
        f"Rubric: {rubric_id}\n"
        f"Question: {case.input}\n"
        f"{reference_line}\n"
        f"{criteria_line}\n"
        f"Candidate answer: {candidate_answer}\n"
        f"{_RESPONSE_FORMAT_INSTRUCTION}"
    )
