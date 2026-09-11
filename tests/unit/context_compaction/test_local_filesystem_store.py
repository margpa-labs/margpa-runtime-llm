"""CL-P9-3-B: Local Filesystem Store -- Digest, Restart Read, Corruption, CAS.

Mandatory Hard Evidence #10 (Sabotage detects a defect, Byte-identical
restore, re-PASS) is exercised for the Store's own Digest Gate in
`test_sabotage_regression.py`; this file proves the Store's normal-path
Digest/Restart/Corruption contract in isolation first.
"""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.context_compaction.local_filesystem_compaction_store import (
    LocalFilesystemCompactionStore,
)
from margpa_runtime_llm.modules.context_compaction.domain.artifacts import (
    ActiveContextProjection,
    CompactionAttempt,
    CompactionAttemptState,
)
from margpa_runtime_llm.modules.context_compaction.domain.errors import (
    ContextCompactionDomainError,
    ContextCompactionDomainErrorCode,
)
from margpa_runtime_llm.modules.context_compaction.domain.identity import (
    DEFAULT_BRANCH_ID,
    CompactionAttemptId,
    CompactionPlanId,
    ContextActionId,
    SnapshotId,
)
from margpa_runtime_llm.modules.conversation.domain.identity import ConversationId

_NOW = datetime.now(UTC)


def _attempt(
    *, attempt_id: str = "attempt-1", state: CompactionAttemptState = CompactionAttemptState.PLANNED
) -> CompactionAttempt:
    terminal = state in (
        CompactionAttemptState.COMPLETED,
        CompactionAttemptState.FAILED,
        CompactionAttemptState.REJECTED,
        CompactionAttemptState.CANCELLED,
        CompactionAttemptState.CONFLICTED,
        CompactionAttemptState.ROLLED_BACK,
        CompactionAttemptState.INTERRUPTED_BY_RESTART,
    )
    return CompactionAttempt(
        attempt_id=CompactionAttemptId(value=attempt_id),
        plan_id=CompactionPlanId(value="plan-1"),
        action_id=ContextActionId(value="action-1"),
        snapshot_id=SnapshotId(value="snapshot-1"),
        conversation_id=ConversationId(value="conv-1"),
        branch_id=DEFAULT_BRANCH_ID,
        state=state,
        requested_at=_NOW,
        updated_at=_NOW,
        terminal_reason="done" if terminal else None,
    )


def test_load_missing_artifact_returns_none_not_an_exception(tmp_path: Path) -> None:
    store = LocalFilesystemCompactionStore(base_dir=tmp_path)
    assert store.load_compaction_attempt(CompactionAttemptId(value="never-saved")) is None


def test_save_then_load_round_trips_exactly(tmp_path: Path) -> None:
    store = LocalFilesystemCompactionStore(base_dir=tmp_path)
    attempt = _attempt()
    store.save_compaction_attempt(attempt)
    loaded = store.load_compaction_attempt(attempt.attempt_id)
    assert loaded == attempt


def test_restart_read_lists_only_non_terminal_attempts_for_the_right_conversation_and_branch(
    tmp_path: Path,
) -> None:
    store = LocalFilesystemCompactionStore(base_dir=tmp_path)
    non_terminal = _attempt(attempt_id="attempt-non-terminal", state=CompactionAttemptState.PLANNED)
    terminal = _attempt(attempt_id="attempt-terminal", state=CompactionAttemptState.COMPLETED)
    store.save_compaction_attempt(non_terminal)
    store.save_compaction_attempt(terminal)
    found = store.list_non_terminal_attempts(
        ConversationId(value="conv-1"), DEFAULT_BRANCH_ID
    )
    assert [a.attempt_id.value for a in found] == ["attempt-non-terminal"]


def test_digest_mismatch_on_disk_is_detected_as_corruption(tmp_path: Path) -> None:
    store = LocalFilesystemCompactionStore(base_dir=tmp_path)
    attempt = _attempt()
    store.save_compaction_attempt(attempt)
    target = tmp_path / "attempts" / "attempt-1.json"
    envelope = json.loads(target.read_text())
    envelope["digest_sha512"] = "f" * 128
    target.write_text(json.dumps(envelope))
    with pytest.raises(ContextCompactionDomainError) as excinfo:
        store.load_compaction_attempt(attempt.attempt_id)
    assert excinfo.value.code is ContextCompactionDomainErrorCode.ARTIFACT_DIGEST_MISMATCH


def test_tampered_body_is_detected_via_digest_even_though_json_is_still_valid(
    tmp_path: Path,
) -> None:
    """A tamper that edits the body WITHOUT updating the digest (the realistic
    threat model -- a partial/manual edit, not a coordinated re-sign) must
    still be caught, not just a manually-corrupted digest field."""

    store = LocalFilesystemCompactionStore(base_dir=tmp_path)
    attempt = _attempt()
    store.save_compaction_attempt(attempt)
    target = tmp_path / "attempts" / "attempt-1.json"
    envelope = json.loads(target.read_text())
    envelope["body"]["state"] = "completed"  # tamper the state without recomputing the digest
    target.write_text(json.dumps(envelope))
    with pytest.raises(ContextCompactionDomainError) as excinfo:
        store.load_compaction_attempt(attempt.attempt_id)
    assert excinfo.value.code is ContextCompactionDomainErrorCode.ARTIFACT_DIGEST_MISMATCH


def test_malformed_json_on_disk_is_a_typed_corruption_error_not_a_raw_exception(
    tmp_path: Path,
) -> None:
    store = LocalFilesystemCompactionStore(base_dir=tmp_path)
    attempt = _attempt()
    store.save_compaction_attempt(attempt)
    target = tmp_path / "attempts" / "attempt-1.json"
    target.write_text("{not valid json")
    with pytest.raises(ContextCompactionDomainError) as excinfo:
        store.load_compaction_attempt(attempt.attempt_id)
    assert excinfo.value.code is ContextCompactionDomainErrorCode.ARTIFACT_CORRUPT


def test_active_projection_cas_accepts_only_the_expected_revision(tmp_path: Path) -> None:
    store = LocalFilesystemCompactionStore(base_dir=tmp_path)
    cid = ConversationId(value="conv-1")
    assert store.load_active_context_projection(cid, DEFAULT_BRANCH_ID) is None

    first = ActiveContextProjection(
        conversation_id=cid,
        branch_id=DEFAULT_BRANCH_ID,
        active_projection_revision=1,
        structured_context_id=None,
        source_conversation_revision=1,
        updated_at=_NOW,
    )
    assert (
        store.compare_and_swap_active_context_projection(
            conversation_id=cid,
            branch_id=DEFAULT_BRANCH_ID,
            expected_active_projection_revision=0,
            new_projection=first,
        )
        is True
    )
    # A second writer racing with the same stale expectation must lose.
    assert (
        store.compare_and_swap_active_context_projection(
            conversation_id=cid,
            branch_id=DEFAULT_BRANCH_ID,
            expected_active_projection_revision=0,
            new_projection=first,
        )
        is False
    )
    loaded = store.load_active_context_projection(cid, DEFAULT_BRANCH_ID)
    assert loaded is not None and loaded.active_projection_revision == 1


def test_active_projection_cas_rejects_a_projection_for_a_different_conversation(
    tmp_path: Path,
) -> None:
    store = LocalFilesystemCompactionStore(base_dir=tmp_path)
    mismatched = ActiveContextProjection(
        conversation_id=ConversationId(value="conv-other"),
        branch_id=DEFAULT_BRANCH_ID,
        active_projection_revision=1,
        structured_context_id=None,
        source_conversation_revision=1,
        updated_at=_NOW,
    )
    with pytest.raises(ContextCompactionDomainError) as excinfo:
        store.compare_and_swap_active_context_projection(
            conversation_id=ConversationId(value="conv-1"),
            branch_id=DEFAULT_BRANCH_ID,
            expected_active_projection_revision=0,
            new_projection=mismatched,
        )
    assert excinfo.value.code is ContextCompactionDomainErrorCode.INVALID_LIFECYCLE
