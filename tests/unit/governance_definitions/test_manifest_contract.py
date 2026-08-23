"""Manifest schema and self-consistency (P3-C-WU-001).

Deliberately reads the real `definitions/` tree (immutable Reference
Bundle input, not user-runtime data) rather than a fixture, so drift
between `manifest.json` and the actual files is caught directly."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.governance_definitions.domain import (
    DefinitionEntry,
    PackageManifest,
    SignedPackageManifest,
    SourceEntry,
    sign_manifest,
    verify_signed_manifest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITIONS_ROOT = PROJECT_ROOT / "definitions"
MANIFEST_PATH = DEFINITIONS_ROOT / "manifest.json"

EXPECTED_DEFINITION_IDS = {
    "argd",
    "dagd",
    "cdogd",
    "sppgd",
    "daagd",
    "sdagd",
    "sdmrgd",
    "dsgd",
    "acrgd",
    "aagd",
    "aisgd",
    "mpgd",
    "dcagd",
    "pmogd",
    "airgd",
    "aiagd",
    "segd",
    "omrgd",
}


@pytest.fixture(scope="module")
def signed_manifest() -> SignedPackageManifest:
    raw = MANIFEST_PATH.read_text(encoding="utf-8")
    return SignedPackageManifest.model_validate_json(raw)


def test_manifest_digest_is_self_consistent(signed_manifest: SignedPackageManifest) -> None:
    assert verify_signed_manifest(signed_manifest) is True


def test_manifest_digest_excludes_itself_from_its_own_input(
    signed_manifest: SignedPackageManifest,
) -> None:
    resigned = sign_manifest(signed_manifest.manifest)
    assert resigned.manifest_digest_sha512 == signed_manifest.manifest_digest_sha512


def test_manifest_covers_exactly_seventeen_sources_and_eighteen_definitions(
    signed_manifest: SignedPackageManifest,
) -> None:
    manifest = signed_manifest.manifest
    assert len(manifest.source_entries) == 17
    assert len(manifest.definition_entries) == 18


def test_manifest_definition_ids_match_expected_catalog(
    signed_manifest: SignedPackageManifest,
) -> None:
    observed = {entry.definition_id for entry in signed_manifest.manifest.definition_entries}
    assert observed == EXPECTED_DEFINITION_IDS


@pytest.mark.parametrize(
    "field",
    ["byte_length", "content_digest_sha512", "relative_path"],
)
def test_every_source_entry_matches_the_file_on_disk(
    signed_manifest: SignedPackageManifest, field: str
) -> None:
    for entry in signed_manifest.manifest.source_entries:
        source_path = PROJECT_ROOT / entry.relative_path
        assert source_path.is_relative_to(DEFINITIONS_ROOT)
        assert source_path.is_file()
        raw = source_path.read_bytes()

        if field == "byte_length":
            assert entry.byte_length == len(raw)
        elif field == "content_digest_sha512":
            assert entry.content_digest_sha512 == hashlib.sha512(raw).hexdigest()
        elif field == "relative_path":
            assert source_path.exists()


def test_every_definition_entry_object_pointer_resolves_in_its_source(
    signed_manifest: SignedPackageManifest,
) -> None:
    sources_by_id = {entry.source_id: entry for entry in signed_manifest.manifest.source_entries}

    for definition in signed_manifest.manifest.definition_entries:
        source_entry = sources_by_id[definition.source_id]
        assert definition.definition_id in source_entry.logical_definition_ids

        data = json.loads((PROJECT_ROOT / source_entry.relative_path).read_bytes())
        pointer_parts = definition.source_object_pointer.removeprefix("$.").split(".")
        node: object = data
        for part in pointer_parts:
            assert isinstance(node, dict) and part in node
            node = node[part]
        assert isinstance(node, dict)  # resolves to a definition object, not a leaf


def test_reference_bundle_adapter_classes_partition_as_designed(
    signed_manifest: SignedPackageManifest,
) -> None:
    by_adapter: dict[str, list[str]] = {}
    for entry in signed_manifest.manifest.source_entries:
        by_adapter.setdefault(entry.trusted_adapter_id, []).extend(entry.logical_definition_ids)

    assert by_adapter["argd_dagd_combined_v1"] == ["argd", "dagd"]
    assert by_adapter["cdogd_v1"] == ["cdogd"]
    assert len(by_adapter["common_domain_extension_v1"]) == 15


def test_manifest_directory_listing_excludes_ds_store_and_manifest_itself(
    signed_manifest: SignedPackageManifest,
) -> None:
    manifest_paths = {entry.relative_path for entry in signed_manifest.manifest.source_entries}
    assert "definitions/manifest.json" not in manifest_paths

    actual_json_files = {
        str(path.relative_to(PROJECT_ROOT))
        for path in DEFINITIONS_ROOT.rglob("*.json")
        if path.name != "manifest.json"
    }
    assert manifest_paths == actual_json_files

    ds_store_files = list(DEFINITIONS_ROOT.rglob(".DS_Store"))
    for ds_store in ds_store_files:
        assert str(ds_store.relative_to(PROJECT_ROOT)) not in manifest_paths


def test_source_entry_rejects_empty_logical_definition_ids() -> None:
    with pytest.raises(ValidationError):
        SourceEntry(
            source_id="x",
            relative_path="definitions/x.json",
            media_type="application/json",
            byte_length=1,
            content_digest_sha512="0" * 128,
            schema_id="s",
            trusted_adapter_id="a",
            logical_definition_ids=(),
        )


def test_definition_entry_rejects_malformed_object_pointer() -> None:
    with pytest.raises(ValidationError):
        DefinitionEntry(
            definition_id="x",
            definition_version="1",
            display_name="X",
            domain="x_domain",
            source_id="x",
            source_object_pointer="not-a-pointer",
            extension_archetype="common_domain_extension",
        )


def test_package_manifest_requires_at_least_one_source_and_definition() -> None:
    with pytest.raises(ValidationError):
        PackageManifest(
            package_id="p",
            package_version="1",
            publisher="pub",
            license="lic",
            source_entries=(),
            definition_entries=(),
        )


# -- P3-CODEX-004: finite resource limits (P3-PER-001) ------------------


def _fake_source(index: int) -> SourceEntry:
    return SourceEntry(
        source_id=f"src-{index:06d}",
        relative_path=f"definitions/fake-{index:06d}.json",
        media_type="application/json",
        byte_length=1,
        content_digest_sha512="0" * 128,
        schema_id="s",
        trusted_adapter_id="a",
        logical_definition_ids=(f"def-{index:06d}",),
    )


def test_relative_path_at_the_max_depth_is_accepted_one_beyond_is_rejected() -> None:
    from margpa_runtime_llm.modules.governance_definitions.domain.limits import (
        MAX_RELATIVE_PATH_DEPTH,
    )

    at_limit = "/".join(["a"] * MAX_RELATIVE_PATH_DEPTH)
    SourceEntry(
        source_id="x",
        relative_path=at_limit,
        media_type="application/json",
        byte_length=1,
        content_digest_sha512="0" * 128,
        schema_id="s",
        trusted_adapter_id="a",
        logical_definition_ids=("x",),
    )

    beyond_limit = "/".join(["a"] * (MAX_RELATIVE_PATH_DEPTH + 1))
    with pytest.raises(ValidationError):
        SourceEntry(
            source_id="x",
            relative_path=beyond_limit,
            media_type="application/json",
            byte_length=1,
            content_digest_sha512="0" * 128,
            schema_id="s",
            trusted_adapter_id="a",
            logical_definition_ids=("x",),
        )


def test_package_manifest_source_entries_beyond_the_count_limit_is_rejected() -> None:
    from margpa_runtime_llm.modules.governance_definitions.domain.limits import (
        MAX_SOURCE_ENTRY_COUNT,
    )

    definitions = (
        DefinitionEntry(
            definition_id="d",
            definition_version="1",
            display_name="D",
            domain="d_domain",
            source_id="src-000000",
            source_object_pointer="$.d",
            extension_archetype="common_domain_extension",
        ),
    )

    at_limit_sources = tuple(_fake_source(i) for i in range(MAX_SOURCE_ENTRY_COUNT))
    PackageManifest(
        package_id="p",
        package_version="1",
        publisher="pub",
        license="lic",
        source_entries=at_limit_sources,
        definition_entries=definitions,
    )

    beyond_limit_sources = tuple(_fake_source(i) for i in range(MAX_SOURCE_ENTRY_COUNT + 1))
    with pytest.raises(ValidationError):
        PackageManifest(
            package_id="p",
            package_version="1",
            publisher="pub",
            license="lic",
            source_entries=beyond_limit_sources,
            definition_entries=definitions,
        )
