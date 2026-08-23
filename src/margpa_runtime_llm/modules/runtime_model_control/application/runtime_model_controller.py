"""RuntimeModelController: CAS-guarded Switch Transaction orchestration (Architecture 3.2)."""

import threading
from collections.abc import Callable
from datetime import UTC, datetime

from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition

from ..domain.errors import (
    RuntimeModelBusyError,
    RuntimeModelContextLimitExceeded,
    RuntimeModelLoadFailure,
    RuntimeModelMaxNewTokensExceeded,
    RuntimeModelRevisionConflict,
    RuntimeModelRollbackFailure,
    RuntimeModelTargetNotRegistered,
)
from ..domain.identifiers import (
    BindingState,
    IndependenceClass,
    ModelRole,
    RuntimeState,
    SwitchOutcome,
)
from ..domain.snapshot import (
    RoleBinding,
    RuntimeModelSnapshot,
    TransitionReceipt,
    compute_runtime_model_snapshot_digest,
)
from ..ports import ModelAccessLeasePort, ModelBackendPort, ModelDefinitionResolverPort


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class RuntimeModelController:
    """Process-local Runtime Model Snapshot store with CAS-guarded Switch Transactions.

    Mirrors the lock + expected-(revision, digest) CAS pattern used by
    ConfigurationControlService.apply() and GuardrailModeController.apply_mode().
    """

    def __init__(
        self,
        *,
        initial_snapshot: RuntimeModelSnapshot,
        backend: ModelBackendPort,
        access_lease: ModelAccessLeasePort,
        definitions: ModelDefinitionResolverPort,
        on_commit: Callable[[RuntimeModelSnapshot], None] | None = None,
    ) -> None:
        self._lock = threading.Lock()
        self._snapshot = initial_snapshot
        self._backend = backend
        self._access_lease = access_lease
        self._definitions = definitions
        # P6-CODEX-036 (Fifth Rework): fired only after a Switch/Context
        # Reload actually COMMITS — never on Rollback/Failure — so a
        # dependent Composition (e.g. Runtime Governance's own frozen-at-
        # Bootstrap Capability) can rebind itself to the new Snapshot
        # inside the exact same success boundary `begin_switch()` already
        # enforces, without this module needing to know anything about
        # what it is notifying. Called OUTSIDE `self._lock` (after it is
        # released) so arbitrary external code in the callback can never
        # deadlock against, or reenter, this Controller's own lock.
        self._on_commit = on_commit

    def snapshot(self) -> RuntimeModelSnapshot:
        with self._lock:
            return self._snapshot

    def available_models(self) -> tuple[ModelDefinition, ...]:
        """Every enabled `logical_role="main"` Definition a Runtime Switch
        may target (Fourth Rework, P6-CODEX-026) — the Web Route's source
        for a Model picker, never a hardcoded list."""
        return tuple(
            definition
            for definition in self._definitions.all_definitions()
            if definition.enabled and definition.logical_role == ModelRole.MAIN.value
        )

    def switch_to_model_key(
        self,
        *,
        expected_revision: int,
        expected_digest: str,
        transition_id: str,
        target_model_key: str,
        requested_context_size: int,
    ) -> RuntimeModelSnapshot:
        """Resolve `target_model_key` against the Registry and delegate to
        `begin_switch()` (Fourth Rework, P6-CODEX-026) — the only entry
        point a Web Route needs; `begin_switch()` itself stays generic and
        directly unit-testable against any `target_definition`."""
        available = {definition.model_key: definition for definition in self.available_models()}
        target_definition = available.get(target_model_key)
        if target_definition is None:
            raise RuntimeModelTargetNotRegistered(target_model_key=target_model_key)
        return self.begin_switch(
            expected_revision=expected_revision,
            expected_digest=expected_digest,
            transition_id=transition_id,
            target_definition=target_definition,
            requested_context_size=requested_context_size,
        )

    def begin_switch(
        self,
        *,
        expected_revision: int,
        expected_digest: str,
        transition_id: str,
        target_definition: ModelDefinition,
        requested_context_size: int,
    ) -> RuntimeModelSnapshot:
        """Preview -> CAS/Exclusive Lease -> Unload -> Load -> Commit or Rollback (3.2).

        P6-CODEX-034 (Fifth Rework): the previous "Busy Gate" was a passive
        `has_active_generation()` peek that only ever saw MAIN Turns — a
        Judge/Repair Background Task holding the shared Model via
        `ModelAccessCoordinator.start_background()` was invisible to it,
        so a Switch could Unload the Model out from under an in-flight
        Background Call. `try_acquire_switch_lease()` now atomically
        claims exclusive access across Main AND Background before any
        Unload is attempted; failure to acquire raises immediately with
        zero Unload/Load performed, and the lease is always released
        (success, Load failure, or an unexpected exception) via `finally`.
        """
        with self._lock:
            current = self._snapshot
            if current.revision != expected_revision or current.digest_sha512 != expected_digest:
                raise RuntimeModelRevisionConflict(
                    expected_revision=expected_revision,
                    expected_digest=expected_digest,
                    current_revision=current.revision,
                    current_digest=current.digest_sha512,
                )
            if not self._access_lease.try_acquire_switch_lease(task_id=transition_id):
                raise RuntimeModelBusyError(
                    reason="active generation lease held; idle-only switch required"
                )
            try:
                previous = current
                started_at = _now_iso()

                self._backend.unload()

                try:
                    handle = self._backend.load(
                        definition=target_definition, context_size=requested_context_size
                    )
                except Exception as load_error:
                    # P6-CODEX-036 (Fifth Rework): a Rollback/Failure never
                    # reaches `on_commit` below — `return` here exits the
                    # whole method from inside the lock, exactly preserving
                    # the "same Rollback boundary" requirement (a dependent
                    # Composition like Runtime Governance must never see a
                    # notification for a Switch that did not actually
                    # commit).
                    return self._rollback_after_load_failure(
                        previous=previous,
                        transition_id=transition_id,
                        target_model_key=target_definition.model_key,
                        started_at=started_at,
                        reason=str(load_error),
                    )

                # P6-CODEX-035 (Fifth Rework): the previous version removed
                # the old MAIN binding but never added a new one for the
                # Target — a committed Snapshot could carry zero MAIN
                # Bindings. The new Binding is built from the Target's own
                # actually-measured `LoadedModelHandle`/Capability, never
                # copied from the previous Binding or the Definition alone.
                new_main_binding = RoleBinding(
                    role=ModelRole.MAIN,
                    model_identity=target_definition.model_key,
                    artifact_digest=handle.artifact_digest,
                    backend_identity=handle.backend_identity,
                    binding_state=BindingState.BOUND,
                    independence_class=IndependenceClass.SHARED_ARTIFACT,
                    capability_digest=handle.capability.capability_digest,
                )
                role_bindings = (
                    new_main_binding,
                    *(
                        binding
                        for binding in previous.role_bindings
                        if binding.role != ModelRole.MAIN
                    ),
                )
                # P6-CODEX-035 (Fifth Rework): a Max New Tokens value valid
                # for the Previous Model can silently exceed the Target
                # Model's own ceiling — clamp explicitly rather than carry
                # forward a value that would make the committed Snapshot
                # internally inconsistent (current_max_new_tokens >
                # max_output_token_limit). The clamped value is what
                # `_runtime_snapshot_provider`/`_build_request` (Fourth
                # Rework, P6-CODEX-025) actually applies to the next real
                # Generation, so API/UI/Attempt Evidence all observe the
                # same effective value.
                effective_max_new_tokens = min(
                    previous.current_max_new_tokens, handle.capability.max_output_token_limit
                )
                new_revision = previous.revision + 1
                new_digest = compute_runtime_model_snapshot_digest(
                    revision=new_revision,
                    selected_model_key=target_definition.model_key,
                    role_bindings=role_bindings,
                    artifact_identity=target_definition.model_key,
                    artifact_digest=handle.artifact_digest,
                    backend_identity=handle.backend_identity,
                    runtime_state=RuntimeState.ACTIVE,
                    loaded_context_size=handle.loaded_context_size,
                    current_max_new_tokens=effective_max_new_tokens,
                )
                receipt = TransitionReceipt(
                    transition_id=transition_id,
                    from_revision=previous.revision,
                    to_model_key=target_definition.model_key,
                    outcome=SwitchOutcome.COMMITTED,
                    started_at=started_at,
                    completed_at=_now_iso(),
                    failure_reason=None,
                )
                committed = RuntimeModelSnapshot(
                    revision=new_revision,
                    digest_sha512=new_digest,
                    selected_model_key=target_definition.model_key,
                    role_bindings=role_bindings,
                    artifact_identity=target_definition.model_key,
                    artifact_digest=handle.artifact_digest,
                    backend_identity=handle.backend_identity,
                    runtime_state=RuntimeState.ACTIVE,
                    loaded_context_size=handle.loaded_context_size,
                    model_native_context_limit=handle.capability.native_context_limit,
                    backend_context_limit=handle.capability.backend_context_limit,
                    deployment_verified_context_limit=(
                        handle.capability.deployment_verified_context_limit
                    ),
                    max_output_token_limit=handle.capability.max_output_token_limit,
                    current_max_new_tokens=effective_max_new_tokens,
                    last_transition_receipt=receipt,
                )
                self._snapshot = committed
            finally:
                self._access_lease.release_switch_lease(task_id=transition_id)
        # P6-CODEX-036 (Fifth Rework): fired only here, after `self._lock`
        # has already been released, and only for a genuine commit — never
        # for a CAS conflict, a busy-lease rejection, or a Rollback (all
        # of which `return`/`raise` from inside the `with self._lock:`
        # block above and never reach this line).
        if self._on_commit is not None:
            self._on_commit(committed)
        return committed

    def request_context_change(
        self,
        *,
        expected_revision: int,
        expected_digest: str,
        transition_id: str,
        requested_context_size: int,
    ) -> RuntimeModelSnapshot:
        """Reload the *same* Model at a new Context Size (Architecture 5.1).

        Reuses begin_switch's Unload->Load->Commit/Rollback machinery with the
        current model as its own target_definition, so a failed reload rolls
        back through the identical Previous-Receipt path as a real Switch and
        never adopts the requested (failed) size as Current.
        """
        with self._lock:
            current = self._snapshot
            if current.revision != expected_revision or current.digest_sha512 != expected_digest:
                raise RuntimeModelRevisionConflict(
                    expected_revision=expected_revision,
                    expected_digest=expected_digest,
                    current_revision=current.revision,
                    current_digest=current.digest_sha512,
                )
            effective_max = min(current.model_native_context_limit, current.backend_context_limit)
            if requested_context_size > effective_max:
                raise RuntimeModelContextLimitExceeded(
                    requested_context_size=requested_context_size,
                    effective_max_context_size=effective_max,
                )
            current_definition = self._definitions.resolve(model_key=current.selected_model_key)

        return self.begin_switch(
            expected_revision=expected_revision,
            expected_digest=expected_digest,
            transition_id=transition_id,
            target_definition=current_definition,
            requested_context_size=requested_context_size,
        )

    def set_max_new_tokens(
        self,
        *,
        expected_revision: int,
        expected_digest: str,
        requested_max_new_tokens: int,
    ) -> RuntimeModelSnapshot:
        """Atomic Runtime Override, no Reload (Architecture 5.2): takes effect next Generation."""
        with self._lock:
            current = self._snapshot
            if current.revision != expected_revision or current.digest_sha512 != expected_digest:
                raise RuntimeModelRevisionConflict(
                    expected_revision=expected_revision,
                    expected_digest=expected_digest,
                    current_revision=current.revision,
                    current_digest=current.digest_sha512,
                )
            if requested_max_new_tokens > current.max_output_token_limit:
                raise RuntimeModelMaxNewTokensExceeded(
                    requested_max_new_tokens=requested_max_new_tokens,
                    max_output_token_limit=current.max_output_token_limit,
                )
            new_revision = current.revision + 1
            new_digest = compute_runtime_model_snapshot_digest(
                revision=new_revision,
                selected_model_key=current.selected_model_key,
                role_bindings=current.role_bindings,
                artifact_identity=current.artifact_identity,
                artifact_digest=current.artifact_digest,
                backend_identity=current.backend_identity,
                runtime_state=current.runtime_state,
                loaded_context_size=current.loaded_context_size,
                current_max_new_tokens=requested_max_new_tokens,
            )
            updated = current.model_copy(
                update={
                    "revision": new_revision,
                    "digest_sha512": new_digest,
                    "current_max_new_tokens": requested_max_new_tokens,
                }
            )
            self._snapshot = updated
            return updated

    def _rollback_after_load_failure(
        self,
        *,
        previous: RuntimeModelSnapshot,
        transition_id: str,
        target_model_key: str,
        started_at: str,
        reason: str,
    ) -> RuntimeModelSnapshot:
        """Load failed; reload the Previous Runtime Receipt (Architecture 3.2).

        Rollback failure must not silently revert to an unverified previous value:
        the Runtime becomes Unavailable and Generation is refused instead.
        """
        rollback_handle = None
        try:
            previous_definition = self._definitions.resolve(model_key=previous.selected_model_key)
            rollback_handle = self._backend.load(
                definition=previous_definition,
                context_size=previous.loaded_context_size,
            )
        except Exception as rollback_error:
            reason = f"{reason}; rollback also failed: {rollback_error}"
            rollback_handle = None

        if rollback_handle is None:
            unavailable_revision = previous.revision + 1
            unavailable_digest = compute_runtime_model_snapshot_digest(
                revision=unavailable_revision,
                selected_model_key=previous.selected_model_key,
                role_bindings=previous.role_bindings,
                artifact_identity=previous.artifact_identity,
                artifact_digest=previous.artifact_digest,
                backend_identity=previous.backend_identity,
                runtime_state=RuntimeState.UNAVAILABLE,
                loaded_context_size=0,
                current_max_new_tokens=previous.current_max_new_tokens,
            )
            receipt = TransitionReceipt(
                transition_id=transition_id,
                from_revision=previous.revision,
                to_model_key=target_model_key,
                outcome=SwitchOutcome.FAILED_UNAVAILABLE,
                started_at=started_at,
                completed_at=_now_iso(),
                failure_reason=reason,
            )
            unavailable_snapshot = RuntimeModelSnapshot(
                revision=unavailable_revision,
                digest_sha512=unavailable_digest,
                selected_model_key=previous.selected_model_key,
                role_bindings=previous.role_bindings,
                artifact_identity=previous.artifact_identity,
                artifact_digest=previous.artifact_digest,
                backend_identity=previous.backend_identity,
                runtime_state=RuntimeState.UNAVAILABLE,
                loaded_context_size=0,
                model_native_context_limit=previous.model_native_context_limit,
                backend_context_limit=previous.backend_context_limit,
                deployment_verified_context_limit=previous.deployment_verified_context_limit,
                max_output_token_limit=previous.max_output_token_limit,
                current_max_new_tokens=previous.current_max_new_tokens,
                last_transition_receipt=receipt,
            )
            self._snapshot = unavailable_snapshot
            raise RuntimeModelRollbackFailure(reason=reason) from RuntimeModelLoadFailure(
                model_key=target_model_key, reason=reason
            )

        rolled_back_revision = previous.revision + 1
        rolled_back_digest = compute_runtime_model_snapshot_digest(
            revision=rolled_back_revision,
            selected_model_key=previous.selected_model_key,
            role_bindings=previous.role_bindings,
            artifact_identity=previous.artifact_identity,
            artifact_digest=rollback_handle.artifact_digest,
            backend_identity=rollback_handle.backend_identity,
            runtime_state=RuntimeState.ACTIVE,
            loaded_context_size=rollback_handle.loaded_context_size,
            current_max_new_tokens=previous.current_max_new_tokens,
        )
        receipt = TransitionReceipt(
            transition_id=transition_id,
            from_revision=previous.revision,
            to_model_key=target_model_key,
            outcome=SwitchOutcome.ROLLED_BACK,
            started_at=started_at,
            completed_at=_now_iso(),
            failure_reason=reason,
        )
        rolled_back_snapshot = RuntimeModelSnapshot(
            revision=rolled_back_revision,
            digest_sha512=rolled_back_digest,
            selected_model_key=previous.selected_model_key,
            role_bindings=previous.role_bindings,
            artifact_identity=previous.artifact_identity,
            artifact_digest=rollback_handle.artifact_digest,
            backend_identity=rollback_handle.backend_identity,
            runtime_state=RuntimeState.ACTIVE,
            loaded_context_size=rollback_handle.loaded_context_size,
            model_native_context_limit=rollback_handle.capability.native_context_limit,
            backend_context_limit=rollback_handle.capability.backend_context_limit,
            deployment_verified_context_limit=rollback_handle.capability.deployment_verified_context_limit,
            max_output_token_limit=rollback_handle.capability.max_output_token_limit,
            current_max_new_tokens=previous.current_max_new_tokens,
            last_transition_receipt=receipt,
        )
        self._snapshot = rolled_back_snapshot
        raise RuntimeModelLoadFailure(model_key=target_model_key, reason=reason)
