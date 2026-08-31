"""Unit tests for Phase 8 (P8-D) ToolRegistry."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.adapters.dev_agent import FakeToolPort
from margpa_runtime_llm.modules.dev_agent import DuplicateToolIdError, ToolDescriptor, ToolRegistry


def _descriptor(tool_id: str = "list_files") -> ToolDescriptor:
    return ToolDescriptor(tool_id=tool_id, name="Name", description="Description")


def test_register_and_lookup() -> None:
    registry = ToolRegistry()
    port = FakeToolPort()
    registry.register(_descriptor("list_files"), port)

    assert registry.get_descriptor("list_files") is not None
    assert registry.get_port("list_files") is port
    assert registry.get_descriptor("unknown") is None
    assert registry.get_port("unknown") is None
    assert len(registry.list_descriptors()) == 1


def test_duplicate_tool_id_rejected() -> None:
    registry = ToolRegistry()
    port = FakeToolPort()
    registry.register(_descriptor("list_files"), port)
    with pytest.raises(DuplicateToolIdError):
        registry.register(_descriptor("list_files"), port)
