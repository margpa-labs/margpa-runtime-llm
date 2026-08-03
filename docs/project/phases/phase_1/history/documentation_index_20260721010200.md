# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 01:02:00 JST`
- 更新日時: `2026-07-21 01:02:00 JST`
- Snapshot: `20260721010200`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721003201.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Lightning Preflight          : Authorized／Not Run
Phase 1-F Lightning CUDA／CPU Gate     : Not Run
generation.max_new_tokens              : 2048／Applied
Phase 1-G Concept                      : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721003201.md](documentation_index_20260721003201.md)から継承する。本Snapshotでは、Phase 1-F Minor Static Gate Follow-up StatusとAccepted Reviewを追加し、前回ReviewのChanges Requested状態を解消する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721003201.md](documentation_index_20260721003201.md) | 本文書 |
| superseded | [Phase 1-F Repository Follow-up設計Review](handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md) | [Phase 1-F Minor Static Gate Follow-up設計Review](handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| implementer_complete_waiting_review | [Phase 1-F Minor Static Gate Follow-up Status](handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md) | Full Mypy修正、2048既定値反映、再検証 |
| accepted | [Phase 1-F Minor Static Gate Follow-up設計Review](handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md) | Repository受入とLightning Preflight進行判定 |

## 5. Phase 1-F Repository Summary

```text
Previous Static Finding     : Resolved
Full Project Mypy           : Pass／70 source files
Default Test                : Pass／183 passed、3 deselected
Ruff／Compile／Shell／Lock   : Pass
Mac Metal Model Smoke       : Pass
Application Default         : max_new_tokens = 2048
New Finding                 : 0
Repository Decision         : Accepted
Phase 1-F Completion        : Waiting Lightning Native Gate
```

## 6. Immediate Next Gate

```text
Lightning Read-only Preflight
  → Preflight Result Review
  → Single Source／Model Upload
  → Lightning Python 3.12.11／CUDA／CPU Verification
  → Phase 1-F Final Review
  → Phase 1-G Canonical Design／Implementation
```

最初はPreflight ScriptだけをTargetへ配置し、Environment Mode、Python、uv、Container、GPU Allocationを確認する。Full Upload、Dependency Sync、Native BuildはPreflight確認後に進める。

## 7. Deferred Items

- Thinking表示Labelの`高度推論`から`推論過程`等への変更はPhase 1-Gで扱う。
- Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未着手である。

## 8. Authorization Boundary

本IndexとReviewはLightning Read-only Preflightを許可する。Source／Config変更、Full Upload、Dependency Install、Native Build、Model Download、Phase 1-G実装、Backup、Git、GitHub公開は許可しない。

## 9. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。
