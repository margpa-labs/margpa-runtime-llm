"""EvaluatorBinding/EvaluationBudget/EvaluationRun (Architecture 6.1)."""

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identifiers import EvaluationMode, EvaluatorClass

SHA512_PATTERN = r"^[0-9a-f]{128}$"


class EvaluatorBinding(ImmutableContract):
    evaluator_id: str = Field(min_length=1)
    evaluator_class: EvaluatorClass
    model_identity: str | None = None
    """None for deterministic evaluators; set for llm_judge (Phase 6-D)."""


class EvaluationBudget(ImmutableContract):
    max_calls: int = Field(gt=0)
    max_tokens: int = Field(gt=0)
    max_wall_time_ms: int = Field(gt=0)


class EvaluationRun(ImmutableContract):
    run_id: str = Field(min_length=1)
    request_id: str = Field(min_length=1)
    conversation_id: str | None = None
    turn_id: str | None = None
    generation_attempt_id: str | None = None
    dataset_id: str = Field(min_length=1)
    case_id: str = Field(min_length=1)
    criteria: tuple[str, ...] = Field(min_length=1)
    evaluator_binding: EvaluatorBinding
    mode: EvaluationMode
    config_digest: str = Field(pattern=SHA512_PATTERN)
    seed: int | None = None
    budget: EvaluationBudget
