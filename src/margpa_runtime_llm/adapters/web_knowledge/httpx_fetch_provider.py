"""Phase 7 (P7-E/F): real HTTP Fetch Provider, bounded by the URL Security
Boundary at every hop (initial URL and every redirect Location).

`transport` is injectable so tests exercise real httpx request-building,
redirect-following, and streaming-size-cap logic against an in-process
`httpx.MockTransport` — genuine HTTP semantics, zero real sockets opened
(see `tests/unit/web_knowledge/test_httpx_fetch_provider.py`).

Phase 8 (P8-MR1 / P8-MANUAL-001): adds a small, fixed Retry Budget shared
across the whole `fetch()` call (every redirect hop draws from the same
budget, so worst-case latency stays bounded by
`(max_retries + 1) * timeout_seconds` regardless of how many redirects
occur — never a separate full retry allowance per hop). Only genuinely
transient reasons are retried (`_RETRYABLE_REASONS`); a Permanent Unsafe
URL rejection (private/loopback/credentials/dangerous port/...) is never
retried — it fails on the very first attempt, exactly as before. `sleep_fn`
is injectable so Tests prove the Retry path deterministically with zero
real wall-clock delay.
"""

from __future__ import annotations

import socket
import ssl
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urljoin

import httpx

from margpa_runtime_llm.modules.web_knowledge.contracts import (
    UrlRejectionReason,
    WebFetchFailureReason,
)
from margpa_runtime_llm.modules.web_knowledge.domain.url_security import (
    Resolver,
    default_resolver,
    validate_url_before_connect,
)
from margpa_runtime_llm.modules.web_knowledge.ports import FetchedContent, FetchRejected

_ALLOWED_CONTENT_TYPES = frozenset({"text/html", "text/plain", "text/markdown", "application/json"})
_REDIRECT_STATUS_CODES = frozenset({301, 302, 303, 307, 308})

DEFAULT_MAX_RETRIES = 2
"""P8-MR1: up to 2 Retries (3 attempts total) for a Retryable Failure —
fixed, not user-configurable, so worst-case latency stays predictable."""
DEFAULT_RETRY_BACKOFF_SECONDS = 0.2

_RETRYABLE_REASONS = frozenset(
    {
        UrlRejectionReason.DNS_RESOLUTION_FAILED,
        UrlRejectionReason.TIMEOUT,
        UrlRejectionReason.CONNECT_FAILED,
    }
)
"""P8-MR1: a one-off DNS hiccup, connect refusal, or timeout is often
transient — retried up to the fixed Budget. `TLS_FAILED`/
`HTTP_PROTOCOL_ERROR` and every Security-Boundary Permanent Rejection
(private/loopback/credentials/dangerous port/unsupported scheme/too many
redirects/response too large/content type unsupported) are never retried
— retrying them cannot plausibly change the outcome within one bounded
fetch attempt."""


@dataclass(frozen=True, slots=True)
class _RedirectTo:
    location: str


def _classify_connect_error(exc: httpx.ConnectError) -> UrlRejectionReason:
    """P8-MR1: `httpx.ConnectError` wraps several distinct lower-level
    failures behind one exception type; the wrapped `__cause__` is used
    (best-effort, never raises) to recover the more specific, honest
    reason a caller/UI can actually act on."""

    cause = exc.__cause__
    if isinstance(cause, socket.gaierror):
        return UrlRejectionReason.DNS_RESOLUTION_FAILED
    if isinstance(cause, ssl.SSLError):
        return UrlRejectionReason.TLS_FAILED
    return UrlRejectionReason.CONNECT_FAILED


class HttpxWebFetchProvider:
    def __init__(
        self,
        *,
        transport: httpx.BaseTransport | None = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff_seconds: float = DEFAULT_RETRY_BACKOFF_SECONDS,
        sleep_fn: Callable[[float], None] = time.sleep,
        resolver: Resolver = default_resolver,
    ) -> None:
        self._transport = transport
        self._max_retries = max_retries
        self._retry_backoff_seconds = retry_backoff_seconds
        self._sleep_fn = sleep_fn
        # P8-MR7-1 (P8-CODEX-013): same Resolver Dependency as
        # `WebKnowledgeService` — this Hop-level Validation Boundary must
        # never be left calling real DNS while the Service Boundary is
        # Faked (or vice versa); both share the identical seam.
        self._resolver = resolver

    def fetch(
        self,
        url: str,
        *,
        timeout_seconds: float,
        max_response_bytes: int,
        max_redirects: int,
    ) -> FetchedContent | FetchRejected:
        current_url = url
        redirects_followed = 0
        retries_used = 0
        with httpx.Client(
            transport=self._transport,
            timeout=timeout_seconds,
            follow_redirects=False,
        ) as client:
            while True:
                result = self._attempt_one_hop(
                    client, current_url, max_response_bytes=max_response_bytes
                )
                if (
                    isinstance(result, FetchRejected)
                    and result.reason in _RETRYABLE_REASONS
                    and retries_used < self._max_retries
                ):
                    retries_used += 1
                    self._sleep_fn(self._retry_backoff_seconds)
                    continue
                if isinstance(result, _RedirectTo):
                    if redirects_followed >= max_redirects:
                        return FetchRejected(reason=UrlRejectionReason.TOO_MANY_REDIRECTS)
                    current_url = result.location
                    redirects_followed += 1
                    continue
                return result

    def _attempt_one_hop(
        self,
        client: httpx.Client,
        url: str,
        *,
        max_response_bytes: int,
    ) -> FetchedContent | FetchRejected | _RedirectTo:
        rejection = validate_url_before_connect(url, resolver=self._resolver)
        if rejection is not None:
            return FetchRejected(reason=rejection)
        try:
            with client.stream("GET", url) as response:
                if response.status_code in _REDIRECT_STATUS_CODES:
                    location = response.headers.get("location")
                    if not location:
                        return FetchRejected(reason=WebFetchFailureReason.FETCH_REJECTED)
                    return _RedirectTo(location=urljoin(url, location))

                content_type = (
                    response.headers.get("content-type", "").split(";", 1)[0].strip().casefold()
                )
                if content_type not in _ALLOWED_CONTENT_TYPES:
                    return FetchRejected(reason=UrlRejectionReason.CONTENT_TYPE_UNSUPPORTED)
                declared_length = response.headers.get("content-length")
                if declared_length is not None:
                    try:
                        if int(declared_length) > max_response_bytes:
                            return FetchRejected(reason=UrlRejectionReason.RESPONSE_TOO_LARGE)
                    except ValueError:
                        pass

                chunks: list[bytes] = []
                total = 0
                for chunk in response.iter_bytes():
                    total += len(chunk)
                    if total > max_response_bytes:
                        return FetchRejected(reason=UrlRejectionReason.RESPONSE_TOO_LARGE)
                    chunks.append(chunk)
                raw = b"".join(chunks)
                try:
                    text = raw.decode("utf-8")
                except UnicodeDecodeError:
                    return FetchRejected(reason=UrlRejectionReason.CONTENT_TYPE_UNSUPPORTED)
                return FetchedContent(
                    content=text,
                    content_type=content_type,
                    fetched_at=datetime.now(UTC).isoformat(),
                    canonical_url=url,
                    published_or_updated_at=response.headers.get("last-modified"),
                )
        except httpx.TimeoutException:
            return FetchRejected(reason=UrlRejectionReason.TIMEOUT)
        except httpx.ConnectError as exc:
            return FetchRejected(reason=_classify_connect_error(exc))
        except httpx.ProtocolError:
            return FetchRejected(reason=UrlRejectionReason.HTTP_PROTOCOL_ERROR)
        except httpx.HTTPError:
            return FetchRejected(reason=WebFetchFailureReason.FETCH_REJECTED)
