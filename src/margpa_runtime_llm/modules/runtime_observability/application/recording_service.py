"""RecordingService (Phase 6-F-WU-005): the sole call site allowed to reach a Writer.

Guarantees OFF => zero envelope construction AND zero Writer calls at the
same layer, not split across two callers that could independently drift.
"""

from ..domain.recording import MetadataValue, RecordingMode, build_recording_envelope
from ..ports import RecordingWriterPort


class RecordingService:
    def __init__(self, *, mode: RecordingMode, writer: RecordingWriterPort) -> None:
        self._mode = mode
        self._writer = writer
        self.write_call_count = 0

    @property
    def mode(self) -> RecordingMode:
        return self._mode

    def record(
        self,
        *,
        request_id: str,
        timestamp: str,
        metadata_fields: dict[str, MetadataValue],
        canonical_input: str | None,
        presented_answer: str | None,
    ) -> None:
        envelope = build_recording_envelope(
            mode=self._mode,
            request_id=request_id,
            timestamp=timestamp,
            metadata_fields=metadata_fields,
            canonical_input=canonical_input,
            presented_answer=presented_answer,
        )
        if envelope is None:
            return
        self._writer.write(envelope=envelope)
        self.write_call_count += 1
