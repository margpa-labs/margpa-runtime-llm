"""Contract tests for persistable citation evidence (Phase 2-E)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CITATION_EVIDENCE_SCHEMA_VERSION,
    CitationUnavailable,
    DocumentationAugmentation,
    DocumentationCitation,
    DocumentationEvidence,
    DocumentationGroundingState,
    DocumentationMeasurementUnit,
    DocumentationRetrievalState,
    DocumentationWarning,
    PersistedTurnCitationEvidence,
    build_turn_citation_evidence,
)

_SHA = "a" * 128


def _citation(order: int = 1) -> DocumentationCitation:
    return DocumentationCitation(
        citation_id=f"citation-{order}",
        project_relative_path="docs/public/overview_ja.md",
        heading_breadcrumb="Overview",
        chunk_id=_SHA,
        document_sha512=_SHA,
        retrieval_score=1.0,
        selected_order=order,
    )


def _grounded_evidence() -> DocumentationEvidence:
    return DocumentationEvidence(
        query_digest=_SHA,
        corpus_manifest_digest=_SHA,
        retriever_key="bm25",
        retriever_version="1",
        selected_chunk_ids=(_SHA,),
        selected_document_digests=(_SHA,),
        selected_scores=(1.0,),
        base_prompt_unit=DocumentationMeasurementUnit.TOKENS,
        context_budget=100,
        context_budget_unit=DocumentationMeasurementUnit.TOKENS,
        context_used=10,
        context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
        context_measurement_limit=100,
        context_token_budget_used=True,
        retrieved_chunk_count=1,
        assembled_block_count=1,
        identifier_subject_count=0,
        retrieval_covered_subject_count=0,
        retrieval_uncovered_subject_count=0,
        covered_subject_count=0,
        uncovered_subject_count=0,
        grounding_state=DocumentationGroundingState.GROUNDED_READY,
        generation_allowed=True,
        retrieval_duration_ms=1.0,
    )


def _augmentation(*, enabled: bool) -> DocumentationAugmentation:
    if not enabled:
        evidence = _grounded_evidence().model_copy(
            update={
                "grounding_state": DocumentationGroundingState.UNAVAILABLE,
                "generation_allowed": False,
                "selected_chunk_ids": (),
                "selected_document_digests": (),
                "selected_scores": (),
                "retrieved_chunk_count": 0,
                "assembled_block_count": 0,
            }
        )
        return DocumentationAugmentation(
            state=DocumentationRetrievalState.DISABLED,
            should_generate=False,
            evidence=evidence,
            document_count=0,
            selected_chunk_count=0,
            duration_ms=0.0,
        )
    return DocumentationAugmentation(
        state=DocumentationRetrievalState.ENABLED,
        should_generate=True,
        reference_message="see references",
        citations=(_citation(),),
        evidence=_grounded_evidence(),
        document_count=1,
        selected_chunk_count=1,
        duration_ms=1.0,
    )


def test_no_free_text_content_field() -> None:
    forbidden = {
        "absolute_path",
        "secret",
        "credential",
        "raw_thinking",
        "system_prompt",
        "tool_internal",
        "hidden_original",
        "partial_output",
        "raw_exception",
        "content",
        "chunk_text",
    }
    assert forbidden.isdisjoint(PersistedTurnCitationEvidence.model_fields)
    assert forbidden.isdisjoint(DocumentationCitation.model_fields)


def test_model_has_no_forbidden_fields() -> None:
    allowed = {
        "schema_version",
        "conversation_id",
        "turn_id",
        "citation_schema_version",
        "corpus_revision",
        "retrieval_state",
        "grounding_state",
        "warning_codes",
        "citations",
    }
    assert set(PersistedTurnCitationEvidence.model_fields) == allowed


def test_extra_fields_rejected() -> None:
    with pytest.raises(ValidationError):
        PersistedTurnCitationEvidence.model_validate(
            {
                "conversation_id": "c1",
                "turn_id": "t1",
                "citation_schema_version": 1,
                "corpus_revision": _SHA,
                "retrieval_state": "enabled",
                "grounding_state": "grounded_ready",
                "citations": (),
                "raw_thinking": "should not be accepted",
            }
        )


def test_only_enabled_state_may_carry_citations() -> None:
    with pytest.raises(ValidationError, match="enabled retrieval state"):
        PersistedTurnCitationEvidence(
            conversation_id="c1",
            turn_id="t1",
            citation_schema_version=1,
            corpus_revision=_SHA,
            retrieval_state=DocumentationRetrievalState.DISABLED,
            grounding_state=DocumentationGroundingState.NO_HIT,
            citations=(_citation(),),
        )


def _no_hit_augmentation() -> DocumentationAugmentation:
    evidence = _grounded_evidence().model_copy(
        update={
            "grounding_state": DocumentationGroundingState.NO_HIT,
            "generation_allowed": True,
            "selected_chunk_ids": (),
            "selected_document_digests": (),
            "selected_scores": (),
            "retrieved_chunk_count": 0,
            "assembled_block_count": 0,
        }
    )
    return DocumentationAugmentation(
        state=DocumentationRetrievalState.ENABLED,
        should_generate=True,
        evidence=evidence,
        warnings=(DocumentationWarning(code="documentation_no_hit", message="no evidence"),),
        document_count=0,
        selected_chunk_count=0,
        duration_ms=1.0,
    )


def _context_insufficient_augmentation() -> DocumentationAugmentation:
    evidence = _grounded_evidence().model_copy(
        update={
            "grounding_state": DocumentationGroundingState.CONTEXT_INSUFFICIENT,
            "generation_allowed": False,
            "assembled_block_count": 0,
        }
    )
    return DocumentationAugmentation(
        state=DocumentationRetrievalState.ENABLED,
        should_generate=False,
        evidence=evidence,
        document_count=1,
        selected_chunk_count=0,
        duration_ms=1.0,
    )


def test_build_turn_citation_evidence_persists_no_hit_with_zero_citations() -> None:
    """P7-RW5-A (P7-CODEX-014): unlike RAG OFF/disabled, a `NO_HIT` Turn's
    Grounding State/Warning Codes are real Evidence a Persistent Detail
    reload needs to reconstruct the same "no current grounds" display the
    Live SSE `retrieval` event already showed - previously this returned
    `None` exactly like RAG OFF, silently dropping it."""
    evidence = build_turn_citation_evidence(
        _no_hit_augmentation(), conversation_id="c1", turn_id="t1"
    )
    assert evidence is not None
    assert evidence.grounding_state is DocumentationGroundingState.NO_HIT
    assert evidence.citations == ()
    assert evidence.warning_codes == ("documentation_no_hit",)


def test_build_turn_citation_evidence_still_returns_none_for_other_zero_citation_states() -> None:
    """Only `NO_HIT` is in this Bounded Rework's scope - `CONTEXT_
    INSUFFICIENT` (and `UNAVAILABLE`, not separately re-tested here since
    it shares the same zero-citation shape) keep the pre-existing
    behavior unchanged."""
    assert (
        build_turn_citation_evidence(
            _context_insufficient_augmentation(), conversation_id="c1", turn_id="t1"
        )
        is None
    )


def test_build_turn_citation_evidence_returns_none_when_rag_disabled() -> None:
    assert (
        build_turn_citation_evidence(
            _augmentation(enabled=False), conversation_id="c1", turn_id="t1"
        )
        is None
    )


def test_build_turn_citation_evidence_projects_enabled_augmentation() -> None:
    evidence = build_turn_citation_evidence(
        _augmentation(enabled=True), conversation_id="c1", turn_id="t1"
    )
    assert evidence is not None
    assert evidence.conversation_id == "c1"
    assert evidence.turn_id == "t1"
    assert evidence.citation_schema_version == CITATION_EVIDENCE_SCHEMA_VERSION
    assert evidence.retrieval_state is DocumentationRetrievalState.ENABLED
    assert evidence.citations == (_citation(),)


def test_citation_unavailable_reason_is_closed() -> None:
    with pytest.raises(ValidationError):
        CitationUnavailable(turn_id="t1", reason="something_else")  # type: ignore[arg-type]
    assert CitationUnavailable(turn_id="t1", reason="not_present").reason == "not_present"
