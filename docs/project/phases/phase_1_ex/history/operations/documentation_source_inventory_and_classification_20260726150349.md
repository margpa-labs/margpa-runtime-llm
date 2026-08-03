# Documentation Source Inventory／Classification

- 文書ID: `documentation_source_inventory_and_classification`
- 状態: `verified_pre_migration_inventory`
- 作成日時: `2026-07-26 15:03:49 JST`
- 更新日時: `2026-07-26 15:03:49 JST`
- Snapshot: `20260726150349`
- 作成担当: 設計統括者役
- 対象: 実Directory Migration前の`docs/`全File
- Machine-readable Manifest: [source_to_target_documentation_migration_manifest_20260726150349.json](source_to_target_documentation_migration_manifest_20260726150349.json)
- Target Architecture: [phase_1_ex_target_documentation_structure_20260726145451.md](../architecture/phase_1_ex_target_documentation_structure_20260726145451.md)
- Preflight: [documentation_migration_preflight_20260726150349.md](documentation_migration_preflight_20260726150349.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Purpose

実移動前の全Sourceを固定し、各Fileについて次をMachine-readable Manifestへ記録する。

- Source Path
- Size
- SHA-512
- Extension
- Timestamped Filename
- Source Category
- Phase Classification
- Disposition
- Target Path
- Stable／History／Public／Exclude
- Classification Reason

## 2. Inventory Boundary

Inventory対象は本書、Link／Rollback Plan、Role Authority後継版、Task通知計画、Preflightおよび同SnapshotのDocumentation Indexを含む。

Machine-readable Manifest自身は自己参照Hashを避けるため対象外とする。

```text
Self-excluded Artifact:
docs/operations/source_to_target_documentation_migration_manifest_20260726150349.json
```

Manifest生成後に追加または変更されたFileは、実移動直前のDelta Scanで列挙する。黙ってSource Setへ混入させない。

## 3. Phase Classification

### Phase 1

Phase 1完了、BackupおよびTransition Evidenceまでに作成された非Public文書。

```text
Cutoff Evidence:
docs/documentation_index_20260726122144.md
```

Target：

```text
docs/project/phases/phase_1/history/
```

### Phase 1-ex

Phase 1-ex開始後に作成された設計、要件、ADR、Role、Migration ControlおよびIndex。

Target：

```text
docs/project/phases/phase_1_ex/
```

AcceptedなCurrent Phase設計文書はStable FilenameへRenameする。Immutable Event、旧IndexおよびSource EvidenceはPhase 1-ex `history/`へ置く。

### Public

```text
docs/public/roadmap_ja.md
  → Current Stableとして維持

docs/public/history/roadmap_ja_20260722023908.md
  → docs/public/history/roadmap_phase_1_ja.md
```

### Exclude

```text
.DS_Store
```

## 4. Disposition Types

```text
history
  → 内容とFile名を維持してPhase Historyへ移す

stable
  → Current／Active PhaseのStable Filenameへ移す

public_current
  → Public Current Pathを維持する

public_history
  → Public Milestone FilenameへRenameする

exclude
  → Target Treeへ移さない

compile
  → Source群からLossless Compilationを後で生成する

generate
  → Canonical／Index／Shared文書を後で生成する
```

`compile`と`generate`はSource FileのDispositionではなく、Manifestの`planned_outputs`へ記録する。

## 5. Stable Phase 1-ex Sources

次はTimestampを外したStable Filenameへ移す。

```text
ADR-0024
  → docs/project/phases/phase_1_ex/adr/
     adr_0024_phase_first_project_documentation_and_lossless_history_ja.md

Target Documentation Structure
  → docs/project/phases/phase_1_ex/architecture/
     target_documentation_structure_ja.md

Documentation Migration Requirements
  → docs/project/phases/phase_1_ex/requirements/
     documentation_migration_and_canonical_content_requirements_ja.md

Link／Rollback Plan
  → docs/project/phases/phase_1_ex/operations/
     documentation_link_update_and_rollback_plan_ja.md

Migration Preflight
  → docs/project/phases/phase_1_ex/operations/
     documentation_migration_preflight_ja.md

Task Notification Plan
  → docs/project/phases/phase_1_ex/handoffs/
     documentation_migration_task_notification_plan_ja.md
```

Role AuthorityはPhase固有ではなく、後継Current Policyを`docs/project/shared/task_roles/`へ生成する。

## 6. Planned Phase 1 Compilations

```text
docs/project/phases/phase_1/phase_index_ja.md
docs/project/phases/phase_1/adr/phase_1_adr_ja.md
docs/project/phases/phase_1/architecture/phase_1_architecture_ja.md
docs/project/phases/phase_1/governance/phase_1_governance_ja.md
docs/project/phases/phase_1/handoffs/phase_1_handoffs_ja.md
docs/project/phases/phase_1/operations/phase_1_operations_ja.md
docs/project/phases/phase_1/requirements/phase_1_requirements_ja.md
docs/project/phases/phase_1/user_manual/phase_1_user_manual_ja.md
docs/project/phases/phase_1/index/phase_1_documentation_index_ja.md
```

これらはMachine Mapping後にSource Manifestを固定してから作成する。

## 7. Planned Current Canonical Set

```text
docs/project/current/documentation_index_ja.md
docs/project/current/requirements/requirements_specification_ja.md
docs/project/current/architecture/system_architecture_ja.md
docs/project/current/architecture/technology_selection_ja.md
docs/project/current/architecture/basic_design_ja.md
docs/project/current/governance/runtime_governance_specification_ja.md
docs/project/current/project_continuity/project_continuity_master_ja.md
```

## 8. Planned Shared Set

```text
docs/project/shared/conventions/documentation_rules_ja.md
docs/project/shared/task_roles/task_role_write_authority_policy_ja.md
```

Schema／Templateは必要性とSourceが確定したものだけ生成する。

## 9. Verified Counts

Machine-readable Manifestによる確定値は次のとおり。

```text
Inventory Entries      : 322
Markdown               : 320
Excluded Metadata      : 2
Phase 1 History        : 307
Phase 1-ex Stable      : 8
Phase 1-ex History     : 3
Public Current         : 1
Public History         : 1
Target Collision       : 0
Planned Output Collision: 0
```

Source FileのDisposition：

```text
History                : 310
Stable                 : 8
Public Current         : 1
Public History         : 1
Exclude                : 2
```

Sourceから後続生成するPlanned Output：

```text
Compile                : 9
Generate               : 10
```

`compile`と`generate`は既存Sourceの移動先ではなく、Lossless Compilation、Canonical文書、IndexおよびManifestの生成予約である。

## 10. Link Classification

Inventory内Markdownの相対Linkは`2,874`件である。

```text
Projected Preserved          : 2,777
Projected Rewrite Required   : 22
Known History Exception      : 39
External to Docs Inventory   : 35
Source Missing               : 1
```

`Source Missing`の1件は、Phase 1旧履歴の次の記述である。

```text
Source:
docs/requirements/
phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md

Raw Link:
docs/public/roadmap_ja.md

Actual Existing Target:
docs/public/roadmap_ja.md
```

Source文書の配置から見た相対Pathとして不正であるが、参照対象自体は存在する。旧履歴原本は変更せず、Known Source DefectとしてManifestとPhase CompilationのSource Noteから解決する。

`Projected Rewrite Required`の22件はすべてStable／Sharedへ昇格するPhase 1-ex文書のLinkであり、Target Copy後のStable版で新Pathへ更新する。Raw Sourceは変更しない。

## 11. Acceptance

- 全Source Fileが1回だけInventoryへ現れる。
- `.DS_Store`以外に未分類Fileがない。
- Source SHA-512が記録される。
- Source Targetが一意である。
- Planned OutputとSource Targetが衝突しない。
- Phase 1 Backup BoundaryとPhase 1-ex開始Boundaryを区別する。
- Manifest Self-exclusionを明示する。
- 実移動前Delta Scanを必須とする。

上記条件は、実移動を除くPre-migration Inventory段階で満たされている。
