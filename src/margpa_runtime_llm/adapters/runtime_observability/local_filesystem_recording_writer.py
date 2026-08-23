"""Local-only Filesystem `RecordingWriterPort` implementation (P6-CODEX-004,
hardened P6-CODEX-022 Third Rework, hardened P6-CODEX-038 Fifth Rework).

Writes each `SafeRecordingEnvelope` as one complete, atomically-renamed JSON
file under a caller-supplied directory (the caller decides the exact
`runtime_data/persistent/<scope>/{evaluations,experiments,evidence,feedback}/`
target — this adapter has no opinion about which sub-kind it is writing).

Restart Recovery is structural, not a separate mechanism: every write is a
single atomic rename (`os.rename`, POSIX-atomic and replace-on-collision on
the same filesystem), so a process crash mid-write can only ever leave
behind an orphaned `.tmp-*` file next to the target — never a half-written
target file a later reader could observe. `_prune_orphan_temp_files()`
clears those opportunistically on the writer's own next write, gated by a
minimum age (P6-CODEX-022) so it never mistakes another Writer's (this
process's, or another process's) just-created, not-yet-renamed temp file
for an orphan.

Cross-instance/cross-process safety (P6-CODEX-022): the in-process `Lock`
alone only serializes calls made through *this* Python object. An
`fcntl.flock` on a dedicated `.write.lock` file inside `base_dir` extends
that same critical section (quota check through atomic rename) across
every `LocalFilesystemRecordingWriter` instance — in this process or
another — pointed at the same directory.

dir_fd containment (P6-CODEX-038, Fifth Rework): every prior hardening
still validated Symlink/Hardlink/ownership by re-deriving a LEXICAL path
and re-opening it in a separate syscall from whatever check had just run
against it — a TOCTOU window between each check and the next path-based
use (another process, or a concurrent write to the same containment tree,
could swap a directory entry in that window). `_open_verified_base_dir_fd`
now walks from the Authorized `containment_root` down to `base_dir` as a
single chain of `dir_fd`-relative `open(..., O_NOFOLLOW, dir_fd=parent)`
calls — each component is opened (not merely stat'd) relative to its
already-verified parent directory's fd, so there is no lexical path left
to re-resolve, and therefore nothing for a race to swap out from under a
check. Every subsequent operation for this write (`.write.lock`, the temp
file, the target file, the quota scan, the atomic rename, the durability
fsync) is bound to that same verified fd via `dir_fd=`/`src_dir_fd=`/
`dst_dir_fd=`, never re-joining a path string and re-opening it.
"""

from __future__ import annotations

import contextlib
import errno
import fcntl
import os
import re
import stat
import threading
import time
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

from margpa_runtime_llm.modules.runtime_observability.domain.recording import (
    SafeRecordingEnvelope,
)

_SAFE_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")

# P6-CODEX-022: a legitimate in-flight write's own temp file is renamed
# within milliseconds of being created (no blocking I/O happens between
# `os.open(..., O_CREAT)` and `os.rename`) — an age this generous can only
# be reached by a temp file whose owning process crashed or was killed
# before it could rename or clean up.
_ORPHAN_TEMP_FILE_MIN_AGE_SECONDS = 300.0


class RecordingWriteFailure(Exception):
    """OS-level write failure (disk full, permission denied, missing parent
    that could not be created, etc.) — Fail-closed: the caller decides how
    to degrade (this adapter never retries or swallows the failure)."""


class RecordingQuotaExceeded(Exception):
    """The write would push the target directory's total size over the
    configured quota. The attempted write is rejected outright — no partial
    write, no eviction of older records."""


class RecordingPathRejected(Exception):
    """The `request_id`, `base_dir`, an intermediate path component, or an
    existing directory entry failed Path Safety validation (P6-CODEX-011,
    extended P6-CODEX-022/038): traversal (`/`, `..`), an absolute-looking
    segment, a `base_dir` (or any component between an Authorized
    Containment Root and it) that is a Symlink, a `base_dir` that is a
    Non-directory, or an existing `*.json` entry that is a Symlink,
    Hardlink, or otherwise not a plain regular file. Rejected outright,
    before any filesystem write is attempted — never sanitized/coerced."""


class LocalFilesystemRecordingWriter:
    def __init__(
        self,
        *,
        base_dir: Path,
        max_total_bytes: int,
        containment_root: Path | None = None,
    ) -> None:
        if max_total_bytes <= 0:
            raise ValueError("max_total_bytes must be a positive integer")
        self._base_dir = base_dir
        self._max_total_bytes = max_total_bytes
        self._containment_root = containment_root
        self._lock = threading.Lock()

    def write(self, *, envelope: SafeRecordingEnvelope) -> None:
        if not _SAFE_REQUEST_ID_PATTERN.match(envelope.request_id):
            raise RecordingPathRejected(
                f"unsafe request_id for a recording file name: {envelope.request_id!r}"
            )
        with self._lock:
            base_fd = self._open_verified_base_dir_fd()
            try:
                with self._cross_process_lock(base_fd):
                    self._prune_orphan_temp_files(base_fd)
                    payload = envelope.model_dump_json().encode("utf-8")
                    file_name = f"{envelope.request_id}.json"
                    self._reject_unsafe_existing_target(base_fd, file_name)
                    current_total = self._current_total_bytes(base_fd, exclude=file_name)
                    if current_total + len(payload) > self._max_total_bytes:
                        raise RecordingQuotaExceeded(
                            f"recording quota exceeded: {current_total} + {len(payload)} "
                            f"bytes > {self._max_total_bytes} byte limit"
                        )
                    tmp_name = f".{file_name}.tmp-{uuid4().hex}"
                    try:
                        fd = os.open(
                            tmp_name,
                            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                            0o600,
                            dir_fd=base_fd,
                        )
                        try:
                            self._write_all(fd, payload)
                            os.fsync(fd)
                        finally:
                            os.close(fd)
                        # POSIX `rename()` (what both `os.rename` and
                        # `os.replace` call on this platform) atomically
                        # replaces an existing destination — `os.replace`
                        # itself does not accept `dir_fd` on this platform,
                        # so `os.rename` (dir_fd-capable, and equivalent to
                        # `os.replace` on POSIX) is used directly.
                        os.rename(tmp_name, file_name, src_dir_fd=base_fd, dst_dir_fd=base_fd)
                        # Durability of the atomic rename itself (POSIX):
                        # fsync-ing the file alone guarantees its content
                        # survives a crash, but the directory entry pointing
                        # at it needs its own fsync to survive one too.
                        os.fsync(base_fd)
                    except OSError as exc:
                        with contextlib.suppress(OSError):
                            os.unlink(tmp_name, dir_fd=base_fd)
                        raise RecordingWriteFailure(f"could not write recording: {exc}") from exc
            finally:
                os.close(base_fd)

    @staticmethod
    def _write_all(fd: int, payload: bytes) -> None:
        """P6-CODEX-022: `os.write()` is permitted by POSIX to write fewer
        bytes than requested even for a regular local file (e.g. if a
        signal interrupts the call) — the previous single unchecked call
        could silently treat a Short Write as a complete one, letting
        `os.fsync`/`os.rename` durably commit a truncated JSON file. This
        loops until every byte is actually written, or raises if a write
        call makes zero progress (a genuine OS-level failure, surfaced to
        the caller's existing `OSError` handling)."""
        written = 0
        while written < len(payload):
            count = os.write(fd, payload[written:])
            if count <= 0:
                raise OSError(
                    f"short write: os.write() made no progress at {written}/{len(payload)} bytes"
                )
            written += count

    def _open_verified_base_dir_fd(self) -> int:
        if self._containment_root is not None:
            return self._open_dir_fd_chain_under_containment_root()
        return self._open_base_dir_fd_without_containment_root()

    def _open_dir_fd_chain_under_containment_root(self) -> int:
        """P6-CODEX-038 (Fifth Rework): replaces the previous approach of
        `lstat()`-checking each LEXICAL component and then separately
        `mkdir(parents=True)`-ing and re-opening `base_dir` by path — two
        more path-based re-resolutions after the check, each its own TOCTOU
        window. This walks from `containment_root` down to `base_dir` as
        one chain of `dir_fd`-relative opens: each component is created (if
        missing) and then opened with `O_NOFOLLOW` relative to its parent's
        already-open, already-verified fd — never by re-joining a path
        string. A Symlink planted at any component, at any time other than
        the exact instant this walk opens that component, is caught."""
        root = self._containment_root
        assert root is not None
        if not self._base_dir.is_absolute() or not root.is_absolute():
            raise RecordingPathRejected(
                f"recording base_dir and containment_root must both be absolute paths: "
                f"{self._base_dir}, {root}"
            )
        try:
            relative = self._base_dir.relative_to(root)
        except ValueError as exc:
            raise RecordingPathRejected(
                f"recording base_dir escapes the authorized containment root: "
                f"{self._base_dir} not under {root}"
            ) from exc
        if ".." in relative.parts:
            raise RecordingPathRejected(
                f"recording base_dir contains a parent-traversal component: {self._base_dir}"
            )
        try:
            os.makedirs(root, exist_ok=True)
        except OSError as exc:
            raise RecordingWriteFailure(
                f"could not create recording containment root: {exc}"
            ) from exc
        try:
            fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise RecordingPathRejected(
                    f"recording containment_root is a symlink: {root}"
                ) from exc
            raise RecordingWriteFailure(
                f"could not open recording containment root: {exc}"
            ) from exc
        try:
            for part in relative.parts:
                next_fd = self._descend_one_dir_fd_component(fd, part)
                os.close(fd)
                fd = next_fd
        except BaseException:
            os.close(fd)
            raise
        return fd

    @staticmethod
    def _descend_one_dir_fd_component(parent_fd: int, name: str) -> int:
        try:
            os.mkdir(name, dir_fd=parent_fd)
        except FileExistsError:
            pass
        except OSError as exc:
            raise RecordingWriteFailure(
                f"could not create recording directory component {name!r}: {exc}"
            ) from exc
        try:
            return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=parent_fd)
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise RecordingPathRejected(
                    f"recording path component is a symlink: {name}"
                ) from exc
            if exc.errno == errno.ENOTDIR:
                raise RecordingPathRejected(
                    f"recording path component is not a directory: {name}"
                ) from exc
            raise RecordingWriteFailure(
                f"could not open recording directory component {name!r}: {exc}"
            ) from exc

    def _open_base_dir_fd_without_containment_root(self) -> int:
        if self._base_dir.is_symlink():
            raise RecordingPathRejected(
                f"recording base_dir must not be a symlink: {self._base_dir}"
            )
        try:
            self._base_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise RecordingWriteFailure(f"could not create recording directory: {exc}") from exc
        try:
            return os.open(self._base_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError as exc:
            if exc.errno in (errno.ELOOP, errno.ENOTDIR):
                raise RecordingPathRejected(
                    f"recording base_dir is not a real directory: {self._base_dir}"
                ) from exc
            raise RecordingWriteFailure(f"could not open recording base_dir: {exc}") from exc

    @staticmethod
    def _reject_unsafe_existing_target(base_fd: int, file_name: str) -> None:
        """P6-CODEX-022, hardened P6-CODEX-028/038: `lstat()` (never
        `stat()`/`exists()`, and now bound to `base_fd` rather than a
        re-resolved path) inspects the directory entry itself, exactly like
        `_current_total_bytes` does for every other entry."""
        try:
            lstat_result = os.stat(file_name, dir_fd=base_fd, follow_symlinks=False)
        except FileNotFoundError:
            return
        if not stat.S_ISREG(lstat_result.st_mode):
            raise RecordingPathRejected(
                f"refusing to replace a non-regular existing path: {file_name}"
            )
        if lstat_result.st_nlink > 1:
            raise RecordingPathRejected(
                f"refusing to replace a hardlinked existing path: {file_name}"
            )

    @staticmethod
    def _current_total_bytes(base_fd: int, *, exclude: str | None = None) -> int:
        total = 0
        for entry in os.scandir(base_fd):
            if not entry.name.endswith(".json") or entry.name == exclude:
                continue
            # P6-CODEX-022: Fail-closed on any existing entry that is not a
            # genuine, single-hardlinked regular file — a Symlink could
            # point outside the sandbox (its target's size, or worse, would
            # silently enter quota accounting); a Hardlink lets content
            # thought "recorded and immutable" be mutated through another
            # path entirely. `entry.stat(follow_symlinks=False)` inspects
            # the entry itself, never its Symlink target.
            lstat_result = entry.stat(follow_symlinks=False)
            if not stat.S_ISREG(lstat_result.st_mode):
                raise RecordingPathRejected(
                    f"refusing to scan a non-regular existing entry: {entry.name}"
                )
            if lstat_result.st_nlink > 1:
                raise RecordingPathRejected(
                    f"refusing to scan a hardlinked existing entry: {entry.name}"
                )
            total += lstat_result.st_size
        return total

    @staticmethod
    def _prune_orphan_temp_files(base_fd: int) -> None:
        now = time.time()
        for entry in os.scandir(base_fd):
            if not (entry.name.startswith(".") and ".tmp-" in entry.name):
                continue
            with contextlib.suppress(OSError):
                if (
                    now - entry.stat(follow_symlinks=False).st_mtime
                    < _ORPHAN_TEMP_FILE_MIN_AGE_SECONDS
                ):
                    continue
                os.unlink(entry.name, dir_fd=base_fd)

    @contextlib.contextmanager
    def _cross_process_lock(self, base_fd: int) -> Iterator[None]:
        """P6-CODEX-022, hardened P6-CODEX-028/038: `O_NOFOLLOW` makes the
        open itself fail (`ELOOP`) if `.write.lock` already exists as a
        Symlink (it never blocks legitimate first-time creation: `O_CREAT`
        without `O_EXCL` only ever creates a genuine regular file, never a
        Symlink). Bound to `base_fd` via `dir_fd=` rather than a re-joined
        path. The `os.fstat` checks below run on the already-open fd, so a
        Symlink or hardlink swap attempted *after* this open cannot
        retroactively change what got opened."""
        try:
            fd = os.open(
                ".write.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600, dir_fd=base_fd
            )
        except OSError as exc:
            if exc.errno == errno.ELOOP:
                raise RecordingPathRejected(
                    "recording write-lock path is a symlink: .write.lock"
                ) from exc
            # Any other OSError here (permission denied, disk/inode
            # exhaustion, ...) is an ordinary I/O failure, not a Path
            # Safety violation — it must still surface as
            # `RecordingWriteFailure` so an unwritable-but-otherwise-safe
            # directory degrades the same way it always has, not as a
            # spurious "unsafe path" rejection.
            raise RecordingWriteFailure(
                f"could not acquire recording cross-process lock: {exc}"
            ) from exc
        try:
            lock_stat = os.fstat(fd)
            if not stat.S_ISREG(lock_stat.st_mode):
                raise RecordingPathRejected(
                    "recording write-lock path is not a regular file: .write.lock"
                )
            if lock_stat.st_nlink > 1:
                raise RecordingPathRejected("recording write-lock path is hardlinked: .write.lock")
            if lock_stat.st_uid != os.getuid():
                raise RecordingPathRejected(
                    "recording write-lock path has an unexpected owner: .write.lock"
                )
            fcntl.flock(fd, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)
