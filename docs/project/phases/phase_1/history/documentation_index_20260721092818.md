# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 09:28:18 JST`
- 更新日時: `2026-07-21 09:28:18 JST`
- Snapshot: `20260721092818`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721090725.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Lightning Preflight          : Accepted
Lightning Project／Studio-local uv     : 0.11.29／Pass
Lightning Existing uv                  : 0.11.18／Unchanged
Lightning Python                       : 3.12.11／Retained
Phase 1-F Full Upload Handoff          : Ready to Create
Phase 1-F Full Upload                  : Not Run／Not Yet Authorized
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

変更のないCurrent Setは[documentation_index_20260721090725.md](documentation_index_20260721090725.md)から継承する。本Snapshotでは、ユーザー実行によるProject／Studio-local uv導入とPreflight再実行のAccepted Reviewを追加し、前回のuv Version Blockを解消する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721090725.md](documentation_index_20260721090725.md) | 本文書 |
| superseded | [Phase 1-F Lightning Read-only Preflight設計Review](handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md) | [Phase 1-F Lightning Project-local uv Preflight設計Review](handoffs/designer_review_phase_1f_lightning_project_local_uv_preflight_20260721092818.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [Phase 1-F Lightning Project-local uv Preflight設計Review](handoffs/designer_review_phase_1f_lightning_project_local_uv_preflight_20260721092818.md) | uv隔離、Preflight再合格、Python維持、次Gate判定 |

## 5. Preflight Final Summary

```text
Project／Studio-local uv      : 0.11.29／Pass
Binary SHA-512                : Recorded
Lightning Existing uv         : 0.11.18／Unchanged
Permanent PATH Mutation       : None
Python                        : 3.12.11／Retained
GPU Preflight                 : Pass／Exit 0
CPU Candidate Preflight       : Pass／Exit 0
nvcc                          : Available
Preflight Decision            : Accepted
Full Upload                   : Waiting Dedicated Handoff
```

## 6. Python Decision

Lightning Pythonは3.12.11のまま維持する。Mac 3.13.14とLightning 3.12.11を正式Support Pairとして検証し、Cross-version交換性を示す。

Python 3.13をLightningへ追加する場合は、3.12.11を置換せず、将来の別Environment／Profileとして扱う。

## 7. Immediate Next Gate

```text
Full Upload／Native Verification Handoff作成
  → Single Upload
  → Dependency／CUDA／CPU Native Gate
  → Designer Final Review
```

## 8. Deferred Items

- Summary ModeはPhase 1-G Accepted後の小規模Follow-upで実装する。
- Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未着手である。

## 9. Authorization Boundary

本IndexとReviewはFull Upload／Native Verification Handoffの作成を許可する。Full Upload、Model Transfer、Dependency Install、Native Build、Python Upgrade、Source変更、Phase 1-G実装、Backup、Git、GitHub公開は専用Handoff前には実行しない。

## 10. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。
