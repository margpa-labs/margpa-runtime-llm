"""ARGD/DAGD Trusted Adapter Extension (P4-C-WU-002, ADR-4-006, P4-GD-001..004).

Reads the *actual* verified Source content Phase 3 already captured
(`PackageSourceResult.verified_source_json`, P3-CODEX-007's single-read
guarantee) — never a re-derived disk read, and not Phase 3's own
Normalized IR (which is deliberately structural-only and discards rule
text; see `governance_definitions/domain/normalized_ir.py`'s module
docstring). Every emitted `ExecutionDescriptor` traces back to one real
`content` string (ARGD) or one real behavior name (DAGD) — nothing is
invented, reordered, or summarized beyond truncation for `summary`'s
length cap. Missing or unexpected structure is skipped, never guessed
(P4-GD-003) — this Adapter is specific to the `argd_dagd_combined_v1`
schema; other Reference Bundle members stay traceable-only via Phase 3's
existing structural IR until their own Typed Adapter exists.
"""

from __future__ import annotations

from margpa_runtime_llm.modules.runtime_governance.domain import (
    EvaluationMethod,
    ExecutionDescriptor,
)

_MAX_SUMMARY_CHARS = 500


def build_argd_dagd_descriptors(content: dict[str, object]) -> tuple[ExecutionDescriptor, ...]:
    return (*_argd_descriptors(content), *_dagd_descriptors(content))


def _argd_descriptors(content: dict[str, object]) -> tuple[ExecutionDescriptor, ...]:
    argd = content.get("argd")
    if not isinstance(argd, dict):
        return ()
    body = argd.get("axiomatic_reasoning_governance_definition")
    if not isinstance(body, dict):
        return ()
    priorities = body.get("response_generation_priorities")
    if not isinstance(priorities, dict):
        return ()
    descriptors: list[ExecutionDescriptor] = []
    for section_key, entries in priorities.items():
        if not isinstance(section_key, str) or not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            rule_content = entry.get("content")
            if not isinstance(rule_content, str) or not rule_content:
                continue
            tag = entry.get("tag")
            descriptors.append(
                ExecutionDescriptor(
                    descriptor_id=f"argd.{section_key}.{index}",
                    source_definition_id="argd",
                    source_pointer=(
                        "$.argd.axiomatic_reasoning_governance_definition."
                        f"response_generation_priorities.{section_key}[{index}]"
                    ),
                    domain_tag=tag if isinstance(tag, str) and tag else None,
                    summary=rule_content[:_MAX_SUMMARY_CHARS],
                    evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
                )
            )
    return tuple(descriptors)


def _dagd_descriptors(content: dict[str, object]) -> tuple[ExecutionDescriptor, ...]:
    dagd = content.get("dagd")
    if not isinstance(dagd, dict):
        return ()
    body = dagd.get("declarative_ai_governance_definition")
    if not isinstance(body, dict):
        return ()
    constraints = body.get("constraints")
    if not isinstance(constraints, dict):
        return ()
    prohibited = constraints.get("prohibited_behaviors")
    if not isinstance(prohibited, dict):
        return ()
    descriptors: list[ExecutionDescriptor] = []
    for group_key, behaviors in prohibited.items():
        if not isinstance(group_key, str) or not isinstance(behaviors, list):
            continue
        for index, behavior in enumerate(behaviors):
            if not isinstance(behavior, str) or not behavior:
                continue
            descriptors.append(
                ExecutionDescriptor(
                    descriptor_id=f"dagd.prohibited_behaviors.{group_key}.{index}",
                    source_definition_id="dagd",
                    source_pointer=(
                        "$.dagd.declarative_ai_governance_definition."
                        f"constraints.prohibited_behaviors.{group_key}[{index}]"
                    ),
                    domain_tag=group_key,
                    summary=f"prohibited behavior: {behavior}"[:_MAX_SUMMARY_CHARS],
                    evaluation_method=EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR,
                )
            )
    return tuple(descriptors)
