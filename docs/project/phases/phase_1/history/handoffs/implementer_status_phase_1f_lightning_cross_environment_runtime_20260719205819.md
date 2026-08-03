# 実装担当 Phase 1-F Lightning Cross-environment Runtime Status

- 文書ID: `implementer_status_phase_1f_lightning_cross_environment_runtime`
- 状態: `repository_implementation_complete_waiting_lightning_native_verification`
- 作成日時: `2026-07-19 20:58:19 JST`
- 更新日時: `2026-07-19 20:58:19 JST`
- Snapshot: `20260719205819`
- 作成担当: 実装担当Task
- 正本言語: 日本語
- Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- Acceptance Follow-up: [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)
- supersedes: なし（Phase 1-F Status系列の初回）

## 1. Authorization／Scope

ユーザーのPhase 1-F実装開始指示に基づき、Handoff記載ScopeのSource、Config、Lock、Tests、Scriptsを変更した。Acceptance Follow-upのCLI Help／Hidden Thinking Token上限Warningも同じMaterial Change Setで実装した。

README、Public Docs、Canonical Requirements／Architecture／ADR／Index、Git／GitHub、Backupは変更していない。`.python-version`は`3.13.14`のまま維持した。

## 2. Current State

```text
Repository Shared Changes       : Complete
Acceptance Follow-up            : Implemented／Mac Native Verified
Mac 3.13.14／Metal Regression   : Pass
Python 3.12／3.13 Lock Resolve  : Pass
Lightning 3.12.11／CUDA Native : Waiting External Execution
Lightning CPU Native            : Waiting External Execution
Phase 1-F Completion            : Not Claimed
```

## 3. Changed／Added Files

### Root／Config

- `pyproject.toml`
- `uv.lock`
- `config/platforms/platform_registry.toml`
- `config/profiles/lightning_linux_x86_64_cuda.toml`
- `config/profiles/lightning_linux_x86_64_cpu.toml`

### Source

- `src/margpa_runtime_llm/bootstrap/profile_resolver.py`
- `src/margpa_runtime_llm/modules/inference/contracts/runtime.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/runtime_detection.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py`
- `src/margpa_runtime_llm/entrypoints/cli/main.py`

### Scripts

- `scripts/setup/verify_phase1_environment.py`
- `scripts/setup/setup_lightning_linux_x86_64_cuda.sh`
- `scripts/models/phase1f_cross_environment_acceptance.py`

### Tests

- `tests/unit/inference/test_config_and_registry.py`
- `tests/unit/inference/test_deployment_platform.py`
- `tests/unit/inference/test_cli.py`
- `tests/integration/llama_cpp/test_phase1b_runtime.py`
- `tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py`

## 4. Implementation Summary

### Python／Lock

- `requires-python = ">=3.12,<3.14"`
- Ruff Targetを`py312`へ変更
- Mypy Python Versionを`3.12`へ変更
- Direct Dependency Pinは維持
- `uv.lock`を117 Packageで再生成
- Linux x86_64／Python 3.12.11とmacOS arm64／Python 3.13.14のDependency TreeをLockから解決確認

### Deployment／Detection

- Platform Registry Schemaを2へ更新
- Execution Environmentを`native／container`として独立管理
- Docker／OCI Marker、`container` Environment、Cgroup MarkerによるContainer検出
- Linux Distribution IDをHost Evidenceへ追加
- ProfileとDetected HostのOS／Architecture／Execution Environment／DistributionをPre-load照合
- Mac Default Profile Resolutionを維持
- Lightning CUDA／CPUはExplicit `--profile`のみとし、自動Fallbackを追加していない

### CUDA／CPU Runtime

- llama.cpp System Infoから`metal／cuda／cpu／unknown` Build Variantを分離
- `gpu_layers=0`はBuild Variantにかかわらず`cpu／cpu_native／gpu_offload=false`
- CUDA Build＋GPU Layersは`gpu／cuda／gpu_offload=true`
- Observed Build VariantをRuntime Info／Runtime Observationへ記録
- ProfileのBuild Variant、Device Kind、Acceleration API、Capability不一致はLoad後にUnloadしてSafe Failure
- CUDA ProfileがCPU Runtimeへ黙ってFallbackする経路をTestで拒否

### Setup／Evidence

- Lightning Ubuntu x86_64 Container／Python 3.12.11／uv 0.11.29のPreflight
- Normal Dependency Syncと`llama-cpp-python==0.3.34` CUDA Source Buildを分離
- Existing CUDA Build再利用と明示`--rebuild-native`
- `--cpu-only`でGPU未割当時にCUDA Build＋`gpu_layers=0`を検証可能
- Cross-environment Acceptance ProbeでSHA-512、Load、Generate、Non-stream、Stream、Cancel、Post-cancel、Language、Thinking、UnloadをEvidence化

### Acceptance Follow-up

- Top-level／`generate`／`model-info` Helpで大文字を仮引数名と明示
- `--profile`をSubcommand後へ置くことを明示
- 意味のあるMetavarとOption説明を追加
- Thinking Enabled、Hidden、Finalなし、`finish_reason=length`、Tagged Thinking Evidenceありの場合だけSafe Warningをstderrへ表示
- Warning Exit Codeは0
- Streaming／Non-streamingを同一判定
- Visible、Thinking Disabled、正常Final、Stop、Plain Empty、CancelでFalse PositiveしないUnit Testを追加

## 5. Mac Verification

Environment：

```text
Python             : CPython 3.13.14／GIL enabled
Host               : macOS arm64／native
Backend            : llama-cpp-python 0.3.34
Build Variant      : metal／observed
Device             : gpu／metal／gpu_offload=true
Model SHA-512      : f182f1d40606572d...26da0fe7e08bfceb
```

Commands／Results：

```text
ruff format --check .                         : Pass／70 files
ruff check .                                  : Pass
mypy                                           : Pass／70 source files
python -m compileall -q src scripts tests      : Pass
bash -n setup_macos + setup_lightning          : Pass
pytest -q                                      : 181 passed, 3 deselected
uv lock --check --offline                      : Pass／117 packages
verify_phase1_environment --target macos-metal : Pass
pytest -q -m model_smoke                       : 2 passed, 1 skipped, 181 deselected
phase1f_cross_environment_acceptance.py        : Pass
```

Cross-environment ProbeのMac実測：

```text
Load including SHA-512 : 2.4483 s
RSS before load        : 55,476,224 bytes
RSS after load         : 3,270,770,688 bytes
RSS after unload       : 176,816,128 bytes
Generate／Stream       : Pass
Cancel／Post-cancel    : Pass
Language／Thinking     : Pass
Unload                 : Pass
```

Metal TestはSandbox内ではMetal Deviceが公開されずCommand Queue作成に失敗したため、Mac実機Contextで再実行してPassした。Sandbox失敗はProduct Failure Evidenceへ数えない。

Hidden Thinking実Model Probe：

```text
Condition : Thinking enabled／hidden／max_new_tokens=8／length
stdout    : Reasoning非表示
stderr    : 最終回答を生成する前にToken上限へ到達しました。
Exit Code : 0
```

## 6. Lightning Execution Commands

ModelはDefinitionのRelative Pathと一致するPersistent Storageへ配置する。

```text
<MODEL_ROOT>/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

CUDA Mandatory Gate：

```bash
scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  --rebuild-native \
  --cuda-smoke \
  --model-path <MODEL_ROOT>/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

同じCUDA BuildによるCPU Candidate A：

```bash
scripts/setup/setup_lightning_linux_x86_64_cuda.sh \
  --cpu-only \
  --cpu-smoke \
  --model-path <MODEL_ROOT>/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
```

追加のPytest Native Entry：

```bash
MARGPA_MODEL_ROOT=<MODEL_ROOT> \
MARGPA_PHASE1F_PROFILE=config/profiles/lightning_linux_x86_64_cuda.toml \
.venv/bin/pytest -q -m model_smoke \
  tests/integration/llama_cpp/test_phase1f_cross_environment_runtime.py
```

CPUの場合はProfile Environmentを`lightning_linux_x86_64_cpu.toml`へ変更する。

## 7. Known Limitations／CPU Disposition

- Lightning外部環境のInstall、CUDA Build、Model配置、GPU利用は本Taskから実行していない。
- CUDA ProfileとCPU ProfileはEvidence取得前のため`verification_state = defined`であり、`native_verified`へ偽装していない。
- CPU Candidate AはRepository実装済みだがNative未確認である。
- GPU未割当時にCUDA-enabled `llama-cpp-python`をImport／Loadできない場合、失敗Evidenceを保存し、別CPU Build Environment案を設計者Reviewへ返す。
- `RuntimeObservation.executed`はCurrent Model Port Contractどおり`null`を維持する。Generation／Stop／CancelはAcceptance ProbeのResult Evidenceへ記録する。

## 8. Remaining Gate／Review Request

次はLightning上でSection 6を実行し、次を取得する。

1. Python 3.12.11 Dependency／Default Test
2. Container／Ubuntu Detection
3. CUDA Build Variant／System Info／GPU Observation
4. Qwen3-4B SHA-512一致
5. Generate／Stream／Non-stream／Cancel／Unload
6. Response Language／Thinking Presentation
7. CPU Candidate AのPassまたは明示Failure Evidence

Lightning Evidence受領後、新Timestampの後継`implementer_status_*`を作成してPhase 1-F Reviewを依頼する。現時点ではPhase 1-F完了を宣言しない。
