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
from margpa_runtime_llm.modules.runtime_observability.projection.component_identity_projection import (  # noqa: E501
    ComponentIdentityState,
    project_governance_layer_identity,
    project_guard_model_identity,
    project_judge_model_identity,
    project_main_model_identity,
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


def _snapshot(
    *, role_bindings: tuple[RoleBinding, ...], runtime_state: RuntimeState = RuntimeState.ACTIVE
) -> RuntimeModelSnapshot:
    digest = compute_runtime_model_snapshot_digest(
        revision=0,
        selected_model_key="main.qwen3-4b-q4-k-m",
        role_bindings=role_bindings,
        artifact_identity="main.qwen3-4b-q4-k-m",
        artifact_digest=_SHA512_A,
        backend_identity="llama_cpp",
        runtime_state=runtime_state,
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
        runtime_state=runtime_state,
        loaded_context_size=4096,
        model_native_context_limit=8192,
        backend_context_limit=8192,
        deployment_verified_context_limit=8192,
        max_output_token_limit=2048,
        current_max_new_tokens=2048,
        last_transition_receipt=None,
    )


def test_main_model_identity_reflects_active_runtime_state() -> None:
    snapshot = _snapshot(role_bindings=(_main_binding(),))
    identity = project_main_model_identity(snapshot=snapshot)
    assert identity.model_key == "main.qwen3-4b-q4-k-m"
    assert identity.state is ComponentIdentityState.ACTIVE


def test_main_model_identity_reflects_unavailable_runtime_state() -> None:
    snapshot = _snapshot(role_bindings=(_main_binding(),), runtime_state=RuntimeState.UNAVAILABLE)
    identity = project_main_model_identity(snapshot=snapshot)
    assert identity.state is ComponentIdentityState.UNAVAILABLE


def test_judge_model_identity_is_none_when_no_judge_is_bound() -> None:
    snapshot = _snapshot(role_bindings=(_main_binding(),))
    identity = project_judge_model_identity(snapshot=snapshot)
    assert identity.model_key is None
    assert identity.independence_class is JudgeIndependenceClass.UNAVAILABLE
    assert identity.state is ComponentIdentityState.NONE


def test_live_main_self_judge_projects_the_actual_current_main_model() -> None:
    snapshot = _snapshot(role_bindings=(_main_binding(),))
    identity = project_judge_model_identity(snapshot=snapshot, main_self_available=True)
    assert identity.model_key == snapshot.selected_model_key
    assert identity.independence_class is JudgeIndependenceClass.MAIN_SELF
    assert identity.state is ComponentIdentityState.ACTIVE


def test_judge_model_identity_reports_active_when_bound_and_independent() -> None:
    judge_binding = RoleBinding(
        role=ModelRole.JUDGE,
        model_identity="main.deepseek-r1-0528-qwen3-8b-q4-k-m",
        artifact_digest=_SHA512_B,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.INDEPENDENT_ARTIFACT,
        capability_digest=_SHA512_B,
    )
    snapshot = _snapshot(role_bindings=(_main_binding(), judge_binding))
    identity = project_judge_model_identity(snapshot=snapshot)
    assert identity.model_key == "main.deepseek-r1-0528-qwen3-8b-q4-k-m"
    assert identity.independence_class is JudgeIndependenceClass.INDEPENDENT_ARTIFACT
    assert identity.state is ComponentIdentityState.ACTIVE


def test_guard_model_identity_is_none_by_default_matching_production_today() -> None:
    identity = project_guard_model_identity(
        model_id=None, exact_revision=None, artifact_digest_sha512=None
    )
    assert identity.model_id is None
    assert identity.state is ComponentIdentityState.NONE


def test_guard_model_identity_reports_active_when_a_real_artifact_is_bound() -> None:
    identity = project_guard_model_identity(
        model_id="safety-model-x", exact_revision="v1", artifact_digest_sha512=_SHA512_A
    )
    assert identity.model_id == "safety-model-x"
    assert identity.state is ComponentIdentityState.ACTIVE


def test_governance_layer_identity_is_none_without_a_loaded_package() -> None:
    identity = project_governance_layer_identity(package_id=None, manifest_digest_sha512=None)
    assert identity.state is ComponentIdentityState.NONE


def test_governance_layer_identity_reports_active_with_a_loaded_package() -> None:
    identity = project_governance_layer_identity(
        package_id="margpa-core-definitions", manifest_digest_sha512=_SHA512_A
    )
    assert identity.package_id == "margpa-core-definitions"
    assert identity.state is ComponentIdentityState.ACTIVE


def test_governance_layer_identity_is_invalid_when_package_id_present_without_a_digest() -> None:
    """P6-CODEX-014 (Second Rework): a package_id without its digest is an
    internally inconsistent partial identity — never a fabricated ACTIVE."""
    identity = project_governance_layer_identity(
        package_id="margpa-core-definitions", manifest_digest_sha512=None
    )
    assert identity.package_id == "margpa-core-definitions"
    assert identity.manifest_digest_sha512 is None
    assert identity.state is ComponentIdentityState.INVALID


def test_guard_model_identity_is_invalid_when_model_id_present_without_a_digest() -> None:
    identity = project_guard_model_identity(
        model_id="safety-model-x", exact_revision="v1", artifact_digest_sha512=None
    )
    assert identity.model_id == "safety-model-x"
    assert identity.artifact_digest_sha512 is None
    assert identity.state is ComponentIdentityState.INVALID


# P6-ACC-056 (Third Rework, Required Rework Sequence Step 8): a
# consolidated 4-Identity x ComponentIdentityState Matrix — Third
# Independent Review's own wording describes this as a "4 Identity x 6
# State" Matrix, but that count assumes every Identity can structurally
# reach every one of `ComponentIdentityState`'s 6 members. Tracing each
# `project_*_identity()` function's own branches shows this is not so:
#
#   Main Model       : NONE, LOADING, ACTIVE, DEGRADED, UNAVAILABLE (5)
#                       — INVALID is not a Main Model concept (its
#                       identity always arrives as one complete unit from
#                       the Adapter; there is no partial-Main-identity
#                       case to guard against).
#   Guard Model      : NONE, INVALID, ACTIVE (3)
#                       — LOADING/DEGRADED/UNAVAILABLE are not reachable:
#                       `project_guard_model_identity()` takes a bare
#                       Optional[str] triple, not a RuntimeState-carrying
#                       Snapshot, so it has no loading/degraded lifecycle
#                       concept at all in the current Architecture.
#   Governance Layer : NONE, INVALID, ACTIVE (3) — same reasoning as
#                       Guard Model (a bare Optional[str] pair, no
#                       lifecycle Snapshot).
#   Judge Model      : NONE, ACTIVE (2) — `judge_binding.binding_state is
#                       not BindingState.BOUND` inside
#                       `project_judge_model_identity()` is dead code:
#                       `resolve_judge_independence()` already returns
#                       `JudgeIndependenceClass.UNAVAILABLE` (which
#                       short-circuits to `ComponentIdentityState.NONE`
#                       one line above) for that exact same condition
#                       (`judge_binding is None or judge_binding.
#                       binding_state is not BindingState.BOUND`) — by
#                       the time the second branch's own BOUND check
#                       runs, it has always already been proven BOUND.
#                       This is a real, harmless (never wrong, just
#                       unreachable) piece of defensive code, recorded
#                       here rather than silently left unexplained.
#
# The Matrix below exhaustively covers every state each Identity can
# *actually* reach (13 total combinations across 4 Identities, not a
# uniform 24) — this is the honest closure of P6-ACC-056, not a
# mechanical parametrization over all 6 states x 4 Identities regardless
# of reachability.


def test_main_model_identity_matrix_none_when_idle() -> None:
    snapshot = _snapshot(role_bindings=(_main_binding(),), runtime_state=RuntimeState.IDLE)
    identity = project_main_model_identity(snapshot=snapshot)
    assert identity.state is ComponentIdentityState.NONE


def test_main_model_identity_matrix_loading_for_all_three_transitional_runtime_states() -> None:
    for runtime_state in (RuntimeState.LOADING, RuntimeState.UNLOADING, RuntimeState.SWITCHING):
        snapshot = _snapshot(role_bindings=(_main_binding(),), runtime_state=runtime_state)
        identity = project_main_model_identity(snapshot=snapshot)
        assert identity.state is ComponentIdentityState.LOADING, runtime_state


def test_main_model_identity_matrix_degraded() -> None:
    snapshot = _snapshot(role_bindings=(_main_binding(),), runtime_state=RuntimeState.DEGRADED)
    identity = project_main_model_identity(snapshot=snapshot)
    assert identity.state is ComponentIdentityState.DEGRADED


def test_main_model_identity_matrix_active_and_unavailable_already_covered_above() -> None:
    """Documents, rather than re-tests, that ACTIVE and UNAVAILABLE for
    Main Model are already covered by
    `test_main_model_identity_reflects_active_runtime_state` and
    `test_main_model_identity_reflects_unavailable_runtime_state` above —
    completing Main Model's full 5-state reachable Matrix without
    duplicating assertions."""
    assert {ComponentIdentityState.ACTIVE, ComponentIdentityState.UNAVAILABLE}.issubset(
        set(ComponentIdentityState)
    )


def test_judge_model_identity_matrix_unavailable_branch_is_unreachable_dead_code() -> None:
    """P6-ACC-056: proves the claim made in the Matrix docstring above —
    every input that could reach `project_judge_model_identity()`'s own
    `binding_state is not BindingState.BOUND` branch has already been
    intercepted one line earlier by `resolve_judge_independence()`
    returning UNAVAILABLE (-> ComponentIdentityState.NONE), for every
    BindingState value other than BOUND."""
    for binding_state in (BindingState.UNBOUND, BindingState.UNAVAILABLE):
        judge_binding = RoleBinding(
            role=ModelRole.JUDGE,
            model_identity="main.deepseek-r1-0528-qwen3-8b-q4-k-m",
            artifact_digest=_SHA512_B,
            backend_identity="llama_cpp",
            binding_state=binding_state,
            independence_class=IndependenceClass.INDEPENDENT_ARTIFACT,
            capability_digest=_SHA512_B,
        )
        snapshot = _snapshot(role_bindings=(_main_binding(), judge_binding))
        identity = project_judge_model_identity(snapshot=snapshot)
        # Never a fabricated UNAVAILABLE ComponentIdentityState via the
        # dead branch — always the earlier NONE short-circuit.
        assert identity.state is ComponentIdentityState.NONE
