# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 16:22:42 JST`
- 更新日時: `2026-07-21 16:22:42 JST`
- Snapshot: `20260721162242`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721155020.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G Cross-thread Follow-up       : Implementer Report Received／Review Pending
Phase 1-H                             : Waiting Phase 1-G Acceptance
Phase 1-ex                            : Accepted Reservation／Not Started
Phase 10 Original R&D Systems         : EASA／DLAGSA／OCILNS
Original R&D Public Names             : Accepted
Original R&D Config ON／OFF            : Accepted Future Requirement
Initial GitHub Publication            : Deferred until Phase 1-ex completion
Git                                   : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721155020.md](documentation_index_20260721155020.md)から継承する。

本SnapshotはEASA／DLAGSAの正式名称公開、OCILNS追加、3 System個別ON／OFF、Phase 10統合Architectureを追加する。

Phase 1-ex総合要件は継続し、本SnapshotのExternal R&D Requirementsを追加要件として適用する。

## 3. Added／Updated Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted_reservation | [External R&D公開・統合要件](requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md) | 3 System名称、記載先、ON／OFF、公開境界 |
| current_future_catalog | [Phase 10 Original R&D Catalog](governance/phase_10_original_r_and_d_system_catalog_20260721162242.md) | EASA／DLAGSA／OCILNSの公開正本 |
| accepted_future_architecture | [Phase 10 Integration Architecture](architecture/phase_10_external_r_and_d_integration_architecture_20260721162242.md) | Governance／Ledger PortとConfig境界 |
| accepted_future_reservation | [ADR-0019](adr/adr_0019_phase_10_original_r_and_d_public_names_and_switches_20260721162242.md) | 正式名称、公開範囲、SwitchのDecision |
| current | [Implementation Roadmap](architecture/implementation_roadmap_20260721162242.md) | Phase 10の3 Systemを同粒度で掲載 |
| current | [Common Project Handoff](handoffs/common_project_handoff_20260721162242.md) | 全Task向けCurrent名称／位置づけ |

## 4. Official Names

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

## 5. Research Areas

```text
EASA
  AI Safety Governance

DLAGSA
  Multi-Agent Governance,
  Distributed Accountability,
  and Safety Assurance

OCILNS
  Cognitive Interaction Provenance,
  Verifiable AI Systems,
  and Distributed Auditability
```

## 6. Config Requirement

```text
EASA   : OFF／ON
DLAGSA : OFF／ON
OCILNS : OFF／ON
Default: All OFF
```

各Systemを独立して切替可能にし、OFF時はLoad、Call、Write、Side Effectを発生させない。

## 7. Integration Boundary

- EASA／DLAGSA：Generic External Governance Provider Port
- OCILNS：Generic Evidence Ledger Port
- Core非依存
- 別Project／別Task
- Phase 10／本体完成後
- Providerなしで本体完全動作

## 8. Public Disclosure

```text
Roadmap             : 名称、研究領域、1から2行概要
System Architecture : 接続位置、Optional、ON／OFF
Continuity Master   : 作業概念をやや詳しく記録
Core Algorithm      : 現在非掲載
```

OCILNSは改竄耐性付き証跡を扱う。単一SHA-512 Digestだけに依存しない予定であるが、具体方式は現在記載しない。

## 9. Phase 1-ex Output Mapping

Phase 1-exで作成する次の文書へ3 Systemを反映する。

- `requirements_specification_ja.md`
- `system_architecture_ja.md`
- `basic_design_ja.md`
- `runtime_governance_specification_ja.md`
- `project_continuity_master_ja.md`
- `roadmap_ja.md`

`technology_selection_ja.md`へ各R&D System内部の使用技術を記載しない。本体Adapter側の技術判断だけを扱う。

## 10. Immediate Next Gate

Phase 1-exとPhase 10へまだ着手しない。Phase 1-G Cross-thread Follow-upの設計者Final Reviewが次である。

## 11. Authorization Boundary

今回許可された変更は3 Systemの名称、概要、研究領域、将来Integration／ON／OFF要件をDocsへAppend-onlyで記録することまでである。

Config、Source、External System、Git、GitHub、Phase 10実装は変更しない。

## 12. Append-Only

既存文書を変更せず、新TimestampのRequirements、Catalog、Architecture、ADR、Roadmap、Handoff、Indexを追加した。
