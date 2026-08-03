# Phase 1-D Response Language Policy 要件定義

- 文書ID: `phase_1d_response_language_requirements`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-D、Configuration Layer分離、Response Language、Prompt Composition、CLI
- 正本言語: 日本語
- Configuration Requirements: [configuration_layer_requirements_20260719041847.md](configuration_layer_requirements_20260719041847.md)
- Architecture: [phase_1d_response_language_architecture_20260719041847.md](../architecture/phase_1d_response_language_architecture_20260719041847.md)
- Accepted ADR: [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
- Amendment ADR: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- supersedes: `phase_1d_response_language_requirements_20260719040237.md`

## 1. 結論

Phase 1-Dは次の二つを同じMigration単位で実施する。

1. Application共通設定とDeployment Profileの責務分離
2. `ja／en／auto` Response Language Policy

Response LanguageはPlatform固有設定ではないため、`local_macos_arm64.toml`へ追加しない。

```text
config/application.toml
  └─ [response]
       language = "ja"
```

## 2. 前版からの変更

前版の次を修正する。

```text
Old:
  local_macos_arm64.tomlへ[response]を追加
  Response追加を理由にProfile Schema 3へ更新

New:
  config/application.tomlへ[response]を追加
  Application Config Schemaを1で新設
  Deployment Profileは共通Field分離を理由にSchema 3へ更新
```

次は維持する。

- Allowed `ja／en／auto`
- Default `ja`
- Application／Orchestration Ownership
- Explicit > Environment > Application > Built-in
- System Message Composition
- Natural-language Classifierを実装しない
- Phase 1-E Thinking Presentationとの分離

## 3. Phase 1-D Scope

### Configuration Layer

- `config/application.toml`
- `ApplicationConfig` Contract／Loader
- `DeploymentProfile` Schema `3`
- Application共通FieldのProfileからの除去
- Typed Effective Config Composer
- Field別Precedence
- Config Source表示

### Response Language

- `ResponseLanguage`: `ja／en／auto`
- Built-in／Application Default `ja`
- `MARGPA_RESPONSE_LANGUAGE`
- `--response-language`
- Effective Policy／Source
- System Message Composer
- Streaming／Non-streaming Parity

## 4. Configuration Ownership

### `config/application.toml`

- `selected_model`
- `model_root`
- Common `load_defaults`
- `generation`
- `response`

### `config/profiles/local_macos_arm64.toml`

- Host
- Compute
- Backend Runtime
- Runtime Requirements
- Hardware `load_overrides`
- Verification State

### `config/models/qwen3_4b_q4_k_m.toml`

- Artifact／Hash／Quantization
- Model Architecture／Native Limit
- Model Capability／Provenance

## 5. Application Config

Phase 1-DのTracked Default：

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

## 6. Response Language Contract

```text
ja   : 日本語を既定とする
en   : 英語を既定とする
auto : ApplicationからLanguage Instructionを追加しない
```

- 未知値を拒否する
- `jp`等を`ja`へ黙ってAlias変換しない
- Phase 1-DでBCP 47全対応を実装しない
- `auto`はLanguage Classifierではない

## 7. DefaultとOverride

```text
Per-request／CLI Explicit
  > MARGPA_RESPONSE_LANGUAGE
  > Application Config [response]
  > Built-in Default ja
```

Deployment ProfileはResponse LanguageをOverrideできない。

Phase 2以降にSession／User Preferenceを追加可能とする。

## 8. System Message Composition

Language PolicyはApplication／Orchestration層でSystem InstructionへCompileする。

### `ja`

```text
回答は原則として日本語で行ってください。
ユーザーが回答言語を明示的に指定した場合は、その指定を優先してください。
```

### `en`

```text
Respond in English by default.
If the user explicitly requests a different response language, follow that request.
```

### `auto`

Language Instructionを追加しない。

要件：

- User Promptを変更しない
- User指定System Messageを破棄しない
- Project PolicyとUser Systemを決定論的に合成する
- CLIと将来APIで同じComposerを使う
- Model AdapterへLanguage文言を置かない

## 9. Structured PolicyとNatural Language

Phase 1-DはDefault Languageを指定する機能であり、Strict Output Enforcementではない。

User Prompt内の「英語で」「日本語で」等をApplicationで解析しない。Default Instructionを通じてModelがUserの明示指定へ従えるようにする。

Applied PolicyとObserved Output Languageを同一視しない。

## 10. Deployment Profile Migration

Current ProfileをSchema `3`へMigrationする。

削除：

```text
selected_model
model_root
generation
loadの共通Field
```

維持：

```text
profile_key
verification_state
host
compute
backend_runtime
runtime_requirements
```

追加／変更：

```text
[load] → [load_overrides]
Hardware Tuning Fieldだけ
```

## 11. Typed Composition

Generic Deep Mergeは禁止する。

```text
Load:
  Explicit > Environment > Deployment Override
           > Application Default > Built-in

Generation:
  Request > Environment > Application > Built-in

Response:
  Request > Environment > Application > Built-in
```

DeploymentはGenerationとResponseを変更できない。

## 12. Observability

`model-info`で最低限次を確認可能にする。

```text
application_key
profile_key
selected_model
load
generation
response.language
response.source
profile_resolution_source
applied_sources
```

## 13. Existing Behavior Preservation

- Model Load／Unload
- Generate／Streaming／Cancel
- Thinking実行On／Off
- Generation Override
- Profile Resolution
- Deployment Validation
- Artifact SHA-512
- `model-info`
- Current Mac／Metal Runtime

## 14. Phase 1-E Scope外

- `<think>`表示／非表示
- Thinking Label
- Model Protocol Parser
- Streaming Thinking Filter
- Raw／Display Output分離
- Raw Thinking保存
- Thinking Sampling Profile
- High-Level Explanation

## 15. その他Scope外

- Language Detection Classifier
- Translation
- Session／User Preference Storage
- Web UI／API
- Multiple Application Config Selector
- Generation／Response Preset Directory
- Dynamic Reload
- Remote Config
- New External Dependency
- Windows／Linux実Profile

## 16. Required Tests

### Configuration

- Application Schema `1`
- Deployment Schema `3`
- Ownership違反Field拒否
- Typed Load Composition
- Field別Precedence
- Selected Model／Deployment Backend整合
- Migration前後のEffective値一致

### Language

- `ja／en／auto`
- Unknown拒否
- Application Default `ja`
- Environment／CLI Override
- Source Tracking
- 6つのMessage Composition Case
- User Prompt／System保持
- Streaming／Non-streaming Parity

### Regression

- Ruff Format／Check
- Mypy Strict
- Default pytest
- Environment Verification
- Bash Syntax
- `uv lock --check`
- Exact Offline Dry Run
- Metal Smoke
- Default `ja`／Explicit `en`／`auto` Native Smoke

## 17. Acceptance Criteria

1. `config/application.toml`が共通正本になる
2. Application Config Schema `1`がStrict Validationされる
3. Deployment Profile Schema `3`がStrict Validationされる
4. Platform Profileから共通Fieldが除かれる
5. Typed ComposerがEffective Configを生成する
6. PlatformがGeneration／Responseを上書きできない
7. `ja／en／auto`が機能する
8. Defaultが`ja`である
9. Environment／CLI Overrideが機能する
10. Effective Language Sourceを確認できる
11. ComposerがAdapter非依存である
12. User Prompt／System Messageが保持される
13. Phase 1-E機能が混入しない
14. 新規外部Dependencyがない
15. Static／Default TestがPassする
16. Current Mac／Metal RuntimeがRegressionしない

## 18. Authorization Boundary

本RequirementsはAcceptedである。

Source、Config、Test、ScriptまたはDependencyの変更は、ユーザーがPhase 1-D実装開始を明示した後に行う。
