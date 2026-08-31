"""Phase 8 (P8-MR1/P8-MR2): minimal, dependency-free HTML title extraction
and Readable-Text normalization for Manual URL Evidence.

Deliberately NOT a general-purpose HTML parser/Readability engine (that
full Extractor/Normalizer/Chunking pipeline is Phase 11+ scope — see
`docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`
UF-P8-006). This module does exactly two small, honest things with pure
stdlib `re`/`html`:

1. Pull the real `<title>` out of a fetched HTML page, so a Citation shows
   what a human would actually call the page instead of its own URL
   (P8-MANUAL-002).
2. Strip `script`/`style`/`noscript` tag bodies and all remaining markup
   from HTML before any of it is spliced into the Main Model's prompt, then
   apply a fixed character Budget — so a large Raw HTML page (Script/CSS/
   Attribute noise included) can never silently blow past the effective
   Model Context and surface as an opaque failure (P8-MANUAL-001).

Neither function ever touches `WebEvidence.fetched_content`/
`fetched_content_sha512` (the stored, Digest-verified raw bytes) — both
operate on a disposable copy used only for Title projection or Model
injection.
"""

from __future__ import annotations

import html as html_stdlib
import re

_TITLE_PATTERN = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_NOISE_TAG_PATTERN = re.compile(
    r"<(script|style|noscript)\b[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL
)
_TAG_PATTERN = re.compile(r"<[^>]+>")
_WHITESPACE_PATTERN = re.compile(r"[ \t\f\v]+")
_BLANK_LINE_PATTERN = re.compile(r"\n\s*\n+")

MAX_WEB_EVIDENCE_INJECTION_CHARACTERS = 12_000
"""Sized to leave comfortable room, alongside System/Conversation History/
Instruction overhead, within a small effective Model Context (the User
Manual reproduction used an 8192-token Runtime) — a rough, deliberately
conservative characters-not-tokens Hard Cap, not a Tokenizer-exact Budget
(no Tokenizer is available at this layer)."""

TRUNCATION_NOTICE = (
    "\n\n[This Evidence was truncated to fit the Model's Context Budget; "
    "the original fetched content was longer.]"
)


def extract_html_title(html: str) -> str | None:
    """Returns the real `<title>` text, or `None` if absent/blank — the
    caller (`WebKnowledgeService.fetch_direct_url()`) falls back to the
    Canonical URL only when this returns `None` (P8-MANUAL-002)."""

    match = _TITLE_PATTERN.search(html)
    if match is None:
        return None
    title = html_stdlib.unescape(match.group(1))
    title = _WHITESPACE_PATTERN.sub(" ", title).replace("\n", " ").strip()
    return title or None


def extract_readable_text(content: str, content_type: str | None) -> str:
    """Strips `script`/`style`/`noscript` bodies and all remaining HTML
    tags for `text/html` content; every other Content-Type is returned
    unchanged (there is no markup to strip)."""

    if (content_type or "").split(";", 1)[0].strip().casefold() != "text/html":
        return content
    without_noise = _NOISE_TAG_PATTERN.sub(" ", content)
    without_tags = _TAG_PATTERN.sub(" ", without_noise)
    unescaped = html_stdlib.unescape(without_tags)
    collapsed = _WHITESPACE_PATTERN.sub(" ", unescaped)
    return _BLANK_LINE_PATTERN.sub("\n\n", collapsed).strip()


def budget_evidence_for_injection(
    text: str, *, max_characters: int = MAX_WEB_EVIDENCE_INJECTION_CHARACTERS
) -> str:
    """Truncates `text` to `max_characters`, appending `TRUNCATION_NOTICE`
    only when truncation actually happened — never silently drops the
    notice's absence as evidence that nothing was cut."""

    if len(text) <= max_characters:
        return text
    return text[:max_characters] + TRUNCATION_NOTICE
