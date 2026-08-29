"""Normalized semantic-governance contracts for Phase 6 Remaining Rework.

Definition-specific adapters compile canonical ARGD/DAGD source records into
these provider-neutral contracts.  Core evaluation code consumes only this
shape and therefore never needs to know an ARGD section or DAGD group name.
"""

from __future__ import annotations

import hashlib
import json
from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$"
_SHA512_PATTERN = r"^[0-9a-f]{128}$"


class SemanticEvaluationStage(StrEnum):
    PRE = "pre"
    POST = "post"
    BOTH = "both"


class SemanticEvaluationMethod(StrEnum):
    CLASSIFICATION = "classification"
    CLASSIFICATION_WITH_REFERENCE = "classification_with_reference"
    ABSOLUTE_SCORING = "absolute_scoring"


class SemanticCriterionDisposition(StrEnum):
    PASS = "pass"
    DEVIATION = "deviation"
    UNKNOWN = "unknown"
    DEFERRED = "deferred"
    NOT_APPLICABLE = "not_applicable"


class SemanticDeferredReason(StrEnum):
    JUDGE_OFF = "judge_off"
    PROVIDER_NONE = "provider_none"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    PROVIDER_FAILURE = "provider_failure"
    BUDGET_EXHAUSTED = "budget_exhausted"
    UNSUPPORTED_MAPPING = "unsupported_mapping"
    MALFORMED_RESULT = "malformed_result"


class SemanticCriterion(ImmutableContract):
    criterion_id: str = Field(min_length=1, max_length=192, pattern=_IDENTIFIER_PATTERN)
    descriptor_id: str = Field(min_length=1, max_length=128)
    source_definition_id: str = Field(min_length=1, max_length=128)
    source_definition_digest_sha512: str = Field(pattern=_SHA512_PATTERN)
    source_pointer: str = Field(min_length=1, max_length=256)
    source_text_digest_sha512: str = Field(pattern=_SHA512_PATTERN)
    instruction: str = Field(min_length=1, max_length=512)
    governance_point: str = Field(min_length=1, max_length=128)
    evaluation_stage: SemanticEvaluationStage
    evaluation_method: SemanticEvaluationMethod
    severity_policy: str = Field(min_length=1, max_length=32, pattern=_IDENTIFIER_PATTERN)
    recommended_action_policy: str = Field(min_length=1, max_length=64, pattern=_IDENTIFIER_PATTERN)
    evidence_requirements: tuple[str, ...] = Field(min_length=1, max_length=16)


class SemanticCriterionResult(ImmutableContract):
    criterion_id: str = Field(min_length=1, max_length=192, pattern=_IDENTIFIER_PATTERN)
    descriptor_id: str = Field(min_length=1, max_length=128)
    disposition: SemanticCriterionDisposition
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    reason_code: str | None = Field(default=None, max_length=64, pattern=_IDENTIFIER_PATTERN)
    evidence_refs: tuple[str, ...] = Field(default_factory=tuple, max_length=32)


class SemanticCompileFinding(ImmutableContract):
    descriptor_id: str = Field(min_length=1, max_length=128)
    source_pointer: str = Field(min_length=1, max_length=256)
    reason: SemanticDeferredReason


class SemanticCompileResult(ImmutableContract):
    criteria: tuple[SemanticCriterion, ...]
    unsupported: tuple[SemanticCompileFinding, ...] = ()
    digest_sha512: str = Field(pattern=_SHA512_PATTERN)


class SemanticBatchPlan(ImmutableContract):
    stage: SemanticEvaluationStage
    selected: tuple[SemanticCriterion, ...]
    deferred: tuple[SemanticCriterionResult, ...]
    digest_sha512: str = Field(pattern=_SHA512_PATTERN)


def semantic_contract_digest(value: object) -> str:
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="json")
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha512(payload.encode("utf-8")).hexdigest()
