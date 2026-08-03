# ADR-0029: Lightning Basic Preview Public Corpus Documentation RAG Adapter Hook

```yaml
document_id: adr_0029_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook
status: accepted
language: ja
created_at: 2026-08-01 08:49:52 JST
accepted_at: 2026-08-01 08:49:52 JST
owner: 設計統括者役
phase: phase_1_ex
implementation_authorized: true_with_accepted_handoff
extends:
  - adr_0026_lightning_basic_preview_lifecycle_and_managed_secrets
  - adr_0027_public_demo_minimal_access_and_deferred_control_hooks
  - adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook
```

## 1. Context

Mac LocalでSparse Documentation RAGが成立し、第2回手動TestでSource／Index／Retrieval／Assembly／Citation、Per-turn RetrievalおよびCoverage Fail-closedをScoped Acceptedとした。

Lightning Basic PreviewはDocumentation RAG `eligible`だが、Web Entry PointがLocal Macの場合だけAdapterを構築するため、Linux x86_64では`unavailable`である。

ユーザーは、公開可能なJA／EN文書8件だけをLightningの`docs/public/`へ配置し、Basic認証Previewで参照可能にする方針を選択した。Public Demoは引き続きRAG禁止である。

## 2. Decision

Lightning Basic Previewに限定し、既存Sparse Documentation RAGを明示Feature ProfileでCompositionできるExternal Adapter Hookを実装する。

```text
Basic Preview:
  RAG eligible
  explicit Lightning feature profile
  exact public 8-file corpus
  existing sparse adapter graph

Public Demo:
  RAG denied
  adapter not constructed
  corpus not scanned
```

Web Entry Pointへ明示的なDocumentation RAG Feature Profile選択を追加し、Access Capability、Platform Compatibility、Adapter AvailabilityおよびUser Requested Modeを分離する。

## 3. Corpus Decision

Lightning Corpusは次の8文書のみとする。

```text
docs/public/overview_ja.md
docs/public/overview_en.md
docs/public/concept_ja.md
docs/public/concept_en.md
docs/public/roadmap_ja.md
docs/public/roadmap_en.md
docs/public/technology_selection_ja.md
docs/public/technology_selection_en.md
```

Mac用Current／Phase／History／LosslessをLightning Corpusへ入れない。Allowlist外のPublic Markdownも自動的に入れない。

## 4. Technology Decision

新規Runtime Dependencyは追加しない。

```text
Source:
  Project-root-bounded UTF-8 Markdown

Chunker／Tokenizer／Retriever／Index／Assembler／Citation:
  reuse existing implementation

Index:
  in-memory／lazy／non-persistent

Integrity:
  SHA-512

Token Count:
  existing loaded-model binder
```

Embedding Model、Vector Database、LangChain、LlamaIndexまたはExternal APIは導入しない。

## 5. Profile Decision

既存Mac Profile v1は変更せず、LightningのExplicit File Corpusを表す後方互換なProfile Contractを追加する。

MacとLightningで同じCorpus Inclusionを強制せず、Feature ProfileがSource Selectionを所有する。

## 6. Access Decision

Documentation RAG Profileの選択はAccess Profileより強い権限を持たない。

```text
Access denied + feature selected:
  no adapter construction

Access eligible + no adapter:
  unavailable

Access eligible + valid adapter + user OFF:
  disabled

Access eligible + valid adapter + user ON:
  enabled
```

Public DemoではClient、EnvironmentまたはCLIからDocumentation RAGを有効化できない。

## 7. Lifecycle Decision

Basic Previewの既存Foreground `run`、Traffic-aware Wake-up、Managed Secrets、Basic認証およびPort 7860の実機契約を維持する。

RAG IndexはProcess Memoryだけに保持し、Sleep／Wake後の最初のRAG ON Requestで再構築する。Persistent Cacheを勝手に書かない。

Lightning Platform操作はユーザーが担当する。Repository実装者はAPI Builder、URL、Port、Secrets、Machine、Sleep／WakeまたはCreditを変更しない。

## 8. Retrieval Guidance Metadata Decision

文書ごとのHit Keyword列またはModel参照用Index表は、将来のOptional Retrieval Metadata Adapterとして予約する。

本Lightning Hookでは実装しない。

将来実装の不変条件：

- Document SHA-512と結び付ける。
- MetadataをAnswerの根拠本文の代替にしない。
- Metadataから真実性、AuthorityまたはExecution Permissionを生成しない。
- Stale Metadataを黙って使用しない。
- Metadataなしを正式Modeとする。

## 9. Quality Decision

Lightning対応は、Mac第2回手動Testで確認したSemantic Precision問題の解消を保証しない。

```text
Accepted target:
  same RAG mechanism on another deployment
  stricter public-only corpus
  access separation
  fail-closed

Deferred:
  semantic reranking
  claim entailment
  governance／judge／repair
  model upgrade
```

## 10. Alternatives

### 10.1 Copy the Entire Mac Docs Tree

不採用。公開不要のInternal Docs、大量重複、旧History、Context NoiseおよびUpload Costを増やす。

### 10.2 Enable RAG for Public Demo

不採用。既存のAccess Decisionと矛盾し、匿名AccessへDocument Surfaceを追加する。

### 10.3 Create a Lightning-only Duplicate RAG Stack

不採用。MacとLightningでCoverage、Citation、Fail-closedおよびTestが分岐する。

### 10.4 Add Embeddings Now

不採用。8文書CorpusのExternal Hook実証に対し、Dependency、Memory、Build、Model DownloadおよびCross-platform差が大きい。

### 10.5 Put the Eight Files Directly under `docs/`

不採用。Current AdapterのCorpus境界と一致せず、Public Docsの責務と配置を分離できない。

## 11. Consequences

### Positive

- MacとLightningが同じRAG Core Contractを使用する。
- Lightningへは公開可能な8文書だけを配置できる。
- Basic PreviewとPublic DemoのRAG可否が分離される。
- Future Home Server／CloudのFeature Profile追加に再利用できる。
- Persistent Indexと追加Modelを必要としない。

### Negative／Trade-off

- First RAG ON RequestでCold Index Buildが発生する。
- JA／EN重複CorpusがRankingに影響する可能性がある。
- Semantic PrecisionはMacと同程度の限界を持つ。
- Feature Profile Schema／Composition／Script Testの追加が必要になる。

## 12. Acceptance

本ADRはAcceptedとし、詳細要件、Architectureおよび実装担当Handoffの範囲でRepository実装を許可する。

Lightning実機操作と最終Acceptanceはユーザー手動Test後に別Reviewで判定する。
