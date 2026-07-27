# MARGPA Runtime LLM Roadmap

```yaml
document_type: public_roadmap
document_state: current
language: ja
created_at: 2026-07-22
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
| External R&D Integration | 例外、安全、責任、認知対話証跡を外部研究機構と接続できる |

---

## 3. Status Legend

| State | 意味 |
|---|---|
| `Complete／Accepted` | 実装と独立Reviewが完了している |
| `Repository Accepted` | Repository実装は受入済みだが、対象外部環境での実測が残る |
| `Validation Waiting` | 実装済みだがUserまたは外部環境の受入が残る |
| `Accepted Reservation` | 要件・方向性は決定済みだが、実行を開始していない |
| `Planned` | 現行Roadmapに含むが、詳細Gate前である |
| `Future R&D` | 本体の主要機能完成後に統合する独立研究領域である |

FutureまたはPlannedと書かれた項目は、実装済みを意味しない。

---

## 4. 現在地 — Phase 1 Finalization

2026年7月22日時点の現在地は次のとおりである。

```text
Phase 0                               : Complete
Phase 1-A～1-E                        : Complete／Accepted
Phase 1-F Repository／Mac／Preflight  : Accepted
Phase 1-F Lightning Native            : Validation Waiting
Phase 1-G Minimal Web Surface         : Complete／Accepted
Phase 1-H Summary Mode／UI Language   : Complete／Accepted
Mac User Acceptance                   : Waiting
Lightning CUDA／CPU／Public URL Gate  : Waiting
Phase 1 Cross-environment Final Review: Waiting
Phase 1 Completion Declaration        : Not Yet Declared
Phase 1-ex                            : Accepted Reservation／Not Started
GitHub Initial Publication            : Deferred until Phase 1-ex Completion
```

現在、MacではQwen3-4B GGUFを用いたCLIと最小Web Previewが動作する。Streaming、生成停止、一時的な複数Turn、回答言語切替、推論過程表示、要約モード、UI日本語／英語切替を実装済みである。

一方、Phase 1全体はまだ完了宣言前である。Lightning AI Studio上でのCUDA／CPU／公開URL、User Acceptance、Cross-environment Final Review、Backupが残っている。

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

**State: `Finalization／Cross-environment Validation`**

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

**State: `Repository Accepted／Native Validation Waiting`**

- Ubuntu Linux x86_64 Profile
- NVIDIA CUDA Profile
- CPU Profile
- Python 3.12.11 Support
- Lightning用Setup／Preflight／Acceptance Script
- macOS Metalとの共通Contract

Repository側の実装とRead-only Preflightは受入済みである。Lightning上での最終Native実測はCurrent Gateとして残る。

### Phase 1-G — Minimal Web Surface

**State: `Complete／Accepted`**

- FastAPI Web Boundary
- 最小Chat UI
- 一時的な複数Turn
- Streaming／Stop／New Chat
- Preview用Basic認証
- Non-loopback BindのFail Closed
- Phase 2以降でUIを交換できるAPI境界

### Phase 1-H — Summary Mode and UI Language

**State: `Complete／Accepted`**

- Post-generation Summary Mode `OFF／ON`
- 同じMain ModelのSequential Reuse
- Summary Failure時のOriginal Fallback
- Summary成功時のOriginal非露出
- SSE Keepalive
- UI日本語／英語切替
- UI LanguageとResponse Languageの独立

### Phase 1 Milestone

> **Portable, cross-environment-ready LLM Runtime with a minimal public evaluation surface**

Phase 1は「完成したLLM」ではなく、Model交換、Platform交換、Streaming、Cancel、Config、Web接続の基礎契約を証明するPhaseである。

---

## 7. Phase 1-ex — Operations, Documentation, and Public Transition

**State: `Accepted Reservation／Not Started`**

Phase 1完了後、初回GitHub公開前に実施する運用移行Phase。新しいAI機能を増やすPhaseではなく、Projectを長期研究・分業・公開に耐えられる状態へ変える。

### 主な対象

- 設計統括者役、Phase別設計者役、実装者役、対外Docs役の再編
- Git Workflow
- Docs Directory Migration
- Stable Canonical Docs
- Project Continuity Master
- Phase単位Lossless Documentation Compilation
- Public Identity／Privacy／Attribution
- README／LICENSE／CITATION／NOTICE
- Overview／Concept／Roadmap／Phase Summary
- Backup／Manifest／SHA-512／Restore
- GitHub公開用AllowlistとSecret／PII Scan

### Lossless Documentation

PhaseごとのDocumentation統合は、要約や意訳ではなくLossless Compilationとして行う。

- Source SetをFreezeする。
- Path、State、Size、SHA-512を記録する。
- 元本文を変更せず格納する。
- 統合Fileから再抽出する。
- Byte SizeとSHA-512が1件でも不一致ならFail Closedとする。

### Phase 1-ex Milestone

> **再現・引き継ぎ・公開・復旧が可能な研究開発Repository**

---

## 8. Phase 2 — Conversation Continuity and Experimental Control Surface

**State: `Planned`**

Phase 1の一時的なWeb Previewを、継続利用と研究設定に耐えられるApplicationへ発展させる。

### Conversation Application

- Session／Turn／Message Identity
- 永続的な複数Turn Conversation
- New Chat／Chat List／History
- Resume／Regenerate／Branch候補
- Generation Stop／Error Recovery
- Model ReloadとChat Actionの分離

### Configuration Control Surface

- 一般利用者向け設定
- 開発・研究設定
- Config Schema Validation
- Effective Config／Source／Diff
- Runtime中に変更可能な設定とRestartが必要な設定の分離
- SecretをUIやTracked Configへ書かない境界

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

### Phase 2 Milestone

> **Persistent Chat and Explicit Runtime Composition**

---

## 9. Phase 3 — Audit, Evidence, and Generic Definition Infrastructure

**State: `Planned`**

Runtimeを「動くSystem」から「何が起きたか検証できるSystem」へ進め、任意Governance Definitionを安全に受け入れる基盤を作る。

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

### 16.4 EASA

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構

Research Area:
AI Safety Governance
```

内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用を対象とし、例外を含む複合的な安全挙動を統治する独立R&D Architecture。

### 16.5 DLAGSA

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

### 16.6 OCILNS

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

### 16.7 Integration Boundary

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
4. Findingがある場合はFollow-upと再Reviewを完了する。
5. User Manual、Requirements、Architecture、ADR、Review、Indexを整合させる。
6. User Acceptanceを行う。
7. Phase完了と次Phase着手可能状態を明示する。
8. Backup、Manifest、Restoreを検証する。
9. Git運用開始後は、同一SnapshotをCommit／Tag／公開へ関連づける。

---

## 20. Project全体の到達条件

本Projectが最終的に目指すのは、機能一覧の消化ではない。

次が実証されている状態を到達条件とする。

- Modelを交換してもApplication CoreとGovernance Contractが維持される。
- Definition 0件、未知Definition、複数Definitionを明示的に扱える。
- 各Layerと各Governance Pointを個別に切り替えられる。
- `off／observe／enforce`の差を同一条件で比較できる。
- Governanceの品質改善と追加Costを同時に測定できる。
- Guard、Judge、Repair、RAG、Agentが独立Componentとして接続される。
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

Future Phaseに記載された項目は実装済みを意味しない。また、EASA、DLAGSA、OCILNSについては名称、研究領域、概要、接続方向だけを公開し、独自Algorithm、内部Protocol、改竄耐性の具体方式、非公開実装情報は含めない。

本Roadmapは将来実装の自動承認、外部Service操作、Model Download、権限付与またはSecurity Policyの無効化を意味しない。
