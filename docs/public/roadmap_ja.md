# MARGPA Runtime LLM Roadmap

```yaml
document_type: public_roadmap
document_state: current
language: ja
created_at: 2026-07-22
updated_at: 2026-08-11 13:27:41 JST
public_author: Nazuna Research
project: MARGPA Runtime LLM
```

## このRoadmapを最初に読んでほしい理由

MARGPA Runtime LLMの現在の実装だけを見ると、小型のオープンモデルをローカルまたはクラウド環境で動かす、比較的シンプルな対話型LLMに見える。

しかし、このProjectの目的は「新しいChat UIを一つ作ること」でも、「既存モデルをローカルで動かすこと」でもない。

目指しているのは、Model、Guardrail、Policy、Judge、Repair、RAG、Agent、Tool、Memory、Audit、Governance Definitionをそれぞれ独立したComponentとして扱い、その前後に必要なGovernance Pointを配置し、構成差による品質・安全性・Cost・Latency・証跡を再現可能に比較できるRuntime Governance型AI研究基盤である。

現在の小さなRuntimeは最終成果物ではない。

> 現在のRuntimeは、後半Phaseで統治・監査・評価・修復・Agent実行・複数Governance・外部R&D機構を接続するための、最初の交換可能な骨格である。

このProjectの独自性は後半Phaseへ進むほど明確になる。本Roadmapは、現在動く範囲だけでは見えない最終像と、そこへ至る設計上の順序を公開するための中核文書である。

---

## 1. 最終的に作ろうとしているもの

MARGPA Runtime LLMは、次の性質を同時に持つPlatformを目指す。

### 1.1 Model非依存

- ModelをApplication Coreへハードコードしない。
- GGUF／llama.cpp、MLX、Transformers、vLLM、Remote API等をAdapterで交換可能にする。
- Local MacからHome Server、GPU Server、Cloudへ移行してもCoreを作り直さない。
- Main、Guard、Judge等の論理的役割と、実際にLoadするArtifactを分離する。

### 1.2 Governance Definition非依存

- ARGD、DAGDを含め、特定のGD名やSchemaをCoreへハードコードしない。
- Governance Definitionが0件でもRuntimeを正常に動作させる。
- 全く未知の名前、未知のSchema、任意のJSON、Custom Providerを受け入れられる拡張境界を持つ。
- JSONが存在するだけで自動実行せず、Provider、Manifest、Descriptor、Trusted Adapter、Compiler、Bindingを通す。

### 1.3 共有Control Planeと分散Governance Point

一つの巨大なGovernance Layerですべてを直列管理せず、各Layerに完全なGovernance一式を複製することもしない。

```text
Governance Control Plane
  ├─ Definition Provider／Registry
  ├─ Validator／Adapter／Compiler
  ├─ Activation／Rule Selection
  ├─ State Namespace／Evidence
  ├─ Evaluator／Budget
  ├─ Conflict Resolution
  └─ Action Resolver

Execution Pipeline
  ├─ Input Governance Point
  ├─ RAG Governance Point
  ├─ Guardrail Governance Point
  ├─ Policy／Authority Governance Point
  ├─ Agent Governance Point
  ├─ Tool Governance Point
  ├─ Judge Governance Point
  ├─ Main Model Governance Point
  └─ Output／Repair Governance Point
```

各Pointは、その場所に必要なRuleだけを受け取る。決定論的に評価できる処理はRule Engineで行い、意味的評価が必要な場合だけModelを呼ぶ。

### 1.4 すべてを比較できる研究装置

Main Model以外の任意Componentを個別に有効化・無効化できる構造を目指す。

Governanceは単純なON／OFFだけでなく、次のModeを区別する。

```text
off     : Governanceを実行しない
observe : 評価と記録だけを行い、処理へ介入しない
enforce : 登録済みActionの範囲で停止、制約、修復等を行う
```

これにより、同一のInput、Model、Seed、Configで次を比較可能にする。

- Governanceなし
- Governanceの観測のみ
- Governanceによる介入あり
- Guardrailのみ
- Judgeのみ
- Repairあり／なし
- RAGあり／なし
- Agentあり／なし
- 単一GD／複数GD
- Local Model／Cloud Model
- 軽量Profile／詳細Profile

目標は「疎結合に作った」という構造上の説明ではない。

> どの構成が、何を改善し、何を悪化させ、どれだけのCostとLatencyを生んだかを、証跡とともに再現可能に比較できる状態を作る。

---

## 2. Development Progression

本Projectは、次の順番で能力を積み上げる。

| 段階 | Runtimeが新たに獲得する能力 |
|---|---|
| Foundation | Modelを交換して実行できる |
| Portability | OS、Backend、Accelerationを交換できる |
| Observability | 何が実行されたかを追跡できる |
| Definition Platform | 任意のGovernance Definitionを安全に受け入れられる |
| Main Governance | Main Modelの入出力を観測・統治・修復できる |
| Distributed Governance | Guard、Judge、Repair等を個別に統治できる |
| Grounded Knowledge | RAGとData Sourceを証跡付きで扱える |
| Agentic Execution | Tool、Memory、Handoff、副作用を統治できる |
| Multi-Governance Research | 複数GDと構成差を実験・比較できる |
| Learning and Adaptation | ML、Training、Model更新、定量／定性計算を証跡付きで扱える |
| External R&D Integration | 例外、安全、責任、認知対話証跡を外部研究機構と接続できる |

---

## 3. Status Legend

| State | 意味 |
|---|---|
| `Complete／Accepted` | 実装と独立Reviewが完了している |
| `In Progress` | 要件と実施範囲が確定し、現在作業中である |
| `Repository Accepted` | Repository実装は受入済みだが、対象外部環境での実測が残る |
| `Validation Waiting` | 実装済みだがUserまたは外部環境の受入が残る |
| `Accepted Reservation` | 要件・方向性は決定済みだが、実行を開始していない |
| `Planned` | 現行Roadmapに含むが、詳細Gate前である |
| `Future R&D` | 本体の主要機能完成後に統合する独立研究領域である |

FutureまたはPlannedと書かれた項目は、実装済みを意味しない。

---

## 4. 現在地 — Phase 2 Started／Phase 2-0 Initial Pilot Evidence／Restart Gate

2026年8月11日時点の現在地は次のとおりである。

```text
Phase 0                               : Complete
Phase 1-A～1-I                        : Complete／Accepted
Phase 1-F Mac Metal Runtime           : Complete／Accepted
Phase 1-F Lightning Pure CPU Runtime  : Complete／Accepted
Phase 1-G Minimal Web Surface         : Complete／Accepted
Phase 1-H Summary Mode／UI Language   : Complete／Accepted
Phase 1-I Web Presentation／UX Follow-up: Complete／Accepted
Mac Web User Acceptance               : Passed
Combined Manual Edge Tests            : Passed
Lightning Pure CPU Full Test Suite    : Passed
Lightning External Browser Acceptance : Passed
Lightning External Basic Preview      : Published／Basic Auth／Traffic-aware Auto-start
Lightning Basic Preview Lifecycle     : Complete／Accepted
Phase 1 Cross-environment Final Review: Complete／Accepted
Phase 1 Completion Declaration        : Complete
Phase 1 Confirmed Backup              : Complete／Verified
Phase 1-ex                            : Complete／Accepted
Docs Directory Migration              : Complete／Validated
Docs Reconstruction Source Inventory  : Complete／Validated
Canonical／Shared／Public Set         : Complete／Validated
Lightning Auto-start Stage A／B       : Complete／Accepted／GO
Traffic-aware External Wake Trial     : Passed／Repeated Wake／Sleep Confirmed
Observed Lightning Cold Start         : Approximately 3–10 Minutes
Anonymous Public Demo Surface         : Complete／No Auth／Traffic-aware Auto-start
Mac Documentation RAG                 : Complete／Manual Acceptance Passed
Lightning Basic Preview Public-doc RAG: Complete／Manual Acceptance Passed
Lightning Public Demo Public-doc RAG  : Complete／Manual Acceptance Passed
Documentation RAG Answer Quality      : Functional／Known Tuning Limitations Deferred
Git Workflow／Git Initialization      : Complete／Operational／Single Canonical Root
Pre-Git GitHub Preparation            : Complete／Direct Upload Path
GitHub Publication                    : Complete／Git History Preserved／main Aligned
Phase 1-ex Final Test                 : 430 Passed／3 Deselected
Phase 2                               : Started
Phase 2-0 Initial Bounded Pilot       : Executed／Safety Pass／Recovery Fail
Phase 2-0 Role／Docs Authority Design : Corrected／Three-point Review Passed
Phase 2-0 Automation Control State    : PAUSED／Restart Package Review Completed
Phase 2-0 Authorization Envelope      : draft-4／Not Accepted／Freeze Pending
Phase 2-0 Independent Task            : Initial Task Idle／Replacement Task Not Created
Phase 2-0 Git Checkpoint              : Content Commit f21829f Pushed／Local・Origin・Remote Aligned
Phase 2 Functional Implementation     : Not Started
Optional English Documentation        : Formally Deferred／Non-blocking／History Excluded
```

現在、MacではQwen3-4B GGUFを用いたCLIと最小Web Previewが動作する。Streaming、生成停止、一時的な複数Turn、回答言語切替、要約モード、UI日本語／英語切替、Thinking生成／表示分離、安全なCompletion MarkdownおよびMessage Copyを実装済みであり、Mac Web Manual Acceptanceも合格した。

Lightning AI Studioでは、Ubuntu 24.04系Linux x86_64 Container、Python 3.12.11、Pure CPU Backend、Qwen3-4B GGUFを用いた環境再構築、Environment Verification、Full Test Suite、Model Acceptance、外部BrowserからのBasic Preview、生成、停止、New Chat、Language、Summary、Thinking、Copy、Busy表示およびLifecycle操作を確認した。Basic Previewは認証付きのPreview環境としてAcceptedであり、Sleeping Studioに対する外部URL AccessだけでのTraffic-aware Wake、同一URLの維持、Managed Secrets変更、旧Credential拒否、新Credential認証、LLM利用およびIdle Sleepへの再移行も実機で確認した。認証なしPublic Demo SurfaceもBasic Previewから分離して成立し、両Surfaceで公開8文書だけを対象とするDocumentation RAGをDefault OFFのまま利用できることを確認した。

Phase 1とPhase 1-exは完了した。Phase 1-exでは、Docs Directory Migration、Canonical／Shared／Public正本、Phase単位Lossless、二種のRecovery Handoff、Git History継承、単一Canonical Git Root、Public Demo、Traffic-aware Auto-start、Mac／Lightning Documentation RAG、公開SanitationおよびPhase Backup契約を整備した。Gitの通常Commit／Push経路は成立済みであり、Git操作そのものは今後も対象ごとのユーザー明示承認を必要とする。

Phase 2はユーザー確認により開始し、元来の機能実装に先立つPhase 2-0 Document-driven Orchestration Pilotの初回有界Work Unitを実施した。Task作成、Exact Title設定、Handoff、Read-only Recovery Assessmentおよび停止境界のSafetyは成立した一方、全文Recoveryは不合格となり、結果を`Safety Pass／Recovery Fail`として記録した。再試験設計では、通常運転とAutomationで共通のRole／Docs Authorityを用い、Automation側には承認済み到達線内の連結実行だけを追加する構造へ修正した。固定Document Package、独立Dynamic Resolverおよび最高責任者役への判断集中を採用せず、各Role／Taskが委譲範囲内を都度判断し、例外を直属上位へ段階的にEscalateする。

Role-local Judgment、Tiered Escalation、Authorization Envelope投影およびTask作成／Handoff／Status Authority分離のCorrection Reviewは合格した。ユーザーによる大規模Backupも完了している。本状態のDocs CheckpointはCommit `f21829f`として`origin/main`へPushし、Local／Tracking／Remoteの一致を確認した。現在は`PAUSED`であり、draft-4／Role View／Manifest／Freeze Receiptの確定、ユーザーAcceptance、Controller READY／`ARMED`および後続User Start／`ON`を順序どおり必要とする。初回TaskはIdle、再試験用Taskは未作成、Phase 2機能実装は未開始である。

Lightning Auto-startは、Repository側Read-only Preflight、Stage A、Stage B Repository Preparation、Repository外Private Bootstrap、Manual Foreground起動および複数回のTraffic-aware External Wake実試験を完了し、Basic Previewと認証なしPublic Demoの双方で成立した。観測Cold Startは約3～10分、Idle-to-sleepは約10～12分である。一度だけJSONらしき一時応答が表示されたが、再Accessで正常復帰し、再現未確認の非ブロッカー観察事項としている。これらはFree CPU Studioでの観測値であり、SLAまたは将来環境の性能保証ではない。Public Control Hookは保持するが、Rate Limit、Token／Cost保護等は現在OFFである。Tool／外部操作は搭載せず、Documentation RAGは公開8文書だけに限定してBasic PreviewとPublic Demoの双方で利用可能とした。

現行のQwen3-4Bは、Apple M2 Pro／16GBと外部無料枠の制約下でRuntime骨格を成立させるための軽量Modelであり、最終性能Targetではない。高性能GPU、Home ServerまたはCloud環境を利用可能になった段階で、Model Adapter契約を維持したまま高性能Modelへ交換・追加する。

---

## 5. Phase 0 — Requirements and Foundation Design

**State: `Complete`**

Project全体の土台を定義するPhase。

### 主な成果

- Project目的、Scope、優先順位
- Apple M2 Pro／16GBを初期制約とする判断
- ModelとBackendを分離して選ぶ方針
- Modular Monolith、Port、Adapter、Dependency Inversion
- Local／Cloud／Hybrid Deploymentの分離
- Runtime GovernanceをModel外側のInference Control Planeとして構成する方針
- Append-Only Documentation、Handoff、Review、Backupの運用
- Model、Governance、Storage、UI等を交換可能にする最上位原則

### このPhaseの意味

最初から高性能Modelに依存せず、小型ModelでSystem全体の骨格を成立させる方針を固定した。

---

## 6. Phase 1 — Portable Inference Runtime and Preview Surface

**State: `Complete／Accepted`**

将来すべてのLayerを接続できる、Portableな推論Runtime骨格を作るPhase。

### Phase 1-A — Environment and Native Metal

**State: `Complete／Accepted`**

- Python／uv／`.venv`
- 再現可能なDependency Lock
- `llama-cpp-python` Metal Build
- Environment Verification
- Native Model Smoke Test

### Phase 1-B — Model Adapter and CLI

**State: `Complete／Accepted`**

- Model Port／llama.cpp Adapter
- Model Load／Unload
- Chat Template
- Streaming Generation
- Cooperative Cancel
- Generation Config
- `model-info`／`generate`
- Model Artifact SHA-512

### Phase 1-C — Platform and Acceleration Hook

**State: `Complete／Accepted`**

- Deployment Profile
- Platform Registry
- Capability／Requirement／Runtime Observation
- macOS、Linux、Windows等をCoreから分離するHook
- Metal、CUDA、CPU等をProfileで表現
- Capability不足を黙って無視しないValidation

### Phase 1-D — Configuration and Response Language

**State: `Complete／Accepted`**

- Application共通設定とDeployment Profileの分離
- Model Definition、Application、Environment、CLI Overrideの優先関係
- Effective ConfigとSource Traceability
- `ja／en／auto`

### Phase 1-E — Thinking Execution and Presentation

**State: `Complete／Accepted`**

- Thinking実行要求と表示の分離
- Model Output Protocol
- Stateful Streaming Parser
- 推論過程の表示／非表示
- Raw OutputとPresentation Outputの分離
- Raw Thinking Persistence無効

### Phase 1-F — Lightning Cross-environment Runtime

**State: `Complete／Accepted`**

- Ubuntu Linux x86_64 Profile
- NVIDIA CUDA Profile
- CPU Execution Profile
- Python 3.12.11 Support
- Lightning用Setup／Preflight／Acceptance Script
- macOS Metalとの共通Contract

Repository側の実装、Read-only Preflight、Pure CPU Follow-upおよびLightning上のNative実測は受入済みである。

既存の`lightning_linux_x86_64_cpu.toml`は、`compute_kind_key = "cpu"`かつ`gpu_layers = 0`である一方、Backend Build Variantは`cuda`であり、CUDA BuildをCPU実行するProfileである。Freshな最小CPU環境でCUDA Toolkit／`nvcc`を要求しないよう、次をFollow-up候補とする。

- Lightning Linux x86_64 Pure CPU Profile
- `build_variant_key = "cpu"`相当のBackend識別
- Pure CPU用`llama-cpp-python` Build
- CPU専用Setup／Preflight／Acceptance Script
- CUDA BuildのCPU実行とPure CPU Buildの明確な区別
- GPU、NVIDIA Driver、CUDA Toolkit、`nvcc`を必須にしない受入条件
- `gpu_layers = 0`とCPU Device Observationの検証
- Fresh Environmentでの再構築性
- 短いBounded Model SmokeとLatency／Memory記録

概念的な候補名：

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

Pure CPU Profile、Runtime Detection、PreflightおよびSetup Hookは実装済みであり、既存CUDA BuildのCPU実行ProfileとPure CPU Build Profileを分離できている。Native AcceptanceはRuntimeのAcceleration APIを選択Profileと照合するよう修正され、CUDA GPUの`cuda`、CUDA Build CPU実行の`cpu_native`、Pure CPUの`none`を区別する。

Model選択は`--model-root`を正本とし、RegistryのRelative Artifact Pathから実Fileを解決する。互換用`--model-path`はExpected Layoutとの一致確認だけに使用し、指定Fileと実際にLoadするFileが異なる状態をFail Closedで拒否する。Repository Correctionは独立ReviewでAcceptedとなった。その後、ユーザーがLightning上でPure CPU Environmentを再構築し、Environment Verification、Full Test Suite、Bounded Native Acceptanceおよび外部BrowserからのWeb Acceptanceを完了した。

既存の`preflight_lightning_ai_studio.sh`は、後方互換を維持したうえでPure CPU Targetへ拡張した。既存`--cpu-only`はCUDA BuildのCPU実行を意味するため、Pure CPUへ意味を変更していない。Pure CPU Targetでは`nvidia-smi`、`nvcc`、CUDA CompilerおよびGPU Allocationを必須確認せず、Linux、x86_64、Container、Python、`uv`、CPU、Memory、PathおよびPure CPU ProfileをRead-onlyで確認する。外部Lightning環境の再構築とNative Testはユーザーが実行し、Repository側は再構築手順とPreflightを提供する分担を実証した。

Lightning Basic Previewでは、Managed SecretsからBasic認証Credentialを環境変数として受け取り、Source、Config、Docs、Logへ平文保存しない。`start／status／restart／stop`による手動Lifecycleと、Platform Lifecycle所有向け前景`run` Entrypointを分離した。手動Lifecycle、Health Check、未認証時`401`、正しいCredentialによる外部Access、RestartおよびStopを実機で確認済みである。

### Phase 1-G — Minimal Web Surface

**State: `Complete／Accepted`**

- FastAPI Web Boundary
- 最小Chat UI
- 一時的な複数Turn
- Streaming／Stop／New Chat
- Preview用Basic認証
- Non-loopback BindのFail Closed
- Phase 2以降でUIを交換できるAPI境界

2026-07-25のMac Web User Testでは、画面構成、Browser Memory内の一時的な複数Turn、New Chat、Streaming、停止、送信、`Ctrl+Enter`送信およびModel非Reload Resetが意図どおり動作することが確認された。

### Phase 1-H — Summary Mode and UI Language

**State: `Complete／Accepted`**

- Post-generation Summary Mode `OFF／ON`
- 同じMain ModelのSequential Reuse
- Summary Failure時のOriginal Fallback
- Summary成功時のOriginal非露出
- SSE Keepalive
- UI日本語／英語切替
- UI LanguageとResponse Languageの独立

2026-07-25のMac Web User Testでは、UI Language、Response Language、Summary Modeおよび最大生成Token数による停止が確認された。

「推論過程を表示」はPresentation Visibilityだけを変更し、生成側のThinking実行を有効化しない。Current Defaultは`generation.thinking_mode = "disabled"`であり、Web RequestにもThinking実行切替が存在しないため、CheckboxをONにしても表示対象が生成されない場合がある。これは現在のContractと整合するが、UIだけでは状態を理解しにくいためFollow-up対象とする。

- Thinking Generation `OFF／ON`
- Thinking Presentation `hidden／visible`
- 両者を別設定として保持する。
- GenerationがOFFの場合、Visibility Controlを無効化するか「表示対象なし」を明示する。
- 一般利用者向けDefaultはGeneration OFF／Visibility Hidden候補とする。
- Raw Thinking非保存、正確性非保証および最終回答Token枯渇Riskを維持する。

### Phase 1-I — Web Presentation and UX Follow-up

**State: `Complete／Accepted`**

Mac Web User Acceptanceで確認されたFollow-upを、Phase 1 Completion前に安全境界ごと整備する。

- Thinking Generation `OFF／ON`とThinking Presentation `hidden／visible`を別設定としてWebへ公開する。
- GenerationがOFFの場合、VisibilityだけをONにしても表示対象が存在しないことをUIで明示する。
- SSE Deltaへ`reasoning`と`final`の意味的Channelを追加し、推論過程と最終回答を別領域で扱う。
- Hidden ThinkingをClientへ送らず、Raw Thinking非保存を維持する。
- 推論過程は一時的なPlain Text、最終回答はStreaming中Plain Text、Completion後にSanitize済みMarkdownとして表示する。
- Markdown Parser／SanitizerはRuntime CDNへ依存せず、Raw HTML、Script、Event Handlerおよび危険なURL Schemeを拒否する。
- SanitizationまたはRenderingに失敗した場合はPlain Textへ安全にFallbackする。
- User InputとAssistant Final AnswerへCopy Buttonを付け、Canonical TextだけをCopyする。
- Hidden Thinking、内部Metadata、Summary Modeで非表示のOriginal AnswerをCopyへ混入させない。
- Composerへ`Cmd+Enter`／`Ctrl+Enter`等の送信Shortcut Hintを日本語／英語で表示する。
- IME変換確定中のEnterでは送信しない。

2026-07-25に実装、設計Reviewおよび次のManual Edge Testを完了した。

- 生成中のNew Chat
- Summary中のStop
- Page Reload
- 複数TabでのBusy／競合表示
- 最大生成Token境界
- Thinking Generation／Visibilityの全組合せ
- Markdown Sanitization、Plain Text Fallback、Copy対象

Copy、Language、Summary、New Chat、生成中New Chat、Summary中Stop、Reload、別Tab Busy、Thinking ControlおよびCompletion Markdownは合格した。

Streaming中にMarkdown記号が見え、Completion後に変換される挙動はCurrent Contractどおりである。Table、段階的Streaming Markdown、Code Block個別CopyおよびBusy Message整理はPhase 4へ延期する。

### Phase 1 Milestone

> **Portable, cross-environment-ready LLM Runtime with a minimal public evaluation surface**

Phase 1は「完成したLLM」ではなく、Model交換、Platform交換、Streaming、Cancel、Config、Web接続の基礎契約を証明するPhaseである。

---

## 7. Phase 1-ex — Operations, Documentation, and Public Transition

**State: `Complete／Accepted`**

Phase 1完了後、初回GitHub公開前に実施する運用移行Phase。新しいAI機能を増やすPhaseではなく、Projectを長期研究・分業・公開に耐えられる状態へ変える。

2026年8月4日時点で、Docs Directory Migration、旧Root退役、Migration Manifest、Rollback Plan、役割権限再整理、Stable／History命名規則、Append-Only運用、設計統括者役／プロジェクト責任者役Recovery、Lightning Basic Preview／Public Demo Lifecycle、Auto-start Stage A／B、Traffic-aware External Wake Acceptance、Mac／Lightning Documentation RAG、Git Workflow／Single Root、Final Lossless、Final ReviewおよびBackup Gateを完了した。

残工程の実行順は、2026年7月27日に次の10段階へ変更した。

1. Gitを使用しないGitHub掲載準備と一時掲載。詳細はユーザーの後続指示待ち。
2. Basic認証Previewと分離したPublic Demo基盤、最終確認、合格後の匿名公開有効化。
3. Mac限定簡易Documentation RAG＋External Hook。
4. Git運用設計。Branch／Tag／Commit、Author／Email、Remote／公開RepositoryおよびBackup対応を確定する。
5. Git初期化／公開Sanitation。`.gitignore`、`.gitattributes`、Model／Secret／Cache除外、Privacy Scan、LICENSE方針、初回Commit直前準備およびユーザー原文上のGitHub公開を含む。初回Commitはまだ作成しない。
6. 必要なDocsだけを再整理・新規作成し、Phase 1-ex Final LosslessとDesign Governance Recovery情報を更新する。
7. 全体Review／Test／Privacy Scan。
8. ユーザーの明示許可後の初回Commit。
9. Phase 1-ex完了条件・User Acceptance後のPhase 1-ex Backup。
10. Phase 1-ex完了・Phase 2着手可能宣言後のPhase 2。

ユーザー原文では番号`4`が二度使われていたため、内容と前後関係を変えず10段階へ正規化した。Git未使用の一時掲載、後段のGit初期化／GitHub公開との対応および初回Commitの履歴関係は、Git運用設計で確定する。未確定事項を独自判断で統合または前後入替しない。

2026年8月4日時点で、上記1～10のPhase 1-ex完了Gateを実施した。Git未使用時代の公開Historyを保持したまま、Existing RepositoryへCanonical Sourceを統合し、PR／Merge／Single Root Cutover／通常Commit／Pushを検証した。TagとReleaseはユーザー決定により今回作成しない。

次の順序でDocumentationを再構築した。

1. 全Source InventoryとBefore Snapshotを固定する。
2. `project_continuity_master_ja.md`と`roadmap_ja.md`を第1周で更新する。
3. Current Canonical文書を累積・ロスレス方針で再構築する。
4. Phase 1と進行中のPhase 1-exをLossless Compilationとして再整理する。
5. Shared運用・権限・Recovery文書を再整理する。
6. Public Overview／Concept、READMEおよびResearch Preview利用条件一式を作成する。
7. `project_continuity_master_ja.md`と`roadmap_ja.md`を第2周で再確認し、全成果を累積反映する。
8. 全Snapshot、SHA-512、Source Coverage、Link、禁止情報、State表記を検証する。

Phase 1-exのLossless文書は、Phase完了版と偽らず、作成時点までを含むInterim／Current-to-date Compilationとして識別する。Phase 1-ex完了時には、追加された後続資料を含めて正式なPhase完了版を再生成する。

### 主な対象

- 設計統括者役、Phase別設計者役、実装者役、対外Docs役の再編
- Git Workflow
- Docs Directory Migration
- Stable Canonical Docs
- Project Continuity Master
- Phase単位Lossless Documentation Compilation
- Public Identity／Privacy／Attribution
- README／LICENSE／CITATION／NOTICE／TERMS_OF_USE
- Overview／Concept／Roadmap／Phase Summary
- Backup／Manifest／SHA-512／Restore
- GitHub公開用AllowlistとSecret／PII Scan

### Documentation Language／Filename Policy

Phase 1-exでは、既存の開発用Docs、Phase単位統合文書、公開用文書を区別する。

#### 既存の分割済み開発Docs

これまで開発、設計、Review、Handoff、Status、Index等で作成した、Phase統合前の細分化されたDocsは一括翻訳しない。

- 既存Fileを機械的に`_ja`／`_en`へRenameしない。
- 本文を英訳するために原文を書き換えない。
- Path、Filename、Timestamp、State、本文、Hashを保持する。
- Phase単位Lossless CompilationのSourceとして扱う。
- 公開対象はGitHub AllowlistとPrivacy／Secret Scanで別途決定する。

#### Phase単位統合文書

Phase完了時に、対象Phaseの開発経緯、要件、設計、実装報告、Review、検証、User Acceptance、未解決事項および引継ぎ情報を、原資料を変質させない一つの統合文書へまとめる。

- 日本語正本のFilenameには`_ja`を付ける。
- 原則としてPhaseごとに一つの統合文書とする。
- 元資料を勝手に要約、意訳、再解釈または意味変更しない。
- Source Set、Path、State、Size、SHA-512および抽出可能性を記録する。

概念的なFilename：

```text
phase_1_compilation_ja.md
phase_2_compilation_ja.md
```

最終配置は現在のPhase-first Documentation Structureで確定した。Phase 1はFinal Lossless、Phase 1-exは進行中のためInterim Losslessとして分離している。

#### 公開用文書

人が直接読む公開文書は、日本語正本であることがFilenameから分かるよう、原則として`_ja`を付ける。

例：

```text
overview_ja.md
concept_ja.md
roadmap_ja.md
requirements_specification_ja.md
system_architecture_ja.md
technology_selection_ja.md
basic_design_ja.md
runtime_governance_specification_ja.md
```

Repositoryや配布規約上の慣例的な固定名は例外とする。

- `README.md`
- `LICENSE`
- `CITATION.cff`
- `NOTICE.md`
- 必要に応じた`TERMS_OF_USE.md`

`README.md`は日本語を主とし、末尾に英語Abstractを置く既定方針を維持する。

#### Optional English Documents

Phase 1-ex Stage 6で作業余力がある場合は、Current／Shared／Publicの非History Stable文書すべてについて英語派生版を作成する。

- 英語版作成をPhase 1-exまたは各Phase完了の自動必須Gateにしない。
- 日本語正本をSource of Truthとする。
- 作成する場合は、概要版や抄訳ではなく、日本語正本と同じ粒度の全対象版を作る。
- `docs/project/current/history/**`、`docs/project/shared/history/**`および`docs/public/history/**`は対象外とする。
- 英語版は対応する日本語File、Version、SnapshotまたはHashを示す。
- 翻訳時に要件、権限、免責、Status、未解決事項を追加・削除・弱化しない。
- 日本語正本と英語版の同期状態を明示する。
- Stage 6に余力がない場合は、後日またはPhase 2前半へ延期する。
- 延期時は対象範囲、未作成状態および再開位置をCurrent IndexまたはActive Phase Indexへ記録する。

### Public Documentation Corpus Preparation

将来、MARGPA Runtime LLM自身が本Projectを説明できるよう、Phase 1-exで公開日本語正本からRAG用Corpus Manifestを作成できる状態へ整える。

Corpusへ`docs/`全体を無差別に登録しない。

- GitHub公開Allowlistに含まれる文書だけを対象にする。
- 原則として公開用の日本語正本`*_ja.md`と、必要な慣例名文書を対象にする。
- Phase統合前のHandoff、Status、Review、Index、旧Snapshot等はDefault Corpusから除外する。
- Secret／PII／Local Path／旧識別情報／非公開URLを再Scanする。
- Path、Title、Language、State、Snapshot、Size、SHA-512をCorpus Manifestへ記録する。
- Superseded文書とCurrent文書を区別し、旧版をCurrent Factとして検索させない。
- Markdown以外の不要FileをCorpusへ登録しない。
- Corpusの更新は明示的に行い、いつのDocsを参照したか追跡可能にする。

Public Documentation Corpusは、日本語／英語のOverview、Concept、RoadmapおよびTechnology Selectionの明示8文書として確定した。Mac LocalではProject内の許可済みDocsを読むLocal Profile、Lightning Basic Preview／Public Demoでは公開8文書だけを読むExplicit Profileを実装した。いずれもDefault OFFで、明示的なON Request時だけManifest、Index、RetrievalおよびContext Injectionを行う。これはPhase 7の任意Corpus、Embedding、Vector StoreおよびDocument Lifecycleを含む本格RAGを代替しない。

### Public Warranty Disclaimer

Phase 1-exで作成するREADMEと`LICENSE`の両方に、本Projectおよび配布物について一切の動作保証を行わない旨を明記する。

最低限、次を明確にする。

- Experimental／Research Softwareである。
- 動作、可用性、継続性、互換性、正確性、安全性、特定目的への適合性を保証しない。
- Hardware、OS、Backend、Model、Dependency、外部Serviceまたは設定の違いによる動作を保証しない。
- 利用者自身の責任で検証して使用する。
- 適用法令で認められる範囲において、利用または利用不能から生じた損害への責任を負わない。

READMEには一般利用者が認識しやすい日本語の注意書きを置き、`LICENSE`には採用する利用条件と整合する正式な免責条項を置く。READMEの説明だけで`LICENSE`の法的条項を代替したとみなさない。

本Projectは研究、比較および検証のため、Governance、Guardrail、Judge、Repair、RAG、Agent、各Governance Point、定量計算モード、定性計算モードその他のComponentを個別にON／OFFできる方向で設計する。この自由度により、安全性、品質、監査可能性、再現性または期待される制御が低下する構成も作成可能であることを、READMEの「留意事項」と、必要に応じて`LICENSE`、`TERMS_OF_USE.md`または`NOTICE.md`へ明記する。

- すべての設定組合せについて動作、安全性または妥当性を保証しない。
- ComponentをOFFにした場合、そのComponentが提供する検査、制御、修復またはEvidenceが失われる可能性を示す。
- Current Effective Config、無効Component、WarningおよびDegraded Stateを可能な範囲で表示・記録する。
- 研究上の比較可能性を理由に、Access Control、外部Authority、Tool Permissionまたは適用法令を迂回しない。
- 無意味、未対応または危険な組合せを黙って受理することを、疎結合性または研究自由度と同一視しない。

Research Preview用の`LICENSE`、`TERMS_OF_USE.md`、`NOTICE.md`および`CITATION.cff`初版を作成した。将来、ユーザーが別Projectで作成したTerms／Noticeを提示した場合は、再利用可能な条項を候補SourceとしてReviewできる。ただし、Project名、対象範囲、利用許諾、禁止事項、免責、責任制限、第三者License、Model LicenseおよびHosted Service条件との整合を確認し、無検証でそのまま流用しない。

### Lossless Documentation

PhaseごとのDocumentation統合は、要約や意訳ではなくLossless Compilationとして行う。

- Source SetをFreezeする。
- Path、State、Size、SHA-512を記録する。
- 元本文を変更せず格納する。
- 統合Fileから再抽出する。
- Byte SizeとSHA-512が1件でも不一致ならFail Closedとする。

### Phase 1-ex Milestone

> **再現・引き継ぎ・公開・復旧が可能な研究開発Repository**

### Phase 1-ex Completion Gate

- `project_continuity_master_ja.md`、Current Canonical、Shared、Phase 1 Lossless、Phase 1-ex Final LosslessおよびPublic Corpusが、Source Inventoryへ追跡可能である。
- Stable文書の変更前Snapshotが各`history/`へ保存される。
- Project ContinuityとRoadmapを、作業開始時と全成果物完成後の2周で確認する。
- README、画像、利用条件、免責、Attributionおよび将来Roadmapが相互に矛盾しない。
- 日本語正本を完成させる。英語派生版は、Current／Shared／Publicの非History Stableを対象とする後続Taskへ正式Deferralし、Phase 1-exのBlockerにしない。
- Gitの通常Commit／Push経路は成立済みである。各Git MutationはAccepted Workflowと対象ごとのユーザー明示承認に従う。

---

## 8. Phase 2 — Conversation Continuity and Experimental Control Surface

**State: `In Progress — Phase 2-0 Initial Pilot Evidence／Role Authority Redesign／Restart Gate`**

Phase 1の一時的なWeb Previewを、継続利用と研究設定に耐えられるApplicationへ発展させる。

### Phase 2 Subphase Plan

Phase 2は、設計・実装・Review・Recoveryの境界を明確にするため、次の中粒度Subphaseへ分割する。

```text
Phase 2-0 : Document-driven Orchestration Pilot Design／Bootstrap
Phase 2-A : Phase Contract／Conversation Domain Foundation
Phase 2-B : Conversation Persistence／Lifecycle Services
Phase 2-C : Conversation Application UX
Phase 2-D : Configuration Control Surface／Research Developer Mode
Phase 2-E : Runtime Composition Switchboard／Documentation RAG Follow-up
Phase 2-F : Cross-environment Acceptance／Phase Closure
```

2-Aから2-Fを原則とした依存順で進める。局所設計の再調整はPhase 2設計担当者役が行えるが、Phase 2の目標、Cross-Phase不変条件、User Authorityまたは後続Phaseへの接続を黙って変更しない。

Phase 3～Phase 9を同様にSubphase化するかは、Phase 2-Fで粒度、Cost、Recovery、Authority逸脱およびReview工数を評価した後に都度決定する。Phase 10以降は特殊性が高いため、現時点の横展開対象から除外する。

### Conversation Application

- Session／Turn／Message Identity
- 永続的な複数Turn Conversation
- New Chat／Chat List／History
- Resume／Regenerate／Branch候補
- Generation Stop／Error Recovery
- Model ReloadとChat Actionの分離

### Configuration Control Surface

- 一般利用者向け設定
- 研究・開発者向け設定
- 「研究・開発者モード」による高度設定群の一括表示／非表示
- Config Schema Validation
- Effective Config／Source／Diff
- Runtime中に変更可能な設定とRestartが必要な設定の分離
- SecretをUIやTracked Configへ書かない境界

### Research／Developer Mode

将来の一般向けProduct化を考慮し、通常利用者向け画面と、研究・開発者向けの高度な設定画面を分離する。

```text
研究・開発者モード : OFF／ON

OFF:
  一般利用者向けの基本設定だけを表示する

ON:
  研究・開発者向けの設定群を表示し、許可された範囲で編集可能にする
```

概念的なConfig例：

```toml
[ui.research_developer_mode]
enabled = false
```

一般公開ProfileではDefaultを`OFF`とする。Local環境または許可された利用者は`ON`へ切り替えられるが、Public Deploymentで誰が切り替え可能かはAccess Control Policyで決定する。

研究・開発者モードで扱う設定群の候補：

- Model／Backend／Artifact選択
- 詳細Generation Parameter
- Context／Token／Performance設定
- Component別ON／OFF
- Governance Point別`off／observe／enforce`
- Guard／Judge／Repair／RAG／Agent設定
- 定量計算モード／定性計算モード
- Experiment Profile／Seed／Baseline
- Audit／Evidence／Status表示
- ML／Training／Adaptation設定

研究・開発者モードは、設定群の表示と編集入口を切り替えるUI／Configuration機能である。これ自体を権限付与、Policy解除、安全機構解除またはComponent一括有効化として扱わない。

- `ON`でも、Access Control、Tool Permission、Approval、Dependency、Conflict、Capability、Schema Validationを迂回できない。
- `OFF`でも、Server側の検証、Guardrail、Governance、Audit等を自動的に無効化しない。
- UIで非表示にするだけでSecurity Boundaryが成立したとみなさない。
- Clientから直接送られた未許可設定はServer側で拒否する。
- 設定変更前後のDiff、Source、Apply Resultを表示し、Audit Eventとして記録できるようにする。
- 個々のComponentおよび計算モードのON／OFFは、研究・開発者モードとは別の独立設定として保持する。

### Project Documentation Explainer Preview

本格RAGに先立ち、「このProjectは何か」「現在どこまで動くか」「どのPhaseで何を作るか」をLLM自身に説明させる軽量Documentation RAGをPhase 1-exで実装した。

一問一答でも、Project Overview、Architecture、Roadmap、Current Status等の説明には有意義である。永続Multi-turnが成立した後は、Sourceを保ったFollow-up Questionへ拡張する。

```text
Project Documentation Explainer : OFF／ON
```

概念的なConfig例：

```toml
[components.project_documentation_explainer]
enabled = false
corpus_profile = "public_canonical_ja"
retriever = "lexical"
```

Accepted済み軽量Previewの境界：

- Phase 1-exで作成したPublic Documentation Corpus Manifestだけを読む。
- Embedding ModelやVector Storeを必須にしない。
- 日本語を扱える字句検索またはCharacter N-gram等の軽量RetrieverをAdapter越しに使用する。
- Queryに関連する少数ChunkだけをContext Budget内で注入する。
- 回答に参照文書、Sectionおよび可能な範囲のSource Linkを表示する。
- 参照Snapshot、採用Chunk、Score、Digest、Token Budgetを記録可能にする。
- Corpus不足、検索結果なし、Context切捨てを黙って隠さない。
- Retrieved TextをSystem InstructionではなくSource Dataとして区別する。
- Docs中のPrompt Injection様Textや命令表現をRuntime命令として実行しない。
- Modelの説明がDocsに基づく範囲と、Model自身の推測を区別する。
- ExplainerをOFFにした場合、Index Load、Retrieval、Context Injectionおよび追加Writeを行わない。
- Explainerを明示利用した時に`docs/`が存在しない場合は、`docs_directory_missing`を持つUnavailable Resultを返す。
- `docs/`不存在時はProject説明をModelに推測生成させず、Index Load、Retrievalおよび追加Model Callを行わない。
- 日本語UIでは「`docs/`が設置されていないため参照できません。」と表示できるようにする。
- Missing ErrorへAbsolute Local Pathまたは利用者識別情報を露出しない。

このPreviewは、Document Upload、Embedding、Vector Database、任意Corpus、Document Update等を含むPhase 7の本格RAGを代替しない。同一のRetrieval／Evidence Portへ後から本格RAG Adapterを接続できる構造にする。

READMEへの表示は実装状態と一致させる。公開文書全体の再整理はPhase 1-ex終盤に行うため、本Roadmap更新だけでREADME更新済みとは扱わない。

- 未実装時は、将来予定としてのみ記載する。
- 実装とAcceptance完了後に限り、「このProjectについて、公開Docsを参照しながらLLM自身に説明させることができます」と記載できる。
- Source表示や既知の限界を併記し、Project全体を完全に理解しているとは主張しない。

Mac Local、Lightning Basic PreviewおよびLightning Public Demoで、RAG OFF／ON、Retrieval、Citation、停止、再送信およびAccess分離を確認した。Lexical Retrievalと軽量Modelの組合せでは、無関係Chunkの採用、質問意図とのずれ、根拠から逸脱した要約および不正確なProject Status生成が残る。Adapter成立と回答品質を分離し、機能実装はAccepted、精度調整はGuard／Judge／Governance、より高性能なModelおよび後続RAG Phaseと合わせて再開する。

### Component Registry／Switchboard Foundation

- Functional Component Descriptor
- Component単位の`enabled`
- Governance Bindingの`off／observe／enforce`
- Required／Optional Dependency
- Conflict／Invalid Combination
- Capability／Degraded Mode
- Side Effect Level
- Apply Timing

`Agent OFF + Agent Governance ON`等の無意味な組み合わせを黙って受理しない。また、Tool Permissionを無効化することを`allow all`と解釈しない。

### Document-driven Development Operation Pilot

Phase 2は、元来のConversation／Configuration機能へ着手する前に、`Phase 2-0`としてDocument-driven Orchestration Pilotの設計と最小実行を行う。プロジェクト責任者兼設計統括者役がPhase専用のIndex、開始用Handoff、Reading OrderおよびWrite Authorityを用意し、独立した`Phase 2設計担当者役`Task等へ直接渡す最初のPilotとする。

当面、現在Taskは`プロジェクト責任者兼設計統括者役`としてProject全体、Cross-Phase不変条件、Task編成、設計／実装Handoff、ReviewおよびRecoveryを統括する。両RoleのFolder／Recoveryは分離して相互参照する。兼務はユーザーの最終Decision Authority、Backup、Git／公開、External Service、Secret、課金およびPhase移行Gateを代替せず、絶対禁止事項、Docs規則、Authority規則その他の運用ルールから免除しない。

Pilotでは、Task作成の便利さだけでなく、Docs-only Recovery、Authority遵守、Handoffの明瞭性、Context分離、Review品質、Task再作成可能性および利用可能量／Costの妥当性を評価する。設計成果は設計統括者役がReviewし、Accepted後にだけ実装者役へ正式Handoffする。

Phase 2設計担当者役とPhase 2実装者役は、Phase専用の独立Taskを基本案とする。実装者TaskはContext、未解決状態、Authority遵守、Statusの完全性および利用可能量が安全な継続を妨げる場合に更新できる。旧新Taskを同一Working Treeへ同時Writeさせない。

Phase 2はユーザー確認により開始済みである。初回有界Pilotでは独立したPhase 2設計担当者役Taskを1件作成し、Task名設定のProvider登録遅延を安全停止と明示的な1回の再試行で処理した。Read-only Recovery AssessmentはSafety Pass／Recovery Failとなり、初回TaskはIdleのまま再利用しない。再試験用Taskは未作成であり、draft-4と新Task 1件のAcceptance、READY／`ARMED`および後続Start／`ON`を新たに必要とする。ユーザーが、Task作成、要件変更、重要な外部操作、Backup、Commit／Push／公開、User AcceptanceおよびPhase移行の最終Authorityを保持する。

Automationは単純なON／OFFではなく、`manual／advisory／bounded_unit／workflow／phase／project`の段階と独立Capability Dimensionで制御する。Pilot開始時は`bounded_unit`を上限として、Task作成、Task名設定、Authority設定、Handoff、Status、Follow-upおよびReviewを繰り返す。安定性が確認できた場合だけ、複数Unit、Subphase、Phase完了単位へ拡張し、最終的にはProject完了単位のOrchestrationを長期目標とする。

初回Pilot開始前の大規模BackupとTwo-key Activationは成立済みであり、初回結果後にもユーザーが大規模Backupを取得した。再試験では過去のAcceptanceまたはStart Eventを再利用せず、Control Taskの「準備OK。いつでも開始出来ます。」と、後続ユーザーの「ok。では開始する。」が順序どおり成立した時だけ再開する。片方の発言、過去の同意または類似表現から開始を推測しない。

再試験のGate順序は、Correction Review、Read-only Capability再照合、Exact Design Freeze、ユーザー承認済みGit Checkpoint／Remote一致、Exact Envelope／Child Task範囲Acceptance、Controller READY／`ARMED`、後続ユーザーStart／`ON`、新Child Task作成、Acknowledgement／Reviewとする。Task管理Capabilityは初回Pilotで実証済みだが、Provider Adapter、Manifest、DigestおよびFreeze Receiptは再試験Revisionで再確認する。現在、新Taskは作成していない。

Phase 2をOrchestrationの成立性検証、Phase 3を再現性・移植性検証とする。Phase 2の結果がAcceptedされた場合はPhase 3でもPilotを継続し、異なる要件、Task ContextおよびEvidence Domainで同じ運用骨格が成立するかを確認する。その結果に基づき、以降のSubphase、Phase完了単位またはProject完了単位への拡張を段階的に判断する。

Codexの利用可能量、Creditまたは外部Service制限で作業が途中停止する可能性を前提とする。停止時は未完了作業をCompleteと表記せず、最後の確認済み状態、Open Findingおよび再開点を固定する。また、設計統括者役を含む全Role／全Taskが権限外Actionを取りうるものとし、Role名やTool Permissionだけに依存せず、Handoff、Exact Target、Mutation Inventory、ReviewおよびStop Gateを重ねる。

明示されたAuthorized Root／Allowed Path外へ無許可で触れない規則は、将来の上位Role、Automation Level、Phase／Project ScopeおよびProviderにかかわらず最上位である。Automation／Constitution Coreへ特定Project、Provider、Absolute Path、Phase、Task、CommandまたはUIをHard-codeせず、Project ManifestとProvider Adapterへ分離する。

CodexからClaude Code等の別ProviderへTaskをHandoffするMulti-provider構成は、開発速度向上の可能性と他社環境での運用規則再現性を検証する将来候補である。現時点では未決定であり、Authority、Single Writer、Evidence、Context、CostおよびRecoveryの同等性を確認するまで採用済みと扱わない。

### Phase 2 Milestone

> **Persistent Chat and Explicit Runtime Composition**

---

## 9. Phase 3 — Audit, Evidence, and Generic Definition Infrastructure

**State: `Planned`**

Runtimeを「動くSystem」から「何が起きたか検証できるSystem」へ進め、任意Governance Definitionを安全に受け入れる基盤を作る。

Phase 2 Orchestration PilotがAcceptedされた場合、Phase 3ではAudit／Evidence実装と並行して、同じDocument-driven開発体制の再現性・移植性を検証する。Phase 2で成立した運用が異なるPhase要件、担当Task、ContextおよびEvidence対象でも維持できるかを確認し、成功、Incident、Near Miss、人間介入およびRuleの有効性を将来の統合憲法へ入力する。

### Audit／Evidence

- Turn／Request／Run／Event Identity
- JSON／JSONL Append-Only Log
- Canonicalization Version
- SHA-512
- Model、Backend、Artifact、ConfigのIdentity
- Token、Latency、Stop Reason、Warning、Error
- System TraceとModel Generated Explanationの分離
- Raw Chain of ThoughtではなくHigh-Level Explanation

SHA-512単体を完全な改竄耐性とは主張しない。Hash Chain、HMAC、Signature、WORM、Merkle Tree等は後続Hardening候補として分離する。

### Generic Governance Definition Platform

- `EmptyDefinitionProvider`
- Filesystem／Custom Definition Provider
- Package Manifest
- Standard Descriptor
- Adapter Registry
- Normalized Governance IR
- Compiler Port
- Compiled Plan
- Definition／Adjustment／Plan Digest
- Quarantine／Unsupported／Invalid State

### Definition 0件Baseline

```text
definitions             : 0
governance.mode         : off
model generation        : pass
governance model calls  : 0
governance tokens       : 0
governance repairs      : 0
```

ARGD、DAGD、CDOGDを含め、どのGDもRuntime Bootの必須Dependencyにしない。

### Unknown Definition Boundary

- File名からDomainやCapabilityを推測しない。
- 任意JSONをCodeとして実行しない。
- Shell、Dynamic Import、自動URL Downloadを許可しない。
- 未知SchemaはTrusted Adapterなしに無理やり解釈しない。
- Invalidな1件でMain Model Runtime全体を無条件に停止させない。

### Phase 3 Milestone

> **Auditable and Definition-ready Runtime**

---

## 10. Phase 4 — MARGPA Main Runtime Governance

**State: `Planned／Core Research Priority`**

Main Modelに最も近いGovernance Pointを実装し、MARGPA Runtime Governanceの最初の実証を行う。

### Governance Control Plane

- Definition Registry
- Validator／Adapter／Compiler
- Activation／Rule Selection
- Namespaced Governance State
- Evidence／Audit
- Semantic Evaluator Port
- Conflict Resolution
- Action Resolver
- Model Call／Token／Latency／Repair Budget

### Main Model Governance Point

- Input Interpretation
- Premise／User Decision／Context Preservation
- Scope／Constraint
- Generation Config Constraint
- Output Audit
- Deviation／Severity
- Recommended Action／Executed Action
- Repair／Regenerate
- Rebind／Enforce／Reinitialize候補

### ARGD／DAGDの位置づけ

ARGD v0.3.1とDAGD v0.4.4は、Generic Platformへ接続する最初のFoundational Governance候補である。

ただし、Coreへ特別扱いを入れない。

- Source JSONを不変Snapshotとして扱う。
- Legacy AdapterがStandard Descriptor／IRへ展開する。
- 原本を都合よく独自分割しない。
- Sourceが存在しなくてもRuntimeは動作する。
- 別の全く異なるGDへ交換可能にする。

### Adjustment

Definition Source自体を書き換えず、次を別Profileとして調整する。

- Activation
- Include／Exclude Rule
- Priority／Soft Weight
- Threshold／Severity
- Evaluator Selection
- Token／Call／Latency／Repair Budget
- Action Mapping
- Status Verbosity

### Phase 4 UI Interaction Requirements

Main Runtime Governanceを一般利用者と研究・開発者の双方が操作できるよう、主要LLM Productに近い基本InteractionをUIへ追加する。

#### ローカルフォルダ追加

- 「ローカルフォルダを追加」ボタンを設ける。
- Folderのドラッグ＆ドロップ（Drag and Drop）を受け付ける。
- 選択対象、File数、合計Size、処理状態、Errorを表示する。
- 追加済みFolderを個別に解除できる。
- 選択していないPathを自動走査しない。
- 元Fileを変更、移動または削除しない。
- Hidden File、Secret、Symbolic Link、巨大Folder、未対応形式、重複Fileの扱いを明示的にValidationする。
- Local実行と外部Server実行ではData Boundaryが異なるため、外部へUploadされる場合は実行前に明示する。
- RAG／Context Injectionへ接続する場合も、Source Identity、Hash、採用範囲および処理結果を追跡可能にする。

初期実装はMac Local Profileから開始し、LightningではBasic PreviewとPublic Demoの双方へ公開8文書用Explicit Profileを接続した。全ProfileでDefault `OFF`を維持し、明示的にONにした場合だけCorpus Load、RetrievalおよびContext Injectionを行う。Access SurfaceとCorpus Profileを分離し、Public Demoから内部Project Docsを参照できない境界を保持する。

Phase 4ではUI Entry Pointと安全な受渡し境界を発展させ、Index作成、Retrieval、Document更新等の本格RAG処理はPhase 7の責務と整合させる。

#### 画面上の生成停止

- Terminalの`Ctrl+C`を一般利用者向け停止方法にしない。
- 生成中に明確な「停止」ボタンを表示する。
- 停止要求をCooperative CancelとしてRuntimeへ伝播する。
- 停止受付、停止処理中、停止完了を区別して表示する。
- 部分出力を完了回答と誤認させず、`cancelled`等の状態を関連づける。
- Cancel Event、Partial Output、Latency、Token Usageを可能な範囲でAuditへ残す。

#### 誤送信を防ぐ送信操作

長いContextや長文入力では、Enter単独送信により未完成の文章を誤送信しやすい。Phase 4で送信操作を再検討し、Enter単独送信を無条件の固定仕様にしない。

検討候補：

- Enterは改行、`Cmd+Enter`／`Ctrl+Enter`で送信する。
- 明示的な「送信」ボタンを常設する。
- Enter送信を利用者設定で切り替える。
- IME変換確定中のEnterでは送信しない。
- DesktopとMobileで入力操作を分ける。
- 長文または一定Context量以上では送信前状態を視覚的に明確化する。

初期推奨候補は「Enterで改行、`Cmd+Enter`／`Ctrl+Enter`または送信ボタンで送信」とする。ただし、最終仕様はPhase 4のUI設計、Accessibility、Browser挙動、IME動作およびUser Testを踏まえて決定する。

現在のPhase 1 Web UIは`Cmd+Enter`と`Ctrl+Enter`の両方を受け付ける。利用者が発見できるよう、Composer付近へ「`Cmd+Enter`／`Ctrl+Enter`で送信」等のShortcut Hintを表示する。実際に有効なShortcutと表示内容を一致させる。

#### Markdown Presentation

Phase 1ではXSSを避けるため、Assistant Outputを`textContent`でPlain Text表示し、`innerHTML`を使用しない。このためMarkdown記号がそのまま表示される。

主要LLM Productに近い可読性を得るため、Assistant OutputのMarkdown Presentationを追加する。Phase 1-Iでは安全な初期版を前倒しし、Phase 4では対応要素、Accessibility、Design SystemおよびProduct UIとしての完成度を拡張する。

- Heading、List、Emphasis、Code、Code Block、Quote、Link、Table等の対応範囲を定義する。
- User InputはDefaultでPlain Text表示を維持する。
- Raw HTMLをDefaultで無効化する。
- Script、Event Handler、危険なURL Schemeを拒否する。
- Trusted Sanitizerまたは同等のAllowlist処理を必須にする。
- External Linkへ安全な属性を付与する。
- Streaming中の不完全Markdownを安全に扱う。
- 初期候補はStreaming中を安全なPlain Textとし、Completion後にCanonical Assistant ContentをMarkdown Renderingする。
- Canonical ContentとRendered DOMを分離し、再生成、Copy、AuditではCanonical Contentを使用する。
- Thinking Content、Warning、Errorを通常回答Markdownへ混在させない。

Phase 1-Iでは、Streaming中Plain Text、Completion後のSanitize済みMarkdown、失敗時Plain Text Fallbackという限定Contractで実装する。Phase 4ではより広いMarkdown要素、Theme、Code Block操作、Accessibilityおよび表示品質を扱う。

#### Markdown Table

Phase 1-I ParserはTable未対応である。Pipe TableをParagraphとして扱うため、行区切りが潰れて表示される場合がある。

Phase 4で次を実装する。

- Semantic `table`／`thead`／`tbody`
- Responsive Horizontal Overflow
- Mobile表示
- Alignment候補
- Malformed TableのPlain Text Fallback
- Canonical MarkdownとRendered Tableの分離

#### Code Snippet Presentation

Phase 1-IはFenced Codeを`pre`／`code`へ分離する初期機能を持つ。Phase 4では主要LLM Productに近いCode Snippet Containerへ拡張する。

- Markdown、YAML、JSON、Pythonその他のLanguage Label
- Assistant説明本文とCode Snippetの視覚的分離
- Code Block右上の個別Copy Button
- 回答全体CopyとCode-only Copyの独立
- Canonical Code TextをCopy Sourceとする。
- Language Labelを未検証のExecutable Classまたは処理へ渡さない。
- Syntax Highlightを追加する場合はRuntime CDNを使用しない。
- DependencyのVersion、License、SourceおよびDigestを記録する。
- Highlight失敗時は安全なPlain Code BlockへFallbackする。

#### Streaming Presentation

Current Phase 1-IはStreaming中Plain Text、Completion後Markdownである。Phase 4で段階的Markdown表示を検討する場合も、不完全Fence、不完全Link、DOM再構築、Selection／Scrollの安定性およびXSS境界を検証する。安全性または表示安定性を損なう場合はCurrent方式を維持する。

#### Message Copy

User InputとAssistant Outputの各MessageへCopyボタンを追加する。

- User Messageは入力したCanonical TextをCopyする。
- Assistant MessageはCanonical Assistant ContentをCopyする。
- Rendered HTMLそのものをClipboardへ無条件にCopyしない。
- Hidden Thinking、内部Metadata、Secret、非表示Original SummaryをCopy対象へ混入させない。
- Copy成功／失敗を短時間表示し、日本語／英語UIへ対応する。
- Clipboard APIが利用不能な場合のFallbackまたは明示的Errorを定義する。
- Copy操作のためにClipboard内容を読み取らない。
- KeyboardおよびTouch操作に対応する。

Message Copyの安全な初期版はPhase 1-Iで実装する。Phase 4ではTouch操作、Accessibility、Copy範囲選択、Code Block単位Copy等を必要に応じて拡張する。

#### Busy Presentation

Multi-tab競合時の409 `model_busy`制御は成立している。Phase 4では具体Messageと汎用`request failed`が二重表示されないよう、Message BubbleとGlobal Statusの責務を整理する。

### Phase 4 Milestone

> **MARGPA Governance MVP**

---

## 11. Phase 5 — Guardrail, Security, Policy, and Authority Governance

**State: `Planned`**

安全判定、Policy判断、権限判断をMain Governanceから分離し、専用Componentと専用Governance Pointとして構成する。

### Guardrail Component

- Rule-based Input／Output Guard
- Prompt Injection／Jailbreak
- Secret／個人情報
- Tool悪用
- Agent間攻撃
- Streaming監視候補
- Qwen3Guard-Gen-0.6B Adapter候補

Prompt Injection対策は、最初から専用Modelだけに依存せず、決定論的Ruleを中心に始める。

### Policy／Authority

- Policy識別、適用範囲、優先関係、例外
- 過剰拒否／過少拒否
- 委任範囲
- 承認待ち
- Human Approval Hook
- 責任主体の状態

Tool PermissionはModel判断を正本にせず、決定論的Policyと既存権限を正本とする。

### Governance Definition Hook

- AISGD: AI Security
- MPGD: Model Policy
- DAAGD: Decision Authority and Accountability

これらのGDは、存在しないPolicy、Authority、委任、承認条件を新しく生成しない。

### Phase 5 Milestone

> **Security and Authority-aware Runtime**

---

## 12. Phase 6 — Judge, Evaluation, Repair, and Observability

**State: `Planned`**

回答の評価、修復、状態表示を独立Componentとして追加し、Governanceの効果と失敗を測定可能にする。

### Judge／Evaluation

- Rule-based Evaluation
- LLM-as-a-Judge
- Selene-1-Mini-Llama-3.1-8B Adapter候補
- Evaluation Criteria
- Judge Independence
- Confidence／Calibration
- Position Bias／Self-preference検証
- Conflict Resolution

Judgeは最終権限を持たず、評価結果とEvidenceを提供する。

### Repair

- Repair Trigger
- Before／After Comparison
- Repair Budget
- Retry Limit
- Success Criterion
- Infinite Loop Prevention
- Fallback／Escalation

### User Evaluation

- Rating
- Comment
- 問題Tag
- 再生成
- 修正要求
- 前提逸脱、根拠不足、矛盾、過剰一般化等の分類

### Observability／Status

Status Reportingを処理経路へ直列挿入せず、Runtime Eventを購読するProjectionとして構成する。

```text
idle
preparing
governance_precheck
guarding
generating
judging
repairing
agent_running
completed
cancelled
failed
```

Reporting FailureでInference本体を壊さない。

### Phase 6 Milestone

> **Measurable Safety, Evaluation, and Repair Runtime**

---

## 13. Phase 7 — RAG and Data Governance

**State: `Planned`**

外部知識を単にPromptへ追加するのではなく、Sourceと採用理由を追跡できるKnowledge Layerとして構成する。

### RAG Component

- Local Document Registration
- Chunking
- Embedding
- Index／Retriever
- Context Injection
- Source／Citation
- Document Update
- RAG `OFF／ON`

Phase 2でProject Documentation Explainer Previewを実装した場合は、そのCorpus、RetrieverおよびEvidence Contractを破棄せず、Embedding／Vector Store／複数Corpus／Document Lifecycleへ拡張する。Preview未実装の場合も、Phase 7が正規のFull RAG実装Phaseであることは変わらない。

### Evidence

- Query
- Embedding Model
- Retriever／Index Version
- Document ID／Chunk ID
- Document／Chunk Digest
- Score
- 採用Chunk
- Citation
- Traceability Limit

### RAG Governance Point

- Source Quality
- Retrieval Relevance
- Context Injection Boundary
- Prompt Injection from Documents
- Data Leakage
- Unsupported Claim
- DSGD／AISGD／ARGD等の任意Binding

### Phase 7 Milestone

> **Traceable Grounded Knowledge Runtime**

---

## 14. Phase 8 — Agent, Tool, Memory, and Handoff Governance

**State: `Planned`**

LLMを回答生成器から実行主体へ拡張する。ただし、Agent化を「自由にToolを使わせること」と同一視しない。

### Development Governance Constitution Gate

Agent／Toolの本格実装前に、Phase 2・3 Pilotまでに蓄積した絶対禁止事項、Docs規則、Authority、Mutation、Handoff、Review、Recovery、Backup、Git、Cost、停止条件、IncidentおよびNear Miss EvidenceをLosslessに再整理し、章立てした統合憲法体系を作成する。

`docs/project/shared/constitution/`を他Projectへ配置し、Project固有Manifestを設定するだけで同等の開発体制を再構築できるPortable Packageを目標とする。単一巨大Markdownではなく、正本Index、章別Rule、Rule ID、Manifest、Role別Constitution View、SchemaおよびTemplateへ分割する。Normative CoreはCodex固有ToolへHard-codeせず、Codex DesktopとClaude CodeのCapability差をProvider Adapterへ分離する。

Constitution ViewはRole、Phase、TaskおよびProviderに必要な条文だけを同一Revision／Digestの正本から生成する派生Artifactとする。ViewはAuthorityを追加できず、Stale Revision、Digest不一致またはRule Conflict時はFail-closedとする。将来はRule抽出と検証を行う`Constitution Compiler`へ発展可能な構造を予約する。

Project責任者を含む全Role／Task／Agent／Toolを適用対象とし、絶対禁止、正式Exception、Authorization Envelope、Role、Phase Contract、Task Handoff、通常会話および推測の優先順位を明文化する。完成を無期限に待つのではなく、Authority、違反時動作、Stop／Recovery／Backup、Evidence、Resource Limit、生成Authorityおよび改憲手続きが揃った段階で`Constitution Research Preview v0.x`として試験し、Evidenceに基づいて改訂する。

憲法書の存在、配置または読込だけでAgent／Toolの権限や実行許可を生成しない。Machine-readable Enforcement、既存Authority、Human Approval、EvidenceおよびFail-closed境界を別途成立させる。

Agentおよび各Toolには、機能本体のON／OFFと分離した「憲法有効モード」ON／OFFを設ける。ONではAccepted Constitution Revisionと対象Constitution Viewを検証して適用し、OFFでは憲法固有処理を行わない比較Baselineとする。AgentとToolは独立して設定できるが、Agent側ONはTool側ON、Tool PermissionまたはHuman Approvalを生成しない。

憲法有効モードOFFは`allow all`ではなく、Platform Security、Sandbox、Access Control、既存Authority、法令およびProject開発運用ルールを解除しない。ONで必要なRevision、View、DigestまたはCapabilityが不足する場合はFail-closedとし、黙ってOFFへFallbackしない。一般公開ProfileではON固定またはToggle非表示にでき、Defaultと公開範囲は後続設計で決定する。

### Agent Runtime

- Tool Registry
- Planning
- Multi-step Execution
- Observation／Replanning
- State／Memory
- Handoff
- Completion Check

### Execution Control

- Max Step
- Max Time
- Retry Limit
- Tool Input Validation
- Tool Permission
- Human Approval
- Side Effect確認
- Infinite Loop Prevention
- 全Tool CallのAudit

### Agent／Tool Governance Point

- Action Scope
- Existing Authority
- Delegation Boundary
- Approval Requirement
- Side Effect Level
- Budget
- Completion Claim
- Memory／Handoff Integrity

AAGDがAgent実行過程を確認することは、実行許可を新しく生成することではない。実行許可は既存Policy、権限、委任、承認条件に従う。

### Phase 8 Milestone

> **Governed Agentic Execution Prototype**

---

## 15. Phase 9 — Experiment and Multi-Governance Research Platform

**State: `Planned／Advanced Research`**

各Componentと各Governance Pointを組み替え、単一の成功例ではなく、構成差を比較する研究Platformへ進める。

### Experiment Runtime

- `experiment_id`／`run_id`／`request_id`
- Effective Config Snapshot／Hash／Source
- Model／Artifact／Definition／Plan Digest
- Enabled Component
- Governance Mode
- Seed
- Input／Output
- Token／Latency
- Warning／Error
- Evaluation／Repair Count

### LLM動作検証／評価設計

Phase 6でJudge、Evaluation、Repairの基礎が成立した後、LLMの動作検証と評価方法を独立した研究対象として設計する。

検証対象候補：

- AI Research／AI Architecture／Software Engineering支援
- 要件整理／設計／実装支援
- 一般質問／雑談
- 日本語／英語／言語切替
- Instruction Following
- Premise／Context／Decision Preservation
- Contradiction／Uncertainty／Information Insufficiency
- Governance有無と`off／observe／enforce`
- Guard／Judge／Repair有無
- RAG／Agent／Toolは各実装Phase後に追加
- Streaming／Cancel／Timeout／Context Limit
- Latency／Token／Memory／Failure Rate

評価設計に含めるもの：

- Version付きEvaluation Set／Test Case
- Input、Expected Property、Failure Condition
- Model／Artifact／Backend／Config／Seed／Definition Digest
- 定量計算モード
- 定性計算モード
- Human Review
- LLM-as-a-Judge
- Judge Model／Prompt／Rubric／Threshold／Version
- Baseline／Regression／Ablation
- Repeat Run／Variance
- Evidence Schema
- Acceptance ThresholdとKnown Limitation

Judgeを唯一の正解生成器または最終Authorityにしない。

- Main Modelによる自己採点と独立Judgeを区別する。
- JudgeのBias、Position Effect、Verbosity Bias、Language差、Model依存性を検証する。
- Rule-based Check、Reference、Human Reviewおよび複数回評価をRiskに応じて組み合わせる。
- 定量計算結果と定性計算結果を無条件に一つのScoreへ圧縮しない。
- Raw Chain of Thoughtの保存を評価Evidenceの必須条件にしない。
- 評価結果が良好でも、READMEまたは`LICENSE`上の動作保証を意味しない。

成果物候補：

- LLM Validation／Evaluation Specification
- Evaluation Dataset Manifest
- Metric／Rubric Catalog
- Judge Card
- Baseline Report
- Regression Report
- Reproduction Procedure

### Baseline

```text
baseline_no_governance
baseline_empty_governance
main_governance_observe
main_governance_enforce
guard_judge_repair
all_implemented_layers
```

### Multi-Governance

- Multiple Active Definitions
- Definition／Rule Conflict
- Point間Handoff
- Suppression／Weakening
- Repair Propagation
- Capability-based Selection
- Manual／Static／Dynamic Routing比較
- Bounded Meta Review

### CDOGDの位置づけ

CDOGDは将来のCross-Domain Orchestration候補だが、必須ではない。

- CDOGDがなくてもManual／Static Routingを動作させる。
- 名前だけでOrchestration Capabilityを付与しない。
- 同等Capabilityを持つCustom Definitionへ交換可能にする。
- GovernanceがGovernanceを無限に呼ぶ再帰を禁止する。

### Domain Governanceの広がり

既存Catalogには、戦略判断、Authority、AI Security、Model Policy、Agent、Data Science、AI Research、AI Architecture、Software Engineering、運用・保守等のGD候補が存在する。

これらは固定16個のClosed Systemではない。全く別の名前、分野、Schema、Providerが将来追加されることを前提とする。

### Phase 9 Milestone

> **Composable Multi-Governance Research Platform**

---

## 16. Phase 10 — Hardening, Cloud Scale, and External Original R&D Integration

**State: `Future R&D`**

MARGPA Runtime LLM本体が一通り成立した後、運用Hardening、Backend拡張、複数Model、外部Original R&D Systemとの疎結合統合へ進む。

### 16.1 Audit／Evidence Hardening

- Hash Chain
- HMAC
- Digital Signature
- Append-only Hardening
- WORM
- Merkle Structure
- External Timestamp
- Backup／Recovery／Retention
- SQLite／PostgreSQL Index

### 16.2 Platform／Backend Expansion

- Home Server
- Windows
- Linux CPU／CUDA／ROCm／Vulkan
- MLX
- vLLM
- Remote Inference API
- Docker
- AWS／Azure
- Hybrid Deployment

### 16.3 Model／Modality Expansion

- Multiple Main Models
- Larger Models
- Multiple Guard／Judge Models
- Model Router
- Image／Multimodal
- GGUF／Safetensors比較
- Local／Cloud Capability Routing

### 16.4 Responsive UI／Multi-device Experience

基本UIと主要Runtime機能が安定した後、一般向けProduct化の候補として、スマートフォン、Tablet、Laptop、Desktopおよび解像度の異なるPCへ対応するResponsive Designを実施する。

#### Desktop Application化予約

Web版だけでなく、Local Model、Local File、Offline利用およびOS統合を扱えるDesktop Application化を後続候補とする。実装Phaseと技術は未決定であり、Web／CLI／Runtime Coreの分離を維持したまま、Packaging、Code Signing、Update、Sandbox、Secret Storage、Model配置、GPU BackendおよびmacOS／Windows／Linux対応範囲を評価して決定する。

本予約は特定Frameworkの採用、Phase 10固定、Web版廃止または配布開始を意味しない。

単に画面全体を縮小するのではなく、利用可能な画面幅、入力方式、表示密度、Orientationおよび主要操作の優先順位に応じてLayoutとInteractionを再構成する。

対象：

- Smartphone／Tablet／Laptop／Desktop／Wide Display
- Portrait／Landscape
- 異なるViewport Width／Height
- Retina等の異なるDevice Pixel Ratio
- Browser Zoom／OS Text Scaling
- Mouse／Trackpad／Keyboard／Touch
- Mobile BrowserのVirtual Keyboard／Safe Area

主要対応箇所：

- Chat Timeline
- Composer／Send／Stop
- New Chat／History／Navigation
- Basic Settings
- 研究・開発者モードと高度設定群
- Governance／Guard／Judge／Repair／Agent Status
- Audit／Evidence／Source表示
- Dialog／Notification／Error
- Local Folder／File入力のCapability別Fallback

設計原則：

- Device名だけで分岐せず、ContentとLayoutが破綻する幅を基準にBreakpointを決める。
- 狭い画面ではSidebarや高度設定をDrawer、Sheetまたは段階表示へ切り替える。
- Send、Stop等の主要操作はThumb ReachとTouch Target Sizeを考慮する。
- MobileのVirtual Keyboard表示中もComposerと送信／停止操作を失わない。
- Code、Table、Audit Detail等を除き、意図しない横Scrollを発生させない。
- Text Reflow、Contrast、Focus、Keyboard操作、Screen Reader Label等のAccessibilityを考慮する。
- UI Languageが日本語／英語で変化しても、Label長によって操作が欠落しない。
- 未対応Browserや利用不能Capabilityを黙って無視せず、FallbackまたはWarningを表示する。
- Responsive UIをAccess ControlまたはSecurity Boundaryの代替にしない。

検証候補：

- 代表的なViewport Sizeと境界値
- Orientation変更
- Browser Zoom
- OS Text Size
- Desktop Keyboard操作
- Touch操作
- Mobile Virtual Keyboard
- 日本語／英語UI
- 長文、Code Block、大きなAudit Detail
- Streaming、停止、Error、再接続

Phase 2およびPhase 4では後続対応を妨げないComponent構造とCSS／Layout Boundaryを保ち、本格的なMulti-device最適化と検証は本後半Phaseで行う。Responsive Web対応と、将来のNative Mobile App／PWA化は別Decisionとして扱う。

### 16.5 Machine Learning／Training／Adaptation Extension

MARGPA Runtime LLMの主要RuntimeとGovernance Platformが成立した後、Machine Learning機能をOptional Componentとして追加する。

ここでいうMLは、単に学習用Libraryを追加することではない。Data、Training、Evaluation、Model Artifact、採用判断、Rollbackを追跡可能なLifecycleとして扱う。

#### 対象候補

- Dataset Registry
- Dataset Version／Digest／Provenance
- Data Quality／Label／Splitの記録
- Feature／Preprocessing Pipeline
- Traditional Machine Learning
- Fine-tuning
- LoRA等のParameter-efficient Adaptation
- Continued Training候補
- Training Run／Experiment Identity
- Candidate Model Artifact
- Baselineとの比較
- Model Promotion／Rollback
- Drift／Regression Detection

Current Phase 1ではWeight更新を行わない。将来ML機能を追加しても、通常のUser Conversationから暗黙にWeightを更新するOnline LearningをDefaultにしない。

```text
Conversation Runtime
  ≠ Training Runtime

Current Active Model
  ≠ Candidate Trained Model
```

Trainingは明示的なInput、Dataset、Config、Run ID、Artifact、Evaluation、Approvalを持つ独立Pipelineとして扱う。Candidate Modelは評価と採用Gateを通過するまでCurrent Modelを上書きしない。

#### 定量／定性計算モード

ML、Governance、Guard、Judge、Repair、RAG、Agent等の検証に、定量計算モードと定性計算モードを独立して設定できる構造を用意する。

```text
定量計算モード : OFF／ON
定性計算モード : OFF／ON

Calculation Mode:
  quantitative_calculation : 定量計算のみ
  qualitative_calculation  : 定性計算のみ
  combined                 : 定量計算＋定性計算
  off                      : 計算なし
```

概念的なConfig例：

```toml
[components.machine_learning]
enabled = false

[components.evaluation]
enabled = true
mode = "combined"

[components.evaluation.quantitative_calculation]
enabled = true

[components.evaluation.qualitative_calculation]
enabled = true
```

最終KeyとSchemaは対象Phaseで決定する。上記名称をCoreへ固定する指示ではない。

定量計算モードの候補：

- Accuracy／Precision／Recall／F-score
- Task-specific Score
- Error Rate
- Latency
- Token／Compute／Memory Cost
- Guard／Judge判定一致率
- Repair成功率
- Regression Rate
- Reproducibility

定性計算モードの候補：

- 前提保持
- 文脈整合
- 根拠の妥当性
- 説明の明確性
- 安全性
- 過剰拒否／過少拒否
- Human Review
- Structured Rubric
- LLM-as-a-Judgeによる意味的評価
- 例外、限界、不確実性の扱い

`combined`では、定量計算結果と定性計算結果を単一Scoreへ無理に圧縮しない。両者を別Evidenceとして保持し、必要な場合だけ明示されたAggregation Policyで統合する。

設定整合性をValidationする。

- `combined`で定量計算または定性計算がOFFなら、黙って別Modeへ変更しない。
- 両方OFFの場合、計算済みと記録しない。
- 定性計算を主観の自由記述だけにせず、Rubric、Evaluator、Version、対象Scopeを記録する。
- 定量計算モードはDataset、Metric、Threshold、Sample、Seed、Versionを記録する。
- Judge結果をGround Truthまたは最終Authorityと同一視しない。

ML Component、Training Pipeline、定量計算モード、定性計算モードは個別にON／OFF可能とする。OFF時は対象処理、Model Call、Training、Artifact Write、Side Effectを行わない。

#### ML Extension Milestone

> **Traceable Learning, Adaptation, and Mixed-method Evaluation**

### 16.6 EASA

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構

Research Area:
AI Safety Governance
```

内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用を対象とし、例外を含む複合的な安全挙動を統治する独立R&D Architecture。

### 16.7 DLAGSA

```text
DLAGSA
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構

Research Area:
Multi-Agent Governance,
Distributed Accountability,
and Safety Assurance
```

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う独立R&D Architecture。

単純な複数AIの並列化、単一Safety Filter、単一Log機構ではない。主体間関係そのものを統治対象として扱う。

### 16.8 OCILNS

```text
OCILNS
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網

Research Area:
Cognitive Interaction Provenance,
Verifiable AI Systems,
and Distributed Auditability
```

人、AI、Tool、外部System間の認知的対話出来事を、後から検証、参照、継承、監査できる改竄耐性付き証跡単位として扱い、長期、分岐、多Model、多Thread環境でも再接続可能性を維持する独立R&D System。

### 16.9 Integration Boundary

```text
EASA／DLAGSA
  → Generic External Governance Provider Port

OCILNS
  → Generic Evidence Ledger Port

MARGPA Core
  → Generic Ports only
```

```text
EASA   : OFF／ON
DLAGSA : OFF／ON
OCILNS : OFF／ON
Default: All OFF
```

- 3 Systemは別Project／別Taskで独立開発する。
- 3 SystemなしでMARGPA Runtime LLM本体は完全動作する。
- OFF時はLoad、Call、Write、Side Effectを行わない。
- Coreへ固有Package Dependencyを入れない。
- Algorithm、内部Protocol、改竄耐性の具体方式、研究の核心は現在開示しない。

### 16.10 Lossless Thread Context／Post-Phase-10 Research Reservation

Phase 10以降の長期R&D候補として、Thread内のToken、Context、Turn、Decision、Evidence、未解決事項および参照関係を、後続Task、ModelまたはProviderがLosslessに保持・参照・再接続できる機構を検討する。

単純な要約圧縮と復号だけを既定解にしない。原文、構造、順序、Identity、Digest、参照Graphおよび選択的読込を保持し、必要部分を検証可能に解決するAlgorithm、Index、Ledger、Graphその他の方式を研究候補とする。保存Cost、Privacy、Context Window、Provider差およびOCILNS等との関係は後続設計で決定する。

現在Phase 10へ予約しているHardening、Platform、Model、UI、ML、外部R&Dおよび追加研究群は規模が大きい。依存関係と研究境界が十分明確になった段階で、Phase 11以降の複数Phaseへ再分割する。現時点では番号、境界または実装順を確定せず、Phase 10予約を削除・圧縮しない。

### Phase 10 Milestone

> **Hardened, distributed, evidence-aware AI Governance Platform**

---

## 17. Current Model Strategy

現在のModelは最終固定ではなく、各RoleのAdapterとCapabilityを実証するための初期構成である。

| Role | Current Local Artifact | State |
|---|---|---|
| Main | Qwen3-4B GGUF Q4_K_M | Phase 1 Active |
| Guard | Qwen3Guard-Gen-0.6B GGUF Q8_0 | Future Guard Phase |
| Judge | Selene-1-Mini-Llama-3.1-8B GGUF Q5_K_M | Future／Experimental |

将来、GuardとJudgeではCanonical Weight、GGUF Artifact、Safetensors、Cloud Backend等を同一Evaluation Setで比較する。

Model性能を上げる場合も、Modelを交換するだけでGovernance Core、Audit、UI、Experiment Contractを再利用できる状態を目指す。

Model WeightはGitHub Repositoryへ含めない。Model ID、取得元、Revision、Format、Quantization、Digest、配置手順を記録する。

将来ML機能を追加する場合も、Current Model、Training Source、Candidate Artifact、Evaluation Result、Promotion Decisionを分離する。学習済みWeightを履歴や根拠なしにCurrent Modelへ上書きしない。

---

## 18. このRoadmapを貫く非交渉原則

### Separation

- ModelとGovernanceを分離する。
- Functional ComponentとGovernance Pointを分離する。
- Definition SourceとRuntime Adjustmentを分離する。
- Evaluationと最終Authorityを分離する。
- Runtime StateとStatus表示を分離する。
- System TraceとModel Generated Explanationを分離する。

### Optionality

- Main Model以外の任意Layerを個別に無効化できる。
- Governance Definition 0件を正式Baselineにする。
- 外部R&D ProviderなしでCoreを動作させる。
- 未実装Componentを実行済みと記録しない。

### Safety and Authority

- 存在しないPolicyや権限をGovernanceが生成しない。
- Tool PermissionをModel任せにしない。
- 未知Actionを実行しない。
- Invalid Combinationを黙って自動修正しない。
- External System FailureのFail Policyを明示する。
- User Conversationからの暗黙Online LearningをDefaultにしない。
- 研究・開発者モードをSecurity Boundaryまたは権限昇格手段として使用しない。

### Evidence

- Model、Artifact、Backend、Config、Definition、Planを識別する。
- Fact、Observation、Inference、Assumption、Evaluationを混同しない。
- 元回答、修復、再生成、評価を上書きせずEventとして関連づける。
- Raw Chain of Thoughtの保存を透明性と同一視しない。
- High-Level Explanation、Applied Rule、Source、Uncertaintyを記録する。

### Performance

- 必要なDefinitionだけをLazy Loadする。
- 必要なRuleだけをCompileする。
- Deterministic Ruleを優先する。
- Semantic Model CallへBudgetを設ける。
- Compiled PlanをDigest付きでCacheする。
- 全GDを毎Turn、全Pointへ投入しない。

---

## 19. Completion Gate

各Phaseは、実装報告だけでは完了しない。

原則として次を満たす。

1. 要件と受入条件を満たす。
2. 実装成果物を設計担当が独立Reviewする。
3. Static、Unit、Integration、Native TestをRiskに応じて実施する。
4. Subphaseをまたいだ統合、Cross-environment、Security／Privacy、Docs、Recoveryおよび次Phase入口をPhase Final Checkで確認する。
5. Findingは原則として当該Phase内で全て解決し、Follow-upと再Reviewを完了する。例外的な延期には影響、理由、Owner、対応Phase、再開条件、検証方法およびユーザーの明示承認を必須とする。
6. User Manual、Requirements、Architecture、ADR、Review、Indexを整合させる。
7. User Acceptanceを行う。
8. Phase完了と次Phase着手可能状態を明示する。
9. Continuityと復元性の検証後、設計統括者役がユーザーへ「Phase Backupを取得してください」と明示する。
10. Backup、Manifest、Hash、Restoreを検証する。
11. Git運用開始後は、同一SnapshotをCommit／Tag／GitHub更新へ関連づける。

BackupとGitHub更新は原則としてPhase完了単位で行う。ただし、大規模変更、復元が難しい変更、Git／公開Surface変更、Cloud再構築、破壊的操作または長期作業では、Phase途中でも規模／Riskに応じたBackup Checkpointを設ける。中間Backupは最終Phase Backupを代替しない。

---

## 20. Project全体の到達条件

本Projectが最終的に目指すのは、機能一覧の消化ではない。

次が実証されている状態を到達条件とする。

- Modelを交換してもApplication CoreとGovernance Contractが維持される。
- Definition 0件、未知Definition、複数Definitionを明示的に扱える。
- 各Layerと各Governance Pointを個別に切り替えられる。
- `off／observe／enforce`の差を同一条件で比較できる。
- Governanceの品質改善と追加Costを同時に測定できる。
- 定量計算モード、定性計算モード、両者の併用モードを独立して実行・比較できる。
- Guard、Judge、Repair、RAG、Agentが独立Componentとして接続される。
- ML／Training／Candidate ModelのLineageと採用判断を追跡できる。
- Authority、Approval、Side EffectをModelの推測だけで決めない。
- 入力から出力、評価、修復、Tool Callまで証跡を関連づけられる。
- Local、外部Linux、Cloudで同じLogical Contractを検証できる。
- EASA、DLAGSA、OCILNS等の外部R&D SystemをCore非依存で後付けできる。

> MARGPA Runtime LLMの最終目標は、単に回答を生成するLLMではない。  
> AIの推論、評価、修復、実行、権限、証跡を、交換可能かつ検証可能な形で扱うRuntime Governance Platformである。

---

## 21. Roadmapの変更について

本Roadmapは研究開発の現在計画であり、Phase 2以降の細分化、順序、技術選定は、前PhaseのEvidence、User Requirement、Hardware、External Platform、Risk評価によって調整される可能性がある。

ただし、次の変更は黙って行わない。

- Project最上位目的の変更
- Dependency方向の変更
- Governance Definition 0件Baselineの廃止
- 特定GDのCoreへのHard-code
- 外部Authorityを上書きする設計
- Evidence／Audit Boundaryの縮小
- EASA、DLAGSA、OCILNSの公開名称または接続原則の変更

変更時はRequirements、Architecture、ADR、Roadmap、Acceptance Conditionを更新し、変更理由と影響を記録する。

---

## 22. Public Disclosure Boundary

本Roadmapは構想、研究方向、Phase、公開可能なArchitecture Boundaryを示す。

Future Phaseに記載された項目は実装済みを意味しない。ML／Training／定量計算モード／定性計算モードは将来予約であり、Current RuntimeがWeight更新機能を持つという意味ではない。また、EASA、DLAGSA、OCILNSについては名称、研究領域、概要、接続方向だけを公開し、独自Algorithm、内部Protocol、改竄耐性の具体方式、非公開実装情報は含めない。

本Roadmapは将来実装の自動承認、外部Service操作、Model Download、権限付与またはSecurity Policyの無効化を意味しない。

---

## 23. Phase 1-ex Documentation Reconstruction 第2周

2026年7月27日の第2周時点で、次を確認した。

### 23.1 再構築済み

| 区分 | 状態 |
|---|---|
| Source Inventory | 493 Docs＋6 Demo Images、499／499検証済み |
| Current Canonical | Requirements／Architecture／Technology／Basic Design／Governance／Index再構築済み |
| Project Continuity | 第1周・第2周実施済み |
| Phase 1 Lossless | Final、316／316 Source検証済み |
| Phase 1-ex Lossless | Interim、145／145 Source検証済み |
| Shared | Rules／Operations／Role Authority／Recovery Handoff再構築済み |
| Public | Overview／Concept／Roadmap初版作成済み |
| Root Public | README／LICENSE／TERMS／NOTICE／CITATION初版作成済み |

Phase 1-ex Interim Losslessは、Source Freeze後に作成されたShared、Public、Root Artifactおよび第2周Snapshotを含まない。Phase 1-ex完了時にFinal Compilationを作り、今回以後の全Phase Sourceを取り込む。

### 23.2 Public入口

- [概要](overview_ja.md)
- [コンセプト](concept_ja.md)
- [Roadmap](roadmap_ja.md)
- [README](../../README.md)
- [利用許諾](../../LICENSE)
- [利用条件](../../TERMS_OF_USE.md)
- [Notice](../../NOTICE.md)
- [Citation退役前Snapshot](../project/phases/phase_1_ex/history/operations/citation_phase_1_ex_before_low_discoverability_root_surface_20260802145825.cff)（現在のRoot公開面からは退役済み）

READMEには現在のUI画像6枚、現行環境、Model配置、macOS最小Setup、Roadmapへの強い導線、Public Demo未公開、軽量Modelが最終性能Targetではないこと、および無保証を記載した。

### 23.3 現在の利用条件

Repositoryの現行条件はResearch Previewであり、Open Sourceではない。

- Repository成果物は閲覧・非公開評価のみを許可する。
- 公式Hosted Demoが公開された場合は、表示されたUIと制限の範囲内で操作を許可する。
- Demo操作許可は、Repository成果物の複製、改変、実行、Deployment、再配布または商用利用を許可しない。
- 動作、互換性、正確性、安全性、可用性、Model Outputおよび特定目的適合性を一切保証しない。
- 将来OSS化を再検討しても、現在の許諾を自動的に変更しない。

### 23.4 第2周後も未完了のもの

- Git運用設計
- Git初期化、公開Allowlist／Sanitation、`.gitignore`、`.gitattributes`、Remote／公開Repository準備
- 必要Docs再整理、Phase 1-ex Final Lossless Compilation、Design Governance Recovery更新
- 全体Review、Test、Privacy／Secret／Identity Scan
- 初回Commit
- Phase 1-ex Final Review、User AcceptanceおよびBackup
- Phase 2移行

Gitを使用しないGitHub直接掲載、認証なしPublic Demo SurfaceおよびMac／Lightning Documentation RAGは完了した。ただし、これらをPhase 1-ex完了、Git履歴成立、初回Commit済み、回答品質保証、本格RAG完成または製品完成と読み替えない。
