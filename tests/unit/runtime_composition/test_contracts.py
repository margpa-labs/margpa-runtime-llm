"""Contract tests for the runtime composition switchboard descriptors."""

from __future__ import annotations

import pytest

from margpa_runtime_llm.modules.runtime_composition.contracts import (
    ComponentDescriptor,
    ComponentSideEffectLevel,
    ComponentState,
    build_component_descriptor,
    component_digest,
)


def _descriptor(**overrides: object) -> ComponentDescriptor:
    fields: dict[str, object] = {
        "component_key": "documentation_rag",
        "kind": "feature",
        "version": "1",
        "state": ComponentState.ENABLED,
        "capabilities": ("retrieval",),
    }
    fields.update(overrides)
    return build_component_descriptor(**fields)  # type: ignore[arg-type]


def test_enabled_descriptor_constructs() -> None:
    descriptor = _descriptor()
    assert descriptor.state is ComponentState.ENABLED
    assert descriptor.side_effect_level is ComponentSideEffectLevel.NONE


def test_build_component_descriptor_self_verifies() -> None:
    descriptor = _descriptor()
    assert descriptor.canonical_digest == component_digest(descriptor)
    assert len(descriptor.canonical_digest) == 128


@pytest.mark.parametrize("state", [ComponentState.UNAVAILABLE, ComponentState.DENIED])
def test_unavailable_or_denied_requires_no_capabilities_and_a_reason(
    state: ComponentState,
) -> None:
    with pytest.raises(ValueError, match="capabilities"):
        _descriptor(state=state, capabilities=("retrieval",), degraded_reasons=("x",))
    with pytest.raises(ValueError, match="reason"):
        _descriptor(state=state, capabilities=(), degraded_reasons=())
    descriptor = _descriptor(state=state, capabilities=(), degraded_reasons=("adapter_missing",))
    assert descriptor.capabilities == ()


def test_invalid_component_key_rejected() -> None:
    with pytest.raises(ValueError):
        _descriptor(component_key="Not-Valid")
    with pytest.raises(ValueError):
        _descriptor(component_key="")


def test_seam_mode_rejects_non_off() -> None:
    with pytest.raises(ValueError, match="governance seam"):
        _descriptor(governance_seam_mode="observe")


def test_self_reference_rejected() -> None:
    with pytest.raises(ValueError, match="conflict with itself"):
        _descriptor(conflicts_with=("documentation_rag",))
    with pytest.raises(ValueError, match="depend on itself"):
        _descriptor(required_dependencies=("documentation_rag",))


def test_require_and_conflict_with_same_key_rejected() -> None:
    with pytest.raises(ValueError, match="require and conflict"):
        _descriptor(
            required_dependencies=("conversation_persistence",),
            conflicts_with=("conversation_persistence",),
        )


def test_duplicate_dependency_entries_rejected() -> None:
    with pytest.raises(ValueError, match="distinct"):
        _descriptor(required_dependencies=("a", "a"))


def test_digest_is_deterministic_and_excludes_itself() -> None:
    first = _descriptor()
    second = _descriptor()
    assert first.canonical_digest == second.canonical_digest
    assert component_digest(first) == component_digest(second)
    third = _descriptor(capabilities=("retrieval", "citation"))
    assert third.canonical_digest != first.canonical_digest
    assert "canonical_digest" not in first.digest_payload


def test_digest_changes_when_any_payload_field_changes() -> None:
    baseline = _descriptor().canonical_digest
    assert _descriptor(kind="other").canonical_digest != baseline
    assert _descriptor(version="2").canonical_digest != baseline
    assert _descriptor(state=ComponentState.DISABLED, capabilities=()).canonical_digest != baseline
    assert _descriptor(revision=2).canonical_digest != baseline


# --- P2E-CODEX-002: empty/malformed/mismatched digests are never silently accepted. ---


def test_empty_digest_rejected() -> None:
    with pytest.raises(ValueError, match="digest"):
        ComponentDescriptor(
            component_key="documentation_rag",
            kind="feature",
            version="1",
            state=ComponentState.ENABLED,
            canonical_digest="",
            capabilities=("retrieval",),
        )


def test_invalid_digest_format_rejected() -> None:
    with pytest.raises(ValueError, match="digest"):
        ComponentDescriptor(
            component_key="documentation_rag",
            kind="feature",
            version="1",
            state=ComponentState.ENABLED,
            canonical_digest="not-a-digest",
            capabilities=("retrieval",),
        )


def test_wellformed_but_mismatched_digest_rejected() -> None:
    valid = _descriptor()
    other_hex_128 = ("a" if valid.canonical_digest[0] != "a" else "b") + valid.canonical_digest[1:]
    with pytest.raises(ValueError, match="does not match"):
        ComponentDescriptor(
            component_key=valid.component_key,
            kind=valid.kind,
            version=valid.version,
            state=valid.state,
            canonical_digest=other_hex_128,
            capabilities=valid.capabilities,
        )


def test_invalid_revision_rejected() -> None:
    with pytest.raises(ValueError, match="revision"):
        _descriptor(revision=0)
    with pytest.raises(ValueError, match="revision"):
        _descriptor(revision=True)
