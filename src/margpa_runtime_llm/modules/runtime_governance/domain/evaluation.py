"""Generic Typed Execution Descriptor (P4-C-WU-001, architecture §6).

Core never knows ARGD/DAGD (or any other Definition) by name — a Trusted
Adapter Extension (`adapters/runtime_governance/reference_definition_adapter.py`)
reads a Definition-specific Normalized IR and emits only these Generic
Descriptors. `evaluation_method` is honest about what Phase 4 can actually
decide without a Model: most ARGD/DAGD rules describe semantic/qualitative
judgment (e.g. "do not hallucinate") that this Phase's Deterministic
Evaluator cannot mechanically verify, so those surface as
`requires_semantic_evaluator` — recorded for traceability (P4-RES-003,
P4-GD-004), never silently marked `pass` (P4-EVL-005).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class EvaluationMethod(StrEnum):
    DETERMINISTIC = "deterministic"
    REQUIRES_SEMANTIC_EVALUATOR = "requires_semantic_evaluator"


class ExecutionDescriptor(ImmutableContract):
    """One Rule/Condition surfaced by a Trusted Adapter Extension.

    `source_definition_id`/`source_pointer` must trace back to real
    Source content — an Adapter never fabricates a Descriptor for a Rule
    that is not actually present in the Source (P4-GD-002/003).
    """

    descriptor_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    source_definition_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    source_pointer: str = Field(min_length=1, max_length=256)
    source_definition_digest_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    source_text_digest_sha512: str | None = Field(default=None, pattern=r"^[0-9a-f]{128}$")
    domain_tag: str | None = Field(default=None, max_length=32, pattern=_IDENTIFIER_PATTERN)
    summary: str = Field(min_length=1, max_length=512)
    evaluation_method: EvaluationMethod
    recommended_action_id: str | None = Field(
        default=None, max_length=64, pattern=_IDENTIFIER_PATTERN
    )
