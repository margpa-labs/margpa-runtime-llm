# MARGPA Runtime LLM Current Documentation Index

```yaml
document_id: current_documentation_index
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-27 07:52:36 JST
owner: 設計統括者役
active_phase: phase_1_ex
rag_default: true
```

## Current Position

```text
Phase 1                  : COMPLETE／ACCEPTED
Phase 1 Backup           : COMPLETED／VERIFIED
Phase 1-ex               : IN PROGRESS
Documentation Migration : COMPLETE／LEGACY ROOT RETIRED
Git／GitHub              : NOT STARTED
```

## Current Canonical

- [要件定義書](requirements/requirements_specification_ja.md)
- [全体設計書](architecture/system_architecture_ja.md)
- [技術選定書](architecture/technology_selection_ja.md)
- [基本設計書](architecture/basic_design_ja.md)
- [Runtime Governance仕様書](governance/runtime_governance_specification_ja.md)
- [Project Continuity Master](project_continuity/project_continuity_master_ja.md)

## Active Phase

- [Phase 1-ex Index](../phases/phase_1_ex/phase_index_ja.md)
- [Phase 1-ex Target Documentation Structure](../phases/phase_1_ex/architecture/target_documentation_structure_ja.md)
- [Migration Manifest](../phases/phase_1_ex/operations/source_to_target_documentation_migration_manifest.json)
- [Migration Receipt](../phases/phase_1_ex/operations/documentation_directory_migration_receipt_ja.md)
- [Migration Validation](../phases/phase_1_ex/operations/documentation_directory_migration_validation_ja.md)
- [Legacy Root Retirement Manifest](../phases/phase_1_ex/operations/documentation_legacy_root_retirement_manifest.json)
- [Legacy Root Retirement Validation](../phases/phase_1_ex/operations/documentation_legacy_root_retirement_validation_ja.md)
- [ADR-0025 Public Demo／Auto-start／Pre-release Gate](../phases/phase_1_ex/adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [Public Demo／Auto-start／Pre-release Requirements](../phases/phase_1_ex/requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Public Demo／Auto-start／RAG Extension Architecture](../phases/phase_1_ex/architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [Pre-initial Commit Documentation Refresh Plan](../phases/phase_1_ex/operations/pre_initial_commit_documentation_refresh_plan_ja.md)

## Completed Phase

- [Phase 1 Index](../phases/phase_1/phase_index_ja.md)
- [Phase 1 ADR](../phases/phase_1/adr/phase_1_adr_ja.md)
- [Phase 1 Architecture](../phases/phase_1/architecture/phase_1_architecture_ja.md)
- [Phase 1 Governance](../phases/phase_1/governance/phase_1_governance_ja.md)
- [Phase 1 Requirements](../phases/phase_1/requirements/phase_1_requirements_ja.md)
- [Phase 1 Operations](../phases/phase_1/operations/phase_1_operations_ja.md)
- [Phase 1 Handoffs／Reviews／Status](../phases/phase_1/handoffs/phase_1_handoffs_ja.md)
- [Phase 1 User Manual](../phases/phase_1/user_manual/phase_1_user_manual_ja.md)
- [Phase 1 Index History Compilation](../phases/phase_1/index/phase_1_documentation_index_ja.md)

## Shared

- [Documentation Rules](../shared/conventions/documentation_rules_ja.md)
- [Documentation Structure／Task Operations](../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Role／Write Authority](../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Design Governance Handoff](../shared/design_governance_handoff/design_governance_handoff_ja.md)

Sharedには`schemas/`、`templates/`および対応Historyの正式な配置先を予約している。Artifactが未作成のDirectoryへDummy文書は作らない。

## Public

- [Public Roadmap](../../public/roadmap_ja.md)
- [Phase 1 Roadmap History](../../public/history/roadmap/roadmap_phase_1_ja.md)

PublicのOverview／ConceptはPhase 1-exのCanonical／Public作成工程で作成する。対応History Rootは`docs/public/history/overview/`および`docs/public/history/concept/`である。

## Stable History

- Current Stable Index変更前後原文：`docs/project/current/history/index/`
- Current Canonical変更前後原文：`docs/project/current/history/<category>/`
- Shared Stable変更前後原文：`docs/project/shared/history/<category>/`
- Public Stable変更前後原文：`docs/public/history/<category>/`

Stable HistoryとActive PhaseのAppend-only Documentation Index Snapshotは別Artifactであり、両方を保持する。

## Reading Rule

通常はCurrentとPhase Indexを読む。Raw HistoryはSource確認、監査、矛盾追跡または明示指定時だけ参照する。
