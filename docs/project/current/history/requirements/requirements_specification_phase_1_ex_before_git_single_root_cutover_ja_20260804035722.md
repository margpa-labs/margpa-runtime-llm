# MARGPA Runtime LLM 要件定義書

```yaml
document_id: requirements_specification
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-27 10:01:20 JST
owner: Nazuna Research
active_phase: phase_1_ex
rag_default: true
```

## 1. 目的

Hugging Face由来の事前学習済みOpen Modelを利用し、Model外部のRuntimeが推論、統治、監査、評価、修復、安全性および権限境界を扱う、Model非依存の対話型AI研究基盤を構築する。

本Projectは独自基盤Modelの事前学習を主張しない。小型Modelでも全体骨格を成立させ、将来の機材更新、Home ServerまたはCloud移行時にModel／Backendを交換して継続できることを優先する。

## 2. 最上位原則

- 単一責任、疎結合、依存性逆転、Port／Adapterおよび依存性注入を採用する。
- Model、Backend、UI、Storage、Governance Definitionおよび各機能Layerを交換可能にする。
- Framework固有処理を境界へ隔離し、CoreへOS固有Pathや外部SDKを埋め込まない。
- 初期構成は内部境界を明確にしたModular Monolithとする。
- Main Model以外の機能は個別に無効化でき、無効時にLoad、Call、WriteまたはSide Effectを行わない。
- Capability不足、無効な依存関係またはDegraded状態を黙って無視しない。

## 3. 対象利用

- AI研究、AI設計、AI実装
- 要件整理、Architecture、開発相談、Code支援
- 技術調査、一般的な質問、通常の雑談
- 将来のRAG、Agent、Tool、Judge、Guardrailおよび実験比較

## 4. 機能要件

### 4.1 Phase 1実装済み

- GGUF ModelのLoadとSHA-512検証
- Model Portおよび`llama.cpp` Adapter
- CLIによる一問一答、Streaming、停止、Generation Config
- `system／user／assistant` Message
- Model Capability／Deployment Profile／Runtime Observation
- Application共通設定とPlatform Profileの分離
- 回答言語`ja／en／auto`
- Thinking実行と表示の分離、Raw Thinking非保存
- FastAPIによる最小Web Preview
- Browser Memory内の一時的な複数Turn
- New Chat、Stop、Copy、最大生成Token数
- UI日本語／English切替と回答言語の独立
- Post-generation Summary Mode
- Completion後の安全なMarkdown表示
- Preview用Basic認証
- macOS MetalおよびLightning Linux x86_64 Pure CPU実行

### 4.2 Phase 1-ex

- DocumentationのCurrent／Phase／History／Public分離
- Phase 1文書のLossless Compilation再検証
- Phase 1-ex進行時点文書のInterim Lossless Compilation
- Current Canonical文書の累積再構築
- Git／GitHub公開準備、Identity／License／Terms整理
- 公開対象AllowlistとSanitation
- Local Mac用簡易Documentation RAGの要件・境界
- Mac限定RAGでも、将来Lightning／Home Server／CloudへAdapter追加できるPort Hookを持つ。
- LightningではPhase 1-ex中のRAG実装を強制せず、Public DemoではRAGをLoad／Callしない。
- Lightning Auto-start Read-only Preflight
- Basic Previewと分離したSide-effect-free Public Demo基盤
- Current／Publicの日本語正本
- 日本語正本と同粒度の英語派生版はPhase 1-ex後半で再判断する。
- Initial Commit前Documentation Refresh Gate

### 4.3 後続Phase

- Append-only Audit LogとSHA-512整合性
- Generic Governance Definition Platform
- ARGD／DAGDを利用可能なMain Governance
- Guardrail、Model Policy、Authority、Judge、Repair
- RAG、Source Traceability、会話履歴
- Agent、Tool、Memory、Handoff、Human Approval
- 複数GD、複数Model、実験Profile、定量／定性計算
- ML、Training、Model更新
- Responsive／Mobile UI
- Home Server／Cloud／Hybrid／Remote Backend

## 5. Governance要件

- Governance Definitionが0件でもCoreは正常動作する。
- ARGD／DAGDを含む固有GD名をApplication CoreへHard-codeしない。
- 全く未知の名称、Schemaまたは任意JSONを、明示Provider／Adapter／Compiler／Binding経由で扱える。
- JSONが存在するだけで自動実行しない。
- Governanceは`off／observe／enforce`を区別する。
- 共有Control Planeと分散Governance Pointを採用する。
- Rule Basedで処理可能な項目は決定論的に処理し、意味評価時だけModelを呼ぶ。
- Recommended ActionとExecuted Action、外部AuthorityとDefinition上の提案を分離する。
- Repair／Regenerateは回数、時間、Tokenおよび成功条件を持つ。

## 6. Layer切替要件

Main Model以外の各Component本体と、そのComponent専用Governanceを独立設定する。

```text
Main Governance
Guardrail／Guardrail Governance
Policy／Policy Governance
Judge／Judge Governance
Repair／Repair Governance
RAG／RAG Governance
Agent／Agent Governance
Tool／Tool Governance
Memory／Memory Governance
Status Reporting
External R&D Integration
```

無意味または危険な組合せはConfig Validationで拒否またはDegradedとして明示する。

## 7. Model要件

初期構成：

```text
Main:
  Qwen/Qwen3-4B-GGUF
  Qwen3-4B-Q4_K_M.gguf

Guard候補:
  Qwen3Guard-Gen-0.6B
  GGUF Q8_0または通常版

Judge候補:
  AtlaAI/Selene-1-Mini-Llama-3.1-8B
  GGUF Q5_K_Mまたは通常版
```

Guard／Judgeは初期常駐させず、必要性とResourceを確認してOn-Demand導入する。Model本体をGitへ含めない。

## 8. Platform要件

- Local既定：Apple M2 Pro、16GB、macOS ARM64、Metal
- External実証：Lightning AI Studio、Ubuntu Linux x86_64、Pure CPU
- 将来：Linux CUDA、Windows、AMD GPU、Home Server、vLLM、Remote API
- Platformは自動検出と明示Profileを組み合わせ、未対応環境をMacとして扱わない。
- Device／Backend／AccelerationはProfileとRuntime Observationで照合する。

## 9. 非機能要件

### 9.1 交換性

Port Contractを満たすAdapter交換でCore変更を最小化する。Model File名、Directory名またはGD略称をRuntime Semanticsにしない。

### 9.2 再現性

Python範囲、Dependency Version、Model ID、Artifact Digest、Quantization、Backend Version、Config SourceおよびDeployment Profileを記録する。

### 9.3 Resource

16GB Unified Memoryを基準とし、複数大型Modelの同時常駐を避ける。重いGovernance、Judge、SummaryおよびRepairは回数とBudgetを持つ。

### 9.4 Security／Privacy

- Credential、Secret、個人連絡先、実会話Log、Model本体を公開しない。
- Tool Permissionは決定論的Policyを正本とし、Model単独で権限を生成しない。
- 生のChain of Thoughtを永続保存しない。
- Public Previewと将来の本番Access Controlを区別する。
- Basic認証Previewと匿名Public Demoを別Access Profileとする。
- Public DemoはRate、Token、時間、入力、Generation BudgetをServer側で制限する。
- Public DemoではTool、RAG、Agent、外部I/O、永続化およびFile Writeを禁止する。
- 本Projectは動作、正確性、安全性、互換性または特定目的への適合性を保証しない。

### 9.5 Audit／説明

生の内部思考ではなく、System Traceと高水準の説明概要を分離して記録する。Turn、Model、Config、Definition、Rule、ActionおよびRepairを追跡可能にする。

### 9.6 Documentation

- File名は原則英語lower_snake_case、本文は日本語とする。
- Current／Publicは日本語正本`_ja`を持つ。英語派生版`_en`を作る場合は、日本語正本と同じ粒度を必須とする。
- 2026年7月27日時点では英語派生版を未作成とし、日本語正本の再構築を優先する。
- Phase／Shared／Historyは日本語のみとする。
- Current、Phase Compilation、Raw History、Publicを区別する。
- Historyは原則Immutableとし、Currentの変更前後をTimestamp付きAppend-only Development Logへ保存する。Git運用は未決定であり、将来Gitを採用してもGit HistoryをDevelopment Logの代替にしない。
- Lossless Compilationで決定、例外、未解決事項を削らない。

## 10. 初期対象外

- 独自基盤Modelの事前学習
- Fine-tuning、LoRA、DPO、RLHF
- Image入力
- Microservices化
- SQL必須化
- 複数大型Modelの常時同時Load
- 全GDの同時Prompt投入
- 自動的なTool権限生成

## 11. 受入原則

- 要求機能が実際に動く。
- Module単位で無効化、交換およびTestができる。
- Capability不足とErrorが観測可能である。
- Localと外部環境で同じCore Contractを維持する。
- 構成差、Cost、Latency、品質およびGovernance結果を将来再現可能に比較できる。

## 12. Traceability

- [System Architecture](../architecture/system_architecture_ja.md)
- [Basic Design](../architecture/basic_design_ja.md)
- [Runtime Governance Specification](../governance/runtime_governance_specification_ja.md)
- [Phase 1 Requirements Compilation](../../phases/phase_1/requirements/phase_1_requirements_ja.md)
- [Phase 1-ex Requirements](../../phases/phase_1_ex/requirements/documentation_migration_and_canonical_content_requirements_ja.md)
- [Public Demo／Auto-start／Pre-release Requirements](../../phases/phase_1_ex/requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)

## 13. Project制約と優先順位

### 13.1 初期Hardware制約

初期の継続開発環境は次のとおりである。

```text
Device       : MacBook Pro Mac14,9
SoC          : Apple M2 Pro
CPU          : 10 Core
GPU          : Apple Integrated GPU
Memory       : 16GB Unified Memory
Architecture : Apple Silicon／ARM64
Acceleration : Metal
CUDA         : 使用不可
```

OS、Model、KV Cache、RAG、Web、Auditおよび将来のGovernanceが同じ16GBを共有する。したがって、初期版では複数大型Modelを常時同時Loadせず、Main Model以外はOn-Demandまたは後続Phaseで追加する。

### 13.2 優先順位

1. 要求機能が一通り実際に動くこと
2. Moduleが分離・交換可能であること
3. Governance、Audit、説明、評価およびRepairが成立すること
4. 現在のMacで動作すること
5. GitHubへ成果物として提示できること
6. 推論速度
7. Context長
8. Model単体の回答品質

小型Modelの能力不足は許容する。ただし、Model能力不足とRuntime／Governance／UIの不具合を混同せず、後からModelだけを交換できる契約を維持する。

### 13.3 Prototype境界

本Projectは本番Serviceではなく、設計と主要機能を一通り成立させる研究開発Prototypeである。将来の本格運用では、GPU Server、AWS／Azure等のCloud、vLLM、PostgreSQL、Container、外部監査基盤およびMulti-user Access Controlを再評価する。

## 14. Model Runtime詳細要件

### 14.1 Model Port

Model Adapterは最低限、次を共通Contractとして提供する。

- Load／Close
- Chat Message入力
- Chat Template選択
- Streaming／Non-streaming
- Cooperative Cancel
- Generation Config
- Context Limit
- Stop Sequence
- Seed
- Token Usage
- Stop Reason
- Model Metadata
- Capability申告
- Device／Acceleration Observation

Backend固有のTokenizer、Grammar、JSON Schema、Logit Bias、Token Probability、Native Tool Calling等はCapabilityとして申告し、未対応を黙って成功扱いしない。

### 14.2 Model Artifact

- Model FileはRepositoryへ含めない。
- Model RootとRegistry上のRelative Artifact Pathから解決する。
- File名だけをModel IdentityまたはRuntime Semanticsにしない。
- Model ID、Upstream、Distribution Repository、Revision、Artifact Size、Format、Quantization、SHA-512、BackendおよびBackend Versionを記録する。
- Registryが期待するArtifactと実際にLoadするArtifactの不一致はFail Closedとする。
- Hash検証を有効にした場合、不一致ArtifactをLoadしない。

### 14.3 Generation

- Default最大生成Token数は当面2048とする。
- UIおよびCLIから範囲検証済みOverrideを可能にする。
- Thinkingを有効にした場合、最終回答生成前にToken上限へ到達し得る。
- 最終回答が生成される前に上限へ到達した場合、将来は「最終回答を生成する前にToken上限へ到達しました」と観測可能にする。
- Cancel、Token Limit、Natural Stop、Backend Errorを区別する。
- 同一Model Runtimeの同時Generation上限は1を既定とし、競合時は`model_busy`として安全に拒否する。

### 14.4 Thinking

- `generation.thinking_mode`と`presentation.thinking.visibility`を分離する。
- Thinking GenerationがOFFの場合、VisibilityだけをONにできないか、表示対象がないことを明示する。
- Thinking表示LabelはPresentationであり、Model ProtocolのDelimiterと分離する。
- Raw Thinkingは既定で保存しない。
- Thinking表示は内部推論の完全性、正確性または真のModel内部状態を保証しない。
- 一般利用者向けDefaultはGeneration OFF／Visibility Hiddenとする方向を維持する。

### 14.5 Response Language

- 回答言語は`ja／en／auto`を選択できる。
- UI表示言語とは独立する。
- Language指定はModelへの指示強化であり、Model出力を完全保証しない。
- System／User文脈の衝突時は、適用Sourceと最終Effective Configを観測可能にする。

## 15. Conversation／UI詳細要件

### 15.1 Current Preview

Phase 1のWebは少人数検証用Previewであり、次を提供する。

- Browser Memory内の一時的な複数Turn
- New Chat
- Streaming表示
- Stop
- Send
- `Cmd+Enter`／`Ctrl+Enter`送信
- UI日本語／English
- 回答言語`ja／en／auto`
- 最大生成Token数
- Thinking Generation
- Thinking Visibility
- Summary Mode
- User／Assistant Message Copy

Browser Reloadでは会話とRuntime Optionを既定値へ戻す。永続Conversation、Chat List、Resume、Regenerate、Branchおよび削除はPhase 2以降とする。

### 15.2 Presentation

- Streaming中はPlain Textとして安全に表示する。
- 完了後はSanitize済みMarkdownへ変換する。
- Raw HTML、Script、Event Handlerおよび危険URL Schemeを拒否する。
- Markdown変換失敗時はPlain TextへFallbackする。
- CopyはCanonical User TextまたはFinal Answerだけを対象とする。
- Hidden Thinking、内部MetadataおよびSummary Modeで非表示のOriginal AnswerをCopyへ混入させない。

次は後続UI Phaseで扱う。

- Streaming中の段階的Markdown Rendering
- Table表示改善
- Code FenceのLanguage別表示
- Code Block単位Copy
- User MessageとAssistant Messageの視覚分離
- Input Folder追加／Drag-and-drop
- Mobile／Responsive UI
- Enter誤送信を避ける送信方式

### 15.3 Summary Mode

- Summary Modeは明示的`OFF／ON`とする。
- Original Generation完了後、同じMain ModelをSequentialに再利用する。
- Summary成功時はSummaryだけをUserへ返す。
- Summary失敗時はOriginalへFallbackする。
- Summaryは詳細、前提、注意事項を省略・変形する可能性がある旨を表示する。
- Summary CallにはOriginal Generationと独立したToken Budgetを持たせる。

## 16. Configuration／Switchboard要件

### 16.1 Source優先順位

```text
Built-in Default
  < Application Config
  < Deployment Profile
  < Environment
  < Explicit CLI／Request Override
```

各値について適用Sourceを追跡し、`model-info`または将来UIでEffective Configを表示する。

### 16.2 Component Mode

Main Model以外のComponentと各Governance Pointには、最低限次を持たせる。

```text
enabled = true／false
mode = off／observe／enforce
profile
required_dependencies
optional_dependencies
timeout
budget
failure_policy
```

単純なBooleanだけでなく、判定だけを行う`observe`と、停止・修復等を実行する`enforce`を比較できるようにする。

### 16.3 Invalid Combination

- `Agent OFF／Agent Governance ON`等の無意味な構成を検出する。
- `Judge OFF／Judge依存Repair ON`等は、代替Evidenceの有無に応じて拒否またはDegradedとする。
- Runtime変更可能な設定とRestart必須設定を区別する。
- 無効な組合せを黙って自動修正しない。

### 16.4 UI設定階層

一般利用者向け基本設定は、Model、回答言語、New Chat等の最小項目とする。

その他は「研究・開発者モード」でまとめて表示し、同Mode自体をON／OFF可能にする。

- Generation Parameter
- Layer別ON／OFF／Mode
- Governance Profile
- Judge Threshold
- Repair回数
- Timeout／Budget
- Logging／Evidence
- Backend固有設定
- 定量計算モード
- 定性計算モード

研究・開発者モードはSecurity Boundaryまたは権限昇格手段ではない。

## 17. Deployment／Cross-platform要件

### 17.1 Profile Resolution

- OS、Architecture、Execution Environment、Compute、Vendor、Acceleration、Backend Build Variantを別Fieldで表現する。
- macOS以外をDefaultでmacOS ProfileへRoutingしない。
- 明示Profile、Environment Hint、Platform Defaultの優先関係を定義する。
- 未対応Platformは明示Errorとし、誤ったProfileへ黙ってFallbackしない。

### 17.2 Verified Environment

```text
Mac:
  macOS／ARM64／Apple M2 Pro／Metal
  Python 3.13.14

Lightning:
  Ubuntu 24.04系／Linux x86_64／Container
  Intel Xeon系 4 vCPU／約15GiB RAM
  Python 3.12.11
  Pure CPU llama.cpp
```

Lightningでは、`.venv`をProject直下に構築し、Studio既定Conda環境をProject Environmentとして再利用しない。`uv 0.11.29`はProject用固定Tool Pathから使用する。

### 17.3 Basic PreviewとAuto-start

- Basic PreviewはBasic認証付き手動LifecycleとしてAcceptedである。
- CredentialはManaged SecretsまたはEnvironmentから取得し、Repositoryへ保存しない。
- `start／status／restart／stop`は手動Terminal用とする。
- 前景`run`はPlatformがProcess Lifecycleを所有するEntrypointとする。
- Traffic-aware Wake-upは、第三者がURLを開いた時にSleeping Studio／Serviceが起動できることを実機で確認するまで成立扱いにしない。
- Stage A／BのRepository Preparation完了を、Platform上のWake-up成功と混同しない。

### 17.4 Public Demo

匿名Public Demoを将来有効化する場合、Basic Previewと別Profile／Policyにする。

- 認証なし
- Rate Limit
- Input／Message／Token／Time／Concurrent Request上限
- Global Cost／Credit保護
- Tool OFF
- RAG OFF
- Agent OFF
- External I/O OFF
- File Write OFF
- 永続Conversation OFF
- Secret非使用
- 安全なError Response

2026年7月27日時点では未実装・未公開である。

## 18. Documentation／Task Governance要件

### 18.1 Directory

```text
docs/project/current/
  現在のCanonical正本

docs/project/phases/
  Phase Stable、Lossless Compilation、Raw History、Index

docs/project/shared/
  共通規則、運用、権限、Recovery

docs/public/
  対外説明文書とPublic History
```

### 18.2 StableとHistory

- Stable文書はTimestampなしの固定名を使用する。
- Stable変更前の原文を対応`history/`へ保存する。
- 更新後の完全原文もHistory Snapshotとして保存する。
- Timestampを付けるのはHistory SnapshotとEvent Artifactだけとする。
- Git HistoryをAppend-only Development Logの代替にしない。
- User許可なくDocumentation運用を変更しない。

### 18.3 Lossless Compilation

- PhaseごとのSource SetをFreezeする。
- Path、Size、SHA-512およびStateを記録する。
- Source本文を改変せず収録する。
- CompilationからSourceを再抽出できる。
- 再抽出結果のByte SizeとSHA-512が1件でも不一致ならFail Closedとする。
- Phase 1-ex進行中CompilationはInterim／Current-to-dateと明記し、Phase完了版と偽らない。

### 18.4 Task Role

- 設計統括者役はProject全体、Phase、Review、Documentation運用を統括する。
- Phase別設計者役は、設計統括者役のPhase設計を受け、要求変更の範囲内で詳細化する。
- 実装者役はSource、Test、ScriptおよびStatusを担当し、Canonical要件・設計を勝手に編集しない。
- 対外Docs役は公開文書を担当し、Canonical正本の意味を変えない。
- 設計統括者役Taskを新規作成しても即時復元できるRecovery Packageを各Phase完了・Backup直前に作成する。

## 19. Audit／Evidence詳細要件

一往復のUser InputからAssistant Outputまでを基本単位とし、将来次を構造化保存する。

- Schema Version
- Session／Turn／Request／Message ID
- Timestamp
- User Input
- System／Developer／Runtime Context
- Modelへ渡したMessage列
- Model ID／Revision／Artifact Digest
- Quantization／Backend／Backend Version
- Generation Config
- Output／Stop Reason／Error
- Token Count／Latency
- Governance Definition／Version／Digest
- Compiled Plan／Applied Rule
- State Before／After
- Dimension Score／Deviation／Severity
- Recommended Action／Executed Action
- Repair／Regenerate／Rebind
- Guardrail／RAG／Tool Call
- High-level Explanation

PayloadはCanonical JSONへ正規化し、`integrity`を除いたPayloadへSHA-512を適用する。UTF-8、Key順、Whitespace、Unicode Normalization、Number表現およびCanonicalization方式をSchemaとして固定する。

SHA-512単体はPayloadとDigestの同時改変を防止しない。将来、Hash Chain、HMAC、Digital Signature、Append-only Storage、WORM、Merkle TreeまたはExternal Timestampを追加可能にする。

## 20. Evaluation／Repair要件

### 20.1 User Evaluation

- Rating
- Comment
- 問題Tag
- Regenerate
- 修正要求
- 修正前後比較

問題Tag候補：

- 前提逸脱
- 根拠不足
- 文脈喪失
- 矛盾
- 過剰一般化
- 過剰肯定
- 過剰否定
- 不要な確認
- 出典不足
- 不確実性未開示

過去回答を削除または上書きせず、Evaluation／Repair Eventとして関連づける。

### 20.2 LLM-as-a-Judge

- JudgeはMain Modelと独立Componentとする。
- Judge Model、Prompt、Criteria、Threshold、Seed、EvidenceおよびCostを記録する。
- Judge出力を事実または最終Authorityとみなさない。
- Self-evaluationと独立Judgeを区別する。
- False Positive／False Negative、Over-refusal／Under-refusalを評価する。
- JudgeなしBaselineと比較可能にする。

### 20.3 Repair

- RepairはJudgeだけに依存しない。
- Rule、User Feedback、Guardrail、Governance Deviation等のTriggerを識別する。
- Max Attempt、Max Time、Max Token、Max Total Callを持つ。
- Repair成功条件を事前に定義する。
- 失敗時は元回答と全AttemptをEvidenceとして保持する。

## 21. RAG／Agent／ML要件

### 21.1 Documentation RAG

初期簡易RAGはMac限定で実装してよい。ただし、Document Source、Chunker、Embedding、Index Store、Retriever、Context AssemblerおよびCitationをPort化し、Lightning／Home Server／CloudへAdapter追加可能にする。

`docs/`が存在しない場合は、推測で補わず「docsが設置されていないため参照できません」と明示する。Raw HistoryをDefault Corpusへ無差別投入しない。

### 21.2 General RAG

- Local Document登録
- Chunking
- Embedding
- Index
- Retrieval
- Context Injection
- Source表示
- Document更新
- RAG ON／OFF
- Query／Model／Retriever／Index／Document／Chunk／Score／Hash／Citation記録

### 21.3 Agent

- Tool Registry
- Tool Selection
- Multi-step Execution
- Planning／Observation／Replanning
- State／Memory／Handoff
- Completion Check
- Human Approval
- Max Step／Time／Retry
- Side Effect確認
- Infinite Loop防止
- 全Tool Call Audit

AAGDが実行過程を統治しても、Tool Permissionまたは外部実行権限を生成しない。

### 21.4 Machine Learning

ML／Training／AdaptationはPhase後半のOptional Componentとして追加する。

- Training Data Lineage
- Base Model／Candidate Model分離
- Fine-tuning／LoRA等のMethod識別
- Evaluation Set
- 定量計算モード
- 定性計算モード
- 両者併用
- Promotion／Rollback
- Weight／Config／Dataset／Code Digest

User Conversationから暗黙Online LearningをDefaultにしない。

## 22. External Original R&D統合要件

Phase 10以降に、MARGPA Runtime LLM本体完成後の独立R&Dとして次を疎結合接続できるようにする。

### 22.1 EASA

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構
Research Area: AI Safety Governance
```

Model内部に形成された安全傾向、周辺安全制御およびComposite Safety Behaviorを、単一の物理Layerと断定せず作業概念として扱う。Coreへ固有Algorithmを埋め込まず、Generic External Governance ProviderとしてDefault OFFで接続する。

### 22.2 DLAGSA

```text
DLAGSA
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構
Research Area:
  Multi-Agent Governance,
  Distributed Accountability,
  and Safety Assurance
```

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う。単純な複数AI並列化、単一Filterまたは単一Log機構として扱わない。

### 22.3 OCILNS

```text
OCILNS
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
Research Area:
  Cognitive Interaction Provenance,
  Verifiable Dialogue Ledgers,
  and Cross-System Continuity
```

人、AI、Toolおよび外部System間の対話を、検証・参照・継承・監査可能な証跡単位として扱う。特定LLM Provider、Storage、UIまたはCloudへ依存しないGeneric Evidence Ledger Portとして接続する。

### 22.4 共通境界

- Default OFF
- 個別ON／OFF
- Provider不在でもCore動作
- OFF時Zero Load／Zero Call／Zero Write／Zero Side Effect
- Capability／Schema／Version／Digestを明示
- Failure Isolation
- Access Control／Authority／Policyを上書きしない
- 固有名称をCore Routing条件にしない

## 23. Publication／Legal要件

### 23.1 Public Identity

```text
Organization／Repository Owner : margpa-labs
Public Author／Research Name    : Nazuna Research
Repository                     : margpa-labs/margpa-runtime-llm
```

公開対象では、本名、個人用Profile、LinkedIn、職務経歴書、個人連絡先、Local User Name、Mail Addressおよび不要な絶対Pathを削除または匿名化する。

### 23.2 Initial Access Terms

初期公開は次を前提とする。

- GitHub上のSource／Docsは閲覧・評価のみ許可する。
- それ以外の複製、改変、再配布、商用利用等は明示許可がない限り禁止する。
- Hosted Demoが公開された場合、その画面上での試用は許可する。
- Hosted Demoの利用許可はRepository Sourceの利用許諾を意味しない。
- ある程度以上完成した時点でOSS化を再検討する。

最終条文は`LICENSE`、`TERMS_OF_USE.md`および`NOTICE.md`を相互整合させる。

### 23.3 Warranty

READMEと利用条件文書へ、動作、可用性、継続性、互換性、正確性、安全性、特定目的適合性を一切保証しない旨を明記する。

研究目的で各ComponentをOFF／ONできるため、無効化により検査、制御、Repair、Evidenceまたは安全性が失われ得ることを留意事項として示す。

### 23.4 Public Artifacts

- `README.md`
- `LICENSE`
- `TERMS_OF_USE.md`
- `NOTICE.md`
- `CITATION.cff`
- `docs/public/overview_ja.md`
- `docs/public/concept_ja.md`
- `docs/public/roadmap_ja.md`
- Current Canonical日本語正本
- Demo画像6件

READMEでは、現在のUI画像を相対Pathで掲載し、現在の軽量Model／Hardware制約と将来の高性能Model交換予定を示す。現在機能だけでProject価値を判断されないよう、Roadmapへの導線を強調する。

## 24. Current Acceptance Gate

2026年7月27日時点の状態：

```text
Phase 1                              : Complete／Accepted
Phase 1 Backup                       : Complete／Verified
Mac Metal Runtime                    : Accepted
Lightning Pure CPU Runtime           : Accepted
Lightning External Basic Preview     : Accepted
Phase 1-ex                           : In Progress
Docs Directory Migration             : Complete／Validated
Docs Reconstruction Source Inventory : 499／499 PASS
Current Canonical Reconstruction      : In Progress
Phase 1 Lossless Reconstruction       : Pending
Phase 1-ex Interim Lossless           : Pending
Public Docs／README／Legal             : Pending
Traffic-aware External Wake Trial     : Manual Validation Waiting
Anonymous Public Demo                : Not Implemented／Not Public
Git／GitHub                           : Not Started
```

Phase 1-exは、次を満たすまで完了扱いにしない。

1. Current、Shared、PublicおよびPhase CompilationがSource Inventoryへ追跡可能である。
2. Project ContinuityとRoadmapを第1周・第2周の両方で確認する。
3. History SnapshotとStable本文が一致する。
4. Phase 1 Losslessから全Sourceを再抽出できる。
5. Phase 1-ex Interim Losslessが作成時点までの全Sourceを含む。
6. README、利用条件、Roadmap、Current Stateが矛盾しない。
7. Secret、Credential、PII、不要な絶対Path、Model Weightを公開対象へ含めない。
8. Git操作は別途設計・承認されるまで行わない。
