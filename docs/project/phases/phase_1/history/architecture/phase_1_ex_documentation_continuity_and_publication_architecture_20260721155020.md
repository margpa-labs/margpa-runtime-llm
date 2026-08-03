# Phase 1-ex Documentation／Continuity／Publication Architecture

- 文書ID: `phase_1_ex_documentation_continuity_and_publication_architecture`
- 状態: `accepted_reservation_not_started`
- 作成日時: `2026-07-21 15:50:20 JST`
- 更新日時: `2026-07-21 15:50:20 JST`
- Snapshot: `20260721155020`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- Requirements: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- ADR: [adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md](../adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md)
- supersedes: `public_documentation_and_phase_compilation_architecture_20260720231036.md`

## 1. Architectural Goal

Phase 1-exでは、現在のGranular／Timestamp Docsを保持しながら、次の4用途を分離する。

```text
Canonical Technical Truth
Public Explanation
Lossless Historical Evidence
Project／Task Continuity
```

Git Historyを導入しても、Canonical、Public Derived、Historical Evidence、Handoffを同一Artifactへ混在させない。

## 2. Target Documentation Layers

```text
Source Granular Docs／Evidence
  ├─ Requirements／ADR／Architecture／Governance
  ├─ Handoff／Status／Review
  └─ Test／Backup／Operations Evidence
          │
          ├─ Lossless Compiler
          │    └─ Immutable Phase Compilation
          │
          ├─ Canonical Curator
          │    └─ Stable Canonical Technical Docs
          │
          ├─ Public Documentation
          │    └─ README／Overview／Concept／Roadmap
          │
          └─ Continuity Compiler
               └─ Project Continuity Master
```

## 3. Proposed Target Tree

Phase 1-exでInventoryとMigration PlanをAcceptedにした後、次を目標構造とする。

```text
margpa-runtime-llm/
├─ README.md
├─ LICENSE
├─ CITATION.cff
├─ NOTICE.md
└─ docs/
   ├─ requirements_specification_ja.md
   ├─ system_architecture_ja.md
   ├─ technology_selection_ja.md
   ├─ basic_design_ja.md
   ├─ runtime_governance_specification_ja.md
   ├─ public/
   │  ├─ overview_ja.md
   │  ├─ concept_ja.md
   │  ├─ roadmap_ja.md
   │  └─ phases/
   │     └─ phase_<id>_summary_ja.md
   ├─ project_continuity/
   │  └─ project_continuity_master_ja.md
   ├─ compilations/
   │  └─ phases/
   │     └─ phase_<id>_compilation_ja.md
   └─ historical／operational directories
      ├─ requirements/
      ├─ architecture/
      ├─ governance/
      ├─ adr/
      ├─ operations/
      ├─ user_manual/
      └─ handoffs/
```

`compilations/`の最終名称とHistorical Docsの物理配置はMigration Inventory後に確定する。既存Fileを先に移動しない。

## 4. Canonical Truth Model

```text
Granular Accepted Sources
  ↓ curated without changing decisions
Stable Canonical Docs
  ↓ references
README／Public Derived Docs
```

Stable Canonical DocsはCurrent Technical Truthの入口である。Granular DocsはDecisionの由来、詳細、Evidenceを保持する。

矛盾がある場合、Stable Docsが勝手に解決しない。Current Index、Accepted ADR、設計統括者Reviewを通じてDispositionを確定する。

## 5. Stable Filename／Git Model

5つのCanonical Docs、Public Docs、Project Continuity MasterはStable Filenameを持つ。

```text
Stable File Update
  → Review
  → Git Commit
  → Git Historyで過去差分保持
```

Timestamp付きEvent Docsは、Git移行後も必要なAudit／Handoff系列で維持できる。どの系列をStable化するかはPhase 1-exでOwnerごとに確定する。

## 6. Project Continuity Architecture

`project_continuity_master_ja.md`は、Task再開時の第一入口である。

```text
New Task
  → Project Continuity Master
  → Current Canonical Docs 5件
  → Current Phase Compilation／Review
  → Source／Test／Config
  → Work Resume
```

Masterは次の状態を明示する。

- Fact／Decision／Assumption／Pending／Known Issue
- Implemented／Accepted／Deferred／Not Started
- Current Owner／Write Authority
- Current Phase／Next Gate
- Prohibited Action／Authorization Boundary
- Source Document Link／Commit／Snapshot

Master自体は公開可能とする。SecretやLocal Identifierを含めずに、再開に必要な情報を保持する。

## 7. Lossless Compilation Architecture

```text
Frozen Source Set
  → Inventory／State／Size／SHA-512
  → Deterministic Ordering
  → Verbatim Payload Packaging
  → Payload Re-extraction
  → Size／SHA-512 Comparison
  → Pass／Fail Closed
```

Lossless CompilationとProject Continuity Masterは別物である。

- Compilation：元Payloadの完全保持
- Continuity Master：Current Stateを再開可能に再統合
- Public Derived Docs：閲覧者向けに説明

## 8. Role／Write Architecture

```text
設計統括者役
  ├─ Canonical Requirements／Architecture／Governance
  ├─ Project Continuity Master
  ├─ Cross-Phase Review
  └─ Final Acceptance

Phase別設計者役
  ├─ Phase Requirements／Design
  ├─ Implementer Handoff
  └─ Phase Review

実装者役
  ├─ Source／Tests／Scripts
  └─ Implementer Status

対外Docs役
  ├─ README／Public Derived Docs
  ├─ NOTICE／CITATION
  ├─ Lossless Compilation Procedure実行
  └─ External Docs Status
```

複数Ownerが同一Stable Fileを同時編集しない。内容Ownerと編集担当が異なる場合、Handoff、Diff、Reviewを必須とする。

## 9. Publication Architecture

```text
Development Tree／Evidence
  → Read-only Inventory
  → Classification Manifest
  → Allowlist Public Staging
  → Privacy／Secret／License／Binary Scan
  → Reproducibility／Test／Link Check
  → User Final Approval
  → Clean Public Commit
  → margpa-labs/margpa-runtime-llm
```

Development原本や既存履歴を直接破壊的に洗浄しない。Privacy Exceptionが必要な場合は既存Policyに従い、実値を再掲しない。

## 10. Public Document Relationship

```text
README
  → Overview／Concept／Roadmap
  → Canonical Docs 5件
  → Project Continuity Master
  → Phase Compilation／Detailed Evidence
```

READMEは一般閲覧者の入口、Canonical Docsは技術正本、Continuity Masterは開発再開、Compilationは完全Evidenceを担う。

## 11. Phase 10 External R&D Placement

```text
External Original R&D Projects
  ├─ 例外認識型安全統治機構
  └─ 分散証跡型例外認識エージェント統治安全機構
          ↓ Adapter
External Governance Provider Port
          ↓
Governance Registry／Capability Resolution
          ↓
Shared Governance Control Plane
          ↓
Distributed Governance Points／Audit／Action
```

Coreは2機構の固有Algorithm、内部State、名称を実行依存としてHard-codeしない。Registry MetadataやPublic Roadmap上の名称記載はHard-code禁止の対象外である。

## 12. Generic Extension Contracts

Phase 10統合に備え、将来次の汎用Contractを利用できる構造を維持する。

- External Governance Provider Registration
- Definition／Provider ID、Version、Hash
- Capability Declaration
- Activation Condition
- Input／Output Scope
- Governance／Decision／Delegation／Execution Event
- Exception State
- Evidence Reference
- Standard Governance Result
- Recommended／Executed Action
- `off／observe／enforce`
- Timeout／Failure／Degraded Policy
- Audit／Status Reporting

これらはPhase 10固有機構を実装する指示ではなく、既存のOptional Generic Governance Platform方針を維持するHookである。

## 13. Migration Sequence

```text
Freeze Current Docs
  → Inventory
  → Target Tree／Authority／Canonical Mapping
  → Migration Plan Review
  → Reversible Staging Migration
  → Link／Filename／Content Validation
  → Stable Docs／Master生成
  → Compilation Verification
  → Public Docs生成
  → Task Notification
  → Acceptance
  → Git／Backup／Publication
```

途中状態で新旧Pathを暗黙併用しない。Migration MarkerとCurrent Entry Pointを明示する。

## 14. Failure／Rollback

次の場合はFail Closedとする。

- Canonical Sourceが特定できない
- Lossless Payload Hashが一致しない
- Link切れ
- Public FileへPII／Secret／Model Binaryが混入
- Owner不明または権限競合
- Git SnapshotとBackup Snapshotが不一致
- Task再開試験で必要情報が欠落

旧Treeを削除せず、Accepted Migration完了までRollback可能にする。

## 15. Authorization Boundary

本ArchitectureはPhase 1-exの予約設計である。現在のDirectory変更、File移動、Stable Docs生成、Git操作、公開、Phase 10実装を許可しない。
