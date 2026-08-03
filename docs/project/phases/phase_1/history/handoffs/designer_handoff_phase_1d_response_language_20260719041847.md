# Phase 1-D Configuration Layer／Response Language 実装担当Handoff

- 文書ID: `designer_handoff_phase_1d_response_language`
- 状態: `ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719041847.md](../documentation_index_20260719041847.md)
- Configuration Requirements: [configuration_layer_requirements_20260719041847.md](../requirements/configuration_layer_requirements_20260719041847.md)
- Configuration Architecture: [configuration_layer_architecture_20260719041847.md](../architecture/configuration_layer_architecture_20260719041847.md)
- Phase Requirements: [phase_1d_response_language_requirements_20260719041847.md](../requirements/phase_1d_response_language_requirements_20260719041847.md)
- Phase Architecture: [phase_1d_response_language_architecture_20260719041847.md](../architecture/phase_1d_response_language_architecture_20260719041847.md)
- ADR-0008: [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
- ADR-0009: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- Previous Phase Final Review: [designer_review_phase_1c_final_20260719035156.md](designer_review_phase_1c_final_20260719035156.md)
- supersedes: `designer_handoff_phase_1d_response_language_20260719040237.md`

## 1. Handoff Conclusion

Phase 1-Dは、単なるLanguage Flag追加ではなく、先にConfiguration Layerの責務を分離した上でResponse Languageを接続する。

```text
Step A : Application Config／Deployment Profile分離
Step B : Response Language Resolver／Message Composer
```

前版Handoffの`response.language`をCurrent Mac Profileへ追加する指示は無効である。

本Handoffの作成は実装開始を自動的に解禁しない。

## 2. Required Reading Order

1. [documentation_index_20260719041847.md](../documentation_index_20260719041847.md)
2. [configuration_layer_requirements_20260719041847.md](../requirements/configuration_layer_requirements_20260719041847.md)
3. [configuration_layer_architecture_20260719041847.md](../architecture/configuration_layer_architecture_20260719041847.md)
4. [phase_1d_response_language_requirements_20260719041847.md](../requirements/phase_1d_response_language_requirements_20260719041847.md)
5. [phase_1d_response_language_architecture_20260719041847.md](../architecture/phase_1d_response_language_architecture_20260719041847.md)
6. [adr_0009_application_deployment_configuration_separation_20260719041847.md](../adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
7. [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
8. [designer_review_phase_1c_final_20260719035156.md](designer_review_phase_1c_final_20260719035156.md)
9. [documentation_rules_20260718193435.md](../requirements/documentation_rules_20260718193435.md)

同一系列では`20260719041847`版を旧`20260719040237`版より優先する。

## 3. Authorization／Write Scope

実装前にユーザーから次を確認する。

1. Phase 1-D実装開始
2. `src/`／`tests/`変更
3. `config/application.toml`新規作成
4. `config/profiles/local_macos_arm64.toml`変更
5. Static／Default Test実行
6. Native Metal Test実行
7. 実装担当Status作成

Dependency追加、`pyproject.toml`または`uv.lock`変更は想定しない。必要になった場合は設計者へ返す。

## 4. Locked Configuration Decisions

```text
Common Config Path         : config/application.toml
Application Schema         : 1
Deployment Profile Schema  : 3
Generic Deep Merge         : 禁止
Selected Model Owner       : Application Config
Model Root Owner           : Application Config
Generation Owner           : Application Config
Response Owner             : Application Config
Platform Owner             : Deployment Profile
Hardware Load Tuning Owner : Deployment Profile
Artifact Owner             : Model Definition
```

## 5. Locked Response Decisions

```text
Allowed                 : ja／en／auto
Default                 : ja
Environment             : MARGPA_RESPONSE_LANGUAGE
CLI                     : --response-language
Precedence              : Explicit > Environment > Application > Built-in
auto                    : Language Instructionなし
Language Classifier     : 実装しない
Adapter Language Logic  : 禁止
Thinking Presentation   : Phase 1-E
```

## 6. Step A Required Deliverables

### 6.1 Application Config

`config/application.toml`を追加する。

含めるもの：

- `application_key`
- `selected_model`
- `model_root`
- `load_defaults`
- `generation`
- `response`

### 6.2 Deployment Profile Migration

Current ProfileをSchema `3`へMigrationする。

削除：

- `selected_model`
- `model_root`
- `generation`
- Common Load Field

保持：

- Host／Compute／Backend／Runtime Requirements
- Verification State
- Hardware `load_overrides`

### 6.3 Typed Composer

Application、Model、Deployment、Environment、CLIをField Ownerに従って合成する。

Generic Recursive Mergeを作らない。

### 6.4 Effective Config

最低限次を追加・維持する。

```text
application_key
profile_key
selected_model
model_root
load
generation
response
profile_resolution_source
applied_sources
```

## 7. Step B Required Deliverables

### 7.1 Response Contract

```text
ResponseLanguage
ResponseLanguageSource
ResponsePolicyConfig
ResolvedResponseLanguagePolicy
```

### 7.2 Resolver

```text
Explicit
  > MARGPA_RESPONSE_LANGUAGE
  > Application Config
  > Built-in ja
```

### 7.3 Message Composer

Backend-independentなPure Functionまたは小Serviceとする。

- `ja` Policy
- `en` Policy
- `auto` No-injection
- User Prompt保持
- User System保持
- Stable Composition

### 7.4 CLI

```text
--response-language {ja,en,auto}
```

### 7.5 Observability

`model-info`にApplication KeyとEffective Responseを含める。

## 8. Candidate File Scope

```text
config/application.toml
config/profiles/local_macos_arm64.toml
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/modules/inference/contracts/response.py
src/margpa_runtime_llm/modules/inference/contracts/__init__.py
src/margpa_runtime_llm/modules/inference/public.py
src/margpa_runtime_llm/orchestration/response_language.py
src/margpa_runtime_llm/entrypoints/cli/main.py
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_response_language.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
```

原則変更しない：

```text
config/models/qwen3_4b_q4_k_m.toml
config/platforms/platform_registry.toml
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/
src/margpa_runtime_llm/modules/inference/ports/model_port.py
pyproject.toml
uv.lock
```

## 9. Implementation Sequence

1. Migration前のEffective ConfigをTestで固定
2. Application Config Contract／Loader
3. Deployment Profile Schema `3`
4. Typed Composer
5. Tracked Config Migration
6. Existing Override／Validation接続
7. Configuration Unit Test
8. Response Contract／Resolver
9. Message Composer
10. CLI／`model-info`
11. Response Unit／CLI Test
12. Static／Default Gate
13. Environment／Lock／Offline Gate
14. Native Metal／Language Smoke
15. Implementer Status

## 10. Required Tests

### Configuration Ownership

- Application Configが共通Fieldを所有
- Deployment Profileが共通Fieldを拒否
- Hardware Override Allowlist
- Model Definitionの責務維持

### Composition

- Application Default
- Deployment Load Override
- Environment Override
- CLI Override
- Field別Precedence
- Migration前後のEffective値一致
- Cross-object Compatibility

### Response

- `ja／en／auto`
- Invalid Language拒否
- Source Tracking
- 6 Composition Cases
- User Content保持
- Streaming／Non-streaming Parity

### Regression

- Ruff Format／Check
- Mypy Strict
- Default pytest
- Environment Verification
- Bash Syntax
- `uv lock --check`
- Exact Offline Dry Run
- `model-info`
- Metal Smoke
- Default `ja`／Explicit `en`／`auto`

## 11. Acceptance Evidence

実装担当Statusへ次を記録する。

- 変更File一覧
- Config Before／After
- Field Ownership一覧
- Effective Config Before／After
- Application Config Hash
- Deployment Profile Hash
- Model Definition／Platform Registry Hash
- `model-info`該当部分
- Resolver／Composer Test Evidence
- Static／Default／Native結果
- 新規Dependencyなし
- Adapter Language Logicなし
- Phase 1-E Scope混入なし
- Known Non-blocking Item

## 12. Prohibited Scope Expansion

- Generic Deep Merge Engine
- Multiple Application Config UI
- Dynamic Reload
- Generation／Response Preset Directory
- Windows／Linux実Profile
- `<think>` Parser／Filter／Label
- Output Language Classifier／Translation
- Web UI／API
- Guard／Judge／Governance実行
- New Backend／Model Download
- New External Dependency

## 13. Completion Boundary

Phase 1-D完了は、共通Application ConfigがPlatform Profileから分離され、`ja／en／auto`がApplication PolicyとしてCurrent Mac／Metal Runtimeで成立した状態を意味する。

Phase 1-Eまたは他PlatformのNative対応完了を意味しない。
