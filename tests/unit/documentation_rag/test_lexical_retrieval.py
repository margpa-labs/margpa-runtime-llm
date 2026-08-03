"""Japanese, identifier, field weight, diversity, and tie-break retrieval tests."""

from __future__ import annotations

import hashlib
import inspect

import pytest

from margpa_runtime_llm.adapters.documentation_rag.bm25_retriever import (
    Bm25DocumentationRetriever,
)
from margpa_runtime_llm.adapters.documentation_rag.in_memory_lexical_index import (
    LexicalIndexSnapshot,
)
from margpa_runtime_llm.adapters.documentation_rag.lexical_tokenizer import (
    JapaneseAwareLexicalTokenizer,
)
from margpa_runtime_llm.adapters.documentation_rag.query_analyzer import (
    GenericNaturalLanguageQueryAnalyzer,
)
from margpa_runtime_llm.modules.documentation_rag.contracts import (
    CorpusPriority,
    DocumentationChunk,
    DocumentationRetrievalConfig,
    RetrievalQuery,
)


def chunk(
    *,
    path: str,
    heading: str,
    content: str,
    ordinal: int = 0,
    priority: CorpusPriority = CorpusPriority.CURRENT,
) -> DocumentationChunk:
    document_digest = hashlib.sha512(path.encode()).hexdigest()
    content_digest = hashlib.sha512(content.encode()).hexdigest()
    return DocumentationChunk(
        chunk_id=hashlib.sha512(
            f"{path}\0{heading}\0{ordinal}\0{content_digest}".encode()
        ).hexdigest(),
        source_id=hashlib.sha512(path.encode()).hexdigest(),
        project_relative_path=path,
        corpus_priority=priority,
        heading_breadcrumb=heading,
        ordinal=ordinal,
        content=content,
        content_sha512=content_digest,
        document_sha512=document_digest,
        character_count=len(content),
    )


def query(text: str, *, top_k: int = 4, per_document: int = 2) -> RetrievalQuery:
    return RetrievalQuery(
        query_text=text,
        query_digest=hashlib.sha512(text.encode()).hexdigest(),
        top_k=top_k,
        minimum_score=0.1,
        max_chunks_per_document=per_document,
    )


def retriever() -> Bm25DocumentationRetriever:
    return Bm25DocumentationRetriever(
        tokenizer=JapaneseAwareLexicalTokenizer(),
        config=DocumentationRetrievalConfig(),
    )


def test_tokenizer_handles_nfkc_japanese_ngrams_and_identifiers() -> None:
    tokenizer = JapaneseAwareLexicalTokenizer()
    tokens = tokenizer.tokenize("ＡＲＧＤ 設計統治 src/My_Module.py")  # noqa: RUF001

    assert "argd" in tokens
    assert "設計" in tokens
    assert "設計統" in tokens
    assert "src/my_module.py" in tokens
    assert "my" in tokens


def test_query_analyzer_prioritizes_generic_identifiers_without_dropping_context() -> None:
    analyzer = GenericNaturalLanguageQueryAnalyzer(JapaneseAwareLexicalTokenizer())

    analysis = analyzer.analyze("Sample_IDについて詳しく説明してください")
    weights = dict(analysis.weighted_terms)

    assert analysis.identifier_tokens == ("sample_id", "sample", "id")
    assert analysis.subject_identifiers == ("sample_id",)
    assert weights["sample_id"] > weights["説明"]
    assert weights["説明"] > 0
    assert analyzer.analyze("設計統治").identifier_tokens == ()


def test_query_analyzer_separates_english_prose_from_high_signal_subjects() -> None:
    analyzer = GenericNaturalLanguageQueryAnalyzer(JapaneseAwareLexicalTokenizer())

    analysis = analyzer.analyze("What are EASA, DLAGSA, and OCILNS. Explain briefly.")

    assert {"what", "are", "and", "explain", "briefly"} <= set(analysis.identifier_tokens)
    assert analysis.subject_identifiers == ("easa", "dlagsa", "ocilns")


def test_query_analyzer_recognizes_unknown_generic_identifier_shapes() -> None:
    analyzer = GenericNaturalLanguageQueryAnalyzer(JapaneseAwareLexicalTokenizer())

    analysis = analyzer.analyze("Compare ZXQ, NVRTA, and PLMKS with model_v2 and AlphaNode")

    assert analysis.subject_identifiers == (
        "zxq",
        "nvrta",
        "plmks",
        "model_v2",
        "alphanode",
    )


def test_production_query_analysis_has_no_project_subject_allowlist() -> None:
    source = "\n".join(
        (
            inspect.getsource(GenericNaturalLanguageQueryAnalyzer),
            inspect.getsource(Bm25DocumentationRetriever),
        )
    ).casefold()

    for project_subject in (
        "roadmap",
        "argd",
        "dagd",
        "easa",
        "dlagsa",
        "ocilns",
    ):
        assert project_subject not in source


def test_heading_path_phrase_and_corpus_priority_affect_ranking() -> None:
    values = (
        chunk(
            path="docs/project/current/architecture_ja.md",
            heading="Runtime Governance",
            content="ARGD compiler and deterministic governance.",
        ),
        chunk(
            path="docs/public/overview_ja.md",
            heading="Overview",
            content="ARGD is mentioned once.",
            priority=CorpusPriority.PUBLIC,
        ),
        chunk(
            path="docs/project/current/other_ja.md",
            heading="Other",
            content="Unrelated content.",
        ),
    )
    engine = retriever()
    index = engine.build(
        cache_key="cache",
        corpus_manifest_digest="a" * 128,
        chunker_key="test_chunker",
        chunker_version="1",
        chunks=values,
    )

    result = engine.retrieve(index, query("Runtime Governance"))

    assert result.selected[0].chunk.project_relative_path.endswith("architecture_ja.md")
    assert result.selected[0].score_components.heading > 0
    assert result.selected[0].score_components.exact_phrase > 0


def test_tie_break_document_diversity_and_no_hit_are_deterministic() -> None:
    values = (
        chunk(path="docs/project/current/b_ja.md", heading="Same", content="共有用語"),
        chunk(
            path="docs/project/current/a_ja.md",
            heading="Same",
            content="共有用語",
            ordinal=0,
        ),
        chunk(
            path="docs/project/current/a_ja.md",
            heading="Same",
            content="共有用語",
            ordinal=1,
        ),
    )
    engine = retriever()
    index = engine.build(
        cache_key="cache",
        corpus_manifest_digest="a" * 128,
        chunker_key="test_chunker",
        chunker_version="1",
        chunks=values,
    )

    result = engine.retrieve(index, query("共有用語", top_k=3, per_document=1))
    repeated = engine.retrieve(index, query("共有用語", top_k=3, per_document=1))

    assert result == repeated
    assert [item.chunk.project_relative_path for item in result.selected] == [
        "docs/project/current/a_ja.md",
        "docs/project/current/b_ja.md",
    ]
    assert engine.retrieve(index, query("完全に無関係")).selected == ()


def test_document_frequency_counts_each_repeated_english_term_once_per_chunk() -> None:
    values = (
        chunk(
            path="docs/project/current/repeated_ja.md",
            heading="Repeated",
            content="test " * 20,
        ),
        chunk(
            path="docs/project/current/other_ja.md",
            heading="Other",
            content="unrelated evidence",
        ),
    )
    engine = retriever()
    index = engine.build(
        cache_key="cache",
        corpus_manifest_digest="a" * 128,
        chunker_key="test_chunker",
        chunker_version="1",
        chunks=values,
    )

    assert isinstance(index, LexicalIndexSnapshot)
    assert dict(index.body_document_frequency)["test"] == 1
    assert all(frequency <= len(values) for _, frequency in index.body_document_frequency)
    assert engine.retrieve(index, query("test")).selected[0].chunk == values[0]


def test_document_frequency_bounds_repeated_japanese_ngrams_and_retrieves() -> None:
    values = (
        chunk(
            path="docs/project/current/governance_ja.md",
            heading="設計統治",
            content="設計統治" * 20,
        ),
        chunk(
            path="docs/project/current/other_ja.md",
            heading="別資料",
            content="無関係な説明",
        ),
    )
    engine = retriever()
    index = engine.build(
        cache_key="cache",
        corpus_manifest_digest="a" * 128,
        chunker_key="test_chunker",
        chunker_version="1",
        chunks=values,
    )

    assert isinstance(index, LexicalIndexSnapshot)
    for frequencies in (
        index.body_document_frequency,
        index.heading_document_frequency,
        index.path_document_frequency,
    ):
        assert all(frequency <= len(values) for _, frequency in frequencies)
    assert engine.retrieve(index, query("設計統治")).selected[0].chunk == values[0]


@pytest.mark.parametrize(
    ("natural_query", "identifier_reference", "canonical"),
    [
        (
            "roadmapの現在の進捗を教えてください",
            "roadmap",
            chunk(
                path="docs/public/roadmap_ja.md",
                heading="Roadmap > 現在地と進捗",
                content="Roadmapの現在地はPhase 1-exで、受入Gateごとに進捗を管理します。",
                priority=CorpusPriority.PUBLIC,
            ),
        ),
        (
            "ARGDとDAGDについて説明してください",
            "ARGD DAGD",
            chunk(
                path="docs/project/current/governance/runtime_governance_specification_ja.md",
                heading="ARGD/DAGD",
                content="ARGDはPremise、Context、矛盾、情報不足とRepairを扱い、"
                "DAGDはPolicy Goal、Constraint、Capability、Audit-to-Actionを扱います。",
            ),
        ),
        (
            "EASAとは何ですか?",
            "EASA",
            chunk(
                path="docs/public/concept_ja.md",
                heading="External R&D Hook > EASA",
                content="EASAは内部安全傾向、周辺安全制御、入力文脈、生成過程から現れる"
                "Composite Safety Behaviorを扱い、単一物理Layerと断定しません。",
                priority=CorpusPriority.PUBLIC,
            ),
        ),
        (
            "DLAGSAとは何ですか?",
            "DLAGSA",
            chunk(
                path="docs/public/concept_ja.md",
                heading="External R&D Hook > DLAGSA",
                content="DLAGSAは複数の判断・実行・検証主体間の責任、委譲、例外、改竄耐性付き証跡、"
                "全体整合および異常時の安全側制御を扱います。",
                priority=CorpusPriority.PUBLIC,
            ),
        ),
        (
            "OCILNSとは何ですか?",
            "OCILNS",
            chunk(
                path="docs/public/concept_ja.md",
                heading="External R&D Hook > OCILNS",
                content="OCILNSは人、AI、Tool、外部System間の認知的対話を検証、参照、継承、監査できる"
                "改竄耐性付き証跡単位として扱う台帳網です。",
                priority=CorpusPriority.PUBLIC,
            ),
        ),
        (
            "システムArchitectureを説明してください",
            "Architecture",
            chunk(
                path="docs/project/current/architecture/system_architecture_ja.md",
                heading="System Architecture",
                content=(
                    "System ArchitectureはModular MonolithとPort/Adapterの依存方向を定義します。"
                ),
            ),
        ),
        (
            "Nazuna Research Governance LLMとは何ですか?",
            "Nazuna Research Governance LLM",
            chunk(
                path="docs/public/overview_ja.md",
                heading="Project Overview",
                content="Nazuna Research Governance LLMはLocal LLMを統治するModular Runtimeです。",
                priority=CorpusPriority.PUBLIC,
            ),
        ),
    ],
)
def test_natural_query_ranks_canonical_subject_first_in_noisy_corpus(
    natural_query: str,
    identifier_reference: str,
    canonical: DocumentationChunk,
) -> None:
    noise = (
        "現在の進捗を教えてください。"
        "この項目について詳しく説明してください。"
        "概要と現在の状況は何ですか。"
    )
    distractors = tuple(
        chunk(
            path=f"docs/project/current/noise/noise_{index}_ja.md",
            heading=f"共通説明 {index}",
            content=f"{identifier_reference}は別項目から参照されます。{noise * 4}",
        )
        for index in range(8)
    )
    engine = retriever()
    index = engine.build(
        cache_key="natural-query-cache",
        corpus_manifest_digest="a" * 128,
        chunker_key="test_chunker",
        chunker_version="1",
        chunks=(canonical, *distractors),
    )

    result = engine.retrieve(index, query(natural_query))
    repeated = engine.retrieve(index, query(natural_query))

    assert result == repeated
    assert result.selected[0].chunk == canonical
    assert len(result.selected) == 4


def test_combined_identifier_query_covers_each_canonical_subject_deterministically() -> None:
    canonical = (
        chunk(
            path="docs/public/concepts/easa_ja.md",
            heading="External R&D Hook > EASA",
            content=(
                "EASAは内部安全傾向、周辺安全制御、入力文脈、生成過程から現れる"
                "Composite Safety Behaviorを扱い、単一物理Layerと断定しません。"
            ),
            priority=CorpusPriority.PUBLIC,
        ),
        chunk(
            path="docs/public/concepts/dlagsa_ja.md",
            heading="External R&D Hook > DLAGSA",
            content=(
                "DLAGSAは複数の判断・実行・検証主体間の責任、委譲、例外、"
                "改竄耐性付き証跡、全体整合および異常時の安全側制御を扱います。"
            ),
            priority=CorpusPriority.PUBLIC,
        ),
        chunk(
            path="docs/public/concepts/ocilns_ja.md",
            heading="External R&D Hook > OCILNS",
            content=(
                "OCILNSは人、AI、Tool、外部System間の認知的対話を検証、参照、継承、"
                "監査できる改竄耐性付き証跡単位として扱う台帳網です。"
            ),
            priority=CorpusPriority.PUBLIC,
        ),
    )
    catalog = chunk(
        path="docs/public/concepts/catalog_ja.md",
        heading="External R&D Hook Catalog",
        content="EASA、DLAGSA、OCILNSは研究Hookの一覧に含まれます。",
        priority=CorpusPriority.PUBLIC,
    )
    polite_noise = tuple(
        chunk(
            path=f"docs/project/current/noise/polite_{index}_ja.md",
            heading=f"一般説明 {index}",
            content=("この項目について詳しく説明してください。現在の状況と概要を確認します。") * 4,
        )
        for index in range(8)
    )
    engine = retriever()
    index = engine.build(
        cache_key="combined-subject-cache",
        corpus_manifest_digest="a" * 128,
        chunker_key="test_chunker",
        chunker_version="1",
        chunks=(*canonical, catalog, *polite_noise),
    )
    natural_query = "EASAとは何ですか?DLAGSAとは何ですか?OCILNSとは何ですか?"

    result = engine.retrieve(index, query(natural_query, top_k=4))
    repeated = engine.retrieve(index, query(natural_query, top_k=4))
    selected_paths = {item.chunk.project_relative_path for item in result.selected}

    assert result == repeated
    assert {item.project_relative_path for item in canonical} <= selected_paths
    assert result.identifier_subject_count == 3
    assert result.covered_subject_count == 3
    assert result.uncovered_subject_count == 0
    assert len(result.subject_coverage) == 3
    assert all(trace.retrieved_chunk_ids for trace in result.subject_coverage)
    assert engine.tokenizer_version == "2"
    assert engine.version == "5"


@pytest.mark.parametrize(
    ("natural_query", "subjects"),
    [
        ("What are EASA, DLAGSA, and OCILNS?", ("EASA", "DLAGSA", "OCILNS")),
        ("What are ZXQ, NVRTA, and PLMKS?", ("ZXQ", "NVRTA", "PLMKS")),
    ],
)
def test_english_prose_noise_consumes_no_subject_coverage_slots(
    natural_query: str,
    subjects: tuple[str, ...],
) -> None:
    canonical = tuple(
        chunk(
            path=f"docs/public/concepts/{subject.casefold()}_ja.md",
            heading=f"Definition > {subject}",
            content=f"{subject} is the canonical definition for this generic subject.",
            priority=CorpusPriority.PUBLIC,
        )
        for subject in subjects
    )
    prose_noise = tuple(
        chunk(
            path=f"docs/project/current/noise/{word.casefold()}_ja.md",
            heading=word,
            content=f"{word} {word} Explain Briefly ordinary prose without a definition.",
        )
        for word in ("What", "Are", "And", "Explain", "Briefly")
    )
    engine = retriever()
    index = engine.build(
        cache_key="english-prose-noise-cache",
        corpus_manifest_digest="a" * 128,
        chunker_key="test_chunker",
        chunker_version="1",
        chunks=(*canonical, *prose_noise),
    )

    result = engine.retrieve(index, query(natural_query, top_k=3))

    assert result.identifier_subject_count == 3
    assert result.covered_subject_count == 3
    assert result.uncovered_subject_count == 0
    assert {item.chunk for item in result.selected} == set(canonical)
