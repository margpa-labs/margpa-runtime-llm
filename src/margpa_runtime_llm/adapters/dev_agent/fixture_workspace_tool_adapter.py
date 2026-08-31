"""Phase 8 (P8-MR5 / P8-MANUAL-005): traceable real-File Tool Adapter,
bounded to one fixed `fixture_workspace/` directory under the Configured
Runtime Data Root.

Replaces `FakeToolPort`'s Process-Memory-only `write_note` in Production
Composition (`bootstrap/dev_agent.py`) — this is still a PoC Fixture
boundary, never a general Project File Tool: every List/Read/Write is
confined to `<runtime-data-root>/persistent/<scope-id>/dev_agent/
fixture_workspace/`, never Project Source, never any other User File, never
the Network. Mirrors `JsonFileDevAgentRunStore`'s own local-file safety
discipline exactly (Absolute Path/`..`/Symlink/Root-Escape rejection,
Owner-only 0700/0600 modes, Atomic same-directory Replace) — this Task's
established convention for any Runtime-Data-Root-relative File I/O.
"""

from __future__ import annotations

import hashlib
import os
import stat
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from threading import Lock

from ...modules.dev_agent.ports import (
    ToolExecutionFailed,
    ToolExecutionOutcome,
    ToolExecutionSucceeded,
)

LIST_FILES_TOOL_ID = "list_files"
READ_FILE_TOOL_ID = "read_file"
WRITE_NOTE_TOOL_ID = "write_note"

_SEED_FILES: Mapping[str, str] = {
    "notes/readme.md": "# Fixture Notes\n\nThis is Fixture content only.",
    "notes/todo.md": "- [ ] Fixture item one\n- [ ] Fixture item two",
}
"""The exact pre-Rework `FakeToolPort.FIXTURE_FILES` content, written once
to real disk the first time this Workspace is used — a Restart must never
overwrite an already-seeded File with this default again (a User's real
prior Write into `notes/new.md`, or an edited Seed File, must survive)."""


class DevAgentFixtureWorkspaceUnsafePath(Exception):
    """Raised for any Path that would resolve outside the Workspace Root,
    traverse a Symlink, or fail the Owner/Directory chain check — never
    silently coerced into a safe path, and never allowed to reach real
    filesystem I/O."""


def _safe_filename_segment(value: str) -> bool:
    return bool(value) and value not in {".", ".."} and all(c.isalnum() or c in "-_" for c in value)


class FixtureWorkspaceToolPort:
    """Implements the same `tool_id` dispatch shape as `FakeToolPort`
    (`list_files` / `read_file` / `write_note`) so `bootstrap/dev_agent.py`
    can substitute this Adapter without changing any `ToolDescriptor` or
    Plan Fixture — only the Composition Root changes which Port a
    `ToolDescriptor` is registered against."""

    def __init__(self, *, runtime_data_root: Path, scope_key: str = "default") -> None:
        if not runtime_data_root.is_absolute():
            raise ValueError("runtime_data_root must be absolute")
        if not _safe_filename_segment(scope_key):
            raise ValueError("scope_key must be a safe single path segment")
        self._root = runtime_data_root
        self._workspace = (
            runtime_data_root / "persistent" / scope_key / "dev_agent" / "fixture_workspace"
        )
        self._lock = Lock()

    def execute(self, tool_id: str, input: Mapping[str, object]) -> ToolExecutionOutcome:
        # P8-MR6 Internal Review: a real filesystem is capable of failures
        # `FakeToolPort`'s in-memory dict never could (e.g. a `path` that
        # collides with an existing Directory raises `IsADirectoryError`
        # from `os.replace()`) — this Adapter must never let such a
        # failure become an uncaught exception reaching `DevAgentRunService.
        # advance()` (which has no Tool-layer try/except of its own), the
        # same "Runtime/Evidence Failure must not break the core feature"
        # discipline every other Tool Port/Fetch Provider in this codebase
        # already follows.
        with self._lock:
            try:
                self._ensure_seeded()
            except DevAgentFixtureWorkspaceUnsafePath:
                return ToolExecutionFailed(reason="workspace_unsafe_path")
            try:
                if tool_id == LIST_FILES_TOOL_ID:
                    return self._list_files()
                if tool_id == READ_FILE_TOOL_ID:
                    return self._read_file(input)
                if tool_id == WRITE_NOTE_TOOL_ID:
                    return self._write_note(input)
                return ToolExecutionFailed(reason="unknown_tool")
            except OSError:
                return ToolExecutionFailed(reason="workspace_io_error")

    # -- Tool implementations ---------------------------------------------

    def _list_files(self) -> ToolExecutionOutcome:
        paths = sorted(
            str(path.relative_to(self._workspace))
            for path in self._workspace.rglob("*")
            if path.is_file()
        )
        return ToolExecutionSucceeded(output={"paths": paths})

    def _read_file(self, input: Mapping[str, object]) -> ToolExecutionOutcome:
        target = self._resolve_safe_path(input.get("path"))
        if target is None or not target.is_file():
            return ToolExecutionFailed(reason="path_not_found")
        try:
            content = target.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ToolExecutionFailed(reason="path_not_found")
        digest = hashlib.sha512(content.encode("utf-8")).hexdigest()
        return ToolExecutionSucceeded(
            output={
                "path": str(target.relative_to(self._workspace)),
                "content": content,
                "content_sha512": digest,
            }
        )

    def _write_note(self, input: Mapping[str, object]) -> ToolExecutionOutcome:
        content = input.get("content")
        if not isinstance(content, str):
            return ToolExecutionFailed(reason="invalid_input")
        target = self._resolve_safe_path(input.get("path"))
        if target is None:
            return ToolExecutionFailed(reason="invalid_input")
        overwrite = target.exists()
        self._ensure_private_directory(target.parent)
        digest = hashlib.sha512(content.encode("utf-8")).hexdigest()
        written_at = datetime.now(UTC).isoformat()
        self._atomic_write(target, content)
        return ToolExecutionSucceeded(
            output={
                "path": str(target.relative_to(self._workspace)),
                "written": True,
                "content_sha512": digest,
                "written_at": written_at,
                "overwrite": overwrite,
            }
        )

    # -- Path safety --------------------------------------------------------

    def _resolve_safe_path(self, raw: object) -> Path | None:
        """`None` for anything unsafe — Absolute Path, `..`, a Symlink
        anywhere along the chain, or a resolved location outside the
        Workspace Root. Never raises; the caller treats `None` as an
        ordinary Tool-level Failure, not a crash."""

        if not isinstance(raw, str) or not raw:
            return None
        candidate = PurePosixPath(raw)
        if candidate.is_absolute() or ".." in candidate.parts or "." in candidate.parts:
            return None
        if not candidate.parts:
            return None
        current = self._workspace
        for part in candidate.parts:
            current = current / part
            if current.is_symlink():
                return None
        resolved = self._workspace / candidate
        try:
            resolved.relative_to(self._workspace)
        except ValueError:
            return None
        return resolved

    def _atomic_write(self, path: Path, content: str) -> None:
        tmp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
        try:
            descriptor = os.open(tmp_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(content)
            os.chmod(tmp_path, 0o600)
            os.replace(tmp_path, path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    def _ensure_seeded(self) -> None:
        self._validate_path_chain(self._workspace)
        self._ensure_private_directory(self._workspace / "notes")
        for relative, content in _SEED_FILES.items():
            path = self._workspace / relative
            if path.exists():
                continue
            self._atomic_write(path, content)

    def _ensure_private_directory(self, directory: Path) -> None:
        missing: list[Path] = []
        current = directory
        while not current.exists():
            missing.append(current)
            if current == self._root:
                break
            current = current.parent
        if current.exists() and current.is_symlink():
            raise DevAgentFixtureWorkspaceUnsafePath(str(current))
        for path in reversed(missing):
            path.mkdir(mode=0o700)
            os.chmod(path, 0o700)

    def _validate_path_chain(self, directory: Path) -> None:
        current = self._root
        if current.exists() and current.is_symlink():
            raise DevAgentFixtureWorkspaceUnsafePath(str(current))
        try:
            relative_parts = directory.relative_to(self._root).parts
        except ValueError as exc:
            raise DevAgentFixtureWorkspaceUnsafePath(str(directory)) from exc
        for part in relative_parts:
            current = current / part
            if current.is_symlink():
                raise DevAgentFixtureWorkspaceUnsafePath(str(current))
            if not current.exists():
                return
            info = current.stat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
                raise DevAgentFixtureWorkspaceUnsafePath(str(current))


__all__ = [
    "LIST_FILES_TOOL_ID",
    "READ_FILE_TOOL_ID",
    "WRITE_NOTE_TOOL_ID",
    "DevAgentFixtureWorkspaceUnsafePath",
    "FixtureWorkspaceToolPort",
]
