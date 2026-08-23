"""Generic Definition Provider port (architecture §5.1).

`DefinitionProviderPort` only hides *source* differences (filesystem,
empty, future remote/package). It never interprets schema, converts to
IR, compiles, or activates anything — those are separate Phase 3-D/E
concerns.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .domain import DefinitionState, PackageManifest, PackageState, ProviderState

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class ProviderDescriptor(ImmutableContract):
    provider_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    provider_kind: str = Field(min_length=1, max_length=64, pattern=_IDENTIFIER_PATTERN)
    state: ProviderState
    unavailable_reason_code: str | None = Field(
        default=None, max_length=64, pattern=_IDENTIFIER_PATTERN
    )


class PackageLoadRequest(ImmutableContract):
    """Empty by default: a Provider with nothing configured (e.g.
    `EmptyDefinitionProvider`) accepts the default request and reports
    `found=False` rather than requiring a caller to already know a
    package_id that cannot exist yet."""

    requested_package_id: str | None = Field(
        default=None, max_length=128, pattern=_IDENTIFIER_PATTERN
    )


class DefinitionStateEntry(ImmutableContract):
    definition_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    state: DefinitionState


class PackageSourceResult(ImmutableContract):
    found: bool
    package_state: PackageState | None = None
    package_id: str | None = Field(default=None, max_length=128, pattern=_IDENTIFIER_PATTERN)
    manifest: PackageManifest | None = None
    # Per-definition Partial Acceptance Policy result (P3-C-WU-004),
    # attached here so callers of the generic Port never need to know a
    # concrete Provider's own verification mechanism to get it.
    definition_states: tuple[DefinitionStateEntry, ...] = ()
    # Verified Bytes / Verified Source Record (P3-CODEX-007): parsed JSON
    # content for every source_id whose corresponding `SourceVerification`
    # is exactly `LOADED`, captured from the *same* read that verified its
    # Size/Digest — never a separate later re-read. A caller (the Runtime)
    # must treat this dict, not a fresh filesystem read, as the Source of
    # Truth for Normalization input. Sources that are not `LOADED` simply
    # have no entry here — their content is never propagated onward.
    verified_source_json: dict[str, dict[str, object]] = Field(default_factory=dict)
    reason_code: str | None = Field(default=None, max_length=64, pattern=_IDENTIFIER_PATTERN)


@runtime_checkable
class DefinitionProviderPort(Protocol):
    def describe(self) -> ProviderDescriptor: ...

    def load_package(self, request: PackageLoadRequest) -> PackageSourceResult: ...
