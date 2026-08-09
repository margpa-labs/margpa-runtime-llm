# Git Workflow Policy

```yaml
document_id: git_workflow_policy
status: current_effective
language: ja
created_at: 2026-08-04 02:53:18 JST
updated_at: 2026-08-04 11:17:44 JST
owner: 設計統括者役
decision_authority: user
repository: margpa-labs/margpa-runtime-llm
default_branch: main
history_policy: preserve
force_push: prohibited_without_separate_authorization
```

## 1. 目的

本書は、MARGPA Runtime LLMにおけるBranch、Commit、Pull Request、Merge、Tag、Remote、公開Identity、BackupおよびLocal Working Rootの運用正本を定める。

GitはSource差分と公開Historyを管理する追加手段であり、Timestamp付きDocs History、Phase Lossless Compilation、SHA-512 EvidenceおよびユーザーBackupを置き換えない。

## 2. Authority

次の操作は、対象とActionを当該ターンでユーザーが明示承認した場合だけ実行できる。

- Commit
- Push
- Pull Request作成、Draft解除およびMerge
- Branch／Tag／Releaseの作成または削除
- Remote変更
- Default Branch／Branch Protection／Repository Visibility変更
- History Rewrite、Force Push、RebaseまたはRepository再作成

設計統括者役、Phase設計者役、実装者役、対外Docs役、Tool権限、Approval UI、過去の許可および作業の流れは、上記のStanding Authorizationを生成しない。

## 3. Repository／Remote

```text
Repository      : margpa-labs/margpa-runtime-llm
Default Branch  : main
Primary Remote  : origin
Transport       : SSH
Remote History  : preserve
```

- Existing Repositoryと既存公開Historyを継承する。
- Contributor表示の変更を目的としたRepository再作成、Root Commit置換、History RewriteまたはForce Pushを行わない。
- `origin`のFetch／Push先変更はユーザーの個別承認を必要とする。
- RepositoryのPublic継続／Private化は別判断とし、本書だけでは変更しない。

## 4. Public Identity

今後の公開Commit Identityは次へ統一する。

```text
Author／Committer Display Name : Nazuna Research
Email                         : GitHub-linked private noreply address
Push Authentication           : public GitHub account through dedicated SSH identity
```

- Private noreply Emailの具体値、Private Key、Passphrase、Credential、個人Emailおよび個人PathをProject Docsへ記録しない。
- Commit前にRepository-local `user.name`と`user.email`を検証する。
- 過去のContributor Attributionは歴史的記録として保持する。
- Commit署名は現時点では任意であり、必須化する場合は別途設計・ユーザー承認を行う。

## 5. Branch Model

### 5.1 `main`

- `main`をGitHub上の公開・統合済み正本とする。
- 新機能、複数Layer、高Risk、大規模、Phase統合およびReview／Rollback境界の分離が必要な作業は、最新`origin/main`からWorking Branchを作成する。
- 小規模で決定論的なDocs／Metadata／明白な軽微修正は、Exact Diff、Test、Sanitation、Rollback境界および当該Commit／Pushのユーザー明示承認が揃った場合だけ、直接`main`へCommit／Pushできる。
- Direct `main`の過去の承認は、次回以降のStanding Authorizationにならない。
- Merge後はLocal `main`を`origin/main`へFast-forwardし、Clean／SHA一致／`git fsck`を確認する。

### 5.2 Working Branch

```text
phase/<phase-or-subphase>-<short-purpose>
fix/<short-purpose>
docs/<short-purpose>
chore/<short-purpose>
```

例：

```text
phase/2-a-conversation-state
fix/web-cancel-boundary
docs/phase-2a-acceptance
```

- 一つのBranchは一つの有界な目的を持つ。
- Phase 2以降は、原則としてSubphase単位またはReview可能な有界作業単位でBranchを分ける。
- Branch名へ個人情報、Credential、内部Pathまたは未公開Secretを含めない。
- Branchを別目的へ使い回さない。

### 5.3 Branch Retirement

次を全て満たしたBranchは用済みとして削除候補にできる。

- Pull RequestがMerge済み
- Branch tipが`main`へ到達済み
- Local／Remoteの必要Evidenceを保存済み
- RollbackがMerge Commit、Commit SHAおよびBackupから可能
- ユーザーが削除を明示承認

削除はLocal／Remoteを別々の対象として扱う。未Merge、差分不明または作業継続中のBranchを自動削除しない。

## 6. Commit Policy

```text
<type>(<optional-scope>): <imperative summary>
```

主なType：

```text
feat     機能追加
fix      不具合修正
docs     文書だけの変更
test     Testだけの変更
refactor 外部Contractを変えない構造変更
chore    運用、Metadata、整理
build    Build／Dependency
ci       CI
revert   明示的な取消
```

例：

```text
feat(phase-2a): add bounded conversation state
fix(web): preserve cancellation ownership
docs(phase-1-ex): finalize git workflow
```

- CommitはReview可能で、単独で目的を説明できる粒度にする。
- 無関係な変更を同一Commitへ混在させない。
- History／Evidence／Sourceを意味変更する自動整形をCommitへ混ぜない。
- Commit Messageへ個人情報、Credential、内部Absolute Pathまたは秘匿事項を含めない。
- `--amend`、Interactive Rebase、Commit分割・結合またはAuthor書換えは、未Pushであってもユーザー承認なしに行わない。

## 7. Pull Request／Merge

```text
Working Branch
  → Local Test／Review
  → Publication Sanitation
  → Commit
  → Push
  → Draft Pull Request
  → Changed Files／Checks／Docs／Privacy Review
  → User Approval
  → Ready for Review
  → Merge Commit
  → Remote／Local main Postflight
```

- Pull Requestは原則Draftで開始する。
- Title／BodyにPhase、目的、主要変更、Test、既知の非Blocker、Rollback境界を記載する。
- Merge方式は原則`Merge Commit`とし、Branch上のCommitと統合点を保持する。
- Squash MergeまたはRebase Mergeは、当該Pull Requestでユーザーが明示選択した場合だけ使用する。
- GitHub Actionsが未設定の場合は、Local Validationを代替Evidenceとして明記する。未設定のChecksを合格扱いしない。
- Merge後はPR状態、Merge Commit SHA、Parent SHA、`origin/main`、Local `main`およびWorking Treeを再検証する。
- 第5.1節のDirect `main`条件を全て満たす小規模変更は本Flowの例外とできる。その場合もCommit前GateとPush後Postflightを省略しない。

## 8. Tag／Release

Phase完了Tag候補：

```text
phase-<phase>-complete
```

例：

```text
phase-1-ex-complete
phase-2-complete
```

- TagはAnnotated Tagを使用する。
- Tag対象は、Phase Final Review、User Acceptance、Continuity Refresh、Final Backupおよび`main`反映後の確定Commitとする。
- Phase途中のCommitへ完了Tagを付けない。
- 同名Tagを移動・上書きしない。誤Tagは削除・再作成を自動実行せず、影響を提示してユーザー判断を得る。
- Tag作成とTag Pushは別のExternal Mutationとして承認を得る。
- GitHub ReleaseはTagから自動作成しない。Release Note、Artifactおよび公開範囲を別途Reviewしてから作成する。
- Phase 1-ex完了Tag／Releaseは、Phase 1-ex完了時のユーザー判断により作成しなかった。後から作成する場合は別の明示承認を必要とする。

## 9. Backup／Git対応順序

Git HistoryはBackupを代替しない。規模とRiskに応じて次の二種類を使う。

### 9.1 Change-level Safety Backup

大規模統合、Root Migration、公開変更、破壊的操作または復元困難な変更の前に、ユーザーへBackup取得を明示的に依頼する。

### 9.2 Phase Final Backup

```text
実装／Docs完了
  → 全体Test／Review
  → Commit／Pushを行う場合だけPrivacy／Secret／不要物Scan
  → Open Blocker解消
  → Continuity Refresh／Reconstruction Validation
  → ユーザーへPhase Backup取得を依頼
  → Archive／SHA-512 Evidence確認
  → Final Git Commit／PR／Merge
  → main Postflight
  → 必要な最終状態Record
  → 完了Tag候補をユーザーへ提示
```

Merge後に最終状態Record等の追加差分が生じた場合は、その差分を別のReview済みCommitへ反映し、Phase Final Backup／Tag対象との対応を再確認する。Backup、Commit、Merge Commit、TagおよびRelease Evidenceの対応を曖昧にしない。

## 10. Commit／Publication Sanitation Gate

CommitまたはPushを行う作業単位では、[GitHub Publication Sanitation Policy](git_publication_sanitation_policy_ja.md)に従う。通常Docs更新、Review、Test、Task HandoffまたはPhase途中Backupごとに広範Privacy／Secret／不要物Scanを繰り返さない。

最低限、`git status`、Staged Diff、Commit予定Tree、Outgoing Commit Range／Tree／Metadata、Identity、Secret、個人情報、不要物、License、Attribution、Ignore Rule、Test、Link、Manifest、Commit／Push対象SHAおよびRemote Branchを確認する。

Sanitation失敗時はPushをBlockし、Force Push、History Rewriteまたは自動削除で回避しない。

## 11. Branch Protection

現在、Branch Protectionの有効化は未確定であり、本書の作成だけではGitHub設定を変更しない。

将来の推奨候補：

- `main`へのForce Push禁止
- `main`削除禁止
- Pull Request経由を原則化
- Review Conversation解決要求
- CI導入後にRequired Status Checksを設定

単独研究開発の継続性、緊急復旧、GitHub Plan上の制約および自動化方式を確認してから設定する。

## 12. Local Working Root Policy

### 12.1 現在の単一Canonical Root

```text
margpa-runtime-llm:
  開発内容正本
  Git Working Tree
  Existing History／Index／Remote設定
```

Source→Git Staging統合、Publication Set 1,053件のPath／Content一致、PR #1 Merge、追加Docs Commit／Push、両Root Backup、`.git`移行Preflight、macOS `ditto`によるMetadata Copy、Git PostflightおよびFull Testを経て、`margpa-runtime-llm`を単一Canonical Git Rootとした。

旧`margpa-runtime-llm_git_staging`は、ユーザーが最終Backupを取得し、Canonical RootのGit／Runtime検証に合格した後、ユーザー判断で退役・削除した。今後の通常Git運用で二重Root同期を行わない。

### 12.2 今後のRoot変更

- Canonical RootのRename、移動、削除、`.git`入替え、Worktree追加またはRemote変更は、別のBackup／Preflight／Rollback／ユーザ承認を要する。
- 過去の本Cutoverは、将来の`.git`手動Copyに対する一般許可を生成しない。
- Project Archiveの軽量化はCanonical Root自体を変更せず、Backup作業用Copyから`.venv/`等を除外して行う。

## 13. Prohibited Operations

- `main`への無承認Direct Push
- Force Push、History Rewrite、Root Commit置換
- Existing Repositoryの無承認削除・再作成
- Remote／Visibility／Branch Protectionの無承認変更
- 未Merge Branchの自動削除
- Tag移動または同名Tag上書き
- Git Historyを理由とするDocs History／Backup削減
- Backup／Exact Preflight／Rollback／User Explicit Authorizationなしの`.git`手動CopyまたはRoot統合
- Canonical Rootの無承認削除、Rename、移動または入替
- GitHub操作を、Local File Write Authorityだけから自動許可すること

## 14. Current Accepted Baseline

2026-08-04 JST時点：

```text
Pull Request       : #1 merged
Merge Method       : merge commit
Merge Commit       : 9fff303175a3224963254eacddd66f9cf5112a5a
Latest Commit      : 30d347e0ce05dd208898a4f876e54139cdcacbda
Default Branch     : main
Local／origin／remote main : aligned at 30d347e0ce05dd208898a4f876e54139cdcacbda
Working Tree       : clean at postflight
Git fsck           : pass
Publication Files  : 1,053／1,053
Path Mismatch      : 0
Content Mismatch   : 0
Merged Work Branch : retired locally and remotely after containment proof
Canonical Git Root : margpa-runtime-llm
Former Staging Root: retired／deleted after backup
Cutover Full Test  : 430 passed／3 deselected
Tag／Release        : none
Normal Commit／Push : accepted／operational
```

Commit `844394106f0330b9b8bd3652813642f34132a647`では、Canonical RootからDocs限定111件をDirect `main` Commit／Pushした。変更内訳は更新16件、新規95件、削除0件であり、Local `HEAD`、`origin/main`、Remote `main`およびGitHub APIのSHAとCommit Messageが一致した。Commit Attribution、Docs-only Scope、Privacy／Secret Scan、Link、不要Artifact非混入およびWorking Tree Cleanを確認した。

これにより、専用SSH、Existing History継承、Risk-based Branch Model、Publication Sanitation、単一Canonical Git Rootおよび通常のCommit／Push経路は運用可能なAccepted状態となった。以後は`margpa-runtime-llm`だけをGit Working Rootとして使用し、旧Staging Rootや二重同期を必要としない。

Git基盤の成立は、将来のCommit／Pushを包括承認しない。各External Mutationは第2節の明示承認Gateに従う。Branch Protection、Phase完了TagおよびReleaseは、通常Git運用の成立とは分離した任意またはPhase Closure時の別判断である。

Phase 1-ex Final ClosureはCommit `30d347e0ce05dd208898a4f876e54139cdcacbda`で`main`へ反映し、Local `HEAD`、`origin/main`およびGitHub Remote `main`の一致、Working Tree Clean、Phase Backup／RestoreおよびFinal Docs Gateを確認した。Phase 1-exは`complete_accepted`、Phase 2は開始可能状態を経てPhase 2-0 Pilot Designへ移行した。Tag／Releaseはユーザー判断により作成していない。
