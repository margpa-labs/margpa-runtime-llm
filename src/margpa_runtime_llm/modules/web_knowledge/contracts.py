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
MAX_FETCHED_CONTENT_CHARACTERS = 10_000_000
"""P8-MR7-4 (P8-CODEX-016): matches `WebSearchFeatureConfig.max_response_
bytes`'s own upper Field bound (`le=10_000_000`), not an independently
chosen, smaller value — a decoded UTF-8 string's character count can never
exceed the raw byte count it was decoded from (every character is at least
1 byte), so any Content that already passed the Fetch Provider's real
Security Boundary (`max_response_bytes`, enforced before any decoding
happens) is guaranteed to fit here too. Before this fix, a value smaller
than the configurable Byte Cap ceiling let a genuinely successful,
in-bounds Fetch raise an unclassified Pydantic `ValidationError` while
constructing `WebEvidence` — never a weakening of the Byte Cap itself,
which remains the actual Security Boundary."""


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
    URL_FETCH_DISABLED = "url_fetch_disabled"
    URL_REJECTED = "url_rejected"


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
    DANGEROUS_PORT = "dangerous_port"
    """P8-REQ-003 / Controller Recovery §6 item 4."""
    CONNECT_FAILED = "connect_failed"
    """P8-MR1 (P8-MANUAL-001): TCP-level connect failure at real Fetch time
    (distinct from `DNS_RESOLUTION_FAILED`/`TLS_FAILED`, both of which
    `HttpxWebFetchProvider` also classifies from the same underlying
    `httpx.ConnectError`) — e.g. connection refused, network unreachable.
    Retryable (see `_RETRYABLE_REASONS`): often transient."""
    TLS_FAILED = "tls_failed"
    """P8-MR1: TLS handshake/certificate failure at real Fetch time. Not
    retried — a Retry is very unlikely to change a specific host's TLS
    outcome within one bounded fetch attempt."""
    HTTP_PROTOCOL_ERROR = "http_protocol_error"
    """P8-MR1: malformed/violating HTTP response framing at real Fetch
    time (`httpx.ProtocolError`). Not retried."""


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
    requested_url: str = Field(min_length=1, max_length=2048)
    """P8-RW6-A (P8-CODEX-005): the URL actually requested (Search Result
    URL or User-typed Manual URL) *before* any Redirect. Kept distinct from
    `canonical_url` (the final, post-Redirect URL the content actually came
    from) so a caller can always see both "what was asked for" and "what
    was actually read" — never only the latter, which would silently hide
    that a Redirect occurred at all."""
    canonical_url: str = Field(min_length=1, max_length=2048)
    title: str
    provider_key: str
    source_authority: SourceAuthorityClass
    """P8-RW6-A: always classified from `canonical_url`'s host — the final
    Source actually read — never from `requested_url`'s host. A Redirect
    that crosses Authority Classes (e.g. a `.gov` URL redirecting to a
    `.com` domain) must never inherit the pre-Redirect host's Trust Class."""
    snippet: str = Field(max_length=MAX_SNIPPET_CHARACTERS)
    fetched: bool
    fetched_content: str | None = Field(default=None, max_length=MAX_FETCHED_CONTENT_CHARACTERS)
    fetched_content_sha512: str | None = Field(default=None, pattern=SHA512_PATTERN)
    withheld_by_governance: bool = False
    fetched_at: str | None = None
    published_or_updated_at: str | None = None
    content_type: str | None = None
    transformation: WebContentTransformation | None = None
    """P8-MR2 (P8-MANUAL-002): set for every genuinely fetched Evidence
    (regardless of `withheld_by_governance`, mirroring `content_type`'s own
    unconditional-on-fetch rule), `None` for evidence that was never
    fetched at all."""
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
            if self.transformation is None:
                raise ValueError("fetched evidence must declare its content transformation")
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
            if self.transformation is not None:
                raise ValueError("unfetched evidence must not declare a content transformation")
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


class WebContentTransformation(StrEnum):
    """P8-MR2 (P8-MANUAL-002) / Architecture §3 `ExternalUrlEvidence.
    Transformation`: what, if anything, is done to this Evidence's raw
    fetched bytes before any part of it ever reaches the Main Model.
    `content_sha512`/`fetched_content` on `WebEvidence` always stay the
    *raw*, untransformed bytes (Digest integrity is never computed over a
    transformed copy) — this Field only documents what downstream
    Model-injection processing (`html_normalizer.py`) will honestly apply,
    so a Citation never silently implies "the Model saw exactly this raw
    text" when a Content-Type it cannot render verbatim (HTML) is
    involved."""

    RAW = "raw"
    HTML_TEXT_EXTRACTED = "html_text_extracted"


def classify_content_transformation(content_type: str | None) -> WebContentTransformation:
    if (content_type or "").split(";", 1)[0].strip().casefold() == "text/html":
        return WebContentTransformation.HTML_TEXT_EXTRACTED
    return WebContentTransformation.RAW


PUBLIC_WEB_SOURCE_CLASS = "public_web"


class WebCitation(ImmutableContract):
    """Mirrors `documentation_rag.DocumentationCitation`'s allowlist shape
    for the Web Source Class — no free-text content field."""

    citation_id: str = Field(pattern=r"^web-citation-[1-9][0-9]*$")
    requested_url: str = Field(min_length=1, max_length=2048)
    """P8-RW6-A (P8-CODEX-005): mirrors `WebEvidence.requested_url` — kept
    on the Citation itself (not only the transient `WebEvidence`) so it
    survives Persistence/REST/UI projection too."""
    canonical_url: str = Field(min_length=1, max_length=2048)
    title: str
    provider_key: str
    source_authority: SourceAuthorityClass
    fetched_at: str | None = None
    content_type: str | None = None
    transformation: WebContentTransformation
    """P8-MR2 (P8-MANUAL-002): mirrors `WebEvidence.transformation` — every
    `WebCitation` is only ever built from genuinely fetched, non-withheld
    Evidence, so this is always present (never `None`) on a Citation."""
    content_sha512: str | None = Field(default=None, pattern=SHA512_PATTERN)
    source_class: str = PUBLIC_WEB_SOURCE_CLASS
    """P8-REQ-007 / P8-ACC-010: fixed value for this Task (only one Web
    Source Class exists). Kept as its own Field, not merged with
    `source_authority` (a Trust tier), so a future Citation-merging UI can
    discriminate Web from `documentation_rag`/`local_corpus` Citations by
    Field name alone, mirroring that module's own `source_class`/
    `corpus_source_class` discriminator pattern."""
    selected_order: int = Field(gt=0)


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


WEB_CITATION_EVIDENCE_SCHEMA_VERSION = 3
"""P8-A (P8-ACC-011): independent of `CITATION_EVIDENCE_SCHEMA_VERSION`
(`documentation_rag/contracts.py`) — the two Evidence kinds evolve on
separate schedules, mirroring how `WebCitation` already mirrors
`DocumentationCitation` without sharing a type.

P8-RW6-A (P8-CODEX-005): bumped 1 -> 2 when `WebCitation.requested_url`
became a required Field.

P8-MR2 (P8-MANUAL-002): bumped 2 -> 3 when `WebCitation.transformation`
became a required Field. Each bump follows the same truthfulness
discipline: a record predating the new Field no longer matches this
shape; the Reader's existing `model_validate()` ->
`WebCitationUnavailable(reason="corrupt_record")` fallback already degrades
such a record safely (never crashes), so the bump is a truthfulness
correction — the Version number must describe the shape actually
produced — not a functional prerequisite for that safety."""


class PersistedTurnWebCitationEvidence(ImmutableContract):
    """Safe, allowlisted Manual URL Fetch evidence for one completed
    Conversation Turn (P8-A / P8-ACC-011). Mirrors `documentation_rag.
    contracts.PersistedTurnCitationEvidence`'s discipline exactly: reuses
    `WebCitation` (already an allowlist type), carries no free-text content
    field, so the fetched page body itself is never persisted here — only
    its Citation (URL, Digest, Content Type, Source Class)."""

    conversation_id: str = Field(min_length=1)
    turn_id: str = Field(min_length=1)
    citation_schema_version: int = Field(ge=1)
    activation: WebSearchActivation
    failure_reason: WebFetchFailureReason | None = None
    specific_failure_reason: str | None = None
    """P8-MR2 (P8-MANUAL-002) / UF-P8-007: the per-Evidence
    `WebEvidence.rejection_reason` (e.g. `dns_resolution_failed`,
    `private_or_loopback_address`) — kept distinct from the coarser
    `failure_reason` Aggregate above, which alone previously left a User
    unable to tell *why* a Fetch failed beyond a generic `url_rejected`.
    Manual URL Fetch (the only caller of `build_turn_web_citation_evidence()`)
    always carries at most one Evidence item, so this is the single Reason
    that item's own `rejection_reason` carried, if any."""
    citations: tuple[WebCitation, ...] = ()

    @model_validator(mode="after")
    def validate_activation_consistency(self) -> PersistedTurnWebCitationEvidence:
        if self.activation is WebSearchActivation.DISABLED and self.citations:
            raise ValueError("disabled activation must not carry citations")
        return self


class WebCitationUnavailable(ImmutableContract):
    """Fail-closed placeholder returned instead of raising on a bad record
    (mirrors `documentation_rag.contracts.CitationUnavailable`)."""

    turn_id: str = Field(min_length=1)
    reason: Literal["unsupported_schema_version", "corrupt_record", "not_present"]


def build_turn_web_citation_evidence(
    result: WebSearchAndFetchResult,
    *,
    conversation_id: str,
    turn_id: str,
) -> PersistedTurnWebCitationEvidence:
    """Project a completed `WebSearchAndFetchResult` into persistable
    evidence. Callers only invoke this when a Manual URL Fetch genuinely
    ran for this Turn (`ConversationGenerationSession.web_search_result is
    not None`) — every such attempt, success or failure/rejection alike, is
    real Evidence worth persisting (P7-RW5-A's lesson applied from the
    start here: a Turn that tried and failed must reconstruct that same
    honest outcome on reload, never silently drop it)."""

    specific_reason = next(
        (
            item.rejection_reason.value
            for item in result.evidence
            if item.rejection_reason is not None
        ),
        None,
    )
    return PersistedTurnWebCitationEvidence(
        conversation_id=conversation_id,
        turn_id=turn_id,
        citation_schema_version=WEB_CITATION_EVIDENCE_SCHEMA_VERSION,
        activation=result.activation,
        failure_reason=result.failure_reason,
        specific_failure_reason=specific_reason,
        citations=result.citations,
    )


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
