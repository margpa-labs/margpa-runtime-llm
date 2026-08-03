# Phase 1-E Thinking Presentation 実装担当Handoff

- 文書ID: `designer_handoff_phase_1e_thinking_presentation`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 13:03:03 JST`
- 更新日時: `2026-07-19 13:03:03 JST`
- Snapshot: `20260719130303`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719130303.md](../documentation_index_20260719130303.md)
- Requirements: [phase_1e_thinking_presentation_requirements_20260719130303.md](../requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719130303.md](../architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
- Accepted ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- Previous Phase Final Review: [designer_review_phase_1d_final_20260719122035.md](designer_review_phase_1d_final_20260719122035.md)
- supersedes: `designer_handoff_phase_1e_thinking_presentation_20260719123547.md`

## 1. Handoff Conclusion

Phase 1-EのRequirements／Architecture／ADRはユーザーによりAcceptedとなった。

Default Display Labelは`高度推論`である。

```text
Raw Model Output
  → Model-declared Output Parser
  → Reasoning／Final Normalization
  → Hidden／Visible Renderer
  → CLI Display
```

本Handoffは実装担当への正式な設計引き渡しである。

ただし、正式Handoffの作成と実装開始許可は別である。ユーザーがPhase 1-E実装開始を明示するまで、Source／Config／Testを変更しない。

## 2. Required Reading Order

1. [documentation_index_20260719130303.md](../documentation_index_20260719130303.md)
2. [phase_1e_thinking_presentation_requirements_20260719130303.md](../requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
3. [phase_1e_thinking_presentation_architecture_20260719130303.md](../architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
4. [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
5. [designer_review_phase_1d_final_20260719122035.md](designer_review_phase_1d_final_20260719122035.md)
6. [phase_1d_response_language_architecture_20260719041847.md](../architecture/phase_1d_response_language_architecture_20260719041847.md)
7. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
8. [documentation_rules_20260718193435.md](../requirements/documentation_rules_20260718193435.md)

同一系列では`20260719130303`版を`20260719123547`版より優先する。

## 3. Authorization Gate

Requirements／Architecture／ADR／HandoffはAccepted済みである。

実装に必要な残るGate：

```text
ユーザーによるPhase 1-E実装開始の明示許可
```

実装時のWrite Scope：

```text
src/
tests/
config/application.toml
config/models/qwen3_4b_q4_k_m.toml
docs/handoffs/implementer_status_phase_1e_*
```

Dependency追加、`pyproject.toml`変更、`uv.lock`変更は想定しない。必要になった場合は実装を拡大せず設計者／ユーザーへ返す。

## 4. Locked Decisions

```text
Thinking Execution Default : disabled
Visibility Default         : hidden
Display Label Default      : 高度推論
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

`高度推論`はDisplay Labelであり、Reasoning品質の保証ではない。

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

Thinkingは実行し得るが、stdoutにCanonical Tag／Reasoningを出さずFinalだけを表示する。

### Thinking Visible

```bash
margpa-llm generate \
  --prompt "..." \
  --thinking \
  --show-thinking
```

Default Output：

```text
<高度推論>...</高度推論>
Final Answer
```

Custom：

```bash
margpa-llm generate \
  --prompt "..." \
  --thinking \
  --show-thinking \
  --thinking-label "思考過程"
```

### Separation

`--show-thinking`はThinking ExecutionをONにしない。`--thinking`はVisibilityをVisibleにしない。

## 6. Step A: Regression Fixture

変更前に次をTestで固定する。

- `GenerationResult.content`はRaw Text
- `GenerationChunk.text_delta`はRaw Delta
- `--thinking／--no-thinking`はGeneration Override
- DefaultはThinking Disabled
- Streaming Cancel／Close／Usage／Finish
- Phase 1-D `ja／en／auto`

## 7. Step B: Application Config Migration

```toml
schema_version = "2"

[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

Environment：

```text
MARGPA_THINKING_VISIBILITY
MARGPA_THINKING_LABEL
```

Explicit Bootstrap Override：

```text
thinking_visibility
thinking_label
```

Source：

```text
visibility_source
display_label_source
persistence_source
```

Generic Deep Mergeを使用しない。

## 8. Step C: Model Definition Migration

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Definition File SHA-512はLoaderが再計算するExisting方式を維持する。Model Artifact SHA-512は変更しない。

## 9. Step D: Presentation Module

作成するもの：

- Presentation Contract
- Parser Port
- Parser Registry
- Plain Text Parser
- Tagged Stateful Parser
- Renderer
- Presentation Service

Model Backend Adapter内にDisplay Logicを追加しない。

## 10. Step E: Parser

Recognition：

- Optional Leading Whitespace + Leading Opening DelimiterだけをProtocolとして認識
- OpeningなしはPlain Final
- First ClosingでReasoning終了
- Final Contentを無断変更しない

Streaming：

- Stateful
- Delimiter Split対応
- Minimum Suffix Buffer
- Hidden No-flash
- 1-character Chunk
- Empty Delta

Malformed：

- Unclosed Status／Warning
- HiddenでReasoning非表示
- VisibleでDisplay Closing Tag補完
- Extra Delimiterを無断削除しない

## 11. Step F: CLI

```text
--show-thinking
--hide-thinking
--thinking-label
```

`--show-thinking`と`--hide-thinking`をMutually Exclusiveにする。

Non-streaming／Streamingの両方がPresentation Serviceを使う。CLIにCanonical Tag文字列をハードコードしない。

## 12. Step G: Observability

`model-info`に次を追加する。

- Effective Presentation Policy
- Default／Resolved Display Label
- Field別Source
- Parser Key
- Application Schema
- Model Definition Schema

JSONは`ensure_ascii=False`を維持する。

## 13. Candidate File Scope

```text
Change Expected:
  config/application.toml
  config/models/qwen3_4b_q4_k_m.toml
  bootstrap config／parser composition
  model definition contract
  new presentation module
  output protocol adapters
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
- Default `高度推論`
- Field Ownership／Precedence／Source
- Invalid Visibility／Label／Persistence

### Protocol

- Plain／Tagged Parser
- Unknown Key／Invalid Delimiter
- Model Key／Architecture非依存

### Parser／Renderer

- Plain／Complete／Unclosed／Extra Tag
- Hidden／Visible
- Default／Custom Label
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
- Real CLI Visible + Default `高度推論`
- Real CLI Visible + Custom Label
- Phase 1-D `ja／en／auto`
- Cancel後の再Generation

## 15. Native Test Guidance

Native TestでReasoning文章の完全一致を要求しない。

必須判定：

- HiddenでCanonical Tag／Reasoningがstdoutへ出ない
- Visibleで`<高度推論>...</高度推論>`が使われる
- Custom Labelが使われる
- Canonical TagがDisplay Tagとして残らない
- Final Answerが存在する

Protocolが生成されない確率的CaseはRuntime ObservationとしてStatusに記録し、Deterministic Parser Testと分離する。

## 16. Implementation Status

実装完了後は新Timestampで次を作成する。

```text
docs/handoffs/implementer_status_phase_1e_thinking_presentation_YYYYMMDDHHMMSS.md
```

必須記載：

- Implementation Summary
- Changed／Added Files
- Schema Migration
- Parser／Renderer Structure
- Config／Environment／CLI Precedence
- Test Commands／Results
- Native Hidden／Visible Evidence
- Default `高度推論` Evidence
- Raw Persistenceなし
- Model Artifact Hash不変
- Dependency不変
- Known Limitation
- Acceptance Criteria 22項目対応表
- Review依頼

## 17. Stop／Escalation Conditions

- Model Port Contractの破壊的変更が必要
- llama.cpp AdapterへDisplay Policyを入れる必要がある
- External Dependencyが必要
- Raw Reasoningの永続保存が必要
- Unknown ParserのSilent Fallbackが必要
- Hidden No-flashを満たせない
- Current Mac／Metal Regression
- Phase 1-D Language Regression
- Model File／Artifact Hash変更が必要
- Phase 2以降のComponentが必要

発生時はScopeを独断拡大せず、設計者／ユーザーへ返す。

## 18. Done Definition

RequirementsのAcceptance Criteria 22項目をEvidence付きで判定でき、Implementer Statusが作成された状態をReview Readyとする。

Phase 1-EのComplete／Accepted判定は設計者役のIndependent Review後に行う。

