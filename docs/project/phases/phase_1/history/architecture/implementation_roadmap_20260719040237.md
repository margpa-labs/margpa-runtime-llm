# MARGPA Runtime LLM 実装Roadmap

- 文書ID: `implementation_roadmap`
- 状態: `current`
- 作成日時: `2026-07-19 04:02:37 JST`
- 更新日時: `2026-07-19 04:02:37 JST`
- Snapshot: `20260719040237`
- 作成担当: 設計者役担当Task
- 対象: Phase構成、現在地点、次段階、Deferred Scope
- 正本言語: 日本語
- 最新Index: [documentation_index_20260719040237.md](../documentation_index_20260719040237.md)
- supersedes: `implementation_roadmap_20260719013109.md`

## 1. Current Position

```text
Phase 1-A Environment                         : Complete／Accepted
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration  : Complete／Accepted
Phase 1-D Response Language Policy            : Designed／Accepted／Implementation Not Authorized
Phase 1-E Thinking Presentation Policy        : Planned／Not Designed／Not Authorized
Phase 2 Conversation Application              : Not Started
```

Current Native Verification：

```text
macOS／Apple Silicon arm64／Metal
Qwen3-4B-GGUF Q4_K_M
llama-cpp-python 0.3.34
Python 3.13.14
```

## 2. Phase 1の最終構成

Phase 1は`1-A`から`1-E`までとする。

### Phase 1-A：Environment

状態：Complete／Accepted

- `.venv`
- Python 3.13.14
- uv Lock／Setup Recipe
- llama-cpp-python Metal Build
- Environment Verification
- Native Metal Smoke

### Phase 1-B：Model Runtime

状態：Complete／Accepted

- Model Port
- llama.cpp Adapter
- Model Registry
- Profile Config
- Load／Unload
- Generate／Streaming／Cancel
- Generation Config
- Thinking実行On／Off
- CLI一問一答
- SHA-512 Model Artifact Verification

### Phase 1-C：Deployment／Platform／Acceleration

状態：Complete／Accepted

- Deployment Contract
- Platform Registry
- Profile Resolver
- Platform Normalization
- Model Capability／Deployment Requirement分離
- Pre-load／Post-load Validation
- Runtime Observation
- Current Mac／Metal Regression
- 将来Windows／Linux／Home Server／Cloud Hook

### Phase 1-D：Response Language Policy

状態：Designed／Accepted／Implementation Not Authorized

- `ja／en／auto`
- Default `ja`
- Profile／Environment／CLI Override
- Explicit > Environment > Profile > Built-in
- Response Language Source
- System Message Composition
- User Prompt／System Message保持
- Streaming／Non-streaming共通Policy
- Config／`model-info`表示

正本：

- [phase_1d_response_language_requirements_20260719040237.md](../requirements/phase_1d_response_language_requirements_20260719040237.md)
- [phase_1d_response_language_architecture_20260719040237.md](phase_1d_response_language_architecture_20260719040237.md)
- [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
- [designer_handoff_phase_1d_response_language_20260719040237.md](../handoffs/designer_handoff_phase_1d_response_language_20260719040237.md)

### Phase 1-E：Thinking Presentation Policy

状態：Planned／Not Designed／Not Authorized

候補Scope：

- Thinking実行と表示の分離
- Thinking表示／非表示
- Thinking Display Label
- Model Protocol Parser
- Streaming Thinking Filter
- Raw Output／Display Output分離
- Malformed Thinking Tag Policy
- Raw Thinking保存方針
- Thinking／Non-Thinking Sampling Profile
- High-Level Explanationへの将来Hook

Phase 1-Dへ混在させない。

設計元：

- [response_language_and_thinking_output_policy_20260719013109.md](response_language_and_thinking_output_policy_20260719013109.md)

## 3. Phase 2：Conversation Application

Phase 1-E完了後に開始する。

- FastAPI等のApplication API
- GPT風Web UI
- Multi-turn Conversation
- New Chat
- History
- Resume
- Stop
- Regenerate
- Generation Config UI
- Model／Deployment／Governance State表示Hook

UI技術はPhase 2開始前に最終選定する。

## 4. Phase 3：Audit／Core Governance

- Audit Log Directory
- Turn Log
- JSON／JSONL
- Canonicalization
- SHA-512
- Definition Loader
- ARGD／DAGD Snapshot
- Core Governance
- High-Level Explanation

## 5. Phase 4：Evaluation／Repair／Guardrail

- User Rating
- Problem Tag
- Deviation
- Severity
- Repair／Regeneration
- Re-fix
- Rebind／Enforce
- Audit Log UI
- Guard Model
- Rule Based Prompt Injection Guard
- Deterministic Tool Permission Hook

## 6. Phase 5：RAG

- Document Registration
- Chunking
- Embedding
- Index
- Retrieval
- Context Injection
- Source／Citation
- Retrieval Audit

## 7. Phase 6：Agent

- Tool Registry
- Tool Selection
- Multi-step Execution
- Planning／Observation／Replanning
- State／Memory／Handoff
- Completion Check
- Human Approval
- Side Effect確認
- Agent Audit
- Loop制限

## 8. Phase 7：Extensions

- SQLite／PostgreSQL
- Lightweight ARGD／DAGD
- Multiple Models
- Multiple GDs
- Image
- Docker
- Home Server Profile
- Windows／Linux Native Profile
- CUDA／ROCm／Vulkan／SYCL／MLX
- AWS／Azure／Google Cloud
- vLLM／Remote Adapter
- Routing
- LLM-as-a-Judge本格統合
- AISGD／AAGD／MPGD／DAAGD
- CDOGD

## 9. Current Deferred Items

- Native Packageを通常同期でも再BuildするSetup Recipeは重い
- Response Languageは設計済みだが未実装
- Thinking表示／非表示はPhase 1-E
- Thinking時もNon-Thinking Sampling Defaultを使用する
- Raw Output／Display Output未分離
- Runtime Device判定がMetal／CPU中心
- Logical Model／Artifact Variant全面分離は未実装
- Windows／Linux Native Verification未実施
- `.DS_Store`再生成はRepository Hygiene課題

## 10. Phase Gate原則

各Phaseは次の順で進める。

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
Designer Review＋Documentation Index
```

次Phaseの設計開始または実装開始を、前Phase完了だけから自動的に推定しない。

## 11. Authorization Boundary

Phase 1-DのRequirements、ArchitectureおよびADRはAcceptedである。

Phase 1-DのSource／Config／Test実装は未解禁である。ユーザーが実装開始を明示した後に着手する。

Phase 1-EはPhase名と大分類だけが決まっており、RequirementsとArchitectureは未確定である。
