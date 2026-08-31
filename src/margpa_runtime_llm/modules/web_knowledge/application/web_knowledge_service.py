"""Phase 7 (P7-E/F): orchestrate Governed Web Search -> Security Boundary ->
Fetch -> Prompt Injection Governance -> Citation, mirroring
`DocumentationRagApplicationService`'s single deterministic Pipeline shape.

Phase 8 (P8-A): adds `fetch_direct_url()`, a second entry point that fetches
one User-supplied URL without invoking a Search Provider at all. It shares
every downstream stage with `search_and_fetch()` (Security Boundary,
Prompt Injection Governance, Citation building) but never touches
`self._search_provider` (P8-REQ-002: Manual URL Evidence is not Search).
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from urllib.parse import urlsplit

from ..contracts import (
    PUBLIC_WEB_SOURCE_CLASS,
    UrlRejectionReason,
    WebCitation,
    WebEvidence,
    WebEvidenceGovernanceMode,
    WebFetchFailureReason,
    WebSearchActivation,
    WebSearchAndFetchResult,
    WebSearchFeatureConfig,
    WebSearchQuery,
    WebSearchRun,
    classify_content_transformation,
    classify_source_authority,
)
from ..domain import (
    Resolver,
    default_resolver,
    detect_prompt_injection,
    detect_secret_candidates,
    extract_html_title,
    validate_url_before_connect,
)
from ..ports import FetchedContent, FetchRejected, WebFetchProviderPort, WebSearchProviderPort

__all__ = ["PUBLIC_WEB_SOURCE_CLASS", "WebKnowledgeService"]

DEFAULT_PREFLIGHT_MAX_RETRIES = 2
"""P8-MR8-2 (P8-CODEX-020): mirrors `HttpxWebFetchProvider.DEFAULT_MAX_
RETRIES` — up to 2 Retries (3 attempts total), fixed and not User-
configurable, for this Service's *own* Security Preflight Validation call
(`validate_url_before_connect()`), independent of and prior to the Fetch
Provider's own Retry Budget."""
DEFAULT_PREFLIGHT_RETRY_BACKOFF_SECONDS = 0.2

_PREFLIGHT_RETRYABLE_REASONS = frozenset({UrlRejectionReason.DNS_RESOLUTION_FAILED})
"""Preflight Validation only ever performs DNS resolution (no real Socket
Connect/TLS/HTTP), so `DNS_RESOLUTION_FAILED` is the only Reason it can
ever produce that is plausibly transient — every Permanent Security
Rejection (Private/Loopback/Credentials/Dangerous Port/Unsupported
Scheme/...) is never retried, unchanged."""


class WebKnowledgeService:
    def __init__(
        self,
        *,
        search_provider: WebSearchProviderPort,
        fetch_provider: WebFetchProviderPort,
        config: WebSearchFeatureConfig,
        direct_fetch_provider: WebFetchProviderPort | None = None,
        resolver: Resolver = default_resolver,
        preflight_max_retries: int = DEFAULT_PREFLIGHT_MAX_RETRIES,
        preflight_retry_backoff_seconds: float = DEFAULT_PREFLIGHT_RETRY_BACKOFF_SECONDS,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self._search_provider = search_provider
        self._fetch_provider = fetch_provider
        self._config = config
        # P8-MR7-1 (P8-CODEX-013): the same Resolver Dependency threaded
        # through every `validate_url_before_connect()` call this Service
        # makes — Production default is the real DNS resolver; a Test may
        # inject a deterministic Fake instead of relying on monkeypatching
        # the global `socket` module.
        self._resolver = resolver
        # P8-MR8-2 (P8-CODEX-020): a Transient DNS hiccup on this Service's
        # *own* Preflight Validation call must not short-circuit to
        # `url_rejected` before `HttpxWebFetchProvider`'s own Retry Budget
        # is ever reached — Manual URL Fetch reliability (P8-MANUAL-001) is
        # decided by the whole Production Composition, not by the Fetch
        # Provider's Unit Test alone.
        self._preflight_max_retries = preflight_max_retries
        self._preflight_retry_backoff_seconds = preflight_retry_backoff_seconds
        self._preflight_sleep_fn = sleep_fn
        # P8-A / Controller Recovery §6 item 1: Direct URL Fetch must not
        # share the Search Golden Path's Fixture Fetch Provider in Production
        # (that Provider only ever "fetches" its own fixed, known URL set —
        # any real User URL would be rejected outright). A second, separate
        # Port lets Production wire a real `HttpxWebFetchProvider` here while
        # `search_and_fetch()`'s Fixture behavior stays untouched. Defaulting
        # to `fetch_provider` when omitted keeps every existing caller/Test
        # that constructs this Service with a single Fetch Provider correct
        # unchanged (Phase 7 behavior, and every pre-Phase-8 Unit Test).
        self._direct_fetch_provider = direct_fetch_provider or fetch_provider

    def search_and_fetch(
        self,
        query_text: str,
        *,
        request_id: str,
        activation: WebSearchActivation,
        governance_mode: WebEvidenceGovernanceMode,
    ) -> WebSearchAndFetchResult:
        if activation is WebSearchActivation.DISABLED:
            return WebSearchAndFetchResult(
                request_id=request_id,
                activation=activation,
                governance_mode=governance_mode,
                network_calls_made=0,
                failure_reason=WebFetchFailureReason.SEARCH_DISABLED,
            )
        if activation is WebSearchActivation.AUTOMATIC:
            # P7-REQ-013's trigger heuristics are not wired to any live
            # caller in this Task (Recovery Index P7-E §1) — raising here
            # instead of silently degrading to a no-op means a future
            # caller that *does* wire an automatic trigger will fail loudly
            # the moment it's connected, not discover a silent gap later.
            raise NotImplementedError(
                "automatic web search activation is not implemented in this Task"
            )
        if detect_secret_candidates(query_text):
            # Architecture §4 / P7-ACC-022: checked before the Search
            # Provider is ever called — a Secret-shaped candidate never
            # leaves this process, fail-closed (rejected outright, not
            # redacted-and-sent).
            return WebSearchAndFetchResult(
                request_id=request_id,
                activation=activation,
                governance_mode=governance_mode,
                network_calls_made=0,
                failure_reason=WebFetchFailureReason.SECRET_CANDIDATE_IN_QUERY,
            )

        network_calls = 0
        started = time.perf_counter()
        query = WebSearchQuery(
            request_id=request_id,
            query_text=query_text,
            query_digest=_digest(query_text),
        )
        try:
            # Counted before the call resolves, not after: `network_calls_made`
            # records attempted outbound calls (Evidence/Audit purpose — see
            # `WebSearchAndFetchResult.validate_disabled_means_zero_calls`,
            # which cares that DISABLED made *zero attempts*), not only calls
            # that happened to succeed.
            network_calls += 1
            results = self._search_provider.search(query, max_results=self._config.max_results)
        except Exception:
            return WebSearchAndFetchResult(
                request_id=request_id,
                activation=activation,
                governance_mode=governance_mode,
                failure_reason=WebFetchFailureReason.SEARCH_PROVIDER_UNAVAILABLE,
                network_calls_made=network_calls,
            )

        search_run = WebSearchRun(
            request_id=request_id,
            activation=activation,
            provider_key=self._search_provider.provider_key,
            provider_version=self._search_provider.provider_version,
            query_digest=query.query_digest,
            results=results,
            duration_ms=_duration_ms(started),
        )
        if not results:
            return WebSearchAndFetchResult(
                request_id=request_id,
                activation=activation,
                governance_mode=governance_mode,
                search_run=search_run,
                failure_reason=WebFetchFailureReason.NO_RELEVANT_EVIDENCE,
                network_calls_made=network_calls,
            )

        evidence: list[WebEvidence] = []
        for item in results[: self._config.fetch_top_n]:
            hostname = urlsplit(item.url).hostname or ""
            authority = classify_source_authority(hostname)
            evidence_id = _digest(f"{request_id}\0{item.result_id}\0{item.url}")
            rejection = self._validate_url_with_retry(item.url)
            if rejection is not None:
                evidence.append(
                    WebEvidence(
                        evidence_id=evidence_id,
                        result_id=item.result_id,
                        requested_url=item.url,
                        canonical_url=item.url,
                        title=item.title,
                        provider_key=self._search_provider.provider_key,
                        source_authority=authority,
                        snippet=item.snippet,
                        fetched=False,
                        governance_mode=governance_mode,
                        rejected=True,
                        rejection_reason=rejection,
                    )
                )
                continue

            network_calls += 1
            try:
                fetch_result: FetchedContent | FetchRejected = self._fetch_provider.fetch(
                    item.url,
                    timeout_seconds=self._config.request_timeout_seconds,
                    max_response_bytes=self._config.max_response_bytes,
                    max_redirects=self._config.max_redirects,
                )
            except Exception:
                # A Fetch Provider bug/unexpected exception becomes Evidence
                # of a rejected fetch, never an uncaught crash that would
                # propagate into the caller's request handling (Architecture
                # §3 Invariant 10: Runtime/Evidence Failure must not break
                # the core feature).
                fetch_result = FetchRejected(reason=WebFetchFailureReason.FETCH_REJECTED)
            if isinstance(fetch_result, FetchRejected):
                evidence.append(
                    WebEvidence(
                        evidence_id=evidence_id,
                        result_id=item.result_id,
                        requested_url=item.url,
                        canonical_url=item.url,
                        title=item.title,
                        provider_key=self._search_provider.provider_key,
                        source_authority=authority,
                        snippet=item.snippet,
                        fetched=False,
                        governance_mode=governance_mode,
                        rejected=True,
                        rejection_reason=fetch_result.reason,
                    )
                )
                continue

            evidence.append(
                self._build_fetched_evidence(
                    evidence_id=evidence_id,
                    result_id=item.result_id,
                    url=item.url,
                    title=item.title,
                    snippet=item.snippet,
                    fetched=fetch_result,
                    governance_mode=governance_mode,
                )
            )

        citations = tuple(
            WebCitation(
                citation_id=f"web-citation-{index + 1}",
                requested_url=item.requested_url,
                canonical_url=item.canonical_url,
                title=item.title,
                provider_key=item.provider_key,
                source_authority=item.source_authority,
                fetched_at=item.fetched_at,
                content_type=item.content_type,
                transformation=classify_content_transformation(item.content_type),
                content_sha512=item.fetched_content_sha512,
                source_class=PUBLIC_WEB_SOURCE_CLASS,
                selected_order=index + 1,
            )
            for index, item in enumerate(evidence)
            if item.fetched and not item.withheld_by_governance
        )
        return WebSearchAndFetchResult(
            request_id=request_id,
            activation=activation,
            governance_mode=governance_mode,
            search_run=search_run,
            evidence=tuple(evidence),
            citations=citations,
            should_generate_with_evidence=bool(citations),
            failure_reason=(None if citations else WebFetchFailureReason.NO_RELEVANT_EVIDENCE),
            network_calls_made=network_calls,
        )

    def fetch_direct_url(
        self,
        url: str,
        *,
        request_id: str,
        activation: WebSearchActivation,
        governance_mode: WebEvidenceGovernanceMode,
    ) -> WebSearchAndFetchResult:
        """Fetch one explicitly supplied URL without invoking a Search
        Provider (P8-REQ-002). Shares the same Security Boundary, Governance
        scan and Citation shape as `search_and_fetch()`'s per-result path,
        but never calls `self._search_provider` and uses the Production-wired
        `self._direct_fetch_provider` (P8-A) instead of the Search Fixture's
        `self._fetch_provider`."""
        if activation is WebSearchActivation.DISABLED:
            return WebSearchAndFetchResult(
                request_id=request_id,
                activation=activation,
                governance_mode=governance_mode,
                network_calls_made=0,
                failure_reason=WebFetchFailureReason.URL_FETCH_DISABLED,
            )
        if activation is WebSearchActivation.AUTOMATIC:
            raise NotImplementedError("automatic URL fetch activation is not implemented")

        authority = classify_source_authority(urlsplit(url).hostname or "")
        evidence_id = _digest(f"{request_id}\0direct-url\0{url}")
        rejection = self._validate_url_with_retry(url)
        if rejection is not None:
            return WebSearchAndFetchResult(
                request_id=request_id,
                activation=activation,
                governance_mode=governance_mode,
                evidence=(
                    WebEvidence(
                        evidence_id=evidence_id,
                        result_id=_digest(url),
                        requested_url=url,
                        canonical_url=url,
                        title=url,
                        provider_key="direct_url",
                        source_authority=authority,
                        snippet="",
                        fetched=False,
                        governance_mode=governance_mode,
                        rejected=True,
                        rejection_reason=rejection,
                    ),
                ),
                failure_reason=WebFetchFailureReason.URL_REJECTED,
                network_calls_made=0,
            )

        try:
            fetched = self._direct_fetch_provider.fetch(
                url,
                timeout_seconds=self._config.request_timeout_seconds,
                max_response_bytes=self._config.max_response_bytes,
                max_redirects=self._config.max_redirects,
            )
        except Exception:
            fetched = FetchRejected(reason=WebFetchFailureReason.FETCH_REJECTED)
        if isinstance(fetched, FetchRejected):
            return WebSearchAndFetchResult(
                request_id=request_id,
                activation=activation,
                governance_mode=governance_mode,
                evidence=(
                    WebEvidence(
                        evidence_id=evidence_id,
                        result_id=_digest(url),
                        requested_url=url,
                        canonical_url=url,
                        title=url,
                        provider_key="direct_url",
                        source_authority=authority,
                        snippet="",
                        fetched=False,
                        governance_mode=governance_mode,
                        rejected=True,
                        rejection_reason=fetched.reason,
                    ),
                ),
                failure_reason=WebFetchFailureReason.URL_REJECTED,
                network_calls_made=1,
            )

        # P8-MR2 (P8-MANUAL-002): the real page `<title>` is the honest
        # Title a human would recognize — the URL itself is only ever a
        # Fallback, used exactly when the fetched page has none (or is not
        # HTML at all).
        resolved_title = (
            extract_html_title(fetched.content)
            if fetched.content_type.split(";", 1)[0].strip().casefold() == "text/html"
            else None
        ) or fetched.canonical_url
        evidence = self._build_fetched_evidence(
            evidence_id=evidence_id,
            result_id=_digest(url),
            url=url,
            title=resolved_title,
            snippet="",
            fetched=fetched,
            governance_mode=governance_mode,
            provider_key="direct_url",
        )
        citations = (
            (
                WebCitation(
                    citation_id="web-citation-1",
                    requested_url=evidence.requested_url,
                    canonical_url=evidence.canonical_url,
                    title=evidence.title,
                    provider_key=evidence.provider_key,
                    source_authority=evidence.source_authority,
                    fetched_at=evidence.fetched_at,
                    content_type=evidence.content_type,
                    transformation=classify_content_transformation(evidence.content_type),
                    content_sha512=evidence.fetched_content_sha512,
                    source_class=PUBLIC_WEB_SOURCE_CLASS,
                    selected_order=1,
                ),
            )
            if not evidence.withheld_by_governance
            else ()
        )
        return WebSearchAndFetchResult(
            request_id=request_id,
            activation=activation,
            governance_mode=governance_mode,
            evidence=(evidence,),
            citations=citations,
            should_generate_with_evidence=bool(citations),
            failure_reason=None if citations else WebFetchFailureReason.NO_RELEVANT_EVIDENCE,
            network_calls_made=1,
        )

    def _validate_url_with_retry(self, url: str) -> UrlRejectionReason | None:
        """P8-MR8-2 (P8-CODEX-020): a fixed, bounded Retry Budget around
        this Service's own Security Preflight Validation call —
        `HttpxWebFetchProvider` already retries its own Hop-level
        Validation, but that Retry Budget is only ever reached if this
        earlier, Service-level call succeeds first. A single Transient
        `DNS_RESOLUTION_FAILED` here used to short-circuit straight to
        `url_rejected`, `network_calls_made=0`, before the Fetch Provider
        was ever invoked. Every Permanent Security Rejection still fails
        on the very first attempt, exactly as before."""
        retries_used = 0
        while True:
            rejection = validate_url_before_connect(url, resolver=self._resolver)
            if (
                rejection in _PREFLIGHT_RETRYABLE_REASONS
                and retries_used < self._preflight_max_retries
            ):
                retries_used += 1
                self._preflight_sleep_fn(self._preflight_retry_backoff_seconds)
                continue
            return rejection

    def _build_fetched_evidence(
        self,
        *,
        evidence_id: str,
        result_id: str,
        url: str,
        title: str,
        snippet: str,
        fetched: FetchedContent,
        governance_mode: WebEvidenceGovernanceMode,
        provider_key: str | None = None,
    ) -> WebEvidence:
        content_digest = _digest(fetched.content)
        injection_detected = (
            governance_mode is not WebEvidenceGovernanceMode.OFF
            and detect_prompt_injection(fetched.content)
        )
        withhold = injection_detected and governance_mode is WebEvidenceGovernanceMode.ENFORCE
        # P8-RW6-A (P8-CODEX-005): Source Authority must reflect the Host
        # actually read (`fetched.canonical_url`, the final, post-Redirect
        # URL — see `FetchedContent.canonical_url` / `HttpxWebFetchProvider`),
        # never the pre-Redirect `url` a caller merely requested. A Redirect
        # that crosses Authority Classes must never inherit the requested
        # Host's Trust Class.
        authority = classify_source_authority(urlsplit(fetched.canonical_url).hostname or "")
        return WebEvidence(
            evidence_id=evidence_id,
            result_id=result_id,
            requested_url=url,
            canonical_url=fetched.canonical_url,
            title=title,
            provider_key=provider_key or self._search_provider.provider_key,
            source_authority=authority,
            snippet=snippet,
            fetched=True,
            fetched_content=None if withhold else fetched.content,
            fetched_content_sha512=content_digest,
            withheld_by_governance=withhold,
            fetched_at=fetched.fetched_at,
            published_or_updated_at=fetched.published_or_updated_at,
            content_type=fetched.content_type,
            transformation=classify_content_transformation(fetched.content_type),
            prompt_injection_detected=injection_detected,
            governance_mode=governance_mode,
        )


def _digest(value: str) -> str:
    return hashlib.sha512(value.encode("utf-8")).hexdigest()


def _duration_ms(started: float) -> float:
    return max(0.0, (time.perf_counter() - started) * 1000.0)
