# Phase 1-C Deployment／Platform／Acceleration 実装担当Handoff

- 文書ID: `designer_handoff_phase_1c_deployment_platform_acceleration`
- 状態: `ready_for_implementation_authorization`
- 作成日時: `2026-07-19 01:31:09 JST`
- 更新日時: `2026-07-19 01:31:09 JST`
- Snapshot: `20260719013109`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719013109.md](../documentation_index_20260719013109.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- Phase 1-B Final Review: [designer_review_phase_1b_model_runtime_final_20260719001604.md](designer_review_phase_1b_model_runtime_final_20260719001604.md)
- supersedes: なし（新規Phase 1-C専用Handoff系列）

## 1. Handoff Conclusion

Phase 1-Bは完了・最終受入済みである。

ユーザーはPhase 1-Cを、Windows専用Hookではなく、Deployment／Platform／Accelerationを独立軸として扱う汎用Hookとする設計を承認した。

実装担当は、ユーザーからPhase 1-C実装開始とWrite Scopeについて明示的な許可を得た後、本Handoffの範囲を実装する。

本Handoffの作成は、実装、File変更、Native Build、Dependency変更またはCommand実行を自動的に解禁しない。

## 2. Required Reading Order

実装開始前に、次を読み取り専用で確認する。

1. [documentation_index_20260719013109.md](../documentation_index_20260719013109.md)
2. [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
3. [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
4. [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
5. [designer_review_phase_1b_model_runtime_final_20260719001604.md](designer_review_phase_1b_model_runtime_final_20260719001604.md)
6. [phase_1b_model_runtime_contract_20260718223203.md](../architecture/phase_1b_model_runtime_contract_20260718223203.md)
7. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
8. [documentation_rules_20260718193435.md](../requirements/documentation_rules_20260718193435.md)

Response Language／Thinking設計は実装Scope外の参照資料として読む。

9. [response_language_and_thinking_output_policy_20260719013109.md](../architecture/response_language_and_thinking_output_policy_20260719013109.md)

## 3. Authorization／Write Scope Gate

暫定担当分担における実装者役の通常Write Scope：

```text
src/
tests/
scripts/
docs/handoffs/implementer_status_*
```

Phase 1-Cでは、設計上次への変更が必要になる可能性が高い。

```text
config/profiles/local_macos_arm64.toml
config/models/qwen3_4b_q4_k_m.toml
pyproject.toml                 # Marker／CLI設定等が必要な場合のみ
```

実装前にユーザーから少なくとも次を確認する。

1. Phase 1-C実装開始
2. `config/`変更
3. 必要な場合の`pyproject.toml`変更
4. Static／Default Test実行
5. 実Model／Metal Test実行
6. Docs Handoff Status作成

Requirements、Architecture、Governance、ADR、Designer ReviewおよびIndexを実装担当が編集しない。

## 4. Objective

Current Mac／Metalの成立状態を維持しながら、次を実現する。

```text
Model固有条件
Deployment固有条件
Runtime観測事実
```

を分離し、将来のWindows、Linux、Home Server、Cloud、CPU、CUDA、ROCm、Vulkan、Remote Backend追加時にApplication Coreを大規模変更しなくてよい境界を作る。

## 5. Locked Decisions

実装担当が独断変更しない。

```text
Phase名                         : Deployment／Platform／Acceleration Abstraction Hook
全Platform実装                  : 行わない
Current Native Verification     : macOS／Apple Silicon／Metalのみ
gpu_offload                     : Model必須からDeployment必須へ再分類
Mac Metal Profile               : gpu_offload必須を維持
Unknown Platform                : Macへ暗黙Fallbackしない
Profile Priority                : Explicit > Environment > Platform Default
Vendor／Backend Key             : 拡張可能Identifier
Required／Detected／Executed     : 分離
Tracked User Absolute Path      : 禁止
追加Heavy Dependency            : 追加しない
Windows／Linux Native Setup     : Scope外
CUDA／ROCm／Vulkan Build        : Scope外
Response／Thinking Policy       : Scope外
```

## 6. Required Deliverables

### 6.1 Deployment Requirement Contract

最低限、次を表現する。

- Host OS Key
- Architecture Key
- Execution Environment Key
- Compute Kind Key
- Vendor Key（Optional）
- Acceleration API Key
- Backend Build Variant Key
- Required Runtime Capabilities
- Fallback Policy
- Verification Stateまたは将来追加点

全候補Fieldを一度に実装する必要はない。Requirementsの意味境界を壊さない最小Contractとする。

### 6.2 Capability再分類

現在のModel Required Capabilityから`gpu_offload`を分離する。

```text
Model Required
  chat
  streaming
  cooperative_cancel
  stop_sequences
  seed
  token_usage
  model_metadata
  chat_template
  thinking_control

Mac Deployment Required
  gpu_offload
```

Model Registryの`gpu_offload`はOptionalへ移すか、Deployment側だけで要求する。二重の矛盾した正本を残さない。

### 6.3 Requirement Validation

Load後のEffective CapabilityとDeployment Required Capabilityを比較する。

不足時：

- 明示Error
- Resource解放
- Lifecycle破損防止
- Safe Error

を保証する。

暗黙CPU Fallbackは行わない。

### 6.4 Profile Resolver Hook

候補Priority：

```text
CLI／Application Explicit
  > MARGPA_PROFILE等のEnvironment
  > Platform Default Resolver
```

Current CLIのDefault挙動を維持しつつ、将来差し替え可能にする。

Windows Profileを作る必要はない。

### 6.5 Platform Normalization

Host Libraryの生値を正規化する最小境界を作る。

```text
Darwin → macos
AMD64／x86_64 → x86_64
arm64／aarch64 → arm64
```

未知値を推測で既知Platformへ割り当てない。

### 6.6 Runtime Observation Hook

Current `device="metal" if "MTL" else "cpu"`を、将来Backend固有Detectorへ交換できる境界へ整理する。

Phase 1-CでCUDA／ROCm等を正確に検出する必要はない。

Current Macで`metal`と`gpu_offload=true`が維持されること。

## 7. Suggested Implementation Sequence

1. Existing Testを変更前に確認する
2. Deployment Contractを追加する
3. Profile Loaderへ新Fieldを追加する
4. Current Mac ProfileをMigrationする
5. Capability再分類を行う
6. BootstrapへRequirement Validationを追加する
7. Profile Resolver／Platform Normalizerを追加する
8. Unit／Contract Testを追加する
9. Static／Default Gateを実行する
10. Metal Model Smokeを実行する
11. 実装担当Statusを新Timestampで作成する

## 8. Candidate File Scope

候補であり、不要なFileを量産しない。

```text
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/bootstrap/profile_resolver.py
src/margpa_runtime_llm/modules/inference/contracts/runtime.py
src/margpa_runtime_llm/modules/inference/domain/capabilities.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
config/profiles/local_macos_arm64.toml
config/models/qwen3_4b_q4_k_m.toml
tests/unit/inference/
tests/contract/model_port/
tests/integration/llama_cpp/
```

`shared/platform/`は複数Consumerが存在する場合のみ追加する。

## 9. Required Test Cases

### Profile／Platform

- Current Mac Profile Parse Pass
- Unknown Field拒否
- Known OS／Architecture Normalize
- Unknown Platform明示Error
- Explicit Profile優先
- Environment Profile優先
- Platform Defaultは最後

### Capability

- Model Requiredに`gpu_offload`が含まれない
- Mac Deployment Requiredに`gpu_offload`が含まれる
- Runtime GPU Offload不足でMac ProfileはFail
- CPU概念ProfileではGPU不足を理由にFailしないContract Test
- Capability不足時にSafe Error

### Regression

- Static Check
- Default pytest
- Environment Verification
- `model-info`
- Qwen3 Generation
- Streaming
- Cancel
- Metal Model Smoke

Test件数の固定値ではなく、Failure／Errorが0であることを基準とする。

## 10. Prohibited Scope Expansion

- Windows Profile作成
- PowerShell Script作成
- Windows用Dependency Build
- Linux Profile作成
- Docker追加
- CUDA／ROCm／Vulkan Dependency追加
- MLX／Transformers／vLLM Adapter追加
- Multi-GPU実装
- Remote API実装
- Model Download
- Response Language実装
- Thinking表示Filter実装
- Phase 2機能

追加が必要と判断した場合、独断実装せず設計担当へ報告する。

## 11. Response／Thinking Observationの引き継ぎ

Phase 1 CLIで次を観測済みである。

- 日本語を明示しないThinking Requestが英語出力になった
- `日本語で`を明示すると日本語出力になった
- 2048 TokensではThinkingとFinal Answerが完了した
- Software Model交換を物理Hardware Slotとして解釈するScope Driftが発生した

これは単に4B／Q4であることだけが原因ではない。

- Project Context不足
- Input曖昧性
- Thinkingによる誤前提の深掘り
- Response Language未指定
- Output Budget
- Thinking Sampling Profile未分離

が関係する。

詳細は専用Architectureを参照する。

本Phase 1-Cでは修正しない。

## 12. Acceptance Evidence

実装担当Statusへ次を記録する。

- 変更File一覧
- Contract概要
- Capability Before／After
- Profile Schema Before／After
- Config Hash
- Static Check結果
- Default Test結果
- Environment Verification結果
- Model Smoke結果
- `model-info`のDevice／Capability
- Scope外変更がないこと
- Windows／LinuxをNative Verifiedと主張していないこと
- Known Non-blocking Item

## 13. Completion Boundary

Phase 1-C完了は、Current Mac Runtimeを維持しながら汎用Hookが実装された状態を意味する。

Windows、Linux、CUDA、ROCm、VulkanまたはHome Serverで実際に動作したことを意味しない。

Native Platform追加は、Hardware決定後の新Profile、Setup、Testおよび専用Acceptanceで行う。

