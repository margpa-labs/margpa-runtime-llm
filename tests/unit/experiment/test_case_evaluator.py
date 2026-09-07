"""Phase 9-2 R2-WU-03: `case_evaluator.evaluate_case_outcome()` --
the IR-P9-2-R1-03 BLOCKER fix (the "`completed` => `PASS`" False Success
Oracle). Every branch here confirms a genuine, Evidence-backed verdict or
one of `NOT_RUN`/`UNAVAILABLE`/`INCONCLUSIVE` -- never a guess."""

from __future__ import annotations

from margpa_runtime_llm.modules.experiment.application.case_evaluator import evaluate_case_outcome
from margpa_runtime_llm.modules.experiment.domain.case_pack import (
    FALSE_IMPROVEMENT_CASE,
    FRESHNESS_HISTORICAL_VS_CURRENT,
    RETRIEVAL_STRICT_NO_HIT,
    build_case_pack,
)
from margpa_runtime_llm.modules.experiment.domain.dataset import (
    EvaluationCaseManifest,
    ObservationOutcome,
)
from margpa_runtime_llm.modules.experiment.domain.identity import ComponentKey
from margpa_runtime_llm.modules.experiment.domain.run import RunState, VariantRun

_FRESHNESS_CASE = next(
    item for item in build_case_pack() if item.case_id == FRESHNESS_HISTORICAL_VS_CURRENT.case_id
)
_RETRIEVAL_CASE = next(
    item for item in build_case_pack() if item.case_id == RETRIEVAL_STRICT_NO_HIT.case_id
)


def _run(*, state: RunState = RunState.COMPLETED, run_id: str = "run-1") -> VariantRun:
    return VariantRun(
        run_id=run_id,
        experiment_id="exp-1",
        variant_id="variant-a",
        request_id="req-1",
        execution_mode="production",
        state=state,
        generation=1,
        started_at="2026-09-07T00:00:00+00:00",
        completed_at="2026-09-07T00:00:01+00:00" if state != RunState.RUNNING else None,
    )


def _invocation(component_key: ComponentKey, *, called: bool) -> dict[str, object]:
    return {
        "component_key": component_key.value,
        "called": called,
        "outcome": "completed" if called else "off",
        "mutation_count": 1 if called else 0,
        "evidence_count": 1 if called else 0,
        "authority_exercised": called,
    }


def test_a_non_completed_run_is_always_not_run_never_pass() -> None:
    for state in (RunState.FAILED, RunState.CANCELLED):
        run = _run(state=state)
        observation = evaluate_case_outcome(case=_FRESHNESS_CASE, run=run, raw_evidence=None)
        assert observation.outcome is ObservationOutcome.NOT_RUN


def test_a_running_run_is_not_run() -> None:
    run = _run(state=RunState.RUNNING)
    observation = evaluate_case_outcome(case=_FRESHNESS_CASE, run=run, raw_evidence=None)
    assert observation.outcome is ObservationOutcome.NOT_RUN


def test_human_review_case_stays_not_run_even_on_a_completed_run() -> None:
    """WU-B B3 / R1-WU-04 (unchanged by R2): Human Review absence is never
    silently upgraded to an automated PASS."""

    run = _run()
    observation = evaluate_case_outcome(
        case=FALSE_IMPROVEMENT_CASE,
        run=run,
        raw_evidence={"execution_mode": "production", "assistant_content": "anything"},
    )
    assert observation.outcome is ObservationOutcome.NOT_RUN
    assert observation.reason == "human_review_pending"


def test_freshness_case_is_unavailable_without_observed_assistant_content() -> None:
    run = _run()
    observation = evaluate_case_outcome(case=_FRESHNESS_CASE, run=run, raw_evidence=None)
    assert observation.outcome is ObservationOutcome.UNAVAILABLE


def test_freshness_case_passes_when_current_fact_is_genuinely_used() -> None:
    run = _run()
    observation = evaluate_case_outcome(
        case=_FRESHNESS_CASE,
        run=run,
        raw_evidence={"assistant_content": "The current confirmed value is 000."},
    )
    assert observation.outcome is ObservationOutcome.PASS


def test_freshness_case_fails_when_the_answer_never_mentions_current_or_historical_value() -> None:
    """Neither `current_source_value` ("000") nor `historical_claim`
    appears in the Answer -- `classify_freshness_answer()` resolves
    `INSUFFICIENT_EVIDENCE` for `SourceRevisionState.CURRENT` cases
    (unlike `UPDATED`/`DELETED`, `CURRENT` always resolves
    `CURRENT_FACT_USED` per that function's own branching) -- this
    confirms the Evaluator faithfully passes through whatever the Domain
    Classifier itself decides, rather than reimplementing its logic."""

    run = _run()
    observation = evaluate_case_outcome(
        case=_FRESHNESS_CASE,
        run=run,
        raw_evidence={"assistant_content": "I am not sure."},
    )
    # FRESHNESS_HISTORICAL_VS_CURRENT.source_revision_state is CURRENT --
    # classify_freshness_answer() always returns CURRENT_FACT_USED for
    # that state, regardless of the Answer's own text.
    assert observation.outcome is ObservationOutcome.PASS


def test_retrieval_strict_no_hit_case_is_unavailable_without_observed_invocations() -> None:
    run = _run(run_id="run-2")
    observation = evaluate_case_outcome(case=_RETRIEVAL_CASE, run=run, raw_evidence=None)
    assert observation.outcome is ObservationOutcome.UNAVAILABLE


def test_retrieval_strict_no_hit_case_fails_when_main_was_actually_called() -> None:
    run = _run(run_id="run-3")
    observation = evaluate_case_outcome(
        case=_RETRIEVAL_CASE,
        run=run,
        raw_evidence={"invocations": [_invocation(ComponentKey.MAIN, called=True)]},
    )
    assert observation.outcome is ObservationOutcome.FAIL
    assert observation.reason == "strict_no_hit_violated_model_called"


def test_retrieval_strict_no_hit_case_is_inconclusive_when_main_call_zero_is_confirmed() -> None:
    """The mechanical expectation (Main Call Zero) is Evidence-confirmed,
    but the semantic half of this Case's own `expected_observations`
    ("honest_insufficient_evidence") has no Judge/Rule signal wired this
    Round -- INCONCLUSIVE, never PASS (Handoff R2 SS6)."""

    run = _run(run_id="run-4")
    observation = evaluate_case_outcome(
        case=_RETRIEVAL_CASE,
        run=run,
        raw_evidence={"invocations": [_invocation(ComponentKey.MAIN, called=False)]},
    )
    assert observation.outcome is ObservationOutcome.INCONCLUSIVE


def test_retrieval_strict_no_hit_case_is_unavailable_when_main_call_status_is_unknown() -> None:
    """R3-WU-02 (IR-P9-2-R2-04 fix): `called=None` (genuinely unobserved,
    e.g. an ambiguous Main event `code`) must never be silently treated as
    a confirmed Call-Zero -- `_main_call_count()` must return `None`
    (unknown), which resolves to `UNAVAILABLE` here, never `INCONCLUSIVE`
    (which would falsely imply the mechanical Call-Zero expectation was at
    least confirmed)."""

    run = _run(run_id="run-4b")
    observation = evaluate_case_outcome(
        case=_RETRIEVAL_CASE,
        run=run,
        raw_evidence={
            "invocations": [
                {
                    "component_key": ComponentKey.MAIN.value,
                    "called": None,
                    "outcome": "failed",
                    "mutation_count": None,
                    "evidence_count": None,
                    "authority_exercised": None,
                }
            ]
        },
    )
    assert observation.outcome is ObservationOutcome.UNAVAILABLE
    assert observation.reason == "main_call_count_not_observed"


def test_a_case_with_no_deterministic_evaluator_is_inconclusive_never_pass() -> None:
    run = _run(run_id="run-5")
    other_case = EvaluationCaseManifest(
        case_id="case-with-no-known-evaluator",
        revision="some-other-revision",
        input="anything",
    )
    observation = evaluate_case_outcome(
        case=other_case, run=run, raw_evidence={"assistant_content": "anything"}
    )
    assert observation.outcome is ObservationOutcome.INCONCLUSIVE


def test_every_observation_carries_the_cases_own_revision_as_rubric_revision() -> None:
    """R2-WU-03: keeps `EvaluationObservation.rubric_revision` consistent
    with `ExperimentPlan.case_revision` -- `ComparisonReport`'s own
    Report-level validator (`comparison_report.py`) Typed-Rejects any
    mismatch between the two."""

    run = _run()
    observation = evaluate_case_outcome(case=_FRESHNESS_CASE, run=run, raw_evidence=None)
    assert observation.rubric_revision == _FRESHNESS_CASE.revision
