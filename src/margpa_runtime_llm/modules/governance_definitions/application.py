"""EmptyDefinitionProvider: the canonical zero-definition Provider.

`definitions = 0` is a *正式な* Runtime Baseline (P3-DEF-001), not a
degraded or failed state — `describe()` reports `ProviderState.EMPTY`,
distinct from `UNAVAILABLE`/`FAILED` (P3-PRV-007).
"""

from __future__ import annotations

from .domain import ProviderState
from .ports import PackageLoadRequest, PackageSourceResult, ProviderDescriptor

_PROVIDER_ID = "empty-provider"
_PROVIDER_KIND = "empty"


class EmptyDefinitionProvider:
    """Always reports zero packages; never touches the filesystem."""

    def describe(self) -> ProviderDescriptor:
        return ProviderDescriptor(
            provider_id=_PROVIDER_ID,
            provider_kind=_PROVIDER_KIND,
            state=ProviderState.EMPTY,
        )

    def load_package(self, request: PackageLoadRequest) -> PackageSourceResult:
        return PackageSourceResult(
            found=False,
            reason_code="provider_has_no_packages",
        )
