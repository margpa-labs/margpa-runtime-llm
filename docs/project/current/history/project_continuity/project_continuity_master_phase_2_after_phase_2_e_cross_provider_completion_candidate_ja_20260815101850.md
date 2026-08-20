# MARGPA Runtime LLM Project Continuity Master

```yaml
document_id: project_continuity_master
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-08-15 10:18:50 JST
owner: Nazuna Research
active_phase: phase_2_e_mac_manual_acceptance_pending
public_repository_eligible: true
rag_default: true
```

## 1. Project Identity

```text
Project Name : margpa-runtime-llm
Display Name : MARGPA Runtime LLM
Public Author: Nazuna Research
Concept Name : Nazuna Research Governance LLM
```

Model、Governance、Guardrail、Judge、Repair、RAG、Agent、Tool、Memory、Auditおよび外部R&D機構を疎結合に接続し、構成差を証跡付きで比較できるRuntime Governance型AI研究基盤を作る。

## 2. Current Position

```text
Phase 0                       : COMPLETE
Phase 1                       : COMPLETE／ACCEPTED
Phase 1 Backup                : COMPLETED／VERIFIED
Phase 1-ex                    : COMPLETE／ACCEPTED
Documentation Migration      : COMPLETE／LEGACY ROOT RETIRED
Documentation Reconstruction : COMPLETE／CURRENT STATE MAINTENANCE ACTIVE
Git／GitHub                   : OPERATIONAL／SINGLE CANONICAL ROOT／MAIN ALIGNED AT E007110 BEFORE CURRENT CHECKPOINT
Simple Documentation RAG     : MAC／LIGHTNING BASIC／PUBLIC ACCEPTED
Optional English Docs        : FORMALLY DEFERRED／NON-BLOCKING／HISTORY EXCLUDED
Lightning Basic Preview      : MANUAL LIFECYCLE ACCEPTED
Lightning Auto-start         : ACCEPTED／GO
Traffic-aware Wake-up        : REPEATED WAKE／SLEEP PASS
Public Demo                  : IMPLEMENTED／ANONYMOUS ACCESS ACCEPTED
Phase 2                       : STARTED／PHASE 2-E TECHNICAL COMPLETE_CANDIDATE
Phase 2-A～2-D                 : COMPLETE／USER ACCEPTED
Phase 2-E Functional Work     : TECHNICAL COMPLETE_CANDIDATE／MANUAL ACCEPTANCE PENDING
Phase 2-E Cross-provider      : TECHNICAL・HANDOFF SUCCESS／GOVERNANCE VIOLATION RECORDED
```

Phase 1でmacOS MetalとLightning Linux x86_64 Pure CPUのCLI／Web Runtimeを成立させ、ユーザーによるMac／Lightning Web Acceptance、Basic認証、停止、再送信、New Chat、Language、Summary、Thinking、Copy、BusyおよびPublic URL確認を完了した。

Phase 1-exはFinal Docs、Final Lossless、二種のRecovery、Full Test／Static Gate、Backup、Commit／PushおよびLocal／Origin／GitHub一致を通過し、ユーザー確認を含めComplete／Acceptedである。Git基盤と通常運用経路もAccepted／Operationalである。Phase 2-0 Automation Pilotは完了し、Phase 2-A～2-Dは実装とユーザーMac Acceptanceを完了した。Phase 2-EはClaude Codeへの有界Cross-provider委譲、Codex独立ReviewおよびClaude側Reworkまで完了し、Technical `COMPLETE_CANDIDATE`である。現在はClaude側Mac Manual Acceptance ResultとCodex Final Closureを待つ。

## 3. Current Runtime

```text
Main Model       : Qwen3-4B-GGUF Q4_K_M
Local Backend    : llama-cpp-python 0.3.34／Metal
External Backend : llama-cpp-python 0.3.34／Pure CPU
Local Python     : 3.13.14
Lightning Python : 3.12.11
UI               : FastAPI Minimal Web
Storage          : Browser Memory v1／Local SQLite Persistent Conversation v2 Opt-in
Governance       : Design only／Not implemented
Documentation RAG: Local Project Corpus／Lightning Public Corpus／Persistent Citation Candidate
Git Working Root : margpa-runtime-llm／main
```

## 4. Completed Capability

- Model Port／GGUF／llama.cpp
- Config Layer／Deployment Profile／Capability
- Streaming／Cancel／Model Busy
- CLI／Minimal Web
- Response Language／UI Language
- Thinking Execution／Visibility
- Summary Mode
- Safe Markdown／Copy
- macOS Metal Acceptance
- Lightning Pure CPU／External Web Acceptance
- Lightning Traffic-aware Auto-start／Anonymous Public Demo
- Documentation RAG／Citation／Fail-closed Boundary on Mac and Lightning
- Existing Git History継承／Source→Target統合／PR Merge
- Single Canonical Git Working Root
- Phase 1 Backup
- Phase 1 Lossless Documentation Compilation

## 5. Active Phase 1-ex Work

完了済み基盤：

- Documentation Migration／Source Inventory／Current Canonical／Shared／Public初版
- Phase 1 Final Lossless／Phase 1-ex Interim Lossless
- Project Continuity Master／Roadmap第1周・第2周
- Lightning Traffic-aware Auto-start Acceptance

現在の残工程：

1. 必要Docsの累積再整理と現状更新。
2. Phase 1-ex Final Lossless Compilation／Manifest。
3. Phase 1-ex完了版Design Governance Recovery Manifest。
4. 全体Review／Full Test／Static Check／Link／Privacy／Publication Sanitation。
5. Open Findingの解決またはユーザーが明示承認したDeferral。
6. User Acceptance。
7. Phase 1-ex Backup取得をユーザーへ明示依頼し、Backup Evidenceを確認。
8. 必要な最終Docs差分がある場合のReview済みCommit／Push判断。Git基盤の再構築は不要。
9. Phase 1-ex完了Tag／Releaseの別判断。
10. Phase 1-ex完了・Phase 2着手可能宣言後のPhase 2。

Stage 6で作業余力がある場合は、Current／Shared／Publicの非History Stable文書すべてについて、日本語正本と同じ粒度の英語派生版を作成する。全`history/`以下は対象外とする。余力がない場合は後日またはPhase 2前半へ延期し、英語版未作成をPhase 1-exの必須Blockerにしない。

## 6. Role Model

```text
設計統括者役:
  Project全体、Cross-Phase、Current Canonical、Final Review
  Phase完了時の完全復元PackageとReconstruction Validation

Phase別設計者役:
  Phase 2以降のPhase-local Requirements／Architecture／ADR

実装者役:
  src／tests／scripts
  Accepted Handoff範囲のconfig等

対外Docs役:
  README／LICENSE／NOTICE／CITATION／docs/public
```

Current Canonical、Shared PolicyおよびFrozen Compilationは、Owner以外の担当には原則Read-onlyである。

Phase 2は、Document-driven Codex Task Orchestrationの最初の正式Pilotとする。Phase 1-ex完了後、プロジェクト責任者兼設計統括者役がPhase 2 Index、開始用Handoff、Reading OrderおよびWrite Authorityを用意し、ユーザーの明示指示後に独立した`Phase 2設計担当者役`Taskを作成する。設計統括者役としてその成果をReviewし、Accepted後にだけ実装者役へHandoffする。これは完全自律化またはUser Authorityの代替を許可しない。

Phase 2は2-A～2-Fへ分割する。2-AでPhase Contract／Conversation Domainを固定し、2-BでPersistence／Lifecycle、2-CでConversation UX、2-DでConfiguration Control Surface／Research Developer Mode、2-EでRuntime Composition Switchboard／Documentation RAG Follow-up、2-FでCross-environment Acceptance／Phase Closureを扱う。詳細は[Phase 2 Subphase／Task Orchestration Preplan](../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)を開始前Sourceとする。

Phase 2設計担当者役とPhase 2実装者役は専用の独立Taskを基本案とする。実装者TaskはPhase内で継続利用できるが、Context Limit、Service利用可能量、Authority逸脱、Status不備または繰り返し失敗が安全な継続を妨げる場合は、旧Taskの最終Evidenceを固定してから更新する。

Codex利用可能量またはCreditによる途中停止を正常な運用前提とし、未完了状態をCompleteと表記しない。設計統括者役を含む全Role／全Taskは権限逸脱しうるとし、Role名、長期の成功実績またはTool PermissionをAuthority遵守の保証とみなさない。Mutation前のScope解決、変更後のMutation Inventory、Cross-role Review、即時停止およびRecovery Evidenceを組み合わせる。

## 7. Major Decisions

- Modular Monolith
- Model／Backend／GD／Storage／UIの分離
- Application ConfigとDeployment Profileの分離
- Governance Definition 0件Baseline
- 共有Control Plane＋分散Governance Point
- 各Componentと専用Governanceの個別切替
- `off／observe／enforce`
- Raw Thinking非保存
- Audit原本はAppend-only JSON／JSONL候補
- Local Macを日常開発、Lightningを外部互換実証に使用
- Public RepositoryへModel、Credential、実Logを含めない。
- Basic PreviewとPublic Demoを別Access Profileとする。
- Public DemoはSide-effect-free、RAG／Tool／外部操作なしとする。
- Mac限定RAGでもExternal Adapter Hookを持つ。
- Current／Shared／Publicは日本語正本を必須とする。英語派生版を作る場合は同じ粒度とし、全`history/`以下は対象外とする。Phase 1-ex Stage 6に余力がなければ後日またはPhase 2前半へ延期する。

## 8. Known Limitations

- Main Modelは小型であり、回答品質や事実性を保証しない。
- Lightning Pure CPUは生成が遅い。
- ConversationはBrowser Reloadで消える。
- Guardrail、Judge、Governance、汎用AuditおよびAgentは未実装。Documentation RAGは実装・受入済みだが、小型ModelのHallucination、Retrieval取捨選択、Multi-target QueryおよびGroundingの精度改善は後続Phaseで扱う。
- Lightning Traffic-aware Auto-startは現在のBasic Preview用途でAccepted／GOであり、複数回のWake／Sleepを確認した。ただし観測Cold Startは約3～10分で、Production SLAまたは将来環境の性能保証ではない。
- Public DemoとTraffic-aware Auto-startは受入済みだが、LightningのCold Startは数分～約10分の幅があり、Production SLAまたは常時稼働を保証しない。
- Linux／Windowsの全Platform自動Routingは後続検証が必要。
- Mobile Responsive Acceptanceは未実施。
- Summaryは情報を省略・変形する可能性がある。
- Thinking内容は正確な内部状態を保証しない。
- Current Main ModelはHardware制約下の小型Modelであり、Projectの最終品質上限を示さない。
- Public／Canonical Docsは再構築中であり、Initial Commit前にもう一度全体整合を確認する。

## 9. Independent R&D Reservations

### 9.1 EASA

```text
Exception Aware Safety Architecture
例外認識型安全統治機構
Research: AI Safety Governance
```

内部安全傾向、周辺安全制御、入力文脈および生成過程等の相互作用を対象とし、例外を含むComposite Safety Behaviorを扱う。`Embedded Safety Layer`は作業概念であり、単一物理Layerの存在を断定しない。

MARGPAとはGeneric External Governance Provider Portで接続し、Default OFFとする。

### 9.2 DLAGSA

```text
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構
Research:
  Multi-Agent Governance,
  Distributed Accountability,
  and Safety Assurance
```

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う。単純な複数AIの並列化や単一Filter／Logではない。`LEA`の意味を本Project側で推測または再定義しない。

MARGPAとはGeneric External Governance Provider Portで接続し、Default OFFとする。

### 9.3 OCILNS

```text
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
Research:
  Cognitive Interaction Provenance,
  Verifiable AI Systems,
  and Distributed Auditability
```

人、AI、Tool、外部System間の認知的対話出来事を、検証、参照、継承、監査できる改竄耐性付き証跡単位として扱う。長期、分岐、多Model、多Thread環境でも、入力、出力、順序、時刻、判断根拠、未解決事項、継承対象および改変検知情報の再接続可能性を維持する。

LLM回答精度の直接向上を目的としない。MARGPAとはGeneric Evidence Ledger Portで接続し、Default OFFとする。

### 9.4 Disclosure Boundary

上記3機構は構想の存在と方向性を公開するが、核心Algorithm、内部Protocolまたは具体的な改竄耐性方式は本書へ記載しない。Phase 10で別Project／別Taskの成果を疎結合統合する。

今後さらに多数の外部Systemを追加する可能性があるため、固有名称を前提にしないGeneric Hookを維持する。

## 10. Backup／Release

Phase 1 Backup：

```text
Snapshot : 20260726121941
Files    : 422
SHA-512  : 9eaabdee62a36e072df5d990d68e9986ca34b2894f8d6212ac3db4c26c85b2947be6052e0b4bbace2575f774a28eb1694a8e6a846330d6b1c307b75d6931b483
Status   : VERIFIED
```

変更後のPhase 1-ex順序では、Local Git開始前にGitを使用しないGitHub掲載準備と一時掲載を行う。掲載対象、操作方法および完了条件はユーザーの後続指示を待つ。

その後、Public Demo、Mac簡易Documentation RAG、Git運用設計、Git初期化／公開Sanitation、必要Docs更新および全体Reviewを経て、ユーザーの明示許可後に初回Commitを作成する。Stage 1の掲載物とGit管理Repositoryの関係、Remote公開時点および初回Commitとの順序はGit運用設計で確定する。

各Phaseでは、完了宣言前にPhase Final Checkを実施し、Phase全体の要件、統合、Test、Cross-environment、Security／Privacy、Docs、Recovery、Open Findingおよび次Phase入口を確認する。Findingは原則として当該Phase内で全て解決し、例外延期には完全な影響・再開・検証記録とユーザーの明示承認を必須とする。

その後、設計統括者役のPhase完了・次Phase移行可能宣言後、Phase Backupの直前にDesign Governance Continuity RefreshとReconstruction Validationを行う。これが未完了の場合、Phase Backupおよび後続公開工程へ進まない。完了後、設計統括者役は必ず「Phase Backupを取得してください」とユーザーへ明示し、完了報告後にManifest、HashおよびRestoreを検証する。規模、復元難度、不可逆性または作業期間に応じ、Phase途中でもBackup Checkpointを勧告する。詳細は[Phase Completion Review／Backup Gate](../../shared/operations/phase_completion_review_and_backup_gate_ja.md)に従う。

## 11. New Task Reading Order

1. [Current Documentation Index](../documentation_index_ja.md)
2. [Requirements](../requirements/requirements_specification_ja.md)
3. [System Architecture](../architecture/system_architecture_ja.md)
4. [Runtime Governance](../governance/runtime_governance_specification_ja.md)
5. [本書](project_continuity_master_ja.md)
6. [Active Phase Index](../../phases/phase_1_ex/phase_index_ja.md)
7. [Documentation Structure／Task Operations](../../shared/operations/documentation_structure_and_task_operations_ja.md)
8. [Design Governance Handoff](../../shared/design_governance_handoff/design_governance_handoff_ja.md)
9. 必要なCompleted Phase Compilation
10. 必要時のみRaw History

## 12. Resume Checklist

- Active PhaseとCurrent Indexを確認する。
- Role AuthorityとWrite Scopeを確認する。
- Latest Phase Index、Open Finding、Handoffを確認する。
- Source／Config／Docsを変更する前にユーザー許可と担当境界を確認する。
- Historyを勝手に編集しない。
- Model、Credential、外部ServiceまたはGit操作を自動実行しない。
- 新しい決定をCurrent、Active Phaseおよび必要なPublic文書へ反映する。

## 13. Design Governance Complete Recovery

### 13.1 Objective

設計統括者役Taskが長期化、Context Limit、障害、手動終了または再作成により継続不能になっても、新しい設計統括者役TaskがDocsだけから現設計統括者役を完全に引き継げる状態を維持する。

設計統括者役を復元できれば、設計統括者役は次を再作成できる。

- Phase別設計者役
- 実装者役
- 対外Docs役
- Review／Handoff／Statusの読解順序
- 次Phaseの開始Handoff

### 13.2 Mandatory Timing

原則として各Phase完了後、Phase Backupを取得する直前に実施する。

```text
User Acceptance／User Test Acceptance
  → 設計統括者役のPhase完了・次Phase移行可能宣言
  → Current／Shared／Continuity Refresh
  → Stable変更前後History Snapshot
  → Design Governance Recovery Manifest
  → Reconstruction Validation
  → Phase Backup
```

TaskがPhase途中で限界へ近づいた場合は、Phase完了を待たず臨時Refreshを行ってよい。臨時Refreshも同じHistory、HashおよびIndex規則に従う。

### 13.3 Recovery Source Set

新Taskは次を正本入口とする。

1. Current Documentation Index
2. Current Requirements／Architecture／Governance
3. Project Continuity Master
4. Shared Documentation Rules／Operations／Role Authority
5. Active Phase Index
6. Completed Phase Index／Lossless Compilation／Final Review
7. 最新のDesign Governance Recovery Manifest
8. 最新Accepted Handoff／Status／Review
9. 必要時だけRaw History

### 13.4 Required Recovery State

Recovery Packageは少なくとも次を欠落なく保持する。

- Project Identity、目的、設計原則
- Phase一覧、完了状態、Active／Next Phase
- Accepted Requirements、Architecture、ADR、Governance
- Model、Backend、Runtime、Config、Deployment Profile
- 実装済み機能、Test、Known Limitation
- Open Finding、未決事項、保留項目、再評価条件
- Role Authority、Write Scope、External Action Boundary
- Docs構造、Append-only規則、Stable History規則
- External Serviceの状態とユーザー担当操作
- Backup、Git、GitHub、Public Demo、Licenseの状態
- 主要Artifact Path、Version、SHA-512
- 次に行う安全な一手

Credential実値、個人情報、Private URLまたは非公開ModelをRecovery Packageへ含めない。

### 13.5 Recovery Manifest

設計統括者役専用Historyへ次を追加する。

```text
docs/project/shared/history/design_governance_handoff/
design_governance_recovery_manifest_YYYYMMDDHHMMSS.md
```

ManifestはSource Path、SHA-512、Reading Order、Current Phase、最新Accepted Review、未完了作業、Known External DependencyおよびReconstruction Validation結果を記録する。

### 13.6 Completion Condition

旧設計統括者役Taskの会話内容を参照せず、次を説明・再開できれば`pass`とする。

- 何を作っているか
- 現在どこまで完了しているか
- 何が正本か
- どの判断がAcceptedか
- 何が未確認・未許可か
- 各担当がどこへ書けるか
- 次に何を安全に行うか
- 必要な担当TaskをどのDocsから復元するか

一つでも解決不能な場合、Recovery Packageは未完了であり、Phase Backupへ進まない。

## 14. Project ContinuityはProjectの生命線

本書は簡易Status、直近差分または次作業だけを示す文書ではない。本Projectを新しいTaskへ継承し、過去の再説明なしで設計と作業を再開するための累積・自己完結のProject継続性正本である。

本書の更新では、情報ロスを一切許さない水準を適用する。

- Project Identity、目的、設計思想および独自性を保持する。
- 完了済み、進行中、未着手、保留、却下および再評価条件を保持する。
- Accepted Decision、例外、Known Limitation、Open Findingおよび外部状態を保持する。
- Phase、Runtime、Model、Backend、Docs、Role、Backup、Git、Public Demo、LicenseおよびR&D Hookの状態を保持する。
- 次の安全な一手だけでなく、その前提、禁止事項、Authorityおよび完了条件を保持する。
- EASA、DLAGSA、OCILNSおよび将来のGeneric External Hookを、後続実装が接続可能な粒度で保持する。

新版をDiff-onlyにしない。過去版を読まなければ現在状態を理解できない構成を禁止する。更新後の本書単体と参照先から、現時点のProjectを復元できる状態を維持する。

訂正、優先順位変更またはScope変更時も、更新前原文を`docs/project/current/history/project_continuity/`へ完全保存する。現在無効になった内容は黙って削るのではなく、必要に応じて旧状態、変更理由、現在状態および再評価条件を明示する。

この厳格な運用は、情報ロスによる再説明必要化、復元不能状態、判断の再作成および機会損失を防ぐために行う。

## 15. Design Governance HandoffのStable入口

設計統括者役を新Taskへ復元するための共通入口を次へ置く。

```text
docs/project/shared/design_governance_handoff/
design_governance_handoff_ja.md
```

変更前後Snapshot、Phase完了時Recovery ManifestおよびReconstruction Validation Evidenceは次へAppend-onlyで保持する。

```text
docs/project/shared/history/design_governance_handoff/
```

原則各Phase完了後、Phase Backup直前に、本書、Current Index、Shared Rules、Active／Completed Phase IndexおよびDesign Governance Handoffを一組としてRefreshする。

設計統括者役TaskがPhase途中でContext Limit、障害または継続困難へ近づいた場合は、Phase完了を待たず臨時Refreshを行う。臨時Refreshも更新前後Snapshot、Hash、変更RecordおよびIndex規則を省略しない。

新Taskが設計統括者役を完全復元できれば、そのTaskは次も復元できなければならない。

- Phase別設計者役のScopeと開始Handoff
- 実装者役のAccepted HandoffとWrite Boundary
- 対外Docs役のPublic SourceとReview Boundary
- 各担当の最新Status、Reviewおよび次の安全な作業

## 16. Foundational Context／制約

### 16.1 初期実行環境

```text
Device          : MacBook Pro Mac14,9
SoC             : Apple M2 Pro
CPU             : 10 Core
GPU             : Apple Integrated GPU
Memory          : 16GB Unified Memory
Architecture    : ARM64
Acceleration    : Metal
CUDA on macOS   : 使用不可
```

16GB Unified MemoryをOS、Model、KV Cache、UI、RAG、Auditおよび将来Componentで共有する。複数大型Modelの同時常駐を初期前提にしない。小型Modelの回答品質をProject全体の完成条件にせず、交換可能な骨格、統治、証跡および比較可能性を先に成立させる。

### 16.2 Project Priority

1. 要求機能が実際に動く。
2. 各Module／Layerを分離、交換、無効化、Testできる。
3. Governance、Audit、説明、Evaluation、Repairが成立する。
4. 現在のMacで継続開発できる。
5. GitHubへ研究成果として提示できる。
6. 将来のHome Server／Cloud移行時にModel／Backend交換だけで再開できる。
7. Performance、Context Length、回答品質はHardware更新後にも強化できる。

### 16.3 Initial Non-goals

- 独自基盤Modelの事前学習を主張しない。
- Phase 1ではFine-tuning、LoRA、DPO、RLHF、継続事前学習を行わない。
- Model Weight、Private RAG資料、実会話Log、CredentialをRepositoryへ含めない。
- 初期構成をMicroservicesにしない。
- SQL、Docker、Cloud SDKまたは特定FrameworkをCoreの必須Dependencyにしない。

## 17. Architectural Invariants

### 17.1 Separation

- ModelとBackendを分離する。
- Functional Componentと専用Governance Pointを分離する。
- Governance Definition SourceとRuntime Adjustment／Bindingを分離する。
- Evaluation、Recommendation、Executed Actionおよび最終Authorityを分離する。
- Runtime StateとStatus Reportingを分離する。
- System TraceとModel Generated Explanationを分離する。
- UI、Application、Domain／Port、Adapterの依存方向を維持する。
- OS、Device、Path、Cloud SDKおよびFramework固有処理を境界へ閉じ込める。

### 17.2 Optionality

Main Model以外のComponentと、そのComponent専用Governanceを独立して切り替える。

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
External R&D Provider
```

Governanceは`off／observe／enforce`を区別する。OFF時は対象処理、Model Call、Load、WriteおよびSide Effectを行わない。依存関係上無意味または危険な組合せを黙って受理しない。

### 17.3 Generic Extension

- Model名、File名、Directory名、GD略称をRuntime Semanticsにしない。
- Governance Definition 0件を正式Baselineにする。
- 未知名称、未知Schema、任意JSONまたはCustom Providerを、明示Adapter／Compiler／Bindingなしに実行しない。
- 将来の外部System名をCore Enumへ固定しない。
- Component、Definition、Point、ActionおよびCapabilityは拡張可能Identifierを使う。

## 18. Runtime／Configuration Baseline

### 18.1 Config Resolution

```text
Built-in Default
  < Application Config
  < Deployment Profile
  < Environment
  < Explicit CLI／Request Override
```

Application共通値とPlatform固有値を分離する。Effective Configには適用Sourceを残し、UIがTOMLを無検証で直接変更する構造にしない。

### 18.2 Current Model

```text
Role            : Main
Repository      : Qwen/Qwen3-4B-GGUF
Upstream        : Qwen/Qwen3-4B
Artifact        : Qwen3-4B-Q4_K_M.gguf
Quantization    : Q4_K_M
Local Backend   : llama-cpp-python 0.3.34／Metal
External Backend: llama-cpp-python 0.3.34／Pure CPU
```

Current Modelは、M2 Pro／16GBで全Runtime骨格を検証する初期Modelであり、将来の固定Modelではない。Hardware、Home Server、CloudまたはRemote Inference導入後は、Model Port／Capability Contractを維持して高性能Modelへ交換・追加する。

### 18.3 Reserved Model Roles

```text
Guard:
  Qwen3Guard-Gen-0.6B
  GGUF Q8_0またはCanonical Weight

Judge:
  AtlaAI/Selene-1-Mini-Llama-3.1-8B
  GGUF Q5_K_MまたはCanonical Weight
```

Guard／JudgeをPhase 1で常駐させない。専用PhaseでResource、Backend、Model Format、Judge Biasおよび独立性を評価する。

### 18.4 Model Provenance

将来のAudit／Experimentでは次を識別する。

- Model ID／Upstream／Distribution Repository
- Revision
- Artifact File／Format／Quantization
- Size／SHA-512
- Definition File Digest
- Backend／Version／Build Variant
- Chat Template／Digest
- Loaded Context
- Device／Acceleration

## 19. Current Feature Baseline

Phase 1で成立したもの：

- Reproducible Python／uv／`.venv`
- GGUF Load／Unload／SHA-512検証
- Model Port／llama.cpp Adapter
- CLI `model-info`／`generate`
- Chat Template／Streaming／Non-streaming
- Cooperative Cancel／Shutdown Cancel
- Generation Config／Stop／Seed
- Deployment Profile／Platform Registry／Capability
- Application Config／Deployment Profile分離
- Response Language `ja／en／auto`
- Thinking Execution／Presentation分離
- Raw Thinking非保存
- FastAPI Minimal Web
- Browser Memory上の一時Conversation
- New Chat／Stop／Send／Copy
- UI LanguageとResponse Languageの独立
- Summary Mode
- Completion後のSanitize済みMarkdown
- Model Busy／複数Tab安全拒否
- Basic Preview Access Control
- macOS Metal Acceptance
- Lightning Linux x86_64 Pure CPU Acceptance
- Lightning Public URL／Basic認証Manual Acceptance

Phase 1で意図的に残したもの：

- Browser Reload後のConversation永続化
- Full Chat History
- Responsive／Mobile Acceptance
- 段階的Streaming Markdown
- Markdown Table整形
- Code Snippet別Block／個別Copy
- 本番Access Control
- Audit／Governance／Guard／Judge／Repair／RAG／Agent

## 20. Governance Definition Platform

### 20.1 Main Reference

```text
ARGD:
  Axiomatic Reasoning Governance Definition
  v0.3.1

DAGD:
  Declarative AI Governance Definition
  v0.4.4
  EXPERIMENTAL

Author:
  Nazuna Research

Definition License:
  CC-BY-SA-4.0
```

ARGDはInput Interpretation、Premise、Context Priority、矛盾、情報不足、Reasoning Quality、ExpressionおよびRepairを扱う。DAGDはPolicy Goal、Constraint、Capability、Evaluation、Severity、State、Audit-to-ActionおよびStatusを扱う。

69KB全体を毎Turn投入しない。必要RuleだけCompileし、決定論的処理はRuntime側、意味評価だけModel Callへ分離する。

### 20.2 Generic Definition Catalog Reservation

既知の候補：

| ID | Domain |
|---|---|
| CDOGD | Cross-Domain Orchestration |
| SPPGD | Strategic Planning／Prioritization |
| DAAGD | Decision Authority／Accountability |
| SDAGD | Strategic Decision Audit |
| SDMRGD | Strategic Decision Meta-Review |
| DSGD | Data Science |
| ACRGD | Artifact Composition／Review |
| AAGD | Agentic AI |
| AISGD | AI Security |
| MPGD | Model Policy |
| DCAGD | Development Consulting |
| PMOGD | Project Management／Orchestration |
| AIRGD | AI Research |
| AIAGD | AI Architecture |
| SEGD | Software Engineering |
| OMRGD | Operations／Maintenance／Reliability |

このCatalogはClosed Setではない。全部空、JSON 0件、全く異なる名称・分野・Schema、CDOGDなしを正式に想定する。

### 20.3 Shared Control Plane／Distributed Points

```text
Governance Control Plane
  ├─ Definition Provider／Registry
  ├─ Schema Adapter／Validator／Compiler
  ├─ Binding／Activation／Rule Selection
  ├─ Shared State／Point-local Namespace
  ├─ Evidence／Evaluator／Budget
  ├─ Conflict Resolution
  └─ Action Resolver／Status Event

Execution Pipeline
  ├─ Input Point
  ├─ RAG Point
  ├─ Guardrail Point
  ├─ Policy／Authority Point
  ├─ Agent／Tool Point
  ├─ Judge Point
  ├─ Main Model Point
  └─ Output／Repair Point
```

各Pointへ完全なGovernance一式を複製せず、その場所に必要なRuleだけを渡す。

## 21. Evidence／Audit／Evaluation Direction

Audit原本はAppend-only JSON／JSONL候補とする。Turn単位PayloadからIntegrity Fieldを除外してCanonicalizeし、SHA-512を適用する。SHA-512単体は同時改竄に耐えないため、後続PhaseでHash Chain、HMAC、Digital Signature、WORM、Merkle Structure、External Timestamp等を検討する。

記録候補：

- Session／Turn／Request／Message ID
- User Input／System Prompt／Modelへ渡したMessage
- Model／Artifact／Backend／Config
- Definition／Plan／Rule／Point／Mode
- Output／Stop Reason／Token／Latency
- State Before／After
- Deviation／Severity／Score
- Recommended／Executed Action
- Repair／Regenerate／Rebind
- RAG Source／Tool Call
- System Trace／High-level Explanation

Raw Chain of Thoughtを保存しない。説明可能性はBasis、Source、Applied Rule、Affected Claim、UncertaintyおよびHigh-level Process Summaryとして扱う。

LLM-as-a-Judgeは将来候補だが、唯一の正解生成器または最終Authorityにしない。Rule-based Check、Reference、Human Review、独立Judge、複数回評価をRiskに応じて組み合わせる。

## 22. RAG／Agent／ML Direction

### 22.1 Documentation RAG

Phase 1-exでMac限定簡易Documentation RAGを導入し、後続のLightning Public Corpus AdapterとともにCross-environment Acceptanceを完了した。

```text
DocumentSourcePort
ChunkerPort
EmbeddingPort
IndexStorePort
RetrieverPort
ContextAssemblerPort
CitationPort
```

Home Server、CloudへAdapter追加できるHookを持つ。`docs/`がない場合は推測せず、「docsが設置されていないため参照できません」と明示する。Lightning Basic／Publicでは、公開承認済み8文書のCorpusだけを参照可能とする。

### 22.2 Agent

将来のAgent RuntimeはPlanning、Tool Call、Observation、Replanning、State、Memory、Handoff、Completion CheckおよびHuman Approvalを扱う。

制御：

- Max Step／Time／Retry
- Tool Permission
- Side Effect確認
- Infinite Loop防止
- Input／Output Validation
- 全Tool Call Evidence

AAGDが実行過程を統治しても、新しい実行権限を生成しない。

### 22.3 Machine Learning

ML／Training／AdaptationはRuntime主要機能完成後のOptional Componentとする。

- Conversation RuntimeとTraining Runtimeを分離する。
- Current ModelとCandidate Modelを分離する。
- Dataset、Config、Run、Artifact、Evaluation、Approval、Promotion、Rollbackを追跡する。
- 通常Conversationから暗黙にWeightを更新するOnline LearningをDefaultにしない。
- 定量計算モードと定性計算モードを独立ON／OFFできるようにする。
- 両者を無条件に単一Scoreへ圧縮しない。

## 23. Deployment／External Environment State

### 23.1 Local Mac

日常開発、Model Smoke、Web Manual Testおよび将来のMac簡易RAGを担当する。

### 23.2 Lightning AI Studio

```text
OS              : Ubuntu 24.04.4 LTS
Architecture    : x86_64
Environment     : Container
Python          : 3.12.11
CPU             : 4 vCPU
Memory          : 約15GiB
GPU検証時候補   : Tesla T4 15GiB
Current Profile : Pure CPU
```

GPUはCredit消費を考慮し、Pure CPUを主な外部互換実証に使用する。Pure CPU生成が遅いことはKnown Limitationである。

Basic Preview Lifecycle Script、Managed Secrets、Start／Status／Restart／Stop、Health Check、Basic認証および外部Browser AccessはManual Acceptance済みである。

Traffic-aware Auto-startの本来の完了条件は、Studio Browser Tabを開かずStudioがSleepしている状態でも、第三者がPublic URLへAccessしたときPlatformが起動することである。Repository側PreparationだけでGO判定しない。

### 23.3 Future

- Home Server
- Linux CUDA／ROCm／Vulkan／CPU
- Windows
- MLX
- vLLM
- Remote Inference API
- AWS／Azure
- Hybrid Deployment

## 24. Documentation／Publication State

### 24.1 Current Structure

```text
docs/project/current/
  → 現在正本

docs/project/phases/
  → Phase Stable／Lossless Compilation／Raw History

docs/project/shared/
  → Phase横断Rule／Operations／Role／Handoff

docs/public/
  → 人が最初に読む公開文書
```

Current、Shared、Public、Phase Stable、Phase CompilationおよびLossless再整理後正本はTimestampなしFilenameを維持する。Timestampを付けるのはHistory SnapshotとEvent Artifactだけである。

### 24.2 Reconstruction Source Snapshot

```text
Snapshot Time     : 2026-07-27 09:37:27 JST
Source Files      : 499
Docs Files        : 493
Markdown          : 489
Demo Images       : 6
Entry Verification: PASS 499／499
```

Machine-readable Inventory：

`docs/project/phases/phase_1_ex/history/operations/documentation_reconstruction_source_inventory_20260727093727.json`

Project Continuity MasterとRoadmapは最初と最後の2周行う。Phase 1と進行中Phase 1-exの両方をLossless再整理する。

### 24.3 Public Documents

初版作成済み：

- `overview_ja.md`
- `concept_ja.md`
- `roadmap_ja.md`
- `README.md`
- `LICENSE`
- `TERMS_OF_USE.md`
- `NOTICE.md`
- `CITATION.cff`

READMEではDemo画像6枚を相対Pathで掲載し、現在の画面例であること、将来予定はRoadmapを読むこと、現在の環境制約により高性能Model等を使用できていないこと、および将来交換予定であることを明記する。

### 24.4 Current Permission／Warranty Direction

予定する公開条件：

- Repositoryの現状は閲覧・評価目的に限定する。
- 将来公開する公式Demo環境内の操作は許可する。
- 許可範囲外の利用、改変、再配布その他の行為は原則禁止する。
- Project、Model、Output、互換性、正確性、安全性および特定目的適合性を保証しない。
- 研究上、各機能をOFF／ON、`observe／enforce`等へ切替可能であること自体がRiskを伴うため、無保証を明確にする。

READMEの要約表現とLICENSE／TERMS／NOTICEを矛盾させない。Research Preview初版は作成済みだが、Initial Commit前に利用条件、第三者Attribution、Model Licenseおよび公開対象との最終整合を再確認する。

### 24.5 Identity

```text
Organization／Owner : margpa-labs
Repository          : margpa-labs/margpa-runtime-llm
Public Author       : Nazuna Research
```

本名、個人連絡先、LinkedIn、個人ProfileおよびLocal User名を公開Artifactへ含めない。

## 25. Phase Progression

```text
Phase 0:
  Requirements／Foundation Design

Phase 1:
  Portable Inference Runtime／Preview Surface
  COMPLETE／ACCEPTED

Phase 1-ex:
  Operations／Documentation／Public Transition
  IN PROGRESS

Phase 2:
  Conversation Continuity／Experimental Control Surface
  First Document-driven Codex Task Orchestration Pilot
  2-A Phase Contract／Conversation Domain Foundation
  2-B Conversation Persistence／Lifecycle Services
  2-C Conversation Application UX
  2-D Configuration Control Surface／Research Developer Mode
  2-E Runtime Composition Switchboard／Documentation RAG Follow-up
  2-F Cross-environment Acceptance／Phase Closure

Phase 3:
  Audit／Evidence／Generic Definition Infrastructure

Phase 4:
  MARGPA Main Runtime Governance

Phase 5:
  Guardrail／Security／Policy／Authority

Phase 6:
  Judge／Evaluation／Repair／Observability

Phase 7:
  RAG／Data Governance

Phase 8:
  Agent／Tool／Memory／Handoff Governance

Phase 9:
  Experiment／Multi-Governance Research Platform

Phase 10:
  Hardening／Cloud Scale／External Original R&D Integration
```

Phase順序と細分化は前Phase Evidence、Hardware、RiskおよびUser Requirementにより変更し得る。ただし最上位目的、疎結合、Definition 0件、Authority BoundaryおよびEvidence Boundaryを黙って変更しない。

## 26. External Original R&D Integration

### 26.1 EASA

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構
Research Area: AI Safety Governance
```

内部安全傾向、周辺安全制御、入力文脈および生成過程等の相互作用から生じるComposite Safety Behaviorを扱う。`Embedded Safety Layer`は作業概念であり、単一物理Layerの存在を断定しない。

### 26.2 DLAGSA

```text
DLAGSA
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構
Research Area:
  Multi-Agent Governance,
  Distributed Accountability,
  and Safety Assurance
```

複数の判断、実行、検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う。単純な複数AI並列化、単一Safety Filterまたは単一Logではない。主体間関係自体をRisk Sourceとして扱う。

### 26.3 OCILNS

```text
OCILNS
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
Research Area:
  Cognitive Interaction Provenance,
  Verifiable AI Systems,
  and Distributed Auditability
```

人、AI、Tool、外部Systemの認知的対話出来事を、検証、参照、継承、監査できる改竄耐性付き証跡単位として扱う。長期、分岐、多Model、多Thread環境でも入力、出力、順序、時刻、判断根拠、未解決事項、継承対象および改変検知情報の再接続可能性を維持する。

### 26.4 Integration Contract

```text
EASA／DLAGSA:
  Generic External Governance Provider Port

OCILNS:
  Generic Evidence Ledger Port

Default:
  All OFF
```

3 Systemは別Project／別Taskで独立開発し、MARGPA本体が一通り成立したPhase 10以降に疎結合統合する。存在しなくてもMARGPA Coreは完全動作し、OFF時はLoad、Call、WriteおよびSide Effectを行わない。

公開文書では名称、研究領域、概要および接続方向を示す。核心Algorithm、内部Protocol、具体的な改竄耐性方式および未公開実装情報は記載しない。

将来さらに多数の外部Systemを追加する可能性があるため、3名称だけに閉じないGeneric Hookを維持する。

## 27. Current Safe Continuation

完了済みDocumentation作業：

1. Frozen InventoryからProject Continuity／Roadmap第1周を作る。（完了）
2. Current CanonicalをLossless再構築する。（完了）
3. Phase 1 CompilationをRaw Source／Hashで再検証する。（完了）
4. Phase 1-ex Current-to-date Compilationを作る。（完了）
5. Shared一式を再整理する。（完了）
6. Overview／Concept／READMEを作る。（初版完了）
7. LICENSE／TERMS／NOTICE／CITATIONを作る。（Research Preview初版完了）
8. Project Continuity／Roadmap第2周を行う。（完了）
9. Link、Identity、Secret、Permission、Warrantyおよび情報欠落を検証する。（初回Corpus分完了）

次工程として記録済みだが、詳細指示待ち／未実施：

- Git初期化／Commit／Tag／Remote／Push
- Git未使用のGitHub掲載準備／一時掲載
- Anonymous Public Demo有効化
- Model Download／Dependency変更
- Lightning Platform UI操作
- Phase 1-ex完了宣言／Backup

本書第1周後に追加・変更されたCurrent、Phase Lossless、Shared、Public、READMEおよび利用条件Artifactは、本第2周で統合した。以後に追加されるPhase 1-ex Sourceは、Final Phase CompilationとInitial Commit前Refreshへ含める。

## 28. Documentation Reconstruction第2周結果

### 28.1 完了した再構築

```text
Source Inventory:
  Docs                     : 493
  Demo Images              : 6
  Total                    : 499
  Verification             : 499 / 499 pass

Current Canonical:
  Requirements             : rebuilt
  System Architecture      : rebuilt
  Technology Selection     : rebuilt
  Basic Design             : rebuilt
  Runtime Governance       : rebuilt
  Current Index            : rebuilt

Phase Lossless:
  Phase 1 Final            : 316 / 316 pass
  Phase 1-ex Interim       : 145 / 145 pass

Shared:
  Documentation Rules      : rebuilt
  Structure／Operations    : rebuilt
  Role Authority           : rebuilt
  Design Governance Handoff: rebuilt

Public／Root:
  overview_ja.md           : created
  concept_ja.md            : created
  roadmap_ja.md            : second pass
  README.md                : created
  LICENSE                  : created
  TERMS_OF_USE.md          : created
  NOTICE.md                : created
  CITATION.cff             : created
```

Phase 1-ex Losslessは再構築開始時点までのInterimであり、本作業で追加したShared、Public、Root Artifactおよび第2周Snapshotを含まない。これは欠落ではなくFreeze後Deltaである。Phase 1-ex完了時にFinal Source Freezeを行い、後続Sourceを含むFinal Compilationを作る。

### 28.2 Root／Public Artifact Digest

```text
README.md:
  0c1077021cd5930d9ba956da80c0060281ef1b0ce649e678b946643d0ee744fdb9ed324e6dca2e7c9f1b4b488717ceac01add37759b629d40d0dd698909b7c5f

LICENSE:
  8d378c4c2994c3e55bb2ccaae27367eb7e66c5da04d028a0d73d727a330ab1ebf0d71f98c9d4f667f2fe6c43881f50d2e5d1fab74b5fd908e357a3db6e867485

TERMS_OF_USE.md:
  83ee862ca210f03e50c32a289f4d45f36335678adb377a0bfaac25a0b108d7eb52f1ec5f028a8f8167239f440992fe4e3e9771b244cde492f0cd19d2a4f3c1da

NOTICE.md:
  8ae8440b7fea8c10663608deee3b352fc960a25fb8f4197518dd6ceb9c60179011b1bbaefc8756fe9add0714020d50fcdd929615c91eb7913882076e027af0c3

CITATION.cff:
  9260fd358f8821df72a28c022b30630f948c91ae7611d132f7a777d343a0aade8ce2b3714773122267f173521b6a5968c397fa5643a07676a80278be2a5f86d1

overview_ja.md:
  5866fceee5f43775d880b64fc6f0956c23efde8e81f6ba2f8b7774ba11d90a171e381d5706e01e29bc05dde932943c97c1563e34dc7964fbd81fa10e3957bf71

concept_ja.md:
  7ac64ccaa77c3dcce6bcda6b7c04f0af0b94759632051bf8cf0054e4e70ba38c1dfff602ddb1717187b8af32066448ccfa87e2027f3fd55d4f1b4948c5cb21d6
```

上記Digestは各Artifact作成直後の値であり、第2周後に内容を修正した場合はFinal Validation Recordの値を正とする。

## 29. Research Preview利用条件の現在状態

Rootの`LICENSE`は、現段階のRepositoryをOpen Sourceではなく、閲覧・非公開評価だけを許可するResearch Previewとして定義する。

Hosted Demoが別途公式公開された場合は、表示されたUIと制限の範囲内で操作できる。ただしHosted Demo操作許可は、Repository成果物の複製、改変、実行、Deployment、再配布または商用利用を許可しない。

README、LICENSE、TERMS_OF_USEおよびNOTICEは、次を共通して明示する。

- 一切の動作保証を行わない。
- Model Output、Governance、Guardrail、Judge、Repairおよび各設定組合せを保証しない。
- 高Risk用途へ依存させない。
- Model Weightと第三者Componentは別条件である。
- 将来OSS化を検討しても、現在の権利を自動的に拡張しない。

本条件はResearch Preview初版であり、Initial Commit前に最終公開対象、第三者Attribution、Model Licenseおよび適用範囲を再検証する。

## 30. 第2周後の残作業

```text
1. Git未使用のGitHub掲載準備／一時掲載
2. Public Demo基盤／最終確認／匿名公開有効化
3. Mac限定簡易Documentation RAG＋External Hook
4. Git運用設計
5. Git初期化／公開Sanitation／初回Commit直前準備
6. 必要Docs再整理／Phase 1-ex Final Lossless／Design Governance Recovery更新
7. 全体Review／Test／Privacy Scan
8. 初回Commit
9. Phase 1-ex Backup
10. Phase 2
```

現在のPublic文書が人に見せられる粒度であることと、GitHub掲載準備・掲載操作が許可・完了していることは別である。Stage 1の詳細はユーザーの後続指示を待つ。Git操作、外部公開、Lightning Platform操作およびPhase完了宣言は、ユーザーの明示許可と各Gate完了まで行わない。

## 31. 2026-08-04 Git公開統合／単一Root Recovery Point

本節は、第2節、第5節、第27節および第30節の時点依存Statusを現在値で上書きする。過去節は当時の計画／Baselineとして削除せず保持する。

### 31.1 Git／Repository

```text
Repository             : margpa-labs/margpa-runtime-llm
Existing History       : preserved
Canonical Working Root : margpa-runtime-llm
Former Staging Root    : retired／deleted by user after backup
Default Branch         : main
Current HEAD           : 844394106f0330b9b8bd3652813642f34132a647
origin/main            : 844394106f0330b9b8bd3652813642f34132a647
Remote main            : 844394106f0330b9b8bd3652813642f34132a647
PR #1 Merge Commit     : 9fff303175a3224963254eacddd66f9cf5112a5a
Merged Work Branch     : retired locally and remotely
Tag／Release           : none
```

Existing GitHub Historyを削除・再作成・書換えせず、開発内容正本をPublication Set 1,053件としてTargetへ統合した。Source-only、Target-onlyおよびContent Mismatchは0件である。

PR #1はMerge Commit方式で`main`へ統合した。その後、Git Workflow／運用記録の16文書をユーザーがDirect `main` Commit／Pushとして明示承認し、`9ac8a6b`でLocal／Origin／Remoteを同期した。単一Root Cutover後の正当な次回Docs更新では、Docs限定111件をCommit `8443941`としてDirect `main`へPushし、Local `HEAD`、`origin/main`、Remote `main`およびGitHub APIのSHA／Message一致を確認した。

### 31.2 Canonical Root Cutover

Source／Git Stagingの双方のBackup、HEAD一致、Clean Working Tree、`git fsck`、Publication Set一致、`.git`のNon-bare／Index Lock非存在／Config確認およびユーザー明示承認を経て、macOS `ditto`でGit Metadataを開発内容正本へ移行した。

```text
COPY_PREFLIGHT_EXIT : 0
DITTO_EXIT          : 0
GIT_CUTOVER_EXIT    : 0
Post-cutover Test   : 430 passed／3 deselected
```

Cutover後に単一化Backupを取得し、旧Git Staging Rootはユーザーが削除した。今後、Source→Stagingの二重同期を行わない。

### 31.3 Backup方式

Canonical Rootの`.venv/`を一時削除してArchiveを作らない。Canonical RootをBackup作業用Copyへ複製し、そのCopyから`.venv/`、Model、Cache、SecretおよびLocal Runtime Dataを除外してArchive化する。`.venv/`は必要な場合だけ別に保管し、原則はLock／Setupから再構築する。

### 31.4 Git運用

```text
小規模／決定論的Docs／Metadata:
  Direct main候補
  Exact Diff／Test／Sanitation／Rollback／User Approval必須

新機能／大規模／高Risk／Phase統合:
  Working Branch／Draft PR／Review／Merge Commitを原則
```

Commit、Push、Merge、Tag、Release、Branch削除、Remote変更およびVisibility変更は、それぞれユーザーの明示承認を必要とする。Git Working TreeがCanonical Rootに存在することは、Standing Authorizationを意味しない。

### 31.5 現在の実装状態

```text
macOS Metal Runtime                 : accepted
Lightning Pure CPU Runtime          : accepted
Lightning Basic Preview             : accepted
Traffic-aware Auto-start            : accepted／GO
Anonymous Public Demo               : accepted
Mac Documentation RAG               : accepted
Lightning Basic Public Corpus RAG   : accepted
Lightning Public Public Corpus RAG  : accepted
General Governance／Guard／Judge     : not implemented
Phase 1-ex                           : in progress
```

Documentation RAGは「参照機構が成立した」ことをAcceptanceとする。小型ModelのHallucination、Multi-target Query、Retrieval選定、Grounding、Token Budget、ARGD／DAGD、Guard／Judge／Repairを含む精度改善は後続Phaseで扱う。

### 31.6 Phase 1-ex残作業

1. Current／Shared／Phase Index／Recoveryの現状更新。
2. Phase 1-ex Final Source Freeze、Lossless CompilationおよびManifest。
3. Roadmapを含む必要Docsの最終Refresh。Optional English派生版は余力次第とし、非Historyだけを対象にする。
4. Full Test、Static Check、Shell／TOML、Link、Privacy、Publication Sanitation、Git状態のPhase Final Check。
5. Blocker解決。後送りは影響、Owner、対応Phase、再開条件、検証法およびユーザー承認を要する。
6. User Acceptance。
7. 設計統括者役がユーザーへ「Phase Backupを取得してください」と明示。
8. Phase 1-ex Final Backup／SHA-512／Restore Evidence。
9. Git通常運用の再確認はCommit `8443941`で完了済み。Phase Closure時に最終差分が存在する場合だけ、明示承認後に通常のCommit／Push Gateを適用する。Dummy Commitは作らない。
10. Phase完了Tag／Releaseの別判断とPhase 2開始Gate。

### 31.7 復旧時の必須参照

- [Current Documentation Index](../documentation_index_ja.md)
- [Git Workflow Policy](../../shared/operations/git_workflow_policy_ja.md)
- [GitHub Publication Sanitation Policy](../../shared/operations/git_publication_sanitation_policy_ja.md)
- [Task Role／Write Authority Policy](../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Phase 1-ex Index](../../phases/phase_1_ex/phase_index_ja.md)
- [Git Source→Target統合／公開反映／単一Git Root移行記録](../../phases/phase_1_ex/history/operations/git_source_target_integration_publication_and_single_root_cutover_20260804035722.md)
- Latest Design Governance Recovery Manifest

本節は`interim_current_state`であり、Phase 1-ex Final Recovery Manifestを置き換えない。

### 31.8 Git通常運用Acceptance

```text
Commit                    : 844394106f0330b9b8bd3652813642f34132a647
Message                   : docs(phase-1-ex): record git cutover and governance plans
Changed Scope             : docs only
Modified／Added／Deleted  : 16／95／0
Local／origin／remote／API: identical
Working Tree Postflight   : clean
Normal Git Operation      : accepted／operational
```

本Acceptanceにより、`margpa-runtime-llm/.git`を使用した単一RootのCommit／Push経路は成立した。今後は好きな時点でGit操作を検討できるが、各Commit、Push、Merge、Tag、Release、Branch削除、Remote変更およびVisibility変更には、その都度ユーザーの明示承認が必要である。

Git関連の初期構築、History継承、公開統合、Root Cutoverおよび通常運用確認は完了とする。Branch Protection、Phase完了TagおよびReleaseはGit基盤の未完了事項ではなく、必要性とPhase Closureに応じて判断する独立Gateである。

## 32. Phase 2 Pilot／Governance Constitution／Desktop予約

### 32.1 Phase 2開始順

Phase 2では、元来のConversation Continuity／Experimental Control Surfaceへ着手する前に、Document-driven Task Orchestration Pilotの設計を完了し、Accepted Authorization Envelopeの範囲内でPilotを始動する。

```text
Phase 1-ex Completion／User Acceptance／Backup
  → Phase 2 Orchestration Pilot Design
  → User-approved Authorization Envelope
  → Pilot Bootstrap／Bounded Work Unit
  → GO／ADJUST／STOP Review
  → 元来のPhase 2-A～2-F
```

現設計統括者役はProject責任者として、Project全体、Cross-Phase不変条件、Task編成、最終ReviewおよびRecoveryを統括する。ただしユーザーの最終Decision Authority、Backup、External Mutation、Git／公開、Secret、課金およびPhase移行Gateを代行しない。Project責任者も絶対禁止事項、Docs規則、Authority規則その他の運用ルールへ完全に従属し、Role名や責任から自己免除を生成しない。承認・確認待ちの安全な停止は別の正常運用である。

Pilotでは、必要に応じた独立Taskの作成、Task名設定、Authority設定、初回Handoff、Task間Follow-up、Status取得、Reviewおよび次TaskへのHandoffをDocument-drivenで連結する。当面は一つのSubphaseまたは有界なWork Unitごとに回し、Evidenceが安定した場合だけ複数Unit、Phase完了単位、最終的にはProject完了単位へ粒度を拡大する。

Phase 2を成立性検証とする。Phase 2の結果が`GO`または条件付き`ADJUST`としてAcceptedされた場合、Phase 3でもPilotを継続し、異なるRequirements、担当Task、ContextおよびEvidence Domainで同じ骨格の再現性・移植性を検証する。Phase 3以降の粒度拡大は自動ではなく、各PhaseのEvidenceとUser Gateで再決定する。

### 32.2 Phase 2 Index Path

Phase 2以降のAppend-only Documentation Index Snapshotは、各Phaseの`history/index/`へ保存する。

```text
docs/project/phases/phase_2/history/index/
documentation_index_YYYYMMDDHHMMSS.md
```

Stable `phase_index_ja.md`とHistory Snapshotを分離する。Phase 1／Phase 1-exの既存Raw Indexは、相対Linkと原文を守るため遡及移動しない。

### 32.3 Development Governance Constitution

Agent／Tool本格実装前に、Projectで蓄積した絶対禁止、Docs、Authority、Mutation、Handoff、Review、Recovery、Backup、Git、Costおよび停止規則をLosslessに統合した、章立て済みの完全な開発統治憲法体系を作成する。

Canonical予定Rootは`docs/project/shared/constitution/`である。Folder単位で新規／他Projectへ配置し、Project固有Manifestを設定すれば、同等の開発体制を再構築できるPortable Packageを目標とする。

Normative CoreはProvider-neutralとし、Codex DesktopとClaude CodeのCapability差はAdapterへ分離する。Providerが異なっても、Authority、禁止事項、Evidence、Human Gate、StopおよびRecoveryの意味を変えない。

憲法体系は単一巨大Markdownではなく、正本Index、章別Rule、Rule ID、Manifest、Capability Contract、Role別Constitution View、Schema、AdapterおよびTemplateで構成する。Role ViewはCanonical RevisionとDigestから生成し、Authorityを独自追加しない。絶対禁止から推測までの優先順位、正式Exception、改憲、Version、Migration、RollbackおよびStale View検知を憲法自身へ含める。

憲法書完成までは、Phase 2 Pilotを含む運用データを収集し続ける。詳細は[Cross-project Development Governance Constitution Plan](../../shared/operations/cross_project_development_governance_constitution_plan_ja.md)を正本予約とする。

Phase 2・3では、`RULE_EFFECTIVE`、`RULE_AMBIGUOUS`、`RULE_MISSING`、`RULE_OVERRESTRICTIVE`、`RULE_UNENFORCEABLE`、`HUMAN_GATE_REQUIRED`および`AUTOMATION_CANDIDATE`を観測分類に使用する。成功ログだけでなくNear Miss、人間介入地点、偶然成功および停止遅延をEvidenceとして残す。

重大Conflict、Authority、Absolute Rule違反時動作、Stop／Recovery／Backup、Evidence、Resource Limit、生成Authorityおよび改憲手続きが揃った時点を`Constitution Research Preview v0.x`開始候補とし、完成待ちで永久停止しない。ただし開始はUser Acceptanceを必要とする。

### 32.4 Desktop Application

Desktop Application化を後続PhaseのCross-phase予約とする。実装Phaseと技術は未決定であり、Web／CLI／Runtime Coreの境界、Local Model、File Access、Sandbox、Update、Code SigningおよびCross-platform要件を先に評価する。

Desktop化予約を、現行Web版の廃止、Phase 4への自動割当て、特定Framework採用または配布開始の承認と解釈しない。

### 32.5 Agent／Tool Constitution Mode

将来のAgentおよび各Toolには、Component本体のON／OFFとは別に`constitution.enabled = ON／OFF`を持たせる。ONではAccepted Constitution RevisionとRole／Phase／Task／Component別Viewを検証して適用し、OFFでは憲法固有処理を実行しない比較Baselineとする。

OFFを`allow all`と解釈しない。Platform Security、Sandbox、File／Tool Permission、Access Control、Human Approval、既存Authority、法令およびProject開発中の絶対禁止／Docs／Authority規則は維持する。Agent側ONはTool側ONまたはTool実行許可を生成しない。

Constitution ONでRevision、View、DigestまたはEnforcement Capabilityを解決できない場合はFail-closedとし、黙ってOFFへFallbackしない。Default値、UI露出および一般公開ProfileでのON固定は後続設計事項であり、本予約だけで実装済みとしない。

## 33. Phase 1-ex Final Closure Source State

2026-08-04、ユーザーはPhase 1-exのFinal Docs、Final Lossless、最終検査、Backup、Commit／Push、完了判定およびPhase 2開始可能Gateまでを、今回限定のScoped Authorizationとして事前に明示承認した。これは今後のStanding Authorizationではない。

### 33.1 Final Documentation State

- Current／Shared／Public／Phase Indexの完了状態を累積更新した。
- 設計統括者役のRecoveryを保持したまま、プロジェクト責任者役専用Stable／Historyを新設した。
- 日本語正本をPhase 1-ex完了Gateとし、Current／Shared／PublicのOptional English Derivativeは同粒度作成を条件に後続へFormal Deferralした。
- `history/**`は英語派生対象外のままとする。

### 33.2 Pre-final Test Evidence

```text
pytest                         : 430 passed, 3 deselected
ruff check                     : pass
ruff format --check            : 122 files already formatted
mypy                           : success, 122 source files
shell syntax                   : pass
TOML／JSON parse                : pass
```

### 33.3 Backup Evidence Before Closure

ユーザーは完了作業開始前に次のCheckpoint Backupを取得し、別位置へ移動済みと報告した。

```text
Archive   : margpa-runtime-llm_phase1-ex_完了間近_20260804.zip
Size      : 25,420,406 bytes
SHA-512   : ea0dc3f6af88beb54777f9824a0e632ab0e76285d0a8aecc36f4387c58a1e93a7c3da1ec1ecd12497450df331f316c14a4f385b122fe5b9c0066e16c3bcc3265
Authority : user-created checkpoint; read-only evidence
```

Phase Final Backupは本Checkpointと分離し、Final Source、Manifest、SHA-512およびRestore Verificationを持つ別Artifactとして作成する。

### 33.4 Final Source Freeze Boundary

Phase 1-ex Final Losslessは、Final Source Freeze時点の`docs/project/phases/phase_1_ex/`配下のMarkdown／JSONを、`lossless/**`およびOS Metadataを除いて収録する。Final Lossless自身、Backup Receipt、Commit SHAを記録するPost-freeze Completion Record、最終Index SnapshotおよびRecovery Manifestは自己参照を避けるためPost-freeze Artifactとし、個別Path／Hash／Link検証対象とする。

### 33.5 Transactional Closure Rule

本Stable状態は、Final Lossless、両Recovery Manifest、Phase Final Backup／Restore、Publication Sanitation、Final Commit／PushおよびLocal／Origin／GitHub一致がすべて合格した場合だけCommitするTransactional Completion Candidateとして作成した。いずれかがFailした場合はCommit／Pushせず停止する。合格しCommitされた本書は、Phase 1-ex `complete_accepted`およびPhase 2 `ready_to_start`を表す。

## 34. Phase 2 Start／Automation Pilot Design Recovery Point

### 34.1 Accepted Transition

2026-08-04、ユーザーはGitHub、最新DocsおよびBackupを確認し、Phase 1-ex完了を改めてAcceptedし、Phase 2開始とAutomation Pilot設計の継続を明示した。

```text
Phase 1-ex                    : COMPLETE／ACCEPTED
Phase 2                       : STARTED
Active Subphase               : Phase 2-0 Automation Pilot Design
Phase 2 Functional Work       : NOT STARTED
Independent Phase Task        : NOT CREATED
Authorization Envelope        : DRAFT／NOT ACCEPTED
Current Stop                  : DESIGN REVIEW PENDING
```

Phase開始とTask作成を分離する。Phase 2がStartedであっても、ユーザーがAuthorization Envelopeを明示承認し、独立Task作成を別途明示依頼するまで、Task生成、Task間指示、Pilot実行またはPhase 2-A機能作業へ進まない。

### 34.2 Project Responsibility Recovery

プロジェクト責任者役のStable入口は[Project Responsibility Handoff](../../shared/project_responsibility_handoff/project_responsibility_handoff_ja.md)、Phase 1-ex完了時点のRecoveryは[Project Responsibility Recovery Manifest](../../shared/history/project_responsibility_handoff/project_responsibility_recovery_manifest_20260804061104.md)である。

このRecoveryは、設計統括者役用Recoveryを削除または改称したものではない。Project全体、Cross-Phase Gate、Role編成および複数Role Recoveryを扱うプロジェクト責任者役が、技術設計とCanonical Meaningを扱う設計統括者役のStable／RecoveryをLosslessに参照し、両Roleを分離したまま再構築するための専用Manifestである。

### 34.3 Phase 1-ex Closure Evidence

[Automation／Governance Evidence Log](../../shared/automation/automation_governance_evidence_log_ja.md)へ、Phase 1-ex Closureから得た次の知見を記録した。

- Exact staged scopeとUnexpected Path Gateの有効性
- 構造検査とCurrent Stateの意味的鮮度を分ける必要性
- Test後のCache再生成とSanitation順序
- Transactional Phase Closure State Machine
- Post-freeze Evidenceと自己参照回避
- Stable／History Byte一致
- Project Responsibility／Design Governance Recovery分離
- Scoped AuthorizationをStanding Authorityへ昇格させないこと

本EvidenceはPhase 2・3 Pilotと将来のProvider-neutral統合憲法の初期Empirical Inputである。

### 34.4 Phase 2-0 Design Package

- [Phase 2 Index](../../phases/phase_2/phase_index_ja.md)
- [Pilot Requirements](../../phases/phase_2/requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Pilot Architecture](../../phases/phase_2/architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Authorization Envelope Draft](../../phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Execution Plan](../../phases/phase_2/operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Phase Designer Bootstrap Handoff Draft](../../phases/phase_2/handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)

初回候補Work Unitは`P2-0-WU-001 Docs-only Recovery and Authority Acknowledgement`である。最大1件の独立Phase 2設計担当者役TaskへRead-only Authorityだけを与え、旧会話なしでCurrent StateとAuthorityを復元できるか評価する。File／Git／External／Secret／Destructive／Sub-agent Authorityは与えない。

### 34.5 Privacy／Secret／不要物Scan Timing

Repository全体を対象とするPrivacy、Secret、識別情報、不要物および公開Sanitation Scanは、今後CommitまたはPushを行う作業単位のPreflight／Postflightに限定する。通常のDocs編集、Read-only Review、設計、Test、HandoffまたはPhase途中Backupごとに広域Scanを反復しない。

具体的Incident、疑わしいPath、ユーザーの明示依頼または外部送信を伴わない限定確認が必要な場合は、対象を明示したRead-only Checkだけを例外実施できる。Commit／Pushのない本Phase 2-0設計単位では広域Sanitation Scanを実施しない。

### 34.6 Combined Control Role／Automation Start Boundary

当面、現在Taskは`プロジェクト責任者兼設計統括者役`として両責務を兼務する。独立した設計統括者Taskは新設しないが、Project ResponsibilityとDesign GovernanceのFolder、Stable、HistoryおよびRecoveryは分離して相互参照する。兼務はAuthority合算、User Gate代替または運用ルール免除を意味しない。

AutomationはBinary ON／OFFではなく、`manual／advisory／bounded_unit／workflow／phase／project`の段階と独立Capability Dimensionで制御する。初回Pilotは`bounded_unit` Draftであり、まだActiveではない。

Pilot開始には次を全て必要とする。

1. Design Package Review合格。
2. 対象差分Reviewと、ユーザーが当該Commit／Pushを明示承認した場合のGit Checkpoint／Remote一致確認。
3. ユーザーによる大規模Backup取得完了の明示報告。
4. Accepted Automation Profile／Authorization Envelope。
5. Control Taskによる「準備OK。いつでも開始出来ます。」の明示。
6. 後続ユーザーによる「ok。では開始する。」の明示。

Start Event成立直後にだけ、Provider Capabilityが許す場合は現在Task名を`プロジェクト責任者兼設計統括者役`へ変更する。変更不能、Profile不一致またはState変化時は停止する。

Authorized Root／Allowed Path外へ無許可で触れない規則は、Role、Automation Level、Phase／Project ScopeおよびProviderを超えて適用する最上位規則群の一つである。Automation／Constitution Coreは特定Project、Provider、Absolute Path、Phase、Task、CommandまたはUIをHard-codeせず、Project ManifestとProvider Adapterへ分離する。

CodexとClaude Code等を併用し、Control Taskから別ProviderへHandoffする構成は未決定の将来候補である。開発速度の可能性と、Authority、Single Writer、Evidence、Context、CostおよびRecoveryのRiskを別Pilotで比較し、現Phase 2-0初回Work Unitへは含めない。

### 34.7 Dedicated Constitution Research／Future Context Research

憲法関連の専用入口として[Constitution Research Index](../../shared/constitution/constitution_research_index_ja.md)と[Constitution Source Evidence Register](../../shared/constitution/constitution_source_evidence_register_ja.md)を作成し、Historyを`docs/project/shared/history/constitution/`へ分離した。Automation Evidenceを事実Source、Constitution RegisterをSource Trace付き制度候補として分け、後のLossless Source CompilationとNormative Constitution作成へ接続する。

最上位規則群は、人間が将来追加を明示指示できる意味で現時点の列挙に固定しない。追加、変更、削除、並替え、例外化、候補登録およびそれらの指示Authorityは、ユーザーまたはユーザーが明示指定した人間に専有する。AI／Role／Task／Agent／Tool／Automation／Providerは、EvidenceやConflictから最上位規則候補を自発登録せず、事実を報告して停止する。Agent／Tool本格実装前を原則編纂Gateとするが、Rule Conflict、Provider差またはSource肥大化Riskに応じた前倒しも人間が決定する。

Phase 10以降には、Thread内のToken／Context／Turn／Decision／Evidence／未解決事項を、単純な要約圧縮／復号だけに依存せずLosslessに保持・参照・再接続するR&Dを予約する。Algorithm、Index、Ledger、Graphその他の方式とOCILNS等との関係は将来決定する。

Phase 10へ集約済みの後半R&D群は、依存関係と規模が明確になった時点でPhase 11以降へ再分割する。現時点では番号と境界を固定しない。

### 34.8 Pre-pilot Governance Consolidation／Current Recovery State

Phase 2-0 Pilot Review前の統合入口は[Pre-pilot Automation Governance Baseline](../../shared/automation/pre_pilot_governance_baseline_ja.md)とする。同書は、兼務Role、Human-only最上位規則Authority、Authorized Root最上位境界、Automation Level／Control State分離、READY Evidence、Two-key Activation、Backup／Restore Evidence、Git Cadence、軽量Checkpoint、機械的強制研究、Permission Hardening研究、Multi-provider予約および将来研究を再整理する。新しいAuthorityを生成するNormative Constitutionではない。

現在State：

```text
Control State           : OFF
Automation Level Draft  : bounded_unit
Design Review           : gate reconciled／final validation pending
Envelope                : draft_not_authorized
Independent Task        : not created
Pilot                    : not started
Task Rename              : not executed
Capability Preflight     : passed／recheck before task creation
Pre-pilot Git Checkpoint : containing commit／remote alignment required for effective
Large Backup             : not confirmed
Permission Hardening     : undecided／not authorized
Mechanical Enforcement  : unimplemented／unapproved research candidates
Multi-provider           : undecided future candidate
```

Pilot開始前に発生した`/tmp/margpa_phase2_docs_20260809184134.list` Incidentは、Authorized Root外へのFile作成と、その後の無許可削除という二つの独立違反としてAutomation Evidenceへ保存した。削除済みFile自体は復元していないが、当時含まれていた24 PathはEvidence Logへ完全列挙し、各Pathの存在をProject内で確認した。この復元は違反を解消済み扱いにせず、以後のIncidentでは自己生成ArtifactもCleanup／Rollbackせず、人間へExact Stateを報告して待つ。

Permission／ACL Hardeningは、AI側作成物であっても作成者Authorityから自動許可しない。採用する場合は正確なTarget、Before／After、Platform継承、Lockout、Rollbackおよびユーザー明示承認を必要とする。

Pilot前の大規模Backupはユーザー担当であり、AIはAuthorized Root外を検査しない。Backupの存在、対象包含、復元手順およびSample Restoreを区別し、確認粒度は人間が決定する。

### 34.9 Pre-activation Gate Reconciliation

2026-08-09、Phase 2-0 Design Package内で、Capability PreflightがREADY／User Startより後に置かれていた順序矛盾と、Bootstrap HandoffのRevision／Reading Order不足を検出し、全面再設計ではなく限定Gate Reconciliationで修正した。

Canonical順序は、Design Review、Read-only Capability Preflight、Exact Design Freeze、ユーザー承認済みGit Checkpoint／Remote一致、ユーザー大規模Backup、Exact Envelope／Child Task範囲Acceptance、Controller READY／`ARMED`、後続ユーザーStart／`ON`、Child Task作成、Acknowledgement／Reviewである。

Read-only Capability Preflightでは、Task作成、Task名設定、初回Handoff、Follow-up、Status取得およびWaitを`available`、Interruptを`manual_required`、Pin／Archiveを`available but optional`として確認した。Taskは作成していない。Provider契約、対象Project、Envelope RevisionまたはHandoff Revisionが変化した場合は結果を失効させ、Task作成直前に再確認する。

本更新を含むCommit／PushがLocal／Remote一致まで合格した場合、技術的な開始準備として残るのはユーザーによる大規模Backup完了報告である。正式なActivation Gateとして、Exact Envelope／Task範囲AcceptanceとTwo-key Activationは引き続き独立して必要であり、Backup完了だけからTask作成またはPilot開始を推測しない。

## 35. Phase 2-E Technical Completion Candidate／Cross-provider Recovery Point

2026-08-15、Phase 2-EはRuntime Composition Switchboard Foundation、Documentation RAG Multi-turn Follow-upおよびPersistent Citation Evidenceの設計・実装・自動検証を完了し、Technical `COMPLETE_CANDIDATE`へ到達した。

```text
Phase 2-A～2-D            : COMPLETE／USER ACCEPTED
Phase 2-E Functional Work: TECHNICAL COMPLETE_CANDIDATE
Latest Full Suite        : 674 PASSED／3 DESELECTED
Static Validation        : RUFF／MYPY／NODE PASS
Mac Manual Acceptance   : PENDING／CLAUDE HANDOFF READY
Codex Final Closure     : PENDING AFTER MANUAL RESULT
Phase 2-F               : NOT STARTED
Lightning Phase 2       : DEFERRED UNTIL AFTER PHASE 3 OR 4
```

Phase 2-E実装は、Reload、Server Restart、Chat再Open、Resume、Retry／RegenerateおよびBranch Selectを越えるCitation復元、明示Opt-inのSQLite Migration、Checkpoint／Digest／Rollback、Embedded Citation Schema Versionの一致、Safe DecodeおよびRead-only Runtime Composition Inspectionを含む。Public／Basic／v1既存境界は変更せず、Phase 2-Eの実Mac Manual Acceptanceは別Gateとして残す。

Phase 2-EはAgent自動化／Cross-provider実験も含む。Codexプロジェクト責任者兼設計統括者役を最高責任者とし、Claude設計統括者役、Claude Phase 2-E設計担当者役およびClaude Phase 2-E実装者役が、Repository内Recovery Index／Handoffから設計、実装、Review、CorrectionおよびCompletion Handoffまでを連結した。Codex独立ReviewはClaude側Reviewを通過していた実装・Migration境界の欠陥を検出し、Exact Rework Handoffを介したClaude側修正でCloseした。したがって、Technical Outcome、Automation ChainおよびCross-provider Reviewは成功である。

一方、Claude Provider MemoryへのAuthorized Root外書込みが発生し、最上位規則適合は失敗した。この違反を実装成功で相殺しない。既存Codex／Claude Provider Memoryは非正本として無視し、将来の作成、更新または依存を禁止する。`.claude/settings.local.json`はユーザーが権限操作を認識したうえで維持するが、Authority、RecoveryまたはEvidence正本には使用しない。Cross-providerの正本はRepository内Index／Handoff／Evidenceだけへ限定する。

Recovery入口：

- [Phase 2 Index](../../phases/phase_2/phase_index_ja.md)
- [Claude Final Rework Completion Handoff](../../phases/phase_2/history/handoffs/claude_phase_2_e_final_rework_completion_handoff_20260815092725.md)
- [Codex to Claude Mac Manual Acceptance Handoff](../../phases/phase_2/history/handoffs/codex_to_claude_phase_2_e_mac_manual_acceptance_handoff_20260815095155.md)
- [Cross-provider Final Assessment](../../shared/history/automation/automation_governance_evidence_phase_2_e_cross_provider_final_assessment_ja_20260815095155.md)
- [Provider Memory／Repository Canonical Authority](../../shared/automation/provider_memory_and_repository_canonical_authority_ja.md)

Phase 2-Eを`COMPLETE／ACCEPTED／CLOSED`へ変更できるのは、Mac Manual Acceptance ResultがRepository内Handoffとして返却され、CodexがDiff、Runtime Data、Boundaryおよび結果をFinal Reviewした後だけである。本CheckpointのCommit／PushはTechnical CandidateとCross-provider Evidenceを固定するものであり、Final Acceptanceを代替しない。
