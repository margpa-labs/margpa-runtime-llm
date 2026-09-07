"""Phase 9-2 R4-WU-01: `bootstrap.experiment_live_configuration.
BootstrapLiveConfigurationReader.provider_identity()`."""

from __future__ import annotations

from margpa_runtime_llm.bootstrap.experiment_live_configuration import (
    BootstrapLiveConfigurationReader,
)
from margpa_runtime_llm.modules.inference.domain.model_definition import ModelDefinition
from margpa_runtime_llm.modules.runtime_model_control.application import (
    ProviderSelectionController,
)
from margpa_runtime_llm.modules.runtime_model_control.application.provider_selection_controller import (  # noqa: E501
    GEMMA_E2B_JUDGE,
    QWEN3_GUARD,
    QWEN_MAIN,
)
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
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

_SHA512_FILLER = "c" * 128


class _FakeBackend:
    def probe_capability(self, *, definition: ModelDefinition) -> CapabilityProbeResult:
        return CapabilityProbeResult(
            native_context_limit=32768,
            backend_context_limit=32768,
            deployment_verified_context_limit=8192,
            max_output_token_limit=8191,
            capability_digest=_SHA512_FILLER,
        )

    def load(self, *, definition: ModelDefinition, context_size: int) -> LoadedModelHandle:
        raise NotImplementedError

    def unload(self) -> None:
        raise NotImplementedError


class _FakeAccessLease:
    def try_acquire_switch_lease(self, *, task_id: str) -> bool:
        return True

    def release_switch_lease(self, *, task_id: str) -> None:
        return None


class _FakeDefinitions:
    def resolve(self, *, model_key: str) -> ModelDefinition:
        raise NotImplementedError

    def all_definitions(self) -> tuple[ModelDefinition, ...]:
        return ()


def _runtime_model_control(
    *, model_key: str = QWEN_MAIN, runtime_state: RuntimeState = RuntimeState.ACTIVE
) -> RuntimeModelController:
    binding = RoleBinding(
        role=ModelRole.MAIN,
        model_identity=model_key,
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        binding_state=BindingState.BOUND,
        independence_class=IndependenceClass.SHARED_ARTIFACT,
        capability_digest=_SHA512_FILLER,
    )
    digest = compute_runtime_model_snapshot_digest(
        revision=0,
        selected_model_key=model_key,
        role_bindings=(binding,),
        artifact_identity=model_key,
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=runtime_state,
        loaded_context_size=4096,
        current_max_new_tokens=2048,
    )
    snapshot = RuntimeModelSnapshot(
        revision=0,
        digest_sha512=digest,
        selected_model_key=model_key,
        role_bindings=(binding,),
        artifact_identity=model_key,
        artifact_digest=_SHA512_FILLER,
        backend_identity="llama_cpp",
        runtime_state=runtime_state,
        loaded_context_size=4096,
        model_native_context_limit=32768,
        backend_context_limit=32768,
        deployment_verified_context_limit=8192,
        max_output_token_limit=8191,
        current_max_new_tokens=2048,
        last_transition_receipt=None,
    )
    return RuntimeModelController(
        initial_snapshot=snapshot,
        backend=_FakeBackend(),
        access_lease=_FakeAccessLease(),
        definitions=_FakeDefinitions(),
    )


def test_main_configured_and_active_come_from_runtime_model_control_when_active() -> None:
    reader = BootstrapLiveConfigurationReader(
        runtime_model_control=_runtime_model_control(runtime_state=RuntimeState.ACTIVE),
        provider_selection_control=None,
        judge_mode_control=None,
        guardrail_governance_composition=None,
        runtime_governance_composition=None,
        repair_mode_control=None,
        recording_mode_control=None,
    )
    detail = reader.provider_identity().main
    assert detail.configured_selector_id == QWEN_MAIN
    assert detail.active_selector_id == QWEN_MAIN
    assert detail.artifact_digest_sha512 == _SHA512_FILLER


def test_main_active_and_artifact_digest_are_unavailable_while_not_confirmed_active() -> None:
    """R4-WU-01 (Handoff R4 SS4.1.5): a Switch still `loading`/`switching`
    must never report Active/Artifact-Digest as if it had already
    committed -- Unavailable (`None`), never presumed success."""

    reader = BootstrapLiveConfigurationReader(
        runtime_model_control=_runtime_model_control(runtime_state=RuntimeState.LOADING),
        provider_selection_control=None,
        judge_mode_control=None,
        guardrail_governance_composition=None,
        runtime_governance_composition=None,
        repair_mode_control=None,
        recording_mode_control=None,
    )
    detail = reader.provider_identity().main
    assert detail.configured_selector_id == QWEN_MAIN
    assert detail.active_selector_id is None
    assert detail.artifact_digest_sha512 is None


def test_judge_configured_but_not_active_is_distinguishable_from_active() -> None:
    """Hard Assert: "Configured Gemma/Active noneと、Configured Gemma/
    Active Gemmaを区別できる"."""

    control = ProviderSelectionController()
    reader = BootstrapLiveConfigurationReader(
        runtime_model_control=None,
        provider_selection_control=control,
        judge_mode_control=None,
        guardrail_governance_composition=None,
        runtime_governance_composition=None,
        repair_mode_control=None,
        recording_mode_control=None,
    )
    # Fresh `ProviderSelectionController()` default: Judge is CONFIGURED to
    # Gemma but never Activated (`active_provider=None`).
    detail = reader.provider_identity().judge
    assert detail.configured_selector_id == GEMMA_E2B_JUDGE
    assert detail.active_selector_id is None
    assert detail.artifact_digest_sha512 is None

    snapshot = control.snapshot()
    control.select_active(
        role=ModelRole.JUDGE,
        provider_id=GEMMA_E2B_JUDGE,
        expected_revision=snapshot.revision,
        expected_digest=snapshot.digest_sha512,
    )
    activated_detail = reader.provider_identity().judge
    assert activated_detail.configured_selector_id == GEMMA_E2B_JUDGE
    assert activated_detail.active_selector_id == GEMMA_E2B_JUDGE
    assert activated_detail.artifact_digest_sha512 is not None


def test_guard_artifact_digest_is_never_borrowed_from_main() -> None:
    """Hard Assert: "Judge/Guard Artifact不明をMain Artifact Digestで代用
    しない"."""

    reader = BootstrapLiveConfigurationReader(
        runtime_model_control=_runtime_model_control(runtime_state=RuntimeState.ACTIVE),
        provider_selection_control=ProviderSelectionController(),
        judge_mode_control=None,
        guardrail_governance_composition=None,
        runtime_governance_composition=None,
        repair_mode_control=None,
        recording_mode_control=None,
    )
    envelope = reader.provider_identity()
    # Guard is CONFIGURED (Qwen3Guard) but never Activated by default --
    # its own Artifact Digest must stay Unavailable, never fall back to
    # Main's (which IS confirmed Active/digest-bearing here).
    assert envelope.guard.configured_selector_id == QWEN3_GUARD
    assert envelope.guard.active_selector_id is None
    assert envelope.guard.artifact_digest_sha512 is None
    assert envelope.main.artifact_digest_sha512 is not None
    assert envelope.guard.artifact_digest_sha512 != envelope.main.artifact_digest_sha512
