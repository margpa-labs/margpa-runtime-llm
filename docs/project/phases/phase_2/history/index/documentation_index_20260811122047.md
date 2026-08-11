# Phase 2 Documentation Index Snapshot — 20260811122047

```yaml
document_id: phase_2_documentation_index_snapshot_20260811122047
status: recorded_paused_pending_review
phase: phase_2
subphase: phase_2_0
created_at: 2026-08-11 12:20:47 JST
language: ja
owner_role: プロジェクト責任者兼設計統括者役
upstream_role: user
intended_readers:
  - user
  - プロジェクト責任者兼設計統括者役
  - Phase 2設計担当者役候補
work_unit: P2-0 design correction before P2-0-WU-002
control_state: PAUSED
history_policy: append_only
```

## 1. Event

Role／Docs Authority再設計後の自己Reviewとユーザー訂正を受け、Automationを判断の機械化ではなく、最高責任者役が共通規則に沿って行う都度判断と、Accepted Completion Line内の連結実行へ再整理した。

## 2. New Evidence

- [Responsible-role Dynamic Judgment Correction](../operations/phase_2_0_responsible_role_dynamic_judgment_correction_20260811122047.md)

## 3. Updated Stable Documents

- [Phase 2 Index](../../phase_index_ja.md)
- [Phase 2-0 Requirements](../../requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Phase 2-0 Architecture](../../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Authorization Envelope draft-4](../../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Phase Designer Role View draft-2](../../governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Bootstrap Handoff draft-4](../../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Execution Plan](../../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Role Authority Matrix](../../../../shared/task_roles/role_authority_matrix_ja.md)
- [Documentation Structure／Task Operations](../../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Automation Governance Index](../../../../shared/automation/automation_governance_index_ja.md)
- [Automation Control Profile](../../../../shared/automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../../../../shared/automation/automation_governance_evidence_log_ja.md)
- [Pre-pilot Governance Baseline](../../../../shared/automation/pre_pilot_governance_baseline_ja.md)
- [Constitution Research Index](../../../../shared/constitution/constitution_research_index_ja.md)
- [Constitution Source Evidence Register](../../../../shared/constitution/constitution_source_evidence_register_ja.md)

## 4. Before／After Snapshot Set

`20260811122047`のBefore／After Snapshotを、Phase 2のArchitecture／Governance／Handoff／Index／Operations／Requirementsと、SharedのTask Roles／Operations／Automation／Constitutionへ各16件、計32件保存した。既存Historyは変更していない。

## 5. Corrected Contracts

- 最上位規則群と共通Docs／運用規則は、通常運転とAutomationで原則維持する。
- その時点の最高責任者役が、許可範囲内で必要なRole、Docs、Evidence、Handoff、Review、Test、Hard-code回避手段および停止地点を都度判断する。
- Automationは判断を固定Resolverへ置き換えず、Accepted Completion Line内の`ROLE_ALLOWED` Actionを追加確認なしに連結する。
- Human-only事項だけを人間へ返す。
- General Hard-code ProhibitionのNormative本文はTask Role／Write Authority Policyへ集約する。
- From／Toは伝達責任があるArtifactへ付け、Index、Requirements／Designおよび単一Role内Evidenceは各責務に応じたMetadataを持つ。
- 旧EvidenceはAppend-onlyで保持し、後続Eventで意味を訂正する。

## 6. Current State

```text
Automation        : PAUSED
Envelope draft-4  : NOT ACCEPTED
Role View draft-2 : NOT ACCEPTED
New Task          : NOT CREATED
Pilot Restart     : NOT STARTED
Git／External     : NONE
```

本SnapshotはPilot Start Event、Task作成Authority、Envelope AcceptanceまたはGit／External Mutationを生成しない。
