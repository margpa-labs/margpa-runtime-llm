"""Phase 9-2 R1-WU-03: Production Turn Variant Adapter projection layer.

Fixture-free but Model-free too -- a `FakeProductionTurnPort` stands in for
the real Bootstrap-layer Adapter, so these tests verify the projection logic
itself (`run_production_turn_variant`) without ever touching a real Model."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from margpa_runtime_llm.modules.experiment.application.production_turn_runner import (
    ProductionTurnObservation,
    run_production_turn_variant,
)
from margpa_runtime_llm.modules.experiment.domain.identity import ComponentKey


@dataclass
class FakeProductionTurnPort:
    observation: ProductionTurnObservation
    calls: list[str] = field(default_factory=list)

    def run_turn(
        self, *, user_input: str, on_request_id: Callable[[str], None] | None = None
    ) -> ProductionTurnObservation:
        self.calls.append(user_input)
        if on_request_id is not None:
            on_request_id(self.observation.request_id)
        return self.observation


def test_a_main_only_turn_reports_only_main_called() -> None:
    port = FakeProductionTurnPort(
        ProductionTurnObservation(
            request_id="real-req-1",
            main_called=True,
            main_outcome="completed",
            judge_called=False,
            judge_outcome="off",
            guard_called=False,
            guard_outcome="off",
            repair_called=False,
            repair_outcome="off",
            repair_adopted=None,
            final_disposition="candidate_accepted",
            assistant_content="Paris.",
        )
    )
    execution = run_production_turn_variant(port=port, user_input="What is the capital of France?")
    by_key = {record.component_key: record for record in execution.invocations}
    assert by_key[ComponentKey.MAIN].called is True
    assert by_key[ComponentKey.MAIN].outcome == "completed"
    assert by_key[ComponentKey.JUDGE].called is False
    assert by_key[ComponentKey.JUDGE].outcome == "off"
    assert by_key[ComponentKey.GUARD].called is False
    assert by_key[ComponentKey.REPAIR].called is False
    assert execution.observation.request_id == "real-req-1"
    assert port.calls == ["What is the capital of France?"]


def test_a_main_plus_judge_turn_reports_both_called() -> None:
    port = FakeProductionTurnPort(
        ProductionTurnObservation(
            request_id="real-req-2",
            main_called=True,
            main_outcome="completed",
            judge_called=True,
            judge_outcome="pass",
            guard_called=False,
            guard_outcome="off",
            repair_called=False,
            repair_outcome="off",
            repair_adopted=None,
            final_disposition="candidate_accepted",
            assistant_content="Paris.",
        )
    )
    execution = run_production_turn_variant(port=port, user_input="x")
    by_key = {record.component_key: record for record in execution.invocations}
    assert by_key[ComponentKey.MAIN].called is True
    assert by_key[ComponentKey.JUDGE].called is True
    assert by_key[ComponentKey.JUDGE].outcome == "pass"
    assert by_key[ComponentKey.GUARD].called is False


def test_a_called_false_record_always_reports_zero_mutation_evidence_authority() -> None:
    """Same Invariant `ActorInvocationRecord` itself enforces for Fixture
    Runs (WU-C C3) must hold for Production-derived records too."""
    port = FakeProductionTurnPort(
        ProductionTurnObservation(
            request_id="real-req-3",
            main_called=True,
            main_outcome="completed",
            judge_called=False,
            judge_outcome="off",
            guard_called=False,
            guard_outcome="off",
            repair_called=False,
            repair_outcome="off",
            repair_adopted=None,
            final_disposition="candidate_accepted",
            assistant_content=None,
        )
    )
    execution = run_production_turn_variant(port=port, user_input="x")
    for record in execution.invocations:
        # R3-WU-02: a CONFIRMED non-call (`called=False`) must report
        # exactly zero of each; a genuinely UNOBSERVED one (`called=None`)
        # must report `None` for each -- never conflated.
        if record.called is False:
            assert record.mutation_count == 0
            assert record.evidence_count == 0
            assert record.authority_exercised is False
        elif record.called is None:
            assert record.mutation_count is None
            assert record.evidence_count is None
            assert record.authority_exercised is None


def test_on_request_id_callback_is_forwarded_to_the_port() -> None:
    """R1-WU-05: `ExperimentRunWorker` registers a real Cancel hook via
    this callback, as soon as the real request_id is known -- before the
    Turn finishes, not only after."""
    port = FakeProductionTurnPort(
        ProductionTurnObservation(
            request_id="real-req-5",
            main_called=True,
            main_outcome="completed",
            judge_called=False,
            judge_outcome="off",
            guard_called=False,
            guard_outcome="off",
            repair_called=False,
            repair_outcome="off",
            repair_adopted=None,
            final_disposition="candidate_accepted",
            assistant_content="x",
        )
    )
    observed: list[str] = []
    run_production_turn_variant(port=port, user_input="x", on_request_id=observed.append)
    assert observed == ["real-req-5"]


def test_unmodeled_components_are_reported_not_observed_never_off() -> None:
    """R1-WU-03 / R2-WU-02 / R3-WU-02: this Round's Production Adapter has
    no real per-Component Evidence source for Main Governance/Definition
    Set/RAG/Recording/Presentation -- reporting them as `off` would
    falsely claim a verified absence; `not_observed` is the honest,
    distinct outcome (R2-WU-02 renamed this from R1's `not_applicable`).
    R3-WU-02 additionally upgrades `called` itself from R2's confirmed
    `False` to the honest `None` (IR-P9-2-R2-04 fix) -- a `bool` `False`
    alongside an `outcome="not_observed"` string was its own internal
    contradiction (a verified absence AND an admission of never having
    observed it, at once)."""
    port = FakeProductionTurnPort(
        ProductionTurnObservation(
            request_id="real-req-4",
            main_called=True,
            main_outcome="completed",
            judge_called=False,
            judge_outcome="off",
            guard_called=False,
            guard_outcome="off",
            repair_called=False,
            repair_outcome="off",
            repair_adopted=None,
            final_disposition="candidate_accepted",
            assistant_content="x",
        )
    )
    execution = run_production_turn_variant(port=port, user_input="x")
    by_key = {record.component_key: record for record in execution.invocations}
    for key in (
        ComponentKey.MAIN_GOVERNANCE,
        ComponentKey.DEFINITION_SET,
        ComponentKey.RAG,
        ComponentKey.RECORDING,
        ComponentKey.PRESENTATION,
    ):
        assert by_key[key].called is None
        assert by_key[key].mutation_count is None
        assert by_key[key].evidence_count is None
        assert by_key[key].authority_exercised is None
        assert by_key[key].outcome == "not_observed"
