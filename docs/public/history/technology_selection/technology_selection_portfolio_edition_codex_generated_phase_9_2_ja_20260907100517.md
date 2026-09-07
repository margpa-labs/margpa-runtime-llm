# MARGPA Runtime LLM 技術選定 — Portfolio Edition

```yaml
document_type: public_technology_selection_portfolio_edition
document_state: current
language: ja
project_initiated_at: 2026-07-18 17:46:37 JST
created_at: 2026-09-01
updated_at: 2026-09-07 09:54 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
edition: portfolio_selected_detail
source_basis: current_project_records
current_phase: phase_9_2_in_progress
```

MARGPA Runtime LLMは、ローカルLLM、知識検索、安全性確認、回答評価、回答修正、Agent実行を組み合わせて検証するWeb Platformである。

本書では、主要な技術と選定理由を、現在動作している範囲に絞って説明する。

## 1. 技術選定の考え方

- Local-firstで開始し、特定Cloudを必須にしない。
- Model、Storage、検索、Frontendを交換できる境界を維持する。
- 実装済み、調整中、将来候補を明確に分ける。
- 成功結果だけでなく、実行状態と失敗理由を確認できるようにする。
- 自動Test、実Model Test、実画面確認を使い分ける。
- Hardware、Latency、Memory、Costを設計条件に含める。

## 2. 主要なTechnology Stack

| 領域 | 技術 | 主な役割 |
|---|---|---|
| Backend | Python／FastAPI／Uvicorn | Domain処理、API、Streaming |
| Contract | Pydantic／pydantic-settings | 型、Validation、設定 |
| Local Inference | GGUF／llama.cpp／llama-cpp-python | Model Load、生成、停止 |
| Frontend | React 19／TypeScript／Vite | Chat、Settings、Evidence、実験画面 |
| Persistence | SQLite／JSON／Filesystem | 会話、Citation、Run、Evidence |
| Retrieval | BM25／HTML本文抽出 | Local文書と指定URLの検索 |
| Backend Test | pytest | Unit、Integration、Regression |
| Frontend Test | Vitest／Testing Library | 表示、操作、状態遷移 |
| Static Analysis | Mypy／Ruff／TypeScript／ESLint | 型、Lint、Build検査 |
| Package管理 | uv／npm | Dependency、Lock、Build |
| Integrity | Canonical JSON／SHA-512 | Digest、Revision、Identity |

## 3. Model構成

### 3.1 Main Model

Qwen3 4BのGGUF Modelを、Mac LocalのStartup Defaultとして使用する。

小型で扱いやすく、Chat、RAG、Governance、UIを通した基準構成に適している。別Modelへ切り替えても、会話、Storage、Frontendを再利用できる。

### 3.2 Judge Model

Gemma 4 E2Bを独立したLLM-as-a-Judgeとして使用する。

Main ModelとJudge Modelを分けることで、回答生成と評価を同じ役割へ固定しない。JudgeはMain GovernanceがOFFでも単独で動作でき、回答修正後の再評価にも利用する。

構造化された評価結果を安定して扱うため、Judgeに限って生成形式を制約する。通常Chatや他のModel処理には影響させない。

### 3.3 Guard Model

Qwen3Guard 0.6Bを安全性確認用のDedicated Modelとして使用する。

OBSERVEでは検知結果だけを記録し、ENFORCEでは必要なActionを実行する。JudgeやMain Governanceとは独立して有効化できる。

### 3.4 Model Candidate

DeepSeek系ModelとSeleneは、比較用または将来構成として保持する。現在のHardwareと実行条件に適したModelを既定構成とし、候補Modelの存在だけで自動的に切り替えない。

## 4. Application Architecture

Backendは次の役割へ分けている。

```text
Domain
→ Application Service
→ Port
→ Adapter
→ Web API／Model／Storage
```

- Domainは特定のWeb FrameworkやModel Libraryへ直接依存しない。
- Application Serviceが会話、検索、評価、修正の流れを構成する。
- Portが必要なCapabilityを定義する。
- Adapterがllama.cpp、SQLite、Filesystem等を接続する。
- FrontendはBackendの状態を表示し、UIだけで実行事実を作らない。

この分離により、一つの技術変更がApplication全体へ波及しにくい構造を維持する。

## 5. Component構成

次の機能を独立したComponentとして扱う。

- Main Model。
- Local RAGとCitation。
- Main Runtime Governance。
- Guardrail。
- LLM-as-a-Judge。
- 回答修正と再評価。
- RecordingとEvidence。
- AgentとTool。
- Experiment Runtime。

各Componentは必要なものだけを有効にする。OFFのComponentが、不要なModel CallやActionを発生させないことを重視する。

設定されたProvider、現在有効なProvider、実際に実行したProviderを分けて記録する。画面上の選択だけで、実行済みとは判断しない。

## 6. Governanceと回答評価

Main Modelの前後へ検査Pointを置き、入力、回答候補、評価結果、最終回答を区別する。

`OFF／OBSERVE／ENFORCE`の3 Modeを基本とする。

| Mode | 動作 |
|---|---|
| OFF | Componentを実行しない |
| OBSERVE | 結果を記録するが回答へ介入しない |
| ENFORCE | 許可されたActionを回答へ反映する |

回答修正は、JudgeまたはMain Governanceが必要と判断した場合に起動する。修正後は再評価し、採用または不採用を決める。

Modelの判定品質と、評価・修正・記録を接続するPlatform基盤の品質は分けて検証する。

## 7. DataとRetrieval

- 会話とCitationはSQLiteへ保存する。
- Project Docsと登録Documentを検索対象として分ける。
- 現在のCorpus規模ではBM25をBaselineとして使用する。
- 検索結果にはSource、Title、PathまたはURL、Digestを保持する。
- 文書更新後も、過去の回答が参照したEvidenceを維持する。
- 指定したPublic URLだけを取得し、外部Contentとして区別する。
- Model Weight、Private Data、CredentialをRepositoryへ含めない。

EmbeddingやVector Databaseは、Corpus規模と検索品質から必要性が確認できた段階で比較する。

## 8. Experiment Runtime

同じCaseへ異なる構成を適用し、結果を比較するExperiment Runtimeを構築している。

- Plan、Case、Variant、Runを別のIdentityとして保存する。
- 実行設定を固定し、途中の設定変更を結果へ混入させない。
- 実行結果とEvidenceを再起動後も読み直せるようにする。
- 非同期実行、停止、Deadline、二重結果防止を扱う。
- 実行完了とCase合格を別の判定にする。
- Fixtureと実Modelの結果を区別する。

React UIからPreset、実行状態、Comparison、詳細Evidenceを確認できる最小画面も用意している。

## 9. Frontendと操作性

ReactとTypeScriptで次の画面を構成する。

- Persistent Chat ListとArchive。
- Message Streaming、停止、再生成、Copy。
- ModelとContextの設定。
- CitationとWeb Evidence。
- Governance、Guard、Judge、Repairの状態。
- Local CorpusとData Controls。
- Agent Run、Step、Approval。
- Experiment Plan、Run、Comparison。

重要なRuntime StateはServer側を正本とする。Reloadや再起動後も必要な情報を取得し直せる設計を採る。

## 10. Qualityと検証

| 検証層 | 主な対象 |
|---|---|
| Unit Test | Domain、Validation、境界条件 |
| Integration Test | API、Storage、Component連携 |
| Frontend Test | 表示、操作、状態遷移 |
| Static Analysis | 型、Lint、Production Build |
| Real Model Test | Load、推論、連携、停止 |
| 実画面確認 | 操作順、表示、再起動後の状態 |
| Independent Review | 要件、回帰Risk、完成判定 |

Backendでは2,600件を超えるTest、Frontendでは330件を超えるTestを継続している。

Testが成功することだけでなく、対象の不具合を実際に検出できることも確認する。Fixture、Production経路、実Model、実画面を別のEvidenceとして扱う。

## 11. 現在選定していない方式

| 技術／方式 | 現在の判断 |
|---|---|
| MLX Runtime | 現行llama.cpp経路の安定化を優先 |
| vLLM／SGLang | GPU Server／Cloud向けの将来候補 |
| LangChain／LangGraph | 明示的なDomain／Port Contractを優先 |
| Vector Database | 現在のCorpus規模ではBM25を優先 |
| Public Conversation Persistence | PrivacyとAccess設計を先に行う |
| 暗黙のOnline Learning | 通常会話から無断でWeightを更新しない |

## 12. 現在地

Local Runtime、Persistent Chat、RAG、Citation、Manual Web Evidence、Governance、Guardrail、Judge、回答修正、Agent／Tool基盤は実装済みである。

Phase 9-1では、独立Judge、Main Governance、Guardrail、Repair、Rejudge、Recordingを実Modelと実画面で接続できることを確認した。

現在はPhase 9-2で、これらを異なるVariantとして同じCaseへ適用し、結果とEvidenceを比較する仕組みを整えている。その後、Context圧縮と復旧、Project全体の文書・Runtime規約・UI統合へ進む。
