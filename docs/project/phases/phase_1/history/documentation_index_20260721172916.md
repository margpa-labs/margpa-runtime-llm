# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 17:29:16 JST`
- 更新日時: `2026-07-21 17:29:16 JST`
- Snapshot: `20260721172916`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721164248.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G Minimal Web Surface           : Accepted
Phase 1-G Cross-thread Cancel           : Resolved
Phase 1-G Shutdown Cancel               : Resolved
Phase 1-H Summary Mode                  : Ready for Requirements／Design
Phase 1-ex                              : Accepted Reservation／Not Started
Phase 10 Original R&D Systems           : EASA／DLAGSA／OCILNS
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721164248.md](documentation_index_20260721164248.md)から継承する。

本SnapshotはPhase 1-G Shutdown Cancel Follow-upのAccepted Reviewを追加し、Phase 1-G全体をAcceptedへ更新する。

EASA／DLAGSA／OCILNSの正式名称、公開範囲、Phase 10統合予約、個別ON／OFF要件は継続する。

## 3. Added Document

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [Phase 1-G Shutdown Cancel Follow-up Review](handoffs/designer_review_phase_1g_shutdown_cancel_follow_up_20260721172916.md) | Shutdown Finding解消とPhase 1-G最終受入 |

## 4. Phase 1-G Final Result

### Accepted Areas

- FastAPI／Vanilla UI／SSEのDelivery Adapter分離
- Browser-owned Ephemeral Conversation
- Response Language／Max New Tokens／Thinking Visibility
- Streaming／Stop／New Chat／Post-cancel Generation
- Bounded Queue／Backpressure Cleanup
- Producer Thread上のNative Cancel／Close
- Active Generation Shutdown／Restart
- Token Exhaustion WarningとCanonical History分離
- Preview Basic Authentication／Non-loopback Fail Closed
- Safe Error／Shutdown Failure Visibility
- Model Load once／Close once

## 5. Verification

```text
Static Format／Lint／Type／Compile : Pass
Default Regression                    : 215 passed、3 deselected
Conversation／Web Targeted            : 32 passed
uv Lock                               : Pass／122 packages
Setup Shell Syntax                    : Pass
Implementer Native Model Smoke        : 2 passed、1 skipped
Implementer Manual Native Gate        : Shutdown／Restart／Generation Pass
Reviewer Native Model Smoke           : Environment Failure／2 failed、1 skipped
```

Reviewer Native FailureはPhase 1-G Source実行前の`llama_context` creationである。Phase 1-G Source Findingとせず、Phase 1全体の最終User Gateで再実行する。

## 6. Non-blocking Observation

Public Session Surfaceに未使用の`force_cancel()`定義が残る。Current Source Callerは0件であり、現行LifecycleはCooperative Cancelだけを使う。将来の並行実行拡張前に削除／非公開化またはThread-safe Contract化する。

## 7. Next Gate

```text
Phase 1-G Accepted
  ↓
Phase 1-H Summary Mode Requirements／Design
  ↓
ユーザー承認
  ↓
Phase 1-H Implementation
  ↓
Lightning Batch Upload／Native Validation
  ↓
User Manual／Phase 1 Final Gate
```

## 8. Deferred State

- Phase 1-H実装は未着手。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。
- Phase 10 Original R&D統合は将来予約のまま。

## 9. Authorization Boundary

本IndexはPhase 1-GのAccepted判定と次Gateを記録する。Phase 1-H実装、Lightning操作、Upload、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 10. Append-Only

既存Review／Indexを変更せず、新TimestampのAccepted ReviewとIndexを追加した。
