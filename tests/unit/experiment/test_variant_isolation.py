"""Phase 9-2 WU-C C5: Variant Isolation.

Fixture-level concurrency check: two Variants run through
`run_variant()` with distinct `FixtureActor` registries must never
observe or report each other's calls/outcomes -- verified both for
sequential execution and for genuinely interleaved execution via a
`ThreadPoolExecutor` (Real-Model Variants remain sequential per Handoff
§4.4; this test only proves the Runner itself introduces no shared
mutable state that could leak between concurrently-driven Variants)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from margpa_runtime_llm.adapters.experiment.fixture_actor_adapters import FixtureActor
from margpa_runtime_llm.modules.experiment.application.composition_runner import run_variant
from margpa_runtime_llm.modules.experiment.domain.composition import VariantExecutionResult
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    VariantDescriptor,
)


def _variant(variant_id: str, judge_mode: str) -> VariantDescriptor:
    return VariantDescriptor(
        variant_id=variant_id,
        components=(ComponentSelection(component_key=ComponentKey.JUDGE, mode=judge_mode),),
    )


def test_sequential_variants_use_independent_actor_state() -> None:
    variant_a = _variant("variant-a", "observe")
    variant_b = _variant("variant-b", "enforce")
    judge_a = FixtureActor(outcome="a-outcome")
    judge_b = FixtureActor(outcome="b-outcome")

    result_a = run_variant(variant_a, {ComponentKey.JUDGE: judge_a})
    result_b = run_variant(variant_b, {ComponentKey.JUDGE: judge_b})

    assert result_a.variant_id == "variant-a"
    assert result_b.variant_id == "variant-b"
    assert result_a.invocation(ComponentKey.JUDGE).outcome == "a-outcome"  # type: ignore[union-attr]
    assert result_b.invocation(ComponentKey.JUDGE).outcome == "b-outcome"  # type: ignore[union-attr]
    assert judge_a.calls == [(ComponentKey.JUDGE, "observe")]
    assert judge_b.calls == [(ComponentKey.JUDGE, "enforce")]


def test_concurrently_driven_variants_never_cross_contaminate_evidence() -> None:
    """Runs 20 independent Variant/Actor pairs through a Thread Pool --
    each Variant's own FixtureActor must show exactly one call carrying
    that Variant's own mode, never another Variant's."""
    pairs = [(f"variant-{i}", "observe" if i % 2 == 0 else "enforce") for i in range(20)]
    actors = {variant_id: FixtureActor(outcome=f"outcome-{variant_id}") for variant_id, _ in pairs}

    def _run(pair: tuple[str, str]) -> tuple[str, VariantExecutionResult]:
        variant_id, mode = pair
        variant = _variant(variant_id, mode)
        result = run_variant(variant, {ComponentKey.JUDGE: actors[variant_id]})
        return variant_id, result

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = dict(pool.map(_run, pairs))

    for variant_id, mode in pairs:
        result = results[variant_id]
        assert result.variant_id == variant_id
        record = result.invocation(ComponentKey.JUDGE)
        assert record is not None
        assert record.outcome == f"outcome-{variant_id}"
        actor = actors[variant_id]
        assert actor.calls == [(ComponentKey.JUDGE, mode)]
