"""Immutable contracts for thinking output parsing and presentation."""

import unicodedata
from enum import StrEnum

from pydantic import Field, field_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

DEFAULT_THINKING_DISPLAY_LABEL = "推論過程"


class ThinkingVisibility(StrEnum):
    HIDDEN = "hidden"
    VISIBLE = "visible"


class ThinkingPersistence(StrEnum):
    DISABLED = "disabled"


class ThinkingPresentationSource(StrEnum):
    BUILT_IN_DEFAULT = "built_in_default"
    APPLICATION = "application"
    ENVIRONMENT = "environment"
    EXPLICIT = "explicit"


class ThinkingPresentationConfig(ImmutableContract):
    visibility: ThinkingVisibility = ThinkingVisibility.HIDDEN
    display_label: str = DEFAULT_THINKING_DISPLAY_LABEL
    persistence: ThinkingPersistence = ThinkingPersistence.DISABLED

    @field_validator("display_label")
    @classmethod
    def validate_display_label(cls, value: str) -> str:
        if not 1 <= len(value) <= 64:
            raise ValueError("thinking display label must contain 1 to 64 characters")
        if value != value.strip():
            raise ValueError("thinking display label must not have edge whitespace")
        if any(character in value for character in "<>/"):
            raise ValueError("thinking display label contains a forbidden character")
        if any(unicodedata.category(character).startswith("C") for character in value):
            raise ValueError("thinking display label contains a control character")
        return value


class PresentationConfig(ImmutableContract):
    thinking: ThinkingPresentationConfig = ThinkingPresentationConfig()


class ResolvedThinkingPresentationPolicy(ImmutableContract):
    visibility: ThinkingVisibility
    display_label: str
    persistence: ThinkingPersistence
    visibility_source: ThinkingPresentationSource
    display_label_source: ThinkingPresentationSource
    persistence_source: ThinkingPresentationSource

    @field_validator("display_label")
    @classmethod
    def validate_display_label(cls, value: str) -> str:
        return ThinkingPresentationConfig(display_label=value).display_label


class ThinkingContentKind(StrEnum):
    REASONING = "reasoning"
    FINAL = "final"


class ThinkingParseStatus(StrEnum):
    PLAIN_TEXT = "plain_text"
    COMPLETE = "complete"
    UNCLOSED_REASONING = "unclosed_reasoning"
    MALFORMED_PROTOCOL = "malformed_protocol"


class ThinkingSegmentDelta(ImmutableContract):
    kind: ThinkingContentKind
    text_delta: str


class ThinkingParseWarning(ImmutableContract):
    code: str = Field(min_length=1, pattern=r"^[a-z][a-z0-9_]*$")
    safe_message: str = Field(min_length=1)


class ThinkingParseSummary(ImmutableContract):
    status: ThinkingParseStatus
    warnings: tuple[ThinkingParseWarning, ...] = ()


class ThinkingParserFinish(ImmutableContract):
    segments: tuple[ThinkingSegmentDelta, ...] = ()
    summary: ThinkingParseSummary


class NormalizedThinkingOutput(ImmutableContract):
    reasoning_content: str | None
    final_content: str
    parse_status: ThinkingParseStatus
    warnings: tuple[ThinkingParseWarning, ...] = ()


class PresentedThinkingOutput(ImmutableContract):
    display_content: str
    normalized: NormalizedThinkingOutput


class PresentedThinkingStreamDelta(ImmutableContract):
    display_deltas: tuple[str, ...] = ()
    semantic_deltas: tuple[ThinkingSegmentDelta, ...] = ()


class PresentedThinkingStreamFinish(ImmutableContract):
    display_deltas: tuple[str, ...] = ()
    semantic_deltas: tuple[ThinkingSegmentDelta, ...] = ()
    presented: PresentedThinkingOutput
