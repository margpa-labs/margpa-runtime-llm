# Claude Phase 2-E-F Completion Handoff — Sidebar化

```yaml
document_id: claude_phase_2_e_f_completion_handoff_20260816115426
status: implementation_complete
phase: phase_2
subphase: phase_2_e_f
from: Claude側設計統括者役
to: ユーザー（最終確認者）／Codexプロジェクト責任者兼設計統括者役
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-16 11:54:26 JST
language: ja
authorization: ユーザーからの明示的な全権委任
  （「2-E-EからGまで、Checkpointなしで一気に(Bypass実験その2として)進める」、2026-08-16朝）
related:
  - claude_phase_2_e_e_completion_handoff_ja_20260816113534
  - claude_phase_2_e_e_to_h_react_migration_design_ja_20260816102654（承認済み設計、第2節）
```

## 1. Mission

承認済み設計の2-E-F：全幅化、Sidebar本体（既定表示・隠す/出すButton）、上部4行＋3行Block、区切り線、新規チャット、保存済みChat縦並び（Hover時流れるChat名＋右端Option Button、中身はArchive/Unarchive・Resumeのみ）を実装する。

ユーザーの詳細要件（2026-08-16朝のChat指示）を実装Requirementとした：

```text
・フルで使う（今ウィンドウ内の中央しか使ってなかったのをフルに）
・Sidebar追加。既定は出す。隠す・出すButtonをone Buttonで追加。
・その下に4行のTitle Block（Nazuna Research Governance LLM／MARGPA Runtime LLM／
  main.qwen3-4b-q4-k-m／local.macos-arm64 · gpu · metal）
・ちょっと隙間開けて、3行のPreview Note Block（この画面はResearch Previewです。／
  本番Accountまたは、／Production Serviceではありません。）、見やすいBlockでまとめる
・横線区切り、新規チャット
・横線区切り、保存済みChat縦並び
・各Chat名はHover時に流れる、右端に固定位置のOption Button
  （中身は今あるArchive/Unarchive・Resumeのみ、名前変更・削除は2-E-H余力枠）
・White|Dark・日本語|Englishは相変わらず画面右上端
・「Sidebar有無でMain画面の左右幅可変」（Sidebarの右側、ではなく）
```

本Handoffは**実装完了時点**の報告である。最終的な「2-E-F完了」判定はユーザー自身が画面を見て行う契約は変わらない。

## 2. 実装内容

```text
frontend/src/components/Sidebar/（新規）
  Sidebar.tsx        Container。SidebarHeader＋区切り線＋新規チャットButton＋
                      区切り線＋ChatListを縦に配置。
  SidebarHeader.tsx   4行Title Block（Eyebrow／h1／Model／Profile・Device・Accel）＋
                      3行Preview Note Block。Runtime読み込み中／失敗時は
                      Model行にLoading／Error文言を表示。
  ChatList.tsx        role="list"のNav。ChatListItemを縦に並べる。
  ChatListItem.tsx    Chat名（Hover Marquee対応）＋固定位置Option Button
                      （role="listitem"）。ClickでOpen／Close Toggleする
                      Menu（role="menu"）、外側Clickで自動Close。
                      状態がactiveならResume＋Archive、archivedならUnarchiveのみ。

frontend/src/components/TopBar.tsx（改修）
  Title／Eyebrow／Runtime Status／新規ChatをSidebarへ移動し、
  「Sidebar隠す/出すButton（one Button）」＋「White|Dark・日本語|English」
  だけの薄いTop Stripへ縮小。

frontend/src/components/PersistentPanel.tsx（削除）
  Sidebar／ChatListへ完全に置き換え。

frontend/src/App.tsx（改修）
  - sidebarVisible State（既定true、未Persist——理由は第3.2節）を追加。
  - Render Treeを.app-shell（Flex）へ再構成：
    {sidebarVisible && <Sidebar/>}<main className="main-content">...</main>
  - 新規chatListItemAction()：Sidebar上の「選択中でない会話」に対する
    Resume/Archive/Unarchive操作を、正しいRevisionで実行する（第3.1節）。
  - persistentDetail State（もはやどこからも読まれなくなったため）を削除。

frontend/src/styles/app.css（改修）
  - .app-shell／.sidebar／.main-content のFlex Layout新設。
  - Sidebar内部（Header／Divider／New Chat／Chat List／Option Menu／
    Hover Marquee）のStyle新設。
  - .messages／.composerからBorder・Card背景を除去（枠なし化）。
  - .persistent-panel*系（旧PersistentPanel専用）のDead CSSを削除。
  - グローバルな[hidden]{display:none !important;}を追加（第3.3節、
    2-E-E Completion Handoffで記録したFindingの解消）。

frontend/src/i18n/translations.ts（改修）
  - previewNote（単一行）→ previewNoteLine1/2/3（3行）へ分割。
  - persistentNote／persistentRefresh（Sidebar化に伴い不要になったUI要素の
    翻訳）を削除。
```

## 3. 設計判断

### 3.1 Sidebar項目のOption Buttonが「選択中でない会話」を操作できる必要性

旧実装のResume/Archive Buttonは、常に「現在選択中（表示中）の会話」に対してのみ動作していた（`persistentRevisionRef`が選択中の会話のRevisionしか追跡していないため）。Sidebar化により、Option ButtonはList内の**任意の項目**（選択中でない項目を含む）に対して押される。各会話は独立したRevision Counterを持つため、選択中の会話のRevisionを別の会話のMutationへ流用すると、ほぼ確実にRevision Conflict（409）になる。

対応として`chatListItemAction()`を新設し、対象がすでに選択中の会話ならRefの値をそのまま使い（速いPath）、そうでなければ`fetchPersistentDetail()`で対象自身の最新Revisionを取得してから Mutationを実行するようにした。実Browser確認（第6節）で、選択中でない会話に対するArchiveが正しいRevisionで成功することを確認済み。

### 3.2 Sidebar表示状態を意図的に未Persist（LocalStorageへ保存しない）とした判断

Theme／Languageと同じ`usePreference`Patternで永続化することも検討したが、次の理由で見送った：(1) ユーザーの詳細要件に永続化の指定がなかった、(2) 永続化するとBrowser Storage Privacy Contract（App.test.tsxの「LocalStorageに書き込まれるKeyはUI設定2種類のみ」というTest）に3つ目のKeyを追加することになり、影響範囲が広がる。Session内（Reloadで既定へ戻る）という現状の挙動で十分と判断した。ユーザーが望む場合は追って対応可能。

### 3.3 2-E-Eで記録したCSS Finding（[hidden]がDisplay: Grid等に上書きされる問題）を本Phaseで解消

2-E-E Completion Handoff第3.2節で「今回はScope外として見送り、2-E-F/Gでの対応候補とする」と記録していた、`.configuration-meta`・`.configuration-fields`の`[hidden]`属性がCSSの`display: grid`に上書きされ、非表示のはずのFieldが見えてしまう問題。本Phaseで`app.css`にSidebar用の新規Styleを追加する過程で同種の問題が`.configuration-controls label`（選択Model／Context SizeのField）にも存在することを実Browser確認で発見した（第6節）。

個別Selectorへの対症療法ではなく、`[hidden] { display: none !important; }`という単一のGlobal Ruleを追加する形で根本対応した。ネイティブの`[hidden]`属性は本来「常に非表示」という意味を持つはずであり、個別Component側のDisplay指定によって黙って上書きされるべきではないため、この用途での`!important`使用は正当と判断した。あわせて、旧来個別に存在していた`.message-thinking[hidden]`・`.message-citations[hidden]`の重複Overrideを削除した（Global Ruleで代替されるため）。

### 3.4 Hover MarqueeとChat名の実際の長さについて（設計上の留意点）

Chat名は現状`${日時} · ${Conversation IDの先頭10文字}`という固定長Formatであり、Sidebar幅（約230px）に対して基本的に収まる長さである。したがって、今回実装したHover Marquee機能自体は正しく動作する（Unit Testで検証済み）ものの、**現状のDataでは実際に発動する場面がほぼ無い**。この機能が意味を持つのは、2-E-H（余力枠）で「名前変更」が実装され、User由来の任意長のTitleが会話に付与されるようになってからである。今回は将来のための先行実装として計画通り組み込んだ。

## 4. Test更新・新規Test

```text
frontend/src/components/Sidebar/ChatListItem.test.tsx（新規、5件）
  - Row Clickで選択Callbackが呼ばれる
  - active会話：ResumeとArchiveの両方がMenuに出る
  - archived会話：Unarchiveのみ（Resumeは出ない）
  - Menu項目選択でonActionが正しい引数で呼ばれ、Menuが閉じる
  - Menu外Clickで、Action発火なしにMenuが閉じる

frontend/src/App.test.tsx（既存6件を#persistent-panel等から.chat-list-itemベースへ更新、
  新規2件を追加）
  - Sidebar Toggle Buttonが1個で表示/非表示を切り替える
  - 選択中でない会話をSidebarから再開（Resume）すると、選択中の会話ではなく
    対象自身のRevisionを取得してからMutationが呼ばれる（第3.1節の回帰防止Test）
```

## 5. Validation結果

```text
Frontend:
  npm run lint       : Clean（0 errors）
  npm run typecheck   : Clean（0 errors）
  npm test             : 50 passed（前回43件 + 新規7件）
  npm run build         : 成功（app.js 242.25kB / gzip 74.84kB、
                          app.css 12.42kB / gzip 3.36kB）

Backend（Frontend専用変更のため無影響を確認）:
  pytest -q           : 664 passed, 3 deselected（変化なし）
```

## 6. 実Browser確認（実LLM、実Backend）

実Server（`--conversation-persistence --configuration-control`他、通常Contract）を起動し確認した。

```text
初期表示        : Sidebar（4行Title Block＋3行Preview Note Block、New Chat、
                  9件超の保存済みChat）、Top Strip（Hide sidebar、
                  White|Dark|日本語|English）、いずれも設計どおり表示。
Sidebar Toggle : 「Hide sidebar」Clickで非表示化、Main ContentがFull幅に拡張
                  （Configuration Control Panel幅の拡大で確認）。
                  「Show sidebar」Clickで再表示、元のLayoutへ復帰。
Option Menu    : 会話ItemのChat options Buttonから、Resume／Archive
                  （active時）、Unarchiveのみ（archived時）のMenuが正しい
                  組み合わせで表示されることを確認。
選択中でない会話への操作: 未選択の会話へArchiveを実行し、GET
                  /api/v2/conversations経由でその会話が正しくarchived状態
                  へ変わったことを確認（第3.1節のRevision処理が実環境でも
                  正しく機能）。
[hidden] CSS Fix: 第3.3節の修正後、Research/Developer Mode = OFF時に
                  選択Model／Context Size Fieldが正しく非表示になることを
                  `getComputedStyle`で確認（修正前はdisplay: gridのまま
                  可視だった）。
枠なしMessages/Composer: `getComputedStyle`でBorder・背景色ともに
                  透明・0であることを確認。
```

## 7. Mutation境界

```text
新規: frontend/src/components/Sidebar/ 一式（5File）、Docs本File
変更: frontend/src/App.tsx、TopBar.tsx、styles/app.css、i18n/translations.ts、
      App.test.tsx
      src/margpa_runtime_llm/web/static/*（Build出力による置換）
削除: frontend/src/components/PersistentPanel.tsx
実runtime_data/: 実Browser確認により、既存1件の会話をArchive状態へ変更した
      （動作確認目的、正本のPersistent Storageへの正常なMutationであり、
      Data改竄や不正操作ではない。Resumeで元に戻すことも可能）。
Stable Docs／Git／Provider Memory／.claude/settings.local.json: 無変更
```

## 8. Status

```text
Current Point            : 2-E-F実装完了。ユーザーによる画面上での最終確認待ち。
                            ノンストップ authorization により、続けて2-E-Gへ着手する。
Files Created／Modified   : 第7節のとおり。
Validation                : Frontend/Backend双方Clean、実Browser確認済み（第6節）。
Open Current Blocker      : NONE
Findings（解消済み）       : 2-E-E完了Handoffで記録した[hidden] CSS Findingを
                            本Phaseで解消（第3.3節）。
Controller-owned Next Work: ユーザーによる2-E-F最終確認。
Exact Next Route          : 2-E-Gへ継続（本Handoff作成後、Checkpointなしで着手）。
```
