# Claude Phase 2-E-G Completion Handoff — Account→設定Modal化

```yaml
document_id: claude_phase_2_e_g_completion_handoff_20260816120251
status: implementation_complete
phase: phase_2
subphase: phase_2_e_g
from: Claude側設計統括者役
to: ユーザー（最終確認者）／Codexプロジェクト責任者兼設計統括者役
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-16 12:02:51 JST
language: ja
authorization: ユーザーからの明示的な全権委任
  （「2-E-EからGまで、Checkpointなしで一気に(Bypass実験その2として)進める」、2026-08-16朝）
related:
  - claude_phase_2_e_f_completion_handoff_ja_20260816115426
  - claude_phase_2_e_e_to_h_react_migration_design_ja_20260816102654（承認済み設計、第2節）
```

## 1. Mission

承認済み設計の2-E-G：Sidebar最下部にAccount Entry、Click時に画面中央のModal（×閉じ）を開き、中に既存「設定」＋（仮称）「アドバンスモード」→ Runtime設定制御を格納する。Phase 10以降のCategory追加を妨げない拡張可能な構造にする。

これにより、ユーザーが2026-08-16朝に述べた「もう画面は基本、入出力とメッセージ送信欄だけにしたい」という最終形が、2-E-E〜Gの3段階を経て実現する。

本Handoffは**実装完了時点**の報告である。最終的な「2-E-G完了」判定はユーザー自身が画面を見て行う契約は変わらない。

## 2. 実装内容

```text
frontend/src/components/Sidebar/AccountFooter.tsx（新規）
  Sidebar最下部の単一Button。現状は汎用的な「Account」Labelのみ表示する
  （実Auth／複数User機構が無いため）。将来のIdentity（名前・Avatar・
  切替）が入る場所として、あえて単独Componentに分離した。

frontend/src/components/SettingsModal/SettingsModal.tsx（新規）
  中央固定・Backdrop付きのModal。Header（Title＋×閉じ）、Body
  （左Nav＋右Content）の2段構成。
  - 左Nav：「設定」（既定選択）／「アドバンスモード」
    （configurationBootstrapEnabled が true の時だけ表示——true でない
    環境ではRuntime設定制御自体が何も返さないため、選んでも空になる
    項目をそもそも見せない）。
  - 右Content：選択中のCategoryだけを表示（他方はhidden属性で非表示）。
    既存のSettingsPanel／ConfigurationControlPanelをそのまま埋め込み、
    中身のRefactorは行っていない。
  - 閉じ方3種：×Button、Backdrop（Modal外側）Click、Escapeキー。
  - Modalを開くたび、必ず「設定」Categoryへ戻る
    （前回「アドバンスモード」を見ていても、次回Openは常に設定から）。

frontend/src/components/Sidebar/Sidebar.tsx（改修）
  ChatListの下にAccountFooterを追加。onOpenSettings PropをApp.tsxから
  受け取り、そのままAccountFooterへ橋渡しする。

frontend/src/App.tsx（改修）
  - settingsModalOpen State（既定false）を追加。
  - Main Content内に直接置いていた<ConfigurationControlPanel>・
    <SettingsPanel>を削除し、<SettingsModal>（Main Content外、
    Overlayとして）へ一本化。Main Contentは
    TopBar／MessageList／Composerのみになった。

frontend/src/styles/app.css（改修）
  .sidebar-account-footer、.settings-modal-backdrop、.settings-modal、
  .settings-modal-header、.settings-modal-nav、.settings-modal-content
  等、Modal専用Styleを新設。SettingsPanel／ConfigurationControlPanelの
  既存Card装飾（Border・背景）はModal内部では相殺し
  （.settings-modal-content内で margin/padding/border/background を
  リセット）、Modal自体のCardと二重にならないようにした。
```

## 3. 設計判断

### 3.1 左Nav＋右Content形式にした理由（単純な折りたたみ式にしなかった理由）

「設定を押したら…それを押したら、Runtime設定制御が表示される」という要件を満たす最短実装は、「アドバンスモード」を単純なAccordion（折りたたみ）として設定Panelの下に追加することだった。しかし、承認済み設計に明記されている「将来のPhase 10以降のCategory追加を妨げない拡張可能な構造」という要件を踏まえ、Claude／ChatGPT等でも一般的な「左Nav（Category一覧）＋右Content（選択中のCategoryの中身）」という、Category数が増えても素直に拡張できる構造を採用した。現状はCategoryが2つ（設定／アドバンスモード）しかなくNavが多少過剰に見えるが、Phase 10以降を見据えた先行投資と判断した。

### 3.2 Modalを開くたび「設定」Categoryへ強制的に戻す設計

一度「アドバンスモード」を見た後にModalを閉じて再度開いた時、前回の選択（アドバンスモード）を覚えておくべきか、常に「設定」へ戻すべきか、ユーザー要件には明記が無かった。「アドバンスモード」はResearch/Developer向けの一段深い設定であり、毎回の起動で意図せずそこに居続けるより、常に基本の「設定」から始まる方が事故が少ないと判断し、後者を採用した。

### 3.3 Sidebar Toggleと同様、SettingsModalの開閉状態も意図的に未Persist

2-E-F Completion Handoff第3.2節と同じ理由（要件に明記がない、Privacy Contractへの影響を避ける）により、Modalの開閉状態もLocalStorageへは保存していない。

## 4. Test更新・新規Test

```text
frontend/src/components/Sidebar/AccountFooter.test.tsx（新規、1件）
  - ClickでonOpenSettingsが呼ばれる

frontend/src/components/SettingsModal/SettingsModal.test.tsx（新規、9件）
  - Close時は何もRenderしない
  - 既定でBasic Settings Categoryが開き、Advanced Modeは非表示（hidden属性）
  - Advanced ModeへのCategory切替で、Runtime設定制御が表示されBasic
    Settingsが非表示になる
  - configurationBootstrapEnabled=falseの時、Advanced Mode Nav自体が
    出ない（Configuration Panelも一切Mountされない）
  - ×Buttonでのonclose
  - Backdrop（Modal外側）Clickでのonclose
  - Dialog内部Clickではoncloseが呼ばれない（誤閉じ防止）
  - EscapeキーでのOnclose
  - 再OpenのたびBasic Settingsへ戻る（前回Advanced Modeを見ていても）

frontend/src/App.test.tsx（新規1件）
  - Sidebar Account EntryからModalが開き、既定でBasic Settings
    （回答言語Label等）が見えること。×Closeで閉じること。
  - 既存の「configuration control loads once bootstrap enabled」Testを、
    Modal経由（Account Click→Advanced Mode Click）でConfiguration
    Panelへ到達する形へ更新（旧：Main Content直下を直接検証）。
```

## 5. Validation結果

```text
Frontend:
  npm run lint       : Clean（0 errors）
  npm run typecheck   : Clean（0 errors）
  npm test             : 61 passed（前回50件 + 新規11件）
  npm run build         : 成功（app.js 244.58kB / gzip 75.32kB、
                          app.css 13.74kB / gzip 3.60kB）

Backend（Frontend専用変更のため無影響を確認）:
  pytest -q           : 664 passed, 3 deselected（変化なし）
```

## 6. 実Browser確認（実LLM、実Backend）

実Server（通常Contract）を起動し確認した。

```text
Main Content       : Configuration Control・設定PanelがいずれもMain
                      Content上から消え、Top Strip・Messages・Composerの
                      みになったことを確認（要件「入出力とメッセージ
                      送信欄だけ」の実現）。
Account→Modal      : Sidebar最下部のAccount Buttonから、画面中央に
                      Backdrop付きModalが開き、既定で「設定」Category
                      （回答言語・最大生成Token数等の既存Field一式）が
                      表示されることを確認。
Advanced Mode      : 左Navの「Advanced Mode」選択で、右ContentがRuntime
                      configuration control（第3.3節までの[hidden] Fix
                      込みで、Research/Developer Mode=OFF時はField群が
                      正しく非表示）へ切り替わることを確認。
Close 3種          : ×Button、Escapeキー、両方でModalが閉じることを
                      確認（Ref経由のClickで正確に検証——見た目上の
                      座標Clickでは1280論理px vs 800pxScreenshotの
                      Scale差により誤クリックする場面があったため、
                      read_pageのRefで確実な要素を特定して検証した）。
```

## 7. Mutation境界

```text
新規: frontend/src/components/Sidebar/AccountFooter.tsx（＋Test）、
      frontend/src/components/SettingsModal/ 一式（＋Test）、Docs本File
変更: frontend/src/App.tsx、Sidebar.tsx、styles/app.css、App.test.tsx
      src/margpa_runtime_llm/web/static/*（Build出力による置換）
実runtime_data/: 実Browser確認は既存会話のView・Modal開閉操作のみで、
      Conversation Dataへの書き込みは発生していない。
Stable Docs／Git／Provider Memory／.claude/settings.local.json: 無変更
```

## 8. Status（2-E-E〜G 全体の区切りとして）

```text
Current Point            : 2-E-E・2-E-F・2-E-Gの3段階すべて実装完了。
                            ユーザーが2026-08-16朝に依頼した「Checkpointなし
                            で一気に」というNon-stop authorizationの対象範囲
                            を完了した。
Files Created／Modified   : 各段階のCompletion Handoff（2-E-E／2-E-F／
                            本File）第7節（または相当節）のとおり。
Validation                : 各段階でFrontend/Backend双方Clean、実Browser
                            確認済み（各段階のHandoff参照）。
Open Current Blocker      : NONE
未着手（次の候補）        : 2-E-H（余力枠、名前変更・削除の新規Backend実装）。
                            設計上は「余力があれば」の位置づけであり、
                            必須ではない。
Controller-owned Next Work: ユーザーによる2-E-E〜G一連の最終確認。
Exact Next Route          : ユーザー確認待ち。2-E-Hへ進めるかはユーザー
                            判断による（本Handoffでは着手しない）。
```
