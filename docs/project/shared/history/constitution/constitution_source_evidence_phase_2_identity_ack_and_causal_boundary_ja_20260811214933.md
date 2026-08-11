# Constitution Source Evidence — Identity ACK／Causal Boundary

```yaml
document_id: constitution_source_evidence_phase_2_identity_ack_and_causal_boundary_20260811214933
status: append_only_history_event
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-002
created_at: 2026-08-11 21:49:33 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role:
  - user
  - future_constitution_compiler
source_id: CONST-SRC-019
normative: false
```

## 1. Candidate Principle — Identity ACK before Capability

Provider上でTask、Role名またはTitleが存在・登録・表示されたことは、Taskが自己Identity、Authority、Stop ConditionsまたはHuman Gatesを認識した証明ではない。

```text
Task Exists
!= Metadata Registered
!= In-band Contract Received
!= Identity Acknowledged
!= Capability Authorized
!= Work Completed
```

Read／Write／External／Toolその他のCapabilityを起動する前に、TaskがMachine-readable Contractを返し、上位Review RoleがExact一致を確認するCandidate Ruleとする。

## 2. Candidate Principle — Dual Evidence

Provider MetadataとIn-band Handoffは競合する正本ではなく、異なる失敗を検知する二つのEvidence Channelとして扱う。片方の成功で他方を省略しない。不一致時はCapabilityを起動せず停止する。

## 3. Candidate Principle — Causal Restraint

一回の再試験で複数Variableを同時変更した場合、成功または失敗を単一Variableへ帰属させない。確認済み事実、未分離要因および追加実験が必要な範囲を明示する。

## 4. Candidate Principle — Full Recovery／Operational View Separation

Lossless Full Recovery Testと、日常運転用の軽量Role Viewを分離する。軽量化はCanonical Source削除、履歴消失または復元不能化を意味しない。DigestとSource Traceにより、必要時にFull Corpusへ戻れる構造を要求する。

## 5. Non-elevation

本記録はHuman-only最上位規則、憲法正本または実行可能Ruleへの自動昇格を行わない。Phase 2／3の追加Evidence、Conflict、CostおよびHuman Reviewを経て、将来のConstitution Compilation候補としてのみ保持する。

## 6. Evidence

- [Automation Evidence](../automation/automation_governance_evidence_phase_2_bounded_read_recovery_ja_20260811214933.md)
- [Controller Review](../../../phases/phase_2/history/operations/phase_2_0_bounded_read_retest_review_20260811210503.md)
