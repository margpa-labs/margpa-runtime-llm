# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-26 09:42:41 JST`
- 更新日時: `2026-07-26 09:42:41 JST`
- Snapshot: `20260726094241`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726093437.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Phase 1-F Lightning External Pure CPU Runtime  : Accepted
Repository Test Isolation Follow-up            : Accepted
Mac Full Repository Suite                      : Green
Lightning Full Repository Suite                : Green
Lightning Web Preview Acceptance               : Pending
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726093437.md](documentation_index_20260726093437.md)を継承する。

ユーザーがLightningへTest-only変更を反映し、Targeted TestおよびFull Suiteを再実行した。Cross-platform Full Suite Greenを確認した。

## 3. Accepted Revalidation

[designer_review_phase_1f_lightning_full_suite_revalidation_20260726094241.md](handoffs/designer_review_phase_1f_lightning_full_suite_revalidation_20260726094241.md)

```text
Targeted Test : 41 passed
Full Suite    : 266 passed／1 skipped／3 deselected
Failure       : 0
```

## 4. Current Runtime State

```text
Environment Verification   : PASS
External Pure CPU Runtime  : ACCEPTED
Native Acceptance          : PASS
Required Checks            : ALL TRUE
Mac Full Suite             : GREEN
Lightning Full Suite       : GREEN
```

## 5. Current Manual

[lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)

## 6. Next Gate

```text
Lightning Web Preview起動
  → Health Check
  → Basic認証境界
  → Port公開
  → Browser手動確認
  → Shutdown
  → Lightning Web Acceptance Review
```

## 7. Native Acceptance

Test-only変更のため再実行を要求しない。前回の`all_required_checks_passed=true`を有効なEvidenceとして維持する。

## 8. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 9. Authorization Boundary

次のユーザー実行GateはLightning Web Previewの起動・手動確認である。

Git／GitHub、Phase 1完了宣言、Backup、Phase 1-ex開始またはRAG実装を自動許可しない。

## 10. Append-Only

旧Index、旧Review、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。

