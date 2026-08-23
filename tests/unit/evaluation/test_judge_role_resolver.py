from margpa_runtime_llm.modules.evaluation.application.judge_role_resolver import (
    resolve_judge_independence,
)
from margpa_runtime_llm.modules.evaluation.domain.llm_judge import JudgeIndependenceClass
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

_SHA512_A = "a" * 128
_SHA512_B = "b" * 128


def _main_binding(*, artifact_digest: str = _SHA512_A) -> RoleBinding:
    return RoleBinding(
        role=ModelRole.MAIN,
        model_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=artifact_digest,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=_SHA512_A,
    )


def _snapshot(*, role_bindings: tuple[RoleBinding, ...]) -> RuntimeModelSnapshot:
    digest = compute_runtime_model_snapshot_digest(
        revision=0,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=role_bindings,
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_A,
        backend_identity="llama_cpp",
        runtime_state=RuntimeState.ACTIVE,
        loaded_context_size=4096,
        current_max_new_tokens=2048,
    )
    return RuntimeModelSnapshot(
        revision=0,
        digest_sha512=digest,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=role_bindings,
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_A,
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


def test_no_judge_binding_is_unavailable_not_fabricated() -> None:
    snapshot = _snapshot(role_bindings=(_main_binding(),))
    assert resolve_judge_independence(snapshot=snapshot) is JudgeIndependenceClass.UNAVAILABLE


def test_unbound_judge_is_unavailable() -> None:
    judge_binding = RoleBinding(
        role=ModelRole.JUDGE,
        model_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_A,
        backend_identity="llama_cpp",
        binding_state=BindingState.UNAVAILABLE,
        independence_class=IndependenceClass.UNAVAILABLE,
        capability_digest=_SHA512_A,
    )
    snapshot = _snapshot(role_bindings=(_main_binding(), judge_binding))
    assert resolve_judge_independence(snapshot=snapshot) is JudgeIndependenceClass.UNAVAILABLE


def test_same_artifact_as_main_is_main_self_not_independent() -> None:
    judge_binding = RoleBinding(
        role=ModelRole.JUDGE,
        model_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_A,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.INDEPENDENT_ARTIFACT,
        capability_digest=_SHA512_A,
    )
    snapshot = _snapshot(role_bindings=(_main_binding(artifact_digest=_SHA512_A), judge_binding))
    assert resolve_judge_independence(snapshot=snapshot) is JudgeIndependenceClass.MAIN_SELF


def test_different_artifact_marked_independent_is_reported_independent() -> None:
    judge_binding = RoleBinding(
        role=ModelRole.JUDGE,
        model_identity="main.deepseek-r1-0528-qwen3-8b-q4-k-m",
        artifact_digest=_SHA512_B,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.INDEPENDENT_ARTIFACT,
        capability_digest=_SHA512_B,
    )
    snapshot = _snapshot(role_bindings=(_main_binding(artifact_digest=_SHA512_A), judge_binding))
    assert (
        resolve_judge_independence(snapshot=snapshot) is JudgeIndependenceClass.INDEPENDENT_ARTIFACT
    )


def test_different_role_binding_same_underlying_artifact_is_shared_not_independent() -> None:
    judge_binding = RoleBinding(
        role=ModelRole.JUDGE,
        model_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_A,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=_SHA512_A,
    )
    # Different artifact digest from Main so it is not MAIN_SELF, but the
    # binding itself declares SHARED_ARTIFACT (e.g. a second load of the
    # same weights under a different role) rather than INDEPENDENT_ARTIFACT.
    snapshot = _snapshot(role_bindings=(_main_binding(artifact_digest=_SHA512_B), judge_binding))
    assert resolve_judge_independence(snapshot=snapshot) is JudgeIndependenceClass.SHARED_ARTIFACT
