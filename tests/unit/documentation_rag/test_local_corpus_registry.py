"""Phase 7 (P7-B): Local Corpus JSON-file registry CRUD and safety tests."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.documentation_rag.local_corpus_registry import (
    JsonFileLocalCorpusRegistry,
    LocalCorpusRegistryCorrupt,
    LocalCorpusRegistryUnsafePath,
)
from margpa_runtime_llm.modules.documentation_rag.local_corpus_contracts import (
    MAX_ACTIVE_DOCUMENTS,
    LocalCorpusDocumentInput,
    LocalCorpusDocumentNotFound,
    LocalCorpusDocumentState,
    LocalCorpusLimitExceeded,
)


def _registry(tmp_path: Path) -> JsonFileLocalCorpusRegistry:
    return JsonFileLocalCorpusRegistry(runtime_data_root=tmp_path / "runtime_data")


def test_register_then_list_active_round_trips(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    record = registry.register(
        LocalCorpusDocumentInput(
            title="MARGPA概要", content="MARGPAはRuntime Governance Frameworkです。"
        )
    )

    assert record.state is LocalCorpusDocumentState.ACTIVE
    assert record.current_revision == 1
    assert len(record.revisions) == 1
    active = registry.list_active()
    assert active == (record,)
    assert registry.get(record.document_id) == record


def test_update_appends_a_new_revision_and_keeps_history(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    created = registry.register(LocalCorpusDocumentInput(title="v1", content="content v1"))

    updated = registry.update(
        created.document_id,
        LocalCorpusDocumentInput(title="v2", content="content v2"),
    )

    assert updated.current_revision == 2
    assert [entry.revision for entry in updated.revisions] == [1, 2]
    assert updated.revisions[0].content_sha512 != updated.revisions[1].content_sha512
    assert updated.revisions[0].title == "v1"
    assert updated.revisions[1].title == "v2"
    assert updated.content == "content v2"


def test_delete_is_soft_and_preserves_revisions(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    created = registry.register(LocalCorpusDocumentInput(title="t", content="c"))

    deleted = registry.delete(created.document_id)

    assert deleted.state is LocalCorpusDocumentState.DELETED
    assert deleted.revisions == created.revisions
    assert registry.list_active() == ()
    assert registry.list_all() == (deleted,)
    assert registry.get(created.document_id) == deleted


def test_update_or_delete_of_unknown_document_raises_not_found(tmp_path: Path) -> None:
    registry = _registry(tmp_path)

    with pytest.raises(LocalCorpusDocumentNotFound):
        registry.update("0" * 32, LocalCorpusDocumentInput(title="t", content="c"))
    with pytest.raises(LocalCorpusDocumentNotFound):
        registry.delete("0" * 32)


def test_update_or_delete_of_already_deleted_document_raises_not_found(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    created = registry.register(LocalCorpusDocumentInput(title="t", content="c"))
    registry.delete(created.document_id)

    with pytest.raises(LocalCorpusDocumentNotFound):
        registry.delete(created.document_id)
    with pytest.raises(LocalCorpusDocumentNotFound):
        registry.update(created.document_id, LocalCorpusDocumentInput(title="t2", content="c2"))


def test_document_count_limit_is_enforced(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    for index in range(MAX_ACTIVE_DOCUMENTS):
        registry.register(LocalCorpusDocumentInput(title=f"doc-{index}", content="x"))

    with pytest.raises(LocalCorpusLimitExceeded) as captured:
        registry.register(LocalCorpusDocumentInput(title="overflow", content="x"))
    assert captured.value.code == "local_corpus_document_limit_exceeded"


def test_deleting_a_document_frees_its_slot_in_the_count_limit(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    records = [
        registry.register(LocalCorpusDocumentInput(title=f"doc-{index}", content="x"))
        for index in range(MAX_ACTIVE_DOCUMENTS)
    ]
    registry.delete(records[0].document_id)

    # Must not raise: one slot was freed by the soft-delete above.
    registry.register(LocalCorpusDocumentInput(title="new", content="x"))


def test_persists_across_new_registry_instances(tmp_path: Path) -> None:
    first = _registry(tmp_path)
    created = first.register(LocalCorpusDocumentInput(title="t", content="c"))

    second = _registry(tmp_path)
    assert second.get(created.document_id) == created


def test_store_file_and_directories_use_owner_only_permissions(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    registry.register(LocalCorpusDocumentInput(title="t", content="c"))

    store_path = (
        tmp_path / "runtime_data" / "persistent" / "default" / "local_corpus" / "documents.json"
    )
    assert store_path.exists()
    assert oct(store_path.stat().st_mode & 0o777) == "0o600"
    assert oct(store_path.parent.stat().st_mode & 0o777) == "0o700"


def test_symlinked_store_directory_is_rejected(tmp_path: Path) -> None:
    real_target = tmp_path / "elsewhere"
    real_target.mkdir()
    runtime_data = tmp_path / "runtime_data"
    runtime_data.mkdir()
    persistent_default = runtime_data / "persistent" / "default"
    persistent_default.mkdir(parents=True)
    (persistent_default / "local_corpus").symlink_to(real_target, target_is_directory=True)
    registry = JsonFileLocalCorpusRegistry(runtime_data_root=runtime_data)

    with pytest.raises(LocalCorpusRegistryUnsafePath):
        registry.list_active()


def test_corrupt_store_file_fails_closed_rather_than_silently_resetting(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    registry.register(LocalCorpusDocumentInput(title="t", content="c"))
    store_path = (
        tmp_path / "runtime_data" / "persistent" / "default" / "local_corpus" / "documents.json"
    )
    store_path.write_text("not json{{{", encoding="utf-8")

    with pytest.raises(LocalCorpusRegistryCorrupt):
        registry.list_active()


def test_document_store_path_matches_the_actual_read_write_location(tmp_path: Path) -> None:
    """P7-RW5-C (P7-CODEX-016): the exposed `document_store_path` must be
    the exact same File the Registry itself reads/writes, dynamically
    derived from the `runtime_data_root`/`scope_key` this instance was
    constructed with - never a Hard-coded literal."""
    registry = JsonFileLocalCorpusRegistry(
        runtime_data_root=tmp_path / "runtime_data", scope_key="another-scope"
    )
    registry.register(LocalCorpusDocumentInput(title="t", content="c"))

    assert registry.document_store_path == (
        tmp_path
        / "runtime_data"
        / "persistent"
        / "another-scope"
        / "local_corpus"
        / "documents.json"
    )
    assert registry.document_store_path.exists()


def test_write_is_atomic_no_partial_file_survives_on_replace(tmp_path: Path) -> None:
    registry = _registry(tmp_path)
    registry.register(LocalCorpusDocumentInput(title="t", content="c"))
    store_dir = tmp_path / "runtime_data" / "persistent" / "default" / "local_corpus"

    leftovers = [entry for entry in os.listdir(store_dir) if entry.endswith(".tmp")]
    assert leftovers == []
    payload = json.loads((store_dir / "documents.json").read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
