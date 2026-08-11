# Automation Governance Evidence — Task Identity／Layered Recovery

```yaml
document_id: automation_governance_evidence_phase_2_task_identity_and_layered_recovery_20260811220038
status: append_only_history_event
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-002
created_at: 2026-08-11 22:00:38 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role:
  - user
  - future_automation_governance_compiler
observation_id: OGE-P2PILOT-019
normative: false
```

## 1. Purpose

`P2-0-WU-002`の再試験成功後に得られた、Task Identity、Task命名およびRecovery Corpus制御に関する追加知見を保存する。本記録は既存Evidenceを置換せず、後続Phaseの反復観測によって検証・修正される非Normativeな追加証跡である。

## 2. Causality Remains Open

初回失敗後の再試験では、次の二条件を同時に変更した。

1. 既存の同系統Taskをユーザーが削除した。
2. Initial PromptへExact `Task Title`とFormal Stop ConditionsをMachine-readable Fieldとして明記した。

再試験は成功したが、現時点のDataだけでは、既存Task削除が直接的要因だったのか、Prompt Contract修正が直接的要因だったのか、両方の組合せが必要だったのかを分離できない。したがって、いずれか一方を成功原因として断定しない。

Phase 2以降のTask生成では、可能な範囲で次を継続観測する。

- 既存の同Role Taskの有無および件数
- Provider上で設定されたTask Title
- In-band Handoffに記載されたTask Title／Role／Work Unit
- Task自身がACKしたIdentity
- Formal Stop Conditionsの明示方法
- ACK成功／失敗と、Capability起動前の停止結果

複数回の反復観測または条件を分離した試験によりEvidenceが蓄積するまで、原因は未確定として保持する。

## 3. Role、Task InstanceおよびWork Unitの分離

```text
Role Identity
  != Task Instance Identity
  != Work Unit Identity
  != Provider Display Title
```

今回の`Phase 2設計担当者役 P2-0-WU-002`というTask名は、Pilot中のWork Unitを他の試行、旧Taskおよび後続Taskから分離し、ACK、Handoff、StatusおよびEvidenceを一対一で追跡するためのExecution Instance名である。全ての将来Taskへ同一形式を固定するHard-coded Naming Ruleではない。

その時点の最高責任者役は、適用中の最上位規則、Role Authority、Context状態、Task寿命、Isolation要件および追跡可能性を踏まえてTask名を動的に決定する。

- 一つのTaskがPhase全体を継続担当する場合は、安定したRole名をTask名として使用できる。
- 独立したBounded Work UnitごとにTaskを分ける場合は、Role名へWork Unit IDを付加できる。
- Context限界、Recoveryまたは担当交代によりTaskを再設営する場合は、Role名へ識別可能なInstance IDを付加できる。
- Provider Display TitleだけをTask Identityの証明とせず、In-band ACKとの一致を確認する。

命名形式そのものを目的化せず、そのTaskを他のRole、Instance、Work UnitおよびEvidenceから曖昧なく識別できることを目的とする。

## 4. Layered Recovery Model

Full Corpus Recoveryは、Cold TaskがProjectをLosslessに復元できることを確認する検証として有効だった。一方、通常運転で毎回Full Corpusを読む方式は、Context、Time、利用可能量およびCredit Costが大きい。

通常運転では、次のLayered Recoveryを優先候補とする。

### 4.1 Phase／Work Unit Bootstrap

Task開始時には、そのTaskへ適用される範囲に限定して、次を与える。

- 適用対象となる最上位規則および不可侵境界
- Role View／Authority／Read・Write Scope
- 当該PhaseおよびWork Unitに必要なCanonical文書
- 現在State、Handoff、Stop ConditionsおよびHuman Gate
- Source Trace、RevisionおよびDigest

### 4.2 Differential Supplement

子Taskが根拠不足を検出した場合、または親Taskが追加Contextを必要と判断した場合は、親Taskが必要な文書だけを差分Packageとして追加提供する。

```text
Bounded Bootstrap
  -> Missing Evidence Detected
  -> Child reports exact insufficiency or Parent identifies need
  -> Parent dynamically resolves additional scope
  -> Exact Differential Package supplied
  -> ACK／Digest／Boundary revalidated
  -> Work resumes
```

子Taskは不足を推測で補完せず、与えられたAuthorityを超えて探索範囲を自動拡張しない。親Taskも固定Packageを機械的に追加するのではなく、その都度の目的、Risk、EvidenceおよびCostに基づいて必要範囲を動的に判断する。

### 4.3 Full Corpus Recovery

Full Corpusは少なくとも次の用途で保持する。

- Cold Recovery成立性の検証
- 最高責任者役または重要Roleの完全復元
- 大きなPhase境界、Recovery訓練または監査
- Canonical／View間のDriftが疑われる場合
- 軽量Viewだけでは安全な判断が成立しない場合

軽量化はCanonical Sourceの削除、要約による置換、History損失または復元不能化を意味しない。必要時にFull Corpusへ戻れるTraceとDigestを維持する。

## 5. Dynamic Authority Principle

Automation中であっても、判断を固定Packageや固定Naming Tableへ置換しない。各Role／Taskは、最高責任者役から委譲されたAuthority内で動的判断を行う。追加Readが現在のAuthorityを超える場合だけ、親RoleへExactな不足内容を返して追加Packageを受け取る。

これにより、次の両方を維持する。

- 子Taskが何でも最高責任者役へ逐次確認することによるRole分割の形骸化を防ぐ。
- 子Taskが不足を理由に許可範囲外へ自律拡張することを防ぐ。

## 6. Current Outcome

```text
Task Naming Model          : DYNAMIC／CONTEXT-DEPENDENT
Current Pilot Task Name    : EXECUTION INSTANCE TRACEABILITY USE
Causal Attribution         : OPEN／INSUFFICIENT DATA
Default Recovery Candidate : PHASE／WORK-UNIT BOUNDED
Additional Context         : PARENT-SUPPLIED DIFFERENTIAL PACKAGE
Full Corpus                : RETAINED FOR VALIDATION／RECOVERY／AUDIT
Automatic Scope Expansion  : PROHIBITED
Constitution Elevation     : NOT PERFORMED
```

## 7. Evidence

- [Bounded Read Recovery Evidence](automation_governance_evidence_phase_2_bounded_read_recovery_ja_20260811214933.md)
- [Controller Review](../../../phases/phase_2/history/operations/phase_2_0_bounded_read_retest_review_20260811210503.md)
- [Phase Designer Status](../../../phases/phase_2/history/handoffs/phase_2_0_phase_designer_status_p2_0_wu_002_20260811210503.md)
