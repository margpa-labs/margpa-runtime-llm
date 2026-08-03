# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 18:24:16 JST`
- 更新日時: `2026-07-21 18:24:16 JST`
- Snapshot: `20260721182416`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721182038.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H Implementation               : Changes Requested
Phase 1-H Follow-up Handoff            : Ready／Waiting User Authorization
Phase 1-H Automated／Mac Metal Base    : Pass
Phase 1-F Lightning Native             : Deferred／Not Run
Phase 1-ex                              : Accepted Reservation／Not Started
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721182038.md](documentation_index_20260721182038.md)から継承する。

本SnapshotはPhase 1-H Reviewの4 Mandatory Findingを解消する実装担当Follow-up Handoffを追加する。

Phase 1-G Accepted、Phase 1-H正本要件、Phase 1-ex予約、EASA／DLAGSA／OCILNS予約、公開名義、Append-only規則は継続する。

## 3. Added Document

| 状態 | 文書 | 役割 |
|---|---|---|
| waiting_user_authorization | [Phase 1-H Review Follow-up Handoff](handoffs/implementer_handoff_phase_1h_review_follow_up_20260721182416.md) | 4 Findingの限定修正指示 |

## 4. Follow-up Scope

1. Summary成功SSEからOriginal全文と重複Summary全文を除く。
2. 非本文Transformation Metadataへ整理する。
3. 15秒IntervalのSSE Comment Keepaliveを追加する。
4. KeepaliveのDisconnect／Cancel／Cleanup Testを追加する。
5. Summary Risk Noticeへ情報欠落／変形可能性を日英で追加する。
6. Runtime Known ErrorをUI Language切替後に再描画する。

Config Schema、Summary Prompt、Model Adapter、CLI、Dependencyは変更しない。

## 5. Fixed Follow-up Values

```text
Keepalive Interval : 15.0 seconds
Keepalive Format   : : keepalive\n\n
Summary Success    : Presented Summary only
Summary Fallback   : Presented Original only
Client Metadata    : Non-content Transformation State
```

## 6. Next Gate

```text
User authorizes Follow-up
  → Implementer Correction
  → Implementer Status
  → Designer Re-review＋New Index
  → User Mac Acceptance
  → Batch Lightning Upload／Validation
```

## 7. Deferred State

- Follow-up Source修正は未着手。
- Phase 1-Hは未Accepted。
- User Mac Acceptanceは未実施。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。

## 8. Authorization Boundary

本IndexとHandoffは修正範囲を定義する。Follow-up実装、Lightning操作、Upload、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 9. Append-Only

既存Status／Review／Indexを変更せず、新TimestampのFollow-up HandoffとIndexを追加した。新しいTimestampの本Indexを最新とする。
