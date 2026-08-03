# ADR-0028: Mac限定Sparse Documentation RAG／External Adapter Hook

```yaml
document_id: adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook
status: accepted
language: ja
created_at: 2026-07-31 17:11:16 JST
accepted_at: 2026-07-31 17:22:59 JST
owner: 設計統括者役
phase: phase_1_ex
implementation_authorized: true_with_accepted_handoff
previous_state:
  - ../../history/adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_20260731172259.md
clarifies:
  - adr_0025_public_demo_auto_start_and_pre_release_gate
  - adr_0027_public_demo_minimal_access_and_deferred_control_hooks
```

## 1. Context

Phase 1で、Local Mac MetalとLightning Pure CPUの交換可能なLLM Runtime、Web UI、Streaming、Cancel、Summary、Thinking Presentation、Basic Preview、Public DemoおよびAccess Profile分離が成立した。

Phase 1-exでは、Project DocsをLLM自身が参照し、Projectを説明できる簡易Documentation RAGを追加する予定である。

現在の制約：

- Mac M2 Pro。
- 16GB Unified Memory。
- Qwen3 4B Q4_K_MをMain Modelとして使用。
- Main Model、KV Cache、Webおよび将来Governance処理でMemoryを共有。
- 複数Modelの同時常駐を避けたい。
- Current／Stable Docs候補は38文書、約3.1MB。
- `history/`および`lossless/`はさらに大量かつ重複が多い。
- Public DemoではDocumentation RAGを禁止する既存Decisionがある。
- 将来はLightning、Home Server、Cloud、Dense RetrievalおよびHybrid Retrievalへ拡張したい。

## 2. Decision

初期Documentation RAGは、Local Mac限定のSparse／Lexical Retrievalとして実装する。

```text
Reader:
  Local Markdown／UTF-8

Chunker:
  Heading-aware deterministic chunking

Tokenizer:
  Unicode NFKC
  Japanese character 2-gram／3-gram
  Latin／Identifier token

Retriever:
  BM25-style lexical ranking

Index:
  In-memory／Lazy Build／No Persistent Write

Integrity:
  SHA-512 Document／Chunk／Manifest

Dependency:
  Python standard library中心

Default:
  OFF
```

初期実装でEmbedding Model、Vector Database、LangChainまたはLlamaIndexを導入しない。

## 3. Embedding Decision

`EmbeddingPort`は削除しないが、初期Pipelineの必須Stepにしない。

```text
Initial:
  Source → Chunk → Lexical Index → Lexical Retriever

Future:
  Source → Chunk → EmbeddingPort → Vector Index → Dense Retriever

Future:
  Lexical＋Dense → Fusion Retriever
```

これにより、現在の軽量実装が将来のSemantic Retrievalを妨げず、Embeddingがない状態も正式な構成として扱える。

## 4. Corpus Decision

Default CorpusはCanonical／Stable Docsへ限定する。

```text
Include:
  docs/project/current/
  docs/public/
  Active Phase Index
  Completed Phase Stable Japanese Docs

Exclude by default:
  history/
  lossless/
  Hidden／Temporary／Backup
  Symbolic Link
  Project Root外
```

Raw HistoryおよびLossless文書は削除しない。保存上の重要性と通常検索対象であることを分離する。

## 5. Citation Decision

CitationはModelに生成させず、Retrieverの採用結果からSystemが生成する。

Model AnswerとCitation Metadataを分離する。

ModelがCitationらしい文字列を生成しても、System Citationとして扱わない。

## 6. Trust Decision

取得したDocs本文は、System Policyではなく非信頼の参照Dataとして扱う。

Docs内の命令、権限要求、Tool実行要求、System PromptらしいTextまたは方針変更要求は、Runtime Authorityを持たない。

RAG ContextはUser Messageへ連結せず、System所有のReference Messageとして分離する。

## 7. Runtime／Access Decision

```text
Local Mac:
  eligible
  Adapter available
  Default OFF

Basic Preview:
  eligible
  Initial External Adapter not bound

Public Demo:
  denied
  Adapter must not be constructed
```

Public DemoでのClient Request、UI、Environment VariableまたはConfig Overrideによる有効化を拒否する。

## 8. State Decision

RAG Stateは次を分離する。

```text
disabled
unavailable
enabled
denied
```

存在、Capability、Feature Selection、Adapter AvailabilityおよびCorpus Availabilityを一つのBooleanへ潰さない。

## 9. Index Decision

Phase 1-exではPersistent Indexを作らない。

Corpus Manifest Digest、Feature Profile DigestおよびAlgorithm Versionが一致する場合だけMemory Indexを再利用する。

Source変更時は新Indexを完成させてからAtomic Replaceする。不完全Indexまたは旧Corpus Indexで回答しない。

## 10. Docs Missing Decision

RAG ON時に`docs/`が存在しない場合、Project内容をModelで推測せず、次を返す。

```text
docsが設置されていないため参照出来ません。
```

この状態ではDocumentation RAG経由のModel Callを開始しない。

## 11. Alternatives

### 11.1 Embedding Model＋Vector Storeを最初から導入

不採用。

Semantic Recall向上の可能性はあるが、追加Model、Memory、Download、Backend差、Index運用およびDependencyを増やす。Phase 1-exの骨格確認より先に導入する必要はない。

### 11.2 LangChain／LlamaIndexを使用

不採用。

現在必要なPipelineは小さく、Framework型をDomain Contractに持ち込まずに実装できる。将来のComplex Orchestrationで再評価する。

### 11.3 SQLite FTS5

初期不採用、将来候補。

Persistent Indexと高速検索には有力だが、現在の約3.1MB CorpusではMemory Indexを再構築できる。

### 11.4 Docs全文を毎回Promptへ投入

不採用。

Context Size、Token Cost、Noise、旧情報混入およびCitation追跡性の問題がある。

### 11.5 Main Modelで検索対象を選ばせる

不採用。

Retrievalそのものが非決定的になり、Token、Latency、監査および再現性が悪化する。決定論で処理できる検索はPythonで行う。

### 11.6 Documentation RAGを後のFull RAG Phaseまで延期

不採用。

現在のDocs構造、Port分離、Access ProfileおよびProject自己説明という研究価値を、小規模なSparse RAGで先に検証できる。

## 12. Positive Consequences

- 追加ModelなしでLocal Macへ導入できる。
- 新規Runtime Dependencyを原則追加しない。
- Offlineで動く。
- Retrieval結果を再現できる。
- SHA-512とCitation Evidenceを持てる。
- Public Demoと分離できる。
- RAG OFF時に既存Runtimeへ負荷をかけない。
- Dense／Hybrid／External Adapterを後から追加できる。
- RAG効果とCostのBaselineを作れる。

## 13. Cost／Risk

- 同義語、抽象概念または大きな言い換えのRecallはDense Retrievalより弱い可能性がある。
- 日本語n-gramはIndex Entry数が増える。
- 独自Tokenizer／BM25実装のTest責任が発生する。
- Current Docsに重複や不整合がある場合、検索結果へ影響する。
- Prompt Injectionを意味的に完全排除するものではない。
- Context 4096とOutput最大2048のため、RAG Contextは小さい。
- Project Docsが増えた場合、Memory Index再構築が遅くなる可能性がある。

## 14. Mitigation

- Heading、Path、Corpus PriorityおよびPhrase Bonusを使う。
- Query／Retrieval Fixtureを増やす。
- RAG OFF／ONの比較を残す。
- No Hitを明示する。
- Docsを非信頼Dataとして隔離する。
- Tool／Agent／External I/Oを接続しない。
- CorpusとContextへHard Limitを設ける。
- Dense／Hybrid RetrievalのAdapter Hookを維持する。
- 性能再評価条件を明示する。

## 15. Re-evaluation Triggers

次の場合にTechnology Decisionを再評価する。

- Retrieval EvaluationでRecall不足が確認された。
- Corpusが32MiBまたは20,000 Chunkへ近づいた。
- Cold BuildまたはWarm Retrievalが目標を超えた。
- PDF／Office／External Sourceが必要になった。
- Home Server／CloudでEmbedding Modelを常駐できる。
- RAG Governance／JudgeがSemantic Retrievalを必要とする。
- Multi-language Corpusが大幅に増えた。

## 16. Implementation／External Action Boundary

本ADRのAccepted化により、同時点のAccepted実装担当Handoffに限定して、Project Root内のSource、Test、Configおよび必要な実装Status文書を変更できる。

本ADRは次を許可しない。

- Dependency Install。
- Model Download。
- Embedding Model追加。
- Lightning設定変更。
- Public DemoでのRAG有効化。
- Git／GitHub操作。
- Project Root外のFile操作。
- Handoff Scope外の機能追加。
