# Documentation Legacy Root Retirement Validation

```yaml
document_id: documentation_legacy_root_retirement_validation
phase: phase_1_ex
status: passed
language: ja
created_at: 2026-07-26 16:14:11 JST
owner: 設計統括者役
rag_default: true
```

## 1. 結論

旧`docs/` Rootのカテゴリ別重複配置は、原文保全とSHA-512一致を確認した後に退役した。

退役したのは旧入口と重複Fileであり、開発日誌、判断、要件、Review、Handoff、Evidenceおよび原文そのものではない。

```text
Result                         : PASS
Inventory Entries              : 322
Non-excluded Raw Sources        : 320
Exact Raw Sources Retained      : 320／320
Phase 1-ex Stable Raw Archives  : 8／8
Raw SHA-512 Errors              : 0
Unexpected Legacy Files         : 0
Legacy Files Remaining          : 0
Git Operations                  : 0
```

## 2. Phase 1-ex原文8件

Migration前にStable Sourceとして扱われていた8件を、元File名、Timestamp、本文およびSHA-512を変えずに次へ保存した。

```text
docs/project/phases/phase_1_ex/history/adr/
docs/project/phases/phase_1_ex/history/architecture/
docs/project/phases/phase_1_ex/history/handoffs/
docs/project/phases/phase_1_ex/history/operations/
docs/project/phases/phase_1_ex/history/requirements/
```

8件すべてについて、Source Manifest記録HashとHistory保全先のSHA-512が一致した。

## 3. 全Source保全

非除外Source 320件は次のいずれかで原文を解決できる。

- Phase 1 Raw History
- Phase 1-ex Raw History
- Public Current
- Public Milestone History

Source Path、分類、原文保持先およびSHA-512は[Legacy Root Retirement Manifest](documentation_legacy_root_retirement_manifest.json)に記録した。

`.DS_Store` 2件は文書ではないため保全対象外とし、退役時に除外した。

## 4. 退役範囲

次の旧入口は退役済みであり、再作成しない。

```text
docs/adr/
docs/architecture/
docs/governance/
docs/handoffs/
docs/operations/
docs/requirements/
docs/user_manual/
docs/documentation_index_*.md
```

Public Currentは`docs/public/roadmap_ja.md`を維持し、旧Timestamp Public Historyは`docs/public/history/roadmap_phase_1_ja.md`として保全した。

## 5. 安全停止記録

最初のArchive検証では、macOSが自動更新した`.DS_Store`のHash変化を検出して安全停止した。この時点で旧Root Fileの退役は1件も実行していない。

除外Metadataを文書Hash検証対象から外し、すでに作成済みだった8件のArchiveはHash一致時だけ再利用するよう処理を修正した。その後、全Source保全検証を再実行して合格してから退役した。

## 6. Backup／Rollback

- Phase 1 Verified Backup
- Source→Target Manifest
- Legacy Root Retirement Manifest
- Phase 1／Phase 1-ex Raw History
- Public Milestone History
- ユーザー作成の`margpa-runtime-llm_docs削除前_20260726.zip`

旧Root構造を通常入口へ戻すことはRollbackの既定動作にしない。必要ArtifactだけをRaw HistoryまたはBackupから復元し、Current／Phase Indexを再検証する。

## 7. Evidence

- [Migration Receipt](documentation_directory_migration_receipt_ja.md)
- [Migration Validation](documentation_directory_migration_validation_ja.md)
- [Source→Target Manifest](source_to_target_documentation_migration_manifest.json)
- [Legacy Root Retirement Manifest](documentation_legacy_root_retirement_manifest.json)
- [Link／Rollback Plan](documentation_link_update_and_rollback_plan_ja.md)
