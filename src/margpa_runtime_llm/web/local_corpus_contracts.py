"""Bounded HTTP contracts for the Local Corpus document registry (P7-B)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from margpa_runtime_llm.modules.documentation_rag.local_corpus_contracts import (
    MAX_DOCUMENT_CHARACTERS,
    MAX_TITLE_CHARACTERS,
    LocalCorpusDocumentInput,
    LocalCorpusDocumentRecord,
    LocalCorpusDocumentSummary,
    summarize,
)


class _LocalCorpusContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class LocalCorpusDocumentInputRequest(_LocalCorpusContract):
    title: str = Field(min_length=1, max_length=MAX_TITLE_CHARACTERS)
    content: str = Field(min_length=1, max_length=MAX_DOCUMENT_CHARACTERS)

    def to_domain(self) -> LocalCorpusDocumentInput:
        return LocalCorpusDocumentInput(title=self.title, content=self.content)


class LocalCorpusDocumentSummaryResponse(_LocalCorpusContract):
    document_id: str
    state: str
    title: str
    content_sha512: str
    character_count: int
    current_revision: int
    created_at: datetime
    updated_at: datetime


class LocalCorpusDocumentResponse(LocalCorpusDocumentSummaryResponse):
    content: str


class LocalCorpusDocumentListResponse(_LocalCorpusContract):
    documents: tuple[LocalCorpusDocumentSummaryResponse, ...]


def project_summary(
    value: LocalCorpusDocumentSummary,
) -> LocalCorpusDocumentSummaryResponse:
    return LocalCorpusDocumentSummaryResponse(
        document_id=value.document_id,
        state=value.state.value,
        title=value.title,
        content_sha512=value.content_sha512,
        character_count=value.character_count,
        current_revision=value.current_revision,
        created_at=value.created_at,
        updated_at=value.updated_at,
    )


def project_list(
    values: tuple[LocalCorpusDocumentRecord, ...],
) -> LocalCorpusDocumentListResponse:
    return LocalCorpusDocumentListResponse(
        documents=tuple(project_summary(summarize(record)) for record in values)
    )


def project_document(value: LocalCorpusDocumentRecord) -> LocalCorpusDocumentResponse:
    return LocalCorpusDocumentResponse(
        document_id=value.document_id,
        state=value.state.value,
        title=value.title,
        content_sha512=value.content_sha512,
        character_count=len(value.content),
        current_revision=value.current_revision,
        created_at=value.created_at,
        updated_at=value.updated_at,
        content=value.content,
    )
