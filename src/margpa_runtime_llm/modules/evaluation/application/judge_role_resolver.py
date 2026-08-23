"""Role-separated Judge availability/independence projection (Phase 6-D-WU-002).

Bridges runtime_model_control's RuntimeModelSnapshot (Architecture 3.3 Role
Binding) into the Evaluation domain's JudgeIndependenceClass, without
fabricating Current/Available when no dedicated Judge is bound
(Acceptance P6-ACC-020, P6-ACC-024A).
"""

from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    BindingState,
    IndependenceClass,
    ModelRole,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.snapshot import RuntimeModelSnapshot

from ..domain.llm_judge import JudgeIndependenceClass


def resolve_judge_independence(*, snapshot: RuntimeModelSnapshot) -> JudgeIndependenceClass:
    judge_binding = next(
        (binding for binding in snapshot.role_bindings if binding.role is ModelRole.JUDGE),
        None,
    )
    if judge_binding is None or judge_binding.binding_state is not BindingState.BOUND:
        return JudgeIndependenceClass.UNAVAILABLE

    main_binding = next(
        (binding for binding in snapshot.role_bindings if binding.role is ModelRole.MAIN),
        None,
    )
    if main_binding is not None and judge_binding.artifact_digest == main_binding.artifact_digest:
        return JudgeIndependenceClass.MAIN_SELF

    if judge_binding.independence_class is IndependenceClass.INDEPENDENT_ARTIFACT:
        return JudgeIndependenceClass.INDEPENDENT_ARTIFACT

    return JudgeIndependenceClass.SHARED_ARTIFACT
