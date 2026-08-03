# Phase 1-E Thinking Presentation 実装担当Handoff

- 文書ID: `designer_handoff_phase_1e_thinking_presentation`
- 状態: `draft_waiting_for_adr_acceptance_and_implementation_authorization`
- 作成日時: `2026-07-19 12:35:47 JST`
- 更新日時: `2026-07-19 12:35:47 JST`
- Snapshot: `20260719123547`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719123547.md](../documentation_index_20260719123547.md)
- Requirements: [phase_1e_thinking_presentation_requirements_20260719123547.md](../requirements/phase_1e_thinking_presentation_requirements_20260719123547.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719123547.md](../architecture/phase_1e_thinking_presentation_architecture_20260719123547.md)
- Proposed ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md)
- Previous Phase Final Review: [designer_review_phase_1d_final_20260719122035.md](designer_review_phase_1d_final_20260719122035.md)
- supersedes: なし（Phase 1-E Handoff新規系列）

## 1. Handoff Conclusion

Phase 1-Eは、Existing Model Portを壊さず、後段へ独立Presentation Moduleを追加するPhaseである。

```text
Raw Model Output
  → Model-declared Output Parser
  → Reasoning／Final Normalization
  → Hidden／Visible Renderer
  → CLI Display
```

本Handoffは実装手順を前もって共有するDraftである。

Proposed ADRのAccepted後継版と、ユーザーによる明示的なPhase 1-E実装解禁まで、実装者はSource／Config／Testを変更しない。

## 2. Required Reading Order

1. [documentation_index_20260719123547.md](../documentation_index_20260719123547.md)
2. [phase_1e_thinking_presentation_requirements_20260719123547.md](../requirements/phase_1e_thinking_presentation_requirements_20260719123547.md)
3. [phase_1e_thinking_presentation_architecture_20260719123547.md](../architecture/phase_1e_thinking_presentation_architecture_20260719123547.md)
4. ADR-0014のAccepted後継版（作成後に最新Indexから参照）
5. [designer_review_phase_1d_final_20260719122035.md](designer_review_phase_1d_final_20260719122035.md)
6. [phase_1d_response_language_architecture_20260719041847.md](../architecture/phase_1d_response_language_architecture_20260719041847.md)
7. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
8. [documentation_rules_20260718193435.md](../requirements/documentation_rules_20260718193435.md)

ProposedとAcceptedが両方存在する場合は、最新Indexが示すAccepted後継版を正本とする。

## 3. Authorization Gate

実装前に次の両方を必須とする。

1. ADR-0014 Decisionのユーザー承認
2. Phase 1-E実装開始のユーザー明示許可

実装時の想定Write Scope：

```text
src/
tests/
config/application.toml
config/models/qwen3_4b_q4_k_m.toml
docs/handoffs/implementer_status_phase_1e_*
```

Dependency追加、`pyproject.toml`変更、`uv.lock`変更は想定しない。必要になった場合は実装を拡大せず、理由を設計者とユーザーへ返す。

## 4. Locked Decisions候補

Accepted ADRで変更されない場合、次をLockedとする。

```text
Thinking Execution Default : disabled
Visibility Default         : hidden
Display Label Default      : 推論
Raw Persistence            : disabled only
Application Schema         : 2
Deployment Schema          : 3 unchanged
Model Definition Schema    : 2
Parser Selection           : Definition parser_key
Parser Hardcoding          : 禁止
Raw Model Port Contract    : 維持
Automatic Sampling Switch : 禁止
New Dependency             : なし
```

## 5. Required User-facing Behavior

### Default

```text
thinking_mode=disabled
visibility=hidden
```

Current Final-only CLI動作を維持する。

### Thinking Hidden

```bash
margpa-llm generate --prompt "..." --thinking --hide-thinking
```

Thinking Executionは`enabled`だが、stdoutにCanonical TagまたはReasoningを出さずFinalだけを表示する。

### Thinking Visible

```bash
margpa-llm generate \
  --prompt "..." \
  --thinking \
  --show-thinking \
  --thinking-label "推論"
```

Conceptual Output：

```text
<推論>...</推論>
Final Answer
```

### Separation

`--show-thinking`はThinking ExecutionをONにしない。`--thinking`はVisibilityをVisibleにしない。

## 6. Step A: Regression Fixture

変更前に次をTestで固定する。

- `GenerationResult.content`はRaw Text
- `GenerationChunk.text_delta`はRaw Delta
- Existing `--thinking／--no-thinking`がGeneration Overrideになる
- Existing DefaultはThinking Disabled
- Streaming Cancel／Close／Usage／Finish
- Phase 1-D `ja／en／auto`

## 7. Step B: Config Migration

### Application

`config/application.toml`：

```toml
schema_version = "2"

[presentation.thinking]
visibility = "hidden"
display_label = "推論"
persistence = "disabled"
```

### Environment

```text
MARGPA_THINKING_VISIBILITY
MARGPA_THINKING_LABEL
```

### Explicit

Bootstrapへ次を渡す。

```text
thinking_visibility
thinking_label
```

### Source

```text
visibility_source
display_label_source
persistence_source
```

Generic Deep Mergeを使用しない。

## 8. Step C: Model Definition Migration

`config/models/qwen3_4b_q4_k_m.toml`：

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Definition File SHA-512はLoaderが新Contentから再計算するExisting方式を維持する。Model Artifact SHA-512は変更しない。

## 9. Step D: Presentation Module

次を作成する。

- Presentation Contract
- Parser Port
- Parser Registry
- Plain Text Parser
- Tagged Stateful Parser
- Renderer
- Presentation Service

Model Backend Adapter内にDisplay Logicを追加しない。

## 10. Step E: Parser Requirements

### Recognition

- Optional Leading Whitespace + Leading Opening DelimiterだけをProtocolとして認識
- OpeningなしはPlain Final
- First ClosingでReasoning終了
- Final Contentを無断変更しない

### Streaming

- Stateful
- Delimiter Split対応
- Minimum Suffix Buffer
- Hidden No-flash
- 1-character Chunk対応
- Empty Delta対応

### Malformed

- Unclosed Status／Warning
- HiddenでReasoningを非表示
- VisibleでDisplay Closing Tagを補完
- Extra Delimiterを黙って削除しない

## 11. Step F: CLI

追加：

```text
--show-thinking
--hide-thinking
--thinking-label
```

`--show-thinking`と`--hide-thinking`をMutually Exclusiveにする。

Non-streamingとStreamingの両方がPresentation Serviceを使う。CLI内にCanonical Tag文字列をハードコードしない。

## 12. Step G: Observability

`model-info`に次を追加する。

- Effective Presentation Policy
- Field別Source
- Parser Key
- Application Schema
- Model Definition Schema

Display Labelは日本語を保持する。JSON OutputはExistingの`ensure_ascii=False`を維持する。

## 13. Candidate File Scope

Architecture正本のCandidate File Scopeを参照する。

特に次の境界を守る。

```text
Change Expected:
  config/application.toml
  config/models/qwen3_4b_q4_k_m.toml
  bootstrap config／parser composition
  new presentation module
  CLI
  tests

Keep Stable:
  model_port.py
  llama_cpp adapter／stream
  local_macos_arm64.toml
  platform_registry.toml
  pyproject.toml
  uv.lock
```

## 14. Required Test Matrix

### Config

- Schema `2`
- Field Ownership
- Precedence
- Source
- Invalid Value
- Label Validation

### Protocol

- Plain Parser
- Tagged Parser
- Unknown Key
- Invalid Delimiter
- Model Key／Architecture非依存

### Parser／Renderer

- Plain
- Complete
- Unclosed
- Extra Tag
- Hidden
- Visible
- Custom Label
- All Delimiter Splits
- One-character Chunks
- Streaming／Non-streaming Parity

### CLI

- Execution／Visibility Independence
- Flag Exclusivity
- Environment／CLI Override
- `model-info`
- Streaming／Non-streaming

### Regression／Native

- Ruff Format／Check
- Mypy Strict
- Default Pytest
- Compileall
- Environment Verification
- Bash Syntax
- `uv lock --check`
- Exact Offline Dry Run
- Metal Model Smoke
- Real CLI Hidden
- Real CLI Visible + Custom Label
- Phase 1-D `ja／en／auto`
- Cancel後の再Generation

## 15. Native Test Guidance

Model Outputは確率的である。Native TestでReasoning文章の完全一致を要求しない。

必須の判定：

- Hiddenで`<think>`／`</think>`がstdoutへ出ない
- HiddenでParserが検出したReasoningがstdoutへ出ない
- VisibleでCustom Labelが使われる
- VisibleでCanonical TagがDisplay Tagとして残らない
- Final Answerが存在する（ModelがLength終了したCaseはFinish Reasonを報告）

NativeでProtocolが生成されないまれなCaseは、Deterministic Parser Testを不合格とせず、Runtime ObservationとしてStatusに記録する。

## 16. Implementation Status Format

実装完了後は新Timestampで次を作成する。

```text
docs/handoffs/implementer_status_phase_1e_thinking_presentation_YYYYMMDDHHMMSS.md
```

必須記載：

- 実装Summary
- Changed／Added Files
- Schema Migration
- Parser／Renderer Structure
- Config／Environment／CLI Precedence
- All Test Commandsと結果
- Native Hidden／Visible Evidence
- Raw Persistenceが追加されていないこと
- Model Artifact Hash不変
- Dependency不変
- Known Limitation
- Acceptance Criteria対応表
- Review依頼

## 17. Stop／Escalation Conditions

次のいずれかが発生したら、独断でScopeを拡大せず設計者へ返す。

- Model Port Contractの破壊的変更が必要
- llama.cpp AdapterへDisplay Policyを入れる必要がある
- External Dependencyが必要
- Raw Reasoningの永続保存が必要
- Unknown ParserをSilent Fallbackしたい
- Hidden No-flashを満たせない
- Current Mac／Metal Regression
- Phase 1-D Language Regression
- Model FileまたはArtifact Hash変更が必要
- Phase 2以降のComponent Registry／Event Busが必要

## 18. Done Definition

RequirementsのAcceptance Criteria 22項目をすべてEvidence付きで判定でき、実装担当Statusが作成された状態をReview Readyとする。

Phase 1-EのComplete／Accepted判定は設計者役のIndependent Review後に行う。

