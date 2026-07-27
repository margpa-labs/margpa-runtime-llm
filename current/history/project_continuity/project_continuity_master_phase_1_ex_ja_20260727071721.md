# MARGPA Runtime LLM Project Continuity Master

```yaml
document_id: project_continuity_master
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-27 07:12:34 JST
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
Documentation Migration      : COPY-FIRST CUTOVER
Git／GitHub                   : NOT STARTED
Simple Documentation RAG     : RESERVED
Lightning Auto-start         : PREFLIGHT RESERVED
Public Demo                  : DESIGN ACCEPTED／NOT IMPLEMENTED
Phase 2以降                   : NOT STARTED
```

Phase 1でmacOS MetalとLightning Linux x86_64 Pure CPUのCLI／Web Runtimeを成立させた。現在はGit開始前のDocumentation再編、公開準備、Identity／License／Termsおよび継続性の整備を行う。

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

1. Lightning Auto-start Read-only Preflight
2. Auto-start Go／No-Go
3. Basic Previewと分離したPublic Demo基盤
4. 既存DocsのLossless再整理
5. Current／PublicのJA／EN作成
6. Local Mac用簡易Documentation RAG＋External Hook
7. Git運用設計
8. Initial Commit前Documentation Refresh
9. Sanitation／Allowlist／Git初期化
10. Public Demo最終確認
11. Phase 1-ex Review／Backup／GitHub公開

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
- Current／Publicは日本語正本＋英語派生版、Phase／Sharedは日本語のみとする。

## 8. Known Limitations

- Main Modelは小型であり、回答品質や事実性を保証しない。
- Lightning Pure CPUは生成が遅い。
- ConversationはBrowser Reloadで消える。
- Guardrail、Judge、Governance、Audit、RAG、Agentは未実装。
- Lightning Auto-startは未検証である。
- Public Demoは設計済みだが未実装・未公開である。
- Linux／Windowsの全Platform自動Routingは後続検証が必要。
- Mobile Responsive Acceptanceは未実施。
- Summaryは情報を省略・変形する可能性がある。
- Thinking内容は正確な内部状態を保証しない。

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

GitはPhase 1-ex後半で開始する。Initial Commit前にCurrent／Public JA／EN、README、License／Terms、Setup、Public Demo、RAG、Identity、Sanitation、Allowlist、Hash、LinkおよびManifestを再確認する。最初のGitHub公開はPhase 1-ex完了後とする。

各Phaseでは、設計統括者役のPhase完了・次Phase移行可能宣言後、Phase Backupの直前にDesign Governance Continuity RefreshとReconstruction Validationを行う。これが未完了の場合、Phase Backupおよび後続公開工程へ進まない。

## 11. New Task Reading Order

1. [Current Documentation Index](../documentation_index_ja.md)
2. [Requirements](../requirements/requirements_specification_ja.md)
3. [System Architecture](../architecture/system_architecture_ja.md)
4. [Runtime Governance](../governance/runtime_governance_specification_ja.md)
5. [本書](project_continuity_master_ja.md)
6. [Active Phase Index](../../phases/phase_1_ex/phase_index_ja.md)
7. [Documentation Structure／Task Operations](../../shared/operations/documentation_structure_and_task_operations_ja.md)
8. 必要なCompleted Phase Compilation
9. 必要時のみRaw History

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

各PhaseのActive Historyへ次を追加する。

```text
docs/project/phases/<phase>/history/operations/
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
