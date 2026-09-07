"""Phase 9-2 WU-B B2/B3: Evaluator Identity separation and Metrics."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.experiment.domain.dataset import ObservationOutcome
from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)
from margpa_runtime_llm.modules.experiment.domain.evaluation import (
    EvaluationObservation,
    EvaluatorKind,
    MetricObservation,
    RuntimeOutcomeState,
    build_automated_observation,
    build_human_observation,
    is_successful_runtime_state,
)


def test_build_human_observation_prefixes_the_evaluator_identity() -> None:
    observation = build_human_observation(
        run_id="run-1",
        case_id="case-1",
        reviewer_id="reviewer-42",
        rubric_revision="rubric-v1",
        outcome=ObservationOutcome.PASS,
    )
    assert observation.evaluator_kind is EvaluatorKind.HUMAN
    assert observation.evaluator_identity == "human:reviewer-42"


@pytest.mark.parametrize(
    "kind", [EvaluatorKind.DETERMINISTIC, EvaluatorKind.SELF_JUDGE, EvaluatorKind.INDEPENDENT_JUDGE]
)
def test_build_automated_observation_never_produces_human_kind(kind: EvaluatorKind) -> None:
    observation = build_automated_observation(
        run_id="run-1",
        case_id="case-1",
        evaluator_kind=kind,
        provider_identity="judge.gemma-4-e2b-it-q4-0",
        rubric_revision="rubric-v1",
        outcome=ObservationOutcome.PASS,
    )
    assert observation.evaluator_kind is kind
    assert not observation.evaluator_identity.startswith("human:")


def test_build_automated_observation_rejects_human_kind_outright() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        build_automated_observation(
            run_id="run-1",
            case_id="case-1",
            evaluator_kind=EvaluatorKind.HUMAN,
            provider_identity="judge.gemma-4-e2b-it-q4-0",
            rubric_revision="rubric-v1",
            outcome=ObservationOutcome.PASS,
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.HUMAN_KIND_REQUIRES_HUMAN_FACTORY


def test_evaluation_observation_rejects_hand_constructed_human_kind_without_human_prefix() -> None:
    """WU-B B3's mechanical guarantee at the Contract boundary itself --
    even bypassing both factory functions and constructing the Contract
    directly cannot produce a `HUMAN`-kind Observation without the
    `human:` identity prefix `build_human_observation()` alone applies."""
    with pytest.raises(ExperimentCoreError) as excinfo:
        EvaluationObservation(
            run_id="run-1",
            case_id="case-1",
            evaluator_kind=EvaluatorKind.HUMAN,
            evaluator_identity="judge.gemma-4-e2b-it-q4-0",
            rubric_revision="rubric-v1",
            outcome=ObservationOutcome.PASS,
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.HUMAN_KIND_REQUIRES_HUMAN_FACTORY


def test_evaluation_observation_rejects_human_prefixed_identity_on_a_non_human_kind() -> None:
    with pytest.raises(ExperimentCoreError) as excinfo:
        EvaluationObservation(
            run_id="run-1",
            case_id="case-1",
            evaluator_kind=EvaluatorKind.INDEPENDENT_JUDGE,
            evaluator_identity="human:reviewer-42",
            rubric_revision="rubric-v1",
            outcome=ObservationOutcome.PASS,
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.HUMAN_KIND_REQUIRES_HUMAN_FACTORY


def test_is_successful_runtime_state_is_true_only_for_completed() -> None:
    assert is_successful_runtime_state(RuntimeOutcomeState.COMPLETED) is True
    for state in (
        RuntimeOutcomeState.FAILED,
        RuntimeOutcomeState.CANCELLED,
        RuntimeOutcomeState.NOT_RUN,
        RuntimeOutcomeState.UNAVAILABLE,
        RuntimeOutcomeState.UNSUPPORTED,
    ):
        assert is_successful_runtime_state(state) is False


def test_metric_observation_leaves_unmeasured_fields_none_not_zero() -> None:
    metric = MetricObservation(
        run_id="run-1", case_id="case-1", runtime_state=RuntimeOutcomeState.NOT_RUN
    )
    assert metric.deviation_count is None
    assert metric.call_count is None
    assert metric.repair_adopted is None
