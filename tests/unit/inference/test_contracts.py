"""Validation tests for the model-independent public contracts."""

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.inference.contracts.generation import (
    GenerationChunk,
    GenerationParameters,
    GenerationRequest,
    TokenUsage,
)
from margpa_runtime_llm.modules.inference.contracts.messages import ChatMessage, MessageRole
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)


def test_contracts_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ChatMessage.model_validate(
            {
                "role": "user",
                "content": "hello",
                "backend_payload": {"unsafe": True},
            }
        )


def test_contracts_are_frozen() -> None:
    parameters = GenerationParameters()
    with pytest.raises(ValidationError):
        parameters.max_new_tokens = 10


@pytest.mark.parametrize("content", ["", " ", "\n\t"])
def test_blank_messages_are_rejected(content: str) -> None:
    with pytest.raises(ValidationError):
        ChatMessage(role=MessageRole.USER, content=content)


def test_generation_request_requires_messages() -> None:
    with pytest.raises(ValidationError):
        GenerationRequest(request_id="request-1", model_key="model", messages=())


def test_empty_and_duplicate_stop_sequences_are_rejected() -> None:
    with pytest.raises(ValidationError):
        GenerationParameters(stop_sequences=("",))
    with pytest.raises(ValidationError):
        GenerationParameters(stop_sequences=("END", "END"))


def test_token_usage_must_balance() -> None:
    assert TokenUsage(prompt_tokens=2, completion_tokens=3, total_tokens=5).total_tokens == 5
    with pytest.raises(ValidationError):
        TokenUsage(prompt_tokens=2, completion_tokens=3, total_tokens=4)


def test_only_final_chunk_accepts_terminal_fields() -> None:
    with pytest.raises(ValidationError):
        GenerationChunk(
            request_id="request-1",
            sequence=0,
            text_delta="",
            is_final=True,
        )


def test_error_string_and_serialization_are_safe() -> None:
    error = InferenceError(
        code=InferenceErrorCode.GENERATION_FAILED,
        safe_message="Generation failed safely.",
        request_id="request-1",
        details={"exception_type": "NativeFailure"},
    )

    assert str(error) == "Generation failed safely."
    assert error.to_safe_dict()["code"] == "generation_failed"
    assert "0x" not in str(error.to_safe_dict())
