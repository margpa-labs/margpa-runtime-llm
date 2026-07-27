# MARGPA Runtime LLM 全体設計書

```yaml
document_id: system_architecture
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-26 17:53:18 JST
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

Phase 1-exでは既存Basic Previewを維持し、次を追加候補とする。

```text
Lightning Auto-start
  → Public URL／Wake-up
  → Web Access Profile
     ├─ basic_preview
     └─ public_demo
  → Public Policy Middleware
  → Existing Conversation Runtime
```

Public DemoはRate、Token、時間、入力およびGlobal Budgetを制限し、Tool／RAG／外部操作を強制無効とする。

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

Current／Publicは日本語正本と英語派生版を持ち、Phase／Shared／Raw Historyは日本語だけを正本とする。

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
