# Phase 1-E Thinking Presentation 要件定義

- 文書ID: `phase_1e_thinking_presentation_requirements`
- 状態: `proposed_ready_for_user_review`
- 作成日時: `2026-07-19 12:35:47 JST`
- 更新日時: `2026-07-19 12:35:47 JST`
- Snapshot: `20260719123547`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-E、Thinking実行、Output Protocol正規化、表示、Streaming、保存境界
- 正本言語: 日本語
- 設計元: [response_language_and_thinking_output_policy_20260719013109.md](../architecture/response_language_and_thinking_output_policy_20260719013109.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719123547.md](../architecture/phase_1e_thinking_presentation_architecture_20260719123547.md)
- Proposed ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md)
- supersedes: なし（Phase 1-E Requirements新規系列）

## 1. 結論

Phase 1-Eでは、次の4責務を独立したContractとして実装する。

```text
Thinking Execution   : ModelにThinkingを実行させるか
Protocol Parsing     : Model固有OutputをReasoningとFinalへ正規化する
Presentation         : Reasoningを利用者へ表示するか
Persistence          : Raw Reasoningを永続化するか
```

これらを一つのBooleanへ統合しない。

Phase 1-Eの初期値は次とする。

```text
Thinking Execution   : disabled
Thinking Visibility  : hidden
Display Label        : 推論
Raw Persistence      : disabled
```

## 2. 背景

Current Runtimeには`ThinkingMode`があり、CLIの`--thinking`でQwen3のThinking実行を切り替えられる。

しかし、Current CLIはModelが生成した`<think>...</think>`をRaw Textのまま表示する。次は未分離である。

- Thinkingを実行するか
- Thinkingを見せるか
- Canonical Protocol Tagと表示Tag
- Reasoning ContentとFinal Content
- Non-streamingとStreamingの表示動作
- 表示とAudit保存

利用者は、Application Configで日本語または英語を切り替えるのと同様に、Thinkingの表示／非表示と表示ラベルを変更できる必要がある。

## 3. 用語

### 3.1 Raw Model Output

Model Portが返した未変換のText。Current `GenerationResult.content`と`GenerationChunk.text_delta`が該当する。

### 3.2 Canonical Thinking Protocol

ModelまたはChat Templateが使用する機械的Delimiter。Current Qwen3では次である。

```text
<think>
</think>
```

### 3.3 Normalized Output

Raw Model Outputを次へ分離した内部表現。

```text
reasoning_content
final_content
parse_status
parse_warnings
```

### 3.4 Display Output

VisibilityとDisplay Labelを適用し、CLI／将来API／Web UIへ渡す表示用Output。

## 4. Phase 1-E Scope

- Application Config Schema `2`へのMigration
- `[presentation.thinking]`追加
- Thinking Presentation用のImmutable Contract
- Field別PrecedenceとSource Tracking
- Model DefinitionのOutput Protocol宣言
- Parser KeyによるParser選択
- Tagged Thinking Output Parser
- Non-streaming正規化と表示
- Stateful Streaming Parser
- Hidden ModeでのReasoning非表示
- Visible ModeでのUser-defined Display Label
- Parse Status／Warning
- CLI Override
- `model-info`のEffective Presentation表示
- Current Mac／Metal RuntimeのRegression確認

## 5. Scope外

- Thinkingが正しいことの保証
- Thinking内容の品質評価
- High-level Explanation生成
- Raw Chain of ThoughtのAudit Log保存
- Thinkingの自動要約
- Thinking用Sampling Presetの自動適用
- ThinkingのToken Budget分離
- Strict Language Enforcement
- Web UI／API
- Multi-turn Session
- Governance／Judge／Repair
- 新規外部Dependency

## 6. Configuration Migration

`config/application.toml`をSchema `1`から`2`へMigrationする。

Deployment Profile Schema `3`は変更しない。PresentationはOS／GPU／Backend固有ではないため、Deployment Profileには置かない。

```toml
schema_version = "2"

[presentation.thinking]
visibility = "hidden"
display_label = "推論"
persistence = "disabled"
```

Current `[generation].thinking_mode`は保持する。

```toml
[generation]
thinking_mode = "disabled"
```

## 7. Thinking Execution Contract

Existing Contractを維持する。

```text
disabled      : Thinking実行を無効化
enabled       : Thinking実行を有効化
model_default : Model／Templateの既定動作に委ねる
```

Presentation設定はThinking Executionを暗黙変更しない。

## 8. Thinking Presentation Contract

### Visibility

```text
hidden  : CanonicalなReasoning SectionをDisplay Outputへ出さない
visible : Canonical TagをDisplay Labelへ変換して表示する
```

Unknown Valueを拒否する。`on／off`等を黙ってAlias変換しない。

### Display Label

Defaultは`推論`とする。

CLI Visible Outputは次の形である。

```text
<推論>
Reasoning Content
</推論>
Final Content
```

`display_label = "思考過程"`であれば次のようになる。

```text
<思考過程>...</思考過程>
```

Display Labelは次を満たす。

- 1～64文字
- 空白だけでない
- 先頭／末尾空白を許可しない
- `<`、`>`、`/`を含まない
- CR／LF／制御文字を含まない
- 日本語、英語等のUnicode文字は許可する

Display LabelはModelへ送信しない。

## 9. Persistence Contract

Phase 1-Eでは次のみを許可する。

```text
persistence = "disabled"
```

- Raw ReasoningをFile／JSON／JSONL／Databaseへ保存しない
- Visibleであっても保存を意味しない
- Parserが一時的にMemory上で扱うことは永続化ではない
- 将来Persistenceを追加する場合は、別Requirements／ADR／Audit Policyを必要とする

`enabled`等の未対応値は拒否する。

## 10. PrecedenceとSource Tracking

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
  > Built-in 推論
```

### Persistence

```text
Application Config
  > Built-in disabled
```

Phase 1-EでPersistenceのEnvironment／CLI Overrideは許可しない。

FieldごとにSourceを保持する。

```text
visibility_source
display_label_source
persistence_source
```

## 11. CLI Contract

ExistingのExecution Flagを維持する。

```text
--thinking
--no-thinking
```

Presentation Flagを追加する。

```text
--show-thinking
--hide-thinking
--thinking-label "推論"
```

`--show-thinking`と`--hide-thinking`はMutually Exclusiveとする。

Example：

```bash
margpa-llm generate \
  --prompt "設計案を考えて" \
  --thinking \
  --show-thinking \
  --thinking-label "推論"
```

`--show-thinking`だけを指定してもThinking Executionを自動で`enabled`にしない。

## 12. Execution／Presentation Matrix

| Execution | Visibility | 期待動作 |
|---|---|---|
| `disabled` | `hidden` | Finalだけ表示 |
| `disabled` | `visible` | Reasoningが存在しなければFinalだけ表示 |
| `enabled` | `hidden` | Thinkingは実行し得るがFinalだけ表示 |
| `enabled` | `visible` | ReasoningをDisplay Label付きで表示し、続けてFinalを表示 |
| `model_default` | `hidden` | Model既定動作、Canonical Reasoningは非表示 |
| `model_default` | `visible` | Model既定動作、Reasoning検出時のみ表示 |

## 13. Model Output Protocol Definition

Parser選択をModel Key／Architecture／Backend名のハードコードで行わない。

Model Definitionが次を宣言する。

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Display LabelはModel Definitionへ置かない。

Unknown Parser Keyは黙ってPlain TextへFallbackせず、Application Build時に明示Errorとする。

将来のModelは`plain_text_v1`、`tagged_thinking_v1`または追加Parser KeyをDefinitionで選べる構造とする。

## 14. Parser Semantics

Phase 1-EのTagged Parserは、先頭の単1個のCanonical Thinking SectionだけをProtocolとして解釈する。

```text
[optional leading whitespace]
<think>
reasoning
</think>
final
```

規則：

1. 先頭にOpening Delimiterがなければ、全TextをFinalとする
2. Opening／Closingが完成していればReasoningとFinalへ分離する
3. Opening後にClosingがなければ`unclosed_reasoning`とする
4. Final内のTagらしきTextはユーザーContentの可能性があるため黙って削除しない
5. Parseで判断した結果とWarningを返す

Parse Status：

```text
plain_text
complete
unclosed_reasoning
malformed_protocol
```

ParserはReasoningの真実性、正しさまたは内部推論との一致を主張しない。

## 15. Non-streaming要件

- Raw `GenerationResult`は改変しない
- Presentation ServiceがRaw Contentを受け取る
- ParserでNormalized Outputを作る
- RendererでDisplay Outputを作る
- Hiddenでは`final_content`だけを表示する
- VisibleではCanonical TagだけをDisplay Tagへ変換する
- Final Contentの文字を無断でTrim／要約／翻訳しない

## 16. Streaming要件

Streaming ParserはStatefulとする。Chunk単位のRegex置換だけで実装しない。

```text
detecting_prefix
inside_reasoning
after_reasoning
plain_text
terminal
```

必須動作：

- `<think>`または`</think>`が複数Chunkへ分割されても検出できる
- Prefix判定中は最小限のSuffix Bufferを保持する
- HiddenでReasoning Chunkを一瞬表示して後から消す動作を禁止する
- VisibleでCanonical Delimiterをそのまま表示しない
- Final Chunk、Finish Reason、Usage、Cancel／CloseのSemanticsを壊さない
- StreamingとNon-streamingで同じRaw Outputから同じDisplay Outputを得る

## 17. Malformed時の方針

### Openingなし

全TextをFinalとし、原則Warningなしとする。Thinkingが生成されない正常系を許容するためである。

### Openingあり／Closingなし

- Status: `unclosed_reasoning`
- Warningを付与する
- Hidden: Reasoningと判定した部分を表示しない
- Visible: Display Opening TagとReasoningを表示し、TerminalでDisplay Closing Tagを補う
- Final Contentは空とする

### Extra／Unexpected Delimiter

- User Contentの可能性があるため黙って削除しない
- `malformed_protocol`またはWarningとして観測可能にする
- Phase 1-EのHiddenは安全性Guardrailではなく、Canonical Leading SectionのPresentation Policyである

## 18. Privacy／Audit境界

- Raw Reasoningを生のChain of Thoughtの真の内部記録と主張しない
- VisibilityとPersistenceを同一視しない
- HiddenをSecurity／Secret Redactionの代替としない
- Current CLIに新しいRaw Output保存機能を追加しない
- 将来Audit LogではHigh-level Process SummaryとSystem Traceを優先する
- Parser Warning／Parse StatusはRaw Reasoning本文なしで監査可能にする

## 19. Thinking Sampling Policy

Phase 1-EではThinking Modeに応じたSampling Parameterの自動変更を行わない。

理由：

- `--thinking`がTemperature等を暗黙変更すると再現性が下がる
- Thinking ExecutionとGeneration Tuningは別責務である
- Modelごとの推奨値は今後変わり得る
- Phase 2以降のExplicit Experiment Presetで比較する方が適する

Current Generation Overrideをそのまま使用できる状態を維持する。

## 20. Observability

`model-info`に最低限次を含める。

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

Runtime生成ごとのParse Status／WarningはPresentation Resultから参照できるようにする。

## 21. Existing Behavior Preservation

- Model Load／Unload
- Non-streaming Generation
- Streaming／Cancel／Close
- Token Usage／Timing／Finish Reason
- Artifact SHA-512
- `ja／en／auto`
- User System Message合成
- Generation Override
- Deployment／Platform Validation
- Current Mac／Metal Runtime
- `GenerationResult`／`GenerationChunk`／Model PortのRaw Contract

## 22. Required Tests

### Config

- Application Schema `2`
- Schema `1`を黙って受理しない
- Default `hidden／推論／disabled`
- Environment／CLI Precedence
- Field別Source
- Invalid Visibility／Label／Persistence拒否
- Deployment ProfileがPresentationを所有できない

### Model Protocol

- Model Definition Schema `2`
- Parser Key／Delimiter検証
- Unknown Parser Key拒否
- Parser選択にModel Key／Architectureの分岐がない

### Non-streaming

- Plain Text
- Complete Thinking Section
- Hidden／Visible
- Custom Label
- Unclosed Reasoning
- Extra Delimiter
- Final Content保持
- Raw Result不変

### Streaming

- Opening Delimiterの全Chunk分割パターン
- Closing Delimiterの全Chunk分割パターン
- 1文字Chunk
- Empty Delta
- Hidden No-flash
- Visible Label
- Malformed Terminal
- Non-streaming Parity
- Finish／Usage／Cancel／Close保持

### CLI／Regression

- `--thinking`と`--show-thinking`の独立
- `--show-thinking／--hide-thinking`の排他
- `--thinking-label`
- `model-info`
- Ruff Format／Check
- Mypy Strict
- Default Pytest
- Environment／Lock／Offline Gate
- Native Metal Thinking Hidden／Visible Smoke
- Phase 1-D Language Smoke

## 23. Acceptance Criteria

1. Thinking ExecutionとVisibilityが独立している
2. PersistenceがVisibilityから独立し、`disabled`に固定される
3. Application Config Schema `2`がStrict Validationされる
4. Deployment Profile Schema `3`が変更されない
5. Defaultが`disabled／hidden／推論／disabled`である
6. Visibility／LabelのEnvironment／CLI Overrideが機能する
7. Field別Sourceを確認できる
8. Canonical DelimiterとDisplay Labelが分離される
9. ParserがModel DefinitionのParser Keyから選択される
10. Model Key／Architecture／Backend名を用いたParserハードコードがない
11. Non-streamingでReasoning／Finalが正規化される
12. StreamingでDelimiterがChunk分割されても正しく動作する
13. Hidden StreamingでReasoningが一瞬表示されない
14. VisibleでCustom Display Labelが使用される
15. Malformed Protocolが決定論的に処理され、Warningが得られる
16. Raw `GenerationResult`／`GenerationChunk`が改変されない
17. StreamingのFinish／Usage／Cancel／Closeが保持される
18. Raw Reasoningが新しく永続保存されない
19. Sampling ParameterがThinking Flagで暗黙変更されない
20. 新規外部Dependencyがない
21. Static／Default TestがPassする
22. Current Mac／Metal RuntimeがRegressionしない

## 24. Authorization Boundary

本書はPhase 1-Eの提案Requirementsである。

ユーザーによるDecision承認前は、次を解禁しない。

- Source／Config／Test実装
- Existing Fileの変更
- Dependency追加
- Model Download
- Phase 2以降の実装

