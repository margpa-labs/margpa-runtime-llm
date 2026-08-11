# Phase 2-0 Phase Designer Bootstrap Handoff Draft

```yaml
document_id: phase_2_0_phase_designer_bootstrap_handoff_draft
status: draft_not_authorized
normative: false
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-09 21:05:03 JST
owner: プロジェクト責任者兼設計統括者役
target_role: Phase 2設計担当者役
target_work_unit: P2-0-WU-001
authorization_envelope: p2-0-envelope-001
authorization_envelope_revision: draft-2
task_created: false
```

## 1. Draft Boundary

本書は、Phase 2-0 Automation Pilotで将来作成する可能性がある独立Taskへ渡すBootstrap HandoffのDraftである。本書の存在は、Task作成、Task命名、Prompt送信、File変更、Git操作またはPhase 2-A開始を許可しない。

開始には、次を順序どおり満たす必要がある。

1. Design Package Review合格。
2. Read-only Provider Capability Preflight合格。
3. Exact Manifest、Envelope Revision、Handoff Revision／DigestおよびReading OrderのFreeze。
4. ユーザー承認済みGit Commit／PushとLocal／Remote一致確認。
5. ユーザーによる大規模Backup取得完了の明示報告。
6. ユーザーが[Authorization Envelope Draft](../governance/phase_2_0_authorization_envelope_draft_ja.md)のExact Revisionと1件のChild Task作成を明示的にAccepted化する。
7. 現在Task`プロジェクト責任者兼設計統括者役`が「準備OK。いつでも開始出来ます。」と明示し、Control Stateを`ARMED`とする。
8. その後ユーザーが「ok。では開始する。」と明示し、Control Stateを`ON`とする。

## 2. Proposed Role

```text
Child Role Name: Phase 2設計担当者役
Work Unit      : P2-0-WU-001 Docs-only Recovery and Authority Acknowledgement
Mode           : read-only recovery assessment
Task Count     : exactly one
Write Authority: none
```

本Work Unitの目的は、旧Taskの会話を渡さず、正本DocsだけからPhase、Role、Authority、禁止事項、Open Gateおよび次の安全なActionを復元できるかを検証することである。Phase 2機能設計、実装、Docs編集またはTask間自動連鎖は行わない。

## 3. Required Reading Order

1. `docs/project/current/documentation_index_ja.md`
2. `docs/project/current/project_continuity/project_continuity_master_ja.md`
3. `docs/project/shared/project_responsibility_handoff/project_responsibility_handoff_ja.md`
4. `docs/project/shared/history/project_responsibility_handoff/project_responsibility_recovery_manifest_20260804061104.md`
5. `docs/project/shared/design_governance_handoff/design_governance_handoff_ja.md`
6. `docs/project/shared/history/design_governance_handoff/design_governance_recovery_manifest_20260804061104.md`
7. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
8. `docs/project/shared/operations/research_asset_mutation_control_ja.md`
9. `docs/project/shared/operations/experimental_document_driven_codex_task_orchestration_ja.md`
10. `docs/project/shared/automation/automation_governance_index_ja.md`
11. `docs/project/shared/automation/automation_control_profile_ja.md`
12. `docs/project/shared/automation/automation_governance_evidence_log_ja.md`
13. `docs/project/shared/automation/pre_pilot_governance_baseline_ja.md`
14. `docs/project/phases/phase_2/phase_index_ja.md`
15. `docs/project/phases/phase_2/requirements/phase_2_0_automation_pilot_requirements_ja.md`
16. `docs/project/phases/phase_2/architecture/phase_2_0_automation_pilot_architecture_ja.md`
17. `docs/project/phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md`
18. `docs/project/phases/phase_2/operations/phase_2_0_automation_pilot_execution_plan_ja.md`

読取不能、Link不成立、Current State矛盾または複数正本競合を検出した場合は推測で補わず停止する。

## 4. Proposed Authority Acknowledgement

Taskは作業開始前に、次を明示して返す。

```text
ACK_STATUS
Role
Work Unit
Current Phase／Subphase
Read Scope
Write Scope = NONE
Git／External／Secret／Destructive Authority = NONE
Task／Sub-agent Creation Authority = NONE
User Gates
Stop Conditions
Current State Summary
Open Questions／Contradictions
```

単なる「了解」では受領成立としない。Authority AcknowledgementがHandoffと一致しない場合は、Follow-upで作業を拡張せず、Pilotを`ADJUST`または`STOP`候補とする。

## 5. Expected Output

TaskはFileを作成・変更せず、会話上の一つの構造化Reportだけを返す。

```text
RECOVERY_ASSESSMENT
Recovery Result: PASS／FAIL／AMBIGUOUS
Recovered Project Objective
Recovered Current State
Recovered Role Separation
Recovered Absolute Prohibitions
Recovered User Gates
Recovered Phase 2-0 Boundary
First Safe Next Action
Evidence Paths
Conflicts／Missing Information
Estimated Context／Cost Observation
```

Project固有のSecret、個人情報、Absolute Local Pathまたは不要な環境識別子を出力しない。

## 6. Absolute Prohibitions for This Work Unit

- File／Directoryを作成、変更、移動、削除またはPermission変更しない。
- Git、GitHub、Commit、Push、Branch、Tag、Releaseを操作しない。
- External Service、Browser、Network、Secret、Credentialまたは課金対象へ触れない。
- 新TaskまたはSub-agentを作成しない。
- Phase 2-A以降を開始しない。
- 「良かれ」、推測、会話の流れまたはRole名をAuthorityとして扱わない。
- 不明点を既知として補完しない。
- 未完了、未確認または不成立を`PASS`／`Complete`と表記しない。
- 明示されたAuthorized Root／Allowed Path外をRead、List、Search、StatまたはSymlink経由で参照しない。
- Codex／Claude Code等のProvider差を理由に、Core Rule、Authority、EvidenceまたはStopを弱めない。

## 7. Stop Conditions

次のいずれかで即時停止する。

- Accepted Envelopeまたは明示的Task作成指示を確認できない。
- Required Readingの一つでも読めない。
- Current／Shared／Phase間でAuthorityまたはCurrent Stateが衝突する。
- Read-only範囲では評価できないMutationが必要になる。
- Context、利用可能量、CreditまたはTool Capabilityが不足する。
- Absolute Prohibition違反またはその疑いがある。

停止時は、確認済み範囲、未確認範囲、停止理由および必要なUser Decisionだけを返す。自動修復、追加探索またはAuthority拡張を行わない。

## 8. Review Gate

設計統括者役はReportを、正確性、Docs-only Recovery、Authority一致、推測抑制、Evidence完全性、Costおよび再現可能性でReviewする。結果は`GO／ADJUST／STOP`のいずれかとし、ユーザー判断なしに次Work UnitまたはPhase 2-Aへ進めない。

## 9. Draft State

```text
Handoff Draft        : complete
Envelope Revision    : draft-2
Envelope Accepted    : no
Capability Preflight : passed／recheck before task creation
Git Checkpoint       : pending this authorized transaction
Remote Alignment     : pending
Large Backup         : not confirmed
Controller Ready     : no
User Start           : no
Task Creation Request: no
Task Created         : no
Prompt Sent          : no
Pilot Executed       : no
Current Stop         : gate reconciliation／checkpoint pending
```

Provider Capability Preflightでは、Task作成、Task名設定、初回Handoff、Follow-up、状態取得およびWaitを`available`、Interruptを`manual_required`、Pin／Archiveを`available but optional`として確認した。Task作成前にTool契約が変わった場合は本結果を失効させ、Read-only Preflightから再開する。
