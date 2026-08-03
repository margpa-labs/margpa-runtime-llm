# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 09:07:25 JST`
- 更新日時: `2026-07-21 09:07:25 JST`
- Snapshot: `20260721090725`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721010621.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Read-only Execution          : Accepted
Phase 1-F Lightning Preflight          : Blocked／uv Version Gate
Lightning Existing uv                  : 0.11.18／Unchanged
Project Expected uv                    : 0.11.29／Retained
Phase 1-F Full Upload                  : Not Authorized
Phase 1-F Lightning CUDA／CPU Gate     : Not Run
generation.max_new_tokens              : 2048／Applied
Post-generation Summary Mode           : Accepted／Deferred Phase 1-G Follow-up
Phase 1-G Concept                      : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721010621.md](documentation_index_20260721010621.md)から継承する。本Snapshotでは、Lightning Read-only Preflight Status／ReviewとPost-generation Summary Mode要件予約を追加する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721010621.md](documentation_index_20260721010621.md) | 本文書 |
| superseded | [Phase 1-F Minor Static Gate Follow-up設計Review](handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md) | [Phase 1-F Lightning Read-only Preflight設計Review](handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| blocked_waiting_designer_decision | [Phase 1-F Lightning Read-only Preflight Status](handoffs/implementer_status_phase_1f_lightning_read_only_preflight_20260721013900.md) | Lightning実行Evidenceとuv Version不一致 |
| execution_accepted_follow_up_required | [Phase 1-F Lightning Read-only Preflight設計Review](handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md) | 実行受入、uv方針、Full Upload停止判断 |
| accepted_deferred | [Post-generation Summary Mode要件予約](requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md) | 要約モードOFF／ONと初期Runtime値 |

## 5. Preflight Review Summary

```text
Script Placement／Integrity   : Pass
Implementer Scope Compliance  : Pass
Host／Container／Python       : Pass
GPU Evidence                  : Tesla T4／15360 MiB
nvcc                          : Available
GPU Preflight                 : Fail／uv 0.11.18
CPU Candidate Preflight       : Fail／uv 0.11.18
Expected uv                   : 0.11.29／Retained
Environment Mutation          : None
Full Upload                   : Not Authorized
```

次はLightning既設uvを変更せず、公式uv 0.11.29をProject専用隔離Pathへ導入する限定Follow-upを設計する。

## 6. Summary Mode Accepted Values

```text
User Option                  : 要約モード OFF／ON
Default                      : OFF
Normal max_new_tokens        : 2048
Summary max_new_tokens       : 1024
Summary Thinking             : disabled
Initial Backend              : Main Model再利用
Original Final Answer        : Preserve
Implementation Timing        : Phase 1-G Accepted後の小規模Follow-up
```

要約モードはPhase 1-Fへ混在させない。

## 7. Immediate Next Gate

```text
Project-local uv 0.11.29 Bootstrap Handoff
  → Limited Environment Follow-up
  → Preflight Re-run
  → Designer Review
  → Full Upload可否判定
```

## 8. Deferred Items

- Full Upload、Model Transfer、Dependency Sync、Native Buildはuv Follow-up後に判断する。
- Phase 1-GとSummary Modeの実装はPhase 1-F完了後に扱う。
- Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未着手である。

## 9. Authorization Boundary

本IndexとReviewは、Studio-global uv変更、Project-local uv導入、Full Upload、Model Transfer、Dependency Install、Native Build、Phase 1-G実装、Summary Mode実装、Backup、Git、GitHub公開を許可しない。

## 10. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。
