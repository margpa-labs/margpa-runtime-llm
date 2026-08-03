# Phase 1-I Web Presentation and UX Follow-up 実装担当Handoff

- 文書ID: `designer_handoff_phase_1i_web_presentation_and_ux_follow_up`
- 状態: `accepted_ready_for_implementation`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- 対象: 実装者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md](../requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md)
- Architecture: [phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md](../architecture/phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md)
- Accepted ADR: [adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md](../adr/adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md)
- Source Review: [designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)
- supersedes: なし

## 1. Handoff Conclusion

Phase 1-IをPhase 1 Completion前に実装する。

実装Scope：

1. Thinking Generation／Visibility UI整合
2. Reasoning／Final SSE Channel分離
3. Shortcut Hint
4. User／Assistant Message Copy
5. Completion後のSanitized Markdown Presentation
6. Automated Test
7. 実装報告

## 2. Required Reading Order

1. 本Handoff
2. Requirements
3. Architecture
4. ADR-0021
5. Source Review
6. [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
7. [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
8. [documentation_index_20260725192903.md](../documentation_index_20260725192903.md)

## 3. Authorization

ユーザーによる実装Handoff作成と先行実施の指示を受領済みである。Phase 1-IのSource／Test／必要Config変更へ着手可能である。

外部環境操作、Model Download、Git／GitHub、RAG、Pure CPU Runtimeは本HandoffのScope外である。

## 4. Locked Decisions

```text
Thinking Execution／Visibility : Separate
Reasoning Persistence           : Disabled
Summary Thinking                : Disabled
Reasoning UI                    : Ephemeral Plain Text
Final Streaming UI              : Plain Text
Final Completed UI              : Sanitized Markdown
History／Copy Source             : Canonical Final
User Message Presentation       : Plain Text
Runtime CDN                     : Forbidden
Unsafe Markdown Fallback        : Plain Text
Clipboard Read                  : Forbidden
```

## 5. Step A — Regression Freeze

変更前に既存Testを実行し、結果をStatusへ記録する。

```text
ruff format --check
ruff check
mypy
pytest
web integration tests
```

次をRegression Fixtureとして維持する。

- Language
- Summary
- Stop／Cancel
- New Chat
- Busy
- Token Warning
- Basic Auth
- Shutdown
- No Raw Thinking Persistence

## 6. Step B — Thinking Request／Runtime Contract

追加：

```text
ConversationSettings.thinking_mode
RuntimeDefaults.thinking_mode
RuntimeDefaults.thinking_control_available
```

Web Requestの`thinking_mode`をGeneration Parametersへ適用する。

Unknown ValueとCapability不足を黙って無視しない。

Summary StageはThinking Disabledを維持する。

## 7. Step C — Semantic SSE

Deltaへ`channel`を追加する。

```text
reasoning
final
```

要件：

- Hidden ReasoningをClientへ送らない。
- FinalだけをCanonical Assistant Messageへ保存する。
- Warning／Error／StatusをContentへ混ぜない。
- Unknown ChannelをClientが無視して成功扱いしない。

Presentation RendererのDisplay TagをBrowserが再Parseする方式は禁止する。

## 8. Step D — Message DOM

Assistant MessageをThinking、Final、Actionsに分離する。

Thinking：

- Plain Text
- Visible時だけ作成
- Finalとは別Label
- Historyへ入れない

Final：

- Streaming中Plain Text
- Completion後Canonical FinalをMarkdown Render

Actions：

- Copy
- 完了状態後にAssistant Copyを有効化

## 9. Step E — Thinking UI

UI候補：

```text
推論生成       OFF／ON
推論過程を表示 OFF／ON
```

- Generation OFF時はVisibilityをDisabledにするか、表示対象なしを明示する。
- UI Languageを切り替えてもStateを失わない。
- General Defaultは両方OFF。
- Token／Latency／Persistence Noticeを維持する。

## 10. Step F — Shortcut Hint

ComposerへLocalized Hintを追加する。

```text
Cmd+Enter／Ctrl+Enterで送信
Send with Cmd+Enter / Ctrl+Enter
```

Keyboard Handlerは`event.isComposing`を確認する。

## 11. Step G — Copy

Copy Source：

```text
User      : canonical input
Assistant : canonical completed final
```

- Rendered DOMをSourceにしない。
- Thinkingを混ぜない。
- Summaryの非表示Originalを混ぜない。
- Copy成功／失敗をLocalized表示する。
- Clipboard Readは禁止する。

## 12. Step H — Markdown

### Selection Gate

Parser／Sanitizer方式は次を満たす。

- No Runtime CDN
- Pinned Version
- License Compatible
- Source／SHA-512記録
- Raw HTML Disabled
- XSS Test可能
- Plain Text Fallback

Third-party Artifactを追加する場合、Status ReportへVersion、License、Source、Digest、配置Pathを記載する。

### Rendering

- Final Completion後にCanonical FinalをRenderする。
- Streaming中はPlain Text。
- ThinkingはMarkdown化しない。
- Dangerous URLとUnsafe HTMLをRejectする。
- Parser／Sanitizer Failure時はCanonical Plain Textを表示する。

## 13. Candidate File Scope

Expected：

```text
src/margpa_runtime_llm/modules/conversation/contracts.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/modules/presentation/
src/margpa_runtime_llm/web/contracts.py
src/margpa_runtime_llm/web/static/index.html
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/app.css
tests/unit/
tests/integration/web/
config/application.toml
docs/handoffs/implementer_status_phase_1i_*
```

Conditional：

```text
pyproject.toml
uv.lock
src/margpa_runtime_llm/web/static/vendor/
Third-party notice metadata
```

Do Not Change：

```text
Model Artifact
Model Port
llama.cpp Backend
Deployment Profiles
RAG
External Environment
Public LICENSE
```

## 14. Required Automated Test

- Existing Default Suite
- Web Integration
- Thinking 4組合せ
- Capability不足
- Reasoning／Final Channel
- Hidden Reasoning非送信
- Summary Thinking Disabled
- Markdown Feature
- Markdown XSS／Dangerous URL
- Streaming／Completion
- Copy Canonical Source
- Hidden Thinking／Original Summary非混入
- Shortcut／IME
- New Chat／Stop／Busy

## 15. Deferred Combined User Test

実装担当はManual Testを完了扱いにしない。実装と設計Review後にユーザーがまとめて実施する。

対象：

- 生成中New Chat
- Summary中Stop
- Browser Reload
- 別Tab Busy
- Token `0／1／2048／2049`
- Thinking 4組合せ
- Markdown
- Copy
- Shortcut Hint

## 16. Completion Report

`docs/handoffs/implementer_status_phase_1i_*_YYYYMMDDHHMMSS.md`を新規作成する。

必須内容：

- Changed Files
- Contract Change
- Dependency／License
- Test Command／Result
- Security Test
- Known Limitation
- Manual Test Pending
- No External Operation

## 17. Stop Conditions

次の場合は安全でない代替を実装せず、Statusへ戻す。

- SanitizerなしでHTML Injectionが必要
- Thinking／Final分離が維持できない
- Hidden ThinkingがHistory／Copyへ混入する
- Third-party Licenseが不明
- Existing Stop／Summary／Language Contractが壊れる
- Model Adapter変更が必要
