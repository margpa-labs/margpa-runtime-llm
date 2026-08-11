# Role Authority Matrix

```yaml
document_id: role_authority_matrix
status: design_candidate_pending_user_review
normative_core: true
language: ja
created_at: 2026-08-11 01:09:24 JST
owner_role_archetype: design_governor
decision_authority: user
provider_neutral: true
project_neutral_core: true
default_deny: true
```

## 1. Purpose

本書は、Roleごとの責務とAutomation Envelopeごとの許可を結合し、「どの主体が、どのScopeで、どのActionを、どのGateまで自律実行できるか」を解決する権限表である。

通常運用とAutomation Modeを混同しない。Automation Modeでは、人間がAccepted化したEnvelopeとRole Authorityの共通範囲に対し、Actionごとの再確認なしで自律実行を許す。

本書は最上位規則の追加、変更、削除、並替え、例外化または候補登録を行わない。最上位規則を変更できるのはユーザーまたはユーザーが明示指定した人間だけである。

## 2. Effective Authority Resolution

```text
Effective Authority
  = Human-defined Supreme Rulesに適合
  ∩ Accepted Automation Envelope
  ∩ Role Authority
  ∩ Assigned Work Unit Scope
  ∩ Available Provider Capability
```

優先順位：

```text
Human-defined Supreme Rules
  > Accepted Automation Envelope
  > Role Authority Matrix
  > Work Unit Handoff／Role View
  > Provider Adapter
  > Ordinary Operational Defaults
```

- Role Authorityは「そのRoleに与え得る上限」である。Role名だけで権限は有効化されない。
- Accepted Envelopeは「今回のScopeで実際に有効な権限」を与える。
- EnvelopeがRoleの上限を超える場合、別Roleの明示的兼務またはRole Matrixの人間による改訂がない限り拒否する。
- Envelope内かつRole内のActionは、通常運用のActionごとの確認を再要求しない。これがAutomation Modeの自律実行である。
- Envelope外、Role外、Scope外、Capability不明または最上位規則とのConflictは、拡張解釈せず停止する。

## 3. Authority States

| Code | Meaning | Automation `ON`での動作 |
|---|---|---|
| `AUTO` | Role上限内で自律実行可能 | EnvelopeとWork Unitに含まれれば再確認なしで実行 |
| `REVIEW` | Read／Review／判定は可能、対象のMutationは不可 | Evidenceを返し、OwnerへHandoff |
| `HUMAN_GATE` | 人間のExact Authorizationが必要 | そのActionの前で停止 |
| `DENY` | AI Sideで実行不可 | 拒否し、代替手段も実行しない |

`ARMED`はAuthorityがFrozenだが未開始、`ON`は自律実行可能、`PAUSED`と`EMERGENCY_STOP`は新規Action不可を意味する。

## 4. Abstract Role Archetypes

Normative Coreでは固有のTask名やProvider名ではなく、次のRole Archetypeを使う。Project固有のRole名はManifestまたはRole Bindingで解決する。

| Archetype | Primary Responsibility |
|---|---|
| `project_controller` | Project全体、Role編成、Envelope実行、Phase Gate、最終Review |
| `design_governor` | Cross-Phase要件、Architecture、Canonical Meaning、Role Authority整合 |
| `phase_designer` | Assigned PhaseのRequirements／Architecture／ADR／Handoff |
| `implementer` | Accepted Designに従うSource／Test／Script／Config実装 |
| `external_docs_editor` | Public Docs／README／対外Metadataの作成 |
| `reviewer` | Read-only Review、Test Evidence評価、Finding分類 |
| `operator` | 人間が承認したExternal／Platform／Git Actionの実行 |

一つのTaskが複数Roleを兼務する場合、EnvelopeにRole Setを明記する。兼務は未列挙RoleのAuthorityまたは各RoleのScope外Authorityを生成しない。

## 5. Role Capability Matrix

`AUTO`は、Accepted Envelopeに同じAction、Scope、Target Classおよび上限が記載されている場合だけ有効である。

| Action Class | project_controller | design_governor | phase_designer | implementer | external_docs_editor | reviewer | operator |
|---|---|---|---|---|---|---|---|
| Authorized Docs／Source Read | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `REVIEW` |
| Project／Cross-Phase設計書更新 | `REVIEW` | `AUTO` | `REVIEW` | `DENY` | `DENY` | `REVIEW` | `DENY` |
| Assigned Phase設計書更新 | `REVIEW` | `REVIEW` | `AUTO` | `DENY` | `DENY` | `REVIEW` | `DENY` |
| Source／Tests／Scripts実装 | `REVIEW` | `REVIEW` | `REVIEW` | `AUTO` | `DENY` | `REVIEW` | `DENY` |
| Config／Dependency Metadata変更 | `REVIEW` | `REVIEW` | `REVIEW` | `AUTO` | `DENY` | `REVIEW` | `DENY` |
| Public Docs／README／対外Metadata | `REVIEW` | `REVIEW` | `REVIEW` | `DENY` | `AUTO` | `REVIEW` | `DENY` |
| History／Status／Evidenceの新規追加 | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `REVIEW` |
| 担当成果のTest／Static Check | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `REVIEW` |
| Finding作成／Review結果記録 | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `REVIEW` |
| Task作成／命名／Handoff／Follow-up | `AUTO` | `REVIEW` | `REVIEW` | `DENY` | `DENY` | `DENY` | `DENY` |
| Role内のRoutine判断／修正／再Test | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `AUTO` | `REVIEW` | `REVIEW` |
| Phase Final Gate案／GO・ADJUST・STOP案 | `AUTO` | `AUTO` | `REVIEW` | `REVIEW` | `REVIEW` | `AUTO` | `DENY` |
| Phase完了宣言／次Phase開始 | `HUMAN_GATE` | `HUMAN_GATE` | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` |
| Commit／Push／PR／Merge／Tag／Release | `HUMAN_GATE` | `HUMAN_GATE` | `DENY` | `DENY` | `DENY` | `REVIEW` | `AUTO` |
| Cloud／External Service／Public Access変更 | `HUMAN_GATE` | `HUMAN_GATE` | `DENY` | `DENY` | `DENY` | `REVIEW` | `AUTO` |
| Secret／Credential／Private KeyへのAccess | `HUMAN_GATE` | `HUMAN_GATE` | `DENY` | `DENY` | `DENY` | `DENY` | `AUTO` |
| Delete／Overwrite／Permission／ACL／Destructive | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` | `DENY` | `AUTO` |
| Incident後Cleanup／Rollback | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` | `REVIEW` | `AUTO` |
| Authorized Root／Allowed Path外Access | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` | `HUMAN_GATE` |
| 最上位規則の追加／変更／削除／例外化 | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` | `DENY` |

`operator`の`AUTO`は、Human Gateで承認済みのExact Actionを実行する意味であり、独立した意思決定Authorityではない。

## 6. Automation Mode Contract

Automation `ON`の間、次の条件を全て満たすActionは自律実行できる。

```yaml
autonomous_action_required_conditions:
  control_state: ON
  envelope_status: accepted_and_unexpired
  role_binding: exact_match
  work_unit: active_and_within_limit
  target_root: authorized
  target_path: allowed
  action_class: envelope_allowed
  role_matrix_state: AUTO
  supreme_rule_conflict: none
  required_human_gate: already_satisfied_or_not_applicable
  provider_capability: available_without_scope_expansion
```

自律実行できる例：

- Phase Designerが、承認済みPhase Work UnitのRequirements／Architecture／ADRを作成し、整合を再検査する。
- Implementerが、承認済みHandoffのSource／Tests／Scriptsを実装し、Test Findingを修正し、同じWork Unitで再Testする。
- Project Controllerが、Envelopeに列挙されたTaskを作成し、命名、Handoff、Status回収、Reviewおよび承認済み次Unitへの連結を行う。
- 各Roleが、自分のScope内でFindingを解決し、未解決またはScope外だけを上位RoleへEscalateする。

次は自律実行できない。

- EnvelopeにないTask、Role、Path、Action、External TargetまたはMutation Classの追加。
- `REVIEW`、`HUMAN_GATE`または`DENY`のActionを`AUTO`と解釈すること。
- 実行途中で「必要になった」ことを新規Authorityの根拠にすること。
- Roleを自分で追加、兼務、交代または拡張すること。
- 最上位規則を通常運用規則と同じようにEnvelopeで置換すること。

## 7. Ordinary Mode Boundary

Automation `OFF`またはEnvelope未Acceptedの場合、本Matrixの`AUTO`はStanding Mutation Authorizationにならない。通常運用では従来どおり、ユーザーの個別指示と対象ごとの運用Gateに従う。

## 8. Human Gates and Absolute Denials

`HUMAN_GATE`は、対象、Action、Root／Path、実行主体、有効期限およびStop条件を人間が明示した場合だけ開く。過去のGate、類似Actionまたは上位Roleから継承しない。

最上位規則の編集AuthorityはAI SideのどのRole、Task、Agent、Tool、Provider、Automation Levelにも与えない。人間の明示指示を文書へ反映する代行作業は可能だが、意味、対象または例外を拡張しない。

Human-private Recovery AssetはAI Control PlaneのInput、Read Target、EvidenceまたはActivation Gateにしない。本Matrixはその存在、場所または状態を要求しない。

## 9. Delegation Contract

Project ControllerがTaskを作成する場合、Taskに次のRole Viewを渡す。

```yaml
role_view:
  authority_matrix_revision: exact_digest
  role_archetype: exact
  combined_roles: []
  envelope_id: exact
  work_unit_id: exact
  authorized_root: manifest_reference
  allowed_paths: exact_or_manifest_reference
  allowed_actions: exact
  human_gates: exact
  prohibited_actions: exact
  evidence_contract: exact
  stop_conditions: exact
  expiration: exact
```

TaskはRole Viewを受け取っただけでActionを開始せず、ACKで一致を返す。Control Stateが`ON`になった後は、Role Viewの`AUTO`範囲を自律実行する。

## 10. Stop Conditions

- Role、Envelope、Work Unit、Root、Path、ActionまたはControl Stateの不一致。
- 最上位規則とのConflictまたは違反疑い。
- Scope内ActionとScope外Actionを分離できない。
- Providerの暗黙副作用またはTool Capabilityが不明。
- Human Gateの必要なActionが到来。
- Resource、Context、ServiceまたはEvidenceの異常。

停止後はCleanup、Rollback、代替Tool、別TaskまたはScope拡張を自動実行せず、確認済み範囲とExact Stop Reasonを返す。

## 11. Project Binding Boundary

Project固有のRole名、Phase、Task、Path、ProviderおよびWork Unitは本Coreに記載せず、Project Manifest、Authorization EnvelopeまたはRole ViewでArchetypeへBindingする。BindingはCore MatrixのAuthority Stateを拡張できない。

## 12. Review Checklist

- [ ] 全Roleの上限Authorityが定義されている。
- [ ] 通常運用とAutomation Modeが分離されている。
- [ ] `AUTO`と`HUMAN_GATE`の境界が明確である。
- [ ] 最上位規則が全AI Roleに対し絶対境界である。
- [ ] Envelope内Routine Actionが個別再確認を要求しない。
- [ ] Envelope外Actionが自動拡張されない。
- [ ] Project／Provider固有値がCoreから分離されている。
- [ ] Human-private Recovery AssetがAI Gateに含まれていない。

## 13. Related Documents

- [Task Role／Write Authority Policy](task_role_write_authority_policy_ja.md)
- [Automation Control Profile](../automation/automation_control_profile_ja.md)
- [Automation Governance Index](../automation/automation_governance_index_ja.md)
- [Research Asset Mutation Control](../operations/research_asset_mutation_control_ja.md)
- [Experimental Document-driven Task Orchestration](../operations/experimental_document_driven_codex_task_orchestration_ja.md)
