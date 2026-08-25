# MARGPA Runtime LLM 技術選定

```yaml
document_type: public_technology_selection
document_state: phase_6_interim_checkpoint
language: ja
created_at: 2026-08-23
updated_at: 2026-08-25 16:21:55 JST
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
- User MacでのRuntime Load、Qwen→DeepSeek→Qwen、会話継続および再起動後Qwen復帰は成立し、起動中に選択・利用できる。
- User Mac実Chatでは明白な誤答、訂正拒否、不安定な回答を確認している。ただし、原因は
  Model固有品質、Q8_0からの再量子化Caveat、Chat Template／Generation設定／Local Runtime、および
  未完成のGovernance／Judge／Repair／RAGの影響を分離できていない。
- 現時点の位置付けは、**Macで選択・利用できる仮使用Model／Research Candidate**である。Startup Defaultは
  Qwenを維持するが、DeepSeekを使用不可または改善不能と判定したものではない。
- Phase 6のSemantic Governance／Dedicated Judge／Guard、Phase 7のRAG／Web Search、および後続のRuntime／Artifact比較による
  改善・原因切り分け後に、Default昇格と実用品質Acceptanceを再判定する。

### DeepSeek-V4-Flash-0731

- Official Snapshotは将来のServer／Cloud比較Candidateとして保持。
- Mac Localでの実用Load対象には大きすぎるため、Local Currentへ昇格しない。
- AWS／GPU Server／Backend／Cost Gate成立後に再評価する。

### DeepSeek-V4-Pro-0813

- `deepseek-ai/DeepSeek-V4-Pro-0813`を、DeepSeek-V4-Flash-0731より上位の将来比較Candidate／
  Research-only Ceilingとして保持する。
- Official Repositoryは確認済みだが、現ProjectではModel Download、Local Load、Conversion／Quantization、
  Benchmark、Current Promotionを行っていない。
- Mac Localの実用対象とはせず、大規模GPU Server／Cloud、vLLM／SGLang等のBackend、Resource／Cost／
  License／Security Gate成立後に、Flash、他ModelおよびGovernance構成と比較する。

### Guard／Judge Model

- Current GuardはRule／Pattern Base Detector。専用Guardとして
  `Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf`のLocal Artifactは取得済みで、Phase 6 Remaining Reworkで
  Runtime Adapter、Provider選択、`OFF／OBSERVE／ENFORCE`、品質／Latency Gateへ接続する。
- Current LLM-as-a-JudgeはMain Modelを使うRole-separated `main_self`。専用Judgeとして
  `Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf`のLocal Artifactは取得済みで、Phase 6 Remaining Reworkで
  Dedicated Judge Adapter、Provider選択、Semantic Rule評価、Repair後再評価へ接続する。
- 両Artifactは既に実装対象として選定済みであり、無期限にCurrent構成のまま維持する計画ではない。
  ただし、Runtime接続とUser Mac Acceptance前にCurrent／Active／Availableとは表示しない。

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
| `Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf`のCurrent Guard昇格 | Local Artifact取得済み／Phase 6 Rework接続予定／Current未昇格 | Dedicated Guard候補として選定済み。Runtime Adapter、Provider Lifecycle、Quality／Latency／User Mac Acceptance前にCurrentを捏造しない |
| `Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf`のCurrent Judge昇格 | Local Artifact取得済み／Phase 6 Rework接続予定／Current未昇格 | Dedicated Judge候補として選定済み。Structured Output、Semantic Rule評価、Repair後再評価、Resource／User Mac Acceptance前にCurrentを捏造しない |
| DeepSeek Mac Q4のDefault昇格 | 現時点で保留／Macで使える仮使用Model | Load／Switch／会話継続は成立。現在の回答は不安定だが、量子化、Runtime、Governance、Judge／Repair、RAGの原因切り分けが未完了のため、改善不能または最終不採用とは判定しない |
| DeepSeek-V4-Flash-0731／DeepSeek-V4-Pro-0813のMac Local Load | 不採用 | Artifact規模とMac Resource条件が不適合。FlashはServer／Cloud候補、Proはその上位のResearch-only Ceilingとして保持 |
| Public Conversation Persistence | 未採用 | Privacy、Ownership、Authentication、Retention、Costを明示Gateなしで有効化しない |
| Online Learning | 未採用 | User Conversationから暗黙にWeight更新しない。Trainingは独立Dataset／Run／Approvalで扱う |

## 7. Current Status

Phase 3 Generic Definition、Phase 4 Main Governance、Phase 5 Guardrail／Policy／AuthorityはAccepted。Phase 6のModel切替、Runtime Identity、Recording等は実装済みで、Repair実行・採用経路もUser Macで一度観測した。一方、修復後回答は依然として誤っており、ARGD／DAGD Semantic Ruleは未接続、Current JudgeはMain-self、Dedicated Guard／JudgeはRuntime未接続である。そのためPhase 6全体は`進行中／ADJUST`である。

本書はPhase 6途中CheckpointのPublic要約であり、Phase 9 Closure時にSource、Lockfile、Model Definition、RAG、Agent／Tool、Experiment Runtime、採用／不採用Decisionを再Inventoryして更新する。
