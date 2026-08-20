"""Registration/resolution tests for the process-local component registry."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.runtime_composition.application import ComponentRegistryService
from margpa_runtime_llm.modules.runtime_composition.contracts import (
    ComponentDescriptor,
    ComponentRegistrationError,
    ComponentRegistrationErrorCode,
    ComponentState,
    build_component_descriptor,
)


def _descriptor(key: str, state: ComponentState, **overrides: object) -> ComponentDescriptor:
    fields: dict[str, object] = {
        "component_key": key,
        "kind": "feature",
        "version": "1",
        "state": state,
        "capabilities": () if state is not ComponentState.ENABLED else ("x",),
        "degraded_reasons": () if state is ComponentState.ENABLED else ("unavailable",),
    }
    fields.update(overrides)
    return build_component_descriptor(**fields)  # type: ignore[arg-type]


def test_register_and_resolve_round_trip() -> None:
    registry = ComponentRegistryService()
    descriptor = _descriptor("documentation_rag", ComponentState.ENABLED)
    registry.register(descriptor)
    assert registry.resolve("documentation_rag") == descriptor
    assert registry.resolve("missing") is None
    assert registry.list_components() == (descriptor,)


def test_list_components_is_sorted_by_key() -> None:
    registry = ComponentRegistryService()
    registry.register(_descriptor("zeta", ComponentState.DISABLED))
    registry.register(_descriptor("alpha", ComponentState.DISABLED))
    assert [item.component_key for item in registry.list_components()] == ["alpha", "zeta"]


def test_duplicate_registration_rejected() -> None:
    registry = ComponentRegistryService()
    registry.register(_descriptor("documentation_rag", ComponentState.DISABLED))
    with pytest.raises(ComponentRegistrationError) as excinfo:
        registry.register(_descriptor("documentation_rag", ComponentState.DISABLED))
    assert excinfo.value.code is ComponentRegistrationErrorCode.DUPLICATE_COMPONENT


def test_conflicting_registration_rejected() -> None:
    registry = ComponentRegistryService()
    registry.register(
        _descriptor("a", ComponentState.ENABLED, conflicts_with=("b",)),
    )
    with pytest.raises(ComponentRegistrationError) as excinfo:
        registry.register(_descriptor("b", ComponentState.ENABLED, conflicts_with=("a",)))
    assert excinfo.value.code is ComponentRegistrationErrorCode.CONFLICTING_COMPONENTS_ENABLED


def test_conflict_with_a_disabled_component_is_allowed() -> None:
    registry = ComponentRegistryService()
    registry.register(_descriptor("a", ComponentState.DISABLED, conflicts_with=("b",)))
    registry.register(_descriptor("b", ComponentState.ENABLED, conflicts_with=("a",)))
    assert registry.resolve("b") is not None


def test_unresolved_required_dependency_rejected() -> None:
    registry = ComponentRegistryService()
    with pytest.raises(ComponentRegistrationError) as excinfo:
        registry.register(
            _descriptor("dependent", ComponentState.ENABLED, required_dependencies=("base",)),
        )
    assert excinfo.value.code is ComponentRegistrationErrorCode.UNRESOLVED_REQUIRED_DEPENDENCY


def test_required_dependency_must_itself_be_enabled() -> None:
    registry = ComponentRegistryService()
    registry.register(_descriptor("base", ComponentState.DISABLED))
    with pytest.raises(ComponentRegistrationError):
        registry.register(
            _descriptor("dependent", ComponentState.ENABLED, required_dependencies=("base",)),
        )


def test_registry_grants_no_execution_authority() -> None:
    """Registering ENABLED does not itself run, call, or open anything."""

    registry = ComponentRegistryService()
    descriptor = _descriptor("documentation_rag", ComponentState.ENABLED)
    registry.register(descriptor)
    resolved = registry.resolve("documentation_rag")
    assert resolved is not None
    assert not hasattr(resolved, "execute")
    assert not hasattr(resolved, "run")
