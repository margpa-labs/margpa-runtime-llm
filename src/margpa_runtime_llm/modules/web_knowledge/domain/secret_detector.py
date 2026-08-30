"""Phase 7 (P7-F, Internal Review Rework — resolves an Acceptance gap found
against P7-ACC-022/P7-REQ-015): lightweight, deterministic Secret-shaped
candidate detector for the OUTBOUND Search Query, checked before any
Search Provider call (Architecture §4: "Search Providerへ送るQueryと
Conversation Contextは明示Policyで最小化し、Secret/PII候補は送信前に検査する").

Scoped to high-confidence Secret *shapes* (API keys, private key blocks,
bearer tokens, explicit credential assignments), not general PII (email/
phone numbers) — a broad PII scan would false-positive on ordinary,
innocuous Search queries (e.g. "contact page email format") and make the
Manual Search Golden Path impractical. This is a heuristic, deterministic
pattern scan, not a guarantee of catching every possible Secret shape.
"""

from __future__ import annotations

import re

_SECRET_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern)
    for pattern in (
        r"sk-[A-Za-z0-9]{20,}",  # OpenAI-style secret key
        r"AKIA[0-9A-Z]{16}",  # AWS access key id
        r"gh[pousr]_[A-Za-z0-9]{20,}",  # GitHub token
        r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
        r"(?i)\b(api[_-]?key|secret|password|token)\s*[=:]\s*\S{6,}",
        r"(?i)\bbearer\s+[A-Za-z0-9._-]{10,}",
    )
)


def detect_secret_candidates(text: str) -> bool:
    return any(pattern.search(text) is not None for pattern in _SECRET_PATTERNS)
