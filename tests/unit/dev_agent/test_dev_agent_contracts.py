"""Unit tests for Phase 8 (P8-D) Dev Agent contracts."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.dev_agent import (
    AuthorizationEnvelope,
    Plan,
    PlanStep,
    RunSnapshot,
)


def _plan_step(step_id: str = "step-one", tool_id: str = "list_files") -> PlanStep:
    return PlanStep(step_id=step_id, tool_id=tool_id, input={})


def test_plan_rejects_duplicate_step_ids() -> None:
    with pytest.raises(ValidationError):
        Plan(steps=(_plan_step("step-a"), _plan_step("step-a")))


def test_plan_accepts_unique_step_ids() -> None:
    plan = Plan(steps=(_plan_step("step-a"), _plan_step("step-b")))
    assert len(plan.steps) == 2


def _envelope(**overrides: object) -> AuthorizationEnvelope:
    defaults: dict[str, object] = {
        "run_id": "run-1",
        "allowed_step_ids": ("step-one",),
        "allowed_tool_ids": ("write_note",),
        "resource_scope": "fixture_only",
        "max_steps": 10,
        "max_attempts": 1,
        "expires_at": None,
        "issued_at": "2026-08-30T00:00:00+00:00",
    }
    defaults.update(overrides)
    return AuthorizationEnvelope(**defaults)  # type: ignore[arg-type]


def test_authorization_envelope_is_frozen() -> None:
    envelope = _envelope()
    with pytest.raises(ValidationError):
        envelope.run_id = "run-2"


def test_authorization_envelope_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        _envelope(authority="everything")


def test_run_snapshot_authority_is_only_via_the_frozen_envelope_field() -> None:
    """P8-CR2: `RunSnapshot` may carry Authority *only* through its one
    typed, server-issued `envelope` field — never a second, looser
    Authority-shaped field a caller or a future change could widen."""

    forbidden_substrings = ("permission", "grant_all")
    for field_name, info in RunSnapshot.model_fields.items():
        if field_name == "envelope":
            assert info.annotation == AuthorizationEnvelope | None
            continue
        for forbidden in forbidden_substrings:
            assert forbidden not in field_name.lower(), (
                f"RunSnapshot must never carry a loose Authority-shaped field, found: {field_name}"
            )
        assert "authority" not in field_name.lower(), (
            f"RunSnapshot must never carry an ad-hoc 'authority' field outside "
            f"the typed `envelope`, found: {field_name}"
        )
