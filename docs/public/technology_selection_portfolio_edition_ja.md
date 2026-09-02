# MARGPA Runtime LLM 技術選定 — Portfolio Edition

```yaml
document_type: public_technology_selection_portfolio_edition
document_state: current_portfolio_edition
language: ja
created_at: 2026-09-01
updated_at: 2026-09-01 19:46 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
edition: employment_portfolio
source_basis: current_project_records
current_phase: phase_9_1_in_progress_adjust
```

本書は、MARGPA Runtime LLMで採用している主要技術と選定理由を、採用・技術面談向けに整理した用途別文書である。全Decisionや内部仕様を置き換えるものではなく、通常版Technology Selectionと各Architecture Documentを正本とする。

## 1. Selection Principles

- Local-firstで開始し、特定Cloudや特定Vendorを必須条件にしない。
- Domainと外部Libraryを分離し、Model、Storage、Frontend、検索方式を交換可能にする。
- 実装状態、Candidate、Deferred、未採用を明確に区別する。
- Test、Digest、Evidence、MigrationおよびRollback可能性を重視する。
- 個人R&D／PoC／MVPとして、実証価値と保守可能性の釣り合いを取る。

### 1.1 Decision Criteria

| 観点 | 選定時の考え方 |
|---|---|
| Portability | Mac Localを起点に、Linux／Serverへ移行可能な境界を維持する |
| Replaceability | 外部LibraryやModelをCoreへ直接固定しない |
| Observability | 成功だけでなく、失敗理由と実行状態を追跡できる |
| Data Control | Local Data、External Data、Public Surfaceを分離する |
| Testability | Networkや各実Modelを有効化無効化し、主要Contractを検証できる |
| Resource | 個人環境のMemory、Latency、Cost、Quotaを考慮する |
| Maintainability | 少数の明示的な依存と型付きContractを優先する |
| Evidence | 採用理由、実測、未成立点および変更履歴を残す |

## 2. Current Technology Stack

| 領域 | 採用技術 | 主な用途 |
|---|---|---|
| Language | Python 3.12〜3.13 | Runtime、Domain、Adapter、Backend、Test |
| Contract／Config | Pydantic／pydantic-settings | Validation、Immutable Data、Configuration |
| Local Inference | GGUF／llama.cpp／llama-cpp-python | Model Load、Streaming、停止、Role別推論 |
| Web Backend | FastAPI／Uvicorn | REST API、SSE、Local Control Surface |
| Web Frontend | React 19／TypeScript／Vite | Chat、Settings、Status、Evidence UI |
| Persistence | SQLite／JSON／Filesystem | Conversation、Citation、Run、Evidence |
| Retrieval | BM25 Baseline／HTML本文抽出 | Project Docs、Local Corpus、Manual Web Evidence |
| Backend Test | pytest | Unit、Integration、Contract、Regression |
| Frontend Test | Vitest／Testing Library | Component、State、Interaction、Regression |
| Static Analysis | Mypy／Ruff／TypeScript／ESLint | 型、Lint、Format、Build前検査 |
| Package／Build | uv／npm | Lock、Dependency、Frontend Build |
| Integrity | Canonical JSON／SHA-512 | Manifest、Revision、Digest、Evidence Identity |

この構成では、Python BackendがRuntimeとDomain Contractを担当し、React Frontendは状態の表示とUser Interactionを担当する。Model、Database、RetrievalおよびToolはAdapterを介して接続するため、単一Technologyの変更がApplication全体の再実装へ波及しにくい。

## 3. Model Strategy

### Main Model

- Qwen3-4B GGUF Q4_K_MをMac LocalのCurrent Defaultとして使用する。
- 小型Modelの品質限界を前提に、Runtime、RAG、評価機構およびUIのBaselineとして扱う。
- DeepSeek系8B ModelはLocal Loadと切替を確認済みだが、回答品質の検証が未完了のためDefaultへ昇格していない。
- より大規模なModelはServer／Cloud Candidateとして分離し、Mac Localの必須要件にしない。

Model選定では、単純なParameter数だけでなく、実Hardware上のLoad可否、生成速度、Context、出力安定性、日本語品質およびApplicationとの接続性を確認する。ModelをLoadできることと、Defaultとして採用できることは別の判定とする。

### Guard／Judge Model

- Qwen3Guard-Gen 0.6BはLocal Artifactを使った基本的な検知・拒否経路を実機 Macで確認済みである。
- Selene 1 Mini 8BはLocal Loadまで成立したが、実評価経路とResource負荷に未解決事項があり調整中である。
- Main Modelによる自己評価は利用可能だが、出力形式と安定性の追加検証を必要とする。
- Seleneを修復対象として維持しつつ、Current Hardwareに適した軽量Judge Candidateも比較する。

専用Modelについても、Artifactの存在や単発Inferenceだけで採用済みとは扱わない。Role切替、通常Chatとの共存、停止、失敗後の復帰および実機 Macでの操作可能性までを評価する。

## 4. Application Architecture

- BackendはDomain、Application、Port、Adapter、Web Entry Pointを分離する。
- Model、RAG、Guardrail、Judge、Repair、Agent、ToolおよびStorageを独立Componentとして扱う。
- FrontendはBackendの状態を表示し、UIだけでRuntime上の事実や権限を作らない。
- Conversation、Turn、Generation、Citation、Run、StepおよびEvidenceへ安定Identityを持たせる。
- 外部作用や重要操作には明示的な承認境界を設ける。

### 4.1 Backend Boundary

- DomainはWeb Framework、Model SDKおよびDatabase Driverへ直接依存しない。
- Application ServiceがUse Caseを構成し、AdapterがLocal Model、SQLite、Filesystem等を担当する。
- Web LayerはRequest／ResponseとStreaming Eventを型付きContractへ変換する。
- Failureは可能な範囲で分類し、Frontendが汎用Errorだけに収束しないようにする。

### 4.2 Frontend Boundary

- ServerをRuntime Stateの正本とし、Browserだけに重要状態を保持しない。
- Streaming中と完了後の表示責務を分離する。
- Settings変更、Chat切替、ReloadおよびRestart後の再取得をState Lifecycleとして扱う。
- Internal Research情報と通常利用に必要な情報を段階的に整理する。

## 5. Data／Retrieval

- ConversationとCitationはSQLiteをServer側の正本として保存する。
- Project Docsと登録Documentを検索対象として分離する。
- 検索結果にはSource、Title、Path／URL、Digest等を保持する。
- Public URLは指定した場合だけ取得し、外部Contentであることを画面へ明示する。
- Local CorpusのRevision更新後も、過去Turnが参照したEvidenceを維持する。
- General Web Search、Automatic Searchおよび外部Provider運用は後続Phaseで扱う。

| Data Source | Current Handling |
|---|---|
| Conversation | Local SQLiteへ保存し、Chat単位で再開可能 |
| Project Docs | 許可されたDocumentを検索し、Citationを表示 |
| Local Corpus | 登録、Revision更新、Soft Delete、過去Evidence保持 |
| Public URL | 指定時のみ取得し、外部Contentとして区別 |
| Agent Fixture | Project Sourceと分離した限定WorkspaceでFile操作を検証 |

RetrievalはCurrent Corpus規模に合わせてBM25をBaselineとし、EmbeddingやVector Databaseを先回りで必須化していない。検索品質、Filter、更新CostおよびCorpus規模が必要性を示した段階で比較する。

## 6. Frontend／UX

- ReactとTypeScriptでChat、Sidebar、Settings、Archive、Model状態およびEvidence表示を構成する。
- SSEによる生成表示、停止、再生成、Copy、言語切替およびContext使用量表示を実装する。
- 通常ChatとAgent Foundationを同じ画面から切り替えられる。
- White／Dark Themeと日本語／英語UIを保持する。
- 大規模な情報再配置とResponsive最適化は後続の統合工程で扱う。

Frontendでは、機能追加だけでなく「現在何が選択され、何が実行され、何が失敗したか」を区別できることを重視する。Chat本文とResearch Statusを分け、通常利用を内部情報で過密にしない構成を目指している。

### 6.1 Implemented UI Areas

- Persistent Chat List、Rename、Archiveおよび再開。
- Message Streaming、Stop、Retry、RegenerateおよびCopy。
- Local RAG／Web EvidenceのCitation Card。
- Model、Context、TokenおよびComponent Status。
- Local Corpus、Data Controlsおよび各種Settings。
- Agent Run、Step、Input／Output、ApprovalおよびCompletion表示。

## 7. Quality and Operations

- 2,000件超のBackend Testと300件超のFrontend Testを継続運用している。
- Mypy、Ruff、TypeScript、ESLintおよびProduction Buildを検証工程へ含める。
- Fixture／Mock Testと実Model／実機 Mac Manualを分離し、片方だけで完成を主張しない。
- Recovery IndexとHandoffにより、開発Agent長時間作業や担当セッション変更後も途中状態を復元する。
- Source実装、Test、Review、Manual AcceptanceおよびPhase Closureを別Gateで管理する。

### 7.1 Validation Layers

| Layer | Tool／Method | Purpose |
|---|---|---|
| Backend Unit | pytest | Domain、Validation、Failure、Budget |
| Backend Integration | pytest／FastAPI Test Client | API、Storage、Streaming、Component連携 |
| Frontend Unit | Vitest | State、Projection、Utility、Regression |
| Frontend Interaction | Testing Library | 操作、表示、切替、Dialog |
| Type／Lint | Mypy／Ruff／TypeScript／ESLint | Contract不一致と静的欠陥の検出 |
| Build | Vite Production Build | 配信Artifactの成立確認 |
| Real Model | Local Smoke／Focused Probe | Load、Inference、Latency、Failure |
| Test Manual | Mac実画面 | 操作順、再起動、実用性、表示の正直さ |

Testの件数だけで品質を判断せず、新しいTestが対象Failureを実際に検出できるか、回帰を再現できるかも確認する。自動Testで確認できない画面操作やResource負荷はManual Gateへ分離する。

## 8. Deferred／Not Selected

| 技術／方式 | 現在の扱い | 判断理由 |
|---|---|---|
| MLX Runtime | 未採用 | 現行llama.cpp経路を先に安定化し、Backend比較を後続化 |
| vLLM／SGLang | 将来候補 | GPU Server／Cloud向けで、Mac Local Currentには不要 |
| LangChain／LangGraph | 未採用 | 現時点では明示的なDomain／Port Contractを優先 |
| Vector Database | Deferred | Current Corpus規模ではBM25 Baselineを優先し、必要時に比較 |
| Public Conversation Persistence | 未採用 | Privacy、Authentication、Retention、Costの設計が先 |
| Online Learning | 未採用 | Conversationから暗黙にModel Weightを更新しない |

## 9. Deployment and Data Boundaries

- Current PrimaryはMac Local Runtimeであり、Model WeightをRepositoryへ含めない。
- Local Path、Private Conversation、Runtime DataおよびCredentialをPublic Artifactから分離する。
- Cloud、AWS、Public Demoおよび外部Search Providerは、Cost／Privacy／Securityを含む別工程とする。
- Public SurfaceへLocal Persistenceや管理機能を自動的に公開しない。
- Download、Network、Git、Deployment等は通常のSource変更と別Authorityで扱う。
- Backup、MigrationおよびRestart後の復元を、追加機能と同じくAcceptance対象にする。

## 10. Current Status

Local Runtime、Persistent Chat、RAG／Citation、Manual Web Evidence、Security／Evaluation基盤およびAgent／Tool Foundationは実装済みである。現在はPhase 9-1として、専用Judge／Guard、意味評価、修正連携およびModel Lifecycleを実Modelで調整している。

技術選定は固定された完成表ではなく、As-built、実測、Failureおよび次の研究目的に応じて更新する。Current StackはMVPを動かす安定基盤として維持し、Candidate Technologyは比較結果とHuman Acceptanceが揃った場合だけ昇格する。

このPortfolio Editionは、採用技術の列挙だけでなく、なぜ今その技術を使い、何をまだ採用せず、どのEvidenceで次の判断へ進むかを単体で理解できる構成としている。
