# Documentation Link Update／Rollback Plan

- 文書ID: `documentation_link_update_and_rollback_plan`
- 状態: `completed_legacy_root_retired`
- 作成日時: `2026-07-26 15:03:49 JST`
- 更新日時: `2026-07-26 16:14:11 JST`
- Snapshot: `20260726150349`
- 作成担当: 設計統括者役
- Target Architecture: [phase_1_ex_target_documentation_structure_20260726145451.md](../architecture/target_documentation_structure_ja.md)
- Inventory: [documentation_source_inventory_and_classification_20260726150349.md](documentation_source_inventory_and_classification_ja.md)
- Machine Manifest: [source_to_target_documentation_migration_manifest_20260726150349.json](source_to_target_documentation_migration_manifest.json)
- 正本言語: 日本語
- supersedes: なし

## 1. Migration Strategy

一括Move／Deleteを最初に行わない。

```text
Source Freeze
  → Target Copy
  → Stable Rename／Link Update
  → Compilation／Canonical生成
  → Inventory／Hash／Link検証
  → Current Index切替
  → Task通知
  → Source Tree Retirement判定
```

Old Sourceを残したままTargetを検証し、Cutover完了前に破壊しない。

この順序を守り、Target検証、Task通知、ユーザー確認、Phase 1-ex原文8件の追加History保全、全Source Hash再検証の後に旧Root重複配置を退役した。

## 2. Link Classes

### 2.1 History内相対Link

Phase 1旧Treeを`phase_1/history/`配下へ同じ相対構造でCopyする。

```text
history/adr/
history/architecture/
history/governance/
history/handoffs/
history/operations/
history/requirements/
history/user_manual/
history/documentation_index_*.md
```

同一Phase History内のCategory横断Linkは可能な限り原文のまま成立させる。

### 2.2 Cross-phase Link

Phase 1-ex文書からPhase 1 Historyを参照するLinkは、Stable文書側で新Pathへ更新する。

Raw History原本のLinkは改変しない。Raw History内で壊れるCross-phase LinkはKnown ExceptionとしてLink Reportへ記録し、Phase IndexまたはSource ManifestからTargetを解決できるようにする。

### 2.3 Public Link

Public Current Pathを維持する。

```text
docs/public/roadmap_ja.md
```

旧Historyだけ次へRenameする。

```text
docs/public/history/roadmap_phase_1_ja.md
```

Public Historyへ直接Linkする場合はMilestone Filenameへ更新する。

### 2.4 Current／Compilation Link

新規Current、Phase CompilationおよびPhase IndexはTarget Pathだけを使う。旧Timestamp Pathへ直接依存しない。

Source TraceabilityはSource Manifestから解決する。

## 3. Link Rewrite Boundary

Rewrite可能：

- Stable Phase 1-ex文書
- Current Canonical Docs
- Phase Compilation
- Phase Index
- Public Current Docs
- Task Notification

Rewriteしない：

- Phase Historyの旧Granular本文
- Immutable Status／Review／Handoff
- 旧Documentation Index

## 4. Link Validation

実移動前：

- Source Link存在確認
- Source→Target Mapping
- Projected Target Link解析
- Cross-phase／Public／Missing分類

Target Copy後：

- Markdown Relative Link
- Local File Link
- Anchor候補
- Duplicate Target
- Case Sensitivity
- `_ja` Filename
- Timestamp除去後のCollision

History Raw Linkの既知例外を除き、Stable／Current／Compilation／PublicのBroken Linkを0にする。

## 5. Copy-first Cutover

### Stage A

Target Directoryを作り、SourceをCopyする。Old Treeは維持する。

### Stage B

- Stable FilenameへRename
- Stable文書のLink更新
- History Treeの相対構造検証
- Compilation／Canonical生成
- Current Index生成

### Stage C

- Source Count
- Target Count
- SHA-512
- Link
- Identity
- Secret
- RAG Scope
- Test

### Stage D

設計統括者役がCutover Reviewを行い、ユーザー確認後にOld Tree Retirementへ進む。

## 6. Rollback Sources

```text
Phase 1 Verified Backup:
MARGPA-RUNTIME-LLM/phase_backups/phase_1/

Phase 1-ex Pre-migration Source:
Source→Target Manifest＋Source SHA-512

Old docs Tree:
退役前は変更せず保持

Post-retirement Raw Sources:
Phase History＋Public History＋Source Manifest

User-managed Pre-migration Backup:
margpa-runtime-llm_docs削除前_20260726.zip
```

Phase 1 BackupはPhase 1-ex開始後の文書を含まないため、Pre-migration ManifestとDelta Scanを併用する。

## 7. Rollback Conditions

- Source Count不一致
- SHA-512不一致
- Target Collision
- Stable Broken Link
- Current Indexから正本を解決不能
- Lossless Source Mapping不足
- Public／Project境界誤り
- RAG DefaultにHistoryが混入
- 個人情報、CredentialまたはSecret検出
- Task Write Scopeが不明

## 8. Rollback Procedure

Cutover前：

```text
Target Candidateを無効化
→ Current Indexを旧Pathのまま維持
→ Old Source Treeを使用
```

Cutover後かつGit開始前：

```text
Migration Receiptを確認
→ Retirement ManifestからRaw保持先とSHA-512を確認
→ Phase History／Public History／Backupから必要Artifactを復元
→ Current IndexとStable Targetを再検証
→ 新TimestampのRollback Recordを作成
```

Git開始後：

```text
Accepted Git Procedureに従う
```

`git reset --hard`等を自動使用しない。

## 9. Source Retirement

Old Treeを即Deleteせず、Raw保全とHash一致の検証後に重複配置だけを退役する。

Retirement前提：

- Target Acceptance
- User Confirmation
- Backup／Manifest
- Task Notification
- Git Initial Commit Allowlistとの整合

Old SourceをProjectから外す場合も、Phase Historyへ同内容が存在し、Hashが一致することを確認する。

## 10. Authorization Boundary

本Planに基づくCopy-first Migration、Link Rewrite、Raw History保全、旧Root重複配置の退役までをユーザー許可の範囲内で実行した。

## 11. Execution Result

```text
Copy-first Target Construction : completed
Stable Link Rewrite            : 22／22
Non-history Broken Link        : 0
Immutable Copy Hash Error      : 0
Legacy Root Duplicate Retire   : 319
Excluded Metadata Retire       : 2
Self-excluded Manifest Retire  : 1
Legacy Files Remaining         : 0
Git Operation                  : not executed
```

Rollback SourceはPhase History、Public History、Source Manifest、Retirement Manifest、Phase 1 Verified Backupおよびユーザー作成のMigration前Backupとして引き続き保持する。
