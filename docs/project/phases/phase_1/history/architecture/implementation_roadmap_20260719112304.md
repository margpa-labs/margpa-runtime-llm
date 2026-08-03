# MARGPA Runtime LLM 実装Roadmap

- 文書ID: `implementation_roadmap`
- 状態: `current`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: Project全体Phase、Milestone、Phase Gate、現在地点
- 正本言語: 日本語
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- 関連ADR: [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md)
- supersedes: `implementation_roadmap_20260719041847.md`

## 1. Roadmap再編の要旨

`margpa-runtime-llm`は、単一のLocal LLM Runtimeから、疎結合なAI実験・Runtime Governance Platformへ拡張する。

そのため、旧Roadmapの「Conversation UI → Audit／Governance」の順を改め、UIの前に次を置く。

- Component Registry／Switchboard
- Experiment Runtime
- Runtime Event／Status／Minimal Audit
- Lightning AI StudioでのLinux／CUDA検証
- Generic Governance Definition Platform
- MARGPA Main Governance

## 2. Current Position

```text
Phase 0   Project Definition／Technology Selection : Complete

Phase 1-A Environment                               : Complete／Accepted
Phase 1-B Model Runtime                             : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration      : Complete／Accepted
Phase 1-D Configuration／Response Language         : Implemented／Review Requested／Not Yet Accepted
Phase 1-E Thinking Presentation                     : Planned／Not Designed／Not Authorized

Phase 2+                                              : Requirements／Architecture Accepted／Implementation Not Authorized
```

Phase 1-Dについては、実装担当から次の報告がある。本Snapshotでは索引に取り込むが、今回はReview依頼ではないため受入判定は行わない。

- [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md)

## 3. Phase 0: Project Definition／Technology Selection

状態: Complete

- Project目的、Scope、優先順位
- M2 Pro／16GBの制約
- Model・Backend候補
- Main／Guard／Judge Modelの初期選定
- Modular Monolith／Port／Adapter
- Python／Dependency Strategy
- Docs／Handoff／Append-Only Rule

## 4. Phase 1: Portable Model Runtime Foundation

### 4.1 Phase 1-A: Environment

状態: Complete／Accepted

- Python 3.13.14
- `.venv`
- uv
- llama-cpp-python Metal Build
- Environment Verification
- Native Metal Smoke
- 再現性Recipe

### 4.2 Phase 1-B: Model Runtime

状態: Complete／Accepted

- Model Port／llama.cpp Adapter
- Model Registry／Profile Config
- Load／Generate／Streaming／Cancel／Unload
- Generation Config
- Thinking実行制御
- CLI
- Model Artifact SHA-512

### 4.3 Phase 1-C: Deployment／Platform／Acceleration

状態: Complete／Accepted

- Deployment Contract
- Platform Registry／Profile Resolver
- Capability／Requirement／Observation
- Pre-load／Post-load Validation
- Cross-platform Hook
- macOS／MetalのNative Verification

### 4.4 Phase 1-D: Configuration／Response Language

状態: Implemented／Review Requested／Not Yet Accepted

- `config/application.toml`
- Application Config Schema 1
- Deployment Profile Schema 3
- Application／Deploymentの責務分離
- Typed Section Composition
- `ja／en／auto`
- Default `ja`
- Explicit／Environment／Application／Built-in Precedence
- System Message Composer
- Effective Source表示

正本設計：

- [configuration_layer_requirements_20260719041847.md](../requirements/configuration_layer_requirements_20260719041847.md)
- [configuration_layer_architecture_20260719041847.md](configuration_layer_architecture_20260719041847.md)
- [phase_1d_response_language_requirements_20260719041847.md](../requirements/phase_1d_response_language_requirements_20260719041847.md)
- [phase_1d_response_language_architecture_20260719041847.md](phase_1d_response_language_architecture_20260719041847.md)

### 4.5 Phase 1-E: Thinking Presentation

状態: Planned／Not Designed／Not Authorized

- Thinking実行と表示の分離
- Thinking表示／非表示
- User-defined Display Label
- Model Protocol Parser
- Streaming Filter
- Raw Output／Display Output分離
- Thinking Sampling Profile
- 保存／非公開Policy

Phase 1-E完了時のMilestone：

> Portable Runtime MVP

## 5. Phase 2: Experimental Runtime Control Plane

状態: Requirements／Architecture Accepted、Implementation Not Authorized

### 5.1 Phase 2-A: Component Registry／Switchboard

- Functional Component Descriptor
- Componentごとの`enabled`
- Governance Bindingの`off／observe／enforce`
- Required／Optional Dependency
- Conflict／Invalid Combination
- Capability
- Degraded Mode
- Side Effect Level
- Immediate／Next Request／Model Reload／Restart
- Point／Binding Hook

Phase 2-AではGuard、Judge、Agent本体を実装しない。将来Componentを登録・検証できる汎用基盤を作る。

### 5.2 Phase 2-B: Experiment Runtime

- Experiment Profile
- Experiment ID／Run ID
- Effective Config Snapshot／Hash／Source
- Model／Artifact／Definition Digest Hook
- Component Switch／Governance Mode
- Seed／Input／Output
- Token／Latency／Stop／Warning／Error
- Baseline Profile

初期Baseline：

```text
baseline_no_governance
baseline_empty_governance
main_governance_observe
main_governance_enforce
```

### 5.3 Phase 2-C: Runtime Event／Status／Minimal Audit

- Runtime Event Contract
- Component／Governance Lifecycle Event
- Runtime Status Projection
- CLI／将来UI用Status
- JSON／JSONL Append-Only
- Canonicalization Version
- SHA-512
- Minimal Run／Turn Record

Status ReportingはPipeline直列Layerではなく、EventのProjectionとする。Reporting FailureでInferenceを壊さない。

### 5.4 Phase 2-D: Lightning AI Studio

- Linux x86_64／CUDA Platform Entry
- Deployment Profile
- llama.cpp CUDA Build Recipe
- Environment Verification
- Native CUDA Smoke
- Mac Metal／Lightning CUDAのCommon Contract Test
- Persistent Model Placement／SHA-512
- SSH／VS Code／Port Hook

Phase 2完了時のMilestone：

> Cross-environment Experimental Runtime

## 6. Phase 3: Generic Governance Definition Platform + MARGPA Main Governance

状態: Requirements／Architecture Accepted、Implementation Not Authorized

### 6.1 Generic Definition Platform

- Empty Definition Provider
- Filesystem Definition Provider
- Repository State
- Package Manifest
- Standard Descriptor
- Adapter Registry
- Legacy ARGD／DAGD Adapter
- Standard GD Adapter
- Generic Declarative Rule Adapter
- Normalized Governance IR
- Compiler Port／Compiled Plan
- Definition／Package／Adjustment／Plan Digest
- Lazy Load／Plan Cache
- Quarantine／Unsupported／Invalid State

Definition 0件を正式Baselineとする。ARGD／DAGD／CDOGDを含め、どのGDもCoreの必須Dependencyにしない。

### 6.2 Governance Control Plane／Kernel

- Definition Registry
- Rule Selection
- Namespaced State
- Evidence／Audit
- Evaluator Port
- Conflict／Action Resolver
- Budget
- `off／observe／enforce`

### 6.3 MARGPA Main Governance

- Main Model Pre／Post Governance Point
- ARGD／DAGDの第一実証（利用可能時）
- Prompt／Context／Generation Constraint
- Output Audit
- Core／Standard／Full Profile
- Basic Repair／Regenerate
- Status／Evidence

### 6.4 Adjustment

- Immutable Definition Source
- Include／Exclude
- Priority／Soft Weight
- Threshold／Severity
- Evaluator Selection
- Token／Call／Latency／Repair Budget
- Action Mapping
- Status Verbosity

Phase 3完了時のMilestone：

> MARGPA Governance MVP

## 7. Phase 4: Conversation Application／Web UI

状態: Planned

- Application API
- Session／Turn／Multi-turn
- New Chat／History／Resume
- Stop／Regenerate
- Web UI
- Typed Config Service
- Local Runtime Override
- Effective Config／Source／Diff／Apply Mode
- Basic UI: Model／Response Language／Chat Action／Simple Status
- `開発・研究設定`
- Component／Governance／Experiment／Status UI

Phase 4完了時のMilestone：

> Usable Governance Chat Prototype

## 8. Phase 5: Guardrail／Security／Policy

状態: Planned

- Rule-based Input／Output Guard
- Prompt Injection／Jailbreak
- Secret／PII対応
- Qwen3Guard-Gen-0.6B Adapter
- Deterministic Tool Permission
- Guard Governance Point／Binding
- Policy Governance Point／Binding
- AISGD／MPGD／DAAGD Hook
- Human Approval Hook

注意：

- Qwen3GuardはPhase 5まで常駐必須にしない。
- Tool PermissionはModelではなく決定論的Policyを正本とする。
- GuardのOFFをSystem／Host Policyの無効化にしない。

## 9. Phase 6: Judge／Evaluation／Repair

状態: Planned

- Rule-based Evaluation
- LLM-as-a-Judge
- Selene-1-Mini-Llama-3.1-8B Adapter
- Judge Governance Point／Binding
- Judge Independence／Confidence／Conflict
- Repair Component
- Repair Governance Point／Binding
- Repair Budget／Success Criterion／Loop Prevention
- User Rating／Comment／Problem Tag
- Before／After Comparison

Phase 6完了時のMilestone：

> Safety／Evaluation／Repair Research Prototype

## 10. Phase 7: RAG／Data Governance

状態: Planned

- Document Registration
- Chunking
- Embedding
- Index／Retriever
- Context Injection
- Source／Citation
- Document／Chunk Digest
- RAG ON／OFF
- RAG Governance Point／Binding
- DSGD／AISGD／ARGD Hook
- Retrieval／Source／Score Audit

## 11. Phase 8: Agent／Tool／Memory

状態: Planned

- Tool Registry
- Planning／Multi-step Execution
- Observation／Replanning
- State／Memory／Handoff
- Completion Check
- Max Step／Time／Retry
- Tool Permission／Human Approval
- Side Effect Control
- Agent／Tool Governance Point
- AAGD／AISGD／DAAGD Hook
- Tool Call／State／Handoff Audit

Phase 8完了時のMilestone：

> Full Original-scope Prototype

## 12. Phase 9: Multi-Governance Orchestration

状態: Future

- Multiple Active Definition
- Definition／Rule Conflict
- Cross-point Handoff
- Suppression／Weakening／Repair Propagation
- Task／Capability-based Dynamic Routing
- CDOGDまたはCustom Orchestrator Capability
- Meta Review
- Bounded Governance-on-governance
- Manual／Static／Dynamic Routing比較

CDOGDは必須ではない。不在時はManual／Static Routingを使い、Custom Orchestrator Definitionと交換できる。

Phase 9完了時のMilestone：

> Multi-Governance Research Platform

## 13. Phase 10: Hardening／Public Release／Expansion

状態: Future

### 13.1 Audit／Storage／Operations

- Hash Chain／HMAC／Signature
- Append-only Hardening／WORM／Merkle候補
- SQLite／PostgreSQL Index
- Backup／Recovery／Retention
- OMRGD Hook
- Performance／Reliability／Security Hardening

### 13.2 Platform／Backend

- Home Server
- Windows
- Linux CPU／CUDA／ROCm／Vulkan
- MLX
- vLLM
- Remote Inference API
- AWS／Azure
- Docker

### 13.3 Model／Modality

- Multiple Main Model
- Larger Model
- Image／LLaVA
- Multiple Guard／Judge
- Model Router

### 13.4 Public Release

- README／Architecture Diagram
- Setup／Model Download
- Governance／Audit／SHA-512仕様
- Anonymous Sample Log
- License／Model License／CC-BY-SA-4.0表記
- GitHub Release

### 13.5 ZeroGPU

- Gradio Adapter
- Transformers／PyTorch Model Adapter
- Safetensors Model
- `@spaces.GPU` Lifecycle
- Public Demo
- Backend交換性実証

Phase 10完了時のMilestone：

> Public／Hardened／Expanded Platform

## 14. Milestone Summary

| Milestone | Phase | 成果 |
|---|---:|---|
| Portable Runtime MVP | 1-E | Model Runtime、Platform Hook、Language、Thinking Presentation |
| Cross-environment Experimental Runtime | 2 | Switchboard、Experiment、Event／Status、Lightning |
| MARGPA Governance MVP | 3 | Generic GD Platform、Main Governance、Empty Baseline |
| Usable Governance Chat Prototype | 4 | API、Conversation、Web UI、Typed Settings |
| Safety／Evaluation／Repair Prototype | 6 | Guard、Judge、Repair |
| Full Original-scope Prototype | 8 | RAG、Agentまで統合 |
| Multi-Governance Research Platform | 9 | 複数GD、Routing、Conflict、Meta Review |
| Public／Expanded Platform | 10 | Hardening、Cloud、ZeroGPU、GitHub |

## 15. Governance Definition Implementation Boundary

- Phase 3で「入れ物」と0 Definition Baselineを作る。
- ARGD／DAGDを第一実証に使うが、必須にしない。
- Catalogの16 GDをPhase 3で一括実装しない。
- Functional Layerの実装Phaseで必要なBinding／Adapterを追加する。
- Dynamic RoutingはPhase 9まで延期する。

## 16. Phase Gate

```text
Requirements
  ↓
Architecture
  ↓
Accepted ADR
  ↓
Designer Handoff
  ↓
User Implementation Authorization
  ↓
Implementation
  ↓
Implementer Status
  ↓
Designer Review + Documentation Index
```

### 16.1 ReviewとIndex

- 実装担当のStatusは、設計者Review後にReview文書と同時に新Indexへ取り込む。
- 今回のPhase 1-D Statusは未Reviewのまま索引に取り込み、Acceptedとは表記しない。

## 17. Current Next Actions

1. Phase 1-Dの設計者Review（ユーザーからReview指示があった場合）
2. Phase 1-E Requirements／Architecture／ADR／Handoff
3. Phase 1-E実装・Review
4. Portable Runtime MVPのGate
5. Phase 2-Aの詳細Schema／Handoff

## 18. Current Deferred Items

- Phase 1-E Thinking Presentation
- Phase 2～10のSource／Config／Test実装
- Lightning Account／GPU操作
- ARGD／DAGD SnapshotのProject内取込み
- Manifest／Standard Envelopeの最終Schema
- UI Frameworkの最終選定
- ZeroGPU
- CDOGD Dynamic Routing
- Guard／Judge／Agent／RAG本体

## 19. Authorization Boundary

本RoadmapはAcceptedされた実装順序の正本である。本Roadmapの存在だけで個別Phaseの実装、Dependency Install、Model Download、Lightning操作、Config変更を解禁しない。
