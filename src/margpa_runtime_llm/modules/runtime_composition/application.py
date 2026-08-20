"""Process-local, non-persistent implementation of the component registry.

Rebuilt fresh on every process start (matching the existing non-persistent
Configuration Control state). Registration only records the state a
component's own existing gate already resolved; it never itself decides
whether a component may run.
"""

from __future__ import annotations

from .contracts import (
    ComponentDescriptor,
    ComponentRegistrationError,
    ComponentRegistrationErrorCode,
    ComponentState,
)


class ComponentRegistryService:
    def __init__(self) -> None:
        self._components: dict[str, ComponentDescriptor] = {}

    def register(self, descriptor: ComponentDescriptor) -> None:
        if descriptor.component_key in self._components:
            raise ComponentRegistrationError(
                code=ComponentRegistrationErrorCode.DUPLICATE_COMPONENT,
                safe_message="A component with this key is already registered.",
                component_key=descriptor.component_key,
            )
        if descriptor.state is ComponentState.ENABLED:
            for existing in self._components.values():
                if existing.state is not ComponentState.ENABLED:
                    continue
                if (
                    descriptor.component_key in existing.conflicts_with
                    or existing.component_key in descriptor.conflicts_with
                ):
                    raise ComponentRegistrationError(
                        code=ComponentRegistrationErrorCode.CONFLICTING_COMPONENTS_ENABLED,
                        safe_message="Two conflicting components cannot both be enabled.",
                        component_key=descriptor.component_key,
                    )
            for dependency_key in descriptor.required_dependencies:
                dependency = self._components.get(dependency_key)
                if dependency is None or dependency.state is not ComponentState.ENABLED:
                    raise ComponentRegistrationError(
                        code=ComponentRegistrationErrorCode.UNRESOLVED_REQUIRED_DEPENDENCY,
                        safe_message="An enabled component is missing a required dependency.",
                        component_key=descriptor.component_key,
                    )
        self._components[descriptor.component_key] = descriptor

    def resolve(self, component_key: str) -> ComponentDescriptor | None:
        return self._components.get(component_key)

    def list_components(self) -> tuple[ComponentDescriptor, ...]:
        return tuple(self._components[key] for key in sorted(self._components))
