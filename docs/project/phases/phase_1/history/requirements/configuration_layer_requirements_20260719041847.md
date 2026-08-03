# Configuration Layer 分離要件

- 文書ID: `configuration_layer_requirements`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- 作成担当: 設計者役担当Task
- 対象: Application Config、Model Definition、Deployment Profile、Platform Registry、Effective Config
- 正本言語: 日本語
- 上位要件: [project_requirements_20260718193435.md](project_requirements_20260718193435.md)
- Architecture: [configuration_layer_architecture_20260719041847.md](../architecture/configuration_layer_architecture_20260719041847.md)
- Accepted ADR: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- supersedes: なし（新規Configuration Layer専用Requirements系列）

## 1. 結論

Current `config/profiles/local_macos_arm64.toml`は、Application共通設定、Model選択、Storage、Generation、DeploymentおよびHardware Tuningを一つのFileへ混在させている。

Linux、Windows、Home ServerまたはCloud Profileを追加した場合、Platformと無関係な`max_new_tokens`、Language、Model Root等まで複製され、設定Driftが発生する。

Phase 1-D実装前に、Configを責務単位へ分離する。

```text
Application Config
Model Definition
Deployment Profile
Platform Registry
Environment／Explicit Override
        ↓
Typed Configuration Composer
        ↓
Effective Phase 1 Config
```

## 2. Required Directory Structure

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

Phase 1-Dでは、Generation／Responseごとの小Fileを量産しない。

将来複数Presetが必要になった場合は、次を追加可能とする。

```text
config/presets/
├─ generation/
└─ response/
```

## 3. Configuration Ownership

### 3.1 Application Config

`config/application.toml`はPlatformをまたいで共有するApplication Defaultを所有する。

- Application Key／Schema Version
- Selected Model
- Model Root
- Common Load Default
- Generation Default
- Response Policy Default

### 3.2 Model Definition

`config/models/*.toml`はModel ArtifactとModel固有事実を所有する。

- Model Key／Role
- Source／Revision
- Artifact Path／Hash／Format／Quantization
- Backend Compatibility
- Architecture
- Native Context Limit
- Chat Template Source
- Required／Optional Model Capability
- Provenance／Verification

Model DefinitionはCurrent Platform、Default Languageまたは利用者のGeneration Preferenceを所有しない。

### 3.3 Deployment Profile

`config/profiles/*.toml`はDeployment固有事実とHardware Tuningだけを所有する。

- Profile Key／Schema Version／Verification State
- Host OS／Architecture／Execution Environment
- Compute／Vendor／Acceleration／Memory Topology
- Backend Runtime／Build Variant／Execution Mode
- Runtime Requirements／Fallback Policy
- Hardware-dependent Load Override

Deployment ProfileはSelected Model、Model Root、Generation DefaultまたはResponse Languageを所有しない。

### 3.4 Platform Registry

`config/platforms/platform_registry.toml`は次だけを所有する。

- OS Alias
- Architecture Alias
- Platform Default Profile Path
- Registry Schema／Reference Integrity

Application Defaultを所有しない。

## 4. Field Placement

| Field | Owner | 備考 |
|---|---|---|
| `selected_model` | Application Config | Environment／CLIでOverride可能 |
| `model_root` | Application Config | Storage設定、Platformではない |
| `context_size` | Application Common Load Default | 必要時だけDeployment／CLI Override |
| `verify_artifact_hash` | Application Common Load Default | Integrity Policy |
| `verbose_backend` | Application Common Load Default | Diagnostic Default |
| `max_new_tokens` | Application Generation | Request Override可能 |
| Sampling値 | Application Generation | 将来Preset化可能 |
| `thinking_mode` | Application Generation | 表示Policyとは別 |
| `response.language` | Application Response | Phase 1-Dで`ja` Default |
| `host` | Deployment Profile | OS／Architecture等 |
| `compute` | Deployment Profile | GPU／CPU／Acceleration等 |
| `backend_runtime` | Deployment Profile | Build Variant等 |
| `runtime_requirements` | Deployment Profile | Current Deployment要求 |
| `batch_size` | Deployment Load Override | Hardware Tuning |
| `micro_batch_size` | Deployment Load Override | Hardware Tuning |
| `threads` | Deployment Load Override | Hardware Tuning |
| `threads_batch` | Deployment Load Override | Hardware Tuning |
| `gpu_layers` | Deployment Load Override | Hardware／Backend Tuning |
| `use_mmap` | Deployment Load Override | Host／Backend Tuning |
| `use_mlock` | Deployment Load Override | Host／Memory Tuning |
| Artifact SHA-512 | Model Definition | Artifact Identity |
| Native Context Limit | Model Definition | Model固有上限 |

## 5. Application Config Contract

初期概念形：

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

Tracked Fileでは再現性のため値を明示する。

## 6. Deployment Profile Contract

Migration後の概念形：

```toml
schema_version = "3"
profile_key = "local.macos-arm64"
verification_state = "native_verified"

[host]
...

[compute]
...

[backend_runtime]
...

[runtime_requirements]
...

[load_overrides]
batch_size = 256
micro_batch_size = 256
threads = 6
threads_batch = 6
gpu_layers = -1
use_mmap = true
use_mlock = false
```

`context_size`はApplication Defaultを使用する。特定Deploymentで異なる値が必要になった場合だけ`load_overrides.context_size`を許可する。

## 7. Schema Version

```text
Application Config Schema : 1
Deployment Profile Schema : 2 → 3
Model Definition Schema   : 1のまま
Platform Registry Schema  : 1のまま
```

Deployment Profile Version更新の理由は、Response追加ではなく、Application共通Fieldの除去と`load`から`load_overrides`への責務変更である。

## 8. Typed Composition

汎用的なDictionary Deep Mergeを禁止する。

理由：

- Typoが新しいFieldとして混入する
- Field Ownerが不明になる
- PlatformがApplication Policyを上書きできる
- List置換／結合規則が曖昧になる
- AuditでSourceを説明しにくい

Typed ContractとField Allowlistによって合成する。

```text
ModelLoadConfig
  = Built-in ModelLoad Default
  + Application load_defaults
  + Deployment load_overrides Allowlist
  + Environment Load Override
  + Explicit／CLI Load Override
```

GenerationとResponseにはDeployment Overrideを適用しない。

## 9. Resolution Precedence

### Model Selection／Model Root

```text
Explicit／CLI
  > Environment
  > Application Config
  > Built-in Default
```

### Load

```text
Explicit／CLI
  > Environment
  > Deployment Load Override
  > Application Common Load Default
  > Built-in Default
```

### Generation

```text
Per-request／CLI
  > Environment
  > Application Generation Default
  > Built-in Default
```

### Response Language

```text
Per-request／CLI
  > Environment
  > Application Response Default
  > Built-in Default
```

### Deployment Profile Selection

```text
Explicit Profile
  > Environment Profile
  > Platform Default Resolver
```

## 10. Source Tracking

Effective Configは、値だけでなくSourceを追跡可能にする。

最低限：

- `applied_sources`
- `profile_resolution_source`
- `response_language_source`

将来AuditではField単位のSource Mapへ拡張可能とする。

Phase 1-Dで全Fieldの詳細Provenance Engineは実装しない。

## 11. Functional Requirements

### CR-1 Application Config Loader

`config/application.toml`をStrict Validationで読み込む。

- Unknown Field拒否
- Unknown Schema拒否
- Unsafe Model Root拒否
- Unknown Language拒否
- Generation／Load値Validation

### CR-2 Deployment Profile Loader

Migration後のSchema `3`を読み込む。

- Application FieldをProfileへ書いた場合はUnknown Fieldとして拒否
- `load_overrides`以外の任意Deep Mergeを許可しない
- Hardware Override FieldをAllowlistで制限する

### CR-3 Effective Config Composer

Application Config、Model Definition、Deployment Profile、EnvironmentおよびExplicit Overrideから既存`EffectivePhase1Config`相当を生成する。

### CR-4 Compatibility Validation

- Selected Model BackendとDeployment Backendの整合を確認する
- Context SizeがModel Native Limitを超えないことを確認可能にする
- Deployment Runtime RequirementをPre-load／Post-loadで維持する
- Unknown／Incompatibleを黙ってFallbackしない

### CR-5 CLI Compatibility

既存CLI操作を維持する。

- `--model-root`
- `--model-key`
- `--context-size`
- `--profile`
- Generation Override
- `model-info`

### CR-6 Observability

`model-info`でApplication ConfigとDeployment Profileが別Sourceであることを確認できるようにする。

最低限：

```text
application_key
selected_model
profile_key
profile_resolution_source
load
generation
response
applied_sources
```

## 12. Non-functional Requirements

- 新規外部Dependencyを追加しない
- Application CoreへmacOS固有処理を追加しない
- Model AdapterへConfig合成を追加しない
- Config Loader／Composerを実ModelなしでUnit Test可能にする
- Existing Native Metal RuntimeをRegressionさせない
- Config File Hashを実装担当Statusへ記録する
- Tracked ConfigへUser固有Absolute Pathを記載しない

## 13. Scope外

- Multiple Application Config Selector UI
- Remote Config Service
- Dynamic Config Reload
- Secret Manager
- User／Session Preference Storage
- Generic Plugin Config
- Arbitrary Deep Merge
- 全FieldのField-level Provenance Log
- Windows／Linux実Profile
- Generation Preset Directory実装
- Response Preset Directory実装
- Phase 1-E Thinking Presentation

## 14. Required Tests

### Loader

- Application Config Schema `1`
- Deployment Profile Schema `3`
- Unknown Field拒否
- Old Mixed ProfileをCurrentとして受理しない
- Unsafe Path拒否

### Ownership

- Application ConfigがSelected Model／Model Root／Generation／Responseを持つ
- Deployment Profileがこれらを持たない
- Deployment ProfileがHardware Load Overrideを持つ
- Model DefinitionがArtifact／Capabilityを維持する

### Composition

- 共通Default継承
- Deployment Hardware Override
- Environment Override
- CLI Override
- Field別Precedence
- Invalid Override Safe Error
- Unknown PlatformのNo Fallback

### Regression

- Static Gate
- Default pytest
- Environment／Lock／Offline Gate
- `model-info`
- Load／Generate／Stream／Cancel／Unload
- Metal Smoke
- Artifact Hash Verification

## 15. Acceptance Criteria

1. `config/application.toml`が追加される
2. Application Config Schema `1`がStrict Validationされる
3. Deployment Profile Schemaが`3`になる
4. Platform ProfileからApplication共通Fieldが除かれる
5. `load_overrides`がHardware Fieldだけを受理する
6. GenerationとResponseがPlatform Profileへ複製されない
7. Typed ComposerがEffective Configを生成する
8. Field別PrecedenceがTestされる
9. Model／Deployment Backend整合Validationが維持される
10. Existing CLIがRegressionしない
11. Current Mac／Metal RuntimeがRegressionしない
12. 新規外部Dependencyがない

## 16. Authorization Boundary

本Requirementsはユーザー承認済みのConfiguration Layer分離を記録する。

Source、Config、TestまたはScriptの変更は、ユーザーからPhase 1-D実装開始の明示許可を得た後に行う。
