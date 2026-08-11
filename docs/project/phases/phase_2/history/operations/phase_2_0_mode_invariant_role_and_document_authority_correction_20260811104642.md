# Phase 2-0 Mode-invariant Role／Document Authority Correction

```yaml
document_id: phase_2_0_mode_invariant_role_and_document_authority_correction_20260811104642
event_type: design_correction_evidence
created_at: 2026-08-11 10:46:42 JST
from_role: user
to_role: project_controller_and_design_governor
logical_author: project_controller_and_design_governor
pilot_restarted: false
task_created: false
git_mutation: false
external_mutation: false
```

## 1. User Correction

ユーザーは、Role別の実行権限とDocs権限は、通常運転とAutomationで変わらないと訂正した。Automationは、最上位規則を除き、ユーザーが指定した到達線まで、各Roleが与えられた範囲内を自律的に完了させる状態である。

通常運転とAutomationで同じ作業、Role権限、Docs権限およびTask Artifact規則を二重化してはならない。

## 2. Prior Design Defect

直前の設計は、次をAutomation固有契約として過剰に分離しかけていた。

- Role別実行権限。
- DocsのRead／Stable Write／Append／Review／Deny。
- Task間HandoffとStatus。
- Roleごとの文書作成範囲。

これは本来共通契約である内容をMode別Ruleへ増殖させる。結果として、Docs量、Storage、AI利用可能量、時間、Review CostおよびContext量を増加させ、AI自身が参照規則を混線するRiskを高める。

「本来必要なRuleを定義すること」と「同じRuleをMode別に重複させること」は別である。

## 3. Corrected Authority Model

```text
Common Role Authority
  = Supreme Rulesに適合
  ∩ Role Authority Ceiling
  ∩ Assigned Role／Work Unit Scope

Effective Execution Authority
  = Common Role Authority
  ∩ Current Authorization Instance
  ∩ Provider Capability
```

Current Authorization InstanceだけがModeによって異なる。

- 通常運転：現在のユーザー明示指示。ユーザーはPhase設計へ要件を追加または変更できる。
- Automation：ユーザー承認済み到達線と、その内側でProject Controllerが発行するWork Unit指示。

Automation側には、承認済み到達線、連結実行、Control State、継続上限および停止条件だけを差分として保持する。

## 4. Common Document Contract

- 既存Stable文書への直書きは、Modeを問わず、ユーザーがExact TargetとActionを明示した場合だけ許可する。
- 上位Roleの指示、Automation Envelope、Meaning OwnershipまたはRole兼務だけでは既存Stableへの直書き権限を生成しない。
- 既存HistoryはImmutableとし、新規EventだけをAppendする。
- 作業、担当、RoleまたはTaskごとに、既存Artifactを使い回さず、新規Index、Inbound Handoff、Outbound Statusおよび必要なReview／Acceptance Eventを作成する。
- 全Role間Handoff、Status、Review、RequestおよびAcknowledgementに`from_role`と`to_role`を必須とする。
- Read-only Roleの記録を別Roleが代行する場合も、論理的著者とFrom／Toを保持する。

## 5. Phase Role Behavior

Phase Designerは、Automation中はユーザー承認済み到達線の内側で上位RoleのWork Unit指示に従う。通常運転中は、ユーザーが追加または変更した要件を取り込み、Cross-Phase影響をProject Controller／Design GovernorへEscalateする。

Context、安全性または実装規模上の必要がある場合は、Phase別Implementerを新規配置できる。これもMode別権限ではなく、共通Role契約へProject固有Bindingを与える処理である。

## 6. Cost／Complexity Control Principle

新規Ruleまたは新規Docsを追加する前に、既存の共通正本へ差分として表現できるかを確認する。

```text
必要な独立概念
  → 新規Rule／Document候補

既存概念と同一でMode／Provider／Projectだけが違う
  → 共通正本＋Overlay／Binding／Adapter
```

抽象化によって安全要件を失わない一方、同義Ruleの複製による文書量と認知負荷の増殖を防ぐ。

## 7. State Preservation

本修正中にPilot、Task作成、Task名変更、File実装、Permission変更、Git Mutation、External ActionまたはProvider操作は行っていない。

```text
Control State      : PAUSED／ROLE_AUTHORITY_DESIGN
Automation Level   : bounded_unit design candidate
Envelope           : draft-4 not accepted
Role View          : draft-2／reprojection pending
New Task           : not created
Pilot Restart      : not performed
```

## 8. Corrected Stable Sources

- [Role Authority Matrix](../../../../shared/task_roles/role_authority_matrix_ja.md)
- [Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Documentation Structure／Task Operations](../../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Automation Control Profile](../../../../shared/automation/automation_control_profile_ja.md)
- [Automation Governance Index](../../../../shared/automation/automation_governance_index_ja.md)
- [Automation／Governance Evidence Log](../../../../shared/automation/automation_governance_evidence_log_ja.md)
- [Phase 2 Index](../../phase_index_ja.md)
