# Lightning AI Studio Cross-environment Architecture

- 文書ID: `lightning_ai_studio_cross_environment_architecture`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 20:07:11 JST`
- 更新日時: `2026-07-19 20:07:11 JST`
- Snapshot: `20260719200711`
- 作成担当: 設計者役担当Task
- 対象: Lightning AI Studio Linux x86_64 Container、CUDA／CPU Dual Runtime
- 正本言語: 日本語
- 要件: [lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md](../requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md)
- ADR: [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md)
- supersedes: `lightning_ai_studio_cross_environment_architecture_20260719112304.md`

## 1. Decision

第一外部開発／検証環境はLightning AI Studioのままとする。実Environment Observationに基づき、単一CUDA ProfileではなくCUDA／CPU Dual Profile Architectureへ具体化する。

```text
Shared Application Core
  ├─ Local Mac
  │    └─ macOS arm64／Metal Profile
  └─ Lightning AI Studio Container
       ├─ Linux x86_64／NVIDIA CUDA Profile
       └─ Linux x86_64／CPU Profile
```

GPU利用上限、未割当、Maintenance等を考慮してCPU Profileを用意する。ただし初期版では自動Fallbackせず、明示Profileで切り替える。

## 2. Stable Profile Identity

```text
lightning_linux_x86_64_cuda.toml
  external.lightning-linux-x86_64.cuda

lightning_linux_x86_64_cpu.toml
  external.lightning-linux-x86_64.cpu
```

Tesla T4、Xeon 8488C、Driver 580.159.03等はObserved Hardwareであり、Profile Identityではない。Lightningが別SKUを割り当てても、Contractを満たせば同じProfileを使用できる。

## 3. Current Gaps

### 3.1 Execution Environment

Current Platform Registryは`execution_environment_key = native`を単一値として持ち、`detect_host_platform`はOSとArchitectureだけをHost APIから検出する。

LightningはDocker Containerであるため、次が必要である。

```text
Execution Environment Detector
  ├─ native
  ├─ container
  ├─ wsl
  └─ future environment
```

ContainerをProfile上`native`として通す方法は採用しない。Audit／Experiment Evidenceの正確性を優先する。

### 3.2 CUDA Device Detection

Current `llama_cpp` Runtime Detectorは次のPhase 1規則である。

```text
Metal marker + GPU layers != 0 → metal／gpu
otherwise                      → cpu_native／cpu
```

CUDA BuildでGPU OffloadしてもMetal markerがないため、現状ではCPUとして誤分類される。Backend System Infoと実Load条件に基づくCUDA DetectionをAdapter内へ追加する。

### 3.3 Multiple Profiles for One Host

Current Registryは`OS + Architecture + Execution Environment`ごとにDefault Profileを1つだけ許す。Lightning CUDA／CPUは同じHost Keyを共有するため、Profile Fileを2つ作るだけでは自動選択できない。

初期解決：

```text
Explicit --profile
```

将来解決：

```text
Host Detection
  → Accelerator Observation
  → Eligible Profile Set
  → Explicit Policy／Fallback Chain
  → Selected Profile + Selection Evidence
```

## 4. Runtime Flow

```text
CLI／将来UI
  → Explicit Lightning CUDA／CPU Profile
  → Host + Container Detection
  → Pre-load Validation
  → llama.cpp Adapter
  → CUDA／CPU Runtime Detection
  → Post-load Capability Validation
  → Generation
  → Runtime Observation／Experiment Evidence
```

## 5. CPU Fallback Build Strategy

ProfileとNative Package Buildを別概念として扱う。

### Candidate A: One CUDA-enabled Environment

- CUDA Buildを保持する。
- CPU Profileは`gpu_layers = 0`を指定する。
- GPU Device未割当でもImport／CPU Load可能か実機確認する。

利点：再Buildなしで切替可能。

未確定点：CUDA Library／Driver／Deviceがない状態のImportとCPU実行。

### Candidate B: Separate Native Build Environment

- CUDA Build Environment
- CPU Build Environment

利点：各Backendの成立条件が明確。

欠点：Environment切替またはNative Package再Buildが必要。

初回検証ではCandidate Aを先に試し、成立しない場合だけCandidate Bへ進む。未検証の自動Package入替をRuntimeへ組み込まない。

## 6. Environment Evidence

Native Verificationは最低限次を保存する。

```text
Python Version
OS／Kernel／Distribution
Container State
CPU／RAM／Swap
GPU Name／VRAM
NVIDIA Driver
CUDA Runtime／Toolkit
llama-cpp-python Version
llama.cpp System Info
Backend Build Variant
Model Digest
Profile Digest
Detected／Executed Device
Latency／Token Usage／Stop Reason
```

## 7. Phase Placement

Dual Profileは将来のGovernance／UI／Audit Coreを作り直す変更ではない。Deployment／Adapter境界へ閉じ込める。

Phase 1はMac Native Runtime Snapshotとして先に確定する。Lightning Profile実装は外部環境対応Phaseで、Setup、Build、Native Smoke、Comparison Evidenceまでまとめて行う。

## 8. ZeroGPU

Hugging Face ZeroGPUを第一移植先にしないDecisionは維持する。GGUF／llama.cppのMacとLightning間の交換性を先に実証し、ZeroGPUはPyTorch／Transformers／Gradio Adapter追加の後続候補とする。

## 9. Security／External Boundary

- Lightning Credential、SSH Key、TokenをRepositoryへ保存しない。
- ModelをGitへCommitしない。
- 実会話Log、RAG資料、個人情報を自動Uploadしない。
- Public Port公開はUI／API Security要件成立後に行う。
- GPU利用、Package Install、Model Downloadは外部状態変更として個別許可を必要とする。
