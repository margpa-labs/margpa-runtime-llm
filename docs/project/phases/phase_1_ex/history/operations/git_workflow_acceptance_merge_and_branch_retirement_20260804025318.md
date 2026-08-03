# Git Workflow Acceptance／PR Merge／Branch Retirement Record

```yaml
document_id: git_workflow_acceptance_merge_and_branch_retirement
phase: phase_1_ex
status: accepted
created_at: 2026-08-04 02:53:18 JST
owner: 設計統括者役
decision_authority: user
supersedes: null
```

## 1. Scope

本Recordは、既存Repository Historyを保持したGit統合、Pull Request #1、`main`反映、Postflight、残るGit運用設計およびMerge済み作業Branchの退役を記録する。

本RecordはPhase 1-ex完了、Tag作成、Release作成、Branch Protection設定またはLocal Working Root統合を意味しない。

## 2. Accepted Repository Result

```text
Repository           : margpa-labs/margpa-runtime-llm
Pull Request         : #1
Pull Request State   : merged
Merge Method         : merge commit
Merge Commit         : 9fff303175a3224963254eacddd66f9cf5112a5a
First Parent         : 55e0ab854db07212dce987d1a7d7c4e43e2b63c6
Second Parent        : 3a645f7317cd5c7f702c6004b8eb0b96d9c261cf
Default Branch       : main
Local main           : aligned with origin/main
Working Tree         : clean at postflight
Git fsck             : pass
Tag／Release          : none
```

Pull RequestはDraftで作成し、変更範囲、Test、Sanitation、Rename／DeleteおよびRollback境界をReviewした後、ユーザー承認によりDraft解除とMerge Commit方式のMergeを行った。

## 3. Source／Target Final Verification

```text
Source Publication Files : 1,053
Target Tracked Files      : 1,053
Source-only               : 0
Target-only               : 0
Missing in Source         : 0
Content Mismatch          : 0
Legacy docs/phases        : 0
Obsolete Lightning Images : 0
Current Lightning Images  : 6
Root Demo Images          : 6
```

Gitの非実行Bit File Mode差はGit Tree上で同じ`100644`として扱われるため、内容不一致ではない。Executable Contractは別途Test済みである。

## 4. Branch Retirement

対象Branch：

```text
phase/1-ex-publication-preparation
```

削除前に次を確認した。

```text
Local Branch tip  is ancestor of main        : yes
Remote Branch tip is ancestor of origin/main : yes
Pull Request state                            : merged
Merge Commit／Parents                         : verified
```

ユーザーは、用済みであればBranchを削除してよいと明示した。包含証明後、Remote BranchとLocal Branchを削除した。`main`、Pull Request、Merge Commit、既存Commit、Backup、TagおよびReleaseには変更していない。

## 5. Git Workflow Design Acceptance

次をShared Stable正本として確定した。

- [Git Workflow Policy](../../../../shared/operations/git_workflow_policy_ja.md)
- [GitHub Publication Sanitation Policy](../../../../shared/operations/git_publication_sanitation_policy_ja.md)
- [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)

主な確定事項：

- Existing Repository／Historyを保持する。
- `main`を統合済み正本とし、通常変更はWorking Branch＋Draft PRから行う。
- Merge方式は原則Merge Commitとする。
- Commit Messageは`type(optional-scope): summary`形式を用いる。
- Author／Committerは公開名義とGitHub-linked private noreply Emailを使い、具体値をDocsへ記録しない。
- Force Push、History Rewrite、Repository再作成を無承認で行わない。
- Phase完了TagはAnnotated Tag候補`phase-<phase>-complete`とし、Phase Final Gate後に別承認で作成・Pushする。
- GitはDocs HistoryおよびBackupを代替しない。
- Branch Protectionは未設定であり、別途検討する。

## 6. Local Working Root Decision

現在の責務：

```text
Original Project Working Tree : 開発内容正本。Git Metadataなし
Git Staging Clone             : Git History／Remote／Commit／PR用
```

`margpa-runtime-llm_git_staging`を永久に別Rootとして使う必要はない。ただしPhase 1-ex途中でRoot構成を変更すると、既に検証済みPath、`.venv`、Model Link、Task CWD、BackupおよびGit History境界が同時に変わるため、本時点では二重Rootを維持する。

Phase 1-ex Final Backup後、Phase 2開始前を第一候補として、Git Clone全体を単一Git Working Rootへ移行する。`.git`だけをOriginalへCopyしない。移行はBackup、SHA-512、Tree一致、Runtime Test、Path更新、Rollbackおよびユーザー承認を必須とする。

## 7. Remaining Decisions／Work

- Branch Protectionをいつ有効化するか。
- Phase 1-ex Final Review／Continuity Refresh／Backup／Tag。
- 二重Rootから単一Git Rootへ移行するか、およびCanonical Path。
- Optional `_en` Stable DocsをPhase 1-exで実施するかPhase 2前半へ延期するか。
- GitHub Releaseを作成する時期とArtifact Scope。

## 8. Mutation Boundary

```text
Original Project Docs     : Git運用正本、Stable更新、History／Indexを追加
Original Runtime Code     : unchanged
Original Config／Tests    : unchanged
Git Staging main          : unchanged after postflight
Remote main               : unchanged after accepted merge
Merged Local Branch       : deleted with user authorization
Merged Remote Branch      : deleted with user authorization
Tag／Release              : none
Visibility／Metadata      : unchanged
Branch Protection         : unchanged
other/                    : not accessed
```
