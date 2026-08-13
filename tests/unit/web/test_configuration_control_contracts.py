"""Bounded configuration-control HTTP contract tests."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.web.configuration_contracts import (
    ConfigurationApplyRequest,
    ConfigurationPatchRequest,
    ConfigurationPreviewRequest,
)


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"unknown": "value"},
        {"secret": "do-not-project"},
        {"model_root": "/private/model"},
        {"tool_permission": True},
        {"protected_capture": True},
        {"selected_model": "x" * 129},
        {"context_size": 0},
        {"context_size": True},
    ],
)
def test_patch_rejects_unknown_protected_empty_and_invalid_fields(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        ConfigurationPatchRequest.model_validate(payload)


def test_preview_and_apply_reject_extra_or_missing_cas_fields() -> None:
    with pytest.raises(ValidationError):
        ConfigurationPreviewRequest.model_validate(
            {"patch": {"research_developer_mode": "on"}, "extra": True}
        )
    with pytest.raises(ValidationError):
        ConfigurationApplyRequest.model_validate(
            {
                "operation_id": "apply-1",
                "expected_revision": 1,
                "patch": {"research_developer_mode": "on"},
            }
        )
    with pytest.raises(ValidationError):
        ConfigurationApplyRequest.model_validate(
            {
                "operation_id": "bad operation",
                "expected_revision": 1,
                "expected_digest": "a" * 128,
                "patch": {"research_developer_mode": "on"},
            }
        )


def test_apply_accepts_only_safe_typed_cas_contract() -> None:
    request = ConfigurationApplyRequest.model_validate(
        {
            "operation_id": "apply:research-1",
            "expected_revision": 1,
            "expected_digest": "a" * 128,
            "patch": {"research_developer_mode": "on"},
        }
    )

    assert request.operation_id == "apply:research-1"
    mode = request.patch.to_domain().research_developer_mode
    assert mode is not None and mode.value == "on"
