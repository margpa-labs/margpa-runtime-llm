"""Framework-independent contracts for deterministic documentation retrieval."""

from __future__ import annotations

import re
from enum import IntEnum, StrEnum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from margpa_runtime_llm.modules.inference.contracts.base import ImmutableContract

SHA512_PATTERN = r"^[0-9a-f]{128}$"
LIGHTNING_PUBLIC_DOCUMENTATION_FILES = (
    "docs/public/overview_ja.md",
    "docs/public/overview_en.md",
    "docs/public/concept_ja.md",
    "docs/public/concept_en.md",
    "docs/public/roadmap_ja.md",
    "docs/public/roadmap_en.md",
    "docs/public/technology_selection_ja.md",
    "docs/public/technology_selection_en.md",
)


class DocumentationRagMode(StrEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"


class DocumentationRagAvailability(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DENIED = "denied"


class DocumentationRagPlatform(StrEnum):
    MACOS_ARM64 = "macos-arm64"
    LINUX_X86_64_CONTAINER = "linux-x86_64-container"


class DocumentationRetrievalState(StrEnum):
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    ENABLED = "enabled"
    DENIED = "denied"


class DocumentationGroundingState(StrEnum):
    NO_HIT = "no_hit"
    GROUNDED_READY = "grounded_ready"
    CONTEXT_INSUFFICIENT = "context_insufficient"
    SUBJECT_COVERAGE_INSUFFICIENT = "subject_coverage_insufficient"
    UNAVAILABLE = "unavailable"


class DocumentationMeasurementUnit(StrEnum):
    TOKENS = "tokens"
    UNICODE_CHARACTERS = "unicode_characters"


class CorpusPriority(IntEnum):
    CURRENT = 0
    PUBLIC = 1
    ACTIVE_PHASE_INDEX = 2
    COMPLETED_PHASE = 3


class DocumentationWarning(ImmutableContract):
    code: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    message: str
    count: int = Field(default=1, ge=1)


class DocumentManifestEntry(ImmutableContract):
    source_id: str = Field(pattern=SHA512_PATTERN)
    project_relative_path: str = Field(min_length=1)
    corpus_priority: CorpusPriority
    document_sha512: str = Field(pattern=SHA512_PATTERN)
    size_bytes: int = Field(ge=0)
    modified_time_ns: int = Field(ge=0)
    media_type: Literal["text/markdown"] = "text/markdown"
    encoding: Literal["utf-8"] = "utf-8"

    @field_validator("project_relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        return _validate_project_relative_path(value)


class CorpusManifest(ImmutableContract):
    docs_present: bool
    entries: tuple[DocumentManifestEntry, ...] = ()
    corpus_manifest_digest: str = Field(pattern=SHA512_PATTERN)
    total_bytes: int = Field(ge=0)
    warnings: tuple[DocumentationWarning, ...] = ()

    @model_validator(mode="after")
    def validate_totals(self) -> CorpusManifest:
        if self.total_bytes != sum(entry.size_bytes for entry in self.entries):
            raise ValueError("corpus byte total must match manifest entries")
        return self


class DocumentSource(ImmutableContract):
    manifest: DocumentManifestEntry
    content: str


class DocumentationChunk(ImmutableContract):
    chunk_id: str = Field(pattern=SHA512_PATTERN)
    source_id: str = Field(pattern=SHA512_PATTERN)
    project_relative_path: str = Field(min_length=1)
    corpus_priority: CorpusPriority
    heading_breadcrumb: str
    ordinal: int = Field(ge=0)
    content: str
    content_sha512: str = Field(pattern=SHA512_PATTERN)
    document_sha512: str = Field(pattern=SHA512_PATTERN)
    character_count: int = Field(ge=1)
    split_from_oversized_block: bool = False

    @field_validator("project_relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        return _validate_project_relative_path(value)

    @model_validator(mode="after")
    def validate_character_count(self) -> DocumentationChunk:
        if self.character_count != len(self.content):
            raise ValueError("chunk character count must match content")
        return self


class RetrievalQuery(ImmutableContract):
    query_text: str
    query_digest: str = Field(pattern=SHA512_PATTERN)
    top_k: int = Field(gt=0)
    minimum_score: float = Field(ge=0.0)
    max_chunks_per_document: int = Field(gt=0)


class RetrievalScoreComponents(ImmutableContract):
    body: float = Field(ge=0.0)
    heading: float = Field(ge=0.0)
    path: float = Field(ge=0.0)
    exact_phrase: float = Field(ge=0.0)
    corpus_priority: float = Field(ge=0.0)

    @property
    def total(self) -> float:
        return self.body + self.heading + self.path + self.exact_phrase + self.corpus_priority


class RetrievedChunk(ImmutableContract):
    chunk: DocumentationChunk
    score: float = Field(ge=0.0)
    rank: int = Field(gt=0)
    score_components: RetrievalScoreComponents


class SubjectCoverageTrace(ImmutableContract):
    """Transient mapping from a redacted query subject to retrieved chunks."""

    subject_digest: str = Field(pattern=SHA512_PATTERN)
    retrieved_chunk_ids: tuple[str, ...] = ()

    @field_validator("retrieved_chunk_ids")
    @classmethod
    def validate_chunk_ids(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("subject coverage chunk ids must be distinct")
        if any(re.fullmatch(SHA512_PATTERN, chunk_id) is None for chunk_id in value):
            raise ValueError("subject coverage chunk ids must be SHA-512 digests")
        return value


class RetrievalResult(ImmutableContract):
    query_digest: str = Field(pattern=SHA512_PATTERN)
    selected: tuple[RetrievedChunk, ...] = ()
    subject_coverage: tuple[SubjectCoverageTrace, ...] = ()
    identifier_subject_count: int = Field(default=0, ge=0)
    covered_subject_count: int = Field(default=0, ge=0)
    uncovered_subject_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_subject_coverage(self) -> RetrievalResult:
        if len(self.subject_coverage) != self.identifier_subject_count:
            raise ValueError("subject coverage trace must match subject count")
        subject_digests = tuple(trace.subject_digest for trace in self.subject_coverage)
        if len(subject_digests) != len(set(subject_digests)):
            raise ValueError("subject coverage digests must be distinct")
        selected_chunk_ids = {item.chunk.chunk_id for item in self.selected}
        if any(
            chunk_id not in selected_chunk_ids
            for trace in self.subject_coverage
            for chunk_id in trace.retrieved_chunk_ids
        ):
            raise ValueError("subject coverage must reference selected chunks")
        traced_covered_count = sum(
            bool(trace.retrieved_chunk_ids) for trace in self.subject_coverage
        )
        if traced_covered_count != self.covered_subject_count:
            raise ValueError("covered subject count must match subject coverage trace")
        if self.covered_subject_count + self.uncovered_subject_count != (
            self.identifier_subject_count
        ):
            raise ValueError("covered and uncovered subjects must equal subject count")
        return self


class DocumentationRagRequestContext(ImmutableContract):
    """Safe request-scoped inputs used to resolve the documentation budget."""

    effective_context_size: int = Field(gt=0)
    requested_max_new_tokens: int = Field(gt=0)
    system_history_current_prompt_tokens: int | None = Field(default=None, ge=0)
    prompt_measurement_unit: DocumentationMeasurementUnit = DocumentationMeasurementUnit.TOKENS
    prompt_token_count_exact: bool = False

    @model_validator(mode="after")
    def validate_prompt_measurement(self) -> DocumentationRagRequestContext:
        if self.prompt_measurement_unit is not DocumentationMeasurementUnit.TOKENS:
            raise ValueError("base chat prompt measurement must use tokens")
        if self.prompt_token_count_exact and self.system_history_current_prompt_tokens is None:
            raise ValueError("exact prompt measurement requires a measured token count")
        return self


class DocumentationContextBudget(ImmutableContract):
    maximum_tokens: int = Field(ge=0)
    minimum_useful_tokens: int = Field(gt=0)
    safety_margin_tokens: int = Field(ge=0)
    fallback_maximum_characters: int = Field(ge=0)


class DocumentationReferenceBlock(ImmutableContract):
    reference_id: str = Field(pattern=r"^ref-[1-9][0-9]*$")
    project_relative_path: str = Field(min_length=1)
    heading_breadcrumb: str
    chunk_id: str = Field(pattern=SHA512_PATTERN)
    content: str
    measured_size: int = Field(gt=0)
    measurement_unit: DocumentationMeasurementUnit
    truncated: bool = False

    @field_validator("project_relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        return _validate_project_relative_path(value)


class AssembledDocumentationContext(ImmutableContract):
    reference_message: str | None = None
    blocks: tuple[DocumentationReferenceBlock, ...] = ()
    context_used: int = Field(ge=0)
    measurement_unit: DocumentationMeasurementUnit
    measurement_limit: int = Field(ge=0)
    token_budget_used: bool = False
    token_counter_fallback_used: bool = False
    truncated: bool = False

    @model_validator(mode="after")
    def validate_measurement_semantics(self) -> AssembledDocumentationContext:
        uses_tokens = self.measurement_unit is DocumentationMeasurementUnit.TOKENS
        if self.token_budget_used != uses_tokens:
            raise ValueError("token budget flag must match the context measurement unit")
        if self.token_counter_fallback_used == uses_tokens:
            raise ValueError("token counter fallback flag must match the measurement unit")
        if self.context_used > self.measurement_limit:
            raise ValueError("context usage must not exceed its same-unit limit")
        if any(block.measurement_unit is not self.measurement_unit for block in self.blocks):
            raise ValueError("block measurement units must match the context measurement unit")
        return self


class DocumentationCitation(ImmutableContract):
    citation_id: str = Field(pattern=r"^citation-[1-9][0-9]*$")
    project_relative_path: str = Field(min_length=1)
    heading_breadcrumb: str
    chunk_id: str = Field(pattern=SHA512_PATTERN)
    document_sha512: str = Field(pattern=SHA512_PATTERN)
    retrieval_score: float = Field(ge=0.0)
    selected_order: int = Field(gt=0)
    truncated: bool = False

    @field_validator("project_relative_path")
    @classmethod
    def validate_relative_path(cls, value: str) -> str:
        return _validate_project_relative_path(value)


class DocumentationEvidence(ImmutableContract):
    query_digest: str = Field(pattern=SHA512_PATTERN)
    corpus_manifest_digest: str = Field(pattern=SHA512_PATTERN)
    retriever_key: str
    retriever_version: str
    selected_chunk_ids: tuple[str, ...] = ()
    selected_document_digests: tuple[str, ...] = ()
    selected_scores: tuple[float, ...] = ()
    base_prompt_used: int | None = Field(default=None, ge=0)
    base_prompt_unit: DocumentationMeasurementUnit
    base_prompt_exact: bool = False
    context_budget: int = Field(ge=0)
    context_budget_unit: DocumentationMeasurementUnit
    context_used: int = Field(ge=0)
    context_measurement_unit: DocumentationMeasurementUnit
    context_measurement_limit: int = Field(ge=0)
    context_token_budget_used: bool = False
    token_counter_fallback_used: bool = False
    retrieved_chunk_count: int = Field(ge=0)
    assembled_block_count: int = Field(ge=0)
    identifier_subject_count: int = Field(ge=0)
    retrieval_covered_subject_count: int = Field(ge=0)
    retrieval_uncovered_subject_count: int = Field(ge=0)
    covered_subject_count: int = Field(ge=0)
    uncovered_subject_count: int = Field(ge=0)
    grounding_state: DocumentationGroundingState
    generation_allowed: bool
    truncation_state: bool = False
    index_rebuilt: bool = False
    retrieval_duration_ms: float = Field(ge=0.0)

    @model_validator(mode="after")
    def validate_measurement_semantics(self) -> DocumentationEvidence:
        if self.base_prompt_unit is not DocumentationMeasurementUnit.TOKENS:
            raise ValueError("base chat prompt measurement must use tokens")
        if self.base_prompt_exact and self.base_prompt_used is None:
            raise ValueError("exact base prompt measurement requires a value")
        if self.context_budget_unit is not DocumentationMeasurementUnit.TOKENS:
            raise ValueError("dynamic context budget must be recorded in tokens")
        uses_tokens = self.context_measurement_unit is DocumentationMeasurementUnit.TOKENS
        if self.context_token_budget_used != uses_tokens:
            raise ValueError("token budget flag must match the context measurement unit")
        if self.token_counter_fallback_used == uses_tokens:
            raise ValueError("token counter fallback flag must match the measurement unit")
        if self.context_used > self.context_measurement_limit:
            raise ValueError("context usage must not exceed its same-unit limit")
        if uses_tokens and self.context_measurement_limit != self.context_budget:
            raise ValueError("token measurement limit must match the dynamic token budget")
        if self.retrieved_chunk_count != len(self.selected_chunk_ids):
            raise ValueError("retrieved chunk count must match selected chunk evidence")
        if len(self.selected_document_digests) != self.retrieved_chunk_count:
            raise ValueError("selected document evidence must match retrieved chunk count")
        if len(self.selected_scores) != self.retrieved_chunk_count:
            raise ValueError("selected score evidence must match retrieved chunk count")
        if (
            self.retrieval_covered_subject_count + self.retrieval_uncovered_subject_count
            != self.identifier_subject_count
        ):
            raise ValueError("retrieval coverage must equal subject count")
        if self.covered_subject_count + self.uncovered_subject_count != (
            self.identifier_subject_count
        ):
            raise ValueError("assembled coverage must equal subject count")
        if self.covered_subject_count > self.retrieval_covered_subject_count:
            raise ValueError("assembled coverage cannot exceed retrieval coverage")
        if self.grounding_state is DocumentationGroundingState.GROUNDED_READY:
            if not self.generation_allowed or self.retrieved_chunk_count == 0:
                raise ValueError("grounded generation requires retrieved evidence")
            if self.assembled_block_count == 0:
                raise ValueError("grounded generation requires assembled reference blocks")
            if self.uncovered_subject_count != 0:
                raise ValueError("grounded generation requires full subject coverage")
        elif self.grounding_state is DocumentationGroundingState.CONTEXT_INSUFFICIENT:
            if self.generation_allowed or self.retrieved_chunk_count == 0:
                raise ValueError("context-insufficient state must deny a retrieval hit")
            if self.assembled_block_count != 0:
                raise ValueError("context-insufficient state must not contain reference blocks")
            if self.covered_subject_count != 0:
                raise ValueError("zero assembled blocks cannot cover subjects")
        elif self.grounding_state is DocumentationGroundingState.SUBJECT_COVERAGE_INSUFFICIENT:
            if self.generation_allowed or self.retrieved_chunk_count == 0:
                raise ValueError("subject-coverage state must deny a retrieval hit")
            if self.assembled_block_count == 0 or self.uncovered_subject_count == 0:
                raise ValueError("subject-coverage state requires partial assembled coverage")
        elif self.grounding_state is DocumentationGroundingState.NO_HIT:
            if not self.generation_allowed or self.retrieved_chunk_count != 0:
                raise ValueError("no-hit state must allow only ungrounded general generation")
            if self.assembled_block_count != 0:
                raise ValueError("no-hit state must not contain reference blocks")
        elif self.grounding_state is DocumentationGroundingState.UNAVAILABLE:
            if self.generation_allowed or self.assembled_block_count != 0:
                raise ValueError("unavailable state must deny generation without references")
        return self


class DocumentationAugmentation(ImmutableContract):
    state: DocumentationRetrievalState
    should_generate: bool
    reference_message: str | None = None
    citations: tuple[DocumentationCitation, ...] = ()
    evidence: DocumentationEvidence
    warnings: tuple[DocumentationWarning, ...] = ()
    document_count: int = Field(ge=0)
    selected_chunk_count: int = Field(ge=0)
    index_rebuilt: bool = False
    duration_ms: float = Field(ge=0.0)

    @model_validator(mode="after")
    def validate_selected_count(self) -> DocumentationAugmentation:
        if self.selected_chunk_count != len(self.citations):
            raise ValueError("selected chunk count must match system citations")
        if self.selected_chunk_count != self.evidence.assembled_block_count:
            raise ValueError("citations must match assembled reference block evidence")
        if self.should_generate != self.evidence.generation_allowed:
            raise ValueError("generation decision must match grounding evidence")
        if not self.should_generate and self.reference_message is not None:
            raise ValueError("blocked augmentation must not include a reference message")
        if self.evidence.grounding_state is DocumentationGroundingState.GROUNDED_READY:
            if self.reference_message is None or not self.citations:
                raise ValueError("grounded-ready augmentation requires references and citations")
        elif (
            self.evidence.grounding_state
            is DocumentationGroundingState.SUBJECT_COVERAGE_INSUFFICIENT
        ):
            if self.reference_message is not None or not self.citations:
                raise ValueError("subject-coverage denial exposes citations but no model reference")
        elif self.reference_message is not None or self.citations:
            raise ValueError("non-grounded augmentation must not expose references or citations")
        return self


CITATION_EVIDENCE_SCHEMA_VERSION = 1


class PersistedTurnCitationEvidence(ImmutableContract):
    """Safe, allowlisted citation evidence for one completed conversation turn.

    Reuses `DocumentationCitation` (already an allowlist type with a validated
    `project_relative_path`) rather than redefining overlapping fields. Carries
    no free-text content field, so absolute paths, secrets, raw thinking,
    system prompts, tool-internal state, hidden originals, unconfirmed partial
    output, raw exceptions, and unbounded raw retrieved chunks are all
    structurally impossible to persist through this type.
    """

    conversation_id: str = Field(min_length=1)
    turn_id: str = Field(min_length=1)
    citation_schema_version: int = Field(ge=1)
    corpus_revision: str = Field(pattern=SHA512_PATTERN)
    retrieval_state: DocumentationRetrievalState
    grounding_state: DocumentationGroundingState
    warning_codes: tuple[str, ...] = ()
    citations: tuple[DocumentationCitation, ...] = ()

    @model_validator(mode="after")
    def validate_state_consistency(self) -> PersistedTurnCitationEvidence:
        if self.retrieval_state is not DocumentationRetrievalState.ENABLED and self.citations:
            raise ValueError("only an enabled retrieval state may carry citations")
        return self


class CitationUnavailable(ImmutableContract):
    """Fail-closed placeholder returned instead of raising on a bad record."""

    turn_id: str = Field(min_length=1)
    reason: Literal["unsupported_schema_version", "corrupt_record", "not_present"]


def build_turn_citation_evidence(
    augmentation: DocumentationAugmentation,
    *,
    conversation_id: str,
    turn_id: str,
) -> PersistedTurnCitationEvidence | None:
    """Project a live `DocumentationAugmentation` into persistable evidence.

    Returns `None` when there is nothing to persist (RAG disabled/unavailable/
    denied, or no citations were produced) so the caller writes zero rows for
    that turn, matching the "RAG OFF => Citation Write 0" requirement.
    """

    if augmentation.state is not DocumentationRetrievalState.ENABLED or not augmentation.citations:
        return None
    return PersistedTurnCitationEvidence(
        conversation_id=conversation_id,
        turn_id=turn_id,
        citation_schema_version=CITATION_EVIDENCE_SCHEMA_VERSION,
        corpus_revision=augmentation.evidence.corpus_manifest_digest,
        retrieval_state=augmentation.state,
        grounding_state=augmentation.evidence.grounding_state,
        warning_codes=tuple(warning.code for warning in augmentation.warnings),
        citations=augmentation.citations,
    )


class DocumentationRagDefaultsConfig(ImmutableContract):
    schema_version: Literal["1"] = "1"
    profile_key: Literal["documentation-rag.defaults"] = "documentation-rag.defaults"
    default_mode: DocumentationRagMode = DocumentationRagMode.DISABLED


class DocumentationCorpusConfig(ImmutableContract):
    include_current: Literal[True] = True
    include_public: Literal[True] = True
    include_active_phase_index: Literal[True] = True
    include_completed_phase_stable: Literal[True] = True
    include_history: Literal[False] = False
    include_lossless: Literal[False] = False


class ExplicitDocumentationCorpusConfig(ImmutableContract):
    selection_mode: Literal["explicit_files"] = "explicit_files"
    files: tuple[str, ...]
    include_history: Literal[False] = False
    include_lossless: Literal[False] = False

    @field_validator("files")
    @classmethod
    def validate_files(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value or len(value) != len(set(value)):
            raise ValueError("explicit documentation paths must be non-empty and distinct")
        for path in value:
            _validate_project_relative_path(path)
            relative = Path(path)
            if relative.suffix.lower() != ".md" or relative.parent.as_posix() != "docs/public":
                raise ValueError("explicit documentation paths must be public Markdown files")
        return value


class DocumentationLimitsConfig(ImmutableContract):
    max_documents: int = Field(default=512, gt=0, le=10_000)
    max_file_bytes: int = Field(default=4 * 1024 * 1024, gt=0)
    max_corpus_bytes: int = Field(default=32 * 1024 * 1024, gt=0)
    max_chunks: int = Field(default=20_000, gt=0)


class DocumentationChunkingConfig(ImmutableContract):
    target_characters: int = Field(default=900, gt=0)
    overlap_characters: int = Field(default=120, ge=0)
    maximum_characters: int = Field(default=1600, gt=0)

    @model_validator(mode="after")
    def validate_sizes(self) -> DocumentationChunkingConfig:
        if self.target_characters > self.maximum_characters:
            raise ValueError("chunk target must not exceed maximum")
        if self.overlap_characters >= self.target_characters:
            raise ValueError("chunk overlap must be smaller than target")
        return self


class DocumentationRetrievalConfig(ImmutableContract):
    top_k: int = Field(default=4, gt=0, le=20)
    max_chunks_per_document: int = Field(default=2, gt=0)
    minimum_score: float = Field(default=0.1, ge=0.0)
    bm25_k1: float = Field(default=1.5, gt=0.0)
    bm25_b: float = Field(default=0.75, ge=0.0, le=1.0)
    body_weight: float = Field(default=1.0, ge=0.0)
    heading_weight: float = Field(default=1.75, ge=0.0)
    path_weight: float = Field(default=1.5, ge=0.0)
    exact_phrase_bonus: float = Field(default=2.0, ge=0.0)
    corpus_priority_weight: float = Field(default=0.25, ge=0.0)


class DocumentationContextConfig(ImmutableContract):
    maximum_tokens: int = Field(default=768, gt=0)
    minimum_useful_tokens: int = Field(default=128, gt=0)
    safety_margin_tokens: int = Field(default=512, ge=0)
    fallback_maximum_characters: int = Field(default=2400, gt=0)

    def as_budget(self) -> DocumentationContextBudget:
        return DocumentationContextBudget(
            maximum_tokens=self.maximum_tokens,
            minimum_useful_tokens=self.minimum_useful_tokens,
            safety_margin_tokens=self.safety_margin_tokens,
            fallback_maximum_characters=self.fallback_maximum_characters,
        )


class LocalDocumentationRagFeatureConfig(ImmutableContract):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1"] = "1"
    profile_key: Literal["local.documentation-rag.lexical"]
    mode: Literal["enabled"]
    provider_key: Literal["local_lexical"]
    provider_display_name: str = Field(min_length=1, max_length=80)
    active_phase: str = Field(pattern=r"^phase_[a-z0-9_]+$")
    completed_phases: tuple[str, ...] = ()
    corpus: DocumentationCorpusConfig
    limits: DocumentationLimitsConfig
    chunking: DocumentationChunkingConfig
    retrieval: DocumentationRetrievalConfig
    context: DocumentationContextConfig

    @field_validator("completed_phases")
    @classmethod
    def validate_completed_phases(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(set(value)) != len(value):
            raise ValueError("completed phase keys must be unique")
        if any(
            not phase.startswith("phase_") or "/" in phase or "\\" in phase or ".." in phase
            for phase in value
        ):
            raise ValueError("completed phase keys must be safe identifiers")
        return value


class LightningPublicDocumentationRagFeatureConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["2"] = "2"
    profile_key: Literal["external.lightning-public-corpus.documentation-rag.lexical"]
    mode: Literal["enabled"]
    provider_key: Literal["project_filesystem_lexical"]
    provider_display_name: str = Field(min_length=1, max_length=80)
    allowed_access_modes: tuple[Literal["basic_preview", "public_demo"], ...]
    allowed_platforms: tuple[Literal["linux-x86_64-container"], ...]
    corpus: ExplicitDocumentationCorpusConfig
    limits: DocumentationLimitsConfig
    chunking: DocumentationChunkingConfig
    retrieval: DocumentationRetrievalConfig
    context: DocumentationContextConfig

    @model_validator(mode="after")
    def validate_external_profile_contract(
        self,
    ) -> LightningPublicDocumentationRagFeatureConfig:
        if self.allowed_access_modes != ("basic_preview", "public_demo"):
            raise ValueError("Lightning public profile access modes must match the contract")
        if self.allowed_platforms != ("linux-x86_64-container",):
            raise ValueError("Lightning public profile platform must match the contract")
        if self.corpus.files != LIGHTNING_PUBLIC_DOCUMENTATION_FILES:
            raise ValueError("Lightning public profile corpus must match the exact allowlist")
        if self.limits.max_documents < len(LIGHTNING_PUBLIC_DOCUMENTATION_FILES):
            raise ValueError("document limit must accommodate the complete public corpus")
        return self


type DocumentationRagFeatureConfig = (
    LocalDocumentationRagFeatureConfig | LightningPublicDocumentationRagFeatureConfig
)


def _validate_project_relative_path(value: str) -> str:
    if (
        value.startswith("/")
        or "\\" in value
        or "\n" in value
        or "\r" in value
        or value.endswith("/")
        or any(part in {"", ".", ".."} for part in value.split("/"))
    ):
        raise ValueError("path must be a normalized project-relative path")
    return value
