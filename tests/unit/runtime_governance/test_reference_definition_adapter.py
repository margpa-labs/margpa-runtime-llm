"""ARGD/DAGD Trusted Adapter Extension: descriptors trace to real Source
content, never fabricated (P4-C-WU-002, P4-GD-001..004)."""

from __future__ import annotations

from margpa_runtime_llm.adapters.runtime_governance.reference_definition_adapter import (
    build_argd_dagd_descriptors,
)
from margpa_runtime_llm.modules.runtime_governance.domain import EvaluationMethod


def _real_argd_dagd_content() -> dict[str, object]:
    return {
        "argd": {
            "axiomatic_reasoning_governance_definition": {
                "response_generation_priorities": {
                    "intp_interpretive_premises": [
                        {"tag": "KEEP", "content": "Do not compress input without authorization"},
                        {"content": "Define technical terms first"},
                    ],
                    "qual_reasoning_quality": [
                        {"tag": "ANTI", "content": "Do not fabricate unsupported claims"},
                    ],
                },
                "meta_data": {"version": "0.3.1"},
            }
        },
        "dagd": {
            "declarative_ai_governance_definition": {
                "constraints": {
                    "prohibited_behaviors": {
                        "epistemic_errors": ["hallucination", "unsupported_assertion"],
                        "alignment_bias": ["sycophancy"],
                    }
                },
                "meta_data": {"version": "0.4.4"},
            }
        },
    }


def test_descriptors_trace_to_real_argd_rule_content() -> None:
    descriptors = build_argd_dagd_descriptors(_real_argd_dagd_content())
    argd_descriptors = [d for d in descriptors if d.source_definition_id == "argd"]
    assert len(argd_descriptors) == 3
    first = next(
        d for d in argd_descriptors if d.descriptor_id == "argd.intp_interpretive_premises.0"
    )
    assert first.summary == "Do not compress input without authorization"
    assert first.domain_tag == "KEEP"
    assert first.evaluation_method is EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR
    assert first.source_pointer.startswith("$.argd.axiomatic_reasoning_governance_definition")

    untagged = next(
        d for d in argd_descriptors if d.descriptor_id == "argd.intp_interpretive_premises.1"
    )
    assert untagged.domain_tag is None


def test_descriptors_trace_to_real_dagd_prohibited_behaviors() -> None:
    descriptors = build_argd_dagd_descriptors(_real_argd_dagd_content())
    dagd_descriptors = [d for d in descriptors if d.source_definition_id == "dagd"]
    assert len(dagd_descriptors) == 3
    hallucination = next(
        d
        for d in dagd_descriptors
        if d.descriptor_id == "dagd.prohibited_behaviors.epistemic_errors.0"
    )
    assert "hallucination" in hallucination.summary
    assert hallucination.domain_tag == "epistemic_errors"


def test_missing_sections_are_skipped_not_guessed() -> None:
    descriptors = build_argd_dagd_descriptors({"argd": {}, "dagd": {}})
    assert descriptors == ()


def test_empty_content_produces_no_descriptors() -> None:
    assert build_argd_dagd_descriptors({}) == ()


def test_descriptor_ids_are_unique_across_real_bundle() -> None:
    import hashlib
    import json
    from pathlib import Path

    real_path = (
        Path(__file__).resolve().parents[3]
        / "definitions"
        / "core_governance"
        / "argd_v0.3.1_en_dagd_v0.4.4_en.json"
    )
    raw = real_path.read_bytes()
    content = json.loads(raw)
    descriptors = build_argd_dagd_descriptors(content)

    # This mirrors the real Manifest's own recorded digest for this
    # Source (definitions/manifest.json) — a change here would mean the
    # fixture content and the Manifest have drifted apart.
    assert hashlib.sha512(raw).hexdigest() == (
        "e32c6dc0289743794de7943cd9ebab252fbe4b0209522858a4f2c560d905fe6"
        "f4ac8fcc32c91bc89d56b9fd6fb079e8e29b110203905e33d6114b6b65cc22e16"
    )
    assert len(descriptors) > 0
    descriptor_ids = [d.descriptor_id for d in descriptors]
    assert len(descriptor_ids) == len(set(descriptor_ids))
    assert all(
        d.evaluation_method is EvaluationMethod.REQUIRES_SEMANTIC_EVALUATOR for d in descriptors
    )
