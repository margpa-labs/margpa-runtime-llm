"""Normalized IR / Compiled Plan finite resource limits (P3-PER-001,
P3-CODEX-004 rework) — boundary tests at `limit` and `limit + 1`."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.governance_definitions.domain import (
    CompiledPlan,
    IrIdentity,
    IrSection,
    IrSourceProvenance,
    NormalizedGovernanceDefinition,
    SelectedSectionRef,
)
from margpa_runtime_llm.modules.governance_definitions.domain.limits import (
    MAX_COMPILED_PLAN_ITEM_COUNT,
    MAX_IR_SECTION_CHILD_KEY_COUNT,
    MAX_IR_SECTION_COUNT,
)


def _identity() -> IrIdentity:
    return IrIdentity(definition_id="d", definition_version="1", display_name="D")


def _provenance() -> IrSourceProvenance:
    return IrSourceProvenance(
        source_id="s", source_object_pointer="$.d", content_digest_sha512="0" * 128
    )


def test_ir_sections_at_the_count_limit_is_accepted_one_beyond_is_rejected() -> None:
    at_limit = tuple(
        IrSection(section_key=f"s{i:06d}", value_kind="object") for i in range(MAX_IR_SECTION_COUNT)
    )
    NormalizedGovernanceDefinition(
        ir_id="ir-1",
        identity=_identity(),
        source_provenance=_provenance(),
        domain="d",
        sections=at_limit,
    )

    beyond_limit = tuple(
        IrSection(section_key=f"s{i:06d}", value_kind="object")
        for i in range(MAX_IR_SECTION_COUNT + 1)
    )
    with pytest.raises(ValidationError):
        NormalizedGovernanceDefinition(
            ir_id="ir-1",
            identity=_identity(),
            source_provenance=_provenance(),
            domain="d",
            sections=beyond_limit,
        )


def test_ir_section_child_keys_beyond_the_limit_is_rejected() -> None:
    at_limit = tuple(f"k{i:06d}" for i in range(MAX_IR_SECTION_CHILD_KEY_COUNT))
    IrSection(section_key="s", child_keys=at_limit, value_kind="object")

    beyond_limit = tuple(f"k{i:06d}" for i in range(MAX_IR_SECTION_CHILD_KEY_COUNT + 1))
    with pytest.raises(ValidationError):
        IrSection(section_key="s", child_keys=beyond_limit, value_kind="object")


def test_compiled_plan_selected_rule_refs_at_the_limit_is_accepted_one_beyond_is_rejected() -> None:
    ref = SelectedSectionRef(ir_id="ir-1", section_key="s")
    at_limit = tuple(ref for _ in range(MAX_COMPILED_PLAN_ITEM_COUNT))
    CompiledPlan(
        compiled_plan_id="plan-1",
        compiler_id="c",
        compiler_version="1",
        selected_rule_refs=at_limit,
    )

    beyond_limit = tuple(ref for _ in range(MAX_COMPILED_PLAN_ITEM_COUNT + 1))
    with pytest.raises(ValidationError):
        CompiledPlan(
            compiled_plan_id="plan-1",
            compiler_id="c",
            compiler_version="1",
            selected_rule_refs=beyond_limit,
        )
