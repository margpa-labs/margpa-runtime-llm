# Documentation Directory Migration Receipt

```yaml
document_id: documentation_directory_migration_receipt
phase: phase_1_ex
status: completed_validated_legacy_root_retired
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-26 16:14:11 JST
migration_snapshot: 20260726151624
owner: 設計統括者役
rag_default: true
```

## 1. Execution Scope

```text
Delta Scan              : PASS
Source Inventory        : 322
Mapped Sources          : 320
Excluded .DS_Store      : 2
Phase 1 Raw History     : 307
Phase 1-ex Raw History  : 11
Stable Copy             : 8
Public Current In-place : 1
Public History Copy     : 1
Exact Raw Retained      : 320／320
Stable Link Rewrite     : 22
Phase 1 Compilation     : 307 Sources／8 Categories
Legacy Duplicate Retire : 319
Excluded Metadata Retire: 2
Manifest Duplicate Retire: 1
Legacy Files Remaining  : 0
Git Operation           : NO
Retirement Notification : SENT／ACKNOWLEDGED
```

## 2. Copy-first Boundary

最初に旧`docs/` Treeを残したまま、`docs/project/`と新Public Milestone Historyを構築した。

Raw HistoryはSource SHA-512一致を要求し、Stable文書は本文を維持したままTarget配置に必要なLocal Linkだけを更新した。

その後、Phase 1-exのStable Source 8件もTimestamp付き原文のまま`phase_1_ex/history/`へ追加保全した。全320件の非除外SourceについてRaw保持先とSHA-512一致を再検証し、ユーザーが作成したMigration前Backupの存在を確認してから、旧Rootの重複配置だけを個別に退役した。

ここで退役したのは旧入口と重複Fileであり、開発日誌・判断・Evidence・原文そのものではない。

## 3. Compilation Counts

```text
ADR                     : 26
Architecture            : 45
Governance              : 5
Handoffs／Reviews       : 99
Operations              : 11
Requirements            : 38
User Manual             : 7
Documentation Index     : 76
Total                   : 307
```

## 4. Source Evidence

- [Source Inventory](documentation_source_inventory_and_classification_ja.md)
- [Migration Manifest](source_to_target_documentation_migration_manifest.json)
- [Legacy Root Retirement Manifest](documentation_legacy_root_retirement_manifest.json)
- [Legacy Root Retirement Validation](documentation_legacy_root_retirement_validation_ja.md)
- [Candidate Report](documentation_migration_candidate_report.json)
- [Rollback Plan](documentation_link_update_and_rollback_plan_ja.md)

## 5. Validation

Target Validationは合格した。

```text
Original Source Error         : 0
Mapped Target Missing         : 0
Immutable Target Hash Error   : 0
Phase 1 Compilation Coverage  : 307／307
Non-history Local Links       : 2,975
Non-history Broken Links      : 0
Required Canonical Missing    : 0
Forbidden Identity／Secret    : 0
```

- [Target Validation](documentation_directory_migration_validation_ja.md)
- [Target Manifest](documentation_directory_migration_target_manifest.json)

## 6. Cutover

```text
Current Entry:
docs/project/current/documentation_index_ja.md

Active Phase Entry:
docs/project/phases/phase_1_ex/phase_index_ja.md

Target Path Authority:
effective

Old Category Root:
retired／must not be used

Raw Source Evidence:
Phase History／Public History／Manifest
```

実装者役と対外Docs役へ最初のPath／Authority変更を通知し、両担当のAcknowledgementを受領した。旧Root退役後にも再通知した。

Git操作およびGitHub公開は実行していない。Public Canonical文書の本格作成もまだ開始していない。
