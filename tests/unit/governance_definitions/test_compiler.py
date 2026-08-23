"""Deterministic Compiler: Unbound Plan, no Model/Action Call, Plan Digest
determinism, stale-cache rejection, IR Content Integrity Identity
(P3-E-WU-001/002, P3-CODEX-006 rework)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.governance_definitions.compiler_cache import CompiledPlanCache
from margpa_runtime_llm.modules.governance_definitions.domain import (
    CompilerInput,
    DigestedNormalizedGovernanceDefinition,
    IrIdentity,
    IrSection,
    IrSourceProvenance,
    NormalizedGovernanceDefinition,
    compile_plan,
    digest_ir,
    digest_plan,
    plan_matches_requested_digests,
    verify_digested_plan,
)

_CAP_DIGEST = "a" * 128
_AUTH_DIGEST = "b" * 128


def _digested_ir(
    ir_id: str, definition_id: str, *, section_key: str = "description"
) -> DigestedNormalizedGovernanceDefinition:
    ir = NormalizedGovernanceDefinition(
        ir_id=ir_id,
        identity=IrIdentity(
            definition_id=definition_id, definition_version="1", display_name=definition_id.upper()
        ),
        source_provenance=IrSourceProvenance(
            source_id=definition_id,
            source_object_pointer=f"$.{definition_id}",
            content_digest_sha512="0" * 128,
        ),
        domain=f"{definition_id}_domain",
        sections=(
            IrSection(section_key=section_key, child_keys=("purpose",), value_kind="object"),
        ),
    )
    return digest_ir(ir)


def _compiler_input(
    *digested: DigestedNormalizedGovernanceDefinition,
    profile: str = "core",
    capability_digest: str = _CAP_DIGEST,
    authority_digest: str = _AUTH_DIGEST,
) -> CompilerInput:
    return CompilerInput(
        normalized_ir_refs=tuple(d.ir.ir_id for d in digested),
        normalized_ir_digests=tuple(d.ir_digest_sha512 for d in digested),
        profile=profile,  # type: ignore[arg-type]
        runtime_capability_snapshot_digest=capability_digest,
        authority_snapshot_digest=authority_digest,
    )


def test_compiled_plan_is_always_unbound_and_non_executable() -> None:
    digested = _digested_ir("a-ir", "a")
    plan = compile_plan(compiler_input=_compiler_input(digested), definitions=(digested,))

    assert plan.binding_state == "unbound"
    assert plan.executable is False


def test_compiled_plan_selects_a_rule_ref_per_ir_section() -> None:
    digested = _digested_ir("a-ir", "a")
    plan = compile_plan(compiler_input=_compiler_input(digested), definitions=(digested,))

    assert len(plan.selected_rule_refs) == 1
    assert plan.selected_rule_refs[0].ir_id == "a-ir"
    assert plan.selected_rule_refs[0].section_key == "description"
    assert plan.source_definition_digests == ("0" * 128,)


def test_unresolvable_ir_ref_is_reported_not_silently_dropped() -> None:
    compiler_input = CompilerInput(
        normalized_ir_refs=("missing-ir",),
        normalized_ir_digests=("f" * 128,),
        runtime_capability_snapshot_digest=_CAP_DIGEST,
        authority_snapshot_digest=_AUTH_DIGEST,
    )
    plan = compile_plan(compiler_input=compiler_input, definitions=())
    assert plan.unresolved_dependencies == ("missing-ir",)
    assert plan.selected_rule_refs == ()


def test_empty_ir_refs_produces_a_valid_empty_unbound_plan() -> None:
    compiler_input = CompilerInput(
        normalized_ir_refs=(),
        normalized_ir_digests=(),
        runtime_capability_snapshot_digest=_CAP_DIGEST,
        authority_snapshot_digest=_AUTH_DIGEST,
    )
    plan = compile_plan(compiler_input=compiler_input, definitions=())
    assert plan.binding_state == "unbound"
    assert plan.selected_rule_refs == ()
    assert plan.unresolved_dependencies == ()


def test_plan_digest_is_deterministic_and_self_consistent() -> None:
    digested = _digested_ir("a-ir", "a")
    compiler_input = _compiler_input(digested)
    plan_first = compile_plan(compiler_input=compiler_input, definitions=(digested,))
    plan_second = compile_plan(compiler_input=compiler_input, definitions=(digested,))

    digested_plan = digest_plan(plan_first)
    assert digest_plan(plan_second).plan_digest_sha512 == digested_plan.plan_digest_sha512
    assert verify_digested_plan(digested_plan) is True


def test_cache_hit_only_on_exact_key_match() -> None:
    cache = CompiledPlanCache()
    digested = _digested_ir("a-ir", "a")
    compiler_input = _compiler_input(digested)
    plan = compile_plan(compiler_input=compiler_input, definitions=(digested,))

    assert cache.get(compiler_input) is None
    cache.put(compiler_input, plan)
    assert cache.get(compiler_input) is plan
    assert cache.size() == 1


def test_cache_misses_when_authority_snapshot_digest_changes() -> None:
    cache = CompiledPlanCache()
    digested = _digested_ir("a-ir", "a")
    compiler_input = _compiler_input(digested)
    plan = compile_plan(compiler_input=compiler_input, definitions=(digested,))
    cache.put(compiler_input, plan)

    changed_input = compiler_input.model_copy(update={"authority_snapshot_digest": "c" * 128})
    assert cache.get(changed_input) is None  # a stale entry is never reused


def test_cache_misses_when_profile_changes() -> None:
    cache = CompiledPlanCache()
    digested = _digested_ir("a-ir", "a")
    compiler_input = _compiler_input(digested, profile="core")
    plan = compile_plan(compiler_input=compiler_input, definitions=(digested,))
    cache.put(compiler_input, plan)

    changed_input = compiler_input.model_copy(update={"profile": "full"})
    assert cache.get(changed_input) is None


# -- P3-CODEX-006: IR ID alone is a Name, not a Content Integrity
# Identity — the same ir_id with different Section/Digest content must
# never Cache Hit. -------------------------------------------------------


def test_normalized_ir_digests_must_have_one_entry_per_ref() -> None:
    with pytest.raises(ValidationError):
        CompilerInput(
            normalized_ir_refs=("a-ir",),
            normalized_ir_digests=(),  # length mismatch
            runtime_capability_snapshot_digest=_CAP_DIGEST,
            authority_snapshot_digest=_AUTH_DIGEST,
        )


def test_same_ir_id_different_content_digest_is_a_cache_miss() -> None:
    cache = CompiledPlanCache()
    old_version = _digested_ir("a-ir", "a", section_key="old_section")
    new_version = _digested_ir("a-ir", "a", section_key="new_section")
    assert old_version.ir.ir_id == new_version.ir.ir_id  # same Name...
    assert old_version.ir_digest_sha512 != new_version.ir_digest_sha512  # ...different content

    old_input = _compiler_input(old_version)
    old_plan = compile_plan(compiler_input=old_input, definitions=(old_version,))
    cache.put(old_input, old_plan)

    new_input = _compiler_input(new_version)
    assert cache.get(new_input) is None  # the changed content must miss, not reuse old_plan


def test_plan_matches_requested_digests_detects_a_mismatched_cache_entry() -> None:
    digested = _digested_ir("a-ir", "a")
    compiler_input = _compiler_input(digested)
    plan = compile_plan(compiler_input=compiler_input, definitions=(digested,))
    assert plan_matches_requested_digests(plan, compiler_input) is True

    other_version = _digested_ir("a-ir", "a", section_key="different")
    other_input = _compiler_input(other_version)
    assert plan_matches_requested_digests(plan, other_input) is False
