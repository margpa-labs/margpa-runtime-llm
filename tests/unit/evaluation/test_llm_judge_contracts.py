import pydantic
import pytest

from margpa_runtime_llm.modules.evaluation.domain.identifiers import (
    EvaluationExecutionState,
    EvaluationRecommendation,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import (
    JudgeFailureReason,
    JudgeIndependenceClass,
    LlmJudgeRequest,
    LlmJudgeResponse,
)

_SHA512_FILLER = "9" * 128


def _request(**overrides: object) -> LlmJudgeRequest:
    base = {
        "judge_role": JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
        "model_identity": "main.qwen3-4b-q4-k-m",
        "artifact_digest": _SHA512_FILLER,
        "rubric_id": "definition_confusion_v1",
        "prompt_digest": _SHA512_FILLER,
        "config_digest": _SHA512_FILLER,
        "timeout_ms": 30000,
        "max_tokens": 512,
    }
    base.update(overrides)
    return LlmJudgeRequest.model_validate(base)


def test_request_requires_valid_sha512_digests() -> None:
    with pytest.raises(pydantic.ValidationError):
        _request(prompt_digest="not-a-hash")


def test_request_never_carries_a_raw_prompt_field() -> None:
    request = _request()
    assert "prompt" not in request.model_dump()
    assert "prompt_digest" in request.model_dump()


def test_response_records_a_typed_failure_reason_on_timeout() -> None:
    response = LlmJudgeResponse(
        judge_role=JudgeIndependenceClass.INDEPENDENT_ARTIFACT,
        recommendation=EvaluationRecommendation.UNKNOWN,
        confidence=0.0,
        token_usage=0,
        latency_ms=30000,
        execution_state=EvaluationExecutionState.FAILED,
        failure_reason=JudgeFailureReason.TIMEOUT,
    )
    assert response.execution_state is EvaluationExecutionState.FAILED
    assert response.failure_reason is JudgeFailureReason.TIMEOUT
