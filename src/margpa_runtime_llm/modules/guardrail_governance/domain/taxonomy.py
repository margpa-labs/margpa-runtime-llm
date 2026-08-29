"""Guardrail Category Taxonomy (P5-RES-003/004).

`CategoryId` is a plain validated String, never a closed Core Enum —
Core Routing (Action Resolver, Conflict Rule) never Hard-codes a
specific Category name. The constants below are the initial Registry
entries a Detector/Policy may reference; a Registry can grow without a
Core code change (P5-RES-003).
"""

from __future__ import annotations

from pydantic import Field

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .identities import IDENTIFIER_PATTERN

CATEGORY_PROMPT_INJECTION = "prompt_injection"
CATEGORY_JAILBREAK = "jailbreak"
CATEGORY_SECRET = "secret"
CATEGORY_PII = "pii"
CATEGORY_TOOL_ABUSE = "tool_abuse"
CATEGORY_AUTHORITY_SPOOFING = "authority_spoofing"
CATEGORY_UNSAFE_CONTENT = "unsafe_content"
CATEGORY_UNKNOWN_UNRESOLVED = "unknown_unresolved"
# P6-RR-R23 (Post-Codex Independent Review Rework, resolves P6-CODEX-087):
# the remaining 7 of Qwen3Guard's 9 official Category labels (`Jailbreak`
# and `PII` already had internal IDs above) — sourced from the official
# QwenLM/Qwen3Guard GitHub Repository README `## Safety Categories`
# section (exact Commit/Digest recorded in `config/guardrail/qwen3guard/
# manifest.json`). `Jailbreak` maps to the existing `CATEGORY_JAILBREAK`
# and is Input/Context-only (never a valid Output Candidate label — see
# `qwen3guard_manifest.py`'s per-Target Category Set); the other 8 apply
# to both Input/Context and Output Candidate.
CATEGORY_VIOLENT = "violent"
CATEGORY_NON_VIOLENT_ILLEGAL_ACTS = "non_violent_illegal_acts"
CATEGORY_SEXUAL_CONTENT = "sexual_content"
CATEGORY_SUICIDE_SELF_HARM = "suicide_self_harm"
CATEGORY_UNETHICAL_ACTS = "unethical_acts"
CATEGORY_POLITICALLY_SENSITIVE_TOPICS = "politically_sensitive_topics"
CATEGORY_COPYRIGHT_VIOLATION = "copyright_violation"

_INITIAL_CATEGORY_IDS = (
    CATEGORY_PROMPT_INJECTION,
    CATEGORY_JAILBREAK,
    CATEGORY_SECRET,
    CATEGORY_PII,
    CATEGORY_TOOL_ABUSE,
    CATEGORY_AUTHORITY_SPOOFING,
    CATEGORY_UNSAFE_CONTENT,
    CATEGORY_UNKNOWN_UNRESOLVED,
    CATEGORY_VIOLENT,
    CATEGORY_NON_VIOLENT_ILLEGAL_ACTS,
    CATEGORY_SEXUAL_CONTENT,
    CATEGORY_SUICIDE_SELF_HARM,
    CATEGORY_UNETHICAL_ACTS,
    CATEGORY_POLITICALLY_SENSITIVE_TOPICS,
    CATEGORY_COPYRIGHT_VIOLATION,
)


class CategoryRegistryEntry(ImmutableContract):
    category_id: str = Field(min_length=1, max_length=64, pattern=IDENTIFIER_PATTERN)
    display_name: str = Field(min_length=1, max_length=128)


class CategoryRegistry:
    """A small, explicit, extensible Registry — never a bare `set[str]`
    literal scattered across Core Routing (P5-RES-003)."""

    def __init__(self, entries: tuple[CategoryRegistryEntry, ...] = ()) -> None:
        self._entries = {entry.category_id: entry for entry in entries}

    def is_known(self, category_id: str) -> bool:
        return category_id in self._entries

    def entries(self) -> tuple[CategoryRegistryEntry, ...]:
        return tuple(self._entries.values())


def default_category_registry() -> CategoryRegistry:
    return CategoryRegistry(
        tuple(
            CategoryRegistryEntry(category_id=category_id, display_name=category_id)
            for category_id in _INITIAL_CATEGORY_IDS
        )
    )
