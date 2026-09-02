"""Turn-frozen semantic evaluation, action, and evidence contracts.

These contracts deliberately keep a Judge recommendation separate from the
authority-owned final action.  A provider result can recommend repair, but it
cannot claim that repair or a safe fallback was actually presented.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .results import Observation
from .semantic_criteria import SemanticCriterion, SemanticCriterionResult

_SHA512_PATTERN = r"^[0-9a-f]{128}$"


class SemanticProviderState(StrEnum):
    NONE = "none"
    UNAVAILABLE = "unavailable"
    ACTIVE = "active"
    FAILED = "failed"


class SemanticFinalDisposition(StrEnum):
    OBSERVED = "observed"
    CANDIDATE_ACCEPTED = "candidate_accepted"
    REPAIR_REQUESTED = "repair_requested"
    REPAIR_ACCEPTED = "repair_accepted"
    SAFE_FALLBACK = "safe_fallback"
    NOT_EVALUATED = "not_evaluated"


class SemanticTurnSnapshot(ImmutableContract):
    request_id: str = Field(min_length=1, max_length=128)
    generation: int = Field(gt=0)
    language: str = Field(min_length=2, max_length=16)
    frozen_main_mode: str = Field(min_length=1, max_length=16)
    frozen_judge_mode: str = Field(min_length=1, max_length=16)
    frozen_repair_mode: str = Field(min_length=1, max_length=16)
    configured_provider: str = Field(min_length=1, max_length=128)
    active_provider: str | None = Field(default=None, max_length=128)
    provider_state: SemanticProviderState
    budget_profile: str = Field(min_length=1, max_length=64)
    max_criteria: int = Field(ge=0)
    criteria: tuple[SemanticCriterion, ...] = Field(default_factory=tuple, max_length=4096)
    deferred_criteria_count: int = Field(default=0, ge=0)
    batch_digest_sha512: str = Field(pattern=_SHA512_PATTERN)
    frozen_digest_sha512: str = Field(pattern=_SHA512_PATTERN)


class SemanticEvaluationRequest(ImmutableContract):
    snapshot: SemanticTurnSnapshot
    stage: str = Field(pattern=r"^(pre|post)$")
    user_input: str
    candidate_answer: str
    dialogue_context: tuple[str, ...] = Field(default_factory=tuple, max_length=256)
    evidence_context: tuple[str, ...] = Field(default_factory=tuple, max_length=256)


class SemanticEvaluationBudget(ImmutableContract):
    """Bounded dedicated-evaluator budget and the work actually admitted."""

    max_criteria_per_call: int = Field(gt=0)
    max_calls: int = Field(ge=0)
    max_prompt_tokens_per_call: int = Field(ge=0)
    max_output_tokens_per_call: int = Field(gt=0)
    context_limit_tokens: int | None = Field(default=None, gt=0)
    inference_deadline_ms: int = Field(ge=0)
    calls_started: int = Field(ge=0)
    calls_completed: int = Field(ge=0)
    prompt_tokens_by_call: tuple[int, ...] = Field(default_factory=tuple, max_length=64)
    completion_tokens: int = Field(ge=0)
    budget_deferred_criteria: int = Field(ge=0)
    deadline_exceeded: bool = False
    cancelled: bool = False


class SemanticEvaluationResponse(ImmutableContract):
    request_id: str = Field(min_length=1, max_length=128)
    generation: int = Field(gt=0)
    provider_id: str = Field(min_length=1, max_length=128)
    provider_state: SemanticProviderState
    results: tuple[SemanticCriterionResult, ...] = Field(default_factory=tuple, max_length=4096)
    latency_ms: int = Field(ge=0)
    failure_reason: str | None = Field(default=None, max_length=128)
    budget: SemanticEvaluationBudget | None = None


class SemanticActionDecision(ImmutableContract):
    recommended_disposition: SemanticFinalDisposition
    executed_disposition: SemanticFinalDisposition
    repair_eligible: bool
    reason_code: str = Field(min_length=1, max_length=128)


class SemanticRuntimeEvidence(ImmutableContract):
    request_id: str = Field(min_length=1, max_length=128)
    generation: int = Field(gt=0)
    frozen_snapshot_digest_sha512: str = Field(pattern=_SHA512_PATTERN)
    configured_provider: str = Field(min_length=1, max_length=128)
    active_provider: str | None = Field(default=None, max_length=128)
    provider_state: SemanticProviderState
    criterion_results: tuple[SemanticCriterionResult, ...] = Field(
        default_factory=tuple, max_length=4096
    )
    merged_observations: tuple[Observation, ...] = Field(default_factory=tuple, max_length=4096)
    action: SemanticActionDecision
    evaluation_budget: SemanticEvaluationBudget | None = None
    evidence_digest_sha512: str = Field(pattern=_SHA512_PATTERN)
