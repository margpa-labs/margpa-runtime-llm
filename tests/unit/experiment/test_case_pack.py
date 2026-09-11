"""Phase 9-2 WU-D: Semantic Research Case Pack neutrality and integration
with Experiment Core's own Plan/Case Manifest machinery."""

from __future__ import annotations

from margpa_runtime_llm.modules.experiment.domain.case_pack import (
    CASE_PACK_REVISION,
    FALSE_IMPROVEMENT_CASE,
    build_case_pack,
)
from margpa_runtime_llm.modules.experiment.domain.dataset import compute_case_digest_sha512
from margpa_runtime_llm.modules.experiment.domain.identity import (
    ComponentKey,
    ComponentSelection,
    VariantDescriptor,
    build_experiment_plan,
)

_NAMES_NOT_ALLOWED_IN_A_NEUTRAL_FIXTURE_DATASET = ("田中", "佐藤", "Tanaka", "Sato", "山田")


def test_build_case_pack_returns_a_non_empty_pack_pinned_to_one_revision() -> None:
    pack = build_case_pack()
    assert len(pack) > 0
    assert {case.revision for case in pack} == {CASE_PACK_REVISION}


def test_every_required_semantic_scenario_is_a_routed_revisioned_manifest() -> None:
    routes = {case.case_id: case.evaluator_route.value for case in build_case_pack()}
    assert routes == {
        "case-freshness-alpha-15": "freshness",
        "case-freshness-alpha-15-updated": "freshness",
        "case-freshness-alpha-15-deleted": "freshness",
        "case-retrieval-rag-off": "retrieval",
        "case-retrieval-relevant-hit": "retrieval",
        "case-retrieval-irrelevant-hit": "retrieval",
        "case-retrieval-no-hit-model-call": "retrieval",
        "case-retrieval-strict-no-hit": "retrieval",
        "case-belief-revision-alpha-15": "belief_revision",
        "case-false-improvement-beta-01": "false_improvement",
        "case-composition-matrix-alpha-01": "composition_matrix",
    }


def test_case_pack_case_ids_use_neutral_placeholder_names_only() -> None:
    pack = build_case_pack()
    for case in pack:
        for forbidden in _NAMES_NOT_ALLOWED_IN_A_NEUTRAL_FIXTURE_DATASET:
            assert forbidden not in case.case_id
            assert forbidden not in case.input


def test_false_improvement_case_requires_human_review() -> None:
    assert FALSE_IMPROVEMENT_CASE.requires_human_review is True


def test_case_pack_revision_can_back_a_real_experiment_plan() -> None:
    """The Pack's own fixed `case_revision` slots directly into
    `ExperimentPlan.case_revision` (WU-A A1) -- no separate ad hoc
    revision string invented for Plan-building."""
    variant = VariantDescriptor(
        variant_id="variant-a",
        components=(ComponentSelection(component_key=ComponentKey.MAIN, selector_id="main-a"),),
    )
    plan = build_experiment_plan(
        experiment_id="exp-case-pack-1",
        case_id=FALSE_IMPROVEMENT_CASE.case_id,
        case_revision=CASE_PACK_REVISION,
        case_digest_sha512=compute_case_digest_sha512(FALSE_IMPROVEMENT_CASE),
        variants=(variant,),
        execution_order=("variant-a",),
    )
    assert plan.case_revision == CASE_PACK_REVISION
    assert plan.case_id == FALSE_IMPROVEMENT_CASE.case_id
