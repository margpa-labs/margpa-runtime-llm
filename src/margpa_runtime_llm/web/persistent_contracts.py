"""Typed safe contracts for the local-private persistent conversation API."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from margpa_runtime_llm.modules.conversation.contracts import (
    MAX_CONVERSATION_MESSAGE_CHARACTERS,
    ConversationSettings,
)
from margpa_runtime_llm.modules.conversation.domain import (
    MAX_CONVERSATION_TITLE_CHARACTERS,
    ConversationSnapshot,
)
from margpa_runtime_llm.modules.conversation.ports import ConversationPage, StoredConversation
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CitationUnavailable,
    PersistedTurnCitationEvidence,
)
from margpa_runtime_llm.modules.web_knowledge import (
    PersistedTurnWebCitationEvidence,
    WebCitationUnavailable,
)

WEB_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"


class _PersistentContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class PersistentRuntimeResponse(_PersistentContract):
    enabled: bool
    api_version: Literal["2"] = "2"
    source_of_truth: Literal["server"] = "server"
    features: tuple[str, ...] = ()


class PersistentCreateRequest(_PersistentContract):
    operation_id: str = Field(min_length=1, max_length=128, pattern=WEB_ID_PATTERN)
    expected_revision: None = None


class PersistentMutationRequest(_PersistentContract):
    operation_id: str = Field(min_length=1, max_length=128, pattern=WEB_ID_PATTERN)
    expected_revision: int = Field(strict=True, ge=1)


class PersistentTurnStreamRequest(PersistentMutationRequest):
    content: str = Field(max_length=MAX_CONVERSATION_MESSAGE_CHARACTERS)
    settings: ConversationSettings

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("persistent conversation content must not be blank")
        return value


class PersistentDerivedStreamRequest(PersistentMutationRequest):
    settings: ConversationSettings


class PersistentRenameRequest(PersistentMutationRequest):
    title: str = Field(max_length=MAX_CONVERSATION_TITLE_CHARACTERS)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        stripped = value.strip()
        if stripped and any(
            ord(character) < 0x20 or ord(character) == 0x7F for character in stripped
        ):
            raise ValueError("persistent conversation title must not contain control characters")
        return stripped


class PersistentStopRequest(_PersistentContract):
    request_id: str = Field(min_length=1, max_length=128)
    expected_revision: int = Field(strict=True, ge=1)

    @field_validator("request_id")
    @classmethod
    def validate_request_id(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("request id must not be blank")
        return value


class PersistentConversationSummaryResponse(_PersistentContract):
    conversation_id: str
    state: str
    title: str | None = None
    head_turn_id: str | None = None
    created_at: datetime
    updated_at: datetime
    has_active_session: bool


class PersistentConversationPageResponse(_PersistentContract):
    items: tuple[PersistentConversationSummaryResponse, ...]
    next_cursor: str | None = None


class PersistentSessionResponse(_PersistentContract):
    session_id: str
    state: str
    opened_at: datetime
    finished_at: datetime | None = None


class PersistentMessageResponse(_PersistentContract):
    role: Literal["user", "assistant"]
    content: str


class PersistentCitationResponse(_PersistentContract):
    """Same safe projection shape as the live SSE `retrieval` event."""

    source_class: str
    project_relative_path: str
    heading_breadcrumb: str
    chunk_id: str
    document_sha512: str
    retrieval_score: float
    selected_order: int
    truncated: bool = False
    # P7-RW5-B/C: carried unchanged from `DocumentationCitation` - `None`
    # for Project Docs and for any Citation persisted before these fields
    # existed (lossless decode of an older record).
    document_title: str | None = None
    storage_display_path: str | None = None


class PersistentTurnCitationsResponse(_PersistentContract):
    """Distinguishes "no citation evidence" from "evidence present but unreadable"."""

    available: bool
    unavailable_reason: Literal["unsupported_schema_version", "corrupt_record"] | None = None
    citations: tuple[PersistentCitationResponse, ...] = ()
    # P7-RW5-A (P7-CODEX-014): reuses `PersistedTurnCitationEvidence.
    # warning_codes` unchanged - lets a Persistent Detail reload rebuild
    # the same NO_HIT "no current grounds" display the Live SSE `retrieval`
    # event already showed, even though `citations` itself stays empty for
    # that Grounding State. Always `()` for a Turn whose citations are
    # non-empty (no behavior change there).
    warning_codes: tuple[str, ...] = ()


class PersistentWebCitationResponse(_PersistentContract):
    """P8-A: same safe projection shape as the live SSE `web_evidence` event."""

    citation_id: str
    requested_url: str
    canonical_url: str
    title: str
    provider_key: str
    source_authority: str
    fetched_at: str | None = None
    content_type: str | None = None
    transformation: str
    content_sha512: str | None = None
    source_class: str
    selected_order: int


class PersistentTurnWebCitationsResponse(_PersistentContract):
    """Distinguishes "no Manual URL Fetch was requested" from "Evidence
    present but unreadable" (mirrors `PersistentTurnCitationsResponse`)."""

    available: bool
    unavailable_reason: Literal["unsupported_schema_version", "corrupt_record"] | None = None
    citations: tuple[PersistentWebCitationResponse, ...] = ()
    failure_reason: str | None = None
    specific_failure_reason: str | None = None
    """P8-MR2 (P8-MANUAL-002) / UF-P8-007: the per-Evidence Reason
    alongside the coarser Aggregate `failure_reason` above — see
    `PersistedTurnWebCitationEvidence.specific_failure_reason`."""


class PersistentTurnResponse(_PersistentContract):
    turn_id: str
    sequence: int
    state: str
    origin: str
    parent_turn_id: str | None = None
    derived_from_turn_id: str | None = None
    request_id: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    failure_reason_code: str | None = None
    messages: tuple[PersistentMessageResponse, ...]
    citations: PersistentTurnCitationsResponse | None = None
    web_citations: PersistentTurnWebCitationsResponse | None = None


class PersistentConversationDetailResponse(_PersistentContract):
    conversation_id: str
    state: str
    title: str | None = None
    head_turn_id: str | None = None
    storage_revision: int
    created_at: datetime
    updated_at: datetime
    sessions: tuple[PersistentSessionResponse, ...]
    turns: tuple[PersistentTurnResponse, ...]


class PersistentMutationResponse(_PersistentContract):
    status: Literal["accepted"] = "accepted"
    detail: PersistentConversationDetailResponse


class PersistentStopResponse(_PersistentContract):
    status: Literal["cancellation_requested"] = "cancellation_requested"


def project_persistent_page(page: ConversationPage) -> PersistentConversationPageResponse:
    return PersistentConversationPageResponse(
        items=tuple(
            PersistentConversationSummaryResponse(
                conversation_id=item.conversation_id.value,
                state=item.state.value,
                title=item.title,
                head_turn_id=item.head_turn_id.value if item.head_turn_id is not None else None,
                created_at=item.created_at,
                updated_at=item.updated_at,
                has_active_session=item.has_active_session,
            )
            for item in page.items
        ),
        next_cursor=page.next_cursor,
    )


def _project_turn_citations(
    entry: PersistedTurnCitationEvidence | CitationUnavailable | None,
) -> PersistentTurnCitationsResponse | None:
    if entry is None:
        return None
    if isinstance(entry, CitationUnavailable):
        if entry.reason == "not_present":
            return None
        return PersistentTurnCitationsResponse(available=False, unavailable_reason=entry.reason)
    return PersistentTurnCitationsResponse(
        available=True,
        citations=tuple(
            PersistentCitationResponse(
                source_class=citation.source_class,
                project_relative_path=citation.project_relative_path,
                heading_breadcrumb=citation.heading_breadcrumb,
                chunk_id=citation.chunk_id,
                document_sha512=citation.document_sha512,
                retrieval_score=citation.retrieval_score,
                selected_order=citation.selected_order,
                truncated=citation.truncated,
                document_title=citation.document_title,
                storage_display_path=citation.storage_display_path,
            )
            for citation in entry.citations
        ),
        warning_codes=entry.warning_codes,
    )


def _project_turn_web_citations(
    entry: PersistedTurnWebCitationEvidence | WebCitationUnavailable | None,
) -> PersistentTurnWebCitationsResponse | None:
    if entry is None:
        return None
    if isinstance(entry, WebCitationUnavailable):
        if entry.reason == "not_present":
            return None
        return PersistentTurnWebCitationsResponse(available=False, unavailable_reason=entry.reason)
    return PersistentTurnWebCitationsResponse(
        available=True,
        citations=tuple(
            PersistentWebCitationResponse(
                citation_id=citation.citation_id,
                requested_url=citation.requested_url,
                canonical_url=citation.canonical_url,
                title=citation.title,
                provider_key=citation.provider_key,
                source_authority=citation.source_authority.value,
                fetched_at=citation.fetched_at,
                content_type=citation.content_type,
                transformation=citation.transformation.value,
                content_sha512=citation.content_sha512,
                source_class=citation.source_class,
                selected_order=citation.selected_order,
            )
            for citation in entry.citations
        ),
        failure_reason=(entry.failure_reason.value if entry.failure_reason is not None else None),
        specific_failure_reason=entry.specific_failure_reason,
    )


def project_persistent_detail(
    stored: StoredConversation,
    *,
    citations_by_turn: Mapping[str, PersistedTurnCitationEvidence | CitationUnavailable]
    | None = None,
    web_citations_by_turn: (
        Mapping[str, PersistedTurnWebCitationEvidence | WebCitationUnavailable] | None
    ) = None,
) -> PersistentConversationDetailResponse:
    snapshot: ConversationSnapshot = stored.conversation
    messages_by_turn: dict[str, list[PersistentMessageResponse]] = {}
    for message in snapshot.messages:
        messages_by_turn.setdefault(message.turn_id.value, []).append(
            PersistentMessageResponse(role=message.role.value, content=message.content)
        )
    return PersistentConversationDetailResponse(
        conversation_id=snapshot.conversation_id.value,
        state=snapshot.state.value,
        title=snapshot.title,
        head_turn_id=(snapshot.head_turn_id.value if snapshot.head_turn_id is not None else None),
        storage_revision=stored.storage_revision,
        created_at=snapshot.created_at,
        updated_at=snapshot.updated_at,
        sessions=tuple(
            PersistentSessionResponse(
                session_id=session.session_id.value,
                state=session.state.value,
                opened_at=session.opened_at,
                finished_at=session.finished_at,
            )
            for session in snapshot.sessions
        ),
        turns=tuple(
            PersistentTurnResponse(
                turn_id=turn.turn_id.value,
                sequence=turn.sequence,
                state=turn.state.value,
                origin=turn.origin.value,
                parent_turn_id=(
                    turn.parent_turn_id.value if turn.parent_turn_id is not None else None
                ),
                derived_from_turn_id=(
                    turn.derived_from_turn_id.value
                    if turn.derived_from_turn_id is not None
                    else None
                ),
                request_id=turn.request_id,
                started_at=turn.started_at,
                finished_at=turn.finished_at,
                failure_reason_code=turn.failure_reason_code,
                messages=tuple(messages_by_turn.get(turn.turn_id.value, ())),
                citations=_project_turn_citations(
                    None if citations_by_turn is None else citations_by_turn.get(turn.turn_id.value)
                ),
                web_citations=_project_turn_web_citations(
                    None
                    if web_citations_by_turn is None
                    else web_citations_by_turn.get(turn.turn_id.value)
                ),
            )
            for turn in snapshot.turns
        ),
    )
