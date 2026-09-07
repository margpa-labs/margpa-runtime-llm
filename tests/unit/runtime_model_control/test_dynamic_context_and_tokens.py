import pytest

from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.errors import (
    RuntimeModelContextLimitExceeded,
    RuntimeModelMaxNewTokensExceeded,
    RuntimeModelRevisionConflict,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import RuntimeState

from .test_runtime_model_controller import (
    _QWEN_KEY,
    _FakeAccessLease,
    _FakeBackend,
    _FakeDefinitionResolver,
    _initial_snapshot,
    _make_controller,
)


def test_context_change_reloads_the_same_model_at_the_new_size() -> None:
    controller, backend = _make_controller()
    initial = controller.snapshot()

    updated = controller.request_context_change(
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        transition_id="ctx-1",
        requested_context_size=8192,
    )

    assert updated.selected_model_key == _QWEN_KEY
    assert updated.loaded_context_size == 8192
    assert updated.revision == initial.revision + 1
    assert backend.load_calls == [_QWEN_KEY]
    assert backend.unload_calls == 1


def test_context_change_above_effective_max_is_rejected_without_touching_the_backend() -> None:
    controller, backend = _make_controller()
    initial = controller.snapshot()
    effective_max = initial.effective_context_limit

    with pytest.raises(RuntimeModelContextLimitExceeded) as excinfo:
        controller.request_context_change(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="ctx-too-big",
            requested_context_size=effective_max + 1,
        )

    assert excinfo.value.effective_max_context_size == effective_max
    assert backend.load_calls == []
    assert backend.unload_calls == 0
    assert controller.snapshot() == initial


def test_context_change_at_effective_max_minus_one_and_minimum_succeeds() -> None:
    for requested in (8191, 512):
        controller, backend = _make_controller()
        initial = controller.snapshot()

        updated = controller.request_context_change(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id=f"ctx-boundary-{requested}",
            requested_context_size=requested,
        )

        assert updated.loaded_context_size == requested
        assert backend.unload_calls == 1


def test_context_change_below_minimum_is_rejected_without_backend_mutation() -> None:
    controller, backend = _make_controller()
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelContextLimitExceeded) as excinfo:
        controller.request_context_change(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="ctx-below-minimum",
            requested_context_size=511,
        )

    assert excinfo.value.minimum_context_size == 512
    assert backend.load_calls == []
    assert backend.unload_calls == 0
    assert controller.snapshot() == initial


def test_context_change_reload_failure_does_not_adopt_the_requested_size_as_current() -> None:
    backend = _FakeBackend(fail_load_for=frozenset({_QWEN_KEY}))
    controller, _ = _make_controller(backend=backend)
    initial = controller.snapshot()

    with pytest.raises(Exception):  # noqa: B017 - RuntimeModelRollbackFailure: same model fails both times
        controller.request_context_change(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            transition_id="ctx-fail",
            requested_context_size=8192,
        )

    after = controller.snapshot()
    assert after.runtime_state is RuntimeState.UNAVAILABLE
    assert after.loaded_context_size != 8192


def test_set_max_new_tokens_is_atomic_and_requires_no_reload() -> None:
    controller, backend = _make_controller()
    initial = controller.snapshot()

    updated = controller.set_max_new_tokens(
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        requested_max_new_tokens=1024,
    )

    assert updated.current_max_new_tokens == 1024
    assert updated.revision == initial.revision + 1
    assert updated.selected_model_key == initial.selected_model_key
    assert backend.load_calls == []
    assert backend.unload_calls == 0


def test_set_max_new_tokens_above_limit_is_rejected() -> None:
    controller, _ = _make_controller()
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelMaxNewTokensExceeded) as excinfo:
        controller.set_max_new_tokens(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            requested_max_new_tokens=initial.max_output_token_limit + 1,
        )

    assert excinfo.value.max_output_token_limit == initial.max_output_token_limit
    assert controller.snapshot() == initial


def test_set_max_new_tokens_accepts_minimum_and_effective_maximum() -> None:
    for requested in (1, 8191):
        controller, backend = _make_controller()
        initial = controller.snapshot()

        updated = controller.set_max_new_tokens(
            expected_revision=initial.revision,
            expected_digest=initial.digest_sha512,
            requested_max_new_tokens=requested,
        )

        assert updated.current_max_new_tokens == requested
        assert backend.load_calls == []
        assert backend.unload_calls == 0


def test_set_max_new_tokens_accepts_8192_and_rejects_8193_at_the_real_package_3_ceiling() -> None:
    """P9-1 Package 3 (P3-WU-04): pins the literal real-deployment boundary
    (Maximum max_new_tokens 8192) the generic `+1`/`-1`-relative tests above
    already exercise for arbitrary Fixture numbers -- this Test fixes the
    Fixture's own `max_output_token_limit` to the real Package 3 value
    (8192) so the boundary itself, not just the mechanism, is pinned."""
    snapshot = _initial_snapshot().model_copy(
        update={"max_output_token_limit": 8192, "current_max_new_tokens": 4096}
    )
    controller = RuntimeModelController(
        initial_snapshot=snapshot,
        backend=_FakeBackend(),
        access_lease=_FakeAccessLease(),
        definitions=_FakeDefinitionResolver(),
    )
    initial = controller.snapshot()

    accepted = controller.set_max_new_tokens(
        expected_revision=initial.revision,
        expected_digest=initial.digest_sha512,
        requested_max_new_tokens=8192,
    )
    assert accepted.current_max_new_tokens == 8192

    with pytest.raises(RuntimeModelMaxNewTokensExceeded) as excinfo:
        controller.set_max_new_tokens(
            expected_revision=accepted.revision,
            expected_digest=accepted.digest_sha512,
            requested_max_new_tokens=8193,
        )
    assert excinfo.value.max_output_token_limit == 8192
    assert excinfo.value.requested_max_new_tokens == 8193


def test_set_max_new_tokens_with_stale_cas_is_rejected() -> None:
    controller, _ = _make_controller()
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelRevisionConflict):
        controller.set_max_new_tokens(
            expected_revision=initial.revision + 1,
            expected_digest=initial.digest_sha512,
            requested_max_new_tokens=1024,
        )
