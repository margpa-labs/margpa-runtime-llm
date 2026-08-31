"""Map internal safe errors to HTTP status codes."""

from margpa_runtime_llm.modules.inference.domain.errors import InferenceErrorCode


def http_status_for_inference_error(code: InferenceErrorCode) -> int:
    if code is InferenceErrorCode.MODEL_BUSY:
        return 409
    if code in {
        InferenceErrorCode.INVALID_REQUEST,
        InferenceErrorCode.INVALID_CONFIGURATION,
        InferenceErrorCode.INVALID_MODEL_DEFINITION,
        InferenceErrorCode.CONTEXT_LIMIT_EXCEEDED,
        InferenceErrorCode.CONTENT_BUDGET_EXCEEDED,
        InferenceErrorCode.UNSUPPORTED_CAPABILITY,
    }:
        return 400
    if code in {
        InferenceErrorCode.MODEL_NOT_LOADED,
        InferenceErrorCode.BACKEND_UNAVAILABLE,
        InferenceErrorCode.MODEL_LOAD_FAILED,
        InferenceErrorCode.GENERATION_FAILED,
    }:
        return 503
    return 500
