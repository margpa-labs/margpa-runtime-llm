# Configuration Layer Architecture

- 文書ID: `configuration_layer_architecture`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- 作成担当: 設計者役担当Task
- 対象: Application Config、Deployment Profile、Model Definition、Typed Composition
- 正本言語: 日本語
- Requirements: [configuration_layer_requirements_20260719041847.md](../requirements/configuration_layer_requirements_20260719041847.md)
- Accepted ADR: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- 関連Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- supersedes: なし（新規Configuration Layer専用Architecture系列）

## 1. Architecture Conclusion

Configurationを「Fileを順番にDeep Mergeする仕組み」ではなく、「責務別の型付き入力をComposition Rootで合成する仕組み」として実装する。

```text
config/application.toml
        │
        ├─ Application Default
        ├─ Selected Model
        ├─ Storage
        ├─ Common Load Default
        ├─ Generation
        └─ Response
        │
        ├──────────────┐
        ↓              ↓
Model Definition   Deployment Profile ← Platform Registry
        │              │
        └──────┬───────┘
               ↓
      Typed Config Composer
               ↓
      EffectivePhase1Config
               ↓
       Phase1Application
```

## 2. Why Current Mixed Profile Is Unsuitable

Current `local_macos_arm64.toml`は次を同時に所有する。

- `selected_model`
- `model_root`
- `load`
- `generation`
- Platform／Compute／Backend／Runtime Requirement

Phase 1-D設計案では、さらに`response.language`を追加する予定だった。

この状態でLinux Profileを追加すると、Platformと無関係な設定が複製される。

```text
local_macos_arm64.toml
  max_new_tokens = 512
  language = ja

local_linux_x86_64_cuda.toml
  max_new_tokens = 512
  language = ja
```

片方だけを変更した場合、同じApplicationでPlatformによって回答Policyが変わるConfiguration Driftが発生する。

## 3. Target Structure

```text
config/
├─ application.toml
├─ models/
│    └─ qwen3_4b_q4_k_m.toml
├─ profiles/
│    └─ local_macos_arm64.toml
└─ platforms/
     └─ platform_registry.toml
```

Directory名`profiles/`は当面維持するが、文書とContract上の意味はDeployment Profileに限定する。

## 4. Domain Objects

### 4.1 `ApplicationConfig`

候補Location：

```text
src/margpa_runtime_llm/bootstrap/config_loader.py
```

概念形：

```python
class ApplicationConfig(BaseModel):
    schema_version: Literal["1"]
    application_key: str
    selected_model: str
    model_root: ModelRootConfig
    load_defaults: CommonLoadDefaults
    generation: GenerationParameters
    response: ResponsePolicyConfig
```

### 4.2 `DeploymentProfile`

Current `Phase1Profile`を責務に合わせて`DeploymentProfile`相当へ整理する。

概念形：

```python
class DeploymentProfile(BaseModel):
    schema_version: Literal["3"]
    profile_key: str
    verification_state: DeploymentVerificationState
    host: HostPlatformDefinition
    compute: ComputeTargetDefinition
    backend_runtime: BackendRuntimeDefinition
    runtime_requirements: DeploymentRequirements
    load_overrides: DeploymentLoadOverrides
```

### 4.3 `DeploymentLoadOverrides`

全Field Optionalの型付きAllowlistとする。

```python
class DeploymentLoadOverrides(ImmutableContract):
    context_size: int | None = None
    batch_size: int | None = None
    micro_batch_size: int | None = None
    threads: int | None = None
    threads_batch: int | None = None
    gpu_layers: int | None = None
    use_mmap: bool | None = None
    use_mlock: bool | None = None
```

次をDeployment Overrideへ含めない。

```text
verbose_backend
verify_artifact_hash
generation
response
selected_model
model_root
```

### 4.4 `EffectivePhase1Config`

既存名称は維持してよい。

```python
class EffectivePhase1Config(ImmutableContract):
    application_key: str
    profile_key: str
    selected_model: str
    ...
    model_root: Path
    load: ModelLoadConfig
    generation: GenerationParameters
    response: ResolvedResponseLanguagePolicy
    profile_resolution_source: ...
    applied_sources: tuple[str, ...]
```

Effective Configは合成結果であり、Source Fileと一対一ではない。

## 5. File Contracts

### 5.1 `config/application.toml`

```toml
schema_version = "1"
application_key = "default"
selected_model = "main.qwen3-4b-q4-k-m"

[model_root]
default = "./models"
environment_variable = "MARGPA_MODEL_ROOT"

[load_defaults]
context_size = 4096
verbose_backend = false
verify_artifact_hash = true

[generation]
max_new_tokens = 512
temperature = 0.7
top_p = 0.8
top_k = 20
min_p = 0.0
presence_penalty = 1.5
frequency_penalty = 0.0
repeat_penalty = 1.0
stop_sequences = []
thinking_mode = "disabled"

[response]
language = "ja"
```

### 5.2 `config/profiles/local_macos_arm64.toml`

```toml
schema_version = "3"
profile_key = "local.macos-arm64"
verification_state = "native_verified"

[host]
operating_system_key = "macos"
architecture_key = "arm64"
execution_environment_key = "native"

[compute]
compute_kind_key = "gpu"
vendor_key = "apple"
acceleration_api_key = "metal"
memory_topology_key = "unified"
device_selector = "auto"
offload_policy_key = "full_or_backend_auto"

[backend_runtime]
backend_key = "llama_cpp"
required_version = "0.3.34"
build_variant_key = "metal"
execution_mode_key = "in_process"

[runtime_requirements]
required_capabilities = ["gpu_offload"]
required_device_kind = "gpu"
required_acceleration_api = "metal"
fallback_policy = "deny"

[load_overrides]
batch_size = 256
micro_batch_size = 256
threads = 6
threads_batch = 6
gpu_layers = -1
use_mmap = true
use_mlock = false
```

## 6. Composition Algorithm

### 6.1 Load Inputs

```text
Application Config
Selected Model Definition
Resolved Deployment Profile
Environment
Explicit Overrides
```

### 6.2 Validate Independently

各Fileを別ContractでValidationする。

```text
Application Config Validation
Model Definition Validation
Deployment Profile Validation
Platform Registry Reference Validation
```

一つの巨大Schemaで全FileをValidationしない。

### 6.3 Compose by Field Owner

```text
selected_model
  Application → Environment → Explicit

model_root
  Application → Environment → Explicit

load
  Built-in → Application Defaults → Deployment Overrides
           → Environment → Explicit

generation
  Built-in → Application Defaults → Environment → Request／CLI

response
  Built-in → Application Defaults → Environment → Request／CLI

deployment
  Resolved Deployment Profile
```

### 6.4 Cross-object Validation

独立Validation後、次を検証する。

- `selected_model`とModel Definition Key一致
- Model BackendとDeployment Backend一致
- Required Version／Build Variant整合
- Effective Context SizeとModel Native Limit
- Deployment Required CapabilityとRuntime Capability
- Detected HostとExpected Host

## 7. No Generic Deep Merge

次の実装を避ける。

```python
effective = deep_merge(
    built_in,
    application_toml,
    model_toml,
    deployment_toml,
    environment,
    cli,
)
```

理由：

- `response.language`をDeploymentが上書きできる
- `required_capabilities`のList規則が不明
- `None`、未指定、削除の意味が曖昧
- Configuration Provenanceを説明できない
- Typoが通りやすい

代わりに、Sectionごとの明示関数を使う。

概念形：

```python
load = resolve_load_config(...)
generation = resolve_generation_config(...)
response = resolve_response_policy(...)
```

## 8. Bootstrap Flow

```text
load_application_config(config/application.toml)
        ↓
resolve_profile_path(Explicit > Environment > Platform Default)
        ↓
load_deployment_profile(resolved path)
        ↓
resolve selected_model(Application > Environment > CLI)
        ↓
load_model_definition(registry path)
        ↓
compose_effective_config(...)
        ↓
validate_preload_deployment(...)
        ↓
Model Load
        ↓
validate_loaded_deployment(...)
```

Platform検出前にApplication Configを読んでも、Application ConfigはPlatform固有値を含まない。

## 9. Existing Override Compatibility

次を維持する。

```text
MARGPA_MODEL_ROOT
MARGPA_MODEL_KEY
MARGPA_CONTEXT_SIZE
MARGPA_MAX_NEW_TOKENS
MARGPA_TEMPERATURE
MARGPA_TOP_P
MARGPA_TOP_K
MARGPA_MIN_P
MARGPA_PRESENCE_PENALTY
MARGPA_FREQUENCY_PENALTY
MARGPA_REPEAT_PENALTY
MARGPA_THINKING_MODE
MARGPA_PROFILE
```

Phase 1-Dで追加：

```text
MARGPA_RESPONSE_LANGUAGE
```

既存CLI Overrideも維持する。

## 10. Config Path

Initial Application Configの正本Path：

```text
config/application.toml
```

Composition RootではPathを引数として注入可能にし、Unit TestでTemporary Configを使用できるようにする。

Phase 1-Dでは`--application-config`またはRemote Config選択UIを必須にしない。

## 11. Observability

`model-info`はEffective Configだけでなく構成要素の識別子を示す。

```json
{
  "effective_config": {
    "application_key": "default",
    "profile_key": "local.macos-arm64",
    "selected_model": "main.qwen3-4b-q4-k-m",
    "load": {},
    "generation": {},
    "response": {},
    "applied_sources": []
  }
}
```

将来Auditでは次のHashを別々に記録する。

- Application Config Hash
- Model Definition Hash
- Deployment Profile Hash
- Platform Registry Hash
- Effective Config Canonical Hash

Phase 1-D実装担当Statusでは、少なくとも変更したTracked ConfigのHashを記録する。

## 12. Model Exchange

Modelを交換する場合、Deployment Profileを編集しない。

```text
Application selected_model変更
  または
MARGPA_MODEL_KEY／--model-key Override
```

選択ModelとDeployment Backend／Capabilityが非互換なら、明示Errorとする。

将来、Cloud用ModelとLocal用Modelを自動選択するRoutingは別機能である。

## 13. Platform Addition

Linux Profile追加時：

```text
追加するもの:
  config/profiles/local_linux_x86_64_cuda.toml
  Platform Registry Entry
  必要なSetup／Test

複製しないもの:
  selected_model
  model_root
  generation
  response.language
```

Hardware Tuningだけを新Profileで指定する。

## 14. Future Preset Hook

Application Configが巨大化した場合、次へ分離可能とする。

```text
config/application.toml
  generation_profile = "balanced"
  response_profile = "default_ja"

config/presets/generation/balanced.toml
config/presets/response/default_ja.toml
```

Phase 1-Dでは実装しない。現在は一つのApplication Configを正本とする。

## 15. Candidate File Changes

```text
config/application.toml                              # New
config/profiles/local_macos_arm64.toml               # Schema 3 Migration
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/entrypoints/cli/main.py
src/margpa_runtime_llm/modules/inference/contracts/response.py
src/margpa_runtime_llm/orchestration/response_language.py
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_response_language.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
```

`config/models/qwen3_4b_q4_k_m.toml`とPlatform Registryは、参照整合Test以外で原則変更不要である。

## 16. Migration Sequence

1. Current Effective ConfigをTest Fixtureで固定する
2. Application Config Contract／Loaderを追加する
3. Deployment Profile ContractをSchema `3`へ追加する
4. Typed Composerを実装する
5. `config/application.toml`を追加する
6. Current Mac ProfileをMigrationする
7. Existing Environment／CLI Overrideを接続する
8. Cross-object Validationを維持する
9. Phase 1-D Response Policyを接続する
10. Static／Default／Native Regressionを実行する

## 17. Acceptance Mapping

| Requirement | Architecture Evidence |
|---|---|
| Common Config | `config/application.toml` |
| Platform分離 | `DeploymentProfile` |
| Hardware Override | `DeploymentLoadOverrides` |
| No Deep Merge | Section Resolver |
| Model独立 | Model Definition別読込 |
| Platform追加 | Generation／Response非複製 |
| Traceability | Application／Profile Key、Hash Hook |
| Regression | Existing Effective Config Fixture＋Native Test |

## 18. Authorization Boundary

本ArchitectureはAccepted Decisionである。

Source／Config／Test変更はPhase 1-D実装許可後に実装担当が行う。
