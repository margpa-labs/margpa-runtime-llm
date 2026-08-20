"""Typed registry port for the runtime composition switchboard."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .contracts import ComponentDescriptor


@runtime_checkable
class ComponentRegistryPort(Protocol):
    def register(self, descriptor: ComponentDescriptor) -> None: ...

    def resolve(self, component_key: str) -> ComponentDescriptor | None: ...

    def list_components(self) -> tuple[ComponentDescriptor, ...]: ...
