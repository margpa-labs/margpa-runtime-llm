# GitHub Publication Sanitation Timing Policy Decision

```yaml
document_id: git_publication_sanitation_timing_policy_decision
phase: phase_1_ex
status: accepted_user_decision_recorded
created_at: 2026-08-02 07:39:01 JST
owner: 設計統括者役
decision_authority: user
```

## 1. Decision

Identity、Privacy、Affiliationおよび公開不要Artifactを目的とした広範Scan／Cleanupの実施時点を、GitHub Push Preparation Gateへ限定する。

通常開発、通常Docs更新、通常ReviewまたはPhase途中の各作業で、同一目的の全Project再帰Scan、名称置換および削除を繰り返さない。

## 2. Target Categories

- 第一者の旧個人Account Handle
- 作者個人情報その他の識別可能情報
- 意図しないOrganization／Company／Affiliation表記
- `.DS_Store`、`__MACOSX/`、Cache、Temporary Artifact等

正式な第三者Attribution、License、Model配布元、Platform名、研究Sourceおよび技術選定理由は自動削除対象ではない。

## 3. Git History Boundary

Push直前に現在Fileだけを修正しても、既に作成したCommitへ情報が残る。このため、Publication Gateは次を対象とする。

```text
初回公開:
  Clean Root Commitの全Tree／Metadata

後続公開:
  Remote既公開SHAからPush予定HEADまでの全Outgoing Commit Tree／Metadata
```

Sanitation合格前に公開予定Commitを確定しない。問題を含むCommitを作成済みの場合、そのCommitをそのままPushしない。

## 4. Repository Recreation／Contributor Identity

既存Web Upload由来Repository Historyは移行しない。RepositoryをClean Root Commitから作り直す。

```text
Repository Owner : margpa-labs
Contributor      : Nazuna Research専用GitHub Account
Commit Name      : Nazuna Research
Commit Email     : 専用AccountのGitHub noreply Email
```

旧個人Accountへ紐付くContributor Historyを新Repositoryへ含めない。手動File Uploadではなく、Repository-local Git Identityを設定したCommand Line Commitを使用する。

## 5. `.gitignore` Adjustment

既存Ignore Ruleを確認し、重複を避けて次を追加した。

```text
.env
.env.*
!.env.example
!.env.template
__MACOSX/
```

`.DS_Store`、`__pycache__/`、`*.py[cod]`、Test／Lint Cache、`.venv/`、`models`および`*.gguf`は既存Ruleで対応済みである。`models`全体を除外するため、その配下の個別Model Binary Patternは重複追加していない。

## 6. Supersession Boundary

本決定は、従来の「各通常作業またはBackup前に同一のIdentity／Public Debris Scanを繰り返す」と読める運用を置き換える。

ただし、次は維持する。

- Secret／CredentialのFail-closed
- Backup AllowlistとModel／`.venv`／Cache除外
- Research Asset Mutation Control
- 元Projectの無許可変更・削除禁止
- 第三者Attribution／License保持
- GitHub Push／Repository削除・再作成のユーザー最終Authority

## 7. Canonical Policy

- `docs/project/shared/operations/git_publication_sanitation_policy_ja.md`
- `docs/project/shared/operations/documentation_structure_and_task_operations_ja.md`
- `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`

## 8. Current Authorization Boundary

本記録は運用変更を有効化するが、Repository削除・再作成、`git init`、Commit、Tag、Remote設定、PushまたはHistory Rewriteを自動許可しない。
