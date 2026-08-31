"""Phase 8 (P8-D): replaceable Ports for the Dev Agent Tool Harness.

Both `ToolPort` and `McpClientPort` share the same `ToolExecutionOutcome`
shape (`ToolExecutionSucceeded | ToolExecutionFailed`) so the Run Service
never needs to know whether a given Tool call was served by an in-process
Fake/Deterministic adapter or (in a future Package) a real MCP Client — the
Foundation ships only the former plus a Fixture-only implementation of the
latter (P8-D scope: Port + Fixture, never a real network-connected Client).
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from .contracts import RunSnapshot


@dataclass(frozen=True, slots=True)
class ToolExecutionSucceeded:
    output: dict[str, object]


@dataclass(frozen=True, slots=True)
class ToolExecutionFailed:
    reason: str


ToolExecutionOutcome = ToolExecutionSucceeded | ToolExecutionFailed


@runtime_checkable
class ToolPort(Protocol):
    def execute(
        self,
        tool_id: str,
        input: Mapping[str, object],
    ) -> ToolExecutionOutcome: ...


@runtime_checkable
class McpClientPort(Protocol):
    """P8-D: the shape a real MCP Client Adapter would implement. This
    Package ships only a Fixture-backed implementation
    (`adapters.dev_agent.mcp_fixture_adapter.FixtureMcpClient`) — no
    Production wiring exists that reaches a real MCP Server (Real Network /
    Remote MCP are explicitly out of this Task's Authority)."""

    def call_tool(
        self,
        name: str,
        arguments: Mapping[str, object],
    ) -> ToolExecutionOutcome: ...


@runtime_checkable
class DevAgentRunStorePort(Protocol):
    """P8-E: Run/Step Evidence Persistence boundary. `save()` is called
    after every state transition the Run Service produces; `load_all()` is
    called once at Composition time so a Restart/Reload recovers every Run
    that existed before the process stopped (Two-tab and mid-Run Shutdown
    are both covered by the same mechanism — state lives here, not in any
    one connection)."""

    def save(self, run: RunSnapshot) -> None: ...

    def load_all(self) -> tuple[RunSnapshot, ...]: ...
