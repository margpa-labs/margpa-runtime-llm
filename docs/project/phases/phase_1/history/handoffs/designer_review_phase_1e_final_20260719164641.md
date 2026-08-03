# Phase 1-E Thinking Presentation 最終設計Review

- 文書ID: `designer_review_phase_1e_final`
- 状態: `accepted_phase_1e_complete`
- 作成日時: `2026-07-19 16:46:41 JST`
- 更新日時: `2026-07-19 16:46:41 JST`
- Snapshot: `20260719164641`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-E実装の最終受入
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1e_thinking_presentation_20260719134914.md](implementer_status_phase_1e_thinking_presentation_20260719134914.md)
- 実装Handoff: [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
- 最新Roadmap: [implementation_roadmap_20260719164641.md](../architecture/implementation_roadmap_20260719164641.md)
- 最新共通Handoff: [common_project_handoff_20260719164641.md](common_project_handoff_20260719164641.md)
- 最新Index: [documentation_index_20260719164641.md](../documentation_index_20260719164641.md)
- supersedes: なし（Phase 1-E最終Reviewの新規系列）

## 1. 最終結論

Phase 1-Eを受け入れ、`Complete／Accepted`と判定する。

```text
Blocking Finding           : 0
High Finding               : 0
Medium Finding             : 0
Low Diagnostic Observation : 1
Required Follow-up         : 0
Acceptance Criteria        : 22／22 Pass
Static／Default Gate       : Pass
Dependency／Offline Gate  : Pass
Native Metal Gate          : Pass
Final Decision             : Accepted
```

Phase 1-EのCompletion Boundaryである次が成立した。

- Thinking Execution、Protocol Parsing、Presentation、Persistenceの4責務分離
- Application Config Schema `2`
- Model Definition Schema `2`
- Model Definitionの`parser_key`によるParser選択
- Plain Text／Tagged Thinking Parser
- Stateful Streaming Parser
- Hidden No-flash
- Default `高度推論`／Custom Display Label
- Raw Model Port Contractの維持
- Raw Reasoning永続保存なし
- Thinking FlagによるSampling暗黙変更なし
- Current Mac／Apple Silicon／Metalの非Regression

## 2. Review対象の正本

### Requirements

- [phase_1e_thinking_presentation_requirements_20260719130303.md](../requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)

### Architecture

- [phase_1e_thinking_presentation_architecture_20260719130303.md](../architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)

### ADR／Handoff

- [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](designer_handoff_phase_1e_thinking_presentation_20260719130303.md)

### Implementer Status

- [implementer_status_phase_1e_thinking_presentation_20260719134914.md](implementer_status_phase_1e_thinking_presentation_20260719134914.md)

## 3. Review対象File

### Configuration

```text
config/application.toml
config/models/qwen3_4b_q4_k_m.toml
config/profiles/local_macos_arm64.toml
config/platforms/platform_registry.toml
```

### Source

```text
src/margpa_runtime_llm/adapters/output_protocols/
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/output_parser_registry.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/entrypoints/cli/main.py
src/margpa_runtime_llm/modules/inference/domain/model_definition.py
src/margpa_runtime_llm/modules/inference/public.py
src/margpa_runtime_llm/modules/presentation/
src/margpa_runtime_llm/orchestration/thinking_presentation.py
```

### Stable Boundary

```text
src/margpa_runtime_llm/modules/inference/ports/model_port.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py
```

### Tests

```text
tests/unit/presentation/test_thinking_presentation.py
tests/unit/inference/test_cli.py
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_deployment_platform.py
tests/contract/model_port/test_model_port_contract.py
tests/integration/llama_cpp/test_phase1b_runtime.py
```

## 4. Findings

### 4.1 Blocking／High／Medium

該当なし。

Source変更を要求する設計逸脱、Regression、Raw境界破壊、Reasoning漏洩、Dependency増加は発見されなかった。

### 4.2 Low Diagnostic Observation

`resolve_thinking_presentation_policy`は、Environment由来のFieldが不正であっても、別FieldにExplicit Overrideが存在すると、最終Error Codeを`invalid_request`として分類する。

確認例：

```text
MARGPA_THINKING_VISIBILITY = sometimes   # 不正なEnvironment値
explicit_display_label     = 明示推論     # 正常な別Field
result error code          = invalid_request
```

原因は、Validation ErrorとなったFieldのSourceではなく、いずれかのExplicit Overrideが存在するかでError Codeを選んでいるためである。

影響：

- 不正値そのものは安全に拒否される
- Raw値やPathはErrorへ露出しない
- 正常値のPrecedence／Source Trackingに影響しない
- Phase 1-Eの受入条件には抵触しない
- UI／Config診断を精密化する段階で、Field別Error Attributionへ改善可能

したがって、Phase 1-Eを止めるFindingではなく、将来のConfiguration UX改善候補として記録する。必須Follow-upは発行しない。

### 4.3 Inline Code Comment

修正必須のInline Findingはない。

## 5. Configuration／Schema Review

### 5.1 Application Config

`config/application.toml`はSchema `2`へMigrationされ、次を所有する。

```toml
[generation]
thinking_mode = "disabled"

[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

`ApplicationConfig`は`schema_version: Literal["2"]`および`extra="forbid"`を用いる。旧Schema、未知Field、欠落したPresentation SectionをSilent Acceptanceしない。

### 5.2 Deployment Profile

Deployment ProfileはSchema `3`のまま不変であり、Presentation Fieldを追加できない。PresentationはPlatform固有設定へ混入していない。

### 5.3 Model Definition

Model DefinitionはSchema `2`へMigrationされ、Canonical Protocolを所有する。

```toml
[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Display LabelはModel Definitionへ入っていない。Plain Text ParserはDelimiterを拒否し、Tagged Parserは両Delimiter必須、同一値、空、制御文字を拒否する。

## 6. Four-way Separation Review

```text
Thinking Execution : GenerationParameters／ThinkingMode
Protocol Parsing   : Output Parser Port／Adapter／Registry
Presentation       : Presentation Policy／Renderer／Service
Persistence        : disabled-only Contract
```

`--show-thinking`はGenerationの`thinking_mode`を変更せず、`--thinking`はVisibilityを変更しない。TestとSourceの両方で独立性を確認した。

Persistenceは`ThinkingPersistence.DISABLED`のみを持ち、Environment／CLI Overrideを提供しない。Presentation Module内にFile、JSONL、Database Writerは存在しない。

## 7. Parser／Renderer Review

### 7.1 Parser Selection

ParserはModel Definitionの`parser_key`からComposition Rootで構築される。Model Key、Architecture、Backend名によるParser分岐はない。

Unknown Parserは`LlamaCppModelAdapter` ConstructionおよびModel Load前に`invalid_model_definition`として拒否される。

### 7.2 Stateful Parser

Tagged Parserは次のStateを持つ。

```text
detecting_prefix
inside_reasoning
after_reasoning
plain_text
```

確認した動作：

- Optional Leading Whitespace
- OpeningなしをOriginal Finalへ復元
- Opening／Closing DelimiterのChunk分割
- Minimum Suffix Buffer
- 1文字Chunk／Empty Delta
- Complete／Unclosed／Extra Delimiter
- Extra Delimiterの保持とWarning
- FinishのIdempotency

Non-streamingも同じStreaming SessionへRaw Contentを1回Feedしており、別Parser実装を持たない。

### 7.3 Hidden No-flash

Opening候補を判定中はOutputをBufferし、Reasoning SegmentはHidden Rendererで破棄する。Closing確定後のFinalだけを表示する。

Delimiterが複数Chunkへ分割されてもReasoningやCanonical Tagを先にstdoutへ出さないことをDeterministic Testで確認した。

### 7.4 Visible Rendering

RendererはCanonical Delimiterを知らず、Resolved Display Labelから表示Containerを作る。

```text
Default : <高度推論>...</高度推論>
Custom  : <思考過程>...</思考過程>
```

Unclosed Reasoningでは表示ContainerだけをTerminalで閉じる。Raw Model Outputを修復または上書きしない。

## 8. CLI／Observability Review

CLIは次を分離する。

```text
Execution     : --thinking／--no-thinking
Visibility    : --show-thinking／--hide-thinking
Display Label : --thinking-label
```

Visibility FlagはMutually Exclusiveである。Invalid LabelはRaw値を表示せず、安全なErrorとして拒否する。

`model-info`には次が含まれる。

- Application Schema Version
- Model Definition Schema Version
- Thinking Mode
- Visibility／Display Label／Persistence
- 各FieldのSource
- Parser Key／Canonical Delimiter Definition

JSONは`ensure_ascii=False`を維持し、日本語LabelをUnicode Escapeへ変換しない。

## 9. Stable Raw Boundary Review

`GenerationResult.content`と`GenerationChunk.text_delta`はRaw Model Outputのままであり、Presentation Serviceが後段で表示結果を生成する。

Model Port、llama.cpp Adapter、Stream Adapterには次が存在しない。

- Display Label
- Thinking Visibility
- Parser Key分岐
- Canonical Tag置換
- Presentation Policy

CLIにもCanonical `<think>`／`</think>`はハードコードされていない。

## 10. Acceptance Criteria

| # | Criteria | Result | Independent Evidence |
|---:|---|---|---|
| 1 | ExecutionとVisibilityが独立 | Pass | CLI Source／Unit Test |
| 2 | Persistenceが独立しdisabled固定 | Pass | Enum／Resolver／Override非実装 |
| 3 | Application Schema 2 Strict | Pass | Literal Schema／Old Schema／Unknown Field Test |
| 4 | Deployment Schema 3不変 | Pass | Config Hash／Ownership Test |
| 5 | Default disabled／hidden／高度推論／disabled | Pass | Config／Resolver／model-info Test |
| 6 | Visibility／Label Env・CLI Override | Pass | Precedence／CLI Test |
| 7 | Field別Source確認 | Pass | Contract／model-info Test |
| 8 | Canonical DelimiterとDisplay Label分離 | Pass | Model Definition／Renderer Source Search |
| 9 | Definition Parser Keyで選択 | Pass | Registry／Bootstrap Test |
| 10 | Model／Architecture／Backend Hardcodeなし | Pass | Source Search |
| 11 | Non-streaming正規化 | Pass | Plain／Complete／Malformed Test |
| 12 | Streaming Delimiter Split対応 | Pass | 全Single Split／1文字Chunk Test |
| 13 | Hidden Streaming No-flash | Pass | Deterministic No-flash Test |
| 14 | Visible Default／Custom Label | Pass | Unit／CLI Test／Native Raw Presentation |
| 15 | Malformed決定論処理／Warning | Pass | Unclosed／Extra Delimiter Test |
| 16 | Raw Result／Chunk不変 | Pass | Contract Test／Source Review |
| 17 | Finish／Usage／Cancel／Close保持 | Pass | Contract／CLI／Native Smoke |
| 18 | Raw Reasoning新規永続保存なし | Pass | Source Search／Writerなし |
| 19 | Thinking FlagでSampling非変更 | Pass | CLI Sampling Test |
| 20 | 新規External Dependencyなし | Pass | Dependency File Hash不変 |
| 21 | Static／Default Test Pass | Pass | Independent Gate |
| 22 | Current Mac／Metal非Regression | Pass | Independent Native Gate |

## 11. 独立検証結果

### 11.1 Static／Default

```text
ruff format --check . : Pass／68 files already formatted
ruff check .          : Pass
mypy                  : Pass／68 source files
compileall            : Pass／Temporary Pycache outside Project
bash -n Setup Recipe  : Pass
pytest -q             : Pass／161 passed, 2 deselected
```

### 11.2 Environment／Dependency

```text
Python                         : CPython 3.13.14／arm64／GIL enabled
llama-cpp-python               : 0.3.34
GPU Offload Support            : true
Metal System Info              : present
Dependency Versions Match      : true
Out-of-scope Packages Absent   : true
uv lock --check                : Pass／Resolved 117 packages
uv sync --dry-run --frozen ... : Pass／Checked 115／Would make no changes
```

`uv`の最初のSandbox内実行は、Project外の既存User Cacheを読めず`Operation not permitted`となった。既存Cacheへの読み取りを許可した同一CommandでPassしたため、実装またはLockの不具合とは判定しない。

### 11.3 Native Mac／Metal

```text
pytest -q -m model_smoke
  2 passed, 161 deselected
```

Native Testで確認したもの：

- Qwen3 GGUF Load／SHA-512 Verify
- Apple Silicon arm64／Metal／GPU Offload
- Application Schema `2`
- Model Definition Schema `2`
- Default Presentation Policy
- ja／en／auto Regression
- Thinking Raw OutputのHidden／Visible Presentation
- Canonical Tag非表示
- Stream Cancel／Close
- Cancel後のGeneration
- Unload

## 12. Hash／Dependency確認

```text
Application Config SHA-512:
928888197b39c066b3e0befc08ba490c166752eae76c9c07fad47f48367dc851759642b5f2243349a1ab7fdc8d85ffcabcc5e39e93c0fac536cfbb64e48434e5

Model Definition SHA-512:
e41866e73a1847abbf973f39b6b26038d30454277b1d9fb6a278b9f165af7de9e00695df79c48e3d5b9c53f84c6e6aba5cafee000ac895e0d643035cb2a171d2

Mac Deployment Profile SHA-512:
861aa54e159285a5445df853b260b2465194a93bc2c254d3cfd9ec4b58c4fc6c1af0dd1ba7d80251a5e46f9c886fe2205d7931b346709002edb2e7d9f9ce2b40

Platform Registry SHA-512:
5af43fff30e5cf0716a927e05d1bde74a443e5a0484490a32398421824e3b4cc0539f64578dcc509fe620790686d7473587d7650665f2436b4c988281712d574

pyproject.toml SHA-256:
a46fcd0b61e8db84a5f90ac4459b92bf9ec9deb7d6219ce88d7b22c240b5ecfa

uv.lock SHA-256:
e5efe33d69105547fe0d4f348b6b189b85f7ed55323f8ecd993ef5df7846fee1
```

Model Artifact DigestはNative Runtimeの`artifact_digest_verified = true`で確認した。

## 13. Phase 1全体の状態

Phase 1-AからPhase 1-Eまでの実装Subphaseは、すべて`Complete／Accepted`となった。

ただし、Top-Level Phase 1はまだ完了宣言しない。現在のUser ManualはPhase 1-A／1-Bのみを対象としており、Phase 1-C／1-D／1-Eの操作、Config、Response Language、Thinking Presentationを反映していない。

残るFinalization：

1. Phase 1 User ManualのAccepted後継版を作る。
2. Phase 1-A～1-Eの最終Cross-phase確認を行う。
3. 最新Review／Roadmap／Common Handoff／Indexの整合性を確認する。
4. 設計者役が「Phase 1は完了です。次はPhase 2です」と明示する。
5. 明示直後にPhase 1 Backupを取得・検証する。

したがって、本ReviewはPhase 1-Eの完了判定であり、Top-Level Phase 1の完了宣言ではない。

## 14. Authorization Boundary

本ReviewによりPhase 1-EをAcceptedとする。

本Reviewで実施していないもの：

- Source／Config／Testの修正
- User Manualの更新
- Top-Level Phase 1完了宣言
- Phase 1 Backup Archive／Manifest／Receipt生成
- Phase 2実装

