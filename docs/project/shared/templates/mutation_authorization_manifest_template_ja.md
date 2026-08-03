# Mutation Authorization Manifest Template

本Templateは、研究資産へMutationを行う前の人間確認用である。

一項目でも未確定の場合、Mutationへ進まない。

```yaml
schema_version: "1"
mutation_id: ""
requested_by: user

target_kind: original_project | user_copy | public_copy | explicit_external_target
target_root: ""

allowed_paths:
  - ""

allowed_actions:
  - create | edit | replace | move | rename | delete | metadata | permission

forbidden_actions:
  - external_access
  - follow_symlinks

external_access: deny
follow_symlinks: false
bulk_operation: false

before_inventory_complete: true
proposed_diff_presented: true
backup_status: user_confirmed_complete
rollback_plan_presented: true
irreversible_effects_presented: true

final_user_approval: ""
approval_scope: single_operation
expires_after_operation: true

notes: []
```

## Before実行確認

- [ ] 対象は元ProjectかCopyか明示されている。
- [ ] Target Rootを正規化済み絶対Pathで確認した。
- [ ] Project Root外へのアクセス有無を確認した。
- [ ] Symbolic Linkを追跡しない。
- [ ] 対象File／Directoryを完全列挙した。
- [ ] Mutation候補と削除候補をユーザーへ提示した。
- [ ] 復元不能になる情報を提示した。
- [ ] ユーザーが今回のBackup完了を明示した。
- [ ] Rollback方法を提示した。
- [ ] ユーザーが今回の対象とActionを最終承認した。
- [ ] Commandが暗黙に別Pathへ書き込まない。
- [ ] 承認範囲外の追加作業を含まない。

## After実行確認

- [ ] 承認対象だけを変更した。
- [ ] Before／After差分を検証した。
- [ ] 変更・未変更・失敗を報告した。
- [ ] 削除物と復元不能物を報告した。
- [ ] Project Root外Artifactを作成していない、または明示承認済みである。
- [ ] 承認を別作業へ再利用していない。
