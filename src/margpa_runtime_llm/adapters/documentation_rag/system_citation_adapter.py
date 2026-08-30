"""Derive citations only from selected system retrieval results."""

from __future__ import annotations

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    AssembledDocumentationContext,
    DocumentationCitation,
    RetrievalResult,
)


class SystemCitationAdapter:
    schema_version = "1"

    def build(
        self,
        retrieval: RetrievalResult,
        context: AssembledDocumentationContext,
    ) -> tuple[DocumentationCitation, ...]:
        retrieved_by_chunk = {item.chunk.chunk_id: item for item in retrieval.selected}
        citations: list[DocumentationCitation] = []
        for block in context.blocks:
            selected = retrieved_by_chunk[block.chunk_id]
            citations.append(
                DocumentationCitation(
                    citation_id=f"citation-{len(citations) + 1}",
                    project_relative_path=block.project_relative_path,
                    heading_breadcrumb=block.heading_breadcrumb,
                    chunk_id=block.chunk_id,
                    document_sha512=selected.chunk.document_sha512,
                    retrieval_score=selected.score,
                    selected_order=len(citations) + 1,
                    truncated=block.truncated,
                    source_class=block.source_class,
                    document_title=block.document_title,
                    storage_display_path=block.storage_display_path,
                )
            )
        return tuple(citations)
