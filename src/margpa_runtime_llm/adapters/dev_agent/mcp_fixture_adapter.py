"""Phase 8 (P8-D): MCP Client Adapter — Port + Fixture only.

`FixtureMcpClient` proves the `McpClientPort` shape is implementable and
Testable end to end, using a fixed in-memory response table. It is
deliberately **not** wired into `bootstrap/dev_agent.py`'s Production
Registry — Remote MCP (any real network-connected MCP Server) is outside
this Task's Authority (Forbidden list). A future Package would compose a
real network-backed implementation of the same `McpClientPort` Protocol
without this Adapter, this Port, or any caller of either needing to change.
"""

from __future__ import annotations

from collections.abc import Mapping

from ...modules.dev_agent.ports import (
    ToolExecutionFailed,
    ToolExecutionOutcome,
    ToolExecutionSucceeded,
)

FIXTURE_TOOL_RESPONSES: Mapping[str, Mapping[str, object]] = {
    "fixture.echo": {"echoed": True},
}


class FixtureMcpClient:
    def call_tool(self, name: str, arguments: Mapping[str, object]) -> ToolExecutionOutcome:
        if name not in FIXTURE_TOOL_RESPONSES:
            return ToolExecutionFailed(reason="unknown_mcp_tool")
        output = dict(FIXTURE_TOOL_RESPONSES[name])
        output["arguments_echo"] = dict(arguments)
        return ToolExecutionSucceeded(output=output)
