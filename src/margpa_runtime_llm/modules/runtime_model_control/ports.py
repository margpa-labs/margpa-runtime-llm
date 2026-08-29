"""Ports for Runtime Model Control (Architecture 3.2). Adapters implemented in Phase 6-B-WU-002+."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition

from .domain.identifiers import ModelRole
from .domain.provider_selection import ProviderOption


@dataclass(frozen=True, slots=True)
class CapabilityProbeResult:
    """Actually-measured Backend Capability for a candidate Load (Architecture 3.2)."""

    native_context_limit: int
    backend_context_limit: int
    deployment_verified_context_limit: int
    max_output_token_limit: int
    capability_digest: str

    @property
    def effective_context_limit(self) -> int:
        """Highest context size supported by every known active boundary."""
        return min(
            self.native_context_limit,
            self.backend_context_limit,
            self.deployment_verified_context_limit,
        )

    @property
    def context_limit_reason_code(self) -> str:
        effective = self.effective_context_limit
        if effective < self.native_context_limit:
            if effective == self.deployment_verified_context_limit:
                return "deployment_hardware_verified_limit"
            if effective == self.backend_context_limit:
                return "backend_limit"
        return "model_native_limit"


@dataclass(frozen=True, slots=True)
class LoadedModelHandle:
    """Opaque success result of a Candidate Load."""

    backend_identity: str
    artifact_digest: str
    loaded_context_size: int
    capability: CapabilityProbeResult


@runtime_checkable
class ModelBackendPort(Protocol):
    """Load/Unload/Probe a single Model Definition on a concrete inference backend."""

    def probe_capability(self, *, definition: ModelDefinition) -> CapabilityProbeResult: ...

    def load(self, *, definition: ModelDefinition, context_size: int) -> LoadedModelHandle: ...

    def unload(self) -> None: ...


@runtime_checkable
class ModelAccessLeasePort(Protocol):
    """Exclusive Switch/Context-Reload lease over the shared Model Access
    contract (Architecture 3.2/12, hardened P6-CODEX-034 Fifth Rework).

    Replaces the previous `GenerationBusyGatePort` (a passive, TOCTOU-prone
    "peek `active_request_id`, then Unload" pattern that only ever saw MAIN
    Turns — never a Judge/Repair Background Task holding the shared Model
    via `ModelAccessCoordinator.start_background()`). `try_acquire_switch_
    lease()` atomically claims exclusive access — succeeding only if
    neither a MAIN Turn nor a Background Task is currently active — so a
    Switch's own Unload/Load can never race a live Judge/Repair Call.
    `ModelAccessCoordinator` implements this port directly."""

    def try_acquire_switch_lease(self, *, task_id: str) -> bool: ...

    def release_switch_lease(self, *, task_id: str) -> None: ...


@runtime_checkable
class ModelDefinitionResolverPort(Protocol):
    """Resolves a Registry model_key to its full ModelDefinition.

    The Snapshot only carries model_key/artifact/backend identity, not the full
    Definition, so a Rollback (reloading the Previous Runtime Receipt's model)
    needs this lookup rather than reconstructing a Definition from Snapshot fields.
    """

    def resolve(self, *, model_key: str) -> ModelDefinition: ...

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        """Every registered Definition, regardless of `enabled`/`logical_role`
        (Fourth Rework, P6-CODEX-026: backs `RuntimeModelController.
        available_models()` — the Runtime Switch surface a user picks a
        target `model_key` from)."""
        ...


@runtime_checkable
class RoleProviderAdapterPort(Protocol):
    @property
    def provider_id(self) -> str: ...

    def preflight(self) -> tuple[bool, str | None]: ...

    def load(self) -> None: ...

    def unload(self) -> None: ...


@runtime_checkable
class RoleAdapterFactoryPort(Protocol):
    def create(self, *, role: ModelRole, option: ProviderOption) -> RoleProviderAdapterPort: ...


@runtime_checkable
class RoleResourceGatePort(Protocol):
    def allow_activation(
        self, *, role: ModelRole, option: ProviderOption
    ) -> tuple[bool, str | None]: ...
