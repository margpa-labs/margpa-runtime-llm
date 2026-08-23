import pytest

from margpa_runtime_llm.modules.runtime_model_control.domain.errors import (
    RuntimeModelContextLimitExceeded,
    RuntimeModelMaxNewTokensExceeded,
    RuntimeModelRevisionConflict,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import RuntimeState

from .test_runtime_model_controller import _QWEN_KEY, _FakeBackend, _make_controller


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
    effective_max = min(initial.model_native_context_limit, initial.backend_context_limit)

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


def test_set_max_new_tokens_with_stale_cas_is_rejected() -> None:
    controller, _ = _make_controller()
    initial = controller.snapshot()

    with pytest.raises(RuntimeModelRevisionConflict):
        controller.set_max_new_tokens(
            expected_revision=initial.revision + 1,
            expected_digest=initial.digest_sha512,
            requested_max_new_tokens=1024,
        )
