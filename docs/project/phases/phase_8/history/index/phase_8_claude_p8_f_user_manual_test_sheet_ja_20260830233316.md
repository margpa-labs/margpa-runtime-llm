# Phase 8 Claude P8-F User Manual Test Sheet

```yaml
document_type: user_manual_test_sheet
phase: phase_8
package: P8-F
provider: Claude
created_at: 2026-08-30 23:33 JST
covers: P8-A, P8-B, P8-C, P8-D, P8-E
```

このSheetはUser（Human Reviewer）が実際に手を動かしてPhase 8 P8-A〜P8-Eの成立をManualで確認するための手順書である。全項目、実Model・実Network・実Browser（外部Site）を必要としない（既存`.venv`／既存Node Modules／既存Fixture Dataのみで完結する）。

## 起動

```bash
uv run margpa-web
```

- 既定で`http://127.0.0.1:8000`（Loopback限定）で起動する。
- 実Model（Qwen3-4B）のRegistry読込には数秒〜十数秒かかる。「Application startup complete」のLogが出るまで待つこと。
- Browserで`http://localhost:8000`を開く。

## 1. Manual URL Fetch／Evidence（P8-A）

1. Chat画面のComposer（メッセージ入力欄）付近、または Settings → Web Search Panel を開く。
2. 「URL Fetch (Manual)」欄にPublic URL（例：`https://example.org/`）を入力しFetchを押す。
   - **期待**：Untrusted Labelとともに取得Contentが表示される。
   - Real Network User Authorityが必要（本Task内ではFixture/Mock検証のみ）。
3. Web Search機能をOFFのまま同じ操作を行う。
   - **期待**：「Web search is OFF...」の案内が出て、入力欄・Fetch Buttonが無効化される。
4. 危険Port（例：`https://example.org:6379/`）を入力しFetchを試みる。
   - **期待**：Rejectedとして表示され、実際のFetchは発生しない。

## 2. Branch UI非表示／Archive Management（P8-B）

1. Settings → Data Controls を開く。
2. 「アーカイブ済みChatを表示」ボタン（初期状態ではList未取得）をクリックする。
   - **期待**：Archive済みChatのTitle／Timestampが一覧表示される（未取得の間はNetwork Callが発生しない＝Lazy）。
3. 一覧の「開く」を押す。
   - **期待**：該当Chatが開き、Settings Modalが閉じる。
4. 一覧の「Archive解除」を押す。
   - **期待**：一覧からOptimisticに消え、その直後にそのChatへ手動Resumeなしでメッセージ送信できる。
5. Chat画面でBranch選択UIが既定で表示されていないことを確認する（`localStorage`の`margpa.branch_ui_visible.v1`を`"shown"`に手動設定すると再表示できる — 専用切替UIは未実装、既知の残課題）。

## 3. Provisional Runtime Constitution（P8-C）

1. Settings → アドバンスモード を開く。
2. 「Provisional Runtime Constitution」セクションまでScrollする。
   - **期待**：Revision・Digest（短縮表示）・Rule数、およびchat／agent／tool別のMode（**必ずOFF**）とRule件数が表示される。
3. `constitution/manifest.json`を手動で1文字改変してから再読み込みする（Optional、破壊的操作なのでコピーを取ってから行うこと）。
   - **期待**：Panelが静かに非表示になる（Errorダイアログ等は出ない、404へ収束）。改変後は必ず元に戻すこと。

## 4. Chat／Dev Agent切替とDemo Run（P8-D／P8-E／P8-F）

1. 同じくアドバンスモード内、「Dev Agent（Foundation）」セクションで「Dev Agent」を選択する。
   - **期待**：List Files／Read File／Write Note の3 Toolが一覧表示され、Write Noteのみ「承認必須 (external_write)」の表示がある。
2. 「Demo Runを開始」を押す。
   - **期待**：Run状態が`running`になり、list／read／writeの3 Stepが`pending`で表示される。
3. 「次のStepへ進める」を2回押す。
   - **期待**：1回目でlistが`succeeded`、2回目でreadが`succeeded`になる。
4. 「次のStepへ進める」をもう1回押す。
   - **期待**：writeが`awaiting_approval`になり、「承認待ちStep：'write'」というBoxと「承認」「却下」Buttonが現れる（**これがGate**）。
5. 「承認」を押す。
   - **期待**：Run状態が`running`に戻り、writeが`pending`（承認済み）に戻る。
6. 「次のStepへ進める」をもう1回押す。
   - **期待**：writeが`succeeded`、Run状態が`completed`、完了理由が`completed — All Plan Steps completed successfully.`と表示される。
7. 「新しいDemo Runを開始」を押し、新しいRunで「次のStepへ進める」を1回だけ押した後、「中止」を押す。
   - **期待**：Run状態が`cancelled`になり、全Stepが`cancelled`、完了理由が`cancelled — Run was cancelled.`になる（**これがStop**）。
8. Chatに切り替え、Tool一覧・Demo Run欄が消え、通常Chat機能に何の変化もないことを確認する。

## 5. 完全削除／一括操作（P8-REQ-012／P8-REQ-018確認）

- Data ControlsのUIに「完全削除」「一括Delete」「Export」に類するButtonが**存在しない**ことを目視確認する（実装済みという虚偽表示が無いことの確認）。

## 期待される制約（Regressionではない、意図された挙動）

```text
- Dev Agent Demo Runは常にFixed Fixture Plan（list_files→read_file→write_note）のみ。
  任意のTool/Planを自由入力できるUIはまだ無い。
- MCP Client（Real）は接続できない（Portのみ存在、意図的に非配線）。
- Constitution ModeはOFF固定（Observe/Enforceへ昇格するUIはまだ無い）。
- Guardrail（GD）とDev Agent Runの相関はまだ無い（Constitution相関のみ）。
```
