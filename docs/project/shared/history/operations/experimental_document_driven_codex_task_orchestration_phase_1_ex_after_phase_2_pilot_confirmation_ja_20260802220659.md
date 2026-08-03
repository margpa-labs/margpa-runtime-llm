# Experimental Document-driven Codex Task Orchestration

```yaml
document_id: experimental_document_driven_codex_task_orchestration
status: planned_experiment
normative: false
language: ja
created_at: 2026-08-02 21:34:43 JST
updated_at: 2026-08-02 22:06:59 JST
owner: 設計統括者役
selected_pilot: phase_2
rag_default: true
```

## 1. 位置付け

本書は、Codex Desktopの独立Task作成、Task命名、Pin、初期Prompt送信、Follow-up送信、進捗確認、完了待機およびArchive機能を、MARGPAのDocument-driven開発運用へ接続する将来実験予約である。

現時点では`planned_experiment`であり、Task自動生成、Task間自動指示またはPhase 2開始を許可する正本ではない。ユーザーが実験開始を明示した時点で、対象Phase、作成Task、Write Authority、Git環境、Cost上限および停止条件を別途Accepted化する。

## 2. 構想

設計統括者役が、Current／Shared／Phase文書をControl Planeとして使用し、必要な独立Codex Taskを作成・命名し、IndexとHandoffを直接渡し、受領・進捗・Review・Follow-upを管理する。

```text
設計統括者役
  → Phase開始条件を確認
  → Phase Index／Requirements／Architecture／Handoffを作成
  → 必要な独立Codex Taskを作成
  → Task名をRole／Phaseに合わせて設定
  → Reading Order／Authority／禁止事項／Handoff Pathを初回Promptで送信
  → 受領確認を待機
  → Status／成果物をReview
  → Follow-upまたは次Roleへ直接Handoff
  → User Gateを通過
  → Phase完了Evidence／Recovery／Backupへ接続
```

「同時にIndexとHandoffを送る」とは、一つの操作要求の中で、先に正本をProjectへ作成・検証し、その存在を確認した後に新Taskを作成し、初回Promptから正本Pathを参照させることを意味する。Taskを先に開始して未完成文書を読ませない。

## 3. 独立Codex Taskの役割

独立Codex TaskはSidebarへ残るユーザー所有Taskとして扱う。ユーザーはTaskを直接開き、進捗確認、追加会話および判断を行える。

候補Role：

```text
Phase <N> 設計担当者役
Phase <N> 実装者役
Phase <N> Review担当
対外Docs役
限定調査Task
```

Task名は人間と設計統括者役が役割、Phaseおよび状態を識別できる名称にする。Task ID、Host IDおよびGit Stateは必要なEvidenceへ記録できるが、Credential、個人情報または不要な環境識別子をDocsへ保存しない。

## 4. Sub-agentとの分離

独立Codex TaskとSub-agentを混同しない。

| Execution Unit | 主用途 | 継続性 | User Direct Access | 推奨例 |
|---|---|---|---|---|
| 独立Codex Task | Phase／Role単位の継続作業 | 長期 | あり | Phase設計、実装、対外Docs |
| Sub-agent | 親Task内の限定並列作業 | 一時的 | 主に親Task経由 | 探索、Test分析、Triage、要約 |

Sub-agentは各Agentが独立してModel／Tool処理を行うため、単一AgentよりToken消費が増える可能性がある。並列化は時間短縮または品質向上が明確なRead-heavy作業を中心にし、同じWorking TreeへのWrite-heavy並列作業は競合Riskが高いため原則避ける。

## 5. DocsをControl Planeとして使う

```text
Current Documentation Index : Project現在地とReading Order
Shared Rules／Authority      : 共通規則と権限
Phase Index                  : Phase状態と入口
Requirements／Architecture   : 実施内容と設計契約
Handoff                      : Taskへの正式指示
Status                       : Task実行結果
Review                       : Accepted／Follow-up／Rejected
History                      : Append-only開発日誌
Recovery Manifest            : Task再作成と完全復元
Backup／Git Evidence         : Phase確定点
```

Taskの会話記憶だけをControl Planeにしない。新TaskはDocsだけでRole、Scope、Current State、Open Findingおよび次Actionを解決できることを目標とする。

## 6. Phase 2 Pilot

Phase 2を最初の正式Pilotとする。ただし、Phase 2開始時に自動適用しない。Phase 1-exの完了、User Acceptance、Backupおよびユーザーの明示的なTask作成指示を開始Gateとする。

Pilot手順：

1. ユーザーがPhase 2設計担当者役Taskの作成を明示指示する。
2. 設計統括者役がPhase 2 Index、開始用Handoff、Write AuthorityおよびReading Orderを作成する。
3. 設計統括者役が同Project内に独立Taskを作成する。
4. Task名を`Phase 2 設計担当者役`相当へ設定し、必要に応じてPinする。
5. 初回PromptでRole、対象Phase、読取順序、Write Scope、禁止事項、成果物、Status形式およびEscalation条件を送る。
6. Taskの受領確認を取得する。
7. 設計成果を設計統括者役がReviewする。
8. Accepted後に実装者役Taskへ正式Handoffする。

Phase 2 PilotはTask作成機能の便利さだけでなく、Docs-only Recovery、Authority遵守、Token Cost、Context分離、Handoff明瞭性、Review品質およびTask再作成可能性を評価する。

## 7. Human Authority Gate

次は自動化せず、ユーザーの明示判断を維持する。

- Project要件、Phase優先順位および大幅なScope変更
- 新しい独立Taskを作成する最初の指示
- Backup完了宣言
- Destructive Action、Overwrite、Deleteおよび復元不能操作
- External Service、Credential、Secretおよび課金環境の操作
- Commit、Tag、Push、Repository Visibilityおよび公開
- User Acceptance／Manual Test Acceptance
- Phase完了および次Phase移行承認

Task作成Toolが利用可能であることは、Taskを無断作成するAuthorityを意味しない。

## 8. Write Concurrency

同じWorking Treeへ複数Taskが同時Writeする運用は原則禁止する。RoleごとにDirectory Write Scopeが分離されていても、Index、Config、Generated Artifact、FormatterまたはTest Fixtureが交差する可能性を考慮する。

```text
Read-heavy並列作業 : 条件付き許可
Write-heavy作業     : 原則直列
同一File Write      : 禁止
Cross-Role変更      : 設計統括者役へEscalate
```

Git運用確立後は、独立Worktreeへ分離する案を再評価できる。ただしWorktreeはAuthority、Handoff、Review、MergeおよびSanitationを不要にしない。

## 9. Cost Control

全自動化できることと、常時多Task／多Agentを使うことは同義ではない。

- 必要なRoleだけを作成する。
- 小さな定型作業は通常GPT＋ユーザー手動またはScriptへRoutingする。
- Phase設計、実装およびReviewのContextを分離し、主TaskのContext Pollutionを抑える。
- Sub-agent並列化は独立性と便益が明確な場合だけ使用する。
- 完了Taskを無期限に動かさず、必要に応じてArchiveする。
- Model／Reasoning選択はTaskの難度とCostを考慮するが、ユーザー明示指定がない場合は現在の既定設定を維持する。

## 10. Planned Orchestration Evidence

将来Pilotを実施した場合は、少なくとも次を記録する。

```text
Experiment ID
Phase／Role
Created Task Name
Task ID／Host ID  # 必要な内部Evidenceのみ
Initial Handoff Path／SHA-512
Write Authority
Creation／Acknowledgement／Completion Time
Status／Review／Follow-up Paths
Files Created／Modified／Deleted
Concurrent Task Count
Token／Credit Observation  # 取得可能な範囲、Secretなし
Conflict／Block／Deviation
User Gate Evidence
Recovery／Archive State
```

## 11. Stop Conditions

次の場合はOrchestrationを停止する。

- 新TaskがHandoffまたはAuthorityを解決できない。
- 同一Fileへの同時Writeが発生または予見される。
- TaskがAccepted Scopeを越えてMutationしようとする。
- Task作成・送信・待機機能の現在挙動が設計前提と一致しない。
- Costが想定を超え、分業便益を失う。
- User Gateが未成立である。
- External／Git／Secret操作へ新しいAuthorityが必要になる。

停止時は追加Task作成、無許可修復または自動再実行を行わず、既存Task、Docs、Git StateおよびExternal Stateを列挙してユーザー判断を待つ。

## 12. Acceptance Criteria for Future Pilot

Pilotは次を全て満たした場合だけAccepted候補とする。

- ユーザーの明示指示後にだけTaskが作成された。
- Task名、Role、PhaseおよびHandoffが一致した。
- TaskがDocsからCurrent Stateを復元できた。
- Write Authority違反がなかった。
- Task間File Conflictがなかった。
- Status、Review、Follow-upおよびUser Gateが追跡できた。
- Source／Docs／Git／External StateのBefore／Afterが説明できた。
- 従来の手動Task作成より再説明CostまたはContext Pollutionを減らした。
- 利用可能量／Creditに対して合理的な便益があった。
- Task停止または再作成時にDocsからRecoveryできた。

## 13. Current Decision

```text
Capability Concept     : confirmed
Operational Adoption   : not started
Automatic Task Creation: prohibited without explicit user request
Selected Pilot         : Phase 2
Current Phase Impact   : none
```

本構想は「ユーザーがAuthorityと重要Gateを保持し、設計統括者役がDocumentを介してTask群を編成・監督する」運用を目標とする。完全自律化またはユーザーAuthorityの置換を目標としない。

## 14. Related Rules

- [Task Execution Routing／Cost Control](task_execution_routing_and_cost_control_ja.md)
- [Documentation Structure／Task Operations](documentation_structure_and_task_operations_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Research Asset Mutation Control](research_asset_mutation_control_ja.md)
