# 将来拡張設計

- 文書ID: `future_extensions`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: RAG、AI Agent、Image、Cloud、複数Model、複数GD
- 正本言語: 日本語
- 上位Architecture: [system_architecture_20260718174637.md](system_architecture_20260718174637.md)

## 1. 基本方針

将来機能は初期Module BoundaryへHookを用意するが、初期MVPで同時実装しない。

- 基本Chatを先に成立させる
- Runtime GovernanceとAuditを成立させる
- GuardrailとRepairを追加する
- その後にRAGとAgentを追加する
- ModelとGovernance Definitionの交換性を維持する
- 不要なModuleを無効化できるようにする

## 2. RAG

実装Phase：`Phase 5`

候補機能：

- Local Document登録
- File Parsing
- Chunking
- Embedding
- Index
- Retrieval
- Context Injection
- Source表示
- Document更新
- Document削除
- Re-index
- RAG On／Off
- Citation
- Traceability

Audit Logへ記録するもの：

- Query
- Embedding Model
- Retriever
- Index Version
- Document ID
- Chunk ID
- Source
- Score
- Document Hash
- 採用Chunk
- Citation
- Traceability Limit

技術候補：

- LangChainを優先的に検討
- LlamaIndexは初期不採用方向
- Vector Storeは未決
- Embedding Modelは未選定
- Rerankerは将来追加

Model Directory予約：

```text
models/embedding/
models/reranker/
```

## 3. AI Agent

実装Phase：`Phase 6`

候補機能：

- Tool Registry
- Tool Selection
- Multi-Step Execution
- Planning
- Observation
- Replanning
- State
- Memory
- Handoff
- Completion Check
- Human Approval

制御：

- Max Step
- Max Time
- Retry Limit
- Tool Permission
- Input Validation
- Side Effect確認
- Infinite Loop防止
- 全Tool CallのAudit Log
- Cancel
- Resume
- Failure State
- Partial Completion

LangGraphは有力候補だが未確定。

将来的に次と接続する。

- AAGD
- AISGD
- MPGD
- DAAGD

AAGDはAgentの実行過程を統治するが、外部に存在しない実行権限を生成しない。

## 4. Image／Vision

初期版ではImage入力を実装しない。

既存Model：

```text
llava-phi-3-mini-int4.gguf
llava-phi-3-mini-mmproj-f16.gguf
```

将来、Vision Port／Adapterを通して接続する。

Model Directory予約：

```text
models/vision/
```

## 5. Prompt Injection Classifier

初期はRule Basedを中心とする。

将来、専用Classifierを追加できるようにする。

Model Directory予約：

```text
models/classifier/
```

ClassifierはGuardrail Portの一実装とし、Tool Permissionの最終決定権を持たない。

## 6. 複数Model

将来の候補：

- 複数Main Model
- Task別Model
- Remote Model
- Local／Cloud切り替え
- Fallback Model
- Vision Model
- Embedding Model
- Reranker
- Classifier
- 複数Judge

初期版では自動Model Routingを実装しない。

設定でActive Modelを明示的に選択する。

同じModel Artifactを複数Roleで使用する場合、Fileを複製せずRegistryから同じArtifactを参照できるようにする。

## 7. 複数Governance Definition

将来の候補：

- Governance Registry
- 複数Definition
- Lazy Load
- Task別Activation
- Rule別Compile
- Dependency解決
- Conflict解決
- Standard Governance Result
- CDOGDによるOrchestration

初期版ではARGD／DAGDを基盤とし、他GDはHookのみとする。

## 8. Cloud

将来候補：

- GPU Server
- CUDA
- vLLM
- Remote Inference API
- PostgreSQL
- Object Storage
- Cloud Audit
- AWS
- Azure
- Container

Application Coreを共通化し、Deployment ProfileとAdapterを交換する。

## 9. Docker

初期版では使用しない。

将来候補：

- APIのみContainer化
- DBのみContainer化
- RAGのみContainer化
- Cloud Deployment
- CI用Environment

## 10. SQL

初期必須ではない。

SQLite追加を検討する条件：

- 基本機能が完成した
- 履歴検索が必要
- Audit Log UIの検索性能が必要
- RAG Metadata管理が必要
- Event間関係の検索が必要

有力な分担：

```text
JSON / JSONL : Audit原本
SQLite       : Index、検索、管理
PostgreSQL   : 将来Cloud
```

## 11. ContextとMemory

初期段階では長大なContextを最優先しない。

将来候補：

- Conversation Summary
- Retrieval Based Memory
- Long-Term Memory
- User Profile
- Context Budget Manager
- Importance Based Selection
- Context Compression
- External Memory Store

ARGDの無断要約禁止と両立するため、Summaryの作成、承認、参照元、LossをAudit可能にする必要がある。

## 12. 将来機能の導入原則

- Coreの既存境界を壊さない
- 新Moduleを無効化可能にする
- Capabilityを明示する
- Failure時のDegradeを定義する
- Modelへ不要な情報を渡さない
- Audit Eventを追加する
- Security／Permissionを後付けにしない
- User固有Dataを公開Repositoryへ含めない
