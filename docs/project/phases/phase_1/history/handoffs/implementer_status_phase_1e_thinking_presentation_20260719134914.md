# Phase 1-E Thinking Presentation実装状況

- 文書ID: `implementer_status_phase_1e_thinking_presentation`
- 状態: `implementation_complete_review_requested`
- 作成日時: `2026-07-19 13:49:14 JST`
- 更新日時: `2026-07-19 13:49:14 JST`
- 作成担当: 実装者役担当Task
- 対象: 設計者役担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260719130303.md](../documentation_index_20260719130303.md)
- Implementer Handoff: [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
- Requirements: [phase_1e_thinking_presentation_requirements_20260719130303.md](../requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719130303.md](../architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
- Accepted ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- Previous Phase Final Review: [designer_review_phase_1d_final_20260719122035.md](designer_review_phase_1d_final_20260719122035.md)
- supersedes: なし（Phase 1-E初回Status）

## 1. 結論

Phase 1-EのThinking Execution／Protocol Parsing／Presentation／Persistence分離を実装した。

```text
Application Config Schema 2                   : Pass
Model Definition Schema 2                    : Pass
Deployment Profile Schema 3不変              : Pass
Model-declared Parser Registry                : Pass
Stateful Streaming／Delimiter Split           : Pass
Hidden No-flash                              : Pass
Visible Default Label「高度推論」             : Pass
Visible Custom Label                         : Pass
Raw Model Port Contract不変                   : Pass
Raw Reasoning Persistenceなし                 : Pass
Sampling暗黙切替なし                          : Pass
Static／Default／Lock／Native Metal Gate      : Pass
Acceptance Criteria                          : 22／22 Pass
```

実装担当側のCompletion Boundaryは成立したと判定し、Designer Reviewを依頼する。

## 2. Implementation Summary

Raw Model Outputの後段へ独立Presentation Moduleを追加した。

```text
Generation Config
  └─ Thinking Execution
           ↓
      Model Port／Backend Adapter
           ↓ Raw GenerationResult／GenerationChunk
Model Definition Schema 2
  └─ output_protocol.thinking
           ↓
      Parser Registry
           ↓
 Tagged Stateful Parser
           ↓ Reasoning／Final Segment
Resolved Presentation Policy
           ↓
      Renderer／Presentation Service
           ↓
      CLI Display
```

Model Port、Inference Service、llama.cpp AdapterはRaw Textを返す既存Contractのままである。CLIのNon-streaming／Streamingだけが後段Presentation Serviceを利用する。

## 3. Schema Migration

### 3.1 Application Config

`config/application.toml`をSchema `1`から`2`へMigrationした。

```toml
schema_version = "2"

[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

既存のModel選択、Model Root、Load、Generation、Response値は維持した。

Default：

```text
thinking_mode : disabled
visibility    : hidden
display_label : 高度推論
persistence   : disabled
```

### 3.2 Model Definition

`config/models/qwen3_4b_q4_k_m.toml`をSchema `1`から`2`へMigrationした。

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Model Artifact Path、Size、SHA-512、Backend、Capability、Native Context Limitは変更していない。Definition File SHA-512だけがSchema Migrationにより更新された。

### 3.3 不変領域

```text
Deployment Profile Schema : 3 unchanged
Platform Registry          : unchanged
Model Artifact             : unchanged
pyproject.toml              : unchanged
uv.lock                     : unchanged
External Dependency        : none added
```

## 4. Parser／Renderer Structure

### 4.1 Contract／Port

追加した主要Contract：

```text
ThinkingVisibility
ThinkingPersistence
ThinkingPresentationSource
ThinkingPresentationConfig
ResolvedThinkingPresentationPolicy
ThinkingContentKind
ThinkingParseStatus
ThinkingSegmentDelta
ThinkingParseWarning
ThinkingParseSummary
NormalizedThinkingOutput
PresentedThinkingOutput
```

Parser PortはSession単位で`feed`と`finish`を提供する。Raw Result／Chunkを書き換えず、Reasoning／Final SegmentとParse Summaryを返す。

### 4.2 Parser Registry

```text
plain_text_v1       → PlainTextOutputParser
tagged_thinking_v1  → TaggedThinkingOutputParser
unknown             → invalid_model_definition
```

Parser選択にModel Key、Architecture、Backend名の分岐はない。Unknown ParserはNative Adapter Construction／Model Loadより前に拒否する。

### 4.3 Stateful Tagged Parser

```text
detecting_prefix
  ├─ opening complete → inside_reasoning
  ├─ mismatch         → plain_text
  └─ terminal partial → plain_text

inside_reasoning
  ├─ closing complete → after_reasoning
  └─ terminal          → unclosed_reasoning

after_reasoning
  └─ remaining text    → final
```

- Optional Leading Whitespace＋Leading OpeningだけをProtocol認識
- Opening／Closing Delimiterの全Chunk Splitに対応
- Delimiterと一致し得る最小SuffixだけをBuffer
- 1文字Chunk／Empty Deltaに対応
- Extra Delimiterを削除せず`malformed_protocol`＋Warning
- Unclosed ReasoningはHiddenで非表示、VisibleでDisplay Closing Tag補完

### 4.4 Renderer／Service

RendererはCanonical Delimiterを知らず、Normalized SegmentとResolved Display Labelだけを扱う。

```text
Hidden:
  REASONING → 表示しない
  FINAL     → そのまま表示

Visible:
  REASONING → <高度推論>...</高度推論>
  FINAL     → そのまま表示
```

Non-streamingとStreamingは同じParser State Machine／Rendererを使用する。

## 5. Config／Environment／CLI Precedence

### 5.1 Visibility

```text
CLI Explicit
  > MARGPA_THINKING_VISIBILITY
  > Application Config
  > Built-in hidden
```

### 5.2 Display Label

```text
CLI Explicit
  > MARGPA_THINKING_LABEL
  > Application Config
  > Built-in 高度推論
```

### 5.3 Persistence

```text
Application Config
  > Built-in disabled
```

`MARGPA_THINKING_PERSISTENCE`、Persistence CLI Overrideは実装していない。

Field別Source：

```text
visibility_source
display_label_source
persistence_source
```

CLI：

```text
Execution:
  --thinking
  --no-thinking

Presentation:
  --show-thinking
  --hide-thinking
  --thinking-label
```

`--show-thinking／--hide-thinking`はMutually Exclusiveである。`--show-thinking`はExecutionをONにせず、`--thinking`はVisibilityをVisibleにしない。

## 6. Changed／Added Files

```text
M config/application.toml
M config/models/qwen3_4b_q4_k_m.toml

A src/margpa_runtime_llm/adapters/output_protocols/__init__.py
A src/margpa_runtime_llm/adapters/output_protocols/plain_text.py
A src/margpa_runtime_llm/adapters/output_protocols/tagged_thinking.py
M src/margpa_runtime_llm/bootstrap/config_loader.py
A src/margpa_runtime_llm/bootstrap/output_parser_registry.py
M src/margpa_runtime_llm/bootstrap/phase1_application.py
M src/margpa_runtime_llm/entrypoints/cli/main.py
M src/margpa_runtime_llm/modules/inference/domain/model_definition.py
M src/margpa_runtime_llm/modules/inference/public.py
A src/margpa_runtime_llm/modules/presentation/__init__.py
A src/margpa_runtime_llm/modules/presentation/public.py
A src/margpa_runtime_llm/modules/presentation/contracts/__init__.py
A src/margpa_runtime_llm/modules/presentation/contracts/thinking.py
A src/margpa_runtime_llm/modules/presentation/ports/__init__.py
A src/margpa_runtime_llm/modules/presentation/ports/thinking_output_parser.py
A src/margpa_runtime_llm/modules/presentation/application/__init__.py
A src/margpa_runtime_llm/modules/presentation/application/thinking_presentation_service.py
A src/margpa_runtime_llm/orchestration/thinking_presentation.py

M tests/contract/model_port/test_model_port_contract.py
M tests/integration/llama_cpp/test_phase1b_runtime.py
M tests/unit/inference/test_cli.py
M tests/unit/inference/test_config_and_registry.py
M tests/unit/inference/test_deployment_platform.py
A tests/unit/presentation/test_thinking_presentation.py

A docs/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md
```

次は変更していない。

```text
src/margpa_runtime_llm/modules/inference/ports/model_port.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py
config/profiles/local_macos_arm64.toml
config/platforms/platform_registry.toml
scripts/
pyproject.toml
uv.lock
```

## 7. Deterministic Test Evidence

```text
Application Schema 2／Old Schema拒否                 : Pass
Model Definition Schema 2／Old Schema拒否            : Pass
Default hidden／高度推論／disabled                    : Pass
Field Ownership／Precedence／Source                  : Pass
Invalid Visibility／Label／Persistence               : Pass
Plain／Tagged／Unknown Parser                        : Pass
Invalid／Equal／Control-character Delimiter          : Pass
Model Key／Architecture非依存                        : Pass
Plain／Complete／Unclosed／Malformed                 : Pass
Hidden／Visible／Default／Custom Label               : Pass
Opening／Closingを含む全Single Split Position        : Pass
1文字Chunk／Empty Delta                              : Pass
Hidden No-flash                                     : Pass
Streaming／Non-streaming Parity                      : Pass
Raw GenerationResult／GenerationChunk不変            : Pass
Execution／Visibility独立                            : Pass
Sampling Parameter非連動                            : Pass
CLI Flag Exclusivity／Safe Error                     : Pass
Unknown Parser Pre-load Rejection                    : Pass
Cancel／Close／Usage／Finish Regression              : Pass
Phase 1-D ja／en／auto Regression                    : Pass
```

## 8. Static／Default／Environment／Lock Gate

```text
Ruff Format Check          : Pass／68 files
Ruff Check                 : Pass
mypy --strict              : Pass／68 source files
compileall                 : Pass
bash -n Setup Recipe       : Pass
Default pytest             : 161 passed, 2 deselected
Environment Verification  : Pass
```

Environment：

```text
Python                    : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python          : 0.3.34
GPU Offload Support       : true
Metal System Info         : present
Dependency Version Match  : true
Out-of-scope Package      : absent
```

Dependency Gate：

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

## 9. Native Metal／CLI Evidence

Sandbox外のNative macOS／Apple Silicon arm64／Metal環境で実行した。

```text
.venv/bin/pytest -q -m model_smoke
  2 passed, 161 deselected
```

Real `model-info`：

```text
application_schema_version      : 2
model_definition_schema_version : 2
thinking_mode                   : disabled
visibility                      : hidden
display_label                   : 高度推論
persistence                     : disabled
visibility_source               : application
display_label_source            : application
persistence_source              : application
parser_key                      : tagged_thinking_v1
device                          : gpu／metal
gpu_offload                     : true
```

Real CLI Structural Evidence：

```text
Hidden／Non-streaming:
  Thinking Execution : enabled
  Reasoning Display  : none
  Canonical Tag Leak : none
  Final              : 2

Visible／Non-streaming:
  Thinking Execution : enabled
  Opening Label      : <高度推論>
  Closing Label      : </高度推論>
  Canonical Tag Leak : none
  Final              : 2

Visible／Streaming／Custom:
  Thinking Execution : enabled
  Opening Label      : <思考過程>
  Closing Label      : </思考過程>
  Canonical Tag Leak : none
  Final              : 2
```

Raw Reasoning本文はPersistence Policyに従い、本Statusへ記録していない。

Phase 1-D Regression：

```text
Default ja  : 成功
Explicit en : success
auto        : OK
```

Production Acceptance：

```text
Success                         : true
Load including SHA-512          : 2.4690 seconds
Generation Result               : フェーズ1-B生産ランタイム成功
Generation Speed                : 26.45 tokens／second
Explicit Stream Terminal State  : cancelled
Post-cancel Generation          : OK／stop
Unload                          : 0.0469 seconds
Detected Device                 : gpu／metal
Artifact Digest Verified        : true
```

## 10. Raw Persistence／Boundary Evidence

Phase 1-EのPresentation／Output Protocol／Resolver内にFile／JSONL／Database Writerは存在しない。

```text
Raw Reasoning Persistence : disabled only
Memory上のParser Buffer   : temporary
Visible stdout            : user explicit opt-in
Disk Persistence          : none
```

Model Backend AdapterとModel Portに次は存在しない。

- Display Label
- Thinking Visibility
- Parser Key分岐
- Canonical Tag置換
- Presentation Policy

CLIにもCanonical `<think>`文字列またはDefault Label文字列をハードコードしていない。

## 11. Hash／Dependency不変

```text
Application Config SHA-512:
928888197b39c066b3e0befc08ba490c166752eae76c9c07fad47f48367dc851759642b5f2243349a1ab7fdc8d85ffcabcc5e39e93c0fac536cfbb64e48434e5

Model Definition SHA-512:
e41866e73a1847abbf973f39b6b26038d30454277b1d9fb6a278b9f165af7de9e00695df79c48e3d5b9c53f84c6e6aba5cafee000ac895e0d643035cb2a171d2

Model Artifact SHA-512（不変）:
f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb

Mac Deployment Profile SHA-512（不変）:
861aa54e159285a5445df853b260b2465194a93bc2c254d3cfd9ec4b58c4fc6c1af0dd1ba7d80251a5e46f9c886fe2205d7931b346709002edb2e7d9f9ce2b40

Platform Registry SHA-512（不変）:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256（不変）:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256（不変）:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

Definition File SHA-512は意図したSchema Migrationにより変化し、Runtime InfoとLoader再計算値が一致した。Model Artifact SHA-512は不変である。

## 12. Known Limitation／Runtime Observation

1. Thinking Protocol生成はModel出力に依存する。最初のNative Promptでは128 Token上限までにClosing／Finalへ到達せず、Hidden表示は空となった。Canonical Reasoningの漏洩はなく、決定論的Testでは`unclosed_reasoning`として扱うことを確認した。
2. HiddenはLeading Canonical Thinking SectionのPresentation制御であり、Secret Redaction／Prompt Injection Guardではない。
3. Extra DelimiterはUser Contentの可能性を考慮して削除せず、`malformed_protocol`／Warningとして観測する。
4. Parse Status／WarningはPresentation Contractから取得できるが、Raw Reasoning本文は保存しない。
5. `高度推論`はDisplay Channel Labelであり、Reasoning品質、正しさまたは真の内部推論を保証しない。

いずれもRequirementsに記録された非Blocker／Scope境界である。

## 13. Acceptance Criteria 22項目対応表

| # | Criteria | Result | Evidence |
|---:|---|---|---|
| 1 | ExecutionとVisibilityが独立 | Pass | CLI独立Test／Native Hidden・Visible |
| 2 | Persistenceが独立しdisabled固定 | Pass | Enum／Resolver／Override非実装Test |
| 3 | Application Schema 2 Strict | Pass | Config／Old Schema／Unknown Field Test |
| 4 | Deployment Schema 3不変 | Pass | Hash／Ownership Test |
| 5 | Default disabled／hidden／高度推論／disabled | Pass | Config／Resolver／model-info |
| 6 | Visibility／Label Env・CLI Override | Pass | Field別Precedence／CLI Test |
| 7 | Field別Source確認 | Pass | Contract／model-info／Test |
| 8 | Canonical DelimiterとDisplay Label分離 | Pass | Model Definition／Renderer Boundary |
| 9 | Model Definition Parser Keyで選択 | Pass | Registry／Bootstrap Test |
| 10 | Model／Architecture／Backend Hardcodeなし | Pass | Parser Registry Source Search |
| 11 | Non-streaming正規化 | Pass | Plain／Complete／Malformed Test |
| 12 | Streaming Delimiter Split対応 | Pass | 全Split Position／1文字Chunk Test |
| 13 | Hidden Streaming No-flash | Pass | Deterministic No-flash Test |
| 14 | Visible Default／Custom Label | Pass | Unit／Real CLI Non-stream・Stream |
| 15 | Malformed決定論処理／Warning | Pass | Unclosed／Extra Delimiter Test |
| 16 | Raw Result／Chunk不変 | Pass | Model Port Contract／Presentation Test |
| 17 | Finish／Usage／Cancel／Close保持 | Pass | Existing Contract／CLI／Native Acceptance |
| 18 | Raw Reasoning新規永続保存なし | Pass | Source Search／Writerなし |
| 19 | Thinking FlagでSampling非変更 | Pass | CLI Sampling Regression Test |
| 20 | 新規External Dependencyなし | Pass | pyproject／uv.lock Hash不変 |
| 21 | Static／Default Test Pass | Pass | 161 passed／2 deselected |
| 22 | Current Mac／Metal非Regression | Pass | 2 Native Test／Real CLI／Acceptance |

## 14. 設計者へのReview依頼

次を確認し、Phase 1-Eの最終受入を判定してほしい。

1. Execution／Parsing／Presentation／Persistenceの4責務分離
2. Application／Model Definition Schema `2` Migration
3. Model-declared Parser RegistryとPre-load Error
4. Stateful Streaming Parser／Hidden No-flash
5. RendererのCanonical Protocol非依存
6. Default `高度推論`／Custom Label
7. Raw Model Port／llama.cpp Adapter Contract不変
8. Raw Persistenceなし／Sampling非連動
9. 22 Acceptance CriteriaとStatic／Native Metal Evidence

