# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260726175318
state_at: 2026-07-26 17:53:18 JST
status: historical_reconstructed
snapshot_of: ../phase_index_ja.md
supersedes: documentation_index_20260726170034.md
reconstruction_source: recorded_patch_sequence
reconstruction_fidelity: exact_logical_state_with_history_relative_links_rebased
```

## 1. Phase Goal

Phase 1成果を公開可能・継続可能・Git管理可能な構造へ移し、GitHub初回公開と後続Phaseの基盤を整える。

## 2. Documentation Migration

- [ADR-0024](../adr/adr_0024_phase_first_project_documentation_and_lossless_history_ja.md)
- [Target Documentation Structure](../architecture/target_documentation_structure_ja.md)
- [Migration Requirements](../requirements/documentation_migration_and_canonical_content_requirements_ja.md)
- [Source Inventory](../operations/documentation_source_inventory_and_classification_ja.md)
- [Source→Target Manifest](../operations/source_to_target_documentation_migration_manifest.json)
- [Link／Rollback Plan](../operations/documentation_link_update_and_rollback_plan_ja.md)
- [Migration Preflight](../operations/documentation_migration_preflight_ja.md)
- [Candidate Report](../operations/documentation_migration_candidate_report.json)
- [Migration Receipt](../operations/documentation_directory_migration_receipt_ja.md)
- [Migration Validation](../operations/documentation_directory_migration_validation_ja.md)
- [Legacy Root Retirement Manifest](../operations/documentation_legacy_root_retirement_manifest.json)
- [Legacy Root Retirement Validation](../operations/documentation_legacy_root_retirement_validation_ja.md)
- [Target Manifest](../operations/documentation_directory_migration_target_manifest.json)

## 2.1 Phase 1-ex追加設計

- [ADR-0025](../adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [Public Demo／Auto-start要件](../requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Public Demo／Auto-start／RAG Extension Architecture](../architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [Pre-initial Commit Documentation Refresh Plan](../operations/pre_initial_commit_documentation_refresh_plan_ja.md)

## 3. Role／Notification

- [Task Role／Write Authority](../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Documentation Structure／Task Operations](../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Notification Plan](../handoffs/documentation_migration_task_notification_plan_ja.md)

## 4. Current Canonical

- [Current Documentation Index](../../../current/documentation_index_ja.md)
- [Requirements](../../../current/requirements/requirements_specification_ja.md)
- [System Architecture](../../../current/architecture/system_architecture_ja.md)
- [Technology Selection](../../../current/architecture/technology_selection_ja.md)
- [Basic Design](../../../current/architecture/basic_design_ja.md)
- [Runtime Governance](../../../current/governance/runtime_governance_specification_ja.md)
- [Project Continuity Master](../../../current/project_continuity/project_continuity_master_ja.md)

## 5. Phase 1

- [Phase 1 Index](../../phase_1/phase_index_ja.md)

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
