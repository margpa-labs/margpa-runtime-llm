import pydantic
import pytest

from margpa_runtime_llm.modules.runtime_observability.application.recording_service import (
    RecordingService,
)
from margpa_runtime_llm.modules.runtime_observability.domain.recording import (
    RecordingMode,
    SafeRecordingEnvelope,
    build_recording_envelope,
)


class _FakeWriter:
    def __init__(self) -> None:
        self.written: list[SafeRecordingEnvelope] = []

    def write(self, *, envelope: SafeRecordingEnvelope) -> None:
        self.written.append(envelope)


class _FailingWriter:
    def write(self, *, envelope: SafeRecordingEnvelope) -> None:
        raise OSError("disk full")


def test_off_mode_builds_no_envelope() -> None:
    envelope = build_recording_envelope(
        mode=RecordingMode.OFF,
        request_id="req-1",
        timestamp="t0",
        metadata_fields={},
        canonical_input="hello",
        presented_answer="hi",
    )
    assert envelope is None


def test_off_mode_via_service_never_calls_the_writer() -> None:
    writer = _FakeWriter()
    service = RecordingService(mode=RecordingMode.OFF, writer=writer)

    service.record(
        request_id="req-1",
        timestamp="t0",
        metadata_fields={"latency_ms": 100},
        canonical_input="hello",
        presented_answer="hi",
    )

    assert writer.written == []
    assert service.write_call_count == 0


def test_metadata_mode_never_includes_canonical_input_or_presented_answer() -> None:
    writer = _FakeWriter()
    service = RecordingService(mode=RecordingMode.METADATA, writer=writer)

    service.record(
        request_id="req-1",
        timestamp="t0",
        metadata_fields={"latency_ms": 100},
        canonical_input="the actual user message",
        presented_answer="the actual answer",
    )

    assert len(writer.written) == 1
    envelope = writer.written[0]
    assert envelope.canonical_input is None
    assert envelope.presented_answer is None
    assert envelope.metadata_fields == {"latency_ms": 100}


def test_full_mode_includes_canonical_input_and_presented_answer_only() -> None:
    writer = _FakeWriter()
    service = RecordingService(mode=RecordingMode.FULL, writer=writer)

    service.record(
        request_id="req-1",
        timestamp="t0",
        metadata_fields={},
        canonical_input="the actual user message",
        presented_answer="the actual answer",
    )

    envelope = writer.written[0]
    assert envelope.canonical_input == "the actual user message"
    assert envelope.presented_answer == "the actual answer"


def test_writer_failure_propagates_and_is_not_counted_as_a_successful_write() -> None:
    service = RecordingService(mode=RecordingMode.METADATA, writer=_FailingWriter())

    with pytest.raises(OSError, match="disk full"):
        service.record(
            request_id="req-1",
            timestamp="t0",
            metadata_fields={"latency_ms": 100},
            canonical_input="hello",
            presented_answer="hi",
        )

    assert service.write_call_count == 0


@pytest.mark.parametrize(
    "protected_field",
    [
        "thinking",
        "system_prompt",
        "secret",
        "rag_internal_context",
        "tool_internal_state",
        "hidden_original",
        "partial_output",
    ],
)
def test_protected_data_negative_matrix_no_field_exists_to_smuggle_it_in(
    protected_field: str,
) -> None:
    with pytest.raises(pydantic.ValidationError):
        SafeRecordingEnvelope.model_validate(
            {
                "request_id": "req-1",
                "timestamp": "t0",
                "mode": RecordingMode.FULL.value,
                protected_field: "leaked content",
            }
        )
