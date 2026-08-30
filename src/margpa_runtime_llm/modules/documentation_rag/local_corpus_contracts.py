"""Phase 7 (P7-B): Local Corpus document lifecycle contracts.

A Local Corpus document is a user-registered, plain Text/Markdown record
(P7-A Attachment Sizing: Chat Composer attachment is deferred to Phase 10;
this is the "Local Document register/update/delete" boundary from
P7-REQ-002 instead). It feeds the *same* `DocumentationRagApplicationService`
pipeline as Phase 2's fixed project documentation corpus, through
`LocalCorpusDocumentSource` (a `DocumentSourcePort`) composed alongside it —
see `phase_7_current_claude_task_p7_0_recovery_ja_*.md` §3 for why no new
Orchestrator or Citation/Persistence contract was introduced.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from enum import StrEnum
from typing import Literal

from pydantic import Field, field_validator, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

from .contracts import SHA512_PATTERN

LOCAL_CORPUS_DOCUMENT_ID_PATTERN = r"^[a-f0-9]{32}$"
LOCAL_CORPUS_SOURCE_CLASS = "local_corpus"

MAX_TITLE_CHARACTERS = 200
MAX_DOCUMENT_CHARACTERS = 200_000
MAX_ACTIVE_DOCUMENTS = 200
MAX_CORPUS_TOTAL_CHARACTERS = 4_000_000
"""Deliberately small (Resource Gate — individual PoC, ~33GiB free disk, no
new heavy Vector/Index dependency): bounds the in-memory lexical index this
feeds, not a document-management product limit."""


class LocalCorpusDocumentState(StrEnum):
    ACTIVE = "active"
    DELETED = "deleted"


class LocalCorpusDocumentInput(ImmutableContract):
    """Register/update request body. Content is already-decoded text — no
    binary upload, parser, or Archive/Multimodal handling (P7-A Sizing)."""

    title: str = Field(min_length=1, max_length=MAX_TITLE_CHARACTERS)
    content: str = Field(min_length=1, max_length=MAX_DOCUMENT_CHARACTERS)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("local corpus document title must not be blank")
        if any(ord(character) < 0x20 or ord(character) == 0x7F for character in stripped):
            raise ValueError("local corpus document title must not contain control characters")
        return stripped

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("local corpus document content must not be blank")
        return value


class LocalCorpusDocumentRevision(ImmutableContract):
    """One immutable, append-only revision. Architecture §3 Invariant 6:
    "Document更新後は旧Revision Evidenceを消さず、CurrentとHistoricalを区別する" —
    `LocalCorpusDocumentRecord.revisions` never drops or mutates an entry
    once appended, including across a soft-delete."""

    revision: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=MAX_TITLE_CHARACTERS)
    content_sha512: str = Field(pattern=SHA512_PATTERN)
    character_count: int = Field(ge=1)
    recorded_at: datetime


class LocalCorpusDocumentRecord(ImmutableContract):
    """Current + historical state for one registered document.

    `content` is carried only on the record returned by `register()`/
    `update()`/`get()` (needed to actually feed the RAG pipeline); list
    projections may omit it — see `LocalCorpusDocumentSummary`.
    """

    document_id: str = Field(pattern=LOCAL_CORPUS_DOCUMENT_ID_PATTERN)
    state: LocalCorpusDocumentState
    title: str = Field(min_length=1, max_length=MAX_TITLE_CHARACTERS)
    content: str = Field(min_length=1, max_length=MAX_DOCUMENT_CHARACTERS)
    content_sha512: str = Field(pattern=SHA512_PATTERN)
    current_revision: int = Field(ge=1)
    revisions: tuple[LocalCorpusDocumentRevision, ...] = Field(min_length=1)
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def validate_revision_chain(self) -> LocalCorpusDocumentRecord:
        if self.revisions[-1].revision != self.current_revision:
            raise ValueError("current_revision must match the latest revision entry")
        if tuple(entry.revision for entry in self.revisions) != tuple(
            range(1, len(self.revisions) + 1)
        ):
            raise ValueError("revisions must be a contiguous 1-based sequence")
        if self.state is LocalCorpusDocumentState.ACTIVE and self.revisions[-1].content_sha512 != (
            self.content_sha512
        ):
            raise ValueError("active record content digest must match its latest revision")
        return self

    @property
    def path_slug(self) -> str:
        """Deterministic, safe synthetic `project_relative_path` component
        (`local-corpus/<slug>-<document_id[:8]>.md`) used only for citation
        display — never a real filesystem path (`LocalCorpusDocumentSource`
        serves `content` from this record directly, never from disk)."""

        return _slugify(self.title, self.document_id)


class LocalCorpusDocumentSummary(ImmutableContract):
    """Safe listing projection — no `content` (Settings UI list view)."""

    document_id: str = Field(pattern=LOCAL_CORPUS_DOCUMENT_ID_PATTERN)
    state: LocalCorpusDocumentState
    title: str
    content_sha512: str = Field(pattern=SHA512_PATTERN)
    character_count: int = Field(ge=1)
    current_revision: int = Field(ge=1)
    created_at: datetime
    updated_at: datetime


class LocalCorpusDocumentNotFound(Exception):
    def __init__(self, document_id: str) -> None:
        super().__init__(f"local corpus document not found: {document_id}")
        self.document_id = document_id


class LocalCorpusLimitExceeded(Exception):
    code: Literal[
        "local_corpus_document_limit_exceeded",
        "local_corpus_total_size_limit_exceeded",
    ]

    def __init__(
        self,
        code: Literal[
            "local_corpus_document_limit_exceeded",
            "local_corpus_total_size_limit_exceeded",
        ],
    ) -> None:
        super().__init__(code)
        self.code = code


def summarize(record: LocalCorpusDocumentRecord) -> LocalCorpusDocumentSummary:
    return LocalCorpusDocumentSummary(
        document_id=record.document_id,
        state=record.state,
        title=record.title,
        content_sha512=record.content_sha512,
        character_count=len(record.content),
        current_revision=record.current_revision,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


def _slugify(title: str, document_id: str) -> str:
    lowered = title.strip().lower()
    characters: list[str] = []
    previous_dash = False
    for character in lowered:
        if character.isalnum() and character.isascii():
            characters.append(character)
            previous_dash = False
        elif not previous_dash:
            characters.append("-")
            previous_dash = True
    slug = "".join(characters).strip("-")[:64].strip("-")
    if not slug:
        slug = "document"
    return f"{slug}-{document_id[:8]}"


def content_digest(content: str) -> str:
    return hashlib.sha512(content.encode("utf-8")).hexdigest()
