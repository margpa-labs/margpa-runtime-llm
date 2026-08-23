"""Typed Span for Detection/Redaction (P5-MOD-006, ADR-5-008).

A `TypedSpan` never carries the raw matched text — only Bounds and a
Safe Category — so Evidence built from it never leaks Secret/PII
content (P5-EVD-002). Redaction is only ever permitted when the Span is
Verified (non-overlapping, in-range) against the exact content it
claims to describe.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identities import IDENTIFIER_PATTERN


class TypedSpan(ImmutableContract):
    category_id: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    start: int = Field(ge=0)
    end: int = Field(ge=0)

    @model_validator(mode="after")
    def _end_after_start(self) -> TypedSpan:
        if self.end <= self.start:
            raise ValueError("a Span's end must be strictly after its start")
        return self


def spans_are_verified(spans: tuple[TypedSpan, ...], *, content_length: int) -> bool:
    """A Span set is Verified only if every Span is in-range and no two
    Spans overlap — Ambiguous/Overlapping Spans never become an
    executable Redaction Candidate (ADR-5-008)."""

    ordered = sorted(spans, key=lambda span: span.start)
    previous_end = -1
    for span in ordered:
        if span.start < previous_end:
            return False
        if span.end > content_length:
            return False
        previous_end = span.end
    return True
