# Phase 6／8 Component Identity、Mode Default、Constitution分離 Follow-up

```yaml
document_id: phase_6_8_component_identity_mode_and_constitution_separation_followup_20260822151607
status: accepted_user_direction_planned_not_started
document_type: append_only_planned_work_followup
recorded_at: 2026-08-22 15:16:07 JST
implementation_authorized: false
```

## 1. Purpose

次の予約文書に対するユーザー追加決定を、上書きせずAppend-onlyで固定する。

1. `phase_6_0_advanced_runtime_component_identity_projection_ja_20260822150342.md`
2. `pre_phase_8_portable_margpa_constitution_package_and_runtime_identity_ja_20260822150342.md`

本Follow-upは、実装時期、Mode初期値、正式名称、Root Folder名およびGovernance DefinitionsとConstitutionの非同一性を明確化する。先行文書と解釈が衝突する場合、このユーザー追加決定を後続設計入力として優先する。

## 2. Phase 6 Implementation Order

Advanced SettingsのEnvironment／Effective Runtime Informationへ追加する次の4項目は、Phase 6開始時ではなく、**Phase 6実装ターンの最後**に実装・統合・検証する。

```text
Current Main Model
Current Guardrail Model
Current LLM-as-a-Judge Model
Current Governance Layer
```

DeepSeek Local Feasibility、Runtime Model Switch、Dynamic Context SizeおよびDynamic Max New Tokensの基盤契約はPhase 6-0で先に成立させてよい。ただし、4項目をAdvanced Settingsの統合Environment表示へ完成させる作業は、Phase 6の最終実装Subphase／Integrated UI Work Unitへ配置する。

Phase 6 Closure前に、実Runtime Identity、Settings再Open、Browser Reload、別Tab、None／Unavailable／Invalid／DegradedおよびSafe Displayを横断確認する。

## 3. Phase 8 Implementation Order

`MARGPA Constitution`のRuntime Identity、ModeおよびAdvanced Settings表示は、**Phase 8実装ターンの最後**に実装・統合・検証する。

先に次を成立させる。

1. Existing Rule／EvidenceのLossless Inventory。
2. 統合憲法のNormative Core、Manifest、Rule ID、Schema、Role ViewおよびProvider Adapter。
3. Root PackageのValidation、Revision、Digest、BindingおよびFail-closed。
4. Agent／Tool／Authority／Permissionとの分離。
5. OFF／OBSERVE／ENFORCEの実行契約。

その後、Phase 8最終実装SubphaseでAdvanced SettingsへIdentity／Revision／Mode／Binding Stateを投影する。UIを先に作り、未成立のConstitutionをActiveに見せない。

## 4. Common Mode Default

OFF／OBSERVE／ENFORCEを持つComponent／FeatureのStartup Defaultは、原則として全て`OFF`とする。

```text
Default : OFF
Userが明示Applyした場合だけ : OBSERVE／ENFORCE
```

将来、Evidence、安全性、Public ProfileまたはOperational RequirementによりDefault変更が必要になった場合は、Componentごとに別Decision、Migration、Backward Compatibility、UI表示およびHuman Acceptanceを設ける。暗黙にDefaultを変更しない。

### OFF

- 当該Component固有のEvaluation／Intervention／Evidence Callを原則0にする。
- 既存Platform Security、Sandbox、Access Control、Authority、Tool Permission、Human Approval、法令および最上位規則を解除しない。
- `OFF = allow all`と解釈しない。

### OBSERVE

- Input／Plan／Action／Output等を対象Contractで評価し、Result／Deviation／Deferred／Evidenceを生成できる。
- 当該Component固有の理由だけでMain Actionを変更、拒否または実行しない。
- Observation失敗をPassへ変換しない。

### ENFORCE

- Valid Definition／Constitution／Policy、Binding、Authority、Permission、CapabilityおよびBudgetが揃う場合だけ、登録済みActionを実行できる。
- Unknown、Invalid、Stale、Unsupported、Low ConfidenceまたはAuthority不足をSafe Allowへ変換しない。
- Mode自体はAuthorityを生成しない。

## 5. MARGPA Constitution Research Mode

`MARGPA Constitution`にも、他のGovernance Component同様に`OFF／OBSERVE／ENFORCE`を設け、Startup Defaultを`OFF`とする。

目的は、Agent／Tool／Role／TaskがConstitutionなし、観測のみ、強制適用ありの各条件でどのように振る舞うかを比較し、Constitutionが実際に統治へ効くかを再現可能に研究することである。

### Constitution OFF

- Constitution固有のRule Load／Evaluation／Interventionを行わない比較Baseline。
- 既存の最上位規則、Platform Security、Sandbox、Authority、Permission、HandoffおよびHuman Gateは引き続き有効。

### Constitution OBSERVE

- Agent／Tool／Role／TaskのPlan、Requested Action、Mutation、Handoff、EvidenceおよびCompletionをConstitution Viewに照らして評価する。
- Potential Violation、Ambiguity、Missing Rule、Stale ViewおよびDeferredをEvidence化する。
- Constitution固有Actionとして実行を止めない。ただし既存最上位規則／Platform／Authorityにより停止する場合は別責務として維持する。

### Constitution ENFORCE

- Accepted Revision／Digest、正しいRole View、Valid Bindingおよび既存Authorityの範囲内でRuleを強制する。
- 違反Actionの拒否、安全停止、上位EscalationまたはEvidence要求を、登録済みActionとして実行する。
- ConstitutionがAgent／Tool Permission、Filesystem Scope、External AuthorityまたはHuman Approvalを新規生成しない。
- Required Revision／View／Digest／Capabilityが不足する場合はFail-closedし、OBSERVEまたはOFFへSilent Downgradeしない。

比較Evidence候補：

```text
Rule Violation Attempt
Near Miss
False Positive／False Negative
Human Intervention
Task Completion Fidelity
Unauthorized Mutation Prevention
Recovery Fidelity
Latency／Token／Evidence Cost
Agent／Tool Performance Delta
```

## 6. Two Separate MARGPA Components

次の2つは名称、目的、Folder、Manifest、Identity、Revision、Digest、ModeおよびRuntime Roleが異なる**別Component**である。相互に同一視、代替または暗黙Bindingしない。

### 6.1 MARGPA Governance Definitions

```text
Root Folder Candidate／Current : definitions/
Safe Display Candidate          : MARGPA Governance Definitions v1
Runtime Role                    : LLM／Governance Point向けDefinition／Rule Corpus
Primary Consumers               : Governance Binder／Evaluator／Point Runtime
```

ARGD、DAGDその他のGovernance Definition／Referenceを扱う。Folder `definitions/`のIdentity、ManifestおよびBinding StateからCurrent Governance Layerを投影する。

### 6.2 MARGPA Constitution

```text
Root Folder : constitution/
Safe Display: MARGPA Constitution <revision>
Runtime Role: Development／Agent／Tool／Role／Task運用の統合憲法
Primary Consumers: Agent／Tool Runtime、Task Orchestration、Role／Provider View、Governance Enforcement
```

Phase 8前Gateで、運用ルール、絶対禁止、Authority、Docs、Mutation、Handoff、Review、Recovery、Backup、Git、Cost、IncidentおよびNear Missを統合する。

### 6.3 Separation Invariants

- `definitions/`と`constitution/`を同じFolder、ManifestまたはVersionへ統合しない。
- Governance DefinitionsがActiveでもConstitutionがActiveとは限らない。
- ConstitutionがENFORCEでもGovernance Definitionsが存在するとは限らない。
- 一方がNone／Invalid／Unavailableでも、もう一方のStateを推測しない。
- 一方のMode変更で、もう一方のModeを暗黙変更しない。
- `MARGPA`という共通接頭辞だけを根拠に同一Componentと扱わない。
- UI、API、EvidenceおよびStatusで別Field／別Identityとして投影する。

## 7. Exact Root Folder Decision

Project Root直下へ配置するConstitution PackageのFolder名は、ユーザー決定により次で固定する。

```text
margpa-runtime-llm/
├── definitions/
└── constitution/
```

`margpa_constitution/`、`MARGPA_Constitution/`その他の重複Prefix付きFolder名は採用しない。

既存Docsを無差別にMoveしない。`docs/`は設計、説明、History、EvidenceおよびMigration Traceを保持し、Accepted Normative Coreを`constitution/`へPromote／Compileする構造とする。

## 8. Advanced Settings Target State

Phase 6最終実装後の候補：

```text
Current Main Model         : <identity> | None／Unavailable
Current Guardrail Model    : <identity> | None／Unavailable
Current LLM-as-a-Judge     : <identity> | None／Unavailable
Current Governance Layer   : MARGPA Governance Definitions <revision> | None／Invalid
```

Phase 8最終実装後に追加する候補：

```text
Current Constitution       : MARGPA Constitution <revision> | None／Invalid
Constitution Mode          : OFF／OBSERVE／ENFORCE
Constitution Binding State : active／unavailable／invalid／degraded
```

Governance LayerとConstitutionを別Row／別Contractとして表示する。

## 9. Non-Authorization

本Follow-upは実装順と将来要件の予約であり、次を許可しない。

- Phase 6／8開始。
- `constitution/`Folder作成。
- Existing Docs／Rule／DefinitionのMove、編集、削除または再編成。
- Source／Frontend／Test／Config変更。
- Agent／Tool／Constitution Runtime開始。
- Git／GitHub、Network、External Service、User Data、Secretまたは課金操作。

