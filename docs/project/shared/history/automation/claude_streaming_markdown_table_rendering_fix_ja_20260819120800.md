# Claude側設計統括者役 — Markdown表（Table）レンダリング崩れの修正

```yaml
document_id: claude_streaming_markdown_table_rendering_fix_20260819120800
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
role: design_governor
created_at: 2026-08-19 12:08:00 JST
language: ja
```

## 1. 経緯

ユーザーが実機確認で発見した問題（前回Recovery Index作成時点では「1はまだ何もしないで」と保留指示があったもの）に対し、その後のユーザー指示「表Markdown崩れの方に着手してくれ」を受けて着手した。

事象：本来、見出しと空行を挟んで

```text
| 能力 | 機能 | 説明 |
|------|------|------|
| ✅ 文章生成 | ✅ | 自然な文章をつくる |
```

のように改行を保った表として出力されるべきところ、実際は

```text
📈 性能と能力
| 能力 | 機能 | 説明 | |------|------|------| | ✅ 文章生成 | ✅ | 自然な文章をつくる | ...
```

のように1行に連結され、表として成立していなかった。

## 2. 根本原因

[frontend/src/lib/safeMarkdown.tsx](../../../../../frontend/src/lib/safeMarkdown.tsx)の独自Markdown Parser（`parseSafeMarkdown`）には、GFM Pipe Table用のBlock型が一切存在しなかった。`|`で始まる行は、既存のどのBlock検出条件（見出し・水平線・引用・リスト）にも一致せず、最終的に汎用の`paragraph`分岐へ落ちる。

その`paragraph`分岐は、連続する非空行を`\n`で連結して単一のTextNodeにまとめる実装になっており、`renderInline`はその`\n`を含む文字列をそのまま`<Fragment>`として描画していた。CSSの`white-space`が既定の`normal`であるため、Text Node内の生の改行文字はBrowser上で空白1個に折り畳まれる——これが「改行なしで出してる」ように見えた直接の機序である。パーサー自体は改行を保持していたが、Browserの空白折り畳み仕様により視覚的に失われていた、という点が実態。

## 3. 修正内容

### 3.1 Parser拡張（`safeMarkdown.tsx`）

- 新規`BlockNode`型`table`を追加（`align: TableAlignment[]`, `header: InlineNode[][]`, `rows: InlineNode[][][]`）。
- Header行の直後にGFM形式のDelimiter行（`:?-+:?`をCellごとに`|`区切りしたもの）が続く場合にのみTableとして検出する。Header行単体では（Delimiter行がまだStreamingで届いていない場合を含め）既存のParagraph Fallbackへ安全に委ねる——Streaming中の未完成状態でも例外を投げない設計は、既存のStreaming Markdown実装（[claude_streaming_markdown_rendering_ja_20260819110633.md](claude_streaming_markdown_rendering_ja_20260819110633.md)）の方針を踏襲。
- Cell分割は、Escapeされた`\|`をCell区切りとして扱わないよう実装（`splitTableRow`）。
- Alignment指定（`:---`・`:---:`・`---:`）をParseし、`th`/`td`への`text-align`Styleへ反映。
- `startsBlock`（段落継続判定）に「非空行かつ`|`を含む」を追加し、既存の段落へTable行が誤って連結されないようにした。

### 3.2 Rendering拡張（`safeMarkdown.tsx`の`renderBlock`）

`table`Block型を`<table><thead><tr><th>...</th></tr></thead><tbody><tr><td>...</td></tr>...</tbody></table>`として描画。

### 3.3 CSS（`frontend/src/styles/app.css`）

`.message-markdown table/th/td`のStyleを新規追加（枠線・Header背景・Padding）。既存の`--border-strong`・`--bg-inset`Token を再利用し、White/Dark両Themeで自動的に整合する。

## 4. 実装中に発見した追加の頑健性課題（実LLM出力による検証で判明）

実装後、実際のLocal LLM（`qwen3-4b`）へ表形式出力を要求して実Browser検証を行ったところ、モデルがDelimiter行の末尾に`|`を二重出力するCase（例：`|------|------||`）が実際に観測された。当初のDelimiter行判定は各Cellが厳密に`/^:?-+:?$/`へ一致することを要求しており、この二重Pipeによって生じる空Cellにより判定が失敗し、Tableとして認識されなかった（各行が個別のParagraphとして表示される状態——1行連結よりは改善しているが、真の目標である「枠付きTable」には至っていなかった）。

Delimiter行のCellが空になるのは、構造上（最低1個のHyphenを要求するため）Pipeの重複等のArtifact以外にありえないため、Delimiter行判定時にのみ空Cellを除外する修正を行った（`isTableDelimiterRow`・Alignment算出の双方）。Header行・Body行側のCell（実データ）に対しては、意図的な空Cellもあり得るため、この除外Logicは適用していない。

## 5. Validation

- Frontend Unit Test（Vitest）：[safeMarkdown.test.tsx](../../../../../frontend/src/lib/safeMarkdown.test.tsx)へ8件追加（既存8件と合わせ計16件、全件Pass）。基本Table・Alignment・Escaped Pipe・Delimiter行欠落時のParagraph Fallback・Streaming途中でのDelimiter行未到達時の非例外・実観測された二重Pipe Delimiterへの耐性、Table描画（`<table>`/`<thead>`/`<tbody>`実体化）・Alignment Styleの反映を対象とした。
- ESLint：対象File（`safeMarkdown.tsx`・`safeMarkdown.test.tsx`）Clean（初回、`textAlign`への不要な非Null Assertionを2件検出・修正済み）。
- TypeScript型検査（`tsc --noEmit`）・Production Build（`vite build`）：Clean。
- 実Browser確認（Local LLMサーバー、`http://127.0.0.1:8001`、実装検証用の一時Instance）：
  - Dark／White両Themeで、実際の生成結果が本物の`<table>`要素（`<thead>`3 Header Cell・`<tbody>`複数Row）として枠付きで描画されることを確認。
  - Streaming途中（生成完了前）の時点でも、既に完成済みの表部分がTableとして正しく描画されており、崩れが生じないことを確認。
  - 上記第4節の二重Pipe Delimiter Caseは、修正後に同一会話を再読込することで再描画させ、正しくTable化されることを確認（`tables:1, headCells:3, bodyRows:10`）。

## 6. 付随観測（Bugではないが記録）

検証中、モデルが表全体を```` ```markdown ```` の Fenced Code Block で囲んで出力するCaseが1回観測された。この場合、`<pre><code data-language="markdown">`として、生のPipe構文を含む文字列がそのままCode Blockとして描画された。これはCommonMark仕様上正しい挙動（Fence内のContentはLiteralとして扱われ、Markdown構文解釈の対象外）であり、既存の`code_block`処理（本修正では変更していない）がそのまま機能した結果である。今回のBugとは無関係のため、追加対応は行っていない。

## 7. 別途発見した無関係の既存問題（本作業対象外）

Validation実行中、`frontend/src/App.test.tsx`・`frontend/src/hooks/usePreference.test.tsx`が、`TypeError: window.localStorage.clear is not a function`／`window.localStorage.removeItem is not a function`で失敗することを発見した。本修正が触れたFile（`safeMarkdown.tsx`・`safeMarkdown.test.tsx`・`app.css`）を含めずに該当2File単独でVitestを実行しても再現するため、本修正とは無関係の、既存のTest基盤側の問題（jsdom環境における`localStorage`実装の問題と推測）と判断した。本節はユーザーへの透明性のための記録のみとし、修正はScope外として行っていない。

## 8. Status

```text
Current Point            : Markdown表のStreaming中崩れ問題を修正完了。実LLM
                            出力での追加耐性課題も含め解消。
Files Created／Modified   : frontend/src/lib/safeMarkdown.tsx、
                            frontend/src/lib/safeMarkdown.test.tsx、
                            frontend/src/styles/app.css、本Evidence File。
Validation                : Vitest 16/16 Pass、ESLint Clean、tsc Clean、
                            vite build Clean、実Browser確認（Dark／White、
                            Streaming中・完了後）Clean。
Open Current Blocker      : NONE
Controller-owned Next Work: 第7節のTest基盤問題（localStorage）は、ユーザー
                            への報告のみで対応保留。対応要否はユーザー判断
                            待ち。
```
