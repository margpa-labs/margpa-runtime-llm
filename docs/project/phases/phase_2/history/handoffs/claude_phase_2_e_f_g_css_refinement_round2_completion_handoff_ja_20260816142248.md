# Claude Phase 2-E-F/G CSS微調整（第2弾）Completion Handoff

```yaml
document_id: claude_phase_2_e_f_g_css_refinement_round2_completion_handoff_20260816142248
status: implementation_complete
phase: phase_2
subphase: phase_2_e_f_g_refinement
from: Claude側設計統括者役
to: ユーザー（最終確認者）／Codexプロジェクト責任者兼設計統括者役
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-16 14:22:48 JST
language: ja
authorization: ユーザーの実画面確認後の明示CSS修正依頼（2026-08-16、
  「ちょうど制限解除された」に続く一連のChat指示、最終的に「修正よろしく」）
related:
  - claude_phase_2_e_f_g_css_refinement_completion_handoff_ja_20260816132247
```

## 1. Mission

第1弾CSS微調整の実画面確認後、ユーザーが追加で提起した6項目の修正。

```text
1. Sidebar Preview Note（「この画面はResearch Previewです」ブロック）の背景透過
2. Header行（White|Dark・日本語|English）をFixed化、常時最前面表示
3. Composer（メッセージ入力欄）も同様にFixed化
4. Composer幅を「Sidebar状態に応じたMain Chat画面の40%」へ
5. Messages Log幅も同様に40%へ（Composerと同じ幅で縦に整列）
6. Copy／再生成／Branch選択Buttonを1つのRowへ統合、同じSize、右から
   Copy・再生成・Branch選択の順
```

## 2. 実装内容

```text
frontend/src/components/MessageBubble.tsx（改修）
  旧来別々だった.message-actions（Copyのみ）と.persistent-turn-actions
  （再生成／Branch選択）を1つの.message-actions Rowへ統合。
  再生成／Branch選択ButtonをCopy Buttonと同じClass（message-copy
  secondary）にし、Sizeを完全に統一。

frontend/src/App.tsx（改修）
  buildTurnActions()内の配列順序をselectBranch→regenerateへ入れ替え
  （DOM順序＝画面表示順であり、右寄せRowでは末尾ほど右端に来るため、
  Copyを最後に描画することで「Branch選択・再生成・Copy」の並びを実現）。
  .app-shellへdata-sidebar-visible属性を追加（Sidebar状態をCSS側へ
  伝えるための唯一の橋渡し）。

frontend/src/styles/app.css（大幅改修）
  - .app-shellに--sidebar-width（288px、唯一の定義箇所）と
    --sidebar-offset（data-sidebar-visible="false"時は0pxへ切替）を追加。
    .sidebarの幅もこの変数を参照するよう統一。
  - .sidebar-preview-noteの背景をvar(--bg-inset)からtransparentへ。
  - .topbar／.composerをposition: fixedへ変更（z-index: 40）。
  - .composerの横幅を`calc((100vw - var(--sidebar-offset)) * 0.4)`、
    left: var(--sidebar-offset); right: 0; margin: 0 auto;で、
    Sidebar状態に応じて自動追従するCenteringを実装。
  - .messagesの横幅もvar(--chat-column-width)（40%、.main-content基準）
    で統一——ComposerとMessagesが常に同じ幅で縦に揃う。
  - .main-contentのPaddingを拡張（Fixed化したTopbar／Composerの下に
    隠れないよう、Scroll時の実Content用余白を確保）。
  - 旧.persistent-turn-actions Selectorを削除（Dead CSS）。
```

## 3. 実装中に発見・修正した問題（実装方針の転換）

### 3.1 「Position: FixedのContaining Block化」がScroll Containerと共存できない問題

当初、`.main-content`に`transform: translateZ(0)`を付与し、`position: fixed`の子要素（Topbar／Composer）をViewport全体ではなく`.main-content`自身のBoxへ紐付ける実装を試みた（第1弾のHandoffで記録した`.app-shell`高さ固定化と同じ発想の延長）。

しかし実Browser確認したところ、`.main-content`自体が`overflow-y: auto`のScroll Containerでもあるため、`transform`によるContaining Block化は「Fixed要素をViewportに固定する」効果ではなく、**「Fixed要素を、Scrollする中身の座標系に閉じ込める（Scrollと一緒に動いてしまう）」効果になってしまう**ことが判明した（Position: Fixedの子要素がAbsolute相当の挙動になり、Scroll量に応じてViewport外へ流れて消えてしまった）。

対応として、この方式を撤回し、`.app-shell`側でSidebar状態を`data-sidebar-visible`属性として保持し、そこから導出したCSS変数（`--sidebar-offset`）を、真にViewport基準のPosition: FixedであるTopbar／Composerから`calc()`経由で参照する方式へ切り替えた。CSS Custom Propertyは、Position: Fixedの「配置基準」には影響を受けず、DOM階層に沿って通常どおり継承されるため、この方式であればFixed要素を正しくViewportへ固定したまま、Sidebar幅の変化にも追従できる。

## 4. Validation結果

```text
Frontend:
  npm run lint       : Clean（0 errors）
  npm run typecheck   : Clean（0 errors）
  npm test             : 64 passed（新規MessageBubble.test.tsx 3件を追加
                          ——Action Row統合・Size統一・並び順・Click時の
                          Callback呼び出しを検証）
  npm run build         : 成功（app.js 245.39kB / gzip 75.58kB、
                          app.css 15.15kB / gzip 3.91kB）

Backend（Frontend専用変更のため無影響を確認）:
  pytest -q           : 664 passed, 3 deselected（変化なし）
```

## 5. 実Browser確認（実LLM、実Backend、White／Dark両Theme）

```text
Preview Note透過: Sidebar内Preview Note Blockの背景が他のBlockと同化
                  することを確認。
Fixed Header/Composer: 長い会話をScrollしても、Header行・Composer
                  いずれも画面上の同じ位置に留まり続けることを確認
                  （第3.1節の問題修正後）。
幅の追従        : Sidebar表示中・非表示中それぞれで、Composer・
                  Messagesの幅が「その時点のMain Chat領域の40%」へ
                  正しく追従し、かつ両者が常に同じ幅で縦に揃うことを
                  確認。
最終Message到達性: 長い会話をScrollし最下部まで到達させても、最後の
                  MessageとそのAction Rowが、Fixed Composerに隠れず
                  完全に見えることを確認（.main-content Padding調整
                  により確保）。
Action Row統合  : 完了済みTurnで「Branch選択」「再生成」「Copy」が
                  1つのRow・同じSize・右寄せで、右端がCopyになる順序
                  で表示されることを確認。
```

## 6. Mutation境界

```text
新規: frontend/src/components/MessageBubble.test.tsx、Docs本File
変更: frontend/src/components/MessageBubble.tsx、App.tsx、styles/app.css
      src/margpa_runtime_llm/web/static/*（Build出力による置換）
実runtime_data/: 実Browser確認は既存会話のView・Scroll・Theme切替のみで、
      新規書き込みは発生していない。
Stable Docs／Git／Provider Memory／.claude/settings.local.json: 無変更
```

## 7. Status

```text
Current Point            : CSS微調整第2弾6項目すべて実装完了。実装方針の
                            転換を伴う技術的問題も解消。
Files Created／Modified   : 第6節のとおり。
Validation                : Frontend/Backend双方Clean、実Browser確認済み
                            （White／Dark両Theme、第5節）。
Open Current Blocker      : NONE
Controller-owned Next Work: ユーザーによる最終確認。
Exact Next Route          : ユーザー確認待ち。
```
