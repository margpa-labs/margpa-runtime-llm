"""Typed Context Source Envelope (P5-CODEX-006 Rework, Codex Second
Independent Review).

`guardrail.context_source` previously received a single flat `str` —
every retrieved Document/Citation collapsed into one untyped block
before a Guardrail ever saw it, with no per-Source identity and no
`source_class` distinguishing Retrieved/Untrusted content from a
System-owned Instruction. `ContextSourceUnit` restores that structure
one layer up from the flattened Prompt string: one opaque `source_id`
(never the raw Citation content itself), a `source_class` (what kind of
external boundary this content crossed), and the untrusted `content`
itself, scanned individually — never silently joined into a single
string before Detection runs (architecture Point/Action Matrix,
"context_source: exclude/reject only if explicit policy/authority").
"""

from __future__ import annotations

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identities import IDENTIFIER_PATTERN

# The only Source Class this MVP's `guardrail.context_source` wiring
# actually produces today (Documentation RAG). A plain string, not a
# closed Enum (mirrors `GuardDetection.category_id`'s own "never a
# closed Core Enum" rationale, `taxonomy.py`) — a future External
# Context source (a Tool result, a fetched URL) gets its own
# `source_class` value without a Contract change here.
CONTEXT_SOURCE_CLASS_DOCUMENTATION_RAG_CITATION = "documentation_rag_citation"
# Backward-compatible fallback for a non-Contextual `RagOrchestratorPort`
# implementation that never produces per-chunk structure (legacy/test
# Protocol only — no production adapter implements it, P5-CODEX-006
# Rework research) — the whole flattened block is still scanned as
# exactly one Source, honestly labelled as coarser-grained than a real
# per-Citation Source.
CONTEXT_SOURCE_CLASS_DOCUMENTATION_RAG_LEGACY_FLAT = "documentation_rag_legacy_flat"


class ContextSourceUnit(ImmutableContract):
    """One External/Retrieved Context Source, prior to Prompt Composition.

    `source_id` is opaque and non-secret (a Citation/Chunk identity such
    as a SHA-512 Chunk id) — never itself a place raw matched Content is
    stored (mirrors `TypedSpan`'s own "Bounds only" discipline)."""

    source_id: str = Field(min_length=1, max_length=200)
    source_class: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    content: str = Field(min_length=1)
