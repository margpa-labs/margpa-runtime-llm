# Claude Phase 2-E-I I-6：実装完了（Resume表示不具合のBackend根本修正含む）

```yaml
document_id: claude_phase_2_e_i_i6_implementation_20260819002250
status: evidence
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／将来の復旧Task
role: design_governor
created_at: 2026-08-19 00:22:50 JST
language: ja
purpose: |
  [claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md]
  （I-6要件Doc）に基づく実装の完了記録。ユーザー指示「うん。いいよ。
  よろしく。」により実装着手。#5（「再開」表示不具合）については、
  実装着手後の原因調査により、要件Docの想定（Frontend表示制御のみ）
  より深い、Backend側のData Model欠落であることが判明したため、
  ユーザーへ方針確認（AskUserQuestion）を行った上で、Backend拡張を
  含む対応を実施した。
created: Claude Code
```

## 1. 実装内容

### 1.1 #2：Panel展開中のHover Tooltip欠落（修正）

`ContextUsageGauge.tsx`は、Panel展開中はTooltip自体をJS側で非表示にしていた（`{!panelOpen && ...}`）。原因は、TooltipとPanelが同一のCSS絶対位置（`bottom: calc(100% + 6px); right: 0;`）を共有しており、同時表示すると重なってしまうため。

対応として、両者を`.context-usage-popouts`という新設Wrapper（`position: absolute`＋`flex-direction: column`）の中へ移し、Tooltipは常時DOMに存在させ、CSSの`:hover`のみで表示制御する、SidebarToggleButtonと同じ既存Patternへ揃えた。これによりPanel展開中もHover Tooltipが正しく表示され、かつPanelの上に自然に積み重なる（重複なし）。

### 1.2 #3：Panel外Clickで閉じない（修正）

`ContextUsageGauge`のWrapper Elementへ`ref`を付与し、`useEffect`＋`document.addEventListener("mousedown", ...)`によるOutside-click Close処理を追加した。設計Docは「SettingsModalのBackdrop Click Pattern」への追随を示唆していたが、実装時に、ContextUsageGaugeは全面Backdropを持たない小さな浮動Popoverであり、SettingsModalのBackdrop Patternはそぐわないと判断した。代わりに、同種の小規模Popoverである`ChatListItem.tsx`のOptions Menu（同じくOutside-click Close）が既に採用している`mousedown`＋`ref.contains()`判定のPatternへ揃えた。

### 1.3 新規Toggle：「コンテキスト表示」ON/OFF（追加）

`SettingsPanel.tsx`の基本設定末尾に、新規Switch「コンテキスト表示」（既定OFF）を追加した。`SettingsFormState.showContextUsage`として保持し、`Composer.tsx`は`showContextUsage`が真の時のみ`<ContextUsageGauge>`をRenderする（OFFの場合はGauge自体が完全に非表示になる。既存の「LLMへContext使用率を伝える」Toggle＝Prompt Injection制御とは独立）。

### 1.4 #5：「再開」表示不具合（Backend拡張を含む修正）

#### 1.4.1 原因調査

要件Docは、本件をSidebar/ChatListItemの表示制御のみの問題と想定していた。実装着手前に原因を調査した結果、次の事実が判明した。

- Backend側`resume_conversation`の実際のGuard条件は「会話がACTIVE状態、かつ、その会話に現在ACTIVEなSessionが1つも無い」こと（`persistent_conversation_service.py`）。
- しかしFrontendへ渡るList Summary（`PersistentConversationSummaryResponse`）には、会話単位の`state`（active/archived/deleted）のみが含まれ、Session単位の状態は一切含まれていなかった。
- 既存Code（`item.state === "active"`）は、ほぼ全ての非アーカイブ会話で真になるため、実質「常に表示」になっていた。

Frontend側のみの回避案（「選択中の会話ではResumeを隠す」）も検討したが、実際のMessage送信Flow（`sendPersistentMessage`）を追った結果、選択＝自動的にSessionを開く動作にはなっておらず、この案は「再開が必要な、選択中の休眠中の会話」からResume自体を消してしまい、再開不能になる回帰を生むと判断し、採用しなかった。

この調査結果をユーザーへ報告し、Backend拡張を伴う正しい修正への進行可否を確認した（AskUserQuestion）。ユーザー回答：「Backend拡張して正しく直す」。

#### 1.4.2 Backend拡張の内容

Sessionは別Tableではなく、`conversations`Tableの`snapshot_json`列（既存Column）内にJSONとして保持されていることを確認した。新規Tableや`ALTER TABLE`によるMigrationを伴わず、一覧取得Query（`SQLiteConversationStore.list()`）へ、SQLite JSON1拡張（`json_each`／`json_extract`、Python標準の`sqlite3`Moduleで利用可能であることを実機確認済み）による`EXISTS`副問い合わせを追加するだけで、既存Schema（`sqlite-3`）のまま実現できた。

```text
ConversationSummary（Domain）      : has_active_session: bool フィールドを追加
SQLiteConversationStore.list()     : SELECT文へ
                                      EXISTS(SELECT 1 FROM json_each(snapshot_json,
                                      '$.conversation.sessions') WHERE
                                      json_extract(value,'$.state')='active') を追加
PersistentConversationSummaryResponse（Web Contract）
                                    : has_active_session: bool を追加
project_persistent_page()          : 新Fieldを転写
Frontend PersistentConversationSummary（型）
                                    : has_active_session: boolean を追加
ChatListItem.tsx                   : Resume表示条件を
                                      state === "active" から
                                      state === "active" && !has_active_session へ変更
```

## 2. Validation

```text
Backend  : pytest 694件 Pass（3 deselected、既存と同数）、ruff clean、
           mypy clean（変更3File個別実行）
Frontend : Vitest 75件 Pass（74→75、ChatListItem・ContextUsageGauge
           へ新規Test追加）、eslint clean、tsc --noEmit clean、
           vite build成功
```

追加したTestの要点：

- `ContextUsageGauge.test.tsx`：Panel展開中もTooltipがDOM上に存在すること、Outside-clickでPanelが閉じること。
- `ChatListItem.test.tsx`：`has_active_session: true`のACTIVE会話にはResumeが出ないこと（既存の「ACTIVE会話にはResumeが出る」Testは`has_active_session: false`を明示する形へ調整）。
- `test_persistent_conversation_service.py`：`create_conversation`直後（Session Active）→`close_session`後→`resume_conversation`後の3時点で`list_conversations()`の`has_active_session`を確認。
- `test_persistent_web_app.py`：実HTTP API（`/api/v2/conversations`）経由で、Archive後・Resume後の一覧Responseの`has_active_session`を確認。

## 3. 実Browser確認（実Local Model、Mac Metal、Dark Theme含む）

1. `コンテキスト表示`Toggleを既定OFFから手動でONへ切替 → Gauge Iconが表示されることを確認。
2. Message送信後、Gauge ClickでPanel展開 → Hover Tooltip「コンテキスト状況を非表示」がPanelと重ならず表示されることを確認（#2）。
3. Panel外（Chat領域）をClick → Panelが閉じることを確認（#3、White／Dark両Theme）。
4. 新規会話作成直後（Session Active中）にChat Optionsを開き、「再開」が表示されないことを確認。
5. Archiveを実行 → 「アーカイブ解除」のみ表示（想定通り、変更なし）。
6. Unarchiveを実行（Sessionは閉じたまま）→ Chat Optionsに「再開」が表示されることを確認。
7. 「再開」をClick → 直後にChat Optionsを再度開くと「再開」が消えていることを確認。

## 4. Scopeとして対応しなかった項目

- **#1**（会話切替でGaugeが「未取得」表示に初期化される）：要件Doc第2.1節の通り、保留のまま。新規Toggle（既定OFF）による緩和のみ。
- **#4**（Injection Toggle OFF状態での思考過程混入）：原因未特定のままScope外。継続してOpen Question扱い。

## 5. Status

```text
Current Point            : Phase 2-E-I I-6（#2・#3・新規Toggle・#5）が
                            完了。#5はFrontend表示制御ではなく、Backend
                            Data Model欠落が真因と判明し、Schema変更
                            なしでBackend拡張し修正した。
Files Created／Modified   : Backend 3File（domain/models.py、
                            sqlite_conversation_store.py、
                            persistent_contracts.py）、Frontend 6File
                            （ContextUsageGauge.tsx、app.css、
                            Composer.tsx、SettingsPanel.tsx、
                            translations.ts、App.tsx、
                            ChatListItem.tsx、types.ts）、Test 5File。
Validation                : Backend pytest 694件・ruff・mypy、Frontend
                            Vitest 75件・eslint・tsc・build、いずれも
                            Clean。実Browser確認完了（本Doc第3節）。
Open Current Blocker      : NONE
Controller-owned Next Work: #1・#4は、いずれも別Trigger待ち（第4節
                            参照）。次のCompaction前には、いつも通り
                            Phase Index・Recovery Indexの最新性を確認する。
Exact Next Route          : ユーザーの次の判断待ち。
```
