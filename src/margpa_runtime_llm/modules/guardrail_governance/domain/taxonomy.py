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

_INITIAL_CATEGORY_IDS = (
    CATEGORY_PROMPT_INJECTION,
    CATEGORY_JAILBREAK,
    CATEGORY_SECRET,
    CATEGORY_PII,
    CATEGORY_TOOL_ABUSE,
    CATEGORY_AUTHORITY_SPOOFING,
    CATEGORY_UNSAFE_CONTENT,
    CATEGORY_UNKNOWN_UNRESOLVED,
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
