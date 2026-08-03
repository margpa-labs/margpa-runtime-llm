# Phase 1-I Repository and Mac Manual Acceptance 設計Review

- 文書ID: `designer_review_phase_1i_repository_and_mac_manual_acceptance`
- 状態: `accepted_with_deferred_phase_4_presentation_enhancements`
- 作成日時: `2026-07-25 21:25:59 JST`
- 更新日時: `2026-07-25 21:25:59 JST`
- Snapshot: `20260725212559`
- 作成担当: 設計者役担当Task
- 対象Status: [implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md](implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md)
- 対象Handoff: [designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md](designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Phase 1-IのRepository実装とMac Web Manual AcceptanceをAcceptedとする。

Blocking Findingはない。Streaming中のRaw Markdown、Table未対応、Busy時の二重MessageおよびCode Block強化は、Current Contractを壊す問題ではなくPhase 4 Presentation／UX Follow-upとして保持する。

## 2. User Manual Acceptance

| Test | Result | Review |
|---|---:|---|
| User Message Copy | PASS | 入力単位のCopyが動作した。 |
| Assistant Final Copy | PASS | 出力単位のCopyが動作した。 |
| UI日本語／英語 | PASS | 既確認結果を再確認した。 |
| Response Language日本語／英語 | PASS | UI Languageと独立して動作した。 |
| Summary Mode | PASS | Post-generation Summaryが動作した。 |
| New Chat Context Reset | PASS | 別Topicを開始でき、旧会話をContextへ送らない。 |
| New Chat during Generation | PASS | 停止・初期化後に再送信できた。 |
| Stop during Summary | PASS | 正常復帰した。 |
| Browser Reload | PASS | 会話とUI Language以外のOptionがRuntime Defaultへ戻った。 |
| UI Language Persistence | PASS | UI LanguageだけがBrowser Storageから復元された。 |
| Multi-tab Model Busy | PASS | 競合側へ`model_busy`が安全に表示され、先行生成完了後に再実行できた。 |
| Thinking Control Dependency | PASS | 推論生成ON時だけ推論過程表示を選択できた。 |
| Thinking／Final Separation | PASS | 推論過程と最終回答が別領域に表示された。 |
| Completion Markdown | PASS with limitation | 完了後に対応MarkdownをDOMへ変換した。 |

## 3. Busy Message Assessment

競合Tabで次が表示された。

```text
The model is processing another request.
The request failed.
```

前者はServerの`model_busy`を翻訳した具体的Error、後者はRequest Catch時の汎用Statusである。409 Busyを安全に拒否し、先行Request完了後に次の生成が動作するため、機能上は正しい。

ただし同一原因に対して具体Messageと汎用Messageを同時表示するため、一般利用者には冗長である。Phase 4ではStatusも`model_busy`へ統一するか、Message BubbleとGlobal Statusの責務を整理する。

## 4. Markdown Assessment

Current Contract：

```text
Streaming中 : Plain Text
Completion後: Allowlist Markdown DOM
Failure時   : Canonical Plain Text
```

生成中にMarkdown記号が見えることは設計どおりであり、Completion後に変換されることを確認した。安全性と表示安定性を優先するPhase 1実装としてAcceptedとする。

### Table

Current ParserはTableを実装していない。Pipe TableはParagraphとして扱われ、`white-space: normal`により行区切りが潰れて見える場合がある。

安全性問題ではないが可読性が低いため、Phase 4でSemantic Table、Responsive OverflowおよびFallbackを実装する。

## 5. Code Block Assessment

Fenced Code Block自体はCurrent Parserで`pre`／`code`へ分離済みである。

Phase 4では次を追加する。

- Markdown、YAML、JSON、Pythonその他のLanguage Label
- Assistant説明本文とCode Snippet Blockの視覚的分離
- Code Block右上の個別Copy Button
- 回答全体CopyとCode-only Copyの独立
- Canonical Code TextをCopy Sourceとし、Rendered DOMをSourceにしない。
- Language名を無制限にCSS ClassまたはExecutable処理へ渡さない。
- Syntax Highlightを追加する場合もRuntime CDNを使用せず、Version、License、Digestを管理する。
- Highlight失敗時はPlain Code BlockへFallbackする。

## 6. Thinking Assessment

推論生成をONにした場合だけ推論過程表示を選択できる。これはGenerationとPresentationを正しく分離した状態である。

実Qwen3では、推論過程が英語、最終回答が日本語となる場合がある。推論過程はModel生成内容であり、Response Languageが最終回答と同程度に強制される保証はない。Phase 1-IのUI不具合とは扱わない。

Raw Thinking非保存、Assistant Final Copyへの非混入および次Turn Contextへの非混入は、Source Contractと自動Testで確認した。

## 7. Independent Code Review

確認した主要境界：

- `thinking_mode`／`thinking_visibility`
- Capability不足時Fail Closed
- `reasoning`／`final` SSE Channel
- Hidden Reasoning非送信
- Summary Thinking Disabled
- Canonical Final
- Clipboard Write-only
- `innerHTML`不使用
- Raw HTML Inert化
- Dangerous URL Scheme拒否
- External Link属性
- IME Composition Guard

重大な安全境界違反は確認しなかった。

## 8. Independent Verification

```text
pytest                         : 265 passed, 3 deselected
Phase 1-I／Pure CPU Targeted   : 30 passed, 1 deselected
Ruff Check                     : PASS
Ruff Format                    : PASS
Mypy                           : PASS
Node Safe Markdown             : 5 passed
Shell Syntax                   : PASS
uv lock --check                : PASS／122 packages
```

追加のMac Model Smokeは、既にWeb Runtimeが同じQwen ModelをMemory Mapした状態で別Contextを作ろうとして`Failed to create llama_context`となった。実装回帰とは判定しない。

- 常駐Web RuntimeのModel Mappingを確認した。
- ユーザーによる実Web Model生成は合格している。
- Phase 1 Final GateではWeb Runtime停止後にModel Smokeを再実行する。
- Reviewのためにユーザーの常駐Processを停止しなかった。

## 9. Deferred Phase 4 Enhancements

- Streaming Markdownの段階的安全Rendering
- Markdown Table
- Code Snippet Container
- Language Label
- Code-only Copy
- Syntax Highlight候補
- Busy Message／Global Status整理
- Thinking表示の追加説明

これらはPhase 1-I Acceptanceを妨げない。

## 10. Final State

```text
Repository Implementation : ACCEPTED
Mac Manual Acceptance     : ACCEPTED
Security Boundary         : ACCEPTED
Phase 4 Enhancements      : DEFERRED
Phase 1-I                 : COMPLETE／ACCEPTED
```

