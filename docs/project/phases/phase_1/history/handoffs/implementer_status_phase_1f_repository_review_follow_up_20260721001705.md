# 実装担当 Phase 1-F Repository Review Follow-up Status

- 文書ID: `implementer_status_phase_1f_repository_review_follow_up`
- 状態: `repository_review_follow_up_complete_waiting_designer_review`
- 作成日時: `2026-07-21 00:17:05 JST`
- 更新日時: `2026-07-21 00:17:05 JST`
- Snapshot: `20260721001705`
- 作成担当: 実装担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260720235113.md](../documentation_index_20260720235113.md)
- Review: [designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md](designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md)
- Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- supersedes: `implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md`

## 1. Authorization／Scope

ユーザーの「最新のIndexとReviewを読んで作業」指示に基づき、Phase 1-F Repository ReviewのHigh 2件、Medium 2件、Low 1件へ対応した。

変更範囲は`src/`、`tests/`、`scripts/`および本Implementer Statusだけである。Canonical Requirements／Architecture／Governance／ADR／Index／Review、Config、Root File、Phase 1-G、Git／GitHub、Backup、Lightning外部環境は変更していない。

## 2. Current State

```text
Phase 1-F Repository Review Follow-up : Complete
Default Test／Lint／Type Check         : Pass
Mac Metal Native Regression           : Pass
Strict Acceptance on Mac Metal        : Pass
Lightning Target Preflight            : Waiting External Execution
Lightning CUDA／CPU Native Gate       : Waiting External Execution
Phase 1-F Completion                  : Not Claimed
Phase 1-G                             : Not Started／Not Authorized
```

## 3. Changed／Added Files

### Source

- `src/margpa_runtime_llm/modules/inference/contracts/runtime.py`
- `src/margpa_runtime_llm/modules/inference/public.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py`
- `src/margpa_runtime_llm/bootstrap/profile_resolver.py`

### Scripts

- `scripts/setup/verify_phase1_environment.py`
- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`
- `scripts/setup/preflight_lightning_ai_studio.sh`（新規）
- `scripts/models/phase1f_cross_environment_acceptance.py`

### Tests

- `tests/contract/model_port/test_model_port_contract.py`
- `tests/unit/inference/test_deployment_platform.py`
- `tests/unit/inference/test_llama_cpp_boundary.py`
- `tests/unit/inference/test_cli.py`
- `tests/integration/llama_cpp/test_phase1b_runtime.py`
- `tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py`

## 4. Review Finding対応

### 4.1 High: CUDA Build CapabilityとActual GPU Offload Evidenceの分離

`GpuOffloadEvidence`を追加し、次を独立記録する。

```text
supported                : Native Backendが対象BuildでGPU Offload可能か
requested                : gpu_layersによりGPU Offloadを要求したか
observed                 : Load後にActual GPU利用を観測したか
observation_source       : 証拠Source
process_gpu_memory_bytes : CUDA時のCurrent Process GPU Memory
```

- MetalはModel／Context Load成功後の`metal_model_load`をActual Evidenceとする
- CUDAはModel Load後に`nvidia-smi --query-compute-apps=pid,used_gpu_memory`を実行し、Current PIDのGPU Memoryが正値の場合だけ`observed=true`とする
- CUDA Build／GPU要求があってもCurrent Process Memoryを確認できなければ`gpu_offload=false`、`device_kind=unknown`としてFail Closedとする
- `CapabilityFeature.GPU_OFFLOAD`はProduction AdapterでActual Observation成功時だけ公開する
- CPU ProfileはCUDA Build Capabilityと`requested=false／observed=false`を分離する
- Pre-load Environment VerifierはActual GPU利用を主張せず、`gpu_offload_observed=null／requires_native_model_load`と記録する

### 4.2 High: Acceptance ProbeのFail-closed化

- 全必須条件をBooleanの`required_checks`へ集約
- `all_required_checks_passed = all(required_checks.values())`
- 1件でもFalseなら`success=false`かつProcess Exit Code 1
- 予期しない例外もSafe Errorだけを返してExit Code 1
- Integration Testは`success`、`all_required_checks_passed`、全`required_checks`を明示Assert
- Lightning Setupは`set -euo pipefail`によりProbeのNon-zeroを成功扱いしない

### 4.3 High／Medium: Language／Thinking Acceptance Evidence

- 日本語、英語、Streaming、Post-cancelに言語識別可能な別Markerを使用
- 日本語／英語のResolved Policyを別々に確認
- 各Policyに対応するSystem Message本文が実際の先頭System Messageへ注入されたことを確認
- Thinkingは`max_new_tokens=1024`へ拡張し、`finish_reason != length`を必須化
- `ThinkingParseStatus.COMPLETE`、Reasoning Segment、Final Segment、Final Markerを別々に必須化
- Hiddenは表示ContentがFinal ContentだけでCanonical Thinking Tagを含まないことを確認
- Visibleは`<高度推論>...</高度推論>`Label、Reasoning、Finalの分離を確認
- Unclosed ReasoningのSafe処理は既存Unit Testで別途維持し、Native Acceptance成功条件には数えない

### 4.4 Medium: Lightning Environment Mode

Lightning TargetでProject Venvだけを仮定しないよう、次を追加した。

```text
auto           : VIRTUAL_ENV／CONDA_PREFIX検出時はstudio-active、なければproject-venv
studio-active  : StudioのPersistent Active Environmentを直接使用
project-venv   : Project Local Venvを明示使用
```

- `scripts/setup/preflight_lightning_ai_studio.sh`はProject／Modelの大容量Upload前に単独実行できるRead-only Probe
- PreflightはHost、Container、Python 3.12.11、uv 0.11.29、Active Prefix、GPU Allocationを確認
- Environment作成、Package Install、Source Buildは行わない
- Full Setupは選択ModeとTarget Prefixを出力する
- Studio Active Prefixへ`uv sync`する場合は`--inexact`でStudio既存Packageを破壊しない
- Mac `.venv`は転送も再利用もしない

### 4.5 Low: `nvcc`判定順

- Dependency Sync前にTarget Python内の既存CUDA Buildを確認
- 既存CUDA Buildが有効で`--rebuild-native`未指定なら`nvcc`なしで再利用
- `nvcc`はNative CUDA Rebuildが実際に必要な場合だけ必須
- `--cpu-only`でもCUDA Buildが存在しなければRebuild用`nvcc`を要求する
- Build後にCUDA MarkerとGPU Offload Capabilityを再検証し、不一致はFail Closed

## 5. Verification

### Static／Default

```text
ruff format --check src scripts tests : Pass／70 files
ruff check src scripts tests          : Pass
mypy src + Phase 1-F Python Scripts   : Pass／54 source files
pytest -q                             : 183 passed, 3 deselected
bash -n Lightning Setup／Preflight    : Pass
Setup／Preflight --help               : Pass
```

### Mac Native Regression

```text
pytest -q -m model_smoke tests/integration
Result: 2 passed, 1 skipped, 1 deselected
```

Sandbox内ではMetal Command Queue作成が拒否されたため、Mac実機Contextで再実行してPassした。失敗位置は本変更のRuntime Evidence生成前であり、Sandbox外では同一TestがPassしている。

### Strict Phase 1-F Acceptance on Mac Metal

```text
success                         : true
all_required_checks_passed      : true
required_checks                 : 22／22 true
GPU Evidence                    : supported／requested／observed = true
GPU Observation Source          : metal_model_load
Japanese／English Marker        : Pass
Stream／Cancel／Post-cancel      : Pass
Thinking Parse                  : complete
Thinking Finish                 : stop
Thinking Reasoning              : 896 chars
Thinking Final                  : 15 chars
Hidden／Visible Separation      : Pass
Unload                          : Pass
Load including SHA-512          : 2.5276 s
RSS before／after／unload        : 55,656,448／3,265,462,272／177,225,728 bytes
```

## 6. Lightning Next Gate

最初に小さいPreflight ScriptだけをTargetへ配置して実行する。

```bash
scripts/setup/preflight_lightning_ai_studio.sh --environment-mode auto
```

GPU未割当でCPU Candidateだけを調べる場合：

```bash
scripts/setup/preflight_lightning_ai_studio.sh \
  --environment-mode auto \
  --cpu-only
```

Preflightで選択されたModeをFull Setupへ明示する。例：

```bash
scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  --environment-mode studio-active \
  --cuda-smoke \
  --model-path <MODEL_ROOT>/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

Project VenvがTargetで利用可能な場合：

```bash
scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  --environment-mode project-venv \
  --venv .venv \
  --cuda-smoke \
  --model-path <MODEL_ROOT>/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

`--rebuild-native`は明示的な再Build時だけ付与する。既存CUDA Buildがなければ、OptionなしでもSetupがRebuildを選択してその時点で`nvcc`を確認する。

## 7. Remaining／Review Request

- Lightning Target Preflightは未実行
- Lightning Python 3.12.11 Dependency Syncは未実行
- CUDA Source Build／既存Build再利用は未実行
- CUDA Current Process GPU Memory Evidenceは未取得
- Lightning CUDA／CPU Native Acceptanceは未実行
- Phase 1-F完了は宣言しない

設計者役は本Follow-upをReviewし、Pass後にLightning Preflight／Upload／Native Gateへ進めるか判定する。Phase 1-Gへは進まない。
