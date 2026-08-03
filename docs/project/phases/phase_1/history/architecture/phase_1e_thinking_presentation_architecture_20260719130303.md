# Phase 1-E Thinking Presentation Architecture

- 文書ID: `phase_1e_thinking_presentation_architecture`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 13:03:03 JST`
- 更新日時: `2026-07-19 13:03:03 JST`
- 承認日時: `2026-07-19 13:03:03 JST`
- Snapshot: `20260719130303`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: Phase 1-E、Presentation Module、Output Parser、Streaming State Machine、CLI
- 正本言語: 日本語
- Requirements: [phase_1e_thinking_presentation_requirements_20260719130303.md](../requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
- Accepted ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- supersedes: `phase_1e_thinking_presentation_architecture_20260719123547.md`

## 1. Architecture Conclusion

Model RuntimeのRaw Contractは変更せず、Model Portの後段に独立Presentation Moduleを配置する。

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
        CLI／Future API／Future Web UI
```

Default Display LabelはユーザーDecisionにより`高度推論`とする。これはDisplay Channelの名称であり、Reasoning品質の保証ではない。

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
  → output parser registry／factory
  → typed config composer
```

禁止：

```text
inference core → CLI
model backend adapter → display label
presentation core → llama_cpp
deployment profile → presentation policy
model definition → user display label
```

## 3. Module Layout

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

Output ProtocolはBackendと異なる軸のため、`adapters/model_backends/llama_cpp/`にParserを置かない。

## 4. Stable Raw Boundary

Existing Contract：

```python
class GenerationResult:
    content: str

class GenerationChunk:
    text_delta: str
```

Model Port／Inference Service／llama.cpp AdapterはRaw Model Outputを返す。

`GenerationResult.content`をFinal Contentだけに置き換えない。Presentationは後段で行う。

## 5. Configuration Architecture

```text
Application Config Schema : 2
Deployment Profile Schema : 3 unchanged
Model Definition Schema   : 2
```

```toml
[generation]
thinking_mode = "disabled"

[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

Field Owner：

| Field | Owner | Deployment Override |
|---|---|---:|
| `generation.thinking_mode` | Application／Request | 不可 |
| `presentation.thinking.visibility` | Application／Request | 不可 |
| `presentation.thinking.display_label` | Application／Request | 不可 |
| `presentation.thinking.persistence` | Application Policy | 不可 |
| Canonical Delimiter | Model Definition | 不可 |
| Parser Key | Model Definition | 不可 |

## 6. Contracts

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
    display_label: str = "高度推論"
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

`ApplicationConfig`と`EffectivePhase1Config`へPresentationを追加する。

## 7. Resolver

Generic Deep Mergeを使用せず、Field別に解決する。

```text
Visibility:
  Explicit > Environment > Application > Built-in hidden

Display Label:
  Explicit > Environment > Application > Built-in 高度推論

Persistence:
  Application > Built-in disabled
```

```text
MARGPA_THINKING_VISIBILITY
MARGPA_THINKING_LABEL
```

`MARGPA_THINKING_MODE`はGeneration Resolverが所有する。

## 8. Label Validation

```text
length             : 1..64
leading/trailing   : 禁止
forbidden literal  : < > /
forbidden category : Control／CR／LF
Unicode            : 許可
```

Validation後のLabelだけをRendererへ渡す。Invalid Labelは`invalid_configuration`または`invalid_request`とする。

## 9. Model Definition

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

```python
class ThinkingOutputProtocolDefinition(ImmutableContract):
    parser_key: str
    opening_delimiter: str | None = None
    closing_delimiter: str | None = None

class ModelOutputProtocolDefinition(ImmutableContract):
    thinking: ThinkingOutputProtocolDefinition
```

Validation：

```text
plain_text_v1:
  delimiterなし

tagged_thinking_v1:
  opening／closing必須
  non-empty
  同一値禁止
  CR／LF／制御文字禁止
```

## 10. Parser Port／Registry

```python
class ThinkingOutputParserSession(Protocol):
    def feed(self, text_delta: str) -> tuple[ThinkingSegmentDelta, ...]: ...
    def finish(self) -> ThinkingParseSummary: ...

class ThinkingOutputParser(Protocol):
    def start(self) -> ThinkingOutputParserSession: ...
```

```python
build_output_parser(
    definition.output_protocol.thinking
) -> ThinkingOutputParser
```

Unknown Parser KeyはModel Load前に拒否する。Model Key／ArchitectureのConditional分岐を作らない。

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

Raw Outputは元の`GenerationResult`が所有し、Normalized Contractに全Raw Textを重複保持しない。

## 12. Stateful Parser

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

Optional Leading Whitespaceを一時Bufferし、Openingなしと判断した場合はOriginal Finalへ戻す。

Delimiterと一致可能性のある最小SuffixだけをBufferする。

## 13. Renderer

RendererはNormalized Segmentだけを受け取り、Canonical Delimiterを知らない。

### Hidden

```text
REASONING → 表示しない
FINAL     → そのまま表示
```

### Visible

```text
First Reasoning:
  <高度推論> + reasoning

Reasoning Complete:
  </高度推論>

Final:
  final text
```

Actual TagはResolved `display_label`から作る。Unclosed時のClosing Tag補完はPresentation Containerを閉じるためだけに行い、Raw Outputを修復したと主張しない。

## 14. Presentation Service

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

Non-streamingもStreamingも同じState Machineを使う。

## 15. CLI Integration

```text
--thinking／--no-thinking         : Execution
--show-thinking／--hide-thinking : Presentation
--thinking-label                   : Display Label
```

Non-streaming：

```text
Raw GenerationResult
  → present_text
  → print(display_content)
```

Streaming：

```text
for raw_chunk in GenerationStream:
  display_deltas = presentation_session.feed(raw_chunk.text_delta)
  print(display_deltas)

presentation_session.finish()
```

CLIで`str.replace("<think>", ...)`を行わない。Underlying StreamのCancel／CloseはExisting CLIが所有する。

## 16. Bootstrap

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

`Phase1Application`に`presentation_service`を明示的に注入する。

Parser Key Errorは可能な限り重いModel Load前に検出する。

## 17. Observability

```json
{
  "effective_config": {
    "generation": {
      "thinking_mode": "disabled"
    },
    "presentation": {
      "thinking": {
        "visibility": "hidden",
        "display_label": "高度推論",
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

## 18. Warning／Error Boundary

Configuration Error：

- Invalid Visibility／Label／Persistence
- Invalid Delimiter
- Unknown Parser Key

Runtime Parse Warning：

- Unclosed Reasoning
- Unexpected Extra Delimiter
- Malformed Protocol

Parse WarningはRaw GenerationのFinish Reasonを上書きしない。

## 19. Security／Privacy

- HiddenでLeading Canonical Reasoning Sectionをstdoutへ出さない
- Chunk Split時もFlashさせない
- Custom LabelのControl Character注入を拒否
- Raw ReasoningをDiskへ新規保存しない
- HiddenをPrompt Injection／Secret Filterにしない

## 20. Candidate File Scope

```text
config/application.toml
config/models/qwen3_4b_q4_k_m.toml
src/margpa_runtime_llm/bootstrap/config_loader.py
src/margpa_runtime_llm/bootstrap/model_registry_loader.py
src/margpa_runtime_llm/bootstrap/output_parser_registry.py
src/margpa_runtime_llm/bootstrap/phase1_application.py
src/margpa_runtime_llm/modules/inference/domain/model_definition.py
src/margpa_runtime_llm/modules/presentation/
src/margpa_runtime_llm/adapters/output_protocols/
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

## 21. Test Architecture

- Config Resolver／Label Validator
- Model Protocol Definition／Parser Registry
- Plain／Tagged Parser
- Renderer／Presentation Service
- Opening／Closing Delimiter全Split Position
- 1文字Chunk／1 Chunk
- Streaming／Non-streaming Parity
- Hidden No-flash
- Default `高度推論`／Custom Label
- Finish／Usage／Cancel／Close保持
- Native Qwen3 Metal Hidden／Visible
- Phase 1-D Language Regression

Native Testでは確率的なReasoning本文の完全一致ではなく、Protocol／表示境界を検証する。

## 22. Implementation Sequence

1. Existing Raw Contract／CLI Regression Fixture
2. Presentation Contract
3. Application Schema `2`／Resolver／Source
4. Model Definition Schema `2`／Output Protocol
5. Parser Port／Registry
6. Plain Text Parser
7. Tagged Stateful Parser
8. Renderer／Presentation Service
9. Non-streaming CLI
10. Streaming CLI
11. `model-info`
12. Unit／Contract／CLI Test
13. Static／Default Gate
14. Environment／Lock／Offline Gate
15. Native Metal Hidden／Visible Smoke
16. Implementer Status

## 23. Authorization Boundary

本ArchitectureはAcceptedである。ただし、Source／Config／Test変更はユーザーのPhase 1-E実装開始許可後に限る。

