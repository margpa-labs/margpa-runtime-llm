"""Bounded HTTP contracts for Governed Web Search/Fetch (P7-E/F)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from margpa_runtime_llm.modules.web_knowledge.contracts import (
    MAX_QUERY_CHARACTERS,
    WebEvidenceGovernanceMode,
    WebFetchFailureReason,
    WebSearchActivation,
    WebSearchAndFetchResult,
)


class _WebSearchContract(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class WebSearchRuntimeResponse(_WebSearchContract):
    enabled: bool = True
    governance_mode: WebEvidenceGovernanceMode


class WebSearchRequest(_WebSearchContract):
    query: str = Field(min_length=1, max_length=MAX_QUERY_CHARACTERS)
    activation: WebSearchActivation = WebSearchActivation.MANUAL

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("web search query must not be blank")
        return value

    @field_validator("activation")
    @classmethod
    def validate_activation(cls, value: WebSearchActivation) -> WebSearchActivation:
        if value is WebSearchActivation.AUTOMATIC:
            raise ValueError("automatic activation cannot be requested by a client")
        return value


class WebEvidenceResponse(_WebSearchContract):
    evidence_id: str
    canonical_url: str
    title: str
    provider_key: str
    source_authority: str
    snippet: str
    fetched: bool
    fetched_content: str | None
    withheld_by_governance: bool
    fetched_at: str | None
    content_type: str | None
    prompt_injection_detected: bool
    rejected: bool
    rejection_reason: str | None


class WebCitationResponse(_WebSearchContract):
    citation_id: str
    canonical_url: str
    title: str
    provider_key: str
    source_authority: str
    fetched_at: str | None
    selected_order: int


class WebSearchResponse(_WebSearchContract):
    request_id: str
    activation: WebSearchActivation
    governance_mode: WebEvidenceGovernanceMode
    evidence: tuple[WebEvidenceResponse, ...]
    citations: tuple[WebCitationResponse, ...]
    should_generate_with_evidence: bool
    failure_reason: WebFetchFailureReason | None
    network_calls_made: int


def project_web_search_result(value: WebSearchAndFetchResult) -> WebSearchResponse:
    return WebSearchResponse(
        request_id=value.request_id,
        activation=value.activation,
        governance_mode=value.governance_mode,
        evidence=tuple(
            WebEvidenceResponse(
                evidence_id=item.evidence_id,
                canonical_url=item.canonical_url,
                title=item.title,
                provider_key=item.provider_key,
                source_authority=item.source_authority.value,
                snippet=item.snippet,
                fetched=item.fetched,
                fetched_content=item.fetched_content,
                withheld_by_governance=item.withheld_by_governance,
                fetched_at=item.fetched_at,
                content_type=item.content_type,
                prompt_injection_detected=item.prompt_injection_detected,
                rejected=item.rejected,
                rejection_reason=(
                    item.rejection_reason.value if item.rejection_reason is not None else None
                ),
            )
            for item in value.evidence
        ),
        citations=tuple(
            WebCitationResponse(
                citation_id=item.citation_id,
                canonical_url=item.canonical_url,
                title=item.title,
                provider_key=item.provider_key,
                source_authority=item.source_authority.value,
                fetched_at=item.fetched_at,
                selected_order=item.selected_order,
            )
            for item in value.citations
        ),
        should_generate_with_evidence=value.should_generate_with_evidence,
        failure_reason=value.failure_reason,
        network_calls_made=value.network_calls_made,
    )
