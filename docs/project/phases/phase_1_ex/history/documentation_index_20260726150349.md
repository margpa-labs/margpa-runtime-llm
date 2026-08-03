# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current_phase_1_ex_pre_migration_design_verified`
- 作成日時: `2026-07-26 15:03:49 JST`
- 更新日時: `2026-07-26 15:03:49 JST`
- Snapshot: `20260726150349`
- 作成担当: 設計統括者役
- 正本言語: 日本語
- supersedes: `documentation_index_20260726145451.md`

## 1. Current Position

```text
Phase 1-ex                              : Started
Target Documentation Architecture      : Accepted
Role Transition                        : Effective
Human Migration Control Docs           : Verified
Machine-readable Manifest              : Generated／Verified
Inventory Entries                      : 322
Unclassified／Target Collision         : 0／0
Planned Output Collision               : 0
Pre-migration Design Gate              : PASS
Directory Migration                    : Not Started
Canonical Docs                         : Not Created
Task Notification                      : Not Sent
Git／GitHub                             : Not Started
```

## 2. Target Architecture

[phase_1_ex_target_documentation_structure_20260726145451.md](architecture/phase_1_ex_target_documentation_structure_20260726145451.md)

## 3. Source Inventory

[documentation_source_inventory_and_classification_20260726150349.md](operations/documentation_source_inventory_and_classification_20260726150349.md)

Machine-readable：

[source_to_target_documentation_migration_manifest_20260726150349.json](operations/source_to_target_documentation_migration_manifest_20260726150349.json)

## 4. Link／Rollback

[documentation_link_update_and_rollback_plan_20260726150349.md](operations/documentation_link_update_and_rollback_plan_20260726150349.md)

## 5. Role Authority

[task_role_write_authority_policy_20260726150349.md](requirements/task_role_write_authority_policy_20260726150349.md)

## 6. Task Notification

[documentation_migration_task_notification_plan_20260726150349.md](handoffs/documentation_migration_task_notification_plan_20260726150349.md)

通知はMigration Cutover後まで送らない。

## 7. Preflight

[documentation_migration_preflight_20260726150349.md](operations/documentation_migration_preflight_20260726150349.md)

Machine Result：

```text
Mapped／Excluded Sources        : 320／2
Relative Links                 : 2,874
Projected Preserved            : 2,777
Stable Rewrite Required        : 22
Known History Exceptions       : 39
Known Source Defect            : 1
```

Known Source Defectは、実在するPublic Roadmapに対する旧履歴内の不正相対Linkであり、File欠損ではない。

## 8. R&D Canonical Reservation

EASA、DLAGSA、OCILNSを次へ配置する予約は有効である。

- Public Roadmap／Overview
- System Architecture
- Runtime Governance Specification
- Project Continuity Master

## 9. Authorization Boundary

Inventory／Machine Manifest／Plan／Authority／Notification設計とPre-migration検証を完了した。

実Directory作成、Copy、Move、Rename、Link Rewrite、Canonical Docs生成、Task通知またはGit操作はまだ行っていない。
