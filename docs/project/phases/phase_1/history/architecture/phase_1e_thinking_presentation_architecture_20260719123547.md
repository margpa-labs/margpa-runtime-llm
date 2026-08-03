# Phase 1-E Thinking Presentation Architecture

- 文書ID: `phase_1e_thinking_presentation_architecture`
- 状態: `proposed_ready_for_user_review`
- 作成日時: `2026-07-19 12:35:47 JST`
- 更新日時: `2026-07-19 12:35:47 JST`
- Snapshot: `20260719123547`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-E、Presentation Module、Output Parser、Streaming State Machine、CLI
- 正本言語: 日本語
- Requirements: [phase_1e_thinking_presentation_requirements_20260719123547.md](../requirements/phase_1e_thinking_presentation_requirements_20260719123547.md)
- Proposed ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md)
- Phase 1-D Architecture: [phase_1d_response_language_architecture_20260719041847.md](phase_1d_response_language_architecture_20260719041847.md)
- supersedes: `response_language_and_thinking_output_policy_20260719013109.md`のThinking候補設計部分

## 1. Architecture Conclusion

Model RuntimeのRaw Contractは変更せず、Model Portの後ろに独立したPresentation Moduleを配置する。

```text
Generation Config
  └─ Thinking Execution
           ↓
      Model Port
           ↓ Raw GenerationResult／GenerationChunk
Model Output Protocol Definition
           ↓
      Parser Registry
           ↓
 Tagged Thinking Parser
           ↓ Normalized Segment
Thinking Presentation Policy
           ↓
 Presentation Renderer
           ↓ Display Delta／Display Result
        CLI
```

この境界により、将来のWeb UI／APIはCLI固有文字列操作を再実装せず、同じPresentation Serviceを使用できる。

## 2. Dependency Direction

```text
entrypoints/cli
  → modules/presentation/application
  → modules/presentation/contracts
  → modules/inference/public

adapters/output_protocols
  → modules/presentation/ports
  → modules/presentation/contracts

bootstrap
  → parser registry／factory
  → application config composer
```

禁止する依存：

```text
inference core → CLI
model backend adapter → display label
presentation core → llama_cpp
deployment profile → presentation policy
model definition → user display label
```

## 3. Directory候補

```text
src/margpa_runtime_llm/
  modules/
    presentation/
      __init__.py
      public.py
      contracts/
        __init__.py
        thinking.py
      ports/
        __init__.py
        thinking_output_parser.py
      application/
        __init__.py
        thinking_presentation_service.py
  adapters/
    output_protocols/
      __init__.py
      plain_text.py
      tagged_thinking.py
  bootstrap/
    output_parser_registry.py
```

Output ProtocolはBackendと異なる軸であるため、`adapters/model_backends/llama_cpp/`内へParserを置かない。

## 4. Stable Raw Boundary

Existingの次を維持する。

```python
class GenerationResult:
    content: str

class GenerationChunk:
    text_delta: str
```

Model Port／Inference Service／llama.cpp AdapterはRaw Model Outputを返す。

Phase 1-Eで`GenerationResult.content`をFinal Contentだけに置き換えない。これにより、Backend Contract、Token Usage、Timing、Governanceの将来介入点を安定させる。

## 5. Configuration Architecture

### Application Schema

```text
Phase 1-D : 1
Phase 1-E : 2
```

Schema `2`の追加Section：

```toml
[presentation.thinking]
visibility = "hidden"
display_label = "推論"
persistence = "disabled"
```

### Field Owner

| Field | Owner | Deployment Override |
|---|---|---:|
| `generation.thinking_mode` | Application／Request | 不可 |
| `presentation.thinking.visibility` | Application／Request | 不可 |
| `presentation.thinking.display_label` | Application／Request | 不可 |
| `presentation.thinking.persistence` | Application Policy | 不可 |
| Canonical Delimiter | Model Definition | 不可 |
| Parser Key | Model Definition | 不可 |

## 6. Configuration Contract

候補Contract：

```python
class ThinkingVisibility(StrEnum):
    HIDDEN = "hidden"
    VISIBLE = "visible"

class ThinkingPersistence(StrEnum):
    DISABLED = "disabled"

class ThinkingPresentationSource(StrEnum):
    BUILT_IN_DEFAULT = "built_in_default"
    APPLICATION = "application"
    ENVIRONMENT = "environment"
    EXPLICIT = "explicit"

class ThinkingPresentationConfig(ImmutableContract):
    visibility: ThinkingVisibility = ThinkingVisibility.HIDDEN
    display_label: str = "推論"
    persistence: Literal[ThinkingPersistence.DISABLED] = ThinkingPersistence.DISABLED

class PresentationConfig(ImmutableContract):
    thinking: ThinkingPresentationConfig = ThinkingPresentationConfig()

class ResolvedThinkingPresentationPolicy(ImmutableContract):
    visibility: ThinkingVisibility
    display_label: str
    persistence: ThinkingPersistence
    visibility_source: ThinkingPresentationSource
    display_label_source: ThinkingPresentationSource
    persistence_source: ThinkingPresentationSource
```

`ApplicationConfig`に`presentation`を追加し、`EffectivePhase1Config`にResolved Policyを追加する。

## 7. Resolver

候補Location：

```text
src/margpa_runtime_llm/orchestration/thinking_presentation.py
```

Field別に解決する。Generic Deep Mergeを使用しない。

```text
Visibility:
  Explicit > Environment > Application > Built-in

Display Label:
  Explicit > Environment > Application > Built-in

Persistence:
  Application > Built-in
```

Environment：

```text
MARGPA_THINKING_VISIBILITY
MARGPA_THINKING_LABEL
```

`MARGPA_THINKING_MODE`はGeneration Resolverが引き続き所有する。

## 8. Display Label Validation

ValidationはContractまたは専用Validatorで一度だけ行う。CLI Rendererで再解釈しない。

```text
length             : 1..64
leading/trailing   : 禁止
forbidden literal  : < > /
forbidden category : Control／CR／LF
Unicode            : 許可
```

Error時は`invalid_configuration`または`invalid_request`の安全なMessageを返し、入力Labelを無条件にLogへ出さない。

## 9. Model Definition Migration

Current Qwen3 Model DefinitionをSchema `2`へMigrationする。

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

候補Contract：

```python
class ThinkingOutputProtocolDefinition(ImmutableContract):
    parser_key: str
    opening_delimiter: str | None = None
    closing_delimiter: str | None = None

class ModelOutputProtocolDefinition(ImmutableContract):
    thinking: ThinkingOutputProtocolDefinition
```

Parser Key別のValidation：

```text
plain_text_v1:
  delimitersなし

tagged_thinking_v1:
  opening／closing必須
  non-empty
  同一値禁止
  CR／LF／制御文字禁止
```

## 10. Parser Port

候補：

```python
class ThinkingOutputParserSession(Protocol):
    def feed(self, text_delta: str) -> tuple[ThinkingSegmentDelta, ...]: ...
    def finish(self) -> ThinkingParseSummary: ...

class ThinkingOutputParser(Protocol):
    def start(self) -> ThinkingOutputParserSession: ...
```

Parser Factory／Registryは`parser_key`でParserを生成する。

```python
build_output_parser(
    definition.output_protocol.thinking
) -> ThinkingOutputParser
```

Unknown KeyはApplication Build時に拒否する。`if model_key == ...`または`if architecture == "qwen3"`の分岐は作らない。

## 11. Normalized Contract

```python
class ThinkingContentKind(StrEnum):
    REASONING = "reasoning"
    FINAL = "final"

class ThinkingParseStatus(StrEnum):
    PLAIN_TEXT = "plain_text"
    COMPLETE = "complete"
    UNCLOSED_REASONING = "unclosed_reasoning"
    MALFORMED_PROTOCOL = "malformed_protocol"

class ThinkingSegmentDelta(ImmutableContract):
    kind: ThinkingContentKind
    text_delta: str

class ThinkingParseWarning(ImmutableContract):
    code: str
    safe_message: str

class ThinkingParseSummary(ImmutableContract):
    status: ThinkingParseStatus
    warnings: tuple[ThinkingParseWarning, ...]

class NormalizedThinkingOutput(ImmutableContract):
    reasoning_content: str | None
    final_content: str
    parse_status: ThinkingParseStatus
    warnings: tuple[ThinkingParseWarning, ...]
```

`NormalizedThinkingOutput`にRaw Output全体を複製保持しない。Rawは元の`GenerationResult`が所有する。

## 12. Tagged Parser State Machine

```text
detecting_prefix
  ├─ opening delimiter complete → inside_reasoning
  ├─ prefix mismatch            → plain_text
  └─ terminal partial prefix   → plain_text

inside_reasoning
  ├─ closing delimiter complete → after_reasoning
  └─ terminal without closing   → unclosed_reasoning

after_reasoning
  └─ all remaining text         → final segment
```

Openingの前のOptional WhitespaceはPrefix判定のため一時Bufferする。Openingがないと判断した場合は、Whitespaceも含めてOriginal Final Textへ戻す。

Delimiter候補と一致するSuffixだけをBufferし、不要に全OutputをBufferしない。

## 13. Renderer

RendererはNormalized Segmentだけを受け取る。Canonical Delimiterを知らない。

### Hidden

```text
REASONING segment → 破棄
FINAL segment     → そのままDisplay
```

### Visible

```text
First REASONING segment:
  <{display_label}> + text

Following REASONING segment:
  text

Reasoning completed:
  </{display_label}>

FINAL segment:
  text
```

OpeningがありClosingなしでTerminalに達した場合、Visible RendererはDisplay Closing Tagを補完する。これはModel Raw Outputの修復ではなく、表示Containerを閉じるためのPresentation処理である。

## 14. Presentation Service

候補API：

```python
class ThinkingPresentationService:
    def present_text(
        self,
        raw_content: str,
        policy: ResolvedThinkingPresentationPolicy,
    ) -> PresentedThinkingOutput: ...

    def start_stream(
        self,
        policy: ResolvedThinkingPresentationPolicy,
    ) -> ThinkingPresentationSession: ...
```

```python
class PresentedThinkingOutput(ImmutableContract):
    display_content: str
    normalized: NormalizedThinkingOutput
```

Streaming Session：

```python
display_deltas = session.feed(raw_delta)
terminal = session.finish()
```

Non-streamingも同じState MachineにRaw Textを1回FeedしてFinishする。別Regex実装を作らない。

## 15. CLI Integration

CLIは次のみを担当する。

- CLI Argument取得
- Presentation OverrideをBootstrapへ渡す
- Presentation Serviceが返したDisplay Deltaをstdoutへ描画
- 既存Cancel操作

CLIで`str.replace("<think>", ...)`を行わない。

Non-streaming：

```text
Raw GenerationResult
  → present_text
  → print(display_content)
```

Streaming：

```text
for raw_chunk in GenerationStream:
  for display_delta in presentation_session.feed(raw_chunk.text_delta):
    print(display_delta)

presentation_session.finish()
```

Underlying `GenerationStream`のCancel／Close／Terminal StateはCLIが引き続き所有する。

## 16. Bootstrap Integration

`Phase1Application`に次の依存を明示的に持たせる候補とする。

```text
service                 : InferenceService
presentation_service    : ThinkingPresentationService
definition              : ModelDefinition
config                  : EffectivePhase1Config
runtime_observation     : RuntimeObservation
```

Composition Sequence：

```text
Load Application Config
  → Resolve Presentation Policy
Load Model Definition
  → Validate Output Protocol
  → Resolve Parser Key
Build Model Adapter
Build Inference Service
Build Presentation Service
Return Phase1Application
```

Parser Key ErrorはModel Load後ではなく、可能な限りModel Artifactの重いLoad前に検出する。

## 17. `model-info`

```json
{
  "effective_config": {
    "generation": {
      "thinking_mode": "disabled"
    },
    "presentation": {
      "thinking": {
        "visibility": "hidden",
        "display_label": "推論",
        "persistence": "disabled",
        "visibility_source": "application",
        "display_label_source": "application",
        "persistence_source": "application"
      }
    }
  },
  "model_output_protocol": {
    "thinking": {
      "parser_key": "tagged_thinking_v1"
    }
  }
}
```

Canonical Delimiter自体の表示は、将来のPublic UIで必須としない。Current Developer CLIではModel Definitionの検証済み値として出力してもよいが、Secretとして扱う必要はない。

## 18. Warning／Error Boundary

### Configuration Error

- Invalid Visibility
- Invalid Display Label
- Unsupported Persistence
- Invalid Delimiter
- Unknown Parser Key

これらはGeneration前に拒否する。

### Runtime Parse Warning

- Unclosed Reasoning
- Unexpected Extra Delimiter
- Malformed Protocol

Parse WarningはRaw GenerationのFinish Reasonを上書きしない。Presentation Result側のWarningとして保持する。

## 19. Security／Privacy Properties

- Hidden ModeはCanonical Leading Reasoning Sectionをstdoutへ出さない
- Prefix／DelimiterがChunk分割されてもFlashさせない
- Custom Labelを制御文字注入に使わせない
- Raw ReasoningをDiskへ新規保存しない
- HiddenはPrompt Injection／Secret Filterではない
- Malformed Contentを完全な安全性境界として利用しない

## 20. Candidate File Scope

```text
config/application.toml
config/models/qwen3_4b_q4_k_m.toml
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/model_registry_loader.py
src/margpa_runtime_llm/bootstrap/output_parser_registry.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/modules/inference/domain/model_definition.py
src/margpa_runtime_llm/modules/presentation/__init__.py
src/margpa_runtime_llm/modules/presentation/public.py
src/margpa_runtime_llm/modules/presentation/contracts/__init__.py
src/margpa_runtime_llm/modules/presentation/contracts/thinking.py
src/margpa_runtime_llm/modules/presentation/ports/__init__.py
src/margpa_runtime_llm/modules/presentation/ports/thinking_output_parser.py
src/margpa_runtime_llm/modules/presentation/application/__init__.py
src/margpa_runtime_llm/modules/presentation/application/thinking_presentation_service.py
src/margpa_runtime_llm/adapters/output_protocols/__init__.py
src/margpa_runtime_llm/adapters/output_protocols/plain_text.py
src/margpa_runtime_llm/adapters/output_protocols/tagged_thinking.py
src/margpa_runtime_llm/orchestration/thinking_presentation.py
src/margpa_runtime_llm/entrypoints/cli/main.py
tests/unit/presentation/
tests/unit/inference/test_config_and_registry.py
tests/unit/inference/test_cli.py
tests/integration/llama_cpp/test_phase1b_runtime.py
```

原則変更しない：

```text
src/margpa_runtime_llm/modules/inference/ports/model_port.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
src/margpa_runtime_llm/adapters/model_backends/llama_cpp/stream.py
config/profiles/local_macos_arm64.toml
config/platforms/platform_registry.toml
pyproject.toml
uv.lock
```

Backend Adapter変更が必要になった場合は、理由と境界をStatusで明記し設計者へ返す。

## 21. Test Architecture

### Pure Unit

- Config Resolver
- Label Validator
- Model Protocol Definition
- Parser Registry
- Plain Text Parser
- Tagged Parser
- Renderer
- Presentation Service

### Property-like Parameterization

Opening／Closing Delimiterの全Split PositionをParameterizeする。

```text
< | think>
<t | hink>
<th | ink>
...
</ | think>
...</think | >
```

1文字ずつのChunkと、全文字を1Chunkで与えるCaseも必須とする。

### Parity

同じRaw Textに対し、任意のChunk分割でのStreaming Display連結結果がNon-streaming Displayと一致することを検証する。

### Native

Qwen3-4B GGUF／Metalで次を確認する。

```text
thinking enabled + hidden  → Canonical Tag／ReasoningがDisplayされない
thinking enabled + visible → Custom Label + Final
thinking disabled          → Existing Final Behavior
post-cancel generation     → 成功
```

Model出力の内容自体は確率的であるため、Native Testで長文内容の完全一致を要求しない。Protocol／表示境界はDeterministic Fixtureで強く検証する。

## 22. Implementation Sequence

1. Existing Raw Contract／CLI BehaviorをRegression Testで固定
2. Presentation Contract
3. Application Schema `2`／Resolver／Source Tracking
4. Model Definition Schema `2`／Output Protocol
5. Parser Port／Registry
6. Plain Text Parser
7. Tagged Stateful Parser
8. Renderer／Presentation Service
9. Non-streaming CLI接続
10. Streaming CLI接続
11. `model-info`
12. Unit／Contract／CLI Test
13. Static／Default Gate
14. Environment／Lock／Offline Gate
15. Native Metal Hidden／Visible Smoke
16. Implementer Status

## 23. Design Boundaries

- Presentation ModuleはReasoningの品質を評価しない
- ParserはGovernance Evaluatorではない
- RendererはModel Protocolを知らない
- Model AdapterはDisplay Policyを知らない
- VisibilityはPersistenceを変更しない
- Thinking ExecutionはSampling値を暗黙変更しない
- Phase 1-EはRaw CoT公開の正当性を主張しない

## 24. Authorization Boundary

本ArchitectureはユーザーReview待ちの提案である。Accepted ADRの後継版と明示的な実装解禁がない限り、Source／Config／Testを変更しない。

