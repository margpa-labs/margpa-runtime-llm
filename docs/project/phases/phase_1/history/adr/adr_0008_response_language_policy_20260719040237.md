# ADR-0008: Response Language Policy

- 文書ID: `adr_0008_response_language_policy`
- 状態: `accepted`
- 作成日時: `2026-07-19 04:02:37 JST`
- 更新日時: `2026-07-19 04:02:37 JST`
- 承認日時: `2026-07-19 04:02:37 JST`
- Snapshot: `20260719040237`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザー
- 対象: Phase 1-D、Response Language、Config、Prompt Composition
- 正本言語: 日本語
- 要件: [phase_1d_response_language_requirements_20260719040237.md](../requirements/phase_1d_response_language_requirements_20260719040237.md)
- Architecture: [phase_1d_response_language_architecture_20260719040237.md](../architecture/phase_1d_response_language_architecture_20260719040237.md)
- 関連ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- 関連ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: なし（Response Language専用の新規Decision）

## Status Decision

ユーザーはPhase 1の残りを次のように分割する方針を承認した。

```text
Phase 1-D : Response Language Policy
Phase 1-E : Thinking Presentation Policy
```

本ADRはPhase 1-Dの要件・設計Decisionを`accepted`とする。

本ADRのAccepted化はSource実装、Config変更、Test変更またはCommand実行を自動的に解禁しない。

## Context

Current Qwen3-4B Runtimeでは、回答言語を明示しない日本語Promptに対して英語で回答する場合がある。Promptへ`日本語で`を追加すると日本語になったため、Model交換とは別に、Application側でDefault Response Languageを扱う必要がある。

Default Languageを個別Prompt、llama.cpp AdapterまたはQwen固有Chat Templateへ埋め込むと、将来のModel／Backend交換時に同じPolicyを再実装する必要が生じる。

また、Thinkingの実行制御は既に存在するが、Thinkingの表示、非表示、Label、Streaming Filterおよび保存方針は別の責務である。

## Decision

### 1. Phase分割

Response LanguageをPhase 1-D、Thinking PresentationをPhase 1-Eとする。

### 2. Initial Contract

```text
ja
en
auto
```

の3値を採用する。

### 3. Default

Built-in DefaultおよびCurrent Tracked Profile Defaultを`ja`とする。

### 4. `auto`

`auto`ではApplicationが特定言語のSystem Instructionを追加しない。

Phase 1-Dでは自動言語判定Classifierを実装しない。

### 5. Ownership

Response Language Policyの解決とSystem Message CompositionはApplication／Orchestration層が所有する。

Model Portとllama.cpp AdapterはLanguage Policyを所有しない。

### 6. Precedence

```text
Per-request Explicit Override
  > Environment Override
  > Deployment Profile
  > Built-in Default
```

を採用する。

Phase 2以降にSession／User Preferenceを追加できる構造を維持する。

### 7. Config Surface

```toml
[response]
language = "ja"
```

```text
MARGPA_RESPONSE_LANGUAGE=en
--response-language en
```

を採用する。

### 8. Profile Schema

Deployment Profile構造変更を明示するため、Schema Versionを`2`から`3`へ更新する。

### 9. Natural-language Override

Default Instructionは、Userが自然文で別の回答言語を明示した場合にその指定へ従える意味とする。

Phase 1-Dでは自然文の言語指定をApplicationが解析・判定しない。

### 10. Observability

Effective LanguageとPolicy SourceをConfig／`model-info`から確認可能にする。

Applied PolicyとModelのObserved Output Languageを混同しない。

### 11. Phase 1-E Boundary

次はPhase 1-Dへ含めない。

- Thinking表示／非表示
- Thinking Label
- `<think>` Parser
- Streaming Filter
- Raw／Display Output分離
- Raw Thinking保存
- Thinking Sampling Profile

## Reasons

- 日本語を初期利用者のDefaultにできる
- Promptごとに`日本語で`と書く必要を減らせる
- 英語またはModel任せへ設定だけで切り替えられる
- Model／Backend Adapter交換時も同じPolicyを再利用できる
- 将来API／Web UIへ同じContractを公開できる
- Effective PolicyとObserved Outputを監査上分離できる
- Thinking Presentationの複雑性をPhase 1-Dへ混在させずに済む

## Consequences

### Positive

- Current CLIの日本語既定動作が明示的になる
- `ja／en／auto`をProfile、Environment、CLIから交換できる
- Language PolicyがPureなResolver／ComposerとしてTest可能になる
- 将来のGovernance Prompt Compilerへ接続しやすい

### Negative／Cost

- Profile Schema Migrationが必要になる
- System Message Composition規則が増える
- Model出力が指定言語へ完全一致する保証はない
- User自然文指示と構造化Policyが矛盾する場合を完全には判定できない

### Risk Mitigation

- Defaultと強制を区別する
- Natural-language Classifierを推測実装しない
- Deterministicな構造化OverrideだけをResolverで扱う
- User PromptとUser System Messageを破棄しない
- Model AdapterへLanguage固有処理を追加しない
- Native BehaviorだけでなくMessage CompositionをUnit Testする

## Alternatives Considered

### 全Promptへユーザーが毎回`日本語で`と書く

手作業で再現性が低く、UI／API追加時にも同じ問題が残るため不採用。

### Qwen Chat Templateへ日本語をハードコードする

Model／Backend交換性を損なうため不採用。

### llama.cpp AdapterでLanguageを制御する

Application PolicyがBackend固有責務へ漏れるため不採用。

### Promptの言語を自動判定して同じ言語で返す

Code、固有名詞、多言語Promptおよび短文で判定が不安定になり、Phase 1-D Scopeを超えるため不採用。`auto`はInstruction非注入として扱う。

### `ja／en`だけにして`auto`を持たない

Model本来のChat Template挙動との比較、明示System Messageだけを使う用途および将来の自動Policy追加に不便なため不採用。

### Response LanguageとThinking Presentationを同時実装する

Parser、Streaming、保存および表示責務が混在し、Acceptanceが大きくなるためPhase 1-D／1-Eへ分離する。

## Acceptance

本ADRはAcceptedである。

実装は、次を満たした後に開始する。

1. 実装担当が最新Index、Requirements、Architecture、本ADRおよび専用Handoffを読む
2. ユーザーがPhase 1-D実装開始を明示する
3. `src/`、`tests/`、`config/`等のWrite Scopeを確認する
4. Static／Default Testおよび必要なNative Testの実行許可を確認する

Decision変更時は本Fileを編集せず、新Timestampまたは新ADRを作成する。
