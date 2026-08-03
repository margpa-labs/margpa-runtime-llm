# Phase 1-I Web Presentation／UX Follow-up 実装者Status

- 文書ID: `implementer_status_phase_1i_web_presentation_and_ux_follow_up`
- 状態: `repository_implementation_completed_native_and_manual_acceptance_pending`
- 作成日時: `2026-07-25 20:35:08 JST`
- 更新日時: `2026-07-25 20:35:08 JST`
- Snapshot: `20260725203508`
- 作成担当: 実装者役担当Task
- 対象Handoff: [designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md](designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md)

## 1. Result

Phase 1-IのRepository実装と自動Testを完了した。

```text
Thinking Generation : disabled／enabled
Thinking Visibility : hidden／visible
SSE Delta Channel   : reasoning／final
Reasoning DOM        : Ephemeral Plain Text
Final Streaming     : Plain Text
Final Completion    : Allowlist DOM Markdown
Copy Source         : Canonical Text
Runtime CDN         : none
Third-party追加     : none
```

ユーザー指定のまとめManual Acceptanceと実Model Thinking ON／OFF Native Testは実施していない。

## 2. Changed Files

### Runtime／Contract

- `src/margpa_runtime_llm/modules/conversation/contracts.py`
- `src/margpa_runtime_llm/modules/conversation/public.py`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
- `src/margpa_runtime_llm/modules/presentation/contracts/thinking.py`
- `src/margpa_runtime_llm/modules/presentation/application/thinking_presentation_service.py`
- `src/margpa_runtime_llm/modules/presentation/public.py`
- `src/margpa_runtime_llm/web/contracts.py`
- `src/margpa_runtime_llm/bootstrap/web_application.py`

### Static Web

- `src/margpa_runtime_llm/web/static/index.html`
- `src/margpa_runtime_llm/web/static/app.js`
- `src/margpa_runtime_llm/web/static/app.css`
- `src/margpa_runtime_llm/web/static/safe_markdown.js`

### Test

- `tests/unit/conversation/test_conversation_generation.py`
- `tests/unit/web/test_safe_markdown.py`
- `tests/unit/web/safe_markdown.test.mjs`
- `tests/integration/web/test_web_app.py`

## 3. Contract Implementation

### Thinking

- `ConversationSettings.thinking_mode`を追加した。
- Webでは`disabled`／`enabled`だけを許可し、`model_default`とUnknown ValueをValidation Errorにする。
- Explicit Web Settingを`GenerationParameters.thinking_mode`へ適用する。
- Runtime Snapshotへ`thinking_mode`と`thinking_control_available`を追加した。
- Thinking Control CapabilityがないModelへのEnable Requestは`unsupported_capability`でFail Closedにする。
- Generation OFF時はVisibilityをServer側でもHiddenへ正規化する。
- Summary Stageは既存どおりThinking Disabled／Visibility Hiddenを固定した。

### SSE／Canonical Boundary

- Delta Payloadへ`channel=reasoning|final`を追加した。
- Visibility Hidden時はReasoning DeltaをClientへ送らない。
- BrowserはPresentation Tag／Display LabelをParseしない。
- Completion Eventの`assistant_message.content`はCanonical Finalだけを維持する。
- ReasoningはCompletion、Browser History、次Turn、Copyへ混入しない。

### Web UX

- Thinking GenerationとThinking Visibilityを別Controlにした。
- Generation OFFまたはCapability Unavailable時はVisibilityをDisabledにする。
- Assistant Thinking／Finalを別DOM Regionにした。
- Shortcut Hintを日本語／英語で表示し、HandlerへIME Composition Checkを追加した。
- User Messageと完了済みAssistant FinalへCopy Buttonを追加した。
- Clipboardは`writeText`だけを使い、Copy元はClosureで保持するCanonical Textに固定した。
- Copy成功／失敗Feedbackを日本語／英語で表示する。

## 4. Markdown Security

第三者Dependencyは追加せず、Repository-localのAllowlist Parser／DOM Builderを実装した。

- `innerHTML`不使用
- `document.createElement`／`createTextNode`によるDOM Construction
- Raw HTMLはExecutable DOMにせずPlain Textとして保持
- `javascript:`、`data:`、`vbscript:`、Control Character、Protocol-relative URLを拒否
- External HTTP(S) Linkへ`target="_blank"`と`rel="noopener noreferrer"`を設定
- Streaming中はPlain Text
- Completion後だけCanonical FinalをRender
- Parser Failure時はCanonical Plain TextへFallbackし、UIへ明示

初期対応：

- Heading
- Paragraph
- Unordered／Ordered List
- Emphasis／Strong
- Inline Code
- Fenced Code Block
- Block Quote
- Link
- Horizontal Rule

Tableは未対応であり、Plain Text相当として扱う。

## 5. Verification

実行結果：

```text
pytest                    : 265 passed, 3 deselected
Ruff check                : passed
Ruff format --check       : passed
Mypy strict               : passed / 95 source files
uv lock --check           : passed / 122 packages
Node Markdown security    : 5 passed
Shell syntax              : passed
```

自動Testで確認したもの：

- Thinking Generation／Visibility 4組合せ
- Hidden Reasoning非送信
- Visible Reasoning／Final Channel分離
- Unknown Thinking Mode拒否
- Capability Unavailable拒否
- Summary Thinking Disabled
- Canonical Final維持
- XSS／Raw HTML／Event Handler Inert化
- Dangerous URL拒否
- External Link属性
- Malformed Fence Plain Text Fallback Hook
- Copy Canonical Source／Clipboard Read不使用
- Shortcut Hint／IME Check
- Existing Stop／Summary／Language／SSE Keepalive Regression

## 6. Pending

- 実Qwen3でのThinking Generation ON／OFF Native Test
- User指定のまとめManual Acceptance
- Browser実操作による4組合せ、Copy、Markdown、Shortcut確認

上記をCompletedとは記録しない。

## 7. Boundary

- Model Port、llama.cpp Adapter、Deployment Profile、RAG、StorageはPhase 1-Iとして変更していない。
- Dependency Version、`pyproject.toml`、`uv.lock`は変更していない。
- External CDN、External Service、Clipboard Readは追加していない。

