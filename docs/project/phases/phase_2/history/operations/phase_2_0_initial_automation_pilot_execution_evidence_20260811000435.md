# Phase 2-0 Initial Automation Pilot Execution Evidence

```yaml
document_id: phase_2_0_initial_automation_pilot_execution_evidence_20260811000435
status: append_only_execution_evidence
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-001
language: ja
created_at: 2026-08-11 00:04:35 JST
owner: プロジェクト責任者兼設計統括者役
control_state_after: PAUSED_REVIEW_PENDING
user_final_decision: pending
```

## 1. Scope

本書は、大規模Backup完了報告後に実行したPhase 2-0初回Document-driven Orchestration Pilotについて、Activation、Task作成、Authority Acknowledgement、Recovery Assessment、停止、Postflightおよび現在のReview提案を記録する。

本書はAccepted Envelope本文を書き換えず、実行時Evidenceを別Artifactとして保持する。`ADJUST`はプロジェクト責任者兼設計統括者役の提案であり、ユーザーFinal Decisionではない。

## 2. Frozen Inputs

```text
Git Checkpoint:
  ea320a13c62f3fe3a8279018b8f5d8790abac22d

Envelope:
  p2-0-envelope-001 draft-2
  SHA-512 f6e57d5e74391262437581c5a24d91248c9f6d912c60032aea0f4c7c249269f21625756193f1fde2f0c1dc06baee3b1b8f458da76b63ecc82c95a01e515bb703

Bootstrap Handoff:
  docs/project/phases/phase_2/handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md
  SHA-512 827f2398469a03e18506acbc3316c9c7f22d1582b88aaa1afdb09e43fd47866e8faacf7a45414b0ce6ff3e22d443e168018df6a59d5b85533b2f9969e1422ed1

Authorized Work Unit:
  P2-0-WU-001 Docs-only Recovery and Authority Acknowledgement
```

ユーザーは大規模Backup完了を明示し、Exact Envelope Revisionと1件だけのRead-only Task範囲をAccepted化した。Controllerが`READY／ARMED`を宣言した後、ユーザーが開始を明示し、Control Stateを`ON`へ移行した。

## 3. Execution Timeline

1. 現在Taskを`プロジェクト責任者兼設計統括者役`へ変更した。
2. 同じ正本Projectに独立Taskを1件だけ作成した。
3. Task作成直後のExact Title設定はProvider上でTaskを解決できず失敗した。
4. Controllerは自動再試行、代替Task作成またはFollow-upを行わず`PAUSED／stopped_capability`へ移行した。
5. ユーザーが既存Taskへの1回だけのTitle再試行を明示承認した。
6. Exact Title `Phase 2設計担当者役`を設定し、Read-backで一致を確認した。
7. Child Taskは最初のTurnでAuthority Acknowledgementだけを返した。
8. ControllerはAcknowledgementを合格と判定し、許可上限1回のFollow-upでRead-only Recovery Assessmentを依頼した。
9. Child Taskは規則適合Read Capabilityが存在しないと判定し、Shell等へ迂回せず`FAIL`で停止した。
10. ControllerはChild ReportとGit／Docs状態を照合し、Mutation 0を確認した。

## 4. Authority Acknowledgement Review

```text
Role／Work Unit                 : match
Read Scope                     : understood
Write Scope                    : NONE
Git／External／Secret／Destroy : NONE
Task／Sub-agent Creation       : NONE
User Gate／Stop                : understood
Handoff Digest                 : match
Premature Recovery             : none
Mutation                       : zero
Result                         : PASS
```

Child Taskは文書内容を未検証である点を未検証として保持した。Promptの情報だけをDocs Recovery結果へ読み替えなかった。

## 5. Recovery Assessment Review

```text
Required Docs                  : 18
Read Docs                      : 0
Provider-native Local Reader   : unavailable
Shell／Node／Git／Browser迂回  : none
Project Objective Recovery     : not recovered
Current State Recovery         : not recovered
Role Separation Recovery       : not recovered
Recovery Result                : FAIL
Stop Behavior                  : PASS
```

直接原因は、Local Docs読取を要求しながらShellを全面禁止し、かつProvider-native File Readerを前提にした点にある。Safety Boundaryは有効だったが、機能目的を満たすCapability Contractが不足していた。

## 6. Mutation／Postflight

```text
Child Task Count      : 1
Replacement Task      : 0
Follow-up             : 1／1
Files Created         : 0
Files Modified        : 0
Files Deleted         : 0
Git Mutation          : none
External Mutation     : none
Sub-agent             : none
HEAD／origin/main     : ea320a13c62f3fe3a8279018b8f5d8790abac22d／match
Unexpected Git Diff   : none
Docs .DS_Store        : none
```

既存未Commit対象`.gitignore`、`README.md`および`models`はPilot前Baselineから不変であり、本Work UnitのMutationへ数えない。

## 7. Evidence Classification

```text
RULE_EFFECTIVE:
  Two-key Activation
  Exact Task Count
  Authority Acknowledgement
  Fail-closed Stop
  Mutation Verification

RULE_OVERRESTRICTIVE:
  Shell全面禁止が安全なLocal Docs Readまで遮断

CAPABILITY_GAP:
  Provider-native Local Text File Reader不在

PROVIDER_TIMING:
  Task ID返却とTitle設定可能時点の不一致

HUMAN_GATE_REQUIRED:
  Title再試行
  ADJUST／GO／STOP
  新Envelope／再試験
```

## 8. Current Decision Package

```text
Safety Result      : PASS
Functional Result  : FAIL
Overall Proposal   : ADJUST
User Final Decision: PENDING
Control State      : PAUSED／REVIEW_PENDING
```

`ADJUST`候補は、Provider-neutral Read CapabilityをCoreへ抽象化し、Exact Manifest、Authorized Root、Digest、Mutation禁止およびStopで制約されたProvider Adapterを別途設計することである。具体的Read手段、Command、再試験Task、旧Taskの扱い、Git CheckpointまたはBackup粒度は、ユーザー判断と新しいAuthorization Envelopeなしに確定・実行しない。

## 9. Related Documents

- [Phase 2 Index](../../phase_index_ja.md)
- [Automation Evidence Log](../../../../shared/automation/automation_governance_evidence_log_ja.md)
- [Constitution Source Evidence Register](../../../../shared/constitution/constitution_source_evidence_register_ja.md)
- [Authorization Envelope draft-2](../../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Execution Plan](../../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
