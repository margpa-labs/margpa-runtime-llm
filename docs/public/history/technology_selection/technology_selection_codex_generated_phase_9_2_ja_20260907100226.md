# MARGPA Runtime LLM 技術選定

```yaml
document_type: public_technology_selection
document_state: phase_9_1_complete_phase_9_2_in_progress
language: ja
project_initiated_at: 2026-07-18 17:46:37 JST
created_at: 2026-08-23
updated_at: 2026-09-07 09:54 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
current_phase: phase_9_2_in_progress
```

## 1. 選定方針

MARGPA Runtime LLMは、特定のModel、Cloud、検索方式、Agent Frameworkへ固定しない。

中心となる処理はDomainとPortで表し、Model Runtime、Storage、検索、Web、Frontendなどの外部技術をAdapterとして接続する。

技術選定では、機能の多さだけでなく次を重視する。

| 観点 | 判断基準 |
|---|---|
| 交換可能性 | ModelやLibraryを変更してもCoreを再実装しない |
| 独立性 | 不要なComponentをOFFにしても他の機能を利用できる |
| 観測可能性 | 設定、実行、評価、失敗を区別して追跡できる |
| 復旧可能性 | 再起動や中断後も会話と実験結果を読み直せる |
| Test容易性 | 外部接続や実Modelなしでも主要Contractを検証できる |
| Resource | 16GB Unified MemoryのMacで実行可能な構成を優先する |
| Data Control | Local Data、External Data、公開情報を分離する |
| Integrity | Digest、Revision、IdentityでArtifactを照合する |

## 2. 現在の主要技術

| 領域 | 技術 | 用途 |
|---|---|---|
| 言語 | Python 3.12〜3.13 | Domain、Application、Adapter、Backend、Test |
| 型と設定 | Pydantic／pydantic-settings | 型付きContract、Validation、Configuration |
| Local推論 | GGUF／llama.cpp／llama-cpp-python | Model Load、生成、Streaming、停止 |
| Web Backend | FastAPI／Uvicorn | REST API、SSE、Local Control Surface |
| Web Frontend | React 19／TypeScript／Vite | Chat、Settings、Evidence、Experiment UI |
| 永続化 | SQLite／JSON／Filesystem | Conversation、Citation、Run、Evidence |
| 検索 | BM25／HTML本文抽出 | Project Docs、Local Corpus、Public URL |
| Backend Test | pytest | Unit、Integration、Contract、実Model Smoke |
| Frontend Test | Vitest／Testing Library | Component、操作、状態遷移 |
| Static Analysis | Mypy／Ruff／TypeScript／ESLint | 型、Lint、Build前検査 |
| Package管理 | uv／npm | Dependency、Lock、Build、Test |
| Integrity | Canonical JSON／SHA-512 | Manifest、Digest、Revision、Evidence Identity |

## 3. Model Runtime

### 3.1 Main Model — Qwen3 4B

Qwen3-4B GGUF Q4_K_MをMac LocalのStartup Defaultとして使用する。

- 小型で起動しやすく、ChatとGovernanceの基準構成に適している。
- Context Size、出力Token上限、Model状態をRuntimeから変更・表示できる。
- Model品質とPlatform基盤の品質を分けて評価するBaselineとして使う。
- 別Modelの追加だけでStartup Defaultを自動変更しない。

Local macOS Profileでは、Main用Context Sizeを16,384に設定する。Dedicated RoleはMainと設定を共有せず、8,192の独立Contextを使う。

### 3.2 Judge Model — Gemma 4 E2B

Gemma 4 E2B Q4_0を、現在の軽量な独立Judgeとして使用する。

- Main Qwenとは異なるModel系列で評価できる。
- Main GovernanceがOFFでも単独でJudgeを実行できる。
- Judge OBSERVE、Judge ENFORCE、Repair後Rejudgeに同じAdapterを利用する。
- Configured、Active、Executed、EvaluatedのIdentityを分けて記録する。

GemmaのJSON出力安定化には、Judge専用のStructured Output Constraintを使う。llama-cpp-pythonの`LlamaGrammar.from_json_schema`Capabilityを実行時に確認し、Criterion BatchごとのSchemaをGrammarへ変換する。

Grammarを構築できない場合は通常生成へ戻さず、型付きFailureへ収束する。この制約はMain通常回答、Repair Candidate、Guardrail、RAG、Web、Agentへ波及させない。

SamplingはJudge Roleに限って決定的な値へ固定する。初回JudgeとRejudgeは同じSampling Contractを使う。

### 3.3 Guard Model — Qwen3Guard 0.6B

Qwen3Guard-Gen 0.6B Q8_0をDedicated Guardとして使用する。

- 入力、出力候補、Context Source、Streaming候補をTarget別に扱う。
- OBSERVEではDetectionを記録し、Actionを実行しない。
- ENFORCEではPolicyに応じて安全な拒否等を実行する。
- JudgeやMain GovernanceがOFFでも独立して利用できる。

Guardの検知精度とGuard Runtimeの成立は分けて扱う。現在の実装経路は成立しているが、正当な検証入力を過剰にBlockする場合があるため、分類精度とPolicyは継続調整対象である。

### 3.4 その他のModel

#### DeepSeek R1 Qwen3 8B

DeepSeek-R1-0528-Qwen3-8B Q4_K_MをMain Model候補として保持する。MainとしてのLoadと切替経路は存在するが、現在のDefaultにはしていない。

JudgeとしてはMain-shared Adapter扱いであり、Main QwenとDeepSeek Judgeを独立した組合せとして使うことはできない。Dedicated Judge化するかは後続判断とする。

#### Selene 1 Mini 8B

Selene 1 Mini Q5_K_MはDedicated Judge候補として登録済みである。現在のMacでは実用速度と同時Load時の安定性に課題があるため、保留としている。

#### 大規模Model

DeepSeek V4 Flash／Pro等は、GPU ServerまたはCloud向けの将来候補として分離する。Mac Localの必須構成には含めない。

## 4. Application Architecture

### 4.1 Domain／Port／Adapter

- DomainはFastAPI、React、llama.cpp、SQLiteへ直接依存しない。
- Application ServiceがUse Caseを構成する。
- Portが必要なCapabilityを定義する。
- AdapterがModel、Storage、Web、Filesystemを接続する。
- Web LayerがRequest、Response、SSE Eventへ変換する。

この構成により、外部Libraryの変更とDomain Ruleの変更を分離する。

### 4.2 Component Independence

Main Governance、Guardrail、Judge、Repair、Recording、RAG、Agent、Toolを別Componentとして扱う。

- OFFのComponentはModel Call、Mutation、Evidence、Authorityを発生させない。
- OBSERVEは判定を記録するが、回答を変更しない。
- ENFORCEは許可されたActionだけを実行する。
- Main Governance OFFでもJudgeを実行できる。
- Judge OFFでもGuardrailや通常Chatを利用できる。
- Guardrail OFFでもJudgeやMain Governanceを利用できる。
- 全Mode OFF後はDedicated ModelをUnloadし、通常Chatへ戻る。

意味評価TurnはRequest単位のLedgerで管理する。複数Turnが重なっても、Snapshot、Latest Pointer、Cancellation、Resultを別Requestへ混入させない。

### 4.3 Identity

次のIdentityを分けて保持する。

- 設定されたProvider。
- 現在有効なProvider。
- 実際に呼び出したProvider。
- 評価に使ったModelとArtifact。
- Conversation RequestとExperiment Request。
- Candidate、Repair、Rejudge、Presented Final。

Identityが一致しない場合は、実行前にCall 0で拒否するか、型付きFailureとして記録する。

## 5. Governance／Judge／Repair

### 5.1 意味評価

ARGD／DAGDから構成される109 CriterionをRuntimeへ接続する。Local実行では、1 Turnあたり32 Criterionを選び、残り77件をDeferredとして保持する。

実行したCriterionはPass、Deviation、Unknown、Not Applicableへ分類する。分類数とDeferred数の保存則を持ち、未評価をPassへ変換しない。

### 5.2 Budget

32 CriterionのRejudgeでは、1 Criterionあたり100 Tokenを見積もり、最大3,200 TokenをRejudgeへ割り当てる。Repair Candidate最大400 Tokenと合わせ、追加Budgetは3,600 Tokenとする。

Token、Context、Deadline、Cancellation、最大Call数はPlannerで事前確認する。条件を満たさない場合はModelを呼ばず、拒否理由を分けて記録する。

### 5.3 Repair

Repairは独立した常時実行機能ではなく、JudgeまたはMain Governanceからの要求で起動する。

```text
Candidate
→ Judge／Main Governanceの判定
→ Repair Candidate生成
→ 同じCriterionでRejudge
→ 採用または不採用
→ Presented Final
```

JudgeとMain Governanceの双方が要求した場合は`judge_and_main`として記録する。Repairが呼ばれたことと、修正結果が採用されたことを別の状態として保持する。

## 6. Experiment Runtime

Phase 9-2では`modules/experiment/`を新設し、既存のMain、Judge、Guard、Repairへ直接埋め込まずに比較実験を構成する。

### 6.1 IdentityとPersistence

- Experiment Plan。
- Case ManifestとCase Digest。
- Variant Configuration。
- Variant RunとRequest ID。
- Raw Evidence。
- Evaluation Observation。
- Comparison Report。

これらをFilesystemへ保存し、Process再構成後も読み直せるようにする。Terminal結果の二重Publishと、完了後に届くLate Resultを拒否する。

### 6.2 Evaluation

Freshness、RAG Grounding、Belief Revision、False Improvementを独立したCaseとして扱う。

Runが例外なく完了したことをCase PASSへ変換しない。実回答とEvidenceをClassifierへ渡し、PASS、FAIL、INCONCLUSIVE、UNAVAILABLEを分ける。

Human ReviewとLLM EvaluationはEvaluator Identityを分け、どちらが判定したかを保持する。

### 6.3 Production Variant

実験用FixtureとProduction実行を分離する。ProductionではVariantごとに必要な設定をFreezeし、実行前後のLive設定と照合する。

現在は、同一Plan内の異なるProduction Variantを安全に逐次実行するためのConfig Lease、Tri-state Evidence、Top-level Real Model Gateを調整している。

### 6.4 Minimal UI

Experiment画面では、Preset、Execution Mode、Plan、Variant、Run状態、Comparison、詳細Evidenceを表示する。

大規模な右側Trace PanelやSettings再編はPhase 10へ分離し、Phase 9-2では比較実験に必要な最小UIに限定する。

## 7. Data／Retrieval

- ConversationとCitationはSQLiteを正本とする。
- Project DocsとLocal Corpusを検索対象として分離する。
- BM25を現在の小規模Corpus向けBaselineとする。
- Source、Title、Path／URL、Chunk ID、Document Digestを保持する。
- Document更新後も、過去TurnのCitationを変更しない。
- Public URLは明示指定時だけ取得し、Untrusted External Contentとして表示する。
- Local CorpusはRevision、Soft Delete、Historical Evidenceを管理する。

EmbeddingとVector Databaseは、Corpus規模と検索品質が必要性を示した段階で比較する。

## 8. Frontend

React 19、TypeScript、Viteを使い、次を実装している。

- Persistent Chat List、再開、名称変更、Archive。
- Streaming、停止、再生成、Copy。
- RAG／Web EvidenceのCitation Card。
- Model、Context、Token、Provider状態。
- Governance、Judge、Repair、Recordingの設定と結果。
- Local CorpusとData Controls。
- Agent Run、Step、Approval、Completion。
- Experiment Plan、Run、Comparison、Evidence。

ServerをRuntime Stateの正本とし、Browserだけに重要状態を保持しない。Current TurnとHistorical Resultを分けて表示する設計を継続する。

## 9. Quality／Operations

- Backendは2,600件を超えるpytest Testを継続。
- Frontendは330件を超えるVitest Testを継続。
- Mypy、Ruff、TypeScript、ESLint、Vite Buildを検証工程に含める。
- Fixture、Production-fixture、実Model、実画面を別のEvidenceとして扱う。
- Criticalな境界ではSabotage-regressionによりTestの検出力を確認する。
- Handoff、Recovery、HistoryをAppend-onlyで保持する。
- 完了、未解決、保留、予約を別状態として管理する。

## 10. 現在選定していない方式

| 技術／方式 | 状態 | 理由 |
|---|---|---|
| MLX Runtime | 未選定 | 現行llama.cpp Adapterを先に安定化する |
| vLLM／SGLang | 将来候補 | GPU Server／Cloud向けとして分離する |
| LangChain／LangGraph | 未選定 | 現在は明示的なDomain／Port Contractを優先する |
| Vector Database | 保留 | 現在のCorpus規模ではBM25を優先する |
| Public Conversation Persistence | 未選定 | Privacy、Authentication、Retention設計を先に行う |
| 暗黙のOnline Learning | 未選定 | 通常会話から無断でWeightを更新しない |
| JSON後処理による緩い補修 | 未選定 | Judge SchemaとStrict Decodeの意味を弱めるため |
| 無制限Retry | 未選定 | LatencyとFailureの隠蔽を防ぐため |

## 11. Data／Deployment境界

- Model WeightをRepositoryへ含めない。
- Local Path、Conversation、Runtime Data、Credentialを公開情報から分離する。
- Network、Download、Git、Deploymentは通常のSource変更と別Authorityで扱う。
- Cloud接続はCost、Privacy、Security、Credentialを含む独立工程とする。
- 学習Dataは明示的な収集、Dataset、Run、Evaluation、Promotionを持つPipelineとして扱う。
- 将来の収集Dataは特定Modelへ閉じず、全Modelから利用できる共通構造を検討する。

## 12. 現在地

Phase 9-1で、Qwen Main、Gemma Judge、Qwen3Guard、Main Governance、Repair、Rejudge、Recordingを組み合わせた機械的な実行基盤が実画面で成立した。

Phase 9-2では、これらを同じCaseへ異なるVariantとして適用し、結果を比較するExperiment Runtimeを構築している。Core、Persistence、Evaluation、非同期Worker、Minimal UI、Production Adapterは実装済みであり、現在は複数Production VariantとEvidenceの最終整合を進めている。

