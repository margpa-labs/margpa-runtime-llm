"""Unit tests for Phase 8 (P8-D) FixtureMcpClient (Port + Fixture only)."""

from __future__ import annotations

from margpa_runtime_llm.adapters.dev_agent import FixtureMcpClient
from margpa_runtime_llm.modules.dev_agent import (
    McpClientPort,
    ToolExecutionFailed,
    ToolExecutionSucceeded,
)


def test_fixture_mcp_client_satisfies_the_port_protocol() -> None:
    assert isinstance(FixtureMcpClient(), McpClientPort)


def test_known_fixture_tool_succeeds_and_echoes_arguments() -> None:
    client = FixtureMcpClient()
    result = client.call_tool("fixture.echo", {"a": 1})
    assert isinstance(result, ToolExecutionSucceeded)
    assert result.output["echoed"] is True
    assert result.output["arguments_echo"] == {"a": 1}


def test_unknown_fixture_tool_fails_closed() -> None:
    client = FixtureMcpClient()
    result = client.call_tool("not_a_real_tool", {})
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "unknown_mcp_tool"
