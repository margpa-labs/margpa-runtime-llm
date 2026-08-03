# MARGPA Runtime LLM Project Continuity Master

```yaml
document_id: project_continuity_master
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-08-02 22:06:59 JST
owner: Nazuna Research
active_phase: phase_1_ex
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
Phase 1-ex                    : IN PROGRESS
Documentation Migration      : COMPLETE／LEGACY ROOT RETIRED
Documentation Reconstruction : SECOND PASS COMPLETE／CORPUS VALIDATION PENDING
Git／GitHub                   : LOCAL GIT NOT STARTED／PRE-GIT PUBLICATION PREPARATION NEXT
Simple Documentation RAG     : RESERVED
Optional English Docs        : RESERVED／CURRENT＋SHARED＋PUBLIC／HISTORY EXCLUDED
Lightning Basic Preview      : MANUAL LIFECYCLE ACCEPTED
Lightning Auto-start         : ACCEPTED／GO
Traffic-aware Wake-up        : REPEATED WAKE／SLEEP PASS
Public Demo                  : DESIGN ACCEPTED／NOT IMPLEMENTED／NOT PUBLIC
Phase 2以降                   : NOT STARTED
```

Phase 1でmacOS MetalとLightning Linux x86_64 Pure CPUのCLI／Web Runtimeを成立させ、ユーザーによるMac／Lightning Web Acceptance、Basic認証、停止、再送信、New Chat、Language、Summary、Thinking、Copy、BusyおよびPublic URL確認を完了した。

現在はPhase 1-exの実行順を変更し、Gitを使用しないGitHub掲載準備を次工程とする。詳細指示はユーザーから後続提示される。Local Gitは未開始であり、本順序変更だけを根拠にGit操作、GitHub掲載または匿名Public Demo公開を行わない。Phase 1-exは進行中であり、現時点の再整理版を完了済みFrozen版と誤認させない。

## 3. Current Runtime

```text
Main Model       : Qwen3-4B-GGUF Q4_K_M
Local Backend    : llama-cpp-python 0.3.34／Metal
External Backend : llama-cpp-python 0.3.34／Pure CPU
Local Python     : 3.13.14
Lightning Python : 3.12.11
UI               : FastAPI Minimal Web
Storage          : Browser Memory／No persistent conversation
Governance       : Design only／Not implemented
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
- Phase 1 Backup
- Phase 1 Lossless Documentation Compilation

## 5. Active Phase 1-ex Work

完了済み基盤：

- Documentation Migration／Source Inventory／Current Canonical／Shared／Public初版
- Phase 1 Final Lossless／Phase 1-ex Interim Lossless
- Project Continuity Master／Roadmap第1周・第2周
- Lightning Traffic-aware Auto-start Acceptance

変更後の残工程：

1. Gitを使用しないGitHub掲載準備と一時掲載。詳細はユーザー指示待ち。
2. Basic認証Previewと分離したPublic Demo基盤、最終確認、合格後の匿名公開有効化。
3. Local Mac用簡易Documentation RAG＋External Hook。
4. Git運用設計。Branch／Tag／Commit、Author／Email、Remote／公開Repository、Backup対応を確定する。
5. Git初期化／公開Sanitation。`.gitignore`、`.gitattributes`、Model／Secret／Cache除外、Privacy Scan、LICENSE方針、初回Commit直前準備およびユーザー原文上のGitHub公開を含む。初回Commitはまだ作らない。
6. 必要Docsの再整理・新規作成、Phase 1-ex Final Lossless、Design Governance Recovery情報の更新。
7. 全体Review／Test／Privacy Scan。
8. ユーザーの明示許可後の初回Commit。
9. Phase 1-ex完了条件・User Acceptance後のPhase 1-ex Backup。
10. Phase 1-ex完了・Phase 2着手可能宣言後のPhase 2。

ユーザー原文では番号`4`が二度使われていたため、内容と前後関係を変えず10段階へ正規化した。Stage 1のGit未使用掲載、Stage 5のGitHub公開との対応およびStage 8の初回Commitの履歴関係は、Stage 4で明示的に確定する。設計統括者役が推測で統合、削除または前後入替しない。

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

Phase 2は、Document-driven Codex Task Orchestrationの最初の正式Pilotとする。Phase 1-ex完了後、設計統括者役がPhase 2 Index、開始用Handoff、Reading OrderおよびWrite Authorityを用意し、ユーザーの明示指示後に独立した`Phase 2 設計担当者役`Taskを作成する。設計統括者役はその成果をReviewし、Accepted後にだけ実装者役へHandoffする。これは完全自律化またはUser Authorityの代替を許可しない。

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
- Guardrail、Judge、Governance、Audit、RAG、Agentは未実装。
- Lightning Traffic-aware Auto-startは現在のBasic Preview用途でAccepted／GOであり、複数回のWake／Sleepを確認した。ただし観測Cold Startは約3～10分で、Production SLAまたは将来環境の性能保証ではない。
- Public Demoは設計済みだが未実装・未公開である。
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

各Phaseでは、設計統括者役のPhase完了・次Phase移行可能宣言後、Phase Backupの直前にDesign Governance Continuity RefreshとReconstruction Validationを行う。これが未完了の場合、Phase Backupおよび後続公開工程へ進まない。

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

Phase 1-exではMac限定簡易Documentation RAGを候補とする。

```text
DocumentSourcePort
ChunkerPort
EmbeddingPort
IndexStorePort
RetrieverPort
ContextAssemblerPort
CitationPort
```

将来Lightning、Home Server、CloudへAdapter追加できるHookを持つ。`docs/`がない場合は推測せず、「docsが設置されていないため参照できません」と明示する。Public DemoではRAGをLoad／Callしない。

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
