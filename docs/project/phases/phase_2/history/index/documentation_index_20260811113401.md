# Phase 2 Documentation Index Snapshot — 20260811113401

```yaml
document_id: phase_2_documentation_index_snapshot_20260811113401
status: append_only_snapshot
phase: phase_2
subphase: phase_2_0
created_at: 2026-08-11 11:34:01 JST
owner: プロジェクト責任者兼設計統括者役
trigger: dynamic_documentation_and_general_hardcode_rule_revision
```

## 1. Current State

```text
Control State       : PAUSED／ROLE_AUTHORITY_DESIGN
Automation Level    : bounded_unit draft
Role Matrix         : design candidate／dynamic resolver projected／review pending
Role View           : draft-2／reprojected／not accepted
Envelope            : draft-4／not accepted
New Task            : not created
Pilot Restart       : not started
Functional Phase 2  : not started
Git／External        : no mutation in this transaction
```

## 2. Revision Purpose

- 固定Work Unit Documentation PackageをDynamic Documentation Requirement Resolverへ置換した。
- 人間の明示指示によりGeneral Hard-code Prohibitionを最上位規則群へ追加した。
- 前回のTransaction記録から漏れたPhase 2現行Draft 6文書を完全なSnapshot／Index対象へ復帰させた。
- Phase IndexのRole View再投影待ちという古い状態を補正した。

## 3. Current／Stable Sources

### Shared

- `docs/project/shared/task_roles/role_authority_matrix_ja.md`
- `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
- `docs/project/shared/operations/documentation_structure_and_task_operations_ja.md`
- `docs/project/shared/automation/automation_control_profile_ja.md`
- `docs/project/shared/automation/automation_governance_index_ja.md`
- `docs/project/shared/automation/automation_governance_evidence_log_ja.md`
- `docs/project/shared/automation/pre_pilot_governance_baseline_ja.md`
- `docs/project/shared/constitution/constitution_research_index_ja.md`
- `docs/project/shared/constitution/constitution_source_evidence_register_ja.md`

### Phase 2

- `docs/project/phases/phase_2/phase_index_ja.md`
- `docs/project/phases/phase_2/requirements/phase_2_0_automation_pilot_requirements_ja.md`
- `docs/project/phases/phase_2/architecture/phase_2_0_automation_pilot_architecture_ja.md`
- `docs/project/phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md`
- `docs/project/phases/phase_2/governance/phase_2_0_phase_designer_role_view_draft_ja.md`
- `docs/project/phases/phase_2/handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md`
- `docs/project/phases/phase_2/operations/phase_2_0_automation_pilot_execution_plan_ja.md`

## 4. Evidence

- [Dynamic Documentation Resolution／General Hard-code Rule Evidence](../operations/phase_2_0_dynamic_documentation_resolution_and_general_hardcode_rule_20260811113401.md)
- [Previous Mode-invariant Role／Document Authority Correction](../operations/phase_2_0_mode_invariant_role_and_document_authority_correction_20260811104642.md)
- [Previous Documentation Index Snapshot](documentation_index_20260811104642.md)

## 5. Snapshot Families

各Sourceには、対応するHistory Class内に次の完全Snapshotが存在する。

```text
*_before_dynamic_documentation_and_general_hardcode_rule_*_20260811113401.md
*_after_dynamic_documentation_and_general_hardcode_rule_*_20260811113401.md
```

Phase 2現行Draft 6文書については、`20260811013723`の`after_document_authority_matrix`、今回のBefore、今回のAfterを用いて、前回修正前、前回修正後／今回修正前、今回修正後をLosslessに再構築できる。

## 6. Next Gate

1. Dynamic Resolverの必要Artifact判定をReviewする。
2. General Hard-code Prohibitionの共通Core／Phase 2投影をReviewする。
3. P2-0-WU-002用Resolver結果、Artifact ClassおよびExact PathをFreezeする。
4. draft-4／Role View／Manifest／Adapter／Handoff／Freeze Receiptを再照合する。
5. ユーザーAcceptance前はTaskを作成せず、`PAUSED`を維持する。
