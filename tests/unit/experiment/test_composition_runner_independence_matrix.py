"""Phase 9-2 WU-C C1/C2/C3: Composition Runner Independence Matrix.

Design §8 C3's representative Matrix, Fixture-only: for every entry, the
Component(s) declared OFF/absent must show `called=False` and zero
Mutation/Evidence/Authority, while every other declared Component is
genuinely, independently invoked."""

from __future__ import annotations

from margpa_runtime_llm.adapters.experiment.fixture_actor_adapters import FixtureActor
from margpa_runtime_llm.modules.experiment.application.composition_runner import run_variant
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    VariantDescriptor,
)


def _actors(
    *, mutation: int = 1, evidence: int = 1, authority: bool = True
) -> dict[ComponentKey, FixtureActor]:
    return {
        key: FixtureActor(
            mutation_count=mutation, evidence_count=evidence, authority_exercised=authority
        )
        for key in ComponentKey
    }


def test_all_components_off_baseline_calls_nothing() -> None:
    variant = VariantDescriptor(
        variant_id="all-off",
        components=tuple(ComponentSelection(component_key=key, mode="off") for key in ComponentKey),
    )
    actors = _actors()
    result = run_variant(variant, actors)
    for key in ComponentKey:
        record = result.invocation(key)
        assert record is not None
        assert record.called is False
        assert record.mutation_count == 0
        assert record.evidence_count == 0
        assert record.authority_exercised is False
        assert actors[key].calls == []


def test_judge_only_observe_calls_only_judge() -> None:
    variant = VariantDescriptor(
        variant_id="judge-observe-only",
        components=(
            ComponentSelection(component_key=ComponentKey.MAIN, mode="off"),
            ComponentSelection(component_key=ComponentKey.JUDGE, mode="observe"),
            ComponentSelection(component_key=ComponentKey.GUARD, mode="off"),
            ComponentSelection(component_key=ComponentKey.MAIN_GOVERNANCE, mode="off"),
            ComponentSelection(component_key=ComponentKey.RAG, mode="off"),
            ComponentSelection(component_key=ComponentKey.REPAIR, mode="off"),
        ),
    )
    actors = _actors()
    result = run_variant(variant, actors)
    assert result.was_called(ComponentKey.JUDGE) is True
    for key in ComponentKey:
        if key is ComponentKey.JUDGE:
            continue
        assert result.was_called(key) is False
        assert actors[key].calls == []
    assert actors[ComponentKey.JUDGE].calls == [(ComponentKey.JUDGE, "observe")]


def test_judge_only_enforce_calls_only_judge_with_enforce_mode() -> None:
    variant = VariantDescriptor(
        variant_id="judge-enforce-only",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),),
    )
    result = run_variant(variant, _actors())
    record = result.invocation(ComponentKey.JUDGE)
    assert record is not None
    assert record.called is True
    assert record.mutation_count == 1


def test_guard_only_observe_and_enforce_call_only_guard() -> None:
    for mode in ("observe", "enforce"):
        variant = VariantDescriptor(
            variant_id=f"guard-{mode}-only",
            components=(ComponentSelection(component_key=ComponentKey.GUARD, mode=mode),),
        )
        actors = _actors()
        result = run_variant(variant, actors)
        assert result.was_called(ComponentKey.GUARD) is True
        for key in ComponentKey:
            if key is ComponentKey.GUARD:
                continue
            assert result.was_called(key) is False


def test_main_governance_only_observe_calls_only_main_governance() -> None:
    variant = VariantDescriptor(
        variant_id="main-governance-observe-only",
        components=(
            ComponentSelection(component_key=ComponentKey.MAIN_GOVERNANCE, mode="observe"),
        ),
    )
    actors = _actors()
    result = run_variant(variant, actors)
    assert result.was_called(ComponentKey.MAIN_GOVERNANCE) is True
    for key in ComponentKey:
        if key is ComponentKey.MAIN_GOVERNANCE:
            continue
        assert result.was_called(key) is False


def test_main_governance_judge_and_repair_together_call_exactly_those_three() -> None:
    variant = VariantDescriptor(
        variant_id="governance-judge-repair",
        components=(
            ComponentSelection(component_key=ComponentKey.MAIN_GOVERNANCE, mode="enforce"),
            ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),
            ComponentSelection(component_key=ComponentKey.REPAIR, mode="enforce"),
            ComponentSelection(component_key=ComponentKey.GUARD, mode="off"),
            ComponentSelection(component_key=ComponentKey.RAG, mode="off"),
        ),
    )
    actors = _actors()
    result = run_variant(variant, actors)
    called = {key for key in ComponentKey if result.was_called(key)}
    assert called == {ComponentKey.MAIN_GOVERNANCE, ComponentKey.JUDGE, ComponentKey.REPAIR}


def test_rag_on_and_off_call_only_rag_and_are_independent_of_each_other() -> None:
    off_variant = VariantDescriptor(
        variant_id="rag-off",
        components=(ComponentSelection(component_key=ComponentKey.RAG, mode="off"),),
    )
    on_variant = VariantDescriptor(
        variant_id="rag-on",
        components=(ComponentSelection(component_key=ComponentKey.RAG, mode="enabled"),),
    )
    off_actors = _actors()
    on_actors = _actors()
    off_result = run_variant(off_variant, off_actors)
    on_result = run_variant(on_variant, on_actors)
    assert off_result.was_called(ComponentKey.RAG) is False
    assert on_result.was_called(ComponentKey.RAG) is True
    assert off_actors[ComponentKey.RAG].calls == []
    assert on_actors[ComponentKey.RAG].calls == [(ComponentKey.RAG, "enabled")]


def test_an_unregistered_actor_never_gets_called_and_is_reported_unsupported() -> None:
    """WU-C C3: 'unavailable/unsupported' Components must also show zero
    Call/Mutation/Evidence/Authority -- this Registry deliberately omits
    the JUDGE Actor entirely (as if unavailable in this environment)."""
    variant = VariantDescriptor(
        variant_id="judge-unsupported",
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode="enforce"),),
    )
    actors: dict[ComponentKey, FixtureActor] = {
        key: actor for key, actor in _actors().items() if key is not ComponentKey.JUDGE
    }
    result = run_variant(variant, actors)
    record = result.invocation(ComponentKey.JUDGE)
    assert record is not None
    assert record.called is False
    assert record.outcome == "unsupported"
    assert record.mutation_count == 0
    assert record.authority_exercised is False


def test_an_absent_component_reports_absent_never_off() -> None:
    variant = VariantDescriptor(variant_id="main-only", components=())
    result = run_variant(variant, _actors())
    record = result.invocation(ComponentKey.MAIN)
    assert record is not None
    assert record.called is False
    assert record.outcome == "absent"


def test_a_present_component_with_mode_none_is_call_zero_never_called() -> None:
    """R1-WU-02 (IR-P9-2-07 fix): a *present* `ComponentSelection` whose
    `mode` was left `None` (the field's own documented default meaning,
    `identity.py`'s `ComponentSelection` docstring: "None means this
    Component is OFF/absent for this Variant") must be Call 0, exactly
    like an explicit `mode="off"` -- the Controller's Independent Review
    reproduced a real violation where such a Selection reached a live
    Actor call."""
    variant = VariantDescriptor(
        variant_id="main-present-mode-none",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    actors = _actors()
    result = run_variant(variant, actors)
    record = result.invocation(ComponentKey.MAIN)
    assert record is not None
    assert record.called is False
    assert record.outcome == "off"
    assert record.mutation_count == 0
    assert record.evidence_count == 0
    assert record.authority_exercised is False
    assert actors[ComponentKey.MAIN].calls == []
