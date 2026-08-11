# Role Authority Matrix

```yaml
document_id: role_authority_matrix
status: design_candidate_pending_user_review
normative_core: true
language: ja
created_at: 2026-08-11 01:09:24 JST
updated_at: 2026-08-11 12:20:47 JST
owner_role_archetype: design_governor
decision_authority: user
provider_neutral: true
project_neutral_core: true
default_deny: true
```

## 1. Purpose

本書は、通常運転とAutomationの双方で共用する、Role別の実行権限とDocs権限の正本候補である。Roleが同じである限り、通常運転かAutomationかによってRole Authority、Docs Authority、History原則またはTask Artifact契約を二重定義しない。

Automationが追加するのは、ユーザーが事前承認した到達線の内側で、Project ControllerがWork Unitを連結し、各RoleがActionごとの再確認なしに担当範囲を完了へ進めるという実行差分だけである。権限そのものを別体系へ置換しない。

本書は最上位規則の追加、変更、削除、並替え、例外化または候補登録を行わない。最上位規則を変更できるのはユーザーまたはユーザーが明示指定した人間だけである。

本Revisionは、ユーザーの明示指示に基づき、可能な限りHard-codeを避ける一般最上位規則と、許可範囲内の具体的な設計判断をその時点の最高責任者役が都度担う原則を反映する。

## 2. Effective Authority Resolution

```text
Common Role Authority
  = Human-defined Supreme Rulesに適合
  ∩ Role Authority Ceiling
  ∩ Assigned Role／Work Unit Scope

Effective Execution Authority
  = Common Role Authority
  ∩ Current Authorization Instance
  ∩ Available Provider Capability
```

`Current Authorization Instance`は実行Modeによって次のように与えられる。

- 通常運転：現在のユーザー明示指示。ユーザーが既存要件へ追加または変更を加えた場合、Project Controllerと担当Roleが矛盾を解消し、今回の作業範囲へ反映する。
- Automation：ユーザーが承認した到達線と、その内側でProject Controllerが発行するWork Unit指示。

優先順位：

```text
Human-defined Supreme Rules
  > Current User Direction／User-approved Completion Line
  > Role Authority Matrix
  > Work Unit Handoff／Role View
  > Provider Adapter
  > Ordinary Operational Defaults
```

- Role AuthorityはRoleに与え得る上限であり、Role名だけで権限は有効化されない。
- Project Controllerを含む上位Roleの指示は、ユーザーが許可した線、Role上限またはWork Unit Scopeを超えるAuthorityを生成しない。
- 通常運転とAutomationの差はAuthorizationの与え方と継続確認の頻度であり、Role権限表またはDocs権限表の差ではない。
- 許可外、Role外、Scope外、Capability不明または最上位規則とのConflictは、拡張解釈せず停止する。

### 2.1 General Hard-code Prohibition

General Hard-code ProhibitionのNormative本文は[Task Role／Write Authority Policy](task_role_write_authority_policy_ja.md)を正本とし、本書へ重複転記しない。許可範囲内でHard-codeの不可避性、抽象化方法、記録およびTestを判断する責任は、その時点の最高責任者役にある。固定Resolverまたは一律の人間承認へ判断責任を移さない。

## 3. Authority States

| Code | Meaning |
|---|---|
| `ROLE_ALLOWED` | Role上限内で実行可能。Current Authorization InstanceとWork Unitに含まれる場合だけ有効 |
| `REVIEW_ONLY` | Read／Review／判定は可能だが対象Mutationは不可 |
| `USER_EXPLICIT` | 対象とActionに対するユーザーのExact Authorizationが必要 |
| `DENY` | AI Sideの全Roleで実行不可 |

`ARMED`、`ON`、`PAUSED`および`EMERGENCY_STOP`はAutomation Control Stateであり、共通Role権限を変更しない。

## 4. Abstract Role Archetypes

| Archetype | Primary Responsibility |
|---|---|
| `project_controller` | Project全体、Role編成、Work Unit連結、Phase Gate、最終Review |
| `design_governor` | Cross-Phase要件、Architecture、Canonical Meaning、Role Authority整合 |
| `phase_designer` | Assigned PhaseのRequirements／Architecture／ADR／Handoff |
| `implementer` | Accepted Designに従うSource／Test／Script／Config実装 |
| `external_docs_editor` | Public Docs／README／対外Metadataの作成 |
| `reviewer` | Read-only Review、Test Evidence評価、Finding分類 |
| `operator` | ユーザーが承認したExternal／Platform／Git ActionのExact実行 |

Project固有のRole名はBindingで解決する。兼務は明記されたRole Setの共通範囲だけを有効にし、未列挙RoleまたはScope外のAuthorityを生成しない。Phase Designerは原則Phaseごとに配置し、Context、安全性または実装規模上の必要がある場合はPhase別Implementerも配置できる。

## 5. Role Capability Matrix

| Action Class | project_controller | design_governor | phase_designer | implementer | external_docs_editor | reviewer | operator |
|---|---|---|---|---|---|---|---|
| Authorized Docs／Source Read | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `REVIEW_ONLY` |
| Project／Cross-Phase設計書の設計判断 | `REVIEW_ONLY` | `ROLE_ALLOWED` | `REVIEW_ONLY` | `DENY` | `DENY` | `REVIEW_ONLY` | `DENY` |
| Assigned Phase設計書の設計判断 | `REVIEW_ONLY` | `REVIEW_ONLY` | `ROLE_ALLOWED` | `DENY` | `DENY` | `REVIEW_ONLY` | `DENY` |
| Source／Tests／Scripts実装 | `REVIEW_ONLY` | `REVIEW_ONLY` | `REVIEW_ONLY` | `ROLE_ALLOWED` | `DENY` | `REVIEW_ONLY` | `DENY` |
| Config／Dependency Metadata変更 | `REVIEW_ONLY` | `REVIEW_ONLY` | `REVIEW_ONLY` | `ROLE_ALLOWED` | `DENY` | `REVIEW_ONLY` | `DENY` |
| Public Docs／README／対外Metadataの設計判断 | `REVIEW_ONLY` | `REVIEW_ONLY` | `REVIEW_ONLY` | `DENY` | `ROLE_ALLOWED` | `REVIEW_ONLY` | `DENY` |
| Work Unit用Index／Handoff／Statusの新規作成 | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `REVIEW_ONLY` |
| History／Review／Evidence Eventの新規追加 | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `REVIEW_ONLY` |
| 担当成果のTest／Static Check | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `REVIEW_ONLY` |
| Finding作成／Review結果記録 | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `REVIEW_ONLY` |
| Task作成／命名／Handoff／Follow-up | `ROLE_ALLOWED` | `REVIEW_ONLY` | `REVIEW_ONLY` | `DENY` | `DENY` | `DENY` | `DENY` |
| Role内Routine判断／修正／再Test | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `REVIEW_ONLY` | `REVIEW_ONLY` |
| Phase Final Gate案／GO・ADJUST・STOP案 | `ROLE_ALLOWED` | `ROLE_ALLOWED` | `REVIEW_ONLY` | `REVIEW_ONLY` | `REVIEW_ONLY` | `ROLE_ALLOWED` | `DENY` |
| Phase完了宣言／次Phase開始 | `USER_EXPLICIT` | `USER_EXPLICIT` | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` |
| Commit／Push／PR／Merge／Tag／Release | `USER_EXPLICIT` | `USER_EXPLICIT` | `DENY` | `DENY` | `DENY` | `REVIEW_ONLY` | `USER_EXPLICIT` |
| Cloud／External Service／Public Access変更 | `USER_EXPLICIT` | `USER_EXPLICIT` | `DENY` | `DENY` | `DENY` | `REVIEW_ONLY` | `USER_EXPLICIT` |
| Secret／Credential／Private KeyへのAccess | `USER_EXPLICIT` | `USER_EXPLICIT` | `DENY` | `DENY` | `DENY` | `DENY` | `USER_EXPLICIT` |
| Delete／Overwrite／Permission／ACL／Destructive | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` | `DENY` | `USER_EXPLICIT` |
| Incident後Cleanup／Rollback | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` | `REVIEW_ONLY` | `USER_EXPLICIT` |
| Authorized Root／Allowed Path外Access | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` | `USER_EXPLICIT` |
| 最上位規則の追加／変更／削除／例外化 | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` |

`operator`の`USER_EXPLICIT`は、ユーザーが承認したExact Actionだけを実行できることを意味し、独立した意思決定Authorityを与えない。

## 6. Document Authority

### 6.1 Mode-invariant Document States

| Code | Meaning |
|---|---|
| `READ` | Exact Authorized Docsの読取のみ可 |
| `CREATE_NEW` | Work Unit用Index／Handoff／Status等を新規Fileとして作成可 |
| `APPEND_NEW` | Role所有のHistory／Review／Evidenceを新規Event Fileとして追加可 |
| `EXISTING_WRITE_USER_EXPLICIT` | 既存Stable文書はユーザーがExact TargetとActionを明示した場合だけ更新可 |
| `REVIEW_ONLY` | 読取、差分確認、Finding作成のみ可 |
| `DENY` | 対象Docs ActionをAI Sideで実行不可 |

既存Stable文書への直書きは、通常運転かAutomationかを問わず、ユーザーの明示指示がない限り禁止する。上位Roleの指示、Accepted Envelope、Role兼務またはMeaning Ownershipだけでは、この権限を生成しない。

Historyは全Roleに対してAppend-onlyである。`APPEND_NEW`は新規Event Fileだけを許可し、既存History Fileの変更、上書き、移動、削除、統合または退役は`DENY`とする。

### 6.2 Document Class×Role Matrix

| Document Class | project_controller | design_governor | phase_designer | implementer | external_docs_editor | reviewer | operator |
|---|---|---|---|---|---|---|---|
| Current Canonical正本 | `REVIEW_ONLY` | `EXISTING_WRITE_USER_EXPLICIT` | `READ` | `READ` | `READ` | `REVIEW_ONLY` | `REVIEW_ONLY` |
| Shared Normative／Role／Automation／Constitution正本 | `REVIEW_ONLY` | `EXISTING_WRITE_USER_EXPLICIT` | `READ` | `READ` | `READ` | `REVIEW_ONLY` | `REVIEW_ONLY` |
| Assigned Phase Requirements／Architecture／ADR／Governance／Operations正本 | `REVIEW_ONLY` | `REVIEW_ONLY` | `EXISTING_WRITE_USER_EXPLICIT` | `READ` | `READ` | `REVIEW_ONLY` | `REVIEW_ONLY` |
| Active Phase Stable Index | `REVIEW_ONLY` | `EXISTING_WRITE_USER_EXPLICIT` | `EXISTING_WRITE_USER_EXPLICIT` | `READ` | `READ` | `REVIEW_ONLY` | `REVIEW_ONLY` |
| Public Stable／README／License／Notice／Publication Metadata | `REVIEW_ONLY` | `REVIEW_ONLY` | `READ` | `READ` | `EXISTING_WRITE_USER_EXPLICIT` | `REVIEW_ONLY` | `REVIEW_ONLY` |
| 最高責任者役が必要と判断し、許可Class／Pathを固定した新規Work Unit Artifact | `CREATE_NEW` | `CREATE_NEW` | `CREATE_NEW` | `CREATE_NEW` | `CREATE_NEW` | `CREATE_NEW` | `REVIEW_ONLY` |
| Role-owned新規History／Evidence Event | `APPEND_NEW` | `APPEND_NEW` | `APPEND_NEW` | `APPEND_NEW` | `APPEND_NEW` | `APPEND_NEW` | `REVIEW_ONLY` |
| Existing History／Frozen Compilation／他Phase正本 | `READ` | `READ` | `READ` | `READ` | `READ` | `READ` | `REVIEW_ONLY` |
| Existing HistoryのMutation | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` |

## 7. 最高責任者役による動的Documentation判断

作業、担当、RoleまたはTaskごとに固定Packageを一律生成しない。その時点の最高責任者役が、最上位規則群、共通Docs／運用規則、Current Authorization、Work Unit、Role／Task境界、State Transition、Mutation Risk、Review／Human Gate、Audit／Recovery、Provider Capability、情報Loss、CostおよびContextを総合し、必要ArtifactとExact Pathを都度判断する。

これは機械的な「Dynamic Resolver」という別Subsystemを要求するものではない。通常運転で最高責任者役が担ってきた判断責任をAutomationでも維持し、許可済み到達線の内側ではActionごとの追加確認なしに適用する。

判定原則：

- Indexは、独立したNavigation／Recovery入口が必要な場合だけ作る。
- Handoffは、RoleまたはTask間で責任、Authority、入力または次Actionを移転する場合だけ作る。
- Statusは、進捗、停止、失敗、完了またはRecovery Stateを永続化する必要がある場合だけ作る。
- Review／Acceptance Eventは、独立Review、Gateまたは受領判定が存在する場合だけ作る。
- Evidenceは、監査、復元、Authority証明または再現性のために必要な場合だけ作る。
- 一つのArtifactが複数の責務をLosslessに満たせる場合、重複Fileを増やさない。
- 必要性を示せないArtifactは作らない。

Handoff、Status、Review、Request、Acknowledgementその他、Role／Task間で責任、Authority、入力、判定または次Actionを移転するArtifactには、論理的な送信元`from_role`と宛先`to_role`を必須とする。IndexはOwner、Upstream、Intended ReadersおよびStateを、Requirements／DesignはOwnerとDecision Authorityを保持する。単一Role内の機械的Evidenceへ意味のないFrom／Toを強制せず、別Roleまたはユーザーへ提出するEvidenceにはFrom／Toを付ける。Read-only Roleの記録を別Roleが代行する場合は、論理的著者と移転関係を保持する。

CoreはArtifactのExact Name、件数または固定Packageを持たない。Project Bindingが許可されたDocument Root／Classを与え、最高責任者役がWork Unit開始前または必要性判明時に対象をExact Pathへ固定する。この判断は、既存Stable文書への直書き、既存History Mutation、許可外Document Class、Authorized Root外またはExternal ActionのAuthorityを生成しない。

## 8. Normal Operation／Automation Delta

共通するもの：

- Role別実行権限。
- Role別Docs権限。
- 最高責任者役による動的Documentation判断。
- From／To、History、Evidence、Review、StopおよびEscalation契約。
- 最上位規則、Authorized Root、外部操作および破壊的Actionの境界。

差分：

- 通常運転では、ユーザーがTaskと直接やり取りし、設計へ新規要件または変更を追加できる。Project ControllerとPhase Designerは、その時点のユーザー指示を正本候補へ整合させる。
- Automationでは、ユーザーが到達線を事前承認し、Project Controllerがその線内でRoleへWork Unitを割り当てる。各Roleは最上位規則、共通Role権限およびWork Unit内で、Actionごとのユーザー確認なしに完了へ進める。
- Automationは、通常運転と同じ作業を別のRole権限表またはDocs権限表で再定義しない。

## 9. Delegation Contract

```yaml
role_view:
  authority_matrix_revision: exact_digest
  role_archetype: exact
  combined_roles: []
  authorization_instance: user_direction_or_accepted_envelope
  work_unit_id: exact
  authorized_root: manifest_reference
  allowed_paths: exact_or_manifest_reference
  allowed_actions: exact
  document_authority: exact
  documentation_judgment: responsible_role_decided_and_targets_fixed
  human_gates: exact
  prohibited_actions: exact
  evidence_contract: exact
  stop_conditions: exact
  expiration: exact
```

Phase Designerは、Automation中はProject Controllerの指示へ従う。ただし、その指示がユーザー承認済み到達線、Role AuthorityまたはWork Unitを超える場合は停止する。通常運転中は、ユーザーがPhase設計へ追加・変更した要件を取り込み、Cross-Phase影響をProject Controller／Design GovernorへEscalateする。

## 10. Stop Conditions

- Role、Authorization Instance、Work Unit、Root、Path、ActionまたはDocs Authorityの不一致。
- 最上位規則とのConflictまたは違反疑い。
- Scope内ActionとScope外Actionを分離できない。
- Providerの暗黙副作用またはTool Capabilityが不明。
- `USER_EXPLICIT`のActionが到来したがExact Authorizationがない。
- Resource、Context、ServiceまたはEvidenceの異常。

停止後はCleanup、Rollback、代替Tool、別TaskまたはScope拡張を自動実行せず、確認済み範囲とExact Stop Reasonを返す。

## 11. Project Binding Boundary

Project固有のRole名、Phase、Task、Path、ProviderおよびWork UnitはProject Manifest、Authorization EnvelopeまたはRole ViewでArchetypeへBindingする。BindingはCore MatrixのAuthority Stateを拡張できない。

## 12. Review Checklist

- [ ] 通常運転とAutomationが一つのRole／Docs Matrixを共有している。
- [ ] Mode差分がAuthorization Sourceと連結実行だけに限定されている。
- [ ] 既存Stable文書への直書きがユーザー明示に限定されている。
- [ ] 最高責任者役がWork Unitの特性から必要Artifactだけを都度判断している。
- [ ] 不要な固定Package、Exact File数またはArtifact名をCoreへHard-codeしていない。
- [ ] Role／Task間の移転ArtifactにFrom／Toがある。
- [ ] Phase Designerの通常運転／Automation時の指示経路が明確である。
- [ ] 必要に応じたPhase別Implementer配置を妨げない。
- [ ] 最上位規則とAuthorized Rootが全Role共通の絶対境界である。
- [ ] Automation用の重複Role／Docs規則を作らない。
- [ ] Project／Provider固有値がCoreから分離されている。
- [ ] 不可避なHard-codeには理由、範囲、代替不能性、除去条件およびEvidenceがある。
- [ ] Automationを理由に判断責任を固定Resolverまたは一律の人間承認へ移していない。

## 13. Related Documents

- [Task Role／Write Authority Policy](task_role_write_authority_policy_ja.md)
- [Automation Control Profile](../automation/automation_control_profile_ja.md)
- [Automation Governance Index](../automation/automation_governance_index_ja.md)
- [Research Asset Mutation Control](../operations/research_asset_mutation_control_ja.md)
- [Experimental Document-driven Task Orchestration](../operations/experimental_document_driven_codex_task_orchestration_ja.md)
