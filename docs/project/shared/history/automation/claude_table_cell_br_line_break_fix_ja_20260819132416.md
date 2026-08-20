# Claude側設計統括者役 — 表Cell内`<br>`混入の修正

```yaml
document_id: claude_table_cell_br_line_break_fix_20260819132416
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
role: design_governor
created_at: 2026-08-19 13:24:16 JST
language: ja
```

## 1. 経緯

Markdown表の横幅拡張・表現重視モードの実機確認完了直後、ユーザーが新たなBugを発見：多列比較表（ChatGPT／Claude／Gemini／Qwen比較）で、各列内の複数箇条書きを区切るために出力された`<br>`が、改行として機能せず、Cell内に文字列`<br>`がそのまま表示されていた（Screenshot添付にて報告）。

## 2. 根本原因

[safeMarkdown.tsx](../../../../../frontend/src/lib/safeMarkdown.tsx)は、XSS対策として「生HTMLを一切Renderしない」設計方針を持つ（既存Test「raw HTML and event handlers remain inert text」で明示的に保証）。この方針自体は正しいが、GFM Pipe Tableでは、単一行しか持てないCell内で改行を表現する標準的な手法として`<br>`Tagが広く使われる——これは通常のMarkdown記法だけでは実現できない（Table Row自体が改行を含められないため）。今回のModel出力もこの一般的な記法に従っていたが、Inline Parser（`parseInline`）が`<`を特別扱いしていなかったため、他の生HTMLと同様、文字列としてそのまま出力されていた。

## 3. 修正内容

[safeMarkdown.tsx](../../../../../frontend/src/lib/safeMarkdown.tsx)の`parseInline`へ、`<br>`・`<br/>`・`<br />`（大小文字問わず、属性なし）のみを認識する狭いException を追加した。新規`InlineNode`型`break`を追加し、`renderInline`側で実際の`<br />`Elementとして描画する。

安全性への影響：この正規表現（`/^<br\s*\/?>/iu`）は、属性を一切含まない、この厳密な形しか一致しない。`<br onclick="...">`や`<img>`・`<script>`等、Payloadを持ちうる全てのTagは、従来通り無害な文字列として扱われ続ける（第4節のTest「attributes stay inert text」で明示的に保証）。`<br>`自体は構造上いかなる属性・Payloadも持ち得ないTagであるため、この一点のみを実HTML Elementとして描画しても、「生HTMLを一切Renderしない」というSecurity Invariantは実質的に損なわれない。

`parseInline`はTable Cellだけでなく、見出し・段落・List項目・引用等、全てのInline Context共通で使われる関数のため、本修正は表Cellに限定せず全Inline Contextへ一律適用される（Design判断：Table専用の特別扱いを個別実装するより、共通層で一度だけ扱う方が単純で一貫性がある）。

## 4. Validation

- Vitest：[safeMarkdown.test.tsx](../../../../../frontend/src/lib/safeMarkdown.test.tsx)へ3件追加（`<br>`/`<br/>`/`<br />`/`<BR>`全variantがbreak nodeになること、属性付き`<br onclick="...">`は引き続き無害な文字列のままであること、表Cell内で複数の`<br>`が正しく複数のbreak nodeへ変換されること）。計18/18 Pass。
- ESLint・`tsc --noEmit`・`vite build`：Clean。
- 実Browser確認（Local LLMサーバー一時Instance）：実際に「各セル内に複数の箇条書きを`<br>`で改行して詰め込んだ...表」を生成させ、`hasLiteralBrText: false`・`realBrElements: 34`（文字列としての`<br`は0件、実`<br>`Element 34件）をJavaScript直接測定で確認。Screenshotでも、Cell内が複数行のList状に正しく折り返されて表示されていることを確認。

## 5. Status

```text
Current Point            : 表Cell内`<br>`混入問題を修正完了。
Files Created／Modified   : frontend/src/lib/safeMarkdown.tsx、
                            frontend/src/lib/safeMarkdown.test.tsx、
                            本Evidence File。
Validation                : Vitest 18/18 Pass、ESLint／tsc／Build Clean、
                            実Browser確認Clean。
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし。次のユーザー指示待ち。
```
