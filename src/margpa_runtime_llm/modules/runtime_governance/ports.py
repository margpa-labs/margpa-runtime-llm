"""Replaceable ports for runtime governance (architecture §2/§11).

`DeterministicEvaluatorPort` and `ActionAdapterPort` are the two seams a
Trusted Adapter or a future Phase 5/6 component plugs into — Core
(`application/`) depends only on these Protocols, never on a concrete
evaluator or action implementation.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .domain import (
    BudgetSnapshot,
    ExecutedAction,
    ExecutionDescriptor,
    Observation,
    SemanticEvaluationRequest,
    SemanticEvaluationResponse,
)


@runtime_checkable
class DeterministicEvaluatorPort(Protocol):
    """Evaluates a finite set of `ExecutionDescriptor`s against one
    snapshot of Governance Point input (pre-generation request fields or
    post-generation canonical text) without any additional Model Call
    (P4-EVL-001/003).

    `snapshot` is stage-shaped: for `stage="pre"` it is a small canonical
    JSON projection of the outgoing request (message/char counts,
    thinking mode, generation-config field names); for `stage="post"` it
    is the raw canonical final text. `descriptors` are recorded for
    traceability only — Phase 4 has no Semantic Evaluator, so every
    `REQUIRES_SEMANTIC_EVALUATOR` descriptor always yields a `deferred_to_
    semantic_evaluator` Observation, never a fabricated pass/fail
    (P4-EVL-005)."""

    def evaluate(
        self,
        *,
        descriptors: tuple[ExecutionDescriptor, ...],
        stage: str,
        snapshot: str,
        budget: BudgetSnapshot,
    ) -> tuple[Observation, ...]: ...


@runtime_checkable
class ActionAdapterPort(Protocol):
    """One registered Action Adapter (architecture §9/§31). `execute()`
    never raises for a routine refusal — it returns an `ExecutedAction`
    with `executed=False` and a Typed reason; only a genuine adapter
    fault may raise, and callers must never record that as success."""

    def execute(self, *, action_id: str, point_id: str, stage: str) -> ExecutedAction: ...


@runtime_checkable
class SemanticEvaluatorPort(Protocol):
    """Evaluates normalized criteria with one explicitly selected provider."""

    def evaluate(self, *, request: SemanticEvaluationRequest) -> SemanticEvaluationResponse: ...
