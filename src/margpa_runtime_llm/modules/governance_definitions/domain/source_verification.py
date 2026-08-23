"""Per-source verification result (architecture §5.3's `Source` state axis).

Kept separate from `PackageState`/`DefinitionState`: one invalid source
must not be silently promoted or demoted into a package-wide decision —
that aggregation (and any quarantine policy) is Phase 3-C-WU-004's job.
This module only answers "does this one source, as read from disk, match
what the Manifest declared?".
"""

from __future__ import annotations

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .states import SourceState

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class SourceVerification(ImmutableContract):
    source_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    state: SourceState
    reason_code: str | None = Field(default=None, max_length=64, pattern=_IDENTIFIER_PATTERN)
