"""Phase 9-2 WU-C C4: Multiple-Definition Conflict/Suppression/Routing/
Repair-Propagation."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.adapters.experiment.fixture_actor_adapters import (
    DynamicRoutingStrategy,
    ManualRoutingStrategy,
    StaticRoutingStrategy,
)
from margpa_runtime_llm.modules.experiment.domain.composition import (
    DefinitionVerdict,
    DefinitionVerdictOutcome,
    RepairOrigin,
    RoutingStrategyKind,
    resolve_governance_composition,
)
from margpa_runtime_llm.modules.experiment.domain.errors import (
    ExperimentCoreError,
    ExperimentCoreErrorCode,
)

_VERDICTS = (
    DefinitionVerdict(
        definition_id="def-a", outcome=DefinitionVerdictOutcome.MATCH, authority_weight=1
    ),
    DefinitionVerdict(
        definition_id="def-b", outcome=DefinitionVerdictOutcome.MATCH, authority_weight=5
    ),
    DefinitionVerdict(definition_id="def-c", outcome=DefinitionVerdictOutcome.CONFLICT),
    DefinitionVerdict(definition_id="def-d", outcome=DefinitionVerdictOutcome.NO_MATCH),
)


def test_conflicts_are_reported_regardless_of_routing_strategy() -> None:
    for routing in (
        ManualRoutingStrategy(manual_selection_ids=("def-a",)),
        StaticRoutingStrategy(),
        DynamicRoutingStrategy(),
    ):
        result = resolve_governance_composition(
            verdicts=_VERDICTS,
            routing=routing,
            repair_requested_by=None,
            registered_actors=frozenset(),
        )
        assert result.conflicts == ("def-c",)
        assert "def-d" not in result.selected
        assert "def-d" not in result.suppressed
        assert "def-d" not in result.conflicts


def test_manual_routing_selects_exactly_the_declared_ids() -> None:
    routing = ManualRoutingStrategy(manual_selection_ids=("def-a",))
    result = resolve_governance_composition(
        verdicts=_VERDICTS,
        routing=routing,
        repair_requested_by=None,
        registered_actors=frozenset(),
    )
    assert result.routing_strategy_used is RoutingStrategyKind.MANUAL
    assert result.selected == ("def-a",)
    assert result.suppressed == ("def-b",)


def test_static_routing_selects_every_match_and_suppresses_none() -> None:
    routing = StaticRoutingStrategy()
    result = resolve_governance_composition(
        verdicts=_VERDICTS,
        routing=routing,
        repair_requested_by=None,
        registered_actors=frozenset(),
    )
    assert result.routing_strategy_used is RoutingStrategyKind.STATIC
    assert set(result.selected) == {"def-a", "def-b"}
    assert result.suppressed == ()


def test_dynamic_routing_selects_only_the_highest_authority_weight_match() -> None:
    routing = DynamicRoutingStrategy()
    result = resolve_governance_composition(
        verdicts=_VERDICTS,
        routing=routing,
        repair_requested_by=None,
        registered_actors=frozenset(),
    )
    assert result.routing_strategy_used is RoutingStrategyKind.DYNAMIC
    assert result.selected == ("def-b",)
    assert result.suppressed == ("def-a",)


@pytest.mark.parametrize("actor", ["judge", "main_governance", "judge_and_main"])
def test_implicitly_registered_repair_actors_are_accepted(actor: str) -> None:
    routing = StaticRoutingStrategy()
    result = resolve_governance_composition(
        verdicts=(), routing=routing, repair_requested_by=actor, registered_actors=frozenset()
    )
    assert result.repair_propagation is RepairOrigin(actor)


def test_an_explicitly_registered_other_actor_is_accepted_as_other_registered_actor() -> None:
    routing = StaticRoutingStrategy()
    result = resolve_governance_composition(
        verdicts=(),
        routing=routing,
        repair_requested_by="custom_definition_actor",
        registered_actors=frozenset({"custom_definition_actor"}),
    )
    assert result.repair_propagation is RepairOrigin.OTHER_REGISTERED_ACTOR


def test_an_unregistered_repair_actor_is_rejected_never_auto_authorized() -> None:
    routing = StaticRoutingStrategy()
    with pytest.raises(ExperimentCoreError) as excinfo:
        resolve_governance_composition(
            verdicts=(),
            routing=routing,
            repair_requested_by="totally_unregistered_actor",
            registered_actors=frozenset({"custom_definition_actor"}),
        )
    assert excinfo.value.code is ExperimentCoreErrorCode.UNREGISTERED_REPAIR_ACTOR
