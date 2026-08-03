# Phase 1-D Configuration／Response Language 最終設計Review

- 文書ID: `designer_review_phase_1d_final`
- 状態: `accepted_phase_1d_complete`
- 作成日時: `2026-07-19 12:20:35 JST`
- 更新日時: `2026-07-19 12:20:35 JST`
- Snapshot: `20260719122035`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-D実装の最終受入
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](implementer_status_phase_1d_configuration_and_response_language_20260719095111.md)
- 実装Handoff: [designer_handoff_phase_1d_response_language_20260719041847.md](designer_handoff_phase_1d_response_language_20260719041847.md)
- 最新Roadmap: [implementation_roadmap_20260719122035.md](../architecture/implementation_roadmap_20260719122035.md)
- 最新Index: [documentation_index_20260719122035.md](../documentation_index_20260719122035.md)
- supersedes: なし（Phase 1-D最終Reviewの新規系列）

## 1. 最終結論

Phase 1-Dを受け入れ、`Complete／Accepted`と判定する。

```text
Blocking Finding          : 0
High Finding              : 0
Medium Finding            : 0
Required Follow-up        : 0
Acceptance Criteria       : 16／16 Pass
Static／Default Gate      : Pass
Dependency／Offline Gate : Pass
Native Metal Gate         : Pass
Final Decision            : Accepted
```

Phase 1-DのCompletion Boundaryである次が成立した。

- Application共通設定とDeployment／Hardware設定の分離
- Application Config Schema `1`
- Deployment Profile Schema `3`
- Typed Section Composition
- `ja／en／auto` Response Language Policy
- Application／Environment／Explicitの優先順位
- Backend非依存Message Composition
- CLI／Streaming／Non-streamingの共通経路
- Mac／Apple Silicon／Metalの非Regression

## 2. Review対象の正本

### Requirements

- [configuration_layer_requirements_20260719041847.md](../requirements/configuration_layer_requirements_20260719041847.md)
- [phase_1d_response_language_requirements_20260719041847.md](../requirements/phase_1d_response_language_requirements_20260719041847.md)

### Architecture

- [configuration_layer_architecture_20260719041847.md](../architecture/configuration_layer_architecture_20260719041847.md)
- [phase_1d_response_language_architecture_20260719041847.md](../architecture/phase_1d_response_language_architecture_20260719041847.md)

### ADR／Handoff

- [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
- [adr_0009_application_deployment_configuration_separation_20260719041847.md](../adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- [designer_handoff_phase_1d_response_language_20260719041847.md](designer_handoff_phase_1d_response_language_20260719041847.md)

### Implementer Status

- [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](implementer_status_phase_1d_configuration_and_response_language_20260719095111.md)

## 3. Review対象File

### Configuration

```text
config/application.toml
config/profiles/local_macos_arm64.toml
config/models/qwen3_4b_q4_k_m.toml
config/platforms/platform_registry.toml
```

### Source

```text
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/modules/inference/contracts/response.py
src/margpa_runtime_llm/modules/inference/public.py
src/margpa_runtime_llm/orchestration/response_language.py
src/margpa_runtime_llm/entrypoints/cli/main.py
```

### Test／Acceptance

```text
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_response_language.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
scripts/models/phase1b_runtime_acceptance.py
```

## 4. Findings

### 4.1 Blocking／High／Medium

該当なし。

Source変更を求める不具合、設計逸脱、Regression、安全境界違反は発見されなかった。

### 4.2 Inline Code Comment

修正必須のInline Findingはない。

## 5. Configuration責務分離Review

### 5.1 Application Config

`config/application.toml`が次を所有することを確認した。

- `application_key`
- `selected_model`
- `model_root`
- Common `load_defaults`
- `generation`
- `response.language`

Tracked DefaultはUser固有Absolute Pathを持たず、`model_root.default = "./models"`を使う。Application Config内のAbsolute Pathおよび`..`をValidatorが拒否する。

### 5.2 Deployment Profile

`config/profiles/local_macos_arm64.toml`がSchema `3`へMigrationされ、次のPlatform／Hardware責務のみを持つことを確認した。

- Host
- Compute
- Backend Runtime
- Runtime Requirements
- Verification State
- Hardware-dependent `load_overrides`

Raw TOMLに次が残っていない。

```text
selected_model
model_root
generation
response
load
```

### 5.3 Model／Platform責務の不変

- Model DefinitionはArtifact／Hash／Model Capability／Native Context Limitを維持する。
- Platform RegistryはAlias／Default Profile Referenceだけを維持する。
- Model DefinitionとPlatform RegistryのDigestがPhase 1-C最終時点から不変である。

## 6. Typed Composition Review

`resolve_effective_config`は次のTyped Sectionを個別に解決する。

```text
Model／Root
Load
Generation
Response
Profile
```

Generic Recursive Dictionary Mergeは導入されていない。

### 6.1 Precedence

| 領域 | 確認した順位 |
|---|---|
| Model／Root | Explicit > Environment > Application |
| Load | Explicit > Environment > Deployment > Application > Built-in |
| Generation | Explicit > Environment > Application > Built-in |
| Response | Explicit > Environment > Application > Built-in |
| Profile | Explicit > Environment > Platform Default |

Pydantic Contractの`extra="forbid"`により、未知Field、所有権違反、旧Schema `2`を拒否する。

### 6.2 Pre-load Validation

Applicationの実効`context_size`がModel Native Limitを超える場合、`LlamaCppModelAdapter`のConstructionより前に`invalid_configuration`として拒否することをSourceとTestで確認した。

## 7. Response Language Review

### 7.1 Contract

```text
ResponseLanguage       : ja／en／auto
ResponseLanguageSource : built_in_default／application／environment／explicit
ResponsePolicyConfig
ResolvedResponseLanguagePolicy
```

Unknown Value、`jp`、不正なEnvironment ValueをAlias推測せず拒否する。

### 7.2 Message Composer

`margpa_runtime_llm.orchestration.response_language`にBackend非依存のResolver／Composerが置かれている。

- `ja`: 日本語Default Instruction
- `en`: 英語Default Instruction
- `auto`: Language Instructionなし
- User Prompt: Byte-for-byte保持
- User System Message: 破棄せず決定論的に結合
- Streaming／Non-streaming: 同一Composer経路

### 7.3 Adapter Boundary

`src/margpa_runtime_llm/adapters/`およびModel Portに、Response Languageの値、文言、分岐は存在しない。Language PolicyはApplication／Orchestration責務に留まっている。

## 8. Phase 1-E Scope Boundary

次のPhase 1-E対象は実装されていない。

- `<think>` Parser
- Thinking表示／非表示
- User-defined Thinking Label
- Streaming Thinking Filter
- Raw／Display Output分離
- Raw Thinking保存Policy
- Thinking Sampling Profile

Phase 1-Bから存在する`thinking_mode`と、Test／AcceptanceのThinking Tag非出現確認のみである。Phase 1-Eの責務混入とは判定しない。

## 9. Acceptance Criteria

| # | Criteria | Result | Evidence |
|---:|---|---|---|
| 1 | `config/application.toml`が共通正本 | Pass | Tracked Config／Loader／Unit Test |
| 2 | Application Schema `1` Strict Validation | Pass | Literal Schema／Unknown Field／Unsafe Root Test |
| 3 | Deployment Schema `3` Strict Validation | Pass | Literal Schema／Unknown Field／Old Schema Test |
| 4 | Platform Profileから共通Field除去 | Pass | Raw TOML Ownership Test |
| 5 | Typed ComposerがEffective Config生成 | Pass | Section別Resolver／Migration Test |
| 6 | PlatformがGeneration／ResponseをOverride不可 | Pass | Profile Contract `extra=forbid` |
| 7 | `ja／en／auto`が機能 | Pass | Unit／CLI／Native Metal |
| 8 | Default `ja` | Pass | Application Config／Resolver／Real CLI |
| 9 | Environment／CLI Override | Pass | Precedence Test／CLI Test |
| 10 | Effective Language Sourceを確認可 | Pass | `model-info`／Real Runtime JSON |
| 11 | ComposerがAdapter非依存 | Pass | Orchestration配置／Adapter検索 |
| 12 | User Prompt／System Message保持 | Pass | 6 Composition Exact Test |
| 13 | Phase 1-E機能混入なし | Pass | Source Search／Scope Review |
| 14 | 新規External Dependencyなし | Pass | `pyproject.toml`／`uv.lock`不変 |
| 15 | Static／Default Test Pass | Pass | Independent Gate |
| 16 | Mac／Metal Runtime非Regression | Pass | 2 Native Smoke + Production Acceptance |

## 10. 独立検証結果

### 10.1 Static／Default

```text
ruff format --check . : Pass／54 files already formatted
ruff check .          : Pass
mypy                  : Pass／54 source files
compileall            : Pass
bash -n Setup Recipe  : Pass
pytest -q             : Pass／94 passed, 2 deselected
```

### 10.2 Environment／Dependency

```text
Python                         : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python               : 0.3.34
GPU Offload Support            : true
Metal System Info              : present
Dependency Versions Match      : true
Out-of-scope Packages Absent   : true
uv lock --check                : Pass／Resolved 117 packages
uv sync --dry-run --frozen ... : Pass／Checked 115／Would make no changes
```

Sandbox内のNative TestはMetal Contextを作成できず`Failed to create llama_context`となった。同一CommandをSandbox外のNative macOS環境で再実行し、次のとおりPassした。これはSandboxのGPU／Metal制約であり、Phase 1-D実装不具合とは判定しない。

### 10.3 Native Metal

```text
pytest -q -m model_smoke : 2 passed, 94 deselected

Default ja:
  Prompt : 「成功」とだけ答えてください。
  Result : 成功。

Explicit en:
  Prompt : Reply with the single word success.
  Result : success

auto:
  Prompt : OKとだけ答えてください。
  Result : OK
```

### 10.4 Real `model-info`

```text
application_key           : default
profile_key               : local.macos-arm64
selected_model            : main.qwen3-4b-q4-k-m
response.language         : ja
response.source           : application
profile_resolution_source : platform_default
verification_state        : native_verified
device                    : gpu／metal
gpu_offload               : true
executed                  : null
```

### 10.5 Production Runtime Acceptance

```text
success                         : true
load_seconds_including_sha512   : 2.4349
unload_seconds                  : 0.0660
generation_content              : フェーズ1-B生産ランタイム成功
generation_tokens_per_second    : 29.36
stream_terminal_state           : cancelled
post_cancel_content             : OK
post_cancel_finish_reason       : stop
artifact_digest_verified        : true
response                        : ja／application
thinking_tags_absent            : true
```

## 11. Hash照合

Implementer Statusの記録と独立計算が一致した。

```text
Application Config SHA-512:
1f38d7f0ed5ed1157cac76ad63f14fd57f0fa688448180c37c5c01abd6f046db27edaed25dfab8c72dca3324f9a1a930579efdcb503c74bc5ef60bbc20f1f83b

Mac Deployment Profile SHA-512:
861aa54e159285a5445df853b260b2465194a93bc2c254d3cfd9ec4b58c4fc6c1af0dd1ba7d80251a5e46f9c886fe2205d7931b346709002edb2e7d9f9ce2b40

Model Definition SHA-512:
2a1d3951b56dba2514fd4c37161dbea8048e80efc1ac9a8672f4a7f1f5d2c6aa3e3aaace7216b522dd2c1627fb30d676a80d7a761881f039f2337983d510f4be

Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

## 12. 非ブロッカー／設計どおりの延期項目

### 12.1 Response LanguageはDefault Policy

Phase 1-DはSystem InstructionによるDefault Language Policyであり、Output Language Classifier、Translation、Strict Enforcementではない。Modelが常に指定言語を守る保証はない。これはRequirementで明示された正常なScope境界である。

### 12.2 Source Trackingの粒度

Phase 1-Dは`applied_sources`、`profile_resolution_source`、`response.source`を提供する。全FieldのSource Mapは後続のTyped Config／Experiment／Auditで追加する。

### 12.3 Runtime Observation

Load時点の`runtime_observation.executed = null`と`build_variant_declared_not_observed`はPhase 1-CのAccepted境界を維持している。Phase 1-DのBlockerではない。

### 12.4 Setup RecipeのNative Rebuild

通常Setupで`--reinstall-package llama-cpp-python`を使うため、Native Packageを毎回Rebuildする点は既存の非ブロッカーである。将来、通常Syncと明示的Native Rebuildを分離可能である。

## 13. Status Transition

```text
Phase 1-D
  Designed／Accepted
    → Implementation Complete／Review Requested
    → Designer Review Accepted
    → Complete／Accepted
```

次のPhase状態：

```text
Phase 1-D : Complete／Accepted
Phase 1-E : Planned／Not Designed／Not Authorized
```

## 14. Authorization Boundary

本ReviewはPhase 1-Dを受け入れる。

次は自動的に解禁されない。

- Phase 1-EのSource／Config／Test実装
- `<think>` Parser／Filter／Label
- Phase 2以降の実装
- Dependency追加
- Model Download
- Lightning AI Studio外部操作

Phase 1-Eは次の設計対象として進められるが、実装には別途ユーザー許可が必要である。
