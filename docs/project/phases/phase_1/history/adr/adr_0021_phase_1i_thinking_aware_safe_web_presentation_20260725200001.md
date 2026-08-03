# ADR-0021: Phase 1-I Thinking-aware Safe Web Presentation

- 文書ID: `adr_0021_phase_1i_thinking_aware_safe_web_presentation`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Requirements: [phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md](../requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md)
- Architecture: [phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md](../architecture/phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md)
- supersedes: なし

## Context

Phase 1-G／1-HのMac Web User Testで、Chat、Streaming、Stop、New Chat、Language、Summary、Token Limitが成立した。

次のFollow-upが確認された。

- Thinking VisibilityをONにしても、Generation DefaultがDisabledのため表示対象がない。
- Assistant MarkdownがPlain Textとして表示される。
- Shortcutは動作するが画面上で発見できない。
- User／Assistant MessageにCopy Buttonがない。

Current SSE DeltaはPresentation済み文字列だけを持ち、ReasoningとFinalを意味的に区別できない。Current Completion EventはCanonical Finalだけを持つ。そのため、単純にCompletion後Markdown化するとThinking表示を消すか、ThinkingをFinalへ混入させる危険がある。

## Decision

### 1. Phase 1-Iを追加する

Phase 1 Completion前のSubphaseとして、Web PresentationとUX Follow-upを実施する。

### 2. Thinking GenerationとVisibilityを独立させる

Web Requestに`thinking_mode`を追加する。

```text
Generation : disabled／enabled
Visibility : hidden／visible
```

Generation OFF時のVisibility ONを、UIで有効な表示状態として誤認させない。

### 3. SSEでReasoningとFinalを区別する

DeltaへSemantic Channelを追加する。

```text
reasoning
final
```

Hidden ReasoningはClientへ送らない。

### 4. ThinkingとFinalを別DOM Regionにする

- Thinking：Ephemeral Plain Text
- Final：Streaming Plain Text、Completion後Sanitized Markdown

ThinkingをBrowser Conversation History、Copy、次Turnへ混入させない。

### 5. MarkdownはCompletion後にRenderする

Streaming中の不完全Markdownを毎Chunk Renderしない。

Canonical FinalをCompletion後にParse／Sanitizeし、安全なDOMへ置換する。Failure時はPlain TextへFallbackする。

### 6. CopyはCanonical Textを使う

Rendered DOMからCopy Textを逆生成しない。

### 7. Runtime CDNを使用しない

Third-party Parser／Sanitizerを使う場合はVersion、License、Source、Digestを固定し、Runtime Networkを不要にする。

## Rationale

- Thinking ExecutionとPresentationの既存ADR-0014をWeb UIでも維持できる。
- Semantic ChannelによりUIがTag文字列や可変Labelを再Parseせずに済む。
- Canonical／Rendered分離によりHistory、Copy、Auditの一貫性を保てる。
- Completion後RenderはStreaming中のMalformed DOMとFlickerを避けられる。
- Plain Text FallbackによりMarkdown Dependency FailureがChat Failureにならない。

## Rejected Alternatives

### Visibility ONでGenerationも暗黙ON

却下。ExecutionとPresentationの独立性を壊す。

### Current表示文字列から`<推論過程>`をBrowserが解析

却下。Display Labelが可変であり、Model Contentとの衝突、Tag Injection、Localization依存が起きる。

### ThinkingとFinalを一つのMarkdownへ投入

却下。Thinking漏えい、Copy混入、History混入、Markdown解釈差が起きる。

### Streaming ChunkごとにHTMLへ再変換

却下。Incomplete Markdown、DOM再構築Cost、Flicker、Security Review範囲が増える。

### Raw `innerHTML`

却下。Model OutputはUntrusted Contentであり、XSSを許容できない。

### External CDN

却下。Offline／Local再現性、Supply Chain、CSP、外部通信なしというCurrent Boundaryを壊す。

### Rendered DOMの`innerText`をCopy

却下。Canonical Markdown、Code、List、Whitespaceが変形し、Hidden Node混入Riskもある。

## Consequences

- Conversation SSE Contractが更新される。
- Thinking Segment Routing Testが増える。
- Markdown Parser／Sanitizer選定とLicense記録が必要になる可能性がある。
- UI DOM StructureがMessage単位へ細分化される。
- Phase 1 User ManualとまとめAcceptance Testが必要になる。
- Plain Text Fallbackを維持するため、Markdown Failure時も生成結果を失わない。

## Implementation Gate

ユーザーは2026-07-25、Phase 1完了前に本Follow-upを先行実施し、実装担当Handoffを作成するよう指示した。本ADRとHandoffのScope内でPhase 1-I実装へ着手可能である。

