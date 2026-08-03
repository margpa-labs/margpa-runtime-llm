# Phase 1-E Thinking Presentation 要件定義

- 文書ID: `phase_1e_thinking_presentation_requirements`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 13:03:03 JST`
- 更新日時: `2026-07-19 13:03:03 JST`
- 承認日時: `2026-07-19 13:03:03 JST`
- Snapshot: `20260719130303`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: Phase 1-E、Thinking実行、Output Protocol正規化、表示、Streaming、保存境界
- 正本言語: 日本語
- Architecture: [phase_1e_thinking_presentation_architecture_20260719130303.md](../architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
- Accepted ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- supersedes: `phase_1e_thinking_presentation_requirements_20260719123547.md`

## 1. 承認結論

Phase 1-Eは、次の4責務を独立したContractとして実装する。

```text
Thinking Execution   : ModelにThinkingを実行させるか
Protocol Parsing     : Model固有OutputをReasoningとFinalへ正規化する
Presentation         : Reasoningを利用者へ表示するか
Persistence          : Raw Reasoningを永続化するか
```

承認された初期値：

```text
Thinking Execution   : disabled
Thinking Visibility  : hidden
Display Label        : 高度推論
Raw Persistence      : disabled
```

## 2. 提案版からの変更

ユーザー承認により、Default Display Labelを次のように変更した。

```text
Old : 推論
New : 高度推論
```

理由：

- LLMの通常回答も広い意味では推論である
- Thinking Onで表示される専用Sectionと通常回答を区別したい
- Display Labelは後からApplication Config／Environment／CLIで変更できる

`高度推論`はUI上の識別Labelであり、Reasoningが必ず高品質、正しい、真の内部推論であると主張するものではない。

その他の提案Decisionは承認され、本書に取り込む。

## 3. 背景

Current Runtimeは`ThinkingMode`とCLIの`--thinking／--no-thinking`を持つが、Modelが生成した`<think>...</think>`をRaw Textのまま表示する。

次を分離する必要がある。

- Thinkingを実行するか
- Thinkingを見せるか
- Model Protocol TagとDisplay Tag
- Reasoning ContentとFinal Content
- Non-streamingとStreaming
- UI表示とAudit保存

## 4. Scope

- Application Config Schema `2`
- `[presentation.thinking]`
- Thinking Presentation用Immutable Contract
- Field別Precedence／Source Tracking
- Model Definition Schema `2`
- Output Protocol宣言
- Parser KeyによるParser選択
- Plain Text／Tagged Thinking Parser
- Non-streaming正規化／表示
- Stateful Streaming Parser
- Hidden No-flash
- Visible Custom Display Label
- Parse Status／Warning
- CLI Override
- `model-info`
- Current Mac／Metal Regression確認

## 5. Scope外

- Thinkingの正しさ保証
- Thinkingの品質評価
- High-level Explanation生成
- Raw Chain of ThoughtのAudit Log保存
- Thinkingの自動要約
- Thinking用Sampling Presetの自動適用
- ThinkingのToken Budget分離
- Strict Language Enforcement
- Web UI／API／Multi-turn
- Governance／Judge／Repair
- 新規外部Dependency

## 6. Configuration

`config/application.toml`をSchema `1`から`2`へMigrationする。

```toml
schema_version = "2"

[generation]
thinking_mode = "disabled"

[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

Deployment Profile Schema `3`は変更しない。PresentationはPlatform固有設定ではない。

## 7. Thinking Execution

Existing Contractを維持する。

```text
disabled      : Thinking実行を無効化
enabled       : Thinking実行を有効化
model_default : Model／Templateの既定動作に委ねる
```

VisibilityはExecutionを暗黙変更しない。

## 8. Presentation

### Visibility

```text
hidden  : CanonicalなReasoning SectionをDisplay Outputへ出さない
visible : Canonical TagをDisplay Labelへ変換して表示する
```

### Display Label

Default：

```text
高度推論
```

CLI Visible Output：

```text
<高度推論>
Reasoning Content
</高度推論>
Final Content
```

User Override例：

```text
display_label = "思考過程"
<思考過程>...</思考過程>
```

Label Validation：

- 1～64文字
- Blank禁止
- 先頭／末尾空白禁止
- `<`、`>`、`/`禁止
- CR／LF／制御文字禁止
- Unicode許可

Display LabelはModelへ送信しない。

## 9. Persistence

Phase 1-Eで許可する値：

```text
persistence = "disabled"
```

- Raw ReasoningをFile／JSON／JSONL／Databaseへ保存しない
- VisibleでもPersistedを意味しない
- ParserのMemory上の一時保持は永続化ではない
- 将来の保存機能は別Requirements／ADR／Audit Policyを必要とする

## 10. Precedence／Source

### Visibility

```text
CLI Explicit
  > MARGPA_THINKING_VISIBILITY
  > Application Config
  > Built-in hidden
```

### Display Label

```text
CLI Explicit
  > MARGPA_THINKING_LABEL
  > Application Config
  > Built-in 高度推論
```

### Persistence

```text
Application Config
  > Built-in disabled
```

Phase 1-EでPersistenceのEnvironment／CLI Overrideを許可しない。

Field別Source：

```text
visibility_source
display_label_source
persistence_source
```

## 11. CLI

Execution：

```text
--thinking
--no-thinking
```

Presentation：

```text
--show-thinking
--hide-thinking
--thinking-label "高度推論"
```

`--show-thinking`と`--hide-thinking`はMutually Exclusiveとする。

`--show-thinking`はExecutionをONにせず、`--thinking`はVisibilityをVisibleにしない。

## 12. Execution／Presentation Matrix

| Execution | Visibility | 期待動作 |
|---|---|---|
| `disabled` | `hidden` | Finalだけ表示 |
| `disabled` | `visible` | ReasoningがなければFinalだけ表示 |
| `enabled` | `hidden` | Thinkingを実行し得るがFinalだけ表示 |
| `enabled` | `visible` | ReasoningをDisplay Label付きで表示後、Finalを表示 |
| `model_default` | `hidden` | Model既定動作、Canonical Reasoningは非表示 |
| `model_default` | `visible` | Model既定動作、Reasoning検出時のみ表示 |

## 13. Model Output Protocol

Parser選択をModel Key／Architecture／Backend名のハードコードで行わない。

Model Definition Schema `2`：

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Canonical DelimiterはModel Definitionが所有し、Display LabelはApplicationが所有する。

Unknown Parser KeyはSilent Fallbackせず明示Errorとする。

## 14. Normalized Output

```text
reasoning_content
final_content
parse_status
parse_warnings
```

Parse Status：

```text
plain_text
complete
unclosed_reasoning
malformed_protocol
```

ParserはReasoningの真実性、正しさまたは真の内部推論との一致を主張しない。

## 15. Parser Semantics

Leading Canonical Thinking Sectionを1個だけProtocolとして解釈する。

```text
[optional leading whitespace]
<think>
reasoning
</think>
final
```

1. Openingなし: 全TextをFinal
2. Opening／Closingあり: Reasoning／Finalへ分離
3. Openingあり／Closingなし: `unclosed_reasoning`
4. Final内のTagらしきTextを無断削除しない
5. Parse Status／Warningを返す

## 16. Non-streaming

- Raw `GenerationResult`を改変しない
- Presentation ServiceでNormalize／Renderする
- HiddenはFinalだけ
- VisibleはCanonical TagをDisplay Tagへ変換
- Final ContentをTrim／要約／翻訳しない

## 17. Streaming

Stateful Parserを使用し、Chunk単位Regex置換にしない。

```text
detecting_prefix
inside_reasoning
after_reasoning
plain_text
terminal
```

必須：

- Opening／Closing DelimiterのChunk分割対応
- Minimum Suffix Buffer
- Hidden No-flash
- VisibleでCanonical Tagをそのまま表示しない
- Finish／Usage／Cancel／Close保持
- Non-streamingとのDisplay Parity

## 18. Malformed Policy

### Openingなし

全TextをFinal。原則Warningなし。

### Openingあり／Closingなし

- Status: `unclosed_reasoning`
- Warning付与
- Hidden: 検出済みReasoningを表示しない
- Visible: Display Closing TagをTerminalで補完
- Final Contentは空

### Extra Delimiter

- User Contentの可能性があるため無断削除しない
- `malformed_protocol`またはWarningとして観測
- HiddenはSecurity Guardrailではない

## 19. Privacy／Audit

- Raw Reasoningを真のChain of Thoughtと主張しない
- VisibilityとPersistenceを同一視しない
- HiddenをSecret Redactionの代替にしない
- Raw Reasoning保存を追加しない
- Parse Status／WarningはRaw本文なしで観測できる

## 20. Sampling

Thinking ModeによるTemperature／Top-p／Presence Penalty等の自動変更を行わない。

Thinking用PresetはPhase 2以降のExplicit Experiment Profile候補とする。

## 21. Observability

`model-info`に次を含める。

```text
effective_config.generation.thinking_mode
effective_config.presentation.thinking.visibility
effective_config.presentation.thinking.display_label
effective_config.presentation.thinking.persistence
effective_config.presentation.thinking.visibility_source
effective_config.presentation.thinking.display_label_source
effective_config.presentation.thinking.persistence_source
model.output_protocol.thinking.parser_key
```

## 22. Existing Behavior Preservation

- Model Load／Unload
- Non-streaming／Streaming／Cancel／Close
- Token Usage／Timing／Finish Reason
- Artifact SHA-512
- `ja／en／auto`
- User System Message合成
- Generation Override
- Deployment／Platform Validation
- Current Mac／Metal
- Raw `GenerationResult`／`GenerationChunk`／Model Port

## 23. Required Tests

### Config

- Application Schema `2`
- Old SchemaのSilent Acceptance禁止
- Default `hidden／高度推論／disabled`
- Environment／CLI Precedence
- Field別Source
- Invalid Value／Label拒否
- DeploymentがPresentationを所有できない

### Model Protocol

- Model Definition Schema `2`
- Parser Key／Delimiter Validation
- Unknown Parser Key拒否
- Model Key／Architecture非依存

### Parser／Renderer

- Plain Text
- Complete Thinking
- Hidden／Visible
- Default／Custom Label
- Unclosed／Extra Delimiter
- Final Content保持
- Raw Result不変

### Streaming

- Opening／Closingの全Chunk Split
- 1文字Chunk
- Empty Delta
- Hidden No-flash
- Visible Label
- Malformed Terminal
- Non-streaming Parity
- Finish／Usage／Cancel／Close保持

### CLI／Regression

- Execution／Visibility独立
- Flag Exclusivity
- `--thinking-label`
- `model-info`
- Ruff／Mypy／Pytest／Compileall
- Environment／Lock／Offline
- Native Metal Hidden／Visible
- Phase 1-D Language Smoke

## 24. Acceptance Criteria

1. Thinking ExecutionとVisibilityが独立している
2. PersistenceがVisibilityから独立し、`disabled`に固定される
3. Application Config Schema `2`がStrict Validationされる
4. Deployment Profile Schema `3`が変更されない
5. Defaultが`disabled／hidden／高度推論／disabled`である
6. Visibility／LabelのEnvironment／CLI Overrideが機能する
7. Field別Sourceを確認できる
8. Canonical DelimiterとDisplay Labelが分離される
9. ParserがModel DefinitionのParser Keyから選択される
10. Model Key／Architecture／Backend名のParserハードコードがない
11. Non-streamingでReasoning／Finalが正規化される
12. StreamingでDelimiterがChunk分割されても正しく動作する
13. Hidden StreamingでReasoningが一瞬表示されない
14. VisibleでDefault／Custom Display Labelが使用される
15. Malformed Protocolが決定論的に処理され、Warningが得られる
16. Raw `GenerationResult`／`GenerationChunk`が改変されない
17. StreamingのFinish／Usage／Cancel／Closeが保持される
18. Raw Reasoningが新しく永続保存されない
19. Sampling ParameterがThinking Flagで暗黙変更されない
20. 新規外部Dependencyがない
21. Static／Default TestがPassする
22. Current Mac／Metal RuntimeがRegressionしない

## 25. Authorization Boundary

本RequirementsとDecisionはAcceptedである。

ただし、本Accepted化はSource／Config／Test実装を自動解禁しない。Phase 1-E実装開始には、ユーザーの明示的な実装許可を必要とする。

