"""Independent Main/Guard/Judge provider selection contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .canonicalization import runtime_model_snapshot_digest
from .identifiers import ModelRole

_SHA512_PATTERN = r"^[0-9a-f]{128}$"


class ProviderKind(StrEnum):
    NONE = "none"
    BUILT_IN = "built_in"
    MODEL = "model"


class ProviderRuntimeState(StrEnum):
    NONE = "none"
    CONFIGURED = "configured"
    UNAVAILABLE = "unavailable"
    LOADING = "loading"
    ACTIVE = "active"
    DEGRADED = "degraded"
    FAILED = "failed"


class ProviderIndependence(StrEnum):
    NONE = "none"
    SELF = "self"
    BUILT_IN = "built_in"
    INDEPENDENT_SAME_FAMILY = "independent_same_family"
    INDEPENDENT_OTHER_MODEL = "independent_other_model"
    UNAVAILABLE = "unavailable"


class ProviderOption(ImmutableContract):
    provider_id: str = Field(min_length=1, max_length=128)
    role: ModelRole
    kind: ProviderKind
    display_name: str = Field(min_length=1, max_length=128)
    enabled: bool = True
    model_key: str | None = Field(default=None, max_length=128)
    artifact_relative_path: str | None = Field(default=None, max_length=512)
    artifact_digest_sha512: str | None = Field(default=None, pattern=_SHA512_PATTERN)
    model_family: str | None = Field(default=None, max_length=64)


class RoleProviderSelection(ImmutableContract):
    role: ModelRole
    configured_provider: str = Field(min_length=1, max_length=128)
    active_provider: str | None = Field(default=None, max_length=128)
    state: ProviderRuntimeState
    independence: ProviderIndependence
    failure_reason: str | None = Field(default=None, max_length=128)
    failure_at: str | None = Field(default=None, max_length=64)


class ProviderSelectionSnapshot(ImmutableContract):
    revision: int = Field(ge=1)
    digest_sha512: str = Field(pattern=_SHA512_PATTERN)
    selections: tuple[RoleProviderSelection, ...]
    options: tuple[ProviderOption, ...]


def provider_selection_digest(
    *, revision: int, selections: tuple[RoleProviderSelection, ...]
) -> str:
    return runtime_model_snapshot_digest(
        payload={
            "revision": revision,
            "selections": [
                item.model_dump(mode="json")
                for item in sorted(selections, key=lambda value: value.role.value)
            ],
        }
    )


class ProviderSelectionErrorCode(StrEnum):
    REVISION_CONFLICT = "revision_conflict"
    UNKNOWN_PROVIDER = "unknown_provider"
    ROLE_MISMATCH = "role_mismatch"
    PROVIDER_DISABLED = "provider_disabled"
    ACTIVATION_FAILED = "activation_failed"
    ACTIVE_TURN = "active_turn"


class ProviderSelectionError(Exception):
    def __init__(
        self,
        *,
        code: ProviderSelectionErrorCode,
        safe_message: str,
        current_snapshot: ProviderSelectionSnapshot | None = None,
    ) -> None:
        super().__init__(safe_message)
        self.code = code
        self.safe_message = safe_message
        self.current_snapshot = current_snapshot
