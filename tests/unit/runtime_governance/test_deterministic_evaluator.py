"""Deterministic Evaluator: structural checks vs. Semantic Deferral
(P4-C-WU-003, P4-EVL-001..005)."""

from __future__ import annotations

import json

from margpa_runtime_llm.adapters.runtime_governance.deterministic_evaluator import (
    DeterministicEvaluator,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    STAGE_POST,
    STAGE_PRE,
    BudgetSnapshot,
    EvaluationMethod,
    ExecutionDescriptor,
    ObservationOutcome,
    Severity,
)


def _budget(**overrides: object) -> BudgetSnapshot:
    base = {
        "max_calls_per_invocation": 0,
        "max_latency_ms": 1000,
        "max_snapshot_chars": 0,
        "allowed_generation_config_fields": (),
    }
    base.update(overrides)
    return BudgetSnapshot(**base)  # type: ignore[arg-type]


def _descriptor(descriptor_id: str = "argd.rule-1") -> ExecutionDescriptor:
    return ExecutionDescriptor(
        descriptor_id=descriptor_id,
        source_definition_id="argd",
        source_pointer="$.argd",
        summary="qualitative rule",
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
    )


def test_every_descriptor_is_deferred_never_fabricated_pass_or_fail() -> None:
    evaluator = DeterministicEvaluator()
    observations = evaluator.evaluate(
        descriptors=(_descriptor("argd.a"), _descriptor("argd.b")),
        stage=STAGE_POST,
        snapshot="a real, non-empty answer",
        budget=_budget(),
    )
    deferred = [o for o in observations if o.descriptor_id in {"argd.a", "argd.b"}]
    assert len(deferred) == 2
    assert all(o.outcome is ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR for o in deferred)


def test_empty_output_is_a_high_severity_deviation_recommending_reject() -> None:
    evaluator = DeterministicEvaluator()
    observations = evaluator.evaluate(
        descriptors=(), stage=STAGE_POST, snapshot="   ", budget=_budget()
    )
    assert len(observations) == 1
    assert observations[0].outcome is ObservationOutcome.DEVIATION
    assert observations[0].detail_code == "empty_output"
    assert observations[0].severity is Severity.HIGH
    assert observations[0].recommended_action_id == "reject_output"


def test_non_empty_output_within_budget_produces_no_structural_deviation() -> None:
    evaluator = DeterministicEvaluator()
    observations = evaluator.evaluate(
        descriptors=(), stage=STAGE_POST, snapshot="a fine answer", budget=_budget()
    )
    assert observations == ()


def test_oversized_output_is_a_deviation_when_budget_is_set() -> None:
    evaluator = DeterministicEvaluator()
    observations = evaluator.evaluate(
        descriptors=(),
        stage=STAGE_POST,
        snapshot="x" * 100,
        budget=_budget(max_snapshot_chars=10),
    )
    assert len(observations) == 1
    assert observations[0].detail_code == "output_exceeds_budget"
    assert observations[0].recommended_action_id == "reject_output"


def test_zero_budget_means_unbounded_no_size_deviation() -> None:
    evaluator = DeterministicEvaluator()
    observations = evaluator.evaluate(
        descriptors=(),
        stage=STAGE_POST,
        snapshot="x" * 100_000,
        budget=_budget(max_snapshot_chars=0),
    )
    assert observations == ()


def test_oversized_request_is_a_pre_stage_deviation() -> None:
    evaluator = DeterministicEvaluator()
    snapshot = json.dumps({"total_chars": 500, "generation_config_fields": []})
    observations = evaluator.evaluate(
        descriptors=(), stage=STAGE_PRE, snapshot=snapshot, budget=_budget(max_snapshot_chars=100)
    )
    assert len(observations) == 1
    assert observations[0].detail_code == "request_exceeds_budget"
    assert observations[0].recommended_action_id == "stop_before_generation"


def test_disallowed_generation_config_field_is_a_pre_stage_deviation() -> None:
    evaluator = DeterministicEvaluator()
    snapshot = json.dumps({"total_chars": 5, "generation_config_fields": ["temperature", "seed"]})
    observations = evaluator.evaluate(
        descriptors=(),
        stage=STAGE_PRE,
        snapshot=snapshot,
        budget=_budget(allowed_generation_config_fields=("temperature",)),
    )
    assert len(observations) == 1
    assert observations[0].detail_code == "disallowed_config_field"
    assert observations[0].recommended_action_id == "constrain_generation_config"


def test_malformed_pre_snapshot_fails_closed_to_no_structural_observation() -> None:
    evaluator = DeterministicEvaluator()
    observations = evaluator.evaluate(
        descriptors=(), stage=STAGE_PRE, snapshot="not json", budget=_budget(max_snapshot_chars=1)
    )
    assert observations == ()
