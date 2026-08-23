"""Advanced Component Identity Projection (Architecture 11.1, Phase 6-G-WU-002).

Guard Model Identity and Governance Layer Identity take already-resolved
values rather than reaching into guardrail_governance/governance_definitions
themselves: as of Phase 5, Production's default SafetyModelPort adapter is
`UnavailableSafetyModelAdapter` (no Artifact bound), so the honest current
projection is `model_id=None` (Acceptance P6-ACC-024A: never fabricate
Current/Available). Guard Model state is intentionally independent of
Guardrail Mode (off/observe/enforce) — ENFORCE with zero bound Guard Model
is a valid, common combination here since detection is deterministic/
pattern-based today (Acceptance P6-ACC-054: never conflate the two).
Governance Layer Identity is the Definition Package's own identity
(`package_id`/`manifest_digest_sha512` from governance_definitions'
PackageManifest), not GovernanceModeSnapshot's mode-only digest.
"""

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    BindingState,
    ModelRole,
    RuntimeState,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.snapshot import RuntimeModelSnapshot

from ...evaluation.application.judge_role_resolver import resolve_judge_independence
from ...evaluation.domain.llm_judge import JudgeIndependenceClass


class ComponentIdentityState(StrEnum):
    NONE = "none"
    UNAVAILABLE = "unavailable"
    INVALID = "invalid"
    LOADING = "loading"
    DEGRADED = "degraded"
    ACTIVE = "active"


_RUNTIME_STATE_TO_IDENTITY_STATE: dict[RuntimeState, ComponentIdentityState] = {
    RuntimeState.IDLE: ComponentIdentityState.NONE,
    RuntimeState.LOADING: ComponentIdentityState.LOADING,
    RuntimeState.ACTIVE: ComponentIdentityState.ACTIVE,
    RuntimeState.UNLOADING: ComponentIdentityState.LOADING,
    RuntimeState.SWITCHING: ComponentIdentityState.LOADING,
    RuntimeState.DEGRADED: ComponentIdentityState.DEGRADED,
    RuntimeState.UNAVAILABLE: ComponentIdentityState.UNAVAILABLE,
}


class MainModelIdentity(ImmutableContract):
    model_key: str = Field(min_length=1)
    artifact_digest: str = Field(min_length=1)
    backend_identity: str = Field(min_length=1)
    state: ComponentIdentityState


class JudgeModelIdentity(ImmutableContract):
    model_key: str | None
    independence_class: JudgeIndependenceClass
    state: ComponentIdentityState


def project_main_model_identity(*, snapshot: RuntimeModelSnapshot) -> MainModelIdentity:
    return MainModelIdentity(
        model_key=snapshot.selected_model_key,
        artifact_digest=snapshot.artifact_digest,
        backend_identity=snapshot.backend_identity,
        state=_RUNTIME_STATE_TO_IDENTITY_STATE[snapshot.runtime_state],
    )


class GuardModelIdentity(ImmutableContract):
    model_id: str | None
    exact_revision: str | None
    artifact_digest_sha512: str | None
    state: ComponentIdentityState


class GovernanceLayerIdentity(ImmutableContract):
    package_id: str | None
    manifest_digest_sha512: str | None
    state: ComponentIdentityState


def project_guard_model_identity(
    *,
    model_id: str | None,
    exact_revision: str | None,
    artifact_digest_sha512: str | None,
) -> GuardModelIdentity:
    """`model_id=None` is the honest current default (no bound Safety Model
    Artifact). P6-CODEX-014 (Second Rework): `model_id` present without its
    `artifact_digest_sha512` is an internally inconsistent partial identity
    — never presented as a fully `ACTIVE`, verified binding — reported as
    `INVALID` instead (None/Unavailable/Invalid/Loading/Degraded/Active
    State Matrix)."""
    if model_id is None:
        return GuardModelIdentity(
            model_id=None,
            exact_revision=None,
            artifact_digest_sha512=None,
            state=ComponentIdentityState.NONE,
        )
    if artifact_digest_sha512 is None:
        return GuardModelIdentity(
            model_id=model_id,
            exact_revision=exact_revision,
            artifact_digest_sha512=None,
            state=ComponentIdentityState.INVALID,
        )
    return GuardModelIdentity(
        model_id=model_id,
        exact_revision=exact_revision,
        artifact_digest_sha512=artifact_digest_sha512,
        state=ComponentIdentityState.ACTIVE,
    )


def project_governance_layer_identity(
    *, package_id: str | None, manifest_digest_sha512: str | None
) -> GovernanceLayerIdentity:
    """P6-CODEX-014 (Second Rework): `package_id` present without its
    `manifest_digest_sha512` must never be reported as a fully `ACTIVE`,
    verified Governance Layer binding — it is an internally inconsistent
    partial identity, reported as `INVALID` instead. The real fix for the
    underlying "shows None even though Phase 4 actually bound Definitions"
    bug lives at the caller (`runtime_model_control_routes.py` must source
    these two values from the real Phase 4 `RuntimeGovernanceComposition`
    binding, never the Phase 3 `governance_definitions` control-surface
    flag) — this function only guards against a caller ever passing a
    half-populated pair through."""
    if package_id is None:
        return GovernanceLayerIdentity(
            package_id=None, manifest_digest_sha512=None, state=ComponentIdentityState.NONE
        )
    if manifest_digest_sha512 is None:
        return GovernanceLayerIdentity(
            package_id=package_id,
            manifest_digest_sha512=None,
            state=ComponentIdentityState.INVALID,
        )
    return GovernanceLayerIdentity(
        package_id=package_id,
        manifest_digest_sha512=manifest_digest_sha512,
        state=ComponentIdentityState.ACTIVE,
    )


def project_judge_model_identity(*, snapshot: RuntimeModelSnapshot) -> JudgeModelIdentity:
    independence = resolve_judge_independence(snapshot=snapshot)
    if independence is JudgeIndependenceClass.UNAVAILABLE:
        return JudgeModelIdentity(
            model_key=None,
            independence_class=independence,
            state=ComponentIdentityState.NONE,
        )
    judge_binding = next(
        binding for binding in snapshot.role_bindings if binding.role is ModelRole.JUDGE
    )
    state = (
        ComponentIdentityState.ACTIVE
        if judge_binding.binding_state is BindingState.BOUND
        else ComponentIdentityState.UNAVAILABLE
    )
    return JudgeModelIdentity(
        model_key=judge_binding.model_identity,
        independence_class=independence,
        state=state,
    )
