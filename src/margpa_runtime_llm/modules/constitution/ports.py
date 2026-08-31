"""Phase 8 (P8-C): replaceable Port for the Provisional Runtime Constitution."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .contracts import ConstitutionManifest, ConstitutionManifestUnavailable


@runtime_checkable
class ConstitutionProviderPort(Protocol):
    def load_manifest(self) -> ConstitutionManifest | ConstitutionManifestUnavailable: ...
