"""Deterministic Case Evaluator (Phase 9-2 R2, WU-03).

Replaces R1's `_observation_for_row()` "`completed` => `PASS`" Oracle,
the IR-P9-2-R1-03 BLOCKER the Controller's Independent Review confirmed:
a Run reaching `RunState.COMPLETED` was, by itself, previously enough to
credit a Case with `PASS`, without ever consulting the Case's own
`expected_observations`, Actual Output, or Actual Evidence.

This module instead dispatches by `case_id` to the already-built Domain
Classifiers (`freshness.classify_freshness_answer`, `retrieval_case.
expected_call_count_for_no_hit_strategy`) that Phase 9-2 WU-D built for
exactly this purpose but WU-E/R1 never wired into the Web/Comparison
path (the Controller's own confirmed finding). Handoff R2 SS6: "評価に
必要なEvidenceがない場合はINCONCLUSIVE、NOT_RUNまたはUNAVAILABLEであり、
PASSではない" -- every branch below either resolves a genuine, Evidence-
backed verdict or returns one of those three honest non-PASS outcomes,
never a guess."""

from __future__ import annotations

from ..domain.case_pack import FRESHNESS_HISTORICAL_VS_CURRENT, RETRIEVAL_STRICT_NO_HIT
from ..domain.dataset import EvaluationCaseManifest, ObservationOutcome
from ..domain.evaluation import (
    EvaluationObservation,
    EvaluatorKind,
    build_automated_observation,
    is_successful_runtime_state,
)
from ..domain.freshness import FreshnessOutcome, classify_freshness_answer
from ..domain.identity import ComponentKey
from ..domain.retrieval_case import NoHitStrategy, expected_call_count_for_no_hit_strategy
from ..domain.run import VariantRun
from .comparison_service import runtime_state_for_run

_PROVIDER_IDENTITY = "metric.deterministic-v1"

_FRESHNESS_OUTCOME_TO_OBSERVATION: dict[FreshnessOutcome, ObservationOutcome] = {
    FreshnessOutcome.CURRENT_FACT_USED: ObservationOutcome.PASS,
    FreshnessOutcome.STALE_FACT_REPEATED: ObservationOutcome.FAIL,
    FreshnessOutcome.HISTORICAL_CITATION_ALTERED: ObservationOutcome.FAIL,
    FreshnessOutcome.INSUFFICIENT_EVIDENCE: ObservationOutcome.INCONCLUSIVE,
}


def _main_call_count(invocations: list[object]) -> int | None:
    """`None` means "MAIN's own Call status is not confirmed" -- either
    its Invocation Record was never observed at all (no Raw Evidence, or
    an Evidence shape from before this Round), or (R3-WU-02, tri-state
    Evidence) it WAS observed but `called=None` (this Round's Evidence
    source genuinely cannot tell). Both are honestly "unknown", distinct
    from `0`, a genuine CONFIRMED Main-Call-Zero (`called=False`)."""

    count = 0
    saw_main = False
    for item in invocations:
        if not isinstance(item, dict):
            continue
        if item.get("component_key") == ComponentKey.MAIN.value:
            saw_main = True
            called = item.get("called")
            if called is None:
                return None
            if called:
                count += 1
    return count if saw_main else None


def evaluate_case_outcome(
    *,
    case: EvaluationCaseManifest,
    run: VariantRun,
    raw_evidence: dict[str, object] | None,
) -> EvaluationObservation:
    """The one Deterministic Evaluator every `execution_mode` and every
    `case_id` in `case_pack.build_case_pack()` goes through -- computed
    fresh from `(case, run, raw_evidence)` every time, never persisted
    separately from the `EvaluationObservation` it returns (there is
    nothing else to keep in sync)."""

    def _observation(outcome: ObservationOutcome, reason: str) -> EvaluationObservation:
        return build_automated_observation(
            run_id=run.run_id,
            case_id=case.case_id,
            evaluator_kind=EvaluatorKind.DETERMINISTIC,
            provider_identity=_PROVIDER_IDENTITY,
            rubric_revision=case.revision,
            outcome=outcome,
            reason=reason,
        )

    if not is_successful_runtime_state(runtime_state_for_run(run)):
        return _observation(ObservationOutcome.NOT_RUN, "run_not_completed")
    if case.requires_human_review:
        # WU-B B3 / R1-WU-04 (unchanged by R2): Human Review absence is
        # never silently upgraded to an automated PASS.
        return _observation(ObservationOutcome.NOT_RUN, "human_review_pending")

    if case.case_id == FRESHNESS_HISTORICAL_VS_CURRENT.case_id:
        assistant_content = (
            raw_evidence.get("assistant_content") if raw_evidence is not None else None
        )
        if not isinstance(assistant_content, str) or not assistant_content:
            return _observation(ObservationOutcome.UNAVAILABLE, "assistant_content_not_observed")
        freshness_outcome = classify_freshness_answer(
            case=FRESHNESS_HISTORICAL_VS_CURRENT,
            new_turn_answer=assistant_content,
            # This Round's Production Turn has no mechanism that could
            # ever mutate a past Turn's own citation record -- passing
            # the Case's own frozen digest back unchanged is a true
            # statement about what this Adapter is capable of doing, not
            # an assumed/fabricated "nothing changed".
            historical_turn_citation_digest_after_answer=(
                FRESHNESS_HISTORICAL_VS_CURRENT.historical_citation_digest_sha512
            ),
        )
        return _observation(
            _FRESHNESS_OUTCOME_TO_OBSERVATION[freshness_outcome], freshness_outcome.value
        )

    if case.case_id == RETRIEVAL_STRICT_NO_HIT.case_id:
        invocations_raw = raw_evidence.get("invocations") if raw_evidence is not None else None
        invocations = invocations_raw if isinstance(invocations_raw, list) else []
        main_calls = _main_call_count(invocations)
        expected = expected_call_count_for_no_hit_strategy(
            NoHitStrategy.STRICT_NO_HIT_MODEL_CALL_ZERO
        )
        if main_calls is None:
            return _observation(ObservationOutcome.UNAVAILABLE, "main_call_count_not_observed")
        if expected is not None and main_calls != expected:
            return _observation(ObservationOutcome.FAIL, "strict_no_hit_violated_model_called")
        # The mechanical expectation (Main Call Zero) is confirmed by
        # real Evidence, but the semantic half of this Case's own
        # `expected_observations` ("honest_insufficient_evidence", a
        # judgment about the Answer's own content) has no Judge/Rule
        # signal wired this Round -- INCONCLUSIVE, never PASS, until one
        # is (Handoff R2 SS6).
        return _observation(
            ObservationOutcome.INCONCLUSIVE, "model_call_zero_confirmed_content_unverified"
        )

    return _observation(ObservationOutcome.INCONCLUSIVE, "no_deterministic_evaluator_for_case")
