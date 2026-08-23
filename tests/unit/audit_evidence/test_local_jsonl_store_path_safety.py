"""LocalJsonlEvidenceStore root/scope/path safety (P3-B-WU-001)."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.audit_evidence.local_jsonl_store import (
    LocalJsonlEvidenceStore,
)
from margpa_runtime_llm.modules.audit_evidence.domain.errors import (
    EvidenceStoreError,
    EvidenceStoreErrorCode,
)


def test_store_creates_private_scope_directory(tmp_path: Path) -> None:
    store = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")

    scope_dir = tmp_path / "scope-a"
    segments_dir = scope_dir / "segments"
    assert segments_dir.is_dir()
    assert stat.S_IMODE(segments_dir.stat().st_mode) == 0o700
    assert stat.S_IMODE(scope_dir.stat().st_mode) == 0o700
    assert store.status().event_count == 0


def test_store_rejects_scope_with_path_separators(tmp_path: Path) -> None:
    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="../escape")
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION


def test_store_rejects_empty_scope(tmp_path: Path) -> None:
    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="")
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION


def test_store_rejects_symlinked_scope_directory(tmp_path: Path) -> None:
    real_target = tmp_path / "outside"
    real_target.mkdir(mode=0o700)
    (tmp_path / "root").mkdir(mode=0o700)
    symlinked_scope = tmp_path / "root" / "scope-a"
    symlinked_scope.symlink_to(real_target, target_is_directory=True)

    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path / "root", relative_root="", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION


def test_store_rejects_group_or_world_writable_existing_directory(tmp_path: Path) -> None:
    scope_dir = tmp_path / "scope-a"
    (scope_dir / "segments").mkdir(parents=True, mode=0o777)
    os.chmod(scope_dir / "segments", 0o777)
    os.chmod(scope_dir, 0o777)

    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION


def test_two_scopes_are_independent(tmp_path: Path) -> None:
    store_a = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-a")
    store_b = LocalJsonlEvidenceStore(anchor=tmp_path, relative_root="", scope="scope-b")

    assert store_a.status().event_count == 0
    assert store_b.status().event_count == 0
    assert (tmp_path / "scope-a").resolve() != (tmp_path / "scope-b").resolve()


# -- P3-CODEX-012 Finding A: `anchor` and every `relative_root` component
# must go through the same O_NOFOLLOW dir_fd chain as `scope`/`segments`
# — a previous version called `root.expanduser().resolve()` before ever
# starting that chain, silently following a symlink planted at the
# configured root (or any ancestor) into a new, unverified "trusted"
# anchor. ------------------------------------------------------------


def test_anchor_itself_a_symlink_is_rejected_without_creating_anything_at_the_target(
    tmp_path: Path,
) -> None:
    real_target = tmp_path / "real-anchor"
    real_target.mkdir(mode=0o700)
    symlinked_anchor = tmp_path / "symlinked-anchor"
    symlinked_anchor.symlink_to(real_target, target_is_directory=True)

    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(anchor=symlinked_anchor, relative_root="evidence", scope="scope-a")
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION
    # Nothing was ever created through the symlink at the real target.
    assert list(real_target.iterdir()) == []


def test_relative_root_component_that_is_a_symlink_is_rejected_without_creating_anything(
    tmp_path: Path,
) -> None:
    anchor = tmp_path / "anchor"
    anchor.mkdir(mode=0o700)
    outside = tmp_path / "outside-runtime-data"
    outside.mkdir(mode=0o700)
    # A pre-planted symlink standing in for `runtime_data/` — the exact
    # component a single `.resolve()` on the old combined `root` would
    # have silently followed before the dir_fd chain ever started.
    (anchor / "runtime_data").symlink_to(outside, target_is_directory=True)

    with pytest.raises(EvidenceStoreError) as excinfo:
        LocalJsonlEvidenceStore(
            anchor=anchor, relative_root="runtime_data/audit_evidence", scope="scope-a"
        )
    assert excinfo.value.code is EvidenceStoreErrorCode.PATH_VIOLATION
    assert list(outside.iterdir()) == []
