# Phase 1-F Lightning Pure CPU Runtime Follow-up Architecture

- 文書ID: `phase_1f_lightning_pure_cpu_runtime_follow_up_architecture`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md](../requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md)
- supersedes: なし

## 1. Architecture Goal

```text
Same Application Core
  ├─ macOS／arm64／Metal
  ├─ Linux／x86_64／CUDA
  ├─ Linux／x86_64／CUDA Build CPU Execution
  └─ Linux／x86_64／Pure CPU
```

Build Capability、Configured Device、Observed Deviceを分離する。

## 2. Profile Separation

### Existing

```text
lightning_linux_x86_64_cuda.toml
  build : cuda
  run   : gpu

lightning_linux_x86_64_cpu.toml
  build : cuda
  run   : cpu
```

### New

```text
lightning_linux_x86_64_cpu_native.toml
  build : cpu
  run   : cpu
```

Existing Profileを無断Rename／Deleteしない。MigrationはReference確認後に別Changeとする。

## 3. Backend Build Identity

Runtime Observation候補：

```text
build_variant_key       : cpu
build_variant_source    : observed／declared
device_kind_key         : cpu
acceleration_api_key    : none
gpu_offload             : false
```

CPU Buildで`llama_supports_gpu_offload()`等がFalseでもFailureとしない。Pure CPU ProfileではGPU OffloadをRequired Capabilityにしない。

## 4. Setup Flow

```text
Preflight
  ↓
Python／uv決定
  ↓
Application Dependency Sync
  ↓
llama-cpp-python CPU Build確認
  ├─ Compatible Existing Build → Reuse
  └─ Missing／Mismatch → Explicit CPU Rebuild
  ↓
Environment Verification
  ↓
Optional Bounded Model Smoke
```

Normal SyncとNative Rebuildを別Optionにする。

## 5. CPU Build Verification

少なくとも次を確認する。

- Package Version
- Native System Info
- CUDA／Metal Marker不在または非Required
- GPU Offload Unsupported／Disabled
- Import Success
- CPU Execution

単なる`gpu_layers=0`だけでPure CPU Buildと判定しない。

## 6. Verification Target

Current `lightning-cpu`はCUDA Build CPU Executionを意味するため、新Target候補を追加する。

```text
lightning-cpu-native
```

VerificationはProfileとBackend Observationの両方を照合する。

## 7. Optional Component Hook

Deployment Profileは将来のOptional Component設定をCoreへHard-codeしない。

Project Documentation Explainerが後から追加された場合：

```text
Local Mac:
  enabled = selectable
  provider = lightweight local retriever

Lightning CPU:
  enabled = false
  provider = none allowed
```

OFF時はComponent Registry／Config Schema Hookだけ存在できる。Index、Retriever、Corpus、追加Model CallをLoadしない。

## 8. Model Storage

Logical Layout：

```text
workspace/
├─ margpa-runtime-llm/
│  └─ models -> ../models/margpa-runtime-llm/models
└─ models/
   └─ margpa-runtime-llm/
      └─ models/
```

SymlinkはEnvironment-localでGit対象外とする。Canonical Resolutionは`MARGPA_MODEL_ROOT`で可能にする。

## 9. Expected Change

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
scripts/setup/preflight_lightning_ai_studio.sh
scripts/setup/verify_phase1_environment.py
config／profile contracts if required
tests/unit/
tests/integration/
docs/handoffs/implementer_status_phase_1f_pure_cpu_*
```

Keep Stable：

```text
Mac Metal Profile
CUDA GPU Profile
Model Port
Conversation／Web UI
RAG
Model Artifact
```

## 10. External Gate

Repository Testでは次を証明できない。

- Actual Studio Persistence
- Actual CPU Instruction Set
- Native Build Time
- Model Latency
- Public Port

これらを`native_validation_pending`として記録する。

## 11. Failure Policy

- CPU ProfileでCUDAを暗黙要求しない。
- CPU Build不可時にCUDA ProfileへFallbackしない。
- Model不足時にDownloadを自動開始しない。
- RAG Provider不足時、Component OFFなら正常、ONなら明示Errorとする。
- Unsupported Architectureを黙って受理しない。

