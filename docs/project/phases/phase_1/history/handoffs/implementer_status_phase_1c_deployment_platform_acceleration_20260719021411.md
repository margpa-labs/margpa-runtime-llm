# Phase 1-C Deployment／Platform／Acceleration 実装状況

- 文書ID: `implementer_status_phase_1c_deployment_platform_acceleration`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 02:14:11 JST`
- 更新日時: `2026-07-19 02:14:11 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719013109.md](../documentation_index_20260719013109.md)
- Implementer Handoff: [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md)
- Requirements: [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
- Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- Accepted ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- Previous Phase Review: [designer_review_phase_1b_model_runtime_final_20260719001604.md](designer_review_phase_1b_model_runtime_final_20260719001604.md)
- supersedes: なし（新規Phase 1-C Status系列）

## 1. 結論

Phase 1-C Deployment／Platform／Acceleration Abstraction Hookを実装した。

```text
Deployment Contract               : Pass
Host／Compute／Backend表現         : Pass
Required／Detected／Executed分離   : Pass
Model／Deployment Capability分離  : Pass
Mac Profile Schema Migration      : Pass
Profile Resolver Priority         : Pass
Unknown Platform Fail Closed      : Pass
Runtime Observation Hook          : Pass
Requirement Validation／Cleanup   : Pass
Static／Default Test               : Pass
実Model／Metal Regression          : Pass
Phase 2以降への越境                : なし
```

Current Mac／Metalの既存動作を維持しながら、将来Platformを接続する境界を追加した。

Windows、Linux、CUDA、ROCm、Vulkan等を実装または実機検証済みとは主張しない。

実装担当側ではPhase 1-C Acceptance CriteriaをPassと判定し、設計者Reviewを依頼する。

## 2. Deployment Contract

追加した主要Contract：

```text
HostPlatformDefinition
ComputeTargetDefinition
BackendRuntimeDefinition
DeploymentRequirements
DeploymentVerificationState
FallbackPolicy
DetectedRuntimeState
ExecutedRuntimeState
RuntimeObservation
```

Profile／Runtimeで次を独立して表現する。

```text
Host OS
Architecture
Execution Environment
Compute Kind
Vendor
Acceleration API
Memory Topology
Device Selector
Offload Policy
Backend／Version
Build Variant
Execution Mode
Required Capability
Fallback Policy
Verification State
```

Vendor、Acceleration APIおよびBackendは形式検証されたString Keyであり、閉じた全世界Enumにしていない。

未知の将来KeyをContract上保持できるTestを追加した。

## 3. Required／Detected／Executed分離

### Required

Deployment Profileの`runtime_requirements`が保持する。

```text
required_capabilities
required_device_kind
required_acceleration_api
fallback_policy
```

### Detected

Runtime Observationの`detected`が保持する。

```text
backend_key／backend_version
build_variant_key／build_variant_source
device_kind_key
device_name／device_id
acceleration_api_key
capabilities
```

Current llama.cppではBuild VariantをNative APIから直接観測できないため、Profile宣言値として記録する。

```text
build_variant_source              : declared
observation_warning               : build_variant_declared_not_observed
```

観測不能値を実測値として推測していない。

### Executed

Runtime Observationの`executed`が保持する。

```text
backend_key／backend_version
device_kind_key
acceleration_api_key
gpu_offload
```

Current実Modelでは次を確認した。

```text
device_kind_key     : gpu
acceleration_api_key: metal
gpu_offload         : true
```

## 4. Capability Before／After

### Before

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
  gpu_offload
```

### After

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

Model Optional
  gpu_offload

Mac Metal Deployment Required
  gpu_offload
```

`InferenceService`は固定Global Setではなく、Model Definitionの`required_features`を検証する。

Model Capability不足時はModel PortをUnloadする既存Fail-Closed動作を維持する。

Deployment Capability不足時もBootstrap ValidationがServiceをUnloadし、Lifecycleを`unloaded`へ戻す。

CPU概念Profileは`gpu_offload`不足だけを理由にFailしないContract Testを追加した。実Windows Profileは作成していない。

## 5. Mac Profile Migration

Tracked ProfileをSchema Version 2へMigrationした。

```text
schema_version     : 2
profile_key        : local.macos-arm64
verification_state : native_verified
```

既存`profile_key`は互換性のため維持した。

追加Section：

```text
[host]
macos／arm64／native

[compute]
gpu／apple／metal／unified

[backend_runtime]
llama_cpp／0.3.34／metal／in_process

[runtime_requirements]
gpu_offload／gpu／metal／deny
```

Model Rootは引き続き相対Pathであり、Tracked Configへユーザー固有絶対Pathを追加していない。

## 6. Profile Resolver／Platform Normalization

Profile解決Priority：

```text
Explicit CLI／Application
  > MARGPA_PROFILE
  > Platform Default Resolver
```

実CLIで`--profile`を省略した場合、Current Hostの`macos／arm64`を正規化し、Current Mac ProfileをPlatform Defaultとして選択する。

正規化：

```text
Darwin              → macos
Windows             → windows
Linux               → linux
arm64／aarch64      → arm64
AMD64／x86_64       → x86_64
```

未知OS／Architectureは`unsupported_platform`となる。

既知PlatformにDefault Profileがない場合は`profile_required`となり、macOS Profileへ暗黙Fallbackしない。

## 7. Runtime Observation Hook

llama.cpp固有のMetal／CPU判定を次へ隔離した。

[runtime_detection.py](../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py)

Current Detectorは次だけを観測する。

```text
Metal Build＋GPU Offload有効＋gpu_layers != 0
  → device=metal／device_kind=gpu／acceleration=metal／gpu_offload=true

上記以外
  → device=cpu／device_kind=cpu／acceleration=cpu_native／gpu_offload=false
```

CUDA／ROCm等の未実装Backendを推測しない。

Application Runtime Observationは、Host Detection、Backend Runtime InfoおよびExecuted Stateを構造化する。

## 8. Requirement Validation

Load後に次を比較する。

```text
Expected Host              vs Detected Host
Expected Backend／Version  vs Detected Backend／Version
Compute Kind               vs Executed Device Kind
Acceleration API           vs Executed Acceleration API
Required Capability        vs Detected Capability
```

不足または不一致時：

- `unsupported_platform`または`unsupported_capability`
- Safe Errorのみを公開
- 暗黙Fallbackなし
- Loaded RuntimeをUnload
- Lifecycle破損なし

Phase 1-Cでは`fallback_policy=deny`だけを実行可能とし、未実装Policyを黙って適用しない。

## 9. CLI／model-info

CLIのDefault Profile固定をResolver Hookへ置き換えた。

`model-info`へ次を追加した。

```text
deployment.verification_state
deployment.host
deployment.compute
deployment.backend_runtime
deployment.runtime_requirements
deployment.profile_resolution_source
deployment.runtime_observation
```

実Model／Metalで確認した主要値：

```text
profile_resolution_source         : platform_default
verification_state                : native_verified
host                              : macos／arm64／native
required_capability               : gpu_offload
detected backend                  : llama_cpp 0.3.34
detected build variant source     : declared
executed device                   : gpu
executed acceleration             : metal
executed gpu_offload              : true
artifact_digest_verified          : true
```

Model Rootのユーザー絶対Pathは出力しない既存Policyを維持した。

## 10. 変更File

### Source

```text
M src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
A src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py
M src/margpa_runtime_llm/bootstrap/config_loader.py
M src/margpa_runtime_llm/bootstrap/phase1_application.py
A src/margpa_runtime_llm/bootstrap/profile_resolver.py
M src/margpa_runtime_llm/entrypoints/cli/main.py
M src/margpa_runtime_llm/modules/inference/application/inference_service.py
M src/margpa_runtime_llm/modules/inference/contracts/runtime.py
M src/margpa_runtime_llm/modules/inference/domain/capabilities.py
M src/margpa_runtime_llm/modules/inference/domain/errors.py
M src/margpa_runtime_llm/modules/inference/public.py
```

### Config／Script

```text
M config/models/qwen3_4b_q4_k_m.toml
M config/profiles/local_macos_arm64.toml
M scripts/models/phase1b_runtime_acceptance.py
```

### Test

```text
M tests/contract/model_port/test_model_port_contract.py
M tests/integration/llama_cpp/test_phase1b_runtime.py
M tests/unit/inference/test_cli.py
M tests/unit/inference/test_config_and_registry.py
A tests/unit/inference/test_deployment_platform.py
M tests/unit/inference/test_llama_cpp_boundary.py
```

`pyproject.toml`と`uv.lock`は変更していない。

## 11. Static／Default／Environment Gate

変更前Baseline：

```text
Default pytest : 47 passed, 2 deselected
Ruff           : Pass
mypy --strict  : Pass／48 source files
```

変更後：

```text
bash -n Setup Recipe       : Pass
Ruff Format Check          : Pass／51 files
Ruff Check                 : Pass
mypy --strict              : Pass／51 source files
compileall                 : Pass
Default pytest             : 66 passed, 2 deselected
Environment Verification   : Pass
```

Environment：

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

Dependency Gate：

```text
uv lock --check           : Pass／117 packages
uv sync --dry-run offline : Pass／115 packages／Would make no changes
```

## 12. 実Model／Metal Regression

```text
pytest -m model_smoke : 2 passed, 66 deselected
```

Production Acceptance：

```text
Success                         : true
Backend                         : llama-cpp-python 0.3.34
Device                          : Metal／GPU
GPU Offload                     : true
Context                         : 4,096
Artifact SHA-512 Verified       : true
Load including SHA-512          : 2.7767 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 25.63 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0512 seconds
```

Platform Default Resolver経由の実CLI Generation：

```text
フェーズ1-C成功
```

ModelのDownload、Copy、Rename、変更は行っていない。

## 13. Config／Lock Hash

```text
Model Definition SHA-512:
2a1d3951b56dba2514fd4c37161dbea8048e80efc1ac9a8672f4a7f1f5d2c6aa3e3aaace7216b522dd2c1627fb30d676a80d7a761881f039f2337983d510f4be

Local Mac Profile SHA-512:
a2ccc4525223c6c04c2d91114699d7d850bb8092829b3bdc3ce02698e94ee0c943af789c94b10a3332bf97f245950f263211bf9ed818c5f3ca4c451f57cfd77c

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

新規Dependencyはない。

## 14. Scope外／Verification State

実装していない：

```text
Windows／Linux Profile
PowerShell／Windows Native Setup
Docker
CUDA／ROCm／Vulkan／SYCL Build
MLX／Transformers／vLLM Adapter
Remote API Adapter
Multi-GPU
Response Language Policy
Thinking表示Filter／Parser
Multi-Turn／Web UI／Phase 2
```

Native Verified：

```text
macOS／Apple Silicon arm64／Metal : native_verified
```

その他Platform用のTracked Profileは作成しておらず、`native_verified`とも記録していない。

Response Language／Thinking Output Policy文書は参照のみとし、Source／Configへ反映していない。

## 15. Known Non-blocking Item

- llama.cpp Build VariantはProfile宣言値であり、Native APIから直接観測していない
- Current llama.cpp Device DetectorはMetal／CPUだけを正規化する
- 同一ModelのIdempotent Load判定はModel Key中心
- Native Packageを通常同期でも再BuildするSetup Recipeは重い
- Logical Model／Artifact Variantの全面分離は後続事項
- Runtime Device Name／IDは現在観測できないため`null`
- Response Language／Thinking PresentationはDeferred

## 16. 設計者へのReview依頼

次をReviewしてほしい。

1. Deployment Contractの意味境界
2. Required／Detected／Executed State分離
3. Model RequiredとDeployment RequiredのCapability分離
4. Mac Profile Schema Version 2 Migration
5. Profile Resolver PriorityとUnknown Platform Fail-Closed
6. Runtime Observationの事実性
7. Capability不足時のUnload／Lifecycle
8. CPU概念Profile ContractとMac Metal Required GPUの両立
9. `model-info`のDeployment／Observation構造
10. Static／Default／Metal Regression Evidence
11. Windows／Linux等をVerifiedと誤記していないこと
12. Phase 1-C Acceptance Criteriaの完了判定

Phase 1-C完了はWindows、Linux、CUDA、ROCm、VulkanまたはRemote Runtimeの動作確認を意味しない。
