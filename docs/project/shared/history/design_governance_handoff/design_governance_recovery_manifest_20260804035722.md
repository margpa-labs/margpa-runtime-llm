# Design Governance Recovery Manifest

```yaml
document_id: design_governance_recovery_manifest
snapshot: 20260804035722
state_at: 2026-08-04 03:57:22 JST
status: interim_current_state
active_phase: phase_1_ex
owner: 設計統括者役
decision_authority: user
phase_complete: false
canonical_git_root: margpa-runtime-llm
personal_information_included: false
credentials_included: false
absolute_personal_paths_included: false
```

## 1. 復旧目的

本Manifestは、現設計統括者役Taskが直後に継続不能になっても、新しい設計統括者役Taskが旧Task会話の記憶へ依存せず、Project状態、Authority、Git基盤、未完了Gateおよび次の安全な一手を復元するための臨時完全復旧点である。

本ManifestはPhase 1-ex完了版ではない。`interim_current_state`であり、Final Lossless、Final Review、User AcceptanceおよびPhase Backupを経たFinal Recovery Manifestを後続で作成する。

## 2. Project Identity

```text
Project Name : margpa-runtime-llm
Display Name : MARGPA Runtime LLM
Public Author: Nazuna Research
Repository   : margpa-labs/margpa-runtime-llm
```

Model、Governance、Guardrail、Judge、Repair、RAG、Agent、Tool、Memory、Auditおよび外部R&D機構を可能な限り徹底して疎結合に接続し、構成差、権限、責任、介入、Evidence、Cost、FailureおよびRepairを比較可能にするRuntime Governance型AI研究基盤である。

## 3. Mandatory Reading Order

1. [Design Governance Handoff](../../design_governance_handoff/design_governance_handoff_ja.md)の第18節。
2. 本Manifest。
3. [Current Documentation Index](../../../current/documentation_index_ja.md)。
4. [Project Continuity Master](../../../current/project_continuity/project_continuity_master_ja.md)の第31節。
5. [Phase 1-ex Index](../../../phases/phase_1_ex/phase_index_ja.md)。
6. [Git Workflow Policy](../../operations/git_workflow_policy_ja.md)。
7. [GitHub Publication Sanitation Policy](../../operations/git_publication_sanitation_policy_ja.md)。
8. [Task Role／Write Authority Policy](../../task_roles/task_role_write_authority_policy_ja.md)。
9. [Documentation Structure／Task Operations](../../operations/documentation_structure_and_task_operations_ja.md)。
10. [Git Source→Target統合／公開反映／単一Git Root移行記録](../../../phases/phase_1_ex/history/operations/git_source_target_integration_publication_and_single_root_cutover_20260804035722.md)。
11. [Public Roadmap](../../../../public/roadmap_ja.md)。

## 4. Phase State

```text
Phase 0                       : COMPLETE
Phase 1                       : COMPLETE／ACCEPTED
Phase 1 Backup                : COMPLETED／VERIFIED
Phase 1-ex                    : IN PROGRESS
Documentation Migration      : COMPLETE／LEGACY ROOT RETIRED
Phase 1 Final Lossless        : 316／316 PASS
Phase 1-ex Interim Lossless   : 145／145 PASS
Phase 1-ex Final Lossless     : NOT YET
Phase 2                       : NOT STARTED
```

Phase 1-exをCompleteと扱わない。本Docs Refresh、Final Lossless、Phase Final Check、User Acceptance、Phase Backupおよび最終Git判断が残っている。

## 5. Runtime／Deployment State

```text
Main Model             : Qwen3-4B-GGUF Q4_K_M
Local Backend          : llama-cpp-python 0.3.34／Metal
External Backend       : llama-cpp-python 0.3.34／Pure CPU
Local Python           : 3.13.14
Lightning Python       : 3.12.11
UI                     : FastAPI Minimal Web
Conversation Storage   : Browser Memory／Non-persistent
Basic Preview          : Accepted
Traffic-aware Auto-start: Accepted／GO
Anonymous Public Demo  : Accepted
```

LightningのCold Startは実測で約3～10分の幅がある。URL AccessからSleeping Studio／Serviceが起動し、LoginまたはPublic UIとModel利用へ進めることを複数回確認済みである。これはProduction SLA、常時稼働またはCredit永続性を保証しない。

## 6. Documentation RAG State

```text
Mac Project Corpus              : accepted
Lightning Basic Public Corpus   : accepted
Lightning Public Public Corpus  : accepted
Citation UI                     : accepted
Missing Docs Fail-closed        : implemented
Retrieval／Grounding Quality    : known limitation
```

RAG機構自体は成立している。ただし、小型・軽量ModelのHallucination、略称混同、Multi-target Queryの一部Fail-closed、Retrieval後の引用と本文の不一致、Roadmap進捗の要約精度および参照の過剰・不足が残る。精度改善をPhase 1-exのBlockerとせず、ARGD／DAGD、Guard、Judge、Repair、Token BudgetおよびRetrieval改善とともに後続Phaseで比較可能にする。

Public Access Profileでは公開承認済み8文書のみをCorpusにする。Project Internal History、Private Documentまたは未承認SourceをPublic Corpusへ混入させない。

## 7. Git／GitHub State

```text
Existing Repository History : preserved
Repository                  : margpa-labs/margpa-runtime-llm
Canonical Working Root      : margpa-runtime-llm
Former Git Staging Root     : retired／deleted after backup
Default Branch              : main
HEAD                        : 9ac8a6ba4a2120d93856356fababd130af3aa352
origin/main                 : 9ac8a6ba4a2120d93856356fababd130af3aa352
Remote main                 : 9ac8a6ba4a2120d93856356fababd130af3aa352
Remote Transport            : approved SSH alias
Working Branch              : none
Tag／Release                 : none
Branch Protection           : unchanged
Visibility                  : unchanged
```

Accepted Commit Chain：

```text
55e0ab854db07212dce987d1a7d7c4e43e2b63c6  existing remote baseline
ce4f9ce5537aed2f34ceb0e4316685778fb063cc  initial integration commit
3a645f7317cd5c7f702c6004b8eb0b96d9c261cf  canonical tree alignment
9fff303175a3224963254eacddd66f9cf5112a5a  PR #1 merge commit
9ac8a6ba4a2120d93856356fababd130af3aa352  direct main documentation commit
```

Dedicated SSH Identity、Private Key、PassphraseおよびGitHub-linked private noreply Emailはユーザー管理である。具体値をProject Docsへ記録しない。公開Commit Display Nameは`Nazuna Research`とする。

## 8. Source→Target／Cutover Evidence

```text
Publication Files        : 1,053／1,053
Source-only              : 0
Target-only              : 0
Content Mismatch         : 0
Publication Manifest SHA : c33fa4c267c30d2cae1607fab7e584b6f4c83401f4fd87e1e99835c52e45f56434e4ce6f304b757b9bbd01f5447c2373d4c87a1ddf3d4266e2762831bd3ba28f
COPY_PREFLIGHT_EXIT      : 0
DITTO_EXIT               : 0
GIT_CUTOVER_EXIT         : 0
Post-cutover Full Test   : 430 passed／3 deselected
```

現行Demo画像はLightning JA／EN 6枚とRoot Demo 6枚の合計12枚である。廃止Lightning画像8枚と旧`docs/phases/`は現行Treeから除外済みである。

## 9. Git Workflow

```text
小規模／決定論的Docs／Metadata:
  Direct main候補
  Exact Diff／Test／Sanitation／Rollback／User Approval必須

新機能／複数Layer／大規模／高Risk／Phase統合:
  Working Branch／Draft PR／Review／Merge Commitを原則
```

Direct `main`はStanding Authorizationではない。Commit、Push、Merge、Tag、Release、Branch削除、RemoteまたはVisibility変更は、対象ごとのユーザ明示承認を要する。Force Push、History Rewrite、Repository再作成、Root Commit置換およびTag移動は別の明示承認なしに行わない。

## 10. Documentation State

```text
Current Canonical            : cumulative stable set
Shared Rules／Operations    : cumulative stable set
Phase 1 Lossless             : final／316 of 316 pass
Phase 1-ex Lossless          : interim／145 of 145 pass
Public JA Docs               : available
Public EN Docs               : partial／optional completion reserved
Latest Event Record          : git_source_target_integration_publication_and_single_root_cutover_20260804035722.md
Latest Recovery State        : this manifest
```

Stableの変更前後Snapshot、Phase Event Record、Phase Index、Append-only Documentation Index SnapshotおよびSHA-512 Evidenceを必ず保持する。Git Historyはこれらを置き換えない。

## 11. Authority／Absolute Boundaries

- 「良かれ」「推測」「話の流れ」「いずれ必要」をAuthorityに変換しない。
- ユーザーがCommandを求めた場合はCommandだけを提示し、実行しない。
- 許可されたProject Root外を許可なく触らない。ユーザー専用領域はRead／Write／Execute全て対象外。
- 1%でも対象、意図、Actionまたは影響が不明なら停止して確認する。
- ユーザーが書いた原文とHistoryを、要約、読みやすさまたはGit差分のために意味変更しない。
- Phase 2以降のDocument-driven自動化Pilotは別Contractであり、通常運用の確認原則を弱めない。
- 設計統括者役も運用変更の自動Authorityを持たない。

## 12. Backup State／Rule

Source→Target Integration前、Git Cutover前および単一化後のBackupはユーザーにより取得済みである。これらはPhase 1-ex Final Backupの代替ではない。

Project ArchiveはCanonical RootのCopyを作り、Copy側から`.venv/`、Model、Cache、SecretおよびLocal Runtime Dataを除外して作成する。Canonical Root本体の`.venv/`を一時削除しない。

設計統括者役はPhase完了前に、ユーザーが自発的にBackupを取得する予定でも「Phase Backupを取得してください」と明示する。

## 13. Open Work／Next Safe Action

```text
1. Current State Docs Refreshの完了／検証
2. Phase 1-ex Final Source Freeze／Lossless／Manifest
3. 必要Docs／Roadmap Final Refresh
4. Phase Final Full Review／Test／Privacy／Publication Sanitation
5. Open Finding解決または明示承認済みDeferral
6. User Acceptance
7. Phase Backup取得依頼／Evidence
8. Canonical RootからのFinal Commit／Push判断
9. Phase Completion Tag／Releaseの別判断
10. Phase 2 Start Gate
```

次の安全な一手は、本Docs RefreshのBefore／After Snapshot、SHA-512、Link、PrivacyおよびGit Diffを完了させることである。その後、ユーザーが次に明示した一作業単位だけを進める。

## 14. Reconstruction Validation

```text
Project Identity                  : resolved
Active Phase                      : resolved
Canonical Requirements／Architecture: resolved by Current Index
Docs Structure／Stable／History     : resolved
Role／Write Authority               : resolved
Runtime／Deployment                : resolved
Public Demo／RAG                   : resolved
Git Repository／Commit／Root       : resolved
Backup／Release                   : resolved
Open Work／Next Safe Action        : resolved
Credential／Personal Data          : not embedded
Phase 1-ex Completion             : explicitly false
```

Validation Result：`PASS AS INTERIM CURRENT STATE`

## 15. Known Limitations

- Phase 1-ex Final Lossless Compilationは未作成。
- 本Docs Refresh完了後のPhase Final Full Test／Privacy Scanは未実施。
- Canonical Root Cutover後のFull Testは合格済みだが、単一Rootからの次回の正当なCommit／Pushは未実施。
- Phase 1-ex Completion Tag／Releaseは未作成。
- Branch Protectionは未設定。
- Optional English Derived Docsは完全一式未完了。
- Documentation RAGの回答精度は後続改善対象。

## 16. Completion Condition of This Manifest

本Manifest単体の完了条件は、新Taskが本書とReading Orderから次を説明できることである。

1. 何を作っているか。
2. どのPhaseまで完了し、今どこにいるか。
3. Current／Shared／Phase／Public／Historyの正本はどれか。
4. 何が実装・受入済みで、何が未実装か。
5. GitHub History、Commit Chain、Canonical RootおよびRemote状態は何か。
6. どのRoleがどこへ書けるか。
7. 何がユーザーの明示承認を必要とするか。
8. 次に何を安全に行うか。

一つでも解決不能な場合、新Taskは推測で埋めず、Open Findingとして停止する。
