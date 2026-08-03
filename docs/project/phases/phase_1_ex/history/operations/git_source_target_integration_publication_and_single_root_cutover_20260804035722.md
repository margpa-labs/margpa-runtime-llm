# Git Source→Target統合／公開反映／単一Git Root移行記録

```yaml
document_id: git_source_target_integration_publication_and_single_root_cutover
phase: phase_1_ex
status: accepted_current_state
created_at: 2026-08-04 03:57:22 JST
owner: 設計統括者役
decision_authority: user
scope:
  - preintegration_backup_and_manifest_refresh
  - source_to_target_actual_integration
  - publication_tree_alignment
  - git_commit_pull_request_and_merge
  - work_branch_retirement
  - direct_main_documentation_update
  - canonical_git_root_cutover
privacy: sanitized
supersedes_current_state_of:
  - git_workflow_acceptance_merge_and_branch_retirement_20260804025318.md
```

## 1. 目的

本書は、開発内容正本であったSource Working Treeと、既存GitHub Historyを保持したGit Staging Cloneを統合し、公開対象のPath／Contentの一致、Sanitation、Test、Commit、Draft Pull Request、Merge、作業Branch退役、追加Docs Commitおよび最終的な単一Git Root移行までの事実と境界を累積記録する。

本書は作業中の個人Path、Credential、Private Key、Passphrase、Managed Secret、個人Emailの具体値を収録しない。公開Identity、Repository、Commit SHA、非機密のHash、件数、AcceptanceおよびRollback境界だけを保持する。

## 2. 開始時の保護境界

統合開始前のLogical Rootは次の役割で分離されていた。

```text
margpa-runtime-llm:
  開発内容正本
  Runtime／Docs／Config／Testの最新状態
  当初はGit Metadataなし

margpa-runtime-llm_git_staging:
  Existing GitHub RepositoryのClone
  Git History／Remote／Indexの正本
  ユーザーのみがアクセスできるMode 700を維持

other:
  ユーザー専用領域
  本Project TaskによるRead／Write／Executeの対象外
```

Git Staging RootがMode 700であることはGit操作のBlockerではなく、安全性のため維持した。ユーザー専用領域は、本作業で一度もアクセス、権限変更、検査または更新していない。

## 3. 統合前Backup／Handoff Evidence

SourceおよびGit Stagingについて、実統合前にユーザー主体でBackupを取得し、Archiveと元Directoryを分けてSHA-512および内容検証を行った。これらはPhase 1-ex Final Backupではなく、Source→Target IntegrationのChange-level Safety Backupである。

初期Source→Target Integration Manifest Handoffの非機密Evidenceは次である。

```text
Handoff Size:
240783 bytes

Handoff SHA-512:
4ed0e2ac9b15c531a2cf8f4e1f8156b153e61c5c7381d5232085c6af5ca9d2b15fcd2bbcd2dd626eab9ca840ffb78a7b12d506ac66f2354d80a035ce2385f659
```

作業間にSourceが更新されたため、実転送前にDelta Refreshを改めて実施した。

```text
Delta Refresh Handoff Size:
343303 bytes

Delta Refresh Handoff SHA-512:
1be7652ea26350bcd85711c636b02a12ddfaa606fd175732cb3bfbdf292e690d9db941f887d5f06d7d8c2cd30018da5324081acf9d05c088d71d3930ceb6298c
```

## 4. Delta Refresh結果

```text
UPDATE_CANDIDATE             31
ADD_CANDIDATE               808
IDENTICAL                   214
RETAIN_PENDING_DECISION      41
EXCLUDE                   16805
EXCLUDE_SYMLINK               4
BLOCKED_UNCLASSIFIED          0
SCAN_ERROR                    0

EXACT_CANDIDATE_COUNT       839
CANDIDATE_TOTAL_SIZE_BYTES  35579373
```

Exact Candidate Pathset SHA-512：

```text
de4eca93ec8fd51af556f1f89daf964058449ecee85405b951851489df4fe3f680f382b91c6ba2e1e9b8c10899aa8976c944feb3dfc7987601d298583f97e35c
```

`rsync --dry-run`相当の事前照合は次であった。

```text
RSYNC_DRY_RUN_STATUS       : PASS
DRY_RUN_UPDATE_COUNT       : 31
DRY_RUN_ADD_COUNT          : 808
FILES_TRANSFER_FORECAST    : 839
TRANSFER_SIZE_FORECAST     : 35579373 bytes
DELETE_FORECAST            : 0
SYMLINK_TRANSFER_FORECAST  : 0
RSYNC_EXIT_CODE             : 0
```

旧Baseline 772 Candidateは全件維持された。Candidate増加67件は、旧Drift 17件の正式`ADD_CANDIDATE`化、新規Add 24件、新規Update 26件で構成された。旧`RETAIN_PENDING_DECISION` 41件はPath、Size、SHA-512の全項目で不変であった。

本Refreshの時点でSource／Target Mutation、Git Mutation、Permission変更、実転送およびDocs更新は行っていない。Target Working Tree、HEAD、OriginおよびRoot Permissionも不変であった。

## 5. Source→Target実統合

統合はRoot-to-Rootで行い、Target Root下へSource Root Directory自体を入れ子でCopyしない境界を固定した。

対象は承認済みCandidateのみとし、次を転送対象外とした。

- `.git/`
- `.venv/`
- Model Weight／Model実体
- Secret／Credential
- Cache／Temporary Artifact／Runtime State
- Symbolic Link Candidate
- `RETAIN_PENDING_DECISION`
- 分類不明または未承認Path

実統合後、Source側の開発内容とTarget側のGit Historyを両立させた。元のGitHub上には、本来のCanonical Pathではない旧`docs/phases/`と、不完全なDocs配置が含まれていたため、ユーザーと設計統括者役で取扱いを分類した。

## 6. ユーザーによるTarget整合

ユーザーはBackup取得後、Targetに対して次を明示的に実施した。

- 旧`docs/phases/`をDirectoryごと削除。
- `docs/project/phases/`をCanonical Phase Treeとして維持。
- Localで後続使用する空Directory `docs/project/phases/phase_2/history/index/`を配置。空DirectoryはGitにより追跡されない。
- 旧Lightning Demo画像8枚を削除。
- Lightningの日本語／英語画像6枚とRoot Demo画像6枚の合計12枚を現行正本として維持。
- `.DS_Store`および明白なCache／不要Artifactを、ユーザーが確認した対象のみに限定して除外。

この整合により、GitHubの旧Directory構造を保存するためにCanonical Sourceを曲げるのではなく、現行SourceをTargetの公開Treeとして一致させる方針を確定した。旧Treeの削除はGit History上の過去の存在を消去しない。

## 7. Publication Set完全一致

`.venv/`、`.git/`、Model、Cache、Secret、Local Runtime Dataおよびその他承認済み除外を適用したPublication Setを照合した結果は次である。

```text
Source Files          : 1,053
Target Files          : 1,053
Source-only           : 0
Target-only           : 0
Content Mismatch      : 0
Source Directories    : 131
Target Directories    : 131
```

Publication Manifest SHA-512：

```text
c33fa4c267c30d2cae1607fab7e584b6f4c83401f4fd87e1e99835c52e45f56434e4ce6f304b757b9bbd01f5447c2373d4c87a1ddf3d4266e2762831bd3ba28f
```

239件のMode差は、Sourceの`644`とTargetの`600`の差であり、Git Tree上ではいずれも`100644`として同等であった。Executable Bitの不一致は0件であり、Content整合性の不一致ではない。

Directory全体の見かけSize差は、主にSource側の`.venv/`とTarget側の`.git/`による。これらを除外した公開対象は一致していた。

## 8. Git Publication Sanitation

PushごとのPublication Gateとして次を確認した。

- 追跡Path、Staged Diff、Outgoing TreeおよびCommit Metadata。
- 公開IdentityとRepository-local Author／Email。具体のnoreply EmailはDocsに記録しない。
- Secret、Credential、Private Key、個人Email、個人Path、不要な識別可能情報。
- `.DS_Store`、`__MACOSX/`、Cache、Temporary Artifact、Model Weight、`.venv/`、`.env*`。
- Third-party Attribution、License、NOTICEおよびResearch Preview条件。
- Legacy `docs/phases/`および廃止画像がOutgoing Treeに残っていないこと。

`git diff --cached --check`が指摘したLossless／History文書の末尾空行147件とMarkdown改行用の末尾2 Space 11行は、原文保持のための意図的例外とした。実CodeのWhitespace Errorは0件であった。

## 9. Initial Integration Commit／Pull Request／Merge

統合作業Branch：

```text
phase/1-ex-publication-preparation
```

統合Baseline Commit：

```text
ce4f9ce5537aed2f34ceb0e4316685778fb063cc
feat: establish Phase 1 runtime and Phase 1-ex integration baseline
```

Canonical Tree整合Commit：

```text
3a645f7317cd5c7f702c6004b8eb0b96d9c261cf
chore: align repository tree with canonical source
```

後者は旧`docs/phases/**` 33件と廃止Demo画像8件の合計41件を削除した。現行画像12件は意図的に保持した。

Draft Pull Request：

```text
Pull Request : #1
URL          : https://github.com/margpa-labs/margpa-runtime-llm/pull/1
Base         : main
Head         : phase/1-ex-publication-preparation
Draft        : yes at creation
```

GitHub ActionsのRequired Checkは設定されていなかったため、未実施Checkを合格扱いせず、Local ValidationをEvidenceとした。

```text
Main Test Suite                    : 383 passed／3 deselected
Signal-heavy Lifecycle Tests       : 47／47 passed in bounded groups
Ruff                               : pass
Format Check                       : pass
Mypy                               : pass
Shell Syntax                       : 8／8 pass
TOML Parse                         : 13／13 pass
Privacy／Publication Sanitation   : pass
Git fsck                           : pass
```

Pull RequestはMerge Commit方式で`main`へ統合した。

```text
Merge Commit:
9fff303175a3224963254eacddd66f9cf5112a5a

Parent 1:
55e0ab854db07212dce987d1a7d7c4e43e2b63c6

Parent 2:
3a645f7317cd5c7f702c6004b8eb0b96d9c261cf
```

Merge後、Local `main`を`origin/main`へFast-forwardし、Local／Remote SHA、Working Tree Cleanおよび`git fsck`を確認した。

## 10. 作業Branch退役

`phase/1-ex-publication-preparation`は、Local／Remoteの両方でBranch Tipが`main`へ到達済みであることを`merge-base --is-ancestor`相当のContainment Checkで証明した。

ユーザーが明示承認した後、作業BranchをLocal／Remoteから削除した。この操作はMerge Commit、PR、Commit HistoryまたはBackupを削除しない。

## 11. Risk-based Git Workflowへの修正

すべての小規模変更にBranch／PRを必須とする運用は、個人R&DのDocs更新では運用Costが過大である。ユーザー判断により、次のRisk-based Modelへ改めた。

```text
Direct mainを許容できる候補:
  小規模
  決定論的
  Docs／Metadata／明白な軽微修正
  Exact Diff／Test／Sanitation／Rollback可能
  当該CommitとPushのユーザー明示承認あり

Branch／Draft PRを原則とする変更:
  新機能
  複数Layer
  大規模
  高Risk
  Phase統合
  Review／Rollback境界の分離が必要
```

Direct `main`はStanding Authorizationではない。各Commit／Pushの対象、差分、ValidationおよびRemote反映は、その都度ユーザーの明示承認を要する。Force Push、History Rewrite、Root Commit置換、Tag移動および無承認Remote変更は引き続き禁止する。

## 12. Direct `main` Docs Commit／Push

Git Workflow固定後に発生した、既存Stable 4件と新規Docs 12件の合計16件をExact Allowlistで反映した。Source／Target Content Mismatchは0件であった。

```text
Commit:
9ac8a6ba4a2120d93856356fababd130af3aa352

Message:
docs(phase-1-ex): establish git workflow and merge record

Files:
16

Diff:
4650 insertions／18 deletions
```

Staged Diff Check、個人情報／Secret Candidate Scan、追跡対象およびAuthor Identity Checkに合格後、`main`へPushした。

```text
Remote Update:
9fff303..9ac8a6b

Local HEAD:
9ac8a6ba4a2120d93856356fababd130af3aa352

origin/main:
9ac8a6ba4a2120d93856356fababd130af3aa352

Remote main:
9ac8a6ba4a2120d93856356fababd130af3aa352
```

Push後、Local／`origin/main`／Remote `main`の完全一致、Working Tree Cleanおよび`git fsck` PASSを確認した。

## 13. 単一Git Root Cutoverの判断

二重Rootは初回統合の安全性を高めたが、後続運用では次のCostとRiskを持つ。

- 各更新でSource→Staging Copyが必要。
- 同期漏れや古いFileの残存を判断し続ける必要がある。
- どちらが開発正本／Git正本かを毎回識別する必要がある。
- 容量、Backup、Test、IDEおよびTask Working Directoryが二重になる。

ユーザーは、最終的に`margpa-runtime-llm`を開発内容とGit Metadataの両方を持つ単一Canonical Rootとすることを選択した。

## 14. Cutover Preflight／Backup

Cutover前に、SourceとGit Stagingの双方をユーザーがBackupした。Backup完了前に`.git`をCopyしないGateを守った。

Git Staging側の`.git`について、次を確認した。

```text
Type             : normal directory
Permission       : 700
Repository       : non-bare
core.worktree    : unset
index.lock       : absent
core.filemode    : true
main             : aligned with origin/main
Working Tree     : clean
Git fsck         : pass
```

Source側のPublication Setは、Git Staging Working TreeとPath／Contentが一致していた。Source固有の`.venv/`、Model Link／ArtifactおよびLocal Runtime DataはGit非追跡境界にあり、`.git`移植後にもGit Indexへ混入しないことを前提とした。

## 15. `.git` Metadata Cutover

一般的に`.git`だけの手動Copyは安易に行うべきでない。本件では、次が全て揃った状態で、ユーザーが対象と方式を明示承認した。

- Source／Target公開対象が一致。
- `main`／`origin/main`／Remote `main`が同一SHA。
- Staging Working Tree Clean。
- `git fsck` PASS。
- Source／StagingのBackup完了。
- Rollback元となるArchiveを別保管。
- User Explicit Authorizationあり。

macOSのMetadata、Extended AttributeおよびACLを保持できる`ditto`を用いて、Git Stagingの`.git`をSource RootへCopyした。

```text
COPY_PREFLIGHT_EXIT : 0
DITTO_EXIT          : 0
GIT_CUTOVER_EXIT    : 0
```

このCutoverにより、`margpa-runtime-llm`は次の両方を持つ。

```text
Canonical Development Content
+
Existing Git History／Index／Remote Configuration
```

## 16. Cutover Postflight

Cutover後に次を確認した。

```text
Branch                 : main
HEAD                   : 9ac8a6ba4a2120d93856356fababd130af3aa352
origin/main            : 9ac8a6ba4a2120d93856356fababd130af3aa352
origin/HEAD            : origin/main
Working Tree           : clean at cutover verification
Remote                 : approved SSH alias／margpa-labs/margpa-runtime-llm
Git Directory          : present in canonical root
Full Test              : 430 passed／3 deselected
```

上記のTestはRuntime／Docs／Git Cutover後のProject全体を対象とし、58.57秒で完了した。

ユーザーは、単一化完了後のBackupを取得した。その後、旧Git Staging Directoryはユーザーの明示判断で削除された。

## 17. 現在のGit Canonical State

```text
Canonical Working Root : margpa-runtime-llm
Former Git Staging Root : retired／deleted after backup
Default Branch          : main
HEAD                     : 9ac8a6ba4a2120d93856356fababd130af3aa352
origin/main              : 9ac8a6ba4a2120d93856356fababd130af3aa352
Remote main              : 9ac8a6ba4a2120d93856356fababd130af3aa352
Remote Transport         : SSH through approved alias
Git Working Tree         : canonical root
Tag／Release              : none
Branch Protection        : unchanged／not accepted by this record
Repository Visibility    : unchanged
Phase 1-ex               : in progress
```

単一Git Root化の完了により、今後の正常な変更はCanonical RootのWorking Treeと`.git`を用いて実施できる。旧Staging Rootへの同期または二重管理は不要である。

## 18. Backup運用の補足

`.venv/`は大容量であり、Project SourceからLock／Setup手順により再構築可能である。今後のProject Archiveは、Canonical Root自体から`.venv/`を一時削除して作成しない。

承認した方式は次である。

```text
1. Canonical RootをBackup作業用Copyへ完全Copy
2. Backup作業用Copyから`.venv/`を除外
3. 必要なCache／Model／Secret非同梱境界を適用
4. Backup作業用CopyをArchive化
5. ArchiveのSHA-512と必要なRestore Evidenceを保持
6. Local Runtime用`.venv/`はCanonical Root側で不変のまま維持
```

`.venv/`を別にBackupする場合も、復元できる保証がなければLock／Setup手順による再構築を優先する。

## 19. 不変のAuthority／Safety境界

本件でGit運用と単一Rootが成立したことは、無承認Mutationの許可を意味しない。

- ユーザーの明示指示なしにCommit、Push、Merge、Tag、Release、Branch削除またはRemote変更を行わない。
- 「良かれ」「推測」「話の流れ」「いずれ必要」をAuthorityに変換しない。
- Commandの提示依頼を実行許可と解釈しない。
- Project Root外とユーザー専用領域を許可なく触らない。
- 曖昧さ、対象不明、未分類差分、想定外の削除または新たなExternal Mutationがあれば停止して確認する。
- Phase 2以降のDocument-driven自動化実験は別のAccepted Contractであり、日常運用の絶対的確認原則を弱めない。

## 20. 残っているGate

本書のAccepted StateはGit基盤と単一Rootの成立を意味するが、Phase 1-ex完了ではない。

残作業：

1. 本記録を含むCurrent／Shared／Phase Index／Recoveryの最新化。
2. Phase 1-ex Final Lossless CompilationとManifest。
3. 必要DocsとPublic Roadmapの最終Refresh。
4. Full Test／Static Check／Link／Privacy／Publication SanitationのPhase Final Gate。
5. Open Findingの解決または明示承認済みDeferral。
6. User Acceptance。
7. ユーザーへのPhase Backup取得依頼とBackup Evidence。
8. Phase最終Git Commit／Pushの判断。
9. `phase-1-ex-complete` Annotated Tag候補の別判断。
10. Phase 2開始Gate。

Canonical Rootからの次回の実変更Commit／Pushは、単一Root運用を実運用で再確認する。Dummy File、空Commitまたは検証だけの無意味なCommitは作らず、次の正当なDocsまたはSource変更を対象とする。

## 21. Acceptance

```text
Source→Target Manifest Refresh         : PASS
Actual Integration                       : PASS
Publication Path／Content Equality      : PASS
Publication Sanitation                   : PASS
Initial Commit／Draft PR／Review／Merge : PASS
Merged Branch Retirement                 : PASS
Direct main Docs Commit／Push            : PASS
Single Git Root Preflight                : PASS
Single Git Root Cutover                  : PASS
Full Runtime Test after Cutover          : PASS
Former Staging Retirement               : PASS／USER EXECUTED
Phase 1-ex Completion                    : NOT YET
Phase Completion Tag／Release            : NONE
```

## 22. References

- [Git Workflow Policy](../../../../shared/operations/git_workflow_policy_ja.md)
- [GitHub Publication Sanitation Policy](../../../../shared/operations/git_publication_sanitation_policy_ja.md)
- [Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Research Asset Mutation Control](../../../../shared/operations/research_asset_mutation_control_ja.md)
- [Git Read-only Delta Inventory／統合直前Backup Evidence](git_read_only_delta_inventory_and_preintegration_backup_evidence_20260803201448.md)
- [Git Workflow Acceptance／PR Merge／Branch Retirement](git_workflow_acceptance_merge_and_branch_retirement_20260804025318.md)
- [Current Documentation Index](../../../../current/documentation_index_ja.md)
- [Project Continuity Master](../../../../current/project_continuity/project_continuity_master_ja.md)
- [Phase 1-ex Index](../../phase_index_ja.md)
