"""Live `LiveConfigurationPort` Adapter (Phase 9-2 R2, WU-01).

Reads the SAME six live Controllers `web_application.py` already
constructs for ordinary Chat -- `RuntimeModelController`,
`ProviderSelectionController`, `JudgeModeController`,
`GuardrailGovernanceComposition.mode_controller`,
`RuntimeGovernanceComposition.mode_controller`, `RepairModeController`,
`RecordingModeController` -- into one `EffectiveConfigurationSnapshot`
(`modules.experiment.domain.config_snapshot`). Never mutates any of
them (Handoff R2 SS3: "Request-localまたはExperiment-scopedの設定境界を
優先する。それが過大なら...Live Configの完全一致をCall前に検証し...
有界Fallback"; this is that bounded Fallback's read side) and never
forces a different Main/Judge/Guard selection -- the same Option-2-style
non-interference `experiment_production_turn_adapter.py` already commits
to for the Turn itself.

Three `ComponentKey` slots -- `definition_set`, `rag`, `presentation` --
have no live Mode Controller anywhere in this codebase (confirmed by
direct research: ARGD/DAGD reference descriptors are loaded once at
Bootstrap with no runtime mutation path; Documentation RAG mode is a
per-request Turn setting this Round's Production Adapter never engages;
Thinking/Presentation visibility is a Bootstrap-fixed default). Reported
as `ComponentSelection(mode=None)` -- WU-C C3's own "absent" vocabulary --
never a fabricated `"off"`, since nothing here was ever actually
observed to BE off; it simply cannot drift, so there is nothing to
freeze or compare for these three slots this Round."""

from __future__ import annotations

from margpa_runtime_llm.modules.evaluation.application.judge_mode_controller import (
    JudgeModeController,
)
from margpa_runtime_llm.modules.experiment.domain.config_snapshot import (
    EffectiveConfigurationSnapshot,
    build_effective_configuration_snapshot,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    require_safe_identifier,
)
from margpa_runtime_llm.modules.experiment.domain.provider_identity import (
    ProviderIdentityDetail,
    ProviderIdentityEnvelope,
)
from margpa_runtime_llm.modules.repair.application.repair_mode_controller import (
    RepairModeController,
)
from margpa_runtime_llm.modules.runtime_model_control.application import ProviderSelectionController
from margpa_runtime_llm.modules.runtime_model_control.application.runtime_model_controller import (
    RuntimeModelController,
)
from margpa_runtime_llm.modules.runtime_model_control.domain.identifiers import (
    ModelRole,
    RuntimeState,
)
from margpa_runtime_llm.modules.runtime_observability.application.recording_mode_controller import (
    RecordingModeController,
)

from .guardrail_governance import GuardrailGovernanceComposition
from .runtime_governance import RuntimeGovernanceComposition

_MAIN_MODE_SENTINEL = "active"
"""No live Controller models a `main` on/off Mode the way Judge/Guard/
Main-Governance/Repair/Recording do -- a functioning live Chat Runtime's
Main is always active by construction (there is no live control that
turns it off for one Production Turn and still produces an answer). This
fixed sentinel is a documentary constant, never a live read; a Variant
declaring `main` `mode="off"` (WU-C C3's explicit-OFF shape) can then
never match it -- the honest, correct outcome for a genuinely impossible
Preset under Production execution."""


def _safe_selector(value: str | None) -> str | None:
    """Provider identities occasionally carry characters outside
    `identity.require_safe_identifier`'s pattern (e.g. a Built-in
    sentinel or an empty active_provider) -- rather than let an
    unrelated live-read edge case raise inside Snapshot construction,
    an unsafe/absent value degrades to `None` (WU-C C2: `selector_id`
    is always Optional)."""

    if not value:
        return None
    try:
        return require_safe_identifier(value, field_name="selector_id")
    except Exception:
        return None


class BootstrapLiveConfigurationReader:
    """The one real `LiveConfigurationPort` implementation. Constructed
    once by `build_phase1_web_runtime` and threaded onto `WebRuntime.
    live_configuration_reader` -- absent (`None`) unless every Controller
    it needs is itself wired (same Optional-composition idiom as
    `LiveProductionTurnAdapter`)."""

    def __init__(
        self,
        *,
        runtime_model_control: RuntimeModelController | None,
        provider_selection_control: ProviderSelectionController | None,
        judge_mode_control: JudgeModeController | None,
        guardrail_governance_composition: GuardrailGovernanceComposition | None,
        runtime_governance_composition: RuntimeGovernanceComposition | None,
        repair_mode_control: RepairModeController | None,
        recording_mode_control: RecordingModeController | None,
    ) -> None:
        self._runtime_model_control = runtime_model_control
        self._provider_selection_control = provider_selection_control
        self._judge_mode_control = judge_mode_control
        self._guardrail_governance_composition = guardrail_governance_composition
        self._runtime_governance_composition = runtime_governance_composition
        self._repair_mode_control = repair_mode_control
        self._recording_mode_control = recording_mode_control

    def _provider_for(self, role: ModelRole) -> str | None:
        if self._provider_selection_control is None:
            return None
        return _safe_selector(self._provider_selection_control.selection_for(role).active_provider)

    def snapshot(self) -> EffectiveConfigurationSnapshot:
        main_selector = (
            _safe_selector(self._runtime_model_control.snapshot().selected_model_key)
            if self._runtime_model_control is not None
            else None
        )
        provider_artifact_digest = (
            self._runtime_model_control.snapshot().artifact_digest
            if self._runtime_model_control is not None
            else None
        )
        judge_mode = (
            self._judge_mode_control.mode_snapshot().current_mode.value
            if self._judge_mode_control is not None
            else "off"
        )
        guard_mode = (
            self._guardrail_governance_composition.mode_controller.current_mode_value()
            if self._guardrail_governance_composition is not None
            else "off"
        )
        main_governance_mode = (
            self._runtime_governance_composition.mode_controller.current_mode_value()
            if self._runtime_governance_composition is not None
            else "off"
        )
        repair_mode = (
            self._repair_mode_control.mode_snapshot().current_mode.value
            if self._repair_mode_control is not None
            else "off"
        )
        recording_mode = (
            self._recording_mode_control.mode_snapshot().current_mode.value
            if self._recording_mode_control is not None
            else "off"
        )
        return build_effective_configuration_snapshot(
            main=ComponentSelection(
                component_key=ComponentKey.MAIN,
                selector_id=main_selector,
                mode=_MAIN_MODE_SENTINEL,
            ),
            judge=ComponentSelection(
                component_key=ComponentKey.JUDGE,
                selector_id=self._provider_for(ModelRole.JUDGE),
                mode=judge_mode,
            ),
            guard=ComponentSelection(
                component_key=ComponentKey.GUARD,
                selector_id=self._provider_for(ModelRole.GUARD),
                mode=guard_mode,
            ),
            main_governance=ComponentSelection(
                component_key=ComponentKey.MAIN_GOVERNANCE,
                selector_id=None,
                mode=main_governance_mode,
            ),
            definition_set=ComponentSelection(
                component_key=ComponentKey.DEFINITION_SET, selector_id=None, mode=None
            ),
            rag=ComponentSelection(component_key=ComponentKey.RAG, selector_id=None, mode=None),
            repair=ComponentSelection(
                component_key=ComponentKey.REPAIR, selector_id=None, mode=repair_mode
            ),
            recording=ComponentSelection(
                component_key=ComponentKey.RECORDING, selector_id=None, mode=recording_mode
            ),
            presentation=ComponentSelection(
                component_key=ComponentKey.PRESENTATION, selector_id=None, mode=None
            ),
            provider_artifact_digest_sha512=provider_artifact_digest,
        )

    def _judge_or_guard_detail(
        self, *, component_key: ComponentKey, role: ModelRole
    ) -> ProviderIdentityDetail:
        """R4-WU-01 (Handoff R4 SS4.1.5): Configured/Active read straight
        from `ProviderSelectionController` (the live, authoritative source
        for Judge/Guard identity) -- Artifact Digest is looked up for the
        ACTIVE provider ONLY (never Configured's, and never a different
        Role's -- Hard Assert "Judge/Guard Artifact不明をMain Artifact
        Digestで代用しない"), `None` (Unavailable) whenever Active itself
        is `None`, rather than fabricated from Configured's own Option."""

        if self._provider_selection_control is None:
            return ProviderIdentityDetail(component_key=component_key)
        selection = self._provider_selection_control.selection_for(role)
        active = _safe_selector(selection.active_provider)
        artifact_digest: str | None = None
        if active is not None:
            option = self._provider_selection_control.option_for(role=role, provider_id=active)
            if option is not None:
                artifact_digest = option.artifact_digest_sha512
        return ProviderIdentityDetail(
            component_key=component_key,
            configured_selector_id=_safe_selector(selection.configured_provider),
            active_selector_id=active,
            artifact_digest_sha512=artifact_digest,
        )

    def _main_detail(self) -> ProviderIdentityDetail:
        """Main's live identity is authoritatively `RuntimeModelController`
        (never `ProviderSelectionController`'s own MAIN entry, which has no
        live sync back from a real Runtime Model Switch and can go stale --
        `snapshot()`'s own `main_selector` above already makes this same
        choice). Active/Artifact-Digest are only reported once
        `runtime_state` genuinely confirms `ACTIVE`; a Switch still
        `loading`/`switching` reports Active/Artifact-Digest as Unavailable
        rather than presuming success."""

        if self._runtime_model_control is None:
            return ProviderIdentityDetail(component_key=ComponentKey.MAIN)
        model_snapshot = self._runtime_model_control.snapshot()
        configured = _safe_selector(model_snapshot.selected_model_key)
        is_active = model_snapshot.runtime_state is RuntimeState.ACTIVE
        return ProviderIdentityDetail(
            component_key=ComponentKey.MAIN,
            configured_selector_id=configured,
            active_selector_id=configured if is_active else None,
            artifact_digest_sha512=model_snapshot.artifact_digest if is_active else None,
        )

    def provider_identity(self) -> ProviderIdentityEnvelope:
        return ProviderIdentityEnvelope(
            main=self._main_detail(),
            judge=self._judge_or_guard_detail(
                component_key=ComponentKey.JUDGE, role=ModelRole.JUDGE
            ),
            guard=self._judge_or_guard_detail(
                component_key=ComponentKey.GUARD, role=ModelRole.GUARD
            ),
        )
