"""Phase 8 (P8-D): Fake/Deterministic Tool Adapter.

Serves a small, fixed in-memory Fixture — never the real filesystem, never
the network. One `FakeToolPort` instance dispatches on `tool_id` internally
and is registered against several `ToolDescriptor`s, so a multi-step Golden
Path Plan can chain `list_files` -> `read_file` -> `write_note` (the last one
carrying an `important_gate_reason`, driving the Approval-Gate Golden Path)
with fully deterministic, reproducible output.
"""

from __future__ import annotations

from collections.abc import Mapping

from ...modules.dev_agent.ports import (
    ToolExecutionFailed,
    ToolExecutionOutcome,
    ToolExecutionSucceeded,
)

FIXTURE_FILES: Mapping[str, str] = {
    "notes/readme.md": "# Fixture Notes\n\nThis is Fixture content only.",
    "notes/todo.md": "- [ ] Fixture item one\n- [ ] Fixture item two",
}

LIST_FILES_TOOL_ID = "list_files"
READ_FILE_TOOL_ID = "read_file"
WRITE_NOTE_TOOL_ID = "write_note"


class FakeToolPort:
    """Deterministic in-memory Tool implementation for `list_files`,
    `read_file`, and `write_note` — the three Fixture Tools this Package
    registers in `bootstrap/dev_agent.py`."""

    def __init__(self) -> None:
        self._written_notes: dict[str, str] = {}

    def execute(self, tool_id: str, input: Mapping[str, object]) -> ToolExecutionOutcome:
        if tool_id == LIST_FILES_TOOL_ID:
            return ToolExecutionSucceeded(output={"paths": sorted(FIXTURE_FILES)})
        if tool_id == READ_FILE_TOOL_ID:
            path = input.get("path")
            if not isinstance(path, str) or path not in FIXTURE_FILES:
                return ToolExecutionFailed(reason="path_not_found")
            return ToolExecutionSucceeded(output={"path": path, "content": FIXTURE_FILES[path]})
        if tool_id == WRITE_NOTE_TOOL_ID:
            path = input.get("path")
            content = input.get("content")
            if not isinstance(path, str) or not isinstance(content, str):
                return ToolExecutionFailed(reason="invalid_input")
            self._written_notes[path] = content
            return ToolExecutionSucceeded(output={"path": path, "written": True})
        return ToolExecutionFailed(reason="unknown_tool")

    def written_notes(self) -> Mapping[str, str]:
        """Read-only Test/Diagnostic accessor — never used by the Run
        engine itself, which only ever sees `ToolExecutionOutcome`."""
        return dict(self._written_notes)
