# Documentation Migration Preflight

- 文書ID: `documentation_migration_preflight`
- 状態: `pre_migration_design_gate_passed_with_known_link_exceptions`
- 作成日時: `2026-07-26 15:03:49 JST`
- 更新日時: `2026-07-26 15:03:49 JST`
- Snapshot: `20260726150349`
- 作成担当: 設計統括者役
- Inventory: [documentation_source_inventory_and_classification_20260726150349.md](documentation_source_inventory_and_classification_20260726150349.md)
- Machine Manifest: [source_to_target_documentation_migration_manifest_20260726150349.json](source_to_target_documentation_migration_manifest_20260726150349.json)
- Rollback Plan: [documentation_link_update_and_rollback_plan_20260726150349.md](documentation_link_update_and_rollback_plan_20260726150349.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Preflight Scope

- Inventory Completeness
- Source Hash
- Source→Target Uniqueness
- Target Collision
- Planned Output Collision
- Source Relative Link
- Projected Target Link
- Public／Cross-phase Link
- Filename／Case
- Identity／Secret
- Rollback Readiness

## 2. Machine Result

```text
Inventory Entries                  : 322
Mapped Sources                     : 320
Excluded Sources                   : 2
Unclassified Sources               : 0
Target Collisions                  : 0
Planned Output Collisions          : 0
Relative Links                     : 2,874
Source Missing Links               : 1
Projected Preserved Links          : 2,777
Projected Rewrite Required         : 22
Projected Known History Exceptions : 39
External to Docs Inventory         : 35
```

## 3. Acceptance Rule

実Copyへ進むための条件：

```text
Unclassified Sources      : 0
Target Collisions         : 0
Planned Output Collisions : 0
Source Hash               : all present
Rollback Source           : ready
```

Source Missing LinkとProjected History Exceptionは、原本を改変せずKnown Exceptionとして列挙できる。Stable／Current／Compilation／Publicの最終Broken Linkは0を要求する。

今回のSource Missing Link 1件は、存在する`docs/public/roadmap_ja.md`を旧履歴文書が不正な相対Pathで参照している既知Source Defectである。実体欠損ではない。

Projected Rewrite Required 22件はStable／Shared版作成時の必須Link Rewrite ListとしてManifestに固定した。Cutover Acceptanceでは22件すべての解消を確認する。

## 4. Identity／Secret

実個人名、個人連絡先、個人固有Path、Credential実値、Private KeyおよびToken Patternを検査する。

Privacy Test Fixture：

```text
/Users/example/...
test@example.com
https://example.com
```

は実個人情報ではない。

## 5. Rollback Readiness

```text
Phase 1 Verified Backup      : ready
Old docs Tree                : retained
Source SHA-512 Manifest      : ready
Copy-first Procedure         : accepted
Task Notification Plan      : accepted
```

## 6. Decision

```text
Inventory Completeness Gate : PASS
Classification Gate         : PASS
Target Uniqueness Gate      : PASS
Planned Output Gate         : PASS
Rollback Readiness Gate     : PASS
Directory Migration         : NOT STARTED
```

Pre-migration Design Gateは合格とする。

ただし、これは実Directory Migrationの自動許可ではない。次の実行Turnでは、Delta Scan後にCopy-first方式でTarget Candidateを構築し、Stable Link 22件のRewrite、Known Exceptionの分離、HashおよびLink再検証を行う。

Old Treeの削除、Retirement、Git操作、担当Task通知は引き続き禁止する。
