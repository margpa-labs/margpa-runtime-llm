# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 00:32:01 JST`
- 更新日時: `2026-07-21 00:32:01 JST`
- Snapshot: `20260721003201`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260720235113.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-F Repository Follow-up         : Changes Requested／Minor Static Gate
Previous Phase 1-F Findings            : Resolved／5 of 5
Phase 1-F Lightning Preflight          : Not Run
Phase 1-F Lightning CUDA／CPU Gate     : Not Run
Phase 1-G Concept                      : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260720235113.md](documentation_index_20260720235113.md)から継承する。本Snapshotでは、Phase 1-F Implementer Follow-up Statusと設計Reviewを追加し、前回Phase 1-F Reviewの状態を後継Reviewへ置き換える。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260720235113.md](documentation_index_20260720235113.md) | 本文書 |
| superseded | [Phase 1-F Lightning Cross-environment Runtime設計Review](handoffs/designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md) | [Phase 1-F Repository Follow-up設計Review](handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| implementer_complete_waiting_review | [Phase 1-F Repository Review Follow-up Status](handoffs/implementer_status_phase_1f_repository_review_follow_up_20260721001705.md) | 前回Findingへの実装対応と検証結果 |
| changes_requested_minor | [Phase 1-F Repository Follow-up設計Review](handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md) | 独立検証、残存Static Gate、Lightning搬入判定 |

## 5. Phase 1-F Follow-up Summary

```text
Previous High Findings       : Resolved／2 of 2
Previous Medium Findings     : Resolved／2 of 2
Previous Low Observation     : Resolved／1 of 1
Default Test                 : Pass／183 passed、3 deselected
Mac Model Smoke              : Pass
Mac Strict Acceptance        : Pass／22 of 22 required checks
Full Project Mypy            : Fail／1 test error
Lightning Preflight          : Not Run
Lightning CUDA／CPU Gate     : Not Run
Decision                     : Changes Requested／Minor Follow-up
Phase 1-F Completion         : Not Accepted Yet
```

新規必須Follow-upは、Testコード1箇所のMypy Export境界修正と、Full Project Gateの再実行である。

## 6. Accepted Pending Setting Change

ユーザー決定により、次の小規模変更時にDefaultを変更する。

```toml
[generation]
max_new_tokens = 2048
```

Current Repositoryは`512`である。Config既定値と関連Testを同時に更新し、後続のGuardrail／Context／UI実装で再調整可能な設定として維持する。

Thinking表示Label変更はPhase 1-GのUI／注記設計へ残す。

## 7. Immediate Next Gate

```text
Minor Repository Follow-up
  → Short Designer Review
  → Lightning Read-only Preflight
  → Single Source／Model Upload
  → Lightning Python 3.12.11／CUDA／CPU Verification
  → Phase 1-F Final Review
  → Phase 1-G Canonical Design／Implementation
```

Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未許可／未着手である。

## 8. Authorization Boundary

本IndexはSource／Config／Tests／Scriptsの修正、Lightning操作、Upload、Model Download、Phase 1-G実装、Backup、Git、GitHub公開を許可しない。

## 9. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。
