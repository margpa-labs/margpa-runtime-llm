"""Guardrail Point identities (architecture §1/§2, P5-PNT-001).

Point IDs are plain, extensible Strings (never a closed Enum) — a future
Point never requires a Core Enum change. The four initial Points are
constants, not the only legal values.
"""

from __future__ import annotations

IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
POINT_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"

GUARDRAIL_INPUT_POINT_ID = "guardrail.input"
GUARDRAIL_CONTEXT_SOURCE_POINT_ID = "guardrail.context_source"
GUARDRAIL_STREAM_CANDIDATE_POINT_ID = "guardrail.stream_candidate"
GUARDRAIL_OUTPUT_CANDIDATE_POINT_ID = "guardrail.output_candidate"

STAGE_INPUT = "input"
STAGE_CONTEXT = "context"
STAGE_STREAM = "stream"
STAGE_OUTPUT = "output"
