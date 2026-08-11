# Automation Governance Index

```yaml
document_id: automation_governance_index
status: current
normative: true
language: ja
created_at: 2026-08-09 18:11:00 JST
updated_at: 2026-08-11 11:34:01 JST
owner_role: プロジェクト責任者兼設計統括者役
decision_authority: user
provider_neutral: true
project_neutral_core: true
```

## 1. Purpose

本Directoryは、Task Orchestration、自動化Control、Pilot Evidence、Provider差、Human Gate、停止、復旧および将来の統合憲法への入力を、一つの正本入口から追跡するための専用領域である。

自動化関連EvidenceをOperations、Phase、会話またはProvider固有設定へ分散させず、本IndexからStable、History、Phase実験および憲法計画を解決できる状態を維持する。

本DirectoryはAutomation固有のControl、連結実行差分およびEvidenceを保持する。通常運転と共通するRole権限、Docs権限、Task Artifact、From／To、HistoryおよびReview規則を複製せず、[Role Authority Matrix](../task_roles/role_authority_matrix_ja.md)を参照する。

## 2. Canonical Structure

```text
docs/project/shared/automation/
├─ automation_governance_index_ja.md
├─ automation_control_profile_ja.md
├─ automation_governance_evidence_log_ja.md
└─ pre_pilot_governance_baseline_ja.md

docs/project/shared/history/automation/
└─ <stable_name>_<phase>_<language>_YYYYMMDDHHMMSS.md
```

Stable文書を変更する前後に、同名系統の完全SnapshotをHistoryへ保存する。HistoryはAppend-onlyであり、既存Snapshotを要約、再解釈または上書きしない。

## 3. Stable Documents

- [Automation Control Profile](automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](automation_governance_evidence_log_ja.md)
- [Pre-pilot Automation Governance Baseline](pre_pilot_governance_baseline_ja.md)
- [Role Authority Matrix](../task_roles/role_authority_matrix_ja.md)

## 4. Related Normative Sources

- [Research Asset Mutation Control](../operations/research_asset_mutation_control_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Experimental Document-driven Task Orchestration](../operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Task Execution Routing／Cost Control](../operations/task_execution_routing_and_cost_control_ja.md)
- [Git Workflow Policy](../operations/git_workflow_policy_ja.md)
- [Cross-project Development Governance Constitution Plan](../operations/cross_project_development_governance_constitution_plan_ja.md)
- [Constitution Research Index](../constitution/constitution_research_index_ja.md)
- [Constitution Source Evidence Register](../constitution/constitution_source_evidence_register_ja.md)

## 5. Supremacy Boundary

Automation Level、Role、Task数、Provider Capability、Phase ScopeまたはProject Scopeに関係なく、次を上書きできない。

```text
明示的に指定されたAuthorized Root／Allowed Path外へ、
ユーザーの個別許可なく触れてはならない。
```

「触れる」にはRead、List、Search、Stat、Execute、Create、Copy、Move、Rename、Delete、Permission／ACL、Temporary Artifact、Cache、Symlink追跡、External MountおよびToolの暗黙Accessを含む。

本規則はプロジェクト責任者兼設計統括者役、将来の上位Role、全Task、全Agent、全Tool、全Provider、Automation OFF／任意の自動化段階へ適用する最上位規則群の一つである。Roleや自動化範囲から例外を生成しない。

最上位規則群は、ユーザーまたはユーザーが明示指定した人間が将来追加を指示できる意味で閉集合としない。AI、Role、Task、Agent、Tool、AutomationまたはProviderは、最上位規則の新規追加、文言変更、削除、並替え、例外化、候補登録またはそれらの指示を自発的に行ってはならない。できるのは事実、Incident、Conflictまたは不明点を報告して停止することだけである。当該最上位規則へのDocs反映も、人間が対象とActionを明示指示した範囲の代行に限る。

## 6. Role State

当面、Project全体を統括する現在Taskは`プロジェクト責任者兼設計統括者役`として両責務を兼務する。

- Project ResponsibilityとDesign GovernanceのStable／History／Recovery Folderは両方維持する。
- Recoveryは分離したまま相互参照する。
- 兼務はAuthorityの合算、最上位規則からの免除またはUser Gateの代理を意味しない。
- Pilot開始Transitionが成立した時点で、Provider Capabilityが許せば現在Task名を`プロジェクト責任者兼設計統括者役`へ変更する。
- Task名変更が失敗または不可能な場合は、Role Identity不一致としてPilot開始を停止し、推測で続行しない。

## 7. Pilot Start Gate and Effective Authority

Automation Pilotは、共通Role／Docs AuthorityへAccepted Envelopeによる連結実行差分を重ねて起動する。通常運転用とAutomation用のRole権限表またはDocs権限表を別々に作らない。

1. Pilot Design／Role Authority Matrix／Envelope／Handoff／Stop／EvidenceのReview合格。
2. 対象Automation Profile、Role Binding、Authorized Root、Allowed Paths／Actions、Task上限、期限およびHuman GateのFreeze。
3. ユーザーによるExact EnvelopeのAcceptance。
4. プロジェクト責任者兼設計統括者役による「準備OK。いつでも開始出来ます。」の明示。
5. その後のユーザーによる「ok。では開始する。」の明示。

片方の発言、過去の同意、類似表現、会話の流れ、設計完了またはTask作成Capabilityだけでは開始しない。Ready宣言後に状態が変化した場合はReadyを失効させ、再Preflightする。

Automation LevelとControl Stateを分離する。Control Stateは`OFF／ARMED／ON／PAUSED／EMERGENCY_STOP`を基本状態とする。`ON`後は[Role Authority Matrix](../task_roles/role_authority_matrix_ja.md)とAccepted Envelopeの交差にある`ROLE_ALLOWED` Actionを、承認済み到達線まで連結実行できる。

Docs Authorityは共通Role契約の独立Dimensionとし、Role Viewは`READ／CREATE_NEW／APPEND_NEW／EXISTING_WRITE_USER_EXPLICIT／REVIEW_ONLY／DENY`を明示する。既存Stable文書への直書きは、Modeを問わず、ユーザーがExact TargetとActionを明示した場合だけ成立する。必要ArtifactはMode共通のDynamic Documentation Requirement Resolverで解決し、Role／Task間の移転ArtifactにだけFrom／Toを要求する。

## 8. General Hard-code Prohibition／Portability

ユーザーの明示指示により、可能な限りHard-codeを避け、どうしても必要な場合だけ管理された例外として許可することを最上位規則群へ追加する。本規則はAutomation／Constitutionだけでなく、通常運転、全設計、全Role、全Task、全Agent、全Toolおよび全Providerに適用する。

再利用されるCoreへ、次を可能な限りHard-codeしてはならない。

- 特定Project名、Repository、Absolute Pathまたは固定Directory構造
- 特定Phase番号、Task名、個人情報、CredentialまたはAccount
- 特定Provider、Model Vendor、Tool名、Command、UIまたはCloud
- 特定Agent Frameworkまたは一つの開発方式だけに通用する状態遷移
- 固定Artifact Package、Artifact名／件数、固定Thresholdまたは固定Role Binding

CoreはCapability、Authority、Evidence、State、Scope、Stop、RecoveryおよびHuman Gateで記述する。Project固有値はProject Manifest、Provider固有操作はProvider Adapter、Task固有値はAuthorization Envelopeへ分離する。

Codex、Claude Codeその他Providerを併用する場合も、同一Core ContractをAdapter越しに適用し、Provider差を理由にAuthority、禁止、EvidenceまたはStopを弱めない。

Hard-codeは、技術的または論理的に不可避で、同等の抽象化手段では契約を維持できない場合に限る。理由、代替案、代替不能性、Exact Scope、Owner、変更・Review方法、除去／Migration条件、TestおよびEvidenceを記録する。便宜、速度、現行環境への最適化または「一時的」であることだけを理由にしない。

Project Manifest、Authorization Envelope、Role View、ConfigまたはFreeze EventでExact Runtime ValueをBindingすることは、Coreへの固定埋込みと区別する。

### 8.1 Dynamic Documentation Requirement Resolver

Work Unitごとに固定のIndex／Handoff／Status／Review Packageを要求しない。Work Unit種別、Role／Task境界、State Transition、Mutation Risk、Review／Human Gate、Audit／Recovery要件およびProvider Capabilityから、必要Artifactだけを動的に解決する。

IndexはNavigation／Recovery入口、Handoffは責任／Authority／入力／次Actionの移転、StatusはState永続化、Review／Acceptanceは独立判定、Evidenceは監査／復元／再現性が必要な場合だけ作る。一つのArtifactが複数責務をLosslessに満たせる場合は統合し、不要Artifactを作らない。

Project Bindingが許可Document Root／Classを与え、各Work Unit開始時にResolver結果をExact PathへFreezeする。Resolverは既存Stableへの直書き、既存History Mutation、許可外Document ClassまたはAuthorized Root外へのAuthorityを生成しない。

## 9. Evidence Accumulation

Pilot、通常運用、Incident、Near MissまたはProvider併用から、Automation／Constitutionへ直接使える知見を得た場合は[Automation／Governance Evidence Log](automation_governance_evidence_log_ja.md)へ累積追加する。

記録対象：

- 成功だけでなく、偶然成功、停止遅延、Human Interventionおよび未検知領域
- Automation Levelの過剰／不足
- Provider間HandoffとCapability差
- Scope、Folder Boundary、Authority、Cost、ContextおよびRecovery
- 新規Project／既存Projectへの移植性
- Agent／Tool／Agent-driven Developmentへの適用可能性

Evidenceの追加だけでRuleを自動変更しない。最上位Ruleの追加・変更・削除・例外化は、人間の明示指示なしに検討対象、候補またはDocs変更として扱わない。

憲法へのSource採用、Chapter候補、ConflictおよびNormative昇格状態は、Automation Evidence Logと分離して[Constitution Source Evidence Register](../constitution/constitution_source_evidence_register_ja.md)へ登録する。Automation側は事実Evidence、Constitution側はSource Trace付き制度候補を担当する。

## 10. Current State

```text
Combined Role          : selected／task title not changed yet
Automation Profile     : design draft／manual state maintained
Control State          : PAUSED／ROLE_AUTHORITY_DESIGN
Pilot                  : initial unit closed／retest not started
Role Authority Matrix  : design candidate／pending user review
Document Authority     : mode-invariant common matrix corrected／dynamic resolver projected／role view draft-2 pending review
Dual Consent           : not completed
Independent Task       : not created
Multi-provider Use     : future candidate／undecided
Permission Hardening   : future candidate／undecided
Mechanical Enforcement : research reservation only
Git／External Mutation : none
```

## 11. Latest Phase Evidence

- [Phase 2 Pre-pilot Governance Full Consolidation](../../phases/phase_2/history/operations/phase_2_pre_pilot_governance_full_consolidation_20260809195620.md)
- [Phase 2 Documentation Index Snapshot](../../phases/phase_2/history/index/documentation_index_20260809195620.md)
- [Mode-invariant Role／Document Authority Correction](../../phases/phase_2/history/operations/phase_2_0_mode_invariant_role_and_document_authority_correction_20260811104642.md)
- [Phase 2 Documentation Index Snapshot 20260811104642](../../phases/phase_2/history/index/documentation_index_20260811104642.md)

現在のControl Stateは`PAUSED／ROLE_AUTHORITY_DESIGN`である。Pilot再開、新Task作成、Task名変更、Permission変更、機械的強制、CommitまたはPushを実行済みと解釈しない。
