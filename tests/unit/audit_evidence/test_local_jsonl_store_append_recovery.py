"""LocalJsonlEvidenceStore append/receipt/recovery (P3-B-WU-002)."""

from __future__ import annotations

import os
import stat
import threading
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from margpa_runtime_llm.adapters.audit_evidence import local_jsonl_store as local_jsonl_store_module
from margpa_runtime_llm.adapters.audit_evidence.local_jsonl_store import (
    LocalJsonlEvidenceStore,
)
from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditEventEnvelope,
    AuditEventId,
    AuditEventKind,
    AuditEventProvenance,
    AuditRunId,
    CanonicalAuditEvent,
    EmptyEventPayload,
    EvidenceStoreError,
    EvidenceStoreErrorCode,
    canonicalize_event,
)

UTC_NOW = datetime(2026, 8, 21, 12, 0, 0, tzinfo=UTC)


def _canonical(event_id: str, run_id: str = "run-0001") -> CanonicalAuditEvent:
    envelope = AuditEventEnvelope(
        event_id=AuditEventId(value=event_id),
        run_id=AuditRunId(value=run_id),
        occurred_at_utc=UTC_NOW,
        source_component="conversation.generation",
        event_kind=AuditEventKind.RUNTIME_STARTED,
        provenance=AuditEventProvenance.SYSTEM_TRACE,
        safe_payload=EmptyEventPayload(),
    )
    return canonicalize_event(envelope)


def test_append_then_read_all_round_trips(tmp_path: Path) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    first = _canonical("event-0001")
    second = _canonical("event-0002")

    receipt_first = store.append(first)
    receipt_second = store.append(second)

    assert receipt_first.position == 0
    assert receipt_second.position == 1

    events = store.read_all(AuditRunId(value="run-0001"))
    assert [event.envelope.event_id.value for event in events] == [
        "event-0001",
        "event-0002",
    ]
    assert store.status().event_count == 2
    assert store.status().degraded is False


def test_append_rejects_duplicate_event_id(tmp_path: Path) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    store.append(_canonical("event-0001"))

    with pytest.raises(EvidenceStoreError) as excinfo:
        store.append(_canonical("event-0001"))
    assert excinfo.value.code is EvidenceStoreErrorCode.DUPLICATE_EVENT
    assert store.status().event_count == 1


def test_reopening_store_recovers_existing_valid_events(tmp_path: Path) -> None:
    first_open = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    first_open.append(_canonical("event-0001"))
    first_open.append(_canonical("event-0002"))

    second_open = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert second_open.status().event_count == 2
    # Duplicate detection survives a reopen (it is derived from the file,
    # not just in-process memory).
    with pytest.raises(EvidenceStoreError):
        second_open.append(_canonical("event-0001"))


def test_concurrent_append_produces_distinct_positions_and_no_loss(tmp_path: Path) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    thread_count = 8
    barrier = threading.Barrier(thread_count)
    positions: list[int] = []
    positions_lock = threading.Lock()

    def worker(index: int) -> None:
        barrier.wait()
        receipt = store.append(_canonical(f"event-{index:04d}"))
        with positions_lock:
            positions.append(receipt.position)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(thread_count)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sorted(positions) == list(range(thread_count))
    assert store.status().event_count == thread_count


def test_partial_tail_is_detected_and_excluded_without_truncation(tmp_path: Path) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    store.append(_canonical("event-0001"))

    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    before = segment_path.read_bytes()
    with open(segment_path, "ab") as handle:
        handle.write(b'{"envelope": {"incomplete"')  # no trailing newline

    after_corruption = segment_path.read_bytes()
    assert after_corruption.startswith(before)  # existing bytes untouched

    reopened = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    status = reopened.status()
    assert status.event_count == 1
    assert status.degraded is True
    assert status.degraded_reason_code == "partial_tail"

    # The file on disk is still exactly as corrupted — no auto-repair/truncation.
    assert segment_path.read_bytes() == after_corruption

    events = reopened.read_all(AuditRunId(value="run-0001"))
    assert [event.envelope.event_id.value for event in events] == ["event-0001"]


def test_reopened_store_after_partial_tail_still_rejects_duplicate_of_valid_event(
    tmp_path: Path,
) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    store.append(_canonical("event-0001"))
    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    with open(segment_path, "ab") as handle:
        handle.write(b'{"broken"')

    reopened = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    with pytest.raises(EvidenceStoreError) as excinfo:
        reopened.append(_canonical("event-0001"))
    assert excinfo.value.code is EvidenceStoreErrorCode.DUPLICATE_EVENT


# -- P3-CODEX-005: append() must write every byte it claims to have
# written, never silently accept a short `os.write()` as success --------


def test_zero_byte_os_write_is_a_failure_not_a_silent_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    monkeypatch.setattr(os, "write", lambda descriptor, data: 0)

    with pytest.raises(EvidenceStoreError) as excinfo:
        store.append(_canonical("event-0001"))
    assert excinfo.value.code is EvidenceStoreErrorCode.APPEND_FAILED
    assert store.status().event_count == 0

    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    assert not segment_path.exists() or segment_path.read_bytes() == b""


def test_short_os_write_is_completed_by_the_retry_loop(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    real_write = os.write
    call_count = 0

    def half_then_full_write(descriptor: int, data: bytes) -> int:
        nonlocal call_count
        call_count += 1
        if call_count == 1 and len(data) > 1:
            return real_write(descriptor, data[: len(data) // 2])
        return real_write(descriptor, data)

    monkeypatch.setattr(os, "write", half_then_full_write)

    receipt = store.append(_canonical("event-0001"))
    assert call_count >= 2  # the short first write forced a retry

    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    on_disk = segment_path.read_bytes()
    assert on_disk.endswith(b"\n")
    reopened = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert reopened.status() == store.status()
    events = reopened.read_all(AuditRunId(value="run-0001"))
    assert [event.envelope.event_id.value for event in events] == ["event-0001"]
    assert events[0].event_digest_sha512 == receipt.event_digest_sha512


def test_oserror_mid_write_fails_closed_and_leaves_no_valid_line_corrupted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    real_write = os.write
    call_count = 0

    def partial_then_raise(descriptor: int, data: bytes) -> int:
        nonlocal call_count
        call_count += 1
        if call_count == 1 and len(data) > 1:
            return real_write(descriptor, data[: len(data) // 2])
        raise OSError("simulated disk failure mid-write")

    monkeypatch.setattr(os, "write", partial_then_raise)

    with pytest.raises(EvidenceStoreError) as excinfo:
        store.append(_canonical("event-0001"))
    assert excinfo.value.code is EvidenceStoreErrorCode.APPEND_FAILED
    assert store.status().event_count == 0

    # The segment now has a corrupted (non-newline-terminated) tail from the
    # partial write; reopening must detect it as degraded, not as a valid
    # event, and must never truncate or repair it automatically — the same
    # contract already proven for a naturally corrupted tail.
    reopened = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    status = reopened.status()
    assert status.event_count == 0
    assert status.degraded is True


# -- P3-CODEX-004/005: Evidence event/segment capacity is finite and fails
# closed rather than growing an unbounded number of segments -----------


def test_reaching_the_per_segment_event_limit_rolls_over_to_a_new_segment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(local_jsonl_store_module, "MAX_EVENTS_PER_SEGMENT", 2)
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")

    first = store.append(_canonical("event-0001"))
    second = store.append(_canonical("event-0002"))
    third = store.append(_canonical("event-0003"))  # limit+1: forces rollover

    assert first.segment == second.segment == "segment-00000001.jsonl"
    assert third.segment == "segment-00000002.jsonl"
    assert third.position == 0

    segments_dir = tmp_path / "scope-a" / "segments"
    assert sorted(p.name for p in segments_dir.iterdir()) == [
        "segment-00000001.jsonl",
        "segment-00000002.jsonl",
    ]

    reopened = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert reopened.status().event_count == 3


def test_exceeding_the_segment_count_limit_fails_closed_with_capacity_exceeded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(local_jsonl_store_module, "MAX_EVENTS_PER_SEGMENT", 1)
    monkeypatch.setattr(local_jsonl_store_module, "MAX_SEGMENT_COUNT", 1)
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")

    store.append(_canonical("event-0001"))  # fills segment 1 (the only allowed segment)
    with pytest.raises(EvidenceStoreError) as excinfo:
        store.append(_canonical("event-0002"))  # would need segment 2: over the limit
    assert excinfo.value.code is EvidenceStoreErrorCode.CAPACITY_EXCEEDED
    assert store.status().event_count == 1


# -- P3-CODEX-008: dangling symlink root escape, post-failure receipt
# recoverability, receipt uniqueness across rollover, and oversized
# existing segments must all fail closed. --------------------------------


def test_dangling_symlink_segment_never_creates_a_file_outside_root(tmp_path: Path) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    outside_dir = tmp_path.parent / "outside-escape-target"
    outside_target = outside_dir / "escaped.jsonl"  # deliberately never created

    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    segment_path.symlink_to(outside_target)  # target does not exist: dangling

    with pytest.raises(EvidenceStoreError) as excinfo:
        store.append(_canonical("event-0001"))
    assert excinfo.value.code is EvidenceStoreErrorCode.APPEND_FAILED
    assert not outside_target.exists()  # O_NOFOLLOW must have refused to create it
    assert not outside_dir.exists()


def test_write_failure_then_successful_append_is_fully_recoverable_on_reopen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    real_write = os.write
    call_count = 0

    def fail_once(descriptor: int, data: bytes) -> int:
        nonlocal call_count
        call_count += 1
        if call_count == 1 and len(data) > 1:
            real_write(descriptor, data[: len(data) // 2])
            raise OSError("simulated disk failure mid-write")
        return real_write(descriptor, data)

    monkeypatch.setattr(os, "write", fail_once)
    with pytest.raises(EvidenceStoreError) as excinfo:
        store.append(_canonical("event-0001"))
    assert excinfo.value.code is EvidenceStoreErrorCode.APPEND_FAILED
    assert store.status().degraded is True  # the failure is visible immediately, not only on reopen

    monkeypatch.setattr(os, "write", real_write)
    receipt = store.append(_canonical("event-0002"))
    # Routed to a fresh segment, not the corrupted one.
    assert receipt.segment == "segment-00000002.jsonl"

    reopened = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    events = reopened.read_all(AuditRunId(value="run-0001"))
    assert [event.envelope.event_id.value for event in events] == ["event-0002"]
    assert reopened.status().degraded is True  # segment-1's corrupted tail is still on record


def test_rollover_receipt_ids_are_unique_across_segments(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(local_jsonl_store_module, "MAX_EVENTS_PER_SEGMENT", 1)
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")

    first = store.append(_canonical("event-0001"))  # segment 1, position 0
    second = store.append(_canonical("event-0002"))  # rolls to segment 2, position 0
    assert first.position == second.position == 0
    assert first.segment != second.segment
    assert first.receipt_id != second.receipt_id  # position alone would have collided


def test_oversized_existing_segment_is_rejected_without_reading_it_fully(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    store.append(_canonical("event-0001"))

    monkeypatch.setattr(local_jsonl_store_module, "MAX_SEGMENT_FILE_BYTES", 1)
    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.CAPACITY_EXCEEDED


# -- P3-CODEX-011: an in-use segment must never grow past
# MAX_SEGMENT_FILE_BYTES, discovered segment indices must stay within the
# store's own capacity contract, and the segments/ dir_fd chain must
# reject every intermediate component, not just the final one. ----------


def test_segment_byte_limit_triggers_rollover_before_writing_and_stays_recoverable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    first = store.append(_canonical("event-0001"))
    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    first_segment_bytes = segment_path.read_bytes()

    # The active segment can hold at most one more byte than it already
    # has — the second event (far larger than one byte) cannot fit, so it
    # must roll to a fresh segment instead of pushing segment 1 over the
    # ceiling.
    monkeypatch.setattr(
        local_jsonl_store_module, "MAX_SEGMENT_FILE_BYTES", len(first_segment_bytes) + 1
    )
    second = store.append(_canonical("event-0002"))

    assert first.segment == "segment-00000001.jsonl"
    assert second.segment == "segment-00000002.jsonl"
    assert second.position == 0
    # segment 1's existing bytes were never touched by the rollover decision.
    assert segment_path.read_bytes() == first_segment_bytes
    assert store.status().degraded is False

    reopened = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert reopened.status().degraded is False
    events = reopened.read_all(AuditRunId(value="run-0001"))
    assert [event.envelope.event_id.value for event in events] == [
        "event-0001",
        "event-0002",
    ]


def test_event_larger_than_a_fresh_empty_segment_is_capacity_exceeded_not_a_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(local_jsonl_store_module, "MAX_SEGMENT_FILE_BYTES", 10)
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")

    with pytest.raises(EvidenceStoreError) as excinfo:
        store.append(_canonical("event-0001"))
    assert excinfo.value.code is EvidenceStoreErrorCode.CAPACITY_EXCEEDED
    assert store.status().event_count == 0
    # A capacity refusal before any write is not a write failure.
    assert store.status().degraded is False


def test_out_of_range_existing_segment_index_is_rejected(tmp_path: Path) -> None:
    segments_dir = tmp_path / "scope-a" / "segments"
    segments_dir.mkdir(parents=True, mode=0o700)
    (segments_dir / "segment-99999999.jsonl").write_bytes(b"")

    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION


def test_degraded_highest_segment_at_index_ceiling_fails_closed_instead_of_rolling_over(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(local_jsonl_store_module, "MAX_SEGMENT_COUNT", 2)
    segments_dir = tmp_path / "scope-a" / "segments"
    segments_dir.mkdir(parents=True, mode=0o700)
    # No trailing newline: parses as a degraded partial tail.
    (segments_dir / "segment-00000002.jsonl").write_bytes(b'{"broken"')

    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.CAPACITY_EXCEEDED


def test_symlinked_scope_component_is_rejected_even_when_its_target_has_a_real_segments_dir(
    tmp_path: Path,
) -> None:
    outside_root = tmp_path.parent / "outside-scope-target"
    outside_segments = outside_root / "segments"
    outside_segments.mkdir(parents=True, mode=0o700)

    root = tmp_path / "root"
    root.mkdir(mode=0o700)
    (root / "scope-a").symlink_to(outside_root, target_is_directory=True)

    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=root, relative_root="", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION
    # Nothing was ever written through the symlinked intermediate component.
    assert list(outside_segments.iterdir()) == []


# -- P3-CODEX-012 Finding B: every Segment Leaf Open (Read *and* Append)
# must reject a Non-regular file without blocking, verify Identity/Type/
# Mode/Link on the already-open fd, and bound a Read even if the file
# grows after the initial `fstat`. -----------------------------------


def test_a_fifo_replacing_a_segment_is_rejected_at_reopen_without_blocking(
    tmp_path: Path,
) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    store.append(_canonical("event-0001"))

    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    segment_path.unlink()
    os.mkfifo(segment_path)

    # Would hang forever pre-fix if Reopen's discovery/read ever blocked
    # on the FIFO waiting for a peer.
    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION


def test_a_fifo_replacing_the_active_segment_makes_append_fail_without_blocking(
    tmp_path: Path,
) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    os.mkfifo(segment_path)

    # Would hang forever pre-fix if the O_WRONLY open on the FIFO ever
    # blocked waiting for a reader.
    with pytest.raises(EvidenceStoreError) as excinfo:
        store.append(_canonical("event-0001"))
    assert excinfo.value.code is EvidenceStoreErrorCode.APPEND_FAILED
    assert store.status().event_count == 0
    assert stat.S_ISFIFO(segment_path.lstat().st_mode)  # untouched, no data landed


def test_group_writable_segment_is_rejected(tmp_path: Path) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    store.append(_canonical("event-0001"))
    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    os.chmod(segment_path, 0o660)

    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION


def test_hard_linked_segment_is_rejected(tmp_path: Path) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    store.append(_canonical("event-0001"))
    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    hard_link_path = tmp_path / "hard-link-outside.jsonl"
    os.link(segment_path, hard_link_path)

    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION


def test_segment_read_is_bounded_even_if_size_grew_after_fstat(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    store.append(_canonical("event-0001"))
    segment_path = tmp_path / "scope-a" / "segments" / "segment-00000001.jsonl"
    real_size = segment_path.stat().st_size

    real_fstat = os.fstat

    def lying_fstat(fd: int) -> object:
        info = real_fstat(fd)
        if stat.S_ISREG(info.st_mode) and info.st_size == real_size:
            # Simulate a segment that was still empty at `fstat`-check
            # time and grew to its real size only afterward.
            return SimpleNamespace(
                st_mode=info.st_mode,
                st_uid=info.st_uid,
                st_nlink=info.st_nlink,
                st_size=0,
            )
        return info

    monkeypatch.setattr(os, "fstat", lying_fstat)
    monkeypatch.setattr(local_jsonl_store_module, "MAX_SEGMENT_FILE_BYTES", real_size - 1)

    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.CAPACITY_EXCEEDED
