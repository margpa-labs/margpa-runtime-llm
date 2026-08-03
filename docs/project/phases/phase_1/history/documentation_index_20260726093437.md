# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-26 09:34:37 JST`
- 更新日時: `2026-07-26 09:34:37 JST`
- Snapshot: `20260726093437`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726092413.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Phase 1-F Lightning External Pure CPU Runtime  : Accepted
Repository Test Isolation Follow-up            : Accepted
Mac Full Repository Suite                      : Green
Lightning Full Repository Suite                : Revalidation Pending
Lightning Web Preview Acceptance               : Pending
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726092413.md](documentation_index_20260726092413.md)を継承する。

前SnapshotのTest-only Handoffに基づき、Platform Execution Environment IsolationとModel Root Subprocess Environment Isolationが実装された。

設計者役がMac Repositoryで独立ReviewおよびVerificationを行い、Repository変更をAcceptedとした。

## 3. Accepted Review

[designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md](handoffs/designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md)

判定：

```text
Repository Test-only Change : ACCEPTED
Targeted Test               : 41 passed
Mac Full Suite              : 267 passed／3 deselected
Ruff                        : PASS
Ruff Format                 : PASS／95 files
Mypy                        : PASS／95 source files
Production Change           : NONE
```

## 4. Implemented Isolation

### Platform

Mock Native Platform Testへ次を明示した。

```text
raw_execution_environment=native
```

実Lightning Container MarkerからTestを分離する。

### Model Root

Temporary Model Root TestのSubprocessから次を除外した。

```text
MARGPA_MODEL_ROOT
MARGPA_PROFILE
```

ユーザーShellのApplication設定からTestを分離する。

## 5. Current Lightning Manual

[lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)

## 6. External Runtime Review

[designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)

External Pure CPU Runtime Accepted判定を維持する。

## 7. Lightning Revalidation

Lightningへ反映するFile：

```text
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_lightning_cpu_native_setup.py
```

実行：

```text
Targeted Test
  → 41 passed expected

Full Suite
  → 266 passed
  → 1 skipped
  → 3 deselected
  → 0 failed
```

手動Environment UnsetなしでPassすることを確認する。

## 8. Native Acceptance

Production Artifact変更なし。

前回の：

```text
all_required_checks_passed=true
```

を有効なEvidenceとして維持し、Native Acceptance再実行を要求しない。

## 9. Next Gate

```text
Lightning Test 2File反映
  → Lightning Targeted Test
  → Lightning Full Suite
  → Full Suite Green Review
  → Lightning Web Preview Acceptance
  → Top-level Phase 1 Completion Decision
```

## 10. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 11. Authorization Boundary

本SnapshotはLightningへのTest 2File反映とRead-only Test実行手順を示す。

外部操作はユーザー実行Gateである。Production Code変更、Git／GitHub、Phase 1完了宣言、Backup、Phase 1-ex開始またはRAG実装を自動許可しない。

## 12. Append-Only

旧Index、旧Review、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。

