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
from collections.abc import Callable, Sequence
from urllib.parse import urlsplit

from ..contracts import UrlRejectionReason

ALLOWED_SCHEMES = frozenset({"http", "https"})

GetAddrInfoResult = tuple[
    socket.AddressFamily,
    socket.SocketKind,
    int,
    str,
    tuple[str, int] | tuple[str, int, int, int] | tuple[int, bytes],
]
"""Mirrors `socket.getaddrinfo()`'s real return element shape exactly, so
`default_resolver` type-checks as a plain pass-through and a Fake Resolver
in Tests can build the same well-known 5-tuples the existing
`monkeypatch.setattr(socket, "getaddrinfo", ...)`-based Tests already do."""

Resolver = Callable[[str, int], Sequence[GetAddrInfoResult]]
"""P8-MR7-1 (P8-CODEX-013): the sole DNS-resolution seam of the URL
Security Boundary, injectable so Tests can prove Public IPv4/IPv6
acceptance, transient-DNS-failure retry-recovery, and hostname-resolves-
to-private-address rejection deterministically, with zero real sockets
opened — instead of relying only on monkeypatching the global `socket`
module. `default_resolver` below still calls through the real
`socket.getaddrinfo` symbol (not a private copy of it), so every existing
`monkeypatch.setattr(socket, "getaddrinfo", ...)`-based Test keeps working
unchanged; `resolver` is purely an additional, explicit override a caller
may supply instead."""


def default_resolver(hostname: str, port: int) -> Sequence[GetAddrInfoResult]:
    return socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)


_METADATA_HOSTNAME_DENYLIST = frozenset(
    {
        "metadata.google.internal",
        "metadata.goog",
    }
)

# P8-REQ-003 / Controller Recovery §6 item 4: MVP-tier denylist of common
# non-HTTP internal/administrative service ports (PoC/MVP Portfolio Operating
# Policy P2 tier, not an exhaustive enterprise port-scan defense — mirrors
# this module's own documented posture on the hostname denylist above).
# Standard/common HTTP(S) ports (80, 443, 8080, 8443, ...) are deliberately
# never on this list — a candidate port is dangerous only if explicitly
# named here, never rejected merely for being non-standard.
_DANGEROUS_PORTS = frozenset(
    {
        22,  # SSH
        23,  # Telnet
        25,  # SMTP
        135,  # Windows RPC
        139,  # NetBIOS
        445,  # SMB
        1433,  # Microsoft SQL Server
        1521,  # Oracle DB
        2375,  # Docker (unauthenticated)
        2376,  # Docker (TLS)
        3306,  # MySQL/MariaDB
        3389,  # RDP
        5432,  # PostgreSQL
        5900,  # VNC
        6379,  # Redis
        8500,  # Consul
        9200,  # Elasticsearch
        9300,  # Elasticsearch transport
        11211,  # Memcached
        27017,  # MongoDB
    }
)


def validate_url_before_connect(
    url: str,
    *,
    resolver: Resolver = default_resolver,
) -> UrlRejectionReason | None:
    """Returns `None` when the URL is safe to connect to, else the reason
    it was rejected. Never raises for a malformed/unsafe URL — a caller
    that forgets to check the return value gets a rejection reason string
    it must positively test for `is None`, not an exception it can
    accidentally swallow.

    `resolver` (P8-MR7-1) defaults to the real DNS-resolving
    `default_resolver` — Production behavior is unchanged unless a caller
    (a Test, invariably) explicitly overrides it."""

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

    try:
        explicit_port = parts.port
    except ValueError:
        # `urlsplit(...).port` raises for a syntactically out-of-range port
        # (e.g. ":99999999") rather than returning `None` — treated the same
        # as any other malformed URL, never an uncaught exception escaping
        # this Security Boundary.
        return UrlRejectionReason.UNSUPPORTED_SCHEME
    port = explicit_port or (443 if parts.scheme.casefold() == "https" else 80)
    if port in _DANGEROUS_PORTS:
        return UrlRejectionReason.DANGEROUS_PORT

    literal_reason = _reject_if_unsafe_ip(normalized_hostname)
    if literal_reason is not None:
        return literal_reason
    if _is_ip_literal(normalized_hostname):
        return None

    try:
        resolved = resolver(normalized_hostname, port)
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
