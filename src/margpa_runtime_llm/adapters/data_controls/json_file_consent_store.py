"""Phase 7 (P7-G): private, single-JSON-file Data Control Consent store.

Mirrors `local_corpus_registry.JsonFileLocalCorpusRegistry`'s local-file
safety discipline (symlink rejection, owner-only modes, atomic replace) at
a scale proportionate to one small consent record.
"""

from __future__ import annotations

import json
import os
import stat
import threading
from datetime import UTC, datetime
from pathlib import Path

from margpa_runtime_llm.modules.data_controls.contracts import (
    DataControlConsent,
    DataControlConsentUpdate,
)

_SCHEMA_VERSION = 1


class DataControlsStoreUnsafePath(Exception):
    pass


class DataControlsStoreCorrupt(Exception):
    """Fail-closed: a corrupt/tampered store file is never silently reset."""


class JsonFileDataControlConsentStore:
    def __init__(self, *, runtime_data_root: Path, scope_key: str = "default") -> None:
        if not runtime_data_root.is_absolute():
            raise ValueError("runtime_data_root must be absolute")
        if not scope_key or "/" in scope_key or "\\" in scope_key or scope_key in {".", ".."}:
            raise ValueError("scope_key must be a safe single path segment")
        self._root = runtime_data_root
        self._dir = runtime_data_root / "persistent" / scope_key / "data_controls"
        self._path = self._dir / "consent.json"
        self._lock = threading.Lock()

    def get(self) -> DataControlConsent:
        with self._lock:
            return self._read()

    def update(self, patch: DataControlConsentUpdate) -> DataControlConsent:
        with self._lock:
            current = self._read()
            updated = current.model_copy(
                update={
                    **{
                        key: value
                        for key, value in patch.model_dump(exclude_unset=True).items()
                        if value is not None
                    },
                    "updated_at": datetime.now(UTC),
                }
            )
            self._write(updated)
            return updated

    def reset_to_defaults(self) -> DataControlConsent:
        with self._lock:
            defaults = DataControlConsent(updated_at=datetime.now(UTC))
            self._write(defaults)
            return defaults

    # -- private file I/O -------------------------------------------------

    def _read(self) -> DataControlConsent:
        self._validate_path_chain()
        if not self._path.exists():
            return DataControlConsent(updated_at=datetime.now(UTC))
        try:
            raw = self._path.read_text(encoding="utf-8")
            payload = json.loads(raw)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise DataControlsStoreCorrupt(str(self._path)) from exc
        if not isinstance(payload, dict) or payload.get("schema_version") != _SCHEMA_VERSION:
            raise DataControlsStoreCorrupt(str(self._path))
        try:
            return DataControlConsent.model_validate(payload.get("consent"))
        except Exception as exc:
            raise DataControlsStoreCorrupt(str(self._path)) from exc

    def _write(self, consent: DataControlConsent) -> None:
        self._ensure_private_directory()
        payload = {
            "schema_version": _SCHEMA_VERSION,
            "consent": json.loads(consent.model_dump_json()),
        }
        tmp_path = self._path.with_name(f"{self._path.name}.{os.getpid()}.tmp")
        try:
            descriptor = os.open(tmp_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True))
            os.chmod(tmp_path, 0o600)
            os.replace(tmp_path, self._path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)

    def _ensure_private_directory(self) -> None:
        missing: list[Path] = []
        current = self._dir
        while not current.exists():
            missing.append(current)
            if current == self._root:
                break
            current = current.parent
        if current.exists() and current.is_symlink():
            raise DataControlsStoreUnsafePath(str(current))
        for path in reversed(missing):
            path.mkdir(mode=0o700)
            os.chmod(path, 0o700)

    def _validate_path_chain(self) -> None:
        current = self._root
        if current.exists() and current.is_symlink():
            raise DataControlsStoreUnsafePath(str(current))
        try:
            relative_parts = self._dir.relative_to(self._root).parts
        except ValueError as exc:
            raise DataControlsStoreUnsafePath(str(self._dir)) from exc
        for part in relative_parts:
            current = current / part
            if current.is_symlink():
                raise DataControlsStoreUnsafePath(str(current))
            if not current.exists():
                return
            info = current.stat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
                raise DataControlsStoreUnsafePath(str(current))
        if self._path.exists() and self._path.is_symlink():
            raise DataControlsStoreUnsafePath(str(self._path))


__all__ = [
    "DataControlsStoreCorrupt",
    "DataControlsStoreUnsafePath",
    "JsonFileDataControlConsentStore",
]
