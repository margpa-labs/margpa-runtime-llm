# Lightning AI Studio Cross-environment Architecture

- 文書ID: `lightning_ai_studio_cross_environment_architecture`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: Phase 2-D External Linux／CUDA Development and Verification
- 正本言語: 日本語
- 上位要件: [post_phase_1e_research_platform_requirements_20260719112304.md](../requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
- 関連ADR: [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../documentation_index_20260719112304.md)
- supersedes: なし（新規Architecture系列）

## 1. Decision

Macと並行して開発／検証する第一外部環境として`Lightning AI Studio`を採用する。

Hugging Face ZeroGPUは却下しないが、現行GGUF／llama.cpp Runtimeの第一移植先にはせず、Phase 10の公開Demo／Backend交換性検証へ延期する。

## 2. 利用目的

- macOS／Apple Silicon／Metal以外の第二Native Environmentを持つ。
- Linux x86_64／NVIDIA CUDAで現行Repositoryを実行する。
- Model Port／Deployment Profile／Capability抽象の交換性を実証する。
- MacとGPU Serverの開発・検証を並行で行う。
- 将来のHome Server、AWS、Azure、vLLMへの移行リスクを下げる。

## 3. Deployment Topology

```text
Shared Repository／Application Core
  ├─ Local Mac Profile
  │    ├─ macOS arm64
  │    ├─ Apple M2 Pro／16GB
  │    ├─ llama.cpp／Metal
  │    └─ External Model Symlink
  │
  └─ Lightning AI Studio Profile
       ├─ Linux x86_64
       ├─ NVIDIA GPU／CUDA
       ├─ llama.cpp／CUDA
       ├─ Persistent Workspace
       ├─ SSH／VS Code
       └─ Port Exposure
```

Application Core、Model Contract、Config Composer、Experiment Contract、Audit Contractを共有し、差分をDeployment／Platform／Acceleration Adapterに閉じ込める。

## 4. Shared and Environment-specific Responsibilities

| 項目 | Shared | Mac | Lightning |
|---|---|---|---|
| Application Config | Yes | - | - |
| Model Registry | Yes | - | - |
| Model Port | Yes | - | - |
| GGUF Model Family | Yes | Local Path | Studio Path |
| Platform Registry Contract | Yes | macOS arm64 Entry | Linux x86_64 Entry |
| Deployment Profile Contract | Yes | Metal Profile | CUDA Profile |
| llama-cpp-python Version Policy | Yes | Metal Build | CUDA Build |
| Test Contract | Yes | Native Metal Gate | Native CUDA Gate |
| Model Artifact | Git対象外 | External Root | Persistent Storage |
| Secret | Git対象外 | Local Env | Studio Secret／Env |

## 5. Deployment Profile Candidate

実装時の正式KeyはPhase 2-Dで現行Schemaと整合させる。概念上は次を表現する。

```toml
schema_version = 3
profile_key = "external.lightning-linux-x86_64-cuda"

[platform]
os = "linux"
architecture = "x86_64"

[backend]
adapter = "llama_cpp"
acceleration = "cuda"

[runtime_requirements]
gpu_required = true
cuda_required = true

[load_overrides]
gpu_layers = -1
```

Model、Response Language、Generation Default、Common Context SizeはApplication ConfigのOwnerであり、Lightning Profileに重複記載しない。

## 6. Platform Registry Candidate

```text
platform_id          : linux-x86_64-nvidia-cuda
operating_system     : linux
architecture         : x86_64
accelerator_family   : nvidia_cuda
backend_capabilities : llama_cpp, gguf, cuda_offload
verification_state   : unverified → native_verified
default_profile      : external.lightning-linux-x86_64-cuda
```

GPU Model、VRAM、CUDA Runtime、DriverはRuntime Observationで記録し、Platform IDをGPU SKUごとに無制限増殖させない。必要なCapability／LimitとObserved Hardwareを分離する。

## 7. Environment Setup Strategy

### 7.1 Repository

- 同一Git RepositoryをClone／Pullする。
- Lightning専用Forkを通常運用の正本にしない。
- Platform固有修正はAdapter、Profile、Setup Recipeへ限定する。

### 7.2 Python

- 第一候補はProject正本のPython 3.13.14とする。
- Native Build／CUDA Dependencyに問題がある場合のFallbackはPython 3.12とする。
- Python Version差を黙って許容せず、Experiment RunとEnvironment Reportに記録する。

### 7.3 Dependency

- `uv.lock`を第一の再現性Sourceとする。
- `llama-cpp-python`のCUDA BuildはMetal Buildと別のSetup Recipeにする。
- 通常SyncとNative Package再Buildを分離する。
- CUDA Toolkit／DriverはEnvironment-owned DependencyとしてVersionを記録する。

## 8. Model Artifact Strategy

- GGUF ModelをGit RepositoryにCommitしない。
- LightningのPersistent Storageまたは明示的Download Recipeで配置する。
- Local Macと同じLogical Model IDを使う。
- EnvironmentごとのPhysical PathはModel Root／Artifact Resolverで解決する。
- Model File名は現行の原名称を使い、Registry Aliasで整理する。
- SHA-512でArtifact Identityを確認する。

初期Main Model：

```text
Logical Role : main
Model        : Qwen3 4B GGUF
Artifact     : Qwen3-4B-Q4_K_M.gguf
```

Guard／Judge ModelはそのPhaseまで常駐・Downloadを必須にしない。

## 9. Native Verification Gate

### 9.1 Common Gate

- Static Format／Lint／Type
- Unit Test
- Config／Registry Contract
- Model Artifact Hash
- Model Load／Generate／Stream／Cancel／Unload
- Response Language
- Thinking Contract（Phase 1-E後）
- Effective Config／Source表示

### 9.2 Lightning-specific Gate

- OS = Linux／Architecture = x86_64
- NVIDIA GPU Observation
- CUDA Runtime／Driver Observation
- llama.cpp CUDA Capability
- GPU Offload Observation
- Pre-load／Post-load Validation
- GPU Memory不足時のSafe Failure
- Port Exposure（API／UI実装後）

### 9.3 Comparison Record

```text
same repository revision
same model digest
same application config digest
deployment profile digest
platform observation
backend build metadata
seed
input
output
tokens
latency
tokens_per_second
stop_reason
warnings
```

浮動小数点差やBackend差によりOutputのByte-for-byte一致が保証できない場合は、Contract一致、Determinism Level、メタデータ一致を分けて評価する。

## 10. Development Workflow

```text
Design／Docs
  → Shared Repository
  → Mac Unit／Native Metal Verification
  → Lightning Unit／Native CUDA Verification
  → Cross-environment Comparison Record
  → Implementer Status
  → Designer Review
```

MacとLightningで別々に未管理の修正を進めない。環境固有の発見は共通Test／Contract／Profileへ戻す。

## 11. Port Exposure

API／UI実装後のPort公開はDeployment Adapterの責務とする。

- Application CoreはLightning固有URLを知らない。
- Bind Host／Port／Public VisibilityはDeployment Configで管理する。
- Public Access時はAuthentication、Secret、Logの個人情報、Rate Limitを別途要件化する。
- Phase 2-DではCLI中心でもよく、UI公開を受入必須にしない。

## 12. ZeroGPUとの工数比較

### 12.1 Lightning AI Studio

現行Architectureと共通化できるもの：

- Python Repository
- GGUF Model
- llama.cpp Backend
- CLI／将来のFastAPI
- Config／Deployment Profile
- Unit／Integration Test
- SSH／VS Codeによる通常開発

主な追加工事：

- Linux／CUDA Profile
- CUDA Native Build Recipe
- Artifact Placement
- Environment Verification

### 12.2 Hugging Face ZeroGPU

現行GGUF／llama.cpp Runtimeとの間に追加で必要になる可能性が高いもの：

- Gradio Application Adapter
- PyTorch／Transformers／Safetensors Model Adapter
- `@spaces.GPU`を使うGPU Lifecycle適応
- ZeroGPUのPython Version／Runtime制約対応
- GPU Allocation時間・Quota・Queueへの対応
- GGUFとは別のModel Artifact／Tokenizer／Chat Template

この工事はBackend交換性の実証としては価値があるが、「Macと外部Serverで同じRepositoryをすぐ検証する」目的に対してはLightningより大きい。

## 13. Official References

- [Hugging Face ZeroGPU documentation](https://huggingface.co/docs/hub/main/en/spaces-zerogpu)
- [Lightning AI Studio overview](https://lightning.ai/docs/overview/ai-studio/)
- [Connect a local IDE to Lightning Studio](https://lightning.ai/docs/platform/build/ai-studio/connect-local-ide)
- [Lightning SDK Studio documentation](https://lightning.ai/docs/overview/sdk/studio)

外部Serviceの仕様、料金、Quota、Python Version、GPUは変更され得る。Phase 2-D実装開始時に公式情報を再確認する。

## 14. Secret／Data Boundary

- Lightning Credential、Token、SSH KeyをRepositoryへ保存しない。
- 実会話Log、個人情報、RAG資料を自動Uploadしない。
- 公開PortへAudit Log／Config Source／Filesystem Pathを無制限に露出しない。
- Model LicenseとDefinition LicenseのCloud利用／再配布条件を確認する。

## 15. Failure／Degraded Scenario

| Scenario | Expected Behavior |
|---|---|
| GPUが割り当てられない | Capability Mismatch、Load前にSafe Failure |
| CUDA Buildでないllama-cpp-python | Post-install／Pre-load Validationで検出 |
| Model未配置 | Artifact Missing、Downloadを自動実行しない |
| Model Digest不一致 | Load Refusal |
| VRAM不足 | Errorを構造化、CPU FallbackはProfileが許可する場合のみ |
| Studio Restart | Persistent Storageから再開、Environment Verification再実行 |
| Port公開失敗 | CLI／Testは継続可能 |

## 16. Acceptance Criteria

1. 同一Repository RevisionがMacとLightningで動作する。
2. Application CoreにLightning／CUDA固有分岐を入れない。
3. Linux x86_64／CUDAがPlatform Registry／Deployment Profileで解決される。
4. llama.cppのCUDA CapabilityとGPU OffloadをObservationで確認できる。
5. 同一Model Digest／Application ConfigでCommon Contract TestがPassする。
6. Environment DifferenceをRun Recordで追跡できる。
7. Model／Secret／実LogがGitに入らない。
8. Lightning固有障害がMac Runtimeの設計を壊さない。

## 17. 未決事項

- 第一GPU SKU／VRAM
- StudioのPersistenceとCostの運用方針
- Python 3.13.14のNative Build検証結果
- CUDA Toolkit／Driverの正本Version Range
- LightningでのModel Root正本Path
- Setup Recipeの完全自動化範囲
- Phase 4後のPort／Authentication

## 18. Authorization Boundary

本ArchitectureはAcceptedであるが、Lightning Account操作、Studio作成、GPU課金、Model Upload／Download、Source／Config／Script実装は未解禁である。
