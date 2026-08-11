# Phase 2-0 Delegated Escalation／Envelope／Handoff Authority Correction

```yaml
document_id: phase_2_0_delegated_escalation_and_handoff_correction_20260811130930
status: recorded_paused_pending_review
phase: phase_2
subphase: phase_2_0
event_at: 2026-08-11 13:09:30 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role:
  - user
  - Phase 2設計担当者役候補
  - Phase 2実装担当者役候補
owner_role: プロジェクト責任者兼設計統括者役
decision_authority: user
history_policy: append_only
automation_control_state: PAUSED
pilot_restarted: false
new_task_created: false
git_or_external_action: false
```

## 1. Purpose

本記録は、委譲Role-local Judgment／段階的完了連鎖の反映後に行った自己Reviewで検出した三つの不整合と、ユーザーの修正指示に基づくCorrectionをLosslessに保存する。

旧Historyは変更しない。修正前Stableは`20260811130930`のBefore Snapshot、修正後Stableは同TimestampのAfter Snapshotとして保存し、本EventとDocumentation Indexから両方を追跡可能にする。

## 2. Review Findings

### 2.1 Authorization Envelopeの旧中央集権表現

Phase 2 Index、Requirements、Architecture、Role View、HandoffおよびExecution Planは、全Role／Taskが委譲範囲内を都度判断する設計へ揃っていた。一方、Authorization Envelope draft-4だけは、必要ArtifactとExact Pathの判断を最高責任者役へ集中させる表現を保持していた。

Envelopeは実行時契約であるため、未修正のままFreezeするとRole-local Judgmentを上書きするRiskがあった。

### 2.2 不明時のEscalation先Conflict

新設計は、Routine ActionをRole内で閉じ、例外、Scope外、ConflictまたはGateを直属上位へ送る。一方、複数の共通規則は「1%でも不明なら必ずユーザーへ確認」としており、担当内の技術・設計・実装問題までUserへ直接送る解釈が成立していた。

このConflictは、Role分離の意味、責任階層、速度、Context、利用可能量およびユーザー負荷を損なう。

### 2.3 Task Lifecycle Capabilityの重複

Role Authority Matrixでは、`Task作成／命名／Handoff／Follow-up`を一つのCapabilityへ結合し、Phase Designerを`REVIEW_ONLY`としていた。一方、Assigned downstream Roleへの設計伝達、局所Reviewおよび再作業指示は`ROLE_ALLOWED`であり、Phase DesignerがImplementerへHandoff／Follow-upできるかが二重解釈になっていた。

## 3. Correction 1 — Envelope Alignment

Authorization Envelope draft-4を次へ修正した。

- Childは引き続きRead-onlyであり、Docs Mutation Authorityを持たない。
- P2-0-WU-002ではControllerが、自身へ委譲されたDocs Authority内で必要Artifact、許可ClassおよびExact Pathを判断する。
- Controllerが判断主体である理由は最高責任者だからではなく、本Work UnitでDocs Mutation Authorityを持つRoleだからである。
- ChildとControllerのRoutine ActionへActionごとの再確認を追加しない。
- ChildはScope外、Conflict、重大問題、Provider／Resource異常、完了条件不成立または定義済みGateをControllerへ送る。
- Human-only事項だけをUserへ送る。

Envelopeは未承認、未Freezeのままであり、今回の修正はAcceptanceまたはPilot Startを生成しない。

## 4. Correction 2 — Tiered Escalation

不明なActionは引き続きFail-closedで停止する。ただし、Escalation先を次へ分離した。

```text
担当Role内:
  技術／設計／実装／Test／担当Docs／Accepted Design解釈／下位Role調整
  → 直属上位Role

組織境界:
  Cross-Role／Cross-Phase／委譲境界／重大Risk／直属上位で解決不能
  → 段階的に最高責任者役

Human-only:
  ユーザー意図／最上位規則／Authorized Root・Allowed Path／Role Authority上限
  External／Secret／Destructive／ユーザー専用領域／明示Human Gate
  → User
```

直属上位Roleは自身のAuthority内だけで解決し、Authority外を推測で補完しない。Routineな内部問題を直属上位Roleから飛び越してUserへMicro-escalateせず、Human-only事項をAI Roleだけで決定しない。

## 5. Correction 3 — Lifecycle Communication Separation

Role Authority MatrixのCapabilityを次へ分割した。

```text
Task作成／命名
  → Project Controller ROLE_ALLOWED
  → Phase Designer／Implementerは作成不可

Assigned downstream RoleへのHandoff／Follow-up
  → Phase Designer ROLE_ALLOWED
  → Assigned Implementerへの設計伝達／Review／再作業指示を含む

直属上位RoleへのStatus／完了報告／Escalation
  → Phase Designer／Implementerを含む担当Role ROLE_ALLOWED
```

これにより、Phase DesignerはTask Creation Authorityを得ずにAssigned Implementerを統括でき、Implementerは新Taskを作らずPhase Designerへ完了報告とEscalationを返せる。

## 6. Completion Flow after Correction

```text
Implementer
  → Phase DesignerへStatus／完了報告／Escalation

Phase Designer
  → ImplementerへHandoff／Follow-up／Review／再作業指示
  → 局所Accepted後、最高責任者役へTask完了報告

最高責任者役
  → 独立Review／Task完了判定案

User
  → Acceptance
  → 次Work Unit
```

Task作成／命名、下流Communication、上流報告およびFinal Acceptanceを別Authorityとして扱う。

## 7. Modified Stable Documents

- Authorization Envelope draft-4。
- Task Role／Write Authority Policy。
- Role Authority Matrix。
- Research Asset Mutation Control。
- Documentation Structure／Task Operations。
- Documentation Rules。
- Automation／Governance Evidence Log。
- Constitution Source Evidence Register。
- Phase 2 Index。

## 8. Current State／Non-actions

```text
Automation Control State : PAUSED／ROLE_AUTHORITY_DESIGN
Envelope draft-4         : NOT ACCEPTED
Role View draft-2        : NOT ACCEPTED
New Task                 : NOT CREATED
Pilot Restart            : NOT STARTED
Task Rename              : NOT PERFORMED
Git／External Action     : NONE
Authorized Root外Access : NONE
```

本Correctionは、Docs更新とAuthorized Root内History追加だけを行った。Pilot、Task、Permission、Git、External ServiceまたはPhase 2-A機能実装を開始していない。

## 9. Related Sources

- [Phase 2 Index](../../phase_index_ja.md)
- [Authorization Envelope draft-4](../../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Role Authority Matrix](../../../../shared/task_roles/role_authority_matrix_ja.md)
- [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)
- [Documentation Structure／Task Operations](../../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
- [Automation／Governance Evidence Log](../../../../shared/automation/automation_governance_evidence_log_ja.md)
- [Constitution Source Evidence Register](../../../../shared/constitution/constitution_source_evidence_register_ja.md)
- [Delegated Role-local Judgment Evidence](phase_2_0_delegated_role_dynamic_judgment_hierarchy_20260811124635.md)
