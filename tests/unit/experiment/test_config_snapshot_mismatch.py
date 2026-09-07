"""Phase 9-2 R2-WU-01: `config_snapshot.find_mismatched_slots()` -- the
per-slot half of Handoff R2 SS4.3's Frozen-vs-Live Hard Assertions.

Phase 9-2 R3-WU-01 additionally covers `overlay_variant_onto_snapshot()`
-- the IR-P9-2-R2-01 CRITICAL fix that makes two different Production
Variants' own "Desired Configuration" digests genuinely different."""

from __future__ import annotations

from margpa_runtime_llm.modules.experiment.domain.config_snapshot import (
    EffectiveConfigurationSnapshot,
    build_effective_configuration_snapshot,
    find_mismatched_slots,
    overlay_variant_onto_snapshot,
)
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    VariantDescriptor,
)


def _snapshot(
    *,
    main_selector: str | None = None,
    judge_selector: str | None = None,
    guard_selector: str | None = None,
    **modes: str,
) -> EffectiveConfigurationSnapshot:
    defaults: dict[str, str] = {
        "main": "active",
        "judge": "off",
        "guard": "off",
        "main_governance": "off",
        "repair": "off",
        "recording": "off",
    }
    defaults.update(modes)
    return build_effective_configuration_snapshot(
        main=ComponentSelection(
            component_key=ComponentKey.MAIN, selector_id=main_selector, mode=defaults["main"]
        ),
        judge=ComponentSelection(
            component_key=ComponentKey.JUDGE, selector_id=judge_selector, mode=defaults["judge"]
        ),
        guard=ComponentSelection(
            component_key=ComponentKey.GUARD, selector_id=guard_selector, mode=defaults["guard"]
        ),
        main_governance=ComponentSelection(
            component_key=ComponentKey.MAIN_GOVERNANCE, mode=defaults["main_governance"]
        ),
        definition_set=ComponentSelection(component_key=ComponentKey.DEFINITION_SET, mode=None),
        rag=ComponentSelection(component_key=ComponentKey.RAG, mode=None),
        repair=ComponentSelection(component_key=ComponentKey.REPAIR, mode=defaults["repair"]),
        recording=ComponentSelection(
            component_key=ComponentKey.RECORDING, mode=defaults["recording"]
        ),
        presentation=ComponentSelection(component_key=ComponentKey.PRESENTATION, mode=None),
    )


def test_an_absent_component_never_mismatches_whatever_live_actually_is() -> None:
    """WU-C C3's 不在/OFF distinction: a Variant that never declares a
    slot places no constraint on it at all."""

    variant = VariantDescriptor(
        variant_id="judge-only",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="observe"),),
    )
    snapshot = _snapshot(judge="observe", guard="enforce", main_governance="enforce")
    assert find_mismatched_slots(variant=variant, snapshot=snapshot) == ()


def test_a_declared_off_mode_requires_live_off_too() -> None:
    """The literally-named `baseline-all-off` Preset scenario: `main`
    `mode="off"` can never be satisfied by a live, functioning Main
    Runtime (`main` is always frozen `mode="active"` in a real Snapshot,
    `experiment_live_configuration.py`)."""

    variant = VariantDescriptor(
        variant_id="baseline-all-off",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, mode="off"),),
    )
    snapshot = _snapshot()
    assert find_mismatched_slots(variant=variant, snapshot=snapshot) == (ComponentKey.MAIN,)


def test_a_present_selection_with_mode_none_is_treated_as_off() -> None:
    """`identity.py`'s own Contract: a PRESENT `ComponentSelection` with
    `mode=None` means OFF, exactly like the explicit string `"off"`."""

    variant = VariantDescriptor(
        variant_id="v",
        components=(ComponentSelection(component_key=ComponentKey.GUARD, mode=None),),
    )
    assert find_mismatched_slots(variant=variant, snapshot=_snapshot(guard="off")) == ()
    assert find_mismatched_slots(variant=variant, snapshot=_snapshot(guard="enforce")) == (
        ComponentKey.GUARD,
    )


def test_a_declared_specific_mode_requires_an_exact_live_match() -> None:
    """The `judge-observe` scenario Handoff R2 SS4.3 names explicitly:
    Live Judge OFF or ENFORCE must both be rejected, never treated as a
    passable approximation of OBSERVE."""

    variant = VariantDescriptor(
        variant_id="judge-observe",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="observe"),),
    )
    assert find_mismatched_slots(variant=variant, snapshot=_snapshot(judge="observe")) == ()
    assert find_mismatched_slots(variant=variant, snapshot=_snapshot(judge="off")) == (
        ComponentKey.JUDGE,
    )
    assert find_mismatched_slots(variant=variant, snapshot=_snapshot(judge="enforce")) == (
        ComponentKey.JUDGE,
    )


def test_every_mismatched_slot_is_reported_not_only_the_first() -> None:
    variant = VariantDescriptor(
        variant_id="v",
        components=(
            ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),
            ComponentSelection(component_key=ComponentKey.GUARD, mode="enforce"),
        ),
    )
    snapshot = _snapshot(judge="off", guard="off")
    assert set(find_mismatched_slots(variant=variant, snapshot=snapshot)) == {
        ComponentKey.JUDGE,
        ComponentKey.GUARD,
    }


def test_a_fully_satisfiable_production_preset_has_no_mismatch() -> None:
    """The `production-guard-baseline` shape: exactly what Live must be
    for that Preset to be genuinely Run-able."""

    variant = VariantDescriptor(
        variant_id="production-guard-baseline",
        components=(
            ComponentSelection(component_key=ComponentKey.MAIN, mode="active"),
            ComponentSelection(component_key=ComponentKey.GUARD, mode="enforce"),
            ComponentSelection(component_key=ComponentKey.JUDGE, mode="off"),
            ComponentSelection(component_key=ComponentKey.MAIN_GOVERNANCE, mode="off"),
            ComponentSelection(component_key=ComponentKey.REPAIR, mode="off"),
            ComponentSelection(component_key=ComponentKey.RECORDING, mode="off"),
        ),
    )
    snapshot = _snapshot(guard="enforce")
    assert find_mismatched_slots(variant=variant, snapshot=snapshot) == ()


def test_two_differently_declared_variants_get_different_desired_digests() -> None:
    """R3-WU-01 (IR-P9-2-R2-01 CRITICAL fix): this is the exact regression
    the Controller's Independent Review confirmed R2 had -- `production-
    main-only-baseline` and `production-judge-repair-baseline` differ only
    in their own declared JUDGE/REPAIR slots, but R2's Plan-creation code
    read Live ONCE and copied the SAME digest onto every Variant's own
    `VariantConfigurationRef`, making the two indistinguishable. Calling
    `overlay_variant_onto_snapshot()` ONCE PER VARIANT (never once and
    reused) must always produce two different digests for two Variants
    that declare different Components."""

    base = _snapshot()
    main_only = VariantDescriptor(
        variant_id="production-main-only-baseline",
        components=(
            ComponentSelection(component_key=ComponentKey.MAIN, mode="active"),
            ComponentSelection(component_key=ComponentKey.JUDGE, mode="off"),
            ComponentSelection(component_key=ComponentKey.REPAIR, mode="off"),
        ),
    )
    judge_repair = VariantDescriptor(
        variant_id="production-judge-repair-baseline",
        components=(
            ComponentSelection(component_key=ComponentKey.MAIN, mode="active"),
            ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),
            ComponentSelection(component_key=ComponentKey.REPAIR, mode="enforce"),
        ),
    )
    desired_a = overlay_variant_onto_snapshot(variant=main_only, base=base)
    desired_b = overlay_variant_onto_snapshot(variant=judge_repair, base=base)
    assert desired_a.configuration_digest_sha512 != desired_b.configuration_digest_sha512
    assert desired_a.judge.mode == "off"
    assert desired_b.judge.mode == "enforce"


def test_an_undeclared_slot_keeps_the_base_snapshots_own_live_value() -> None:
    """WU-C C3's own 不在/absent semantics: a slot the Variant never
    declares is untouched by the overlay, whatever `base` actually is."""

    base = _snapshot(recording="enforce")
    variant = VariantDescriptor(
        variant_id="judge-only",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="observe"),),
    )
    desired = overlay_variant_onto_snapshot(variant=variant, base=base)
    assert desired.judge.mode == "observe"
    assert desired.recording.mode == "enforce"


def test_a_declared_wrong_selector_mismatches_even_when_mode_agrees() -> None:
    """R4-WU-01 Hard Assert (Handoff R4 SS4.2): Variant declares the Gemma
    Judge ENFORCE; Live actually has the Main-shared Qwen Judge ENFORCE --
    identical Mode, different Provider. This must mismatch, never pass
    just because the Mode strings happen to agree."""

    variant = VariantDescriptor(
        variant_id="judge-gemma-enforce",
        components=(
            ComponentSelection(
                component_key=ComponentKey.JUDGE,
                selector_id="judge.gemma-4-e2b-it-q4-0",
                mode="enforce",
            ),
        ),
    )
    live_qwen_judge = _snapshot(judge_selector="main.qwen3-4b-q4-k-m", judge="enforce")
    mismatched = find_mismatched_slots(variant=variant, snapshot=live_qwen_judge)
    assert mismatched == (ComponentKey.JUDGE,)


def test_a_declared_wrong_main_provider_mismatches() -> None:
    """R4-WU-01 Hard Assert: Variant declares Main=Qwen3 4B; Live Main is
    actually a different Provider -- Call 0 Typed mismatch."""

    variant = VariantDescriptor(
        variant_id="main-qwen",
        components=(
            ComponentSelection(
                component_key=ComponentKey.MAIN, selector_id="main.qwen3-4b-q4-k-m", mode="active"
            ),
        ),
    )
    live_deepseek_main = _snapshot(main_selector="main.deepseek-r1-0528-qwen3-8b-q4-k-m")
    assert find_mismatched_slots(variant=variant, snapshot=live_deepseek_main) == (
        ComponentKey.MAIN,
    )


def test_an_undeclared_selector_stays_dont_care_whatever_live_provider_is() -> None:
    """A Variant that declares only a slot's Mode (never its own
    `selector_id`) leaves that slot's Provider identity Don't-care -- it
    must never mismatch purely on Provider, whatever Live actually has."""

    variant = VariantDescriptor(
        variant_id="judge-enforce-any-provider",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),),
    )
    gemma_live = _snapshot(judge_selector="judge.gemma-4-e2b-it-q4-0", judge="enforce")
    assert find_mismatched_slots(variant=variant, snapshot=gemma_live) == ()
    qwen_live = _snapshot(judge_selector="main.qwen3-4b-q4-k-m", judge="enforce")
    assert find_mismatched_slots(variant=variant, snapshot=qwen_live) == ()


def test_overlay_keeps_lives_own_provider_when_variant_declares_mode_only() -> None:
    """R4-WU-01 (Handoff R4 SS4.1.4 fix): a Variant that declares a slot's
    Mode WITHOUT pinning its own `selector_id` must keep LIVE's own
    Provider identity in the Desired Snapshot -- it must never collapse to
    `None` just because the Variant itself was silent about which
    Provider it wants."""

    base = _snapshot(guard_selector="guard.qwen3guard-gen-0.6b-q8-0", guard="off")
    variant = VariantDescriptor(
        variant_id="guard-enforce-any-provider",
        components=(ComponentSelection(component_key=ComponentKey.GUARD, mode="enforce"),),
    )
    desired = overlay_variant_onto_snapshot(variant=variant, base=base)
    assert desired.guard.mode == "enforce"
    assert desired.guard.selector_id == "guard.qwen3guard-gen-0.6b-q8-0"


def test_overlay_uses_the_variants_own_selector_when_it_declares_one() -> None:
    """The opposite case: a Variant that DOES pin its own `selector_id`
    always wins over whatever Live's Provider happens to be -- the Desired
    Snapshot (and any later Restart Read of it) must show THIS Variant's
    own declared Gemma identity, never Live's Qwen one."""

    base = _snapshot(judge_selector="main.qwen3-4b-q4-k-m", judge="off")
    variant = VariantDescriptor(
        variant_id="judge-gemma-enforce",
        components=(
            ComponentSelection(
                component_key=ComponentKey.JUDGE,
                selector_id="judge.gemma-4-e2b-it-q4-0",
                mode="enforce",
            ),
        ),
    )
    desired = overlay_variant_onto_snapshot(variant=variant, base=base)
    assert desired.judge.mode == "enforce"
    assert desired.judge.selector_id == "judge.gemma-4-e2b-it-q4-0"


def test_a_declared_mode_none_selection_is_normalized_to_off_in_the_desired_snapshot() -> None:
    """Mirrors `find_mismatched_slots()`'s own normalization -- a PRESENT
    selection with `mode=None` means OFF, never a bare `null` in the
    Desired Snapshot's own displayed value."""

    base = _snapshot(guard="enforce")
    variant = VariantDescriptor(
        variant_id="v", components=(ComponentSelection(component_key=ComponentKey.GUARD),)
    )
    desired = overlay_variant_onto_snapshot(variant=variant, base=base)
    assert desired.guard.mode == "off"
