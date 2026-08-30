"""Shared no-real-DNS default for the web_knowledge test suite.

Individual tests that need specific resolution behavior (failure, a
private-address result, etc.) explicitly re-patch `socket.getaddrinfo`
within their own body, which simply overrides this autouse default for
that test — this fixture only saves the common case (most tests just need
DNS to resolve to *some* safe public address without ever touching a real
resolver) from repeating the same boilerplate.
"""

from __future__ import annotations

import socket

import pytest


@pytest.fixture(autouse=True)
def _no_real_dns_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_resolve(host: str, port: int, *, proto: int = 0) -> list[tuple[object, ...]]:
        del host, proto
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_resolve)
