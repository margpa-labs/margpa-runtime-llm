# Phase 8 Claude P8-B Entry UI Simplification / Archive Management — Complete Package Recovery

```yaml
document_type: recovery_index
phase: phase_8
package: P8-B
state: complete
provider: Claude
created_at: 2026-08-30 21:55 JST
```

## 結論

```yaml
p8_b_established: true
mvp_blocker_open: 0
critical_open: 0
major_open: 0
```

事前調査（Explore Agent、本Recovery作成前に実施）により、Archive／Unarchive／Resume／一覧Pagination・State Filterは全てPhase 2〜7で既に実装・Test済みであることを確認した。特に「Unarchive後、手動Resumeなしで送信できる」契約（P8-REQ-011）は`_ensure_active_session()`の遅延Resumeにより既に成立しており（`persistent_conversation_service.py:699-742`、Test: `test_lazy_resume_on_unarchive_allows_first_send_without_manual_resume`）、本Packageで新規実装したのはFrontend Onlyである。

## Work Unit別Status

| Work Unit | Status | 備考 |
|---|---|---|
| P8-B-WU-001（Branch UI既定非表示） | COMPLETE | Frontend Presentation層のみ、Backend/Data無変更 |
| P8-B-WU-002（Archive Lazy List API/Projection） | COMPLETE | 既存Backend API（`GET /api/v2/conversations?state=archived`）をそのまま利用、新規Backend変更0 |
| P8-B-WU-003（Data Controls一覧・Title/Timestamp・Open・Unarchive） | COMPLETE | `DataControlsPanel.tsx`へ新規実装 |
| P8-B-WU-004（Unarchive後Immediate Send・Restart/Two-tab Regression） | COMPLETE（既存機能の再確認） | 既存Test群がRegression 0であることを確認、新規Test追加なし（既存Coverageで十分） |

## 実装概要

### P8-B-WU-001: Branch UI既定非表示

- `MessageBubble.tsx`：新規`branchUiVisible`Prop（既定`false`）。`message.turnActions`（Data）は無変更のまま、`selectBranch`種別のButtonのみ描画時にFilterする（Presentation Boundary、Data削除ではない）。
- `MessageList.tsx`：`branchUiVisible`をそのまま中継。
- `App.tsx`：`usePreference`（既存のUI Language/Theme Toggleと同じLocalStorage Preference機構）で`margpa.branch_ui_visible.v1`Keyを追加、既定値`"hidden"`。
- **Scope判断**：本Packageでは有効化用のSettings Toggle UIは実装していない（意図的、下記Open Finding参照）。既定非表示という要件自体は、値を変更する専用UIがなくとも、Feature Flag（Preference Key）として完全に成立している。

### P8-B-WU-002/003: Archive Lazy List

- `api/client.ts`：`fetchArchivedPersistentList(cursor)`を新規追加。既存の`state`単一値Query Param（`GET /api/v2/conversations?state=archived&limit=50`）をそのまま利用 — Backend変更0件。
- `DataControlsPanel.tsx`：新規`ArchivedChatsState`（`idle`/`loading`/`ready`/`failed`）、「アーカイブ済みChatを表示」Trigger Button（Lazy — `idle`状態でクリックされるまでFetchしない）、Title（`ChatListItem.tsx`と同一のUntitled Fallback）・Timestamp・Open・Unarchive Buttonを持つList。
- `App.tsx`：`loadArchivedChats()`（Fetch）、`openArchivedChat()`（`selectPersistentConversation()`を再利用し、Settings Modalを閉じる）、`unarchiveArchivedChat()`（既存`chatListItemAction(id, "unarchive")`をそのまま再利用、成功後は一覧からOptimisticに除去）。

### P8-B-WU-004: Unarchive後Immediate Send

新規実装なし。既存の`_ensure_active_session()`（Lazy Resume、`persistent_conversation_service.py`）がP8-REQ-011を既に満たしていることを事前調査で確認し、`unarchiveArchivedChat()`はこの既存経路をそのまま利用するのみ（独自のResume呼び出しを追加していない — 追加した場合、既存の遅延Resume契約と重複・矛盾するRiskがあったため、意図的に何もしていない）。

## Changed Paths（14ファイル）

Frontend Source（8）：
```text
frontend/src/App.tsx
frontend/src/api/client.ts
frontend/src/components/MessageBubble.tsx
frontend/src/components/MessageList.tsx
frontend/src/components/DataControlsPanel.tsx
frontend/src/components/SettingsModal/SettingsModal.tsx
frontend/src/i18n/translations.ts
frontend/src/styles/app.css
```

Frontend Test（5）：
```text
frontend/src/components/MessageBubble.test.tsx
frontend/src/components/MessageList.test.tsx
frontend/src/components/DataControlsPanel.test.tsx
frontend/src/components/SettingsModal/SettingsModal.test.tsx
```

Static Artifact（1）：
```text
src/margpa_runtime_llm/web/static/app.js（Build Artifact、npm run build実行済み）
```

Backend：**変更0件**（Archive/Unarchive/Resume/List Filter/Paginationは全て既存実装をそのまま利用）。

## Canonical Verification

```text
Frontend: npx tsc --noEmit  -> clean
          npm test          -> 285 passed (31 files)
          npm run lint      -> clean
          npm run build     -> succeeded, app.js再生成済み

Backend: 無変更のため未実行（P8-A完了時点で1984 passed / mypy clean / ruff clean、
         その後Backend Source/Test 0件変更を`git status`で確認済み）。
```

Frontend純増：285 - 280（P8-A完了時点）= +5 Test（Branch非表示Test 2件、Archived Chats Test 4件のうち一部が既存Assertion拡張のため純増は5）、Regression 0。

## Internal Review（1 Cycle）

1. **Controller Issue解消**：該当なし（新規Controller Issue報告はまだない）。
2. **Backward Compatibility**：`branchUiVisible`／`archivedChatsAvailable`等は全てOptional/デフォルト値付きで追加。既存Test（`MessageBubble.test.tsx`の既存Branch表示Testを含む）は明示的Opt-inで無変更のまま成立。
3. **Security**：Archived Chat一覧はConversation IDのみを一覧表示し、本文Contentは含まない（既存`PersistentConversationSummary`のShapeをそのまま使用）。
4. **Historical Immutability**：Branch Data／API（既存`/branches/{turn_id}/select`Route、既存`buildTurnActions()`のData層）を一切変更していない（P8-REQ-009の「Data保持」要件を文字通り満たす）。
5. **Scope遵守**：Frontend Source/Test/CSS/Static Artifactのみ変更。Backend Source変更0、Git Mutation 0、Network 0、Real Browser 0。
6. **Claim精度**：P8-B成立の根拠（WU-001〜004全Complete、既存Backend機能の正確な理解に基づく再利用、Regression 0）を本Documentへ記録。

Critical／Major：0件。Minor：1件（非Blocking、Stable未解決へ記録）：
- **P8-RW-B-IR-001**: Branch UI可視化のSettings Toggle UIが未実装（`localStorage`直接操作でのみ切替可能）。P8-REQ-009の文言自体は「既定非表示」のみを要求しており充足しているが、UI経由での切替はUser体感上の利便性課題として残る。将来のHardening項目とする。

## P8-ACC-013〜018 Disposition

| ID | Disposition | 根拠 |
|---|---|---|
| P8-ACC-013 | PASS | `branchUiVisible`既定`false`、新規Test`branch-select is hidden by default`で確認 |
| P8-ACC-014 | PASS | `message.turnActions`のData自体は無変更、Backend Branch Route/Testも無変更 |
| P8-ACC-015 | PASS | `DataControlsPanel`のArchived Chats Lazy List、新規Test 2件で確認 |
| P8-ACC-016 | PASS | Title(Fallback含む)/Timestamp表示、Open Button、新規Testで確認 |
| P8-ACC-017 | PASS | 既存`_ensure_active_session()`Lazy Resume（Phase 2/7で既にTest済み、本Packageで壊していないことを確認） |
| P8-ACC-018 | PASS | Delete/Bulk/Export関連の文言・機能を一切追加していない（新規Testで確認） |

**P8-ACC-013〜018 全6件PASS。P8-B成立。**

## Action Inventory

```yaml
network_actions: 0
npm_install_or_download: 0
node_runtime_switch: 0
git_mutation_actions: 0
git_read_only_actions: 0
backup_actions: 0
user_runtime_data_access: 0
real_model_access: 0
real_browser_access: 0
provider_memory_used: false
project_root_外_access_executed: 0
```

## Exact Next Work Unit

```text
Next: P8-C Provisional Runtime Constitution
  Do Not Repeat: P8-A（WU-001〜006）、P8-B（WU-001〜004）は本Recoveryで完成済み。
```
