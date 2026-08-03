# ADR-0022: Lightning Pure CPUとOptional Component Hook-only Profile

- 文書ID: `adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Requirements: [phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md](../requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md)
- Architecture: [phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md](../architecture/phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md)
- supersedes: なし

## Context

Current Lightning CPU Profileは`gpu_layers=0`でCPU実行するが、Backend Build VariantはCUDAである。Freshな最小CPU環境ではCUDA Toolkit／`nvcc`が存在しない可能性があり、CPU実行のためだけにCUDA Buildを要求する構成は再現性が低い。

また、Phase 1-ex後にProject Documentation Explainerの軽量RAGをMac実機へ追加する候補があるが、外部CPU Deploymentでは追加Index、Retrieval、Context、Model Callを既定で実行しない構成が必要である。

## Decision

### 1. Pure CPU Profileを分離する

```text
build variant : cpu
device        : cpu
acceleration  : none
gpu layers    : 0
```

を表すProfileを追加する。

### 2. CUDA Build CPU Executionを維持・識別する

Existing CPU Profileを無断削除せず、CUDA BuildをCPUで実行するProfileとして区別する。

### 3. Pure CPU SetupはCUDAを要求しない

GPU、NVIDIA Driver、CUDA Toolkit、`nvidia-smi`、`nvcc`を必須条件にしない。

### 4. Repository Hookを先に実装する

Profile、Setup、Preflight、Verification、TestはRepositoryで作成可能とする。外部Native実行は別Gateとし、未実行をPassにしない。

### 5. Project Documentation ExplainerはDeployment別にする

Phase 1-ex後：

```text
Mac Local:
  Optional implementation／enablement

Lightning CPU:
  Hook only
  enabled = false
  Provider／Index absent allowed
  No Retrieval／No Additional Model Call
```

同一Component Contractを使うが、Deployment ProfileごとにActivationとProvider Availabilityを分離する。

## Rationale

- CPU RuntimeがGPU Toolchainへ依存しなくなる。
- Build CapabilityとExecution Deviceを正しく表現できる。
- Fresh Environment再構築性が上がる。
- Optional RAG機能をCoreやCloud Deploymentへ強制しない。
- Macで研究機能を試しつつ、外部Demoを軽量に保てる。

## Rejected Alternatives

### Current CUDA Build CPU Profileだけを使う

却下。Fresh CPU環境でCUDA Toolchainがない場合に再構築できない。

### CPU環境でもCUDA ToolkitをInstallする

却下。不要なDependency、Build時間、Failure Surfaceを増やす。

### CPU Setup失敗時にCUDA Profileへ自動Fallbackする

却下。要求DeviceとObserved Runtimeが不明確になる。

### MacでRAGを実装したらLightningでも自動ON

却下。Optional ComponentのDeployment Independenceを失う。

### Lightning用にRAG CodeをForkする

却下。同一Contract＋Profileで表現でき、ForkはDriftを生む。

## Consequences

- ProfileとVerification Targetが一つ増える。
- `llama-cpp-python`のCPU Native Build Recipeが必要になる。
- CUDA CPU ExecutionとPure CPUのTest Matrixが増える。
- External Native Evidenceは利用可能時までPendingとなる。
- Project Documentation ExplainerはProfileごとにAvailability／Enabled Stateを表示する必要がある。

## Implementation Gate

Repository側Pure CPU Hookは実装担当へHandoff可能である。外部環境操作とRAG実装は本ADRだけでは許可しない。

