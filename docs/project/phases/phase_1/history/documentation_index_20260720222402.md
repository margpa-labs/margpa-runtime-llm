# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-20 22:24:02 JST`
- 更新日時: `2026-07-20 22:24:02 JST`
- Snapshot: `20260720222402`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260720220216.md`

## 1. Current Position

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Implemented／Review Pending
Phase 1-F Repository Work      : Reported Complete／Review Pending
Lightning Native Verification : Waiting
Phase 1 Completion／Backup     : Waiting
Phase 1-ex                     : Added／Requirements Pending
Initial GitHub Publication     : Deferred until Phase 1-ex completion
Privacy Scrub                  : Complete for managed files
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260720220216.md](documentation_index_20260720220216.md)から継承する。本Snapshotの置換／追加を下表に示す。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [phase_completion_backup_policy_20260719171836.md](operations/phase_completion_backup_policy_20260719171836.md) | [phase_completion_backup_policy_20260720222402.md](operations/phase_completion_backup_policy_20260720222402.md) |
| historical | [documentation_rules_20260720220216.md](requirements/documentation_rules_20260720220216.md) | [documentation_rules_20260720222402.md](requirements/documentation_rules_20260720222402.md) |
| historical | [common_project_handoff_20260720220216.md](handoffs/common_project_handoff_20260720220216.md) | [common_project_handoff_20260720222402.md](handoffs/common_project_handoff_20260720222402.md) |
| historical | [documentation_index_20260720220216.md](documentation_index_20260720220216.md) | 本文書 |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| pending_definition | [phase_1_ex_operations_reorganization_requirements_20260720222402.md](requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md) | Phase 1-exの存在、目的、初回公開Gate |
| verified | [runtime_and_absolute_path_verification_20260720222402.md](operations/runtime_and_absolute_path_verification_20260720222402.md) | Mac動作、Production Path、`.venv`／Model境界 |

## 5. Accepted Operational Changes

- 各PhaseのBackup確定後、同一Snapshotを原則GitHubへ反映する。
- 初回GitHub公開だけはPhase 1-ex完了後まで延期する。
- Phase 1-ex「運用再整備」をPhase 1と初回公開の間へ追加する。
- 毎回、Backup Candidate内のProject RootをSanitizeし、不要物を除去する。
- 第一者の公開Identityは`Nazuna Research`へ統一する。

## 6. Archive Exclusion Summary

`.DS_Store`、`.venv`、`models` Symlink、Model Binary、`.git`、Cache、Bytecode、Coverage、Notebook Checkpoint、Credential、Secret、Local Runtime Data、Temporary Fileを公開Archiveへ含めない。

## 7. Verification Summary

```text
Default Test                 : 181 passed
Ruff／Mypy                   : Pass
Mac Metal Model Smoke       : 2 passed／1 expected skip
Managed Production /Users   : 0
Lightning Native            : Pending
```

## 8. Next Gate

```text
Phase 1-F Review
  → Lightning Verification
  → Phase 1 User Acceptance／Completion／Backup
  → Phase 1-ex Requirements／Implementation／Acceptance
  → Publication Candidate Backup／Sanitation
  → Initial GitHub Publication
```

Phase 1-Gとの順序は未確定である。

## 9. Authorization Boundary

本IndexはBackup作成、Phase 1-ex／1-G実装、Git初期化、GitHub操作、Lightning操作、外部公開を許可しない。

## 10. Append-Only

既存Docsを変更せず、新Timestampの後継文書を作成した。
