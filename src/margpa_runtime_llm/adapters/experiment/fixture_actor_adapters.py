"""Fixture `ActorPort`/`RoutingStrategyPort` Adapters (Phase 9-2, WU-C C2/C3/C4).

Deterministic, in-memory, real-Model-free -- these are what the
Independence Matrix (C3) and Conflict/Routing comparison (C4) run
against ("全MatrixはFixture中心"). A real Production Adapter wrapping the
actual `judge_live_integration.py`/`guardrail_governance`/etc. entry
points is a distinct, separate Adapter reserved for the WU-F bounded
real-Model gate -- it is not this file's concern."""

from __future__ import annotations

from dataclasses import dataclass, field

from margpa_runtime_llm.modules.experiment.domain.composition import (
    ActorInvocationRecord,
    DefinitionVerdict,
    RoutingStrategyKind,
)
from margpa_runtime_llm.modules.experiment.domain.identity import ComponentKey


@dataclass
class FixtureActor:
    """One configurable, call-recording `ActorPort` implementation. Every
    real call this Actor receives (never one the Runner skipped) is
    appended to `calls`, so a test can assert exactly how many times --
    and with what `mode` -- this specific Component's Actor was really
    invoked for a given Variant."""

    mutation_count: int = 0
    evidence_count: int = 0
    authority_exercised: bool = False
    outcome: str = "completed"
    calls: list[tuple[ComponentKey, str | None]] = field(default_factory=list)

    def invoke(self, *, component_key: ComponentKey, mode: str | None) -> ActorInvocationRecord:
        self.calls.append((component_key, mode))
        return ActorInvocationRecord(
            component_key=component_key,
            called=True,
            mutation_count=self.mutation_count,
            evidence_count=self.evidence_count,
            authority_exercised=self.authority_exercised,
            outcome=self.outcome,
        )


@dataclass
class ManualRoutingStrategy:
    """WU-C C4: Manual Routing selects exactly the caller-declared
    `manual_selection_ids`, in whatever order they were given -- a real
    Human/Config decision replayed verbatim, never re-derived."""

    manual_selection_ids: tuple[str, ...]
    kind: RoutingStrategyKind = RoutingStrategyKind.MANUAL

    def select(
        self, matches: tuple[DefinitionVerdict, ...]
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        match_ids = {verdict.definition_id for verdict in matches}
        selected = tuple(item for item in self.manual_selection_ids if item in match_ids)
        suppressed = tuple(item for item in match_ids if item not in selected)
        return selected, suppressed


@dataclass
class StaticRoutingStrategy:
    """WU-C C4: Static Routing selects every real `MATCH` Definition,
    suppressing none -- a fixed, config-time policy rather than a
    per-Run decision."""

    kind: RoutingStrategyKind = RoutingStrategyKind.STATIC

    def select(
        self, matches: tuple[DefinitionVerdict, ...]
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        return tuple(verdict.definition_id for verdict in matches), ()


@dataclass
class DynamicRoutingStrategy:
    """WU-C C4: Dynamic Routing selects only the single highest-
    `authority_weight` real `MATCH` Definition (ties broken by
    `definition_id` for determinism), suppressing the rest -- a
    per-Run, Evidence-driven decision, distinct from both Manual and
    Static."""

    kind: RoutingStrategyKind = RoutingStrategyKind.DYNAMIC

    def select(
        self, matches: tuple[DefinitionVerdict, ...]
    ) -> tuple[tuple[str, ...], tuple[str, ...]]:
        if not matches:
            return (), ()
        winner = max(
            matches, key=lambda verdict: (verdict.authority_weight, verdict.definition_id)
        )
        suppressed = tuple(
            verdict.definition_id
            for verdict in matches
            if verdict.definition_id != winner.definition_id
        )
        return (winner.definition_id,), suppressed
