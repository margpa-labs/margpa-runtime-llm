# Claude側設計統括者役 — 表Cell内箇条書きMarker（`-`）残留の修正

```yaml
document_id: claude_table_cell_bullet_marker_fix_20260819133331
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
role: design_governor
created_at: 2026-08-19 13:33:31 JST
language: ja
```

## 1. 経緯

[claude_table_cell_br_line_break_fix_ja_20260819132416.md](claude_table_cell_br_line_break_fix_ja_20260819132416.md)（`<br>`混入修正）の直後、ユーザーが同一箇所に別の残留問題を発見：`<br>`は消えて正しく改行されるようになったが、`- 会話型LLM`のように箇条書きMarkerとして使われていた行頭の`-`が、そのまま文字として残ってしまう。

## 2. 根本原因

`safeMarkdown.tsx`のBlock Level Parser（`parseSafeMarkdown`）は、行頭の`- `を`unordered_list`Blockとして正しく検出するが、これは各行が独立した「行」として存在する通常の段落・リストにのみ適用される。表Cellの内容は、複数の論理行が`<br>`という単一のInline要素で連結された、Block Parserからは一枚岩の文字列であり、Block Level のList検出を経由しない（`parseInline`へ直接渡される）。そのため、Cell内で`<br>`区切りにより擬似的に複数行化された`- 箇条書き`は、単なる文字列の一部として扱われ、行頭の`-`がそのまま出力されていた。

## 3. 修正内容

[safeMarkdown.tsx](../../../../../frontend/src/lib/safeMarkdown.tsx)の`parseInline`へ、「現在行の先頭にいるか（`atLineStart`）」を追跡する状態を追加した。`atLineStart`は、文字列の先頭（index 0）と、直前に`<br>`（`break`Node）を処理した直後にのみ真になる。この状態で` {0,3}[-*+]\s+`（Block Level Listの検出正規表現と同じPattern）に一致した場合、そのMarker部分をBullet文字「• 」へ置換する。

Payloadを持ち得る本格的なList構造（`<ul><li>`のNestingを`<td>`内に持たせる）ではなく、視覚的なBullet文字への単純な置換とした——表Cellという限定的な文脈のためのList構造Nestingは複雑さに見合わないと判断（既存Parserの一貫した「必要十分な単純さ」の設計方針に沿う）。

`atLineStart`が真になるのは文字列先頭と`<br>`直後のみであり、通常の段落・リスト・見出し等（`- `始まりの行はBlock Level側で既に`unordered_list`として処理されるため、この経路には到達しない）には影響しない。文中の`-5`のようなMid-line Hyphenも、`atLineStart`が偽であるため一致せず、従来通り無変更のまま出力される。

## 4. Validation

- Vitest：[safeMarkdown.test.tsx](../../../../../frontend/src/lib/safeMarkdown.test.tsx)へ2件追加（`<br>`直後の`-`/`*`/`+`Markerが全てBullet文字へ変換されること、文中のMid-line Hyphenは無変更であること）。計20/20 Pass。
- ESLint・`tsc --noEmit`・`vite build`：Clean。
- 実Browser確認（Local LLMサーバー一時Instance）：ユーザー報告の実際のCell内容（「- 会話型LLM」「- 語彙豊か」「- 自然な対話が得意」）を実際に生成させ、`hasLiteralDash: false`・`hasBullet: true`・`realBrElements: 6`を直接測定で確認。Screenshotでも、各行が「• 」始まりの箇条書きとして正しく表示されることを確認。

## 5. Status

```text
Current Point            : 表Cell内箇条書きMarker残留問題を修正完了。
                            `<br>`混入修正（第2節参照先Doc）と合わせて、
                            表Cell内の複数行箇条書き表現が完全に正しく
                            描画されるようになった。
Files Created／Modified   : frontend/src/lib/safeMarkdown.tsx、
                            frontend/src/lib/safeMarkdown.test.tsx、
                            本Evidence File。
Validation                : Vitest 20/20 Pass、ESLint／tsc／Build Clean、
                            実Browser確認Clean。
Open Current Blocker      : NONE
Controller-owned Next Work: 特になし。次のユーザー指示待ち。
```
