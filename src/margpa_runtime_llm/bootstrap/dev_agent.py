"""Phase 8 (P8-D/P8-E/P8-MR5): composition root for the Dev Agent Foundation.

P8-MR5 (P8-MANUAL-005): Production Composition now wires
`FixtureWorkspaceToolPort` — a traceable, real-File Adapter confined to
`<runtime_data_root>/persistent/<scope_key>/dev_agent/fixture_workspace/` —
in place of the pre-Rework `FakeToolPort`'s Process-Memory-only
`write_note`. This is still a bounded PoC Fixture (never Project Source,
never any other User File, never the Network): only `runtime_data_root`/
`scope_key` change what this Adapter can touch, and Authority never extends
to a real filesystem/network-backed general-purpose Tool or a real MCP
Server (`FixtureMcpClient` exists and is Tested but is never composed into
this Registry). `FakeToolPort` itself is kept as the default for callers
that supply neither `runtime_data_root` nor `scope_key` (Unit Tests that
want pure in-memory state without a real Temp Root — P8-MR5 Required §10.3
"Unit Test用 Pure Fake Adapter は必要なら保持してよい").

`run_store` is optional so unit/integration Tests can compose a Service with
pure in-memory state (as P8-D's own Tests already do); Production wiring
(`entrypoints/web/main.py`) always supplies one so Runs survive a Restart.
"""

from __future__ import annotations

from pathlib import Path

from margpa_runtime_llm.adapters.dev_agent import FakeToolPort, FixtureWorkspaceToolPort
from margpa_runtime_llm.modules.dev_agent import (
    DevAgentRunService,
    DevAgentRunStorePort,
    ImportantGateReason,
    ToolDescriptor,
    ToolRegistry,
)
from margpa_runtime_llm.modules.dev_agent.ports import ToolPort


def build_dev_agent_run_service(
    *,
    run_store: DevAgentRunStorePort | None = None,
    runtime_data_root: Path | None = None,
    scope_key: str = "default",
) -> DevAgentRunService:
    registry = ToolRegistry()
    tool: ToolPort = (
        FixtureWorkspaceToolPort(runtime_data_root=runtime_data_root, scope_key=scope_key)
        if runtime_data_root is not None
        else FakeToolPort()
    )
    registry.register(
        ToolDescriptor(
            tool_id="list_files",
            name="List Files",
            description="Lists the paths available in the Fixture Workspace.",
            budget_cost=1,
        ),
        tool,
    )
    registry.register(
        ToolDescriptor(
            tool_id="read_file",
            name="Read File",
            description="Reads one Fixture Workspace file's content by path.",
            budget_cost=1,
        ),
        tool,
    )
    registry.register(
        ToolDescriptor(
            tool_id="write_note",
            name="Write Note",
            description="Writes a Note into the Fixture Workspace, confined to "
            "`fixture_workspace_only` — never Project Source or the Network. Gated as "
            "`external_write` — this is the Tool the important-gate-only Golden "
            "Path exercises.",
            important_gate_reason=ImportantGateReason.EXTERNAL_WRITE,
            # P8-RW6-B (P8-CODEX-006): a Write costs more Budget Units than a
            # Read — proportional to the Fake/Deterministic Foundation's own
            # Tool set, not a real dollar amount.
            budget_cost=5,
        ),
        tool,
    )
    return DevAgentRunService(tool_registry=registry, run_store=run_store)
