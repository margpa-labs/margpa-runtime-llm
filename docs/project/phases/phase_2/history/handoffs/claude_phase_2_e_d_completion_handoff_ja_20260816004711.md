# Claude Phase 2-E-D Completion Handoff — White/Dark Theme

```yaml
document_id: claude_phase_2_e_d_completion_handoff_20260816004711
status: implementation_complete
phase: phase_2
subphase: phase_2_e_d
from: Claude側設計統括者役
to: ユーザー（最終確認者）／Codexプロジェクト責任者兼設計統括者役
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-16 00:47:11 JST
language: ja
authorization: ユーザーからの明示的な全権委任（2026-08-15夜、Bypass Permissions実験を兼ねる）
```

## 1. Mission

ユーザー依頼「2-E-D」：画面全体のDark基調に加え、White（Light）基調のModeを追加する。既存の「日本語 | English」切替の近くに「White | Dark」切替を設置し、規定値はWhiteとする。配色は裁量に一任（「見やすければOK」）。

本Handoffは**実装完了時点**の報告である。契約どおり、最終的な「2-E-D完了」判定はユーザー自身が画面を見て行う。

## 2. 設計判断

### 2.1 既存Patternの踏襲

`日本語／English`切替（`UI_LANGUAGE_KEY`、`localStorage`、`readStoredUiLanguage`／`setUiLanguage`／`applyTranslations`）の実装を先に読み、同じ構造でTheme版（`UI_THEME_KEY`、`readStoredUiTheme`／`setUiTheme`／`applyTheme`）を実装した。

### 2.2 CSS Custom Property化（既存構造からの唯一の逸脱）

`app.css`は元々39種の色Literalを各SelectorへHardcodeしており、CSS変数は一切使われていなかった。Theme切替を実現するため、33個の意味的Token（`--bg-page`、`--text-primary`、`--accent-primary`等）へ再構成し、`:root`（White既定値）と`:root[data-theme="dark"]`（既存Dark値をそのまま保存）の2Blockへ分離した。レイアウト・余白・SizeなどColor以外のPropertyは一切変更していない。

### 2.3 規定値WhiteとFOUC（Flash of Unstyled Content）についての判断

CSPが`script-src 'self'`（`'unsafe-inline'`なし）のため、Head内Inline ScriptによるTheme早期適用（よくあるFlash防止Hack）は採用できない（CSPで実行Blockされるため）。`:root`をWhite既定にすることで、初回訪問者・既定値のままのUserには**Flashが一切発生しない**設計にした。影響が出るのは「過去にDarkへ切り替えたUser」だけで、その場合も`/assets/app.js`（`type="module"`）のRead-only処理が走るまでの、ごく短い間だけの一過性の見た目である。CSPを緩める形での回避は行っていない（Security Postureを維持）。

### 2.4 個別の実装上の注意点（発見・対応した実装Detail）

- `.message-user`（自分の発言Bubble）はDark版で明示Colorを持たず、`body`のText Colorを暗黙に継承していた（Dark Themeでは近White Textだったため偶然成立）。Light Themeでは`body`のText Colorが近Blackになるため、そのままでは青いBubble上に読みにくい暗Textが乗る。明示的に`--message-user-text`Tokenを新設し、両Themeで正しく効くようにした。
- `.secondary`Button（新規Chat・再読み込み等の大半のButton）も同様に、Dark版はGeneric`button{color:...}`のNear-white文字色に依存していたが、Light版では背景が明るいGrayになるため、そのままでは読みにくい。`--button-secondary-text`Tokenを新設し、`.secondary`へ明示指定した。

この2点は、単純な色置換だけでは発生していたはずの可読性問題であり、実装中の確認で発見・修正した。

## 3. 実装内容

```text
src/margpa_runtime_llm/web/static/app.css
  - :root（White既定）／:root[data-theme="dark"]の2 Token Block新設
  - 既存の全Color宣言をvar(--token)参照へ置換（Layout/Spacing等は無変更）
  - .theme-switcher／.theme-button Selector新設（.language-switcher／.language-buttonと対）

src/margpa_runtime_llm/web/static/index.html
  - #ui-language-switcherの左に#ui-theme-switcher（White｜Dark Button）を追加

src/margpa_runtime_llm/web/static/app.js
  - UI_THEME_KEY = "margpa.ui_theme.v1"、DEFAULT_UI_THEME = "white"
  - readStoredUiTheme()／setUiTheme()／applyTheme()（既存Language関数と対称構造）
  - translations.{ja,en}.uiThemeLabel 追加
  - elements.uiThemeWhite／uiThemeDark 参照、Click Listener登録
```

## 4. Test更新・新規Test

```text
tests/unit/web/test_persistent_static_contract.py
  - test_browser_storage_contains_only_interface_language_not_conversation_text を
    test_browser_storage_contains_only_interface_preferences_not_conversation_text へ改名。
    localStorage.setItem呼び出し数の期待値を 1 → 2 へ更新（Theme分の正当な追加）。

tests/integration/web/test_web_app.py
  - test_static_assets_are_local_thinking_aware_phase_1i_ui の
    script.count("localStorage.") 期待値を 2 → 4 へ更新。

tests/unit/web/test_theme_static_contract.py（新規）
  - Theme切替Markup・既定Whiteの検証
  - JS側のKey／関数／Event Listener存在の検証
  - CSSがLight既定＋Dark Overrideの2 Block構造であること、両Blockに主要Tokenが
    揃っていること、Inline Styleが使われていないことの検証
```

これら3件のPrivacy／Static Contract Testは、いずれも「Browser Storageに何が保存されるか」「Theme構造が正しいか」を機械的に固定するための、既存の設計哲学（Exact Contract Test）に沿った更新である。

## 5. Validation結果

```text
Test    : 679 passed, 3 deselected（既定Suite、新規3件含む）
静的解析: ruff check . — All checks passed
        mypy src/ — Success: no issues found in 117 source files
```

## 6. 実Browser確認

実Server起動（`--conversation-persistence --configuration-control`他、通常Contract）、実際に画面を確認した。

```text
White（既定）: Screenshotで確認。Header・Theme切替・Configuration Controlの
  Field Grid、いずれも高い可読性で表示されることを確認。
Dark          : Theme切替をClickし、Screenshotで確認。既存の見た目と完全に一致
  （後述、Computed Style直接比較でも裏取り済み）。
永続化        : ページRe-load後もDark選択が維持されることを確認（localStorage経由）。
Computed Style直接比較:
  White: --bg-page → rgb(247,248,251) (#f7f8fb)、送信Button背景 → rgb(74,95,224)
         (#4a5fe0)、TextArea背景 → rgb(241,243,247) (#f1f3f7) 等、設計値どおり。
  Dark : messages背景 → rgba(18,21,29,0.92)、送信Button背景 → rgb(86,109,232)
         (#566de8)、body背景 → rgb(11,13,18) (#0b0d12) 等、変更前のHardcode値と
         完全一致（Regressionなし）。
```

**Browser Preview Toolの制約について（今回の作業に起因しないTool側の挙動）**：Screenshotが特定のScroll位置で無地に見える事象を観測したが、`getComputedStyle`によるDOM直接照会では該当箇所の背景色・文字色とも設計どおりの値を返しており、実際の描画は正しいと判断した。原因はこのBrowser Preview Tool側のScreenshot Capture Timingに起因すると考えられ、本Projectの実装側の不具合ではない。**教訓として`claude_side_design_governor_operating_notes_ja.md`へ記録した**（Theme／可視性に関わる検証はScreenshotだけでなく`getComputedStyle`等の直接照会も併用するとよい、という運用知見）。

## 7. Mutation境界

```text
新規変更File: 上記6File（app.css/index.html/app.jsのSource 3File、Test 3File(新規含む)）
実runtime_data/: Server起動・Browser確認のみ、実Conversation Data非改変
                （mtime、既存確認済みの値から不変）
Stable Docs／Git／Provider Memory／.claude/settings.local.json: 無変更
```

## 8. Status

```text
Current Point            : 実装完了。ユーザーによる画面上での最終確認待ち。
Files Created／Modified   : 第7節のとおり。新規Docsは本File＋関連Evidence（別File）。
Validation                : 679 passed / 3 deselected、ruff／mypy Clean、実Browser確認済み。
Open Current Blocker      : NONE
Controller-owned Next Work: ユーザーによる最終確認 → 「2-E-D完了」の宣言はユーザー自身が行う。
Exact Next Route          : ユーザー確認待ち。
```
