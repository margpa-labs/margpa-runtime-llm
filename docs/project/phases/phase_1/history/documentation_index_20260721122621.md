# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 12:26:21 JST`
- 更新日時: `2026-07-21 12:26:21 JST`
- Snapshot: `20260721122621`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721115330.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research／Mandatory
Project Internal Name                 : Nazuna Research Governance LLM
Phase 1-G Previous Findings            : Resolved／3 of 3
Phase 1-G New High Finding             : Cross-thread Native Generator Cancel
Phase 1-G Designer Review              : Changes Requested／One Local Follow-up
Phase 1-H Summary Mode                 : Waiting Phase 1-G Acceptance
Lightning Full Upload                  : Deferred
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721115330.md](documentation_index_20260721115330.md)から継承する。

本Snapshotは、Phase 1-G Review Follow-upの設計Review結果とCross-thread Cancel限定Handoffを追加する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current_review_changes_requested | [Phase 1-G Review Follow-up設計Review](handoffs/designer_review_phase_1g_review_follow_up_20260721122621.md) | 前回Finding解消確認と新規Cross-thread競合 |
| waiting_user_authorization | [実装担当向けCross-thread Cancel Follow-up](handoffs/implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md) | Phase 1-G残件1件の限定修正 |

## 4. Resolved Findings

- Queue Capacity超過時のProducer投入待ち解除
- Final Answer前Token Exhaustion Warningの画面保持
- Warning TextのCanonical History非追加
- Public Namingの`Nazuna Research`統一
- Browser `response_language=auto` Manual Evidence

## 5. Current Finding

```text
Severity : High
Area     : Disconnect／Cancellation Thread Boundary
Cause    : Event Loop Threadから実行中Native Generatorへclose()
Observed : ValueError: generator already executing
Impact   : Producer Await前にCleanupが例外離脱し得る
```

Web CleanupはCooperative Cancelを第一段とし、Native IteratorのCancel／CloseをProducer Thread上で行う必要がある。

## 6. Verification Result

```text
Static／Default Test       : Pass／211 passed、3 deselected
Web Targeted Test         : Pass／28 passed
Mac Native Model Smoke    : Pass／2 passed、1 skipped
uv Lock                   : Pass／122 packages
Public Naming Search      : Pass／0 match
Cross-thread Diagnostic   : Fail／ValueError再現
Final Decision            : Changes Requested
```

## 7. Immediate Next Gate

```text
UserがCross-thread Cancel Follow-upを許可
  → 実装担当がThread-affine CancelとRegression Test
  → 後継Implementer Status
  → 設計者役Phase 1-G Final Review＋新Index
  → Phase 1-G Accepted判定
  → Phase 1-H Summary Mode
```

## 8. Authorization Boundary

本Snapshotで許可された変更はReview、限定Handoff、IndexのAppend-only追加までである。

まだ行わない。

- Source／TestsのFollow-up修正
- Phase 1-H実装
- Lightning Full Upload／Model Transfer
- Phase 1完了宣言／Backup
- Phase 1-ex開始
- Git初期化／Commit／Push／GitHub公開

Follow-up実装は、ユーザーが実装担当Taskへ明示的に開始指示した後に行う。

## 9. Append-Only

既存文書を変更せず、新TimestampのReview、Handoff、Indexを追加した。
