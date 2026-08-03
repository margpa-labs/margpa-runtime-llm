# Phase 1-F Lightning Pure CPU Runtime Follow-up 実装者Status

- 文書ID: `implementer_status_phase_1f_pure_cpu_runtime_follow_up`
- 状態: `repository_implementation_completed_external_native_validation_pending`
- 作成日時: `2026-07-25 20:35:08 JST`
- 更新日時: `2026-07-25 20:35:08 JST`
- Snapshot: `20260725203508`
- 作成担当: 実装者役担当Task
- 対象Handoff: [designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md](designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md)
- Preflight Addendum: [designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md](designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md)

## 1. Result

Lightning Linux x86_64向けPure CPU Repository Hookを実装した。

```text
Build Variant    : cpu
Execution Device : cpu
Acceleration API : none
GPU Layers       : 0
GPU Offload      : false
Fallback         : deny
```

外部Lightning Environment、Dependency Install、Native Build、Model配置、Model Generationは操作していない。External Native AcceptanceはPendingである。

## 2. Changed Files

### Profile／Runtime

- `config/profiles/lightning_linux_x86_64_cpu_native.toml`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py`

### Setup／Verification

- `scripts/setup/preflight_lightning_ai_studio.sh`
- `scripts/setup/setup_lightning_linux_x86_64_cpu.sh`
- `scripts/setup/verify_phase1_environment.py`

### Test

- `tests/unit/inference/test_config_and_registry.py`
- `tests/unit/inference/test_deployment_platform.py`
- `tests/unit/inference/test_lightning_cpu_native_setup.py`
- `tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py`

## 3. Existing CPU Profile Disposition

Existing Profile：

```text
config/profiles/lightning_linux_x86_64_cpu.toml
```

はRename／Delete／意味変更していない。

```text
Existing lightning_linux_x86_64_cpu.toml
  build : cuda
  run   : cpu

New lightning_linux_x86_64_cpu_native.toml
  build : cpu
  run   : cpu
```

CUDA Build CPU ExecutionとPure CPU Buildを別Profileとして維持する。

## 4. Pure CPU Build Detection

Runtime Detectionは、CPU Buildかつ`gpu_layers=0`の場合に次を返す。

```text
build_variant    : cpu
device_kind      : cpu
acceleration_api : none
gpu_offload      : false
```

CUDA Buildを`gpu_layers=0`で実行する場合は既存どおり次を維持する。

```text
build_variant    : cuda
device_kind      : cpu
acceleration_api : cpu_native
```

Setupは`llama-cpp-python==0.3.34`のBackend情報とGPU Offload Supportを確認し、Compatible Pure CPU BuildだけをReuseする。Missing／Mismatchまたは`--rebuild-native`時だけ、Accelerator BackendをOFFにしたSource Buildを実行する。

## 5. Preflight Decision

重複Scriptを追加せず、Existing：

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

を後方互換で拡張した。

Target：

```text
Default                     : cuda-gpu
--cpu-only                  : cuda-cpu
--runtime-target cuda-gpu   : CUDA Build／GPU Execution
--runtime-target cuda-cpu   : CUDA Build／CPU Execution
--runtime-target cpu-native : Pure CPU Build／CPU Execution
```

`--cpu-only`の意味をPure CPUへ変更していない。

CPU-native Preflightは次を確認する。

- Linux／x86_64／Ubuntu／Container
- Environment Mode
- Python 3.12.11
- uv 0.11.29とPath
- CPU Count
- Available Memory
- Project／Environment Path Read／Write条件
- Pure CPU Profile Parse／Locked Value
- Optional Model Root Presence

CPU-native経路で実行しないCommand：

```text
nvidia-smi
nvcc
CUDA Compiler
GPU Allocation Probe
```

## 6. Setup Behavior

`scripts/setup/setup_lightning_linux_x86_64_cpu.sh`は次を実装した。

- Python `>=3.12,<3.14`
- Project Venv／Studio Active Environment
- uv 0.11.29
- Frozen Lock確認
- Normal Dependency SyncとNative Rebuildの分離
- Compatible Pure CPU Build Reuse
- `--rebuild-native`
- `--plan`
- Explicit `--model-smoke`
- Explicit `--model-path`
- Missing Model時Fail Closed
- Model Downloadなし
- GPU／NVIDIA／CUDA Toolchain Commandなし
- Repeated Run可能

## 7. User-run Rebuild Procedure

Lightning CPU Environment上でProject Rootへ移動後、次の順に実行する。

### 1. Help

```bash
scripts/setup/preflight_lightning_ai_studio.sh --help
```

### 2. Read-only Preflight

```bash
scripts/setup/preflight_lightning_ai_studio.sh \
  --runtime-target cpu-native \
  --environment-mode auto
```

### 3. Setup Plan

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh --plan
```

### 4. Environment Setup

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto
```

既存Native Buildを無条件にReuseせず強制再構築する場合：

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --rebuild-native
```

### 5. Environment Verification

Target EnvironmentのPythonを使う。

```bash
python scripts/setup/verify_phase1_environment.py \
  --target lightning-cpu-native
```

### 6. Model Path確認

```bash
test -f /absolute/path/to/Qwen3-4B-Q4_K_M.gguf
```

不足時にScriptはDownloadしない。別Gateで配置する。

### 7. Bounded Smoke

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --model-smoke \
  --model-path /absolute/path/to/Qwen3-4B-Q4_K_M.gguf
```

Main Model一個、短いPrompt、Bounded Token、Single Generationの既存Acceptance Hookを使う。

### 8. Exit Code

```bash
echo $?
```

`0`以外はPassとして扱わず、標準Errorの不足条件を確認する。

## 8. Verification

Repository上の実行結果：

```text
pytest                    : 265 passed, 3 deselected
Ruff check                : passed
Ruff format --check       : passed
Mypy strict               : passed / 95 source files
uv lock --check           : passed / 122 packages
Shell syntax              : passed
CPU-native mocked preflight: passed
```

自動Testで確認したもの：

- Pure CPU Profile Parse／Locked Value
- Existing CUDA GPU／CUDA CPU Profile非Regression
- Pure CPU Build Observation
- `acceleration_api=none`
- `gpu_layers=0`
- Explicit Target Verification Fail Closed
- Preflight Default Compatibility
- `--cpu-only` Compatibility
- CPU-native GPU Command非実行
- Unknown Target拒否
- Target Conflict拒否
- Help表示
- Mac誤実行拒否
- Setup Plan
- Shell Syntax

## 9. External Native Test Pending

次は未実施であり、Passとは記録しない。

- Fresh Lightning CPU Setup
- Actual CPU Instruction Set
- Native Build時間
- Backend Import／System Info
- Actual Model SHA-512
- Model Load
- Short Generation
- Streaming／Cancel／Token Limit
- Japanese Response
- Memory／Latency
- Shutdown

## 10. Known Limitations

- PreflightのLightning基準PythonはObserved Environmentどおり3.12.11固定である。
- Setup自体は3.12／3.13を受理する。
- Pure CPU Build時間、Memory、Latencyは外部環境で未測定である。
- Model ArtifactはRepository外に必要であり、自動Downloadしない。
- Project Documentation Explainer／RAG Hookは本変更で実装していない。
- Public URL、Upload、Credential、Git／GitHub操作は実施していない。

