# Automation Governance Index

```yaml
document_id: automation_governance_index
status: current
normative: true
language: ja
created_at: 2026-08-09 18:11:00 JST
updated_at: 2026-08-09 18:41:34 JST
owner_role: プロジェクト責任者兼設計統括者役
decision_authority: user
provider_neutral: true
project_neutral_core: true
```

## 1. Purpose

本Directoryは、Task Orchestration、自動化Control、Pilot Evidence、Provider差、Human Gate、停止、復旧および将来の統合憲法への入力を、一つの正本入口から追跡するための専用領域である。

自動化関連EvidenceをOperations、Phase、会話またはProvider固有設定へ分散させず、本IndexからStable、History、Phase実験および憲法計画を解決できる状態を維持する。

## 2. Canonical Structure

```text
docs/project/shared/automation/
├─ automation_governance_index_ja.md
├─ automation_control_profile_ja.md
└─ automation_governance_evidence_log_ja.md

docs/project/shared/history/automation/
└─ <stable_name>_<phase>_<language>_YYYYMMDDHHMMSS.md
```

Stable文書を変更する前後に、同名系統の完全SnapshotをHistoryへ保存する。HistoryはAppend-onlyであり、既存Snapshotを要約、再解釈または上書きしない。

## 3. Stable Documents

- [Automation Control Profile](automation_control_profile_ja.md)
- [Automation／Governance Evidence Log](automation_governance_evidence_log_ja.md)

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

最上位規則群は現時点の列挙で閉じない。Pilot、Incident、Near Miss、Agent／Tool実装または新しいProviderから追加候補を受け入れる。ただしEvidence、Conflict Review、検知、違反時動作、RecoveryおよびUser Decisionなしに、Automation主体が自己判断で最上位規則を追加・変更・免除してはならない。

## 6. Role State

当面、Project全体を統括する現在Taskは`プロジェクト責任者兼設計統括者役`として両責務を兼務する。

- Project ResponsibilityとDesign GovernanceのStable／History／Recovery Folderは両方維持する。
- Recoveryは分離したまま相互参照する。
- 兼務はAuthorityの合算、最上位規則からの免除またはUser Gateの代理を意味しない。
- Pilot開始Transitionが成立した時点で、Provider Capabilityが許せば現在Task名を`プロジェクト責任者兼設計統括者役`へ変更する。
- Task名変更が失敗または不可能な場合は、Role Identity不一致としてPilot開始を停止し、推測で続行しない。

## 7. Pilot Start Gate

Automation Pilotは次が全て成立した時だけ、一斉に`active`へ遷移する。

1. Pilot Design／Envelope／Handoff／Stop／RecoveryのReview合格。
2. Pilot開始前Checkpointとして、対象差分のReview、ユーザーによる当該Commit／Pushの明示承認、Commit／PushおよびLocal／Remote一致確認。
3. ユーザーによる大規模Backup取得完了の明示報告。
4. プロジェクト責任者兼設計統括者役による「準備OK。いつでも開始出来ます。」の明示。
5. その後のユーザーによる「ok。では開始する。」の明示。
6. 対象Automation Profile、Authorized Root、Allowed Actions、Task上限、期限およびHuman Gateの最終一致。

片方の発言、過去の同意、類似表現、会話の流れ、設計完了またはTask作成Capabilityだけでは開始しない。Ready宣言後に状態が変化した場合はReadyを失効させ、再Preflightする。

## 8. Portability／Hard-code Prohibition

AutomationおよびConstitutionのNormative Coreへ、次をHard-codeしてはならない。

- 特定Project名、Repository、Absolute Pathまたは固定Directory構造
- 特定Phase番号、Task名、個人情報、CredentialまたはAccount
- 特定Provider、Model Vendor、Tool名、Command、UIまたはCloud
- 特定Agent Frameworkまたは一つの開発方式だけに通用する状態遷移

CoreはCapability、Authority、Evidence、State、Scope、Stop、RecoveryおよびHuman Gateで記述する。Project固有値はProject Manifest、Provider固有操作はProvider Adapter、Task固有値はAuthorization Envelopeへ分離する。

Codex、Claude Codeその他Providerを併用する場合も、同一Core ContractをAdapter越しに適用し、Provider差を理由にAuthority、禁止、EvidenceまたはStopを弱めない。

## 9. Evidence Accumulation

Pilot、通常運用、Incident、Near MissまたはProvider併用から、Automation／Constitutionへ直接使える知見を得た場合は[Automation／Governance Evidence Log](automation_governance_evidence_log_ja.md)へ累積追加する。

記録対象：

- 成功だけでなく、偶然成功、停止遅延、Human Interventionおよび未検知領域
- Automation Levelの過剰／不足
- Provider間HandoffとCapability差
- Scope、Folder Boundary、Authority、Cost、ContextおよびRecovery
- 新規Project／既存Projectへの移植性
- Agent／Tool／Agent-driven Developmentへの適用可能性

Evidenceの追加だけでRuleを自動変更しない。Rule昇格には正本更新、History、ReviewおよびUser Decisionを必要とする。

憲法へのSource採用、Chapter候補、ConflictおよびNormative昇格状態は、Automation Evidence Logと分離して[Constitution Source Evidence Register](../constitution/constitution_source_evidence_register_ja.md)へ登録する。Automation側は事実Evidence、Constitution側はSource Trace付き制度候補を担当する。

## 10. Current State

```text
Combined Role          : selected／task title not changed yet
Automation Profile     : design draft／manual state maintained
Pilot                  : not started
Pre-pilot Backup       : required／not yet confirmed
Pre-pilot Git Checkpoint: required／not yet executed
Dual Consent           : not completed
Independent Task       : not created
Multi-provider Use     : future candidate／undecided
Git／External Mutation : none
```
