# 実装ロードマップと現在地点

- 文書ID: `implementation_roadmap`
- 状態: `current`
- 作成日時: `2026-07-19 01:31:09 JST`
- 更新日時: `2026-07-19 01:31:09 JST`
- Snapshot: `20260719013109`
- 対象: Phase、順序、現在地点、未決事項
- 正本言語: 日本語
- supersedes: `implementation_roadmap_20260718193435.md`
- 上位要件: [project_requirements_20260718193435.md](../requirements/project_requirements_20260718193435.md)

## 1. 現在地点

```text
Phase 0                      : Complete for Phase 1 Scope
Phase 1-A Environment        : Complete
Phase 1-B Model Runtime      : Complete／Accepted
Phase 1 Mac User Verification: Pass
Phase 1-C Platform Hook      : Approved Design／Awaiting Implementation Authorization
```

Current Macで、Qwen3-4B GGUF、llama-cpp-python、Metal、Model Port、Streaming、Cancel、Thinking Control、SHA-512検証およびCLI一問一答が成立している。

## 2. Phase 1-C：Deployment／Platform／Acceleration Abstraction Hook

目的：

Current Mac固定条件をApplication Coreから分離し、将来のWindows、Linux、Home Server、Cloud、CPU、GPU、NPUおよびRemote Runtimeを追加可能にする。

実装候補：

- Deployment Requirement Contract
- Host／Compute／Backend Runtime表現
- Model CapabilityとDeployment Requirementの分離
- `gpu_offload`のmacOS Profileへの移動
- Profile Resolver Hook
- Runtime Observation Hook
- Mac Profile Migration
- Unit／Contract Test
- Current Mac Regression

実装しない：

- Windows／Linux Native Profile
- PowerShell Setup
- CUDA／ROCm／Vulkan等のNative Build
- Docker
- Remote Adapter
- 全Platform検証

詳細：

- [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)

## 3. Phase 1-D候補：Response／Presentation Policy

Phase番号は未確定である。

候補：

- Default Response Language `ja／en／auto`
- User／Session／Profile／CLIのLanguage優先順位
- Thinking実行とThinking表示の分離
- Thinking表示／非表示
- Thinking Display Label
- Model Protocol Parser
- Streaming Thinking Filter
- Raw Thinking非保存
- High-Level Explanationへの接続
- Thinking／Non-Thinking Sampling Profile

Phase 1-Cへ混在させない。

設計整理：

- [response_language_and_thinking_output_policy_20260719013109.md](response_language_and_thinking_output_policy_20260719013109.md)

## 4. Phase 2：対話Application

- FastAPI等
- Web UI
- Multi-Turn
- New Chat
- History
- Resume
- Stop
- Regenerate
- Session管理
- Error表示
- Streaming CancelのHTTP／UI接続

Response／Presentation PolicyをPhase 2前に実装するか、Phase 2内へ含めるかはPhase 1-C後に決定する。

## 5. Phase 3：AuditとCore Governance

- Audit Log Directory
- Turn Log
- JSON／JSONL
- SHA-512
- Definition Loader
- Definition Validator
- ARGD／DAGD Snapshot
- Governance Compiler初期版
- Core Governance Profile
- High-Level Explanation
- Governance State
- Status表示
- Required／Detected／Executed Runtime State記録

## 6. Phase 4：Evaluation、Repair、Guardrail

- Evaluation
- Deviation
- Severity
- Repair
- Re-fix
- Rebind
- Status Reporting
- User Rating
- Audit Log UI
- Guardrail
- Qwen3Guard
- Rule Based Prompt Injection対策
- Output Guard

今回観測したSoftware Scopeから物理Hardware Scopeへの逸脱は、Governance評価Sample候補とする。

## 7. Phase 5：RAG

- Document登録
- Chunking
- Embedding
- Retrieval
- Context Injection
- Source
- Citation
- RAG Audit
- RAG On／Off

## 8. Phase 6：AI Agent

- Tool Registry
- Multi-Step Execution
- Planning
- Observation
- Tool Permission
- Human Approval
- Side Effect確認
- Agent Audit
- Loop制限

## 9. Phase 7：拡張

- SQLite
- Lightweight ARGD／DAGD
- 複数Model
- 複数GD
- Image
- Docker
- Home Server Profile
- Windows／Linux Profile
- CUDA／ROCm／Vulkan／SYCL／MLX
- AWS／Azure／Google Cloud
- vLLM
- Remote Adapter
- Routing
- LLM-as-a-Judge本格統合
- CDOGD
- 他Domain GD

## 10. Platform追加の原則

実Hardware、OS、DriverおよびBackendが決まった時点で必要なProfileだけ追加する。

```text
全Platformを今実装しない
全Platformを後から表現できるContractを今作る
未検証PlatformをVerifiedと表示しない
```

## 11. Current Known Issues／Deferred Items

- 同一ModelのIdempotent Load判定はModel Key中心
- Native Packageを通常同期でも再BuildするSetup Recipeは重い
- Response Language Default未実装
- Thinking表示／非表示未実装
- Thinking時もNon-Thinking Sampling Defaultを使用する
- Raw Output／Display Output未分離
- Runtime Device判定がMetal／CPU中心
- Logical Model／Artifact Variant全面分離は未実装
- Windows／Linux Native Verification未実施
- `.DS_Store`再生成はRepository Hygiene課題

## 12. Authorization Boundary

Phase 1-C設計とADRはAcceptedである。

Source、Config、Test、Script、DependencyまたはRoot Fileの実装変更は、ユーザーの明示的な実装許可後に行う。

