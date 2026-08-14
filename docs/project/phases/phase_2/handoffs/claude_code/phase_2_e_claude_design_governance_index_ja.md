# Phase 2-E Claude Code Design Governance Index

```yaml
document_id: phase_2_e_claude_design_governance_index
status: active_bootstrap_index
phase: phase_2
subphase: phase_2_e
provider: claude_code
language: ja
created_at: 2026-08-14 JST
from_role: Codexプロジェクト責任者兼設計統括者役
to_role: Claude設計統括者役
git_baseline: f923b1989d63e0df428b730a6024b9be07993d51
stable_document_mutation: prohibited
history_operation: append_only
```

## 1. Purpose

本書は、Claude CodeがPhase 2-Eを再開・設計・実装・Reviewし、`COMPLETE_CANDIDATE`まで進めるための最小入口である。長い会話文をAuthorityまたはRecovery Sourceにせず、本書と次のHandoffをRepository内のProvider Bootstrap Packageとして使用する。

最初に次を全文読了する。

1. [Phase 2-E Claude Design Governance Handoff](phase_2_e_claude_design_governance_handoff_ja.md)
2. 本書第2節のRequired Readingを記載順に読む。
3. 読了後、Source／Test／Configの現状は`rg`等によってProject Root内から動的に解決する。固定Package名や過去会話の推測だけで対象を決めない。

## 2. Required Reading Order

### 2.1 Current Phase State

1. `docs/project/phases/phase_2/phase_index_ja.md`
2. `docs/project/phases/phase_2/history/operations/phase_2_e_persistent_rag_citation_evidence_reservation_20260814215110.md`
3. `docs/project/phases/phase_2/history/operations/phase_2_a_to_d_user_manual_acceptance_20260814210500.md`
4. `docs/project/phases/phase_2/history/operations/phase_2_b_to_d_manual_acceptance_rework_20260814205814.md`
5. `docs/project/shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md`
6. `docs/public/roadmap_ja.md`

Phase 2の現在地は上記1～6を優先する。後続のCurrent Canonical Docsに古い進捗表現が残る場合、Phase 2の進捗判定だけは上記に従い、古い記述を理由にPhase 2-A～2-Dを再Openしない。

### 2.2 Authority／Documentation／Automation

7. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
8. `docs/project/shared/task_roles/role_authority_matrix_ja.md`
9. `docs/project/shared/operations/research_asset_mutation_control_ja.md`
10. `docs/project/shared/operations/documentation_structure_and_task_operations_ja.md`
11. `docs/project/shared/conventions/documentation_rules_ja.md`
12. `docs/project/shared/operations/transition_blocker_escalation_and_closure_contract_ja.md`
13. `docs/project/shared/automation/automation_governance_index_ja.md`
14. `docs/project/shared/automation/automation_control_profile_ja.md`

### 2.3 Current Canonical Architecture

15. `docs/project/current/project_continuity/project_continuity_master_ja.md`
16. `docs/project/current/architecture/basic_design_ja.md`
17. `docs/project/current/architecture/system_architecture_ja.md`
18. `docs/project/current/governance/runtime_governance_specification_ja.md`

### 2.4 Phase 2 Predecessor Contracts

19. `docs/project/phases/phase_2/architecture/phase_2_a_conversation_domain_architecture_ja.md`
20. `docs/project/phases/phase_2/adr/phase_2_a_conversation_domain_adr_ja.md`
21. `docs/project/phases/phase_2/architecture/phase_2_b_conversation_persistence_architecture_ja.md`
22. `docs/project/phases/phase_2/adr/phase_2_b_conversation_persistence_adr_ja.md`
23. `docs/project/phases/phase_2/handoffs/phase_2_b_implementation_handoff_ja.md`
24. `docs/project/phases/phase_2/architecture/phase_2_c_persistent_conversation_api_ux_architecture_ja.md`
25. `docs/project/phases/phase_2/adr/phase_2_c_persistent_conversation_api_ux_adr_ja.md`
26. `docs/project/phases/phase_2/handoffs/phase_2_c_implementation_handoff_ja.md`
27. `docs/project/phases/phase_2/architecture/phase_2_d_configuration_control_architecture_ja.md`
28. `docs/project/phases/phase_2/adr/phase_2_d_configuration_control_adr_ja.md`
29. `docs/project/phases/phase_2/handoffs/phase_2_d_implementation_handoff_ja.md`

Raw Historyは最初から全件読まない。上記文書が参照するEvidence、矛盾解決、Source Freeze確認、ReviewまたはRecoveryに必要な範囲だけ追加で読む。

## 3. Startup Integrity Gate

Expected Git Baseline：

```text
f923b1989d63e0df428b730a6024b9be07993d51
```

Claude Code開始時に許容されるBaseline後のBootstrap差分は、次の新規2文書だけである。

```text
docs/project/phases/phase_2/handoffs/claude_code/phase_2_e_claude_design_governance_index_ja.md
docs/project/phases/phase_2/handoffs/claude_code/phase_2_e_claude_design_governance_handoff_ja.md
```

これ以外の予定外差分、Baseline不一致、Merge Conflict、Project Root不一致または既存Stable文書の変更を開始時に検出した場合、削除、復元、Reset、Checkout、Stashまたは帳尻合わせを行わず停止する。

## 4. Provider-independent Continuity

本Index／Handoff方式はClaude Code固有のPromptへ統治内容を埋め込むためのものではない。Providerごとに短いBootstrap入口を置き、共通Canonical／Shared Ruleを参照し、Provider側の成果をAppend-only Evidenceとして返す方式である。将来別Providerを追加する場合も、共通規則を複製・Hard-codeせず、Provider Adapter相当のIndex／Handoffだけを追加する。

## 5. Completion Route

```text
Claude設計統括者役
  → Claude Phase 2-E設計担当者役
  → Claude Phase 2-E実装者役
  → Claude Phase 2-E設計担当者役Review
  → Claude設計統括者役Final Review
  → COMPLETE_CANDIDATE Handoff
  → Codexプロジェクト責任者兼設計統括者役Review
  → ユーザーMac手動Acceptance
```

Claude Codeは`COMPLETE_CANDIDATE`またはHandoffで定義したCurrent Transition Blockerに到達するまで、Routine確認のためにCodexまたはユーザーへ戻さない。
