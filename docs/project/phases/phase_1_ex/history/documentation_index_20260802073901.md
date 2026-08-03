# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260802073901
state_at: 2026-08-02 07:39:01 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - documentation_index_20260801154412.md
  - operations/git_publication_sanitation_timing_policy_decision_20260802073901.md
  - ../../../shared/operations/git_publication_sanitation_policy_ja.md
  - ../../../shared/operations/documentation_structure_and_task_operations_ja.md
  - ../../../shared/task_roles/task_role_write_authority_policy_ja.md
  - ../../../../../.gitignore
supersedes: documentation_index_20260801154412.md
source: user_git_publication_sanitation_timing_change_and_clean_repository_identity_decision
```

本Snapshotは[2026-08-01 15:44:12版](documentation_index_20260801154412.md)までの全状態を継承し、GitHub Publication Sanitationの実施時点変更、Clean Repository Recreation、専用Contributor Identityおよび`.gitignore`追加をAppend-onlyで記録する。

既存Historyは各時点の判断として保持し、編集、削除または新決定への置換を行っていない。

## 1. User Decision

```text
Routine Development:
  Identity／Affiliation／Public Debrisの全Project Scanを定例実行しない

GitHub Publication Unit:
  Push対象Commit作成前からRemote反映後までScan／Sanitationを行う

Scan Target:
  Working Tree
  Git Index
  Commit／Tag Metadata
  初回Root Commit全Tree
  後続Outgoing Commit全Tree
```

対象Categoryは、第一者の旧個人Account Handle、作者個人情報その他の識別可能情報、意図しないOrganization／Company／Affiliation表記および`.DS_Store`等の公開不要Artifactである。

## 2. Clean Repository／Contributor Identity

既存Web Upload由来Historyは正式Repositoryへ移行せず、Clean Root CommitからRepositoryを作り直す方針へ変更した。

```text
Repository Owner : margpa-labs
Contributor      : Nazuna Research専用GitHub Account
Commit Name      : Nazuna Research
Commit Email     : 専用AccountのGitHub noreply Email
```

旧個人Accountへ紐付くCommitおよびContributor Historyを新Repositoryへ含めない。手動File Uploadではなく、Repository-local Git Identityを設定したCommand Line Commitを使用する。

## 3. Canonical Policy

- [GitHub Publication Sanitation Policy](../../../shared/operations/git_publication_sanitation_policy_ja.md)
- [Documentation Structure／Task Operations](../../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Task Role／Write Authority Policy](../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Decision Record](operations/git_publication_sanitation_timing_policy_decision_20260802073901.md)

通常開発時のScan停止は、Secret／Credential Fail-closed、Backup Allowlist、Model／`.venv`／Cache除外、第三者Attribution保持またはResearch Asset Mutation Controlを解除しない。

## 4. `.gitignore`

追加済み：

```text
.env
.env.*
!.env.example
!.env.template
__MACOSX/
```

既存で対応済み：

```text
.DS_Store
__pycache__/
*.py[cod]
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
htmlcov/
.venv/
/models
*.gguf
/var/
```

Model Root全体を除外するため、その配下の`.bin`、`.safetensors`、`.pt`および`.pth`個別Patternは重複追加していない。

## 5. Integrity

```text
Previous Documentation Index:
  b9777e1864efc7b2054f0ff720a0a53fb00f8f42297a6cc7851c43adc5073fc92496e88ddb260031b543bbd4e44d78d268e8d447e90106360b30eb4bf84504cb

.gitignore:
  4d104e1264c06923c7f3f3732ea4808681c9e90d5fa2d568377dd9bec59d0e8b7fd58d15353388568e89fbfb5987c3d8dc5ab34ac7e51bc3c63fd346b476f6c3

GitHub Publication Sanitation Policy Stable／History:
  ea3d60904a971cf8f343636734cdccc7a85a0045b7622ebf02d5d01ff4793bdf3df42a5fee9a92901c6b290da30752f4bbf975c23751c143fafc4a7d95ff5fc7

Documentation Structure／Task Operations Stable／After:
  5889316fe5ea7e58e92834b7757ac71ff314958b27771798a95bb755a547d0a294a0f797978b9b69fb4c5fadf7769b78d8f74dcb5029ced0496f890007b06196

Task Role／Write Authority Stable／After:
  9cda793d74c7ef194afe74e5e92603130a0a329581173bf15cee5e1e3e52e43f609402cb831333811065aa643edb6be827d7d2d2147c896c0648962ae4bd22f3

Phase Index Stable／After:
  3104eae9d551e2d88c62499b7480adddcdc86f86938da650c2013bd7191e6c475f61aae6946526e08db42606159d24eb03de060566b3766099b45adcdc2b8890

Decision Record:
  79d0a7e2cd8f03a2246c316c4bc6ae8d9a7f9ac0b02f7bf7e13fff6b8e506c5f481fccc0bbfad7f48924ff2ac3191002662b765f8bce623587a6d2c333287a22
```

Stable文書と対応After SnapshotのSHA-512一致を確認済みである。

## 6. Mutation Boundary

```text
Git／GitHub Operation:
  NONE

Repository Delete／Recreate:
  NONE

Commit／Tag／Remote／Push:
  NONE

Source／Config／Script／Test Mutation:
  NONE

Root Metadata Updated:
  .gitignore only

Docs Updated:
  Shared Operations
  Shared Role Authority
  Phase 1-ex Index

Append-only Added:
  Canonical Sanitation Policy
  Before／After Stable Snapshots
  Decision Record
  Documentation Index Snapshot
```

## 7. Next Gate

次はGit運用設計を確定する。

```text
Branch／Commit／Tag
Repository-local Author／Committer Identity
Authentication
Backup／Commit／Push順序
Clean Root Commit Allowlist
Repository Recreation Procedure
Rollback／Verification
```

本Snapshotは`git init`、Commit、Repository削除・再作成またはPushを許可しない。
