import pydantic
import pytest

from margpa_runtime_llm.modules.evaluation.domain.dataset import EvaluationCase, EvaluationDataset
from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationMode,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.evaluation.domain.result import DimensionResult, EvaluationResult

from .conftest import SHA512_FILLER, make_case, make_run


def test_dataset_requires_a_valid_sha512_digest() -> None:
    with pytest.raises(pydantic.ValidationError):
        EvaluationDataset(
            dataset_id="ds-1", revision="r1", digest_sha512="not-a-hash", source_class="synthetic"
        )


def test_case_requires_at_least_one_criterion() -> None:
    base = make_case().model_dump()
    with pytest.raises(pydantic.ValidationError):
        EvaluationCase.model_validate({**base, "criteria": ()})


def test_run_is_constructible_for_each_mode() -> None:
    for mode in (EvaluationMode.OFF, EvaluationMode.OBSERVE, EvaluationMode.ENFORCE):
        run = make_run(mode=mode)
        assert run.mode is mode


def test_result_score_and_confidence_are_bounded_zero_to_one() -> None:
    with pytest.raises(pydantic.ValidationError):
        DimensionResult(dimension="accuracy", score=1.5, confidence=0.5)


def test_result_records_execution_state_and_recommendation() -> None:
    result = EvaluationResult(
        run_id="run-1",
        confidence=0.9,
        recommendation=EvaluationRecommendation.ACCEPT,
        token_usage=0,
        latency_ms=1,
        call_count=1,
        execution_state=EvaluationExecutionState.COMPLETED,
    )
    assert result.recommendation is EvaluationRecommendation.ACCEPT
    assert result.execution_state is EvaluationExecutionState.COMPLETED


def test_sha512_filler_constant_is_a_valid_pattern_for_config_digest() -> None:
    run = make_run(mode=EvaluationMode.ENFORCE)
    assert run.config_digest == SHA512_FILLER
