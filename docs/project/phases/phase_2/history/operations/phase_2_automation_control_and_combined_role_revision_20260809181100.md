# Phase 2 Automation Control／Combined Role Revision Record

```yaml
record_id: phase_2_automation_control_and_combined_role_revision_20260809181100
status: recorded
language: ja
timestamp: 2026-08-09 18:11:00 JST
actor: プロジェクト責任者兼設計統括者役
phase: phase_2
subphase: phase_2_0
mutation_scope: documentation_only
pilot_started: false
task_created: false
task_title_changed: false
git_mutation: false
external_mutation: false
```

## 1. User Decisions

- 当面、現在Taskは`プロジェクト責任者兼設計統括者役`として両責務を兼務する。
- Project ResponsibilityとDesign GovernanceのFolder／Stable／History／Recoveryは分離して相互参照する。
- Automation／Constitutionへ直接使える知見を専用Automation DirectoryとHistoryへ集中して累積する。
- AutomationはBinary ON／OFFではなく、許可範囲を段階的に制御する。
- Commit／Pushは原則として大きな有界MilestoneまたはPhase単位とし、各小変更で反復しない。
- 指定Authorized Root／Allowed Path外への無許可接触禁止は、全Role、全Level、全Providerへ適用する最上位規則群の一つとする。
- Pilot開始前にユーザーが大規模Backupを取得する。
- PilotはControl TaskのReady宣言と、その後のUser開始宣言の双方が成立した場合だけ一斉開始する。
- Automation／ConstitutionのNormative CoreへProject／Provider固有値をHard-codeしない。
- Claude Code等のMulti-provider併用は未決定の将来検証候補として保持する。

## 2. Dedicated Automation Structure

```text
docs/project/shared/automation/
├─ automation_governance_index_ja.md
├─ automation_control_profile_ja.md
└─ automation_governance_evidence_log_ja.md

docs/project/shared/history/automation/
└─ Append-only snapshots and evidence
```

旧Stable Evidence Logを専用Automation Directoryへ移し、Stable側の参照を更新した。旧History Artifactは原文証跡として移動・編集しない。

## 3. Combined Role／Recovery Boundary

現在Taskが二つの責務を兼務しても、Recoveryを一つへ圧縮しない。

```text
Project Responsibility Recovery
  ↔ Design Governance Recovery
```

一方はProject編成、Cross-Phase Gate、Role再構成およびFinal Reviewを扱い、他方はRequirements、Architecture、Canonical Meaning、Phase DesignおよびTechnical Reviewを扱う。兼務はAuthority合算、自己免除またはUser Gateの代理を意味しない。

## 4. Automation Profile

```text
manual
advisory
bounded_unit
workflow
phase
project
```

Levelだけでなく、Task Creation、Delegation、Filesystem／Git／External／Secret／Destructive Mutation、Continuation、Resource、Evidence、ExpirationおよびRevocationを独立Fieldで制御する。初回Phase 2 Pilotは`bounded_unit` Draftであり、まだActiveではない。

## 5. Start Gate

Pilot Start Eventには次を全て必要とする。

1. Design Package Review合格。
2. 大規模Backup完了のUser報告。
3. Accepted Automation Profile／Authorization Envelope。
4. Control Taskの「準備OK。いつでも開始出来ます。」。
5. 後続Userの「ok。では開始する。」。

Start Event成立直後にProvider Capabilityが許す場合だけ、現在Task名を`プロジェクト責任者兼設計統括者役`へ変更する。現時点では双方の宣言、Task作成、Pilot実行およびTask名変更を行っていない。

## 6. Portability／Multi-provider Boundary

Normative CoreはCapability、Authority、Evidence、State、Scope、Stop、RecoveryおよびHuman Gateで記述する。Project固有値はManifest、Provider固有操作はAdapter、Work Unit固有値はEnvelopeへ分離する。

CodexからClaude Code等へHandoffする構成は、開発速度と他Providerでの運用再現性を検証する将来候補である。現時点では未決定・未承認であり、Phase 2-0初回Work Unitへ含めない。

## 7. Current Stop State

```text
Phase 2-0 Design Revision : recorded
Automation Profile       : draft／not active
Pre-pilot Backup          : not yet confirmed
Dual Consent              : not completed
Independent Task          : not created
Task Title Change         : not executed
Pilot                     : not started
Git／External Mutation    : none
Next Action               : design review
```

## 8. Related Documents

- [Phase 2 Index](../../phase_index_ja.md)
- [Automation Governance Index](../../../../shared/automation/automation_governance_index_ja.md)
- [Automation Control Profile](../../../../shared/automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../../../../shared/automation/automation_governance_evidence_log_ja.md)
- [Project Responsibility Handoff](../../../../shared/project_responsibility_handoff/project_responsibility_handoff_ja.md)
- [Design Governance Handoff](../../../../shared/design_governance_handoff/design_governance_handoff_ja.md)

