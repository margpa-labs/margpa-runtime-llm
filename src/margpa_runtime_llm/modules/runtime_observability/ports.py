"""Ports for Runtime Observability (Architecture 10)."""

from typing import Protocol, runtime_checkable

from .domain.recording import SafeRecordingEnvelope


@runtime_checkable
class RecordingWriterPort(Protocol):
    """Local-only Recording sink. Never called at all when Recording Mode is OFF."""

    def write(self, *, envelope: SafeRecordingEnvelope) -> None: ...
