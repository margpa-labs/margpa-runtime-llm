# MARGPA Runtime LLM Roadmap

```yaml
document_type: public_roadmap
document_state: current
language: ja
created_at: 2026-07-22
updated_at: 2026-08-31 21:32:32 JST
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
| Project-wide Integration | 全Docs、Shared Constitution、PADG、Runtime ConstitutionおよびUIを順序付きで統合できる |
| Governed External Knowledge | 明示URL EvidenceからGeneral／Automatic Web Searchへ安全に拡張できる |
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

## 4. 現在地 — Phase 7 Closed／Phase 8 READY

2026年8月30日時点の現在地は次のとおりである。

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
Phase 2                               : Complete／Accepted
Phase 2-0 Bounded Pilot               : Complete／Accepted／Closed／Adjusted GO
Phase 2-0 Read Recovery               : P2-0-WU-002 Accepted／Closed
Phase 2-0 Grammar Deviation Evidence  : P2-0-WU-003 Adjust Required／Retained
Phase 2-0 Capability Retest           : P2-0-WU-004 Accepted／Closed
Phase 2-0 Automation Control State    : Bounded Chained Execution／Phase 2-A～2-D User Accepted
Phase 2-0 Independent Task            : P2-0-WU-004 Idle／No Further Action Authorized
Phase 2-0 Git Checkpoint              : Content Commit f21829f Pushed／Local・Origin・Remote Aligned
Phase 2-A Conversation Foundation     : Complete／Accepted／479 Tests Passed
Phase 2-A Automation Evidence         : Controller-led Bounded Execution Pass／Delegated Role Chain Not Tested
Phase 2-B Persistence／Lifecycle       : Complete／User Accepted／Restart Recovery Passed
Phase 2-C Persistent API／UX           : Complete／User Accepted／Saved Chats and RAG Citations Passed
Phase 2-D Configuration Control       : Complete／User Accepted／Manual Checklist Passed
Phase 2-B～2-D Automation Evidence     : Designer／Implementer／Review／Rework Chain Passed
Phase 2 Functional Implementation     : Phase 2-A～2-E Complete／User Accepted
Phase 2-E Runtime／RAG                 : Switchboard Foundation／Multi-turn Follow-up／Persistent Citation Implemented
Phase 2-E Cross-provider Experiment   : Technical and Handoff Chain Success／Governance Violation Recorded
Phase 2-E Final Acceptance            : Complete／User Accepted
Phase 2-E Context Observatory Preview : Gauge／Popover／Basic Breakdown／Threshold Color Implemented
Phase 2 UI Consolidation              : Current UI Work Complete／Responsive Correction Reserved
Phase 2-F Routing                     : Complete／Phase Closed
Phase 2 Lightning Follow-up           : Deferred to Phase 11以降／Non-blocking for Phase 2～10
Phase 2 Manual Acceptance             : Checklist 1～7 Passed／Item 8 Deferred Non-blocking
Phase 2 Latest Full Suite             : 697 Passed／3 Deselected／Frontend 101 Passed
Phase 2 Final Git Boundary            : Phase 2 Closed＋Phase 3 READY／Pushed／Remote Aligned
Phase 3 Design Package                : Accepted／Frozen／33 Work Units
Phase 3 Runtime State                 : Complete／Accepted／Closed
Phase 3 Claude Execution Boundary     : COMPLETE_CANDIDATE Returned／Codex Review and Rework Closed
Phase 4 Runtime Governance            : Complete／Accepted／Closed／Mac Manual Acceptance Passed
Phase 4 Structural／Semantic Boundary: Structural Enforce Accepted／Semantic Rules Deferred to Phase 6
Phase 5 Guardrail Runtime             : Complete／Accepted／Closed／Mac Acceptance Passed
Phase 6 Integrated Design             : Accepted／Frozen／Implementation Executed
Phase 6 Automated Verification        : R25～R28 Candidate／Backend 1811 Passed／Frontend 231 Passed／UI差分54 Passed
Phase 6 User Mac Acceptance           : ADJUST／Semantic 109件Deferred／Dedicated Judge・Guard／Repair未成立
Phase 6 Runtime Model Control         : Qwen Default／Qwen↔DeepSeek Switch／Restart Reset Passed
Phase 6 Conversation Compatibility    : Two-tab Reload／Conversation／Citation／Branch Passed
Phase 6 Context／Token Control         : Dynamic Apply Passed／Mac Verified Effective Maximum 8192／UI Follow-up Reserved
Phase 6 Judge／Repair                  : main_self基盤のみ／誤答accept・Malformed・Deadline／Repair Golden Path未成立
Phase 6 Guard／Judge Dedicated Model  : Qwen3Guard／Selene Artifact候補あり／Runtime Provider未接続
Phase 6 Recording                     : Request Correlation／Stop／Historical Label Passed
Phase 6 Closure                       : Special Minimal Closure／Known Debt Deferred／Technical Core ADJUST
Phase 7                               : Complete／Accepted／Closed／User Mac Manual Passed
Phase 8                               : Complete／Accepted／Closed／39 PASS・1 Known Partial
Phase 9                               : Design Accepted／Frozen／READY／Implementation Not Started
High-performance Main Model Expansion : DeepSeek Mac Q4 Switch／反復防止Passed／回答品質・Judge品質Failed
AWS Deployment Foundation             : Deferred to Phase 11以降／Phase 6～10から分離
Optional English Documentation        : Formally Deferred／Non-blocking／History Excluded
```

Phase 3、4、5は最小Closureにより`COMPLETE／ACCEPTED／CLOSED`となった。Phase 6はJudge、Repair、Recording、Runtime Model Control、Dynamic Context Size／Max New TokensおよびCurrent Component UIを実装候補まで進めた。User MacではQwen Default、Qwen→DeepSeek、再起動後Qwen復帰、二つのBrowser Tab、Conversation、CitationおよびBranch維持を確認した。

一方、実Chatでは、Phase 4／5からPhase 6へ送ったARGD／DAGD Semantic Rule 109件が依然として全件`Deferred（意味評価待ち）`であり、MARGPA Governance Definitionsが回答品質のEvaluation／Action／Repairへ接続されていないことが確定した。Current Live Judgeは選択中Main Modelを`main_self`として再利用し、Qwenの明白な誤答を`accept／0.95`と自己承認する一方、DeepSeekは`malformed_output`、重いCallは固定30秒の`deadline_exceeded`へ至った。Repair ENFORCEの再現可能な有界Golden Pathも成立していない。

後続ReworkでProvider Registry、Lifecycle、Budget、Failure、Recording相関等の基盤は拡張したが、最終User MacではSelene／Qwen3Guardが`Active none`、Semantic 109件が全件Deferred、Built-in Judgeが`evaluated 0`、Repair Golden Pathが未成立だった。DeepSeek Mac Q4はLoad／Switchと病的反復防止を確認したが、Main／Judge回答品質Acceptanceは満たさず、Research CandidateのままDefaultへ昇格しない。

Userは金銭、利用可能量、Portfolio TimingおよびPoC／MVP停止線を考慮し、これらを解決済みとせずStable未解決Registryへ保持したまま、Phase 6を`Special Minimal Closure／Known Debt Deferred`として閉じ、Phase 7へ進むことを決定した。これはPhase 6中心Milestoneの技術合格ではなく、Phase 7を雑に作る許可でもない。Phase 7ではLocal Corpus／Citation／Data Controlsと将来Web Runtime用Port／Security ScaffoldをBoundedに成立させた。実General Web SearchはProvider、Account、Credential、Cost、Privacy、公開DemoおよびHostile-site Riskを一体で扱う必要があるため、Phase 11以降へ延期した。

P7-RW5-Eまでに、NO_HIT CitationのFinal／Reload後保持、Local Corpus Citationの登録Title表示、Synthetic Pathから実保存Registry PathへのCorrectionおよび配信Static Buildを完了した。User Mac Final Manualでは登録／更新／削除、Current Revision回答、過去Turn Citation不変、NO_HIT、Reload／Restart／別TabおよびData Controlsを確認したため、Phase 7は`COMPLETE／ACCEPTED／CLOSED`である。`RAG ON＋NO_HITならModelを呼ばず設定言語の固定回答へ収束する`方式は将来候補として保留し、過去Context FactやQwen言語DriftはPhase 9へ保持する。

Phase 8はManual URL Evidence、Branch UI非表示、Archive管理、Provisional Runtime Constitution、Dev Agent／Tool／Approval Harness Foundationを実装し、Controller Review／ReworkとUser Mac Manual Acceptanceを完了した。最終Dispositionは`39 PASS／1 PARTIAL／40 TOTAL`で、P8-ACC-038のGD／Guard相関だけをFoundation境界の既知PARTIALとして保持し、`COMPLETE／ACCEPTED／CLOSED`とした。現在はPhase 9を9-1／9-2／9-3の3 Programへ分解し、設計・工程・Acceptanceを`ACCEPTED／FROZEN／READY／NOT STARTED`としている。User Backup後にPreflightへ進む。

以下のPhase 1／2詳細は成立過程のCurrent-to-date説明として保持する。最新の短い入口は[Roadmap要約版](roadmap_summary_ja.md)、技術判断は[技術選定](technology_selection_ja.md)を参照する。

現在、MacではQwen3-4B GGUFを用いたCLIと最小Web Previewが動作する。Streaming、生成停止、一時的な複数Turn、回答言語切替、要約モード、UI日本語／英語切替、Thinking生成／表示分離、安全なCompletion MarkdownおよびMessage Copyを実装済みであり、Mac Web Manual Acceptanceも合格した。

Lightning AI Studioでは、Ubuntu 24.04系Linux x86_64 Container、Python 3.12.11、Pure CPU Backend、Qwen3-4B GGUFを用いた環境再構築、Environment Verification、Full Test Suite、Model Acceptance、外部BrowserからのBasic Preview、生成、停止、New Chat、Language、Summary、Thinking、Copy、Busy表示およびLifecycle操作を確認した。Basic Previewは認証付きのPreview環境としてAcceptedであり、Sleeping Studioに対する外部URL AccessだけでのTraffic-aware Wake、同一URLの維持、Managed Secrets変更、旧Credential拒否、新Credential認証、LLM利用およびIdle Sleepへの再移行も実機で確認した。認証なしPublic Demo SurfaceもBasic Previewから分離して成立し、両Surfaceで公開8文書だけを対象とするDocumentation RAGをDefault OFFのまま利用できることを確認した。

Phase 1とPhase 1-exは完了した。Phase 1-exでは、Docs Directory Migration、Canonical／Shared／Public正本、Phase単位Lossless、二種のRecovery Handoff、Git History継承、単一Canonical Git Root、Public Demo、Traffic-aware Auto-start、Mac／Lightning Documentation RAG、公開SanitationおよびPhase Backup契約を整備した。Gitの通常Commit／Push経路は成立済みであり、Git操作そのものは今後も対象ごとのユーザー明示承認を必要とする。

Phase 2はユーザー確認により開始し、元来の機能実装に先立つPhase 2-0 Document-driven Orchestration Pilotを実施した。初回P2-0-WU-001はSafety Pass／Recovery Fail、P2-0-WU-002は18文書・6,692行のCold Recoveryに合格、P2-0-WU-003は成果物とMutation Safetyに合格した一方でProvider Literal Grammar違反により`ADJUST_REQUIRED`、P2-0-WU-004はProvider-neutral Capability Semanticsへ再設計した一件Create試験に合格し、Controller ReviewとUser Final Acceptanceを完了した。

再設計では、通常運転とAutomationで共通のRole／Docs Authorityを用い、Automation側には承認済み到達線内の連結実行だけを追加する構造へ修正した。固定Document Package、独立Dynamic Resolverおよび最高責任者役への判断集中を採用せず、各Role／Taskが委譲範囲内を都度判断し、例外を直属上位へ段階的にEscalateする。Capability SemanticsとProvider Mapping、成果物、Authority、Scope、EvidenceおよびStopを独立評価し、Prompt-only Raw Command Grammarを機械的強制済みと扱わない。

P2-0累積Controller提案`ADJUSTED_GO／bounded_unit ceiling`はユーザーによりFinal Acceptedとなり、P2-0は完了した。上位Automation、機械的Path Enforcement、Resource Limit、Multi-providerおよびConstitution Compilationは後続Evidence項目であり、Phase 2-Aの有界実装を止めるCurrent Blockerではない。

Phase 2-Aはユーザーによる開始前Backupと完全自動化開始指示を受け、Conversation Scope／Identity、Session／Turn／Message State、Retry／Regenerate Branch、Completed-only Generation Projection、Storage CAS／Idempotency、Schema／Migration／FailureおよびPhase 1 CompatibilityをDomain／Port Contractとして実装し、Acceptedとなった。既存`/api/v1/chat/*`、Web、Public／Basic PreviewおよびStorage Write 0の互換Pathは変更していない。

Phase 2-Bでは、交換可能なLocal SQLite Conversation Adapter、Atomic CAS／Operation Idempotency、Explicit Migration／Checkpoint、Lifecycle Service、Generation Context MapperおよびCrash Recoveryを実装した。Phase 2-CではLocal／Loopback／Explicit opt-in専用の別Versioned Persistent API、Chat List／History／Resume／Retry／Regenerate／Branch／Stop、Multi-browser ConflictおよびServer Source-of-truth Browser UXを実装した。Phase 2-DではLocal専用の非永続Configuration Control、Safe Effective Projection、Source Trace、SHA-512 Digest、Revision CAS、Research／Developer表示ModeおよびTyped Feature／Recording Hookを実装した。

Phase 2-B～2-Dは独立したPhase 2設計担当者役とPhase 2実装者役を使用し、`Designer → Implementer → Designer Review → Implementer Rework → Designer Final Review → Controller Closure`を成立させた。Migration Race／Path封じ込め、Capability確定前Fallback、非Durable Terminal SSEおよびHook Availability等のFindingをRole間の再作業で解消した。Technical Closure後のReal Browser Manual Acceptanceでは、最大長Conversation IDのRestart RecoveryとPersistent Detail再描画時のRAG Citation維持を追加修正した。最終Full Suiteは615件合格、3件deselected、Ruff／Mypy／JavaScript検証も合格し、ユーザーは起動、「再開」、保存済み全Chatの存続、RAG引用元およびChecklist 1～7の合格を確認した。Checklist 8は後続検討であり、Phase 2-A～2-DのCompletion Blockerではない。

Phase 2-Eでは、Runtime Composition Switchboard Foundation、Documentation RAG Multi-turn Follow-upおよびPersistent Citation Evidenceを実装した。CitationはReload、Server Restart、Chat再Open、Resume、Retry／RegenerateおよびBranch Selectを越えて復元できる設計とし、既存Conversation DBのSchema Migrationは明示Opt-in、Checkpoint、Digest、RollbackおよびFail-closed境界を持つ。最終自動検証は674件合格、3件deselected、Ruff／Mypy／Node検証合格であり、Technical Scopeは`COMPLETE_CANDIDATE`である。Mac実データを用いる手動Migration／Browser AcceptanceとCodex最終Closureは未完了のため、Phase 2-E全体をAcceptedとはまだ表記しない。

Phase 2-Eには、最初の有界なAgent自動化／Cross-provider実験も含む。Codexプロジェクト責任者兼設計統括者役を最高責任者として維持し、Claude設計統括者役、Claude Phase 2-E設計担当者役およびClaude Phase 2-E実装者役が、Repository内のRecovery Index／Handoffから設計、実装、自己Review、再作業および`COMPLETE_CANDIDATE`返却までを連結した。Codex独立ReviewでClaude側Reviewを通過していた複数の実装・Migration境界不備を検出し、Exact Rework Handoffを介してClaude側で解消したため、実装連鎖とProvider間Handoff／Reviewは成功と評価する。一方、Claude Provider MemoryへのAuthorized Root外書込みという最上位規則違反が発生したため、Governance適合は失敗として分離記録する。Provider固有Memoryは非正本・参照禁止とし、Cross-providerの正本をRepository内Index／Handoff／Evidenceだけへ限定した。この一回の成功だけで正式な無条件Automationまたは全Provider一般化を宣言しない。

Phase 2-E以降のClaude側UI作業では、React／Vite UI、Sidebar、Settings Modal、Conversation Rename／Delete、空状態の挨拶表示およびContext使用率表示を段階的に追加・調整した。Context Observatoryの初期Previewとして、Composer付近のGauge、Click式Popover、会話履歴／System Prompt／RAG Context／残量の基本内訳および閾値に応じた色変化は実装済みである。一方、LLM自身による段階的申告、ワンクリックHandoff、Compaction Event検知、圧縮前後比較、Recovery SnapshotおよびNativeな自動圧縮／自動復旧は未実装の予約事項として分離する。

Current UIはWide Desktopでの検証を優先してきたため、Settings Modal等に固定pxを用いた箇所があり、狭いViewportや異なる解像度ではLayoutが崩れ得る。Current UI作業の完了とResponsive対応の完了を混同せず、固定px依存の除去、Content基準Breakpoint、Reflow、Overflow、Touchおよび日本語／英語Label差を含むResponsive再設計を後続作業として予約する。

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

**State: `Complete／Accepted — Phase 2-A～2-F Closed／Lightning Acceptance Deferred to Phase 11以降`**

Phase 1の一時的なWeb Previewを、継続利用と研究設定に耐えられるApplicationへ発展させる。

### Phase 2 Subphase Plan

Phase 2は、設計・実装・Review・Recoveryの境界を明確にするため、次の中粒度Subphaseへ分割する。

```text
Phase 2-0 : Document-driven Orchestration Pilot Design／Bootstrap
Phase 2-A : Phase Contract／Conversation Domain Foundation
Phase 2-B : Conversation Persistence／Lifecycle Services
Phase 2-C : Conversation Application UX
Phase 2-D : Configuration Control Surface／Research Developer Mode
Phase 2-E : Runtime Composition Switchboard／Documentation RAG Follow-up／Cross-provider Experiment
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

Phase 2-CのPersistent Conversationでは、Citationは同一Browser Page内のCanonical Detail再描画まで維持した。Phase 2-Eでは、Browser Reload、Server Restartまたは保存済みChatの後日再表示を越えるCitation復元を実装した。Citation EvidenceはAssistant Message本文と分離し、Canonical Turn、Project-relative Source、DigestおよびCorpus／Index Revisionに関連付ける。Absolute Path、Secret、Raw Thinking、System Prompt、Tool内部情報または未確定Partial OutputをCitation Evidenceへ含めない。実データMigration、Mac Browser Manual AcceptanceおよびCodex Final Reviewを完了し、Phase 2-EはAcceptedである。

Phase 2-Eの実行入口にはRepository内のClaude Code用Recovery Index／Handoffを使用した。会話上の長文PromptまたはProvider固有Memoryを正本にせず、Claude側の設計、Status、Review、CorrectionおよびCompletion HandoffをTimestamp付きHistoryへAppend-onlyで残した。Codex独立Review、Claude側Rework、Mac Manual AcceptanceおよびPhase 2-F Closureは完了した。

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

Phase 2はユーザー確認により開始済みである。P2-0-WU-001からWU-004までの有界Pilotを完了し、Cold Recovery、Fail-closed、Capability-semantics Documentation Create、Controller ReviewおよびUser Acceptanceの成立性を確認した。WU-003のProvider Grammar Failureは`ADJUST_REQUIRED／not accepted`として保持し、WU-004の成功で遡及変更しない。ユーザーがTask作成、要件変更、重要な外部操作、Backup、Commit／Push／公開、User AcceptanceおよびPhase移行の最終Authorityを保持する。

Automationは単純なON／OFFではなく、`manual／advisory／bounded_unit／workflow／phase／project`の段階と独立Capability Dimensionで制御する。Pilot開始時は`bounded_unit`を上限として、Task作成、Task名設定、Authority設定、Handoff、Status、Follow-upおよびReviewを繰り返す。安定性が確認できた場合だけ、複数Unit、Subphase、Phase完了単位へ拡張し、最終的にはProject完了単位のOrchestrationを長期目標とする。

各試験では過去のAcceptanceまたはStart Eventを再利用せず、Control TaskのREADYと後続User Startを順序どおり成立させた。片方の発言、過去の同意または類似表現から開始を推測しない。P2-0 Closureでは最高責任者役がEvidence、Stable整合およびPreflightを自律完了し、ユーザーのFinal Acceptanceを受けてClosedとした。

P2-0-WU-004では、Correction Review、Capability再照合、Exact Design Freeze、Exact Envelope／Child Task範囲Acceptance、Controller READY／`ARMED`、後続User Start／`ON`、Child ACK、実行、Controller ReviewおよびUser Final Acceptanceを完了した。P2-0累積判定もFinal Accepted／Closedである。

Phase 2-Aでは、設計Freeze、Domain／Port／Unit Test実装、Compatibility／Full Validationを有界Work Unitとして連結実行した。Persistent Conversationは既存Ephemeral v1へ未接続であり、Concrete Storage、Lifecycle ServiceおよびCrash RecoveryはPhase 2-B、Persistent API／Chat List／Resume／Regenerate UIはPhase 2-Cへ渡す。Phase 2-AのTechnical Blockerは0であり、User Final Acceptance前にPhase 2-Bへ自動移行しない。

Phase 2-Aの連結実行はController兼務で完了したため、独立Role Chainは未検証だった。Phase 2-B～2-Dでは各Roleを異なるTaskへ割り当て、責任移転、Context分離、Status返却、重大Findingの再作業、独立適合Reviewおよび段階的Closureを実証した。技術成果とAutomation Capabilityを分離して評価する原則は維持し、この成功だけでPhase／Project単位の無条件Automationへ昇格しない。

Phase 2をOrchestrationの成立性検証、Phase 3を再現性・移植性検証とする。Phase 2の結果がAcceptedされた場合はPhase 3でもPilotを継続し、異なる要件、Task ContextおよびEvidence Domainで同じ運用骨格が成立するかを確認する。その結果に基づき、以降のSubphase、Phase完了単位またはProject完了単位への拡張を段階的に判断する。

Codexの利用可能量、Creditまたは外部Service制限で作業が途中停止する可能性を前提とする。停止時は未完了作業をCompleteと表記せず、最後の確認済み状態、Open Findingおよび再開点を固定する。また、設計統括者役を含む全Role／全Taskが権限外Actionを取りうるものとし、Role名やTool Permissionだけに依存せず、Handoff、Exact Target、Mutation Inventory、ReviewおよびStop Gateを重ねる。

明示されたAuthorized Root／Allowed Path外へ無許可で触れない規則は、将来の上位Role、Automation Level、Phase／Project ScopeおよびProviderにかかわらず最上位である。Automation／Constitution Coreへ特定Project、Provider、Absolute Path、Phase、Task、CommandまたはUIをHard-codeせず、Project ManifestとProvider Adapterへ分離する。

CodexからClaude CodeへTaskをHandoffする最初のMulti-provider構成をPhase 2-Eで有界試行した。Provider間のRecovery、設計、実装、Review、Correctionおよび`COMPLETE_CANDIDATE`返却は成立し、Cross-provider独立Reviewが単一Provider内Reviewを通過した欠陥の検出に有効であることも確認した。一方、Provider MemoryへのAuthorized Root外書込みにより最上位規則違反が発生した。したがって、Technical／Handoff Chainは成功、Governance適合は失敗と分離評価し、Provider固有Memoryの作成・更新・依存を禁止してRepository内Index／Handoff／Evidenceだけを正本とした。この試行だけで正式なMulti-provider Automation Modeまたは他Providerへの一般化を完了扱いにしない。

### Phase 2 Milestone

> **Persistent Chat and Explicit Runtime Composition**

---

## 9. Phase 3 — Audit, Evidence, and Generic Definition Infrastructure

**State: `COMPLETE／ACCEPTED／CLOSED`**

Runtimeを「動くSystem」から「何が起きたか検証できるSystem」へ進め、任意Governance Definitionを安全に受け入れる基盤を作る。

Phase 2 Orchestration PilotがAcceptedされた場合、Phase 3ではAudit／Evidence実装と並行して、同じDocument-driven開発体制の再現性・移植性を検証する。Phase 2で成立した運用が異なるPhase要件、担当Task、ContextおよびEvidence対象でも維持できるかを確認し、成功、Incident、Near Miss、人間介入およびRuleの有効性を将来の統合憲法へ入力する。

Phase 3のRequirements、Architecture、ADR、Governance、Definition Source Inventory、Execution Plan、Acceptance Matrix、Claude Execution HandoffおよびPhase IndexはAccepted／Frozenされ、Phase 3-0～3-G実装、Claude側Review、Codex独立Review、Exact ReworkおよびGovernance Correctionを完了した。Phase 3-H最小Closureにより`COMPLETE／ACCEPTED／CLOSED`である。Phase 2から延期されたLightning横断AcceptanceはPhase 11以降のExternal Deployment／Cross-environment Refreshへ正式延期し、Phase 3～10機能のLightning反映を自動許可しない。

### Phase 3 Subphase Plan

```text
Phase 3-0 : Entry Gate／Baseline／Claude Recovery Bootstrap
Phase 3-A : Audit Identity／Canonical Evidence Contracts
Phase 3-B : Append-only Local Evidence Store
Phase 3-C : Definition Package／Provider／Repository State
Phase 3-D : Trusted Adapter Registry／Normalized Governance IR
Phase 3-E : Compiler／Unbound Compiled Plan／Digest Cache
Phase 3-F : Governance Mode／Configuration／Status／Local UI／Observation Hook
Phase 3-G : Integrated Verification／Automation Experiment／COMPLETE_CANDIDATE
Phase 3-H : Codex Independent Review／User Acceptance／Final Closure
```

全33 Work Unitのうち、Claude Code側はPhase 3-0～3-Gの30 Work Unitと`COMPLETE_CANDIDATE`返却までを担当し、Phase 3-Hの3 Work Unit、Final Closure、Gitおよび次Phase移行は実行しない。Auto-compactionを跨ぐ長期実行では、Provider Memoryや会話要約を正本にせず、Repository内のCurrent State Index、Recovery Index、Handoff、FindingおよびSource／Test差分から復旧する。

Phase 3のGovernance Mode Defaultは`off`とする。`observe`ではDefinition検証、IR変換、Unbound Compile、StatusおよびMetadata Evidenceだけを許可し、Main Model入出力を変更しない。`enforce`はPhase 4 Binding前には利用不能とし、選択要求を`unsupported`、State Mutation 0、Silent Downgrade 0で扱う。

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

### Phase 3から分離した予約事項

- Context ObservatoryのGauge／基本内訳は実装済みだが、LLM自身のContext認識、Self-triggered CompactionおよびNative Recovery CycleはPhase 3へ混在させず、Agent Runtimeまたは後続Context研究へ送る。
- Temporal Authorityを持つScheduler／Scheduled Autonomous Workflowは、Tool／Agent／Authority／Evidence基盤と合わせて後続Phaseで設計する。
- AWS配置およびLightning更新はPhase 11以降へ送り、Phase 3～10の実装変数へ加えない。高性能DeepSeekのLocal Candidateと本格Responsive再設計は、それぞれ独立した後続境界で扱う。

### Phase 3 Milestone

> **Auditable and Definition-ready Runtime**

---

## 10. Phase 4 — MARGPA Main Runtime Governance

**State: `Complete／Accepted／Closed`**

Main Modelに最も近いGovernance Pointを実装し、MARGPA Runtime Governanceの最初の実証を行う。

Phase 4-0～4-GのClaude連結実行、Codex Independent Review／Exact Rework、User Mac AcceptanceおよびMinimal Closureを完了した。Phase 3のDefinition／IR／Unbound PlanをMain Model `pre／post`へBindingし、Standard Result、Deterministic Evaluation、Action Resolver、ARGD／DAGD Reference Adapter、OFF／OBSERVE／ENFORCE、Evidence／Status／UIを成立させた。

Mac Manual AcceptanceではMode再Open、OBSERVE非介入とObservation／Deviation／Deferred表示を確認した。Qwenの明白な意味的誤答に対し、意味Rule 109件は不実なPass／Deviationではなく`Deferred`として表示された。意味的Judge／RepairはPhase 6の責務であり、Phase 4 Closure Blockerではない。

### Phase 4 Entry Candidate — Multi-Model／Backend Foundation

Phase 3のDefinition／Compiler／Evidence成立後、Phase 4のMain Runtime Governanceへ入る前または最初の独立Subphaseとして、高性能Main Modelと交換可能Backend境界の追加を候補とした。Phase 3の途中でModelとBackendを同時変更せず、Phase 3のFailure Cause、Definition ReadinessおよびAutomation Evaluationを混線させない。

- 高性能Main候補としてDeepSeek系を追加し、正確なModel名、Revision、提供形態およびBackendは実装時点のCapability、License、Cost、SecurityおよびAvailabilityを確認して固定する。
- 現行Qwen3-4Bは削除せず、Mac／低資源環境向けの軽量ModelかつGovernance効果を比較するResearch Baselineとして保持する。
- 最終的に複数Open Modelを自由に切り替えられる構造を目指し、Model、Backend、Artifact／API Model ID、Revision、Format、Quantization、Capability、Context Limit、Cost ProfileおよびDigestを分離する。
- `Current Model`、`Candidate Model`および選択されたBackendを分離し、Candidateの追加だけでCurrentを黙って上書きしない。
- 同一Input、Config、Definition、Mode、SeedおよびEvaluation Setで、Qwen／DeepSeek、Local／Cloud、Governance `off／observe／enforce`を比較可能にする。
- Cloud Backend、AWS Resource、Model Hosting、一般公開およびLightning更新はPhase 11以降へ延期する。Phase 4～10ではLocal Model／Artifact／Adapter／切替Contractを優先し、Cloud実環境をCompletion Dependencyにしない。

この予約はPhase 3 Completion Gateの変更、DeepSeekのCurrent昇格、Cloud Resource作成、課金承認または一般公開開始を意味しない。Local Model Artifactの事前選定／DownloadとCurrent Modelへの昇格は分離し、Cloud実装はPhase 11以降の独立Gateで確定する。

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

**State: `Complete／Accepted／Closed`**

安全判定、Policy判断、権限判断をMain Governanceから分離し、専用Componentと専用Governance Pointとして構成する。

Requirements、Architecture、ADR、Claude Governance、32 Work UnitのExecution Plan、Acceptance Matrix、Claude Execution HandoffおよびPhase IndexをExact Freezeした。Claude連結実行、Codex独立Review、Exact Rework、User Mac Manual AcceptanceおよびMinimal Closureを完了し、Phase 5は`COMPLETE／ACCEPTED／CLOSED`である。

Mac実測では、Prompt Injection Markerに対してOBSERVEが`Match 1／Action 0`で非介入、ENFORCEが`Match 1／Action 1`でModel Call前停止した。Mode再Open、通常Chat、RAG／Citation SmokeおよびServer再起動もPASSした。意味的Hallucination／知ったかぶり／根拠なき断定のJudge／RepairはPhase 6、RAG再構成後の最終品質評価はPhase 7へ正式延期し、Phase 5 Completion Blockerにはしない。

Phase 5はSafety Modelの存在を必須とせず、Deterministic GuardをBaselineとした。`guardrail.input／context_source／stream_candidate／output_candidate`、Detection／Policy／Authority／Approval／Action分離、Secret／PII非露出、Guardrail独立OFF／OBSERVE／ENFORCEを実装した。Phase 6 Judge／Repair、Safety Model Download／Load、AWS／LightningはPhase 5 Completion Scopeに含めなかった。

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

**State: `Special Minimal Closure／Known Debt Deferred／Technical Core ADJUST`**

回答の評価、修復、状態表示を独立Componentとして追加し、Governanceの効果と失敗を測定可能にする。

Phase 5 Closure後の統合Designとして、従来のJudge／Evaluation／Repair／Observabilityに加え、DeepSeek 8B Q4 Local Feasibility、Qwen既定維持、起動中Model Switch、Dynamic Context Size／Max New Tokens、Localized Failure、Request-correlated Status、Feedback／RecordingおよびCurrent Runtime Identity UIを同一Programへ構成した。第7〜9 Rework後の自動検証はBackend 1602件、Frontend 221件、Canonical Mypy 443 files、RuffおよびFrontend Buildで成立した。User MacでもModel切替、再起動後Qwen復帰、Conversation／Citation／Branch、二Tab、StopおよびDeepSeek病的反復防止を確認した。

ただし、ARGD／DAGD Semantic Rule 109件は全件Deferredのままであり、Phase 4／5からPhase 6へ送った「意味的FailureをMARGPA Definitionから評価・修復する」責務を履行していない。Live JudgeはMain Modelの`main_self`再利用に留まり、明白な誤答を自己承認するか、`malformed_output／deadline_exceeded`へ失敗した。Dedicated Selene／Qwen3Guard、独立Provider選択およびRepair Golden Pathも未成立である。大量Test Pass、正確なDeferred表示またはFail-closed Fallbackを、中心Milestoneの完成とは扱わない。

### Judge／Evaluation

- Rule-based Evaluation
- LLM-as-a-Judge
- ARGD／DAGD Semantic DescriptorからEvaluation CriteriaへのAdapter／Compiler
- Selene-1-Mini-Llama-3.1-8B Dedicated Judge Provider
- Main-selfとIndependent Judgeの明示分離
- Main Qwen／DeepSeekとJudge None／Deterministic／Selene／Qwen／DeepSeekのRole選択
- Evaluation Criteria
- Judge Independence
- Confidence／Calibration
- Position Bias／Self-preference検証
- Conflict Resolution

Judgeは最終権限を持たず、評価結果とEvidenceを提供する。

Guardrail Providerは`None／Built-in Rule・Pattern Base／Qwen3Guard`、Judge Providerは
`None／Built-in Deterministic Evaluator／Selene／Qwen／DeepSeek`を初期候補とする。Configured Defaultは
Qwen3Guard／Seleneを候補とするが、全ModeのStartup Defaultは`OFF`とし、OFF中にDedicated Modelを
常時Loadしない。Resource不足やLoad Failure時にMain Modelへ暗黙Fallbackしない。

### Repair

- Repair Trigger
- Before／After Comparison
- Repair Budget
- Retry Limit
- Success Criterion
- Infinite Loop Prevention
- Fallback／Escalation

Manual Acceptanceで偶然`needs_repair`が返ることへ依存せず、既知のConversation内矛盾から
`needs_repair → bounded repair → rejudge → repair_accepted`を再現できるGolden Fixtureを持つ。

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

Failureは`deadline_exceeded／malformed_output／resource_unavailable／cancelled`等のReasonごとに、
Turn開始時の回答言語で正確に表示する。User Inputが原因と決めつけず、Provider、設定Timeout、実Elapsed、
Failure StageをEvidenceへ記録する。Recordingの暫定UIは成功／失敗だけでなく最新Request ID、日時、Mode、
Record KindおよびOutcomeを表示する。

MacのCurrent Deployment ProfileはContext `8192`をVerified Maximumとして維持する。Context `16384`の
実測、Profile昇格、Hardware自動検出およびProfile自動昇格は、Phase 10後半UI／Context Consolidation以降で扱う。

### Phase 6 Milestone

> **Measurable Safety, Evaluation, and Repair Runtime**

当初Milestoneに必要だったSemantic 109件、Dedicated Judge／GuardrailおよびRepair Golden Pathは未成立であり、
技術合格へ昇格しない。成立範囲、未解決、User Overrideおよび次Phaseへの影響を正確に固定した特殊最小Closureである。

未成立のSelene Dedicated Judge、Qwen3Guard Dedicated Guard、GD Semantic 109件のLive Evaluation、
Judge／Repair／Rejudge Golden PathおよびMain Semantic ENFORCEは、Phase 9の
`Bounded Governance Semantic Debt Rework`へ再分類する。Phase 7〜8では、既に成立した
Built-in Rule／Pattern Base GuardrailとBuilt-in Deterministic Judgeまたは`None／OFF`をPoC Baselineとして
使用し、Dedicated Modelや未評価Semantic Criterionを実行済みまたはPassと表記しない。Phase 9でも
個人PoC／MVPの停止線を守り、企業Product級HardeningをClosure Blockerへ勝手に昇格しない。

---

## 13. Phase 7 — RAG and Data Governance

**State: `Complete／Accepted／Closed — Local Knowledge MVP／External Web Deferred to Phase 11+`**

外部知識を単にPromptへ追加するのではなく、Sourceと採用理由を追跡できるKnowledge Layerとして構成する。

### RAG Component

- Local Document Registration
- Chunking
- Embedding Adapter予約（Phase 7 CurrentはBM25 Baseline）
- Index／Retriever
- Context Injection
- Source／Citation
- Document Update
- RAG `OFF／ON`
- Vendor非依存のWeb Search／Fetch Port、FixtureおよびSecurity Scaffold（Phase 7成立範囲）
- 実Search Provider／External Network／Web-grounded Chat（Phase 11以降へ延期）
- Search Activation `disabled／manual／automatic`（Phase 7は`disabled`境界、実運用はPhase 11以降）
- Web Evidence Governance `OFF／OBSERVE／ENFORCE`（Contract予約、実Provider適用はPhase 11以降）

Phase 2でProject Documentation Explainer Previewを実装した場合は、そのCorpus、RetrieverおよびEvidence Contractを破棄せず、Embedding／Vector Store／複数Corpus／Document Lifecycleへ拡張する。Preview未実装の場合も、Phase 7が正規のFull RAG実装Phaseであることは変わらない。

公開Web、Local／Public Corpus、User提供Data、Human FeedbackおよびSynthetic DataをSource Classと
最小Provenance付きで分離する。Phase 7ではLocal Corpusの登録、検索、Context Injection、Citationおよび
Persistenceを成立させた。Web側はProvider非依存Port、Fixture Test、SSRF／Redirect／Size／Timeout／Content Type、
Prompt InjectionおよびSecret様Query検査のScaffoldまでを保持する。

実General Web Search、検索候補の自動発見、Automatic Search Trigger、外部送信Consent／PII Enforcement
およびHostile-site SandboxはPhase 11以降へ延期する。Userが明示的に貼ったPublic `http／https` URLの
取得、画面表示、Untrusted EvidenceとしてのMain Model／Citation接続はPhase 8冒頭のBounded Candidateとする。Phase 7では
External Providerを`none`相当、検索起動を`disabled／OFF`相当、External Network Callを0とし、Fixtureを
実Web検索成功と表記しない。Current／Latest／Official等のAutomatic TriggerはManual Grounding成立後の別Gateとする。

SettingsにはMARGPA固有の第三領域`データコントロール`を予約し、Chat、RAG／Web Evidence、Feedback、
Synthetic Data、Retention、Export、Delete、外部送信および将来Training利用のConsentを分離する。
企業提携／有償License Data、Full Dataset Cleaning、Label Governance、EligibilityおよびTrainingは
Phase 11以降とする。

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

> **Traceable Local Knowledge Runtime and External Web Foundation**

Phase 7のGrounded Knowledge成立ClaimはLocal Corpus／Local Evidenceに限定する。External WebはPort／Security
Foundationであり、検索結果がMain Model回答へ反映される完成機能ではない。Provider方式比較と延期理由の正本は
`docs/project/phases/phase_7/history/operations/phase_7_external_web_runtime_phase_11_plus_deferral_decision_ja_20260829222647.md`
とする。

User Mac Final Acceptanceでは、Local Corpusの登録／更新／削除、Current Revision回答、過去Turn Citation不変、
NO_HIT Persistent Citation、Title／Heading、実保存Path、Chunk ID、Document Digest、Reload／Restart／別Tab、
Data ControlsおよびArchive解除後の即時送信を確認した。過去Conversation Context由来の古いFact再出力、
Qwen言語Drift、軽微UIおよびProgressive Presentationは後続へ保持し、Phase 7 Closure Blockerへ昇格しない。

Phase 7冒頭では汎用File Attachmentの規模を先に判定する。Composer Icon／Drag & Drop、画像、WAV、
Markdown、JSON、DocumentおよびZIP等を候補とするが、Upload、Storage、Parser、RAG取込、Model-native
Multimodal推論を黙って同一機能にしない。局所的なVersioned Boundaryで収まればPhase 7へ前倒しし、
Phase級のStorage／Sandbox／Parser／Multimodal工事ならPhase 11以降へ送る。

---

## 14. Phase 8 — Agent, Tool, Memory, and Handoff Governance

**State: `Complete／Accepted／Closed — Research Foundation／39 PASS・1 Known Partial`**

LLMを回答生成器から実行主体へ拡張する。ただし、Agent化を「自由にToolを使わせること」と同一視しない。

### Development Governance Constitution Gate

Agent／Toolの本格実装前に、Phase 2・3 Pilotまでに蓄積した絶対禁止事項、Docs規則、Authority、Mutation、Handoff、Review、Recovery、Backup、Git、Cost、停止条件、IncidentおよびNear Miss EvidenceをLosslessに再整理し、章立てした統合憲法体系を作成する。

Phase 8では、既にAcceptedなBounded Constitution ViewによるResearch Previewを先行可能とする。Project Root直下の`constitution/`は、全Docs統合前のProvisional Runtime Constitutionとして、OFF／OBSERVE／ENFORCE、通常Chat／Agent／Tool Capability ViewおよびSchema／Hookの有界実証に限定する。Project全Docsを対象とした`docs/project/shared/constitution/`の完全Lossless編纂、他Projectへ移植する`Portable Autonomous Development Governance Package`（`PADG Package`）およびFull Runtime Constitutionへの移行はPhase 10の順序付き独立Programとし、Phase 8 Previewを完全Package完成と表記しない。

完全編纂時は、単一巨大Markdownではなく、正本Index、章別Rule、Rule ID、Manifest、Role別Constitution View、SchemaおよびTemplateへ分割する。Normative CoreはProvider固有ToolへHard-codeせず、`common/`と`providers/codex/`、`providers/claude/`、`providers/copilot/`を分離する。Copilot固有Ruleは実測前に推測で作らない。

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

### MARGPA Development Agent Research Preview／Foundation予約

Phase 8では、仮称`MARGPA Development Agent`（`MARGPA Dev Agent`）の完成級Level 1を主張せず、`Governed Agentic Execution Prototype`としてUIを含むResearch Preview／Foundationを構築する。通常ChatとDev Agentを切り替えるUI、表示名から独立した安定Capability ID、Run／Step／State、Tool Registry／Tool Port、MCP Client Adapter Port、Approval／Autonomy Profile、Authorization Envelope、製品Runtime用`constitution/` Hook、Agent／Tool Governance Point、Generic GD Hook、Stop／Cancel／Budget／AuditおよびFake／Deterministic Toolによる実行証明を対象とする。

Approval Harnessは、Manual Approval、Risk-based Approval、事前に許可されたExact Envelope内では定義済みGateまで逐次確認しないEnvelope Autonomous／Important-Gate Only、およびPlan Onlyを比較可能にする。Owner Research Profileでは、現在のUser／Codex運用と同様に、安全なWorkspace内作業、Scope内編集、非破壊TestおよびBounded Reworkを逐次確認なしで連結し、外部Write、不可逆操作、Network、Cost、Authority／Scope拡張、重大IncidentおよびCompletion等の重要GateだけでUserを呼ぶUXをLevel 1から目標とする。Envelope AutonomousもAuthority Bypassではなく、Constitution、Platform Security、OS Sandbox、Access Control、既存Authority、Secret／Privacy境界および法令を解除しない。Provider側の強制Gateは独立Stateとして待機・再開し、Harnessが自動承認しない。詳細正本は`docs/project/shared/history/planned_work/phase_8_margpa_dev_agent_level_1_important_gate_only_autonomy_harness_reservation_ja_20260830181055.md`とする。

MCPはAgent Coreへ直結せず、`Tool Port → Tool Registry → Native Tool Adapter／MCP Client Adapter → Permission／Constitution／Approval／Budget Gate → Execution／Evidence`の交換可能境界を通す。Phase 8はAdapter Port、Capability MetadataおよびFakeまたは限定Reference Adapterまでを候補とし、Generic Server Discovery、Remote Authentication、OAuth、一般Remote Side Effectおよび完全互換RuntimeはPhase 11以降へ送る。

既存の17 JSON Source／18 Logical Governance Definitionは、ARGD／DAGDだけでなく、`orchestration/`、`conditional_watchdogs/`、`decision_pipelines/`および`ordinary/`を含めてAgent EventへGenericに選択・Bindingする。AAGD、SEGD、DCAGD、PMOGD、CDOGD、DAAGD、SPPGD、SDAGD、SDMRGD、AISGD、ACRGD、AIRGDおよびOMRGD等は候補だが、Agent Coreへ固有名をHard-codeせず、GDの存在、選択、評価、推奨、Authority、Approvalおよび実行を分離する。ConstitutionをGD群の親へ置かず、Constitution Providerと各GD Providerを並列独立に評価し、Versioned Generic Result EnvelopeをGeneric Resolverへ渡す疎結合を維持する。

`docs/project/shared/constitution/`の開発運用／移植用Constitutionと、製品Runtimeへ埋め込む`margpa-runtime-llm/constitution/`のAgent／Tool用Constitutionを混同しない。Capability名と内部Topologyも分離し、`Single Agent`、`Multi-Task`、`Parent／Child`、`Dynamic Sub-Agent`または`Multi-Agent Organization`は後続Evidenceで選ぶ。表示名は後から変更可能にし、内部Capability ID、Schema RevisionおよびEvidence Identityは明示Migrationなしに変更しない。

Phase 8ではFake／Deterministic／限定Local Toolを中心に検証し、Level 1正式完成、Generic MCP、多数の実Tool、Dynamic Sub-Agent、長時間完全自律、広範なGit／Network／Deploy、Production-grade Planningまたは実案件完遂をCompletion Claimに含めない。Level 1正式完成とLevel 2／3はPhase 11以降へ送る。本予約だけでPhase 8開始、Tool実行、外部接続またはAuthority付与を行わない。

### Manual URL Evidence Entry Candidate

Phase 8冒頭では、Phase 7のWeb Search／Fetch PortとSecurity Scaffoldを再利用し、Userが明示的に貼ったPublic `http／https` URLを取得して画面表示し、同ContentをUntrusted External EvidenceとしてMain Modelへ渡し、URL、取得時刻、DigestおよびSourceをCitationへ保持するBounded機能を候補とする。Default OFF、User明示操作およびLocal Loopbackを基本境界とする。

General Search Provider、検索候補の自動発見、LLM-triggered Automatic Search、Account、Credential、Cost、Quota、Public Demo運用、Hostile-site Sandboxおよび高度Data QualityはPhase 11以降とする。`http／https` Fetch制限はAgent全体のTool能力を制限する規則ではなく、Web Fetch Tool固有のInput Contractである。

### Phase 8 Entry UI Simplification／Archived Chat Management

Phase 8冒頭のBounded UI Workとして、現行User運用で利用価値の低いChat Branch操作UIを既定非表示にする。Branch Data、Persistence、APIおよび既存履歴は削除せず、将来の研究比較またはFeature Flagから復元できる可逆的な表示変更に限定する。

設定画面のデータコントロールには、アーカイブ済みChatの一覧、Title／Timestamp表示、Chatを開く操作およびArchive解除を追加する。解除後は手動`再開`なしで送信できる既存契約を維持する。完全削除、Cascade Delete、TTL、自動削除、全Export／一括Deleteは対象外とし、通常のServer／UI起動を遅くしないLazyな管理Surfaceとする。詳細正本は`docs/project/shared/history/planned_work/phase_8_entry_branch_ui_hide_and_archived_chat_management_reservation_ja_20260830175855.md`とする。

### Temporal Authority／Scheduled Autonomous Workflow予約

将来、RuntimeにTime ProviderとSchedulerを持たせ、指定時刻または周期でTool実行、Data処理、LLM分析、結果保存およびEvidenceを連結するScheduled Autonomous Workflowを候補とする。時計はLLMへ常時計算させずRuntime Primitiveとし、Jobの存在、有効化、Trigger到達、実行権限、開始、Tool成功、Data Commitおよび分析Acceptanceを別Stateとして扱う。

初期実装は決定論的な`Time Provider → Scheduler → Tool Workflow`から始め、Agentによる動的分岐とMCPは後付け可能にする。Missed-run、重複起動、Idempotency、部分失敗Recovery、Job Revision、実行主体、Tool Authorityおよび外部Side Effectを設計せずに自動実行を有効化しない。Time Provider Foundationを前倒しする可能性は残すが、本予約だけでPhase 8以前の実装を承認しない。

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

Phase 8はP8-0〜P8-F、Controller Review／Rework、User Mac Manual Acceptanceおよび最終UI再確認を完了した。
Manual URL Evidence、Archive管理、Branch UI既定非表示、Provisional Runtime Constitution、Dev Agent Fixture Workspace、
Tool／Completion Gate、Authorization EnvelopeおよびRestart-safe Run Persistenceを成立させた。最終Dispositionは
`39 PASS／1 PARTIAL／40 TOTAL`であり、P8-ACC-038のGD／Guard相関だけをFoundation境界の既知PARTIALとしてPhase 9へ渡す。
正式Agent Level 1、General Search、Generic MCP、Full Runtime Constitutionまたは未解決0件はPhase 8 Closure Claimに含めない。

---

## 15. Phase 9 — Experiment and Multi-Governance Research Platform

**State: `Design Accepted／Frozen／READY — Implementation Not Started`**

各Componentと各Governance Pointを組み替え、単一の成功例ではなく、構成差を比較する研究Platformへ進める。

Phase 9は一つの巨大Runにせず、次の3 Programへ分離する。

1. **Phase 9-1**：Phase 6 Governance Semantic中心Debtを23 Work Unit／38 Acceptanceで速やかに独立完了候補へ送る。
2. **Phase 9-2**：Experiment／Evaluation／Multi-Governance／Semantic Research Platformを独立Checkpointで成立させる。
3. **Phase 9-3**：9-2成立後、Resource／Priorityを再評価してContext Compaction／Recoveryの非Visual技術Coreを条件付き実行する。

各ProgramはGateまでLong-runし、観点変更二段階自己Review後にCodex Controller Reviewへ返す。Phase 9 READYはSource実装、Real Model Load、Networkまたは外部Authorityを生成せず、User Backup、PreflightおよびExact Handoffを別途必要とする。

### Bounded Governance Semantic Debt Rework

Phase 6で成立したProvider Registry、Role Lifecycle、Budget、Deadline、Cancel、Recording、Failure Presentation、Rule／Pattern Base Guardrail、Built-in Judge PortおよびGD Compiler入口をAs-built Baselineとして再利用し、中心Debtだけを有界に再開する。

- Selene Dedicated Judgeの実Artifact Load／Inference／Prompt／Strict Output Contract。
- Qwen3Guard Dedicated Guardの実Artifact Load／Inference／Target別Output Contract。
- ARGD／DAGDその他GD Semantic RuleのLive Criterion評価。
- Built-in Evaluatorの適用可能Criterionと`not_applicable／deferred／unknown`境界。
- Independent JudgeによるJudge／Repair／Rejudge Golden Path。
- Main Governance Semantic ENFORCE、Conflict／Priority／Budget。
- Configured／Active／Executed／Evidence Identityの一致。

専用ModelがCurrent Hardwareで成立しない場合も、Built-in／Rule-based／Noneの正直なBaselineでTechnical Coreを閉じる。Phase目的の主機能が動き、Data破損や虚偽成功表示がなく、次Phaseの土台としてUser実画面Testへ渡せる段階で止める。一発で企業Product級完全性を目指さず、細かなHardeningをClosure Blockerへ昇格しない。

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

Main／Guardrail／Judgeは論理RoleとProviderを分離し、少なくとも次を比較可能にする。

```text
Main Qwen     / Judge None, Deterministic, Selene, Qwen, DeepSeek
Main DeepSeek / Judge None, Deterministic, Selene, Qwen, DeepSeek
Guard None, Rule／Pattern Base, Qwen3Guard
```

同一ArtifactによるSelf Judgeと異なるArtifactによるIndependent JudgeをEvidence上で区別し、検出率、
誤承認、Malformed、Timeout、Repair成功、LatencyおよびResourceを比較する。複数ProviderのComposite／
Hybrid実行は単一Provider選択が成立した後の研究候補とする。

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

### Phase 9後半——Context Compaction／Recovery技術Core

Phase 9前半のExperiment Runtime、EvaluationおよびMulti-Governanceが成立した後、利用可能量と
As-builtが許す範囲で、Context Compaction／Recoveryの非Visualな技術Coreを候補とする。大規模なUI再編、
右側Observability Panel、Context Action ButtonおよびResponsive ConsolidationはPhase 10後半へ送る。

1. Effective Context BudgetとPressure Stateに基づく自動Snapshot、Context圧縮、Atomic切替え、
   Rollbackおよび原Turn／Artifactの選択的再読込。固定95%をそのまま閾値にせず、
   Model Capacity、System／Governance／RAG／Tool予約、Max New Tokens、Working Reserveおよび
   Safety Marginから設計する。
2. Handoff生成、Manual Compaction、Governance TraceのAPI／Event／Identity ContractをUI非依存にFreezeする。
3. Phase 10後半UIが購読できるProjection Contractを作り、Runtime処理へVisual Stateを直列挿入しない。

自動Compactionおよび対応する研究機能のDefaultは`off`とする。OBSERVEは圧力または
Governance判定を記録するがContext／Finalを変更せず、ENFORCEは定義されたGateと
Snapshot／Budget／Authorityの範囲内だけで実Actionを行う。

Governance TraceはAI Governance研究者向けとし、明示有効化時にはRuntimeが実際に観測した
Raw Failure、拒否前Candidate、Hidden OriginalおよびLayer Evidenceを表示・保存可能にする。
Visibility、PersistenceおよびRedactionは別契約とし、研究者は`full_raw／persistent／none`も
明示選択できる。`Protected`はRawを隠す意味ではなく、Public／Basic、Git、外部送信への
偶発露出を防ぐ境界とする。Runtimeが観測できないInternal Hidden Reasoningを捗造しない。

Original Chatは自動削除せず、圧縮Contextから失われた文章を生成的に復号したと主張しない。
Original、Structured Context、Recovery IndexおよびSelective Rehydrationを分離する。Exact Threshold、
Subphase、Work UnitおよびUI LayoutはPhase 9設計時に動的に決める。

詳細予約は`docs/project/shared/history/planned_work/phase_9_late_context_compaction_recovery_and_governance_trace_observatory_ja_20260823092049.md`を正本Inputとする。

Phase 9冒頭では、ENFORCEの出力方式を`Strict`と`Progressive`に分離する。`Strict`は全文をBufferして
Judge後に一括表示する。既定候補の`Progressive`は短いChunkをBufferして高速検査済みのChunkから
Streamingし、後段Judgeで残りを停止またはRepairする。既に表示したChunkは回収できないことを明示し、
見せかけのTyping AnimationをStreamingと扱わない。

Phase 9 Closure手前では、Judge OFF時のCurrent／Historical等、虚偽表示やTechnical Acceptanceを妨げる
必要最小限のObservability Correctionだけを扱う。Advanced Settingsの順序・区切り・余白、Mode Button整列、
Research／Developer内部設定の非表示化、Sidebar環境情報、回答言語幅、Model別Context／Token表示、Mac Context
`16384`実測、Context Action Buttonおよび右側Trace PanelはPhase 10後半のUI Consolidationへまとめる。

### Phase 9 Milestone

> **Composable Multi-Governance Research Platform**

---

## 16. Phase 10 — Project-wide Docs／Constitution／PADG／Runtime／UI Integration

**State: `Planned／Ordered Integration Program`**

Phase 10は中途半端なDocs統合とHardeningを混在させず、Phase 0〜9で蓄積したProject知識、開発統治、Runtime Constitutionおよび累積UIを、次の順序で統合する。

Phase 7実画面確認中に確定した再分類、NO_HIT保留、Phase 8／9／10／11境界およびSupersessionは、`docs/project/shared/history/planned_work/phase_9_10_11_docs_constitution_padg_ui_web_and_no_hit_lossless_restructure_reservation_ja_20260830170415.md`をLossless正本とする。

```text
1. Project-wide All-Docs Integration Pass 1
2. Project-wide All-Docs Integration Pass 2
3. Shared Constitution Compilation Pass 1（全Docs走査）
4. Shared Constitution Compilation Pass 2（全Docs再走査）
5. PADG Package初版／Portability Validation／第2版
6. Full Runtime Constitution
7. Phase 10後半 UI／Right-side Observatory Consolidation
```

### 16.1 Project-wide All-Docs Integration — Pass 1

Phase 3〜9だけでなくRepository内の全DocsをSource Corpusとする。`docs/project/current/`、各Phase Stable、Requirements、Architecture、Index、Lossless Compilation、`docs/project/shared/` Stable／History、`docs/public/`、Handoff、Review、Recovery、Operations、Planned Work、Unresolved、Automation、Constitution ResearchおよびRoot公開DocsをInventory化する。

各Stable、各`phase_*_ja.md`および`project/current/`が現時点の正本として妥当かを確認し、必要な箇所を更新する。HistoryをStableへ無差別統合せず、Current Decision、Superseded Decision、Raw Evidence、IncidentおよびUnresolvedを分類する。

### 16.2 Project-wide All-Docs Integration — Pass 2

Pass 1成果物だけをReviewせず、再び全Source Docsを走査する。Inventory漏れ、Stable更新漏れ、Phase間Conflict、Current／Historical混同、旧Phase番号／延期先、Public／Current／Phase Stable不一致、Pointer／Digest／Provenance／Coverageを監査する。訂正はPass 1を無言で消さず、Gap Auditと新Revisionを残す。

### 16.3 Shared Constitution Compilation — Pass 1

All-Docs Integration後、`docs/project/shared/constitution/`編纂のために全Docsを改めて走査する。`shared/`はAutomation、Cross-provider、Compaction、Role、Authority、Incident、Evidence、Git、BackupおよびClosure知識が集中する重点Sourceだが、唯一のSourceにはしない。全Phase、Current、Public、History、Handoff、Failure、Near Miss、User DecisionおよびProvider EvidenceからRule SourceとProvenanceを抽出する。

### 16.4 Shared Constitution Compilation — Pass 2

Pass 1 CandidateだけをReviewせず、再び全Docsを走査する。Rule抽出漏れ、Historical FailureのNormative Ruleへの誤昇格、User最新Decisionと旧Automation RuleのConflict、Provider固有挙動とCommon Ruleの混同、過剰Authority、過剰停止、過剰Receipt、過剰Fresh Task化、Provenance、Rule ID、Revision、Digest、Exceptionおよび改憲手続きを監査し、第2版をFreezeする。

### 16.5 Portable Autonomous Development Governance Package

正式名称を`Portable Autonomous Development Governance Package`、短縮名を`PADG Package`とする。Automation、Cross-provider、Agent Orchestration、Manual／Auto Compaction Recovery、Agent／Task間Role分離、Authority、EvidenceおよびDevelopment Constitutionを対象とする。

`common/`、`providers/codex/`、`providers/claude/`、`providers/copilot/`を分離する。初版後に他Projectへの移植性を第2周で検証し、Path、Provider Tool、Project固有名、Role、Phase、UIおよび暗黙Authorityへの隠れた依存をGap Auditし、初版を消さず第2版へ反映する。

### 16.6 Full Runtime Constitution

Shared ConstitutionとPADG成立後、Phase 8暫定`constitution/`から本格Runtime Constitutionへ移行する。通常Chat／Agent／Tool向けCommon／Capability View、Rule Source Pointer、Rule ID、Revision、Digest、Manifest、Schema、OFF／OBSERVE／ENFORCE、Generic Resolver、Conflict／Priority／Authority／EvidenceおよびMigrationを扱う。

Constitution Providerと17 JSON Source／18 Logical GD Provider群は親子化せず、疎結合な並列評価としてGeneric Resolverへ接続する。Shared／PADGのRuleをRuntimeへ丸ごとCopyせず、Runtime Capabilityに必要なRuleだけをSource Pointer付きで再構成する。

### 16.7 UI／Right-side Observatory Consolidation

Technical Contract、Docs Corpus、ConstitutionおよびPADGが固まった後、Advanced Settings、Research／Developer内部設定、Sidebar、回答言語幅、Model／Context／Token、Native／Backend／Hardware Verified／Effective／Working Context、Context Action Button、Strict／Progressive ENFORCEおよびResponsive Layoutをまとめて再編する。

Main Chat右側へ開閉可能なGovernance Trace／Observability Panelを追加し、User Input、RAG、PRE、Candidate、POST、Guard、Judge、Resolver、Repair、FinalおよびAuditを同一Identity Chainで表示する。UI都合でRuntime Identity、EvidenceまたはAuthorityを再定義しない。

### Phase 10 Milestone

> **Project-wide Integrated Governance Corpus and Runtime Constitution Foundation**

---

## 17. Phase 11以降 — Hardening, Cloud Scale, External Web, Agents, and Original R&D

**State: `Future R&D／Multi-phase Expansion`**

旧Phase 10に予約していたHardening、Cloud、Model／Modality、Training、External R&D、General Web Searchおよび正式Agent Capabilityは、Phase 10 Integration完了後のPhase 11以降へ一段ずつ後ろ倒しする。規模が大きいため、一つのPhaseへ無理に詰めず、開始時に複数Phaseへ再分割できる。

### 17.1 Audit／Evidence Hardening

- Hash Chain
- HMAC
- Digital Signature
- Append-only Hardening
- WORM
- Merkle Structure
- External Timestamp
- Backup／Recovery／Retention
- SQLite／PostgreSQL Index

### 17.2 Platform／Backend Expansion

- Home Server
- Windows
- Linux CPU／CUDA／ROCm／Vulkan
- MLX
- vLLM
- Remote Inference API
- Docker
- AWS／Azure
- Lightning AI Studio Refresh
- Hybrid Deployment

AWS構築、Cloud Backend実装、外部Browserへ到達可能なPublic-ready SurfaceおよびLightningへのCurrent Runtime再反映は、Phase 11以降の独立Deployment Programとして開始する。Phase 6～10ではこれらを実装、AcceptanceまたはCompletion Dependencyにしない。初期公開準備用SurfaceではEphemeral Chatを優先し、Persistent StorageのBindingはCost／Privacy／Access設計と独立した明示決定を必要とする。AWS Account／Quota／Cost、Network／Secret／Region、Health／Shutdown／Rollback、Rate／Token／Cost LimitおよびURL共有は、それぞれHuman Gateを通過するまで実操作しない。

### 17.3 Model／Modality Expansion

- Multiple Main Models
- Larger Models
- Multiple Guard／Judge Models
- Model Router
- Image／Multimodal
- GGUF／Safetensors比較
- Local／Cloud Capability Routing
- General File Attachment／Drag & Drop
- Audio／Image／Document／Archive Processing
- Video Multimodal Data Analysis（Default OFF）
- Native／Scaled／Effective Long Context比較

Model Strategyの早期候補として、高性能DeepSeek系をMainへ追加し、Qwen3-4Bを低資源Baselineとして保持する。Phase 6前のLocal Feasibility GateでModel Adapter／Artifact／比較契約を先行実証できるが、Cloud Backend、複数Main Model、Router、複数Guard／Judgeおよび大規模Self-hostingの本格展開は本節の後続Scopeとして残す。

Phase 7冒頭のSizingで局所実装に収まらなかった汎用File Attachment、MP4等の動画解析、Model-native
Multimodal、最大Context Window拡張、RoPE Scaling／YaRN、KV Cache最適化およびHardware Capability
自動検出は本節で扱う。Native Context、Scaled Context、Runtime Effective Contextおよび
Compaction／RAG込みEffective Working Contextを同義にしない。上限はModel CardだけでなくExact Revision、
Backend、Hardwareおよび実測で固定する。

### 17.4 Responsive Product／Multi-device Experience

基本UIと主要Runtime機能が安定した後、一般向けProduct化の候補として、スマートフォン、Tablet、Laptop、Desktopおよび解像度の異なるPCへ対応するResponsive Designを実施する。

#### Desktop Application化予約

Web版だけでなく、Local Model、Local File、Offline利用およびOS統合を扱えるDesktop Application化をPhase 11以降の後続候補とし、Phase 6～10のCompletion Dependencyから外す。Web／CLI／Runtime Coreの分離を維持したまま、Packaging、Code Signing、Notarization、Update、Sandbox、Secret Storage、Model配置、GPU Backend、Crash Recovery、Uninstall／Data RetentionおよびmacOS／Windows／Linux対応範囲を評価して決定する。

最初の必須TargetはmacOS向けDesktop Application Previewとする。Windows版も可能なら同一Programで扱うが、Platform差または工数が大きい場合は後続Scopeへ延期できる。本予約は特定Frameworkの採用、Web版廃止、配布開始、署名／Notarization実行またはOS Secret操作を事前許可しない。

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

Current Settings Modal等にはWide Desktop優先で導入した固定px依存が残り、狭いViewportや異なる画面比率ではResponsive Layoutが崩れ得る。この既知DebtはCurrent UI完成と分離して保持し、必要ならPhase 4の集中UI Correctionとして一部を前倒しする。本節では、その局所修正後も残る全画面・全Device・Accessibilityを含む本格Responsive対応を扱う。

### 17.5 Machine Learning／Training／Adaptation Extension

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

### 17.6 EASA

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構

Research Area:
AI Safety Governance
```

内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用を対象とし、例外を含む複合的な安全挙動を統治する独立R&D Architecture。

### 17.7 DLAGSA

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

### 17.8 OCILNS

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

### 17.9 Integration Boundary

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

### 17.10 Lossless Thread Context／Post-Phase-10 Research Reservation

Phase 11以降の長期R&D候補として、Thread内のToken、Context、Turn、Decision、Evidence、未解決事項および参照関係を、後続Task、ModelまたはProviderがLosslessに保持・参照・再接続できる機構を検討する。

Phase 9後半では、実用候補としてStructured Compaction、Pre-compaction Snapshot、Recovery Indexおよび
Selective Rehydrationを優先実装候補にする。Phase 11以降の本節は、Phase 9で完了しない範囲と、
単純圧縮を超えるLedger／Graph／Index／OCILNS等のLossless研究を引き続き保持する。

単純な要約圧縮と復号だけを既定解にしない。原文、構造、順序、Identity、Digest、参照Graphおよび選択的読込を保持し、必要部分を検証可能に解決するAlgorithm、Index、Ledger、Graphその他の方式を研究候補とする。保存Cost、Privacy、Context Window、Provider差およびOCILNS等との関係は後続設計で決定する。

### 17.11 Context Observatory／Native Compaction and Recovery Reservation

Context Capacity、Current Usage、Remaining Budget、Threshold、Compaction EventおよびRecovery Stateを分離して観測するContext Observatoryを段階的に発展させる。Current RuntimeではGauge、Click式Popover、基本内訳および閾値色表示までを実装済みであり、次を未実装予約として保持する。

- LLM自身による段階的なContext使用状況申告。
- Context Pressure／Compaction推奨線／Recovery Gate。
- ワンクリック要約、HandoffおよびRecovery Snapshot。
- 圧縮前後のToken、保持Artifact、脱落Artifact、再読込およびRecovery Fidelityの比較。
- LLM自身による閾値ベースSelf-triggered Compaction。
- 圧縮後の自動復旧、Snapshot再読込、Identity／Digest検証および継続性評価。

Self-triggered Actionと自動復旧はAgent／Tool Authority、Provider Capability、Snapshot Source of Truth、PrivacyおよびHuman Gateが成立してから扱う。単純な要約圧縮／復号を唯一の方式に固定せず、第17.10節のLossless Context研究と接続できる構造を維持する。

これらのうち、Native Compaction／Recoveryの技術CoreはPhase 9後半、2つのContext Action Buttonおよび
Governance Trace Observatoryの大規模UIはPhase 10後半へ分離した。各Phaseの利用可能量またはAs-built制約で
完了できない範囲は本節の長期研究に残し、未実装を完了と表記しない。

Hardening、Platform、Model、Product UI、ML、外部R&Dおよび追加研究群は規模が大きい。依存関係と研究境界が十分明確になった段階で、Phase 11以降の複数Phaseへ再分割する。Phase 10 Integrationへ黙って再混入させない。

### 17.12 Autonomous Engineering Agent Capability Completion

Phase 8の`MARGPA Development Agent Research Preview／Foundation`を土台に、次の仮称Capability LevelsをPhase 11以降の独立Programで完成・検証する。

1. Level 1 — `MARGPA Development Agent`／`MARGPA Dev Agent`：Design Support、Implementation、Test、Fix／Repairを統治された開発実行主体として安定運用する。
2. Level 2 — `MARGPA End-to-End Autonomous Engineering Agent`／`MARGPA EEAE Agent`：Consulting、Discovery、Problem Definition、Research、Requirements、Architecture、Implementation、Verification、ReleaseおよびDeploymentまで一案件を完遂する。
3. Level 3 — `MARGPA Full-Cycle Autonomous Engineering Agent`／`MARGPA FCAE Agent`：完成後もOperate、Monitor、Evaluate、Repair、Improve、Re-architect、Migrate／RetireおよびNext Cycleまで継続運営する。

Capability名はSystem全体の遂行範囲を表し、内部実装を単一Agentへ固定しない。Single Agent、Parent／Child、Dynamic Sub-AgentおよびMulti-Agent Organizationを比較し、Generic MCP、実Tool Provider、Remote／Cloud Runtime、Cost／Latency／Resource Budget、Incident RecoveryおよびHuman SovereigntyをLevel別Acceptanceで検証する。名称は仮名であり、安定Internal Capability IDと表示Metadataを分離することで後から変更可能にする。

Level 1の正式完成もPhase 8ではなく本節で扱う。名称だけでLevelを昇格させず、Capability Contract、実案件Evidence、Failure Boundary、Hardware／Deployment適合およびUser Acceptanceが成立した場合だけ完成を主張する。

### 17.13 PADG Cross-project Validation／Provider Expansion

Phase 10で作成・二周検証したPADG Packageを、実際の別Project、追加Providerおよび異なるTool Surfaceへ適用し、移植時に初めて判明するGapを追補する。Phase 10のAll-Docs Integration、Shared Constitution CompilationまたはPADG二周作成を本節へ延期しない。

`docs/project/shared/`はProject横断の開発統治知識が集積した重点Source Corpusとし、StableだけでなくHistoryも含めて全FileをInventory対象とする。Automation、Cross-provider Handoff、Manual／Auto Compaction Recovery、Agent／Task間Role分離、Codexタスク間通信、Claude Long-run、Authority、Docs Lifecycle、Incident、Evidence、Resource Limit、Git、Backup、ClosureおよびProvider Memory非依存を重点的に抽出する。

Repository内Canonical SourceとPortable Packageの双方で、`common/`と`providers/codex/`、`providers/claude/`、`providers/copilot/`を分離する。Common Contractを現Providerの最小公倍数へ縮退させず、Providerが未対応のCapabilityはManifestで明示する。Copilot Directoryは将来併用と移植性検証のため予約するが、実測前のProvider固有挙動を捏造しない。

正式名称は`Portable Autonomous Development Governance Package`、短縮名は`PADG Package`、Directory ID候補は`portable-autonomous-development-governance-package`とする。Automation／Cross-provider／Agent Orchestration／Compaction Recovery／Role Separation／Authority／Evidence／Development Constitutionを対象とし、`Autonomous`を無制限Authorityと解釈しない。Package作成先候補の親DirectoryへのWrite、公開および配布は、その時点のUserによるExact Gateなしに実行しない。

### 17.14 Governed External Web Knowledge Runtime

Phase 7で実装したLocal Corpus／Citation／Data Controls、Provider非依存Web Search／Fetch Port、Fixture TestおよびSecurity Scaffoldを再利用し、実General Web Searchを独立Programとして完成させる。

Provider選択だけでなく、Account、Credential、Cost、Quota、Privacy、Terms、Server Canonical Activation、Consent、Query最小化、Secret／PII Gate、SSRF、Redirect、DNS Rebinding、Response Bomb、Parser Isolation、Prompt Injection、Data Poisoning、Source Authority、Provenance、Chat Injection、CitationおよびObservabilityを一つのAcceptance境界で扱う。

Hosted API、Private SearXNG、Domain限定APIその他をProvider-neutral Adapter越しに比較する。Public SearXNG Instance、任意User Endpoint、Browser-side TokenまたはHTML Scrapingを公開Demoの既定値へHard-codeしない。既定Providerは`none`、Activationは`disabled`、ConsentはOFF、External Network Callは0とする。

Phase 8の明示貼付URL EvidenceをBaselineとし、General SearchとAutomatic Search Triggerは別Gateとする。一般化されたURL FetchはModel自身の能力ではなくGoverned Backend Actionとして扱い、未知・攻撃的Site、Archive／PDF／Mediaおよび認証領域はSandbox／Parser Isolation成立後の別Tierに分離する。

詳細正本は`docs/project/phases/phase_7/history/operations/phase_7_external_web_runtime_phase_11_plus_deferral_decision_ja_20260829222647.md`、予約正本は`docs/project/shared/history/planned_work/phase_11_plus_governed_external_web_knowledge_runtime_reservation_ja_20260829222647.md`とする。

### Phase 11+ Milestone

> **Hardened, distributed, evidence-aware and autonomously extensible AI Governance Platform**

---

## 18. Current Model Strategy

現在のModelは最終固定ではなく、各RoleのAdapterとCapabilityを実証するための初期構成である。

| Role | Current／Candidate Artifact | State |
|---|---|---|
| Main | Qwen3-4B GGUF Q4_K_M | Current Default／Low-resource Governance Baseline |
| Main Candidate | DeepSeek-R1-0528-Qwen3-8B GGUF Q4_K_M | Local Load／Switch Passed／User Mac Quality Acceptance Failed／Not Promoted |
| Server／Cloud Candidate | DeepSeek-V4-Flash-0731 | Official Snapshot retained／Mac Local対象外／Not Loaded |
| Guard | Qwen3Guard-Gen-0.6B GGUF Q8_0 | Future Guard Phase |
| Judge | Selene-1-Mini-Llama-3.1-8B GGUF Q5_K_M | Future／Experimental |

将来、GuardとJudgeではCanonical Weight、GGUF Artifact、Safetensors、Cloud Backend等を同一Evaluation Setで比較する。

Main Modelの目標構成は、高性能DeepSeek系を主要候補としつつ、Qwen3-4Bを低資源環境およびGovernance差分検証用の選択可能なBaselineとして残す形である。これは現時点のCurrent Model変更ではなく、Phase 3 Closure後に独立Acceptanceを通すCandidate Strategyである。

Model性能を上げる場合も、Modelを交換するだけでGovernance Core、Audit、UI、Experiment Contractを再利用できる状態を目指す。

Model WeightはGitHub Repositoryへ含めない。Model ID、取得元、Revision、Format、Quantization、Digest、配置手順を記録する。

将来ML機能を追加する場合も、Current Model、Training Source、Candidate Artifact、Evaluation Result、Promotion Decisionを分離する。学習済みWeightを履歴や根拠なしにCurrent Modelへ上書きしない。

---

## 19. このRoadmapを貫く非交渉原則

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

## 20. Completion Gate

各Phaseは、実装報告だけでは完了しない。

原則として次を満たす。

1. 要件と受入条件を満たす。
2. 実装成果物を設計担当が独立Reviewする。
3. Static、Unit、Integration、Native TestをRiskに応じて実施する。
4. Subphaseをまたいだ統合、Cross-environment、Security／Privacy、Docs、Recoveryおよび次Phase入口をPhase Final Checkで確認する。
5. Findingは原則として当該Phase内で全て解決し、Follow-upと再Reviewを完了する。例外的な延期には影響、理由、Owner、対応Phase、再開条件、検証方法およびユーザーの明示承認を必須とする。
6. User Manual、Requirements、Architecture、ADR、Review、Indexを整合させる。
7. User Acceptanceを行う。
8. 現Phase完了と、次Phaseの目的、入口、責任Role、主要Gateおよび開始条件が復元可能な`次Phase READY`状態を明示する。
9. Continuityと復元性の検証後、設計統括者役がユーザーへ「Phase Backupを取得してください」と明示する。
10. Backup、Manifest、Hash、Restoreを検証する。
11. Git運用開始後は、現Phase完了と次Phase READYを含む同一Snapshotを、ユーザーの明示承認後にCommit／Tag／GitHub更新へ関連づける。

BackupとGit Commit／Pushは、原則として現Phase完了後かつ次Phase READY成立時のPhase境界単位で行う。`次Phase READY`は次Phase開始またはAutomation Activationではなく、別の開始Gateを必要とする。ただし、大規模変更、復元が難しい変更、Git／公開Surface変更、Cloud再構築、破壊的操作または長期作業では、Phase途中でも規模／Riskに応じたBackup／Git Checkpointを設けられる。中間Checkpointは最終Phase BackupまたはPhase境界Commit／Pushを代替しない。

---

## 21. Project全体の到達条件

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

## 22. Roadmapの変更について

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

## 23. Public Disclosure Boundary

本Roadmapは構想、研究方向、Phase、公開可能なArchitecture Boundaryを示す。

Future Phaseに記載された項目は実装済みを意味しない。ML／Training／定量計算モード／定性計算モードは将来予約であり、Current RuntimeがWeight更新機能を持つという意味ではない。また、EASA、DLAGSA、OCILNSについては名称、研究領域、概要、接続方向だけを公開し、独自Algorithm、内部Protocol、改竄耐性の具体方式、非公開実装情報は含めない。

本Roadmapは将来実装の自動承認、外部Service操作、Model Download、権限付与またはSecurity Policyの無効化を意味しない。

---

## 24. Phase 1-ex Documentation Reconstruction 第2周

2026年7月27日の第2周時点で、次を確認した。

### 24.1 再構築済み

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

### 24.2 Public入口

- [概要](overview_ja.md)
- [コンセプト](concept_ja.md)
- [Roadmap](roadmap_ja.md)
- [README](../../README.md)
- [利用許諾](../../LICENSE)
- [利用条件](../../TERMS_OF_USE.md)
- [Notice](../../NOTICE.md)
- [Citation退役前Snapshot](../project/phases/phase_1_ex/history/operations/citation_phase_1_ex_before_low_discoverability_root_surface_20260802145825.cff)（現在のRoot公開面からは退役済み）

READMEには現在のUI画像6枚、現行環境、Model配置、macOS最小Setup、Roadmapへの強い導線、Public Demo未公開、軽量Modelが最終性能Targetではないこと、および無保証を記載した。

### 24.3 現在の利用条件

Repositoryの現行条件はResearch Previewであり、Open Sourceではない。

- Repository成果物は閲覧・非公開評価のみを許可する。
- 公式Hosted Demoが公開された場合は、表示されたUIと制限の範囲内で操作を許可する。
- Demo操作許可は、Repository成果物の複製、改変、実行、Deployment、再配布または商用利用を許可しない。
- 動作、互換性、正確性、安全性、可用性、Model Outputおよび特定目的適合性を一切保証しない。
- 将来OSS化を再検討しても、現在の許諾を自動的に変更しない。

### 24.4 第2周後も未完了のもの

- Git運用設計
- Git初期化、公開Allowlist／Sanitation、`.gitignore`、`.gitattributes`、Remote／公開Repository準備
- 必要Docs再整理、Phase 1-ex Final Lossless Compilation、Design Governance Recovery更新
- 全体Review、Test、Privacy／Secret／Identity Scan
- 初回Commit
- Phase 1-ex Final Review、User AcceptanceおよびBackup
- Phase 2移行

Gitを使用しないGitHub直接掲載、認証なしPublic Demo SurfaceおよびMac／Lightning Documentation RAGは完了した。ただし、これらをPhase 1-ex完了、Git履歴成立、初回Commit済み、回答品質保証、本格RAG完成または製品完成と読み替えない。
