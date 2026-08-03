# Lightning AI Studio Dual Runtime Profile要件

- 文書ID: `lightning_ai_studio_dual_runtime_profile_requirements`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 20:07:11 JST`
- 更新日時: `2026-07-19 20:07:11 JST`
- Snapshot: `20260719200711`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 対象: Lightning AI Studio Linux x86_64 Container、CUDA／CPU Profile
- 正本言語: 日本語
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719200711.md](../architecture/lightning_ai_studio_cross_environment_architecture_20260719200711.md)
- Handoff: [implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md](../handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md)
- supersedes: なし（新規Dual Profile要件系列）

## 1. Decision

Lightning AI Studioでは、GPU利用可能時とGPU利用上限到達／未割当時の両方を扱うため、次の2つのDeployment Profileを用意する。

```text
config/profiles/lightning_linux_x86_64_cuda.toml
config/profiles/lightning_linux_x86_64_cpu.toml
```

Profile Key候補：

```text
external.lightning-linux-x86_64.cuda
external.lightning-linux-x86_64.cpu
```

Tesla T4、Xeon 8488C等のHardware SKUはProfile名へ固定せず、Runtime Observation／Environment Reportへ記録する。

## 2. Confirmed Environment

```text
Service               : Lightning AI Studio
Operating System      : Ubuntu 24.04.4 LTS
Kernel                : Linux 6.8.0-1058-aws
Architecture          : x86_64
Execution Environment : Docker Container
Python                : 3.12.11
Logical CPU           : 4
Host RAM              : 15 GiB
Swap                  : 9 GiB
GPU                   : NVIDIA Tesla T4
GPU VRAM              : 15,360 MiB
Driver                : 580.159.03
CUDA Runtime          : 13.0
CUDA Toolkit／nvcc    : 13.0／V13.0.88
```

Python 3.12.11は、ProjectのPython 3.13.14 Primaryに対するNative Build互換性Fallback方針と整合する。環境差を隠さずEnvironment Reportへ記録する。

## 3. CUDA Profile Requirements

```text
host.os                    = linux
host.architecture          = x86_64
host.execution_environment = container
host.distribution          = ubuntu
compute.kind               = gpu
compute.vendor             = nvidia
compute.acceleration       = cuda
compute.memory_topology    = discrete
backend                    = llama_cpp
backend.build_variant      = cuda
load.gpu_layers            = -1
runtime.required_device    = gpu
runtime.required_api       = cuda
runtime.required_capability= gpu_offload
fallback                   = deny
```

Profile作成時の`verification_state`は`defined`とし、CUDA Build、Model Load、GPU Offload、Generation、Cancel、Unloadを実機で確認後にだけ`native_verified`の新しいProfileへ進める。

## 4. CPU Profile Requirements

```text
host.os                    = linux
host.architecture          = x86_64
host.execution_environment = container
host.distribution          = ubuntu
compute.kind               = cpu
compute.acceleration       = cpu_native
compute.memory_topology    = cpu_ram
backend                    = llama_cpp
load.gpu_layers            = 0
runtime.required_device    = cpu
runtime.required_api       = cpu_native
runtime.required_capability= none
fallback                   = deny
```

CPU Vendor／SKUはStudio割当により変化し得るため、ProfileへIntel Xeon 8488Cを固定しない。

CPU ProfileのBackend Build Variantは実機確認で次から決める。

1. CUDA-enabled Buildを`gpu_layers = 0`でGPU未割当時にもCPU実行できる場合、同一Environmentを再利用する。
2. CUDA Library／Device不在によりImportまたはLoadが失敗する場合、CPU Build用Environment／Setup Recipeを分離する。

未確認の段階で、同一CUDA BuildによるCPU Fallbackを保証しない。

## 5. Profile Selection

初期版は暗黙Fallbackを行わず、利用者が明示Profileを選択する。

```bash
./.venv/bin/margpa-llm model-info \
  --profile config/profiles/lightning_linux_x86_64_cuda.toml
```

```bash
./.venv/bin/margpa-llm model-info \
  --profile config/profiles/lightning_linux_x86_64_cpu.toml
```

理由：

- Current Platform Registryは同じHost Keyへ複数Defaultを登録できない。
- GPU Quota、GPU未割当、Driver異常、VRAM不足を同一の「CPUへFallback可能」と黙って解釈しない。
- Experiment再現性のため、使用ProfileとCompute Targetを明示する。

将来、Hardware ObservationとExplicit Fallback Chainが成立した後に`auto`選択を追加できる。

## 6. Required Runtime Follow-up

TOML追加だけでは不十分であり、次を同じ実装Scopeに含める。

1. Docker／Container Execution Environment検出
2. Linux x86_64 Container ProfileとのPre-load整合
3. llama.cpp CUDA BuildのRuntime Detection
4. CUDA実行とCPU実行の分離
5. CUDA／CPU Setup Recipe
6. Linux Environment Verification
7. CUDA／CPU Native Smoke Test
8. Profile、Registry、Reference Integrity Test

Current Device DetectorはMetal以外をCPUとして扱うため、CUDA判定を追加しない限りCUDA ProfileはPost-load Validationで拒否される。

## 7. Load Defaults

初期候補：

```text
threads       : 4
threads_batch : 4
context_size  : Application Default 4096
use_mmap      : true
use_mlock     : false
```

Batch／Micro BatchはMac値を無条件に固定せず、CUDA／CPU Smoke時のMemory、Latency、安定性を見て決める。Qwen3-4Bだけでなく将来Model交換を考慮し、GPU SKU固有最適値をProfileの永続的事実と混同しない。

## 8. Acceptance Criteria

- Containerを`native`と偽って記録しない。
- CUDA Profileは実際に`device_kind = gpu`、`acceleration_api = cuda`、`gpu_offload = true`を申告する。
- CPU Profileは`device_kind = cpu`、`acceleration_api = cpu_native`、`gpu_offload = false`を申告する。
- GPU未割当時にCUDA ProfileがCPUへ黙ってFallbackしない。
- CPU ProfileでQwen3-4BをLoad／Generate／Stream／Cancel／Unloadできる。
- Model Artifact SHA-512をMacと一致確認できる。
- Python、Driver、CUDA、Build Variant、Device、VRAM、RAMをEnvironment Evidenceへ記録する。
- Mac Metal Profileと既存Testを壊さない。

## 9. Phase Boundary

本設計は後続Core PhaseをBlockしない。Phase 1 Backup前に未検証Linux Profileを混入させず、Lightning対応Phaseで実装・Native検証する。

## 10. Authorization Boundary

本要件は設計Decisionを記録する。Config／Source／Tests／Setup Recipe変更、Lightning上のInstall、Build、Model Upload／Download、GPU利用は、ユーザーによる実装開始許可後に行う。
