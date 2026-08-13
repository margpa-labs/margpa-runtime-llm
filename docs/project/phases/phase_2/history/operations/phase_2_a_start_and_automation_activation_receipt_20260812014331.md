# Phase 2-A Start／Automation Activation Receipt

```yaml
document_id: phase_2_a_start_and_automation_activation_receipt
status: active
phase: phase_2
subphase: phase_2_a
language: ja
created_at: 2026-08-12 01:43:31 JST
from_role: user
to_role: プロジェクト責任者兼設計統括者役
decision_authority: user
automation_control_state: on
automation_level: bounded_unit
authorized_completion_line: phase_2_a_complete
```

## 1. Accepted Start Evidence

ユーザーは、Phase 2-A開始前Backup、GitHub反映目視、Phase 2-A Standbyを確認した上でPhase 2-A開始を明示した。その後、Phase 2-Aを完全自動化で完遂する方針、利用可能量の途中枯渇を前提とする頻繁なIndex／Current State／Recovery Checkpoint、および途中停止時の差分再開可能性を確認し、「2-A完遂目指して」「任せた」と開始を確定した。

```text
Backup                    : USER REPORTED COMPLETE
Backup Name               : margpa-runtime-llm_2-A_開始前_20260812.zip
Backup Git Metadata       : EXCLUDED BY USER
GitHub Visual Verification: USER CONFIRMED
Phase 2-A                 : STARTED
Automation Control        : ON
Execution Pattern         : CHAINED BOUNDED WORK UNITS
Completion Line           : PHASE 2-A COMPLETE
```

Human-private Backup Assetの実体、配置先、Digestまたは内容はAutomation Evidenceへ取り込まず、ユーザー報告だけをGate Evidenceとする。

## 2. Authorized Scope

Phase 2-Aの目的に直接必要な次の作業を、指定Project Root内で自律的に連結できる。

- Phase Contract、Requirements、Architecture、ADR、Acceptanceの設計
- Conversation／Session／Turn／Message IdentityとState Contractの設計・実装
- Storage Port、Schema Version、Migration／Rollback、Failure Contractの設計・実装
- Phase 1 Ephemeral ConversationとのCompatibility境界
- 対応Unit／Contract／Static Test
- Phase-local Index、Handoff、Status、Evidence、Review、Recovery Checkpoint
- Scope内Findingの調査、局所修正、再TestおよびReview

## 3. Non-authorized Scope

次は本Receiptから許可を生成しない。

- Authorized Project Root外へのAccess
- Phase 2-B以降のPersistence Service／UI／Configuration／Switchboard実装
- Git Commit／Push／Remote／Release／公開
- External Service、Secret、課金、Model Artifact、Lightning操作
- Destructive Action、既存Historyの上書き・削除
- Automation Levelの`workflow／phase／project`への昇格

## 4. Work Unit Chain

```text
P2-A-WU-001 : Phase Contract／Domain／Storage Boundary Design Freeze
P2-A-WU-002 : Domain Contracts／Ports／Unit Test Implementation
P2-A-WU-003 : Compatibility／Acceptance／Subphase Closure Review
```

最高責任者役は、同じ責務を満たす範囲でWork Unitを分割・統合できる。Scope、Human Gateまたは最上位規則を変更してはならない。

## 5. Resource／Recovery Contract

利用可能量、ContextまたはService制限で中断する場合、未完了をCompleteと表示しない。各有界境界で次を更新する。

- `phase_index_ja.md`のCurrent State
- `history/index/`のAppend-only Snapshot
- 完了済み／未完了／次のExact Action
- Files Changed／Validation／Open Finding
- Automation Control Stateと再開条件

## 6. Activation Result

```text
READY Evidence       : PASS
User Start           : PASS
Two-key Activation   : PASS
Control State        : ON／PHASE 2-A／P2-A-WU-001
Source Mutation      : NOT YET STARTED
Git／External        : NOT AUTHORIZED
```
