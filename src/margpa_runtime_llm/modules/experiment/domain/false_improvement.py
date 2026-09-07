"""Runtime Success vs. Human Semantic Success (Phase 9-2, WU-D D4).

Reproduces, as a neutral comparable Case shape, Phase 9-1's observed
UF-P9-013 ("機械的Repair成功だが意味的には誤り"): `classify_repair_
semantic_outcome()` always compares a Runtime-level `repair_accepted`
signal against a genuine `EvaluatorKind.HUMAN` Observation's own outcome
(built only via `evaluation.build_human_observation()`, WU-B B3) --
never an LLM Self/Independent-Judge Observation standing in for it."""

from __future__ import annotations

from enum import StrEnum

from .dataset import ObservationOutcome


class RepairSemanticOutcome(StrEnum):
    GENUINE_IMPROVEMENT = "genuine_improvement"
    FALSE_IMPROVEMENT = "false_improvement"
    GENUINE_NO_CHANGE = "genuine_no_change"
    GENUINE_WORSE = "genuine_worse"
    UNKNOWN = "unknown"


def classify_repair_semantic_outcome(
    *, runtime_repair_accepted: bool, human_outcome: ObservationOutcome
) -> RepairSemanticOutcome:
    if human_outcome in (ObservationOutcome.NOT_RUN, ObservationOutcome.UNAVAILABLE):
        return RepairSemanticOutcome.UNKNOWN
    if runtime_repair_accepted:
        return (
            RepairSemanticOutcome.GENUINE_IMPROVEMENT
            if human_outcome is ObservationOutcome.PASS
            else RepairSemanticOutcome.FALSE_IMPROVEMENT
        )
    return (
        RepairSemanticOutcome.GENUINE_NO_CHANGE
        if human_outcome is ObservationOutcome.PASS
        else RepairSemanticOutcome.GENUINE_WORSE
    )
