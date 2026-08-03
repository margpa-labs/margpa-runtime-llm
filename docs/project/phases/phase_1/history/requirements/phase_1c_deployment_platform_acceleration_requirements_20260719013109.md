# Phase 1-C Deployment／Platform／Acceleration Abstraction要件

- 文書ID: `phase_1c_deployment_platform_acceleration_requirements`
- 状態: `current_approved`
- 作成日時: `2026-07-19 01:31:09 JST`
- 更新日時: `2026-07-19 01:31:09 JST`
- Snapshot: `20260719013109`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-C、Deployment Profile、Platform、Acceleration、Runtime Capability
- 正本言語: 日本語
- 上位要件: [project_requirements_20260718193435.md](project_requirements_20260718193435.md)
- 関連Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- 関連ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: なし（新規Phase 1-C要件系列）

## 1. 結論

Phase 1-Cは、Windows専用実装を追加するPhaseではない。

macOS、Windows、Linux、CPU、GPU、NPU、Local、Home Server、Cloud、Native、ContainerおよびRemote Runtimeを、Application Coreへ固有条件を埋め込まず、同一の構造で後から追加できるDeployment／Platform／Acceleration境界を作る。

```text
Phase 1-Cで行うこと
  全環境を表現・検証・選択できる最小ContractとHookを作る

Phase 1-Cで行わないこと
  全OS、全GPU、全Backendを実装・Build・検証する
```

## 2. 背景

Phase 1-Bでは、次が実装・検証済みである。

```text
Host              : macOS／Apple Silicon arm64
Hardware          : Apple M2 Pro／16GB Unified Memory
Backend           : llama-cpp-python 0.3.34
Acceleration      : Metal
Model             : Qwen3-4B Q4_K_M／GGUF
Application       : Model Port経由
Deployment Config : TOML Profile
```

Model PortとAdapterの分離は成立しているが、現在の実装には次のmacOS／Metal固定点が残る。

- CLIのDefault Profileが`local_macos_arm64.toml`へ固定されている
- `gpu_offload`がModel固有のRequired Capabilityとして扱われている
- CPU Deploymentでは同じModelを使用できてもCapability不足として拒否される
- Runtime Device判定が実質`metal`または`cpu`である
- Environment VerificationとModel SmokeがDarwin／arm64／Metalを前提とする
- Native SetupがBash、POSIX Pathおよび`.venv/bin/`を前提とする

これらを放置したままUI、Audit、GovernanceおよびRemote Runtimeを積み上げると、Deployment固有条件が上位層へ伝播する可能性がある。

一方、Windows、CUDA、ROCm、Vulkan等をHardware未確定の段階ですべて実装すると、未検証ProfileとBuild Scriptが増え、将来の実機に合わず作り直す可能性が高い。

したがって、今は汎用境界だけを確定する。

## 3. macOSとCUDAの整理

CUDAは過去のIntel MacとNVIDIA GPUの組合せでは存在した。

NVIDIA CUDA 10.2はmacOSをSupportした最後のCUDA Toolkitであり、CUDA 11以降はmacOS上の開発・実行をSupportしない。

現在のApple Silicon MacではCUDAを使用できない。

現在のMac候補は次である。

- CPU
- Apple Accelerate
- Metal
- Metal Performance Shaders／PyTorch MPS
- MLX／MLX-LM
- Core ML／Apple Neural Engine
- VulkanからMetalへのTranslation Layer

現在のM2 Pro ProfileはMetalをPrimaryとする。

## 4. 表現対象となる独立軸

全組合せをFile名やClass名へ埋め込まない。次の軸を分離して表現する。

### 4.1 Host

- Operating System
- OS Version／Distribution
- CPU Architecture
- Native／WSL／VM／Container
- Host Identifier
- Headless／Desktop

### 4.2 Compute Device

- CPU
- Integrated GPU
- Discrete GPU
- Unified GPU
- NPU
- TPU
- HPU
- FPGA／ASIC
- Remote Accelerator

### 4.3 Vendor

- Apple
- NVIDIA
- AMD
- Intel
- Qualcomm
- Huawei
- Google
- AWS
- Moore Threads
- その他のVendor

Vendor値は閉じた列挙へ永久固定しない。

### 4.4 Acceleration API／Runtime

- CPU Native
- BLAS／OpenBLAS
- Apple Accelerate
- Metal／MPS
- CUDA
- HIP／ROCm
- Vulkan
- SYCL／oneAPI／XPU
- OpenVINO
- DirectML／WinML
- Core ML
- OpenCL
- CANN
- MUSA
- WebGPU
- RPC／Remote API
- Vendor Plugin

### 4.5 Memory Topology

- CPU RAM
- Unified Memory
- Shared Memory
- Discrete VRAM
- NUMA
- Multi-GPU
- Partial Offload
- Remote Memory

### 4.6 Backend Adapter

- llama.cpp／llama-cpp-python
- MLX／MLX-LM
- Transformers／PyTorch
- vLLM
- ONNX Runtime
- OpenVINO
- TensorRT／TensorRT-LLM
- Core ML
- Remote OpenAI-compatible API
- 将来Adapter

### 4.7 Model Artifact Variant

- GGUF
- Safetensors
- MLX形式
- ONNX
- OpenVINO IR
- TensorRT Engine
- Core ML Package
- Vendor Compile済みArtifact

同じLogical Modelに複数Artifact Variantを関連づけられること。

### 4.8 Execution Topology

- Same Process
- Same Host Service
- Localhost API
- LAN Home Server
- Remote GPU Server
- Cloud API
- Single Device
- Multi-GPU
- Multi-Node
- Hybrid

## 5. Required／Detected／Executedの分離

最低限、次の3種類を分離する。

```text
Required Capability
  Deploymentが成立するために必要な条件

Detected Capability
  Runtimeが実際に検出・申告した能力

Executed State
  当該Requestで実際に使用したDevice／Backend／Offload
```

例：

```text
Qwen3-4B Model Definition
  GPU Offloadを必須にしない

macOS Metal Deployment Profile
  gpu_offloadをRequiredとする

Windows CPU Deployment Profile
  gpu_offloadをRequiredとしない
```

Required Capability不足を黙って無視しない。

- 明示Error
- 許可されたFallback
- Degrade Warning
- Execution Refusal
- Audit Log記録

のいずれかへ解決する。

Phase 1-Cでは、許可されていない暗黙Fallbackを実装しない。

## 6. Functional Requirements

### P1C-REQ-001 Deployment固有要件の分離

Model Definition、Model Adapter、Deployment Requirementを分離する。

ModelがCPUで実行可能であるにもかかわらず、特定DeploymentのGPU要件によってModel全体が使用不能にならないこと。

### P1C-REQ-002 ProfileによるHost表現

Deployment Profileは少なくとも次を表現できること。

- OS
- Architecture
- Execution Environment
- Compute Device種別
- Vendor
- Acceleration API
- Backend Adapter
- Backend Build Variant
- Required Runtime Capability

### P1C-REQ-003 Identifierの拡張性

未知の将来Vendor、Acceleration API、BackendまたはDeviceを追加するとき、Application Coreの条件分岐を増殖させない。

安定した共通概念には型を使用してよいが、Vendor名やBackend名を全世界分の閉じたEnumとして固定しない。

識別子はRegistry追加可能なString Keyとして扱う。

### P1C-REQ-004 Profile Resolution

Profile選択Sourceを次の優先順位で解決できるHookを設ける。

```text
Explicit CLI／Application指定
  > Environment指定
  > Platform Default Resolver
```

未対応PlatformをmacOS Profileへ黙ってFallbackしない。

### P1C-REQ-005 Runtime Observation

Runtimeは可能な範囲で次を申告する。

- 実OS
- 実Architecture
- Backend Key／Version
- Build Variant
- Detected Device
- Acceleration API
- GPU Offload有無
- Device ID／Name（取得可能な場合）
- Memory Topology（取得可能な場合）

観測できない情報を推測で補完しない。

### P1C-REQ-006 Model Artifact分離

Logical ModelとArtifact Variantを分離できるHookを維持する。

初期版では現在のGGUFだけを使用するが、将来Safetensors、MLX、ONNX等を同じLogical Modelへ関連づけられる構造を妨げない。

### P1C-REQ-007 Pathの移植性

- Coreで`/`または`\\`へ依存しない
- Python内部は`pathlib`を使用する
- Tracked Configへユーザー固有絶対Pathを保存しない
- Model RootはEnvironmentまたは明示設定で差し替え可能とする
- Windows Symbolic Linkを必須にしない

### P1C-REQ-008 Verification State

設計済み、実装済み、実機検証済みを混同しない。

候補状態：

```text
defined
implemented
statically_verified
native_verified
unsupported
experimental
```

現在の正しい状態：

```text
macOS／Apple Silicon／Metal : native_verified
その他Platform             : definedまたはfuture
```

### P1C-REQ-009 Mac Regression

Phase 1-C実装後も次を維持する。

- Qwen3-4B Metal Load／Unload
- SHA-512常時検証
- Streaming
- Cooperative Cancel
- Thinking Control
- Context Overflow Policy
- Default Test
- Metal Model Smoke

### P1C-REQ-010 追加Dependency抑制

Phase 1-C Hookだけを理由にCUDA、ROCm、Vulkan、PyTorch、MLX、ONNX RuntimeまたはCloud SDKをInstallしない。

## 7. Phase 1-C Implementation Scope

### 実装対象

- Deployment／Platform／Computeを表す最小Contract
- Deployment RequirementとModel Capabilityの分離
- `gpu_offload`要件のmacOS Profile側への移動
- Profile Resolverの差し替え境界
- Runtime Observationの正規化Hook
- Mac Profile Migration
- Unit／Contract Test
- 既存macOS／Metal Regression

### 実装対象外

- Windows実Profile
- PowerShell Setup
- Windows Native Build
- Linux実Profile
- Docker
- CUDA Build
- ROCm／HIP Build
- Vulkan Build
- SYCL／OpenVINO Build
- MLX Adapter
- Transformers Adapter
- vLLM Adapter
- Remote API Adapter
- Multi-GPU実装
- Model Artifact変換
- 追加Model Download

## 8. 将来Profile候補

次は将来追加候補であり、Phase 1-Cの実装対象ではない。

```text
local.macos-arm64.metal
local.macos-arm64.cpu
local.windows-x86_64.cpu
local.windows-x86_64.cuda
local.windows-x86_64.vulkan
local.windows-x86_64.hip
local.linux-x86_64.cpu
local.linux-x86_64.cuda
local.linux-x86_64.rocm
local.linux-x86_64.vulkan
local.linux-x86_64.sycl
local.linux-arm64.cpu
home-server.linux.cuda
home-server.linux.rocm
remote.openai-compatible
cloud.vllm.cuda
cloud.vllm.rocm
cloud.aws-neuron
cloud.google-tpu
```

Hardware、OS、DriverおよびBackendを決定した時点で、必要なものだけを作成・検証する。

## 9. Acceptance Criteria

Phase 1-C HookのAcceptanceは次とする。

1. Model DefinitionからDeployment固有の`gpu_offload必須`が分離されている
2. macOS Metal Profileが`gpu_offload`を明示的に要求する
3. Required CapabilityとDetected Capabilityが比較される
4. 未対応Platformを暗黙にmacOS扱いしない
5. Profile ResolverがTest可能である
6. 将来のOS／Vendor／Acceleration Key追加にCore変更を必須としない
7. Tracked Configへユーザー固有絶対Pathを入れない
8. 既存Default Test、Static CheckおよびMetal Model SmokeがPassする
9. macOS以外を`native_verified`と誤記しない
10. Phase 2以降の機能へ越境しない

## 10. Authorization Boundary

本要件は設計判断の承認を記録する。

Source、Config、Test、Script、DependencyまたはRoot Fileの変更を自動的に許可しない。

実装担当は、専用Handoffを読み、ユーザーからPhase 1-C実装開始と必要なWrite Scopeを明示的に許可された後に作業する。

## 11. 外部参照

- NVIDIA CUDA 10.2 Release Notes: https://docs.nvidia.com/cuda/archive/10.2/pdf/CUDA_Toolkit_Release_Notes.pdf
- llama.cpp Build Documentation: https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
- llama-cpp-python README: https://github.com/abetlen/llama-cpp-python/blob/main/README.md
- PyTorch MPS Backend: https://docs.pytorch.org/docs/stable/notes/mps
- vLLM Installation: https://docs.vllm.ai/en/latest/getting_started/installation/index.html
- ONNX Runtime Execution Providers: https://onnxruntime.ai/docs/execution-providers/

