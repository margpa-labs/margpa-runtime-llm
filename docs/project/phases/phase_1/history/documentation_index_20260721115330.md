# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 11:53:30 JST`
- 更新日時: `2026-07-21 11:53:30 JST`
- Snapshot: `20260721115330`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721112925.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Public Author／Research Name           : Nazuna Research／Mandatory
Project Internal Name                 : Nazuna Research Governance LLM
Public Repository Owner               : margpa-labs
Phase 1-G Repository Implementation    : Completed Candidate
Phase 1-G Designer Review              : Changes Requested
Phase 1-G Blocking Work                : 3系統／Follow-up Waiting User Authorization
Phase 1-H Summary Mode                 : Waiting Phase 1-G Acceptance
Lightning Full Upload                  : Deferred
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721112925.md](documentation_index_20260721112925.md)から継承する。

本Snapshotは、Phase 1-Gの設計Review結果と、実装担当向け限定Follow-upを追加する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current_review_changes_requested | [Phase 1-G Minimal Web Surface設計Review](handoffs/designer_review_phase_1g_minimal_web_surface_20260721115330.md) | 実装、Security、Streaming、UI、検証Evidenceの合否 |
| waiting_user_authorization | [実装担当向けPhase 1-G Review Follow-up](handoffs/implementer_handoff_phase_1g_review_follow_up_20260721115330.md) | Mandatory Finding 3系統の限定修正 |

## 4. Phase 1-G Review Result

```text
High Finding                 : 1
Medium Finding               : 2
Low Observation              : 2
Static／Default Gate          : Pass／209 passed、3 deselected
Web Targeted Test            : Pass／26 passed
Mac Native Model Smoke       : Pass／2 passed、1 skipped
Final Decision               : Changes Requested
```

Mandatory Follow-up：

1. Backpressure中のClient DisconnectでもProducerとGeneration Gateを確実に解放する。
2. Final Answer前Token Exhaustion WarningをBrowserの`completed`処理で上書きしない。
3. Source内の第一者表示名2箇所を`Nazuna Research`へ統一する。

## 5. Accepted Areas

- FastAPI／UvicornのDelivery Adapter局所化
- Browser-owned Ephemeral Multi-turn
- Request単位の3設定とTracked TOML非変更
- Model Load 1回／Unload 1回
- Basic AuthとNon-loopback Fail Closed
- `/healthz`以外の共通認証境界
- Plain Text Rendering、Local Asset、Security Header
- Hidden ThinkingとCanonical Historyの分離
- Normal Stop／Post-cancel Generation
- Existing CLI／Config／Model Runtime Regressionなし

## 6. Unaccepted Areas

- Queue満杯時のDisconnect Cleanup
- Token Exhaustionの最終User-visible表示
- Source／Web UIのCurrent Public Naming

Browser `auto`の明示Manual EvidenceはFollow-up時に補完する。

## 7. Immediate Next Gate

```text
UserがPhase 1-G Follow-up開始を許可
  → 実装担当が限定修正とRegression Test
  → 後継Implementer Status
  → 設計者役Follow-up Review＋新Index
  → Phase 1-G Accepted判定
  → Phase 1-H Summary Mode
```

## 8. Authorization Boundary

本Snapshotで許可された変更はReview、Follow-up Handoff、IndexのAppend-only追加までである。

まだ行わない。

- Source／Config／Tests／Scriptsの修正
- Phase 1-H実装
- Lightning Full Upload／Model Transfer
- Phase 1完了宣言／Backup
- Phase 1-ex開始
- Git初期化／Commit／Push／GitHub公開

Follow-up実装は、ユーザーが実装担当Taskへ明示的に開始指示した後に行う。

## 9. Append-Only

既存文書を変更せず、新TimestampのReview、Handoff、Indexを追加した。
