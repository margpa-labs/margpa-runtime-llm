# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 18:41:40 JST`
- 更新日時: `2026-07-21 18:41:40 JST`
- Snapshot: `20260721184140`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721182416.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
Phase 1-H Mandatory Findings           : 4／4 Resolved
Phase 1-H Default Regression           : 246 passed、3 deselected
Phase 1-H Mac Metal Model Smoke        : 2 passed、1 skipped
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Phase 1-ex                              : Accepted Reservation／Not Started
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721182416.md](documentation_index_20260721182416.md)から継承する。

本SnapshotはPhase 1-H Review Follow-up実装報告とAccepted Reviewを追加し、Phase 1-H全体をAcceptedへ更新する。

Phase 1-G Accepted、Phase 1-ex予約、EASA／DLAGSA／OCILNS予約、公開名義、Append-only規則は継続する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| reported | [Phase 1-H Follow-up Status](handoffs/implementer_status_phase_1h_review_follow_up_20260721183457.md) | 4 Finding修正と検証報告 |
| accepted | [Phase 1-H Follow-up Review](handoffs/designer_review_phase_1h_review_follow_up_20260721184140.md) | Follow-up受入とPhase 1-H最終判定 |

## 4. Resolved Findings

1. Summary成功SSEからOriginal全文と重複Summary全文を除去した。
2. Non-content Transformation Metadataへ整理した。
3. 15秒SSE Comment Keepaliveを追加した。
4. KeepaliveのDisconnect／Cancel／Cleanup Regressionを追加した。
5. Summary Risk Noticeへ情報欠落／変形可能性を日英で追加した。
6. Runtime Known ErrorをUI Language切替後に再描画できるようにした。

前回4 Findingのうち、1と2は同一Data Minimization Findingの修正項目、3と4はKeepalive Findingの修正項目である。Mandatory Finding単位では4／4解消である。

## 5. Verification Evidence

```text
Format／Lint／Type／Compile            : Pass
Node Syntax                            : Pass
Default Test                           : 246 passed、3 deselected
Conversation／Summary／Web Targeted    : 51 passed
uv Lock                                : Pass／122 packages
Setup Shell Syntax                     : Pass
Mac Metal Model Smoke                  : 2 passed、1 skipped
Successful Summary Original Presence  : False
```

## 6. Current Accepted Phase 1-H Contract

```text
Summary Mode        : off／post_generation
Default             : off
Normal max          : Request／Default 2048
Summary max         : 1024
Summary Thinking    : disabled
Execution           : Same Main Model Sequential
Success Presentation: Summary only
Fallback Presentation: Original only＋Warning
Cancel              : Cancelled／No Fallback
Keepalive           : 15-second SSE Comment
UI Language         : ja／en Browser-only
Response Language   : ja／en／auto Independent
```

## 7. Non-blocking Observations

- Summary Stage Broad ExceptionのSafe Operator Logは将来Observabilityで扱う。
- Legacy `force_cancel()`はRuntime Caller 0件のまま残る。
- Lightning Native／Reverse ProxyでのKeepaliveはBatch Gateで確認する。

## 8. Next Gate

```text
User Mac Acceptance
  → Batch Lightning Upload／Native／Web Validation
  → Cross-environment Final Review
  → User Manual Finalization
  → Phase 1 Completion Gate
```

## 9. Deferred State

- User Mac Acceptanceは未実施。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1全体の完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。

## 10. Authorization Boundary

本IndexとReviewはPhase 1-HをAcceptedとする。Lightning操作、Upload、Model Transfer、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 11. Append-Only

既存Status／Review／Indexを変更せず、新TimestampのAccepted ReviewとIndexを追加した。新しいTimestampの本Indexを最新とする。
