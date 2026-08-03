# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current_pre_phase_1_backup_sanitized`
- 作成日時: `2026-07-26 12:13:46 JST`
- 更新日時: `2026-07-26 12:13:46 JST`
- Snapshot: `20260726121346`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726120229.md`

## 1. Current Position

```text
Top-level Phase 1                          : Complete／Accepted
Phase 1 Pre-backup Documentation           : Complete
Pre-backup Privacy／Sanitation Scan        : Passed
Phase 1 Backup Trigger                     : Ready／Execution Authorized
Phase 1 Backup                             : Not Yet Created
Phase 1-ex                                 : Next／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726120229.md](documentation_index_20260726120229.md)を継承する。

Backup前Privacy Scanで、過去Statusに検索Pattern説明として残っていた旧Public Handle Literalを1件検出した。Public Identity PolicyのPrivacy例外に基づき匿名化し、意味を維持した。

## 3. Pre-backup Privacy／Sanitation Scan

[pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md](operations/pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md)

```text
実個人名／Email／Path   : 0
Credential実値          : 0
Secret File             : 0
旧Public Handle          : 0 after scrub
Expected Test Fixtures  : retained
```

## 4. Phase 1 Lightning Finalization

[phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md](operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md)

## 5. Phase 1 Final Review

[designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)

## 6. Phase 1-ex Current Requirements

[phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md](requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md)

## 7. Backup Input Snapshot

Phase 1 Backupは、本IndexをCurrent Indexとする管理対象からSanitized Candidateを作成する。

Include候補：

```text
.gitignore
.python-version
config/
docs/
pyproject.toml
scripts/
src/
tests/
uv.lock
```

Exclude：

```text
.DS_Store
.venv/
models/
models Symbolic Link
.git/
Cache
Bytecode
Coverage
Secret
Local Data
```

## 8. Authorization Boundary

Phase 1確定Backupの作成、Sanitation、HashおよびRestore検証はユーザーにより許可されている。

Phase 1-ex変更、Git／GitHub操作、Lightning変更はまだ許可されていない。

## 9. Append-Only

旧Indexおよび旧文書は履歴として保持する。本IndexをPhase 1 Backup入力SnapshotのCurrent Indexとする。
