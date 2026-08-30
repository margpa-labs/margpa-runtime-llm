"""Phase 7 (P7-E/F): orchestrate Governed Web Search -> Security Boundary ->
Fetch -> Prompt Injection Governance -> Citation, mirroring
`DocumentationRagApplicationService`'s single deterministic Pipeline shape."""

from __future__ import annotations

import hashlib
import time
from urllib.parse import urlsplit

from ..contracts import (
    PUBLIC_WEB_SOURCE_CLASS,
    SourceAuthorityClass,
    WebCitation,
    WebEvidence,
    WebEvidenceGovernanceMode,
    WebFetchFailureReason,
    WebSearchActivation,
    WebSearchAndFetchResult,
    WebSearchFeatureConfig,
    WebSearchQuery,
    WebSearchRun,
    classify_source_authority,
)
from ..domain import (
    detect_prompt_injection,
    detect_secret_candidates,
    validate_url_before_connect,
)
from ..ports import FetchedContent, FetchRejected, WebFetchProviderPort, WebSearchProviderPort

__all__ = ["PUBLIC_WEB_SOURCE_CLASS", "WebKnowledgeService"]


class WebKnowledgeService:
    def __init__(
        self,
        *,
        search_provider: WebSearchProviderPort,
        fetch_provider: WebFetchProviderPort,
        config: WebSearchFeatureConfig,
    ) -> None:
        self._search_provider = search_provider
        self._fetch_provider = fetch_provider
        self._config = config

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
            rejection = validate_url_before_connect(item.url)
            if rejection is not None:
                evidence.append(
                    WebEvidence(
                        evidence_id=evidence_id,
                        result_id=item.result_id,
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
                    authority=authority,
                    fetched=fetch_result,
                    governance_mode=governance_mode,
                )
            )

        citations = tuple(
            WebCitation(
                citation_id=f"web-citation-{index + 1}",
                canonical_url=item.canonical_url,
                title=item.title,
                provider_key=item.provider_key,
                source_authority=item.source_authority,
                fetched_at=item.fetched_at,
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

    def _build_fetched_evidence(
        self,
        *,
        evidence_id: str,
        result_id: str,
        url: str,
        title: str,
        snippet: str,
        authority: SourceAuthorityClass,
        fetched: FetchedContent,
        governance_mode: WebEvidenceGovernanceMode,
    ) -> WebEvidence:
        content_digest = _digest(fetched.content)
        injection_detected = (
            governance_mode is not WebEvidenceGovernanceMode.OFF
            and detect_prompt_injection(fetched.content)
        )
        withhold = injection_detected and governance_mode is WebEvidenceGovernanceMode.ENFORCE
        return WebEvidence(
            evidence_id=evidence_id,
            result_id=result_id,
            canonical_url=url,
            title=title,
            provider_key=self._search_provider.provider_key,
            source_authority=authority,
            snippet=snippet,
            fetched=True,
            fetched_content=None if withhold else fetched.content,
            fetched_content_sha512=content_digest,
            withheld_by_governance=withhold,
            fetched_at=fetched.fetched_at,
            published_or_updated_at=fetched.published_or_updated_at,
            content_type=fetched.content_type,
            prompt_injection_detected=injection_detected,
            governance_mode=governance_mode,
        )


def _digest(value: str) -> str:
    return hashlib.sha512(value.encode("utf-8")).hexdigest()


def _duration_ms(started: float) -> float:
    return max(0.0, (time.perf_counter() - started) * 1000.0)
