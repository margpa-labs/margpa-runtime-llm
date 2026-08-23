"""Composition root for the Phase 3 Governance Definitions Runtime.

Only called when the caller has already gated on Local/Loopback/
Auth-disabled/Explicit opt-in (mirrors `_configuration_control_enabled`
in `entrypoints/web/main.py`) — this module itself does not re-check
Access Policy, it only builds the Runtime object.
"""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.adapters.governance_definitions.filesystem_provider import (
    FilesystemDefinitionProvider,
)
from margpa_runtime_llm.adapters.governance_definitions.reference_bundle_adapters import (
    ArgdDagdCombinedAdapter,
    CdogdAdapter,
    CommonDomainExtensionAdapter,
)
from margpa_runtime_llm.modules.governance_definitions.adapter_registry import (
    AdapterDescriptor,
    TrustedAdapterRegistry,
)
from margpa_runtime_llm.modules.governance_definitions.application import (
    EmptyDefinitionProvider,
)
from margpa_runtime_llm.modules.governance_definitions.domain import GovernanceMode
from margpa_runtime_llm.modules.governance_definitions.ports import DefinitionProviderPort
from margpa_runtime_llm.modules.governance_definitions.runtime import GovernanceDefinitionsRuntime


def build_reference_bundle_adapter_registry() -> TrustedAdapterRegistry:
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


def build_governance_definitions_runtime(
    *,
    definitions_root: Path | None = None,
) -> GovernanceDefinitionsRuntime:
    """`definitions_root=None` selects `EmptyDefinitionProvider` — a
    genuinely valid `definitions=0` Baseline (P3-DEF-001), not a
    degraded fallback.

    No `project_root` parameter: Source content now comes exclusively
    from the Provider's own verified read
    (`PackageSourceResult.verified_source_json`, P3-CODEX-007) — there is
    no second, Runtime-owned re-read of a Source from disk to root."""

    provider: DefinitionProviderPort = (
        EmptyDefinitionProvider()
        if definitions_root is None
        else FilesystemDefinitionProvider(root=definitions_root)
    )
    return GovernanceDefinitionsRuntime(
        provider=provider,
        registry=build_reference_bundle_adapter_registry(),
        initial_mode=GovernanceMode.OFF,
    )
