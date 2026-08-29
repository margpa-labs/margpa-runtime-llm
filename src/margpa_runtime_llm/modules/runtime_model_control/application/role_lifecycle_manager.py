"""Transactional lifecycle for dedicated Guard/Judge provider adapters."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass

from ..domain.identifiers import ModelRole
from ..domain.provider_selection import (
    ProviderKind,
    ProviderRuntimeState,
    ProviderSelectionError,
    ProviderSelectionErrorCode,
    ProviderSelectionSnapshot,
)
from ..ports import (
    RoleAdapterFactoryPort,
    RoleProviderAdapterPort,
    RoleResourceGatePort,
)
from .provider_selection_controller import ProviderSelectionController


@dataclass(frozen=True, slots=True)
class RoleTurnLease:
    role: ModelRole
    provider_id: str
    generation: int


@dataclass(frozen=True, slots=True)
class RoleTurnHandle:
    """P6-RR-R21 (resolves P6-CODEX-086): pairs a `RoleTurnLease` with the
    exact `RoleProviderAdapterPort` it was granted for, both produced by
    one call to `begin_role_turn()` — see that method's own docstring for
    why a separate `active_adapter()` read followed by a separate
    `begin_turn()` call is a genuine TOCTOU gap this pairing closes."""

    lease: RoleTurnLease
    adapter: RoleProviderAdapterPort


@dataclass(frozen=True, slots=True)
class ModeReadResult:
    """Provider-neutral snapshot of one Mode Controller's current value —
    lets `RoleProviderLifecycleManager` read Judge/Guard Mode without
    importing either concrete Controller type (both `JudgeModeController.
    mode_snapshot()` and `GuardrailModeController.mode_snapshot()` carry
    this exact `revision`/`current_mode.value` shape already)."""

    revision: int | None
    value: str


@dataclass(frozen=True, slots=True)
class CompositeRoleStatus:
    """P6-RR-R17-WU-001..004 (Post-Claude Independent Review Rework,
    resolves P6-CODEX-080): Provider Selection state and both Mode
    Controllers' current value, read together under this Manager's own
    Transition Lock (`self._condition`) — the identical Lock
    `apply_mode_transition`/`apply_provider_selection` hold for their
    entire Activate-then-Commit / Commit-then-Deactivate critical
    section. A caller that obtains its Provider+Mode view exclusively
    through `composite_status()` (a pure read) or through a Mutation
    call's own return value (never through a second, separate,
    post-Lock-release read of either source) can never observe a torn
    tuple — Provider already ACTIVE with Mode still OFF, or Mode already
    committed OFF with Provider not yet Deactivated — because that read
    either runs entirely before the Mutation's critical section starts
    (sees the complete old Tuple) or entirely after it ends (sees the
    complete new Tuple), never during it. A Controller diagnostic
    reproduced the previous gap directly: a Reader using two independent
    Locks (`ProviderSelectionController`'s own, and `JudgeModeController`'s
    own) could observe `active_provider=built_in.deterministic` /
    `mode=off` mid-Transition, because neither of those two Locks is this
    Manager's own `self._condition` — only routing every Reader through
    this Manager's Lock closes that gap."""

    provider: ProviderSelectionSnapshot
    judge_mode: ModeReadResult
    guard_mode: ModeReadResult


class AllowAllRoleResourceGate:
    def allow_activation(self, *, role: ModelRole, option: object) -> tuple[bool, str | None]:
        del role, option
        return True, None


class RoleProviderLifecycleManager:
    """Owns dedicated adapters; configuration alone never loads a model.

    P6-RR-R13 (Post-Claude Independent Review Rework, resolves
    P6-CODEX-074/069/062): this Manager's own `self._condition` lock is
    now the single Role Transition Coordinator boundary for a given Role
    — every operation that reads-then-acts on Mode-vs-Provider state
    (Mode-Apply-to-ON, Mode-Apply-to-OFF, and a Provider-Selection change
    while Mode is currently ON or OFF) goes through `apply_mode_transition`
    /`apply_provider_selection`, both acquiring this exact Lock for their
    entire body. The previous design had each caller (`feature_modes_
    routes.py`, `configuration_control.py`'s Guardrail Mode Applier,
    `provider_selection_routes.py`) independently read Mode, then release
    and re-acquire this Manager's Lock for the Provider half, and commit
    Mode from *outside* this Lock entirely — a genuine TOCTOU window where
    a concurrent request on the other path could interleave and produce
    `Mode ON / Active none` or an orphaned stale Adapter. `commit_mode`/
    `mode_is_on` are Callables (never a concrete `JudgeModeController`/
    `GuardrailModeController` import here — this module stays
    Provider-neutral, matching every other Hook boundary in this
    codebase) invoked *while this Lock is held*, so Mode Controller state
    and Provider/Lifecycle state change together or not at all, and a
    concurrent caller can only ever observe the complete old Tuple or the
    complete new Tuple."""

    def __init__(
        self,
        *,
        selections: ProviderSelectionController,
        factory: RoleAdapterFactoryPort,
        resource_gate: RoleResourceGatePort | None = None,
    ) -> None:
        self._condition = threading.Condition()
        self._selections = selections
        self._factory = factory
        self._resource_gate = resource_gate or AllowAllRoleResourceGate()
        self._active_adapters: dict[ModelRole, RoleProviderAdapterPort] = {}
        self._active_turns: dict[ModelRole, int] = {role: 0 for role in ModelRole}
        self._turn_generation = 0
        self._pending_unload: set[ModelRole] = set()
        self._shutting_down = False

    def activate(self, *, role: ModelRole) -> ProviderSelectionSnapshot:
        """Direct entry point (no Mode commit) — kept for callers/tests
        that only need Provider Activation itself. Production Mode-Apply
        routes use `apply_mode_transition` instead, so Mode is committed
        under the same Lock as this method's own work."""
        with self._condition:
            return self._activate_locked(role=role, commit_mode=None)

    def deactivate(self, *, role: ModelRole) -> ProviderSelectionSnapshot:
        with self._condition:
            return self._deactivate_locked(role=role, commit_mode=None)

    def apply_mode_transition(
        self,
        *,
        role: ModelRole,
        target_mode_is_off: bool,
        commit_mode: Callable[[], None],
        read_judge_mode: Callable[[], ModeReadResult],
        read_guard_mode: Callable[[], ModeReadResult],
    ) -> CompositeRoleStatus:
        """Unified Mode-Apply entry point (P6-RR-R13-WU-001..004, extended
        P6-RR-R17-WU-001..004 to resolve P6-CODEX-080).

        `commit_mode` (e.g. `lambda: judge_mode_control.apply_mode(mode)`)
        runs inside this same Lock. For `target_mode_is_off=False`, it is
        invoked only when Activation genuinely settles at `ACTIVE` — never
        when Activation fails, so a failed Activation can never leave Mode
        committed ON (mirrors the exact `state is not ACTIVE -> raise,
        never commit` contract the pre-R13 caller-side check already had,
        now race-free). For `target_mode_is_off=True`, Mode always
        commits OFF — Deactivation itself never fails in a way that should
        block turning a Role OFF.

        `read_judge_mode`/`read_guard_mode` are called *inside this same
        Lock*, after the Transition settles, and their result is what this
        call returns — the caller building a Mode-Apply HTTP Response must
        use that returned `CompositeRoleStatus` directly and never perform
        a second, separate, post-Lock-release read of Mode or Provider
        state to build that same Response (P6-CODEX-080's "Mode Apply
        Response" finding: a later independent re-read can legitimately
        observe a *different* Transaction's result than the one this
        call itself just committed).
        """
        with self._condition:
            if target_mode_is_off:
                commit_mode()
                self._deactivate_locked(role=role, commit_mode=None)
            else:
                self._activate_locked(role=role, commit_mode=commit_mode)
            return CompositeRoleStatus(
                provider=self._selections.snapshot(),
                judge_mode=read_judge_mode(),
                guard_mode=read_guard_mode(),
            )

    def apply_provider_selection(
        self,
        *,
        role: ModelRole,
        provider_id: str,
        expected_revision: int,
        expected_digest: str,
        mode_is_on: Callable[[], bool],
        read_judge_mode: Callable[[], ModeReadResult],
        read_guard_mode: Callable[[], ModeReadResult],
    ) -> CompositeRoleStatus:
        """Unified Provider-Selection entry point (P6-RR-R13-WU-001..004,
        resolves P6-CODEX-074/062; extended P6-RR-R17-WU-001..004 to
        resolve P6-CODEX-080). `mode_is_on` is read *inside* this same
        Lock — `apply_mode_transition` above commits Mode under this
        identical Lock, so no interleaving between "read Mode" and "act on
        Provider Selection" is observable from any other thread. See
        `apply_mode_transition`'s own docstring for why the caller must
        build its HTTP Response from this call's returned
        `CompositeRoleStatus` and never a later separate re-read."""
        with self._condition:
            if not mode_is_on():
                provider = self._selections.select(
                    role=role,
                    provider_id=provider_id,
                    expected_revision=expected_revision,
                    expected_digest=expected_digest,
                )
            else:
                provider = self._transition_to_locked(
                    role=role,
                    provider_id=provider_id,
                    expected_revision=expected_revision,
                    expected_digest=expected_digest,
                )
            return CompositeRoleStatus(
                provider=provider,
                judge_mode=read_judge_mode(),
                guard_mode=read_guard_mode(),
            )

    def composite_status(
        self,
        *,
        read_judge_mode: Callable[[], ModeReadResult],
        read_guard_mode: Callable[[], ModeReadResult],
    ) -> CompositeRoleStatus:
        """Pure-read counterpart to `apply_mode_transition`/
        `apply_provider_selection` (P6-RR-R17-WU-001..004, resolves
        P6-CODEX-080): a GET-style caller (Provider Selection GET, Feature
        Modes GET) that needs Provider Selection state and Mode value
        together must call this — never independently call
        `ProviderSelectionController.snapshot()` and a Mode Controller's
        own `mode_snapshot()` as two unsynchronized reads — so a Reader
        can never land inside another Thread's in-flight Transition."""
        with self._condition:
            return CompositeRoleStatus(
                provider=self._selections.snapshot(),
                judge_mode=read_judge_mode(),
                guard_mode=read_guard_mode(),
            )

    def _commit_mode_after_activation(
        self,
        *,
        role: ModelRole,
        commit_mode: Callable[[], None] | None,
        configured_provider: str,
        active_snapshot: ProviderSelectionSnapshot,
        candidate: RoleProviderAdapterPort | None,
    ) -> ProviderSelectionSnapshot:
        """Runs `commit_mode()` after Provider Runtime State has already
        settled at ACTIVE (Built-in, or a real Candidate that finished
        Loading). P6-RR-R17-WU-001..004 (resolves P6-CODEX-080's "Mode
        Commit Failure時のHonest Tuple"): if `commit_mode` itself raises,
        Provider must not stay claimed ACTIVE while Mode never actually
        committed — the Candidate (if any) is rolled back and the Tuple
        corrected to an honest UNAVAILABLE/DEGRADED state before this
        Transition's caller (or any concurrent `composite_status()`
        Reader, once the Lock is released) can observe it, mirroring the
        exact rollback discipline `candidate.load()` failure above
        already uses."""
        if commit_mode is None:
            return active_snapshot
        try:
            commit_mode()
        except Exception as exc:
            rollback_failed = False
            if candidate is not None:
                self._active_adapters.pop(role, None)
                try:
                    candidate.unload()
                except Exception:
                    rollback_failed = True
            return self._selections.replace_runtime_state(
                role=role,
                configured_provider=configured_provider,
                active_provider=None,
                state=(
                    ProviderRuntimeState.DEGRADED
                    if rollback_failed
                    else ProviderRuntimeState.UNAVAILABLE
                ),
                failure_reason=(
                    f"mode_commit_and_rollback_failed:{type(exc).__name__}"
                    if rollback_failed
                    else f"mode_commit_failed:{type(exc).__name__}"
                ),
            )
        return active_snapshot

    def _activate_locked(
        self, *, role: ModelRole, commit_mode: Callable[[], None] | None
    ) -> ProviderSelectionSnapshot:
        """Body of the former `activate()` — assumes the caller already
        holds `self._condition`. `commit_mode()` (if supplied) runs only
        on the two paths that settle at `ProviderRuntimeState.ACTIVE`."""
        if role is ModelRole.MAIN:
            raise ProviderSelectionError(
                code=ProviderSelectionErrorCode.ROLE_MISMATCH,
                safe_message="Main lifecycle is owned by RuntimeModelController.",
            )
        if self._shutting_down:
            raise ProviderSelectionError(
                code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                safe_message="Provider lifecycle is shutting down.",
            )
        if self._active_turns[role] > 0:
            raise ProviderSelectionError(
                code=ProviderSelectionErrorCode.ACTIVE_TURN,
                safe_message="An active role turn must drain before provider activation.",
            )
        selection = self._selections.selection_for(role)
        option = self._selections.option_for(role=role, provider_id=selection.configured_provider)
        if option is None:
            raise ProviderSelectionError(
                code=ProviderSelectionErrorCode.UNKNOWN_PROVIDER,
                safe_message="The configured provider is not registered.",
            )
        if option.kind is ProviderKind.NONE:
            self._unload_locked(role)
            return self._selections.replace_runtime_state(
                role=role,
                configured_provider=selection.configured_provider,
                active_provider=None,
                state=ProviderRuntimeState.NONE,
            )
        if option.kind is ProviderKind.BUILT_IN:
            self._unload_locked(role)
            snapshot = self._selections.replace_runtime_state(
                role=role,
                configured_provider=selection.configured_provider,
                active_provider=selection.configured_provider,
                state=ProviderRuntimeState.ACTIVE,
            )
            return self._commit_mode_after_activation(
                role=role,
                commit_mode=commit_mode,
                configured_provider=selection.configured_provider,
                active_snapshot=snapshot,
                candidate=None,
            )
        allowed, gate_reason = self._resource_gate.allow_activation(role=role, option=option)
        if not allowed:
            return self._selections.replace_runtime_state(
                role=role,
                configured_provider=selection.configured_provider,
                active_provider=None,
                state=ProviderRuntimeState.UNAVAILABLE,
                failure_reason=gate_reason or "resource_gate_denied",
            )
        previous = self._active_adapters.get(role)
        previous_provider = previous.provider_id if previous is not None else None
        try:
            candidate = self._factory.create(role=role, option=option)
        except Exception as exc:
            raise ProviderSelectionError(
                code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                safe_message=f"Provider creation failed: {type(exc).__name__}",
            ) from exc
        ready, reason = candidate.preflight()
        if not ready:
            return self._selections.replace_runtime_state(
                role=role,
                configured_provider=selection.configured_provider,
                active_provider=previous_provider,
                state=ProviderRuntimeState.UNAVAILABLE,
                failure_reason=reason or "provider_preflight_failed",
            )
        self._selections.replace_runtime_state(
            role=role,
            configured_provider=selection.configured_provider,
            active_provider=previous_provider,
            state=ProviderRuntimeState.LOADING,
        )
        if previous is not None:
            previous.unload()
            self._active_adapters.pop(role, None)
        try:
            candidate.load()
        except Exception as exc:
            rollback_failed = False
            if previous is not None:
                try:
                    previous.load()
                    self._active_adapters[role] = previous
                except Exception:
                    rollback_failed = True
            return self._selections.replace_runtime_state(
                role=role,
                configured_provider=selection.configured_provider,
                active_provider=(
                    previous_provider if previous is not None and not rollback_failed else None
                ),
                state=(
                    ProviderRuntimeState.FAILED
                    if rollback_failed
                    else ProviderRuntimeState.UNAVAILABLE
                ),
                failure_reason=(
                    "provider_load_and_rollback_failed"
                    if rollback_failed
                    else f"provider_load_failed:{type(exc).__name__}"
                ),
            )
        self._active_adapters[role] = candidate
        self._pending_unload.discard(role)
        snapshot = self._selections.replace_runtime_state(
            role=role,
            configured_provider=selection.configured_provider,
            active_provider=selection.configured_provider,
            state=ProviderRuntimeState.ACTIVE,
        )
        return self._commit_mode_after_activation(
            role=role,
            commit_mode=commit_mode,
            configured_provider=selection.configured_provider,
            active_snapshot=snapshot,
            candidate=candidate,
        )

    def _deactivate_locked(
        self, *, role: ModelRole, commit_mode: Callable[[], None] | None
    ) -> ProviderSelectionSnapshot:
        if commit_mode is not None:
            commit_mode()
        selection = self._selections.selection_for(role)
        if self._active_turns[role] > 0:
            self._pending_unload.add(role)
            return self._selections.replace_runtime_state(
                role=role,
                configured_provider=selection.configured_provider,
                active_provider=selection.active_provider,
                state=ProviderRuntimeState.DEGRADED,
                failure_reason="active_turn_drain_pending",
            )
        unload_ok = self._unload_locked(role)
        return self._selections.replace_runtime_state(
            role=role,
            configured_provider=selection.configured_provider,
            active_provider=None,
            state=(
                ProviderRuntimeState.CONFIGURED
                if unload_ok and selection.configured_provider != "none"
                else ProviderRuntimeState.NONE
                if unload_ok
                else ProviderRuntimeState.DEGRADED
            ),
            failure_reason=(None if unload_ok else "provider_unload_failed"),
        )

    def transition_to(
        self,
        *,
        role: ModelRole,
        provider_id: str,
        expected_revision: int,
        expected_digest: str,
    ) -> ProviderSelectionSnapshot:
        """Direct entry point — kept for callers/tests that only need the
        Provider-Selection transition itself, without a Mode read/commit.
        Production routes use `apply_provider_selection` instead."""
        with self._condition:
            return self._transition_to_locked(
                role=role,
                provider_id=provider_id,
                expected_revision=expected_revision,
                expected_digest=expected_digest,
            )

    def _transition_to_locked(
        self,
        *,
        role: ModelRole,
        provider_id: str,
        expected_revision: int,
        expected_digest: str,
    ) -> ProviderSelectionSnapshot:
        """Atomically replace an active Guard/Judge provider.

        Candidate preflight/load is completed while the previous adapter is
        still usable.  The controller is changed only after the previous
        adapter has unloaded, so status readers observe either the complete old
        tuple or the complete new tuple, never ``mode on / active none``.

        Assumes the caller already holds `self._condition`.
        """
        if role is ModelRole.MAIN:
            raise ProviderSelectionError(
                code=ProviderSelectionErrorCode.ROLE_MISMATCH,
                safe_message="Main lifecycle is owned by RuntimeModelController.",
            )
        if self._shutting_down:
            raise ProviderSelectionError(
                code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                safe_message="Provider lifecycle is shutting down.",
            )
        if self._active_turns[role] > 0:
            raise ProviderSelectionError(
                code=ProviderSelectionErrorCode.ACTIVE_TURN,
                safe_message="An active role turn must drain before provider transition.",
            )
        current = self._selections.snapshot()
        if current.revision != expected_revision or current.digest_sha512 != expected_digest:
            raise ProviderSelectionError(
                code=ProviderSelectionErrorCode.REVISION_CONFLICT,
                safe_message="The provider selection changed; reload and retry.",
                current_snapshot=current,
            )
        previous = self._selections.selection_for(role)
        if previous.configured_provider == provider_id:
            return current
        option = self._selections.option_for(role=role, provider_id=provider_id)
        if option is None or not option.enabled:
            raise ProviderSelectionError(
                code=(
                    ProviderSelectionErrorCode.UNKNOWN_PROVIDER
                    if option is None
                    else ProviderSelectionErrorCode.PROVIDER_DISABLED
                ),
                safe_message="The selected provider is unavailable.",
            )

        candidate: RoleProviderAdapterPort | None = None
        if option.kind is ProviderKind.MODEL:
            allowed, reason = self._resource_gate.allow_activation(role=role, option=option)
            if not allowed:
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                    safe_message=reason or "The provider cannot be activated.",
                )
            try:
                candidate = self._factory.create(role=role, option=option)
            except Exception as exc:
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                    safe_message=f"Provider creation failed: {type(exc).__name__}",
                ) from exc
            ready, reason = candidate.preflight()
            if not ready:
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                    safe_message=reason or "The provider preflight failed.",
                )
            try:
                candidate.load()
            except Exception as exc:
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                    safe_message=f"Provider load failed: {type(exc).__name__}",
                ) from exc

        previous_adapter = self._active_adapters.get(role)
        if previous_adapter is not None:
            try:
                previous_adapter.unload()
            except Exception as exc:
                if candidate is not None:
                    try:
                        candidate.unload()
                    except Exception:
                        pass
                # P6-RR-R13-WU-006 (Post-Claude Independent Review Rework,
                # resolves the rest of P6-CODEX-074): the previous Adapter's
                # own `unload()` raising means its actual usability can no
                # longer be verified — Controller state must not silently
                # claim the old Configured/Active tuple is still fully
                # intact ("preserved tuple" is only honest when the old
                # Adapter was never touched, e.g. a Candidate
                # preflight/load failure above). Recorded as DEGRADED with
                # an exact Failure Reason, matching `_deactivate_locked`'s
                # own existing DEGRADED-on-uncertain-unload contract,
                # rather than a claimed complete Rollback.
                # An Adapter whose own `unload()` just raised is never
                # trusted as still Active/usable by any later Turn-time
                # reader (`active_adapter()`) — treated as gone, exactly
                # like a genuinely unavailable Provider, not as a stale
                # reference a Judge/Guard Dispatch could still reach.
                self._active_adapters.pop(role, None)
                self._selections.replace_runtime_state(
                    role=role,
                    configured_provider=previous.configured_provider,
                    active_provider=None,
                    state=ProviderRuntimeState.DEGRADED,
                    failure_reason=f"previous_provider_unload_failed:{type(exc).__name__}",
                )
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                    safe_message=f"Previous provider unload failed: {type(exc).__name__}",
                ) from exc
        try:
            snapshot = self._selections.select_active(
                role=role,
                provider_id=provider_id,
                expected_revision=expected_revision,
                expected_digest=expected_digest,
            )
        except Exception:
            if candidate is not None:
                try:
                    candidate.unload()
                except Exception:
                    pass
            if previous_adapter is not None:
                previous_adapter.load()
            raise
        if candidate is None:
            self._active_adapters.pop(role, None)
        else:
            self._active_adapters[role] = candidate
        self._pending_unload.discard(role)
        return snapshot

    def active_adapter(self, *, role: ModelRole) -> RoleProviderAdapterPort | None:
        """The currently-loaded dedicated adapter for `role`, if any.

        Read-only projection for a Turn-time caller (Judge/Guard Hook) that
        needs the concrete adapter behind an ACTIVE Role Provider Selection
        (e.g. to invoke Selene's `SeleneSemanticEvaluator` or Qwen3Guard's
        `Qwen3GuardGenAdapter`) without this Manager exposing its private
        adapter dict. Returns None for `none`/`built_in` selections, which
        never populate `_active_adapters` (see `activate()`)."""
        with self._condition:
            return self._active_adapters.get(role)

    def begin_role_turn(self, *, role: ModelRole) -> RoleTurnHandle | None:
        """P6-RR-R21-WU-001 (Post-Codex Independent Review Rework, resolves
        P6-CODEX-086): atomically resolves the currently-loaded dedicated
        Model Adapter AND acquires its Turn Lease under one acquisition of
        this Manager's own `self._condition` — replacing the TOCTOU-prone
        pattern of a Turn-time caller invoking `active_adapter()` and, in a
        second, later, separately-locked call, `begin_turn()`. Between
        those two calls a concurrent Provider Selection change, Mode OFF,
        or Shutdown could interleave and Unload the very Adapter the
        second call would then hand a Lease for — Production Judge/Guard
        dispatch never called either API before this Package (P6-CODEX-086
        found 0 Production call sites; only Tests exercised them), so nothing
        actually protected an in-flight real Model Call from a racing
        Deactivation.

        Mirrors `active_adapter()`'s own silent-`None` contract for
        `none`/`built_in` Selections and for a Role that currently has no
        loaded Adapter (Loading/Unavailable/Degraded/Configured/Failed) —
        a Turn-time caller must already treat `None` as "no Model Lease,
        proceed without one", exactly as it does today for a bare
        `active_adapter()` miss; this never raises for those ordinary
        states, so no Turn-time caller needs new exception handling beyond
        what `active_adapter()` already required. It raises
        `ProviderSelectionError` only when a real Adapter is currently
        loaded but Shutdown has already begun — the one case where
        granting a new Lease would be actively wrong (this Manager is
        already tearing every Adapter down; a Lease on that Adapter after
        this point must never be handed out, even though the Adapter
        reference itself has not yet been Unloaded).

        P6-RR-R26 (Post-Codex Independent Review Rework, resolves
        P6-CODEX-089): a bare Adapter-presence check was not enough —
        Mode OFF/Deactivation while a Turn is already active enters Drain
        (`_deactivate_locked` adds `role` to `_pending_unload` and settles
        `ProviderRuntimeState.DEGRADED`/`active_turn_drain_pending`)
        *without* removing the reference from `_active_adapters` (Unload
        itself is deferred until every Lease Drains via `end_turn()`).
        Controller Probe B proved a *second*, concurrent `begin_role_turn()`
        call during that Drain window could still resolve the same stale
        Adapter and be handed a brand-new Lease — extending the very Drain
        it should have been blocked by. This method now additionally
        requires the Selection to be genuinely `ACTIVE`, with a non-`None`
        `active_provider` that matches this exact Adapter's own
        `provider_id`, and the Role to not already be `_pending_unload` —
        every one of those is checked inside this same Lock acquisition,
        so a Lease already granted before OFF continues to Drain normally
        (untouched by this check), while no *new* Lease is ever granted
        once Drain has begun."""
        with self._condition:
            adapter = self._active_adapters.get(role)
            if adapter is None:
                return None
            if self._shutting_down:
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                    safe_message="Provider lifecycle is shutting down.",
                )
            selection = self._selections.selection_for(role)
            if (
                selection.state is not ProviderRuntimeState.ACTIVE
                or selection.active_provider is None
                or selection.active_provider != adapter.provider_id
                or role in self._pending_unload
            ):
                return None
            self._active_turns[role] += 1
            self._turn_generation += 1
            lease = RoleTurnLease(
                role=role,
                provider_id=selection.active_provider,
                generation=self._turn_generation,
            )
            return RoleTurnHandle(lease=lease, adapter=adapter)

    def begin_turn(self, *, role: ModelRole) -> RoleTurnLease:
        with self._condition:
            selection = self._selections.selection_for(role)
            if (
                self._shutting_down
                or selection.state is not ProviderRuntimeState.ACTIVE
                or selection.active_provider is None
            ):
                raise ProviderSelectionError(
                    code=ProviderSelectionErrorCode.ACTIVATION_FAILED,
                    safe_message="The selected role provider is not active.",
                )
            self._active_turns[role] += 1
            self._turn_generation += 1
            return RoleTurnLease(
                role=role,
                provider_id=selection.active_provider,
                generation=self._turn_generation,
            )

    def end_turn(self, lease: RoleTurnLease) -> None:
        with self._condition:
            if self._active_turns[lease.role] > 0:
                self._active_turns[lease.role] -= 1
            if self._active_turns[lease.role] == 0 and lease.role in self._pending_unload:
                # P6-RR-R26 (resolves P6-CODEX-089): `_unload_locked()`'s
                # own return value was previously discarded here — the
                # Drain-completion State always claimed `CONFIGURED`
                # regardless of whether Unload actually succeeded,
                # disguising a genuine Unload failure as a clean settle.
                # Mirrors `_deactivate_locked`'s own already-correct
                # unload_ok-driven State/Failure Reason resolution exactly
                # (the immediate, no-Drain-needed path through the same
                # Unload outcome), so both Drain-completion routes agree.
                unload_ok = self._unload_locked(lease.role)
                self._pending_unload.discard(lease.role)
                selection = self._selections.selection_for(lease.role)
                self._selections.replace_runtime_state(
                    role=lease.role,
                    configured_provider=selection.configured_provider,
                    active_provider=None,
                    state=(
                        ProviderRuntimeState.CONFIGURED
                        if unload_ok and selection.configured_provider != "none"
                        else ProviderRuntimeState.NONE
                        if unload_ok
                        else ProviderRuntimeState.DEGRADED
                    ),
                    failure_reason=(None if unload_ok else "provider_unload_failed"),
                )
            self._condition.notify_all()

    def shutdown(self) -> bool:
        with self._condition:
            self._shutting_down = True
            if any(self._active_turns.values()):
                return False
            clean = True
            for role in tuple(self._active_adapters):
                clean = self._unload_locked(role) and clean
            return clean

    def _unload_locked(self, role: ModelRole) -> bool:
        adapter = self._active_adapters.get(role)
        if adapter is None:
            return True
        try:
            adapter.unload()
        except Exception:
            # P6-RR-R26 (resolves the second half of P6-CODEX-089, and the
            # Claude-authored IR-R24-001 Observation this Review upgraded
            # to a Finding): an Adapter whose own `unload()` just raised is
            # never trusted as still reachable by a later Turn-time reader
            # — popped here exactly like the success path below, mirroring
            # `_transition_to_locked`'s own already-correct
            # pop-on-failed-unload discipline. Leaving it in `_active_
            # adapters` after a failed Unload let `begin_role_turn()`
            # resolve it again and hand out a fresh Lease for an Adapter
            # this Manager itself no longer trusts.
            self._active_adapters.pop(role, None)
            return False
        self._active_adapters.pop(role, None)
        return True
