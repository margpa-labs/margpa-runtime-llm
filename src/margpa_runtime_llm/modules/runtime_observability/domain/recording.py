"""Recording Modes and Safe Recording Envelope (Architecture 10, Phase 6-F-WU-005/006).

SafeRecordingEnvelope's `extra="forbid"` (via ImmutableContract) is the
Protected Data Negative Matrix enforcement mechanism itself: Thinking,
System Prompt, Secret, RAG Internal Context, Tool-internal state, Hidden
Original, and Partial Output have no field to be smuggled into, so passing
any of them raises a ValidationError rather than silently persisting.
"""

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

MetadataValue = str | int | float | bool


class RecordingMode(StrEnum):
    OFF = "off"
    METADATA = "metadata"
    FULL = "full"


class SafeRecordingEnvelope(ImmutableContract):
    """The only shape ever allowed to reach a Recording Writer."""

    request_id: str = Field(min_length=1)
    timestamp: str = Field(min_length=1)
    mode: RecordingMode
    metadata_fields: dict[str, MetadataValue] = Field(default_factory=dict)
    canonical_input: str | None = None
    presented_answer: str | None = None


def build_recording_envelope(
    *,
    mode: RecordingMode,
    request_id: str,
    timestamp: str,
    metadata_fields: dict[str, MetadataValue],
    canonical_input: str | None,
    presented_answer: str | None,
) -> SafeRecordingEnvelope | None:
    """OFF returns None without constructing anything (P6-ACC-045: Build/Call/Write 0)."""
    if mode is RecordingMode.OFF:
        return None
    if mode is RecordingMode.METADATA:
        return SafeRecordingEnvelope(
            request_id=request_id,
            timestamp=timestamp,
            mode=mode,
            metadata_fields=metadata_fields,
            canonical_input=None,
            presented_answer=None,
        )
    return SafeRecordingEnvelope(
        request_id=request_id,
        timestamp=timestamp,
        mode=mode,
        metadata_fields=metadata_fields,
        canonical_input=canonical_input,
        presented_answer=presented_answer,
    )
