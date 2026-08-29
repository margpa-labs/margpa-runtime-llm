"""Typed LLM-as-a-Judge contracts (Architecture 6.2, Phase 6-D-WU-001).

Selene-1-Mini-Llama-3.1-8B and any future dedicated Judge model can implement
LlmJudgePort without any Core change (Architecture 3.3's Roadmap note); the
Port below is the only seam a new Judge Adapter must satisfy.
"""

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identifiers import EvaluationExecutionState, EvaluationRecommendation
from .result import DimensionResult

SHA512_PATTERN = r"^[0-9a-f]{128}$"


class JudgeIndependenceClass(StrEnum):
    """Mirrors runtime_model_control's IndependenceClass without a hard dependency on it.

    Kept as its own small enum (not imported from runtime_model_control) so the
    Evaluation domain does not need to know about Runtime Model Manager's full
    Snapshot shape just to express this one concept; the Application-layer
    resolver bridges the two (see application/judge_role_resolver.py).
    """

    MAIN_SELF = "main_self"
    SHARED_ARTIFACT = "shared_artifact"
    INDEPENDENT_ARTIFACT = "independent_artifact"
    UNAVAILABLE = "unavailable"
    # P6-RR-N-WU-001 (Production Wiring Delta): Built-in Deterministic is not
    # a Model at all (zero LLM Calls) — reporting it as MAIN_SELF or
    # INDEPENDENT_ARTIFACT would misidentify a real Model Judge that never
    # ran (P6-CODEX-047). Additive member; every existing branch over this
    # enum already falls through an explicit `else`/default, so this alone
    # changes no prior behavior.
    BUILT_IN = "built_in"


class JudgeFailureReason(StrEnum):
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"
    CONTEXT_OVERFLOW = "context_overflow"
    CANCELLED = "cancelled"
    MALFORMED_OUTPUT = "malformed_output"
    MODEL_SWITCH_CONFLICT = "model_switch_conflict"
    COST_LIMIT_EXCEEDED = "cost_limit_exceeded"


class JudgeCriterionDisposition(StrEnum):
    PASS = "pass"
    DEVIATION = "deviation"
    UNKNOWN = "unknown"


class JudgeCriterionResult(ImmutableContract):
    criterion_id: str = Field(min_length=1, max_length=192)
    disposition: JudgeCriterionDisposition
    confidence: float = Field(ge=0.0, le=1.0)
    reason_code: str | None = Field(default=None, max_length=128)
    evidence_refs: tuple[str, ...] = Field(default_factory=tuple, max_length=32)


class LlmJudgeRequest(ImmutableContract):
    judge_role: JudgeIndependenceClass
    model_identity: str = Field(min_length=1)
    artifact_digest: str = Field(pattern=SHA512_PATTERN)
    rubric_id: str = Field(min_length=1)
    prompt_digest: str = Field(pattern=SHA512_PATTERN)
    """SHA-512 of the actual Bounded Typed Prompt. The raw prompt itself is
    never stored as normal Evidence (6-D-WU-003 requirement)."""
    seed: int | None = None
    config_digest: str = Field(pattern=SHA512_PATTERN)
    timeout_ms: int = Field(gt=0)
    max_tokens: int = Field(gt=0)


class LlmJudgeResponse(ImmutableContract):
    judge_role: JudgeIndependenceClass
    recommendation: EvaluationRecommendation
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str | None = None
    """Free-text justification the Judge provided alongside its
    recommendation, if any. Best-effort only: never validated or required by
    the Strict Decoder (unlike `recommendation`/`confidence`, an absent or
    malformed `reasoning` value never fails the decode) — it exists to carry
    human/Repair-readable context, not to gate acceptance."""
    dimension_results: tuple[DimensionResult, ...] = ()
    criterion_results: tuple[JudgeCriterionResult, ...] = ()
    token_usage: int = Field(ge=0)
    latency_ms: int = Field(ge=0)
    cost_estimate: float | None = Field(default=None, ge=0.0)
    execution_state: EvaluationExecutionState
    failure_reason: JudgeFailureReason | None = None
