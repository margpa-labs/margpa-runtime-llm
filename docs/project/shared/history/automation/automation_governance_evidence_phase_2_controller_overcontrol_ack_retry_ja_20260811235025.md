# Automation Governance Evidence — Controller Overcontrol／ACK再送境界

```yaml
document_id: automation_governance_evidence_phase_2_controller_overcontrol_ack_retry_ja_20260811235025
status: accepted_operational_correction
phase: phase_2
work_unit: P2-0-WU-004
recorded_at: 2026-08-11 23:50:25 JST
language: ja
owner_role: プロジェクト責任者兼設計統括者役
classification:
  - RULE_EFFECTIVE
  - RULE_OVERRESTRICTIVE
  - HUMAN_GATE_OVERAPPLICATION
  - CONTROLLER_JUDGMENT_FAILURE
  - AUTOMATION_CANDIDATE
```

## 1. Observation

P2-0-WU-004の新規Taskは、Initial PromptのExact Identity Blockに独立した`Task Title:` Fieldがなかったため、Task Titleを自然文またはThread Metadataから推測補完せず、`ACK_STATUS: REJECTED`と`STOP-IDENTITY-OR-ACK-MISMATCH`を返した。

```text
Child Tool Use         : 0
Child Filesystem Read  : 0
Child Mutation         : 0
Exact Result Creation  : 0
Authority Expansion    : 0
Scope Expansion        : 0
Child Stop Behavior    : correct fail-closed
```

Child Task側の挙動に問題はなかった。欠けていたのは、Controllerが作成したInitial Prompt内の一つの明示Labelである。

## 2. Controller Overcontrol

Controllerは当初、軽微なPrompt記載漏れに対し、Append-only Correction Receiptの新規作成とユーザー再承認を新しいHuman Gateとして要求した。

この判断は、次を区別せず、ACK Rejectを機械的にHuman Gateへ接続した過剰統治である。

```text
A. Accepted Scope内の伝達表現訂正
B. Authority／Scope／Mutation／Task構成／Start Stateの変更
```

今回該当するのはAだけである。Exact Package、Task、Role、Source Set、Result Path、Capability、ProhibitionおよびHuman Gateを変更せず、同じTaskへ欠落Labelを再掲してNo-tool ACKを取り直す行為は、既に委譲されたController Authority内のRoutine Correctionである。

## 3. Correct Operational Rule

最高責任者役および各Role／Taskは、最上位規則、共通運用規則、Role／Docs Authority、Accepted EnvelopeおよびWork Unitの交差内で、影響度を都度判断する。

```text
Automation
  ≠ 全判断の機械化
  ≠ 全RejectのUser Escalation
  ≠ 軽微な訂正ごとの新Human Gate

Automation
  = 通常運転と同じRole-local Judgment
  + 承認済み到達線内の自律的な連結
  + Authority／Scope／Riskが変化する地点だけのGate
```

次の条件を全て満たす訂正は、担当Roleが追加のユーザー承認なしに処理できる。

1. Accepted Objectiveを変更しない。
2. Authority、Allowed Path、Docs AuthorityまたはCapabilityを拡張しない。
3. Source Set、Result Path、Task数またはTask Roleを変更しない。
4. Write、External、Git、Secret、Permission、Deleteその他の新Mutationを追加しない。
5. READY／ARMED／Startまたは完了判定へStateを進めない。
6. 既存Evidenceを削除、上書き、Cleanupまたは遡及改変しない。
7. 訂正内容と理由を追跡可能にする。

今回の`Task Title:` Field再掲と同一TaskへのNo-tool ACK再要求は、全条件を満たす。

## 4. Human Gateが必要な変更

次のいずれかを伴う場合はRoutine Correctionとして処理せず、既存規則に従いユーザーまたは適切な上位RoleへEscalateする。

- Envelope、Manifest、Source SetまたはResult Pathの意味変更。
- Task追加、Task交換、Role変更またはTask数上限変更。
- Authorized Root、Allowed Path、Write範囲またはExternal Scopeの拡張。
- READY／ARMED／Start、Automation LevelまたはCompletion Lineの変更。
- Git／GitHub、Secret、Permission、Delete、CleanupまたはDestructive Actionの追加。
- 最上位規則、Human-only事項、重大Risk、Security／Privacy／RecoveryまたはCross-Phase影響。
- 同じ軽微な失敗の反復により、局所訂正では原因を解消できない場合。

## 5. Evidence／Artifact Rule

軽微な訂正であることを理由にEvidenceを消してはならない。一方、毎回大規模Package、Receipt、Stable文書更新または新Human Gateを増設する必要もない。

```text
Evidence Required  : what failed／why／what was corrected／scope unchanged
New Control Package: not required when semantics are unchanged
New User Gate      : not required for in-scope routine correction
Cleanup            : prohibited
```

Evidenceの粒度はRiskと再発可能性に比例させる。形式を増やすこと自体を安全性と誤認しない。

## 6. Correction to Prior Review Conclusion

[P2-0-WU-004 Initial ACK Review](../../../phases/phase_2/history/operations/phase_2_0_documentation_capability_initial_ack_review_p2_0_wu_004_20260811234420.md)の事実記録、Child Reject判定およびNo-mutation Evidenceは有効である。

ただし、同Review Section 7／8の「Correction Receiptとユーザー再承認を必要とする」というController判断は、本Evidenceにより次へ訂正する。

```text
Correct Next Action:
同じTaskへ、欠落していたExact Task Title Fieldだけを明記して
No-tool ACKを一回再要求する。

Additional User Acceptance:
不要。既存Accepted Scope内のRoutine Correctionとして扱う。
```

旧Reviewは当時の判断証跡としてAppend-onlyで保持し、編集または削除しない。

## 7. Pilot／Constitution Input

本件は、将来のAutomation／Constitutionへ次を入力する。

1. Fail-closed検知と、その後のRecovery Authorityを分離する。
2. Stopが正しかったことは、必ず新Human Gateが必要であることを意味しない。
3. ControllerはMateriality、Authority、Scope、MutationおよびState変化を評価する。
4. Routine Correctionを許可し、Human Gate FatigueとDocs Explosionを防ぐ。
5. 同一原因が反復する場合だけ、局所訂正からDesign Reviewへ昇格する。
6. 高い規律は、判断停止や形式の無制限増設ではなく、適切な境界での自律判断を含む。

## 8. Current State

```text
Task                  : retained／idle
Initial ACK           : rejected／recorded
Corrected Re-ACK      : not yet sent
READY／ARMED          : not declared
Capability Start      : not authorized
Exact Result          : absent
Automation State      : PAUSED_ACK_CORRECTION
```

本Evidence作成はNo-tool ACK再送またはCapability Startを実行したことを意味しない。
