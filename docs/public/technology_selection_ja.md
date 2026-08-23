# MARGPA Runtime LLM 技術選定

```yaml
document_type: public_technology_selection
document_state: phase_6_interim_checkpoint
language: ja
created_at: 2026-08-23
updated_at: 2026-08-23 23:24 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
current_phase: phase_6_in_progress_adjust
```

## 1. 選定方針

MARGPA Runtime LLMは特定Model、Cloud、Vector StoreまたはAgent Frameworkへ固定しない。CoreはDomain／Port、外部技術はAdapterとして分離し、採用済み技術も交換可能性、Evidence、RollbackおよびAuthority境界を維持する。

## 2. 現在の主要技術

| 領域 | 採用技術 | 現在の用途 |
|---|---|---|
| 言語 | Python 3.12〜3.13 | Runtime、Domain、Adapter、Web Backend、Test |
| 型・設定 | Pydantic／pydantic-settings | Immutable Contract、Validation、Configuration |
| Local推論 | GGUF／llama.cpp／llama-cpp-python | Mac Local Model Load、Streaming、停止、Model切替 |
| Web Backend | FastAPI／Uvicorn | Local API、SSE、Persistent Conversation、Control Surface |
| Web Frontend | React 19／TypeScript／Vite | Chat、Settings、Governance／Model Status UI |
| Local永続化 | SQLite／JSONL／Filesystem | Conversation、Citation、Audit／Evidence、Recording |
| Test | pytest／Vitest／Testing Library | Domain、Integration、Web、Frontend、実Model Smoke |
| Static検査 | Mypy strict／Ruff／ESLint／TypeScript | Backend／Frontendの型・Lint・Format検査 |
| Package管理 | uv／npm | Python Lock／Build、Frontend Build／Test |
| Integrity | Canonical JSON／SHA-512／CAS | Manifest、Digest、Revision、Idempotency、Migration |

## 3. Model選定

### Qwen3-4B GGUF Q4_K_M

- Mac／低資源環境のDefault Main Modelとして継続採用。
- 小型ゆえ回答品質には限界があるが、Runtime／Governance差分を観測するBaselineとして有用。
- Startup Defaultであり、他Candidateの追加や失敗で黙って置換しない。

### DeepSeek-R1-0528-Qwen3-8B GGUF Q4_K_M

- Official Hugging Face SnapshotからProject外Model領域へ取得し、Q8_0 Intermediate経由でQ4_K_Mを作成。
- Runtime Load、Qwen→DeepSeek→Qwen、会話継続および再起動後Qwen復帰は成立。
- ただしQ8_0からの再量子化品質Caveatがあり、User Mac実Chatでは明白な誤答と訂正拒否を確認した。
- 現時点ではResearch Candidateであり、Default／Current Promotionおよび実用品質Acceptanceは不採用。

### DeepSeek-V4-Flash-0731

- Official Snapshotは将来のServer／Cloud比較Candidateとして保持。
- Mac Localでの実用Load対象には大きすぎるため、Local Currentへ昇格しない。
- AWS／GPU Server／Backend／Cost Gate成立後に再評価する。

### Guard／Judge Model

- Current Guardは専用Modelを持たず、Rule／Pattern Base Detectorを採用。
- Current LLM-as-a-Judgeは専用Artifact未採用。Phase 6ではMain ModelのRole-separated `main_self`実験を行ったが、実ChatでStructured Output Failureを検出しRework待ち。
- Candidate名だけでCurrent／Availableと表示しない。

## 4. Architecture選定

- Model、Storage、RAG、Guardrail、Judge、Repair、Agent、ToolをPort／Adapterで分離する。
- Governance DefinitionはProvider、Manifest、Trusted Adapter、Normalized IR、Compiler、Bindingを通す。
- Runtime Modeは原則`OFF／OBSERVE／ENFORCE`とし、初期値はOFF。
- Judgeの評価、Policy、Authority、Human Approval、Executed Actionを混同しない。
- Conversation、Session、Turn、Message、Generation Attempt、Model Role、Evidence Identityを分離する。
- Local-private ControlとPublic／Basic Surfaceを分け、Local PersistenceをPublicへ自動Bindingしない。

## 5. 現在のRAG／Data選定

- Phase 2までのDocumentation RAGは、許可済みDocument、Citation、Digest、Persistent Evidenceを使う小規模Preview。
- SQLite Conversation／CitationとServer Source-of-truthを採用し、Browser full-historyとの二重正本を避ける。
- Embedding、Vector Store、任意Corpus、Document Lifecycle、Web SearchはPhase 7で正式選定する。
- RAG回答品質の最終評価は、Phase 7再構成後にJudge／Repairと組み合わせて行う。

## 6. 現時点で採用していない技術と理由

| 技術／方式 | 現在の扱い | 理由 |
|---|---|---|
| MLX Runtime | 未採用 | Phase 1〜6はllama.cpp AdapterでMac／Linux境界を先に実証。Backend比較は後続Gate |
| Transformers直接推論 | Runtime未採用 | 現在はGGUF／llama.cppがCurrent。Transformers類はDeepSeek Conversion用途に限定 |
| vLLM／SGLang | 未採用 | GPU Server／Cloud向け。Mac Local Currentには不要でPhase 10以降に比較予定 |
| AWS Bedrock依存 | 未採用 | Model／Cloud非依存性、Cost、別Platform移行性を優先。Self-hosted Candidateと分離 |
| LangChain／LangGraph | 未採用 | Current Domain／Portで必要契約を明示実装。Agent／Workflow要件成立後に便益を再評価 |
| LlamaIndex | 未採用 | Phase 2 Previewには過剰。Phase 7のCorpus／Index要件と比較して判断 |
| FAISS／Chroma／Qdrant | 未採用 | 本格Embedding／Vector StoreはPhase 7 Scope。規模、Persistence、Filter、運用Costで比較予定 |
| Dedicated Guard Model | 未採用 | Deterministic GuardをBaseline化。Exact Artifact／Quality／Latency Gate前にCurrentを捏造しない |
| Dedicated Judge Model | 未採用 | Candidate未Acceptance。まずMain-self Judge／Repair Contractを安定化する |
| DeepSeek Mac Q4のDefault昇格 | 不採用 | Load／Switchは成立したが、Current User Mac回答品質が実用Acceptanceを満たさない |
| DeepSeek V4のMac Local Load | 不採用 | Artifact規模とMac Resource条件が不適合。Server／Cloud候補として保持 |
| Public Conversation Persistence | 未採用 | Privacy、Ownership、Authentication、Retention、Costを明示Gateなしで有効化しない |
| Online Learning | 未採用 | User Conversationから暗黙にWeight更新しない。Trainingは独立Dataset／Run／Approvalで扱う |

## 7. Current Status

Phase 3 Generic Definition、Phase 4 Main Governance、Phase 5 Guardrail／Policy／AuthorityはAccepted。Phase 6のModel切替、Runtime Identity、Recording等は実装候補まで進んだが、User MacでJudge `malformed_output`とRepair未成立を確認したため、Phase 6全体は`進行中／ADJUST`である。

本書はPhase 6途中CheckpointのPublic要約であり、Phase 9 Closure時にSource、Lockfile、Model Definition、RAG、Agent／Tool、Experiment Runtime、採用／不採用Decisionを再Inventoryして更新する。
