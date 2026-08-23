"""Deterministic Evaluator (ADR-4-004, P4-C-WU-003, P4-EVL-001..005).

Two honest, separate concerns:

1. Every input `ExecutionDescriptor` (ARGD/DAGD-sourced, via the
   Reference Adapter) is recorded as `deferred_to_semantic_evaluator` —
   Phase 4 has no Semantic Evaluator wired, so a qualitative rule like
   "do not hallucinate" is never scored `pass` or `deviation` here
   (P4-EVL-005: Unsupported/Ambiguous Rules must never become Pass).
2. A small, fixed set of Core-owned *structural* checks — genuinely
   computable without a Model — run independently of any Definition:
   empty/oversized output, oversized request, and disallowed generation-
   config fields. These are the only checks that can ever produce a real
   `deviation` Observation in Phase 4.
"""

from __future__ import annotations

import json

from margpa_runtime_llm.modules.runtime_governance.domain import (
    STAGE_POST,
    STAGE_PRE,
    BudgetSnapshot,
    EvaluationMethod,
    ExecutionDescriptor,
    Observation,
    ObservationOutcome,
    Severity,
)

_EMPTY_OUTPUT_DESCRIPTOR_ID = "core.structural.empty_output"
_OUTPUT_BUDGET_DESCRIPTOR_ID = "core.structural.output_size_budget"
_REQUEST_BUDGET_DESCRIPTOR_ID = "core.structural.request_size_budget"
_CONFIG_ALLOWLIST_DESCRIPTOR_ID = "core.structural.generation_config_allowlist"


class DeterministicEvaluator:
    def evaluate(
        self,
        *,
        descriptors: tuple[ExecutionDescriptor, ...],
        stage: str,
        snapshot: str,
        budget: BudgetSnapshot,
    ) -> tuple[Observation, ...]:
        observations: list[Observation] = [_deferred(descriptor) for descriptor in descriptors]
        if stage == STAGE_PRE:
            observations.extend(_evaluate_pre(snapshot, budget))
        elif stage == STAGE_POST:
            observations.extend(_evaluate_post(snapshot, budget))
        return tuple(observations)


def _deferred(descriptor: ExecutionDescriptor) -> Observation:
    if descriptor.evaluation_method is EvaluationMethod.DETERMINISTIC:
        # Reserved for a future Trusted Adapter that emits a genuinely
        # deterministic Descriptor; Phase 4's Reference Adapter never
        # marks one this way (P4-GD-002/003), so this path is presently
        # unreachable but must not silently mis-observe if it ever is.
        return Observation(
            descriptor_id=descriptor.descriptor_id,
            evaluation_method=EvaluationMethod.DETERMINISTIC.value,
            outcome=ObservationOutcome.PASS,
        )
    return Observation(
        descriptor_id=descriptor.descriptor_id,
        evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR.value,
        outcome=ObservationOutcome.DEFERRED_TO_SEMANTIC_EVALUATOR,
    )


def _evaluate_pre(snapshot: str, budget: BudgetSnapshot) -> list[Observation]:
    observations: list[Observation] = []
    try:
        parsed = json.loads(snapshot) if snapshot else {}
    except ValueError:
        return observations
    if not isinstance(parsed, dict):
        return observations

    total_chars = parsed.get("total_chars")
    if (
        budget.max_snapshot_chars > 0
        and isinstance(total_chars, int)
        and total_chars > budget.max_snapshot_chars
    ):
        observations.append(
            Observation(
                descriptor_id=_REQUEST_BUDGET_DESCRIPTOR_ID,
                evaluation_method=EvaluationMethod.DETERMINISTIC.value,
                outcome=ObservationOutcome.DEVIATION,
                detail_code="request_exceeds_budget",
                severity=Severity.MODERATE,
                recommended_action_id="stop_before_generation",
            )
        )

    config_fields = parsed.get("generation_config_fields")
    if budget.allowed_generation_config_fields and isinstance(config_fields, list):
        disallowed = {
            field
            for field in config_fields
            if isinstance(field, str) and field not in budget.allowed_generation_config_fields
        }
        if disallowed:
            observations.append(
                Observation(
                    descriptor_id=_CONFIG_ALLOWLIST_DESCRIPTOR_ID,
                    evaluation_method=EvaluationMethod.DETERMINISTIC.value,
                    outcome=ObservationOutcome.DEVIATION,
                    detail_code="disallowed_config_field",
                    severity=Severity.MODERATE,
                    recommended_action_id="constrain_generation_config",
                )
            )
    return observations


def _evaluate_post(snapshot: str, budget: BudgetSnapshot) -> list[Observation]:
    observations: list[Observation] = []
    if snapshot.strip() == "":
        observations.append(
            Observation(
                descriptor_id=_EMPTY_OUTPUT_DESCRIPTOR_ID,
                evaluation_method=EvaluationMethod.DETERMINISTIC.value,
                outcome=ObservationOutcome.DEVIATION,
                detail_code="empty_output",
                severity=Severity.HIGH,
                recommended_action_id="reject_output",
            )
        )
    if budget.max_snapshot_chars > 0 and len(snapshot) > budget.max_snapshot_chars:
        observations.append(
            Observation(
                descriptor_id=_OUTPUT_BUDGET_DESCRIPTOR_ID,
                evaluation_method=EvaluationMethod.DETERMINISTIC.value,
                outcome=ObservationOutcome.DEVIATION,
                detail_code="output_exceeds_budget",
                severity=Severity.MODERATE,
                recommended_action_id="reject_output",
            )
        )
    return observations
