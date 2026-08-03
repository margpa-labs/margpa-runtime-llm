# Phase 1-ex Documentation Index

```yaml
document_id: phase_1_ex_documentation_index
phase: phase_1_ex
status: active
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-27 08:14:59 JST
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
- [実装担当 Linux `/proc` Test Fixture Follow-up Status](history/handoffs/implementer_status_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726235039.md)
- [設計統括者Review：Linux `/proc` Test Fixture Accepted](history/handoffs/designer_review_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726235422.md)
- [設計統括者Review：Lightning Basic Preview Manual Lifecycle Accepted](history/handoffs/designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md)
- [Lightning Environment Recovery／Lifecycle Acceptance Evidence](history/operations/lightning_basic_preview_environment_recovery_and_lifecycle_acceptance_evidence_20260727003044.md)
- [実装担当向け Lightning Auto-start Go／No-Go Assessment Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727003044.md)
- [実装担当 Lightning Auto-start Go／No-Go Assessment Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727050852.md)
- [設計統括者Review：Lightning Auto-start Go／No-Go Assessment Accepted](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727051659.md)
- [設計統括者訂正Review：Lightning Auto-start Requirement Alignment](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_requirement_alignment_correction_20260727052747.md)
- [実装担当 Stage A Availability Check Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_a_availability_check_20260727053757.md)
- [実装担当 Stage A Target Correction Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_a_target_correction_20260727054456.md)
- [設計統括者Review：Stage A Availability／Target Correction Accepted](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_stage_a_availability_and_target_correction_20260727054823.md)
- [実装担当向け Stage B Preparation Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727055625.md)
- [実装担当 Stage B Preparation Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727063323.md)
- [設計統括者Review：Stage B Preparation Accepted](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727064044.md)

Auto-start Project-side Read-only Preflight、Lightning Basic Preview Lifecycle、正しい対象に対するStage A Read-only Availability CheckおよびStage B Repository PreparationはAcceptedである。API BuilderのInstall候補が現Account／Studio UIに存在し、Free CPU Studioも稼働している。Repository側Blockerはない。Lightning UI／Platform上のStage B作業はユーザーが手動実施し、実装担当は行わない。Traffic-aware Wake-upの成立はStage B実試験まで未確認である。

## 2.3 Shared Documentation Operations

- [Current／Shared／Public Stable Historyおよび設計統括者役完全復元 運用確定Record](history/operations/stable_document_history_and_design_governance_recovery_policy_20260727071721.md)
- [Current Index Public Roadmap History Link Correction](history/operations/current_index_public_roadmap_history_link_correction_20260727072019.md)
- [情報保存最優先／累積完全版／設計統括者役専用Handoff 運用確定Record](history/operations/documentation_information_preservation_and_design_governance_handoff_policy_20260727080023.md)
- [Shared任意Category／Roadmap Lifecycle／Phase 2 History Index予約 運用確定Record](history/operations/shared_documentation_category_and_phase_index_history_policy_20260727081459.md)

Current、SharedおよびPublicのStable文書は、変更前後の原文を対応する`history/`へ`<stem>_<phase>_<language>_YYYYMMDDHHMMSS.md`形式で完全保存する。原則として各Phase完了後、Phase Backup直前に設計統括者役の完全復元PackageとDocs-only Reconstruction Validationを作成する。

Current Indexは`docs/project/current/history/index/`へ変更前後原文を保存する。Sharedでは`schemas/`、`templates/`、`user_manual/`および`design_governance_handoff/`と対応Historyを正式配置とする。PublicではOverview、Concept、RoadmapごとのHistory Directoryを使用する。

Lossless再整理、Current、Project Continuity、Sharedおよび設計統括者役Handoffは、差分だけでなく累積・自己完結の完全版として更新する。Publicも原則追加式とする。

`shared/schemas/`、`shared/templates/`および`shared/user_manual/`は必要な場合だけ使用する。Docs運用は既存`shared/operations/`、権限管理は既存`shared/task_roles/`へ集約する。Roadmap Stable名は`roadmap_ja.md`のまま維持し、Timestamp付き完全SnapshotはHistoryだけへ保存する。Phase 2以降は各Phaseの`history/index/`をAppend-only Index Snapshot置場として使用する。

## 3. Role／Notification

- [Task Role／Write Authority](../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Documentation Structure／Task Operations](../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Design Governance Handoff](../../shared/design_governance_handoff/design_governance_handoff_ja.md)
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
- [Linux `/proc` Test Fixture Follow-up Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726235422.md)
- [Lightning Basic Preview Manual Lifecycle Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md)
- [Lightning Environment Recovery／Lifecycle Acceptance Evidence](history/operations/lightning_basic_preview_environment_recovery_and_lifecycle_acceptance_evidence_20260727003044.md)
- [Lightning Auto-start Go／No-Go Assessment Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727003044.md)
- [Lightning Auto-start Go／No-Go Assessment Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727050852.md)
- [Lightning Auto-start Go／No-Go Assessment Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727051659.md)
- [Lightning Auto-start Requirement Alignment Correction Review](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_requirement_alignment_correction_20260727052747.md)
- [Stage A Availability Check Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_a_availability_check_20260727053757.md)
- [Stage A Target Correction Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_a_target_correction_20260727054456.md)
- [Stage A Availability／Target Correction Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_stage_a_availability_and_target_correction_20260727054823.md)
- [Stage B Preparation Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727055625.md)
- [Stage B Preparation Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727063323.md)
- [Stage B Preparation Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727064044.md)
- [Stable History／Design Governance Recovery Policy](history/operations/stable_document_history_and_design_governance_recovery_policy_20260727071721.md)
- [Current Index Public Roadmap History Link Correction](history/operations/current_index_public_roadmap_history_link_correction_20260727072019.md)
- [Information Preservation／Design Governance Handoff Policy](history/operations/documentation_information_preservation_and_design_governance_handoff_policy_20260727080023.md)
- [Shared Documentation Category／Phase Index History Policy](history/operations/shared_documentation_category_and_phase_index_history_policy_20260727081459.md)

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
- [2026-07-26 23:54:22](history/documentation_index_20260726235422.md)
- [2026-07-27 00:24:40](history/documentation_index_20260727002440.md)
- [2026-07-27 00:30:44](history/documentation_index_20260727003044.md)
- [2026-07-27 05:16:59](history/documentation_index_20260727051659.md)
- [2026-07-27 05:27:47](history/documentation_index_20260727052747.md)
- [2026-07-27 05:48:23](history/documentation_index_20260727054823.md)
- [2026-07-27 05:56:25](history/documentation_index_20260727055625.md)
- [2026-07-27 06:40:44](history/documentation_index_20260727064044.md)
- [2026-07-27 07:17:21](history/documentation_index_20260727071721.md)
- [2026-07-27 07:20:19](history/documentation_index_20260727072019.md)
- [2026-07-27 08:00:23](history/documentation_index_20260727080023.md)
- [2026-07-27 08:14:59](history/documentation_index_20260727081459.md)
