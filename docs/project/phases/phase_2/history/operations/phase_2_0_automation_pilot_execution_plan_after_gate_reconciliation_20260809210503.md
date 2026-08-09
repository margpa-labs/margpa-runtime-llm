# Phase 2-0 Document-driven Orchestration Pilot Execution Plan

```yaml
document_id: phase_2_0_automation_pilot_execution_plan
status: design_draft_awaiting_user_authorization
phase: phase_2
subphase: phase_2_0
language: ja
created_at: 2026-08-04 11:17:44 JST
updated_at: 2026-08-09 21:05:03 JST
owner: プロジェクト責任者兼設計統括者役
technical_owner: プロジェクト責任者兼設計統括者役
execution_started: false
```

## 1. Current Gate

```text
Phase 1                 : complete_accepted
Phase 1-ex              : complete_accepted
Phase 2                 : active
Phase 2-0               : pre_activation_gate
Pilot Design Package    : gate reconciled／validation pending
Authorization Envelope  : draft_not_authorized
Independent Task        : not created
Runtime Implementation  : not started
Git Mutation             : explicitly authorized for this Docs checkpoint transaction
Other External Mutation  : not authorized
```

## 2. Execution Principle

実行は「できるだけ全自動」ではなく、最小有界のStageをEvidence付きで通し、次のStageのAuthorityを別途確定する。

```text
Design
  → Capability Preflight
  → Exact Design Freeze
  → User-authorized Git Checkpoint／Remote Alignment
  → User Large Backup
  → Exact Envelope／Task Acceptance
  → READY／ARMED
  → User Start／ON
  → One Read-only Task
  → Authority Acknowledgement
  → Docs-only Recovery Assessment
  → Review
  → GO／ADJUST／STOP
```

Automation LevelとControl Stateを分離する。初回Level候補は`bounded_unit`だが、現在のControl Stateは`OFF`である。

```text
OFF
  → Design／Validation／Human Review
ARMED
  → READY Evidence成立後、ユーザーStart宣言待ち
ON
  → Accepted Envelope内でP2-0-WU-001を実行
PAUSED
  → Resource／Review／利用可能量等で安全停止
EMERGENCY_STOP
  → Authority／Root境界違反または重大Incident。人間判断まで再開禁止
```

状態遷移はAutomation Levelを拡張せず、Level変更もControl Stateを自動遷移させない。

## 3. Stage 0 — Design Package

### Inputs

- Phase 1-ex Final Recovery／Closure Evidence。
- Project Responsibility／Design Governance。
- Shared Orchestration Preplan／Cost／Authority／Constitution Plan。
- Phase 2-0 Requirements／Architecture／Envelope Draft／Handoff Draft。

### Checks

- Phase 2開始とTask作成許可の分離。
- Role、Read／Write Scope、Stop、Human Gateの整合。
- Relative Link、State、Timestamp、History Index。
- Runtime Source変更が0であること。

### Exit

`gate_reconciled／final_validation_pending`。本Stage完了だけでStage 1を自動開始しない。

## 4. Stage 1 — Read-only Capability Preflight／Design Freeze

Taskを作成せず、利用可能なTool Contractと実行制約をRead-onlyで確認する。「以前できた」ことを現在Capabilityの代替にしない。

### Capability Matrix

| Capability | Required | Current Preflight | Failure Handling |
|---|---:|---|---|
| Independent Task Creation | yes | available | stop |
| Task Title Assignment | yes | available | stop or user-approved manual action |
| Initial Handoff Delivery | yes | available through initial prompt | stop and retain uninitialized task evidence |
| Follow-up Delivery | optional, max 1 | available | proceed without retry loop or stop |
| Status Observation／Wait | yes | available | stop if result cannot be observed |
| Interrupt | conditional | manual_required／not exposed in current contract | manual_required allowed for read-only unit |
| Pin／Archive | no | available | record only; do not execute in initial unit |

Preflight後、Exact Manifest、Envelope Revision、Handoff Revision、Reading OrderおよびExpected OutputをFreezeする。Provider契約、Project、RevisionまたはScopeが変化した場合はPreflight／Freezeを失効させる。

### Exit

`capability_preflight_passed／design_frozen`。Task作成、Task命名、Prompt送信またはControl State変更は行わない。

## 5. Stage 2 — Checkpoint／Backup／User Authorization

次を順序どおり満たした場合だけ通過する。

1. Design Package Review合格。
2. Stage 1のRead-only Capability Preflight合格とExact Design Freeze。
3. 対象差分のFinal Review／Validation。
4. ユーザーによる当該Commit／Pushの明示承認、Commit／PushおよびLocal／Remote一致確認。
5. ユーザーによる大規模Backup取得完了の明示報告。
6. `p2-0-envelope-001 draft-2`と1件のChild Task作成範囲のAccepted化。
7. 現在Task`プロジェクト責任者兼設計統括者役`による「準備OK。いつでも開始出来ます。」の明示と`ARMED`化。
8. その後のユーザーによる「ok。では開始する。」の明示と`ON`化。
9. Child Task`Phase 2設計担当者役`を1つ作成し、Read-only Work Unit `P2-0-WU-001`を実行。

例：

```text
p2-0-envelope-001 draft-2を承認。
Phase 2設計担当者役Taskを1つ作成し、P2-0-WU-001を実行してよい。
```

ユーザーの表現が曖昧、部分的または別Revisionを示す場合は推測Acceptedにしない。本Planの記載自体はCommit／Push Authorityを生成しないが、2026-08-09の本Gate Reconciliation単位については、ユーザーがDocs再設計、Roadmap更新、Validation、Commit／PushおよびRemote確認を明示承認済みである。対象外のFile、次回以降のGit操作または他External Mutationへ拡張しない。Ready宣言後にState、Profile、Authorized Root、EnvelopeまたはProvider Capabilityが変化した場合はReadyを失効させる。

第7項のREADY宣言前に、Backup、Accepted Envelope、Authorized Root／Allowed Path、最上位禁止、Stop／Recovery、Resource、最初のWork Unit、Provider Capability、Handoff Digest、Git Checkpoint／Remote一致および未解決事項をEvidence Packageとして照合する。大規模Backupはユーザー担当とし、AIはAuthorized Root外を検査しない。Backupの存在と復元可能性は区別し、確認粒度はユーザーが決定する。

## 6. Stage 3 — Task Bootstrap

```text
Verify accepted envelope revision
Verify pre-pilot backup and dual-consent start event
Verify current task role title transition if provider supports it
Verify automation level = bounded_unit
Verify authorized root and allowed paths
Verify task count = 0 new active task
Create one independent task
Assign exact task name
Deliver exact bootstrap handoff
Record provider result
Wait for acknowledgement
```

部分成功の扱い：

- Task作成成功／Title失敗：作業させず停止。
- Task作成成功／Handoff失敗：未初期化Taskとして停止。
- 応答未取得：無制限に再試行せず停止。
- 別Task作成による自動代替：禁止。

## 7. Stage 4 — Authority Acknowledgement Gate

AcknowledgementをRequirementsの必須Fieldと照合する。

### Pass

- Role／Phase／Work Unit一致。
- Write Scope `none`。
- Prohibited ActionとHuman Gateを解決。
- Handoff Digest一致。
- Open QuestionがScope内で回答可能。

### Fail

- Authorityを広く解釈。
- Source／Git／ExternalへのActionを予定。
- Phase 2-Aまたは実装開始を含める。
- Handoffを読んだ「つもり」だけで構造化回答がない。

Fail時は最大1回のClarification Follow-up候補をReviewする。権限逸脱の疑いがある場合はFollow-upで継続せずSTOPにする。

## 8. Stage 5 — Read-only Recovery Assessment

TaskはFileへ書かず、指定Formatで次を返す。

- ProjectとPhaseの現在地。
- Role Authorityの分離。
- Source of Truth。
- 読取文書間の矛盾／陳腐化候補。
- 最初の安全Action。
- 欠落情報。
- Mutation 0の報告。

評価対象は文章の華麗さではなく、Docsだけで正確に復元できたか、越権せず不明を不明としたか、意味矛盾を検知できたかである。

## 9. Stage 6 — Review

### Design Governance Review

- Requirements／Architectureへの技術的適合。
- Docsの誤読、欠落、矛盾、過剰解釈。
- HandoffとTask返答の対応。

### Project Responsibility Review

- Envelope／Authority／Human Gate適合。
- Task数、Cost、Stop、Recovery、Git／External不変。
- Phase 2と後続Pilotへの影響。
- Combined RoleがProject Responsibility／Design GovernanceのRecoveryを混同していないこと。
- Authorized Root最上位境界、Automation ProfileおよびHard-code禁止への適合。
- 最上位規則のAmendment Authorityが人間専有であり、AI側が候補登録、文言変更または例外化を自発実行していないこと。

### User Decision Package

```text
Result: GO／ADJUST／STOP proposal
Evidence Summary
Authority Compliance
Files／Git／External State
Cost／Context Observation
Incident／Near Miss
Rule Classification
Next Proposed Envelope
```

## 10. GO／ADJUST／STOP

### GO候補

- Docs-only Recovery、Acknowledgement、StatusおよびReviewが合格。
- Mutation／Authority Deviationが0。
- 従来より再説明Cost／Context Pollutionを減らせる見込み。
- Stage 2の有界Docs Write Pilotを別Envelopeで検討可能。

### ADJUST候補

- Handoffの構造は機能したが、Reading Order、Field、Capability MappingまたはCostの調整が必要。
- Authority Deviationはないが、復元の不完全またはState矛盾がある。

### STOP候補

- Authority外Action、許可ないMutation、User Gate省略。
- Provider Capability不足で観測／停止できない。
- Costが便益を上回る。
- Docs-only Recoveryが成立しない。

GO／ADJUST／STOPはユーザーが確定する。プロジェクト責任者役または設計統括者役の提案をFinal Decisionと表記しない。

## 11. Rollback／Recovery

初回Work UnitはRead-onlyのため、Source Rollbackは発生しない。一方、作成済みTaskとConversation StateはProvider上に残る可能性がある。

- Taskを勝手に削除／Archiveしない。
- 違反または疑いの後、自分が作ったArtifactであっても無許可でDelete／Cleanup／Rollbackしない。
- ユーザーが直接確認できる状態を保つ。
- 不完全Taskは`uninitialized`、`stopped`または`review_pending`と記録する。
- 後続Taskの作成で隠さない。

## 12. Current Stop Point

本Plan作成後は次で停止する。

```text
Phase 2-0 Design Package : gate reconciled／final validation pending
Envelope                 : draft_not_authorized
Task                     : not created
Next Action              : complete authorized Git checkpoint, then wait for user large backup
Pre-pilot Backup         : not yet confirmed
Pre-pilot Git Checkpoint : containing commit／remote alignment required for effective
Capability Preflight     : passed／recheck before task creation
Dual Consent             : not completed
Automation Level         : bounded_unit draft／not active
Current Task Rename      : not executed
Control State            : OFF
Permission Hardening     : undecided／not authorized
Mechanical Enforcement  : research candidates only／not implemented
```

## 13. Related Documents

- [Pilot Requirements](../requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Pilot Architecture](../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Authorization Envelope Draft](../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Bootstrap Handoff Draft](../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Automation Governance Index](../../../shared/automation/automation_governance_index_ja.md)
- [Automation Control Profile](../../../shared/automation/automation_control_profile_ja.md)
- [Constitution Research Index](../../../shared/constitution/constitution_research_index_ja.md)
- [Pre-pilot Governance Baseline](../../../shared/automation/pre_pilot_governance_baseline_ja.md)
