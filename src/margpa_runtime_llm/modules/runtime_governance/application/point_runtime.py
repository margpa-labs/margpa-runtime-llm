"""Governance Point Runtime (architecture §4, P4-D-WU-001, P4-PNT-001..006,
P4-CODEX-011 Rework).

`GovernancePointRuntime.invoke()` is the single Mode-routing entry point
every `main_model.pre`/`post` call goes through:

- `off`   — never calls the Evaluator or Action Resolver; the returned
            Result is the only trace this Point was even wired in
            (P4-MOD-002).
- `observe` — Caller now Binds for `observe` too (P4-CODEX-011 §1.1) so
              `binding_digest_sha512`/Source Plan Identity are real, not
              `None`, in a Valid-Bundle Observe Result/Evidence — but
              still never calls the Action Resolver, so
              `executed_actions` is always empty (P4-MOD-003, ADR-4-007
              "Observeは絶対に非介入"). Zero bound Descriptors short-
              circuits to `INACTIVE_NO_DEFINITIONS` *before* the
              Evaluator runs — a Core-only structural check firing on
              the Definitions-0 Baseline would contradict the Frozen
              Acceptance Matrix (P4-CODEX-004). A non-`None` but
              non-executable Binding (Stale/Unavailable — P4-CODEX-011
              §1.1 "valid definitions + stale binding + observe") also
              short-circuits before the Evaluator, converging to the
              same Typed states `enforce` already uses, carrying the
              Binding's own real `unavailable_reason_code` rather than a
              single hardcoded string.
- `enforce` — requires a `binding.executable` Binding; if one is not
              present the Result is `UNAVAILABLE` (with the Binding's own
              `unavailable_reason_code`), never silently downgraded to
              `observe` (P4-MOD-004/005). Zero bound Descriptors already
              makes a Binding non-executable (`application/binder.py`),
              so this same branch also covers `Definitions 0 + enforce`.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from ..domain import (
    BoundGovernancePlan,
    BudgetSnapshot,
    Deviation,
    ExecutedAction,
    ExecutionDescriptor,
    ExecutionState,
    Observation,
    ObservationOutcome,
    RecommendedAction,
    Severity,
    StandardGovernanceResult,
)
from ..ports import DeterministicEvaluatorPort

_DEFAULT_DEVIATION_ACTION_ID = "warn"

ActionResolverCallable = Callable[[tuple[RecommendedAction, ...]], tuple[ExecutedAction, ...]]


class GovernancePointRuntime:
    def __init__(self, *, evaluator: DeterministicEvaluatorPort) -> None:
        self._evaluator = evaluator

    def invoke(
        self,
        *,
        invocation_id: str,
        point_id: str,
        stage: str,
        mode: str,
        snapshot: str,
        binding: BoundGovernancePlan | None,
        descriptors: tuple[ExecutionDescriptor, ...],
        budget: BudgetSnapshot,
        resolve_actions: ActionResolverCallable | None = None,
    ) -> StandardGovernanceResult:
        if mode == "off":
            return StandardGovernanceResult(
                invocation_id=invocation_id,
                point_id=point_id,
                stage=stage,
                mode=mode,
                execution_state=ExecutionState.NOT_EVALUATED,
            )
        if binding is not None and not binding.executable:
            # A Binding was actually attempted for this Invocation
            # (either Mode now Binds, P4-CODEX-011) but came back
            # non-executable — never silently fall through to the
            # Evaluator regardless of Mode. Zero Descriptors keeps each
            # Mode's own existing `execution_state` name
            # (`unavailable`/`inactive_no_definitions`), but the Safe
            # Reason always comes from the Binding itself
            # (`no_provider`/`provider_failure`/`invalid_bundle`/
            # `no_definitions`/`no_source_plan`/`unresolved_dependency`/
            # `registry_or_authority_empty`) — never collapsed to one
            # hardcoded string (P4-CODEX-011 §1.1).
            execution_state = (
                ExecutionState.UNAVAILABLE
                if mode == "enforce" or descriptors
                else ExecutionState.INACTIVE_NO_DEFINITIONS
            )
            return StandardGovernanceResult(
                invocation_id=invocation_id,
                point_id=point_id,
                stage=stage,
                mode=mode,
                execution_state=execution_state,
                unavailable_reason_code=binding.unavailable_reason_code,
                binding_digest_sha512=binding.binding_digest_sha512,
            )
        if mode == "enforce" and binding is None:
            return StandardGovernanceResult(
                invocation_id=invocation_id,
                point_id=point_id,
                stage=stage,
                mode=mode,
                execution_state=ExecutionState.UNAVAILABLE,
                unavailable_reason_code="binding_missing",
            )
        if not descriptors:
            # Only reachable here with `binding is None` (a caller that
            # never wires a Binding at all for `observe`) — a non-`None`
            # Binding with empty Descriptors is always non-executable
            # (`application/binder.py`) and was already handled above.
            return StandardGovernanceResult(
                invocation_id=invocation_id,
                point_id=point_id,
                stage=stage,
                mode=mode,
                execution_state=ExecutionState.INACTIVE_NO_DEFINITIONS,
                unavailable_reason_code="no_definitions",
            )

        started = time.monotonic()
        observations = self._evaluator.evaluate(
            descriptors=descriptors, stage=stage, snapshot=snapshot, budget=budget
        )
        deviations, recommended = _derive(observations)
        severity = _max_severity(deviations)

        executed_actions: tuple[ExecutedAction, ...] = ()
        if mode == "enforce" and resolve_actions is not None:
            executed_actions = resolve_actions(recommended)

        latency_ms = max(0, round((time.monotonic() - started) * 1000))
        return StandardGovernanceResult(
            invocation_id=invocation_id,
            point_id=point_id,
            stage=stage,
            mode=mode,
            execution_state=ExecutionState.EVALUATED,
            binding_digest_sha512=(binding.binding_digest_sha512 if binding is not None else None),
            selected_descriptor_ids=tuple(descriptor.descriptor_id for descriptor in descriptors),
            observations=observations,
            deviations=deviations,
            severity=severity,
            recommended_actions=recommended,
            executed_actions=executed_actions,
            latency_ms=latency_ms,
            call_count=0,
        )


def _derive(
    observations: tuple[Observation, ...],
) -> tuple[tuple[Deviation, ...], tuple[RecommendedAction, ...]]:
    deviations: list[Deviation] = []
    recommended: list[RecommendedAction] = []
    for observation in observations:
        if observation.outcome is not ObservationOutcome.DEVIATION:
            continue
        detail_code = observation.detail_code or "deviation"
        deviations.append(
            Deviation(
                descriptor_id=observation.descriptor_id,
                severity=observation.severity,
                detail_code=detail_code,
                recommended_action_id=observation.recommended_action_id,
            )
        )
        recommended.append(
            RecommendedAction(
                action_id=observation.recommended_action_id or _DEFAULT_DEVIATION_ACTION_ID,
                reason_descriptor_id=observation.descriptor_id,
                severity=observation.severity,
            )
        )
    return tuple(deviations), tuple(recommended)


_SEVERITY_ORDER = (Severity.NONE, Severity.LOW, Severity.MODERATE, Severity.HIGH, Severity.CRITICAL)


def _max_severity(deviations: tuple[Deviation, ...]) -> Severity:
    highest = Severity.NONE
    for deviation in deviations:
        if _SEVERITY_ORDER.index(deviation.severity) > _SEVERITY_ORDER.index(highest):
            highest = deviation.severity
    return highest
