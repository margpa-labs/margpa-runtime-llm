"""Trusted ARGD/DAGD descriptor -> normalized semantic criterion compiler."""

from __future__ import annotations

from margpa_runtime_llm.modules.runtime_governance.domain import (
    ExecutionDescriptor,
    SemanticBatchPlan,
    SemanticCompileFinding,
    SemanticCompileResult,
    SemanticCriterion,
    SemanticCriterionDisposition,
    SemanticCriterionResult,
    SemanticDeferredReason,
    SemanticEvaluationMethod,
    SemanticEvaluationStage,
    semantic_contract_digest,
)

_ARGD_MAP: dict[str, tuple[SemanticEvaluationStage, SemanticEvaluationMethod, str]] = {
    "intp_interpretive_premises": (
        SemanticEvaluationStage.BOTH,
        SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        "high",
    ),
    "ctxp_context_priority": (
        SemanticEvaluationStage.BOTH,
        SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        "high",
    ),
    "info_contradiction_information": (
        SemanticEvaluationStage.POST,
        SemanticEvaluationMethod.CLASSIFICATION_WITH_REFERENCE,
        "high",
    ),
    "qual_reasoning_quality": (
        SemanticEvaluationStage.POST,
        SemanticEvaluationMethod.ABSOLUTE_SCORING,
        "moderate",
    ),
    "form_structural_expression": (
        SemanticEvaluationStage.POST,
        SemanticEvaluationMethod.ABSOLUTE_SCORING,
        "moderate",
    ),
    "repr_efficiency_repair": (
        SemanticEvaluationStage.POST,
        SemanticEvaluationMethod.ABSOLUTE_SCORING,
        "moderate",
    ),
}


def compile_argd_dagd_semantic_criteria(
    descriptors: tuple[ExecutionDescriptor, ...],
) -> SemanticCompileResult:
    criteria: list[SemanticCriterion] = []
    unsupported: list[SemanticCompileFinding] = []
    for descriptor in sorted(descriptors, key=lambda item: item.descriptor_id):
        mapping = _mapping_for(descriptor)
        if (
            mapping is None
            or descriptor.source_definition_digest_sha512 is None
            or descriptor.source_text_digest_sha512 is None
        ):
            unsupported.append(
                SemanticCompileFinding(
                    descriptor_id=descriptor.descriptor_id,
                    source_pointer=descriptor.source_pointer,
                    reason=SemanticDeferredReason.UNSUPPORTED_MAPPING,
                )
            )
            continue
        stage, method, severity = mapping
        criteria.append(
            SemanticCriterion(
                criterion_id=f"semantic.{descriptor.descriptor_id}",
                descriptor_id=descriptor.descriptor_id,
                source_definition_id=descriptor.source_definition_id,
                source_definition_digest_sha512=descriptor.source_definition_digest_sha512,
                source_pointer=descriptor.source_pointer,
                source_text_digest_sha512=descriptor.source_text_digest_sha512,
                instruction=descriptor.summary,
                governance_point="main_model.semantic",
                evaluation_stage=stage,
                evaluation_method=method,
                severity_policy=severity,
                recommended_action_policy="repair_or_safe_fallback",
                evidence_requirements=(
                    "request_identity",
                    "candidate_digest",
                    "provider_identity",
                    "criterion_result",
                ),
            )
        )
    digest = semantic_contract_digest(
        {
            "criteria": [item.model_dump(mode="json") for item in criteria],
            "unsupported": [item.model_dump(mode="json") for item in unsupported],
        }
    )
    return SemanticCompileResult(
        criteria=tuple(criteria), unsupported=tuple(unsupported), digest_sha512=digest
    )


def build_semantic_batch_plan(
    *,
    criteria: tuple[SemanticCriterion, ...],
    stage: SemanticEvaluationStage,
    max_criteria: int,
) -> SemanticBatchPlan:
    if stage is SemanticEvaluationStage.BOTH:
        raise ValueError("a runtime batch stage must be pre or post")
    if max_criteria < 0:
        raise ValueError("max_criteria must be non-negative")
    applicable = tuple(
        sorted(
            (
                item
                for item in criteria
                if item.evaluation_stage in (stage, SemanticEvaluationStage.BOTH)
            ),
            key=lambda item: item.criterion_id,
        )
    )
    selected = applicable[:max_criteria]
    deferred = tuple(
        SemanticCriterionResult(
            criterion_id=item.criterion_id,
            descriptor_id=item.descriptor_id,
            disposition=SemanticCriterionDisposition.DEFERRED,
            reason_code=SemanticDeferredReason.BUDGET_EXHAUSTED.value,
        )
        for item in applicable[max_criteria:]
    )
    digest = semantic_contract_digest(
        {
            "stage": stage.value,
            "selected": [item.criterion_id for item in selected],
            "deferred": [item.criterion_id for item in deferred],
        }
    )
    return SemanticBatchPlan(
        stage=stage, selected=selected, deferred=deferred, digest_sha512=digest
    )


def _mapping_for(
    descriptor: ExecutionDescriptor,
) -> tuple[SemanticEvaluationStage, SemanticEvaluationMethod, str] | None:
    parts = descriptor.descriptor_id.split(".")
    if descriptor.source_definition_id == "argd" and len(parts) >= 3:
        return _ARGD_MAP.get(parts[1])
    if (
        descriptor.source_definition_id == "dagd"
        and len(parts) >= 4
        and parts[1] == "prohibited_behaviors"
    ):
        return (
            SemanticEvaluationStage.POST,
            SemanticEvaluationMethod.CLASSIFICATION,
            "high",
        )
    return None
