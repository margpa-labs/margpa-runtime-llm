# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 16:42:48 JST`
- 更新日時: `2026-07-21 16:42:48 JST`
- Snapshot: `20260721164248`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721162242.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G SSE Cross-thread Follow-up    : Resolved
Phase 1-G Shutdown Cancel               : Changes Requested／One Mandatory Follow-up
Phase 1-G Final Acceptance              : Pending
Phase 1-H                               : Waiting Phase 1-G Acceptance
Phase 1-ex                              : Accepted Reservation／Not Started
Phase 10 Original R&D Systems           : EASA／DLAGSA／OCILNS
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721162242.md](documentation_index_20260721162242.md)から継承する。

本SnapshotはPhase 1-G Cross-thread Cancel Follow-upの設計Review、Shutdown Cancel追加Finding、実装担当Handoffを追加する。

EASA／DLAGSA／OCILNSの正式名称、公開範囲、Phase 10統合予約、個別ON／OFF要件は直前Indexから継続する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| changes_requested | [Phase 1-G Cross-thread Cancel Follow-up Review](handoffs/designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md) | SSE解消確認、Shutdown Finding、最終受入判定 |
| waiting_user_authorization | [Phase 1-G Shutdown Cancel Follow-up Handoff](handoffs/implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md) | 実装担当の限定修正範囲と受入条件 |

## 4. Review Result

### Resolved

- SSE Consumer Close時のEvent Loop ThreadからNative Generatorへの`force_cancel()`を除去した。
- Producer Thread上のCancel／Closeへ統一した。
- Cleanup TimeoutはThread-unsafe Escalationを行わず明示Failureとする。
- Thread-affine／Backpressure／Timeout Regressionが合格した。

### Remaining Mandatory Finding

```text
Path   : ConversationGenerationService.shutdown()
Trigger: Active Generation + Shutdown Timeout
Result : Cross-thread session.force_cancel()
Error  : ValueError: generator already executing
Impact : Model Close Callback未到達／Shutdown Failure無記録抑制
```

## 5. Independent Verification

```text
Static Format／Lint／Type／Compile : Pass
Default Regression                    : 213 passed、3 deselected
Conversation／Web Targeted            : 30 passed
uv Lock                               : Pass／122 packages
Setup Shell Syntax                    : Pass
Implementer Native Model Smoke        : 2 passed、1 skipped
Reviewer Native Model Smoke           : 2 failed、1 skipped／2 runs
Reviewer Native Failure               : Failed to create llama_context
```

Native FailureはModel Context作成時であり、Phase 1-G Web差分が実行される前に発生した。原因は未確定であり、Shutdown Follow-up後Reviewで再実行する。

## 6. Next Gate

```text
ユーザーによる追加Follow-up開始許可
  ↓
実装担当 Phase 1-G Shutdown Cancel Follow-up
  ↓
設計者役 Phase 1-G Final Review
  ↓
Phase 1-G Accepted判定
  ↓
Phase 1-H Summary Mode
```

## 7. Deferred State

- Phase 1-Hは未着手。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。
- Phase 10 Original R&D統合は将来予約のまま。

## 8. Authorization Boundary

本IndexはReview結果と次Gateを記録する。Source／Tests修正、Lightning操作、Upload、Backup、Phase 1-ex、Git、GitHub公開を許可しない。

## 9. Append-Only

既存Review、Handoff、Indexを変更せず、新TimestampのReview、Handoff、Indexを追加した。
