# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current_pre_phase_1_backup`
- 作成日時: `2026-07-26 12:02:29 JST`
- 更新日時: `2026-07-26 12:02:29 JST`
- Snapshot: `20260726120229`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726111632.md`

## 1. Current Position

```text
Phase 1-A～1-I                              : Complete／Accepted
Mac Web Manual Acceptance                  : Passed
Lightning Pure CPU Runtime                 : Accepted
Mac Full Repository Suite                  : Green
Lightning Full Repository Suite            : Green
Lightning External Web Acceptance          : Passed
Top-level Phase 1                          : Complete／Accepted
Phase 1 Pre-backup Documentation           : Complete
Phase 1 Backup Trigger                     : Ready／Execution Authorized
Phase 1-ex                                 : Next／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726111632.md](documentation_index_20260726111632.md)を継承する。

Lightning Pure CPU環境構築の実績、Test Isolation修正、外部Web Acceptance、CPU／Mobile制約、Studio Sleep、Basic認証継続、将来Public Demo表記、Auto-start早期判定、Git準備前倒しおよびPhase 1-exの最新順序を統合した。

## 3. Phase 1 Lightning Finalization Record

[phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md](operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md)

本書を、Lightning Pure CPU環境構築開始からPhase 1確定Backup直前までの統合入口とする。

## 4. Phase 1 Final Review

[designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)

```text
Blocking Finding            : None
Top-level Phase 1           : Complete／Accepted
Backup Gate A               : Passed
Backup Gate B               : Passed
```

## 5. Current User Manual

[phase_1_web_and_lightning_user_manual_20260726111632.md](user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md)

詳細なLightning再構築：

[lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)

## 6. Phase 1-ex Current Requirements

親要件：

[phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)

最新開始順序／Public Demo／Git準備：

[phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md](requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md)

## 7. Current Decisions

```text
Basic Authentication       : Keep for current Preview
Personal Contact in Repo   : Prohibited
README Demo Statement      : 「将来、Public Demo方式も検討しています。」
Public Demo Implementation : Deferred
Auto-start                 : Early read-only preflight in Phase 1-ex
Git Planning／Preparation  : Before docs Lossless Compilation
Initial Public Commit      : After docs reorganization and final sanitation
Simple RAG                 : Mac only after docs structure stabilization
```

## 8. Phase 1 Backup

ユーザーが、本Indexと統合記録を作成した後にPhase 1確定Backupを取得するよう指示した。

Backupは次を満たすこと。

- Project Root外へ保存
- Allowlist方式
- `.venv`、Model／Symlink、`.git`、Cache、`.DS_Store`、Secretを除外
- File InventoryとSHA-512
- Archive SHA-512
- Detached Receipt
- Temporary Restore
- Restored Inventory／Hash検証
- 個人固有情報／Absolute Local Path／Credential Scan

## 9. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 10. Authorization Boundary

本Indexの後続としてPhase 1確定Backupの作成はユーザーにより許可されている。

次はまだ許可されていない。

- Phase 1-exの実変更
- Git初期化、Commit、Tag、Remote、Push
- GitHub公開
- Lightning Auto-start設定
- Docs Directory Migration
- RAG実装

## 11. Append-Only

旧Index、旧Review、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本IndexをBackup前最新Indexとする。
