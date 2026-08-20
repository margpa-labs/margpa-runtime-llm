# Claude側設計統括者役 — 表を含むMessageの横幅拡張（message-wide）

```yaml
document_id: claude_message_wide_bubble_for_table_content_20260819123330
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
role: design_governor
created_at: 2026-08-19 12:33:30 JST
language: ja
```

## 1. 経緯

Markdown表崩れ修正（[claude_streaming_markdown_table_rendering_fix_ja_20260819120800.md](claude_streaming_markdown_table_rendering_fix_ja_20260819120800.md)）の実Browser確認完了後、ユーザーから追加要望：「通常時の横幅の最大は今の状態から変えず、図（表）を使う時だけもっと広げる。最大が1.5倍ぐらい。」

## 2. 実装内容

- [safeMarkdown.tsx](../../../../../frontend/src/lib/safeMarkdown.tsx)：`renderSafeMarkdown`を`parseSafeMarkdown` + 新規`renderSafeMarkdownBlocks`へ分離し、新規`containsTable(blocks)`を追加。Parseを1回で済ませ、Table有無の判定とRenderingの両方に同じBlock配列を再利用する構成とした（二重Parseを避けるための最小限のRefactor）。
- [MessageBubble.tsx](../../../../../frontend/src/components/MessageBubble.tsx)：Markdown Parse結果（`blocks`）から`containsTable`でTable有無を判定し、`message-wide`Classを条件付き付与。
- [app.css](../../../../../frontend/src/styles/app.css)：`.message`の既存`max-width: 57%`はそのまま変更せず、新規`.message-wide { max-width: 85% }`（57%の約1.5倍）を追加。Mobile Media Query（`max-width: 640px`）側にも、既存の`.message`の94%上限に合わせて`.message-wide`を94%へ揃える追記を行った（Mobileでは元々ほぼ全幅のため、これ以上広げる余地が無いため）。

## 3. Validation

- Vitest：`safeMarkdown.test.tsx`（Refactor後も16/16 Pass）、`MessageBubble.test.tsx`へ2件追加（Table含有Messageに`message-wide`が付与されること／通常Text Messageには付与されないこと）、計25/25 Pass。
- ESLint・`tsc --noEmit`・`vite build`：Clean。
- 実Browser確認（Local LLMサーバー一時Instance）：通常のText Messageは`computedMaxWidth: 57%`・`message-wide`無し、表を含むMessageは`computedMaxWidth: 85%`・`message-wide`付与を、実際のDOM計算値で確認。Screenshotでも、通常Messageに対し表Messageが明確に広く表示されることを確認。

## 4. Status

```text
Current Point            : 表を含むMessageのみ横幅上限を1.5倍（57%→85%）へ
                            拡張する機能を実装完了。
Files Created／Modified   : frontend/src/lib/safeMarkdown.tsx、
                            frontend/src/components/MessageBubble.tsx、
                            frontend/src/components/MessageBubble.test.tsx、
                            frontend/src/styles/app.css、本Evidence File。
Validation                : Vitest 25/25 Pass、ESLint／tsc／Build Clean、
                            実Browser確認Clean。
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし。次のユーザー指示待ち。
```
