# Documentation Directory Migration Validation

```yaml
document_id: documentation_directory_migration_validation
phase: phase_1_ex
status: passed_legacy_root_retired
language: ja
created_at: 2026-07-26 15:36:45 JST
updated_at: 2026-07-26 16:14:11 JST
migration_snapshot: 20260726151624
owner: 設計統括者役
rag_default: true
```

## 1. Result

```text
Migration Validation     : PASS
Cutover State            : COMPLETE
Legacy Root Duplicates   : RETIRED
Raw Development History  : PRESERVED
```

## 2. Source／Target

```text
Original Inventory Sources            : 322
Original Source Added／Missing／Changed: 0／0／0
Mapped Source Targets Missing          : 0
Immutable Target Files                 : 311
Immutable Target SHA-512 Error         : 0
Excluded .DS_Store in Target           : 0
Exact Raw Source Retained              : 320／320
Legacy Root Files Remaining            : 0
```

## 3. Phase 1 Compilation

```text
Expected Source Documents : 307
Compiled Source Markers    : 307
Missing                    : 0
Extra                      : 0
Duplicate                  : 0
```

各Sourceは8 Category Compilationのいずれかに一度だけ収録され、Source PathとSHA-512を保持する。

## 4. Link

Raw Historyを除くStable／Current／Compilationを検査した。

```text
Markdown Documents Checked : 30
Local Links Checked         : 2,975
Broken Links                : 0
Stable Rewrites             : 22／22
```

Raw Historyの既知例外はSource Manifestに保持し、History本文を変更していない。

## 5. Canonical

次の必須文書が存在する。

- Current Documentation Index
- Requirements Specification
- System Architecture
- Technology Selection
- Basic Design
- Runtime Governance Specification
- Project Continuity Master
- Documentation Rules
- Task Role／Write Authority
- Phase 1 Index
- Phase 1-ex Index

Missingは0である。

Target Inventoryの件数、Total BytesおよびInventory Digestは、自己参照を避けてTarget Manifest自体を除外した[Target Manifest](documentation_directory_migration_target_manifest.json)だけを正本とする。

## 6. Identity／Secret

Targetに対し、旧公開名義、実個人名、実個人Path、代表的Credential／TokenおよびPrivate Key Patternを検査した。

```text
Forbidden Identity Literal : 0
Actual Personal Path        : 0
Credential／Secret Pattern  : 0
```

## 7. Rollback

- Phase 1 Verified Backupを維持する。
- Source→Target ManifestとSource SHA-512を維持する。
- Phase 1／Phase 1-ex Raw HistoryとPublic Milestone Historyを維持する。
- ユーザー作成の`margpa-runtime-llm_docs削除前_20260726.zip`をProject外の補助Backupとして扱う。
- 旧Rootの重複配置は退役済みであり、Rollback時も旧構造を通常入口として復活させない。
- Git操作を実行していない。

## 8. Evidence

- [Migration Receipt](documentation_directory_migration_receipt_ja.md)
- [Source→Target Manifest](source_to_target_documentation_migration_manifest.json)
- [Legacy Root Retirement Manifest](documentation_legacy_root_retirement_manifest.json)
- [Legacy Root Retirement Validation](documentation_legacy_root_retirement_validation_ja.md)
- [Target Manifest](documentation_directory_migration_target_manifest.json)
- [Candidate Report](documentation_migration_candidate_report.json)
- [Rollback Plan](documentation_link_update_and_rollback_plan_ja.md)
