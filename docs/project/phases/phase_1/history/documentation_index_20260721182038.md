# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 18:20:38 JST`
- 更新日時: `2026-07-21 18:20:38 JST`
- Snapshot: `20260721182038`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721174346.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H Implementation               : Changes Requested
Phase 1-H Automated Verification       : Pass
Phase 1-H Mac Metal Model Smoke        : Pass outside Sandbox
Phase 1-H Contract／Preview Boundary   : 4 Mandatory Findings
Phase 1-F Lightning Native             : Deferred／Not Run
Phase 1-ex                              : Accepted Reservation／Not Started
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721174346.md](documentation_index_20260721174346.md)から継承する。

本SnapshotはPhase 1-H実装報告と設計Review結果を追加し、Phase 1-Hを`changes_requested`へ更新する。

Phase 1-G Accepted、Phase 1-ex予約、EASA／DLAGSA／OCILNS予約、公開名義、Append-only規則は継続する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| reported | [Phase 1-H Implementer Status](handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md) | 実装・検証報告 |
| changes_requested | [Phase 1-H Designer Review](handoffs/designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md) | 独立検証と受入判定 |

## 4. Review Result

### Pass

- Summary OFF 1回／ON 2回の逐次Inference
- Summary Thinking disabled／max 1024
- Canonical FinalだけのSummary Prompt Boundary
- Fallback Matrix
- Cancel／Disconnect／Shutdown Thread Boundary
- Schema 3／Deployment Profile非変更
- UI Language／Response Language分離
- Local Storage境界
- Static／Type／Unit／Integration／Mac Metal Smoke

### Changes Required

1. Summary成功SSEからOriginal全文を除く。
2. Hidden／Buffered Generation中のSSE Keepaliveを追加する。
3. Summary Noteへ情報欠落／変形可能性を日英で追加する。
4. Runtime API失敗表示をUI Language切替後に再描画する。

## 5. Verification Evidence

```text
Format／Lint／Type／Compile            : Pass
Node Syntax                            : Pass
Default Test                           : 242 passed、3 deselected
Conversation／Summary／Web Targeted    : 47 passed
uv Lock                                : Pass／122 packages
Setup Shell Syntax                     : Pass
Mac Metal Model Smoke outside Sandbox  : 2 passed、1 skipped
```

自動Testは合格しているが、Successful Summary ResponseにOriginalが存在しないことをCurrent TestがAssertしていない。Test PassだけではAcceptance条件を満たさない。

## 6. Required Follow-up

```text
Designer Follow-up Handoff
  → User Authorization
  → Implementer Correction
  → Implementer Status
  → Designer Re-review＋Index
```

Lightning Full UploadはFollow-up Accepted後までDeferredとする。

## 7. Deferred State

- Phase 1-Hは未Accepted。
- User Mac Acceptanceは未実施。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。

## 8. Authorization Boundary

本IndexはReview結果を記録する。Phase 1-H Follow-up実装、Lightning操作、Upload、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 9. Append-Only

既存Status／Review／Indexを変更せず、新TimestampのReviewとIndexを追加した。新しいTimestampの本Indexを最新とする。
