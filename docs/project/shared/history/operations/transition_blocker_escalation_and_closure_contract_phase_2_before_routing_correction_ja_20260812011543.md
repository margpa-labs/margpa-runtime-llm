# Transition Blocker／Escalation／Closure Contract

```yaml
document_id: transition_blocker_escalation_and_closure_contract
status: current
normative: true
language: ja
created_at: 2026-08-12 00:58:18 JST
updated_at: 2026-08-12 00:58:18 JST
decision_authority: user
operational_owner: highest_responsible_role
provider_neutral: true
project_neutral: true
applies_to:
  - normal_operation
  - automation
  - work_unit_transition
  - subphase_transition
  - phase_transition
  - project_transition
```

## 1. Purpose

本Contractは、未解決事項、Blocker、担当Roleの次作業、Deferred EvidenceおよびHuman-only Gateを分離し、安全性を保ったまま人間への不要な判断返却を防ぐ。

中心原則は次のとおりである。

```text
Unresolved != Current Transition Blocker
Evidence Retention != Active Governance State
Safety Stop != Automatic User Escalation
Responsible Role Work != Human Decision
```

安全側へ停止することと、停止理由を誰が解決するかは別Dimensionとして扱う。Evidenceを保持することと、過去事項をCurrent Blockerへ再浮上させることも分離する。

## 2. Current Transitionの明示

Blocker判定前に、現在要求されているTransitionを一つだけ明示する。

```yaml
transition:
  from_state: exact
  to_state: exact
  completion_line: exact
  responsible_role: exact
  accepted_scope: exact_reference
  human_gates: []
```

「Project全体」「将来の理想状態」または上位Automationへの昇格条件を、現在の有界Transitionへ暗黙混入させない。

## 3. Blocker Eligibility

`CURRENT_BLOCKER`と認定できるのは、次の4条件を全て満たす事項だけである。

1. 現在要求されているTransitionの成立条件へ直接必要である。
2. 現時点で未解決である。
3. 担当Role、直属上位Roleまたは最高責任者役が、現在のAccepted Authority内の通常作業または明示された次工程として解決できない。
4. 未解決のままTransitionすると、安全性、完全性、可逆性、Evidence IntegrityまたはAuthority Boundaryを破壊する。

一条件でも満たさない事項を`CURRENT_BLOCKER`として表示してはならない。重大に見えること、過去に失敗したこと、未検証であること、Evidenceとして残っていること、または将来必要になることだけではBlockerにならない。

Blocker認定には次を記録する。

```yaml
blocker:
  transition_id: exact
  eligibility_1_direct_requirement: pass
  eligibility_2_currently_unresolved: pass
  eligibility_3_not_resolvable_within_delegated_authority: pass
  eligibility_4_transition_damage_if_ignored: pass
  evidence: exact_reference
  resolution_owner: exact
  escalation_target: exact
```

## 4. Mandatory Classification

未解決またはOpenに見える事項は、少なくとも次の4区分のいずれかへ分類する。

### 4.1 `CURRENT_BLOCKER`

Section 3の4条件を全て満たし、現在のTransitionを止める。

### 4.2 `RESPONSIBLE_ROLE_OWNED_WORK`

現在または次工程で、担当Roleが委譲済みAuthority内で設計、調査、修正、Stable整合、Evidence整理、TestまたはReviewを行える事項である。

```text
owner can resolve now
  -> resolve before closure report

belongs to the next accepted work stage
  -> carry as next work
  -> do not return as a user decision
```

担当Roleが未着手であることを、User Blockerへ付け替えない。

### 4.3 `DEFERRED_EVIDENCE`

将来の研究、昇格、移植性、性能、Provider差、長期安定性または別Phaseの検証対象である。Evidenceとして保持するが、定義済みTriggerが到来するまでActive Governance Stateへ戻さない。

### 4.4 `USER_GATE`

人間にしか決定、実施または受容できない事項である。技術Blockerと混在させず、User Actionとして別表示する。

## 5. Responsibility-first Resolution

問題を発見したRoleは、直ちにUserへ返す前に次の順序で判定する。

```text
Finding／Uncertainty
  -> affected Actionを必要範囲だけ安全停止
  -> Current Transitionへ直接必要か
     -> NO: Deferred EvidenceまたはObservation
     -> YES: 自Roleの責任・権限内で解消可能か
        -> YES: 調査・設計・修正・検証してEvidence化
        -> NO: 直属上位Roleの委譲範囲内か
           -> YES: Responsibility Escalation
           -> NO: Human-only Eligibilityを判定
```

安全停止は「Userへ聞く」を自動的に意味しない。停止後も、担当Roleと上位Roleは自Authority内の解消責任を保持する。

## 6. Human Decision Burden Minimization

人間の判断容量を有限なControl Resourceとして扱う。AutomationのAcceptance Criterionには、安全性だけでなく、Human-onlyでない判断を人間へ返さないことを含める。

UserへEscalateできる代表例は次に限定する。

- 新しいAuthorityの付与またはRole上限の変更。
- Authorized Root、Allowed Path、Scopeまたは外部境界の拡張。
- Git／Remote／公開／Secret／課金／External／Destructive／不可逆Actionの新規許可。
- Project目的、要求、仕様または優先順位そのものを変える選択。
- 最高責任者役でもAccepted Authority内で解決できない重大Riskの受容。
- User Acceptance、Phase移行承認、Backupその他の明示済みHuman Gate。
- 最上位規則の追加、変更、削除、例外化または解釈不能Conflict。

次をUserへMicro-escalateしてはならない。

- 担当Role自身が行えるStable正本整合、Evidence整理、ReviewおよびPreflight。
- Accepted Scope内の技術、設計、実装、Testおよび局所修正。
- 次Subphase開始後に担当Roleが設計するRole／Task構成。
- Deferred Evidenceの保持方法と、Trigger未到来時の非活性維持。
- 既に定義済みの基準を適用して出せるGO／ADJUST／STOP推奨。

Human Escalationには、Exact Decision、推奨案、選択肢、未決定時の影響、現在の担当Roleが決定できない理由および根拠を添える。単に「どうしますか」と返さない。

## 7. Accepted／Closed／Historical Stateの非再活性化

`ACCEPTED`、`CLOSED`、`ADJUST_REQUIRED`、`STOPPED`、`SUPERSEDED`または別の確定済みHistorical Outcomeは、次のいずれかがない限りCurrent Blockerとして再評価しない。

1. Current Transitionの真偽を変える新しいEvidence。
2. Current Transitionが依存するArtifactのIntegrity Mismatch。
3. 現在適用される上位規則との新たなConflict。
4. Userによる明示的な再Open指示。

再活性化する場合は、Trigger、影響対象、以前のTerminal State、今回の差分およびCurrent Transitionとの直接関係を記録する。Triggerなしに「念のため」「未検証だから」「過去に失敗したから」を理由として再浮上させない。

Evidenceは忘れない。しかし、Evidenceの存在だけでActive Stateを変更しない。

## 8. Stable／Current Alignment Responsibility

Stable正本またはCurrent IndexがAccepted Stateへ追随していない場合、更新Authorityを持つ担当RoleはNormal Snapshot Ruleに従って自分で整合し、Link、Digest、StateおよびDiffを検証してからClosure報告する。

更新Authorityがなく、かつ当該不整合がCurrent Transitionへ直接必要な場合だけ、直属上位Roleまたは適格なAuthorityへEscalateする。Stable未整合を発見しただけでUser Blockerにしない。

## 9. Closure Recommendation Contract

Work Unit、Subphase、PhaseまたはProjectのClosure時、最高責任者役は自分で`GO／ADJUST／STOP`推奨を出し、少なくとも次を提示する。

```text
Closure Recommendation:
  GO | ADJUST | STOP

Technical Blockers:
  NONE | exact blocker list with eligibility evidence

Responsible-role Owned Unfinished Work:
  NONE | exact owner and completion point

Deferred Evidence:
  count／summary
  current transition impact: NONE | exact

Validation:
  exact checks and results

User Action Required:
  only Human-only Gates

Next Transition:
  exact next state after user gate
```

Closure報告前に、担当Roleの権限内で閉じられる作業を残さない。`Deferred Evidence`を列挙してもよいが、Current Transition Impactが`NONE`なら判断要求へ変換しない。

望ましいUser-facing出力は次の意味を持つ。

> Evidence、Stable正本、Closure ReviewおよびPreflightを揃えました。私はGOまたはADJUSTと判定します。技術Blockerはありません。残る人間ActionはBackup、Final Acceptanceおよび次Transition開始承認です。

## 10. Validation Scenarios

少なくとも次をGovernance Testへ含める。

1. 過去の失敗Evidenceが存在しても、TriggerなしにCurrent Blockerへ戻らない。
2. Stable正本が古い場合、Authorityを持つControllerが自分で整合してから報告する。
3. 次Phaseの設計作業を前PhaseのBlockerとしてUserへ返さない。
4. Multi-provider、長時間安定性または上位Automation研究を、現在の有界Transitionへ混入させない。
5. Current Transitionに必要でAuthority外の重大問題は、正しく上位RoleまたはUserへEscalateする。
6. Human Gateを減らすためにAuthority、Root、Externalまたは不可逆境界を推測拡張しない。
7. Closure出力が推奨判定、Blocker、Deferred、ValidationおよびHuman-only Actionを分離する。

## 11. Portability／Hard-code Boundary

本Contractは特定Project名、Phase番号、Provider、Task名、Command、Directoryまたは人数をCoreへHard-codeしない。Project固有Transition、Role Binding、PathおよびGateはManifest／Envelopeへ置き、Provider差はAdapterへ分離する。

## 12. Related Documents

- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Role Authority Matrix](../task_roles/role_authority_matrix_ja.md)
- [Phase Completion Review／Backup Gate](phase_completion_review_and_backup_gate_ja.md)
- [Automation Governance Index](../automation/automation_governance_index_ja.md)
- [Automation Control Profile](../automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../automation/automation_governance_evidence_log_ja.md)
- [Constitution Source Evidence Register](../constitution/constitution_source_evidence_register_ja.md)

