# Mac限定簡易Documentation RAG 技術選定

```yaml
document_id: mac_local_documentation_rag_technology_selection
status: accepted
language: ja
created_at: 2026-07-31 17:11:16 JST
accepted_at: 2026-07-31 17:22:59 JST
owner: 設計統括者役
phase: phase_1_ex
implementation_authorized: true_with_accepted_handoff
previous_state:
  - ../../history/architecture/mac_local_documentation_rag_technology_selection_20260731172259.md
```

## 1. 結論

初期Documentation RAGは、Python標準ライブラリを中心とする決定論的Lexical Retrievalを採用する。

```text
Language:
  Python 3.12／3.13

Document:
  Markdown／UTF-8

Normalization:
  unicodedata／re

Manifest／Integrity:
  pathlib／hashlib SHA-512

Chunk:
  Heading-aware deterministic parser

Retrieval:
  Japanese character n-gram
  Latin／Identifier token
  BM25-style ranking

Index:
  In-memory immutable snapshot

Config:
  TOML／tomllib／Pydantic

Web:
  Existing FastAPI／SSE／Vanilla JavaScript

Test:
  Existing pytest／mypy／ruff

New Runtime Dependency:
  None

New Model:
  None
```

## 2. 選定理由

初期目的は最高精度のSemantic Searchではなく、次を同時に成立させることである。

- 現在のMac M2 Pro／16GBでMain Modelと同時に動く。
- 追加Modelを常駐させない。
- Offlineで再現できる。
- Indexの生成条件を説明できる。
- Query、Chunk、ScoreおよびCitationを監査可能にする。
- 将来のEmbedding／Vector Storeへ交換できる。
- RAG OFF時に完全に処理を外せる。
- 現在の軽量Prototypeへ大規模Framework依存を持ち込まない。

日本語は空白区切りだけでは十分に検索できない。初期版ではUnicode正規化後の文字2-gram／3-gramと、英数字・Path・Identifier Tokenを併用する。

## 3. 採用技術

### 3.1 Python標準ライブラリ

使用候補：

```text
pathlib
hashlib
unicodedata
re
math
collections
dataclasses
threading
time
```

採用理由：

- 新規Dependencyがない。
- Python 3.12／3.13で動作する。
- Mac／Linux／Windowsへ移植しやすい。
- Lock Fileを増やさない。
- AlgorithmとEvidenceを直接管理できる。

### 3.2 Markdown限定Reader

初期ReaderはMarkdown UTF-8だけを対象とする。

完全なMarkdown Rendererは不要であり、次の構造だけを安全に識別する。

- ATX Heading。
- 段落。
- Blank Line。
- Fenced Code Block。
- Listは段落として保持。

HTML、JavaScriptまたはMarkdown Linkを実行しない。ReaderはText Dataとして扱う。

### 3.3 Japanese-aware Lexical Tokenizer

初期Tokenizer：

```text
Unicode NFKC
Latin casefold
Japanese 2-gram／3-gram
Latin／digit／underscore／dot／slash／hyphen token
```

形態素解析器を必須にしない理由：

- MeCab等の辞書Dependencyを増やさない。
- Apple Silicon／Linuxでの再現性差を避ける。
- Project固有略称、File名、Class名およびPath検索では文字n-gramが有効である。
- 初期CorpusがProject Docsに限定される。

### 3.4 BM25-style Ranking

初期RankingはBM25系を採用する。

既定Parameter：

```text
k1 = 1.5
b = 0.75
top_k = 4
max_chunks_per_document = 2
```

Field WeightはConfigで調整可能にする。

```text
body_weight
heading_weight
path_weight
exact_phrase_bonus
corpus_priority_weight
```

Scoreと並び順はEvidenceへ残せる。

### 3.5 In-memory Index

Phase 1-exではPersistent Indexを作らない。

Indexは、Corpus Manifest Digestへ対応するImmutable SnapshotとしてMemory内に保持する。

利点：

- Cache FileやMigrationを増やさない。
- GitHub公開物へIndex生成物が混入しない。
- Source DocsとIndexの不整合を避けやすい。
- Project規模約3.1MBの現状では再構築可能な範囲である。

### 3.6 SHA-512

既存Project方針に合わせ、Document、Chunk ContentおよびCorpus ManifestをSHA-512で識別する。

SHA-512は検索Score向上のためではない。Source同一性、再構築条件、Citation Evidenceおよび将来Auditのために使う。

### 3.7 Existing FastAPI／SSE／Vanilla JavaScript

新しいUI Frameworkを導入しない。

既存Web Runtimeへ次を追加する。

- Documentation RAG Switch。
- Retrieval Status。
- System-derived Citation Event。
- Assistant Messageに対応する参照文書Block。

Model Streaming、Cancel、SummaryおよびCopy契約を再利用する。

## 4. 初期不採用技術

### 4.1 LangChain

初期不採用。

理由：

- 現在必要な処理は小さい。
- Domain ContractへFramework型を漏らしたくない。
- Dependencyと追跡対象が増える。
- Port／Application Serviceだけで構成できる。

将来Agent、Tool、Complex RAGまたはEvaluation Orchestrationで再評価できる。

### 4.2 LlamaIndex

初期不採用。

理由：

- 初期CorpusとRetrievalは単純である。
- Data ConnectorおよびIndex abstractionが現在Scopeより大きい。
- Coreの交換境界を独自Portで先に確定したい。

### 4.3 Sentence Transformers／Transformers／PyTorch

初期不採用。

理由：

- Embedding ModelとRuntime Memoryが増える。
- Model Downloadが必要になる。
- Mac／LightningでBackend差が増える。
- Main Model、KV Cache、Webおよび将来Governance用Memoryを圧迫する。

Dense Retrieval実験を行うPhaseで、独立Adapterとして追加する。

### 4.4 MLX／MLX-LM

初期不採用。

MLXはApple Silicon上の将来Embedding Adapter候補である。ただしMac固有実装をCoreへ固定しない。

### 4.5 llama.cpp Embedding

初期不採用。

Main Generation ModelをEmbedding用途へ暗黙流用すると、Pooling、Embedding品質、Model Capability、同時実行およびLoad責務が曖昧になる。

将来、Embedding対応Modelを明示登録したAdapterとして検討する。

### 4.6 SQLite FTS5

初期不採用。

有力な次段階候補ではあるが、Phase 1-exではPersistent Indexを必要としない。

再構築時間、Corpus Sizeまたは履歴検索が問題になった場合に、`IndexStorePort`／`RetrieverPort` Adapterとして追加する。

### 4.7 FAISS／Chroma／Qdrant等

初期不採用。

現在のCorpus、HardwareおよびPhaseに対して過剰であり、Native Dependency、Service、Persistent Stateまたは運用負荷を増やす。

### 4.8 rank-bm25／scikit-learn

初期不採用。

BM25に必要なAlgorithmは小さく、標準ライブラリで明示実装できる。初期段階ではDependency追加より、Algorithm Version、Tie-breakおよびEvidenceをProject側で固定する価値が高い。

## 5. EmbeddingPortの扱い

既存の予約境界に`EmbeddingPort`があるが、初期Pipelineの必須Stepにはしない。

```text
Initial:
  Chunk
    → Lexical Index
    → Lexical Retriever

Future:
  Chunk
    → EmbeddingPort
    → Vector Index
    → Dense Retriever

Future Hybrid:
  Lexical Retriever
  Dense Retriever
    → Fusion Retriever
```

Portがあることと、Adapterが存在／有効／許可されていることを混同しない。

## 6. Config配置方針

Web Access ProfileとRAG Feature Profileを分離する。

推奨：

```text
config/application.toml
  Portable Default／Mode OFF

config/feature_profiles/local_documentation_rag.toml
  Local Lexical Provider／Corpus／Ranking／Budget

config/web_profiles/*.toml
  Access Capability Ceiling
```

概念例：

```toml
schema_version = "1"
profile_key = "local.documentation-rag.lexical"
mode = "enabled"
provider_key = "local_lexical"

[corpus]
include_current = true
include_public = true
include_active_phase_index = true
include_completed_phase_stable = true
include_history = false
include_lossless = false

[chunking]
target_characters = 900
overlap_characters = 120
maximum_characters = 1600

[retrieval]
top_k = 4
max_chunks_per_document = 2
bm25_k1 = 1.5
bm25_b = 0.75

[context]
maximum_tokens = 768
safety_margin_tokens = 512
fallback_maximum_characters = 2400
```

実際のField名とSchemaは実装前にContract Testで固定する。

## 7. Versioning

次を独立Versionとして識別する。

```text
document_source_schema_version
chunker_key／version
tokenizer_key／version
retriever_key／version
context_assembler_key／version
citation_schema_version
feature_profile_schema_version
```

Algorithm変更によって同じQueryの検索結果が変わる場合、Retriever Versionを更新する。

## 8. Test技術

既存Toolを使用する。

```text
pytest:
  Unit／Integration／Web Contract

mypy:
  Port／Contract／Composition Type

ruff:
  Style／Static Check
```

Test Fixtureは小さな日本語／英語Markdown Corpusを一時Directoryに作り、外部Network、実Modelまたは実Project Docsへ依存しない。

Model接続のAcceptanceだけ、Local Qwen3 GGUFを使う。

## 9. 将来の再評価条件

次のいずれかが発生した場合、Dense／Hybrid Retrievalを再評価する。

- Lexical RetrievalのRecallが要求を満たさない。
- 同義語、言い換えまたは概念検索が主要要件になる。
- Corpusが大幅に増える。
- PDF、Office Documentまたは外部Knowledge Sourceを追加する。
- Home Server／CloudでEmbedding Modelを常駐できる。
- RAG EvaluationでDense Retrievalの改善が実証される。

「高性能そうだから」だけで変更しない。Baseline、検索評価、Latency、Memory、Index Sizeおよび再現性を比較して決定する。

## 10. Technology Decision Summary

```text
Accepted for Initial Design:
  Python standard library
  Markdown UTF-8
  Japanese n-gram＋Latin token
  BM25-style lexical ranking
  In-memory lazy index
  SHA-512 manifest
  Existing FastAPI／SSE／Vanilla JS

Reserved:
  EmbeddingPort
  Dense Retriever
  Hybrid Retriever
  Persistent Index
  External Runtime Adapter

Rejected for Initial Scope:
  New embedding model
  Vector database
  LangChain
  LlamaIndex
  External network
  Public Demo RAG
```
