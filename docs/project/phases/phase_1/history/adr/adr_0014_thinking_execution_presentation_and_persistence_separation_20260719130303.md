# ADR-0014: Thinking Execution、Presentation、Persistenceの分離

- 文書ID: `adr_0014_thinking_execution_presentation_and_persistence_separation`
- 状態: `accepted`
- 作成日時: `2026-07-19 13:03:03 JST`
- 更新日時: `2026-07-19 13:03:03 JST`
- 承認日時: `2026-07-19 13:03:03 JST`
- Snapshot: `20260719130303`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザー
- 対象: Phase 1-E Thinking Presentation
- 正本言語: 日本語
- Requirements: [phase_1e_thinking_presentation_requirements_20260719130303.md](../requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719130303.md](../architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
- 実装担当Handoff: [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
- 関連ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- 関連ADR: [adr_0009_application_deployment_configuration_separation_20260719041847.md](adr_0009_application_deployment_configuration_separation_20260719041847.md)
- supersedes: `adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md`

## Status Decision

ユーザーはPhase 1-Eの提案Decisionを承認し、Default Display Labelだけを`推論`から`高度推論`へ変更した。

本ADRを`accepted`とする。

Accepted化は設計Decisionの確定であり、Source／Config／Test実装の自動解禁ではない。

## Context

Current Runtimeは`ThinkingMode`とCLIの`--thinking`を持つが、Modelが生成した`<think>...</think>`をRaw Textのまま表示する。

次は異なる責務である。

- Thinking実行
- Model Output Protocol解釈
- Reasoning表示
- Raw Reasoning保存

これらを同一Flagにすると、将来のUI、Audit、Governance、Model交換および比較実験で責務が混同する。

## Decision

### 1. Four-way Separation

```text
Execution    : generation.thinking_mode
Parsing      : model output protocol + parser
Presentation : presentation.thinking.visibility／display_label
Persistence  : presentation.thinking.persistence
```

一つの設定が別設定を暗黙変更しない。

### 2. Defaults

```text
thinking_mode : disabled
visibility    : hidden
display_label : 高度推論
persistence   : disabled
```

`高度推論`はThinking On時のDisplay Channelを通常回答から区別するLabelである。高品質、正しさまたは真の内部推論であることを保証しない。

### 3. Application Config Schema 2

`config/application.toml`に次を追加する。

```toml
[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

Application Schemaを`2`へ更新し、Deployment Profile Schema `3`は変更しない。

### 4. User Override

VisibilityとDisplay Labelは次のPrecedenceで解決する。

```text
Explicit > Environment > Application > Built-in
```

PersistenceはPhase 1-Eで`disabled`だけを許可し、Environment／CLI Overrideを設けない。

### 5. Canonical Protocol／Display Label

Canonical `<think>...</think>`はModel Protocolであり、User Preferenceで変更しない。

利用者が変更するのはDisplay Labelだけとする。

```text
Canonical : <think>...</think>
Default   : <高度推論>...</高度推論>
Custom    : <思考過程>...</思考過程>
```

### 6. Model-declared Output Protocol

Parser選択をModel Key／Architecture／Backend名のハードコードで行わない。

Model Definition Schema `2`でParser KeyとCanonical Delimiterを宣言する。

```toml
[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Unknown Parser KeyはExplicit Errorとする。

### 7. Independent Presentation Module

Model Portとllama.cpp AdapterのRaw Contractを維持し、後段Presentation ModuleでParserとRendererを合成する。

Output Protocol Parserは`adapters/output_protocols/`に置き、llama.cpp Backend Adapterから分離する。

### 8. Shared Stateful Parser

Non-streamingとStreamingで同じState Machineを使用する。

Chunk単位Regex置換は使用しない。Delimiter分割を扱い、Hidden ModeでReasoningを一瞬も表示しない。

### 9. Malformed Policy

- Openingなし: 全TextをFinal
- Openingあり／Closingなし: `unclosed_reasoning`
- Hidden: 検出済みReasoningを非表示
- Visible: Display Closing TagをPresentation上補完
- Extra Delimiter: 無断削除せずWarning

HiddenはGuardrailまたはSecret Filterではない。

### 10. No Automatic Sampling Switch

`thinking_mode`の切替でTemperature／Top-p／Presence Penalty等を暗黙変更しない。

Thinking用PresetはPhase 2以降のExplicit Experiment Profile候補とする。

### 11. No Raw Persistence

Phase 1-EでRaw ReasoningのDisk保存を追加しない。VisibleはPersistedを意味しない。

## Consequences

### Positive

- Thinkingを実行しながらFinalだけ表示できる
- Display LabelをModel Protocolを壊さず変更できる
- CLI／将来API／Web UIで同じPresentation Contractを使える
- Streaming HiddenのFlashを防げる
- Model／Backend交換時にParser KeyをDefinitionから選べる
- Raw Backend Contractを保持できる
- Audit保存とUI表示を分離できる
- 実験時の暗黙Sampling変更を防げる

### Negative／Cost

- Application ConfigとModel DefinitionのSchema Migrationが必要
- Presentation Module、Parser Port、Parser Registryが増える
- Streaming State Machine／Chunk Split Testが必要
- Malformed OutputのStatus／Warning Contractが必要
- Visible Reasoningの意味をUser Manualで説明する必要がある

## Risk Mitigation

- Existing Raw Contractを変更しない
- Parser／RendererをPure Unit Test中心で検証する
- Delimiterの全Split PositionをParameterizeする
- Hidden No-flashをAcceptance Criterionにする
- LabelをStrict Validationする
- Unknown Parser KeyをLoad前に拒否する
- Raw Persistenceを`disabled`へ制限する

## Alternatives Considered

### `--thinking`で表示もON

ExecutionとPresentationが再結合するため不採用。

### CLI RegexでTag削除

Chunk Split、Malformed、将来UI共通化を扱えないため不採用。

### llama.cpp AdapterがFinalだけ返す

Backend AdapterがDisplay Policyを所有しRaw Contractが失われるため不採用。

### Qwen3／Model KeyでParser分岐

Model交換／Custom Modelでハードコードが増えるため不採用。

### Canonical TagをUser Configで変更

Model Protocol／Chat Templateと合わずParserが壊れるため不採用。

### Thinking FlagでSamplingを自動変更

暗黙副作用と実験再現性低下のため不採用。

### Raw Reasoningを常時保存

保存量、Privacy、内部推論との一致主張、Audit Policy未確定のため不採用。

## Acceptance

本ADRはAcceptedである。

Decisionを変更する場合は本Fileを編集せず、新Timestampの後継ADRを作成する。

Phase 1-E実装はユーザーの明示的な実装開始許可後に限る。

