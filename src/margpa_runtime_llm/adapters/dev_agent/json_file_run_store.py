"""Phase 8 (P8-E): private, one-JSON-file-per-Run Dev Agent Run store.

Mirrors `data_controls.JsonFileDataControlConsentStore`'s local-file safety
discipline (symlink rejection, owner-only modes, atomic replace), extended
to one file per Run (`{run_id}.json`) so `load_all()` can reconstruct every
Run that existed before the process stopped — this is the whole of
Restart/Reload Recovery for the Dev Agent Foundation; there is no database.
"""

from __future__ import annotations

import json
import logging
import os
import stat
from pathlib import Path
from threading import Lock

from margpa_runtime_llm.modules.dev_agent import RunSnapshot

_SCHEMA_VERSION = 1
_logger = logging.getLogger(__name__)


class DevAgentRunStoreUnsafePath(Exception):
    pass


class DevAgentRunStoreCorrupt(Exception):
    """Raised by `save()`/for a single-file read; `load_all()` itself never
    raises this — a corrupt Run file is logged and skipped so one bad file
    can never block every other Run from reloading (see `load_all()`)."""


def _safe_filename_segment(value: str) -> bool:
    return bool(value) and value not in {".", ".."} and all(c.isalnum() or c in "-_" for c in value)


class JsonFileDevAgentRunStore:
    def __init__(self, *, runtime_data_root: Path, scope_key: str = "default") -> None:
        if not runtime_data_root.is_absolute():
            raise ValueError("runtime_data_root must be absolute")
        if not _safe_filename_segment(scope_key):
            raise ValueError("scope_key must be a safe single path segment")
        self._root = runtime_data_root
        self._dir = runtime_data_root / "persistent" / scope_key / "dev_agent" / "runs"
        self._lock = Lock()

    def save(self, run: RunSnapshot) -> None:
        with self._lock:
            if not _safe_filename_segment(run.run_id):
                raise DevAgentRunStoreUnsafePath(run.run_id)
            self._validate_path_chain()
            self._ensure_private_directory()
            path = self._path_for(run.run_id)
            payload = {
                "schema_version": _SCHEMA_VERSION,
                "run": json.loads(run.model_dump_json()),
            }
            tmp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
            try:
                descriptor = os.open(tmp_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
                os.chmod(tmp_path, 0o600)
                os.replace(tmp_path, path)
            finally:
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)

    def load_all(self) -> tuple[RunSnapshot, ...]:
        with self._lock:
            self._validate_path_chain()
            if not self._dir.exists():
                return ()
            runs: list[RunSnapshot] = []
            for path in sorted(self._dir.glob("*.json")):
                try:
                    runs.append(self._read_one(path))
                except DevAgentRunStoreCorrupt:
                    _logger.warning("dev_agent run store: skipping unreadable Run file at %s", path)
            return tuple(runs)

    # -- private file I/O -------------------------------------------------

    def _read_one(self, path: Path) -> RunSnapshot:
        try:
            raw = path.read_text(encoding="utf-8")
            payload = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DevAgentRunStoreCorrupt(str(path)) from exc
        if not isinstance(payload, dict) or payload.get("schema_version") != _SCHEMA_VERSION:
            raise DevAgentRunStoreCorrupt(str(path))
        try:
            return RunSnapshot.model_validate(payload.get("run"))
        except Exception as exc:
            raise DevAgentRunStoreCorrupt(str(path)) from exc

    def _path_for(self, run_id: str) -> Path:
        return self._dir / f"{run_id}.json"

    def _ensure_private_directory(self) -> None:
        missing: list[Path] = []
        current = self._dir
        while not current.exists():
            missing.append(current)
            if current == self._root:
                break
            current = current.parent
        if current.exists() and current.is_symlink():
            raise DevAgentRunStoreUnsafePath(str(current))
        for path in reversed(missing):
            path.mkdir(mode=0o700)
            os.chmod(path, 0o700)

    def _validate_path_chain(self) -> None:
        current = self._root
        if current.exists() and current.is_symlink():
            raise DevAgentRunStoreUnsafePath(str(current))
        try:
            relative_parts = self._dir.relative_to(self._root).parts
        except ValueError as exc:
            raise DevAgentRunStoreUnsafePath(str(self._dir)) from exc
        for part in relative_parts:
            current = current / part
            if current.is_symlink():
                raise DevAgentRunStoreUnsafePath(str(current))
            if not current.exists():
                return
            info = current.stat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
                raise DevAgentRunStoreUnsafePath(str(current))


__all__ = [
    "DevAgentRunStoreCorrupt",
    "DevAgentRunStoreUnsafePath",
    "JsonFileDevAgentRunStore",
]
