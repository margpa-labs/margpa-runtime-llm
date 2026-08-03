# Task Execution Routing／Cost Control

```yaml
document_id: task_execution_routing_and_cost_control
status: current
language: ja
created_at: 2026-08-02 21:04:38 JST
updated_at: 2026-08-02 21:04:38 JST
owner: 設計統括者役
rag_default: true
```

## 1. 目的

本書は、作業の意味判断、Mutation Risk、反復性およびExternal Operationの有無に応じて、設計統括者役、Phase別設計者役、Codex実装者役、通常GPT＋ユーザー手動操作およびScriptへ作業を振り分ける共通運用を定める。

目的は、必要なGovernance、ReviewおよびEvidenceを弱化せず、Codexの利用可能量、外部ServiceのCredit、ユーザーの操作時間および再説明Costを抑えることである。安価な実行面を選ぶことは、Authority、Backup、Fail-closed、Project Root境界または検証を省略する理由にならない。

## 2. 基本原則

```text
設計統括者役がContract／Authority／停止条件を確定
  → 最小十分な実行面へRouting
  → 実行面は許可範囲だけを処理
  → Evidence Handoff
  → 設計統括者役がAccepted／Follow-up／Stopを判定
```

同じ成果を安全に達成できる場合は、Repository全体の理解を必要とする実装Taskより、限定された通常GPT＋ユーザー手動操作または検証済みScriptを優先できる。ただし、判断を必要とする作業を単純Commandへ偽装しない。

## 3. 設計統括者役へRoutingする作業

次は設計統括者役がOwnerとなる。

- Project横断方針、Authority、Requirements、ArchitectureおよびGovernance
- 作業開始条件、禁止Action、期待結果、RollbackおよびHandoff Contract
- Source→Target Integration、Migration、Git履歴および公開境界の判断
- Security、Privacy、Secret、License、Third-party AttributionおよびSanitation分類
- Error発生後の手順変更、例外承認および作業再開判定
- 実装者Status、通常GPT HandoffおよびユーザーEvidenceのReview
- Commit／Tag／Push対象、Phase Gateおよび完了宣言

設計統括者役は、作業を委譲したことを理由に最終Review責任を失わない。

## 4. Phase別設計者役へRoutingする作業

Phase 2以降に配置するPhase別設計者役は、Assigned Phaseの局所Requirements、Architecture、ADR、実装HandoffおよびReviewを担当する。Cross-Phase不変条件、Shared Governance、Git公開方針または他Phaseへの影響が生じる場合は設計統括者役へEscalateする。

## 5. Codex実装者役へRoutingする作業

次は原則としてCodex実装者役へ渡す。

- `src/`、`tests/`、`scripts/`および許可された`config/`の実変更
- 複数File／複数Layerをまたぐ実装、RefactorまたはSchema変更
- Repository全体のContract理解が必要な修正
- Test追加、Regression修正、Static CheckおよびRuntime Acceptance
- 差分内容の技術的整合性を判断しながら行うSource統合
- 再現可能なScript、Preflightまたは検証ToolのRepository実装

実装者役はAccepted Handoffの範囲を越えて、Docs正本、Git History、External Serviceまたは公開状態を変更しない。

## 6. 通常GPT＋ユーザー手動操作へRoutingできる作業

次の条件を全て満たす作業は、設計統括者役が詳細Handoffを作成したうえで、通常GPTの案内とユーザーの手動Terminal／UI操作へ渡せる。

- 手順が決定論的である。
- 対象Path、Action、禁止Actionおよび期待値が固定されている。
- Read-only、またはユーザーが個別承認した限定Mutationである。
- Repository全体の意味判断を実行中に必要としない。
- 成否をExit Code、Hash、Status、HTTP Responseまたは定型Evidenceで判定できる。
- 失敗時に推測修復せず停止できる。

代表例：

- SSH／CLIのPreflightとRead-only接続確認
- Existing RepositoryのCloneとHEAD／`git fsck`／Working Tree確認
- Git Indexを基準にしたRead-only Delta Inventory
- LightningのManaged Setting、Port、API Builder、Sleep／Wake等のユーザー担当操作
- 明示されたFileの配置、Permission、SHA-512およびProcess Status確認
- Accepted Scriptの起動、停止および結果収集

通常GPTは設計Authority、Source Write Authorityまたは例外判断Authorityを持たない。Commandが失敗した場合、別Command、削除、Permission緩和、Path変更または外部操作を独断で追加せず、Evidenceを返して停止する。

## 7. ScriptへRoutingする作業

同じ手順を複数回実行する場合、Repositoryまたはユーザー管理領域へ置く検証済みScriptを優先する。Script化により、毎回のPrompt、Command転記、入力ミスおよび説明Costを減らす。

Scriptは次を満たす。

- Default Read-onlyまたはFail-closed
- Exact Path／Exact Target
- Secret値をLogへ出さない
- Dry-run／Preflight／Statusを可能な範囲で分離
- Unexpected Stateで非0終了
- Re-run Safetyまたは明示的な非冪等性表示
- Version、HashまたはSource Revisionを解決可能にする

Repository外へ置くPrivate Bootstrap等は、ユーザーが配置・Permission・起動を担当し、Repository DocsにはSecretや非公開実値を記録しない。

## 8. 通常GPT Handoffの必須項目

通常GPTへ渡すHandoffは、少なくとも次を含む。

```text
Objective
Exact Target
Preflight
Allowed Actions
Prohibited Actions
Exact Commands／UI Steps
Expected Results
Stop Conditions
No-improvisation Rule
Evidence Fields
Next Authority
```

外部PathまたはExternal Serviceを扱う場合は、ユーザーが対象とActionを明示承認した範囲だけを記載する。個人情報、Credential、Private Key、Secret値および個人Home PathをDocsへ転記しない。

## 9. Evidence Handoff

実行結果は自由文だけでなく、原則次の形式で設計統括者役へ返す。

```text
<TASK_NAME>_HANDOFF

Status:
PASS / BLOCKED / FAILED

Targets:
<logical targets without personal identifiers>

Checks:
<complete result summary>

Files Created／Modified／Deleted:
<complete list or NONE>

Git／External Mutation:
<complete list or NONE>

Warnings:
<list or NONE>

Remaining Issues:
<list or NONE>

Next Action:
設計統括者役へHandoff
```

## 10. Cost ControlとSafetyの優先順位

Routingは次の優先順位で決める。

```text
Authority／Safety／Research Asset Protection
  → Correctness／Reproducibility
  → Evidence／Rollback
  → User Time／AI Usage／External Credit
  → Convenience
```

Codex利用可能量またはCloud Creditの節約は重要な運用要件であるが、危険な作業を無監督の通常GPTへ移す理由にはならない。逆に、単純なRead-only確認や確定Commandだけのために高文脈の実装Taskを使用し続けない。

## 11. Escalation条件

次を検出した場合、通常GPT、Scriptまたは実装者は即時停止し、設計統括者役へ戻す。

- Expected Resultと不一致
- 対象Path、Repository、Branch、HEADまたはEnvironmentの不一致
- 未承認のFile、Secret、個人情報またはSymbolic Link
- Copy、Delete、Overwrite、History RewriteまたはExternal Mutationが新たに必要
- Commandの代替案に意味判断が必要
- Test Failureの原因がAccepted Handoff外
- 既存運用またはAuthorityとの競合

## 12. 現行Git作業への適用

Existing Repository継続作業では、専用SSH接続確認、Clone、HEAD／`git fsck`／Working Tree確認およびRead-only Delta Inventoryを通常GPT＋ユーザー手動操作へRoutingできる。

Original ProjectからGit Staging CloneへのCopy方式、Delete候補、Merge、Commit、Tag、Push、History、SanitationおよびPublic／Private変更は設計統括者役へ戻し、必要なSource変更は実装者役へ渡す。

## 13. Authority

本書は作業の実行面を選ぶ規則であり、新しいWrite Authority、External AuthorityまたはGit Authorityを生成しない。User Explicit Instruction、[Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)、[Research Asset Mutation Control](research_asset_mutation_control_ja.md)およびAccepted Handoffを優先する。

