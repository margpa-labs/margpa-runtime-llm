# Documentation Migration Task Notification Plan

- 文書ID: `documentation_migration_task_notification_plan`
- 状態: `accepted_plan_not_sent`
- 作成日時: `2026-07-26 15:03:49 JST`
- 更新日時: `2026-07-26 15:03:49 JST`
- Snapshot: `20260726150349`
- 作成担当: 設計統括者役
- 対象: 実装者役、対外Docs役、将来のPhase別設計者役
- Target Architecture: [phase_1_ex_target_documentation_structure_20260726145451.md](../architecture/phase_1_ex_target_documentation_structure_20260726145451.md)
- Authority Policy: [task_role_write_authority_policy_20260726150349.md](../requirements/task_role_write_authority_policy_20260726150349.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Notification Timing

実Directory Migration、ValidationおよびCurrent Index切替が完了した後に通知する。

Migration前に新PathをCurrentとして通知しない。

## 2. Common Notification

全担当へ次を通知する。

```text
Migration State
Current Documentation Index
New Directory Tree
Active Phase
Stable Filename Policy
Timestamp Event Policy
Read-only Scope
Write Scope
History Immutable Rule
Handoff／Status Path
RAG Default Scope
Git State
Rollback Contact Point
```

個人連絡先は記載しない。Project内のHandoff／Indexを連絡点とする。

## 3. 実装者役向け

通知内容：

- `src／tests／scripts`のAuthorityは継続する。
- `config／pyproject／uv.lock`はAccepted Handoff＋ユーザー許可が必要。
- Requirements、Architecture、Governance、ADRはRead-only。
- Statusの新規配置。

Target：

```text
docs/project/phases/<active_phase>/history/handoffs/
implementer_status_<subject>_<timestamp>.md
```

Migration前の旧`docs/handoffs/`へ新規Statusを書かない開始時点を明示する。

## 4. 対外Docs役向け

通知内容：

- `docs/public/`のCurrent／History規則
- README／LICENSE／NOTICE／CITATION
- Public HistoryはPhase／Release Filename
- Canonical技術正本はRead-only
- Lossless Compilationの内容変更禁止
- EASA／DLAGSA／OCILNSの公開粒度
- 個人情報／連絡先を掲載しない

Status Target：

```text
docs/project/phases/<active_phase>/history/handoffs/
external_docs_status_<subject>_<timestamp>.md
```

## 5. Phase別設計者役向け

Phase 2から使用するTemplate通知を準備する。

- Assigned Phase
- Parent Requirements
- Cross-Phase Boundary
- Phase Directory
- Escalation条件
- Phase Index
- Implementer Handoff
- Final Review Gate

## 6. 設計統括者役

本Task自身はMigration完了後に次をCurrent入口とする。

```text
docs/project/current/documentation_index_ja.md
docs/project/phases/phase_1_ex/phase_index_ja.md
```

## 7. Notification Evidence

各通知は新しいHandoff Eventとして記録する。

最低限：

```text
recipient_role
notified_at
current_index
active_phase
write_scope
read_only_scope
acknowledgement
open_questions
```

Task IDまたはThread IDを公開文書へ不要に記録しない。

## 8. Failure Handling

- 担当Taskが旧Pathを参照している場合、移行通知を再送する。
- 未完了作業中なら、旧Pathで完了させるか新Pathへ切り替えるかを明示する。
- 同じStatusを旧新両方へ書かない。
- Acknowledgement前に旧Directoryを削除しない。

## 9. Authorization Boundary

本Planは通知内容を確定するが、現時点では各担当Taskへ通知しない。
