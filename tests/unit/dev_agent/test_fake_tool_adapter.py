"""Unit tests for Phase 8 (P8-D) FakeToolPort."""

from __future__ import annotations

from margpa_runtime_llm.adapters.dev_agent.fake_tool_adapter import FakeToolPort
from margpa_runtime_llm.modules.dev_agent import ToolExecutionFailed, ToolExecutionSucceeded


def test_list_files_is_deterministic() -> None:
    port = FakeToolPort()
    first = port.execute("list_files", {})
    second = port.execute("list_files", {})
    assert first == second
    assert isinstance(first, ToolExecutionSucceeded)
    paths = first.output["paths"]
    assert isinstance(paths, list)
    assert paths == sorted(paths)


def test_read_file_returns_fixture_content() -> None:
    port = FakeToolPort()
    listing = port.execute("list_files", {})
    assert isinstance(listing, ToolExecutionSucceeded)
    path = listing.output["paths"][0]  # type: ignore[index]

    result = port.execute("read_file", {"path": path})
    assert isinstance(result, ToolExecutionSucceeded)
    assert result.output["path"] == path
    assert isinstance(result.output["content"], str)


def test_read_file_unknown_path_fails_closed() -> None:
    port = FakeToolPort()
    result = port.execute("read_file", {"path": "nonexistent.md"})
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "path_not_found"


def test_write_note_is_recorded_and_readable_back_via_accessor() -> None:
    port = FakeToolPort()
    result = port.execute("write_note", {"path": "notes/new.md", "content": "hello"})
    assert isinstance(result, ToolExecutionSucceeded)
    assert port.written_notes() == {"notes/new.md": "hello"}


def test_write_note_invalid_input_fails_closed() -> None:
    port = FakeToolPort()
    result = port.execute("write_note", {"path": "notes/new.md"})
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "invalid_input"


def test_unknown_tool_id_fails_closed() -> None:
    port = FakeToolPort()
    result = port.execute("delete_everything", {})
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "unknown_tool"
