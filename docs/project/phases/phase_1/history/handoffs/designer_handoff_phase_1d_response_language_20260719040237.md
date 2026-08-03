# Phase 1-D Response Language Policy 実装担当Handoff

- 文書ID: `designer_handoff_phase_1d_response_language`
- 状態: `ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:02:37 JST`
- 更新日時: `2026-07-19 04:02:37 JST`
- Snapshot: `20260719040237`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719040237.md](../documentation_index_20260719040237.md)
- Requirements: [phase_1d_response_language_requirements_20260719040237.md](../requirements/phase_1d_response_language_requirements_20260719040237.md)
- Architecture: [phase_1d_response_language_architecture_20260719040237.md](../architecture/phase_1d_response_language_architecture_20260719040237.md)
- Accepted ADR: [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
- Previous Phase Final Review: [designer_review_phase_1c_final_20260719035156.md](designer_review_phase_1c_final_20260719035156.md)
- supersedes: なし（新規Phase 1-D専用Handoff系列）

## 1. Handoff Conclusion

Phase 1-A、1-Bおよび1-Cは完了・最終受入済みである。

ユーザーはPhase 1の残りを次のように分割する方針を承認した。

```text
Phase 1-D : Response Language Policy
Phase 1-E : Thinking Presentation Policy
```

Phase 1-DのRequirements、ArchitectureおよびADRはAcceptedであり、実装可能な粒度まで確定した。

実装担当は、ユーザーからPhase 1-D実装開始とWrite Scopeについて明示的な許可を得た後、本Handoffの範囲を実装する。

本Handoffの作成だけでは、Source／Config／Test変更またはCommand実行は解禁されない。

## 2. Required Reading Order

実装開始前に次を読み取り専用で確認する。

1. [documentation_index_20260719040237.md](../documentation_index_20260719040237.md)
2. [phase_1d_response_language_requirements_20260719040237.md](../requirements/phase_1d_response_language_requirements_20260719040237.md)
3. [phase_1d_response_language_architecture_20260719040237.md](../architecture/phase_1d_response_language_architecture_20260719040237.md)
4. [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
5. [designer_review_phase_1c_final_20260719035156.md](designer_review_phase_1c_final_20260719035156.md)
6. [phase_1b_model_runtime_contract_20260718223203.md](../architecture/phase_1b_model_runtime_contract_20260718223203.md)
7. [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
8. [response_language_and_thinking_output_policy_20260719013109.md](../architecture/response_language_and_thinking_output_policy_20260719013109.md)
9. [documentation_rules_20260718193435.md](../requirements/documentation_rules_20260718193435.md)

旧Combined PolicyのResponse Language部分より、Phase 1-D専用Requirements／Architecture／ADRを優先する。

Thinking部分はPhase 1-E用の参照資料であり、本実装Scopeへ含めない。

## 3. Authorization／Write Scope Gate

暫定担当分担における実装者役の通常Write Scope：

```text
src/
tests/
scripts/
docs/handoffs/implementer_status_*
```

Phase 1-Dでは次の変更が必要になる。

```text
config/profiles/local_macos_arm64.toml
```

実装前にユーザーから少なくとも次を確認する。

1. Phase 1-D実装開始
2. `src/`／`tests/`変更
3. `config/`変更
4. Static／Default Test実行
5. 実Model／Metal Smoke実行
6. 実装担当Status作成

新規Dependencyまたは`pyproject.toml`変更は想定しない。必要になった場合は独断で追加せず設計者へ報告する。

Requirements、Architecture、Governance、ADR、Designer ReviewおよびDocumentation Indexを実装担当が編集しない。

## 4. Objective

Current Mac／Metal Runtimeを維持しながら、回答言語を次の設定だけで切り替えられる状態を作る。

```text
ja
en
auto
```

初期Defaultは`ja`とする。

## 5. Locked Decisions

実装担当が独断で変更しない。

```text
Phase名                  : Phase 1-D Response Language Policy
Allowed                  : ja／en／auto
Built-in Default         : ja
Current Profile Default  : ja
Environment              : MARGPA_RESPONSE_LANGUAGE
CLI                      : --response-language
Precedence               : Explicit > Environment > Profile > Built-in
auto                     : Language Instruction非注入
Policy Owner             : Application／Orchestration
Adapter Language Logic   : 禁止
Profile Schema           : 3
Model Registry Schema    : 変更なし
Natural Language解析     : 実装しない
Observed Language保証    : 行わない
New Dependency           : 追加しない
Thinking Presentation    : Phase 1-E
```

## 6. Required Deliverables

### 6.1 Response Language Contract

最低限次を型付きで表現する。

```text
ResponseLanguage
ResponseLanguageSource
ResolvedResponseLanguagePolicy
```

`GenerationParameters`へLanguageを追加しない。

### 6.2 Profile Migration

`config/profiles/local_macos_arm64.toml`を次へMigrationする。

```toml
schema_version = "3"

[response]
language = "ja"
```

Platform Registry参照Key／Pathを不要に変更しない。

### 6.3 Effective Config Resolution

次を実装する。

```text
MARGPA_RESPONSE_LANGUAGE
Explicit Response Override
Resolved Language
Resolved Source
```

不正値をDefaultへ黙ってFallbackしない。

### 6.4 Message Composer

Backend-independentなPure Functionまたは小Serviceとして実装する。

```text
Input:
  User Prompt
  Optional User System Message
  Resolved Response Policy

Output:
  tuple[ChatMessage, ...]
```

Cases：

- `ja`＋Systemなし
- `ja`＋Systemあり
- `en`＋Systemなし
- `en`＋Systemあり
- `auto`＋Systemなし
- `auto`＋Systemあり

User PromptとUser System文字列を破棄・書換えしない。

### 6.5 CLI

`generate`へ追加する。

```text
--response-language {ja,en,auto}
```

既存`--system`、`--thinking`、`--no-thinking`、Sampling Flagと併用可能にする。

### 6.6 Config Observability

`model-info`の`effective_config`へ次を追加する。

```text
response.language
response.source
```

Applied PolicyをObserved Output Languageと表示しない。

### 6.7 Public Export

将来APIが同じContractを利用できるよう、既存Public Surface方針に従って必要なContractをExportする。

不要なBackend固有Exportは追加しない。

## 7. Initial Instruction Semantics

実装するInstructionの意味：

```text
ja:
回答は原則として日本語で行う。
Userが回答言語を明示した場合は、その指定を優先する。

en:
英語を既定とする。
Userが別の回答言語を明示した場合は、その指定を優先する。

auto:
Applicationから言語指定を追加しない。
```

実装時の正確な文字列をUnit Test Fixtureとして固定する。

## 8. Suggested Implementation Sequence

1. Existing Static／Default Testを変更前に確認する
2. Response Contractを追加する
3. Config ContractとResolverを拡張する
4. Current ProfileをSchema `3`へMigrationする
5. Message Composerを追加する
6. CLIをComposerへ接続する
7. `model-info`へEffective Policyを追加する
8. Unit／CLI／Contract Testを追加する
9. Static／Default Gateを実行する
10. Environment／Lock／Offline Gateを実行する
11. Metal／Qwen3 Native Smokeを実行する
12. 実装担当Statusを新Timestampで作成する

## 9. Candidate File Scope

候補であり、不要なFileを量産しない。

```text
src/margpa_runtime_llm/modules/inference/contracts/response.py
src/margpa_runtime_llm/modules/inference/contracts/__init__.py
src/margpa_runtime_llm/modules/inference/public.py
src/margpa_runtime_llm/orchestration/response_language.py
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/entrypoints/cli/main.py
config/profiles/local_macos_arm64.toml
tests/unit/inference/test_response_language.py
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
```

原則変更不要：

```text
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py
src/margpa_runtime_llm/modules/inference/ports/model_port.py
config/models/qwen3_4b_q4_k_m.toml
pyproject.toml
uv.lock
```

## 10. Required Test Cases

### Contract／Resolver

- `ja／en／auto`受理
- 未知値拒否
- Default `ja`
- Schema `3`
- Explicit > Environment > Profile > Built-in
- Source Tracking
- Environment不正値のSafe Error

### Composer

- 6つのComposition Case
- Stable Language Instruction
- User Prompt完全保持
- User System完全保持
- `auto`でPolicy System Messageなし
- Empty Prompt／Systemの既存Validation
- Backend Import不要

### CLI

- 3 Language Choice
- Invalid Choice Exit `2`
- `--system`併用
- Thinking Flag併用
- Streaming／Non-streaming
- `model-info`表示

### Regression

- Ruff Format Check
- Ruff Check
- Mypy Strict
- Default pytest
- Environment Verification
- Bash Syntax Check
- `uv lock --check`
- Exact Offline Dry Run
- Native Metal Smoke
- Native CLI Default `ja`
- Native CLI Explicit `en`
- Native CLI `auto`

## 11. Acceptance Evidence

実装担当Statusへ次を記録する。

- 変更File一覧
- Contract／Resolver／Composer概要
- Profile Schema Before／After
- Profile SHA-512またはProject既定Hash
- `ja／en／auto` Message Composition Evidence
- Precedence Test Evidence
- `model-info` OutputのResponse部分
- Static Check結果
- Default Test結果
- Environment／Lock／Offline結果
- Native Metal Smoke結果
- Default日本語／Explicit英語／Autoの実行例
- Dependency変更がないこと
- Model AdapterへLanguage Logicを追加していないこと
- Phase 1-E Scopeが混入していないこと
- Known Non-blocking Item

## 12. Prohibited Scope Expansion

- `<think>` Tag削除
- Thinking表示／非表示
- Thinking Label変更
- Streaming Output Filter
- Raw Output／Display Output分離
- Thinking保存
- Thinking Sampling切替
- Language Detection Classifier
- Output翻訳
- BCP 47全対応
- Session／User Preference Storage
- FastAPI／Web UI
- Guard Model／Judge Model
- Governance Compiler
- Model Download／交換
- New Backend Adapter
- New External Dependency

必要と判断した場合、独断実装せず設計担当へ報告する。

## 13. Known Non-blocking Items

- ModelはDefault Languageに常に従うとは限らない
- Natural-languageの別言語指定をApplicationは判定しない
- Native Language Smokeは生成確率の影響を受ける
- `auto`はClassifierではない
- Thinking表示はPhase 1-Eまで現在挙動のまま
- Native Package再Buildを含む通常Setup Recipeは重い
- `.DS_Store`はmacOS操作で再生成される可能性がある

## 14. Completion Boundary

Phase 1-D完了は、Default日本語と`ja／en／auto`切替がApplication Policyとして成立し、Config／CLI／Test／Current Metal Runtimeで受け入れられた状態を意味する。

Phase 1-E、Strict Language Enforcement、Translation、Language EvaluationまたはWeb UI完成を意味しない。
