"""Phase 7 (P7-E/F): real HTTP Fetch Provider, bounded by the URL Security
Boundary at every hop (initial URL and every redirect Location).

`transport` is injectable so tests exercise real httpx request-building,
redirect-following, and streaming-size-cap logic against an in-process
`httpx.MockTransport` — genuine HTTP semantics, zero real sockets opened
(see `tests/unit/web_knowledge/test_httpx_fetch_provider.py`).
"""

from __future__ import annotations

from datetime import UTC, datetime
from urllib.parse import urljoin

import httpx

from margpa_runtime_llm.modules.web_knowledge.contracts import (
    UrlRejectionReason,
    WebFetchFailureReason,
)
from margpa_runtime_llm.modules.web_knowledge.domain.url_security import (
    validate_url_before_connect,
)
from margpa_runtime_llm.modules.web_knowledge.ports import FetchedContent, FetchRejected

_ALLOWED_CONTENT_TYPES = frozenset({"text/html", "text/plain", "text/markdown", "application/json"})
_REDIRECT_STATUS_CODES = frozenset({301, 302, 303, 307, 308})


class HttpxWebFetchProvider:
    def __init__(self, *, transport: httpx.BaseTransport | None = None) -> None:
        self._transport = transport

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
        with httpx.Client(
            transport=self._transport,
            timeout=timeout_seconds,
            follow_redirects=False,
        ) as client:
            while True:
                rejection = validate_url_before_connect(current_url)
                if rejection is not None:
                    return FetchRejected(reason=rejection)
                try:
                    with client.stream("GET", current_url) as response:
                        if response.status_code in _REDIRECT_STATUS_CODES:
                            location = response.headers.get("location")
                            if not location:
                                return FetchRejected(reason=WebFetchFailureReason.FETCH_REJECTED)
                            if redirects_followed >= max_redirects:
                                return FetchRejected(reason=UrlRejectionReason.TOO_MANY_REDIRECTS)
                            current_url = urljoin(current_url, location)
                            redirects_followed += 1
                            continue

                        content_type = (
                            response.headers.get("content-type", "")
                            .split(";", 1)[0]
                            .strip()
                            .casefold()
                        )
                        if content_type not in _ALLOWED_CONTENT_TYPES:
                            return FetchRejected(reason=UrlRejectionReason.CONTENT_TYPE_UNSUPPORTED)
                        declared_length = response.headers.get("content-length")
                        if declared_length is not None:
                            try:
                                if int(declared_length) > max_response_bytes:
                                    return FetchRejected(
                                        reason=UrlRejectionReason.RESPONSE_TOO_LARGE
                                    )
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
                            published_or_updated_at=response.headers.get("last-modified"),
                        )
                except httpx.TimeoutException:
                    return FetchRejected(reason=UrlRejectionReason.TIMEOUT)
                except httpx.HTTPError:
                    return FetchRejected(reason=WebFetchFailureReason.FETCH_REJECTED)
