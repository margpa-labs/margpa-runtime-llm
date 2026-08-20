"""Stable public surface for the runtime composition switchboard module."""

from .application import ComponentRegistryService
from .contracts import (
    ComponentDescriptor,
    ComponentRegistrationError,
    ComponentRegistrationErrorCode,
    ComponentSideEffectLevel,
    ComponentState,
    build_component_descriptor,
    component_digest,
)
from .ports import ComponentRegistryPort

__all__ = [
    "ComponentDescriptor",
    "ComponentRegistrationError",
    "ComponentRegistrationErrorCode",
    "ComponentRegistryPort",
    "ComponentRegistryService",
    "ComponentSideEffectLevel",
    "ComponentState",
    "build_component_descriptor",
    "component_digest",
]
