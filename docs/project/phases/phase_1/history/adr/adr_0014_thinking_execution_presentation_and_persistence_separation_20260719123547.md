# ADR-0014: Thinking Execution、Presentation、Persistenceの分離

- 文書ID: `adr_0014_thinking_execution_presentation_and_persistence_separation`
- 状態: `proposed`
- 作成日時: `2026-07-19 12:35:47 JST`
- 更新日時: `2026-07-19 12:35:47 JST`
- Snapshot: `20260719123547`
- Decision Owner: 設計者役担当Task
- 承認者: ユーザーReview待ち
- 対象: Phase 1-E Thinking Presentation
- 正本言語: 日本語
- Requirements: [phase_1e_thinking_presentation_requirements_20260719123547.md](../requirements/phase_1e_thinking_presentation_requirements_20260719123547.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719123547.md](../architecture/phase_1e_thinking_presentation_architecture_20260719123547.md)
- 実装担当Handoff: [designer_handoff_phase_1e_thinking_presentation_20260719123547.md](../handoffs/designer_handoff_phase_1e_thinking_presentation_20260719123547.md)
- 関連ADR: [adr_0006_model_runtime_port_and_configuration_20260718224308.md](adr_0006_model_runtime_port_and_configuration_20260718224308.md)
- 関連ADR: [adr_0009_application_deployment_configuration_separation_20260719041847.md](adr_0009_application_deployment_configuration_separation_20260719041847.md)
- supersedes: なし（ADR新規系列）

## Status Decision

本ADRは`proposed`である。

ユーザーはPhase 1-Eの要件・設計開始を指示したが、本書で初めて具体化したDefault、Malformed Policy、Schema MigrationおよびParser境界は、ユーザーの確認後にAcceptedとする。

本ADRの作成はSource／Config／Test実装を自動的に解禁しない。

## Context

Phase 1-BでQwen3のThinking Execution Controlを実装した。Current CLIの`--thinking`はModelへThinkingを要求し、Modelが`<think>...</think>`を生成した場合、Raw Textをそのままstdoutへ出力する。

しかし、次は異なる責務である。

- ModelにThinkingを実行させること
- Model Output Protocolを解釈すること
- Reasoningを利用者へ見せること
- Raw Reasoningを保存すること

同一Flagへ統合すると、将来のUI、Audit、Governance、Model交換および比較実験で責務が混同する。

## Proposed Decision

### 1. Four-way Separation

```text
Execution    : generation.thinking_mode
Parsing      : model output protocol + parser
Presentation : presentation.thinking.visibility／display_label
Persistence  : presentation.thinking.persistence
```

一つの設定が別の設定を暗黙変更しない。

### 2. Defaults

```text
thinking_mode : disabled
visibility    : hidden
display_label : 推論
persistence   : disabled
```

### 3. Application Config Schema 2

`config/application.toml`に`[presentation.thinking]`を追加し、Application Schemaを`2`へ更新する。

Deployment Profile Schema `3`は変更しない。

### 4. User Override

VisibilityとDisplay LabelはApplication Config、Environment、CLIから変更可能とする。

```text
Explicit > Environment > Application > Built-in
```

PersistenceはPhase 1-Eで`disabled`だけを許可し、Environment／CLI Overrideを設けない。

### 5. Canonical ProtocolとDisplay Label

Canonical `<think>...</think>`はModel Protocolであり、User Preferenceで変更しない。

利用者が変更するのはDisplay Labelである。

```text
Canonical : <think>...</think>
Display   : <推論>...</推論>
Custom    : <思考過程>...</思考過程>
```

### 6. Output Protocol Declaration

Parser選択をModel Key、ArchitectureまたはBackendのハードコードで行わない。

Model Definition Schema `2`でParser KeyとCanonical Delimiterを宣言する。

```toml
[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Unknown Parser KeyはExplicit Errorとする。

### 7. Independent Presentation Module

Model Portとllama.cpp AdapterのRaw Contractは維持し、後段のPresentation ModuleでParserとRendererを合成する。

Output Protocol Parserは`adapters/output_protocols/`に置き、llama.cpp Backend Adapterから分離する。

### 8. Shared Stateful Parser

Non-streamingとStreamingで同じState Machineを使用する。

ChunkごとのRegex置換を作らない。Delimiter分割を扱い、Hidden ModeでReasoningを一瞬も表示しない。

### 9. Malformed Policy

- Openingなし: 全TextをFinalとする
- Openingあり／Closingなし: `unclosed_reasoning`
- Hidden: 検出済みReasoningを表示しない
- Visible: Display Closing TagをPresentation上補完する
- Extra Delimiter: 黙って削除せずWarningとする

HiddenはGuardrailまたはSecret Filterではない。

### 10. No Automatic Sampling Switch

`thinking_mode`の切替でTemperature／Top-p／Presence Penalty等を暗黙変更しない。

Thinking用PresetはPhase 2以降のExplicit Experiment Profile候補とする。

### 11. No Raw Persistence

Phase 1-EでRaw ReasoningのDisk保存を追加しない。

VisibleはPersistedを意味しない。

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
- Presentation Module、Parser Port、Parser Registryが追加される
- Streaming State MachineとChunk分割Testが必要
- Malformed Outputに対するStatus／Warning Contractが増える
- VisibleでRaw Reasoningを見せることの意味をUser Manualで説明する必要がある

## Risk Mitigation

- Existing Raw Contractを変更しない
- Parser／RendererをPure Unit Test中心で検証する
- Delimiterの全Split PositionをParameterizeする
- Hidden No-flashをAcceptance Criterionにする
- LabelをStrict Validationする
- Unknown Parser KeyをLoad前に拒否する
- Native TestでContent全文一致ではなくProtocol境界を検証する
- Raw Persistenceを明示的に`disabled`へ制限する

## Alternatives Considered

### `--thinking`で表示も同時にONにする

ExecutionとPresentationが再び結合するため不採用。

### CLIで`<think>`をRegex削除する

Chunk分割、Malformed、将来UI共通化を扱えないため不採用。

### llama.cpp Adapter内でFinalだけを返す

Backend AdapterがDisplay Policyを所有し、Raw Contractが失われるため不採用。

### Qwen3またはModel KeyでParser分岐する

将来のModel交換とCustom Modelでハードコードが増えるため不採用。

### Canonical Tag自体をUser Configで変更する

Chat Template／Model Protocolと合わなくなりParseが壊れるため不採用。

### HiddenでRaw Reasoningを一度表示後に削除する

TerminalやUIでFlashが発生し、非表示Contractを満たさないため不採用。

### Thinking Flagで推奨Sampling値へ自動変更する

暗黙副作用と実験再現性低下のためPhase 1-Eでは不採用。

### Raw ReasoningをResult／Logに常時複製保存する

保存量、Privacy、内部推論との一致主張およびAudit Policyの未確定のため不採用。

## Decision Gate

ユーザーは次を一組として承認または修正する。

1. Default `thinking_mode=disabled`
2. Default `visibility=hidden`
3. Default `display_label=推論`
4. Raw Persistenceは`disabled`のみ
5. Application Config Schema `2`
6. Model Definition Schema `2`とParser Key宣言
7. Model Port後段の独立Presentation Module
8. Stateful Streaming Parser
9. Unclosed ReasoningのHidden／Visible Fallback
10. ThinkingによるSampling自動切替なし

## Acceptance

本ADRは現時点でProposedである。

ユーザー承認時は本Fileを編集せず、新TimestampのAccepted後継ADRを作成する。

