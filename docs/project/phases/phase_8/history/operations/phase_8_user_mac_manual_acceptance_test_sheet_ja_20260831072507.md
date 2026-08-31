# Phase 8 User Mac Manual Acceptance Test Sheet

```yaml
document_id: phase_8_user_mac_manual_acceptance_test_sheet_20260831072507
document_type: user_manual_acceptance_test_sheet
document_state: current_candidate
language: ja
created_at: 2026-08-31 07:25:07 JST
review_owner: User
controller: Codex_project_controller
acceptance_target: P8-ACC-040
phase_8_closure_before_completion: prohibited
```

## 1. 目的／停止線

Userが実際のMac／Browser画面で、Phase 8の次の中心経路を確認する。

```text
Manual URL
Archive管理
Branch UI既定非表示
Constitution 3-Mode Preview
Chat／Dev Agent切替
Tool Gate／Completion Gate／Stop
既存Chatの最低限Regression
```

Qwenの回答品質、General Web Search、Real MCP、正式なDevelopment Agent Level 1、Phase 6 Semantic／Judge／Guard残件は
今回の合否対象にしない。

## 2. 起動Command

Project Rootで実行する。

```bash
./.venv/bin/python -m margpa_runtime_llm.entrypoints.web.main \
  --host 127.0.0.1 \
  --port 8000 \
  --conversation-persistence \
  --conversation-persistence-migrate \
  --conversation-runtime-data-root "$PWD/runtime_data" \
  --conversation-scope-id "mac-local-primary" \
  --configuration-control \
  --phase-3-governance-definitions \
  --phase-3-governance-definitions-root "$PWD/definitions" \
  --phase-4-runtime-governance \
  --phase-4-runtime-governance-definitions-root "$PWD/definitions" \
  --phase-5-guardrail-governance \
  --phase-6-runtime-model-control \
  --phase-6-feature-modes \
  --phase-7-local-corpus \
  --local-corpus-runtime-data-root "$PWD/runtime_data" \
  --local-corpus-scope-id "mac-local-primary" \
  --phase-7-web-search \
  --phase-7-web-search-governance-mode off \
  --phase-7-data-controls \
  --data-controls-runtime-data-root "$PWD/runtime_data" \
  --data-controls-scope-id "mac-local-primary"
```

起動後、`http://127.0.0.1:8000`を開く。停止時は起動Terminalで`Ctrl+C`。

Phase 8のConstitution／Dev Agent Foundationは現在のComposition RootへLocal Componentとして組み込まれているため、
専用の`--phase-8-*` Flagは存在しない。

`--conversation-persistence-migrate`は、既存Conversation Storeが旧Schemaの場合だけ、Checkpoint／Digest／Rollback付きの
明示Migrationを許可する。Migration完了後の新Schema Storeに対して指定したままでも、不要な再Migrationは行わない。

## 3. Test 1 — 初期状態／既存Chat

1. 既存Chatまたは新規Chatを開く。
2. 短い質問を1回送信する。
3. 設定を開く。

期待結果：

- 通常Chatが従来どおり送信／表示できる。
- Web検索Modeは既定でOFF。
- Message下に「このBranchを選択」が既定表示されない。
- アーカイブしていない既存Chatは手動「再開」なしで送信できる。

判定：`確認できた／不具合再現／未実施`

## 4. Test 2 — Manual URL Preview／Chat Evidence

### 4.1 OFF境界

1. Web検索ModeをOFFにする。
2. ComposerとSettings内のWeb Search Panelを確認する。

期待結果：

- ComposerのManual URL入力欄が表示されない。
- Settings側のSearch／URL Fetch入力とButtonが無効。
- OFFのままURL Fetchは開始されない。

### 4.2 Public URL Preview

1. Web検索ModeをManualへ切り替える。
2. Settings内の`URL Fetch (Manual)`へ`https://example.org/`を入力してFetchする。

期待結果：

- Fetch成功時、Canonical URL、Source Authorityおよび取得Contentが表示される。
- 取得Contentへ`Untrusted External Content`相当のLabelが付く。
- Fetch成功を「信頼済み」と表示しない。
- Network環境により到達不能の場合は、Successへ偽装せずFailure理由を表示する。この場合は実Network項目だけ`NOT RUN／UNAVAILABLE`として報告する。

### 4.3 Main Model Evidence／Citation／Persistence

1. Settingsを閉じる。
2. Composerに現れたManual URL欄へ`https://example.org/`を入力する。
3. 質問欄へ次を入力して送信する。

```text
このURLから取得した内容だけを根拠に、ページの題名と概要を短く答えて。
```

期待結果：

- 当該TurnだけでURL Fetchが行われる。
- 回答またはSafe Failureの下に`Web Evidence`が表示される。
- Citationへ`Public Web`、Title、Canonical URL、Document Digest、Untrusted Labelが表示される。
- Redirectがあった場合だけ`Redirect元`も表示される。
- Reload後も同TurnのWeb Evidence／Citationが残る。
- 可能ならServer Restart後も同じTurnのEvidence／Citationが残る。

回答品質そのものは合否対象にせず、取得Evidenceと回答の相関、Citation Persistenceおよび虚偽Successがないことを確認する。

### 4.4 Rejected URL

Settings内のManual URL Fetchへ次を入力する。

```text
http://127.0.0.1:8000/
```

期待結果：

- Loopback URLとして拒否される。
- 取得ContentをSuccess表示しない。

危険Site、Login Site、攻撃用URLまたは実Credentialは使用しない。

判定：`確認できた／不具合再現／未実施`

## 5. Test 3 — Branch UI非表示／Archive管理

1. 使い捨て可能なChatを1件アーカイブする。
2. Settings → Data Controlsを開く。
3. `アーカイブ済みChatを表示`を押す。
4. 対象ChatのTitle／Timestampを確認する。
5. `開く`を押し、該当Chatが開くことを確認する。
6. 再度Data Controlsを開き、対象Chatを`アーカイブ解除`する。
7. 解除後のChatで、手動「再開」なしに短い質問を送信する。

期待結果：

- Archive一覧はButtonを押すまで読み込まれない。
- Title／Timestampが表示される。
- `開く`で対象Chatへ移動し、Settingsが閉じる。
- `アーカイブ解除`後、一覧から消える。
- 解除後すぐ送信できる。
- Chat履歴にBranch Dataがあっても「このBranchを選択」は既定非表示。
- Archive管理欄に「完全削除」「一括Delete」「Export」の虚偽Buttonがない。

判定：`確認できた／不具合再現／未実施`

## 6. Test 4 — Provisional Runtime Constitution

1. Settings → アドバンスモードを開く。
2. `Provisional Runtime Constitution`まで移動する。

### 6.1 Production状態

期待結果：

- Revision、Digest、Rule数が表示される。
- `chat／agent／tool`のProduction Modeは全てOFF。
- Previewを開いても`Actual Active Production Mode`はOFFのまま。
- Previewが実Runtime Modeではなく、外部Action、Tool AuthorityまたはModel Injectionを起こさない旨が表示される。

### 6.2 3-Mode比較

`chat／agent／tool`それぞれにOFF／OBSERVE／ENFORCEの比較があり、各Modeへ次の4行が表示されることを確認する。

```text
Decision
評価区分
Action許可範囲
違反時の表示
```

Current Manifestで期待する中心表示：

```text
OFF
  Decision: not_evaluated
  評価区分: 未評価
  Action許可範囲: Constitution由来のActionなし
  違反時の表示: 未評価のため提示なし

OBSERVE
  Decision: unsupported_action
  評価区分: 評価して記録のみ（Blockしない）
  Action許可範囲: Blockなし・Authority変更なし
  違反時の表示: 未対応（Typed Unsupported）

ENFORCE
  Decision: unsupported_action
  評価区分: 評価して対応済みActionのみ適用
  Action許可範囲: 対応済みActionのみ・Authority拡張なし
  違反時の表示: 未対応（Typed Unsupported）
```

Rule件数はCurrent Manifestで`chat=2／agent=3／tool=2`。未対応Ruleを`observed／enforced`と表示しないことが重要である。

判定：`確認できた／不具合再現／未実施`

## 7. Test 5 — Chat／Dev Agent、Gate／Completion／Stop

1. Settings → アドバンスモード → `Dev Agent（Foundation）`を開く。
2. 初期`Chat`から`Dev Agent`へ切り替える。

期待結果：

- `List Files／Read File／Write Note`が表示される。
- Write Noteだけが`承認必須（external_write）`。

### 7.1 Tool Gateから正常完了

1. `Demo Runを開始`。
2. `次のStepへ進める`を2回押す。
3. 3回目を押す。
4. Write StepのGateで`承認`する。
5. 再度`次のStepへ進める`を押す。
6. Run Completion Gateで`承認`する。

期待状態遷移：

```text
Run開始
  running
1回目
  list = succeeded
2回目
  read = succeeded
3回目
  write = awaiting_approval
Tool承認
  write = pending / approved
4回目
  write = succeeded
  Run = awaiting_completion_approval
Completion承認
  Run = completed
  Completion = completed
```

Tool Gateを飛ばしてWriteが実行されないこと、Completion Gateを飛ばしてCompletedへ進まないことを確認する。

### 7.2 Stop／Cancel

1. `新しいDemo Runを開始`。
2. 1 Stepだけ進める。
3. `中止`を押す。

期待結果：

- Runが`cancelled`へ収束する。
- 未完了Stepが勝手にSuccessへ変わらない。
- 中止後に遅れてCurrent Resultが追加されない。

### 7.3 Chatへ戻す

`Chat`へ戻し、Tool一覧／Demo Run UIが隠れることを確認する。通常Chatで短い質問を送信できれば最低限Regressionなしとする。

判定：`確認できた／不具合再現／未実施`

## 8. 今回の合否対象外／既知状態

次は今回のUser Manual FAILにしない。

```text
P8-ACC-038:
  GD相関はPARTIAL。Constitution／Approval相関は成立済み。

P8-CODEX-009:
  過去Manualとの差はCurrent Completion Gate手順で置換して確認する。

P8-CODEX-010:
  Network-restricted Test環境の非Hermetic Test Debt。実画面機能の単独Blockerではない。

P8-CODEX-011:
  Completion Gateは動作するがFrozen Envelopeのgate_reasons表示にcompletionが出ない非Blocking Gap。

Scope外:
  General Web Search、Automatic Search、Real MCP、正式Level 1、Dynamic Sub-Agent、
  正式Constitution Enforcement、Phase 6／9 Semantic Governance Debt。
```

## 9. User返却Template

各項目について、実際の表示文言とともに返す。

```text
1. 初期状態／既存Chat
   確認できた／不具合再現／未実施

2. Manual URL
   OFF境界:
   Public URL Preview:
   Chat Evidence／Citation:
   Reload／Restart Persistence:
   Rejected URL:
   実際の表示文言:

3. Branch／Archive
   Branch UI非表示:
   Lazy一覧:
   Title／Timestamp:
   開く:
   Archive解除後の送信:
   虚偽の完全削除／Export表示:

4. Constitution Preview
   Production Active OFF:
   3 Mode:
   Decision:
   Evaluation:
   Action Permission:
   Violation Presentation:
   実際の表示文言:

5. Dev Agent
   Chat／Dev Agent切替:
   Tool Gate:
   Completion Gate:
   Completed:
   Stop／Cancelled:
   Chat Regression:

総評:
```
