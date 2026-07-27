# MARGPA Runtime LLM 全体設計書

```yaml
document_id: system_architecture
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-27 10:01:20 JST
owner: Nazuna Research
active_phase: phase_1_ex
rag_default: true
```

## 1. Architecture Goal

Model、Backend、Governance Definition、Storage、UIおよび将来機能を独立交換できるRuntime Governance型AI研究基盤を、Modular Monolithとして構成する。

```text
Interface
  ↓
Application Use Case
  ↓
Domain／Ports
  ↑
Adapters／Infrastructure
```

CoreはFilesystem、HTTP、特定Model、特定GD、OSまたはCloud SDKへ直接依存しない。

## 2. 全体構造

```text
CLI／Web／Future UI
        ↓
Application／Conversation Runtime
        ↓
Execution Pipeline
  ├─ Input
  ├─ Optional RAG
  ├─ Optional Guardrail／Policy
  ├─ Optional Agent／Tool
  ├─ Main Model
  ├─ Optional Judge
  ├─ Optional Repair
  └─ Output
        ↓
Response／Status／Audit

Governance Control Plane
  ├─ Definition Provider／Registry
  ├─ Adapter／Validator／Compiler
  ├─ Binding／Activation
  ├─ Rule／Semantic Evaluation
  ├─ State／Evidence
  └─ Conflict／Action Resolution

Distributed Governance Points
  ├─ Input Point
  ├─ RAG Point
  ├─ Guardrail Point
  ├─ Policy／Authority Point
  ├─ Agent／Tool Point
  ├─ Judge Point
  ├─ Main Model Point
  └─ Output／Repair Point
```

共有Control Planeは定義、状態、証跡および競合解決を共通化する。各Pointは必要なRuleだけを受け取り、完全なGovernance一式を複製しない。

## 3. 現在のPhase 1 Runtime

```text
CLI／Minimal Web
  ↓
Typed Configuration Resolution
  ↓
Deployment Profile Resolution
  ↓
Model Registry
  ↓
Model Port
  ↓
llama.cpp Adapter
  ↓
Qwen3-4B GGUF
  ↓
Streaming／Cancel／Presentation
```

Webは一時的なBrowser Memoryを利用し、Server側の永続Conversation Storageはまだ持たない。Summary Modeは同じMain Modelを回答完了後に再利用する。

Phase 1-exでは既存Basic Previewを維持し、Repository側のAuto-start Stage A／B Preparationまで実装済みである。

```text
Lightning Auto-start
  → Public URL／Wake-up
  → Web Access Profile
     ├─ basic_preview
     └─ public_demo
  → Public Policy Middleware
  → Existing Conversation Runtime
```

Traffic-aware Wake-upはLightning Platform上の手動実試験待ちである。Public Demoは未実装であり、将来実装時はRate、Token、時間、入力およびGlobal Budgetを制限し、Tool／RAG／外部操作を強制無効とする。

## 4. Layer責務

### 4.1 Interface

- CLI、FastAPI、Web UI、Streaming
- Request／Response変換
- Presentation、Copy、Language、Error表示
- Model固有処理やGovernance判定を持たない。

### 4.2 Application

- Generate、Stop、New Chat、Summary等のUse Case
- Layer Orchestration
- ConfigとCapabilityの検証
- Turn Lifecycle

### 4.3 Domain／Ports

- Model Runtime Contract
- Message、Generation Config、Capability
- Deployment／Platform Contract
- 将来のGovernance、Audit、Storage、Retrieval、Judge、Tool Port

### 4.4 Adapters

- `llama-cpp-python`
- Filesystem／JSON／JSONL
- 将来のMLX、Transformers、vLLM、Remote API、Database

## 5. Configuration Architecture

概念上の優先順位：

```text
Built-in Default
  < Application Config
  < Deployment Profile
  < Environment
  < Explicit CLI／Request Override
```

Application共通値とPlatform固有値を分離する。Effective Configには適用Sourceを残し、UIはConfig Schema Validationを経由して変更する。

## 6. Model Architecture

Model Portは次を抽象化する。

- Load／Close
- Chat Template
- Streaming
- Cooperative Cancel
- Context Limit
- Seed／Stop Sequence
- Token Usage
- Thinking Control
- Model Metadata
- Device／Acceleration

AdapterはCapabilityを申告し、RuntimeはFallback、Degrade、WarningまたはRefusalを明示する。

## 7. Deployment

```text
Local Mac:
  macOS ARM64／Metal／GGUF

Lightning:
  Ubuntu Linux x86_64 Container／Pure CPU
  Auto-start Preflight／Public Demo Candidate

Future Server:
  Linux CUDA／AMD／CPU／vLLM

Hybrid:
  Local UI／Application + Remote Inference
```

Model ArtifactはProject外に配置でき、Registry上のRelative Artifact PathとModel Rootから解決する。

## 8. State／Event／Storage

Current Phase：

- Model Runtime State
- Browser Memory上の一時Conversation
- Effective Config
- Streaming Event

将来：

- Append-only Turn Event
- Conversation Projection
- Governance State／Evidence
- RAG Source Trace
- Tool Execution
- Experiment Run

Status Reportingは各LayerのEventを購読し、Reporting障害で推論本体を壊さない。

## 9. Trust／Authority Boundary

- Model出力は権限ではない。
- Tool Permissionは外部Policy／Human Approvalを正本とする。
- Governance DefinitionはSystem／Developer／Runtime Policyを上書きしない。
- DAAGD等は存在する権限状態を解釈するが、新しい権限を生成しない。
- Guardrail、Governance、JudgeおよびRepairは責務を分離する。

## 10. Documentation Architecture

```text
docs/project/current/
  → 現在の正本。人、Task、RAGの既定入口

docs/project/phases/
  → Phase Index、Lossless Compilation、Raw History

docs/project/shared/
  → 共通規則、Role、将来Schema／Template

docs/public/
  → 対外説明とMilestone History
```

RAG既定範囲は`current/`、Active Phase Index／Compilationおよび`public/`とし、Raw Historyを自動投入しない。

Phase 1-exの実行はMac限定でよいが、RAGはDocument Source、Chunker、Embedding、Index Store、Retriever、Context AssemblerおよびCitation Portへ分離する。将来Lightning／Home Server／Cloud Adapterを追加し、Core変更を最小化する。

Current／Publicは日本語正本を持つ。英語派生版を作る場合は日本語正本と同じ粒度とし、Phase／Shared／Raw Historyは日本語だけを正本とする。2026年7月27日時点では英語派生版を未作成である。

## 11. Optional External R&D Hooks

Phase 10で、固有名称をCoreへHard-codeせずGeneric Port経由で接続する。

```text
EASA:
  Exception Aware Safety Architecture
  例外認識型安全統治機構
  → Generic External Governance Provider Port

DLAGSA:
  Distributed LEA Agentic Governance & Safety Architecture
  分散証跡型例外認識エージェント統治安全機構
  → Generic External Governance Provider Port

OCILNS:
  Open Cognitive Interaction Ledger Network System
  認知対話証跡台帳網
  → Generic Evidence Ledger Port
```

各HookはDefault OFFであり、存在しなくてもCoreが完全動作する。OFF時はLoad、Call、WriteおよびSide Effectを行わない。

## 12. Traceability

- [Requirements Specification](../requirements/requirements_specification_ja.md)
- [Technology Selection](technology_selection_ja.md)
- [Basic Design](basic_design_ja.md)
- [Runtime Governance Specification](../governance/runtime_governance_specification_ja.md)
- [Phase 1 Architecture Compilation](../../phases/phase_1/architecture/phase_1_architecture_ja.md)

## 13. Architectural Invariants

次はPhaseや実装技術が変わっても維持する。

1. ModelとApplication Coreを分離する。
2. ModelとGovernance Definitionを分離する。
3. Functional Componentと専用Governance Pointを分離する。
4. Definition SourceとCompiled Runtime Planを分離する。
5. Configuration SourceとEffective Configを分離する。
6. Runtime StateとStatus Reportingを分離する。
7. Audit原本と検索Index／Projectionを分離する。
8. System TraceとModel Generated Explanationを分離する。
9. Access ControlとModel Policy判断を分離する。
10. External AuthorityとGovernance上のRecommendationを分離する。
11. Public DemoとBasic Previewを分離する。
12. Stable CanonicalとAppend-only Historyを分離する。

特定Framework、特定Model、特定GD名、特定OS、特定Cloudまたは特定Directory名をDomain Semanticsとして扱わない。

## 14. Dependency Direction

```text
Entrypoints
  ├─ CLI
  ├─ Web
  └─ Future API／UI
       ↓
Application Use Cases
  ├─ Generate
  ├─ Stop
  ├─ New Chat
  ├─ Summarize
  └─ Future Govern／Judge／Repair／Retrieve／Act
       ↓
Domain Models／Ports
  ├─ Model Port
  ├─ Config Port
  ├─ Deployment Port
  ├─ Governance Port
  ├─ Evidence Port
  ├─ Storage Port
  ├─ Retrieval Port
  └─ Tool／Authority Port
       ↑
Adapters
  ├─ llama.cpp
  ├─ Filesystem／JSON／JSONL
  ├─ Future MLX／Transformers／vLLM
  ├─ Future SQLite／PostgreSQL
  └─ Future Local／Cloud／Remote Provider
```

DomainはEntrypoint、FastAPI、llama.cpp、Pydantic Settings、Filesystem LayoutまたはCloud SDKへ逆依存しない。Adapter選択はComposition Rootで行う。

## 15. Runtime Execution Pipeline

### 15.1 Baseline

```text
Request
  ↓
Input Validation
  ↓
Effective Config Resolution
  ↓
Deployment／Capability Validation
  ↓
Conversation Context Assembly
  ↓
Model Generation
  ↓
Streaming／Cancel／Stop Reason
  ↓
Presentation
  ↓
Response
```

### 15.2 Future Optional Pipeline

```text
Request
  ↓
Input Governance Point
  ↓
Optional Documentation／General RAG
  ↓
RAG Governance Point
  ↓
Optional Guardrail／Policy／Authority
  ↓
Guardrail／Policy Governance Point
  ↓
Optional Agent／Tool
  ↓
Agent／Tool Governance Point
  ↓
Main Model Governance Point
  ↓
Main Model
  ↓
Optional Judge
  ↓
Judge Governance Point
  ↓
Optional Repair
  ↓
Output／Repair Governance Point
  ↓
Response／Status／Audit
```

各Optional Layerは無効時にLoad、Call、WriteまたはSide Effectを発生させない。Pipelineへ存在しないComponentを実行済みとしてAuditしない。

## 16. Configuration Control Plane

### 16.1 Logical Layers

```text
Application Config:
  Model選択、回答言語、Generation、Presentation、Component Switch

Deployment Profile:
  OS、Architecture、Execution Environment、Compute、Backend、Acceleration

Model Registry:
  Model Identity、Artifact、Hash、Format、Quantization、Capability

Governance Registry:
  Definition Package、Adapter、Compiler、Binding、Profile

Runtime Override:
  Environment、CLI、Validated Web Request
```

### 16.2 Resolution

```text
Built-in Defaults
  < Application
  < Deployment Profile
  < Environment
  < Explicit Request／CLI
```

Resolution Resultは、値だけでなくSource、Validation Warning、Degraded StateおよびRestart Requirementを含む。

### 16.3 Component Switchboard

```text
Component Registry
  ↓
Dependency／Conflict Validation
  ↓
Enabled Component Graph
  ↓
Governance Point Binding
  ↓
Effective Pipeline
```

Main Model以外のComponent本体と、そのComponent専用Governanceは個別に`off／observe／enforce`を選択できる。Invalid Combinationを黙って補正しない。

## 17. Model Runtime Architecture

### 17.1 IdentityとArtifact

```text
Model Key
  ↓
Model Registry Entry
  ├─ Distribution Repository
  ├─ Upstream Model
  ├─ Revision
  ├─ Artifact Relative Path
  ├─ SHA-512
  ├─ Format／Quantization
  └─ Declared Capability
       ↓
Model Root
       ↓
Resolved Artifact
       ↓
Observed Metadata／Capability
```

Declared CapabilityとObserved Capabilityを区別し、Runtime Requirementと照合する。

### 17.2 Concurrency

初期Model Runtimeは同時Generation数1である。複数Request競合時、先行Generationを壊さず`model_busy`として拒否する。将来Multi-worker／Remote Backendへ拡張する場合も、Model単位のCapacity、Queue、TimeoutおよびCancellation Contractを明示する。

### 17.3 Thinking Protocol

Model Output ProtocolはModel Definition側でDelimiter／Parserを宣言し、Presentation LabelはUI設定とする。Reasoning ChannelとFinal ChannelをStreaming Eventで分離し、Hidden ReasoningをClientへ送らない構成を可能にする。

## 18. Web／Access Architecture

### 18.1 Minimal Preview

```text
Browser
  ↓ HTTP／SSE
FastAPI
  ↓
Application Use Case
  ↓
Single Model Runtime
```

ConversationはBrowser Memoryに保持し、Server側永続化を行わない。Browser Reloadで消えることを仕様とする。

### 18.2 Basic Preview

```text
Lightning Managed Secrets
  ↓ Environment
Basic Authentication Boundary
  ↓
FastAPI Preview
```

CredentialをRepository、Docs、Config、ScreenshotまたはLogへ保存しない。`/healthz`だけは認証外だが最小Statusのみを返す。

Lifecycleは次を分離する。

```text
Manual Terminal:
  start／status／restart／stop

Platform-owned Process:
  run
```

`run`は前景Processとして`margpa-web`へ`exec`し、Platform側にLifecycleを委ねる。`start`は背景Process管理を行うため、API Builder等のPlatform Entrypointへ直接使用しない。

### 18.3 Public Demo

匿名Public DemoはBasic Previewの認証解除ではない。別Access ProfileとPolicy Middlewareを持ち、Server側で次を強制する。

- Rate Limit
- Per-request Token／Time／Input上限
- Global Generation／Credit Budget
- Concurrency制限
- Tool／RAG／Agent／External I/O／File Write／Persistenceの強制OFF
- 内部Path／Exception／Secretの非露出

2026年7月27日時点では未実装・未公開である。

### 18.4 Traffic-aware Wake

```text
Third-party URL Access
  ↓
Lightning Traffic-aware Routing
  ↓
Sleeping Service／Studio Wake
  ↓
Platform-owned `run`
  ↓
Model Load／Hash Verification
  ↓
Health Ready
  ↓
Request Processing
```

Repository PreparationとPlatform Availabilityは確認済みである。URL Accessだけで無人起動できるか、URLが維持されるか、Cold Start、CreditおよびSleep復帰が成立するかは、Lightning上のStage B手動試験まで未確認である。

## 19. Deployment Architecture

### 19.1 Local Profile

```text
Host        : macOS ARM64
Compute     : Apple GPU
API         : Metal
Memory      : Unified
Backend     : llama.cpp Metal Build
Python      : 3.13.14
Model Root  : Project外DirectoryへのPOSIX Symbolic Link
```

### 19.2 Lightning Pure CPU Profile

```text
Host        : Ubuntu 24.04系 Linux x86_64 Container
Compute     : CPU
API         : none
Backend     : llama.cpp Pure CPU Build
Python      : 3.12.11
Environment : Project Root/.venv
Model Root  : Project Rootと同階層のmodels/
```

Project内`models`は、外部Model Rootを指すPOSIX Symbolic Linkとする。`.venv`、Model Weight、Cache、Runtime State、Secretおよび一時Logを公開Sourceへ含めない。

### 19.3 Future Profiles

- Linux NVIDIA CUDA
- Linux AMD ROCm／Vulkan候補
- Windows CPU／CUDA
- Home Server
- Cloud GPU／vLLM
- Hybrid Local UI＋Remote Inference
- Remote API

新Profile追加はRegistry DataとAdapter追加で行い、既存Core分岐を増やさない。

## 20. Governance Architecture

Governanceは中央の共有Control Planeと分散Enforcement Pointで構成する。

```text
Definition Providers
  ↓
Package／Definition Registry
  ↓
Schema Adapter／Normalizer
  ↓
Governance IR
  ↓
Compiler／Rule Selection
  ↓
Compiled Plan Cache
  ↓
Point Binding
  ↓
Governance Point
  ↓
Standard Governance Result
  ↓
Action Resolver／Evidence／State
```

Definition 0件を正式Baselineとする。未知名称、未知Domain、任意JSONまたはCustom Providerを受け入れ得るが、存在するだけで自動実行しない。

ARGD／DAGDは初期Main Governance候補であり、Coreの必須前提ではない。将来のAISGD、AAGD、MPGD、DAAGD、CDOGDその他も同じGeneric Contractで扱う。

## 21. Evidence／Observability Architecture

各LayerはStatus Eventを発行する。

```text
input_received
config_resolved
governance_applied
guardrail_passed／blocked
agent_disabled／started
model_loading／generating／cancelled
judge_evaluating
repair_triggered
turn_completed／failed
```

Event BusのSubscriberとして、CLI Status、Web Status、Audit Writerおよび将来のMonitoringを接続する。Status Reporting障害が推論本体を壊さない。

Audit原本はAppend-only JSON／JSONL候補とし、SQLite等は検索Index／Projectionとして分離する。各Event／Turn PayloadへCanonicalization後のSHA-512を付与し、将来Hash Chain、HMAC、SignatureまたはOCILNS等へ接続できる。

## 22. Documentation／RAG Architecture

### 22.1 Documentation Layers

```text
Current:
  現在の自己完結Canonical

Phase:
  Stable Summary／Lossless Compilation／Index

History:
  変更前後原文／Event／Raw Source

Shared:
  共通Rules／Role／Recovery／Schema／Template

Public:
  Overview／Concept／Roadmap／Public History
```

### 22.2 Stable Lifecycle

```text
Stable Source
  ↓ before snapshot
History
  ↓ reconstruct from prior stable + source corpus
Stable Updated
  ↓ after snapshot
History
  ↓ index／hash／link validation
Next Stable State
```

### 22.3 Documentation RAG

```text
DocumentSourcePort
  ↓
ChunkerPort
  ↓
EmbeddingPort
  ↓
IndexStorePort
  ↓
RetrieverPort
  ↓
ContextAssemblerPort
  ↓
CitationPort
```

Mac実装を先行できるが、外部環境用Adapter Hookを最初から持つ。`docs/`不在時は`docs_unavailable`として説明し、推測でProject内容を補わない。Public Demoでは当面RAGをBindingしない。

## 23. External Original R&D Integration

Phase 10以降の独立Systemは、Generic Port、Manifest、Capability、BindingおよびConfig Switchで接続する。

```text
EASA
  → Generic External Governance Provider Port

DLAGSA
  → Generic External Governance Provider Port

OCILNS
  → Generic Evidence Ledger Port
```

共通要件：

- Default OFF
- Provider不在でCore動作
- OFF時Zero Load／Zero Call／Zero Write／Zero Side Effect
- 固有名称によるCore Routing禁止
- Failure Isolation
- Capability／Schema／Version／Digest記録
- Authority／Access Control非上書き

公開Architectureでは名称、研究領域、1～2行の概要および接続境界だけを示す。独自Algorithm、内部Protocol、改竄耐性の具体方式は公開しない。

## 24. Current Architectural State

```text
Implemented／Accepted:
  Model Port
  llama.cpp Adapter
  Config Resolution
  Deployment Profile
  macOS Metal
  Lightning Pure CPU
  CLI
  Minimal Web
  Basic Preview
  Streaming／Cancel
  Temporary Multi-turn
  Language／Thinking／Summary／Copy／Safe Markdown
  Docs Directory Migration
  Lightning Auto-start Repository Preparation

In Progress:
  Current Canonical Reconstruction
  Phase 1／Phase 1-ex Lossless Reconstruction
  Shared／Public Docs
  Publication Metadata

Designed／Not Implemented:
  Generic Governance Platform
  Main Governance
  Guardrail／Judge／Repair
  Audit Store
  Documentation RAG
  General RAG
  Agent／Tool
  ML／Training
  Anonymous Public Demo
  Traffic-aware Wake実機成立
  Git Workflow
  EASA／DLAGSA／OCILNS Integration
```
