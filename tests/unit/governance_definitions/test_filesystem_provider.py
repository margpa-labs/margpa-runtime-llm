"""FilesystemDefinitionProvider: explicit Root/Manifest only, no directory
scan, no filename inference, no symlink escape (P3-C-WU-003)."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.governance_definitions import (
    filesystem_provider as filesystem_provider_module,
)
from margpa_runtime_llm.adapters.governance_definitions.filesystem_provider import (
    FilesystemDefinitionProvider,
)
from margpa_runtime_llm.modules.governance_definitions.domain import (
    DefinitionEntry,
    PackageManifest,
    PackageState,
    ProviderState,
    SourceEntry,
    SourceState,
    sign_manifest,
)
from margpa_runtime_llm.modules.governance_definitions.ports import PackageLoadRequest


def _write_source(root: Path, relative: str, payload: dict[str, object]) -> tuple[str, int, str]:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload).encode("utf-8")
    path.write_bytes(raw)
    return relative, len(raw), hashlib.sha512(raw).hexdigest()


def _write_raw_source(root: Path, relative: str, raw: bytes) -> tuple[str, int, str]:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return relative, len(raw), hashlib.sha512(raw).hexdigest()


def _write_manifest(root: Path, source_entries: tuple[SourceEntry, ...]) -> None:
    # Built through the same PackageManifest/sign_manifest path production
    # code uses, so the digest is computed exactly like the real Provider
    # expects (including pydantic-default fields a hand-rolled dict would
    # silently omit from its own digest input).
    manifest = PackageManifest(
        package_id="test-bundle",
        package_version="1",
        publisher="Test",
        license="CC0",
        source_entries=source_entries,
        definition_entries=(
            DefinitionEntry(
                definition_id="x",
                definition_version="1",
                display_name="X",
                domain="x_domain",
                source_id=source_entries[0].source_id,
                source_object_pointer="$.x",
                extension_archetype="common_domain_extension",
            ),
        ),
    )
    signed = sign_manifest(manifest)
    (root / "manifest.json").write_text(signed.model_dump_json(), encoding="utf-8")


def _valid_provider_root(tmp_path: Path) -> Path:
    root = tmp_path / "definitions"
    relative, byte_length, digest = _write_source(root, "x.json", {"x": "value"})
    _write_manifest(
        root,
        (
            SourceEntry(
                source_id="x",
                relative_path=f"definitions/{relative}",
                media_type="application/json",
                byte_length=byte_length,
                content_digest_sha512=digest,
                schema_id="s",
                trusted_adapter_id="a",
                logical_definition_ids=("x",),
            ),
        ),
    )
    return root


def test_describe_reports_ready_for_a_valid_manifest(tmp_path: Path) -> None:
    root = _valid_provider_root(tmp_path)
    provider = FilesystemDefinitionProvider(root=root)
    assert provider.describe().state is ProviderState.READY


def test_describe_reports_not_configured_when_manifest_is_missing(tmp_path: Path) -> None:
    root = tmp_path / "definitions"
    root.mkdir()
    provider = FilesystemDefinitionProvider(root=root)
    assert provider.describe().state is ProviderState.NOT_CONFIGURED


def test_load_package_validates_matching_sources(tmp_path: Path) -> None:
    root = _valid_provider_root(tmp_path)
    provider = FilesystemDefinitionProvider(root=root)
    result = provider.load_package(PackageLoadRequest())
    assert result.found is True
    assert result.package_state is PackageState.VALIDATED
    assert result.manifest is not None
    assert result.manifest.package_id == "test-bundle"


def test_load_package_detects_size_mismatch(tmp_path: Path) -> None:
    root = _valid_provider_root(tmp_path)
    (root / "x.json").write_bytes(b'{"x": "value", "extra": "padding-changes-length"}')
    provider = FilesystemDefinitionProvider(root=root)
    verifications = provider.verify_sources(provider._load_signed_manifest())
    assert verifications[0].state is SourceState.SIZE_MISMATCH


def test_load_package_detects_digest_mismatch_with_same_length(tmp_path: Path) -> None:
    root = _valid_provider_root(tmp_path)
    original = (root / "x.json").read_bytes()
    # Same byte length, different content/digest.
    tampered = original[:-2] + b"9}"
    assert len(tampered) == len(original)
    (root / "x.json").write_bytes(tampered)

    provider = FilesystemDefinitionProvider(root=root)
    verifications = provider.verify_sources(provider._load_signed_manifest())
    assert verifications[0].state is SourceState.DIGEST_MISMATCH


def test_rejects_manifest_relative_path_with_parent_traversal(tmp_path: Path) -> None:
    root = tmp_path / "definitions"
    root.mkdir()
    provider = FilesystemDefinitionProvider(
        root=root, manifest_relative_path="../outside/manifest.json"
    )
    assert provider.describe().state is ProviderState.UNAVAILABLE


def test_rejects_absolute_manifest_path(tmp_path: Path) -> None:
    root = tmp_path / "definitions"
    root.mkdir()
    provider = FilesystemDefinitionProvider(root=root, manifest_relative_path="/etc/passwd")
    assert provider.describe().state is ProviderState.UNAVAILABLE


def test_rejects_symlinked_manifest(tmp_path: Path) -> None:
    root = tmp_path / "definitions"
    root.mkdir()
    outside = tmp_path / "outside_manifest.json"
    outside.write_text("{}")
    (root / "manifest.json").symlink_to(outside)

    provider = FilesystemDefinitionProvider(root=root)
    assert provider.describe().state is ProviderState.UNAVAILABLE


def test_load_package_respects_requested_package_id_mismatch(tmp_path: Path) -> None:
    root = _valid_provider_root(tmp_path)
    provider = FilesystemDefinitionProvider(root=root)
    result = provider.load_package(PackageLoadRequest(requested_package_id="a-different-package"))
    assert result.found is False


# -- P3-CODEX-004: symlink components, path-prefix mismatch, and Size
# Gates must fail closed into a Typed result, never an uncaught exception.


def test_rejects_source_reached_through_a_symlinked_intermediate_directory(
    tmp_path: Path,
) -> None:
    root = tmp_path / "definitions"
    real_subdir = root / "real"
    relative, byte_length, digest = _write_source(root, "real/x.json", {"x": "value"})
    linked_subdir = root / "linked"
    linked_subdir.symlink_to(real_subdir, target_is_directory=True)
    _write_manifest(
        root,
        (
            SourceEntry(
                source_id="x",
                relative_path="definitions/linked/x.json",
                media_type="application/json",
                byte_length=byte_length,
                content_digest_sha512=digest,
                schema_id="s",
                trusted_adapter_id="a",
                logical_definition_ids=("x",),
            ),
        ),
    )
    del relative

    provider = FilesystemDefinitionProvider(root=root)
    verifications = provider.verify_sources(provider._load_signed_manifest())
    assert verifications[0].state is SourceState.INVALID
    assert verifications[0].reason_code == "path_unsafe"


def test_verify_sources_reports_path_prefix_mismatch_without_crashing(tmp_path: Path) -> None:
    root = _valid_provider_root(tmp_path)
    provider = FilesystemDefinitionProvider(root=root)
    signed = provider._load_signed_manifest()
    mismatched = signed.manifest.source_entries[0].model_copy(
        update={"relative_path": "not-definitions/x.json"}
    )
    manifest_with_bad_prefix = signed.manifest.model_copy(update={"source_entries": (mismatched,)})

    verifications = provider.verify_sources(
        signed.model_copy(update={"manifest": manifest_with_bad_prefix})
    )
    assert verifications[0].state is SourceState.INVALID
    assert verifications[0].reason_code == "path_prefix_mismatch"


def test_load_package_reports_manifest_too_large_without_crashing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _valid_provider_root(tmp_path)
    monkeypatch.setattr(filesystem_provider_module, "MAX_MANIFEST_BYTES", 1)
    provider = FilesystemDefinitionProvider(root=root)

    assert provider.describe().unavailable_reason_code == "manifest_too_large"
    result = provider.load_package(PackageLoadRequest())
    assert result.found is True
    assert result.package_state is PackageState.INVALID
    assert result.reason_code == "manifest_too_large"


def test_verify_sources_reports_source_too_large_without_crashing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _valid_provider_root(tmp_path)
    monkeypatch.setattr(filesystem_provider_module, "MAX_SOURCE_BYTES", 1)
    provider = FilesystemDefinitionProvider(root=root)

    verifications = provider.verify_sources(provider._load_signed_manifest())
    assert verifications[0].state is SourceState.UNSUPPORTED
    assert verifications[0].reason_code == "source_too_large"


# -- P3-CODEX-007: verified content is captured from the same read that
# checked Size/Digest — a Malformed JSON, non-object JSON, or symlinked
# leaf Source must fail closed here, and the captured content must never
# be re-derived from a later, separate disk read. --------------------


def test_malformed_json_source_is_reported_invalid_and_excluded_from_verified_content(
    tmp_path: Path,
) -> None:
    root = tmp_path / "definitions"
    relative, byte_length, digest = _write_raw_source(root, "x.json", b"{not valid json")
    _write_manifest(
        root,
        (
            SourceEntry(
                source_id="x",
                relative_path=f"definitions/{relative}",
                media_type="application/json",
                byte_length=byte_length,
                content_digest_sha512=digest,
                schema_id="s",
                trusted_adapter_id="a",
                logical_definition_ids=("x",),
            ),
        ),
    )
    provider = FilesystemDefinitionProvider(root=root)

    verifications = provider.verify_sources(provider._load_signed_manifest())
    assert verifications[0].state is SourceState.INVALID
    assert verifications[0].reason_code == "malformed_json"

    result = provider.load_package(PackageLoadRequest())
    assert "x" not in result.verified_source_json


def test_non_object_json_source_is_reported_invalid(tmp_path: Path) -> None:
    root = tmp_path / "definitions"
    relative, byte_length, digest = _write_raw_source(root, "x.json", b"[1, 2, 3]")
    _write_manifest(
        root,
        (
            SourceEntry(
                source_id="x",
                relative_path=f"definitions/{relative}",
                media_type="application/json",
                byte_length=byte_length,
                content_digest_sha512=digest,
                schema_id="s",
                trusted_adapter_id="a",
                logical_definition_ids=("x",),
            ),
        ),
    )
    provider = FilesystemDefinitionProvider(root=root)

    verifications = provider.verify_sources(provider._load_signed_manifest())
    assert verifications[0].state is SourceState.INVALID
    assert verifications[0].reason_code == "not_a_json_object"


def test_rejects_a_source_file_that_is_itself_a_symlink(tmp_path: Path) -> None:
    root = tmp_path / "definitions"
    root.mkdir()
    real_target = tmp_path / "outside_source.json"
    payload = json.dumps({"x": "value"}).encode("utf-8")
    real_target.write_bytes(payload)
    linked = root / "x.json"
    linked.symlink_to(real_target)

    _write_manifest(
        root,
        (
            SourceEntry(
                source_id="x",
                relative_path="definitions/x.json",
                media_type="application/json",
                byte_length=len(payload),
                content_digest_sha512=hashlib.sha512(payload).hexdigest(),
                schema_id="s",
                trusted_adapter_id="a",
                logical_definition_ids=("x",),
            ),
        ),
    )
    provider = FilesystemDefinitionProvider(root=root)

    verifications = provider.verify_sources(provider._load_signed_manifest())
    assert verifications[0].state is SourceState.INVALID
    assert verifications[0].reason_code == "path_unsafe"


def test_verified_source_json_matches_the_exact_digest_verified_bytes(tmp_path: Path) -> None:
    root = _valid_provider_root(tmp_path)
    provider = FilesystemDefinitionProvider(root=root)

    result = provider.load_package(PackageLoadRequest())
    assert result.verified_source_json == {"x": {"x": "value"}}


def test_a_disk_change_after_load_package_returns_never_affects_the_captured_content(
    tmp_path: Path,
) -> None:
    """P3-CODEX-007's core property: `verified_source_json` is a captured
    snapshot from the one read that verified Size/Digest — there is no
    second, later re-read for a caller (the Runtime) to race against."""

    root = _valid_provider_root(tmp_path)
    provider = FilesystemDefinitionProvider(root=root)

    result = provider.load_package(PackageLoadRequest())
    captured = result.verified_source_json["x"]

    # Swap the on-disk file after the verified read already happened.
    (root / "x.json").write_bytes(json.dumps({"x": "swapped-after-verification"}).encode("utf-8"))

    assert captured == {"x": "value"}  # the already-returned snapshot is untouched
    assert result.verified_source_json["x"] == {"x": "value"}


# -- P3-CODEX-010: the Verified Read itself must be a single dir_fd-chain
# Open/Read boundary — a symlinked parent applies to the Manifest exactly
# like it already did to a Source, and a non-regular leaf (FIFO/device)
# must fail closed without ever blocking the process. ------------------


def test_manifest_reached_through_a_symlinked_intermediate_directory_is_rejected(
    tmp_path: Path,
) -> None:
    root = tmp_path / "definitions"
    real_subdir = root / "real"
    real_subdir.mkdir(parents=True)
    (real_subdir / "manifest.json").write_text("{}", encoding="utf-8")
    linked_subdir = root / "linked"
    linked_subdir.symlink_to(real_subdir, target_is_directory=True)

    provider = FilesystemDefinitionProvider(
        root=root, manifest_relative_path="linked/manifest.json"
    )
    descriptor = provider.describe()
    assert descriptor.state is ProviderState.UNAVAILABLE
    assert descriptor.unavailable_reason_code == "manifest_path_unsafe"

    result = provider.load_package(PackageLoadRequest())
    assert result.found is False


def test_a_fifo_replacing_a_source_leaf_is_rejected_without_blocking(tmp_path: Path) -> None:
    root = tmp_path / "definitions"
    root.mkdir()
    os.mkfifo(root / "x.json")  # a reader-blocking non-regular file
    _write_manifest(
        root,
        (
            SourceEntry(
                source_id="x",
                relative_path="definitions/x.json",
                media_type="application/json",
                byte_length=2,
                content_digest_sha512="0" * 128,
                schema_id="s",
                trusted_adapter_id="a",
                logical_definition_ids=("x",),
            ),
        ),
    )
    provider = FilesystemDefinitionProvider(root=root)

    # Would hang forever pre-fix if the leaf open ever blocked on the FIFO.
    verifications = provider.verify_sources(provider._load_signed_manifest())
    assert verifications[0].state is SourceState.UNSUPPORTED
    assert verifications[0].reason_code == "not_a_regular_file"


def test_a_fifo_replacing_the_manifest_is_rejected_without_blocking(tmp_path: Path) -> None:
    root = tmp_path / "definitions"
    root.mkdir()
    os.mkfifo(root / "manifest.json")

    provider = FilesystemDefinitionProvider(root=root)

    # Would hang forever pre-fix if the leaf open ever blocked on the FIFO.
    descriptor = provider.describe()
    assert descriptor.state is ProviderState.FAILED
    assert descriptor.unavailable_reason_code == "manifest_unparseable"
