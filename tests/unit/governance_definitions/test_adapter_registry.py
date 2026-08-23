"""TrustedAdapterRegistry: explicit registration, no Manifest-string
Import, Unknown Adapter safe-unsupported (P3-D-WU-001)."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.governance_definitions.adapter_registry import (
    AdapterDescriptor,
    AdapterRegistrationError,
    TrustedAdapterRegistry,
)
from margpa_runtime_llm.modules.governance_definitions.domain import (
    DefinitionEntry,
    IrIdentity,
    IrSourceProvenance,
    NormalizedGovernanceDefinition,
    SourceEntry,
)


class _StubAdapter:
    def normalize(
        self,
        *,
        source_json: dict[str, object],
        source_entry: SourceEntry,
        definition_entry: DefinitionEntry,
    ) -> NormalizedGovernanceDefinition:
        return NormalizedGovernanceDefinition(
            ir_id="stub-ir",
            identity=IrIdentity(definition_id="x", definition_version="1", display_name="X"),
            source_provenance=IrSourceProvenance(
                source_id="x", source_object_pointer="$.x", content_digest_sha512="0" * 128
            ),
            domain="x_domain",
            sections=(),
        )


def test_register_then_resolve_returns_the_same_adapter() -> None:
    registry = TrustedAdapterRegistry()
    adapter = _StubAdapter()
    descriptor = AdapterDescriptor(adapter_id="a1", schema_id="s1", adapter_version="1")

    registry.register(descriptor, adapter)
    resolved = registry.resolve(
        schema_id="s1", adapter_id="a1", source_media_type="application/json"
    )

    assert resolved is adapter


def test_resolve_returns_none_for_unregistered_adapter_not_raises() -> None:
    registry = TrustedAdapterRegistry()
    resolved = registry.resolve(
        schema_id="unknown", adapter_id="unknown", source_media_type="application/json"
    )
    assert resolved is None


def test_resolve_returns_none_for_unsupported_media_type() -> None:
    registry = TrustedAdapterRegistry()
    descriptor = AdapterDescriptor(
        adapter_id="a1",
        schema_id="s1",
        adapter_version="1",
        supported_media_types=("application/json",),
    )
    registry.register(descriptor, _StubAdapter())

    resolved = registry.resolve(schema_id="s1", adapter_id="a1", source_media_type="text/plain")
    assert resolved is None


def test_register_rejects_duplicate_schema_and_adapter_id_pair() -> None:
    registry = TrustedAdapterRegistry()
    descriptor = AdapterDescriptor(adapter_id="a1", schema_id="s1", adapter_version="1")
    registry.register(descriptor, _StubAdapter())

    with pytest.raises(AdapterRegistrationError):
        registry.register(descriptor, _StubAdapter())


def test_same_adapter_id_under_different_schema_is_allowed() -> None:
    registry = TrustedAdapterRegistry()
    registry.register(
        AdapterDescriptor(adapter_id="a1", schema_id="s1", adapter_version="1"), _StubAdapter()
    )
    registry.register(
        AdapterDescriptor(adapter_id="a1", schema_id="s2", adapter_version="1"), _StubAdapter()
    )
    assert registry.resolve(schema_id="s1", adapter_id="a1", source_media_type="application/json")
    assert registry.resolve(schema_id="s2", adapter_id="a1", source_media_type="application/json")


def test_descriptors_lists_all_registered_adapters() -> None:
    registry = TrustedAdapterRegistry()
    registry.register(
        AdapterDescriptor(adapter_id="a1", schema_id="s1", adapter_version="1"), _StubAdapter()
    )
    registry.register(
        AdapterDescriptor(adapter_id="a2", schema_id="s2", adapter_version="1"), _StubAdapter()
    )
    ids = {d.adapter_id for d in registry.descriptors()}
    assert ids == {"a1", "a2"}
