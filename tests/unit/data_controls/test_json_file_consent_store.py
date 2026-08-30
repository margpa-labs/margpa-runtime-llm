"""Phase 7 (P7-G): Data Control Consent JSON-file store tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.data_controls.json_file_consent_store import (
    DataControlsStoreCorrupt,
    DataControlsStoreUnsafePath,
    JsonFileDataControlConsentStore,
)
from margpa_runtime_llm.modules.data_controls.contracts import DataControlConsentUpdate


def _store(tmp_path: Path) -> JsonFileDataControlConsentStore:
    return JsonFileDataControlConsentStore(runtime_data_root=tmp_path / "runtime_data")


def test_default_consent_is_all_off(tmp_path: Path) -> None:
    consent = _store(tmp_path).get()

    assert consent.external_query_transmission_consent is False
    assert consent.feedback_research_use is False
    assert consent.synthetic_data_use is False
    assert consent.future_training_export is False


def test_partial_update_only_changes_the_specified_fields(tmp_path: Path) -> None:
    store = _store(tmp_path)

    updated = store.update(DataControlConsentUpdate(feedback_research_use=True))

    assert updated.feedback_research_use is True
    assert updated.synthetic_data_use is False
    assert updated.external_query_transmission_consent is False


def test_update_persists_across_new_store_instances(tmp_path: Path) -> None:
    first = _store(tmp_path)
    first.update(DataControlConsentUpdate(synthetic_data_use=True))

    second = _store(tmp_path)
    assert second.get().synthetic_data_use is True


def test_reset_to_defaults_restores_all_off(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.update(
        DataControlConsentUpdate(
            feedback_research_use=True,
            synthetic_data_use=True,
            future_training_export=True,
            external_query_transmission_consent=True,
        )
    )

    reset = store.reset_to_defaults()

    assert reset.feedback_research_use is False
    assert reset.synthetic_data_use is False
    assert reset.future_training_export is False
    assert reset.external_query_transmission_consent is False


def test_store_file_uses_owner_only_permissions(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.update(DataControlConsentUpdate(feedback_research_use=True))

    store_path = (
        tmp_path / "runtime_data" / "persistent" / "default" / "data_controls" / "consent.json"
    )
    assert store_path.exists()
    assert oct(store_path.stat().st_mode & 0o777) == "0o600"


def test_symlinked_store_directory_is_rejected(tmp_path: Path) -> None:
    real_target = tmp_path / "elsewhere"
    real_target.mkdir()
    runtime_data = tmp_path / "runtime_data"
    runtime_data.mkdir()
    persistent_default = runtime_data / "persistent" / "default"
    persistent_default.mkdir(parents=True)
    (persistent_default / "data_controls").symlink_to(real_target, target_is_directory=True)
    store = JsonFileDataControlConsentStore(runtime_data_root=runtime_data)

    with pytest.raises(DataControlsStoreUnsafePath):
        store.get()


def test_corrupt_store_file_fails_closed(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.update(DataControlConsentUpdate(feedback_research_use=True))
    store_path = (
        tmp_path / "runtime_data" / "persistent" / "default" / "data_controls" / "consent.json"
    )
    store_path.write_text("not json{{{", encoding="utf-8")

    with pytest.raises(DataControlsStoreCorrupt):
        store.get()
