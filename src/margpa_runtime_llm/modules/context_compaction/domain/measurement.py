"""Measurement Class-tagged token counts (Canonical Design SS6.1).

Invariant 13: an Unknown Measurement is never converted to 0, and values
from different Turns/units/Models are never silently summed as if
comparable. `MeasuredTokens.value` is `None` exactly when
`measurement_class is UNKNOWN` -- every other class requires a concrete,
non-negative integer.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract


class MeasurementClass(StrEnum):
    OBSERVED = "observed"
    """Read back from a real, already-completed Generation Attempt's actual
    token usage (e.g. the Backend's own `prompt_tokens`/`total_tokens`)."""
    PROVIDER_REPORTED = "provider_reported"
    """Reported directly by the Model/Backend Provider for the current
    configuration (e.g. a declared Context Capacity)."""
    RUNTIME_CALCULATED = "runtime_calculated"
    """Computed now, in-process, from a live source (e.g. counting the
    pending prompt's tokens with the loaded Model's own tokenizer)."""
    ESTIMATED = "estimated"
    """A configured or heuristic approximation, not measured against the
    live loaded Model (e.g. a fixed Reserve constant)."""
    UNKNOWN = "unknown"
    """No usable source was available. Never coerced to 0."""


class MeasuredTokens(ImmutableContract):
    value: int | None = Field(default=None, ge=0)
    measurement_class: MeasurementClass
    source: str = Field(min_length=1, max_length=128)
    observed_at: datetime
    model_identity: str | None = Field(default=None, min_length=1, max_length=256)
    context_config_identity: str | None = Field(default=None, min_length=1, max_length=256)

    @model_validator(mode="after")
    def validate_value_shape(self) -> MeasuredTokens:
        if self.measurement_class is MeasurementClass.UNKNOWN:
            if self.value is not None:
                raise ValueError("an unknown measurement must not carry a value")
        elif self.value is None:
            raise ValueError("a known measurement class requires a concrete value")
        return self

    @staticmethod
    def unknown(*, source: str, observed_at: datetime) -> MeasuredTokens:
        return MeasuredTokens(
            value=None,
            measurement_class=MeasurementClass.UNKNOWN,
            source=source,
            observed_at=observed_at,
        )
