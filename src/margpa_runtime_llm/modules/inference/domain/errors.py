"""Safe, backend-independent inference errors."""

from collections.abc import Mapping
from enum import StrEnum
from types import MappingProxyType

type SafeDetailValue = str | int | float | bool | None


class InferenceErrorCode(StrEnum):
    INVALID_REQUEST = "invalid_request"
    INVALID_CONFIGURATION = "invalid_configuration"
    INVALID_MODEL_DEFINITION = "invalid_model_definition"
    UNSUPPORTED_PLATFORM = "unsupported_platform"
    PROFILE_REQUIRED = "profile_required"
    MODEL_NOT_FOUND = "model_not_found"
    MODEL_INTEGRITY_MISMATCH = "model_integrity_mismatch"
    BACKEND_UNAVAILABLE = "backend_unavailable"
    MODEL_LOAD_FAILED = "model_load_failed"
    MODEL_NOT_LOADED = "model_not_loaded"
    MODEL_ALREADY_LOADED = "model_already_loaded"
    MODEL_BUSY = "model_busy"
    INTERNAL_TASK_PREEMPTION_FAILED = "internal_task_preemption_failed"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    CONTEXT_LIMIT_EXCEEDED = "context_limit_exceeded"
    GENERATION_FAILED = "generation_failed"
    BACKEND_PROTOCOL_ERROR = "backend_protocol_error"
    MODEL_UNLOAD_FAILED = "model_unload_failed"


class InferenceError(Exception):
    """Exception whose string representation is safe for an end user."""

    def __init__(
        self,
        *,
        code: InferenceErrorCode,
        safe_message: str,
        retryable: bool = False,
        request_id: str | None = None,
        model_key: str | None = None,
        details: Mapping[str, SafeDetailValue] | None = None,
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.retryable = retryable
        self.request_id = request_id
        self.model_key = model_key
        self.details: Mapping[str, SafeDetailValue] = MappingProxyType(dict(details or {}))

    def to_safe_dict(self) -> dict[str, object]:
        return {
            "code": self.code.value,
            "safe_message": self.safe_message,
            "retryable": self.retryable,
            "request_id": self.request_id,
            "model_key": self.model_key,
            "details": dict(self.details),
        }
