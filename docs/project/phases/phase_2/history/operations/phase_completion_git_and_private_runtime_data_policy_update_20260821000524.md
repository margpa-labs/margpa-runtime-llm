# Phase Completion Git／Private Runtime Data Policy Update

```yaml
document_type: policy_change_record
status: applied_uncommitted
phase: phase_2
created_at: 2026-08-21 00:05:24 JST
from: user
to: all_project_roles_and_git_operations
commit: not_performed
push: not_performed
```

## 1. Decision

通常のGit Commit／Pushは、原則として次のPhase境界で行う。

```text
現Phase Final Check／User Acceptance
  → 現Phase Complete／Accepted
  → 次Phaseの目的・入口・責任Role・主要Gate・開始条件を整備
  → 次Phase READY／開始可能
  → User Explicit Authorization
  → Sanitation／Test／Scope確認
  → Commit／Push
  → Local／origin／Remote一致確認
```

`次Phase READY`は次Phaseの実装開始、Automation ActivationまたはGit Standing Authorizationを意味しない。重大Risk、長期差分、復元困難な変更またはユーザー指定時は、Phase途中のBackup／Git Checkpointを例外使用できる。

## 2. Private Conversation Git Boundary

個人Chat履歴をCommit／Push対象から除外するため、`.gitignore`へ次を追加した。

```text
/runtime_data/persistent/**/conversations/
/runtime_data/recovery/checkpoints/**/conversations/
/runtime_data/recovery/migrations/**/conversations/
```

対象は、永続Conversation DB、Citationを含むConversation Store、Migration用Conversation SnapshotおよびRecovery Checkpointである。`runtime_data/`全体を除外せず、将来の公開可能なEvaluation／Experiment Artifactと個人Conversation Dataを分離する。

個人Conversation Dataを`git add -f`、別名CopyまたはArchive化でGitへ含めない。現時点で`runtime_data/`配下のGit追跡Fileは0件であることをCommit前に確認する。

## 3. Claude Local Configuration Removal

ユーザー指示により、Project Root内の未追跡`.claude/`を削除した。

削除対象として事前確認した内容：

```text
.claude/settings.local.json
.claude/launch.json
.claude/worktrees/
```

Claude側でも不要と判断済みであり、本DirectoryをRepository Authority、RecoveryまたはEvidenceとして使用しない。削除前にGit追跡対象ではなかったため、Gitからは復元できない。

## 4. Stable Documents Updated

- `docs/project/shared/operations/git_workflow_policy_ja.md`
- `docs/project/shared/operations/phase_completion_review_and_backup_gate_ja.md`
- `docs/public/roadmap_ja.md`

各Stable文書について、変更前後の完全Snapshotを対応Historyへ保存し、`cmp`による原文一致を確認した。

## 5. Current Git Boundary

本変更は、保留中のPhase 2-E差分へ追加された未Commit変更である。本Record作成時点でStage、CommitまたはPushは行わない。今後のCommit／Pushは、本Decisionに従い、現Phase完了と次Phase READYを確認したPhase境界で、ユーザーの明示承認後に行う。
