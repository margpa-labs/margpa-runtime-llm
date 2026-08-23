"""P6-CODEX-011 (Second Rework): Recording is decoupled entirely from
Judge. The core regression this guards against: Recording FULL/METADATA
must produce a record for a completed Turn even when Judge never ran at
all (Judge OFF, or no Judge Hook configured whatsoever) — the previous
design only ever wrote a record from inside `_run_judge()`'s own tail,
so Recording FULL silently produced zero records whenever Judge was OFF
(ADR-6-013 Mode orthogonality violation).

Also covers: Recording OFF is zero Writer calls; a real Judge Run's own
Evidence is written to a distinct file/subdirectory, correlated by
request_id but never colliding with the Turn-level record; and a Writer
failure (Quota exceeded here) degrades the RecordingCompositionState
rather than raising out of the Hook or silently vanishing.
"""

from __future__ import annotations

import json
from pathlib import Path

from margpa_runtime_llm.adapters.runtime_observability.local_filesystem_recording_writer import (
    LocalFilesystemRecordingWriter,
)
from margpa_runtime_llm.bootstrap.recording_live_integration import (
    build_judge_evidence_recorder,
    build_recording_completion_hook,
)
from margpa_runtime_llm.modules.conversation.application.conversation_generation import (
    JudgeCompletionContext,
)
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)
from margpa_runtime_llm.modules.runtime_observability.domain.recording import RecordingMode


def test_recording_full_writes_a_turn_record_with_zero_judge_involvement(
    tmp_path: Path,
) -> None:
    """The exact regression P6-CODEX-011 flags: no Judge Hook exists at
    all in this test, yet Recording FULL still produces a record purely
    from the Conversation completion path."""
    controller = RecordingModeController()
    controller.apply_mode(RecordingMode.FULL)
    writer = LocalFilesystemRecordingWriter(base_dir=tmp_path, max_total_bytes=10_000)
    hook, state = build_recording_completion_hook(
        recording_mode_controller=controller, writer=writer
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-full-1",
            user_input="What is the capital of France?",
            assistant_content="Paris",
        )
    )

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    assert files[0].name == "req-full-1.json"
    payload = json.loads(files[0].read_text())
    assert payload["canonical_input"] == "What is the capital of France?"
    assert payload["presented_answer"] == "Paris"
    outcome = state.last_outcome()
    assert outcome is not None
    assert outcome.ok is True


def test_recording_off_writes_nothing(tmp_path: Path) -> None:
    controller = RecordingModeController()  # default OFF
    writer = LocalFilesystemRecordingWriter(base_dir=tmp_path, max_total_bytes=10_000)
    hook, state = build_recording_completion_hook(
        recording_mode_controller=controller, writer=writer
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-off-1",
            user_input="Q",
            assistant_content="A",
        )
    )

    assert list(tmp_path.glob("*.json")) == []
    assert state.last_outcome() is None


def test_recording_metadata_mode_omits_canonical_input_and_presented_answer(
    tmp_path: Path,
) -> None:
    controller = RecordingModeController()
    controller.apply_mode(RecordingMode.METADATA)
    writer = LocalFilesystemRecordingWriter(base_dir=tmp_path, max_total_bytes=10_000)
    hook, _state = build_recording_completion_hook(
        recording_mode_controller=controller,
        writer=writer,
        metadata_fields_provider=lambda context: {"model_identity": context.model_key},
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-meta-1",
            user_input="Secret question",
            assistant_content="Secret answer",
        )
    )

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    payload = json.loads(files[0].read_text())
    assert payload["canonical_input"] is None
    assert payload["presented_answer"] is None
    assert payload["metadata_fields"]["model_identity"] == "main.test-model"


def test_a_write_failure_degrades_the_composition_state_instead_of_raising(
    tmp_path: Path,
) -> None:
    controller = RecordingModeController()
    controller.apply_mode(RecordingMode.FULL)
    writer = LocalFilesystemRecordingWriter(base_dir=tmp_path, max_total_bytes=1)
    hook, state = build_recording_completion_hook(
        recording_mode_controller=controller, writer=writer
    )

    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-quota-1",
            user_input="Q",
            assistant_content="A" * 500,
        )
    )

    assert list(tmp_path.glob("*.json")) == []
    outcome = state.last_outcome()
    assert outcome is not None
    assert outcome.ok is False
    assert outcome.degraded_reason is not None
    assert "RecordingQuotaExceeded" in outcome.degraded_reason


def test_judge_evidence_is_written_to_a_distinct_file_with_real_provenance(
    tmp_path: Path,
) -> None:
    controller = RecordingModeController()
    controller.apply_mode(RecordingMode.FULL)
    writer = LocalFilesystemRecordingWriter(base_dir=tmp_path, max_total_bytes=10_000)
    record_judge_evidence, state = build_judge_evidence_recorder(writer=writer)

    record_judge_evidence(
        request_id="req-judge-1",
        recording_mode=RecordingMode.FULL,
        model_identity="main.test-model",
        judge_role="main_self",
        rubric_id="live_conversation_general_quality_v1",
        prompt="the full judge prompt text",
        recommendation="accept",
        confidence=0.9,
        token_usage=42,
        latency_ms=123,
        execution_state="completed",
    )

    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    assert files[0].name == "req-judge-1-judge-evidence.json"
    payload = json.loads(files[0].read_text())
    fields = payload["metadata_fields"]
    assert fields["artifact_kind"] == "judge_run_evidence"
    assert fields["model_identity"] == "main.test-model"
    assert fields["rubric_id"] == "live_conversation_general_quality_v1"
    assert fields["recommendation"] == "accept"
    assert fields["token_usage"] == 42
    assert fields["latency_ms"] == 123
    assert fields["cost_estimate_available"] is False
    assert fields["seed_pinned"] is False
    assert fields["seed"] == "unpinned"
    assert fields["config_digest_sha512"] == "unavailable"
    assert "prompt_digest_sha512" in fields
    # The raw prompt text itself is never persisted, only its digest.
    assert "the full judge prompt text" not in json.dumps(payload)
    assert payload["canonical_input"] is None
    assert state.last_outcome() is not None
    assert state.last_outcome().ok is True  # type: ignore[union-attr]


def test_judge_evidence_never_collides_with_the_turn_level_recording_file(
    tmp_path: Path,
) -> None:
    """Both Hooks share the *same* request_id but write into different
    Writer instances/subdirectories — proving they never contend on, or
    overwrite, each other's file."""
    controller = RecordingModeController()
    controller.apply_mode(RecordingMode.FULL)
    turn_writer = LocalFilesystemRecordingWriter(
        base_dir=tmp_path / "evaluations", max_total_bytes=10_000
    )
    evidence_writer = LocalFilesystemRecordingWriter(
        base_dir=tmp_path / "evidence", max_total_bytes=10_000
    )
    turn_hook, _ = build_recording_completion_hook(
        recording_mode_controller=controller, writer=turn_writer
    )
    record_judge_evidence, _ = build_judge_evidence_recorder(writer=evidence_writer)

    turn_hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-shared-1",
            user_input="Q",
            assistant_content="A",
        )
    )
    record_judge_evidence(
        request_id="req-shared-1",
        recording_mode=RecordingMode.FULL,
        model_identity="main.test-model",
        judge_role="main_self",
        rubric_id="r1",
        prompt="p",
        recommendation="accept",
        confidence=0.5,
        token_usage=1,
        latency_ms=1,
        execution_state="completed",
    )

    assert [p.name for p in (tmp_path / "evaluations").glob("*.json")] == ["req-shared-1.json"]
    assert [p.name for p in (tmp_path / "evidence").glob("*.json")] == [
        "req-shared-1-judge-evidence.json"
    ]


def test_recording_mode_is_frozen_at_hook_invocation_time(tmp_path: Path) -> None:
    """A live Mode toggle mid-call cannot retroactively change what this
    one already-invoked Hook call does — it reads the Mode exactly once."""
    controller = RecordingModeController()
    controller.apply_mode(RecordingMode.OFF)
    writer = LocalFilesystemRecordingWriter(base_dir=tmp_path, max_total_bytes=10_000)
    hook, _state = build_recording_completion_hook(
        recording_mode_controller=controller, writer=writer
    )

    # Simulate: by the time this Hook call actually runs, Mode has already
    # moved to FULL — this call must reflect whatever it reads *now*, at
    # its own single read point, not some earlier or later snapshot.
    controller.apply_mode(RecordingMode.FULL)
    hook(
        JudgeCompletionContext(
            model_key="main.test-model",
            request_id="req-mode-1",
            user_input="Q",
            assistant_content="A",
        )
    )

    assert list(tmp_path.glob("*.json")) == [tmp_path / "req-mode-1.json"]
