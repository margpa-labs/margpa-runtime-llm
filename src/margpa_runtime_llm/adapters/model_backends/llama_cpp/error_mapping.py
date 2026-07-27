"""Map llama.cpp protocol values and native failures into public contracts."""

from __future__ import annotations

from typing import Any, NoReturn

from margpa_runtime_llm.modules.inference.contracts.generation import FinishReason, TokenUsage
from margpa_runtime_llm.modules.inference.domain.errors import (
    InferenceError,
    InferenceErrorCode,
)


def map_finish_reason(raw_reason: object) -> tuple[FinishReason, str | None]:
    backend_reason = raw_reason if isinstance(raw_reason, str) else None
    mapping = {
        "stop": FinishReason.STOP,
        "length": FinishReason.LENGTH,
        "tool_calls": FinishReason.TOOL_CALL,
        "content_filter": FinishReason.CONTENT_FILTER,
    }
    if backend_reason is None:
        return FinishReason.UNKNOWN, None
    return mapping.get(backend_reason, FinishReason.UNKNOWN), backend_reason


def parse_token_usage(payload: dict[str, Any]) -> TokenUsage | None:
    raw_usage = payload.get("usage")
    if not isinstance(raw_usage, dict):
        return None
    prompt_tokens = raw_usage.get("prompt_tokens")
    completion_tokens = raw_usage.get("completion_tokens")
    total_tokens = raw_usage.get("total_tokens")
    if (
        not isinstance(prompt_tokens, int)
        or not isinstance(completion_tokens, int)
        or not isinstance(total_tokens, int)
    ):
        return None
    return TokenUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )


def raise_mapped_backend_error(
    operation: str,
    exc: BaseException,
    *,
    request_id: str | None = None,
    model_key: str | None = None,
) -> NoReturn:
    if not isinstance(exc, Exception):
        raise exc
    code_by_operation = {
        "load": InferenceErrorCode.MODEL_LOAD_FAILED,
        "generation": InferenceErrorCode.GENERATION_FAILED,
        "stream": InferenceErrorCode.GENERATION_FAILED,
        "unload": InferenceErrorCode.MODEL_UNLOAD_FAILED,
    }
    safe_message_by_operation = {
        "load": "The model could not be loaded.",
        "generation": "Generation failed in the model backend.",
        "stream": "Streaming failed in the model backend.",
        "unload": "The model backend could not release its resources.",
    }
    raise InferenceError(
        code=code_by_operation.get(operation, InferenceErrorCode.BACKEND_PROTOCOL_ERROR),
        safe_message=safe_message_by_operation.get(
            operation, "The model backend returned an invalid response."
        ),
        retryable=operation in {"load", "generation", "stream", "unload"},
        request_id=request_id,
        model_key=model_key,
        details={"operation": operation, "exception_type": type(exc).__name__},
    ) from exc
