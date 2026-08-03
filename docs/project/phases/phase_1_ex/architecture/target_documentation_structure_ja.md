# Phase 1-ex Target Documentation Structure

- 文書ID: `phase_1_ex_target_documentation_structure`
- 状態: `accepted_migrated_current`
- 作成日時: `2026-07-26 14:54:51 JST`
- 更新日時: `2026-07-26 15:33:53 JST`
- Snapshot: `20260726145451`
- 作成担当: 設計統括者役
- 対象Phase: Phase 1-ex
- ADR: [adr_0024_phase_first_project_documentation_and_lossless_history_20260726145451.md](../adr/adr_0024_phase_first_project_documentation_and_lossless_history_ja.md)
- Requirements: [phase_1_ex_documentation_migration_and_canonical_content_requirements_20260726145451.md](../requirements/documentation_migration_and_canonical_content_requirements_ja.md)
- 正本言語: 日本語
- supersedes: `phase_1_ex_documentation_continuity_and_publication_architecture_20260721155020.md`

## 1. Target Tree

```text
docs/
├─ project/
│  ├─ current/
│  │  ├─ documentation_index_ja.md
│  │  ├─ requirements/
│  │  │  └─ requirements_specification_ja.md
│  │  ├─ architecture/
│  │  │  ├─ system_architecture_ja.md
│  │  │  ├─ technology_selection_ja.md
│  │  │  └─ basic_design_ja.md
│  │  ├─ governance/
│  │  │  └─ runtime_governance_specification_ja.md
│  │  ├─ operations/
│  │  ├─ user_manual/
│  │  └─ project_continuity/
│  │     └─ project_continuity_master_ja.md
│  │
│  ├─ phases/
│  │  ├─ phase_1/
│  │  │  ├─ phase_index_ja.md
│  │  │  ├─ adr/
│  │  │  │  └─ phase_1_adr_ja.md
│  │  │  ├─ architecture/
│  │  │  │  └─ phase_1_architecture_ja.md
│  │  │  ├─ governance/
│  │  │  │  └─ phase_1_governance_ja.md
│  │  │  ├─ handoffs/
│  │  │  │  └─ phase_1_handoffs_ja.md
│  │  │  ├─ operations/
│  │  │  │  └─ phase_1_operations_ja.md
│  │  │  ├─ requirements/
│  │  │  │  └─ phase_1_requirements_ja.md
│  │  │  ├─ user_manual/
│  │  │  │  └─ phase_1_user_manual_ja.md
│  │  │  ├─ index/
│  │  │  │  └─ phase_1_documentation_index_ja.md
│  │  │  └─ history/
│  │  │     ├─ adr/
│  │  │     ├─ architecture/
│  │  │     ├─ governance/
│  │  │     ├─ handoffs/
│  │  │     ├─ operations/
│  │  │     ├─ requirements/
│  │  │     ├─ user_manual/
│  │  │     └─ documentation_index_*.md
│  │  │
│  │  └─ phase_1_ex/
│  │     ├─ phase_index_ja.md
│  │     ├─ adr/
│  │     ├─ architecture/
│  │     ├─ governance/
│  │     ├─ handoffs/
│  │     ├─ operations/
│  │     ├─ requirements/
│  │     ├─ user_manual/
│  │     ├─ index/
│  │     └─ history/
│  │
│  └─ shared/
│     ├─ conventions/
│     ├─ task_roles/
│     ├─ schemas/
│     └─ templates/
│
└─ public/
   ├─ overview_ja.md
   ├─ concept_ja.md
   ├─ roadmap_ja.md
   └─ history/
      ├─ overview_phase_1_ja.md
      ├─ concept_phase_1_ja.md
      └─ roadmap_phase_1_ja.md
```

必要なDirectoryだけ作成し、空DirectoryをGitへ残すためだけのDummy Fileは原則作らない。将来必要なDirectoryはMigration時の実Artifactに合わせて作る。

## 2. `project/current/`

Project横断の最新技術正本を置く。

### 2.1 Required Canonical Set

```text
docs/project/current/requirements/requirements_specification_ja.md
docs/project/current/architecture/system_architecture_ja.md
docs/project/current/architecture/technology_selection_ja.md
docs/project/current/architecture/basic_design_ja.md
docs/project/current/governance/runtime_governance_specification_ja.md
docs/project/current/project_continuity/project_continuity_master_ja.md
```

### 2.2 Current Index

```text
docs/project/current/documentation_index_ja.md
```

New Task、Human Reader、RAGおよびProject OperatorがCurrent Setを解決する第一入口とする。

## 3. `project/phases/`

Phase単位で次を保持する。

- Phase Index
- Category別Lossless Compilation
- Final Review
- User Acceptance
- Backup／Release Evidence
- 旧Granular History

Phase Compilationは人が読める構造へ再整理するが、Source内容を勝手に縮小、意味変更または再解釈しない。

各Compilationは最低限次を持つ。

```text
document_id
phase
status
language
created_at
frozen_at
source_documents
source_manifest
source_hashes
supersedes
rag_default
```

## 4. `project/phases/phase_1/history/`

Phase 1 Backup入力Index `documentation_index_20260726121346.md`を基準に、Git開始前の旧Treeを保持する。

旧Granular Docsは原File名と内容を維持する。

Phase 1 Backup完了後に作成されたDetached Evidenceは、Classification ManifestでPhase 1 Transition EvidenceまたはPhase 1-ex Sourceへ明示分類する。

Phase所属は対象Phaseではなく、原則として「その文書を決定・作成した開発Phase」で判断する。Phase 1中に作成されたPhase 10予約文書は、Phase 1で確定した将来要件EvidenceとしてPhase 1 Historyに含める。

## 5. `project/phases/phase_1_ex/`

Phase 1-ex開始後に作成する要件、Architecture、ADR、Migration Manifest、ReviewおよびHandoffを置く。

現在のTaskは設計統括者役としてPhase 1-ex設計実務も担当する。

Phase 1-ex完了時に、同じLossless Compilation／History／Index構造へFreezeする。

## 6. `project/shared/`

Phaseに依存しないものを置く。

```text
conventions/
  → Filename、Language、Markdown、Git、Documentation規則

task_roles/
  → 設計統括者、Phase別設計者、実装者、対外Docs役のAuthority

schemas/
  → Document Metadata、Manifest、Index、Audit等

templates/
  → ADR、Requirements、Handoff、Status、Review、Phase Compilation
```

Secret、Credential、個人連絡先または非公開研究核心を置くためのDirectoryではない。

## 7. `public/`

人が最初に読む対外説明を置く。

```text
overview_ja.md
concept_ja.md
roadmap_ja.md
```

`docs/public/`の日本語版を正本とし、日本語版作成・更新時に対応する`_en`派生版も作成する。英語版は概要または短縮版ではなく、日本語正本と同じ粒度、情報量および構造を持つ完全な派生版とする。

同様に`docs/project/current/`も日本語正本と、同じ粒度の英語派生版を持つ。Phase／Shared／Raw Historyは日本語のみとする。

`history/`はMilestone Snapshotだけを保持し、細かい編集履歴はGitへ任せる。

## 8. R&D Extension Placement

### 8.1 Public Roadmap

EASA、DLAGSA、OCILNSについて次だけを記載する。

- 略称
- 正式英名
- 正式日本語名
- 研究領域
- 1～2行の概要
- 将来統合であり未実装であること

### 8.2 System Architecture

- Optional External R&D System
- Core非依存
- Generic Port
- 個別OFF／ON
- Default OFF
- Systemなしで本体が完全動作

具体Algorithm、内部Protocolまたは改竄耐性方式の核心は記載しない。

### 8.3 Runtime Governance Specification

- EASA／DLAGSA向けGeneric External Governance Provider Port
- OCILNS向けGeneric Evidence Ledger Port
- OFF時のLoad／Call／Write／Side Effect禁止
- Failure Isolation
- Observe／Enforce状態を偽装しないBoundary

### 8.4 Project Continuity Master

公開可能な範囲で、Roadmapより詳しく次を記載する。

- 研究目的
- 対象問題
- MARGPAとの接続位置
- Adapter／Port境界
- Config OFF／ON
- Phase 10予約
- 外部Project／別Task開発
- 将来拡張時にCoreを変更しない原則

Project Continuity Masterも公開Repositoryへ含める。非公開文書として扱わない。

## 9. Link Architecture

- Current IndexからCurrent Canonical SetへLinkする。
- Phase IndexからCategory Compilation、Final Review、Backup EvidenceへLinkする。
- CompilationからSource ManifestへLinkする。
- Source ManifestからHistory原文書とSHA-512を解決する。
- Public Docsから必要最小限だけCurrent Canonical DocsへLinkする。
- History原文書からCurrentへ無理にBacklinkを追記しない。

## 10. Migration Boundary

実Migration前に次を確定する。

1. Full Inventory
2. Source→Target Mapping
3. Phase Classification
4. Current／Compilation／History／Public／Exclude分類
5. Collision検出
6. Relative Link検証
7. Content Hash
8. Rollback
9. Task通知

本Architectureだけでは実移動しない。

## 11. Migration Result

ユーザー確認、Full Inventory、Source→Target Manifest、Rollback PlanおよびPreflight合格後、`2026-07-26 15:16:24 JST`にCopy-first Migrationを実行した。

```text
Target Tree              : created
Phase 1 Raw History      : copied／SHA-512 verified
Phase 1 Compilation      : 307 Sources／8 Categories
Current Canonical Set    : created
Stable Link Rewrite      : 22
Old Source Tree          : retained through validation, then duplicate root retired
Raw Source Content       : preserved in Phase／Public History
Legacy Root Duplicates   : retired after SHA-512 verification
Legacy Files Remaining  : 0
Git Operation            : not executed
```

Current入口は`docs/project/current/documentation_index_ja.md`とする。
