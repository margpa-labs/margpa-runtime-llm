# UnresolvedからUnresolved WorkへのDirectory移行Evidence

```yaml
document_id: unresolved_to_unresolved_work_directory_migration_evidence_20260906183423
document_type: append_only_directory_migration_evidence
document_state: completed
recorded_at: 2026-09-06 18:34:23 JST
language: ja
authority_owner: Nazuna Research
append_only: true
```

User決定により、未解決のDirectory名を他のWork分類と揃えた。

- `docs/project/shared/unresolved/` → `docs/project/shared/unresolved_work/`
- `docs/project/shared/history/unresolved/` → `docs/project/shared/history/unresolved_work/`

Stable 1 File、History 25 Filesを移行した。Markdown内の`unresolved/`参照は、相対Pathを含め`unresolved_work/`へ機械的に追随させた。Filename内の`unresolved`は文書内容を表す語であり、変更していない。

移行後、旧`unresolved/`参照がDocs内に残っていないこと、Stable Registryと代表History Snapshotを新Pathで読めることを確認した。
