# Phase 1-I Web Presentation and UX Follow-up Architecture

- 文書ID: `phase_1i_web_presentation_and_ux_follow_up_architecture`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md](../requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md)
- supersedes: なし

## 1. Architecture Goal

```text
Raw Model Stream
  ↓
Output Protocol Parser
  ├─ Reasoning Segment
  └─ Final Segment
        ↓
Conversation SSE Contract
  ├─ Ephemeral Reasoning Channel
  ├─ Final Text Channel
  └─ Terminal Canonical Final
        ↓
Web Message View
  ├─ Thinking Region／Plain Text
  ├─ Final Region／Streaming Plain Text
  └─ Completion後 Sanitized Markdown
```

Canonical Data、Ephemeral Thinking、Rendered DOMを分離する。

## 2. Current Problem

Current Web Requestは`thinking_visibility`だけを持ち、Generation Parametersの`thinking_mode`を変更しない。

Current SSE DeltaはPresentation済み文字列だけを持つため、ReasoningとFinalをClientが意味的に区別できない。Completion EventはCanonical Finalだけを持つ。

そのままCompletion後にMarkdown Renderすると、Streaming中に表示されたThinkingを消すか、ThinkingをFinal Markdownへ混入させる危険がある。

## 3. Contract Change

### 3.1 Request

`ConversationSettings`へ`thinking_mode`を追加する。

```json
{
  "response_language": "ja",
  "max_new_tokens": 2048,
  "thinking_mode": "disabled",
  "thinking_visibility": "hidden",
  "summary_mode": "off"
}
```

### 3.2 Runtime Snapshot

Runtime Defaultsへ追加する。

```text
thinking_mode
thinking_visibility
thinking_display_label
thinking_control_available
```

### 3.3 SSE

DeltaへChannel／Kindを追加する。

```json
{
  "request_id": "...",
  "channel": "reasoning",
  "text": "..."
}
```

```json
{
  "request_id": "...",
  "channel": "final",
  "text": "..."
}
```

候補値：

```text
reasoning
final
```

Status／Warning／ErrorはMessage Content Channelへ混ぜない。

Visibility Hidden時はReasoning ChannelをClientへ送らない。

### 3.4 Completion

Completion Eventの`assistant_message.content`をCanonical Final Answerとして維持する。

Raw ThinkingをCompletion PayloadまたはBrowser Conversation Historyへ追加しない。Reasoningは表示中だけ存在するEphemeral UI Stateとする。

## 4. Server-side Flow

`ConversationGenerationService._build_request()`は、Web Settingの`thinking_mode`をGeneration Parametersへ明示適用する。

Presentation LayerはReasoning／Final Segment Kindを失わない形でConversation Layerへ渡す。Model AdapterへUI Logicを追加しない。

Summary Stage：

```text
thinking_mode       : disabled
thinking_visibility : hidden
```

を固定する。

## 5. Client-side Message View

Assistant Turnを次のLogical Nodeに分ける。

```text
Assistant Message Container
  ├─ Thinking Region
  │    ├─ Label
  │    └─ Plain Text Content
  ├─ Final Region
  │    ├─ Streaming Plain Text
  │    └─ Completion後 Sanitized Markdown
  └─ Message Actions
       └─ Copy
```

Browserの`state.messages`へ入れるのは次だけである。

```json
{
  "role": "assistant",
  "content": "canonical final text"
}
```

Thinking RegionのTextを次Requestへ送らない。

## 6. Markdown Rendering

### 6.1 Execution Timing

```text
Streaming:
  Final Region.textContentへ追加

Completed:
  canonical finalをMarkdown Parse
  → Sanitize
  → Final RegionをRendered DOMへ置換
```

Parser／Sanitizer Failure：

```text
canonical finalをtextContentで表示
warningをUIへ表示
```

### 6.2 Dependency Boundary

Runtime CDNは禁止する。

第三者Parser／Sanitizerを利用する場合：

- Exact Version Pin
- Repository-local ArtifactまたはBuild Output
- Source URL
- License
- SHA-512
- NOTICE候補
- No Network at Runtime

実装担当はSecurity Requirementを満たす候補を選択し、Dependency追加が必要な場合はStatus Reportへ明記する。

### 6.3 Sanitization

Markdown Parser Outputを信頼しない。

- Raw HTML Disabled
- Sanitizer Allowlist
- Dangerous URL Scheme Reject
- External Link Protection
- Unknown Tag／Attribute Removal

`innerHTML`を使用する場合はSanitized Resultだけに限定する。安全なDOM Construction方式を採用できる場合は優先してよい。

## 7. Copy Architecture

各Message ViewはCanonical Copy SourceをClosureまたは`data`へ保持する。

```text
User Copy Source      : original user content
Assistant Copy Source : completed canonical final content
```

Rendered DOMから`innerText`を逆生成しない。

Thinking RegionにはPhase 1-IでCopy Buttonを付けない。

## 8. Shortcut／IME

Current Handler：

```text
(metaKey || ctrlKey) && key === "Enter"
```

へIME Composition Checkを追加する。

```text
event.isComposing === false
```

Shortcut HintはTranslation Dictionaryへ置く。

## 9. New Chat／Cancel

New Chatは次を行う。

1. Active SessionへCancel Request
2. Client Stream Abort
3. Ephemeral Thinking／Final DOM Clear
4. Browser Conversation State Clear
5. ModelはReloadしない

Cancelled Partial OutputをCompleted Canonical Messageへ追加しない。

## 10. Module Boundary

Expected Change：

```text
modules/conversation/contracts.py
modules/conversation/application/conversation_generation.py
modules/presentation/*
web/contracts.py
web/static/index.html
web/static/app.js
web/static/app.css
web integration／unit tests
config/application.toml
```

Conditional Change：

```text
pyproject.toml
uv.lock
Repository-local third-party static assets
NOTICE candidate metadata
```

Keep Stable：

```text
Model Port
llama.cpp Adapter
Model Artifact
Deployment Profiles
Storage
RAG
Audit
```

## 11. Test Architecture

- Contract Test：Request／Runtime／SSE Channel
- Unit Test：Thinking Segment routing、Markdown fallback、Copy Source
- Integration Test：FastAPI SSE＋Static UI contract
- Security Test：XSS／URL／Raw HTML
- Native Test：Qwen Thinking ON／OFF
- Manual Test：User指定のまとめTest

Current `innerHTML absent` Testは、新Security Contractへ置き換える。単にAssertionを削除せず、Sanitized Content以外をInjection Sinkへ渡さないことを検証する。

## 12. Degraded Behavior

- Thinking Capabilityなし：Generation Control Disabled
- Markdown Parser unavailable：Plain Text
- Clipboard unavailable：Visible Error
- Sanitizer failure：Plain Text
- Unknown SSE Channel：Fail／Visible Error
- Empty Final：Existing Warning／Rollback Contract

## 13. Migration

Current Browser StateはEphemeralであるためData Migrationは不要。

API ContractはPhase 1 Preview内で更新する。Schema／Contract Testを更新し、旧Payloadを黙って誤解しない。
