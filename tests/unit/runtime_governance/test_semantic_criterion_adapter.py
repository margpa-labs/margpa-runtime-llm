from __future__ import annotations

import random
from pathlib import Path

from margpa_runtime_llm.adapters.runtime_governance.semantic_criterion_adapter import (
    build_semantic_batch_plan,
    compile_argd_dagd_semantic_criteria,
)
from margpa_runtime_llm.bootstrap.runtime_governance import (
    default_authority,
    load_reference_descriptors,
)
from margpa_runtime_llm.modules.runtime_governance.domain import (
    ExecutionDescriptor,
    RuntimeCapabilitySnapshot,
    SemanticCriterionDisposition,
    SemanticEvaluationStage,
)


def _real_descriptors() -> tuple[ExecutionDescriptor, ...]:
    root = Path(__file__).resolve().parents[3] / "definitions"
    loaded = load_reference_descriptors(
        definitions_root=root,
        capability=RuntimeCapabilitySnapshot(
            model_key="main.qwen3-4b-q4-k-m",
            backend_kind="llama_cpp",
            supports_streaming=True,
            supports_thinking=True,
            max_context_tokens=8192,
        ),
        authority=default_authority(),
    )
    assert loaded.state == "loaded"
    return loaded.descriptors


def test_canonical_corpus_compiles_all_109_descriptors_without_silent_drop() -> None:
    compiled = compile_argd_dagd_semantic_criteria(_real_descriptors())
    assert len(compiled.criteria) == 109
    assert compiled.unsupported == ()
    assert len({item.criterion_id for item in compiled.criteria}) == 109
    assert all(item.source_definition_digest_sha512 for item in compiled.criteria)
    assert all(item.source_text_digest_sha512 for item in compiled.criteria)


def test_compiler_digest_and_order_are_input_order_invariant() -> None:
    descriptors = list(_real_descriptors())
    expected = compile_argd_dagd_semantic_criteria(tuple(descriptors))
    random.Random(6).shuffle(descriptors)
    actual = compile_argd_dagd_semantic_criteria(tuple(descriptors))
    assert actual == expected


def test_batch_budget_defers_each_unselected_criterion_with_reason() -> None:
    compiled = compile_argd_dagd_semantic_criteria(_real_descriptors())
    plan = build_semantic_batch_plan(
        criteria=compiled.criteria,
        stage=SemanticEvaluationStage.POST,
        max_criteria=12,
    )
    assert len(plan.selected) == 12
    assert plan.deferred
    assert all(
        item.disposition is SemanticCriterionDisposition.DEFERRED
        and item.reason_code == "budget_exhausted"
        for item in plan.deferred
    )
    assert len({item.criterion_id for item in (*plan.deferred,)}) == len(plan.deferred)
