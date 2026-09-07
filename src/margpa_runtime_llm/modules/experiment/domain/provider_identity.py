"""Provider Identity Envelope (Phase 9-2 R4, WU-01).

Handoff R4 SS4.1.5: "Main/Judge/GuardのConfigured、Active、期待Executed、
Artifact Digestを別Fieldとして保持する... 取得不能値はUnavailableであり、
同一値へ潰さない". `EffectiveConfigurationSnapshot.{main,judge,guard}.
selector_id` (one field per slot) already answers "what SHOULD run" for
Frozen-vs-Live comparison purposes -- it deliberately never grew a second
field, so this is a separate, additive Envelope carried ALONGSIDE a
Snapshot in the persisted Run/Variant Configuration Envelope (never merged
into `EffectiveConfigurationSnapshot` itself, which stays the WU-A A2
Fixture-and-Production-shared shape).

Only Main/Judge/Guard are modeled here -- these are the three slots a real
Model Provider can actually back (Handoff's own three named Preset roles);
Main-Governance/Definition-Set/RAG/Repair/Recording/Presentation have no
live Provider identity of this kind at all (they are pure Mode toggles or
have no live Controller, per `bootstrap/experiment_live_configuration.py`'s
own module docstring)."""

from __future__ import annotations

from pydantic import model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .errors import ExperimentCoreError, ExperimentCoreErrorCode
from .identity import ComponentKey

SHA512_PATTERN = r"^[0-9a-f]{128}$"


class ProviderIdentityDetail(ImmutableContract):
    """One Main/Judge/Guard slot's Provider identity, Configured/Active/
    Expected-Executed/Artifact-Digest kept as four genuinely separate
    fields (Handoff R4 SS4.1.5) -- never merged, never one substituted for
    another when the real value is unavailable.

    - `configured_selector_id`: the Provider this Role is currently set
      to, whether or not it is actually loaded/running yet.
    - `active_selector_id`: the Provider ACTUALLY active/loaded right now
      -- `None` when Configured but not (yet, or no longer) Active; this
      is what lets a reader distinguish "Configured Gemma / Active none"
      from "Configured Gemma / Active Gemma" (Handoff Hard Assert).
    - `expected_executed_selector_id`: what THIS Variant's own declared
      Component Selection says should run for this Role -- filled in by
      the caller once it knows the Variant (a bare Live read alone cannot
      know this); `None` when the Variant leaves this slot Don't-care.
    - `artifact_digest_sha512`: the SHA-512 of the Provider actually
      ACTIVE for this Role (never Configured's, never a different Role's
      digest substituted in) -- `None` (Unavailable) when Active itself
      is `None`, never fabricated from a nearby but different value."""

    component_key: ComponentKey
    configured_selector_id: str | None = None
    active_selector_id: str | None = None
    expected_executed_selector_id: str | None = None
    artifact_digest_sha512: str | None = None


class ProviderIdentityEnvelope(ImmutableContract):
    main: ProviderIdentityDetail
    judge: ProviderIdentityDetail
    guard: ProviderIdentityDetail

    @model_validator(mode="after")
    def _validate_slots(self) -> ProviderIdentityEnvelope:
        expected: dict[ComponentKey, ProviderIdentityDetail] = {
            ComponentKey.MAIN: self.main,
            ComponentKey.JUDGE: self.judge,
            ComponentKey.GUARD: self.guard,
        }
        for key, detail in expected.items():
            if detail.component_key is not key:
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.COMPONENT_SLOT_MISMATCH,
                    safe_message=(
                        f"ProviderIdentityEnvelope.{key.value} must carry "
                        f"component_key={key.value!r}, got {detail.component_key.value!r}"
                    ),
                )
        return self

    def with_expected_executed(
        self,
        *,
        main: str | None,
        judge: str | None,
        guard: str | None,
    ) -> ProviderIdentityEnvelope:
        """Returns a copy with `expected_executed_selector_id` filled in
        per slot -- the ONE mutation this Envelope ever undergoes, applied
        by a caller that knows the Variant (a `LiveConfigurationPort` alone
        never does). Never touches Configured/Active/Artifact-Digest."""

        return ProviderIdentityEnvelope(
            main=self.main.model_copy(update={"expected_executed_selector_id": main}),
            judge=self.judge.model_copy(update={"expected_executed_selector_id": judge}),
            guard=self.guard.model_copy(update={"expected_executed_selector_id": guard}),
        )
