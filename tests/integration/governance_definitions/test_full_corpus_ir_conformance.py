"""Full Corpus IR Conformance: all 17 real sources / 18 real definitions
normalize through the registered Reference Bundle Adapters without a
single exception, with deterministic digests (P3-D-WU-002/003/004)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.governance_definitions.reference_bundle_adapters import (
    ArgdDagdCombinedAdapter,
    CdogdAdapter,
    CommonDomainExtensionAdapter,
)
from margpa_runtime_llm.modules.governance_definitions.adapter_registry import (
    AdapterDescriptor,
    TrustedAdapterRegistry,
)
from margpa_runtime_llm.modules.governance_definitions.domain import (
    SignedPackageManifest,
    digest_ir,
    verify_digested_ir,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITIONS_ROOT = PROJECT_ROOT / "definitions"

_EXPECTED_DEFINITION_IDS = {
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

_RAW_COT_MARKERS = ("<thinking>", "chain_of_thought_raw", "raw_chain_of_thought")


def _build_registry() -> TrustedAdapterRegistry:
    registry = TrustedAdapterRegistry()
    registry.register(
        AdapterDescriptor(
            adapter_id="argd_dagd_combined_v1",
            schema_id="combined_argd_dagd_v1",
            adapter_version="1",
        ),
        ArgdDagdCombinedAdapter(),
    )
    registry.register(
        AdapterDescriptor(adapter_id="cdogd_v1", schema_id="cdogd_v1", adapter_version="1"),
        CdogdAdapter(),
    )
    registry.register(
        AdapterDescriptor(
            adapter_id="common_domain_extension_v1",
            schema_id="common_domain_extension_v1",
            adapter_version="1",
        ),
        CommonDomainExtensionAdapter(),
    )
    return registry


@pytest.fixture(scope="module")
def signed_manifest() -> SignedPackageManifest:
    raw = (DEFINITIONS_ROOT / "manifest.json").read_text(encoding="utf-8")
    return SignedPackageManifest.model_validate_json(raw)


def test_every_definition_normalizes_without_raising(
    signed_manifest: SignedPackageManifest,
) -> None:
    registry = _build_registry()
    manifest = signed_manifest.manifest
    sources_by_id = {entry.source_id: entry for entry in manifest.source_entries}
    normalized_ids = set()

    for definition in manifest.definition_entries:
        source_entry = sources_by_id[definition.source_id]
        source_json = json.loads((PROJECT_ROOT / source_entry.relative_path).read_bytes())
        adapter = registry.resolve(
            schema_id=source_entry.schema_id,
            adapter_id=source_entry.trusted_adapter_id,
            source_media_type=source_entry.media_type,
        )
        assert adapter is not None, f"no adapter for {definition.definition_id}"

        ir = adapter.normalize(
            source_json=source_json, source_entry=source_entry, definition_entry=definition
        )
        assert ir.identity.definition_id == definition.definition_id
        assert ir.source_provenance.content_digest_sha512 == source_entry.content_digest_sha512
        assert len(ir.sections) > 0
        normalized_ids.add(ir.identity.definition_id)

    assert normalized_ids == _EXPECTED_DEFINITION_IDS


def test_decision_pipeline_and_orchestration_references_are_preserved_as_sections(
    signed_manifest: SignedPackageManifest,
) -> None:
    registry = _build_registry()
    manifest = signed_manifest.manifest
    sources_by_id = {entry.source_id: entry for entry in manifest.source_entries}

    for pipeline_id in ("sppgd", "daagd", "sdagd", "sdmrgd"):
        definition = next(d for d in manifest.definition_entries if d.definition_id == pipeline_id)
        source_entry = sources_by_id[definition.source_id]
        source_json = json.loads((PROJECT_ROOT / source_entry.relative_path).read_bytes())
        adapter = registry.resolve(
            schema_id=source_entry.schema_id,
            adapter_id=source_entry.trusted_adapter_id,
            source_media_type=source_entry.media_type,
        )
        assert adapter is not None
        ir = adapter.normalize(
            source_json=source_json, source_entry=source_entry, definition_entry=definition
        )
        section_keys = {section.section_key for section in ir.sections}
        assert "orchestration_reference" in section_keys


def test_ir_digest_is_deterministic_and_self_consistent(
    signed_manifest: SignedPackageManifest,
) -> None:
    registry = _build_registry()
    manifest = signed_manifest.manifest
    sources_by_id = {entry.source_id: entry for entry in manifest.source_entries}
    definition = next(d for d in manifest.definition_entries if d.definition_id == "aagd")
    source_entry = sources_by_id[definition.source_id]
    source_json = json.loads((PROJECT_ROOT / source_entry.relative_path).read_bytes())
    adapter = registry.resolve(
        schema_id=source_entry.schema_id,
        adapter_id=source_entry.trusted_adapter_id,
        source_media_type=source_entry.media_type,
    )
    assert adapter is not None

    ir_first = adapter.normalize(
        source_json=source_json, source_entry=source_entry, definition_entry=definition
    )
    ir_second = adapter.normalize(
        source_json=source_json, source_entry=source_entry, definition_entry=definition
    )
    digested = digest_ir(ir_first)
    assert digest_ir(ir_second).ir_digest_sha512 == digested.ir_digest_sha512
    assert verify_digested_ir(digested) is True


def test_no_normalized_ir_contains_raw_chain_of_thought_markers(
    signed_manifest: SignedPackageManifest,
) -> None:
    registry = _build_registry()
    manifest = signed_manifest.manifest
    sources_by_id = {entry.source_id: entry for entry in manifest.source_entries}

    for definition in manifest.definition_entries:
        source_entry = sources_by_id[definition.source_id]
        source_json = json.loads((PROJECT_ROOT / source_entry.relative_path).read_bytes())
        adapter = registry.resolve(
            schema_id=source_entry.schema_id,
            adapter_id=source_entry.trusted_adapter_id,
            source_media_type=source_entry.media_type,
        )
        assert adapter is not None
        ir = adapter.normalize(
            source_json=source_json, source_entry=source_entry, definition_entry=definition
        )
        rendered = ir.model_dump_json()
        for marker in _RAW_COT_MARKERS:
            assert marker not in rendered
