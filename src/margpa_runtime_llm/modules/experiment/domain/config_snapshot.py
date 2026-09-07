"""Effective Configuration Snapshot (Phase 9-2, WU-A A2).

Design §5's Canonical Domain Candidate names this type
`EffectiveConfigurationSnapshot` -- this IS that type, but it is a
deliberately distinct Python class from `modules.configuration_control.
contracts.EffectiveConfigurationSnapshot` (a different bounded context's
live UI-Settings Patch/Preview/Apply projection: `selected_model`,
`context_size`, `recording_mode`, feature/governance hooks -- an
unrelated shape with no Judge/Guard/Provider-Artifact/Definition/Case/
Plan Digest fields at all). Handoff WU-A A2 explicitly offers "reuse OR
normalize via an Adapter" as alternatives; forcing this Experiment-Core-
specific shape onto that unrelated, already-live class would require
bolting Phase-9-2-only fields onto a Phase 3-5 Settings contract other
Components depend on. This module is the Adapter-normalized target
shape instead -- a real Adapter that builds one of these FROM the live
Settings snapshot (plus Provider/Judge/Guard live state) is a WU-C
concern, not this Contract's.
"""

from __future__ import annotations

import hashlib

from pydantic import model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .canonical import canonical_json_bytes
from .errors import ExperimentCoreError, ExperimentCoreErrorCode
from .identity import ComponentKey, ComponentSelection, VariantDescriptor

SHA512_PATTERN = r"^[0-9a-f]{128}$"


class EffectiveConfigurationSnapshot(ImmutableContract):
    """WU-A A2: one Component Selection per named slot (never a free-form
    dict), plus separate Digests for Provider/Artifact, Definition, Case,
    and Plan -- Configured/Active/Executed identities are never merged
    into one field (WU-A A2 "Configured/Active/Executedを混ぜない"; the
    real three-way split lives on each Actor's own real Evidence, which
    this frozen Snapshot references by these Digests rather than
    embedding). No Secret, User absolute Path, or credential ever appears
    here -- every `ComponentSelection` field is already validated as a
    safe identifier at construction (`identity.py`)."""

    main: ComponentSelection
    judge: ComponentSelection
    guard: ComponentSelection
    main_governance: ComponentSelection
    definition_set: ComponentSelection
    rag: ComponentSelection
    repair: ComponentSelection
    recording: ComponentSelection
    presentation: ComponentSelection
    provider_artifact_digest_sha512: str | None = None
    definition_digest_sha512: str | None = None
    case_digest_sha512: str | None = None
    plan_digest_sha512: str | None = None
    configuration_digest_sha512: str

    @model_validator(mode="after")
    def _validate_slots_and_digest(self) -> EffectiveConfigurationSnapshot:
        expected_keys: dict[ComponentKey, ComponentSelection] = {
            ComponentKey.MAIN: self.main,
            ComponentKey.JUDGE: self.judge,
            ComponentKey.GUARD: self.guard,
            ComponentKey.MAIN_GOVERNANCE: self.main_governance,
            ComponentKey.DEFINITION_SET: self.definition_set,
            ComponentKey.RAG: self.rag,
            ComponentKey.REPAIR: self.repair,
            ComponentKey.RECORDING: self.recording,
            ComponentKey.PRESENTATION: self.presentation,
        }
        for key, selection in expected_keys.items():
            if selection.component_key is not key:
                raise ExperimentCoreError(
                    code=ExperimentCoreErrorCode.COMPONENT_SLOT_MISMATCH,
                    safe_message=(
                        f"EffectiveConfigurationSnapshot.{key.value} must carry "
                        f"component_key={key.value!r}, got {selection.component_key.value!r}"
                    ),
                )
        expected_digest = compute_configuration_digest_sha512(
            main=self.main,
            judge=self.judge,
            guard=self.guard,
            main_governance=self.main_governance,
            definition_set=self.definition_set,
            rag=self.rag,
            repair=self.repair,
            recording=self.recording,
            presentation=self.presentation,
            provider_artifact_digest_sha512=self.provider_artifact_digest_sha512,
            definition_digest_sha512=self.definition_digest_sha512,
            case_digest_sha512=self.case_digest_sha512,
            plan_digest_sha512=self.plan_digest_sha512,
        )
        if self.configuration_digest_sha512 != expected_digest:
            raise ExperimentCoreError(
                code=ExperimentCoreErrorCode.CONFIGURATION_DIGEST_MISMATCH,
                safe_message=(
                    "EffectiveConfigurationSnapshot.configuration_digest_sha512 does not "
                    "match its own recomputed content digest"
                ),
            )
        return self


def compute_configuration_digest_sha512(
    *,
    main: ComponentSelection,
    judge: ComponentSelection,
    guard: ComponentSelection,
    main_governance: ComponentSelection,
    definition_set: ComponentSelection,
    rag: ComponentSelection,
    repair: ComponentSelection,
    recording: ComponentSelection,
    presentation: ComponentSelection,
    provider_artifact_digest_sha512: str | None,
    definition_digest_sha512: str | None,
    case_digest_sha512: str | None,
    plan_digest_sha512: str | None,
) -> str:
    payload: dict[str, object] = {
        "slots": {
            selection.component_key.value: {
                "selector_id": selection.selector_id,
                "mode": selection.mode,
            }
            for selection in (
                main,
                judge,
                guard,
                main_governance,
                definition_set,
                rag,
                repair,
                recording,
                presentation,
            )
        },
        "provider_artifact_digest_sha512": provider_artifact_digest_sha512,
        "definition_digest_sha512": definition_digest_sha512,
        "case_digest_sha512": case_digest_sha512,
        "plan_digest_sha512": plan_digest_sha512,
    }
    return hashlib.sha512(canonical_json_bytes(payload)).hexdigest()


def build_effective_configuration_snapshot(
    *,
    main: ComponentSelection,
    judge: ComponentSelection,
    guard: ComponentSelection,
    main_governance: ComponentSelection,
    definition_set: ComponentSelection,
    rag: ComponentSelection,
    repair: ComponentSelection,
    recording: ComponentSelection,
    presentation: ComponentSelection,
    provider_artifact_digest_sha512: str | None = None,
    definition_digest_sha512: str | None = None,
    case_digest_sha512: str | None = None,
    plan_digest_sha512: str | None = None,
) -> EffectiveConfigurationSnapshot:
    digest = compute_configuration_digest_sha512(
        main=main,
        judge=judge,
        guard=guard,
        main_governance=main_governance,
        definition_set=definition_set,
        rag=rag,
        repair=repair,
        recording=recording,
        presentation=presentation,
        provider_artifact_digest_sha512=provider_artifact_digest_sha512,
        definition_digest_sha512=definition_digest_sha512,
        case_digest_sha512=case_digest_sha512,
        plan_digest_sha512=plan_digest_sha512,
    )
    return EffectiveConfigurationSnapshot(
        main=main,
        judge=judge,
        guard=guard,
        main_governance=main_governance,
        definition_set=definition_set,
        rag=rag,
        repair=repair,
        recording=recording,
        presentation=presentation,
        provider_artifact_digest_sha512=provider_artifact_digest_sha512,
        definition_digest_sha512=definition_digest_sha512,
        case_digest_sha512=case_digest_sha512,
        plan_digest_sha512=plan_digest_sha512,
        configuration_digest_sha512=digest,
    )


def overlay_variant_onto_snapshot(
    *, variant: VariantDescriptor, base: EffectiveConfigurationSnapshot
) -> EffectiveConfigurationSnapshot:
    """R3-WU-01 (IR-P9-2-R2-01 CRITICAL fix): builds this Variant's own
    "Desired Configuration" -- `base` (a real Live Snapshot, read once at
    Plan-creation time) with every slot THIS Variant actually declares
    replaced by its own `ComponentSelection`; an undeclared slot keeps
    `base`'s own live value untouched (WU-C C3's 不在/absent semantics --
    "this Variant does not care about this slot"). A present selection with
    `mode=None` is normalized to the literal `"off"`, mirroring `find_
    mismatched_slots()`'s own normalization, so a Desired Snapshot never
    displays a bare `null` for a slot the Variant explicitly turned off.

    Called ONCE PER VARIANT (never once for a whole Plan and reused) --
    this is what makes the Controller's own confirmed CRITICAL finding
    ("同一Live Snapshot Digestを...相互に異なる全Variantへ複製して解決
    扱いにしない") structurally impossible from this function onward: two
    Variants that declare different slots differently always produce
    different `configuration_digest_sha512` values, because each call
    starts from the same `base` but overlays a genuinely different set of
    declared slots on top of it."""

    def _slot(key: ComponentKey, live: ComponentSelection) -> ComponentSelection:
        declared = variant.component(key)
        if declared is None:
            return live
        normalized_mode = declared.mode if declared.mode is not None else "off"
        # R4-WU-01 (Handoff R4 SS4.1.4 fix): a Variant that declares this
        # slot's Mode but not its own `selector_id` (e.g. a Preset that only
        # turns a Component on/off without pinning a specific Provider)
        # keeps the LIVE Provider identity for this slot -- it must never
        # collapse to `None` just because the Variant itself was silent
        # about which Provider it wants. Only a Variant that explicitly
        # declares its OWN `selector_id` overrides Live's here.
        resolved_selector = (
            declared.selector_id if declared.selector_id is not None else live.selector_id
        )
        return ComponentSelection(
            component_key=key, selector_id=resolved_selector, mode=normalized_mode
        )

    return build_effective_configuration_snapshot(
        main=_slot(ComponentKey.MAIN, base.main),
        judge=_slot(ComponentKey.JUDGE, base.judge),
        guard=_slot(ComponentKey.GUARD, base.guard),
        main_governance=_slot(ComponentKey.MAIN_GOVERNANCE, base.main_governance),
        definition_set=_slot(ComponentKey.DEFINITION_SET, base.definition_set),
        rag=_slot(ComponentKey.RAG, base.rag),
        repair=_slot(ComponentKey.REPAIR, base.repair),
        recording=_slot(ComponentKey.RECORDING, base.recording),
        presentation=_slot(ComponentKey.PRESENTATION, base.presentation),
        provider_artifact_digest_sha512=base.provider_artifact_digest_sha512,
        definition_digest_sha512=base.definition_digest_sha512,
        case_digest_sha512=base.case_digest_sha512,
        plan_digest_sha512=base.plan_digest_sha512,
    )


def find_mismatched_slots(
    *, variant: VariantDescriptor, snapshot: EffectiveConfigurationSnapshot
) -> tuple[ComponentKey, ...]:
    """R2-WU-01 (IR-P9-2-R1-01 fix): the per-slot half of the Frozen-vs-
    Live comparison Handoff SS4.3's Hard Assertions require -- a WHOLE-
    Snapshot digest mismatch (checked separately by the caller, comparing
    `EffectiveConfigurationSnapshot.configuration_digest_sha512` values)
    already catches ANY Live drift since a Plan's Snapshot was frozen;
    this function instead answers a different question: does this
    specific Variant's OWN declared `ComponentSelection`s even describe a
    Configuration this Snapshot could ever satisfy, drift or not.

    An ABSENT `ComponentSelection` (`variant.component(key) is None`)
    means "this Variant does not care about this slot" (WU-C C3's own
    不在/OFF distinction, `identity.py`) -- it can never mismatch,
    whatever the live value is. A PRESENT `ComponentSelection` with
    `mode=None` means "OFF" by the same Contract, compared against this
    Snapshot's own live `"off"` value for that slot (every live Mode
    Controller found for this Round -- Judge/Guard/Main-Governance/
    Repair/Recording -- shares that literal string for its disabled
    state). This is exactly how a genuinely impossible Preset (e.g. one
    that declares `main` `mode="off"`, which no live, functioning Main
    Turn Runtime can ever actually be) is caught, never silently treated
    as satisfied."""

    slot_map: dict[ComponentKey, ComponentSelection] = {
        ComponentKey.MAIN: snapshot.main,
        ComponentKey.JUDGE: snapshot.judge,
        ComponentKey.GUARD: snapshot.guard,
        ComponentKey.MAIN_GOVERNANCE: snapshot.main_governance,
        ComponentKey.DEFINITION_SET: snapshot.definition_set,
        ComponentKey.RAG: snapshot.rag,
        ComponentKey.REPAIR: snapshot.repair,
        ComponentKey.RECORDING: snapshot.recording,
        ComponentKey.PRESENTATION: snapshot.presentation,
    }
    mismatched: list[ComponentKey] = []
    for key, live_selection in slot_map.items():
        declared = variant.component(key)
        if declared is None:
            continue
        declared_mode = declared.mode if declared.mode is not None else "off"
        mode_mismatch = declared_mode != live_selection.mode
        # R4-WU-01 (Handoff R4 SS4.1.3 fix): a Variant that also pins its
        # own selector_id mismatches on Provider identity too, even when
        # Mode agrees (e.g. Variant wants the Gemma Judge ENFORCE while
        # Live actually has the Main-shared Qwen Judge ENFORCE active) --
        # an undeclared selector_id stays Don't-care, never mismatching.
        selector_mismatch = (
            declared.selector_id is not None
            and declared.selector_id != live_selection.selector_id
        )
        if mode_mismatch or selector_mismatch:
            mismatched.append(key)
    return tuple(mismatched)
