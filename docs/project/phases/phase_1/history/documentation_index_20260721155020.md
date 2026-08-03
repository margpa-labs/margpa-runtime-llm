# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 15:50:20 JST`
- 更新日時: `2026-07-21 15:50:20 JST`
- Snapshot: `20260721155020`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721122621.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Project Internal Name                 : Nazuna Research Governance LLM
Phase 1-G Cross-thread Follow-up       : Implementer Report Received／Review Pending
Phase 1-H Summary Mode                 : Waiting Phase 1-G Acceptance
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Complete Reservation Updated／Not Started
Phase 10 Original R&D Hooks            : Accepted Future Reservation
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Git                                    : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721122621.md](documentation_index_20260721122621.md)から継承する。

本SnapshotはPhase 1-ex全内容、Stable Canonical Docs 5件、Project Continuity Master、Phase 10 Original R&D Hookを再統合する。

Phase 1-G Cross-thread Follow-upは[実装担当Status](handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md)を受領済みだが、設計者Final Review前であるためAcceptedへ変更しない。

## 3. Added／Updated Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current_parent_reservation | [Phase 1-ex総合要件](requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md) | Role、Git、Docs、公開、Backup、Continuityの親正本 |
| current_reservation_architecture | [Phase 1-ex Documentation／Continuity／Publication Architecture](architecture/phase_1_ex_documentation_continuity_and_publication_architecture_20260721155020.md) | Target Tree、正本層、Migration、Port構造 |
| accepted_reservation | [ADR-0018](adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md) | Stable Docs、Continuity、R&D公開Hookの決定 |
| accepted_future_reservation | [Phase 10 Original R&D Hook](governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md) | 2つの独立R&Dと疎結合統合方針 |
| current | [Implementation Roadmap](architecture/implementation_roadmap_20260721155020.md) | Current Phase状態とPhase 10予約 |
| current | [Common Project Handoff](handoffs/common_project_handoff_20260721155020.md) | 全Task向けCurrent Entry Point |

## 4. Phase 1-ex Stable Canonical Docs

Phase 1-exで次を作成する。現在は未生成である。

```text
docs/requirements_specification_ja.md
docs/system_architecture_ja.md
docs/technology_selection_ja.md
docs/basic_design_ja.md
docs/runtime_governance_specification_ja.md
```

File名は英語、本文は日本語とする。詳細設計書はPhase 1-ex必須対象外である。

## 5. Project Continuity Master

Phase 1-exで次を作成する。

```text
docs/project_continuity/project_continuity_master_ja.md
```

公開可能な継続正本としてGitHubへ含め、新TaskがProject全体を高精度に再開できる粒度を持たせる。

## 6. Public Derived Files

```text
README.md
LICENSE
CITATION.cff
NOTICE.md
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

Stable Canonical Docs、Project Continuity Master、Lossless Compilation、Derived Public Docsを別Artifactとして扱う。

## 7. Phase 10 Original R&D

### 例外認識型安全統治機構

```text
Research Area : AI Safety Governance
```

### 分散証跡型例外認識エージェント統治安全機構

```text
Research Area : Multi-Agent Governance,
                Distributed Accountability,
                and Safety Assurance
```

後者は公開概要にも`改竄耐性付き証跡`を予定要素として明記する。

両機構は本体完成後のPhase 10で、別Project／別TaskからGeneric External Governance Provider Portを通じて任意統合する。

## 8. Public Disclosure Decision

```text
Roadmap             : 名称、研究領域、1から2行概要
System Architecture : 接続位置、Optional、Core非依存
Continuity Master   : 作業概念と統合Hookをやや詳しく記載
Algorithm／Core Idea: 現時点では非掲載
```

構想の存在と方向性を先に公開し、研究の核心はまだ開示しない。

## 9. Immediate Next Gate

```text
Phase 1-G Cross-thread Follow-up Status
  → Designer Final Review＋新Index
  → Phase 1-G Acceptance
  → Phase 1-H
```

Phase 1-exまたはPhase 10へまだ着手しない。

## 10. Authorization Boundary

今回許可された変更は、Phase 1-exおよびPhase 10予約をCurrent DocsへAppend-onlyで記録することまでである。

まだ行わない。

- Phase 1-ex開始
- Role変更
- Git初期化／Commit／Push
- Docs Move／Rename／Delete
- Stable Canonical Docs 5件の実生成
- Project Continuity Masterの実生成
- README／LICENSE／CITATION／NOTICE生成
- Backup／GitHub公開
- Phase 10 R&D実装／統合

## 11. Append-Only

既存文書を変更せず、新TimestampのRequirements、Architecture、ADR、Governance、Roadmap、Handoff、Indexを追加した。
