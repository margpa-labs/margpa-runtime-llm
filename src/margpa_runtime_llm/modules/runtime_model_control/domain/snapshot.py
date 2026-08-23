"""RuntimeModelSnapshot, RoleBinding, TransitionReceipt (Phase 6 Architecture 3.1-3.3)."""

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .canonicalization import runtime_model_snapshot_digest
from .identifiers import BindingState, IndependenceClass, ModelRole, RuntimeState, SwitchOutcome

SHA512_PATTERN = r"^[0-9a-f]{128}$"


class RoleBinding(ImmutableContract):
    """Model Artifact and Runtime Role are kept separate (Architecture 3.3)."""

    role: ModelRole
    model_identity: str = Field(min_length=1)
    artifact_digest: str = Field(pattern=SHA512_PATTERN)
    backend_identity: str = Field(min_length=1)
    binding_state: BindingState
    independence_class: IndependenceClass
    capability_digest: str = Field(pattern=SHA512_PATTERN)


class TransitionReceipt(ImmutableContract):
    """Record of one Switch Transaction attempt (Architecture 3.2)."""

    transition_id: str = Field(min_length=1)
    from_revision: int = Field(ge=0)
    to_model_key: str = Field(min_length=1)
    outcome: SwitchOutcome
    started_at: str = Field(min_length=1)
    completed_at: str = Field(min_length=1)
    failure_reason: str | None = None


class RuntimeModelSnapshot(ImmutableContract):
    """Canonical Server Snapshot shared by Browser/Sidebar/Advanced Settings/Judge/Repair (3.1)."""

    revision: int = Field(ge=0)
    digest_sha512: str = Field(pattern=SHA512_PATTERN)
    selected_model_key: str = Field(min_length=1)
    role_bindings: tuple[RoleBinding, ...]
    artifact_identity: str = Field(min_length=1)
    artifact_digest: str = Field(pattern=SHA512_PATTERN)
    backend_identity: str = Field(min_length=1)
    runtime_state: RuntimeState
    loaded_context_size: int = Field(ge=0)
    model_native_context_limit: int = Field(gt=0)
    backend_context_limit: int = Field(gt=0)
    deployment_verified_context_limit: int = Field(gt=0)
    max_output_token_limit: int = Field(gt=0)
    current_max_new_tokens: int = Field(gt=0)
    last_transition_receipt: TransitionReceipt | None = None


def compute_runtime_model_snapshot_digest(
    *,
    revision: int,
    selected_model_key: str,
    role_bindings: tuple[RoleBinding, ...],
    artifact_identity: str,
    artifact_digest: str,
    backend_identity: str,
    runtime_state: RuntimeState,
    loaded_context_size: int,
    current_max_new_tokens: int,
) -> str:
    """Hash only the fields that identify *this* Runtime Model configuration.

    Capability limits (native/backend/deployment-verified/max-output) are derived
    facts about the Artifact/Backend pair, not independent mutable state, so they
    are intentionally excluded from the identity digest to avoid spurious CAS
    conflicts when nothing the caller controls has actually changed.
    """
    payload = {
        "revision": revision,
        "selected_model_key": selected_model_key,
        "role_bindings": sorted(
            (
                binding.role.value,
                binding.model_identity,
                binding.artifact_digest,
                binding.backend_identity,
                binding.binding_state.value,
                binding.independence_class.value,
                binding.capability_digest,
            )
            for binding in role_bindings
        ),
        "artifact_identity": artifact_identity,
        "artifact_digest": artifact_digest,
        "backend_identity": backend_identity,
        "runtime_state": runtime_state.value,
        "loaded_context_size": loaded_context_size,
        "current_max_new_tokens": current_max_new_tokens,
    }
    return runtime_model_snapshot_digest(payload=payload)
