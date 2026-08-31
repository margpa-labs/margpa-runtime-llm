"""Domain logic for Phase 7 Governed Web Search/Fetch."""

from .html_normalizer import (
    MAX_WEB_EVIDENCE_INJECTION_CHARACTERS,
    TRUNCATION_NOTICE,
    budget_evidence_for_injection,
    extract_html_title,
    extract_readable_text,
)
from .prompt_injection_detector import detect_prompt_injection
from .secret_detector import detect_secret_candidates
from .url_security import (
    ALLOWED_SCHEMES,
    GetAddrInfoResult,
    Resolver,
    default_resolver,
    validate_url_before_connect,
)

__all__ = [
    "ALLOWED_SCHEMES",
    "MAX_WEB_EVIDENCE_INJECTION_CHARACTERS",
    "TRUNCATION_NOTICE",
    "GetAddrInfoResult",
    "Resolver",
    "budget_evidence_for_injection",
    "default_resolver",
    "detect_prompt_injection",
    "detect_secret_candidates",
    "extract_html_title",
    "extract_readable_text",
    "validate_url_before_connect",
]
