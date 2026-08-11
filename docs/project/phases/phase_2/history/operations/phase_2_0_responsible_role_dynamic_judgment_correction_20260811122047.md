# Phase 2-0 最高責任者役の動的判断／Automation意味訂正記録

```yaml
document_id: phase_2_0_responsible_role_dynamic_judgment_correction
status: recorded_paused_pending_review
phase: phase_2
subphase: phase_2_0
event_at: 2026-08-11 12:20:47 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role:
  - user
  - Phase 2設計担当者役候補
owner_role: プロジェクト責任者兼設計統括者役
decision_authority: user
history_policy: append_only
automation_control_state: PAUSED
pilot_restarted: false
new_task_created: false
git_or_external_action: false
```

## 1. Purpose

本記録は、Role／Docs Authority再設計後の自己Reviewから、最高責任者役の判断責任、Automationの意味、Hard-code判断、規則重複整理およびFrom／To契約を再確認・訂正した経緯を、後続Pilot、RecoveryおよびConstitution SourceへLosslessに残す。

本記録は旧Historyを変更しない。既存Evidenceに残る固定Packageまたは`Dynamic Documentation Requirement Resolver`表現は当時の設計経緯として保持し、現行解釈だけを本EventとStable文書で訂正する。

## 2. Review開始時の状態

ユーザーは、直前のRole／Docs Authority修正が一旦妥当に見えるとした上で、プロジェクト責任者兼設計統括者役自身による再Reviewを要求した。

再Reviewでは、次を指摘した。

1. Dynamic Documentation Requirement Resolverが概念定義止まりである。
2. 不可避なHard-codeの承認Authorityが曖昧である。
3. 最上位規則を複数文書へ重複して書きすぎている。
4. From／Toの適用範囲を整理する必要がある。

このうち3と4は整理対象として妥当だった。一方、1と2を「別Subsystemまたは追加Human GateがないためBlocker」と扱ったことは誤りだった。

## 3. User Correction

ユーザーは次を明確化した。

- 必要Document、Role、Evidence、Handoff、Reviewその他は、その時点の最高責任者役が都度動的に判断する。
- 通常運転でも同じ判断を行ってきており、Automationだから判断方法を別物へ変えない。
- Hard-codeを避ける最上位規則は維持するが、許可範囲内の具体的な設計判断まで全て人間へ返さない。
- どうしても人間に判断させるべき問題、Review、承認、Root／Scope／Authority拡張その他のHuman-only事項だけを人間へ返す。
- 規則の重複が支障を生むなら、確認待ちにせず、既存Authority内で整理する。
- From／Toは従来のTask間運用に沿って、伝達責任が存在するArtifactへ付ければよい。
- General Hard-code Prohibitionは既に最上位規則として扱う。可変要素の固定を可能な限り避け、どうしても必要な場合だけ管理された形で採用する。
- Docs／運用規則も、必要性なく破ってよいものではない。最高責任者役が既存規則、目的、影響および必要性を判断する。
- Automationは「判断まで機械的に固定すること」ではない。

## 4. Corrected Interpretation

```text
Human-defined Supreme Rules
  + Common Docs／Operations／Role Rules
  + Current Authorization Instance
  + Work Unit／Context／Risk／Cost／Recovery／Provider Facts
  ↓
その時点の最高責任者役が都度判断する
  ↓
必要なRole／Docs／Evidence／Handoff／Review／Test／Stopを構成する
```

Automationの差分は次だけである。

```text
通常運転:
  ユーザーと対話しながら、現在の明示指示に沿って進む。

Automation:
  ユーザーがAccepted化した到達線とRole Authorityの内側を、
  最高責任者役がActionごとの追加確認なしにWork Unitとして連結する。
```

したがって、Automationは判断の固定化、固定Package化、機械的Resolver化またはRoutine判断の全面的なHuman Gate化を意味しない。

## 5. Highest Responsible Roleの責任

その時点の最高責任者役は、少なくとも次を都度判断する。

- 必要なRoleおよびTask編成。
- Phase別設計担当者役またはPhase別実装者役の必要性。
- 必要なDocument Class、Exact Pathおよび統合可否。
- Handoff、Status、Review、Acceptance、Evidence、IndexおよびRecovery Artifactの必要性。
- 既存Docs／運用規則の適用、Conflict、例外提案および停止地点。
- 情報Loss、復元性、Audit、Cost、ContextおよびProvider Capability。
- Hard-code回避手段、不可避性、Exact Scope、Migration条件、TestおよびEvidence。
- 人間へ返すべき判断と、Role内で完了させるRoutine判断の分離。

最高責任者役であっても、最上位規則を追加・変更・削除・例外化できず、Authorized Root、Allowed Path、Role上限またはユーザー専用領域を無許可で拡張できない。

## 6. Human-only Boundary

次はAutomationまたは最高責任者役の都度判断で代替しない。

- 最上位規則の追加、変更、削除、並替えまたは例外化。
- Authorized Root、Allowed Path、Project ScopeまたはRole Authority上限の拡張。
- ユーザー専用領域へのAccess。
- Git、External、Secret、Destructiveその他、現行規則が`USER_EXPLICIT`とするAction。
- Project、Research、Product、公開、費用または責任上、最高責任者役だけで決定できない重要判断。
- Accepted Completion Lineの外側へ進むこと。

## 7. Documentation Judgment

固定のIndex／Handoff／Status／Review Packageを全Work Unitへ要求しない。最高責任者役は、Work Unit種別、Role／Task境界、State Transition、Mutation Risk、Review／Human Gate、Audit／Recovery、Provider Capability、情報Loss、CostおよびContextから必要Artifactを判断する。

- Indexは独立したNavigation／Recovery入口が必要な場合。
- Handoffは責任、Authority、入力または次Actionを移転する場合。
- Statusは進捗、停止、失敗、完了またはRecovery Stateの永続化が必要な場合。
- Review／Acceptanceは独立判定またはGateがある場合。
- Evidenceは監査、復元、Authority証明または再現性が必要な場合。
- 一つのArtifactで複数責務をLosslessに満たせる場合は統合する。
- 必要性を示せないArtifactは作らない。

Project Bindingは許可Document Root／Classを与える。最高責任者役は必要な対象をExact Pathへ固定するが、この判断で既存Stableへの直書き、既存History Mutation、許可外Class、Root外またはExternal Authorityを生成しない。

## 8. From／To Contract

- Handoff、Status、Review、Request、Acknowledgementその他、Role／Task間で責任、Authority、入力、判定または次Actionを移転するArtifactは`from_role／to_role`を持つ。
- Indexは`owner_role`、`upstream_role`、`intended_readers`、Work UnitおよびStateを持つ。
- Requirements／DesignはOwnerとDecision Authorityを持つ。
- 単一Role内の機械的Evidenceは、架空の宛先を作らず、Actor、Ownerおよび対象を記録する。
- Evidenceを別Roleまたはユーザーへ提出する場合はFrom／Toを付ける。
- Read-only Roleの記録を別Roleが代行する場合は、論理的著者と伝達関係を保持する。

## 9. Rule Deduplication

General Hard-code Prohibitionと共通Docs判断のNormative本文は、`docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`を正本とする。

Role Authority MatrixはRole／Docs Authorityと判断主体を、Automation文書は連結実行差分を、Phase文書はP2-0固有投影を、Constitution Research文書はSource Traceと将来編纂境界を保持する。同じ一般条文を各文書へ全文複製しない。

## 10. Supersession／Preservation

- `OGE-P2PILOT-012`のMode-invariant Role／Docs Authority修正は維持する。
- `OGE-P2PILOT-013`の固定Document Package廃止は維持する。
- `OGE-P2PILOT-013`の独立Dynamic Resolver前提は、`OGE-P2PILOT-014`と本記録により最高責任者役の都度判断へ修正する。
- 旧Evidenceと旧Snapshotは当時の設計経緯としてAppend-onlyで保持する。
- `pre_pilot_governance_baseline_ja.md`は2026-08-09時点のHistorical Baselineへ戻し、後日追加された一般Hard-code条文の重複を除いた。

## 11. Current State／Non-actions

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

本Eventは、設計修正とDocs Evidence固定だけを行う。Pilot再開は、修正版のReview、Exact Freeze、ユーザーAcceptance、Controller READY／ARMEDおよび後続User Startを経るまで行わない。

## 12. Related Sources

- [Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Role Authority Matrix](../../../../shared/task_roles/role_authority_matrix_ja.md)
- [Documentation Structure／Task Operations](../../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Automation Control Profile](../../../../shared/automation/automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](../../../../shared/automation/automation_governance_evidence_log_ja.md)
- [Constitution Source Evidence Register](../../../../shared/constitution/constitution_source_evidence_register_ja.md)
- [Phase 2 Index](../../phase_index_ja.md)
- [Phase 2-0 Requirements](../../requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Phase 2-0 Architecture](../../architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Authorization Envelope draft-4](../../governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Phase Designer Role View draft-2](../../governance/phase_2_0_phase_designer_role_view_draft_ja.md)
- [Bootstrap Handoff draft-4](../../handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)
- [Execution Plan](../../operations/phase_2_0_automation_pilot_execution_plan_ja.md)
