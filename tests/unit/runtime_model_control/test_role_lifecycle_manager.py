from __future__ import annotations

import threading
from dataclasses import dataclass

import pytest

from margpa_runtime_llm.modules.runtime_model_control.application import (
    NONE_PROVIDER,
    QWEN3_GUARD,
    QWEN_MAIN,
    SELENE_JUDGE,
    ProviderSelectionController,
    RoleProviderLifecycleManager,
)
from margpa_runtime_llm.modules.runtime_model_control.application.role_lifecycle_manager import (
    CompositeRoleStatus,
    ModeReadResult,
    RoleTurnHandle,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import ModelRole
from margpa_runtime_llm.modules.runtime_model_control.domain.provider_selection import (
    ProviderOption,
    ProviderRuntimeState,
    ProviderSelectionError,
)


def _no_op_read_mode() -> ModeReadResult:
    return ModeReadResult(revision=None, value="off")


@dataclass
class _FakeAdapter:
    provider_id: str
    preflight_ok: bool = True
    fail_load: bool = False
    fail_unload: bool = False
    load_calls: int = 0
    unload_calls: int = 0

    def preflight(self) -> tuple[bool, str | None]:
        return self.preflight_ok, None if self.preflight_ok else "preflight_unavailable"

    def load(self) -> None:
        self.load_calls += 1
        if self.fail_load:
            raise RuntimeError("load failed")

    def unload(self) -> None:
        self.unload_calls += 1
        if self.fail_unload:
            raise RuntimeError("unload failed")


class _Factory:
    def __init__(self, adapters: dict[str, _FakeAdapter]) -> None:
        self.adapters = adapters

    def create(self, *, role: ModelRole, option: ProviderOption) -> _FakeAdapter:
        del role
        return self.adapters[option.provider_id]


def _select_judge(controller: ProviderSelectionController, provider_id: str) -> None:
    snapshot = controller.snapshot()
    controller.select(
        role=ModelRole.JUDGE,
        provider_id=provider_id,
        expected_revision=snapshot.revision,
        expected_digest=snapshot.digest_sha512,
    )


def test_activation_loads_only_the_explicit_configured_role() -> None:
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    snapshot = manager.activate(role=ModelRole.JUDGE)
    judge = next(item for item in snapshot.selections if item.role is ModelRole.JUDGE)
    guard = next(item for item in snapshot.selections if item.role is ModelRole.GUARD)
    assert selene.load_calls == 1
    assert judge.state is ProviderRuntimeState.ACTIVE
    assert judge.active_provider == SELENE_JUDGE
    assert guard.active_provider is None


def test_none_configured_provider_never_loads_infers_or_falls_back() -> None:
    """P6-DELTA-006 (Post-Claude Independent Review Rework, closes a real
    Coverage Gap found during R20's own 66-Acceptance-ID Audit): a Role
    Configured to `none` must settle at `ProviderRuntimeState.NONE` with
    `active_provider is None`, having never reached the Adapter Factory
    at all — zero Load, zero Inference (there is nothing to run
    Inference against), zero Budget consumption, and no implicit
    fallback to any other registered Provider."""
    selections = ProviderSelectionController()
    snapshot = selections.snapshot()
    selections.select(
        role=ModelRole.JUDGE,
        provider_id=NONE_PROVIDER,
        expected_revision=snapshot.revision,
        expected_digest=snapshot.digest_sha512,
    )

    class _NeverCalledFactory:
        def create(self, *, role: ModelRole, option: object) -> object:
            raise AssertionError(
                f"factory.create() must not be called for a `none` option: {option}"
            )

    manager = RoleProviderLifecycleManager(
        selections=selections,
        factory=_NeverCalledFactory(),  # type: ignore[arg-type]
    )

    result = manager.activate(role=ModelRole.JUDGE)
    judge = next(item for item in result.selections if item.role is ModelRole.JUDGE)

    assert judge.state is ProviderRuntimeState.NONE
    assert judge.active_provider is None
    assert judge.configured_provider == NONE_PROVIDER
    assert manager.active_adapter(role=ModelRole.JUDGE) is None


def test_none_configured_provider_drains_a_stale_active_adapter() -> None:
    """The converse case: switching a Role's Configured Provider *to*
    `none` while a real Adapter is still loaded must actually unload it
    (never leave a stale Adapter silently referenced) — proven by
    reusing the exact same `_FakeAdapter` load/unload-counting fixture
    the rest of this module already relies on."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)
    assert selene.load_calls == 1
    assert manager.active_adapter(role=ModelRole.JUDGE) is selene

    snapshot = selections.snapshot()
    selections.select(
        role=ModelRole.JUDGE,
        provider_id=NONE_PROVIDER,
        expected_revision=snapshot.revision,
        expected_digest=snapshot.digest_sha512,
    )
    result = manager.activate(role=ModelRole.JUDGE)
    judge = next(item for item in result.selections if item.role is ModelRole.JUDGE)

    assert selene.unload_calls == 1
    assert judge.state is ProviderRuntimeState.NONE
    assert judge.active_provider is None
    assert manager.active_adapter(role=ModelRole.JUDGE) is None


def test_preflight_failure_is_typed_unavailable_without_load_or_fallback() -> None:
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE, preflight_ok=False)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    snapshot = manager.activate(role=ModelRole.JUDGE)
    judge = next(item for item in snapshot.selections if item.role is ModelRole.JUDGE)
    assert selene.load_calls == 0
    assert judge.state is ProviderRuntimeState.UNAVAILABLE
    assert judge.active_provider is None
    assert judge.failure_reason == "preflight_unavailable"


def test_candidate_load_failure_restores_previous_active_adapter() -> None:
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    qwen = _FakeAdapter(QWEN_MAIN, fail_load=True)
    manager = RoleProviderLifecycleManager(
        selections=selections,
        factory=_Factory({SELENE_JUDGE: selene, QWEN_MAIN: qwen}),
    )
    manager.activate(role=ModelRole.JUDGE)
    _select_judge(selections, QWEN_MAIN)
    snapshot = manager.activate(role=ModelRole.JUDGE)
    judge = next(item for item in snapshot.selections if item.role is ModelRole.JUDGE)
    assert selene.unload_calls == 1
    assert selene.load_calls == 2
    assert qwen.load_calls == 1
    assert judge.active_provider == SELENE_JUDGE
    assert judge.state is ProviderRuntimeState.UNAVAILABLE
    assert judge.failure_reason == "provider_load_failed:RuntimeError"


def test_off_deactivation_waits_for_active_turn_then_unloads() -> None:
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)
    lease = manager.begin_turn(role=ModelRole.JUDGE)
    pending = manager.deactivate(role=ModelRole.JUDGE)
    pending_judge = next(item for item in pending.selections if item.role is ModelRole.JUDGE)
    assert pending_judge.state is ProviderRuntimeState.DEGRADED
    assert selene.unload_calls == 0
    manager.end_turn(lease)
    judge = selections.selection_for(ModelRole.JUDGE)
    assert selene.unload_calls == 1
    assert judge.active_provider is None
    assert judge.state is ProviderRuntimeState.CONFIGURED


def test_transition_with_previous_unload_failure_is_degraded_not_a_preserved_active_tuple() -> None:
    """P6-RR-R13-WU-006 (Post-Claude Independent Review Rework, resolves
    the rest of P6-CODEX-074): when the previous Adapter's own `unload()`
    raises mid-transition, its actual usability can no longer be
    verified — the Controller must not claim the old Configured/Active
    tuple is still fully intact (that "preserved tuple" claim is only
    honest when the previous Adapter was never touched at all, e.g. a
    Candidate preflight/load failure). It must instead record DEGRADED
    with an exact Failure Reason, and no later Turn-time reader may still
    reach the untrusted Adapter via `active_adapter()`."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE, fail_unload=True)
    qwen = _FakeAdapter(QWEN_MAIN)
    manager = RoleProviderLifecycleManager(
        selections=selections,
        factory=_Factory({SELENE_JUDGE: selene, QWEN_MAIN: qwen}),
    )
    manager.activate(role=ModelRole.JUDGE)
    assert manager.active_adapter(role=ModelRole.JUDGE) is selene

    snapshot = selections.snapshot()
    with pytest.raises(ProviderSelectionError, match="Previous provider unload failed"):
        manager.transition_to(
            role=ModelRole.JUDGE,
            provider_id=QWEN_MAIN,
            expected_revision=snapshot.revision,
            expected_digest=snapshot.digest_sha512,
        )

    judge = selections.selection_for(ModelRole.JUDGE)
    assert judge.state is ProviderRuntimeState.DEGRADED
    assert judge.active_provider is None
    assert judge.configured_provider == SELENE_JUDGE
    assert judge.failure_reason == "previous_provider_unload_failed:RuntimeError"
    assert manager.active_adapter(role=ModelRole.JUDGE) is None
    # The Candidate itself was rolled back (its own `unload()` invoked) —
    # never left silently loaded either.
    assert qwen.load_calls == 1
    assert qwen.unload_calls == 1


def test_switch_is_rejected_while_role_turn_is_active() -> None:
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)
    lease = manager.begin_turn(role=ModelRole.JUDGE)
    with pytest.raises(ProviderSelectionError, match="active role turn"):
        manager.activate(role=ModelRole.JUDGE)
    assert manager.shutdown() is False
    manager.end_turn(lease)
    assert manager.shutdown() is True


@dataclass
class _BlockingAdapter:
    """P6-RR-R17-WU-001..004 (Post-Claude Independent Review Rework,
    resolves P6-CODEX-080): a controllable Adapter whose `load()`/
    `unload()` blocks on an Event, so a Test can force a real Thread to
    sit inside `RoleProviderLifecycleManager`'s Transition Lock for a
    controllable window — exactly the window a Controller diagnostic
    proved an unsynchronized Reader could observe a torn Provider/Mode
    Tuple inside."""

    provider_id: str
    load_started: threading.Event
    release_load: threading.Event
    unload_started: threading.Event | None = None
    release_unload: threading.Event | None = None

    def preflight(self) -> tuple[bool, str | None]:
        return True, None

    def load(self) -> None:
        self.load_started.set()
        self.release_load.wait(timeout=5.0)

    def unload(self) -> None:
        if self.unload_started is not None:
            self.unload_started.set()
        if self.release_unload is not None:
            self.release_unload.wait(timeout=5.0)


def test_composite_status_blocks_until_on_transition_fully_commits() -> None:
    """R17-A/B (ON方向のProvider ACTIVE -> Mode Commit間): a concurrent
    `composite_status()` call must not return while a Thread is inside
    the ACTIVE-then-commit_mode window — it must block on the identical
    Lock and, once unblocked, observe only the fully-new Tuple (Provider
    ACTIVE and Mode committed together), never an intermediate one."""
    load_started = threading.Event()
    release_load = threading.Event()
    selections = ProviderSelectionController()
    selene = _BlockingAdapter(SELENE_JUDGE, load_started=load_started, release_load=release_load)
    manager = RoleProviderLifecycleManager(
        selections=selections,
        factory=_Factory({SELENE_JUDGE: selene}),  # type: ignore[dict-item]
    )
    _select_judge(selections, SELENE_JUDGE)

    committed_mode: list[str] = []

    def _commit() -> None:
        committed_mode.append("enforce")

    def _read_judge_mode() -> ModeReadResult:
        return ModeReadResult(revision=None, value="enforce" if committed_mode else "off")

    transition_thread = threading.Thread(
        target=lambda: manager.apply_mode_transition(
            role=ModelRole.JUDGE,
            target_mode_is_off=False,
            commit_mode=_commit,
            read_judge_mode=_read_judge_mode,
            read_guard_mode=_no_op_read_mode,
        )
    )
    transition_thread.start()
    assert load_started.wait(timeout=5.0), "Transition did not reach the blocking Load in time"

    reader_result: list[CompositeRoleStatus] = []
    reader_thread = threading.Thread(
        target=lambda: reader_result.append(
            manager.composite_status(
                read_judge_mode=_read_judge_mode, read_guard_mode=_no_op_read_mode
            )
        )
    )
    reader_thread.start()
    reader_thread.join(timeout=0.2)
    assert reader_thread.is_alive(), "composite_status() must block while Thread A holds the Lock"
    assert reader_result == []

    release_load.set()
    transition_thread.join(timeout=5.0)
    reader_thread.join(timeout=5.0)
    assert not reader_thread.is_alive()

    composite = reader_result[0]
    assert composite.judge_mode.value == "enforce"
    judge = next(item for item in composite.provider.selections if item.role is ModelRole.JUDGE)
    assert judge.state is ProviderRuntimeState.ACTIVE
    assert judge.active_provider == SELENE_JUDGE


def test_composite_status_blocks_until_off_transition_fully_commits() -> None:
    """R17-C (OFF方向のMode Commit -> Provider Deactivate間): the mirror
    case — Mode commits OFF first (`_deactivate_locked`'s unconditional
    `commit_mode()` at entry), then the Adapter unloads. A concurrent
    `composite_status()` must not observe "Mode OFF, Provider still
    ACTIVE" — it must block until Deactivation itself also finishes."""
    load_started = threading.Event()
    release_load = threading.Event()
    unload_started = threading.Event()
    release_unload = threading.Event()
    selections = ProviderSelectionController()
    selene = _BlockingAdapter(
        SELENE_JUDGE,
        load_started=load_started,
        release_load=release_load,
        unload_started=unload_started,
        release_unload=release_unload,
    )
    manager = RoleProviderLifecycleManager(
        selections=selections,
        factory=_Factory({SELENE_JUDGE: selene}),  # type: ignore[dict-item]
    )
    _select_judge(selections, SELENE_JUDGE)
    release_load.set()
    manager.activate(role=ModelRole.JUDGE)
    release_load.clear()

    committed_mode: list[str] = ["enforce"]

    def _commit_off() -> None:
        committed_mode.clear()

    def _read_judge_mode() -> ModeReadResult:
        return ModeReadResult(revision=None, value="enforce" if committed_mode else "off")

    transition_thread = threading.Thread(
        target=lambda: manager.apply_mode_transition(
            role=ModelRole.JUDGE,
            target_mode_is_off=True,
            commit_mode=_commit_off,
            read_judge_mode=_read_judge_mode,
            read_guard_mode=_no_op_read_mode,
        )
    )
    transition_thread.start()
    assert unload_started.wait(timeout=5.0), "Deactivation did not reach the blocking Unload"

    reader_result: list[CompositeRoleStatus] = []
    reader_thread = threading.Thread(
        target=lambda: reader_result.append(
            manager.composite_status(
                read_judge_mode=_read_judge_mode, read_guard_mode=_no_op_read_mode
            )
        )
    )
    reader_thread.start()
    reader_thread.join(timeout=0.2)
    assert reader_thread.is_alive(), "composite_status() must block while Deactivate holds the Lock"

    release_unload.set()
    transition_thread.join(timeout=5.0)
    reader_thread.join(timeout=5.0)

    composite = reader_result[0]
    assert composite.judge_mode.value == "off"
    judge = next(item for item in composite.provider.selections if item.role is ModelRole.JUDGE)
    assert judge.active_provider is None
    assert judge.state is ProviderRuntimeState.CONFIGURED


def test_composite_status_blocks_for_guard_role_too() -> None:
    """R17 item 5 (Judge/Guard双方): the identical Lock is shared
    Manager-wide, so the same blocking guarantee must hold for Guard, not
    only Judge."""
    load_started = threading.Event()
    release_load = threading.Event()
    selections = ProviderSelectionController()
    guard_adapter = _BlockingAdapter(
        QWEN3_GUARD, load_started=load_started, release_load=release_load
    )
    manager = RoleProviderLifecycleManager(
        selections=selections,
        factory=_Factory({QWEN3_GUARD: guard_adapter}),  # type: ignore[dict-item]
    )
    snapshot = selections.snapshot()
    selections.select(
        role=ModelRole.GUARD,
        provider_id=QWEN3_GUARD,
        expected_revision=snapshot.revision,
        expected_digest=snapshot.digest_sha512,
    )

    transition_thread = threading.Thread(
        target=lambda: manager.apply_mode_transition(
            role=ModelRole.GUARD,
            target_mode_is_off=False,
            commit_mode=lambda: None,
            read_judge_mode=_no_op_read_mode,
            read_guard_mode=_no_op_read_mode,
        )
    )
    transition_thread.start()
    assert load_started.wait(timeout=5.0)

    reader_thread = threading.Thread(
        target=lambda: manager.composite_status(
            read_judge_mode=_no_op_read_mode, read_guard_mode=_no_op_read_mode
        )
    )
    reader_thread.start()
    reader_thread.join(timeout=0.2)
    assert reader_thread.is_alive()

    release_load.set()
    transition_thread.join(timeout=5.0)
    reader_thread.join(timeout=5.0)
    assert not reader_thread.is_alive()


def test_apply_mode_transition_reports_honest_tuple_after_commit_mode_failure() -> None:
    """R17-D (Mode Commit Failure時のHonest Tuple): `commit_mode` only
    ever runs after the Candidate has already fully Loaded and Provider
    Runtime State has already settled at ACTIVE — so if `commit_mode`
    itself then raises, Provider must not stay claimed ACTIVE while Mode
    never actually committed. The just-Loaded Candidate is rolled back
    (unloaded) and the Tuple corrected to an honest UNAVAILABLE state
    with an exact Failure Reason — never a silently-ACTIVE Provider
    paired with an uncommitted Mode."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    _select_judge(selections, SELENE_JUDGE)

    def _failing_commit() -> None:
        raise RuntimeError("mode commit rejected")

    composite = manager.apply_mode_transition(
        role=ModelRole.JUDGE,
        target_mode_is_off=False,
        commit_mode=_failing_commit,
        read_judge_mode=_no_op_read_mode,
        read_guard_mode=_no_op_read_mode,
    )

    assert selene.load_calls == 1
    assert selene.unload_calls == 1
    judge = next(item for item in composite.provider.selections if item.role is ModelRole.JUDGE)
    assert judge.state is ProviderRuntimeState.UNAVAILABLE
    assert judge.active_provider is None
    assert judge.failure_reason == "mode_commit_failed:RuntimeError"
    assert manager.active_adapter(role=ModelRole.JUDGE) is None

    # A subsequent Reader must observe the identical, already-corrected
    # Tuple — never a stale ACTIVE view left over from before the
    # rollback.
    later = manager.composite_status(
        read_judge_mode=_no_op_read_mode, read_guard_mode=_no_op_read_mode
    )
    later_judge = next(item for item in later.provider.selections if item.role is ModelRole.JUDGE)
    assert later_judge.state is ProviderRuntimeState.UNAVAILABLE
    assert later_judge.failure_reason == "mode_commit_failed:RuntimeError"


def test_composite_status_reports_honest_tuple_after_active_turn_drain_pending() -> None:
    """R17-D (Active Turn Drain時のHonest Tuple): while a Deactivation is
    pending an in-flight Turn's drain, `composite_status()` must report
    the real DEGRADED/`active_turn_drain_pending` state — never a
    fabricated OFF/CONFIGURED tuple that hides the still-loaded Adapter."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    _select_judge(selections, SELENE_JUDGE)
    manager.activate(role=ModelRole.JUDGE)
    lease = manager.begin_turn(role=ModelRole.JUDGE)

    manager.apply_mode_transition(
        role=ModelRole.JUDGE,
        target_mode_is_off=True,
        commit_mode=lambda: None,
        read_judge_mode=_no_op_read_mode,
        read_guard_mode=_no_op_read_mode,
    )
    composite = manager.composite_status(
        read_judge_mode=_no_op_read_mode, read_guard_mode=_no_op_read_mode
    )
    judge = next(item for item in composite.provider.selections if item.role is ModelRole.JUDGE)
    assert judge.state is ProviderRuntimeState.DEGRADED
    assert judge.failure_reason == "active_turn_drain_pending"
    assert selene.unload_calls == 0

    manager.end_turn(lease)
    composite_after = manager.composite_status(
        read_judge_mode=_no_op_read_mode, read_guard_mode=_no_op_read_mode
    )
    judge_after = next(
        item for item in composite_after.provider.selections if item.role is ModelRole.JUDGE
    )
    assert judge_after.state is ProviderRuntimeState.CONFIGURED
    assert selene.unload_calls == 1


# P6-RR-R21-WU-001..004 (Post-Codex Independent Review Rework, resolves
# P6-CODEX-086): `begin_role_turn()` Threaded Regression — proves the
# atomic Adapter+Lease pairing genuinely protects a real, concurrently
# in-flight Model Call from a racing Provider Change/Shutdown, that
# Unload never proceeds before Release, and that a Lease released via
# `finally` after a real-call Exception leaves zero Leak (Shutdown/
# Unload converge cleanly afterward).


def test_begin_role_turn_pairs_adapter_and_lease_from_one_lock_acquisition() -> None:
    """The returned `RoleTurnHandle` carries both the exact loaded Adapter
    and a genuine Lease from a single call — never the pre-R21 two-call
    shape (`active_adapter()` then a separate `begin_turn()`)."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)

    handle = manager.begin_role_turn(role=ModelRole.JUDGE)

    assert handle is not None
    assert handle.adapter is selene
    assert handle.lease.role is ModelRole.JUDGE
    assert handle.lease.provider_id == SELENE_JUDGE

    manager.end_turn(handle.lease)
    assert manager.shutdown() is True
    assert selene.unload_calls == 1


def test_begin_role_turn_returns_none_for_a_none_provider_no_lease_acquired() -> None:
    """Built-in/none never populate `_active_adapters` (see `_activate_
    locked`) — `begin_role_turn()` must mirror `active_adapter()`'s own
    silent-`None` contract for them, acquiring no Lease at all, rather
    than raising or fabricating one."""
    selections = ProviderSelectionController()
    snapshot = selections.snapshot()
    selections.select(
        role=ModelRole.JUDGE,
        provider_id=NONE_PROVIDER,
        expected_revision=snapshot.revision,
        expected_digest=snapshot.digest_sha512,
    )
    manager = RoleProviderLifecycleManager(
        selections=selections,
        factory=_Factory({}),
    )
    manager.activate(role=ModelRole.JUDGE)

    assert manager.begin_role_turn(role=ModelRole.JUDGE) is None
    # No Lease was ever acquired, so Shutdown must not be blocked by one.
    assert manager.shutdown() is True


def test_begin_role_turn_blocks_shutdown_from_unloading_until_release() -> None:
    """P6-RR-R21 (resolves P6-CODEX-086): a real in-flight Model Call
    holding a `begin_role_turn()` Lease must genuinely prevent Shutdown
    from Unloading the exact Adapter it is calling through — proven with
    real Threads and an `Event`-gated "in-flight call", not merely
    sequential same-thread calls (which cannot distinguish "Shutdown
    correctly deferred" from "Shutdown simply never attempted
    concurrently"). Shutdown converges immediately (`False`, Adapter
    untouched) the instant it observes the Active Turn; Unload proceeds
    only once `end_turn()` genuinely runs, after the call finishes — the
    exact ordering a TOCTOU gap between a bare `active_adapter()` read and
    a later, separately-locked `begin_turn()` call could never guarantee."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)

    handle = manager.begin_role_turn(role=ModelRole.JUDGE)
    assert handle is not None

    call_started = threading.Event()
    release_call = threading.Event()

    def _real_model_call() -> None:
        call_started.set()
        release_call.wait(timeout=5.0)

    call_thread = threading.Thread(target=_real_model_call)
    call_thread.start()
    assert call_started.wait(timeout=5.0), "real Model Call Thread did not start in time"

    shutdown_result: list[bool] = []
    shutdown_thread = threading.Thread(target=lambda: shutdown_result.append(manager.shutdown()))
    shutdown_thread.start()
    shutdown_thread.join(timeout=5.0)
    assert not shutdown_thread.is_alive()
    assert shutdown_result == [False]
    assert selene.unload_calls == 0, "Unload must never race a still-in-flight real Model Call"

    # A second concurrent attempt to acquire a fresh Turn must also be
    # refused now that Shutdown has begun, even though the Adapter itself
    # has not been Unloaded yet (it is still serving the first Lease).
    with pytest.raises(ProviderSelectionError, match="shutting down"):
        manager.begin_role_turn(role=ModelRole.JUDGE)

    release_call.set()
    call_thread.join(timeout=5.0)
    manager.end_turn(handle.lease)
    # `end_turn()` alone only auto-Unloads when a prior `deactivate()`
    # marked the Role `_pending_unload` — `shutdown()` never does that; it
    # only refuses to proceed while a Turn is Active. A second `shutdown()`
    # call now that the Lease is genuinely Released (and `_shutting_down`
    # is already latched True from the first call) is what actually
    # performs the Unload.
    assert manager.shutdown() is True
    assert selene.unload_calls == 1, "Unload must proceed once the Lease is genuinely Released"


def test_lease_released_via_finally_after_a_real_call_exception_leaves_zero_leak() -> None:
    """P6-RR-R21 (resolves P6-CODEX-086): mirrors the production discipline
    every real call site now uses (`judge_live_integration.py`'s `_run_
    judge`, `qwen3guard_detector_adapter.py`'s `detect()`) — Release from
    a `finally` around the real call, even when that call raises. Zero
    Lease Leak is proven by Shutdown converging cleanly (`True`, Adapter
    actually Unloaded) immediately afterward; a leaked Lease would leave
    `_active_turns` permanently non-zero and Shutdown permanently `False`."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)
    handle = manager.begin_role_turn(role=ModelRole.JUDGE)
    assert handle is not None

    with pytest.raises(RuntimeError, match="simulated real Model Call failure"):
        try:
            raise RuntimeError("simulated real Model Call failure")
        finally:
            manager.end_turn(handle.lease)

    assert manager.shutdown() is True
    assert selene.unload_calls == 1


def test_multiple_concurrent_role_turns_each_track_their_own_lease_generation() -> None:
    """Several genuinely-concurrent real Calls against the same Role must
    each hold the shared Adapter Lock only for their own brief acquire/
    release critical section — `_active_turns` counts every one of them,
    and Shutdown/Unload converge only once every single one has Released,
    never after just the first."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)

    handles = [manager.begin_role_turn(role=ModelRole.JUDGE) for _ in range(3)]
    assert all(handle is not None for handle in handles)
    generations = {handle.lease.generation for handle in handles if handle is not None}
    assert len(generations) == 3, "each concurrent Turn must get its own distinct generation"

    assert manager.shutdown() is False
    assert selene.unload_calls == 0

    for handle in handles[:-1]:
        assert handle is not None
        manager.end_turn(handle.lease)
    assert manager.shutdown() is False
    assert selene.unload_calls == 0, "Unload must wait for every concurrent Lease, not just one"

    last = handles[-1]
    assert last is not None
    manager.end_turn(last.lease)
    assert manager.shutdown() is True
    assert selene.unload_calls == 1


# P6-RR-R26-WU-001..004 (Post-Codex Independent Review Rework, resolves
# P6-CODEX-089): `begin_role_turn()` Threaded/Deterministic Regression —
# Controller Probe B proved a raw Adapter-presence check alone let a
# second concurrent `begin_role_turn()` call resolve a Role that was
# already Draining toward OFF, and that `_unload_locked()`/`end_turn()`
# left a failed-Unload Adapter both reachable and mislabeled CONFIGURED.


def test_off_inserted_between_frozen_belief_and_lease_acquisition_is_refused() -> None:
    """Deterministically reproduces the exact Production race a real Turn
    is exposed to: `judge_live_integration.py`'s own Hook freezes its
    belief about whether it should dispatch (`judge_mode`/`built_in_
    active`/etc.) once, at entry, and only calls `begin_role_turn()`
    moments later — not atomically with that Freeze. A concurrent
    Mode-Apply-to-OFF request that commits in the exact window between
    those two steps must still make the later `begin_role_turn()` call
    refuse, proven with two real Threads and an `Event` forcing the
    interleaving (never a same-Thread sequential call, which could not
    distinguish "correctly refused" from "OFF simply never attempted
    concurrently")."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)

    frozen_belief_captured = threading.Event()
    off_committed = threading.Event()
    lease_holder: list[RoleTurnHandle | None] = []

    def _turn() -> None:
        # "Mode Freeze": the Turn's own belief that it should dispatch is
        # fixed here, at entry — mirrors judge_live_integration.py's own
        # once-per-Run Freeze discipline (judge_mode/repair_mode/
        # recording_mode/built_in_active read exactly once, before any
        # dispatch decision, never re-read mid-Run).
        frozen_should_dispatch = True
        assert frozen_should_dispatch
        frozen_belief_captured.set()
        # Lease acquisition happens strictly after a concurrent OFF
        # commits, in the exact window this Freeze discipline cannot see.
        off_committed.wait(timeout=5.0)
        lease_holder.append(manager.begin_role_turn(role=ModelRole.JUDGE))

    def _off() -> None:
        frozen_belief_captured.wait(timeout=5.0)
        manager.deactivate(role=ModelRole.JUDGE)
        off_committed.set()

    turn_thread = threading.Thread(target=_turn)
    off_thread = threading.Thread(target=_off)
    turn_thread.start()
    off_thread.start()
    turn_thread.join(timeout=5.0)
    off_thread.join(timeout=5.0)

    assert lease_holder == [None]
    assert selene.unload_calls == 1


def test_begin_role_turn_refuses_a_second_lease_once_drain_has_begun() -> None:
    """Drain待ち中の第二Lease拒否Test: a first Lease is genuinely held when
    Mode OFF/Deactivation arrives — the Role enters Drain (`_pending_
    unload`, `DEGRADED`/`active_turn_drain_pending`) without Unloading yet
    (Unload is deferred until every held Lease releases). A *second*
    `begin_role_turn()` call during that Drain window must be refused —
    this specifically exercises the new `state is ACTIVE`/`_pending_
    unload` checks, not merely the pre-existing "no Adapter at all"
    short-circuit (the Adapter reference is still genuinely present in
    `_active_adapters` throughout Drain)."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)
    first = manager.begin_role_turn(role=ModelRole.JUDGE)
    assert first is not None

    pending = manager.deactivate(role=ModelRole.JUDGE)
    judge = next(item for item in pending.selections if item.role is ModelRole.JUDGE)
    assert judge.state is ProviderRuntimeState.DEGRADED
    assert judge.failure_reason == "active_turn_drain_pending"
    assert selene.unload_calls == 0, "Unload must be deferred until every held Lease releases"

    second = manager.begin_role_turn(role=ModelRole.JUDGE)
    assert second is None

    manager.end_turn(first.lease)
    assert selene.unload_calls == 1


def test_begin_role_turn_refuses_after_an_immediate_unload_exception() -> None:
    """Unload Exception後の新規Lease拒否Test (no Lease held case): a bare
    `deactivate()` with zero active Turns attempts Unload immediately,
    which raises — `begin_role_turn()` afterward must never resolve the
    now-untrusted Adapter, converging to `DEGRADED`/`provider_unload_
    failed`."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE, fail_unload=True)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)

    pending = manager.deactivate(role=ModelRole.JUDGE)
    judge = next(item for item in pending.selections if item.role is ModelRole.JUDGE)
    assert judge.state is ProviderRuntimeState.DEGRADED
    assert judge.failure_reason == "provider_unload_failed"

    assert manager.begin_role_turn(role=ModelRole.JUDGE) is None


def test_end_turn_drain_completion_with_unload_failure_settles_degraded_not_configured() -> None:
    """The exact P6-CODEX-089 "CONFIGUREDへ偽装" bug, directly: `end_turn()`
    previously discarded `_unload_locked()`'s own return value and always
    claimed `CONFIGURED` once the last held Lease Drained, even when
    Unload itself had just raised. It must instead mirror `_deactivate_
    locked`'s own already-correct unload_ok-driven resolution — `DEGRADED`
    with `provider_unload_failed`, never a claimed-clean `CONFIGURED` —
    and a subsequent `begin_role_turn()` on that now-permanently-failed
    Role must refuse."""
    selections = ProviderSelectionController()
    selene = _FakeAdapter(SELENE_JUDGE, fail_unload=True)
    manager = RoleProviderLifecycleManager(
        selections=selections, factory=_Factory({SELENE_JUDGE: selene})
    )
    manager.activate(role=ModelRole.JUDGE)
    handle = manager.begin_role_turn(role=ModelRole.JUDGE)
    assert handle is not None

    pending = manager.deactivate(role=ModelRole.JUDGE)
    judge = next(item for item in pending.selections if item.role is ModelRole.JUDGE)
    assert judge.state is ProviderRuntimeState.DEGRADED
    assert judge.failure_reason == "active_turn_drain_pending"
    assert selene.unload_calls == 0

    manager.end_turn(handle.lease)

    final = selections.snapshot()
    judge_final = next(item for item in final.selections if item.role is ModelRole.JUDGE)
    assert judge_final.state is ProviderRuntimeState.DEGRADED
    assert judge_final.failure_reason == "provider_unload_failed"
    assert judge_final.active_provider is None
    assert selene.unload_calls == 1

    assert manager.begin_role_turn(role=ModelRole.JUDGE) is None
