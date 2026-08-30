"""Phase 7 (P7-F): SSRF-conscious URL Security Boundary (Architecture §4).

Every candidate URL — the initial Search Result URL and every redirect hop a
Fetch follows — passes through `validate_url_before_connect()` before any
socket is opened. This is deliberately proportionate MVP scope (PoC/MVP
Portfolio Operating Policy P2 tier), not enterprise-grade SSRF hardening:

- DNS resolution happens once, at validation time; the resolved address is
  not pinned for the subsequent real connection (a DNS-rebinding attacker
  who controls both the resolver and timing could in principle change the
  answer between this check and the real connect). Pinning the validated
  IP into the actual TCP connection would need a custom httpx Transport;
  deferred to Phase 10 Hardening (documented, not silently absent).
- The hostname denylist below is defense-in-depth on top of the private/
  loopback/link-local IP-range checks (which already cover the AWS/GCP/
  Azure metadata IP `169.254.169.254`), not a claim of covering every
  cloud metadata hostname that will ever exist.
"""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlsplit

from ..contracts import UrlRejectionReason

ALLOWED_SCHEMES = frozenset({"http", "https"})

_METADATA_HOSTNAME_DENYLIST = frozenset(
    {
        "metadata.google.internal",
        "metadata.goog",
    }
)


def validate_url_before_connect(url: str) -> UrlRejectionReason | None:
    """Returns `None` when the URL is safe to connect to, else the reason
    it was rejected. Never raises for a malformed/unsafe URL — a caller
    that forgets to check the return value gets a rejection reason string
    it must positively test for `is None`, not an exception it can
    accidentally swallow."""

    try:
        parts = urlsplit(url)
    except ValueError:
        return UrlRejectionReason.UNSUPPORTED_SCHEME
    if parts.scheme.casefold() not in ALLOWED_SCHEMES:
        return UrlRejectionReason.UNSUPPORTED_SCHEME
    if parts.username is not None or parts.password is not None:
        return UrlRejectionReason.CREDENTIALS_IN_URL
    hostname = parts.hostname
    if not hostname:
        return UrlRejectionReason.UNSUPPORTED_SCHEME
    normalized_hostname = hostname.strip(".").casefold()
    if normalized_hostname in _METADATA_HOSTNAME_DENYLIST or normalized_hostname == "localhost":
        return UrlRejectionReason.LINK_LOCAL_OR_METADATA_ADDRESS

    literal_reason = _reject_if_unsafe_ip(normalized_hostname)
    if literal_reason is not None:
        return literal_reason
    if _is_ip_literal(normalized_hostname):
        return None

    port = parts.port or (443 if parts.scheme.casefold() == "https" else 80)
    try:
        resolved = socket.getaddrinfo(normalized_hostname, port, proto=socket.IPPROTO_TCP)
    except OSError:
        return UrlRejectionReason.DNS_RESOLUTION_FAILED
    if not resolved:
        return UrlRejectionReason.DNS_RESOLUTION_FAILED
    for _family, _kind, _proto, _canonname, sockaddr in resolved:
        address = str(sockaddr[0])
        reason = _reject_if_unsafe_ip(address)
        if reason is not None:
            return reason
    return None


def _is_ip_literal(hostname: str) -> bool:
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        return False
    return True


def _reject_if_unsafe_ip(candidate: str) -> UrlRejectionReason | None:
    try:
        address = ipaddress.ip_address(candidate)
    except ValueError:
        return None
    # Link-local/multicast/reserved checked first: CPython's `is_private`
    # is a superset that also covers link-local ranges (RFC 1918 + several
    # other "private use" blocks combined), so checking it first would mask
    # the more specific/informative LINK_LOCAL_OR_METADATA_ADDRESS reason
    # for addresses like the cloud metadata IP 169.254.169.254.
    if address.is_link_local or address.is_multicast or address.is_reserved:
        return UrlRejectionReason.LINK_LOCAL_OR_METADATA_ADDRESS
    if address.is_loopback or address.is_private or address.is_unspecified:
        return UrlRejectionReason.PRIVATE_OR_LOOPBACK_ADDRESS
    return None
