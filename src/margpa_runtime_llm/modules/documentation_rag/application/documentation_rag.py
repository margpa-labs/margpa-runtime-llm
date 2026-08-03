"""Orchestrate deterministic source, index, retrieval, context, and citation steps."""

from __future__ import annotations

import hashlib
import threading
import time

from ..contracts import (
    CorpusManifest,
    DocumentationAugmentation,
    DocumentationContextBudget,
    DocumentationEvidence,
    DocumentationGroundingState,
    DocumentationMeasurementUnit,
    DocumentationRagRequestContext,
    DocumentationRetrievalConfig,
    DocumentationRetrievalState,
    DocumentationWarning,
    RetrievalQuery,
    RetrievalResult,
)
from ..ports import (
    CancellationCheck,
    ChunkerPort,
    CitationPort,
    ContextAssemblerPort,
    DocumentSourcePort,
    IndexStorePort,
    RetrieverPort,
)

DOCS_MISSING_MESSAGE = "docsが設置されていないため参照出来ません。"
CORPUS_EMPTY_MESSAGE = "参照可能なProject Docsがありません。"
NO_HIT_MESSAGE = "参照対象のDocsから対応する根拠を取得できませんでした。"
INDEX_FAILURE_MESSAGE = "Project Docsの検索準備を安全に完了できませんでした。"
CANCELLED_MESSAGE = "Project Docsの参照処理を停止しました。"
PROMPT_MEASUREMENT_UNAVAILABLE_MESSAGE = (
    "ModelのChat Prompt Token数を安全に計測できないため、Project Docs参照を停止しました。"
)
CONTEXT_BUDGET_INSUFFICIENT_MESSAGE = (
    "根拠を取得しましたが、Context余力不足のため回答に使用できません。"
)
SUBJECT_COVERAGE_INSUFFICIENT_MESSAGE = (
    "質問対象の一部に必要なProject Docsの根拠が揃わないため、回答を停止しました。"
)


class DocumentationRagApplicationService:
    """Build an immutable lexical snapshot lazily and expose only safe metadata."""

    def __init__(
        self,
        *,
        source: DocumentSourcePort,
        chunker: ChunkerPort,
        index_store: IndexStorePort,
        retriever: RetrieverPort,
        context_assembler: ContextAssemblerPort,
        citation: CitationPort,
        retrieval_config: DocumentationRetrievalConfig,
        context_budget: DocumentationContextBudget,
        profile_digest: str,
        max_chunks: int,
    ) -> None:
        self._source = source
        self._chunker = chunker
        self._index_store = index_store
        self._retriever = retriever
        self._context_assembler = context_assembler
        self._citation = citation
        self._retrieval_config = retrieval_config
        self._context_budget = context_budget
        self._profile_digest = profile_digest
        self._max_chunks = max_chunks
        self._build_lock = threading.Lock()

    def augment_with_context(
        self,
        query_text: str,
        request_context: DocumentationRagRequestContext,
        *,
        cancelled: CancellationCheck | None = None,
    ) -> DocumentationAugmentation:
        started = time.perf_counter()
        query_digest = _digest(query_text)
        empty_manifest_digest = _digest("")
        if (
            not request_context.prompt_token_count_exact
            or request_context.system_history_current_prompt_tokens is None
        ):
            unavailable_budget = self._context_budget.model_copy(update={"maximum_tokens": 0})
            return self._unavailable(
                query_digest=query_digest,
                manifest_digest=empty_manifest_digest,
                request_context=request_context,
                context_budget=unavailable_budget,
                warning=DocumentationWarning(
                    code="documentation_prompt_measurement_unavailable",
                    message=PROMPT_MEASUREMENT_UNAVAILABLE_MESSAGE,
                ),
                started=started,
            )
        context_budget = self._resolve_context_budget(request_context)
        if _cancelled(cancelled):
            return self._unavailable(
                query_digest=query_digest,
                manifest_digest=empty_manifest_digest,
                request_context=request_context,
                context_budget=context_budget,
                warning=DocumentationWarning(
                    code="documentation_rag_cancelled",
                    message=CANCELLED_MESSAGE,
                ),
                started=started,
            )

        try:
            manifest = self._source.load_manifest()
        except Exception:
            return self._unavailable(
                query_digest=query_digest,
                manifest_digest=empty_manifest_digest,
                request_context=request_context,
                context_budget=context_budget,
                warning=DocumentationWarning(
                    code="documentation_index_build_failed",
                    message=INDEX_FAILURE_MESSAGE,
                ),
                started=started,
            )

        if not manifest.docs_present:
            return self._unavailable_from_manifest(
                query_digest=query_digest,
                manifest=manifest,
                request_context=request_context,
                context_budget=context_budget,
                warning=DocumentationWarning(
                    code="documentation_docs_missing",
                    message=DOCS_MISSING_MESSAGE,
                ),
                started=started,
            )
        if not manifest.entries:
            return self._unavailable_from_manifest(
                query_digest=query_digest,
                manifest=manifest,
                request_context=request_context,
                context_budget=context_budget,
                warning=DocumentationWarning(
                    code="documentation_corpus_empty",
                    message=CORPUS_EMPTY_MESSAGE,
                ),
                started=started,
            )
        if _cancelled(cancelled):
            return self._unavailable_from_manifest(
                query_digest=query_digest,
                manifest=manifest,
                request_context=request_context,
                context_budget=context_budget,
                warning=DocumentationWarning(
                    code="documentation_rag_cancelled",
                    message=CANCELLED_MESSAGE,
                ),
                started=started,
            )

        cache_key = self._cache_key(manifest)
        index = self._index_store.get(cache_key)
        index_rebuilt = False
        warnings = list(manifest.warnings)
        loaded_document_count = 0
        if index is None:
            try:
                with self._build_lock:
                    index = self._index_store.get(cache_key)
                    if index is None:
                        documents, source_warnings = self._source.load_documents(
                            manifest,
                            cancelled=cancelled,
                        )
                        warnings.extend(
                            warning
                            for warning in source_warnings
                            if isinstance(warning, DocumentationWarning)
                        )
                        loaded_document_count = len(documents)
                        if _cancelled(cancelled):
                            return self._unavailable_from_manifest(
                                query_digest=query_digest,
                                manifest=manifest,
                                request_context=request_context,
                                context_budget=context_budget,
                                warning=DocumentationWarning(
                                    code="documentation_rag_cancelled",
                                    message=CANCELLED_MESSAGE,
                                ),
                                started=started,
                                warnings=tuple(warnings),
                                document_count=len(documents),
                            )
                        if not documents:
                            return self._unavailable_from_manifest(
                                query_digest=query_digest,
                                manifest=manifest,
                                request_context=request_context,
                                context_budget=context_budget,
                                warning=DocumentationWarning(
                                    code="documentation_corpus_empty",
                                    message=CORPUS_EMPTY_MESSAGE,
                                ),
                                started=started,
                                warnings=tuple(warnings),
                                document_count=0,
                            )
                        chunks = tuple(
                            chunk
                            for document in documents
                            for chunk in self._chunker.chunk(document)
                        )
                        if not chunks:
                            return self._unavailable_from_manifest(
                                query_digest=query_digest,
                                manifest=manifest,
                                request_context=request_context,
                                context_budget=context_budget,
                                warning=DocumentationWarning(
                                    code="documentation_corpus_empty",
                                    message=CORPUS_EMPTY_MESSAGE,
                                ),
                                started=started,
                                warnings=tuple(warnings),
                                document_count=0,
                            )
                        if len(chunks) > self._max_chunks:
                            return self._unavailable_from_manifest(
                                query_digest=query_digest,
                                manifest=manifest,
                                request_context=request_context,
                                context_budget=context_budget,
                                warning=DocumentationWarning(
                                    code="documentation_corpus_limit_exceeded",
                                    message="Project DocsのChunk上限を超えました。",
                                ),
                                started=started,
                                warnings=tuple(warnings),
                                document_count=len(documents),
                            )
                        index = self._retriever.build(
                            cache_key=cache_key,
                            corpus_manifest_digest=manifest.corpus_manifest_digest,
                            chunker_key=self._chunker.key,
                            chunker_version=self._chunker.version,
                            chunks=chunks,
                        )
                        self._index_store.replace(index)
                        index_rebuilt = True
            except Exception:
                return self._unavailable_from_manifest(
                    query_digest=query_digest,
                    manifest=manifest,
                    request_context=request_context,
                    context_budget=context_budget,
                    warning=DocumentationWarning(
                        code="documentation_index_build_failed",
                        message=INDEX_FAILURE_MESSAGE,
                    ),
                    started=started,
                    warnings=tuple(warnings),
                    document_count=loaded_document_count,
                )

        query = RetrievalQuery(
            query_text=query_text,
            query_digest=query_digest,
            top_k=self._retrieval_config.top_k,
            minimum_score=self._retrieval_config.minimum_score,
            max_chunks_per_document=self._retrieval_config.max_chunks_per_document,
        )
        retrieval = self._retriever.retrieve(index, query)
        if not retrieval.selected:
            warnings.append(
                DocumentationWarning(
                    code="documentation_no_hit",
                    message=NO_HIT_MESSAGE,
                )
            )
            return self._enabled(
                query_digest=query_digest,
                manifest=manifest,
                request_context=request_context,
                retrieval=retrieval,
                warnings=tuple(warnings),
                document_count=index.document_count,
                context_budget=context_budget,
                index_rebuilt=index_rebuilt,
                started=started,
            )

        context = self._context_assembler.assemble(retrieval, context_budget)
        citations = self._citation.build(retrieval, context)
        assembled_chunk_ids = {block.chunk_id for block in context.blocks}
        assembled_covered_subject_count = sum(
            any(chunk_id in assembled_chunk_ids for chunk_id in trace.retrieved_chunk_ids)
            for trace in retrieval.subject_coverage
        )
        assembled_uncovered_subject_count = (
            retrieval.identifier_subject_count - assembled_covered_subject_count
        )
        if context.token_counter_fallback_used:
            warnings.append(
                DocumentationWarning(
                    code="documentation_token_counter_unavailable",
                    message="Model Token Counterを利用できないため文字数上限を使用しました。",
                )
            )
        if not context.blocks:
            warnings.append(
                DocumentationWarning(
                    code="documentation_context_budget_insufficient",
                    message=CONTEXT_BUDGET_INSUFFICIENT_MESSAGE,
                )
            )
        elif assembled_uncovered_subject_count:
            warnings.append(
                DocumentationWarning(
                    code="documentation_subject_coverage_insufficient",
                    message=SUBJECT_COVERAGE_INSUFFICIENT_MESSAGE,
                )
            )
        duration_ms = _duration_ms(started)
        if not context.blocks:
            grounding_state = DocumentationGroundingState.CONTEXT_INSUFFICIENT
        elif assembled_uncovered_subject_count:
            grounding_state = DocumentationGroundingState.SUBJECT_COVERAGE_INSUFFICIENT
        else:
            grounding_state = DocumentationGroundingState.GROUNDED_READY
        generation_allowed = grounding_state is DocumentationGroundingState.GROUNDED_READY
        evidence = DocumentationEvidence(
            query_digest=query_digest,
            corpus_manifest_digest=manifest.corpus_manifest_digest,
            retriever_key=self._retriever.key,
            retriever_version=self._retriever.version,
            selected_chunk_ids=tuple(item.chunk.chunk_id for item in retrieval.selected),
            selected_document_digests=tuple(
                item.chunk.document_sha512 for item in retrieval.selected
            ),
            selected_scores=tuple(item.score for item in retrieval.selected),
            base_prompt_used=request_context.system_history_current_prompt_tokens,
            base_prompt_unit=request_context.prompt_measurement_unit,
            base_prompt_exact=request_context.prompt_token_count_exact,
            context_budget=context_budget.maximum_tokens,
            context_budget_unit=DocumentationMeasurementUnit.TOKENS,
            context_used=context.context_used,
            context_measurement_unit=context.measurement_unit,
            context_measurement_limit=context.measurement_limit,
            context_token_budget_used=context.token_budget_used,
            token_counter_fallback_used=context.token_counter_fallback_used,
            retrieved_chunk_count=len(retrieval.selected),
            assembled_block_count=len(context.blocks),
            identifier_subject_count=retrieval.identifier_subject_count,
            retrieval_covered_subject_count=retrieval.covered_subject_count,
            retrieval_uncovered_subject_count=retrieval.uncovered_subject_count,
            covered_subject_count=assembled_covered_subject_count,
            uncovered_subject_count=assembled_uncovered_subject_count,
            grounding_state=grounding_state,
            generation_allowed=generation_allowed,
            truncation_state=context.truncated,
            index_rebuilt=index_rebuilt,
            retrieval_duration_ms=duration_ms,
        )
        return DocumentationAugmentation(
            state=DocumentationRetrievalState.ENABLED,
            should_generate=generation_allowed,
            reference_message=(context.reference_message if generation_allowed else None),
            citations=citations,
            evidence=evidence,
            warnings=tuple(warnings),
            document_count=index.document_count,
            selected_chunk_count=len(citations),
            index_rebuilt=index_rebuilt,
            duration_ms=duration_ms,
        )

    def _cache_key(self, manifest: CorpusManifest) -> str:
        raw = "\n".join(
            (
                manifest.corpus_manifest_digest,
                self._profile_digest,
                self._source.schema_version,
                self._chunker.key,
                self._chunker.version,
                self._retriever.tokenizer_key,
                self._retriever.tokenizer_version,
                self._retriever.key,
                self._retriever.version,
                self._context_assembler.key,
                self._context_assembler.version,
                self._citation.schema_version,
            )
        )
        return _digest(raw)

    def _enabled(
        self,
        *,
        query_digest: str,
        manifest: CorpusManifest,
        request_context: DocumentationRagRequestContext,
        retrieval: RetrievalResult,
        warnings: tuple[DocumentationWarning, ...],
        document_count: int,
        context_budget: DocumentationContextBudget,
        index_rebuilt: bool,
        started: float,
    ) -> DocumentationAugmentation:
        duration_ms = _duration_ms(started)
        return DocumentationAugmentation(
            state=DocumentationRetrievalState.ENABLED,
            should_generate=True,
            evidence=DocumentationEvidence(
                query_digest=query_digest,
                corpus_manifest_digest=manifest.corpus_manifest_digest,
                retriever_key=self._retriever.key,
                retriever_version=self._retriever.version,
                base_prompt_used=request_context.system_history_current_prompt_tokens,
                base_prompt_unit=request_context.prompt_measurement_unit,
                base_prompt_exact=request_context.prompt_token_count_exact,
                context_budget=context_budget.maximum_tokens,
                context_budget_unit=DocumentationMeasurementUnit.TOKENS,
                context_used=0,
                context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
                context_measurement_limit=context_budget.maximum_tokens,
                context_token_budget_used=True,
                retrieved_chunk_count=0,
                assembled_block_count=0,
                identifier_subject_count=retrieval.identifier_subject_count,
                retrieval_covered_subject_count=retrieval.covered_subject_count,
                retrieval_uncovered_subject_count=retrieval.uncovered_subject_count,
                covered_subject_count=0,
                uncovered_subject_count=retrieval.identifier_subject_count,
                grounding_state=DocumentationGroundingState.NO_HIT,
                generation_allowed=True,
                index_rebuilt=index_rebuilt,
                retrieval_duration_ms=duration_ms,
            ),
            warnings=warnings,
            document_count=document_count,
            selected_chunk_count=0,
            index_rebuilt=index_rebuilt,
            duration_ms=duration_ms,
        )

    def _unavailable_from_manifest(
        self,
        *,
        query_digest: str,
        manifest: CorpusManifest,
        request_context: DocumentationRagRequestContext,
        context_budget: DocumentationContextBudget,
        warning: DocumentationWarning,
        started: float,
        warnings: tuple[DocumentationWarning, ...] = (),
        document_count: int | None = None,
    ) -> DocumentationAugmentation:
        combined_warnings = list(manifest.warnings)
        combined_warnings.extend(
            candidate for candidate in warnings if candidate not in combined_warnings
        )
        return self._unavailable(
            query_digest=query_digest,
            manifest_digest=manifest.corpus_manifest_digest,
            request_context=request_context,
            context_budget=context_budget,
            warning=warning,
            started=started,
            warnings=tuple(combined_warnings),
            document_count=(len(manifest.entries) if document_count is None else document_count),
        )

    def _unavailable(
        self,
        *,
        query_digest: str,
        manifest_digest: str,
        request_context: DocumentationRagRequestContext,
        context_budget: DocumentationContextBudget,
        warning: DocumentationWarning,
        started: float,
        warnings: tuple[DocumentationWarning, ...] = (),
        document_count: int = 0,
    ) -> DocumentationAugmentation:
        duration_ms = _duration_ms(started)
        return DocumentationAugmentation(
            state=DocumentationRetrievalState.UNAVAILABLE,
            should_generate=False,
            evidence=DocumentationEvidence(
                query_digest=query_digest,
                corpus_manifest_digest=manifest_digest,
                retriever_key=self._retriever.key,
                retriever_version=self._retriever.version,
                base_prompt_used=request_context.system_history_current_prompt_tokens,
                base_prompt_unit=request_context.prompt_measurement_unit,
                base_prompt_exact=request_context.prompt_token_count_exact,
                context_budget=context_budget.maximum_tokens,
                context_budget_unit=DocumentationMeasurementUnit.TOKENS,
                context_used=0,
                context_measurement_unit=DocumentationMeasurementUnit.TOKENS,
                context_measurement_limit=context_budget.maximum_tokens,
                context_token_budget_used=True,
                retrieved_chunk_count=0,
                assembled_block_count=0,
                identifier_subject_count=0,
                retrieval_covered_subject_count=0,
                retrieval_uncovered_subject_count=0,
                covered_subject_count=0,
                uncovered_subject_count=0,
                grounding_state=DocumentationGroundingState.UNAVAILABLE,
                generation_allowed=False,
                retrieval_duration_ms=duration_ms,
            ),
            warnings=(*warnings, warning),
            document_count=document_count,
            selected_chunk_count=0,
            duration_ms=duration_ms,
        )

    def _resolve_context_budget(
        self,
        request_context: DocumentationRagRequestContext,
    ) -> DocumentationContextBudget:
        assert request_context.system_history_current_prompt_tokens is not None
        request_available_tokens = max(
            0,
            request_context.effective_context_size
            - request_context.requested_max_new_tokens
            - request_context.system_history_current_prompt_tokens
            - self._context_budget.safety_margin_tokens,
        )
        effective_tokens = min(
            self._context_budget.maximum_tokens,
            request_available_tokens,
        )
        return self._context_budget.model_copy(
            update={
                "maximum_tokens": effective_tokens,
            }
        )


def _digest(value: str) -> str:
    return hashlib.sha512(value.encode("utf-8")).hexdigest()


def _duration_ms(started: float) -> float:
    return max(0.0, (time.perf_counter() - started) * 1000.0)


def _cancelled(check: CancellationCheck | None) -> bool:
    return check is not None and check()
