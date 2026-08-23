"""FilesystemDefinitionProvider against the real Reference Governance
Definition Bundle (`definitions/`) — end-to-end closure for P3-C-WU-003."""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.adapters.governance_definitions.filesystem_provider import (
    FilesystemDefinitionProvider,
)
from margpa_runtime_llm.modules.governance_definitions.domain import (
    PackageState,
    ProviderState,
    SourceState,
)
from margpa_runtime_llm.modules.governance_definitions.ports import PackageLoadRequest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITIONS_ROOT = PROJECT_ROOT / "definitions"


def _provider() -> FilesystemDefinitionProvider:
    return FilesystemDefinitionProvider(root=DEFINITIONS_ROOT)


def test_describe_reports_ready_for_the_real_bundle() -> None:
    assert _provider().describe().state is ProviderState.READY


def test_load_package_validates_all_seventeen_real_sources() -> None:
    result = _provider().load_package(PackageLoadRequest())
    assert result.found is True
    assert result.package_state is PackageState.VALIDATED
    assert result.manifest is not None
    assert len(result.manifest.source_entries) == 17


def test_verify_sources_reports_loaded_for_every_real_source() -> None:
    provider = _provider()
    signed = provider._load_signed_manifest()
    verifications = provider.verify_sources(signed)
    assert len(verifications) == 17
    assert all(v.state is SourceState.LOADED for v in verifications)
