# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current_phase_1_ex_documentation_design_accepted`
- 作成日時: `2026-07-26 14:54:51 JST`
- 更新日時: `2026-07-26 14:54:51 JST`
- Snapshot: `20260726145451`
- 作成担当: 設計統括者役
- 正本言語: 日本語
- supersedes: `documentation_index_20260726122144.md`

## 1. Current Position

```text
Phase 1                         : Complete／Accepted
Phase 1 Backup                  : Complete／Verified
Phase 1-ex                      : Started
Current Role                    : 設計統括者役 兼 Phase 1-ex設計実務担当
Documentation Target Design    : Accepted
Directory Migration            : Not Started
Canonical Docs                 : Reserved／Not Created
Git／GitHub                     : Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726122144.md](documentation_index_20260726122144.md)を継承する。

ユーザーがPhase 1-ex開始、Documentation再設計の前倒し、Phase-first構造、Stable Filename、Lossless History、Public分離および設計統括者役への移行を承認した。

## 3. Accepted ADR

[adr_0024_phase_first_project_documentation_and_lossless_history_20260726145451.md](adr/adr_0024_phase_first_project_documentation_and_lossless_history_20260726145451.md)

```text
Top-level Container   : docs/project/
Organization          : Phase-first
Current Canonical     : docs/project/current/
Phase Artifacts       : docs/project/phases/
Shared Rules          : docs/project/shared/
Public Docs           : docs/public/
Legacy History        : Phase直下で旧Treeを保持
```

## 4. Target Architecture

[phase_1_ex_target_documentation_structure_20260726145451.md](architecture/phase_1_ex_target_documentation_structure_20260726145451.md)

## 5. Migration／Canonical Requirements

[phase_1_ex_documentation_migration_and_canonical_content_requirements_20260726145451.md](requirements/phase_1_ex_documentation_migration_and_canonical_content_requirements_20260726145451.md)

Reserved Canonical Set：

```text
requirements_specification_ja.md
system_architecture_ja.md
technology_selection_ja.md
basic_design_ja.md
runtime_governance_specification_ja.md
project_continuity/project_continuity_master_ja.md
```

実作成はMigrationとSource Inventory確定後に行う。

## 6. R&D Publication Reservation

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構

DLAGSA
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構

OCILNS
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
```

- Roadmap／Overview：名称、研究領域、1～2行
- System Architecture：Optional Hook／Core非依存
- Governance Specification：Generic Port／OFF／ON
- Project Continuity Master：公開可能な範囲でより詳しく記載
- 研究核心、具体Algorithm、内部Protocol、改竄耐性方式は現在非掲載
- Project Continuity Masterも公開Repositoryへ含める

## 7. Role Transition

[design_governance_role_transition_20260726145451.md](operations/design_governance_role_transition_20260726145451.md)

```text
Current Task:
  設計統括者役
  兼 Phase 1-ex設計実務担当

Phase 1-ex専用設計者役:
  作成しない

Phase 2以降:
  Phase別設計者役を必要に応じて配置
```

## 8. Next Required Artifacts

Directoryを動かす前に作成する。

1. Full Documentation Inventory
2. Source→Target Mapping Manifest
3. Phase Classification
4. Current／Compilation／History／Public／Exclude分類
5. Collision Report
6. Relative Link Report
7. Content Hash Manifest
8. Rollback Procedure
9. Task Notification Plan

## 9. Authorization Boundary

Target StructureはAcceptedである。

Directory作成、Move、Rename、Delete、Canonical Docs生成、Git操作および担当Task通知はまだ実行していない。

## 10. Append-Only

実Migration完了まで、本Indexと既存DirectoryをCurrent入口として使用する。旧Indexを変更しない。
