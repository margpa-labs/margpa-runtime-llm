"""Shared validation policy for the Phase 1-B public contracts."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class ImmutableContract(BaseModel):
    """Immutable, versioned contract that rejects unknown fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1"] = "1"
