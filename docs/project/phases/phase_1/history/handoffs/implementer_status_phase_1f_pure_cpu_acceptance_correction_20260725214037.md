# Phase 1-F Pure CPU Acceptance Correction 実装者Status

- 文書ID: `implementer_status_phase_1f_pure_cpu_acceptance_correction`
- 状態: `repository_correction_completed_designer_review_pending`
- 作成日時: `2026-07-25 21:40:37 JST`
- 更新日時: `2026-07-25 21:40:37 JST`
- Snapshot: `20260725214037`
- 作成担当: 実装者役担当Task
- 対象Handoff: [designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md](designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md)
- Source Review: [designer_review_phase_1f_pure_cpu_repository_20260725212559.md](designer_review_phase_1f_pure_cpu_repository_20260725212559.md)

## 1. Result

Pure CPU Native AcceptanceのBlocking FindingをRepository内で修正した。

```text
Acceleration Match:
  CUDA GPU                : cuda
  CUDA Build CPU Execution: cpu_native
  Pure CPU Build          : none

Model Selection:
  Canonical Input : Model Root
  Artifact        : Registry Relative Path
  Compatibility   : Validated --model-path
  Download        : none
```

外部Lightning Environment、Dependency Install、Model配置、Native BuildおよびModel Generationは実行していない。

## 2. Changed Files

### Implementation

- `scripts/models/phase1f_cross_environment_acceptance.py`
- `scripts/setup/setup_lightning_linux_x86_64_cpu.sh`

### Test

- `tests/unit/inference/test_lightning_cpu_native_setup.py`
- `tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py`

### Status

- `docs/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md`

## 3. Acceleration Match Fix

Native Acceptance ScriptからCPU Runtimeの固定値：

```text
runtime.acceleration_api == "cpu_native"
```

を除去した。

`runtime_evidence_matches_profile()`をPure Functionとして抽出し、全Targetで次を共通確認する。

```text
runtime.acceleration_api
  == selected profile.compute.acceleration_api_key
```

GPU Profileでは併せて次を要求する。

- GPU Offload Supported
- GPU Offload Requested
- GPU Offload Observed
- Runtime GPU Offload True
- Device Kind GPU

CPU Profileでは次を要求する。

- GPU Offload Not Requested
- GPU Offload Not Observed
- Runtime GPU Offload False
- Device Kind CPU
- Profile Acceleration API一致

このため、次を正しく区別する。

```text
lightning_linux_x86_64_cuda.toml
  compute=gpu / acceleration=cuda

lightning_linux_x86_64_cpu.toml
  compute=cpu / acceleration=cpu_native

lightning_linux_x86_64_cpu_native.toml
  compute=cpu / acceleration=none
```

Profile不一致はFail Closedになる。

## 4. Model Root／Path Contract

### Canonical Option

Pure CPU Setupへ次を追加した。

```text
--model-root MODEL_ROOT
```

Setupは選択Registry：

```text
config/models/qwen3_4b_q4_k_m.toml
```

の`artifact.relative_path`を読み、次を解決する。

```text
MODEL_ROOT/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

`--model-smoke`選択時は、この解決結果が実FileでなければSetup／Build前にFail Closedにする。

Native Acceptance Scriptにも`--model-root`を追加し、同じ値をApplication Compositionへ渡す。Reportは実際に解決された`model_artifact_path`を記録する。

### Compatibility Option

既存`--model-path`は削除していない。

ただし任意Artifact Overrideではなく、次を満たすCompatibility Validationとして定義した。

- Registry Relative LayoutとSuffixが完全一致する。
- `--model-root`未指定時はValid PathからRootを導出する。
- `--model-root`併用時は、そのRootから解決したExpected Artifactと完全一致する。
- Layout不一致、Root不一致、改行を含むPathは拒否する。

指定FileとSmokeがLoadするFileが異なる状態を許可しない。

### Display

`--plan`と実Setupは次を表示する。

```text
Model Root
Resolved Artifact
Smoke Artifact
```

## 5. Updated User Commands

推奨手順：

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --plan \
  --model-root /absolute/path/to/model-root
```

Model配置後のBounded Smoke：

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --model-smoke \
  --model-root /absolute/path/to/model-root
```

Compatibility Optionを使う場合：

```bash
scripts/setup/setup_lightning_linux_x86_64_cpu.sh \
  --environment-mode auto \
  --model-smoke \
  --model-path /absolute/path/to/model-root/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Expected Layoutと一致しないPathは受理しない。

## 6. Automated Test

追加／更新した確認：

- CUDA GPU Profileと`cuda`一致
- CUDA Build CPU Profileと`cpu_native`一致
- Pure CPU Profileと`none`一致
- Profile／Runtime Acceleration不一致拒否
- Unknown Compute Kind拒否
- Pure CPU Fixtureで`all_required_checks_passed=True`
- False Checkを含む場合のFail Closed
- Model RootからRegistry Artifact解決
- Valid Compatibility `--model-path`
- Invalid Layout拒否
- Model Root／Path不一致拒否
- Smoke Artifact存在確認
- Specified ArtifactとAcceptanceへ渡すModel Root一致
- Existing `--model-path` Help維持
- Shell Syntax

## 7. Verification Result

```text
pytest              : 267 passed, 3 deselected
Ruff Check          : PASS
Ruff Format         : PASS／95 files
Mypy strict         : PASS／95 source files
uv lock --check     : PASS／122 packages
Shell Syntax        : PASS
```

`3 deselected`にはExternal Native／Model Smokeが含まれる。未実行をPassとは記録しない。

## 8. External Native Pending

次は未実施である。

- Lightning CPU Environment Reconstruction
- Pure CPU Native Build
- Actual Model SHA-512
- Model Load
- `runtime_evidence_matches_profile` Native Result
- Short Generation／Streaming／Cancel
- Memory／Latency
- Shutdown

Repository Correctionが設計ReviewでAcceptedとなった後、ユーザー実行Gateで確認する。

## 9. Known Limitations

- `--model-root`は選択RegistryのExpected Relative Layoutを必要とする。
- `--model-path`は任意File Overrideではない。
- Model Artifactを自動Download／移動／Uploadしない。
- External Native PerformanceとBuild時間は未測定である。
- Web UI、Profile設計、RAG、Git／GitHubは変更していない。

