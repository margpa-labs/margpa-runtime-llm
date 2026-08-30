"""Phase 7 (P7-F): lightweight, deterministic Document Prompt Injection marker
detector for fetched Web content (P7-ACC-023, P7-REQ-015).

A pattern-based heuristic scan, not a Model-backed classifier — proportionate
to MVP scope (mirrors `documentation_rag`'s own `[REFERENCE ...]` fence
approach to untrusted content: contain and label, rather than deeply
understand). False negatives are expected for a sufficiently obfuscated
injection; this is Evidence for `WebEvidenceGovernanceMode`, not a
guaranteed-safe filter.
"""

from __future__ import annotations

import re

_INJECTION_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"ignore (all |any )?(previous|prior|above) instructions",
        r"disregard (all |any )?(previous|prior|above) instructions",
        r"you are now (in )?(developer|dan|jailbreak|unrestricted) mode",
        r"system prompt:",
        r"\[?system\]?\s*:\s*you must",
        r"forget (all |any )?(previous|prior) (instructions|rules)",
        r"reveal your (system prompt|instructions)",
        r"act as if you have no (restrictions|guidelines|rules)",
    )
)


def detect_prompt_injection(content: str) -> bool:
    return any(pattern.search(content) is not None for pattern in _INJECTION_PATTERNS)
