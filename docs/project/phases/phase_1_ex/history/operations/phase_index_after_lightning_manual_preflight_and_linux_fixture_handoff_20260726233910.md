# Phase 1-ex Documentation Index

```yaml
document_id: phase_1_ex_documentation_index
phase: phase_1_ex
status: active
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-26 23:39:10 JST
owner: 設計統括者役
rag_default: true
```

## 1. Phase Goal

Phase 1成果を公開可能・継続可能・Git管理可能な構造へ移し、GitHub初回公開と後続Phaseの基盤を整える。

## 2. Documentation Migration

- [ADR-0024](adr/adr_0024_phase_first_project_documentation_and_lossless_history_ja.md)
- [Target Documentation Structure](architecture/target_documentation_structure_ja.md)
- [Migration Requirements](requirements/documentation_migration_and_canonical_content_requirements_ja.md)
- [Source Inventory](operations/documentation_source_inventory_and_classification_ja.md)
- [Source→Target Manifest](operations/source_to_target_documentation_migration_manifest.json)
- [Link／Rollback Plan](operations/documentation_link_update_and_rollback_plan_ja.md)
- [Migration Preflight](operations/documentation_migration_preflight_ja.md)
- [Candidate Report](operations/documentation_migration_candidate_report.json)
- [Migration Receipt](operations/documentation_directory_migration_receipt_ja.md)
- [Migration Validation](operations/documentation_directory_migration_validation_ja.md)
- [Legacy Root Retirement Manifest](operations/documentation_legacy_root_retirement_manifest.json)
- [Legacy Root Retirement Validation](operations/documentation_legacy_root_retirement_validation_ja.md)
- [Target Manifest](operations/documentation_directory_migration_target_manifest.json)

## 2.1 Phase 1-ex追加設計

- [ADR-0025 Public Demo／Auto-start／Pre-release Gate](adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [ADR-0026 Lightning Basic Preview Lifecycle／Managed Secrets](adr/adr_0026_lightning_basic_preview_lifecycle_and_managed_secrets_ja.md)
- [Public Demo／Auto-start／Pre-release Requirements](requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Public Demo／Auto-start／RAG Extension Architecture](architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [Pre-initial Commit Documentation Refresh Plan](operations/pre_initial_commit_documentation_refresh_plan_ja.md)

## 2.2 Active Implementation Handoff

- [実装担当向け Lightning Auto-start Read-only Preflight Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_read_only_preflight_20260726192912.md)
- [実装担当向け Lightning Basic Preview Lifecycle Scripts Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_basic_preview_lifecycle_scripts_20260726194949.md)
- [設計統括者Review：Auto-start／Lifecycle Scripts](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_and_lifecycle_scripts_20260726202036.md)
- [実装担当向け Lifecycle Safety Follow-up Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726202036.md)
- [実装担当 Lifecycle Safety Follow-up最終Status](history/handoffs/implementer_status_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726212010.md)
- [設計統括者Review：Lifecycle Safety Follow-up Accepted](history/handoffs/designer_review_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726213429.md)
- [Lightning手動Environment／Preflight Evidence](history/operations/lightning_manual_environment_and_preflight_evidence_20260726233910.md)
- [実装担当向け Linux `/proc` Test Fixture Follow-up Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726233910.md)

Auto-start Project-side Read-only PreflightとLightning Basic Preview Lifecycle ScriptsはRepository実装としてAcceptedである。Lightning上のFile、Environment、Managed Secrets、Read-only PreflightおよびBasic Preview Preflightも合格した。Lifecycle Unit TestはLinux `/proc`とTest Fixtureの不整合により`28 passed／2 failed`であり、Test-only Follow-up中である。`start／restart／stop`、Public URL、Sleep／WakeおよびAuto-start Platform判定へはまだ進まない。

## 3. Role／Notification

- [Task Role／Write Authority](../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Documentation Structure／Task Operations](../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Notification Plan](handoffs/documentation_migration_task_notification_plan_ja.md)

## 4. Current Canonical

- [Current Documentation Index](../../current/documentation_index_ja.md)
- [Requirements](../../current/requirements/requirements_specification_ja.md)
- [System Architecture](../../current/architecture/system_architecture_ja.md)
- [Technology Selection](../../current/architecture/technology_selection_ja.md)
- [Basic Design](../../current/architecture/basic_design_ja.md)
- [Runtime Governance](../../current/governance/runtime_governance_specification_ja.md)
- [Project Continuity Master](../../current/project_continuity/project_continuity_master_ja.md)

## 5. Phase 1

- [Phase 1 Index](../phase_1/phase_index_ja.md)

## 6. Remaining Phase 1-ex Scope

1. Lightning Auto-start Read-only Preflight
2. Auto-start Go／No-Go
3. Basic Previewと分離したPublic Demo基盤
4. 既存DocsのLossless再整理
5. Canonical／Public DocsのJA／EN作成
6. Local Mac簡易Documentation RAG＋External Hook
7. Git運用設計
8. Pre-initial Commit Documentation Refresh
9. 公開Allowlist／Sanitation
10. Git初期化／Initial Commit準備
11. Public Demo最終確認
12. Phase 1-ex Review／Backup／GitHub公開

匿名Public Accessは、Public Docs、License／Terms、Git運用、SanitationおよびInitial Commit準備の完了後に、ユーザーの明示許可を得て有効化する。

## 7. History

Phase 1-ex開始時の旧Index、Role Transition、Migration Control EventおよびMigration前Stable Source 8件の原文は`history/`へ保持する。旧Root重複配置は全原文のSHA-512一致確認後に退役済みである。

- [Current／Public JA／EN同等粒度決定](history/requirements/current_public_ja_en_equivalent_granularity_decision_20260726180711.md)
- [Phase Index Append-only History Repair](history/operations/phase_index_append_only_history_repair_20260726202935.md)
- [Append-only／User Authority Governance Freeze](history/operations/append_only_and_user_authority_governance_freeze_20260726203948.md)
- [Lifecycle Safety Follow-up Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726213429.md)
- [Lightning Manual Environment／Preflight Evidence](history/operations/lightning_manual_environment_and_preflight_evidence_20260726233910.md)
- [Linux `/proc` Test Fixture Follow-up Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726233910.md)

### 7.1 Index Snapshot Chain

- [2026-07-26 15:40:09](history/documentation_index_20260726154009.md)
- [2026-07-26 17:00:34](history/documentation_index_20260726170034.md)
- [2026-07-26 17:53:18](history/documentation_index_20260726175318.md)
- [2026-07-26 18:07:11](history/documentation_index_20260726180711.md)
- [2026-07-26 19:29:12](history/documentation_index_20260726192912.md)
- [2026-07-26 19:49:49](history/documentation_index_20260726194949.md)
- [2026-07-26 20:20:36](history/documentation_index_20260726202036.md)
- [2026-07-26 20:29:35](history/documentation_index_20260726202935.md)
- [2026-07-26 20:39:48](history/documentation_index_20260726203948.md)
- [2026-07-26 21:34:29](history/documentation_index_20260726213429.md)
- [2026-07-26 23:39:10](history/documentation_index_20260726233910.md)
