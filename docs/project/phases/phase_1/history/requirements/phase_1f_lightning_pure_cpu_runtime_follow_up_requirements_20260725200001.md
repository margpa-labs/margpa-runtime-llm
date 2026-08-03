# Phase 1-F Lightning Pure CPU Runtime Follow-up 要件定義

- 文書ID: `phase_1f_lightning_pure_cpu_runtime_follow_up_requirements`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Source Review: [designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](../handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)
- supersedes: なし

## 1. Purpose

GPU、NVIDIA Driver、CUDA Toolkitまたは`nvcc`を利用できないFreshなLinux x86_64 CPU環境で、MARGPA Runtime LLMをPure CPU Buildとして再構築できるRepository Hookを用意する。

## 2. Current Gap

Current Profile：

```text
config/profiles/lightning_linux_x86_64_cpu.toml
```

Current Effective Intent：

```text
compute_kind_key  : cpu
gpu_layers        : 0
build_variant_key : cuda
```

これはCUDA BuildをCPU実行するProfileであり、Pure CPU Buildではない。Fresh CPU環境でCUDA Buildが存在しない場合、SetupがCUDA Toolkit／`nvcc`を要求する可能性がある。

## 3. Scope

- Pure CPU Deployment Profile
- Pure CPU Backend Build Variant
- CPU専用Setup Script
- CPU専用Preflight
- CPU専用Environment Verification
- Static／Unit／Integration Test
- Bounded Native Acceptance Hook
- User Manual／Status用情報

## 4. Non-goals

- Lightning外部環境での実行
- GPU／CUDA Profile変更
- Model Download
- Model File Upload
- Public URL
- RAG実装
- Project Documentation Corpus Upload
- Performance Guarantee
- Cloud Provider固有SDK

## 5. Required Profile

候補：

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
```

最低条件：

```text
host.operating_system_key       : linux
host.architecture_key           : x86_64
host.execution_environment_key  : container
compute.compute_kind_key        : cpu
compute.vendor_key              : generic
compute.acceleration_api_key    : none
backend_runtime.backend_key     : llama_cpp
backend_runtime.build_variant   : cpu
load.gpu_layers                 : 0
runtime.required_device_kind    : cpu
runtime.required_acceleration   : none
```

実際のSchema Field名はCurrent Contractに合わせる。意味をCUDAへ偽装しない。

## 6. Setup Requirements

候補：

```text
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

- Python `>=3.12,<3.14`
- Target候補はPython 3.12.11
- Project-local Environmentまたは明示されたStudio Environment
- `llama-cpp-python==0.3.34`
- CPU Build
- CUDA／Metal／ROCmを要求しない。
- NVIDIA Driver／`nvidia-smi`／`nvcc`を要求しない。
- Existing CUDA BuildをPure CPU合格Evidenceにしない。
- Normal SyncとNative Rebuildを分離する。
- Repeated Runを可能にする。
- Failure時に不足条件を明示する。

## 7. Preflight

Preflightで確認する。

- Linux
- x86_64
- Container／Studio Environment
- Python Version
- `uv` Version／Path
- CPU Count
- Memory
- Writable Project／Environment Path
- Model PathはOptional Check

Preflightで要求しない。

- GPU
- NVIDIA Driver
- CUDA
- `nvcc`

## 8. Runtime Observation

Runtimeは次を区別する。

```text
backend build variant : cpu
device kind           : cpu
acceleration api      : none
gpu offload           : false
gpu layers            : 0
```

CPU Buildを`cuda`または`gpu`として表示しない。

## 9. Model／Resource Boundary

Model RootはRepository外を正本とし、`MARGPA_MODEL_ROOT`またはEnvironment-local Symlinkで解決できる。

Model Artifactと`.venv`をRepository／Upload Bundleへ含めない。

CPU SmokeはResourceを抑える。

- Main Model 1個だけをLoad
- Guard／Judge／RAG／SummaryはDefault OFF
- Thinking Default OFF
- 短いPrompt
- Bounded Max New Tokens
- 1 Concurrent Generation

## 10. Project Documentation Explainer Boundary

Phase 1-ex後にMac実機でProject Documentation Explainerを実装する場合も、Lightning CPU DeploymentではHook-onlyをDefaultとする。

```text
Component Contract : present
Provider／Index     : absent allowed
enabled             : false
Index Load          : none
Retrieval           : none
Additional Model Call: none
```

OFF時にProvider不存在をStartup Failureとしない。利用不能機能を実行済みと表示しない。

この要件はRAG実装開始を許可しない。

## 11. Automated Test

- Pure CPU Profile Schema
- Host／Architecture／Container Match
- `build_variant=cpu`
- `device=cpu`
- `acceleration=none`
- `gpu_layers=0`
- `gpu_offload=false`
- CUDA Capabilityを要求しない。
- Explicit Profile Resolution
- Mac／CUDA Profile非Regression
- Setup Script Syntax
- Preflight without GPU Commands
- Verification Fail Closed

## 12. Deferred Native Test

外部CPU環境利用可能時に実施する。

- Fresh Setup
- Backend Import
- CPU System Info
- Model Load
- SHA-512
- Short Generation
- Streaming
- Cancel
- Token Limit
- Japanese Response
- Memory／Latency
- Shutdown

Native未実行をPassとして記録しない。

## 13. Acceptance

Repository Acceptance：

1. Pure CPU ProfileとCUDA CPU Execution Profileが区別される。
2. Setup／PreflightがGPU／CUDA／`nvcc`を必須にしない。
3. Static／Unit／IntegrationがPassする。
4. Mac／CUDA Regressionがない。
5. Native TestがPendingとして明示される。

Final Native Acceptance：

1. Fresh CPU EnvironmentでSetupできる。
2. Pure CPU Buildとして観測される。
3. Qwen3-4B Q4_K_MのBounded Smokeが完了する。

## 14. Authorization

Repository側Profile／Script／Testの実装へ着手可能である。外部環境操作は別Gateとする。

