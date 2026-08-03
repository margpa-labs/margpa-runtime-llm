# Phase 1-I Web Presentation and UX Follow-up 要件定義

- 文書ID: `phase_1i_web_presentation_and_ux_follow_up_requirements`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Source Review: [designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](../handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)
- supersedes: なし

## 1. Purpose

Mac Web User Testで確認されたPhase 1-G／1-Hの基本動作を維持しながら、主要LLM Productに近い可読性と操作性へ仕上げる。

対象：

- Thinking Generation／Visibility UI整合
- Shortcut Hint
- User／Assistant Message Copy
- Sanitized Markdown Presentation
- 実装後のまとめAcceptance Test

## 2. Scope

### 2.1 Thinking

- Thinking Generation `disabled／enabled`をWeb Requestで明示できる。
- Thinking Visibility `hidden／visible`と独立させる。
- Generation OFF時にVisibilityだけONという状態を、UIで誤解なく扱う。
- ThinkingはFinal Answerと別のPresentation Regionへ表示する。
- Raw ThinkingをConversation Historyへ保存しない。
- Summary GenerationのThinkingは引き続きDisabledとする。

### 2.2 Shortcut Hint

- Current実装の`Cmd+Enter`／`Ctrl+Enter`送信を画面上で発見可能にする。
- 日本語／英語UIへ対応する。
- 表示内容と実際のKeyboard Handlerを一致させる。
- IME変換確定中のEnterを送信として扱わない。

### 2.3 Message Copy

- User MessageとAssistant MessageにCopy Buttonを付ける。
- Canonical TextをCopyする。
- Hidden Thinking、Metadata、非表示Original Summary、Rendered HTMLを混入させない。
- 成功／失敗を利用者へ通知する。

### 2.4 Markdown

- Assistant Final AnswerをMarkdownとして表示する。
- User InputはDefault Plain Textとする。
- Streaming中の不完全Markdownを安全に扱う。
- Completion後のCanonical Final AnswerをRender Sourceとする。
- XSS、危険URL、Raw HTMLをFail Closedで扱う。

## 3. Non-goals

- Persistent Conversation
- Account System
- Full Responsive UI
- Project Documentation Explainer／RAG
- Local Folder Upload
- Governance／Guard／Judge／Repair UI
- Raw Thinking Persistence
- Thinking品質保証
- Clipboard Read
- External CDN依存

## 4. Required User-facing Behavior

### 4.1 Thinking Controls

概念表示：

```text
推論生成       : OFF／ON
推論過程を表示 : OFF／ON
```

許可状態：

| Generation | Visibility | Behavior |
|---|---|---|
| OFF | OFF | Final Answerだけを生成・表示 |
| OFF | ON | UIで無効化するか、表示対象なしを明示 |
| ON | OFF | Thinkingを生成し得るが画面へ表示しない |
| ON | ON | ThinkingとFinalを別領域に表示 |

一般利用者向けDefault：

```text
Generation : OFF
Visibility : OFF
```

### 4.2 Thinking Notice

- Thinking表示は真の内部思考、正解、根拠の完全性を保証しない。
- Thinking ONはLatency／Token Usageを増やす可能性がある。
- Token上限へ達するとFinal Answerが生成されない可能性がある。
- Raw Thinkingは永続保存しない。

### 4.3 Shortcut

Composer付近へ、次に相当する表示を置く。

```text
Cmd+Enter／Ctrl+Enterで送信
```

英語表示：

```text
Send with Cmd+Enter / Ctrl+Enter
```

### 4.4 Copy

- 各User MessageにCopy Buttonを表示する。
- 完了したAssistant Final AnswerにCopy Buttonを表示する。
- Copy成功後は短時間`コピーしました／Copied`を表示する。
- Failure時は`コピーできませんでした／Could not copy`を表示する。
- Copy ButtonはKeyboard Focus可能にする。

### 4.5 Markdown

初期対応候補：

- Heading
- Paragraph
- Unordered／Ordered List
- Emphasis／Strong
- Inline Code
- Fenced Code Block
- Block Quote
- Link
- Horizontal Rule
- TableはParser選定と安全性に応じた候補

Raw HTMLは表示しない。危険なURL SchemeはLink化しない。

## 5. Message／Presentation Separation

最低限、次を区別する。

```text
User Canonical Text
Assistant Canonical Final Text
Ephemeral Thinking Text
Rendered Assistant DOM
Status／Warning／Error
```

- Browser Conversation Historyへ保存するAssistant ContentはCanonical Final Textだけとする。
- Rendered DOMからHistoryや次Requestを再構築しない。
- Thinkingを次TurnのAssistant Messageへ混入させない。
- Summary ON時はPresented SummaryだけをCanonical Assistant Contentとする。
- 非表示Original SummaryをCopyまたはDOMへ露出しない。

## 6. Streaming Requirements

- Reasoning DeltaとFinal DeltaをClientが意味的に区別できる。
- Visibility Hidden時にReasoning DeltaをClientへ送らない。
- Final DeltaはStreaming中にPlain Text表示してよい。
- Completion時にCanonical Final Contentを安全なMarkdownへ変換する。
- ReasoningはMarkdown Rendererへ渡さず、専用のPlain Text Regionへ表示する。
- Cancelled／Error／Length Warning時に不完全回答をCompleted Answerと誤認させない。

## 7. Markdown Security Requirements

- Runtime時に外部CDNへ接続しない。
- Parser／Sanitizerを追加する場合、Versionを固定する。
- Third-party License、Source、Version、Artifact Digestを記録する。
- Raw HTMLをDefault Disabledとする。
- `script`、`style`、`iframe`、Form、Event Handler属性等を拒否する。
- `javascript:`等の危険URLを拒否する。
- External Linkは安全な属性を持つ。
- Sanitized Result以外を`innerHTML`へ渡さない。
- Parser Failure時はPlain TextへFallbackする。
- Security TestなしでMarkdown Renderingを有効化しない。

## 8. Copy Security Requirements

- `navigator.clipboard.writeText`等のWriteだけを使用する。
- Clipboard内容をReadしない。
- Canonical Text以外をCopy Sourceにしない。
- Thinking Hidden時にReasoningをCopyしない。
- Clipboard API利用不能時に無言で成功扱いしない。

## 9. Configuration／Contract

Web Runtime DefaultsへThinking Modeを追加する。

Conversation Settings候補：

```text
response_language
max_new_tokens
thinking_mode
thinking_visibility
summary_mode
```

- Unknown ValueはValidation Errorとする。
- Model CapabilityにThinking Controlがなければ、Thinking Generation ControlをDisabled／Unavailableにする。
- Application DefaultとExplicit Web SettingのSourceを区別可能にする。

## 10. Automated Test Requirements

### Thinking

- Generation／Visibility 4組合せ
- Plain Text Model
- Tagged Thinking Complete／Unclosed／Malformed
- Hidden Reasoning非送信
- Visible ReasoningとFinalのRegion分離
- Summary Thinking Disabled
- Final Token Limit Warning

### Markdown

- Heading／List／Emphasis／Code／Link
- Streaming Chunk分割
- Completion後Render
- Raw HTML
- Script／Event Handler
- Dangerous URL
- Malformed Markdown
- Parser Failure Plain Text Fallback
- Japanese／English

### Copy

- User Canonical Text
- Assistant Canonical Final Text
- Markdown Source
- Thinking非混入
- Hidden Original Summary非混入
- Success／Failure Feedback

### UI

- Shortcut Hint
- `Cmd+Enter`／`Ctrl+Enter`
- IME Composition
- New Chat
- Stop
- UI Language
- Response Language

## 11. Deferred Combined Manual Test

Phase 1-I実装後に、次をまとめてUser Testする。

- 生成中New Chat
- Summary中Stop
- Browser Reload
- 別Tab同時生成／Model Busy
- Max New Tokens `0／1／2048／2049`
- Thinking 4組合せ
- Markdown表示
- User／Assistant Copy
- Shortcut Hint

## 12. Acceptance

次をすべて満たす。

1. Existing Phase 1-G／1-H Regressionがない。
2. Thinking GenerationとVisibilityが別契約として動作する。
3. ThinkingとFinalがDOM／History／Copyで混在しない。
4. Assistant Final Answerが安全にMarkdown表示される。
5. XSS TestがFail Closedである。
6. User／Assistant CopyがCanonical Contentを使用する。
7. Shortcut Hintと実動作が一致する。
8. Ruff／Mypy／Pytest／Web IntegrationがPassする。
9. User Manual更新後にCombined Manual Testを実施できる。

## 13. Authorization

ユーザーは2026-07-25、Phase 1完了前に本Follow-upを先行実施する方針と、実装担当Handoff作成を指示した。

