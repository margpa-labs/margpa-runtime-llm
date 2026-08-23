"""Filesystem `DefinitionProviderPort` adapter (Phase 3-C-WU-003,
P3-CODEX-010 rework).

Reads *only* an explicit Manifest at an explicit Root — never scans a
directory, never infers schema/domain from a filename, never follows a
symlink outside Root, never fetches remotely, and never imports a Manifest
string as a Python module path (P3-PRV-002/003, P3-SEC-001/002/004).

Path-safety (P3-CODEX-010): `<root>` is the one Trusted-Anchor Open (a
single absolute-path `os.open`, unavoidable — there is no parent `dir_fd`
to be relative to for the very first hop; `root` is caller-supplied
configuration, never derived from an untrusted request). Every component
below it — every directory hop on the way to a Source or the Manifest,
and the Source/Manifest leaf itself — is opened one `os.open(...,
os.O_NOFOLLOW, dir_fd=parent_fd)` hop at a time. A previous version
`lstat`-walked each component to *check* it, then re-derived an absolute
`Path` and called `.stat()`/`.read_bytes()` on it as a *separate* step —
a Check-to-open Race window in which a component could be swapped for a
symlink (or the leaf for a FIFO/device) between the check and the actual
read. Walking the directory-fd chain makes the check *be* the open
(`ELOOP` on any symlinked component, fails closed at the syscall level
regardless of timing); the leaf is additionally opened `O_NONBLOCK` so a
FIFO substituted for it cannot block the open indefinitely waiting for a
writer (a no-op for a genuine regular file). The resulting leaf fd is
then `fstat`'d (Regular File, not world-writable, within its byte
ceiling) and read with a `MAX_*_BYTES + 1`-bounded loop that rejects an
oversized file before ever finishing the read — and the Manifest's own
Open/Read now goes through this identical boundary, not a separate one.

Per-source verification (`SourceVerification`) reports whether each
Manifest-declared source matches what is actually on disk. Turning those
verifications into a package-wide accept/quarantine *policy* is Phase
3-C-WU-004's Repository State machine — this adapter only observes and
reports.
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
import stat
from pathlib import Path, PurePosixPath

from margpa_runtime_llm.modules.governance_definitions.domain import (
    PackageState,
    ProviderState,
    SignedPackageManifest,
    SourceState,
    SourceVerification,
    resolve_definition_states,
    resolve_package_state,
)
from margpa_runtime_llm.modules.governance_definitions.domain.limits import (
    MAX_MANIFEST_BYTES,
    MAX_RELATIVE_PATH_DEPTH,
    MAX_SOURCE_BYTES,
)
from margpa_runtime_llm.modules.governance_definitions.ports import (
    DefinitionStateEntry,
    PackageLoadRequest,
    PackageSourceResult,
    ProviderDescriptor,
)

_PROVIDER_KIND = "filesystem"
_READ_CHUNK_BYTES = 262_144
_UNSUPPORTED_REASON_BY_READ_FAILURE = {
    "not_a_regular_file": "not_a_regular_file",
    "too_large": "source_too_large",
    "world_writable": "world_writable_source",
}


class _ManifestTooLarge(ValueError):
    """Distinguishes a Size Gate rejection from an ordinary parse failure
    so callers can report a more specific reason code (P3-CODEX-004)."""


class _SourcePathError(Exception):
    """Raised by the `dir_fd`-chain Open/Read helpers below — never
    crosses this module's boundary uncaught; every caller maps
    `reason_code` to a Typed `SourceState`/`ProviderDescriptor` result
    (P3-CODEX-010)."""

    def __init__(self, reason_code: str) -> None:
        super().__init__(reason_code)
        self.reason_code = reason_code


def _parse_relative_path_parts(relative_path: str) -> tuple[str, ...] | None:
    """Syntactic-only validation — rejects an absolute path, `..`/`.`
    traversal, and excessive depth. Returns `None` (not an exception) for
    an unsafe path so callers can report a specific reason code instead
    of raising during construction."""

    if not relative_path or PurePosixPath(relative_path).is_absolute():
        return None
    parts = PurePosixPath(relative_path).parts
    if ".." in parts or "." in parts or not parts:
        return None
    if len(parts) > MAX_RELATIVE_PATH_DEPTH:
        return None
    return parts


def _open_leaf_file_fd(root_fd: int, parts: tuple[str, ...]) -> int:
    """Walks `parts` from `root_fd`, one `O_NOFOLLOW` hop at a time —
    every intermediate component as a directory, the final component as
    a regular file. The open itself is the symlink/existence check; there
    is no separate lstat-then-open window for any component, including
    the leaf, to be swapped through (P3-CODEX-010)."""

    current_fd = root_fd
    owns_current = False
    try:
        for index, part in enumerate(parts):
            is_last = index == len(parts) - 1
            flags = os.O_RDONLY | os.O_NOFOLLOW
            if not is_last:
                flags |= os.O_DIRECTORY
            else:
                # A FIFO substituted for the leaf would otherwise block
                # this open indefinitely waiting for a writer — O_NONBLOCK
                # makes the open return immediately instead (a no-op for
                # a genuine regular file), so the subsequent `fstat`-based
                # Regular File check can reject it (P3-CODEX-010).
                flags |= os.O_NONBLOCK
            try:
                next_fd = os.open(part, flags, dir_fd=current_fd)
            except OSError as error:
                if error.errno == errno.ELOOP:
                    raise _SourcePathError("path_unsafe") from error
                if error.errno == errno.ENOTDIR:
                    # `O_DIRECTORY | O_NOFOLLOW` on a symlinked directory
                    # component reports ENOTDIR rather than ELOOP on some
                    # platforms (macOS/BSD) — this `lstat` only chooses the
                    # reason code; the open already failed closed either
                    # way, so there is nothing left to race.
                    try:
                        link_info = os.lstat(part, dir_fd=current_fd)
                    except OSError:
                        link_info = None
                    if link_info is not None and stat.S_ISLNK(link_info.st_mode):
                        raise _SourcePathError("path_unsafe") from error
                raise _SourcePathError("path_not_found") from error
            if owns_current:
                os.close(current_fd)
            current_fd = next_fd
            owns_current = True
        return current_fd
    except BaseException:
        if owns_current:
            os.close(current_fd)
        raise


def _read_bounded_from_fd(descriptor: int, max_bytes: int) -> bytes:
    """`fstat`s the already-open `descriptor` (Regular File, not
    world-writable, within `max_bytes`) before reading, then reads with a
    hard `max_bytes`-capped loop as defense-in-depth against a file that
    grows after the `fstat` — the same fd is used throughout, so there is
    no window for the bytes actually read to belong to a different file
    than the one just checked (P3-CODEX-010)."""

    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode):
        raise _SourcePathError("not_a_regular_file")
    if info.st_mode & 0o002:
        raise _SourcePathError("world_writable")
    if info.st_size > max_bytes:
        raise _SourcePathError("too_large")
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = os.read(descriptor, _READ_CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise _SourcePathError("too_large")
        chunks.append(chunk)
    return b"".join(chunks)


class FilesystemDefinitionProvider:
    """One instance owns exactly one `<root>` + one Manifest file beneath it."""

    def __init__(self, *, root: Path, manifest_relative_path: str = "manifest.json") -> None:
        resolved_root = root.expanduser().resolve()
        self._manifest_relative_path = manifest_relative_path
        self._manifest_parts = _parse_relative_path_parts(manifest_relative_path)
        try:
            # The one Trusted-Anchor Open (module docstring) — `root` is
            # caller-supplied configuration, not derived from a request.
            self._root_fd: int | None = os.open(str(resolved_root), os.O_DIRECTORY | os.O_NOFOLLOW)
        except OSError:
            self._root_fd = None

    # -- Path safety -----------------------------------------------------

    def _open_manifest_fd(self) -> int:
        if self._manifest_parts is None:
            raise _SourcePathError("path_unsafe")
        if self._root_fd is None:
            raise _SourcePathError("path_not_found")
        return _open_leaf_file_fd(self._root_fd, self._manifest_parts)

    # -- Provider ------------------------------------------------------

    def describe(self) -> ProviderDescriptor:
        try:
            signed = self._load_signed_manifest()
        except _SourcePathError as error:
            if error.reason_code == "path_not_found":
                return ProviderDescriptor(
                    provider_id="filesystem-provider",
                    provider_kind=_PROVIDER_KIND,
                    state=ProviderState.NOT_CONFIGURED,
                    unavailable_reason_code="manifest_not_found",
                )
            return ProviderDescriptor(
                provider_id="filesystem-provider",
                provider_kind=_PROVIDER_KIND,
                state=ProviderState.UNAVAILABLE,
                unavailable_reason_code="manifest_path_unsafe",
            )
        except _ManifestTooLarge:
            return ProviderDescriptor(
                provider_id="filesystem-provider",
                provider_kind=_PROVIDER_KIND,
                state=ProviderState.FAILED,
                unavailable_reason_code="manifest_too_large",
            )
        except ValueError:
            return ProviderDescriptor(
                provider_id="filesystem-provider",
                provider_kind=_PROVIDER_KIND,
                state=ProviderState.FAILED,
                unavailable_reason_code="manifest_unparseable",
            )
        state = ProviderState.EMPTY if not signed.manifest.source_entries else ProviderState.READY
        return ProviderDescriptor(
            provider_id="filesystem-provider", provider_kind=_PROVIDER_KIND, state=state
        )

    def load_package(self, request: PackageLoadRequest) -> PackageSourceResult:
        try:
            signed = self._load_signed_manifest()
        except _SourcePathError:
            return PackageSourceResult(found=False, reason_code="manifest_not_available")
        except _ManifestTooLarge:
            return PackageSourceResult(
                found=True,
                package_state=PackageState.INVALID,
                package_id=None,
                reason_code="manifest_too_large",
            )
        except ValueError:
            return PackageSourceResult(
                found=True,
                package_state=PackageState.INVALID,
                package_id=None,
                reason_code="manifest_unparseable",
            )

        manifest = signed.manifest
        if (
            request.requested_package_id is not None
            and request.requested_package_id != manifest.package_id
        ):
            return PackageSourceResult(found=False, reason_code="package_id_not_found")

        records = self._verify_sources_with_content(signed)
        verifications = tuple(verification for verification, _ in records)
        package_state = resolve_package_state(signed, verifications)
        definition_states = (
            ()
            if package_state is PackageState.QUARANTINED
            else tuple(
                DefinitionStateEntry(definition_id=definition_id, state=state)
                for definition_id, state in resolve_definition_states(
                    manifest, verifications
                ).items()
            )
        )
        # Verified Bytes / Verified Source Record (P3-CODEX-007): the
        # *same* read that just verified Size/Digest/JSON-shape is what
        # gets handed onward — a caller (the Runtime) must never re-read
        # the source from disk a second time as its own Source of Truth.
        verified_source_json = {
            entry.source_id: content
            for entry, (verification, content) in zip(
                signed.manifest.source_entries, records, strict=True
            )
            if verification.state is SourceState.LOADED and content is not None
        }
        return PackageSourceResult(
            found=True,
            package_state=package_state,
            package_id=manifest.package_id,
            manifest=manifest if package_state is not PackageState.QUARANTINED else None,
            definition_states=definition_states,
            verified_source_json=verified_source_json,
            reason_code=(
                "manifest_digest_mismatch_or_structural_source_violation"
                if package_state is PackageState.QUARANTINED
                else None
            ),
        )

    # -- Source verification -----------------------------------------------

    def verify_sources(self, signed: SignedPackageManifest) -> tuple[SourceVerification, ...]:
        return tuple(verification for verification, _ in self._verify_sources_with_content(signed))

    def _verify_sources_with_content(
        self, signed: SignedPackageManifest
    ) -> tuple[tuple[SourceVerification, dict[str, object] | None], ...]:
        results: list[tuple[SourceVerification, dict[str, object] | None]] = []
        for entry in signed.manifest.source_entries:
            try:
                definitions_relative = str(Path(entry.relative_path).relative_to("definitions"))
            except ValueError:
                results.append(
                    (
                        SourceVerification(
                            source_id=entry.source_id,
                            state=SourceState.INVALID,
                            reason_code="path_prefix_mismatch",
                        ),
                        None,
                    )
                )
                continue

            parts = _parse_relative_path_parts(definitions_relative)
            if parts is None:
                results.append(
                    (
                        SourceVerification(
                            source_id=entry.source_id,
                            state=SourceState.INVALID,
                            reason_code="path_unsafe",
                        ),
                        None,
                    )
                )
                continue

            if self._root_fd is None:
                results.append(
                    (
                        SourceVerification(
                            source_id=entry.source_id,
                            state=SourceState.UNSUPPORTED,
                            reason_code="not_a_regular_file",
                        ),
                        None,
                    )
                )
                continue

            try:
                source_fd = _open_leaf_file_fd(self._root_fd, parts)
            except _SourcePathError as error:
                if error.reason_code == "path_unsafe":
                    results.append(
                        (
                            SourceVerification(
                                source_id=entry.source_id,
                                state=SourceState.INVALID,
                                reason_code="path_unsafe",
                            ),
                            None,
                        )
                    )
                else:
                    results.append(
                        (
                            SourceVerification(
                                source_id=entry.source_id,
                                state=SourceState.UNSUPPORTED,
                                reason_code="not_a_regular_file",
                            ),
                            None,
                        )
                    )
                continue

            try:
                try:
                    raw = _read_bounded_from_fd(source_fd, MAX_SOURCE_BYTES)
                except _SourcePathError as error:
                    reason = _UNSUPPORTED_REASON_BY_READ_FAILURE.get(
                        error.reason_code, "not_a_regular_file"
                    )
                    results.append(
                        (
                            SourceVerification(
                                source_id=entry.source_id,
                                state=SourceState.UNSUPPORTED,
                                reason_code=reason,
                            ),
                            None,
                        )
                    )
                    continue
            finally:
                os.close(source_fd)

            if len(raw) != entry.byte_length:
                results.append(
                    (
                        SourceVerification(
                            source_id=entry.source_id, state=SourceState.SIZE_MISMATCH
                        ),
                        None,
                    )
                )
                continue
            digest = hashlib.sha512(raw).hexdigest()
            if digest != entry.content_digest_sha512:
                results.append(
                    (
                        SourceVerification(
                            source_id=entry.source_id, state=SourceState.DIGEST_MISMATCH
                        ),
                        None,
                    )
                )
                continue
            try:
                parsed = json.loads(raw)
            except ValueError:
                results.append(
                    (
                        SourceVerification(
                            source_id=entry.source_id,
                            state=SourceState.INVALID,
                            reason_code="malformed_json",
                        ),
                        None,
                    )
                )
                continue
            if not isinstance(parsed, dict):
                results.append(
                    (
                        SourceVerification(
                            source_id=entry.source_id,
                            state=SourceState.INVALID,
                            reason_code="not_a_json_object",
                        ),
                        None,
                    )
                )
                continue
            results.append(
                (SourceVerification(source_id=entry.source_id, state=SourceState.LOADED), parsed)
            )
        return tuple(results)

    # -- Manifest loading ------------------------------------------------

    def _load_signed_manifest(self) -> SignedPackageManifest:
        manifest_fd = self._open_manifest_fd()
        try:
            try:
                raw = _read_bounded_from_fd(manifest_fd, MAX_MANIFEST_BYTES)
            except _SourcePathError as error:
                if error.reason_code == "too_large":
                    raise _ManifestTooLarge("manifest exceeds the maximum allowed size") from error
                raise ValueError("manifest read failed") from error
        finally:
            os.close(manifest_fd)
        return SignedPackageManifest.model_validate_json(raw)
