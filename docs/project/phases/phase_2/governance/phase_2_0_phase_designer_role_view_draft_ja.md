# Phase 2-0 Phase Designer Role View Draft

```yaml
document_id: phase_2_0_phase_designer_role_view_draft
role_view_id: p2-0-role-view-phase-designer-001
revision: draft-2
status: draft_not_authorized
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-002
role_archetype: phase_designer
role_name: Phase 2設計担当者役
automation_level: bounded_unit
language: ja
created_at: 2026-08-11 01:09:24 JST
updated_at: 2026-08-11 21:05:03 JST
decision_authority: user
```

## 1. Purpose

本Role Viewは、Phase 2設計担当者役の一般的なRole上限から、`P2-0-WU-002` Bounded Read Cold Recovery Retestで実際に有効化する権限だけを抽出する。

本Work UnitのRead-onlyは、通常運転とAutomationでRole権限が異なることを意味しない。共通Phase Designer権限を、今回のRead-only Recovery Scopeへ狭めた結果である。

## 2. Authority Source

```text
Human-defined Supreme Rules
  > Accepted Envelope p2-0-envelope-001
  > Common Role／Docs Authority Matrix／phase_designer
  > This Role View
  > Bounded Read Manifest
  > Provider Adapter
```

通常運用のActionごとの確認、Shell全面禁止、Git／Backup Gateまたはその他の下位Defaultを、本Role Viewの範囲へ再適用しない。

## 3. Autonomous Actions

Control State `ON`後、対象Taskは次をActionごとの再確認なしで自律実行できる。

```yaml
allowed_actions:
  - acknowledge_authority_contract
  - read_exact_manifest_entries
  - measure_line_count_for_exact_entry
  - verify_sha512_for_exact_entry
  - read_complete_text_in_bounded_pages
  - compare_recovered_authority_and_state
  - produce_recovery_assessment
  - produce_mutation_report
  - stop_and_report_on_contract_failure
```

Local Commandは「Shell一般」ではなく、Accepted Provider Adapterに列挙されたBounded Read Capabilityとして許可する。Taskは各回ユーザーへ再確認せず、Manifest完読またはStop Conditionまで連結する。

Phase Designerは最高責任者役の単なる逐次確認窓口ではない。本Work UnitではRead-only Scopeに限定されるが、その内側のReading順守、Evidence整理、Recovery Assessment、矛盾検出、停止判断および完了報告を都度自律判断する。後続Work Unitで実装担当への伝達や局所Reviewが委譲された場合も、Accepted DesignとAssigned Phaseの範囲内ではRoutine Actionごとに最高責任者役へ確認しない。

## 4. Authorized Scope

```yaml
authorized_root: controller_resolved_project_root
allowed_paths: p2-0-read-manifest-001_exact_entries_only
write_scope: none
document_projection:
  source: common_role_authority_matrix
  common_state: READ
  readable: p2-0-read-manifest-001_exact_entries_only
  narrower_work_unit_constraint: all_document_mutation_denied
git_scope: none
external_scope: none
secret_scope: none
destructive_scope: none
task_creation_scope: none
subagent_scope: none
```

Project Root外、Manifest外、Directory探索、Symlink追跡または実行時のScope追加は許可しない。

本Work UnitのChild Docs Authorityは共通Matrixの`READ`だけである。既存Stableへの直書き権限はなく、Role-owned HistoryへのAppendもChildには有効化しない。TaskはRecovery AssessmentをConversation Outputとして返す。

本Work Unitの必要Artifactは固定Packageで決めない。当該Docs Authorityを委譲されたRole／Taskが、共通Docs／運用規則、Work Unit、Role／Task境界、State Transition、Mutation Risk、Review／Human Gate、Audit／Recovery、Provider Capability、情報Loss、CostおよびContextから必要Document Classを都度判断する。最高責任者役はCross-Role対象、競合、委譲境界およびGateを調整する。

ChildをRead-onlyに保つため、本Role ViewではPhase Designer自身のDocs Mutationを有効化しない。会話上のAssessmentを受け取ったControllerが、自身へ委譲されたDocs Authorityの範囲で必要性、許可ClassおよびExact Pathを判断して作成・記録する。Role／Task間の移転Artifactには論理的著者と`from_role／to_role`を保持する。判断結果とExact Pathが未確定の間、本Role ViewをAccepted化しない。

## 5. Human Gates

本Work Unit開始前に必要なHuman Gateは次だけである。

1. Exact Envelope、Role View、Manifest、HandoffおよびTask作成1件のAcceptance。
2. ControllerのREADY／ARMED宣言。
3. その後のUser Start宣言。

Start後、上記のAutonomous ActionsごとにHuman Gateを追加しない。Human-private Recovery Asset、Gitまたは通常運用Checkpointは本Work UnitのGateではない。

最高責任者役への相談またはReview依頼は、Manifest／Authority／規則のConflict、Scope外Action、重大な安全・復旧問題、Provider／Resource異常、完了条件不成立または本書で定義したACK／Completion／Review Gateに限定する。Routineな読取・比較・整理・報告を逐次Escalateしない。

## 6. Prohibited Actions

- 最上位規則の追加、変更、削除、並替え、例外化または候補登録。
- File／Directory／Permission／ACL／MetadataのMutation。
- Manifest外Read、Directory List／Search、GlobまたはSymlink追跡。
- Provider Adapter外CommandまたはTool。
- Git、Network、Browser、Connector、External ServiceまたはSecret Access。
- Task／Sub-agent／Process／Automationの追加作成。
- Docs更新、Phase 2-A開始、権限拡張または未列挙Actionの代替実行。
- Incident後のCleanup／Rollback／Delete／Evidence整合化。

## 7. Completion Contract

```yaml
completion:
  read_coverage: all_manifest_entries
  digest_match: all_manifest_entries
  page_coverage: complete
  recovery_assessment: required
  mutation_report: required
  file_mutation: none
  git_mutation: none
  external_mutation: none
```

Manifest全件の完読前にContext、QuotaまたはTool Failureが発生した場合は、未確認を推測で埋めず`PAUSED`とする。

本Role Viewの完了報告はControllerへ返す。Controllerは独立ReviewとTask完了判定案を作り、User Acceptanceなしに次Work Unitへ移行しない。後続Write Pilotでは、Implementerの完了報告をPhase Designerが局所Reviewし、必要なら再作業を指示した後にControllerへ完了報告する。

## 8. Current State

```text
Role View        : draft-2／design review passed／user acceptance pending
Envelope         : draft-4／not accepted
Control State    : PAUSED／ROLE_AUTHORITY_DESIGN
Task             : not created for P2-0-WU-002
Autonomous Read  : not started
Documentation    : delegated role-local judgment projected／Child write none／Controller exact targets frozen in current candidate
```

## 9. Related Documents

- [Role Authority Matrix](../../../shared/task_roles/role_authority_matrix_ja.md)
- [Authorization Envelope](phase_2_0_authorization_envelope_draft_ja.md)
- [Bounded Read Manifest](phase_2_0_bounded_read_manifest_draft_ja.md)
- [Automation Control Profile](../../../shared/automation/automation_control_profile_ja.md)
- [Provider Adapter](../../../shared/automation/provider_adapters/codex_desktop_bounded_read_adapter_ja.md)
