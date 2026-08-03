# Lightning AI Studio Cross-environment Architecture

- 文書ID: `lightning_ai_studio_cross_environment_architecture`
- 状態: `current_approved_phase_1f`
- 作成日時: `2026-07-19 20:23:33 JST`
- 更新日時: `2026-07-19 20:23:33 JST`
- Snapshot: `20260719202333`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-F、Mac Metal／Lightning CUDA／CPU
- 正本言語: 日本語
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- supersedes: `lightning_ai_studio_cross_environment_architecture_20260719200711.md`

## 1. Phase 1-F Architecture

```text
Shared Repository
├─ Application Core                    Python >=3.12,<3.14
├─ Shared Model Definition             Qwen3-4B GGUF／SHA-512
├─ Shared llama.cpp Model Port
├─ Shared Config／Language／Thinking
│
├─ Mac Deployment
│  ├─ Python 3.13.14
│  ├─ macOS arm64 Native
│  ├─ llama.cpp Metal Build
│  └─ local_macos_arm64.toml
│
└─ Lightning Deployment
   ├─ Python 3.12.11
   ├─ Ubuntu 24.04 x86_64 Container
   ├─ llama.cpp CUDA Build
   ├─ lightning_linux_x86_64_cuda.toml
   └─ lightning_linux_x86_64_cpu.toml
```

Python Minor、OS、Architecture、Execution Environment、Build Variant、Compute Targetを独立したEvidenceとして扱う。

## 2. Compatibility Strategy

- `requires-python`はSupport Rangeを表す。
- `.python-version`はLocal Defaultを表し、Support Rangeそのものではない。
- Lockは両Python Versionを解決する。
- Static Toolは最小Support 3.12を基準にし、3.13専用Syntaxの混入を防ぐ。
- Native Dependency BuildはPlatform Recipeへ分離する。
- Environment VerifierはCommon ContractとPlatform固有Contractへ分ける。

## 3. Deployment Selection

```text
Mac:
  Platform Default Resolver
    → local_macos_arm64.toml

Lightning:
  Explicit --profile
    → lightning_linux_x86_64_cuda.toml
    or lightning_linux_x86_64_cpu.toml
```

同一Linux Host上のCUDA／CPU自動選択はPhase 1-Fで行わない。利用ProfileをExperiment／Logへ明示できる方式を優先する。

## 4. Detection Changes

### Execution Environment

OS／Architectureに加えてContainerを検出し、Lightningを`container`としてPre-load Validationする。

### Acceleration

Metal専用規則を次へ拡張する。

```text
Observed Metal execution → gpu／metal
Observed CUDA execution  → gpu／cuda
gpu_layers = 0           → cpu／cpu_native
Unknown／Conflicting      → Safe Failureまたは明示Warning
```

System Info文字列だけへ過剰依存せず、Backend Capability、Load Config、利用可能なObserved Evidenceを組み合わせる。推測値をObserved値として記録しない。

## 5. Native Package Strategy

```text
Mac        : llama-cpp-python 0.3.34 Metal Build
Lightning  : llama-cpp-python 0.3.34 CUDA Build
```

CPU ProfileはまずCUDA Build＋`gpu_layers=0`を試す。GPU未割当時にCUDA Buildが成立しない場合、CPU Buildを別Environment／Recipeへ分離する。

通常Dependency SyncとNative Package Buildを分け、毎回CUDA Source Buildを強制しない。

## 6. Evidence Matrix

| Contract | Mac | Lightning CUDA | Lightning CPU |
|---|---|---|---|
| Python | 3.13.14 | 3.12.11 | 3.12.11 |
| OS／Arch | macOS arm64 | Linux x86_64 | Linux x86_64 |
| Execution Env | native | container | container |
| API | metal | cuda | cpu_native |
| GPU Offload | true | true | false |
| Required for Phase 1-F | yes | yes | preferred／conditional |

## 7. Publication Meaning

Phase 1公開物はPortable CLI Runtime Source、Config、Docs、Tests、Setup手順である。Model Binaryと実会話Logを含めない。

GitHub URLによるSource公開と、Lightning PortによるLive Web Application公開を分離する。Current Phase 1-Fは前者を対象とし、後者はWeb UI／API／Security成立後とする。

## 8. Failure Policy

- GPU未割当時のCUDA Profile: Safe Failure
- Explicit CPU Profile: CPU実行を試行
- CUDAからCPUへの暗黙Fallback: 禁止
- Python Version不一致: Install／Sync前に明示Error
- Model Hash不一致: Load拒否
- Profile／Detected Host不一致: Pre-load拒否

## 9. Phase Boundary

Phase 1-FはPortable RuntimeのCross-environment実証であり、Phase 2 UI、Phase 3 Audit、Phase 4 Governanceの責務を先取りしない。
