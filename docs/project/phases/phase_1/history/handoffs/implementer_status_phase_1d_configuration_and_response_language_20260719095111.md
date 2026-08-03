# Phase 1-D Configuration Layer分離／Response Language実装状況

- 文書ID: `implementer_status_phase_1d_configuration_and_response_language`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 09:51:11 JST`
- 更新日時: `2026-07-19 09:51:11 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719041847.md](../documentation_index_20260719041847.md)
- Implementer Handoff: [designer_handoff_phase_1d_response_language_20260719041847.md](designer_handoff_phase_1d_response_language_20260719041847.md)
- Configuration Requirements: [configuration_layer_requirements_20260719041847.md](../requirements/configuration_layer_requirements_20260719041847.md)
- Configuration Architecture: [configuration_layer_architecture_20260719041847.md](../architecture/configuration_layer_architecture_20260719041847.md)
- Response Language Requirements: [phase_1d_response_language_requirements_20260719041847.md](../requirements/phase_1d_response_language_requirements_20260719041847.md)
- Response Language Architecture: [phase_1d_response_language_architecture_20260719041847.md](../architecture/phase_1d_response_language_architecture_20260719041847.md)
- Accepted ADR-0009: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- Accepted ADR-0008: [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
- Phase 1-C Final Review: [designer_review_phase_1c_final_20260719035156.md](designer_review_phase_1c_final_20260719035156.md)
- supersedes: なし（Phase 1-D初回Status）

## 1. 結論

Phase 1-DのStep A「Application Config／Deployment Profile分離」とStep B「Response Language `ja／en／auto`」を実装した。

```text
Application Config Schema 1／Strict Validation       : Pass
Deployment Profile Schema 3／Strict Validation       : Pass
Typed Section Composition／Field別Precedence          : Pass
Context Limit Pre-load Rejection                      : Pass
Response Contract／Resolver／Composer                  : Pass
Default ja／Explicit en／auto Native Smoke             : Pass
User Prompt／User System Message保持                  : Pass
Adapter Language Logicなし                            : Pass
Phase 1-E Scope混入なし                               : Pass
Static／Default／Environment／Lock／Native Metal Gate : Pass
```

Phase 1-Dの実装担当側Acceptance Criteriaは全件Passと判定し、Designer Reviewを依頼する。

## 2. Configuration所有権の分離

### 2.1 Before／After

| 設定領域 | Before: Deployment Profile Schema 2 | After |
|---|---|---|
| Application Key | なし | Application Config Schema 1 |
| Selected Model | Deployment Profile | Application Config |
| Model Root | Deployment Profile | Application Config |
| Common Load Default | Deployment Profile | Application Config |
| Platform Load Override | Deployment Profile | Deployment Profile Schema 3 |
| Generation | Deployment Profile | Application Config |
| Response Language | なし | Application Config |
| Platform／Backend／Runtime／Hardware | Deployment Profile | Deployment Profile Schema 3 |

`config/application.toml`を共通Application設定の正本として追加した。`config/profiles/local_macos_arm64.toml`はPlatform固有値だけを保持するSchema `3`へMigrationした。

Generic Deep Mergeは導入していない。Load、Generation、Response、Model／Root、Profileを型付きSection単位で合成する。

### 2.2 Effective Configの維持

Migration前後で、既存Runtimeへ渡す実効値を維持した。

```text
selected_model       : main.qwen3-4b-q4-k-m
model_root           : ./models
context_size         : 4096
batch_size           : 256
micro_batch_size     : 256
threads              : 6
threads_batch        : 6
gpu_layers           : -1
use_mmap             : true
use_mlock             : false
verbose_backend      : false
verify_artifact_hash : true
max_new_tokens       : 512
temperature          : 0.7
top_p                : 0.8
top_k                : 20
min_p                : 0.0
presence_penalty     : 1.5
frequency_penalty    : 0.0
repeat_penalty       : 1.0
thinking_mode        : disabled
```

新規の実効値は次である。

```text
application_key : default
response        : ja／source=application
```

### 2.3 Precedence

```text
Response Language : Explicit > MARGPA_RESPONSE_LANGUAGE > Application > Built-in
Load Field        : Explicit > Environment > Deployment Override > Application > Built-in
Model／Root       : Explicit > Environment > Application
Profile           : Explicit > Environment > Platform Default
```

Field別Precedence、Strict Unknown Field拒否、旧Schema `2`拒否、Application／Deployment所有権違反、Unsafe Model Root、Model／Backend不整合をUnit Test化した。

Applicationの`context_size`がModel Native Limitを超える場合は、Adapter ConstructionおよびModel Loadより前にSafeな`invalid_configuration`として拒否する。

## 3. Response Language

### 3.1 Contract／Resolver

次のContractを追加した。

```text
ResponseLanguage       : ja／en／auto
ResponseLanguageSource : built_in_default／application／environment／explicit
ResponsePolicyConfig
ResolvedResponseLanguagePolicy
```

未定義値、`jp`、不正な環境変数値はFail-Closedし、Safeな`invalid_configuration`へ変換される。

### 3.2 Message Composer

Application Orchestration LayerにAdapter非依存のComposerを追加した。

```text
ja:
回答は原則として日本語で行ってください。
ユーザーが回答言語を明示的に指定した場合は、その指定を優先してください。

en:
Respond in English by default.
If the user explicitly requests a different response language, follow that request.

auto:
言語System Instructionを注入しない
```

`ja／en／auto × User System Message有／無`の6組合せをExact Testした。User PromptはByte-for-byteで保持し、User System Messageがある場合は1件の決定的なSystem Messageへ結合する。

Streaming／Non-streamingは同じComposer結果を使用する。Model AdapterにはResponse Language分岐または言語指示を追加していない。

### 3.3 CLI／model-info

CLIへ次を追加した。

```text
--response-language {ja,en,auto}
```

`model-info`は次を表示する。

```text
application_key           : default
profile_key               : local.macos-arm64
selected_model            : main.qwen3-4b-q4-k-m
response.language         : ja
response.source           : application
applied_sources           : built_in_defaults／application／deployment_profile
profile_resolution_source : platform_default
verification_state        : native_verified
device                    : gpu／metal
gpu_offload               : true
executed                  : null
```

## 4. 変更File

```text
A config/application.toml
M config/profiles/local_macos_arm64.toml

M src/margpa_runtime_llm/bootstrap/config_loader.py
M src/margpa_runtime_llm/bootstrap/phase1_application.py
A src/margpa_runtime_llm/modules/inference/contracts/response.py
M src/margpa_runtime_llm/modules/inference/public.py
A src/margpa_runtime_llm/orchestration/response_language.py
M src/margpa_runtime_llm/entrypoints/cli/main.py

M scripts/models/phase1b_runtime_acceptance.py

M tests/unit/inference/test_config_and_registry.py
M tests/unit/inference/test_deployment_platform.py
M tests/unit/inference/test_cli.py
A tests/unit/inference/test_response_language.py
M tests/integration/llama_cpp/test_phase1b_runtime.py

A docs/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md
```

`pyproject.toml`、`uv.lock`、Model Definition、Platform Registryに変更はない。

## 5. Resolver／Composer Test Evidence

```text
Built-in Default < Application < Environment < Explicit : Pass
ja without User System                                   : Pass／Exact
ja with User System                                      : Pass／Exact
en without User System                                   : Pass／Exact
en with User System                                      : Pass／Exact
auto without User System                                 : Pass／No injection
auto with User System                                    : Pass／User System only
User Prompt preservation                                 : Pass／Exact
Streaming／Non-streaming message parity                  : Pass
Invalid jp／Invalid Environment                          : Pass／Fail-Closed
```

## 6. Static／Default／Environment Gate

```text
Ruff Format Check          : Pass／54 files
Ruff Check                 : Pass
mypy --strict              : Pass／54 source files
compileall                 : Pass
bash -n Setup Recipe       : Pass
Default pytest             : 94 passed, 2 deselected
Environment Verification  : Pass
```

Environment:

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

## 7. Dependency Gate

```text
uv lock --check
  Resolved 117 packages

uv sync --dry-run --frozen --offline \
  --extra inference-llama \
  --group dev \
  --group notebook \
  --no-binary-package llama-cpp-python

  Checked 115 packages
  Would make no changes
```

Source変更後のProject Package自身だけを同じLock固定／Offline条件で`.venv`へ再同期した。外部Package、`pyproject.toml`、`uv.lock`の変更はない。

## 8. Native Metal／Language Smoke

Sandbox外のNative macOS／Apple Silicon arm64／Metal環境で実行した。

```text
.venv/bin/pytest -q -m model_smoke
  2 passed, 94 deselected
```

Real CLI:

```text
Default ja:
  Prompt : 「成功」とだけ答えてください。
  Result : 成功

Explicit en:
  Prompt : Reply with the single word success.
  Result : success

auto:
  Prompt : OKとだけ答えてください。
  Result : OK
```

Production Acceptance:

```text
Success                         : true
Load including SHA-512          : 2.4434 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 27.85 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0486 seconds
Detected Device                 : gpu／metal
Detected GPU Offload            : true
Artifact Digest Verified        : true
Response                        : ja／source=application
Executed State                  : null
```

## 9. Hash／Dependency不変

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

Model Definition、Platform Registry、`pyproject.toml`、`uv.lock`のHashはPhase 1-C Final時点から不変である。新規外部Dependencyはない。

## 10. Scope境界／Known Non-blocking Item

Phase 1-DのResponse LanguageはSystem Instruction Policyであり、生成結果をClassifierまたはTranslationで強制する機能ではない。`auto`は言語を推定せず、言語System Instructionを注入しない。

次は未実装のままである。

- Thinking Content抽出／非表示／表示切替などPhase 1-EのThinking Presentation
- Output Language Classifier／Translation
- Multiple Application Config Selector
- Generation／Response Preset Directory
- Dynamic Reload／Remote Config
- Windows／Linux実Profile
- Web UI／API
- Guard／Judge／Governance実行
- Phase 2以降の機能

既存のQwen3 Thinking Mode制御と`thinking_mode=disabled`はPhase 1-BからのRuntime Contractであり、Phase 1-EのPresentation処理は追加していない。

## 11. 設計者へのReview依頼

次を確認し、Phase 1-Dの受入を判定してほしい。

1. Application Config Schema `1`／Deployment Profile Schema `3`の所有権分離
2. Typed Section CompositionとField別Precedence
3. Migration前後のEffective Config同値性
4. Context LimitのPre-load拒否
5. Response Contract／Resolver／Composer
6. `ja／en／auto`とUser Message保持
7. CLI／`model-info`のEffective Source表示
8. Adapter Language Logicなし／Phase 1-E Scope混入なし
9. Static／Default／Environment／Lock／Native Metal Gate

