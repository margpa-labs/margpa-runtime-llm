"""DimensionResult/EvaluationResult (Architecture 6.1)."""

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identifiers import EvaluationExecutionState, EvaluationRecommendation


class DimensionResult(ImmutableContract):
    dimension: str = Field(min_length=1)
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evidence_refs: tuple[str, ...] = ()


class EvaluationResult(ImmutableContract):
    run_id: str = Field(min_length=1)
    dimension_results: tuple[DimensionResult, ...] = ()
    confidence: float = Field(ge=0.0, le=1.0)
    unsupported_claims: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    recommendation: EvaluationRecommendation
    evidence_refs: tuple[str, ...] = ()
    token_usage: int = Field(ge=0)
    latency_ms: int = Field(ge=0)
    call_count: int = Field(ge=0)
    cost_estimate: float | None = Field(default=None, ge=0.0)
    execution_state: EvaluationExecutionState
    failure_reason: str | None = None
