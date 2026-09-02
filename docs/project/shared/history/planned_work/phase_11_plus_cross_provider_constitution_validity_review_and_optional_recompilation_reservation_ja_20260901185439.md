# Phase 11以降 Cross-provider Constitution妥当性評価／任意再編纂予約

```yaml
document_id: phase_11_plus_cross_provider_constitution_validity_review_and_optional_recompilation_reservation_20260901185439
document_type: append_only_planned_work_reservation
document_state: reserved_not_started_timing_unknown
language: ja
recorded_at: 2026-09-01 18:54:39 JST
decision_authority: user
project_stage: individual_r_and_d_poc_mvp_portfolio
phase_10_scope_changed: false
phase_10_gate: false
mvp_blocker: false
earliest_target: phase_11_plus_after_phase_10_constitution_and_mvp
implementation_authorized: false
```

## 1. User Decision

Phase 10で予定している次の内容は変更しない。

- Project-wide All-Docs Integration。
- Shared Constitution編纂。
- Portable Autonomous Development Governance Package。
- Full Runtime Constitution。
- 既定の二周走査、Provenance、Revision、Gap AuditおよびFreeze。

Phase 10では、Cross-provider外部評価、追加の新規Task評価または評価結果によるConstitution再編纂を行わない。これらをPhase 10へ入れるとMVP完成がさらに遠のくためである。

### 1.1 評価対象は三系統すべて

Phase 11以降の独立妥当性評価は、次の三Artifact系統を**全て**対象にする。一つだけを代表評価して他の妥当性を推定しない。

```text
1. <project-root>/constitution/
   現Repositoryでは margpa-runtime-llm/constitution/
   RuntimeのChat／Agent／ToolへBindingするMachine-readable Full Runtime Constitution

2. <project-root>/docs/project/shared/constitution/
   Development Automation／Cross-provider運用のRepository内Shared Constitution

3. <parent-root>/portable-autonomous-development-governance-package/
   Portable Autonomous Development Governance Package
   短縮名: PADG Package
```

評価は三系統それぞれの単体妥当性に加え、次の相互整合も扱う。

- Shared ConstitutionからRuntime Constitutionへの変換／BindingでAuthorityが増減していないか。
- Shared ConstitutionからPADG PackageへのSanitize／Parameterize／Portable化でRuleが欠落またはProject固有化していないか。
- PADG PackageからSource ProjectへAuthorityやProvider固有設定が逆流していないか。
- Runtime、Development、Portableの責務境界が混ざっていないか。
- Rule ID、Revision、Source Pointer、Digest、ExceptionおよびSupersessionを三系統間で追跡できるか。

必要な場合の再編纂も三系統ごとにDispositionを分ける。ある一系統のFindingだけで三系統すべてを一括Overwriteしない。

## 2. Phase 11以降の予約

Phase 10で作成したDocs統合済みConstitutionが実際に妥当かを、Phase 11以降の時期未定Programで複数の独立視点へ評価させる可能性を予約する。

評価候補：

- Current Task Contextを継承しない新規中立Codex Task。
- Claudeの独立Thread／Task。
- GPT通常Thread。
- 必要に応じて、他Provider／Modelの独立Evaluator。

各Evaluatorへは、Constitution Artifact、Source Inventory、Provenance、Phase 10 Gap Audit、Evaluation QuestionsおよびClaim Boundaryだけを渡す。既存Controllerの結論へ迎合させる誘導Promptを避ける。

## 3. Evaluation Purpose

評価対象：

- Userの最新Decisionと矛盾しないか。
- Historical Incidentを普遍Ruleへ過剰昇格していないか。
- Provider固有FailureをCommon Ruleと混同していないか。
- Capability／Permission／Authority／Stop／Continue／Recoveryを分離できているか。
- 過剰停止と過剰自律を両方統治できるか。
- User Attention／Resource Costを正しく評価しているか。
- Runtime Constitution、Development ConstitutionおよびPADGの責務が混ざっていないか。
- 別Project／別Providerへ移植可能か。
- Rule同士にConflict、Circular Dependency、抜け、過剰制約または実行不能条件がないか。
- Evidence、Exception、Amendment、RevisionおよびRollbackが追跡可能か。

## 4. Feedback／Recompilation Flow

```text
Phase 10 三系統Artifact v1／Frozen Revision
→ independent neutral evaluations
→ provider/model別Findingを分離
→ Runtime／Shared／PADG別と相互整合Findingを分離
→ Codex ControllerへFeedback
→ Source Evidenceと照合
→ User Decision
→ 必要な系統だけv2を再編纂し、相互整合を再検証
```

多数決でRuleを変更しない。Evaluatorの人数、Provider名、慎重さまたは迎合性だけを正しさの根拠にしない。各Findingを一次Evidence、Current User Decision、Runtime BehaviorおよびAuthority Boundaryへ照合する。

再編纂する場合、Phase 10版を上書きまたは消去せず、Revision、Correction、Supersession、ReasonおよびMigration Impactを保持する。

## 5. Neutrality／Privacy Boundary

- 新規中立Taskへ過去会話Contextを自動継承させない。
- 必要なRepository Artifactだけを明示する。
- User個人情報、無関係な別Project／別Account情報または特定の個人名を評価Packageへ混入させない。
- Provider Memoryを正本にしない。
- EvaluatorへWrite／Git／Network／External Message／Closure Authorityを自動付与しない。
- Evaluation ReturnはCandidate Findingであり、Constitution変更Authorityではない。

## 6. Entry Gate

本Programを開始できるのは次を全て満たす時だけとする。

1. Phase 10の予定Scopeが完了している。
2. MVPを遅延させない時点に到達している。
3. UserがCross-provider評価開始を明示する。
4. 評価対象RevisionとSource Packageが固定されている。
5. 利用可能量、金銭、時間およびHuman Attentionに余裕がある。

## 7. Non-goal

本予約はPhase 10のScope、Acceptance、工程またはClosure条件を変更しない。Phase 10で第三者評価を追加実施するAuthorityを与えない。Phase 10で作成するRuntime Constitution、Shared ConstitutionまたはPADG Packageを暫定失敗扱いするものでもなく、三系統のいずれか／全てを必ず再編纂する決定でもない。

```text
Phase 10:
  planned Constitution work stays unchanged

Phase 11+:
  optional independent validity review
  optional recompilation only after evidence and user decision
```
