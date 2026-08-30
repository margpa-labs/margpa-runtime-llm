"""Phase 7 (P7-E/F): framework-independent contracts for Governed Web Search/Fetch.

Mirrors `documentation_rag/contracts.py`'s discipline (immutable, versioned,
allowlist Pydantic models) for a structurally separate Source Class
(`public_web`, never conflated with `documentation_rag_citation` or
`local_corpus` — P7-REQ-006/ADR-7-001).
"""

from __future__ import annotations

import re
from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

SHA512_PATTERN = r"^[0-9a-f]{128}$"
MAX_QUERY_CHARACTERS = 512
MAX_SNIPPET_CHARACTERS = 2_000
MAX_FETCHED_CONTENT_CHARACTERS = 200_000
"""Proportionate to a text/HTML knowledge-grounding fetch (P7-A Sizing scope:
Text系のみ), not a general-purpose downloader — see `WebFetchSecurityConfig`
for the raw byte cap enforced before any decoding happens."""


class WebSearchActivation(StrEnum):
    """P7-REQ-008 / ADR-7-002: kept as its own axis, independent of
    `WebEvidenceGovernanceMode` below — a Search can be activated with no
    Governance scanning (OFF), or Governance can be ENFORCE while Search
    stays disabled (no Evidence ever produced to govern)."""

    DISABLED = "disabled"
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    """Reserved for a future Phase (P7-REQ-013's trigger heuristics are not
    wired to any live trigger in this Task — see Recovery Index P7-E §1).
    The Application Service raises rather than silently degrading if this
    value is ever selected, so a future caller cannot be silently no-op'd."""


class WebEvidenceGovernanceMode(StrEnum):
    OFF = "off"
    OBSERVE = "observe"
    ENFORCE = "enforce"


class SourceAuthorityClass(StrEnum):
    """P7-REQ-012 / ADR-7-005."""

    OFFICIAL = "official"
    PRIMARY = "primary"
    SECONDARY = "secondary"
    GENERAL = "general"
    UNKNOWN = "unknown"


class WebFetchFailureReason(StrEnum):
    """Architecture §7 Failure Model, narrowed to the Web Fetch/Search slice."""

    SEARCH_DISABLED = "search_disabled"
    SEARCH_PROVIDER_UNAVAILABLE = "search_provider_unavailable"
    FETCH_REJECTED = "fetch_rejected"
    FETCH_TIMEOUT = "fetch_timeout"
    CONTENT_UNSUPPORTED = "content_unsupported"
    NO_RELEVANT_EVIDENCE = "no_relevant_evidence"
    PROMPT_INJECTION_DETECTED = "prompt_injection_detected"
    SECRET_CANDIDATE_IN_QUERY = "secret_candidate_in_query"


class UrlRejectionReason(StrEnum):
    """P7-ACC-020/021 — every reason the Security Boundary can refuse a URL
    before any socket is ever opened, or a redirect hop is ever followed."""

    UNSUPPORTED_SCHEME = "unsupported_scheme"
    CREDENTIALS_IN_URL = "credentials_in_url"
    PRIVATE_OR_LOOPBACK_ADDRESS = "private_or_loopback_address"
    LINK_LOCAL_OR_METADATA_ADDRESS = "link_local_or_metadata_address"
    DNS_RESOLUTION_FAILED = "dns_resolution_failed"
    TOO_MANY_REDIRECTS = "too_many_redirects"
    RESPONSE_TOO_LARGE = "response_too_large"
    CONTENT_TYPE_UNSUPPORTED = "content_type_unsupported"
    TIMEOUT = "timeout"


class WebSearchQuery(ImmutableContract):
    request_id: str = Field(min_length=1, max_length=128)
    query_text: str = Field(min_length=1, max_length=MAX_QUERY_CHARACTERS)
    query_digest: str = Field(pattern=SHA512_PATTERN)

    @field_validator("query_text")
    @classmethod
    def validate_query_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("web search query must not be blank")
        return value


class WebSearchResultItem(ImmutableContract):
    """A raw Search Provider hit — a Snippet, never a body of confirmed
    fetched content (ADR-7-005). `rank` is 1-based, provider-reported order."""

    result_id: str = Field(pattern=SHA512_PATTERN)
    title: str
    url: str = Field(min_length=1, max_length=2048)
    snippet: str = Field(max_length=MAX_SNIPPET_CHARACTERS)
    rank: int = Field(gt=0)


class WebSearchRun(ImmutableContract):
    """P7-C `RetrievalRun`-equivalent Canonical Entity for Web Search."""

    request_id: str = Field(min_length=1, max_length=128)
    activation: WebSearchActivation
    provider_key: str
    provider_version: str
    query_digest: str = Field(pattern=SHA512_PATTERN)
    results: tuple[WebSearchResultItem, ...] = ()
    duration_ms: float = Field(ge=0.0)
    failure_reason: WebFetchFailureReason | None = None

    @model_validator(mode="after")
    def validate_failure_consistency(self) -> WebSearchRun:
        if self.failure_reason is not None and self.results:
            raise ValueError("a failed search run must not carry results")
        return self


class WebEvidence(ImmutableContract):
    """P7-C Canonical `WebEvidence` Entity. `snippet` and `fetched_content`
    are structurally distinct fields (ADR-7-005) — a caller can never
    mistake one for the other by field name alone.

    Three independent outcomes are tracked, deliberately not collapsed into
    one boolean: `rejected` (the Security Boundary or the network itself
    never produced content at all), `fetched` (a real fetch attempt did
    produce content), and `withheld_by_governance` (content *was* fetched
    but `WebEvidenceGovernanceMode.ENFORCE` chose not to expose it after a
    Prompt Injection Detection hit — P7-ACC-023). This lets Evidence
    honestly say "we fetched real bytes at Digest X but withheld display",
    rather than forcing that case into either "rejected" (which would
    falsely imply the network attempt itself failed) or a fully exposed
    `fetched_content` (which would defeat ENFORCE's purpose)."""

    evidence_id: str = Field(pattern=SHA512_PATTERN)
    result_id: str = Field(pattern=SHA512_PATTERN)
    canonical_url: str = Field(min_length=1, max_length=2048)
    title: str
    provider_key: str
    source_authority: SourceAuthorityClass
    snippet: str = Field(max_length=MAX_SNIPPET_CHARACTERS)
    fetched: bool
    fetched_content: str | None = Field(default=None, max_length=MAX_FETCHED_CONTENT_CHARACTERS)
    fetched_content_sha512: str | None = Field(default=None, pattern=SHA512_PATTERN)
    withheld_by_governance: bool = False
    fetched_at: str | None = None
    published_or_updated_at: str | None = None
    content_type: str | None = None
    prompt_injection_detected: bool = False
    governance_mode: WebEvidenceGovernanceMode
    rejected: bool = False
    rejection_reason: UrlRejectionReason | WebFetchFailureReason | None = None

    @model_validator(mode="after")
    def validate_fetch_consistency(self) -> WebEvidence:
        if self.fetched:
            if self.fetched_content_sha512 is None:
                raise ValueError("fetched evidence must carry its content digest")
            if self.rejected:
                raise ValueError("fetched evidence must not simultaneously be rejected")
            if self.withheld_by_governance:
                if self.fetched_content is not None:
                    raise ValueError(
                        "content withheld by governance must not expose fetched_content"
                    )
            elif self.fetched_content is None:
                raise ValueError("fetched, non-withheld evidence must carry its content")
        else:
            if self.fetched_content is not None or self.fetched_content_sha512 is not None:
                raise ValueError("unfetched evidence must not carry fetched content")
            if self.withheld_by_governance:
                raise ValueError("evidence that was never fetched cannot be withheld")
        if self.rejected and self.rejection_reason is None:
            raise ValueError("rejected evidence must carry a rejection reason")
        if not self.rejected and self.rejection_reason is not None:
            raise ValueError("non-rejected evidence must not carry a rejection reason")
        if self.prompt_injection_detected and not self.fetched:
            raise ValueError("prompt injection can only be detected in fetched content")
        if self.withheld_by_governance and not self.prompt_injection_detected:
            raise ValueError("this Task only withholds evidence for detected prompt injection")
        return self


class WebCitation(ImmutableContract):
    """Mirrors `documentation_rag.DocumentationCitation`'s allowlist shape
    for the Web Source Class — no free-text content field."""

    citation_id: str = Field(pattern=r"^web-citation-[1-9][0-9]*$")
    canonical_url: str = Field(min_length=1, max_length=2048)
    title: str
    provider_key: str
    source_authority: SourceAuthorityClass
    fetched_at: str | None = None
    selected_order: int = Field(gt=0)


PUBLIC_WEB_SOURCE_CLASS = "public_web"


class WebSearchAndFetchResult(ImmutableContract):
    """Top-level orchestrator output — the Web analogue of
    `DocumentationAugmentation`.

    `request_id` is always present (P7-ACC-028, P7-H Request ID
    correlation) — including on every early-failure path (e.g.
    `SEARCH_DISABLED`) where `search_run` itself is `None`, so a Failure
    can still be correlated back to the exact call that produced it."""

    request_id: str = Field(min_length=1, max_length=128)
    activation: WebSearchActivation
    governance_mode: WebEvidenceGovernanceMode
    search_run: WebSearchRun | None = None
    evidence: tuple[WebEvidence, ...] = ()
    citations: tuple[WebCitation, ...] = ()
    should_generate_with_evidence: bool = False
    failure_reason: WebFetchFailureReason | None = None
    network_calls_made: int = Field(ge=0)

    @model_validator(mode="after")
    def validate_disabled_means_zero_calls(self) -> WebSearchAndFetchResult:
        if self.activation is WebSearchActivation.DISABLED and self.network_calls_made != 0:
            raise ValueError("disabled activation must never make a network call")
        if self.activation is WebSearchActivation.DISABLED and (
            self.search_run is not None or self.evidence or self.citations
        ):
            raise ValueError("disabled activation must never carry search evidence")
        if len(self.citations) > len(self.evidence):
            raise ValueError("citations cannot exceed available evidence")
        return self


class WebSearchFeatureConfig(ImmutableContract):
    schema_version: Literal["1"] = "1"
    default_activation: WebSearchActivation = WebSearchActivation.DISABLED
    default_governance_mode: WebEvidenceGovernanceMode = WebEvidenceGovernanceMode.OFF
    max_results: int = Field(default=5, gt=0, le=20)
    fetch_top_n: int = Field(default=3, gt=0, le=10)
    request_timeout_seconds: float = Field(default=8.0, gt=0.0, le=60.0)
    max_response_bytes: int = Field(default=1_500_000, gt=0, le=10_000_000)
    max_redirects: int = Field(default=3, ge=0, le=10)

    @model_validator(mode="after")
    def validate_fetch_top_n(self) -> WebSearchFeatureConfig:
        if self.fetch_top_n > self.max_results:
            raise ValueError("fetch_top_n must not exceed max_results")
        return self


_OFFICIAL_AUTHORITY_HOST_SUFFIXES: tuple[str, ...] = (
    ".gov",
    ".go.jp",
    ".europa.eu",
)
_PRIMARY_AUTHORITY_HOST_SUFFIXES: tuple[str, ...] = (
    ".edu",
    ".ac.jp",
    "wikipedia.org",
)


def classify_source_authority(hostname: str) -> SourceAuthorityClass:
    """Deterministic, host-suffix-based classification (P7-REQ-012).

    A hand-built heuristic list, not a claim of exhaustive/authoritative
    classification (Requirements §3: "Clean, Label Correct...の認定ではない")
    — any unmatched host is honestly `UNKNOWN`, never defaulted to a higher
    trust tier.
    """

    normalized = hostname.strip(".").casefold()
    if any(
        normalized == suffix.lstrip(".") or normalized.endswith(suffix)
        for suffix in _OFFICIAL_AUTHORITY_HOST_SUFFIXES
    ):
        return SourceAuthorityClass.OFFICIAL
    if any(
        normalized == suffix.lstrip(".") or normalized.endswith(suffix)
        for suffix in _PRIMARY_AUTHORITY_HOST_SUFFIXES
    ):
        return SourceAuthorityClass.PRIMARY
    if re.fullmatch(r"[a-z0-9.-]+\.(com|org|net|io|dev)", normalized):
        return SourceAuthorityClass.GENERAL
    return SourceAuthorityClass.UNKNOWN
