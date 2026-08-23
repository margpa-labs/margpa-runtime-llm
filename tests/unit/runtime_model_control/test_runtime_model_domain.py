import pydantic
import pytest

from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    BindingState,
    IndependenceClass,
    ModelRole,
    RuntimeState,
    SwitchOutcome,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.snapshot import (
    RoleBinding,
    RuntimeModelSnapshot,
    TransitionReceipt,
    compute_runtime_model_snapshot_digest,
)

_SHA512_FILLER = "b" * 128


def _role_binding(role: ModelRole = ModelRole.MAIN) -> RoleBinding:
    return RoleBinding(
        role=role,
        model_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=_SHA512_FILLER,
    )


def _snapshot(revision: int = 0) -> RuntimeModelSnapshot:
    digest = compute_runtime_model_snapshot_digest(
        revision=revision,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=(_role_binding(),),
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=8192,
        current_max_new_tokens=2048,
    )
    return RuntimeModelSnapshot(
        revision=revision,
        digest_sha512=digest,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=(_role_binding(),),
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=8192,
        model_native_context_limit=8192,
        backend_context_limit=8192,
        deployment_verified_context_limit=8192,
        max_output_token_limit=2048,
        current_max_new_tokens=2048,
        last_transition_receipt=None,
    )


def test_snapshot_is_frozen_and_rejects_unknown_fields() -> None:
    snapshot = _snapshot()
    with pytest.raises(pydantic.ValidationError):
        snapshot.model_validate({**snapshot.model_dump(), "unexpected_field": "x"})
    with pytest.raises(pydantic.ValidationError):
        snapshot.revision = 99


def test_digest_is_stable_for_identical_identity_fields() -> None:
    first = compute_runtime_model_snapshot_digest(
        revision=1,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=(_role_binding(),),
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=8192,
        current_max_new_tokens=2048,
    )
    second = compute_runtime_model_snapshot_digest(
        revision=1,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=(_role_binding(),),
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=8192,
        current_max_new_tokens=2048,
    )
    assert first == second


def test_digest_changes_when_selected_model_key_changes() -> None:
    base = compute_runtime_model_snapshot_digest(
        revision=1,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=(_role_binding(),),
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=8192,
        current_max_new_tokens=2048,
    )
    changed = compute_runtime_model_snapshot_digest(
        revision=1,
        selected_model_key="main.deepseek-r1-0528-qwen3-8b-q4-k-m",
        role_bindings=(_role_binding(),),
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=8192,
        current_max_new_tokens=2048,
    )
    assert base != changed


def test_role_binding_rejects_malformed_digest() -> None:
    with pytest.raises(pydantic.ValidationError):
        RoleBinding(
            role=ModelRole.JUDGE,
            model_identity="x",
            artifact_digest="not-a-sha512",
            backend_identity="llama_cpp",
            binding_state=BindingState.BOUND,
            independence_class=IndependenceClass.INDEPENDENT_ARTIFACT,
            capability_digest=_SHA512_FILLER,
        )


def test_shared_artifact_judge_binding_reports_low_independence() -> None:
    binding = RoleBinding(
        role=ModelRole.JUDGE,
        model_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=_SHA512_FILLER,
    )
    assert binding.independence_class is IndependenceClass.SHARED_ARTIFACT


def test_transition_receipt_records_outcome_and_optional_failure_reason() -> None:
    receipt = TransitionReceipt(
        transition_id="t-1",
        from_revision=0,
        to_model_key="main.deepseek-r1-0528-qwen3-8b-q4-k-m",
        outcome=SwitchOutcome.ROLLED_BACK,
        started_at="2026-08-22T00:00:00+00:00",
        completed_at="2026-08-22T00:00:01+00:00",
        failure_reason="load failed: OOM",
    )
    assert receipt.outcome is SwitchOutcome.ROLLED_BACK
    assert receipt.failure_reason == "load failed: OOM"
