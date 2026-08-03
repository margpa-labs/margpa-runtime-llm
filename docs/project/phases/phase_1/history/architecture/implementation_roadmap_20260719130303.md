# MARGPA Runtime LLM 実装Roadmap

- 文書ID: `implementation_roadmap`
- 状態: `current`
- 作成日時: `2026-07-19 13:03:03 JST`
- 更新日時: `2026-07-19 13:03:03 JST`
- Snapshot: `20260719130303`
- 作成担当: 設計者役担当Task
- 対象: Project全体Phase、Milestone、Phase Gate、現在地点
- 正本言語: 日本語
- Phase 1-E Requirements: [phase_1e_thinking_presentation_requirements_20260719130303.md](../requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
- Phase 1-E Architecture: [phase_1e_thinking_presentation_architecture_20260719130303.md](phase_1e_thinking_presentation_architecture_20260719130303.md)
- Accepted ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- Accepted Handoff: [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
- 最新Index: [documentation_index_20260719130303.md](../documentation_index_20260719130303.md)
- supersedes: `implementation_roadmap_20260719123547.md`

## 1. 今回の更新

- Phase 1-E Requirements／Architecture／ADRをAcceptedへ更新した。
- Draft Handoffを実装担当向け正式Handoffへ更新した。
- Default Display Labelを`推論`から`高度推論`へ変更した。
- Phase 1-EのCurrent Positionを`Design Accepted／Ready for Implementation Authorization`とした。

Phase 0～10の再編Scope、Governance Architecture、Lightning AI Studio選定、Definition 0件Baselineは変更しない。

## 2. Current Position

```text
Phase 0   Project Definition／Technology Selection : Complete

Phase 1-A Environment                               : Complete／Accepted
Phase 1-B Model Runtime                             : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration      : Complete／Accepted
Phase 1-D Configuration／Response Language         : Complete／Accepted
Phase 1-E Thinking Presentation                     : Design Accepted／Ready for Implementation Authorization

Phase 2+                                            : Requirements／Architecture Accepted／Implementation Not Authorized
```

Current Native Verification：

```text
OS           : macOS
Architecture : Apple Silicon arm64
Acceleration : Metal
Python       : 3.13.14
Backend      : llama-cpp-python 0.3.34
Model        : Qwen3-4B-Q4_K_M.gguf
```

## 3. Phase 0: Project Definition／Technology Selection

状態: Complete

- Project目的、Scope、優先順位
- M2 Pro／16GBの制約
- Main／Guard／Judge Model選定
- Modular Monolith／Port／Adapter
- Python／Dependency Strategy
- Docs／Handoff／Append-Only Rule

## 4. Phase 1: Portable Model Runtime Foundation

### 4.1 Phase 1-A: Environment

状態: Complete／Accepted

- Python 3.13.14／`.venv`／uv
- llama-cpp-python Metal Build
- Environment Verification
- Native Metal Smoke
- 再現性Recipe

### 4.2 Phase 1-B: Model Runtime

状態: Complete／Accepted

- Model Port／llama.cpp Adapter
- Model Registry
- Load／Generate／Streaming／Cancel／Unload
- Generation Config／Thinking実行制御
- CLI／Artifact SHA-512

### 4.3 Phase 1-C: Deployment／Platform／Acceleration

状態: Complete／Accepted

- Deployment Contract
- Platform Registry／Profile Resolver
- Capability／Requirement／Observation
- Pre-load／Post-load Validation
- Cross-platform Hook

### 4.4 Phase 1-D: Configuration／Response Language

状態: Complete／Accepted

- `config/application.toml`
- Application Config Schema `1`
- Deployment Profile Schema `3`
- Application／Deployment責務分離
- Typed Section Composition
- `ja／en／auto`／Default `ja`
- Backend非依存Message Composer
- Effective Source／`model-info`
- Mac／Metal Native Verification

最終Review：

- [designer_review_phase_1d_final_20260719122035.md](../handoffs/designer_review_phase_1d_final_20260719122035.md)

### 4.5 Phase 1-E: Thinking Presentation

状態: Design Accepted／Ready for Implementation Authorization

Accepted Scope：

- Thinking Execution／Parsing／Presentation／Persistence分離
- Default `disabled／hidden／高度推論／disabled`
- Application Config Schema `2`
- Model Definition Schema `2`
- `[presentation.thinking]`
- Model-declared Parser Key／Canonical Delimiter
- Model Key非依存Parser Registry
- Plain Text／Tagged Thinking Parser
- Stateful Streaming Parser
- Hidden No-flash
- Visible Default／Custom Label
- Raw／Normalized／Display Output分離
- Malformed Status／Warning
- Raw Reasoning Persistenceなし
- ThinkingによるSampling自動切替なし
- CLI／`model-info`
- Mac／Metal Regression Gate

Accepted CLI：

```text
Execution:
  --thinking
  --no-thinking

Presentation:
  --show-thinking
  --hide-thinking
  --thinking-label
```

Default Visible Tag：

```text
<高度推論>...</高度推論>
```

Remaining Gate：

```text
ユーザーによるPhase 1-E実装開始の明示許可
```

Phase 1-E完了時のMilestone：

> Portable Runtime MVP

## 5. Phase 2: Experimental Runtime Control Plane

状態: Requirements／Architecture Accepted、Implementation Not Authorized

### 5.1 Phase 2-A: Component Registry／Switchboard

- Functional Component Descriptor
- Component `enabled`
- Governance `off／observe／enforce`
- Required／Optional Dependency
- Conflict／Capability／Degraded／Invalid Combination
- Apply Mode／Side Effect Level
- Governance Point／Binding Hook

### 5.2 Phase 2-B: Experiment Runtime

- Experiment Profile
- Experiment ID／Run ID
- Effective Config Snapshot／Hash／Source
- Model／Artifact／Definition／Adjustment／Plan Digest Hook
- Seed／Input／Output／Token／Latency／Stop
- Baseline Profile

```text
baseline_no_governance
baseline_empty_governance
main_governance_observe
main_governance_enforce
```

Thinking Visibilityは将来Experiment Configurationが参照できるようにするが、Raw Reasoning Persistenceを暗黙有効化しない。

### 5.3 Phase 2-C: Runtime Event／Status／Minimal Audit

- Runtime Event Contract
- Component／Governance Lifecycle
- Runtime Status Projection
- JSON／JSONL Append-Only
- Canonicalization／SHA-512
- Reporting FailureとInferenceの分離
- Thinking Parse Status／Warning Metadata Hook
- Raw ReasoningをDefault Auditへ含めない

### 5.4 Phase 2-D: Lightning AI Studio

- Linux x86_64／CUDA Platform Entry
- Deployment Profile
- llama.cpp CUDA Build Recipe
- Native CUDA Verification
- Mac Metal／Lightning CUDA Common Contract
- Persistent Model Placement／Digest

Milestone: Cross-environment Experimental Runtime

## 6. Phase 3: Generic Governance Definition Platform + Main Governance

状態: Requirements／Architecture Accepted、Implementation Not Authorized

### 6.1 Generic Definition Platform

- Empty／Filesystem Definition Provider
- Repository State
- Package Manifest／Standard Descriptor
- Adapter Registry
- Legacy ARGD／DAGD Adapter
- Standard GD／Generic Declarative Rule Adapter
- Normalized Governance IR
- Compiler Port／Compiled Plan
- Lazy Load／Cache／Quarantine／Digest

ARGD／DAGD／CDOGDを含むすべてのGDは任意であり、Definition 0件を正式Baselineとする。

### 6.2 Governance Control Plane

- Definition Registry／Rule Selection
- Namespaced State／Evidence／Audit
- Evaluator Port／Budget
- Conflict／Action Resolver
- Shared Control Plane + Distributed Point + Explicit Binding

### 6.3 MARGPA Main Governance

- Main Model Pre／Post Governance Point
- ARGD／DAGDの第一実証（利用可能時）
- Core／Standard／Full Profile
- Basic Audit／Repair／Regenerate
- Immutable Source + Adjustment + Binding
- Presentation済みText／Raw Model Outputの境界識別

Milestone: MARGPA Governance MVP

## 7. Phase 4: Conversation Application／Web UI

状態: Planned

- API／Session／Turn／Multi-turn
- New Chat／History／Resume／Stop／Regenerate
- Web UI
- Typed Config Service／Local Runtime Override
- Effective Config／Source／Diff／Apply Mode
- Basic UI／`開発・研究設定`
- Thinking Visibility／Display Label UI
- Status／Experiment UI

Milestone: Usable Governance Chat Prototype

## 8. Phase 5: Guardrail／Security／Policy

状態: Planned

- Rule-based Injection／Jailbreak／Secret／PII Guard
- Qwen3Guard-Gen-0.6B
- Deterministic Tool Permission
- Guard／Policy Governance Point
- AISGD／MPGD／DAAGD Hook
- Human Approval Hook

## 9. Phase 6: Judge／Evaluation／Repair

状態: Planned

- Rule-based Evaluation
- LLM-as-a-Judge／Selene-1-Mini-Llama-3.1-8B
- Judge／Repair Governance Point
- Repair Budget／Success Criterion／Loop Prevention
- User Rating／Problem Tag／Before／After

Milestone: Safety／Evaluation／Repair Research Prototype

## 10. Phase 7: RAG／Data Governance

状態: Planned

- Document／Chunk／Embedding／Index／Retriever
- Context Injection／Source／Citation／Digest
- RAG ON／OFF
- RAG／Data Governance Point
- DSGD／AISGD／ARGD Hook

## 11. Phase 8: Agent／Tool／Memory

状態: Planned

- Tool Registry／Planning／Multi-step
- Observation／Replanning／State／Memory／Handoff
- Completion Check／Max Step／Time／Retry
- Tool Permission／Human Approval／Side Effect
- Agent／Tool Governance Point
- AAGD／AISGD／DAAGD Hook

Milestone: Full Original-scope Prototype

## 12. Phase 9: Multi-Governance Orchestration

状態: Future

- Multiple Definition／Conflict
- Cross-point Handoff／Suppression／Weakening／Repair Propagation
- Task／Capability-based Dynamic Routing
- CDOGDまたはCustom Orchestrator Capability
- Bounded Meta Review

CDOGDは必須ではない。

Milestone: Multi-Governance Research Platform

## 13. Phase 10: Hardening／Public Release／Expansion

状態: Future

- Hash Chain／HMAC／Signature／Storage Hardening
- SQLite／PostgreSQL／Backup／Recovery
- Windows／Linux CPU／CUDA／ROCm／Vulkan／MLX
- Home Server／vLLM／Remote／AWS／Azure／Docker
- Multiple Model／Image
- GitHub Release／License／Public Docs
- ZeroGPU／Gradio／Transformers／PyTorch Public Demo

Milestone: Public／Hardened／Expanded Platform

## 14. Milestone Summary

| Milestone | Phase | 成果 |
|---|---:|---|
| Portable Runtime MVP | 1-E | Platform Hook、Language、Thinking Presentation |
| Cross-environment Experimental Runtime | 2 | Switchboard、Experiment、Status、Lightning |
| MARGPA Governance MVP | 3 | Generic GD Platform、Main Governance、Empty Baseline |
| Usable Governance Chat Prototype | 4 | API、Conversation、Web UI |
| Safety／Evaluation／Repair Prototype | 6 | Guard、Judge、Repair |
| Full Original-scope Prototype | 8 | RAG、Agentまで統合 |
| Multi-Governance Research Platform | 9 | 複数GD、Routing、Conflict |
| Public／Expanded Platform | 10 | Hardening、Cloud、ZeroGPU、GitHub |

## 15. Current Next Actions

1. ユーザーによるPhase 1-E実装開始許可
2. Phase 1-E Implementation
3. Implementer Status
4. Designer Independent Review + Index
5. Portable Runtime MVP Gate
6. Phase 2-A詳細Schema／Handoff

## 16. Phase Gate

```text
Requirements                 : Accepted
Architecture                 : Accepted
ADR                          : Accepted
Designer Handoff             : Accepted
User Implementation Approval : Waiting
Implementation               : Not Started
Implementer Status           : Not Created
Designer Review              : Not Started
```

## 17. Authorization Boundary

Phase 1-Eは設計確定・引き渡し完了である。

現時点で次は未解禁である。

- Phase 1-E Source／Config／Test実装
- Dependency Install／Update
- Model Download
- Phase 2以降の実装
- Lightning Studio／ZeroGPU操作

