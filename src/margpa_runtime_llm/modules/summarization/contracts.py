"""Typed contracts for the Phase 1-H post-generation summary layer."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict

from margpa_runtime_llm.modules.inference.contracts.generation import ThinkingMode


class SummaryMode(StrEnum):
    OFF = "off"
    POST_GENERATION = "post_generation"


class SummaryBackend(StrEnum):
    MAIN_MODEL = "main_model"


class SummaryFailurePolicy(StrEnum):
    FALLBACK_ORIGINAL = "fallback_original"


class SummarizationConfig(BaseModel):
    """Application-owned summary policy; deployment profiles cannot override it."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: SummaryMode = SummaryMode.OFF
    backend: Literal[SummaryBackend.MAIN_MODEL] = SummaryBackend.MAIN_MODEL
    max_new_tokens: Literal[1024] = 1024
    thinking_mode: Literal[ThinkingMode.DISABLED] = ThinkingMode.DISABLED
    preserve_original: Literal[True] = True
    failure_policy: Literal[SummaryFailurePolicy.FALLBACK_ORIGINAL] = (
        SummaryFailurePolicy.FALLBACK_ORIGINAL
    )
