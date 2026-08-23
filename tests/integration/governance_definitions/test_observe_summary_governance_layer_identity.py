"""P6-CODEX-005: GovernanceObserveSummary must carry the real Package's own
`package_id`/`manifest_digest_sha512` (Governance Layer Identity), not just
the compiled-plan-only fields it already had. Uses the real repo bundle,
the same one `test_filesystem_provider_real_bundle.py` verifies."""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.adapters.governance_definitions.filesystem_provider import (
    FilesystemDefinitionProvider,
)
from margpa_runtime_llm.modules.governance_definitions.adapter_registry import (
    TrustedAdapterRegistry,
)
from margpa_runtime_llm.modules.governance_definitions.application import (
    EmptyDefinitionProvider,
)
from margpa_runtime_llm.modules.governance_definitions.domain import (
    GovernanceMode,
    manifest_digest_sha512,
)
from margpa_runtime_llm.modules.governance_definitions.ports import PackageLoadRequest
from margpa_runtime_llm.modules.governance_definitions.runtime import (
    GovernanceDefinitionsRuntime,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFINITIONS_ROOT = PROJECT_ROOT / "definitions"


def test_observe_summary_carries_the_real_package_id_and_manifest_digest() -> None:
    provider = FilesystemDefinitionProvider(root=DEFINITIONS_ROOT)
    expected_manifest = provider.load_package(PackageLoadRequest()).manifest
    assert expected_manifest is not None

    runtime = GovernanceDefinitionsRuntime(provider=provider, registry=TrustedAdapterRegistry())
    runtime.apply_mode(GovernanceMode.OBSERVE)
    summary = runtime.status().observe_summary

    assert summary is not None
    assert summary.package_id == expected_manifest.package_id
    assert summary.manifest_digest_sha512 == manifest_digest_sha512(expected_manifest)


def test_observe_summary_leaves_identity_none_when_no_package_found() -> None:
    runtime = GovernanceDefinitionsRuntime(
        provider=EmptyDefinitionProvider(),
        registry=TrustedAdapterRegistry(),
    )
    runtime.apply_mode(GovernanceMode.OBSERVE)
    summary = runtime.status().observe_summary

    assert summary is not None
    assert summary.package_found is False
    assert summary.package_id is None
    assert summary.manifest_digest_sha512 is None
