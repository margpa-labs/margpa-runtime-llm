"""Production-safe dedicated-role adapter boundary when artifacts are inaccessible."""

from __future__ import annotations

from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderOption,
)


class UnavailableRoleProviderAdapter:
    def __init__(self, *, provider_id: str, reason: str) -> None:
        self._provider_id = provider_id
        self._reason = reason

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def preflight(self) -> tuple[bool, str | None]:
        return False, self._reason

    def load(self) -> None:
        raise RuntimeError(self._reason)

    def unload(self) -> None:
        return None


class UnavailableRoleAdapterFactory:
    """Never traverses a configured artifact path merely to claim availability."""

    def __init__(self, *, reason: str = "dedicated_provider_artifact_unavailable") -> None:
        self._reason = reason

    def create(self, *, role: ModelRole, option: ProviderOption) -> UnavailableRoleProviderAdapter:
        del role
        return UnavailableRoleProviderAdapter(provider_id=option.provider_id, reason=self._reason)
