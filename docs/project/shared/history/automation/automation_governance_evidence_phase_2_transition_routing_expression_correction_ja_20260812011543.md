# Phase 2 Transition Routing表現訂正Evidence

```yaml
document_id: automation_governance_evidence_phase_2_transition_routing_expression_correction_ja_20260812011543
status: recorded_and_integrated
phase: phase_2
subphase: phase_2_0_closure
created_at: 2026-08-12 01:15:43 JST
language: ja
from_role: user
to_role: プロジェクト責任者兼設計統括者役
source_type: human_review_of_controller_authored_contract
historical_mutation: false
git_action: false
```

## 1. Finding

直前に作成したTransition Blocker／Escalation／Closure Contractには、意図自体ではなくControllerの表現とルーティングに次の重大な不整合があった。

1. Current Transitionへ必須のRole-owned Workと、次工程で行うWorkを同じ区分へ入れた。
2. Historical Outcomeの再活性化Triggerへ、新しいTransitionが過去Failureへ依存する場合を明記しなかった。
3. Human Escalationの代表例を、閉じたAllowlistとして解釈できる表現にした。

これは新しいUser要件または追加判断事項ではなく、最高責任者役が既存意図を正しく抽象化、統合およびルーティングできなかった文書設計上の誤りである。

## 2. Correction

Findingを一つのLabelへ潰さず、次の2軸へ分離した。

```text
Transition Impact:
  HOLD | NONE

Resolution Route:
  ROLE_OWNED_CURRENT | ROLE_OWNED_NEXT | HIGHER_ROLE
  USER_GATE | EXTERNAL_WAIT | DEFERRED_EVIDENCE
```

Current Transitionへ必須のRole-owned Workは、User Escalation不要でも完了まで`HOLD`する。`ROLE_OWNED_NEXT`はCurrent Transition成立条件ではない事項にだけ使用する。

Historical Outcomeは、新Evidenceだけでなく、新しいCurrent Transitionが過去Outcome／Failure Dimensionへ依存する場合、またはDependency／利用Scope／前提／Completion Lineが変化した場合にも再評価する。

Human Escalationは、全AI RoleのAuthority超過、Human-reserved Gate、Objective／Scope／Authority／Root／不可逆性／外部責任の変更、または最高責任者役でも安全かつ可逆的に決定不能という原則で判断する。列挙は非網羅的な例であり、未列挙事象を排除しない。

## 3. Controller Routing Responsibility

最高責任者役は、複数Findingを統合し、Current Transition Impact、解決責任者、Resolution Route、再開条件、Human Gate適格性およびClosure Recommendationを自分で確定する。分類候補をUserへ並べて選択させない。

本訂正はSafety Gateを弱めない。Userへ返す判断を減らす一方、Current Transitionへ必須の未完了作業は、解決担当がAI Roleであっても完了まで通過させない。

## 4. Corrected Sources

- `docs/project/shared/operations/transition_blocker_escalation_and_closure_contract_ja.md`
- `docs/project/shared/operations/phase_completion_review_and_backup_gate_ja.md`
- `docs/project/shared/automation/automation_governance_evidence_log_ja.md`
- `docs/project/shared/automation/automation_governance_index_ja.md`
- `docs/project/shared/constitution/constitution_source_evidence_register_ja.md`

既存Historyは変更せず、本書と新しいBefore／After Snapshotで訂正経路を保持する。
