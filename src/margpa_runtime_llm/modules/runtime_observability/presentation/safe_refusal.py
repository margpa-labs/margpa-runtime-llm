"""Safe Refusal Presentation Mapper (Architecture 11.3, Phase 6-F-WU-003).

Converts an internal Guardrail Reject Code into a fixed, safe user-facing
sentence. The raw code is never exposed in the normal chat body (Acceptance
P6-ACC-041); it may only surface through a separate Developer Detail channel
that this mapper does not implement.
"""

from enum import StrEnum


class SafeRefusalLanguage(StrEnum):
    JA = "ja"
    EN = "en"


_SAFE_REFUSAL_TEXT: dict[SafeRefusalLanguage, str] = {
    SafeRefusalLanguage.JA: "その依頼には対応できません。別の安全な内容であればお手伝いできます。",
    SafeRefusalLanguage.EN: "I cannot help with that request. I can help with a safer alternative.",
}


def render_safe_refusal(*, reject_code: str, language: SafeRefusalLanguage) -> str:
    """`reject_code` is accepted for future differentiation but never appears in the output."""
    del reject_code
    return _SAFE_REFUSAL_TEXT[language]


def is_safety_reject_code(code: str) -> bool:
    """True for any Guardrail/Governance reason_code produced by
    `bootstrap/guardrail_governance.py` or `bootstrap/runtime_governance.py`
    (P6-CODEX-003): these must never reach the normal chat body as a raw
    code (P6-ACC-041) and must render through this module's mapper instead.
    Prefix-based rather than an exact enum so a new reason_code introduced
    by either bootstrap module is safe-by-default without an additional edit
    here."""
    return code.startswith("guardrail_") or code.startswith("governance_")
