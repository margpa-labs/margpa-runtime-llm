# Phase 2-0 Role Authority Matrix Redesign Evidence

```yaml
document_id: phase_2_0_role_authority_matrix_redesign_20260811010924
status: append_only_design_evidence
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-002
created_at: 2026-08-11 01:09:24 JST
owner: プロジェクト責任者兼設計統括者役
pilot_started: false
task_created: false
git_mutation: none
external_mutation: none
```

## 1. Finding

既存設計には、Task Role／Write Authority PolicyとAutomation Control Profileが存在した。しかし、Roleに与え得る上限と、Accepted Envelopeで今回有効化されたScopeを結合し、どのActionを自律実行できるか判定する正式な権限表が存在しなかった。

この欠落により、有界Automation Pilotでも通常運用のActionごとの確認、Shell全面禁止および下位Gateが流入し、承認済みWork Unitの実行に必要なRead Capabilityを有効化できなかった。

## 2. Corrected Model

```text
Human-defined Supreme Rules
  > Accepted Automation Envelope
  > Role Authority Matrix
  > Work Unit Role View
  > Provider Adapter
  > Ordinary Operational Defaults
```

- 最上位規則はAI SideのどのRoleも超えられない。
- Role Authority MatrixはRoleに与え得る上限を定義する。
- Accepted Envelopeは今回のScopeとActionを有効化する。
- Role Viewは対象Taskへ渡す交差を固定する。
- Control State `ON`中、交差内の`AUTO` Actionは再確認なしで自律実行する。
- Envelope外、Role外、Root／Path外、`HUMAN_GATE`および`DENY`は停止境界である。

## 3. Created／Updated Design

- `docs/project/shared/task_roles/role_authority_matrix_ja.md`
- `docs/project/phases/phase_2/governance/phase_2_0_phase_designer_role_view_draft_ja.md`
- Authorization Envelope `draft-4`
- Bounded Read Manifest `draft-2`
- Bootstrap Handoff `draft-4`
- Requirements／Architecture／Execution Plan／Phase Index／Automation Stable Docs

Normative CoreはProject、Provider、Absolute Path、PhaseまたはTask名をHard-codeせず、Project固有値をEnvelope、ManifestおよびRole Viewへ分離した。

## 4. P2-0-WU-002 Binding

Phase 2設計担当者役は`phase_designer`にBindingする。本Work Unitで自律実行できるのは、Exact ManifestのRead、Line Count、SHA-512検証、欠落のないPage Read、Recovery Assessment、Mutation ReportおよびStop Reportである。

File Mutation、Git、External、Secret、Destructive、Task／Sub-agent追加、Manifest外ReadおよびPhase 2-A移行は本Work Unitに含めない。これらは通常運用由来の禁止ではなく、今回のAccepted候補Scope自体の境界である。

## 5. Validation

```text
Local Link Check      : PASS
Markdown Fence Check : PASS
git diff --check     : PASS for reviewed files
Task Creation         : 0
Old Task Action       : 0
Pilot Restart         : no
Control State         : PAUSED／ROLE_AUTHORITY_DESIGN
```

## 6. Remaining Human Decision

Role Authority Matrix、Role View、Envelope draft-4および後続Freeze ReceiptのAcceptanceはユーザーDecision Authorityである。本Design Evidenceの作成だけでTask作成、Control State `ON`またはPilot再開を成立させない。

## 7. Related Documents

- [Role Authority Matrix](../../../../shared/task_roles/role_authority_matrix_ja.md)
- [Phase Designer Role View](../../governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Authorization Envelope draft-4](../../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Bounded Read Manifest draft-2](../../governance/phase_2_0_bounded_read_manifest_draft_ja.md)
- [Execution Plan](../../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
