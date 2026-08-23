"""Deterministic Phase 3 Compiler (architecture §7, P3-E-WU-001/002).

Every `CompiledPlan` this Compiler produces is `binding_state="unbound"`,
`executable=False` — Phase 3 never binds a Plan to a Governance Point or
Action Adapter (ADR-3-001). Because the underlying IR is a structural
passthrough (Phase 3-D), "selecting a rule" here means selecting an IR
*section* by reference, not evaluating rule logic — there is nothing to
execute even in principle yet.
"""

from __future__ import annotations

import hashlib
import json
from typing import Annotated, Literal

from pydantic import Field, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .limits import MAX_COMPILED_PLAN_ITEM_COUNT, MAX_STRING_LENGTH
from .normalized_ir import DigestedNormalizedGovernanceDefinition

_IDENTIFIER_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
_SHA512_HEX_PATTERN = r"^[0-9a-f]{128}$"
_Sha512Hex = Annotated[str, Field(pattern=_SHA512_HEX_PATTERN)]

GovernanceProfile = Literal["core", "standard", "full"]

_BoundedString = Annotated[str, Field(max_length=MAX_STRING_LENGTH)]


class SelectedSectionRef(ImmutableContract):
    ir_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    section_key: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)


class CompilerInput(ImmutableContract):
    normalized_ir_refs: tuple[str, ...] = Field(max_length=MAX_COMPILED_PLAN_ITEM_COUNT)
    # Content Integrity Identity for each `normalized_ir_refs` entry, same
    # order, same length (P3-CODEX-006): the IR ID alone is a stable
    # *name*, not an Integrity Identity — two Compiles of the same ir_id
    # with different Source/Section content must never share a Cache Key
    # or a Plan ID. Required (no default) so no call site can silently
    # omit it and fall back to name-only identity.
    normalized_ir_digests: tuple[_Sha512Hex, ...] = Field(max_length=MAX_COMPILED_PLAN_ITEM_COUNT)
    profile: GovernanceProfile = "core"
    binding_candidate: str | None = None
    runtime_capability_snapshot_digest: str = Field(pattern=_SHA512_HEX_PATTERN)
    authority_snapshot_digest: str = Field(pattern=_SHA512_HEX_PATTERN)

    @model_validator(mode="after")
    def _digests_match_refs_one_to_one(self) -> CompilerInput:
        if len(self.normalized_ir_digests) != len(self.normalized_ir_refs):
            raise ValueError(
                "normalized_ir_digests must have exactly one entry per normalized_ir_refs entry"
            )
        return self


class CompiledPlan(ImmutableContract):
    compiled_plan_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    compiler_id: str = Field(min_length=1, max_length=128, pattern=_IDENTIFIER_PATTERN)
    compiler_version: str = Field(min_length=1, max_length=32, pattern=_IDENTIFIER_PATTERN)
    source_definition_digests: tuple[_BoundedString, ...] = Field(
        default=(), max_length=MAX_COMPILED_PLAN_ITEM_COUNT
    )
    ir_digests: tuple[_BoundedString, ...] = Field(
        default=(), max_length=MAX_COMPILED_PLAN_ITEM_COUNT
    )
    selected_rule_refs: tuple[SelectedSectionRef, ...] = Field(
        default=(), max_length=MAX_COMPILED_PLAN_ITEM_COUNT
    )
    selected_evaluator_refs: tuple[SelectedSectionRef, ...] = Field(
        default=(), max_length=MAX_COMPILED_PLAN_ITEM_COUNT
    )
    selected_action_refs: tuple[SelectedSectionRef, ...] = Field(
        default=(), max_length=MAX_COMPILED_PLAN_ITEM_COUNT
    )
    unresolved_dependencies: tuple[_BoundedString, ...] = Field(
        default=(), max_length=MAX_COMPILED_PLAN_ITEM_COUNT
    )
    conflicts: tuple[_BoundedString, ...] = Field(
        default=(), max_length=MAX_COMPILED_PLAN_ITEM_COUNT
    )
    warnings: tuple[_BoundedString, ...] = Field(
        default=(), max_length=MAX_COMPILED_PLAN_ITEM_COUNT
    )
    binding_state: Literal["unbound"] = "unbound"
    executable: Literal[False] = False


_COMPILER_ID = "phase3-deterministic-compiler"
_COMPILER_VERSION = "1"


def compile_plan(
    *,
    compiler_input: CompilerInput,
    definitions: tuple[DigestedNormalizedGovernanceDefinition, ...],
) -> CompiledPlan:
    """Purely deterministic: no Model Call, no I/O, no Action execution
    (P3-CMP-007). Every IR section becomes a `selected_rule_ref` — Phase
    3's structural IR has no finer Evaluator/Action distinction yet
    (Phase 3-D scope decision), so those two lists stay empty rather than
    being populated with a guess."""

    warnings: list[str] = list(
        {
            "structural IR: selected_rule_refs enumerate IR sections, not "
            "individually evaluated rules — see Phase 3-D scope decision"
        }
    )
    rule_refs: list[SelectedSectionRef] = []
    source_digests: list[str] = []
    ir_digests: list[str] = []
    unresolved: list[str] = []

    by_ir_id = {d.ir.ir_id: d for d in definitions}
    for ir_ref in compiler_input.normalized_ir_refs:
        digested = by_ir_id.get(ir_ref)
        if digested is None:
            unresolved.append(ir_ref)
            continue
        ir = digested.ir
        source_digests.append(ir.source_provenance.content_digest_sha512)
        ir_digests.append(digested.ir_digest_sha512)
        for section in ir.sections:
            rule_refs.append(SelectedSectionRef(ir_id=ir.ir_id, section_key=section.section_key))

    plan_without_digest = CompiledPlan(
        compiled_plan_id=_plan_id(compiler_input),
        compiler_id=_COMPILER_ID,
        compiler_version=_COMPILER_VERSION,
        source_definition_digests=tuple(source_digests),
        ir_digests=tuple(ir_digests),
        selected_rule_refs=tuple(rule_refs),
        unresolved_dependencies=tuple(unresolved),
        warnings=tuple(warnings),
    )
    return plan_without_digest


def _plan_id(compiler_input: CompilerInput) -> str:
    payload = json.dumps(
        compiler_input.model_dump(mode="json"),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return "plan-" + hashlib.sha512(payload).hexdigest()[:32]


def plan_matches_requested_digests(plan: CompiledPlan, compiler_input: CompilerInput) -> bool:
    """Defense-in-depth Cache Hit revalidation (P3-CODEX-006): even though
    `plan_cache_key()` already folds `normalized_ir_digests` into the
    lookup key — so a digest change should already be a Cache Miss by
    construction — this independently re-checks the *returned* Plan's own
    embedded `ir_digests` against what the caller just asked for, rather
    than trusting key equality alone."""

    return plan.ir_digests == compiler_input.normalized_ir_digests


def plan_cache_key(compiler_input: CompilerInput) -> str:
    """Digest over exactly the inputs P3-CMP-004 requires the Cache Key to
    include: Definition set (via normalized_ir_refs, which pin specific
    IRs), Compiler identity, Profile, Binding Candidate, Capability and
    Policy/Authority snapshots. Any change to any of these must miss
    cache (P3-CMP-005)."""

    payload = json.dumps(
        {
            "compiler_id": _COMPILER_ID,
            "compiler_version": _COMPILER_VERSION,
            **compiler_input.model_dump(mode="json"),
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha512(payload).hexdigest()


def plan_payload_for_digest(plan: CompiledPlan) -> dict[str, object]:
    return plan.model_dump(mode="json")


def plan_digest_sha512(plan: CompiledPlan) -> str:
    canonical = json.dumps(
        plan_payload_for_digest(plan),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha512(canonical).hexdigest()


class DigestedCompiledPlan(ImmutableContract):
    plan: CompiledPlan
    plan_digest_sha512: str = Field(pattern=_SHA512_HEX_PATTERN)


def digest_plan(plan: CompiledPlan) -> DigestedCompiledPlan:
    return DigestedCompiledPlan(plan=plan, plan_digest_sha512=plan_digest_sha512(plan))


def verify_digested_plan(digested: DigestedCompiledPlan) -> bool:
    return plan_digest_sha512(digested.plan) == digested.plan_digest_sha512
