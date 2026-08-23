import threading
import time

import pytest

from margpa_runtime_llm.modules.inference.application.model_access_coordinator import (
    ModelAccessCoordinator,
)
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.errors import (
    RuntimeModelBusyError,
    RuntimeModelLoadFailure,
    RuntimeModelRevisionConflict,
    RuntimeModelRollbackFailure,
    RuntimeModelTargetNotRegistered,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    BindingState,
    IndependenceClass,
    ModelRole,
    RuntimeState,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.snapshot import (
    RoleBinding,
    RuntimeModelSnapshot,
    compute_runtime_model_snapshot_digest,
)
from margpa_runtime_llm.modules.runtime_model_control.ports import (
    CapabilityProbeResult,
    LoadedModelHandle,
)

from .conftest import make_model_definition

_SHA512_FILLER = "c" * 128
_QWEN_KEY = "main.qwen3-4b-q4-k-m"
_DEEPSEEK_KEY = "main.deepseek-r1-0528-qwen3-8b-q4-k-m"


def _initial_snapshot() -> RuntimeModelSnapshot:
    binding = RoleBinding(
        role=ModelRole.MAIN,
        model_identity=_QWEN_KEY,
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=_SHA512_FILLER,
    )
    digest = compute_runtime_model_snapshot_digest(
        revision=0,
        selected_model_key=_QWEN_KEY,
        role_bindings=(binding,),
        artifact_identity=_QWEN_KEY,
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=4096,
        current_max_new_tokens=2048,
    )
    return RuntimeModelSnapshot(
        revision=0,
        digest_sha512=digest,
        selected_model_key=_QWEN_KEY,
        role_bindings=(binding,),
        artifact_identity=_QWEN_KEY,
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=4096,
        model_native_context_limit=8192,
        backend_context_limit=8192,
        deployment_verified_context_limit=8192,
        max_output_token_limit=2048,
        current_max_new_tokens=2048,
        last_transition_receipt=None,
    )


class _FakeBackend:
    def __init__(self, *, fail_load_for: frozenset[str] = frozenset()) -> None:
        self.fail_load_for = fail_load_for
        self.unload_calls = 0
        self.load_calls: list[str] = []

    def probe_capability(self, *, definition: ModelDefinition) -> CapabilityProbeResult:
        return CapabilityProbeResult(
            native_context_limit=definition.model.native_context_limit,
            backend_context_limit=8192,
            deployment_verified_context_limit=8192,
            max_output_token_limit=2048,
            capability_digest=_SHA512_FILLER,
        )

    def load(self, *, definition: ModelDefinition, context_size: int) -> LoadedModelHandle:
        self.load_calls.append(definition.model_key)
        if definition.model_key in self.fail_load_for:
            raise RuntimeError(f"simulated load failure for {definition.model_key}")
        return LoadedModelHandle(
            backend_identity="llama_cpp",
            artifact_digest=_SHA512_FILLER,
            loaded_context_size=context_size,
            capability=self.probe_capability(definition=definition),
        )

    def unload(self) -> None:
        self.unload_calls += 1


class _FakeAccessLease:
    """P6-CODEX-034 (Fifth Rework): replaces the retired `_FakeBusyGate`
    (`has_active_generation` peek) — the real `ModelAccessCoordinator`
    exposes `try_acquire_switch_lease`/`release_switch_lease` directly, so
    the Fake mirrors that exact Port instead."""

    def __init__(self, *, busy: bool = False) -> None:
        self.busy = busy
        self.acquire_calls: list[str] = []
        self.release_calls: list[str] = []

    def try_acquire_switch_lease(self, *, task_id: str) -> bool:
        self.acquire_calls.append(task_id)
        return not self.busy

    def release_switch_lease(self, *, task_id: str) -> None:
        self.release_calls.append(task_id)


class _FakeDefinitionResolver:
    def __init__(self) -> None:
        self._definitions = {
            _QWEN_KEY: make_model_definition(model_key=_QWEN_KEY),
            _DEEPSEEK_KEY: make_model_definition(model_key=_DEEPSEEK_KEY),
        }

    def resolve(self, *, model_key: str) -> ModelDefinition:
        return self._definitions[model_key]

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return tuple(self._definitions.values())


def _make_controller(
    *, backend: _FakeBackend | None = None, busy: bool = False
) -> tuple[RuntimeModelController, _FakeBackend]:
    backend = backend or _FakeBackend()
    controller = RuntimeModelController(
        initial_snapshot=_initial_snapshot(),
        backend=backend,
        access_lease=_FakeAccessLease(busy=busy),
        definitions=_FakeDefinitionResolver(),
    )
    return controller, backend


def test_successful_switch_commits_new_revision_and_selected_model() -> None:
    controller, backend = _make_controller()
    initial = controller.snapshot()

    committed = controller.begin_switch(
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        transition_id="t-1",
        target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
        requested_context_size=8192,
    )

    assert committed.selected_model_key == _DEEPSEEK_KEY
    assert committed.revision == initial.revision + 1
    assert committed.runtime_state is RuntimeState.ACTIVE
    assert committed.last_transition_receipt is not None
    assert committed.last_transition_receipt.outcome.value == "committed"
    assert backend.unload_calls == 1
    assert backend.load_calls == [_DEEPSEEK_KEY]
    # P6-CODEX-035 (Fifth Rework): a successful Switch must carry exactly
    # one MAIN Role Binding for the new Target — never zero (the previous
    # implementation removed the old MAIN Binding but never added a new
    # one) and never a Binding still naming the old Model.
    main_bindings = [
        binding for binding in committed.role_bindings if binding.role is ModelRole.MAIN
    ]
    assert len(main_bindings) == 1
    assert main_bindings[0].model_identity == _DEEPSEEK_KEY
    assert main_bindings[0].artifact_digest == _SHA512_FILLER
    assert main_bindings[0].backend_identity == "llama_cpp"


def test_switch_preserves_a_non_main_role_binding_untouched() -> None:
    """P6-CODEX-035: a Judge/Guard Binding (a different Role) must survive
    a MAIN-only Switch unchanged — only the MAIN Binding is replaced."""
    judge_binding = RoleBinding(
        role=ModelRole.JUDGE,
        model_identity=_QWEN_KEY,
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=_SHA512_FILLER,
    )
    initial = _initial_snapshot().model_copy(
        update={"role_bindings": (*_initial_snapshot().role_bindings, judge_binding)}
    )
    controller = RuntimeModelController(
        initial_snapshot=initial,
        backend=_FakeBackend(),
        access_lease=_FakeAccessLease(),
        definitions=_FakeDefinitionResolver(),
    )

    committed = controller.begin_switch(
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        transition_id="t-preserve-judge",
        target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
        requested_context_size=8192,
    )

    judge_bindings = [b for b in committed.role_bindings if b.role is ModelRole.JUDGE]
    main_bindings = [b for b in committed.role_bindings if b.role is ModelRole.MAIN]
    assert judge_bindings == [judge_binding]
    assert len(main_bindings) == 1
    assert main_bindings[0].model_identity == _DEEPSEEK_KEY


def test_switch_clamps_max_new_tokens_to_the_target_models_own_ceiling() -> None:
    """P6-CODEX-035 (Fifth Rework): a Max New Tokens value valid for the
    Previous Model must never silently exceed the Target Model's own
    `max_output_token_limit` — the previous implementation carried the
    Previous value forward unconditionally, which could commit an
    internally-inconsistent Snapshot (current_max_new_tokens >
    max_output_token_limit)."""
    initial = _initial_snapshot().model_copy(update={"current_max_new_tokens": 2048})
    controller = RuntimeModelController(
        initial_snapshot=initial,
        backend=_FakeBackend(),
        access_lease=_FakeAccessLease(),
        definitions=_FakeDefinitionResolver(),
    )

    committed = controller.begin_switch(
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        transition_id="t-clamp",
        # _FakeBackend.probe_capability() always reports max_output_token_limit=2048;
        # override the Target's own ceiling lower to exercise the clamp.
        target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
        requested_context_size=8192,
    )

    # _FakeBackend's max_output_token_limit is 2048 (>= previous 2048), so
    # this asserts the no-op case; the dedicated low-ceiling backend below
    # asserts the actual clamp.
    assert committed.current_max_new_tokens == 2048

    class _LowCeilingBackend(_FakeBackend):
        def probe_capability(self, *, definition: ModelDefinition) -> CapabilityProbeResult:
            probed = super().probe_capability(definition=definition)
            return CapabilityProbeResult(
                native_context_limit=probed.native_context_limit,
                backend_context_limit=probed.backend_context_limit,
                deployment_verified_context_limit=probed.deployment_verified_context_limit,
                max_output_token_limit=256,
                capability_digest=probed.capability_digest,
            )

    low_ceiling_controller = RuntimeModelController(
        initial_snapshot=initial,
        backend=_LowCeilingBackend(),
        access_lease=_FakeAccessLease(),
        definitions=_FakeDefinitionResolver(),
    )
    clamped = low_ceiling_controller.begin_switch(
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        transition_id="t-clamp-2",
        target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
        requested_context_size=8192,
    )
    assert clamped.current_max_new_tokens == 256
    assert clamped.max_output_token_limit == 256


def test_switch_rejected_while_a_real_background_task_is_active_via_coordinator() -> None:
    """P6-CODEX-034 (Fifth Rework), the central Deterministic Test the
    Handoff requires: hold a real Background Call (via the real
    `ModelAccessCoordinator`, not a Fake) at a Barrier, attempt a Switch,
    and confirm it is rejected outright with zero Unload/Load/Snapshot
    Mutation — then confirm the identical Switch succeeds once the
    Background Call completes."""
    coordinator = ModelAccessCoordinator()
    backend = _FakeBackend()
    controller = RuntimeModelController(
        initial_snapshot=_initial_snapshot(),
        backend=backend,
        access_lease=coordinator,
        definitions=_FakeDefinitionResolver(),
    )
    background_entered = threading.Event()
    release_background = threading.Event()

    def _held_background_task() -> None:
        background_entered.set()
        release_background.wait(timeout=5.0)

    started = coordinator.start_background(task_id="bg-race", target=_held_background_task)
    assert started
    assert background_entered.wait(timeout=2.0)

    initial = controller.snapshot()
    with pytest.raises(RuntimeModelBusyError):
        controller.begin_switch(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="t-race-1",
            target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
            requested_context_size=8192,
        )
    assert backend.unload_calls == 0
    assert backend.load_calls == []
    assert controller.snapshot() == initial

    release_background.set()
    deadline = time.monotonic() + 2.0
    while coordinator.current_background_task_id() is not None and time.monotonic() < deadline:
        time.sleep(0.005)
    assert coordinator.current_background_task_id() is None

    committed = controller.begin_switch(
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        transition_id="t-race-2",
        target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
        requested_context_size=8192,
    )
    assert committed.selected_model_key == _DEEPSEEK_KEY
    assert backend.unload_calls == 1
    assert backend.load_calls == [_DEEPSEEK_KEY]


def test_available_models_lists_every_registered_key() -> None:
    """P6-CODEX-026 (Fourth Rework): the Runtime Switch surface reads real
    registered Definitions, never a hardcoded model list."""
    controller, _ = _make_controller()

    available_keys = {definition.model_key for definition in controller.available_models()}

    assert available_keys == {_QWEN_KEY, _DEEPSEEK_KEY}


def test_switch_to_model_key_resolves_and_commits_the_named_target() -> None:
    controller, backend = _make_controller()
    initial = controller.snapshot()

    committed = controller.switch_to_model_key(
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        transition_id="t-switch-1",
        target_model_key=_DEEPSEEK_KEY,
        requested_context_size=8192,
    )

    assert committed.selected_model_key == _DEEPSEEK_KEY
    assert backend.load_calls == [_DEEPSEEK_KEY]


def test_switch_to_model_key_rejects_an_unregistered_target() -> None:
    """The exact P6-CODEX-026 fail-closed boundary: never attempt a Load for
    a `target_model_key` that has no registered Definition."""
    controller, backend = _make_controller()
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelTargetNotRegistered) as excinfo:
        controller.switch_to_model_key(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="t-switch-2",
            target_model_key="main.does-not-exist",
            requested_context_size=8192,
        )

    assert excinfo.value.target_model_key == "main.does-not-exist"
    assert backend.load_calls == []
    assert backend.unload_calls == 0
    assert controller.snapshot().selected_model_key == _QWEN_KEY


def test_stale_expected_revision_is_rejected_as_a_cas_conflict() -> None:
    controller, _ = _make_controller()
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelRevisionConflict) as excinfo:
        controller.begin_switch(
            expected_revision=initial.revision + 5,
            expected_digest=initial.digest_sha512,
            transition_id="t-stale",
            target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
            requested_context_size=8192,
        )
    assert excinfo.value.current_revision == initial.revision


def test_stale_expected_digest_is_rejected_even_with_correct_revision() -> None:
    controller, _ = _make_controller()
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelRevisionConflict):
        controller.begin_switch(
            expected_revision=initial.revision,
            expected_digest="0" * 128,
            transition_id="t-stale-digest",
            target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
            requested_context_size=8192,
        )


def test_switch_is_rejected_while_a_generation_is_active_idle_only_gate() -> None:
    controller, backend = _make_controller(busy=True)
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelBusyError):
        controller.begin_switch(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="t-busy",
            target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
            requested_context_size=8192,
        )
    assert backend.unload_calls == 0
    assert backend.load_calls == []
    assert controller.snapshot() == initial


def test_load_failure_rolls_back_to_previous_model_and_raises_load_failure() -> None:
    backend = _FakeBackend(fail_load_for=frozenset({_DEEPSEEK_KEY}))
    controller, _ = _make_controller(backend=backend)
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelLoadFailure):
        controller.begin_switch(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="t-fail",
            target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
            requested_context_size=8192,
        )

    rolled_back = controller.snapshot()
    assert rolled_back.selected_model_key == _QWEN_KEY
    assert rolled_back.runtime_state is RuntimeState.ACTIVE
    assert rolled_back.revision == initial.revision + 1
    assert rolled_back.last_transition_receipt is not None
    assert rolled_back.last_transition_receipt.outcome.value == "rolled_back"
    assert backend.load_calls == [_DEEPSEEK_KEY, _QWEN_KEY]


def test_double_failure_leaves_runtime_unavailable_not_a_guessed_previous_value() -> None:
    backend = _FakeBackend(fail_load_for=frozenset({_DEEPSEEK_KEY, _QWEN_KEY}))
    controller, _ = _make_controller(backend=backend)
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelRollbackFailure):
        controller.begin_switch(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="t-double-fail",
            target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
            requested_context_size=8192,
        )

    unavailable = controller.snapshot()
    assert unavailable.runtime_state is RuntimeState.UNAVAILABLE
    assert unavailable.loaded_context_size == 0
    assert unavailable.revision == initial.revision + 1
    assert unavailable.last_transition_receipt is not None
    assert unavailable.last_transition_receipt.outcome.value == "failed_unavailable"


def test_on_commit_fires_with_the_committed_snapshot_after_a_successful_switch() -> None:
    """P6-CODEX-036 (Fifth Rework): `on_commit` is the hook a dependent
    Composition (e.g. Runtime Governance) uses to rebind itself to the
    Model a Switch actually committed — it must fire exactly once, after
    `self._lock` has been released (never while still held), with the
    real committed Snapshot."""
    observed: list[RuntimeModelSnapshot] = []
    controller = RuntimeModelController(
        initial_snapshot=_initial_snapshot(),
        backend=_FakeBackend(),
        access_lease=_FakeAccessLease(),
        definitions=_FakeDefinitionResolver(),
        on_commit=observed.append,
    )
    initial = controller.snapshot()

    committed = controller.begin_switch(
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        transition_id="t-on-commit",
        target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
        requested_context_size=8192,
    )

    assert observed == [committed]


def test_on_commit_does_not_fire_on_load_failure_rollback() -> None:
    """P6-CODEX-036: a Rollback is not a commit — a dependent Composition
    must never be notified of a Switch that did not actually succeed,
    which would otherwise rebind Governance to a Model that was never
    actually loaded."""
    observed: list[RuntimeModelSnapshot] = []
    backend = _FakeBackend(fail_load_for=frozenset({_DEEPSEEK_KEY}))
    controller = RuntimeModelController(
        initial_snapshot=_initial_snapshot(),
        backend=backend,
        access_lease=_FakeAccessLease(),
        definitions=_FakeDefinitionResolver(),
        on_commit=observed.append,
    )
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelLoadFailure):
        controller.begin_switch(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="t-on-commit-rollback",
            target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
            requested_context_size=8192,
        )

    assert observed == []


def test_on_commit_does_not_fire_when_the_switch_lease_is_denied() -> None:
    """P6-CODEX-036/034: a busy-rejected Switch attempts zero Unload/Load
    and must never notify a dependent Composition either."""
    observed: list[RuntimeModelSnapshot] = []
    controller = RuntimeModelController(
        initial_snapshot=_initial_snapshot(),
        backend=_FakeBackend(),
        access_lease=_FakeAccessLease(busy=True),
        definitions=_FakeDefinitionResolver(),
        on_commit=observed.append,
    )
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelBusyError):
        controller.begin_switch(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="t-on-commit-busy",
            target_definition=make_model_definition(model_key=_DEEPSEEK_KEY),
            requested_context_size=8192,
        )

    assert observed == []
