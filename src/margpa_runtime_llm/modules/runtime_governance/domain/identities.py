"""Opaque identities for the runtime governance domain (Phase 4).

Point IDs and Stages are deliberately plain validated strings, not a
closed enum — architecture note "Point IDは拡張可能Stringであり、固定
列挙だけに閉じない": Phase 5/6 add `guardrail.pre`, `judge.pre`, etc.
without this module's core ever needing to change.
"""

from __future__ import annotations

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
POINT_ID_PATTERN = r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$"


class _OpaqueIdentifier(ImmutableContract):
    value: str = Field(min_length=1, max_length=128, pattern=IDENTIFIER_PATTERN)


class BindingId(_OpaqueIdentifier):
    """Identity of one immutable Bound Governance Plan (ADR-4-003)."""


class InvocationId(_OpaqueIdentifier):
    """Identity of one Governance Point invocation."""


# Phase 4's two initial Points (architecture §1, ADR-4-001). Held as plain
# module constants, not an enum, so this module never becomes the closed
# registry of every Point that will ever exist across Phase 4-6.
MAIN_MODEL_PRE_POINT_ID = "main_model.pre"
MAIN_MODEL_POST_POINT_ID = "main_model.post"

STAGE_PRE = "pre"
STAGE_POST = "post"
