"""Phase 8 (P8-D): in-memory Tool Registry.

Purely local bookkeeping (Descriptor <-> Port association) — not a
swappable Port itself, since there is nothing to replace: every Provider of
this Task's Dev Agent Foundation composes the same in-memory Registry
against whichever `ToolPort` adapters it wires in (Fake/Deterministic in
Production Bootstrap for this Package; a real adapter would compose the same
Registry differently in a future Package).
"""

from __future__ import annotations

from ..contracts import ToolDescriptor
from ..ports import ToolPort


class DuplicateToolIdError(ValueError):
    pass


class ToolRegistry:
    def __init__(self) -> None:
        self._descriptors: dict[str, ToolDescriptor] = {}
        self._ports: dict[str, ToolPort] = {}

    def register(self, descriptor: ToolDescriptor, port: ToolPort) -> None:
        if descriptor.tool_id in self._descriptors:
            raise DuplicateToolIdError(f"duplicate tool_id: {descriptor.tool_id}")
        self._descriptors[descriptor.tool_id] = descriptor
        self._ports[descriptor.tool_id] = port

    def get_descriptor(self, tool_id: str) -> ToolDescriptor | None:
        return self._descriptors.get(tool_id)

    def get_port(self, tool_id: str) -> ToolPort | None:
        return self._ports.get(tool_id)

    def list_descriptors(self) -> tuple[ToolDescriptor, ...]:
        return tuple(self._descriptors.values())
