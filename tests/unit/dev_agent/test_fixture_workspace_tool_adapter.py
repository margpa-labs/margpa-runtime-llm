"""Phase 8 (P8-MR5 / P8-MANUAL-005): `FixtureWorkspaceToolPort` tests.

Every Test uses `tmp_path` as `runtime_data_root` — never the User's real
`runtime_data/` (Handoff §12 prohibits Test access to it)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from margpa_runtime_llm.adapters.dev_agent import FixtureWorkspaceToolPort
from margpa_runtime_llm.adapters.dev_agent.fixture_workspace_tool_adapter import (
    LIST_FILES_TOOL_ID,
    READ_FILE_TOOL_ID,
    WRITE_NOTE_TOOL_ID,
)
from margpa_runtime_llm.modules.dev_agent.ports import ToolExecutionFailed, ToolExecutionSucceeded


def _digest(content: str) -> str:
    return hashlib.sha512(content.encode("utf-8")).hexdigest()


def test_list_files_returns_the_exact_seed_paths(tmp_path: Path) -> None:
    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    result = port.execute(LIST_FILES_TOOL_ID, {})
    assert isinstance(result, ToolExecutionSucceeded)
    assert result.output["paths"] == ["notes/readme.md", "notes/todo.md"]


def test_read_file_returns_exact_content_and_digest(tmp_path: Path) -> None:
    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    result = port.execute(READ_FILE_TOOL_ID, {"path": "notes/readme.md"})
    assert isinstance(result, ToolExecutionSucceeded)
    content = result.output["content"]
    assert isinstance(content, str)
    assert content == "# Fixture Notes\n\nThis is Fixture content only."
    assert result.output["content_sha512"] == _digest(content)
    assert result.output["path"] == "notes/readme.md"


def test_read_file_missing_path_fails_without_raising(tmp_path: Path) -> None:
    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    result = port.execute(READ_FILE_TOOL_ID, {"path": "notes/does-not-exist.md"})
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "path_not_found"


def test_write_note_persists_to_real_disk_with_matching_digest(tmp_path: Path) -> None:
    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    content = "Hello from the Dev Agent Demo Run."
    result = port.execute(WRITE_NOTE_TOOL_ID, {"path": "notes/new.md", "content": content})
    assert isinstance(result, ToolExecutionSucceeded)
    assert result.output["path"] == "notes/new.md"
    assert result.output["written"] is True
    assert result.output["content_sha512"] == _digest(content)
    assert result.output["overwrite"] is False
    assert isinstance(result.output["written_at"], str)

    written_path = (
        tmp_path / "persistent" / "default" / "dev_agent" / "fixture_workspace" / "notes" / "new.md"
    )
    assert written_path.is_file()
    assert written_path.read_text(encoding="utf-8") == content
    # P8-MR5: Owner-only File mode, same discipline as JsonFileDevAgentRunStore.
    assert (written_path.stat().st_mode & 0o777) == 0o600


def test_write_note_overwrite_flag_reflects_whether_the_target_already_existed(
    tmp_path: Path,
) -> None:
    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    first = port.execute(WRITE_NOTE_TOOL_ID, {"path": "notes/new.md", "content": "first"})
    assert isinstance(first, ToolExecutionSucceeded)
    assert first.output["overwrite"] is False

    second = port.execute(WRITE_NOTE_TOOL_ID, {"path": "notes/new.md", "content": "second"})
    assert isinstance(second, ToolExecutionSucceeded)
    assert second.output["overwrite"] is True

    written_path = (
        tmp_path / "persistent" / "default" / "dev_agent" / "fixture_workspace" / "notes" / "new.md"
    )
    assert written_path.read_text(encoding="utf-8") == "second"


def test_restart_recovers_a_written_file_and_its_digest(tmp_path: Path) -> None:
    """Models a process Restart: a fresh Adapter instance over the same
    Runtime Data Root must see everything a previous instance wrote."""

    first = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    content = "Written before the (simulated) restart."
    first.execute(WRITE_NOTE_TOOL_ID, {"path": "notes/new.md", "content": content})

    second = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    result = second.execute(READ_FILE_TOOL_ID, {"path": "notes/new.md"})
    assert isinstance(result, ToolExecutionSucceeded)
    assert result.output["content"] == content
    assert result.output["content_sha512"] == _digest(content)


def test_seed_files_are_never_overwritten_on_a_later_restart(tmp_path: Path) -> None:
    """P8-MR5 Required: 'Seed は存在する Current File を Restart ごとに
    上書きしない' — a User's edit to a Seed File must survive a fresh
    Adapter instance re-seeding the same Workspace."""

    first = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    first.execute(LIST_FILES_TOOL_ID, {})  # triggers seeding as a side effect
    seed_path = (
        tmp_path
        / "persistent"
        / "default"
        / "dev_agent"
        / "fixture_workspace"
        / "notes"
        / "readme.md"
    )
    seed_path.write_text("User-edited content, must survive.", encoding="utf-8")

    second = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    result = second.execute(READ_FILE_TOOL_ID, {"path": "notes/readme.md"})
    assert isinstance(result, ToolExecutionSucceeded)
    assert result.output["content"] == "User-edited content, must survive."


@pytest.mark.parametrize(
    "unsafe_path",
    [
        "/etc/passwd",
        "../escape.md",
        "notes/../../escape.md",
        "",
    ],
)
def test_read_file_rejects_absolute_and_root_escape_paths(tmp_path: Path, unsafe_path: str) -> None:
    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    result = port.execute(READ_FILE_TOOL_ID, {"path": unsafe_path})
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "path_not_found"


@pytest.mark.parametrize(
    "unsafe_path",
    [
        "/etc/passwd",
        "../escape.md",
        "notes/../../escape.md",
    ],
)
def test_write_note_rejects_absolute_and_root_escape_paths(
    tmp_path: Path, unsafe_path: str
) -> None:
    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    result = port.execute(WRITE_NOTE_TOOL_ID, {"path": unsafe_path, "content": "must never land"})
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "invalid_input"


def test_write_note_rejects_a_symlink_escape(tmp_path: Path) -> None:
    outside = tmp_path / "outside.md"
    outside.write_text("must never be reached", encoding="utf-8")
    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    port.execute(LIST_FILES_TOOL_ID, {})  # ensure the Workspace exists first
    workspace = tmp_path / "persistent" / "default" / "dev_agent" / "fixture_workspace"
    (workspace / "notes" / "escape-link.md").symlink_to(outside)

    result = port.execute(
        WRITE_NOTE_TOOL_ID, {"path": "notes/escape-link.md", "content": "must be rejected"}
    )
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "invalid_input"
    assert outside.read_text(encoding="utf-8") == "must never be reached"


def test_write_note_targeting_an_existing_directory_fails_without_raising(tmp_path: Path) -> None:
    """P8-MR6 Internal Review (Negative Path): a real filesystem can fail
    in ways `FakeToolPort`'s in-memory dict never could — `os.replace()`
    raises `IsADirectoryError` when the target Path collides with an
    existing Directory (here, the seeded `notes/` directory itself). This
    must converge to a Typed Tool Failure, never an uncaught exception
    reaching `DevAgentRunService.advance()`."""

    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    result = port.execute(WRITE_NOTE_TOOL_ID, {"path": "notes", "content": "x"})
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "workspace_io_error"


def test_unknown_tool_id_fails_without_raising(tmp_path: Path) -> None:
    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    result = port.execute("delete_everything", {})
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "unknown_tool"


def test_project_source_and_arbitrary_user_files_are_never_touched(tmp_path: Path) -> None:
    """P8-MR5's central boundary: nothing outside `fixture_workspace/`
    (Project Source, the real `runtime_data/` root itself, or any sibling
    directory) is ever read or written, even via a crafted `path` Input."""

    sibling_secret = tmp_path / "persistent" / "default" / "some_other_module" / "secret.json"
    sibling_secret.parent.mkdir(parents=True)
    sibling_secret.write_text('{"secret": true}', encoding="utf-8")

    port = FixtureWorkspaceToolPort(runtime_data_root=tmp_path, scope_key="default")
    result = port.execute(READ_FILE_TOOL_ID, {"path": "../some_other_module/secret.json"})
    assert isinstance(result, ToolExecutionFailed)
    assert result.reason == "path_not_found"
