# Phase 1-ex Documentation Migration／Canonical Content 要件

- 文書ID: `phase_1_ex_documentation_migration_and_canonical_content_requirements`
- 状態: `accepted_not_migrated`
- 作成日時: `2026-07-26 14:54:51 JST`
- 更新日時: `2026-07-26 14:54:51 JST`
- Snapshot: `20260726145451`
- 作成担当: 設計統括者役
- 対象Phase: Phase 1-ex
- Architecture: [phase_1_ex_target_documentation_structure_20260726145451.md](../architecture/phase_1_ex_target_documentation_structure_20260726145451.md)
- ADR: [adr_0024_phase_first_project_documentation_and_lossless_history_20260726145451.md](../adr/adr_0024_phase_first_project_documentation_and_lossless_history_20260726145451.md)
- Phase 10 Catalog: [phase_10_original_r_and_d_system_catalog_20260721162242.md](../governance/phase_10_original_r_and_d_system_catalog_20260721162242.md)
- 正本言語: 日本語
- supersedes: `phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md`のDocumentation配置部分

## 1. Migration Goal

Git開始前のTimestamp付きAppend-only Docsを失わず、人、Task、RAGおよびGitがCurrent／Phase／History／Publicを一意に解決できる構造へ移行する。

## 2. Required Canonical Documents

実作成はDirectory MigrationとSource Inventory確定後に行う。

```text
docs/project/current/requirements/
└─ requirements_specification_ja.md

docs/project/current/architecture/
├─ system_architecture_ja.md
├─ technology_selection_ja.md
└─ basic_design_ja.md

docs/project/current/governance/
└─ runtime_governance_specification_ja.md

docs/project/current/project_continuity/
└─ project_continuity_master_ja.md
```

File名はTimestampなしとし、作成日、更新日、StatusおよびGit情報を本文Metadataへ記録する。

## 3. Canonical Document Roles

### 3.1 Requirements Specification

- 機能要件
- 非機能要件
- Platform／Resource
- Security／Privacy
- Governance／Audit
- Model／GD交換性
- Phase／Out of Scope／Acceptance
- 未実装／将来要件

### 3.2 System Architecture

- System全体構造
- Layer／Module責務
- Port／Adapter
- Local／Lightning／Cloud／Hybrid
- Data／Control／Event Flow
- Trust／Authority Boundary
- EASA／DLAGSA／OCILNS等のOptional Hook

### 3.3 Technology Selection

- 採用技術／Version
- 採用理由
- 不採用／保留
- Platform／Backend互換性
- Model／Deployment Artifact
- 再評価条件

### 3.4 Basic Design

- API／UI／Config／Model／Storage／Governance
- External／Internal Interface
- State／Error／Cancellation／Security
- Directory／Schema
- 詳細実装へ渡すBoundary

### 3.5 Runtime Governance Specification

- ARGD／DAGD
- GD 0件Baseline
- 未知GD／任意JSON
- Registry／Loader／Validator／Compiler／Instance
- Shared Control Plane＋Distributed Governance Point
- `off／observe／enforce`
- Layer別ON／OFF
- State／Score／Deviation／Action／Repair
- EASA／DLAGSA／OCILNS External Port

### 3.6 Project Continuity Master

- Project目的、思想、現在地点
- Current Phase／Next Phase
- Model／Backend／Environment
- Current Canonical Docs
- Role／Authority
- Major Decisions
- Known Issues
- Backup／Git／Release
- Future Extensions
- EASA／DLAGSA／OCILNSの公開可能な継続情報
- New Taskが即再開するための読込順序

## 4. EASA

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構

Research Area:
AI Safety Governance
```

公開概要：

内部安全傾向、周辺安全制御、入力文脈および生成過程等の相互作用を対象とし、例外を含む複合的な安全挙動を統治する独立R&D Architecture。

`Embedded Safety Layer`はEASA上の作業概念であり、特定製品内に単一の物理Layerが存在すると断定しない。

## 5. DLAGSA

```text
DLAGSA
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構

Research Area:
Multi-Agent Governance,
Distributed Accountability,
and Safety Assurance
```

公開概要：

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う独立R&D Architecture。

単純な複数AIの並列化、単一Safety Filterまたは単一Log機構ではない。`LEA`の意味をMARGPA側で推測または再定義しない。

## 6. OCILNS

```text
OCILNS
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網

Research Area:
Cognitive Interaction Provenance,
Verifiable AI Systems,
and Distributed Auditability
```

公開概要：

人、AI、Toolおよび外部System間の認知的対話出来事を、検証、参照、継承、監査できる改竄耐性付き証跡単位として扱い、長期、分岐、多Model、多Thread環境でも再接続可能性を維持する独立R&D System。

LLM応答精度の直接向上を目的とせず、対話、判断、制約、継承および改変検知情報の長期的な検証可能性を対象とする。

## 7. Public Disclosure Levels

### Roadmap／Overview

```text
名称
研究領域
1～2行の概要
未実装／将来予約
```

### System Architecture／Governance

```text
Optional性
接続Port
Core非依存
個別OFF／ON
Default OFF
Failure Isolation
```

### Project Continuity Master

Roadmapより詳しいが、研究の核心、具体Algorithm、内部Protocolまたは具体的改竄耐性方式は記載しない。

Project Continuity Masterは公開可能文書であり、公開Repositoryへ含める。

## 8. Extension Requirements

```text
EASA   : Generic External Governance Provider Port
DLAGSA : Generic External Governance Provider Port
OCILNS : Generic Evidence Ledger Port
```

- 別Project／別Taskで開発する。
- MARGPA Runtime LLM本体完成後のPhase 10で統合する。
- 3 SystemなしでCoreは完全動作する。
- 各SystemをConfigで個別OFF／ON可能にする。
- DefaultはすべてOFFとする。
- OFF時はLoad、Call、Write、Side Effectを行わない。
- 固有名称をApplication CoreへHard-codeしない。
- 将来さらに多数の外部Systemを追加可能なGeneric Hookを維持する。

## 9. Lossless Compilation

「まとめる」は要約を意味しない。

各Phase Category Compilationは次を満たす。

1. Source Inventoryを先に確定する。
2. 全SourceをManifestへ列挙する。
3. Source SHA-512を記録する。
4. 決定、条件、例外、未解決事項を削らない。
5. 矛盾するSourceは勝手に統合せず、Conflictとして示す。
6. Sourceの意味を変えない。
7. 再配置、見出し整理および重複参照の統合はできる。
8. 省略した重複もSource Mappingから追跡可能にする。
9. History原本を削除しない。

## 10. Migration Preconditions

実移動前に作成する。

- Full File Inventory
- Source→Target Mapping Manifest
- Phase Classification
- Collision Report
- Relative Link Report
- Current／Compilation／History／Public／Exclude分類
- Content Hash
- Rollback Procedure
- Task Notification

## 11. Acceptance Conditions

- Current Canonical Setを一意に解決できる。
- Phase 1 Category Compilationを一意に解決できる。
- 旧Granular DocsをすべてHistoryから解決できる。
- Source CountとMigration Countが一致する。
- Content Hashが一致する。
- Broken Relative Linkが0、または既知例外として列挙される。
- RAG DefaultでHistoryが混入しない。
- Public DocsとProject技術正本の役割が明確である。
- EASA／DLAGSA／OCILNSの公開位置と詳細度が満たされる。
- 個人情報、連絡先、CredentialまたはSecretを追加しない。

## 12. Authorization Boundary

本要件はCanonical Set、R&D記載位置およびMigration条件を確定するが、Canonical文書の実生成またはFile Migrationはまだ開始しない。
