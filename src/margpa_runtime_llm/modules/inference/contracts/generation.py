"""One-shot and streaming generation contracts."""

import hashlib
import json
from collections.abc import Iterator, Mapping
from enum import StrEnum
from types import TracebackType
from typing import Protocol

from pydantic import Field, field_validator, model_validator

from .base import ImmutableContract
from .messages import ChatMessage
from .runtime import InferenceWarning, ModelRuntimeReference


class ThinkingMode(StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    MODEL_DEFAULT = "model_default"


_STRUCTURED_OUTPUT_SCHEMA_MAX_BYTES = 65536
"""Gemma Judge-only Constrained Decoding Rework (WU-01): a Typed-Reject cap
on the canonical (sorted-key) serialized `json_schema`, so a pathological or
mistakenly-huge Schema fails Contract construction immediately rather than
reaching the Backend's own Grammar compiler."""


class StructuredOutputConstraint(ImmutableContract):
    """Backend-neutral, Role-agnostic Optional generation constraint (WU-01):
    a JSON Schema a Backend that supports it MAY compile into a generation
    Grammar. `None` on `GenerationParameters.structured_output` (the
    default, unchanged for every existing caller) means exactly what it did
    before this field existed -- no constraint, ordinary free-form
    generation. Only a Composition that explicitly constructs one and
    attaches it to a specific Request's own `GenerationParameters` ever
    causes a Backend to see a Grammar; this Contract itself has no opinion
    about which Role may do so.

    Immutable once constructed (frozen Contract, like every sibling
    `GenerationParameters` field) -- a Request that freezes with this
    constraint attached can never have it silently swapped afterward.
    `schema_digest_sha512` is the canonical (sorted-key, compact) SHA-512 of
    `json_schema`'s own JSON serialization; Evidence recording can persist
    this Digest alone, never the full Schema text, exactly like every other
    Digest-not-payload Evidence field this project already uses elsewhere
    (`prompt_digest_sha512`, `config_digest_sha512`, ...). Use `from_schema()`
    to construct one from a plain dict -- it computes the matching Digest for
    you; direct construction is fail-closed if the two do not agree.

    Gemma Constrained Decoding Final Contract Micro Rework (IR-FC-02):
    `frozen=True` (via `ImmutableContract`) blocks reassigning the
    `json_schema` field itself, but `dict` is still a mutable object --
    Controller Review confirmed `constraint.json_schema["type"] = "..."`
    still succeeds after construction, leaving `schema_digest_sha512`
    stale. This Contract does not attempt to make the nested `dict` itself
    immutable (no deep-freeze, no large API redesign); instead, the one
    real consumer that turns `json_schema` into an executable Grammar
    (`LlamaCppChatTemplate._build_grammar()`) re-serializes and re-hashes
    it immediately before compiling, and Fails Closed if the recomputed
    Digest no longer matches this Contract's own `schema_digest_sha512` --
    so a Schema mutated after construction can never silently reach the
    Backend under a Digest that no longer describes it.
    """

    json_schema: dict[str, object]
    schema_digest_sha512: str = Field(pattern=r"^[0-9a-f]{128}$")

    @model_validator(mode="after")
    def _validate_schema(self) -> "StructuredOutputConstraint":
        if not self.json_schema:
            raise ValueError("json_schema must not be empty")
        try:
            serialized = json.dumps(
                self.json_schema, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(f"json_schema is not JSON-serializable: {exc}") from exc
        encoded = serialized.encode("utf-8")
        if len(encoded) > _STRUCTURED_OUTPUT_SCHEMA_MAX_BYTES:
            raise ValueError("json_schema exceeds the maximum allowed serialized size")
        expected_digest = hashlib.sha512(encoded).hexdigest()
        if expected_digest != self.schema_digest_sha512:
            raise ValueError(
                "schema_digest_sha512 does not match the canonical json_schema serialization"
            )
        return self

    @classmethod
    def from_schema(cls, json_schema: Mapping[str, object]) -> "StructuredOutputConstraint":
        schema = dict(json_schema)
        try:
            serialized = json.dumps(
                schema, ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
        except (TypeError, ValueError):
            # Gemma Constrained Decoding Final Contract Micro Rework
            # (IR-FC-02): before this fix, a non-JSON-serializable
            # `json_schema` raised a raw `TypeError`/`ValueError` straight
            # out of this classmethod, bypassing the Contract's own Typed
            # Validation Failure entirely. Constructing with an arbitrary
            # placeholder Digest here is safe -- the identical
            # serialization attempt inside `_validate_schema()` fails
            # first (before any Digest comparison is even reached),
            # raising the same canonical `ValueError` (surfaced by Pydantic
            # as a `ValidationError`) every other invalid `json_schema`
            # already produces, rather than a distinct raw exception type
            # escaping this one construction path.
            return cls(json_schema=schema, schema_digest_sha512="0" * 128)
        digest = hashlib.sha512(serialized.encode("utf-8")).hexdigest()
        return cls(json_schema=schema, schema_digest_sha512=digest)


class GenerationParameters(ImmutableContract):
    max_new_tokens: int = Field(default=512, gt=0)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.8, gt=0.0, le=1.0)
    top_k: int = Field(default=20, ge=0)
    min_p: float = Field(default=0.0, ge=0.0, le=1.0)
    presence_penalty: float = Field(default=1.5, ge=-2.0, le=2.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    repeat_penalty: float = Field(default=1.0, gt=0.0)
    seed: int | None = None
    stop_sequences: tuple[str, ...] = ()
    thinking_mode: ThinkingMode = ThinkingMode.DISABLED
    structured_output: StructuredOutputConstraint | None = None
    """Gemma Judge-only Constrained Decoding Rework (WU-01): `None` for
    every Request this project constructs today except the ones a Judge
    Composition explicitly builds one for (see `SeleneSemanticEvaluator`'s
    own `structured_output_schema_factory` and `attempt_live_repair()`'s
    `rejudge_structured_output_schema_factory` -- both `None` by default).
    Main's ordinary generation, the Repair Candidate generation, and every
    Guard/RAG/Web/Dev-Agent Request never sets this field at all, so this
    addition changes zero existing Request construction call sites."""

    @field_validator("stop_sequences")
    @classmethod
    def validate_stop_sequences(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any(not item for item in value):
            raise ValueError("stop sequences must not contain an empty string")
        if len(set(value)) != len(value):
            raise ValueError("stop sequences must be unique")
        return value


class GenerationRequest(ImmutableContract):
    request_id: str
    model_key: str
    messages: tuple[ChatMessage, ...]
    parameters: GenerationParameters = GenerationParameters()

    @field_validator("request_id", "model_key")
    @classmethod
    def validate_identifier(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("identifier must not be blank")
        return value

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, value: tuple[ChatMessage, ...]) -> tuple[ChatMessage, ...]:
        if not value:
            raise ValueError("at least one message is required")
        return value


class FinishReason(StrEnum):
    STOP = "stop"
    LENGTH = "length"
    CANCELLED = "cancelled"
    TOOL_CALL = "tool_call"
    CONTENT_FILTER = "content_filter"
    UNKNOWN = "unknown"


class TokenUsage(ImmutableContract):
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_total(self) -> "TokenUsage":
        if self.total_tokens != self.prompt_tokens + self.completion_tokens:
            raise ValueError("total_tokens must equal prompt_tokens + completion_tokens")
        return self


class GenerationTiming(ImmutableContract):
    first_content_latency_seconds: float | None = Field(default=None, ge=0.0)
    total_generation_seconds: float = Field(ge=0.0)
    tokens_per_second: float | None = Field(default=None, ge=0.0)


class GenerationResult(ImmutableContract):
    request_id: str
    model_key: str
    content: str
    finish_reason: FinishReason
    backend_finish_reason: str | None = None
    usage: TokenUsage | None = None
    timing: GenerationTiming
    runtime_info: ModelRuntimeReference
    warnings: tuple[InferenceWarning, ...] = ()


class GenerationChunk(ImmutableContract):
    request_id: str
    sequence: int = Field(ge=0)
    text_delta: str
    is_final: bool
    finish_reason: FinishReason | None = None
    usage: TokenUsage | None = None

    @model_validator(mode="after")
    def validate_terminal_fields(self) -> "GenerationChunk":
        if self.is_final and self.finish_reason is None:
            raise ValueError("a final chunk requires finish_reason")
        if not self.is_final and (self.finish_reason is not None or self.usage is not None):
            raise ValueError("only a final chunk may contain terminal fields")
        return self


class GenerationTerminalState(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CLOSED_BY_CONSUMER = "closed_by_consumer"
    FAILED = "failed"


class GenerationStream(Protocol):
    @property
    def generation_id(self) -> str: ...

    @property
    def terminal_state(self) -> GenerationTerminalState: ...

    @property
    def timing(self) -> GenerationTiming | None: ...

    def __iter__(self) -> Iterator[GenerationChunk]: ...

    def cancel(self) -> None: ...

    def close(self) -> None: ...

    def __enter__(self) -> "GenerationStream": ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...
