# Phase 1-D Response Language Policy 要件定義

- 文書ID: `phase_1d_response_language_requirements`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:02:37 JST`
- 更新日時: `2026-07-19 04:02:37 JST`
- Snapshot: `20260719040237`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-D、Response Language、Config、Prompt Composition、CLI
- 正本言語: 日本語
- 上位要件: [project_requirements_20260718193435.md](project_requirements_20260718193435.md)
- 前Phase最終Review: [designer_review_phase_1c_final_20260719035156.md](../handoffs/designer_review_phase_1c_final_20260719035156.md)
- Architecture: [phase_1d_response_language_architecture_20260719040237.md](../architecture/phase_1d_response_language_architecture_20260719040237.md)
- Accepted ADR: [adr_0008_response_language_policy_20260719040237.md](../adr/adr_0008_response_language_policy_20260719040237.md)
- supersedes: なし（新規Phase 1-D専用Requirements系列）

## 1. 結論

Phase 1-Dでは、回答言語の既定値をModel、Backend Adapterまたは個別Promptへハードコードせず、交換可能なResponse Language PolicyとしてApplication側に追加する。

初期Contractは次とする。

```text
Allowed Response Language : ja／en／auto
Built-in Default          : ja
Tracked Profile Default   : ja
Phase 1 CLI Override      : --response-language
Environment Override      : MARGPA_RESPONSE_LANGUAGE
Policy Owner              : Application／Orchestration
Model Adapter Modification: 原則不要
```

Phase 1-Dは「既定の回答言語を指定する機能」である。Modelが実際に出力した自然言語を完全に識別・強制・保証する機能ではない。

## 2. 背景

Phase 1-BのQwen3-4B実機確認では、同じ日本語Promptでも、回答言語を明示しない場合に英語で出力し、`日本語で`を加えた場合に日本語で出力する事象を確認した。

この事象は小型Modelだけを原因とするものではない。

- Project ContextがModelへ渡されていない
- 回答言語の既定値が存在しない
- Promptが複数解釈可能である
- Thinkingが誤った前提を深掘りする場合がある
- ThinkingとFinal Answerが同じToken Budgetを消費する

ユーザーは英語を常用しないため、初期Deploymentでは日本語を既定値とする必要がある。一方、将来の英語利用、Model交換、Cloud移行およびAPI利用に備え、言語指定をModel固有実装へ閉じ込めてはならない。

## 3. Phase分割

Phase 1の残りを次のように分割する。

```text
Phase 1-D : Response Language Policy
Phase 1-E : Thinking Presentation Policy
```

Phase 1-Dに含めるもの：

- `ja／en／auto` Contract
- Default Language
- Profile／Environment／CLI Override
- Effective Policy解決
- System Message Composition
- Config／CLI／Audit向け表示
- Unit／Integration／Native Smoke

Phase 1-Eへ送るもの：

- Thinking実行と表示の分離
- `<think>`表示／非表示
- Thinking Label変更
- Streaming Thinking Filter
- Malformed Thinking Tag Policy
- Raw Output／Display Output分離
- Raw Thinking保存方針
- Thinking用Sampling Profile

## 4. 用語

### 4.1 Response Language Policy

回答時にModelへ与える既定の言語方針。

### 4.2 Effective Response Language

Profile、Environmentおよび明示Overrideを解決した結果、当該Requestへ適用するPolicy値。

### 4.3 Observed Output Language

Modelが実際に生成した文章の言語。

Phase 1-Dでは、Effective Response LanguageとObserved Output Languageを同一視しない。

### 4.4 `auto`

Applicationが特定言語のSystem Instructionを追加せず、明示System Message、User Prompt、Conversation ContextおよびModel挙動へ委ねるMode。

`auto`は自動言語判定Classifierの実装を意味しない。

## 5. Functional Requirements

### FR-1 Response Language Contract

初期値は次の3値だけを受理する。

```text
ja
en
auto
```

- 大文字小文字や未知Aliasを黙って正規化しない
- 未知値は`invalid_configuration`またはCLI Parse Errorとして拒否する
- 将来BCP 47相当へ拡張可能な境界を維持する
- Phase 1-Dで全言語一覧を実装しない

### FR-2 Default

Built-in DefaultとCurrent Tracked Profile Defaultは`ja`とする。

既定値は利用者の明示的な別言語指定を禁止する強制Policyではない。

### FR-3 Tracked Profile

Current Deployment Profileへ次を追加する。

```toml
[response]
language = "ja"
```

Profile Schemaは、構造変更を明示するため`2`から`3`へ更新する。

Model Registry Schemaは変更しない。

### FR-4 Environment Override

次を受理する。

```text
MARGPA_RESPONSE_LANGUAGE=ja
MARGPA_RESPONSE_LANGUAGE=en
MARGPA_RESPONSE_LANGUAGE=auto
```

未知値は安全な設定Errorとする。

### FR-5 CLI Override

`generate` Commandへ次を追加する。

```text
--response-language ja
--response-language en
--response-language auto
```

CLIは許可値以外をParse段階で拒否する。

`model-info`はProfile／Environmentから解決したPolicyを表示する。Request専用CLI Overrideは`generate`にだけ適用する。

### FR-6 Precedence

Phase 1-Dの構造化設定は、次の優先順位で解決する。

```text
Per-request Explicit Override
  > Environment Override
  > Deployment Profile
  > Built-in Default
```

Phase 2以降の追加候補：

```text
API Request Override
  > Session Preference
  > User Preference
  > Deployment Profile
  > Built-in Default
```

Phase 1-DでSession／User Preference Storageを実装しない。

### FR-7 Natural-language Instruction

User PromptまたはUser指定System Messageに「英語で」「日本語で」等が書かれている場合、Modelがその明示指示を優先できる内容のDefault Policy Instructionとする。

ただしPhase 1-Dでは、自然文から言語指定を抽出するClassifier、正規表現判定またはLLM判定を実装しない。

そのため、構造化されたEffective Policyと、Modelが自然文を解釈した結果が異なる可能性を認める。これを黙って「Language Policy適用成功」と断定しない。

### FR-8 System Message Composition

Language PolicyはApplication／Orchestration層でSystem InstructionへCompileする。

要件：

- `ja`では日本語Default Instructionを追加する
- `en`では英語Default Instructionを追加する
- `auto`ではLanguage Instructionを追加しない
- User Prompt本文を変更しない
- User指定`--system`を破棄・置換しない
- Project PolicyとUser指定System Instructionを決定論的に合成する
- Model Adapterへ日本語／英語Instructionをハードコードしない
- CLIと将来APIで同じComposerを再利用できる

初期Instructionの意味：

```text
ja   : 原則として日本語で回答する。Userが別言語を明示した場合はその指定に従う。
en   : 原則として英語で回答する。Userが別言語を明示した場合はその指定に従う。
auto : Applicationによる言語指定を加えない。
```

### FR-9 Prompt Ownership

合成後のSystem Messageでは、Projectが追加したLanguage PolicyとUserが指定したSystem Instructionの境界を一定形式で保持する。

User指定文字列は内容を改変せず、合成後Message内に保持する。

生のUser指定System Messageと合成後System Messageを将来Auditで区別できる設計とする。ただしPhase 1-DでAudit永続化は実装しない。

### FR-10 Config Observability

Effective Configおよび`model-info`で最低限次を確認できるようにする。

```text
response_language
response_language_source
```

Source候補：

```text
built_in_default
profile
environment
explicit
```

Applied PolicyをModelのObserved Output Languageとして記録しない。

### FR-11 Streaming／Non-streaming Parity

StreamingとNon-streamingで同じMessage ComposerとEffective Policyを使用する。

CLI描画後に言語を変換しない。

### FR-12 Existing System Flag Compatibility

次の既存形式を維持する。

```text
margpa-llm generate --prompt "..."
margpa-llm generate --prompt "..." --system "..."
```

Language Policy追加によって`--system`が無視されてはならない。

### FR-13 Error Handling

Config／Environmentの不正Languageは既存の安全な`InferenceError`境界へ変換する。

Errorへ次を含めない。

- User Prompt全文
- System Message全文
- Secret
- Absolute Model Path

### FR-14 Model Independence

Phase 1-DのContract、ResolverおよびComposerはQwen3、GGUF、llama.cpp、MetalまたはmacOSへ依存しない。

Current Native VerificationはQwen3-4B／llama.cpp／Metalで実施してよいが、Core Policyは将来Adapterでも利用可能にする。

### FR-15 Existing Behavior Preservation

次をRegressionさせない。

- Model Load／Unload
- One-shot Generation
- Streaming
- Cancel
- Thinking実行On／Off
- Generation Override
- Profile Resolution
- Deployment Validation
- `model-info`
- Model Artifact SHA-512検証

## 6. Non-functional Requirements

### NFR-1 疎結合

- Model PortへLanguage固有Fieldを要求しない
- llama.cpp AdapterへLanguage Policyを持たせない
- EntrypointだけにBusiness Ruleを閉じ込めない
- Pure Functionまたは小さなServiceとしてTest可能にする

### NFR-2 依存性

Phase 1-Dのために新しい外部Libraryを追加しない。

### NFR-3 Immutability／Validation

既存のImmutable Pydantic Contractと`extra="forbid"`方針を維持する。

### NFR-4 Reproducibility

Tracked ProfileへDefaultを明示し、Profile Hash変更を実装担当Statusへ記録する。

### NFR-5 Audit Readiness

将来のAudit Logで次を区別できるField境界を維持する。

- Requested／Effective Response Language
- Policy Source
- Applied Language Instruction
- User System Message
- Model Output
- Observed Output Language（将来Evaluation）

## 7. Scope外

- Output Language Classifier
- 翻訳
- 言語ごとのModeration Model
- 言語ごとのRAG Index
- BCP 47全対応
- Session／User Preference永続化
- Web UI Language Selector
- API実装
- Thinking表示／非表示
- Thinking Label
- `<think>` Parser
- Streaming Thinking Filter
- Raw Thinking保存
- High-Level Explanation
- Governance Score
- Guard Model／Judge Model呼び出し
- Model Download／変更
- Dependency追加

## 8. Required Test

### Contract／Config

- `ja／en／auto`を受理する
- 未知値を拒否する
- Profile Defaultが`ja`
- Schema Version `3`を受理する
- 旧／未知Schemaを黙って受理しない
- Environment Overrideを解決する
- Explicit OverrideがEnvironmentより優先される
- EnvironmentがProfileより優先される
- Sourceが正しく記録される

### Message Composition

- `ja` Instructionを追加する
- `en` Instructionを追加する
- `auto`でLanguage Instructionを追加しない
- User Promptを変更しない
- User System Messageを保持する
- User Systemなし／ありの両方
- Streaming／Non-streamingが同じMessage列を使う
- Model Adapter固有機能を呼ばずにUnit Testできる

### CLI

- `--response-language ja／en／auto`
- 未知値のParse拒否
- Flag省略時はProfile／Environmentを使用
- `model-info`にEffective LanguageとSourceを表示
- 既存Generation Flagとの併用

### Regression

- Ruff Format Check
- Ruff Check
- Mypy Strict
- Default pytest
- Environment Verification
- Bash Syntax
- `uv lock --check`
- Exact Offline Dry Run
- Metal Model Smoke
- Qwen3 Default Japanese Smoke
- Qwen3 Explicit English Smoke

Native Outputは確率的であるため、Unit Testの決定論的Message Compositionを正本Gateとし、Native Smokeは実Modelへの伝達確認として扱う。

## 9. Acceptance Criteria

1. `ja／en／auto`が型付きContractとして存在する
2. Defaultが`ja`である
3. Profile Schemaが`3`へ更新される
4. `MARGPA_RESPONSE_LANGUAGE`が機能する
5. `--response-language`が機能する
6. Explicit > Environment > Profile > Built-inの順で解決される
7. Effective LanguageとSourceを確認できる
8. `auto`が特定言語Instructionを注入しない
9. User PromptとUser System Messageが保持される
10. ComposerがModel Adapterから独立している
11. Streaming／Non-streamingが同じPolicyを使う
12. Thinking表示機能が混入していない
13. 新規外部Dependencyがない
14. Static／Default Testが全件Passする
15. Current Mac／Metal RuntimeがRegressionしない

## 10. Authorization Boundary

本Requirements、Architecture、ADR、HandoffおよびIndexの作成はユーザーが許可した要件・設計作業である。

Source、Config、Test、Script、DependencyまたはRoot Fileの変更は、Phase 1-D実装開始についてユーザーから明示的な許可を得た後に行う。

## 11. Phase 1-D完了境界

Phase 1-D完了とは、Current ProfileのDefault日本語、`ja／en／auto`切替、解決優先順位、Message Composition、CLI、Config表示およびRegressionが成立した状態を意味する。

Phase 1-D完了は、Modelが常に指定言語だけを出力する保証、Thinking非表示、Raw Thinking非保存またはPhase 1-E完了を意味しない。
