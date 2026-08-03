"""Deterministic field-weighted BM25-style lexical retrieval."""

from __future__ import annotations

import hashlib
import math
import time
from collections import Counter
from collections.abc import Iterable, Mapping

from margpa_runtime_llm.modules.documentation_rag.contracts import (
    DocumentationChunk,
    DocumentationRetrievalConfig,
    RetrievalQuery,
    RetrievalResult,
    RetrievalScoreComponents,
    RetrievedChunk,
    SubjectCoverageTrace,
)
from margpa_runtime_llm.modules.documentation_rag.ports import DocumentationIndex

from .in_memory_lexical_index import IndexedChunk, LexicalIndexSnapshot
from .lexical_tokenizer import JapaneseAwareLexicalTokenizer
from .query_analyzer import GenericNaturalLanguageQueryAnalyzer


class Bm25DocumentationRetriever:
    key = "field_weighted_bm25"
    version = "5"

    def __init__(
        self,
        *,
        tokenizer: JapaneseAwareLexicalTokenizer,
        config: DocumentationRetrievalConfig,
        query_analyzer: GenericNaturalLanguageQueryAnalyzer | None = None,
    ) -> None:
        self._tokenizer = tokenizer
        self._config = config
        self._query_analyzer = query_analyzer or GenericNaturalLanguageQueryAnalyzer(tokenizer)

    @property
    def tokenizer_key(self) -> str:
        return self._tokenizer.key

    @property
    def tokenizer_version(self) -> str:
        return self._tokenizer.version

    def build(
        self,
        *,
        cache_key: str,
        corpus_manifest_digest: str,
        chunker_key: str,
        chunker_version: str,
        chunks: tuple[DocumentationChunk, ...],
    ) -> DocumentationIndex:
        indexed: list[IndexedChunk] = []
        body_df: Counter[str] = Counter()
        heading_df: Counter[str] = Counter()
        path_df: Counter[str] = Counter()
        for chunk in chunks:
            body_tokens = self._tokenizer.tokenize(chunk.content)
            heading_tokens = self._tokenizer.tokenize(chunk.heading_breadcrumb)
            path_tokens = self._tokenizer.tokenize(chunk.project_relative_path)
            body_terms = Counter(body_tokens)
            heading_terms = Counter(heading_tokens)
            path_terms = Counter(path_tokens)
            body_df.update(body_terms.keys())
            heading_df.update(heading_terms.keys())
            path_df.update(path_terms.keys())
            indexed.append(
                IndexedChunk(
                    chunk=chunk,
                    normalized_body=self._tokenizer.normalize(chunk.content),
                    normalized_heading=self._tokenizer.normalize(chunk.heading_breadcrumb),
                    normalized_path=self._tokenizer.normalize(chunk.project_relative_path),
                    body_terms=tuple(sorted(body_terms.items())),
                    heading_terms=tuple(sorted(heading_terms.items())),
                    path_terms=tuple(sorted(path_terms.items())),
                    body_length=len(body_tokens),
                    heading_length=len(heading_tokens),
                    path_length=len(path_tokens),
                )
            )
        return LexicalIndexSnapshot(
            index_id=cache_key,
            cache_key=cache_key,
            corpus_manifest_digest=corpus_manifest_digest,
            chunker_key=chunker_key,
            chunker_version=chunker_version,
            tokenizer_key=self.tokenizer_key,
            tokenizer_version=self.tokenizer_version,
            retriever_key=self.key,
            retriever_version=self.version,
            document_count=len({item.chunk.source_id for item in indexed}),
            chunk_count=len(indexed),
            built_at_monotonic=time.monotonic(),
            chunks=tuple(indexed),
            body_document_frequency=tuple(sorted(body_df.items())),
            heading_document_frequency=tuple(sorted(heading_df.items())),
            path_document_frequency=tuple(sorted(path_df.items())),
            average_body_length=_average(item.body_length for item in indexed),
            average_heading_length=_average(item.heading_length for item in indexed),
            average_path_length=_average(item.path_length for item in indexed),
        )

    def retrieve(
        self,
        index: DocumentationIndex,
        query: RetrievalQuery,
    ) -> RetrievalResult:
        if not isinstance(index, LexicalIndexSnapshot):
            raise TypeError("the lexical retriever requires a lexical index snapshot")
        analysis = self._query_analyzer.analyze(query.query_text)
        if not analysis.weighted_terms:
            return RetrievalResult(query_digest=query.query_digest)
        query_terms = dict(analysis.weighted_terms)
        normalized_query = analysis.normalized_query
        body_df = dict(index.body_document_frequency)
        heading_df = dict(index.heading_document_frequency)
        path_df = dict(index.path_document_frequency)
        population = len(index.chunks)
        scored: list[tuple[float, RetrievalScoreComponents, IndexedChunk]] = []
        for item in index.chunks:
            body = (
                self._field_score(
                    query_terms,
                    dict(item.body_terms),
                    body_df,
                    item.body_length,
                    index.average_body_length,
                    population,
                )
                * self._config.body_weight
            )
            heading = (
                self._field_score(
                    query_terms,
                    dict(item.heading_terms),
                    heading_df,
                    item.heading_length,
                    index.average_heading_length,
                    population,
                )
                * self._config.heading_weight
            )
            path = (
                self._field_score(
                    query_terms,
                    dict(item.path_terms),
                    path_df,
                    item.path_length,
                    index.average_path_length,
                    population,
                )
                * self._config.path_weight
            )
            exact = (
                self._config.exact_phrase_bonus
                if normalized_query
                and (
                    normalized_query in item.normalized_body
                    or normalized_query in item.normalized_heading
                    or normalized_query in item.normalized_path
                )
                else 0.0
            )
            lexical = body + heading + path + exact
            if lexical <= 0.0:
                continue
            priority = (
                (3 - int(item.chunk.corpus_priority)) / 3 * self._config.corpus_priority_weight
            )
            components = RetrievalScoreComponents(
                body=body,
                heading=heading,
                path=path,
                exact_phrase=exact,
                corpus_priority=priority,
            )
            score = components.total
            if score >= query.minimum_score:
                scored.append((score, components, item))

        scored.sort(
            key=lambda value: (
                -value[0],
                int(value[2].chunk.corpus_priority),
                value[2].chunk.project_relative_path,
                value[2].chunk.heading_breadcrumb,
                value[2].chunk.ordinal,
                value[2].chunk.chunk_id,
            )
        )
        selected_rows: list[tuple[float, RetrievalScoreComponents, IndexedChunk]] = []
        selected_chunk_ids: set[str] = set()
        per_document: Counter[str] = Counter()
        for subject in analysis.subject_identifiers:
            candidate = self._coverage_candidate(
                subject,
                analysis.subject_identifiers,
                scored,
                selected_chunk_ids,
                per_document,
                query.max_chunks_per_document,
            )
            if candidate is None:
                continue
            score, components, item = candidate
            if item.chunk.chunk_id in selected_chunk_ids:
                continue
            if len(selected_rows) >= query.top_k:
                continue
            selected_rows.append((score, components, item))
            selected_chunk_ids.add(item.chunk.chunk_id)
            per_document[item.chunk.project_relative_path] += 1

        for score, components, item in scored:
            if len(selected_rows) >= query.top_k:
                break
            if item.chunk.chunk_id in selected_chunk_ids:
                continue
            relative = item.chunk.project_relative_path
            if per_document[relative] >= query.max_chunks_per_document:
                continue
            selected_rows.append((score, components, item))
            selected_chunk_ids.add(item.chunk.chunk_id)
            per_document[relative] += 1

        selected = tuple(
            RetrievedChunk(
                chunk=item.chunk,
                score=score,
                rank=index,
                score_components=components,
            )
            for index, (score, components, item) in enumerate(selected_rows, start=1)
        )
        subject_coverage = tuple(
            SubjectCoverageTrace(
                subject_digest=hashlib.sha512(subject.encode("utf-8")).hexdigest(),
                retrieved_chunk_ids=tuple(
                    item.chunk.chunk_id
                    for _, _, item in selected_rows
                    if self._coverage_tier(subject, analysis.subject_identifiers, item) is not None
                ),
            )
            for subject in analysis.subject_identifiers
        )
        subject_count = len(analysis.subject_identifiers)
        covered_subject_count = sum(bool(trace.retrieved_chunk_ids) for trace in subject_coverage)
        return RetrievalResult(
            query_digest=query.query_digest,
            selected=selected,
            subject_coverage=subject_coverage,
            identifier_subject_count=subject_count,
            covered_subject_count=covered_subject_count,
            uncovered_subject_count=subject_count - covered_subject_count,
        )

    @staticmethod
    def _coverage_candidate(
        subject: str,
        subjects: tuple[str, ...],
        scored: list[tuple[float, RetrievalScoreComponents, IndexedChunk]],
        selected_chunk_ids: set[str],
        per_document: Counter[str],
        max_chunks_per_document: int,
    ) -> tuple[float, RetrievalScoreComponents, IndexedChunk] | None:
        candidates: list[tuple[int, int, tuple[float, RetrievalScoreComponents, IndexedChunk]]] = []
        for global_rank, row in enumerate(scored):
            item = row[2]
            tier = Bm25DocumentationRetriever._coverage_tier(subject, subjects, item)
            if tier is None:
                continue
            if (
                item.chunk.chunk_id not in selected_chunk_ids
                and per_document[item.chunk.project_relative_path] >= max_chunks_per_document
            ):
                continue
            candidates.append((tier, global_rank, row))
        if not candidates:
            return None
        candidates.sort(key=lambda candidate: (candidate[0], candidate[1]))
        return candidates[0][2]

    @staticmethod
    def _coverage_tier(
        subject: str,
        subjects: tuple[str, ...],
        item: IndexedChunk,
    ) -> int | None:
        heading_terms = dict(item.heading_terms)
        path_terms = dict(item.path_terms)
        body_terms = dict(item.body_terms)
        if subject in heading_terms:
            return 0
        if subject in path_terms:
            return 1
        if subject in body_terms and sum(candidate in body_terms for candidate in subjects) == 1:
            return 2
        return None

    def _field_score(
        self,
        query_terms: Mapping[str, float],
        document_terms: dict[str, int],
        document_frequency: dict[str, int],
        document_length: int,
        average_length: float,
        population: int,
    ) -> float:
        if not document_terms or population == 0:
            return 0.0
        score = 0.0
        normalized_length = document_length / average_length if average_length else 0.0
        for token, query_frequency in query_terms.items():
            term_frequency = document_terms.get(token, 0)
            if not term_frequency:
                continue
            frequency = document_frequency.get(token, 0)
            inverse_frequency = math.log(1.0 + (population - frequency + 0.5) / (frequency + 0.5))
            denominator = term_frequency + self._config.bm25_k1 * (
                1.0 - self._config.bm25_b + self._config.bm25_b * normalized_length
            )
            score += (
                query_frequency
                * inverse_frequency
                * term_frequency
                * (self._config.bm25_k1 + 1.0)
                / denominator
            )
        return score


def _average(values: Iterable[int]) -> float:
    materialized = tuple(values)
    return sum(materialized) / len(materialized) if materialized else 0.0
