"""P6-CODEX-004: Atomic Write, Quota, Failure, Degraded, Restart Recovery
for LocalFilesystemRecordingWriter. Uses a short pytest `tmp_path` Fixture
(Project-local temp root, never `/tmp` directly) throughout."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.runtime_observability.local_filesystem_recording_writer import (
    LocalFilesystemRecordingWriter,
    RecordingPathRejected,
    RecordingQuotaExceeded,
    RecordingWriteFailure,
)
from margpa_runtime_llm.modules.runtime_observability.domain.recording import (
    MetadataValue,
    RecordingMode,
    SafeRecordingEnvelope,
)


def _envelope(
    *,
    request_id: str = "req-1",
    metadata_fields: dict[str, MetadataValue] | None = None,
    **fields: object,
) -> SafeRecordingEnvelope:
    return SafeRecordingEnvelope(
        request_id=request_id,
        timestamp="2026-08-23T06:00:00Z",
        mode=RecordingMode.METADATA,
        metadata_fields=metadata_fields if metadata_fields is not None else {"latency_ms": 100},
        **fields,  # type: ignore[arg-type]
    )


def test_atomic_write_produces_one_complete_readable_file(tmp_path: Path) -> None:
    writer = LocalFilesystemRecordingWriter(
        base_dir=tmp_path / "evaluations", max_total_bytes=10_000
    )
    writer.write(envelope=_envelope())

    files = list((tmp_path / "evaluations").glob("*.json"))
    assert len(files) == 1
    assert files[0].name == "req-1.json"
    decoded = json.loads(files[0].read_text())
    assert decoded["request_id"] == "req-1"
    # No leftover temp file after a successful write.
    assert list((tmp_path / "evaluations").glob(".*.tmp-*")) == []


def test_no_partial_or_temp_file_leaks_into_the_directory_listing(tmp_path: Path) -> None:
    base = tmp_path / "evaluations"
    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    writer.write(envelope=_envelope(request_id="req-a"))
    writer.write(envelope=_envelope(request_id="req-b"))

    # P6-CODEX-022: `.write.lock` is an expected, permanent cross-process
    # lock file living alongside the records — it is not a leaked temp/
    # partial artifact, so it is excluded from this "clean listing" check
    # rather than asserted away.
    names = sorted(p.name for p in base.iterdir() if p.name != ".write.lock")
    assert names == ["req-a.json", "req-b.json"]
    assert (base / ".write.lock").is_file()


def test_quota_exceeded_rejects_the_write_without_partial_state(tmp_path: Path) -> None:
    base = tmp_path / "evaluations"
    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=1)
    with pytest.raises(RecordingQuotaExceeded):
        writer.write(envelope=_envelope())
    assert list(base.glob("*.json")) == []
    assert list(base.glob(".*.tmp-*")) == []


def test_quota_accounts_for_existing_files_across_writer_instances(tmp_path: Path) -> None:
    base = tmp_path / "evaluations"
    first_writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    first_writer.write(envelope=_envelope(request_id="req-first"))
    existing_size = next(base.glob("*.json")).stat().st_size

    # A quota just barely too small for a second record of the same size,
    # given what a *fresh* Writer instance (Restart Recovery) already sees
    # on disk from before.
    second_writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=existing_size + 1)
    with pytest.raises(RecordingQuotaExceeded):
        second_writer.write(envelope=_envelope(request_id="req-second"))
    assert sorted(p.name for p in base.glob("*.json")) == ["req-first.json"]


def test_write_failure_on_unwritable_directory_raises_recording_write_failure_fail_closed(
    tmp_path: Path,
) -> None:
    base = tmp_path / "evaluations"
    base.mkdir()
    base.chmod(stat.S_IREAD | stat.S_IEXEC)  # read+execute only, no write
    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    try:
        with pytest.raises(RecordingWriteFailure):
            writer.write(envelope=_envelope())
    finally:
        base.chmod(stat.S_IRWXU)  # restore so pytest can clean up tmp_path


def test_restart_recovery_a_fresh_writer_instance_sees_and_extends_prior_records(
    tmp_path: Path,
) -> None:
    base = tmp_path / "evaluations"
    LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000).write(
        envelope=_envelope(request_id="req-before-restart")
    )
    # A brand-new Writer instance, as a process restart would create.
    restarted = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    restarted.write(envelope=_envelope(request_id="req-after-restart"))

    names = sorted(p.name for p in base.glob("*.json"))
    assert names == ["req-after-restart.json", "req-before-restart.json"]


def test_orphan_temp_file_old_enough_to_be_a_crash_artifact_is_pruned(tmp_path: Path) -> None:
    """P6-CODEX-022: pruning is now age-gated (a fresh temp file could
    belong to another in-flight Writer sharing this directory) — an old
    temp file, simulated here via `os.utime`, is still pruned."""
    base = tmp_path / "evaluations"
    base.mkdir()
    orphan = base / ".req-crashed.json.tmp-deadbeef"
    orphan.write_bytes(b"partial garbage")
    old_time = os.stat(orphan).st_mtime - 3600
    os.utime(orphan, (old_time, old_time))

    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    writer.write(envelope=_envelope(request_id="req-after-crash"))

    assert not orphan.exists()
    assert sorted(p.name for p in base.glob("*.json")) == ["req-after-crash.json"]


def test_fresh_temp_file_is_not_pruned_as_an_orphan(tmp_path: Path) -> None:
    """P6-CODEX-022: a temp file created moments ago (as if by another
    Writer instance/process mid-write on the same directory) must survive
    this Writer's own pruning pass — only a genuinely old temp file is
    assumed to be a crash artifact."""
    base = tmp_path / "evaluations"
    base.mkdir()
    fresh = base / ".req-in-flight.json.tmp-cafef00d"
    fresh.write_bytes(b"still being written by someone else")

    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    writer.write(envelope=_envelope(request_id="req-concurrent"))

    assert fresh.exists()


def test_hardlinked_existing_json_entry_is_rejected_fail_closed(tmp_path: Path) -> None:
    """P6-CODEX-022: a Hardlink to a "recorded" file would let its content
    be mutated through the other path entirely — quota scanning must fail
    closed rather than silently trust it as an ordinary immutable record."""
    base = tmp_path / "evaluations"
    base.mkdir()
    original = base / "req-1.json"
    original.write_text('{"request_id": "req-1"}')
    hardlink = base / "req-1-hardlink.json"
    os.link(original, hardlink)

    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope(request_id="req-2"))


def test_symlinked_existing_json_entry_is_rejected_fail_closed(tmp_path: Path) -> None:
    base = tmp_path / "evaluations"
    base.mkdir()
    outside_target = tmp_path / "outside.json"
    outside_target.write_text('{"request_id": "outside"}')
    symlinked_entry = base / "req-1.json"
    symlinked_entry.symlink_to(outside_target)

    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope(request_id="req-2"))


def test_symlinked_intermediate_component_under_containment_root_is_rejected(
    tmp_path: Path,
) -> None:
    """P6-CODEX-022: only the final `base_dir` was checked before this
    Rework — a planted Symlink at an intermediate component (e.g. the
    per-scope directory) between the Authorized Containment Root and
    `base_dir` must be detected too."""
    root = tmp_path / "runtime-data"
    root.mkdir()
    real_scope_dir = tmp_path / "real-scope-elsewhere"
    real_scope_dir.mkdir()
    (root / "scope-a").symlink_to(real_scope_dir, target_is_directory=True)
    base = root / "scope-a" / "evaluations"

    writer = LocalFilesystemRecordingWriter(
        base_dir=base, max_total_bytes=10_000, containment_root=root
    )
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope())
    assert list(real_scope_dir.glob("**/*.json")) == []


def test_symlinked_intermediate_component_pointing_inside_root_is_rejected(
    tmp_path: Path,
) -> None:
    """P6-CODEX-028 (Fourth Rework): the previous check derived its
    "components to inspect" from `base_dir.resolve()` — the already
    Symlink-followed destination. If a Symlinked intermediate component's
    TARGET still happens to live inside the Containment Root,
    `base_dir.resolve().relative_to(root)` still succeeds (the resolved
    destination genuinely is under root), so the old traversal-escape
    check never fired, and it went on to inspect only the resolved
    destination's own components — never the actual symlinked lexical
    path — so the swap went completely undetected. This differs from
    `test_symlinked_intermediate_component_under_containment_root_is_
    rejected` above, whose Symlink target lives OUTSIDE root entirely (a
    case the old check already caught for the wrong reason)."""
    root = tmp_path / "runtime-data"
    root.mkdir()
    real_scope_dir = root / "scope-b"  # a genuine, different directory INSIDE root
    real_scope_dir.mkdir()
    (root / "scope-a").symlink_to(real_scope_dir, target_is_directory=True)
    base = root / "scope-a" / "evaluations"

    writer = LocalFilesystemRecordingWriter(
        base_dir=base, max_total_bytes=10_000, containment_root=root
    )
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope())
    assert list(real_scope_dir.glob("**/*.json")) == []


def test_symlinked_write_lock_file_is_rejected(tmp_path: Path) -> None:
    """P6-CODEX-028 (Fourth Rework): `.write.lock` itself was previously
    opened with no Symlink/regular-file/Hardlink/owner scrutiny at all,
    unlike every other existing path this adapter touches."""
    base = tmp_path / "evaluations"
    base.mkdir()
    outside_target = tmp_path / "outside-lock-target"
    outside_target.write_text("not a lock file")
    (base / ".write.lock").symlink_to(outside_target)

    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope())
    assert outside_target.read_text() == "not a lock file"


def test_hardlinked_write_lock_file_is_rejected(tmp_path: Path) -> None:
    base = tmp_path / "evaluations"
    base.mkdir()
    other_file = tmp_path / "other-file"
    other_file.write_text("x")
    os.link(other_file, base / ".write.lock")

    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope())


def test_hardlinked_target_json_file_is_rejected(tmp_path: Path) -> None:
    """P6-CODEX-028 (Fourth Rework): the target file about to be
    overwritten was explicitly EXCLUDED from `_current_total_bytes`'s own
    Hardlink scan (to avoid double-counting it against the quota it is
    itself replacing) — which meant its own Hardlink count was never
    checked by anything at all, unlike every other existing `*.json`
    entry."""
    base = tmp_path / "evaluations"
    base.mkdir()
    envelope = _envelope()
    other_file = tmp_path / "other-file"
    other_file.write_text("x")
    os.link(other_file, base / f"{envelope.request_id}.json")

    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=envelope)


def test_base_dir_outside_containment_root_is_rejected(tmp_path: Path) -> None:
    root = tmp_path / "runtime-data"
    root.mkdir()
    outside_base = tmp_path / "outside-root" / "evaluations"

    writer = LocalFilesystemRecordingWriter(
        base_dir=outside_base, max_total_bytes=10_000, containment_root=root
    )
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope())


def test_containment_root_allows_a_genuine_nested_base_dir(tmp_path: Path) -> None:
    root = tmp_path / "runtime-data"
    base = root / "persistent" / "scope-a" / "evaluations"

    writer = LocalFilesystemRecordingWriter(
        base_dir=base, max_total_bytes=10_000, containment_root=root
    )
    writer.write(envelope=_envelope())

    assert list(base.glob("*.json"))


def test_two_writer_instances_sharing_a_directory_serialize_via_cross_process_lock(
    tmp_path: Path,
) -> None:
    """P6-CODEX-022: the in-process `Lock` alone only protects one Writer
    object — two independent instances (as two Threads/Processes each
    owning their own Writer would be) pointed at the same directory must
    still never interleave their quota-check-then-write critical sections."""
    import threading
    import time as time_module

    base = tmp_path / "evaluations"
    writer_a = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    writer_b = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    base.mkdir()

    entered: list[str] = []
    real_prune_a = writer_a._prune_orphan_temp_files
    release_b = threading.Event()

    def _slow_prune(base_fd: int) -> None:
        entered.append("a-entered")
        assert release_b.wait(2.0)
        time_module.sleep(0.05)
        real_prune_a(base_fd)

    writer_a._prune_orphan_temp_files = _slow_prune  # type: ignore[method-assign]

    thread_a = threading.Thread(
        target=lambda: writer_a.write(envelope=_envelope(request_id="req-a"))
    )
    thread_a.start()
    deadline = time_module.monotonic() + 2.0
    while not entered and time_module.monotonic() < deadline:
        time_module.sleep(0.005)
    assert entered == ["a-entered"]

    release_b.set()
    writer_b.write(envelope=_envelope(request_id="req-b"))
    thread_a.join(2.0)

    assert sorted(p.name for p in base.glob("*.json")) == ["req-a.json", "req-b.json"]


def test_max_total_bytes_must_be_positive() -> None:
    with pytest.raises(ValueError, match="positive"):
        LocalFilesystemRecordingWriter(base_dir=Path("unused"), max_total_bytes=0)


@pytest.mark.parametrize(
    "request_id",
    [
        "../escape",
        "a/b",
        "/etc/passwd",
        "..",
        ".hidden",
        "trailing/../traversal",
    ],
)
def test_path_traversal_and_unsafe_request_ids_are_rejected_outright(
    tmp_path: Path, request_id: str
) -> None:
    base = tmp_path / "evaluations"
    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope(request_id=request_id))
    # Never partially escapes: nothing was created outside (or inside) base.
    assert not base.exists() or list(base.glob("*.json")) == []


def test_empty_request_id_is_already_rejected_one_layer_up_by_the_envelope() -> None:
    with pytest.raises(Exception, match="request_id"):
        SafeRecordingEnvelope(
            request_id="",
            timestamp="2026-08-23T06:00:00Z",
            mode=RecordingMode.METADATA,
            metadata_fields={},
        )


def test_symlinked_base_dir_is_rejected(tmp_path: Path) -> None:
    real_target = tmp_path / "real-target"
    real_target.mkdir()
    symlinked_base = tmp_path / "evaluations-symlink"
    symlinked_base.symlink_to(real_target, target_is_directory=True)

    writer = LocalFilesystemRecordingWriter(base_dir=symlinked_base, max_total_bytes=10_000)
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope())
    assert list(real_target.glob("*.json")) == []


def test_replacing_an_existing_request_id_subtracts_the_old_size_from_quota(
    tmp_path: Path,
) -> None:
    base = tmp_path / "evaluations"
    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    writer.write(envelope=_envelope(request_id="req-same", metadata_fields={"n": 1}))
    first_size = next(base.glob("*.json")).stat().st_size

    # A quota exactly equal to one record's size: replacing the SAME
    # request_id must not double-count the about-to-be-replaced file.
    tight_writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=first_size)
    tight_writer.write(envelope=_envelope(request_id="req-same", metadata_fields={"n": 2}))

    files = list(base.glob("*.json"))
    assert len(files) == 1
    assert json.loads(files[0].read_text())["metadata_fields"]["n"] == 2


def test_write_fsyncs_the_file_and_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = tmp_path / "evaluations"
    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    fsync_calls: list[int] = []
    real_fsync = os.fsync

    def _spy_fsync(fd: int) -> None:
        fsync_calls.append(fd)
        real_fsync(fd)

    monkeypatch.setattr("os.fsync", _spy_fsync)
    writer.write(envelope=_envelope())

    # One fsync for the written file's fd, one for the directory's fd.
    assert len(fsync_calls) == 2


def test_short_write_is_completed_by_looping_not_silently_truncated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P6-CODEX-022: `os.write()` returning fewer bytes than requested must
    not be treated as a complete write — the loop must keep writing the
    remainder rather than fsync/rename-ing a truncated payload."""
    base = tmp_path / "evaluations"
    real_write = os.write
    call_count = {"n": 0}

    def _short_write(fd: int, data: bytes) -> int:
        call_count["n"] += 1
        if call_count["n"] == 1 and len(data) > 1:
            return real_write(fd, data[:1])  # simulate a 1-byte short write
        return real_write(fd, data)

    monkeypatch.setattr(os, "write", _short_write)
    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    writer.write(envelope=_envelope(request_id="req-short-write"))

    files = list(base.glob("*.json"))
    assert len(files) == 1
    decoded = json.loads(files[0].read_text())
    assert decoded["request_id"] == "req-short-write"
    assert call_count["n"] > 1


def test_write_raises_if_os_write_makes_zero_progress(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    base = tmp_path / "evaluations"

    def _stuck_write(fd: int, data: bytes) -> int:
        return 0

    monkeypatch.setattr(os, "write", _stuck_write)
    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    with pytest.raises(RecordingWriteFailure):
        writer.write(envelope=_envelope())
    assert list(base.glob("*.json")) == []


def test_refuses_to_replace_a_non_regular_existing_path(tmp_path: Path) -> None:
    base = tmp_path / "evaluations"
    base.mkdir()
    target = base / "req-1.json"
    outside_target = tmp_path / "outside.txt"
    outside_target.write_text("not a recording")
    target.symlink_to(outside_target)

    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope(request_id="req-1"))
    assert outside_target.read_text() == "not a recording"


def test_intermediate_component_swapped_to_symlink_between_create_and_open_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P6-CODEX-038 (Fifth Rework): the previous version checked each
    intermediate component for a Symlink via a separate `lstat()` call and
    only later, via a separate `mkdir(parents=True)`/re-open by path,
    actually used it — a race could swap a just-created real directory for
    a Symlink in between the two. The `dir_fd` chain closes this because
    creating and then Symlink-safely opening the SAME component happen
    back-to-back relative to the same parent fd, with no intervening
    lexical path re-resolution. This test simulates the race directly
    (swapping the entry immediately after `os.mkdir` creates it, before
    this Writer's own subsequent `O_NOFOLLOW` open runs) to prove the walk
    still rejects it rather than trusting the pre-race state."""
    root = tmp_path / "runtime-data"
    root.mkdir()
    outside = tmp_path / "outside-scope"
    outside.mkdir()
    base = root / "scope-a" / "evaluations"

    real_mkdir = os.mkdir

    def _create_then_swap_to_symlink(
        path: str, mode: int = 0o777, *, dir_fd: int | None = None
    ) -> None:
        real_mkdir(path, mode, dir_fd=dir_fd)
        if path == "scope-a":
            os.rmdir(path, dir_fd=dir_fd)
            os.symlink(str(outside), path, target_is_directory=True, dir_fd=dir_fd)

    monkeypatch.setattr(os, "mkdir", _create_then_swap_to_symlink)
    writer = LocalFilesystemRecordingWriter(
        base_dir=base, max_total_bytes=10_000, containment_root=root
    )
    with pytest.raises(RecordingPathRejected):
        writer.write(envelope=_envelope())
    assert list(outside.glob("**/*.json")) == []


def test_rename_failure_cleans_up_the_temp_file_and_raises_write_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P6-CODEX-038 (Fifth Rework Fault Injection): a Replace-stage failure
    (disk error, cross-device rename, ...) must not leave a temp file
    behind, and must surface as a `RecordingWriteFailure` — never a
    silently-committed target."""
    base = tmp_path / "evaluations"
    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)

    def _failing_rename(
        src: str, dst: str, *, src_dir_fd: int | None = None, dst_dir_fd: int | None = None
    ) -> None:
        raise OSError("simulated rename failure")

    monkeypatch.setattr(os, "rename", _failing_rename)
    with pytest.raises(RecordingWriteFailure):
        writer.write(envelope=_envelope())

    assert list(base.glob("*.json")) == []
    assert list(base.glob(".*.tmp-*")) == []


def test_directory_fsync_failure_after_rename_raises_write_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """P6-CODEX-038 (Fifth Rework Fault Injection): the rename itself may
    succeed while the directory-durability fsync that follows it fails —
    this must still surface as a `RecordingWriteFailure`, not a silently
    "successful" write whose durability guarantee was never actually met."""
    base = tmp_path / "evaluations"
    base.mkdir()
    writer = LocalFilesystemRecordingWriter(base_dir=base, max_total_bytes=10_000)
    real_fsync = os.fsync
    rename_happened = {"done": False}

    real_rename = os.rename

    def _tracking_rename(
        src: str, dst: str, *, src_dir_fd: int | None = None, dst_dir_fd: int | None = None
    ) -> None:
        real_rename(src, dst, src_dir_fd=src_dir_fd, dst_dir_fd=dst_dir_fd)
        rename_happened["done"] = True

    def _failing_fsync_after_rename(fd: int) -> None:
        if rename_happened["done"]:
            raise OSError("simulated directory fsync failure")
        real_fsync(fd)

    monkeypatch.setattr(os, "rename", _tracking_rename)
    monkeypatch.setattr(os, "fsync", _failing_fsync_after_rename)
    with pytest.raises(RecordingWriteFailure):
        writer.write(envelope=_envelope())
