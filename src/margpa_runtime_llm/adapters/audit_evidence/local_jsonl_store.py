"""Local, append-only JSONL Evidence Store adapter (Phase 3-B, P3-CODEX-005/
008/011/012 rework).

Layout (architecture §4.4):

    <anchor>/<relative_root>/<scope>/
      segments/segment-<8-digit-index>.jsonl
      receipts/               (reserved; Phase 3 keeps receipts derivable
                                 from segment + position and does not
                                 persist them separately)

Path-safety (P3-CODEX-012): the constructor takes a Server-owned Trusted
`anchor` (e.g. Project Root — never derived from request/user input) and a
`relative_root` string (e.g. `runtime_data/audit_evidence`) that is walked
*below* it exactly like `<scope>`/`segments` already were. A previous
version instead took one combined `root: Path` and called
`root.expanduser().resolve()` on it *before* ever starting the dir_fd
chain — `.resolve()` silently follows every symlink in every component,
including `root` itself and any of its ancestors, so a symlink planted at
the configured root (or an ancestor) before this Store was ever
constructed would become the new "trusted" anchor without detection,
defeating the whole point of the chain below it (P3-CODEX-012 Finding A).
Splitting the constructor into `anchor` (opened via one single, genuinely
unresolved `os.open(..., os.O_NOFOLLOW)` — the one hop with no parent
`dir_fd` to be relative to) plus `relative_root` (walked component-by-
component, `O_NOFOLLOW` + mkdir-if-missing, precisely like `_open_
directory_chain` already does for `<scope>`/`segments`) means *no* path
in this module is ever resolved — every component from the anchor down
is either the untouched caller-supplied anchor or an individually-opened
hop.

Every segment Leaf Open/Read/Append (P3-CODEX-012 Finding B) goes through
the held `segments/` dir_fd plus `O_NOFOLLOW` *and* `O_NONBLOCK` — the
latter so a FIFO substituted for a segment filename cannot block the
process indefinitely waiting for a peer (a no-op for a genuine regular
file). The opened fd is then `fstat`'d (`_verify_segment_leaf_fd`):
Regular File, owned by this process, not group/other-writable, and
`st_nlink <= 1` (a hard-linked segment would let a write here silently
mutate — or a read here silently expose — a *different* directory entry
outside this Store's control). Reads are `MAX_SEGMENT_FILE_BYTES + 1`
bounded from that same fd, so a segment that grows *after* the `fstat`
still cannot be read past the ceiling. `_segment_indices()` also rejects
any segment-pattern-matching directory entry that is not a symlink but
also not a regular file (a FIFO/device/socket discovered at listing time,
before any Open is even attempted).

A crash mid-write can only corrupt the tail of the segment being actively
appended to (writes are sequential and append-only) — never an earlier
line. On load, if the highest-indexed segment is degraded, future appends
target a new segment rather than continuing to append after unparseable
bytes; the degraded segment's existing bytes are never truncated or
rewritten (P3-STR-005). A write failure *within the current process* also
immediately marks the active segment degraded in memory (P3-CODEX-008
Finding B) — without that, the next `append()` in the same process would
happily continue writing after the corrupted tail, returning a "success"
Receipt for an Event that becomes unrecoverable on the next reopen.
`append()` also refuses to write past `MAX_SEGMENT_FILE_BYTES` on the
*active* segment (P3-CODEX-011 Finding A) — it `fstat`s the just-opened
segment fd and rolls over to a fresh segment *before* writing whenever
the current size plus the new line would exceed the ceiling, so a
successful Receipt can never describe a segment that a later Reopen would
then reject as oversized. Segment discovery (P3-CODEX-011 Finding B)
rejects any on-disk segment filename whose index falls outside
`1..MAX_SEGMENT_COUNT` — an unbounded 8-digit filename is syntactically
valid but must never be silently accepted past the Store's own capacity
contract — and the highest-segment-degraded rollover path checks the same
bound before ever assigning `highest + 1` as the new active index. Reads
walk every segment in index order, subject to the same finite Segment
Count / Byte Size ceilings `append()` enforces, so a Reopen never reads an
unbounded amount of untrusted-size data into memory before any limit is
applied.

SHA-512 alone is not represented as tamper-evident (P3-STR-007) — it only
detects accidental corruption, not adversarial rewriting.
"""

from __future__ import annotations

import os
import re
import stat
import threading
from pathlib import Path, PurePosixPath

from margpa_runtime_llm.modules.audit_evidence.domain import (
    AuditRunId,
    CanonicalAuditEvent,
    EvidenceReceiptId,
)
from margpa_runtime_llm.modules.audit_evidence.domain.errors import (
    EvidenceStoreError,
    EvidenceStoreErrorCode,
)
from margpa_runtime_llm.modules.audit_evidence.ports import (
    EvidenceReceipt,
    EvidenceStoreStatus,
)

_SEGMENT_FILENAME_PATTERN = re.compile(r"^segment-(\d{8})\.jsonl$")

# P3-PER-001 / P3-CODEX-004,005,008 rework: finite ceilings so a runaway
# or hostile write/read pattern fails closed instead of growing an
# unbounded number of segments, an unbounded segment file, or reading an
# unbounded amount of untrusted-size data into memory before any check.
MAX_EVENTS_PER_SEGMENT = 50_000
MAX_SEGMENT_COUNT = 100_000
MAX_SEGMENT_FILE_BYTES = 64 * 1024 * 1024
MAX_EVENT_LINE_BYTES = 1 * 1024 * 1024

_READ_CHUNK_BYTES = 262_144


def _segment_filename(index: int) -> str:
    return f"segment-{index:08d}.jsonl"


def _error(code: EvidenceStoreErrorCode, message: str, **kwargs: object) -> EvidenceStoreError:
    return EvidenceStoreError(code=code, safe_message=message, **kwargs)  # type: ignore[arg-type]


def _write_all(descriptor: int, data: bytes) -> None:
    """`os.write()` may write fewer bytes than requested (POSIX short write);
    looping until every byte is written keeps a successful `append()` and
    its returned `EvidenceReceipt` truthful about what actually landed on
    disk (P3-CODEX-005)."""

    view = memoryview(data)
    total_written = 0
    length = len(view)
    while total_written < length:
        written = os.write(descriptor, view[total_written:])
        if written <= 0:
            raise OSError("audit evidence append wrote zero bytes")
        total_written += written


def _parse_relative_root_parts(relative_root: str) -> tuple[str, ...] | None:
    """Syntactic-only validation for `relative_root` — rejects an absolute
    path and `..`/`.` traversal. An empty string is valid and means "zero
    hops" (`scope` sits directly under `anchor`); anything else that
    fails validation returns `None` (not an exception) so the caller can
    report a specific error instead of raising deep inside path
    construction."""

    if not relative_root:
        return ()
    posix = PurePosixPath(relative_root)
    if posix.is_absolute():
        return None
    parts = posix.parts
    if not parts or ".." in parts or "." in parts:
        return None
    return parts


def _verify_segment_leaf_fd(descriptor: int) -> os.stat_result:
    """`fstat`s an already-open segment fd and enforces the Identity/Type/
    Mode contract every Read *and* Append must satisfy before touching a
    single byte (P3-CODEX-012 Finding B): Regular File, owned by this
    process, not group/other-writable, and not hard-linked (`st_nlink`
    over 1 would mean some *other* directory entry — potentially outside
    this Store's control entirely — shares the same inode, so a write
    here could silently mutate, and a read here could silently expose,
    that other entry)."""

    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode):
        raise _error(
            EvidenceStoreErrorCode.PATH_VIOLATION,
            "audit evidence segment is not a regular file",
        )
    if info.st_uid != os.getuid() or info.st_mode & 0o022:
        raise _error(
            EvidenceStoreErrorCode.PATH_VIOLATION,
            "audit evidence segment has an unsafe owner or permissions",
        )
    if info.st_nlink > 1:
        raise _error(
            EvidenceStoreErrorCode.PATH_VIOLATION,
            "audit evidence segment shares an inode via a hard link",
        )
    return info


def _read_bounded_segment_from_fd(descriptor: int, max_bytes: int) -> bytes:
    """Verifies the segment fd (see `_verify_segment_leaf_fd`), then reads
    it with a hard `max_bytes`-capped loop — the same fd throughout, so a
    segment that grows *after* the initial `fstat` size check still
    cannot be read past the ceiling (P3-CODEX-012 Finding B)."""

    info = _verify_segment_leaf_fd(descriptor)
    if info.st_size > max_bytes:
        raise _error(
            EvidenceStoreErrorCode.CAPACITY_EXCEEDED,
            "audit evidence segment file exceeds the maximum allowed size",
        )
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = os.read(descriptor, _READ_CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise _error(
                EvidenceStoreErrorCode.CAPACITY_EXCEEDED,
                "audit evidence segment file exceeds the maximum allowed size",
            )
        chunks.append(chunk)
    return b"".join(chunks)


def _open_directory_chain(anchor_fd: int, parts: list[str]) -> int:
    """Consumes (always closes) `anchor_fd` and walks `parts` one
    directory-fd hop at a time, creating any missing component with
    `os.mkdir(..., dir_fd=parent_fd)` and then opening it with
    `os.O_NOFOLLOW, dir_fd=parent_fd)` — the open itself *is* the symlink
    check, so there is no separate lstat-then-open window for any
    component to be swapped through (P3-CODEX-011 Finding C). A freshly
    created directory is `fchmod`'d to `0o700` on the already-open fd
    (immune to a post-creation swap); a pre-existing one is instead
    rejected if it is not owned by this process or is group/other
    writable, mirroring the previous `_reject_unsafe_path` policy without
    ever re-deriving a path string to check it against."""

    current_fd = anchor_fd
    try:
        for part in parts:
            created = False
            try:
                os.mkdir(part, 0o700, dir_fd=current_fd)
                created = True
            except FileExistsError:
                pass
            except OSError as error:
                raise _error(
                    EvidenceStoreErrorCode.PATH_VIOLATION,
                    "audit evidence directory could not be created",
                ) from error
            try:
                next_fd = os.open(part, os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current_fd)
            except OSError as error:
                raise _error(
                    EvidenceStoreErrorCode.PATH_VIOLATION,
                    "audit evidence path contains a symlink",
                ) from error
            if created:
                os.fchmod(next_fd, 0o700)
            else:
                info = os.fstat(next_fd)
                if info.st_uid != os.getuid() or info.st_mode & 0o022:
                    os.close(next_fd)
                    raise _error(
                        EvidenceStoreErrorCode.PATH_VIOLATION,
                        "audit evidence directory is unsafe",
                    )
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


class _ParsedSegment:
    __slots__ = ("degraded", "degraded_reason_code", "event_ids", "events", "valid_line_count")

    def __init__(
        self,
        events: list[CanonicalAuditEvent],
        event_ids: set[str],
        valid_line_count: int,
        degraded: bool,
        degraded_reason_code: str | None,
    ) -> None:
        self.events = events
        self.event_ids = event_ids
        self.valid_line_count = valid_line_count
        self.degraded = degraded
        self.degraded_reason_code = degraded_reason_code


def _parse_segment(raw: bytes) -> _ParsedSegment:
    events: list[CanonicalAuditEvent] = []
    seen: set[str] = set()
    ends_with_newline = raw.endswith(b"\n") if raw else True
    lines = raw.split(b"\n")
    if ends_with_newline and lines and lines[-1] == b"":
        lines = lines[:-1]

    degraded = not ends_with_newline
    degraded_reason = "partial_tail" if degraded else None

    for index, line in enumerate(lines):
        is_last = index == len(lines) - 1
        if len(line) > MAX_EVENT_LINE_BYTES:
            degraded = True
            degraded_reason = "event_line_too_large"
            break
        try:
            canonical = CanonicalAuditEvent.model_validate_json(line)
        except ValueError:
            if not (is_last and not ends_with_newline):
                degraded = True
                degraded_reason = "unknown_schema"
            break
        events.append(canonical)
        seen.add(canonical.envelope.event_id.value)

    return _ParsedSegment(events, seen, len(events), degraded, degraded_reason)


class LocalJsonlEvidenceStore:
    """One store instance owns exactly one
    `<anchor>/<relative_root>/<scope>/` directory."""

    def __init__(self, *, anchor: Path, relative_root: str, scope: str) -> None:
        if not scope or not all(ch.isalnum() or ch in "-_" for ch in scope):
            raise _error(EvidenceStoreErrorCode.PATH_VIOLATION, "audit evidence scope is invalid")

        self._lock = threading.Lock()
        # Held for the store's lifetime: every subsequent Open/Stat/Listdir
        # against `segments/` goes through this fd (P3-CODEX-008/011/012)
        # — even if an attacker replaces `relative_root`, `scope/`,
        # `segments/`, or any still-missing prefix of `relative_root` with
        # a symlink at any point after this point, operations relative to
        # this fd still resolve to the original directory inode, not the
        # replacement.
        self._segments_dir_fd = self._open_segments_dir_fd(anchor, relative_root, scope)

        self._seen_event_ids: set[str] = set()
        self._total_valid_events = 0
        self._degraded = False
        self._degraded_reason_code: str | None = None
        self._active_segment_index = 1
        self._active_segment_position = 0
        # Set the moment a write to the active segment fails partway
        # through, from *within this process* — the next append() must
        # not continue writing after a tail this process itself knows is
        # corrupted (P3-CODEX-008 Finding B), even before any future
        # reopen would otherwise detect it by re-parsing the file.
        self._active_segment_degraded = False
        self._load_existing_segments()

    # -- Path safety ---------------------------------------------------------

    @staticmethod
    def _open_segments_dir_fd(anchor: Path, relative_root: str, scope: str) -> int:
        """Opens `<anchor>/<relative_root>/<scope>/segments` as a held fd.
        `anchor` is the *only* single-shot absolute-path Open (a Server-
        owned Trusted Anchor, e.g. Project Root — never a value derived
        from request/user input, and deliberately never `.resolve()`d:
        the caller is trusted to supply it as-is). Every component from
        there down — each `relative_root` segment, `scope`, then
        `segments` — is walked one `O_NOFOLLOW` dir_fd hop at a time via
        `_open_directory_chain` (P3-CODEX-012 Finding A)."""

        relative_parts = _parse_relative_root_parts(relative_root)
        if relative_parts is None:
            raise _error(
                EvidenceStoreErrorCode.PATH_VIOLATION,
                "audit evidence relative root is invalid",
            )
        try:
            anchor_fd = os.open(str(anchor), os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError as error:
            raise _error(
                EvidenceStoreErrorCode.PATH_VIOLATION,
                "audit evidence anchor path is unsafe",
            ) from error
        return _open_directory_chain(anchor_fd, [*relative_parts, scope, "segments"])

    def _open_segment_relative(self, name: str, flags: int, mode: int = 0) -> int:
        """Every segment Open goes through the held `segments/` dir_fd
        with `O_NOFOLLOW` — closes the Check-to-open Race window between
        `_reject_unsafe_path` and the actual open (P3-CODEX-008) — plus
        `O_NONBLOCK`, so a FIFO substituted for the segment filename
        cannot block this call indefinitely waiting for a peer (a no-op
        for a genuine regular file; P3-CODEX-012 Finding B)."""

        try:
            return os.open(
                name,
                flags | os.O_NOFOLLOW | os.O_NONBLOCK,
                mode,
                dir_fd=self._segments_dir_fd,
            )
        except OSError as error:
            raise _error(
                EvidenceStoreErrorCode.PATH_VIOLATION,
                "audit evidence segment path is unsafe",
            ) from error

    # -- Segment discovery -----------------------------------------------

    def _segment_indices(self) -> list[int]:
        names = os.listdir(self._segments_dir_fd)
        if len(names) > MAX_SEGMENT_COUNT:
            raise _error(
                EvidenceStoreErrorCode.CAPACITY_EXCEEDED,
                "audit evidence store segment capacity exceeded",
            )
        indices: list[int] = []
        for name in names:
            try:
                info = os.stat(name, dir_fd=self._segments_dir_fd, follow_symlinks=False)
            except OSError:
                continue
            if stat.S_ISLNK(info.st_mode):
                raise _error(
                    EvidenceStoreErrorCode.PATH_VIOLATION,
                    "audit evidence path contains a symlink",
                )
            match = _SEGMENT_FILENAME_PATTERN.match(name)
            if match is None:
                continue
            if not stat.S_ISREG(info.st_mode):
                # A FIFO/device/socket named like a segment — reject at
                # discovery, before any Open is even attempted
                # (P3-CODEX-012 Finding B).
                raise _error(
                    EvidenceStoreErrorCode.PATH_VIOLATION,
                    "audit evidence segment is not a regular file",
                )
            index = int(match.group(1))
            if not (1 <= index <= MAX_SEGMENT_COUNT):
                # An 8-digit filename can encode up to 99_999_999 — far
                # past MAX_SEGMENT_COUNT. Discovering one on disk means
                # either corruption or an out-of-contract writer; either
                # way it must fail closed, not be silently indexed
                # (P3-CODEX-011 Finding B).
                raise _error(
                    EvidenceStoreErrorCode.PATH_VIOLATION,
                    "audit evidence segment filename index is out of range",
                )
            indices.append(index)
        return sorted(indices)

    def _read_segment_relative(self, index: int) -> bytes:
        name = _segment_filename(index)
        descriptor = self._open_segment_relative(name, os.O_RDONLY)
        try:
            return _read_bounded_segment_from_fd(descriptor, MAX_SEGMENT_FILE_BYTES)
        finally:
            os.close(descriptor)

    def _load_existing_segments(self) -> None:
        indices = self._segment_indices()
        if not indices:
            return
        for index in indices:
            parsed = _parse_segment(self._read_segment_relative(index))
            self._total_valid_events += parsed.valid_line_count
            self._seen_event_ids |= parsed.event_ids
            if parsed.degraded:
                self._degraded = True
                self._degraded_reason_code = parsed.degraded_reason_code

        highest = indices[-1]
        highest_parsed = _parse_segment(self._read_segment_relative(highest))
        if highest_parsed.degraded:
            # Never continue appending after unparseable bytes — roll over
            # to a fresh segment instead (the degraded one is left as-is).
            next_index = highest + 1
            if next_index > MAX_SEGMENT_COUNT:
                # The same capacity ceiling applies here as it does to a
                # live append-time rollover (P3-CODEX-011 Finding B) — a
                # degraded highest segment sitting at the ceiling must
                # fail closed at load time, not silently mint a 9-digit
                # segment filename that a later scan's regex would then
                # never discover again.
                raise _error(
                    EvidenceStoreErrorCode.CAPACITY_EXCEEDED,
                    "audit evidence store segment capacity exceeded",
                )
            self._active_segment_index = next_index
            self._active_segment_position = 0
        else:
            self._active_segment_index = highest
            self._active_segment_position = highest_parsed.valid_line_count

    # -- Append ------------------------------------------------------------

    def _advance_to_next_segment(self, *, run_id: str, event_id: str) -> None:
        next_index = self._active_segment_index + 1
        if next_index > MAX_SEGMENT_COUNT:
            raise _error(
                EvidenceStoreErrorCode.CAPACITY_EXCEEDED,
                "audit evidence store segment capacity exceeded",
                run_id=run_id,
                event_id=event_id,
            )
        self._active_segment_index = next_index
        self._active_segment_position = 0
        self._active_segment_degraded = False

    def _open_active_segment_with_capacity(
        self, encoded_len: int, *, run_id: str, event_id: str
    ) -> tuple[int, str]:
        """Returns an append-positioned fd for a segment `fstat`-confirmed
        to hold `encoded_len` more bytes without exceeding
        `MAX_SEGMENT_FILE_BYTES`, rolling forward through fresh segments
        as needed — never touching a segment's existing bytes if it
        doesn't fit (P3-CODEX-011 Finding A: a prior version only checked
        the encoded line against `MAX_EVENT_LINE_BYTES`, never the active
        segment's own running total, so a write landing just past the
        ceiling still returned a success Receipt that a later Reopen
        would then reject as oversized)."""

        while True:
            name = _segment_filename(self._active_segment_index)
            descriptor = self._open_segment_relative(
                name, os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600
            )
            try:
                info = _verify_segment_leaf_fd(descriptor)
            except EvidenceStoreError:
                os.close(descriptor)
                raise
            current_size = info.st_size
            if current_size + encoded_len <= MAX_SEGMENT_FILE_BYTES:
                return descriptor, name
            os.close(descriptor)
            if current_size == 0:
                # A brand-new, empty segment still cannot hold this one
                # event — unrecoverable by rolling forward again.
                raise _error(
                    EvidenceStoreErrorCode.CAPACITY_EXCEEDED,
                    "audit evidence event exceeds the maximum allowed segment size",
                    run_id=run_id,
                    event_id=event_id,
                )
            self._advance_to_next_segment(run_id=run_id, event_id=event_id)

    def append(self, canonical: CanonicalAuditEvent) -> EvidenceReceipt:
        event_id = canonical.envelope.event_id.value
        run_id = canonical.envelope.run_id.value
        with self._lock:
            if event_id in self._seen_event_ids:
                raise _error(
                    EvidenceStoreErrorCode.DUPLICATE_EVENT,
                    "duplicate audit event id",
                    run_id=run_id,
                    event_id=event_id,
                )

            encoded = (canonical.model_dump_json() + "\n").encode("utf-8")
            if len(encoded) > MAX_EVENT_LINE_BYTES:
                raise _error(
                    EvidenceStoreErrorCode.CAPACITY_EXCEEDED,
                    "audit evidence event exceeds the maximum allowed serialized size",
                    run_id=run_id,
                    event_id=event_id,
                )

            if self._active_segment_position >= MAX_EVENTS_PER_SEGMENT or (
                self._active_segment_degraded
            ):
                self._advance_to_next_segment(run_id=run_id, event_id=event_id)

            try:
                descriptor, active_segment_name = self._open_active_segment_with_capacity(
                    len(encoded), run_id=run_id, event_id=event_id
                )
            except EvidenceStoreError as error:
                if error.code is EvidenceStoreErrorCode.CAPACITY_EXCEEDED:
                    # Rejected before a single byte was written to any
                    # segment — a legitimate capacity refusal, not a
                    # write failure, so the store is not degraded by it.
                    raise
                self._active_segment_degraded = True
                self._degraded = True
                self._degraded_reason_code = "append_failed"
                raise _error(
                    EvidenceStoreErrorCode.APPEND_FAILED,
                    "audit evidence append failed",
                    run_id=run_id,
                    event_id=event_id,
                ) from error

            try:
                try:
                    _write_all(descriptor, encoded)
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
            except OSError as error:
                # This process now knows the active segment's tail may be
                # corrupted (a partial physical write can already have
                # landed) — never let a later append in this same process
                # continue writing after it (P3-CODEX-008 Finding B), and
                # never let the Store report itself as healthy afterward.
                self._active_segment_degraded = True
                self._degraded = True
                self._degraded_reason_code = "append_failed"
                raise _error(
                    EvidenceStoreErrorCode.APPEND_FAILED,
                    "audit evidence append failed",
                    run_id=run_id,
                    event_id=event_id,
                ) from error

            position = self._active_segment_position
            self._active_segment_position += 1
            self._total_valid_events += 1
            self._seen_event_ids.add(event_id)
            return EvidenceReceipt(
                # Segment index folded in: after a rollover, position
                # alone resets to 0 in the new segment and would otherwise
                # collide with an earlier segment's receipt-000000000000
                # (P3-CODEX-008 "Additional Integrity Defects").
                receipt_id=EvidenceReceiptId(
                    value=f"receipt-{self._active_segment_index:08d}-{position:012d}"
                ),
                event_id=event_id,
                event_digest_sha512=canonical.event_digest_sha512,
                segment=active_segment_name,
                position=position,
            )

    # -- Read --------------------------------------------------------------

    def read_all(self, run_id: AuditRunId) -> tuple[CanonicalAuditEvent, ...]:
        with self._lock:
            events: list[CanonicalAuditEvent] = []
            for index in self._segment_indices():
                parsed = _parse_segment(self._read_segment_relative(index))
                events.extend(parsed.events)
            return tuple(event for event in events if event.envelope.run_id == run_id)

    def status(self) -> EvidenceStoreStatus:
        with self._lock:
            return EvidenceStoreStatus(
                event_count=self._total_valid_events,
                degraded=self._degraded,
                degraded_reason_code=self._degraded_reason_code,
            )
