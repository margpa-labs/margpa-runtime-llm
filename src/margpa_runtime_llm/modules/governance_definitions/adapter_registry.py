"""Trusted Adapter Registry (architecture §6.1, P3-D-WU-001).

Adapters are registered explicitly, in Python, at bootstrap time — never
resolved by treating a Manifest's `trusted_adapter_id` string as an
import path (P3-SEC-004, P3-IR-002). An unregistered (schema_id,
adapter_id) pair resolves to `None`; callers turn that into a `Definition
Adapter Registry"unsupported"` DefinitionState (Phase 3-C's
`resolve_definition_states` already reserves that outcome for exactly
this "no adapter" case) rather than raising.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .domain import DefinitionEntry, SourceEntry
from .domain.normalized_ir import NormalizedGovernanceDefinition

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class AdapterDescriptor(ImmutableContract):
    adapter_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    schema_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    adapter_version: str = Field(min_length=1, max_length=32, pattern=_IDENTIFIER_PATTERN)
    supported_media_types: tuple[str, ...] = ("application/json",)


@runtime_checkable
class DefinitionAdapterPort(Protocol):
    def normalize(
        self,
        *,
        source_json: dict[str, object],
        source_entry: SourceEntry,
        definition_entry: DefinitionEntry,
    ) -> NormalizedGovernanceDefinition: ...


class AdapterRegistrationError(Exception):
    def __init__(self, *, safe_message: str) -> None:
        super().__init__(safe_message)
        self.safe_message = safe_message


class TrustedAdapterRegistry:
    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], tuple[AdapterDescriptor, DefinitionAdapterPort]] = {}

    def register(self, descriptor: AdapterDescriptor, adapter: DefinitionAdapterPort) -> None:
        key = (descriptor.schema_id, descriptor.adapter_id)
        if key in self._entries:
            raise AdapterRegistrationError(
                safe_message="an adapter is already registered for this (schema_id, adapter_id)"
            )
        self._entries[key] = (descriptor, adapter)

    def resolve(
        self, *, schema_id: str, adapter_id: str, source_media_type: str
    ) -> DefinitionAdapterPort | None:
        entry = self._entries.get((schema_id, adapter_id))
        if entry is None:
            return None
        descriptor, adapter = entry
        if source_media_type not in descriptor.supported_media_types:
            return None
        return adapter

    def descriptors(self) -> tuple[AdapterDescriptor, ...]:
        return tuple(descriptor for descriptor, _adapter in self._entries.values())
